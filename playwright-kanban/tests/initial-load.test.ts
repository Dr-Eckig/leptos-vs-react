import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  addJsHeapToLatestEntry,
  createPerformanceResultEntry,
  performanceTargets,
  performanceTestTimeout,
  runs,
  shouldMeasureJsHeap,
  writePerformanceResults,
  type PerformanceResultEntry,
  type PerformanceTarget,
} from './util';

const initialLoadBoardLabel = 'Initial Load';
const initialLoadSettleTimeMs = 1_000;

type InitialLoadMetrics = {
  firstContentfulPaint: number | null;
  largestContentfulPaint: number | null;
};

test.setTimeout(performanceTestTimeout);

for (const target of performanceTargets) {
  test(`${target.framework}: measure initial load repeatedly`, async ({ page }, testInfo) => {
    await measureInitialLoadRepeatedly(page, testInfo, target);
  });
}

async function measureInitialLoadRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
) {
  await installInitialLoadObservers(page);

  const firstContentfulPaintEntries: PerformanceResultEntry[] = [];
  const largestContentfulPaintEntries: PerformanceResultEntry[] = [];
  const shouldMeasureHeap = shouldMeasureJsHeap(testInfo);

  for (let i = 1; i <= runs; i++) {
    const metrics = await measureInitialLoad(page, target, i);

    firstContentfulPaintEntries.push(
      createPerformanceResultEntry(
        target,
        i,
        'initial-load-fcp',
        initialLoadBoardLabel,
        requireMetric(metrics.firstContentfulPaint, 'FCP', target, i),
      ),
    );

    largestContentfulPaintEntries.push(
      createPerformanceResultEntry(
        target,
        i,
        'initial-load-lcp',
        initialLoadBoardLabel,
        requireMetric(metrics.largestContentfulPaint, 'LCP', target, i),
      ),
    );

    if (shouldMeasureHeap) {
      await addJsHeapToLatestEntry(page, firstContentfulPaintEntries, i);
    }
  }

  await writePerformanceResults(
    testInfo,
    target,
    'initial-load',
    'initial-load-fcp.json',
    firstContentfulPaintEntries,
  );
  await writePerformanceResults(
    testInfo,
    target,
    'initial-load',
    'initial-load-lcp.json',
    largestContentfulPaintEntries,
  );

  expect(firstContentfulPaintEntries).toHaveLength(runs);
  expect(largestContentfulPaintEntries).toHaveLength(runs);
}

async function installInitialLoadObservers(page: Page) {
  await page.addInitScript(() => {
    const metricWindow = window as Window & {
      __kanbanInitialLoadMetrics?: InitialLoadMetrics;
    };

    metricWindow.__kanbanInitialLoadMetrics = {
      firstContentfulPaint: null,
      largestContentfulPaint: null,
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
  await page.goto(urlForRun(target.url, run), { waitUntil: 'load' });
  await page.waitForTimeout(initialLoadSettleTimeMs);

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
    };
  });
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
