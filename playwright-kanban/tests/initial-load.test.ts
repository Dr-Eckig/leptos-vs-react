import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  createPerformanceResultEntry,
  performanceTargets,
  performanceTestTimeout,
  runs,
  writePerformanceResults,
  type PerformanceResultEntry,
  type PerformanceTarget,
} from './util';

const initialLoadBoardLabel = 'Initial Load';
const initialLoadMetricTimeout = 10_000;

type InitialLoadMetrics = {
  firstContentfulPaint: number | null;
  largestContentfulPaint: number | null;
  largestContentfulPaintSupported: boolean;
};

type InitialLoadMetricWindow = Window & {
  __kanbanInitialLoadMetrics?: InitialLoadMetrics;
  __kanbanLcpObserver?: PerformanceObserver;
};

test.setTimeout(performanceTestTimeout);

for (const target of performanceTargets) {
  test(
    `${target.framework}: measure initial load repeatedly`,
    async ({ page }, testInfo) => {
      await measureInitialLoadRepeatedly(page, testInfo, target);
    },
  );
}

async function measureInitialLoadRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
): Promise<void> {
  await installInitialLoadObservers(page);

  const firstContentfulPaintEntries: PerformanceResultEntry[] = [];
  const largestContentfulPaintEntries: PerformanceResultEntry[] = [];

  for (let run = 1; run <= runs; run++) {
    await test.step(`run ${run}`, async () => {
      const metrics = await measureInitialLoad(page, target, run);

      firstContentfulPaintEntries.push(
        createPerformanceResultEntry(
          target,
          run,
          'initial-load-fcp',
          initialLoadBoardLabel,
          requireMetric(metrics.firstContentfulPaint, 'FCP', target, run),
        ),
      );

      if (metrics.largestContentfulPaintSupported) {
        largestContentfulPaintEntries.push(
          createPerformanceResultEntry(
            target,
            run,
            'initial-load-lcp',
            initialLoadBoardLabel,
            requireMetric(metrics.largestContentfulPaint, 'LCP', target, run),
          ),
        );
      }
    });
  }

  await writePerformanceResults(
    testInfo,
    target,
    'initial-load',
    'initial-load-fcp.json',
    firstContentfulPaintEntries,
  );

  expect(firstContentfulPaintEntries).toHaveLength(runs);

  if (largestContentfulPaintEntries.length > 0) {
    await writePerformanceResults(
      testInfo,
      target,
      'initial-load',
      'initial-load-lcp.json',
      largestContentfulPaintEntries,
    );

    expect(largestContentfulPaintEntries).toHaveLength(runs);
  } else {
    testInfo.annotations.push({
      type: 'info',
      description: 'Largest Contentful Paint is not supported in this browser.',
    });
  }
}

async function installInitialLoadObservers(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const metricWindow = window as InitialLoadMetricWindow;

    metricWindow.__kanbanInitialLoadMetrics = {
      firstContentfulPaint: null,
      largestContentfulPaint: null,
      largestContentfulPaintSupported:
        typeof PerformanceObserver !== 'undefined' &&
        (PerformanceObserver.supportedEntryTypes ?? []).includes(
          'largest-contentful-paint',
        ),
    };

    const updateFirstContentfulPaint = (
      entries: PerformanceEntry[],
    ): void => {
      const fcpEntry = entries.find(
        (entry) => entry.name === 'first-contentful-paint',
      );

      if (fcpEntry) {
        metricWindow.__kanbanInitialLoadMetrics!.firstContentfulPaint =
          fcpEntry.startTime;
      }
    };

    updateFirstContentfulPaint(performance.getEntriesByType('paint'));

    if (typeof PerformanceObserver === 'undefined') {
      return;
    }

    try {
      new PerformanceObserver((entryList) => {
        updateFirstContentfulPaint(entryList.getEntries());
      }).observe({
        type: 'paint',
        buffered: true,
      });
    } catch {
      // Not all engines expose Paint Timing via PerformanceObserver.
    }

    try {
      const lcpObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];

        if (lastEntry) {
          metricWindow.__kanbanInitialLoadMetrics!.largestContentfulPaint =
            lastEntry.startTime;
        }
      });

      metricWindow.__kanbanLcpObserver = lcpObserver;

      lcpObserver.observe({
        type: 'largest-contentful-paint',
        buffered: true,
      });
    } catch {
      // Not all engines expose Largest Contentful Paint.
    }
  });
}

async function measureInitialLoad(
  page: Page,
  target: PerformanceTarget,
  run: number,
): Promise<InitialLoadMetrics> {
  await page.goto(urlForRun(target.url, run), {
    waitUntil: 'domcontentloaded',
  });

  await page.waitForLoadState('load');

  await expect(page.getByTestId('sidebar-board-0')).toBeVisible();

  await waitForInitialLoadMetrics(page);

  await waitForRenderingCycle(page);

  return await page.evaluate(() => {
    const metricWindow = window as InitialLoadMetricWindow;
    const metrics = metricWindow.__kanbanInitialLoadMetrics;

    const lcpObserver = metricWindow.__kanbanLcpObserver;

    if (lcpObserver) {
      const pendingEntries = lcpObserver.takeRecords();
      const lastEntry = pendingEntries[pendingEntries.length - 1];

      if (lastEntry && metrics) {
        metrics.largestContentfulPaint = lastEntry.startTime;
      }

      lcpObserver.disconnect();
      metricWindow.__kanbanLcpObserver = undefined;
    }

    const paintEntries = performance.getEntriesByType('paint');

    const firstContentfulPaintEntry = paintEntries.find(
      (entry) => entry.name === 'first-contentful-paint',
    );

    return {
      firstContentfulPaint:
        metrics?.firstContentfulPaint ??
        firstContentfulPaintEntry?.startTime ??
        null,

      largestContentfulPaint:
        metrics?.largestContentfulPaint ?? null,

      largestContentfulPaintSupported:
        metrics?.largestContentfulPaintSupported ?? false,
    };
  });
}

async function waitForInitialLoadMetrics(page: Page): Promise<void> {
  await page.waitForFunction(
    () => {
      const metricWindow = window as InitialLoadMetricWindow;
      const metrics = metricWindow.__kanbanInitialLoadMetrics;

      if (!metrics) {
        return false;
      }

      const fcpAvailable =
        typeof metrics.firstContentfulPaint === 'number';

      const lcpAvailable =
        !metrics.largestContentfulPaintSupported ||
        typeof metrics.largestContentfulPaint === 'number';

      return fcpAvailable && lcpAvailable;
    },
    undefined,
    { timeout: initialLoadMetricTimeout },
  );
}

async function waitForRenderingCycle(page: Page): Promise<void> {
  await page.evaluate(
    () =>
      new Promise<void>((resolve) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => resolve());
        });
      }),
  );
}

function urlForRun(url: string, run: number): string {
  const targetUrl = new URL(url);
  targetUrl.searchParams.set('performanceRun', String(run));
  return targetUrl.toString();
}

function requireMetric(
  value: number | null,
  metricName: string,
  target: PerformanceTarget,
  run: number,
): number {
  if (value === null) {
    throw new Error(
      `${metricName} was not reported for ${target.framework} on run ${run}.`,
    );
  }

  return value;
}
