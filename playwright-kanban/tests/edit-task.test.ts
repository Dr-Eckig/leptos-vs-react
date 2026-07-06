import { test, type Page, type TestInfo } from '@playwright/test';
import {
  boardScenariosWithTasks,
  editTaskTitle,
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
  const action = 'task-edit';
  const resultFileName = `edit-task-on-${scenario.resultSlug}.json`;
  await repeatLoggedPerformanceAction(page, testInfo, target, {
    action,
    board: scenario.boardLabel,
    resultGroup: 'edit-task',
    resultFileName,
    run: async (run) => {
      await openBoard(page, target, scenario);
      await editTaskTitle(page, 'todo', 0, `Edited Task ${run}`);
    },
  });
}
