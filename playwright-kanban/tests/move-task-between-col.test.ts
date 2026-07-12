import { test, type Page, type TestInfo } from '@playwright/test';
import {
  boardScenariosWithTasks,
  moveTaskToColumnEnd,
  openBoard,
  performanceTargets,
  performanceTestTimeout,
  repeatLoggedPerformanceAction,
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
): Promise<void> {
  const action = 'task-move-between-columns';
  const resultFileName = `move-task-between-cols-on-${scenario.resultSlug}.json`;
  await repeatLoggedPerformanceAction(page, testInfo, target, {
    action,
    board: scenario.boardLabel,
    resultGroup: 'move-task-between-col',
    resultFileName,
    run: async () => {
      await openBoard(page, target, scenario);
      await moveTaskToColumnEnd(page, 'todo', 0, 'in_progress');
    },
  });
}
