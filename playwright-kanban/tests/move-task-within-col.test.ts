import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  boardScenariosWithTasks,
  collectPerformanceLogEntries,
  moveTaskBeforeTask,
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
      `${target.framework}: move one task within a column on ${scenario.title} repeatedly`,
      async ({ page }, testInfo) => {
        await moveOneTaskWithinColumnRepeatedly(page, testInfo, target, scenario);
      },
    );
  }
}

async function moveOneTaskWithinColumnRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  scenario: BoardScenario,
) {
  const taskMoveWithinColumnLog = collectPerformanceLogEntries(page, target, {
    action: 'task-move-within-column',
    board: scenario.boardLabel,
  });

  for (let i = 1; i <= runs; i++) {
    const previousEntryCount = taskMoveWithinColumnLog.entries.length;

    await openBoard(page, target, scenario);
    await moveTaskBeforeTask(page, 'todo', 1, 'todo', 0);
    await taskMoveWithinColumnLog.waitForNextEntry(previousEntryCount, i);
  }

  await writePerformanceResults(
    testInfo,
    target,
    'move-task-within-col',
    `move-task-within-col-on-${scenario.resultSlug}.json`,
    taskMoveWithinColumnLog.entries,
  );

  expect(taskMoveWithinColumnLog.entries).toHaveLength(runs);
}
