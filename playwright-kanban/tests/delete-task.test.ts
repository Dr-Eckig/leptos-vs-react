import { test, type Page, type TestInfo } from '@playwright/test';
import {
  boardScenariosWithTasks,
  deleteTask,
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
): Promise<void> {
  const action = 'task-delete';
  const resultFileName = `delete-task-from-${scenario.resultSlug}.json`;
  await repeatLoggedPerformanceAction(page, testInfo, target, {
    action,
    board: scenario.boardLabel,
    resultGroup: 'delete-task',
    resultFileName,
    run: async () => {
      await openBoard(page, target, scenario);
      await deleteTask(page, 'todo', 0);
    },
  });
}
