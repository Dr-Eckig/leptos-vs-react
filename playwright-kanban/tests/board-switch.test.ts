import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  boardSwitchScenarios,
  performanceTargets,
  performanceTestTimeout,
  repeatLoggedPerformanceAction,
  type BoardSwitchScenario,
  type PerformanceTarget,
} from './util';

test.setTimeout(performanceTestTimeout);

for (const target of performanceTargets) {
  for (const scenario of boardSwitchScenarios) {
    test(`${target.framework}: ${scenario.title}`, async ({ page }, testInfo) => {
      await switchToBoardRepeatedly(page, testInfo, target, scenario);
    });
  }
}

async function switchToBoardRepeatedly(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  scenario: BoardSwitchScenario,
) {
  const action = 'board-switch';
  const resultFileName = `board-switch-to-${scenario.resultSlug}.json`;
  await repeatLoggedPerformanceAction(page, testInfo, target, {
    action,
    board: scenario.boardLabel,
    resultGroup: 'board-switch',
    resultFileName,
    run: async () => {
      await page.goto(target.url);

      if (scenario.fromBoardTestId) {
        await page.getByTestId(scenario.fromBoardTestId).click();
        await expect(page.getByTestId('todo-task-dropdown-0')).toBeVisible();
      }

      await page.getByTestId(scenario.boardTestId).click();
    },
  });
}
