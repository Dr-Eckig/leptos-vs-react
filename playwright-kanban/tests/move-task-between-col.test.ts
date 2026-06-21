import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  boardScenariosWithTasks,
  collectPerformanceLogEntries,
  moveTaskToColumnEnd,
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
      `${target.framework}: move one task between columns on ${scenario.title} repeatedly`,
      async ({ page }, testInfo) => {
        await moveOneTaskBetweenColumnsRepeatedly(
          page,
          testInfo,
          target,
          scenario,
        );
      },
    );
  }
}

async function moveOneTaskBetweenColumnsRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  scenario: BoardScenario,
) {
  const taskMoveBetweenColumnsLog = collectPerformanceLogEntries(page, target, {
    action: 'task-move-between-columns',
    board: scenario.boardLabel,
  });

  for (let i = 1; i <= runs; i++) {
    const previousEntryCount = taskMoveBetweenColumnsLog.entries.length;

    await openBoard(page, target, scenario);
    await moveTaskToColumnEnd(page, 'todo', 0, 'in_progress');
    await taskMoveBetweenColumnsLog.waitForNextEntry(previousEntryCount, i);
  }

  await writePerformanceResults(
    testInfo,
    target,
    'move-task-between-col',
    `move-task-between-cols-on-${scenario.resultSlug}.json`,
    taskMoveBetweenColumnsLog.entries,
  );

  expect(taskMoveBetweenColumnsLog.entries).toHaveLength(runs);
}
