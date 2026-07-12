import { test, type Page, type TestInfo } from '@playwright/test';
import {
  addTaskToColumn,
  boardScenarios,
  openBoard,
  performanceTargets,
  performanceTestTimeout,
  repeatLoggedPerformanceAction,
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
): Promise<void> {
  const action = 'task-create';
  const resultFileName = `add-task-to-${scenario.resultSlug}.json`;
  await repeatLoggedPerformanceAction(page, testInfo, target, {
    action,
    board: scenario.boardLabel,
    resultGroup: 'add-task',
    resultFileName,
    run: async (run) => {
      await openBoard(page, target, scenario);
      await addTaskToColumn(page, 'todo', `Example Task ${run}`);
    },
  });
}
