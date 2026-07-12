import { expect, test, type Browser, type Response, type TestInfo } from '@playwright/test';
import {
  performanceTargets,
  performanceTestTimeout,
  runs,
  writeBundleSizeResults,
  type BundleSizeResultEntry,
  type PerformanceTarget,
} from './util';

test.setTimeout(performanceTestTimeout);

for (const target of performanceTargets) {
  test(
    `${target.framework}: measure bundle size repeatedly`,
    async ({ browser }, testInfo) => {
      await measureBundleSizeRepeatedly(browser, testInfo, target);
    },
  );
}

async function measureBundleSizeRepeatedly(
  browser: Browser,
  testInfo: TestInfo,
  target: PerformanceTarget,
) {
  const entries: Omit<BundleSizeResultEntry, 'browser'>[] = [];

  for (let run = 1; run <= runs; run++) {
    await test.step(`run ${run}`, async () => {
      const context = await browser.newContext();
      const page = await context.newPage();
      const assetResponses = new Map<string, Response>();
      const targetOrigin = new URL(target.url).origin;

      page.on('response', (response) => {
        if (isBundleAsset(response, targetOrigin)) {
          assetResponses.set(response.url(), response);
        }
      });

      try {
        await page.goto(target.url, { waitUntil: 'networkidle' });
        await expect(page.getByTestId('sidebar-board-0')).toBeVisible();

        const bundleSizeBytes = await sumResponseBodySizes(
          assetResponses.values(),
        );

        expect(bundleSizeBytes).toBeGreaterThan(0);
        entries.push({
          run,
          framework: target.framework,
          bundleSizeBytes,
        });
      } finally {
        await context.close();
      }
    });
  }

  await writeBundleSizeResults(testInfo, target, entries);
  expect(entries).toHaveLength(runs);
}

function isBundleAsset(response: Response, targetOrigin: string) {
  const url = new URL(response.url());

  if (url.origin !== targetOrigin || !response.ok()) {
    return false;
  }

  const resourceType = response.request().resourceType();
  const contentType = response.headers()['content-type']?.toLowerCase() ?? '';

  return (
    resourceType === 'script' ||
    resourceType === 'stylesheet' ||
    contentType.includes('javascript') ||
    contentType.includes('text/css') ||
    contentType.includes('application/wasm') ||
    url.pathname.endsWith('.wasm')
  );
}

async function sumResponseBodySizes(responses: Iterable<Response>) {
  const bodies = await Promise.all(
    Array.from(responses, (response) => response.body()),
  );
  return bodies.reduce((total, body) => total + body.byteLength, 0);
}
