// Run tests: 
// npx playwright test 

// npx playwright test tests/add-task.test.ts
// npx playwright test tests/edit-task.test.ts
// npx playwright test tests/delete-task.test.ts

// npx playwright test tests/move-task-within-col.test.ts
// npx playwright test tests/move-task-between-col.test.ts
// npx playwright test tests/board-switch.test.ts

// npx playwright test --project=chromium
// npx playwright test --project=firefox
// npx playwright test --project=webkit

import { expect, type Locator, type Page, type TestInfo } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

export const resultsDir = path.resolve('results');
export const runs = 50;
export const performanceTestTimeout = 1_000_000;
const performanceLogTimeout = 30_000;

export type PerformanceTarget = {
  id: 'leptos' | 'react';
  framework: 'Leptos' | 'React';
  url: string;
};

export type ColumnType = 'todo' | 'in_progress' | 'done';

export type BoardScenario = {
  title: string;
  boardTestId: string;
  boardLabel: string;
  resultSlug: string;
};

export type BoardSwitchScenario = BoardScenario & {
  fromBoardTestId?: string;
};

export type PerformanceLogEntry = {
  run: number;
  browser: string;
  framework: string;
  board: string;
  action: string;
  performance: string;
};

type CollectedPerformanceLogEntry = Omit<PerformanceLogEntry, 'browser'>;

type CollectPerformanceOptions = {
  action: string;
  board?: string;
};

const allPerformanceTargets: PerformanceTarget[] = [
  {
    id: 'leptos',
    framework: 'Leptos',
    url: 'http://localhost:8080/',
  },
  {
    id: 'react',
    framework: 'React',
    url: 'http://localhost:4173/',
  },
];

export const performanceTargets = getRequestedPerformanceTargets();

export const boardScenarios: BoardScenario[] = [
  {
    title: 'an empty board',
    boardTestId: 'sidebar-board-0',
    boardLabel: 'Board 1 (Leer)',
    resultSlug: 'empty-board',
  },
  {
    title: 'a board with 10 tasks',
    boardTestId: 'sidebar-board-1',
    boardLabel: 'Board 2 (10 Tasks)',
    resultSlug: 'board-with-10-tasks',
  },
  {
    title: 'a board with 100 tasks',
    boardTestId: 'sidebar-board-2',
    boardLabel: 'Board 3 (100 Tasks)',
    resultSlug: 'board-with-100-tasks',
  },
  {
    title: 'a board with 1000 tasks',
    boardTestId: 'sidebar-board-3',
    boardLabel: 'Board 4 (1000 Tasks)',
    resultSlug: 'board-with-1000-tasks',
  },
];

export const boardScenariosWithTasks = boardScenarios.slice(1);

export const boardSwitchScenarios: BoardSwitchScenario[] = [
  {
    title: 'switch to an empty board repeatedly',
    boardTestId: 'sidebar-board-0',
    fromBoardTestId: 'sidebar-board-1',
    boardLabel: 'Board 1 (Leer)',
    resultSlug: 'empty-board',
  },
  {
    title: 'switch to a board with 10 tasks repeatedly',
    boardTestId: 'sidebar-board-1',
    boardLabel: 'Board 2 (10 Tasks)',
    resultSlug: 'board-with-10-tasks',
  },
  {
    title: 'switch to a board with 100 tasks repeatedly',
    boardTestId: 'sidebar-board-2',
    boardLabel: 'Board 3 (100 Tasks)',
    resultSlug: 'board-with-100-tasks',
  },
  {
    title: 'switch to a board with 1000 tasks repeatedly',
    boardTestId: 'sidebar-board-3',
    boardLabel: 'Board 4 (1000 Tasks)',
    resultSlug: 'board-with-1000-tasks',
  },
];

export function collectPerformanceLogEntries(
  page: Page,
  target: PerformanceTarget,
  options: CollectPerformanceOptions,
) {
  const entries: CollectedPerformanceLogEntry[] = [];

  page.on('console', (message) => {
    const entry = parsePerformanceLog(message.text());

    if (
      entry?.framework !== target.framework ||
      entry.action !== options.action ||
      (options.board && entry.board !== options.board)
    ) {
      return;
    }

    entries.push({
      ...entry,
      run: entries.length + 1,
    });
  });

  return {
    entries,
    waitForNextEntry: async (previousEntryCount: number, run: number) => {
      await expect
        .poll(() => entries.length, {
          message: `Expected ${options.action} performance log for run ${run}.`,
          timeout: performanceLogTimeout,
        })
        .toBe(previousEntryCount + 1);
    },
  };
}

export async function writePerformanceResults(
  testInfo: TestInfo,
  target: PerformanceTarget,
  resultGroup: string,
  resultFileName: string,
  entries: CollectedPerformanceLogEntry[],
) {
  const browser = browserNameFromTestInfo(testInfo);
  const targetResultsDir = path.join(
    resultsDir,
    target.id,
    browser,
    resultGroup,
  );
  const serializedEntries = entries.map((entry) =>
    serializePerformanceLogEntry(entry, browser),
  );

  await mkdir(targetResultsDir, { recursive: true });
  await writeFile(
    path.join(targetResultsDir, resultFileName),
    JSON.stringify(serializedEntries, null, 2),
  );
}

