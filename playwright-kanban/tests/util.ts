// npx playwright test 

import {
  expect,
  test,
  type ConsoleMessage,
  type Locator,
  type Page,
  type TestInfo,
} from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

export const resultsDir = path.resolve('../statistics-kanban/data');
export const domMutationResultsDir = path.resolve(
  '../statistics-kanban/dom-mutations-data',
);
export const runs = 50;
export const warmUpRuns = 5;
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
  warmUp: boolean;
  browser: string;
  framework: string;
  board: string;
  action: string;
  performance: string;
  domMutationRecords?: number;
  domTextChanges?: number;
  domAttributeChanges?: number;
  domAddedElements?: number;
  domRemovedElements?: number;
  domAffectedAreas?: string[];
};

type CollectedPerformanceLogEntry = Omit<PerformanceLogEntry, 'browser'>;
export type PerformanceResultEntry = CollectedPerformanceLogEntry;

type CollectPerformanceOptions = {
  action: string;
  board?: string;
};

type RepeatPerformanceActionOptions = CollectPerformanceOptions & {
  resultGroup: string;
  resultFileName: string;
  run: (run: number) => Promise<void>;
};

type CollectDomMutationActionOptions = CollectPerformanceOptions & {
  scenario: string;
  run: () => Promise<void>;
};

