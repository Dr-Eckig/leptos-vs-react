import { expect, test, type Browser, type Response, type TestInfo } from '@playwright/test';
import {
  performanceTargets,
  performanceTestTimeout,
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
    `${target.framework}: measure bundle size`,
    async ({ browser }, testInfo) => {
      await measureBundleSize(browser, testInfo, target);
    },
  );
}

async function measureBundleSize(
  browser: Browser,
  testInfo: TestInfo,
  target: PerformanceTarget,
): Promise<void> {
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

    const entry: Omit<BundleSizeResultEntry, 'browser'> = {
      run: 1,
      framework: target.framework,
      ...bundleSizes,
    };
    await writeBundleSizeResults(testInfo, target, [entry]);
  } finally {
    await context.close();
  }
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
