import { test, type Page, type TestInfo } from '@playwright/test';
import {
  boardScenariosWithTasks,
  moveTaskBeforeTask,
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
): Promise<void> {
  const action = 'task-move-within-column';
  const resultFileName = `move-task-within-col-on-${scenario.resultSlug}.json`;
  await repeatLoggedPerformanceAction(page, testInfo, target, {
    action,
    board: scenario.boardLabel,
    resultGroup: 'move-task-within-col',
    resultFileName,
    run: async () => {
      await openBoard(page, target, scenario);
      await moveTaskBeforeTask(page, 'todo', 1, 'todo', 0);
    },
  });
}