export async function openBoard(
  page: Page,
  target: PerformanceTarget,
  scenario: Pick<BoardScenario, 'boardTestId'>,
) {
  await page.goto(target.url);
  await page.getByTestId(scenario.boardTestId).click();
}

export async function addTaskToColumn(
  page: Page,
  columnType: ColumnType,
  taskTitle: string,
) {
  await page.getByTestId(`add-task-button-${columnType}`).click();
  await page.getByTestId('task-title-input').fill(taskTitle);
  await page.getByTestId(`save-button-${columnType}`).click();
}

export async function editTaskTitle(
  page: Page,
  columnType: ColumnType,
  taskIndex: number,
  taskTitle: string,
) {
  const dropdownTestId = taskDropdownTestId(columnType, taskIndex);

  await page.getByTestId(dropdownTestId).click();
  await page.getByTestId(`${dropdownTestId}-edit`).click();
  await page.getByTestId('task-title-input').fill(taskTitle);
  await page.getByTestId(`save-button-${columnType}`).click();
}

export async function deleteTask(
  page: Page,
  columnType: ColumnType,
  taskIndex: number,
) {
  const dropdownTestId = taskDropdownTestId(columnType, taskIndex);

  await page.getByTestId(dropdownTestId).click();
  await page.getByTestId(`${dropdownTestId}-delete`).click();
}

export async function moveTaskToColumnEnd(
  page: Page,
  fromColumnType: ColumnType,
  fromTaskIndex: number,
  toColumnType: ColumnType,
) {
  await taskDraggable(page, fromColumnType, fromTaskIndex).dragTo(
    columnDropZone(page, toColumnType),
  );
}

export async function moveTaskBeforeTask(
  page: Page,
  fromColumnType: ColumnType,
  fromTaskIndex: number,
  toColumnType: ColumnType,
  beforeTaskIndex: number,
) {
  await taskDraggable(page, fromColumnType, fromTaskIndex).dragTo(
    taskDropTarget(page, toColumnType, beforeTaskIndex),
  );
}

export function taskDropdownTestId(columnType: ColumnType, taskIndex: number) {
  return `${columnType}-task-dropdown-${taskIndex}`;
}

function taskDraggable(
  page: Page,
  columnType: ColumnType,
  taskIndex: number,
): Locator {
  return page
    .locator(
      `.kanban-draggable-item:has([data-testid="${taskDropdownTestId(
        columnType,
        taskIndex,
      )}"])`,
    )
    .first();
}

function taskDropTarget(
  page: Page,
  columnType: ColumnType,
  taskIndex: number,
): Locator {
  return page
    .locator(
      `.kanban-task-drop-target:has([data-testid="${taskDropdownTestId(
        columnType,
        taskIndex,
      )}"])`,
    )
    .first();
}

function columnDropZone(page: Page, columnType: ColumnType): Locator {
  return page
    .locator(`.column:has([data-testid="add-task-button-${columnType}"])`)
    .locator('.kanban-column-drop-zone')
    .first();
}

function parsePerformanceLog(
  text: string,
): Omit<CollectedPerformanceLogEntry, 'run'> | null {
  const match = text.match(
    /^\[(leptos|react)-kanban-performance\]\s+(\d+)\s+-\s+(.+)\s+-\s+([a-z-]+)\s+-\s+(\d+(?:\.\d+)?)\s+ms$/,
  );

  if (!match) {
    return null;
  }

  const [, targetId, _measurementId, board, action, performance] = match;
  const framework = targetId === 'leptos' ? 'Leptos' : 'React';

  return {
    framework,
    board,
    action,
    performance: `${performance} ms`,
  };
}

function serializePerformanceLogEntry(
  entry: CollectedPerformanceLogEntry,
  browser: string,
): PerformanceLogEntry {
  return {
    run: entry.run,
    browser,
    framework: entry.framework,
    board: entry.board,
    action: entry.action,
    performance: entry.performance,
  };
}

function browserNameFromTestInfo(testInfo: TestInfo) {
  return testInfo.project.name || testInfo.project.use.browserName || 'unknown';
}

function getRequestedPerformanceTargets() {
  const requestedTargets = new Set(
    ('react,leptos')
      .split(',')
      .map((target) => target.trim().toLowerCase())
      .filter(Boolean),
  );

  if (requestedTargets.has('all')) {
    requestedTargets.add('react');
    requestedTargets.add('leptos');
  }

  const selectedTargets = allPerformanceTargets.filter((target) =>
    requestedTargets.has(target.id),
  );

  return selectedTargets.length > 0 ? selectedTargets : allPerformanceTargets;
}
