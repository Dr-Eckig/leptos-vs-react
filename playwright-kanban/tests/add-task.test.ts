import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  addTaskToColumn,
  boardScenarios,
  addJsHeapToLatestEntry,
  collectPerformanceLogEntries,
  openBoard,
  performanceTargets,
  performanceTestTimeout,
  runs,
  shouldMeasureJsHeap,
  writePerformanceResults,
  type BoardScenario,
  type PerformanceTarget,
} from './util';

test.setTimeout(performanceTestTimeout);

for (const framework of performanceTargets) {
  for (const scenario of boardScenarios) {
    test(
      `${framework.framework}: add one task to ${scenario.title} repeatedly`,
      async ({ page }, testInfo) => {
        await addOneTaskToBoardRepeatedly(page, testInfo, framework, scenario);
      },
    );
  }
}

async function addOneTaskToBoardRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  scenario: BoardScenario,
) {
  const action = 'task-create';
  const resultFileName = `add-task-to-${scenario.resultSlug}.json`;
  const taskCreateLog = collectPerformanceLogEntries(page, target, {
    action,
    board: scenario.boardLabel,
  });
  const shouldMeasureHeap = shouldMeasureJsHeap(testInfo);

  for (let i = 1; i <= runs; i++) {
    const previousEntryCount = taskCreateLog.entries.length;

    await openBoard(page, target, scenario);
    await addTaskToColumn(page, 'todo', `Example Task ${i}`);
    await taskCreateLog.waitForNextEntry(previousEntryCount, i);

    if (shouldMeasureHeap) {
      await addJsHeapToLatestEntry(page, taskCreateLog.entries, i);
    }
  }

  await writePerformanceResults(
    testInfo,
    target,
    'add-task',
    resultFileName,
    taskCreateLog.entries,
  );

  expect(taskCreateLog.entries).toHaveLength(runs);
}
