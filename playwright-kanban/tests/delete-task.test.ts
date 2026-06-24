import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  addJsHeapToLatestEntry,
  boardScenariosWithTasks,
  collectPerformanceLogEntries,
  deleteTask,
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

for (const target of performanceTargets) {
  for (const scenario of boardScenariosWithTasks) {
    test(
      `${target.framework}: delete one task from ${scenario.title} repeatedly`,
      async ({ page }, testInfo) => {
        await deleteOneTaskFromBoardRepeatedly(page, testInfo, target, scenario);
      },
    );
  }
}

async function deleteOneTaskFromBoardRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  scenario: BoardScenario,
) {
  const action = 'task-delete';
  const resultFileName = `delete-task-from-${scenario.resultSlug}.json`;
  const taskDeleteLog = collectPerformanceLogEntries(page, target, {
    action,
    board: scenario.boardLabel,
  });
  const shouldMeasureHeap = shouldMeasureJsHeap(testInfo);

  for (let i = 1; i <= runs; i++) {
    const previousEntryCount = taskDeleteLog.entries.length;

    await openBoard(page, target, scenario);
    await deleteTask(page, 'todo', 0);
    await taskDeleteLog.waitForNextEntry(previousEntryCount, i);

    if (shouldMeasureHeap) {
      await addJsHeapToLatestEntry(page, taskDeleteLog.entries, i);
    }
  }

  await writePerformanceResults(
    testInfo,
    target,
    'delete-task',
    resultFileName,
    taskDeleteLog.entries,
  );

  expect(taskDeleteLog.entries).toHaveLength(runs);
}
