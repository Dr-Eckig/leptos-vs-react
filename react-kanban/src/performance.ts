const LOG_PREFIX = "[react-kanban-performance]";

let nextMeasurementId = 1;
let currentPerformanceLogFileName: string | null = null;
let performanceLogEntries: PerformanceLogEntry[] = [];

export enum PerformanceAction {
  BoardSwitch = "board-switch",
  TaskCreate = "task-create",
  TaskEdit = "task-edit",
  TaskDelete = "task-delete",
  TaskMoveWithinColumn = "task-move-within-column",
  TaskMoveBetweenColumns = "task-move-between-columns",
}

export type PerformanceContext = {
  boardTitle: string;
};

type PerformanceLogEntry = {
  id: string;
  framework: string;
  board: string;
  action: string;
  performance: string;
  domMutations: DomMutationSummary;
};

type DomMutationSummary = {
  mutationRecords: number;
  textChanges: number;
  attributeChanges: number;
  addedElements: number;
  removedElements: number;
  affectedDomAreas: string[];
};

type DomMutationMetrics = {
  startMeasurement: () => number | null;
  finishMeasurement: (id: number | null) => DomMutationSummary;
};

declare global {
  interface Window {
    KanbanDomMutationMetrics?: DomMutationMetrics;
  }
}

export function performanceContextFromBoard(
  board: { title: string } | null | undefined,
): PerformanceContext {
  return {
    boardTitle: board?.title ?? "no-board",
  };
}

export type FinishPerformanceMeasurement = () => void;

export function start(
  action: PerformanceAction,
  context: PerformanceContext,
): FinishPerformanceMeasurement {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  const performanceApi = window.performance;

  if (!performanceApi) {
    return () => undefined;
  }

  const id = nextMeasurementId;
  nextMeasurementId += 1;

  const logId = `${LOG_PREFIX} ${id}`;
  const boardTitle = sanitizeLogSegment(context.boardTitle);
  const actionName = action.toString();
  const label = `${id} - ${boardTitle} - ${action}`;
  const startMark = `react-kanban:${id}:start`;
  const endMark = `react-kanban:${id}:end`;

  try {
    performanceApi.mark(startMark);
  } catch {
    return () => undefined;
  }

  const domMutationMeasurementId =
    window.KanbanDomMutationMetrics?.startMeasurement()
    ?? null;

  let isFinished = false;

  return () => {
    if (isFinished) {
      return;
    }

    isFinished = true;

    afterNextPaint(() => {
      let duration: number;

      try {
        performanceApi.mark(endMark);
        duration = performanceApi.measure(label, startMark, endMark).duration;
      } catch {
        window.KanbanDomMutationMetrics?.finishMeasurement(domMutationMeasurementId);
        clearPerformanceEntries(performanceApi, startMark, endMark, label);
        return;
      }

      const performance = `${duration.toFixed(2)} ms`;
      const domMutations =
        window.KanbanDomMutationMetrics?.finishMeasurement(domMutationMeasurementId)
        ?? emptyDomMutationSummary();

      console.log(
        `${LOG_PREFIX} ${label} - ${performance} - ${domMutationConsoleSummary(domMutations)}`,
      );

      appendPerformanceLog({
        id: logId,
        framework: "React",
        board: boardTitle,
        action: actionName,
        performance,
        domMutations,
      });

      clearPerformanceEntries(performanceApi, startMark, endMark, label);
    });
  };
}

function afterNextPaint(callback: () => void) {
  window.requestAnimationFrame(() => {
    const channel = new MessageChannel();

    channel.port1.onmessage = () => {
      callback();
    };

    channel.port2.postMessage(undefined);
  });
}

function clearPerformanceEntries(
  performanceApi: Performance,
  startMark: string,
  endMark: string,
  label: string,
) {
  try {
    performanceApi.clearMarks(startMark);
  } catch {
    // Ignore
  }

  try {
    performanceApi.clearMarks(endMark);
  } catch {
    // Ignore
  }

  try {
    performanceApi.clearMeasures(label);
  } catch {
    // Ignore
  }
}

function sanitizeLogSegment(value: string): string {
  return value.replace(/[\n\r]/g, "_");
}

function emptyDomMutationSummary(): DomMutationSummary {
  return {
    mutationRecords: 0,
    textChanges: 0,
    attributeChanges: 0,
    addedElements: 0,
    removedElements: 0,
    affectedDomAreas: [],
  };
}

function domMutationConsoleSummary(domMutations: DomMutationSummary): string {
  return [
    "dom:",
    `records=${domMutations.mutationRecords}`,
    `text=${domMutations.textChanges}`,
    `attributes=${domMutations.attributeChanges}`,
    `added=${domMutations.addedElements}`,
    `removed=${domMutations.removedElements}`,
    `areas=${encodeURIComponent(domMutations.affectedDomAreas.join("|"))}`,
  ].join(" ");
}

export function initPerformanceLogSession() {
  currentPerformanceLogFileName = createPerformanceLogFileName();
  performanceLogEntries = [];
}

function createPerformanceLogFileName(): string {
  const date = new Date();

  return [
    `react`,
    `${padDatePart(date.getFullYear(), 4)}-${padDatePart(date.getMonth() + 1)}-${padDatePart(date.getDate())}`,
    `${padDatePart(date.getHours())}.${padDatePart(date.getMinutes())}.${padDatePart(date.getSeconds())}.json`,
  ].join(" - ");
}

function padDatePart(value: number, length = 2): string {
  return value.toString().padStart(length, "0");
}

function appendPerformanceLog(entry: PerformanceLogEntry) {
  performanceLogEntries.push(entry);
}

export function performanceLogFileContent(): string {
  try {
    return JSON.stringify(performanceLogEntries, null, 2);
  } catch {
    return "[]";
  }
}

export function performanceLogFileName(): string {
  return currentPerformanceLogFileName ?? createPerformanceLogFileName();
}
