import { expect, test, type Page, type TestInfo } from '@playwright/test';
import {
  addTaskToColumn,
  boardScenarios,
  boardScenariosWithTasks,
  boardSwitchScenarios,
  collectLoggedDomMutationAction,
  deleteTask,
  editTaskTitle,
  moveTaskBeforeTask,
  moveTaskToColumnEnd,
  openBoard,
  performanceTargets,
  performanceTestTimeout,
  writeDomMutationResults,
  type BoardScenario,
  type BoardSwitchScenario,
  type DomMutationResultEntry,
  type PerformanceTarget,
} from './util';

type DomMutationScenario = {
  title: string;
  action: string;
  boardLabel: string;
  run: (page: Page, target: PerformanceTarget) => Promise<void>;
};

test.setTimeout(performanceTestTimeout);
test.skip(
  ({ browserName }) => browserName !== 'chromium',
  'DOM mutation measurements are collected only in Chromium.',
);

for (const target of performanceTargets) {
  test(`${target.framework}: collect DOM mutations once per scenario`, async ({
    page,
  }, testInfo) => {
    await collectDomMutationsOncePerScenario(page, testInfo, target);
  });
}

async function collectDomMutationsOncePerScenario(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
) {
  const entries: DomMutationResultEntry[] = [];

  for (const scenario of domMutationScenarios()) {
    await test.step(scenario.title, async () => {
      entries.push(
        await collectLoggedDomMutationAction(page, testInfo, target, {
          action: scenario.action,
          board: scenario.boardLabel,
          scenario: scenario.title,
          run: () => scenario.run(page, target),
        }),
      );
    });
  }

  await writeDomMutationResults(testInfo, target, entries);
  expect(entries).toHaveLength(domMutationScenarios().length);
}

function domMutationScenarios(): DomMutationScenario[] {
  return [
    ...boardScenarios.map(addTaskScenario),
    ...boardScenariosWithTasks.map(editTaskScenario),
    ...boardScenariosWithTasks.map(deleteTaskScenario),
    ...boardScenariosWithTasks.map(moveTaskWithinColumnScenario),
    ...boardScenariosWithTasks.map(moveTaskBetweenColumnsScenario),
    ...boardSwitchScenarios.map(boardSwitchScenario),
  ];
}

function addTaskScenario(scenario: BoardScenario): DomMutationScenario {
  return {
    title: `Aufgabe erstellen | ${scenario.boardLabel}`,
    action: 'task-create',
    boardLabel: scenario.boardLabel,
    run: async (page, target) => {
      await openBoard(page, target, scenario);
      await addTaskToColumn(page, 'todo', 'DOM Mutation Task');
    },
  };
}

function editTaskScenario(scenario: BoardScenario): DomMutationScenario {
  return {
    title: `Aufgabe bearbeiten | ${scenario.boardLabel}`,
    action: 'task-edit',
    boardLabel: scenario.boardLabel,
    run: async (page, target) => {
      await openBoard(page, target, scenario);
      await editTaskTitle(page, 'todo', 0, 'DOM Mutation Edited Task');
    },
  };
}

function deleteTaskScenario(scenario: BoardScenario): DomMutationScenario {
  return {
    title: `Aufgabe löschen | ${scenario.boardLabel}`,
    action: 'task-delete',
    boardLabel: scenario.boardLabel,
    run: async (page, target) => {
      await openBoard(page, target, scenario);
      await deleteTask(page, 'todo', 0);
    },
  };
}

function moveTaskWithinColumnScenario(
  scenario: BoardScenario,
): DomMutationScenario {
  return {
    title: `Aufgabe innerhalb einer Spalte verschieben | ${scenario.boardLabel}`,
    action: 'task-move-within-column',
    boardLabel: scenario.boardLabel,
    run: async (page, target) => {
      await openBoard(page, target, scenario);
      await moveTaskBeforeTask(page, 'todo', 1, 'todo', 0);
    },
  };
}

function moveTaskBetweenColumnsScenario(
  scenario: BoardScenario,
): DomMutationScenario {
  return {
    title: `Aufgabe zwischen Spalten verschieben | ${scenario.boardLabel}`,
    action: 'task-move-between-columns',
    boardLabel: scenario.boardLabel,
    run: async (page, target) => {
      await openBoard(page, target, scenario);
      await moveTaskToColumnEnd(page, 'todo', 0, 'in_progress');
    },
  };
}

function boardSwitchScenario(
  scenario: BoardSwitchScenario,
): DomMutationScenario {
  return {
    title: `Board wechseln | ${scenario.boardLabel}`,
    action: 'board-switch',
    boardLabel: scenario.boardLabel,
    run: async (page, target) => {
      await page.goto(target.url);

      if (scenario.fromBoardTestId) {
        await page.getByTestId(scenario.fromBoardTestId).click();
        await expect(page.getByTestId('todo-task-dropdown-0')).toBeVisible();
      }

      await page.getByTestId(scenario.boardTestId).click();
    },
  };
}
