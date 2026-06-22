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
};

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

  const startTime = performanceApi.now();

  try {
    performanceApi.mark(startMark);
  } catch {
    return () => undefined;
  }

  let isFinished = false;

  return () => {
    if (isFinished) {
      return;
    }

    isFinished = true;

    afterNextPaint(() => {
      try {
        performanceApi.mark(endMark);
      } catch {
        // Ignore performance measurement errors
      }

      const duration = performanceApi.now() - startTime;
      const performance = `${duration.toFixed(2)} ms`;

      try {
        performanceApi.measure(label, startMark, endMark);
      } catch {
        // Ignore performance measurement errors
      }

      console.log(`${LOG_PREFIX} ${label} - ${performance}`);

      appendPerformanceLog({
        id: logId,
        framework: "React",
        board: boardTitle,
        action: actionName,
        performance,
      });

      clearPerformanceEntries(performanceApi, startMark, endMark, label);
    });
  };
}

function afterNextPaint(callback: () => void) {
  window.requestAnimationFrame(() => {
    window.setTimeout(() => {
      callback();
    }, 0);
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
