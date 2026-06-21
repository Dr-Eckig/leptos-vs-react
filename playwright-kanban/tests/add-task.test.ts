import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  addTaskToColumn,
  boardScenarios,
  collectPerformanceLogEntries,
  openBoard,
  performanceTargets,
  performanceTestTimeout,
  runs,
  writePerformanceResults,
  type BoardScenario,
  type PerformanceTarget,
} from './util';

test.setTimeout(performanceTestTimeout);

for (const target of performanceTargets) {
  for (const scenario of boardScenarios) {
    test(
      `${target.framework}: add one task to ${scenario.title} repeatedly`,
      async ({ page }, testInfo) => {
        await addOneTaskToBoardRepeatedly(page, testInfo, target, scenario);
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
  const taskCreateLog = collectPerformanceLogEntries(page, target, {
    action: 'task-create',
    board: scenario.boardLabel,
  });

  for (let i = 1; i <= runs; i++) {
    const previousEntryCount = taskCreateLog.entries.length;

    await openBoard(page, target, scenario);
    await addTaskToColumn(page, 'todo', `Example Task ${i}`);
    await taskCreateLog.waitForNextEntry(previousEntryCount, i);
  }

  await writePerformanceResults(
    testInfo,
    target,
    'add-task',
    `add-task-to-${scenario.resultSlug}.json`,
    taskCreateLog.entries,
  );

  expect(taskCreateLog.entries).toHaveLength(runs);
}
