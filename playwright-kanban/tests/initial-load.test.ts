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
const largestContentfulPaintQuietWindowMs = 250;

type InitialLoadMetrics = {
  firstContentfulPaint: number | null;
  largestContentfulPaint: number | null;
  largestContentfulPaintSupported: boolean;
  lastLargestContentfulPaintAt: number | null;
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
) {
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

async function installInitialLoadObservers(page: Page) {
  await page.addInitScript(() => {
    const metricWindow = window as Window & {
      __kanbanInitialLoadMetrics?: InitialLoadMetrics;
    };

    metricWindow.__kanbanInitialLoadMetrics = {
      firstContentfulPaint: null,
      largestContentfulPaint: null,
      largestContentfulPaintSupported:
        typeof PerformanceObserver !== 'undefined' &&
        (PerformanceObserver.supportedEntryTypes ?? []).includes(
          'largest-contentful-paint',
        ),
      lastLargestContentfulPaintAt: null,
    };

    const updateFirstContentfulPaint = (entries: PerformanceEntry[]) => {
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
      }).observe({ type: 'paint', buffered: true });
    } catch {
      // Not all engines expose Paint Timing via PerformanceObserver.
    }

    try {
      new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];

        if (lastEntry) {
          metricWindow.__kanbanInitialLoadMetrics!.largestContentfulPaint =
            lastEntry.startTime;
          metricWindow.__kanbanInitialLoadMetrics!.lastLargestContentfulPaintAt =
            performance.now();
        }
      }).observe({ type: 'largest-contentful-paint', buffered: true });
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
  await expect(page.getByTestId('sidebar-board-0')).toBeVisible();
  await page.waitForLoadState('load');
  await waitForInitialLoadMetrics(page);

  return await page.evaluate(() => {
    const metricWindow = window as Window & {
      __kanbanInitialLoadMetrics?: InitialLoadMetrics;
    };
    const paintEntries = performance.getEntriesByType('paint');
    const firstContentfulPaintEntry = paintEntries.find(
      (entry) => entry.name === 'first-contentful-paint',
    );

    return {
      firstContentfulPaint:
        metricWindow.__kanbanInitialLoadMetrics?.firstContentfulPaint ??
        firstContentfulPaintEntry?.startTime ??
        null,
      largestContentfulPaint:
        metricWindow.__kanbanInitialLoadMetrics?.largestContentfulPaint ?? null,
      largestContentfulPaintSupported:
        metricWindow.__kanbanInitialLoadMetrics
          ?.largestContentfulPaintSupported ?? false,
      lastLargestContentfulPaintAt:
        metricWindow.__kanbanInitialLoadMetrics?.lastLargestContentfulPaintAt ??
        null,
    };
  });
}

async function waitForInitialLoadMetrics(page: Page) {
  await page.waitForFunction(
    () => {
      const metricWindow = window as Window & {
        __kanbanInitialLoadMetrics?: InitialLoadMetrics;
      };

      return (
        typeof metricWindow.__kanbanInitialLoadMetrics?.firstContentfulPaint ===
        'number'
      );
    },
    undefined,
    { timeout: initialLoadMetricTimeout },
  );

  await page.waitForFunction(
    (quietWindowMs) => {
      const metricWindow = window as Window & {
        __kanbanInitialLoadMetrics?: InitialLoadMetrics;
      };
      const metrics = metricWindow.__kanbanInitialLoadMetrics;

      if (!metrics?.largestContentfulPaintSupported) {
        return true;
      }

      return (
        metrics.largestContentfulPaint !== null &&
        metrics.lastLargestContentfulPaintAt !== null &&
        performance.now() - metrics.lastLargestContentfulPaintAt >=
          quietWindowMs
      );
    },
    largestContentfulPaintQuietWindowMs,
    { timeout: initialLoadMetricTimeout },
  );
}

function urlForRun(url: string, run: number) {
  const targetUrl = new URL(url);
  targetUrl.searchParams.set('performanceRun', String(run));
  return targetUrl.toString();
}

function requireMetric(
  value: number | null,
  metricName: string,
  target: PerformanceTarget,
  run: number,
) {
  if (value === null) {
    throw new Error(
      `${metricName} was not reported for ${target.framework} on run ${run}.`,
    );
  }

  return value;
}