export type DomMutationResultEntry = {
  framework: string;
  board: string;
  action: string;
  scenario: string;
  mutationRecords: number;
  textChanges: number;
  attributeChanges: number;
  addedElements: number;
  removedElements: number;
  affectedDomAreas: string[];
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
      warmUp: isWarmUpRun(entries.length + 1),
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

export async function repeatLoggedPerformanceAction(
  page: Page,
  testInfo: TestInfo,
  target: PerformanceTarget,
  options: RepeatPerformanceActionOptions,
) {
  const performanceLog = collectPerformanceLogEntries(page, target, options);

  for (let run = 1; run <= runs; run++) {
    await test.step(`run ${run}`, async () => {
      const previousEntryCount = performanceLog.entries.length;

      await options.run(run);
      await performanceLog.waitForNextEntry(previousEntryCount, run);
    });
  }

  await writePerformanceResults(
    testInfo,
    target,
    options.resultGroup,
    options.resultFileName,
    performanceLog.entries,
  );

  expect(performanceLog.entries).toHaveLength(runs);
}

export async function collectLoggedDomMutationAction(
  page: Page,
  _testInfo: TestInfo,
  target: PerformanceTarget,
  options: CollectDomMutationActionOptions,
): Promise<DomMutationResultEntry> {
  const entries: CollectedPerformanceLogEntry[] = [];

  const onConsole = (message: ConsoleMessage) => {
    const entry = parsePerformanceLog(message.text());

    if (
      entry?.framework !== target.framework ||
      entry.action !== options.action ||
      (options.board && entry.board !== options.board) ||
      entry.domMutationRecords === undefined ||
      entry.domTextChanges === undefined ||
      entry.domAttributeChanges === undefined ||
      entry.domAddedElements === undefined ||
      entry.domRemovedElements === undefined ||
      entry.domAffectedAreas === undefined
    ) {
      return;
    }

    entries.push({
      ...entry,
      run: 1,
      warmUp: false,
    });
  };

  page.on('console', onConsole);

  try {
    await options.run();
    await expect
      .poll(() => entries.length, {
        message: `Expected DOM mutation log for ${target.framework} ${options.scenario}.`,
        timeout: performanceLogTimeout,
      })
      .toBe(1);
  } finally {
    page.off('console', onConsole);
  }

  const [entry] = entries;

  return {
    framework: entry.framework,
    board: entry.board,
    action: entry.action,
    scenario: options.scenario,
    mutationRecords: requireDomMetric(entry.domMutationRecords, 'mutationRecords'),
    textChanges: requireDomMetric(entry.domTextChanges, 'textChanges'),
    attributeChanges: requireDomMetric(
      entry.domAttributeChanges,
      'attributeChanges',
    ),
    addedElements: requireDomMetric(entry.domAddedElements, 'addedElements'),
    removedElements: requireDomMetric(entry.domRemovedElements, 'removedElements'),
    affectedDomAreas: entry.domAffectedAreas ?? [],
  };
}

export async function writeDomMutationResults(
  _testInfo: TestInfo,
  target: PerformanceTarget,
  entries: DomMutationResultEntry[],
) {
  const targetResultsDir = path.join(domMutationResultsDir, target.id);

  await mkdir(targetResultsDir, { recursive: true });
  await writeFile(
    path.join(targetResultsDir, 'dom-mutations.json'),
    JSON.stringify(entries, null, 2),
  );
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

export function createPerformanceResultEntry(
  target: PerformanceTarget,
  run: number,
  action: string,
  board: string,
  performanceMs: number,
): PerformanceResultEntry {
  if (!Number.isFinite(performanceMs)) {
    throw new Error(
      `Cannot write non-finite performance value for ${target.framework} ${action}: ${performanceMs}`,
    );
  }

  return {
    run,
    warmUp: isWarmUpRun(run),
    framework: target.framework,
    board,
    action,
    performance: `${roundToTwoDecimals(performanceMs)} ms`,
  };
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

function taskDraggableTestId(columnType: ColumnType, taskIndex: number) {
  return `${columnType}-task-draggable-${taskIndex}`;
}

function taskDropTargetTestId(columnType: ColumnType, taskIndex: number) {
  return `${columnType}-task-drop-target-${taskIndex}`;
}

function columnDropZoneTestId(columnType: ColumnType) {
  return `${columnType}-column-drop-zone`;
}

function taskDraggable(
  page: Page,
  columnType: ColumnType,
  taskIndex: number,
): Locator {
  return page.getByTestId(taskDraggableTestId(columnType, taskIndex));
}

function taskDropTarget(
  page: Page,
  columnType: ColumnType,
  taskIndex: number,
): Locator {
  return page.getByTestId(taskDropTargetTestId(columnType, taskIndex));
}

function columnDropZone(page: Page, columnType: ColumnType): Locator {
  return page.getByTestId(columnDropZoneTestId(columnType));
}

function parsePerformanceLog(
  text: string,
): Omit<CollectedPerformanceLogEntry, 'run' | 'warmUp'> | null {
  const match = text.match(
    /^\[(leptos|react)-kanban-performance\]\s+(\d+)\s+-\s+(.+)\s+-\s+([a-z-]+)\s+-\s+(\d+(?:\.\d+)?)\s+ms(?:\s+-\s+dom:\s+records=(\d+)\s+text=(\d+)\s+attributes=(\d+)\s+added=(\d+)\s+removed=(\d+)\s+areas=(.*))?$/,
  );

  if (!match) {
    return null;
  }

  const [
    ,
    targetId,
    _measurementId,
    board,
    action,
    performance,
    domMutationRecords,
    domTextChanges,
    domAttributeChanges,
    domAddedElements,
    domRemovedElements,
    domAffectedAreas,
  ] = match;
  const framework = targetId === 'leptos' ? 'Leptos' : 'React';

  return {
    framework,
    board,
    action,
    performance: `${performance} ms`,
    domMutationRecords: parseOptionalInteger(domMutationRecords),
    domTextChanges: parseOptionalInteger(domTextChanges),
    domAttributeChanges: parseOptionalInteger(domAttributeChanges),
    domAddedElements: parseOptionalInteger(domAddedElements),
    domRemovedElements: parseOptionalInteger(domRemovedElements),
    domAffectedAreas: parseOptionalDomAreas(domAffectedAreas),
  };
}

function parseOptionalInteger(value: string | undefined): number | undefined {
  return value === undefined ? undefined : Number.parseInt(value, 10);
}

function parseOptionalDomAreas(value: string | undefined): string[] | undefined {
  if (value === undefined) {
    return undefined;
  }

  const decodedValue = decodeURIComponent(value);

  if (!decodedValue) {
    return [];
  }

  return decodedValue.split('|').filter(Boolean);
}

function requireDomMetric(value: number | undefined, metric: string): number {
  if (value === undefined) {
    throw new Error(`Missing DOM mutation metric: ${metric}`);
  }

  return value;
}

function serializePerformanceLogEntry(
  entry: CollectedPerformanceLogEntry,
  browser: string,
): PerformanceLogEntry {
  const serializedEntry: PerformanceLogEntry = {
    run: entry.run,
    warmUp: entry.warmUp,
    browser,
    framework: entry.framework,
    board: entry.board,
    action: entry.action,
    performance: entry.performance,
    domMutationRecords: entry.domMutationRecords,
    domTextChanges: entry.domTextChanges,
    domAttributeChanges: entry.domAttributeChanges,
    domAddedElements: entry.domAddedElements,
    domRemovedElements: entry.domRemovedElements,
    domAffectedAreas: entry.domAffectedAreas,
  };

  return serializedEntry;
}

function browserNameFromTestInfo(testInfo: TestInfo) {
  return testInfo.project.name || testInfo.project.use.browserName || 'unknown';
}

function getRequestedPerformanceTargets() {
  const requestedTargets = new Set(
    (process.env.PERFORMANCE_TARGETS ?? 'react,leptos')
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

function roundToTwoDecimals(value: number) {
  return Math.round(value * 100) / 100;
}

function isWarmUpRun(run: number) {
  return run <= warmUpRuns;
}
