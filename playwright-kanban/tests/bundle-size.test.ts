import { expect, test, type Browser, type Response, type TestInfo } from '@playwright/test';
import {
  performanceTargets,
  performanceTestTimeout,
  runs,
  writeBundleSizeResults,
  type BundleSizeResultEntry,
  type PerformanceTarget,
} from './util';

type BundleAssetType = 'script' | 'stylesheet' | 'wasm';

type BundleAsset = {
  response: Response;
  type: BundleAssetType;
};

type BundleSizes = {
  bundleSizeBytes: number;
  scriptSizeBytes: number;
  stylesheetSizeBytes: number;
  wasmSizeBytes: number;
};

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
): Promise<void> {
  const entries: Omit<BundleSizeResultEntry, 'browser'>[] = [];

  for (let run = 1; run <= runs; run++) {
    await test.step(`run ${run}`, async () => {
      const context = await browser.newContext();
      const page = await context.newPage();
      const bundleAssets = new Map<string, BundleAsset>();
      const targetOrigin = new URL(target.url).origin;

      page.on('response', (response) => {
        const type = bundleAssetType(response, targetOrigin);
        if (type) {
          bundleAssets.set(response.url(), { response, type });
        }
      });

      try {
        await page.goto(target.url, { waitUntil: 'networkidle' });
        await expect(page.getByTestId('sidebar-board-0')).toBeVisible();

        const bundleSizes = await measureBundleSizes(bundleAssets.values());

        expect(bundleSizes.bundleSizeBytes).toBeGreaterThan(0);
        entries.push({
          run,
          framework: target.framework,
          ...bundleSizes,
        });
      } finally {
        await context.close();
      }
    });
  }

  await writeBundleSizeResults(testInfo, target, entries);
  expect(entries).toHaveLength(runs);
}

function bundleAssetType(
  response: Response,
  targetOrigin: string,
): BundleAssetType | null {
  const url = new URL(response.url());

  if (url.origin !== targetOrigin || !response.ok()) {
    return null;
  }

  const resourceType = response.request().resourceType();
  const contentType = response.headers()['content-type']?.toLowerCase() ?? '';

  if (contentType.includes('application/wasm') || url.pathname.endsWith('.wasm')) {
    return 'wasm';
  }
  if (resourceType === 'stylesheet' || contentType.includes('text/css')) {
    return 'stylesheet';
  }
  if (resourceType === 'script' || contentType.includes('javascript')) {
    return 'script';
  }

  return null;
}

async function measureBundleSizes(
  assets: Iterable<BundleAsset>,
): Promise<BundleSizes> {
  const measuredAssets = await Promise.all(
    Array.from(assets, async ({ response, type }) => ({
      type,
      size: (await response.body()).byteLength,
    })),
  );

  const sizes: BundleSizes = {
    bundleSizeBytes: 0,
    scriptSizeBytes: 0,
    stylesheetSizeBytes: 0,
    wasmSizeBytes: 0,
  };

  for (const asset of measuredAssets) {
    sizes.bundleSizeBytes += asset.size;
    sizes[`${asset.type}SizeBytes`] += asset.size;
  }

  return sizes;
}
