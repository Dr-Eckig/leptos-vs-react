import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  addJsHeapToLatestEntry,
  boardSwitchScenarios,
  collectPerformanceLogEntries,
  performanceTargets,
  performanceTestTimeout,
  runs,
  shouldMeasureJsHeap,
  writePerformanceResults,
  type BoardSwitchScenario,
  type PerformanceTarget,
} from './util';

test.setTimeout(performanceTestTimeout);

for (const target of performanceTargets) {
  for (const scenario of boardSwitchScenarios) {
    test(`${target.framework}: ${scenario.title}`, async ({ page }, testInfo) => {
      await switchToBoardRepeatedly(page, testInfo, target, scenario);
    });
  }
}

async function switchToBoardRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  scenario: BoardSwitchScenario,
) {
  const action = 'board-switch';
  const resultFileName = `board-switch-to-${scenario.resultSlug}.json`;
  const boardSwitchLog = collectPerformanceLogEntries(page, target, {
    action,
    board: scenario.boardLabel,
  });
  const shouldMeasureHeap = shouldMeasureJsHeap(testInfo);

  for (let i = 1; i <= runs; i++) {
    const previousEntryCount = boardSwitchLog.entries.length;

    await page.goto(target.url);

    if (scenario.fromBoardTestId) {
      await page.getByTestId(scenario.fromBoardTestId).click();
      await expect(page.getByTestId('todo-task-dropdown-0')).toBeVisible();
    }

    await page.getByTestId(scenario.boardTestId).click();
    await boardSwitchLog.waitForNextEntry(previousEntryCount, i);

    if (shouldMeasureHeap) {
      await addJsHeapToLatestEntry(page, boardSwitchLog.entries, i);
    }
  }

  await writePerformanceResults(
    testInfo,
    target,
    'board-switch',
    resultFileName,
    boardSwitchLog.entries,
  );

  expect(boardSwitchLog.entries).toHaveLength(runs);
}
