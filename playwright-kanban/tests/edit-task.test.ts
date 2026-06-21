import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  boardScenariosWithTasks,
  collectPerformanceLogEntries,
  editTaskTitle,
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
  for (const scenario of boardScenariosWithTasks) {
    test(
      `${target.framework}: edit one task on ${scenario.title} repeatedly`,
      async ({ page }, testInfo) => {
        await editOneTaskOnBoardRepeatedly(page, testInfo, target, scenario);
      },
    );
  }
}

async function editOneTaskOnBoardRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  scenario: BoardScenario,
) {
  const taskEditLog = collectPerformanceLogEntries(page, target, {
    action: 'task-edit',
    board: scenario.boardLabel,
  });

  for (let i = 1; i <= runs; i++) {
    const previousEntryCount = taskEditLog.entries.length;

    await openBoard(page, target, scenario);
    await editTaskTitle(page, 'todo', 0, `Edited Task ${i}`);
    await taskEditLog.waitForNextEntry(previousEntryCount, i);
  }

  await writePerformanceResults(
    testInfo,
    target,
    'edit-task',
    `edit-task-on-${scenario.resultSlug}.json`,
    taskEditLog.entries,
  );

  expect(taskEditLog.entries).toHaveLength(runs);
}
