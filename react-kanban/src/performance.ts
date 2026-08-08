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

  const measurementId =
    window.KanbanPerformanceMetrics?.startMeasurement(
      context.boardTitle,
      action,
    ) ?? null;

  return () => {
    window.KanbanPerformanceMetrics?.finishMeasurement(measurementId);
  };
}

export function initPerformanceLogSession() {
  window.KanbanPerformanceMetrics?.initSession("React", "react");
}

export function performanceLogFileContent(): string {
  return window.KanbanPerformanceMetrics?.logFileContent() ?? "[]";
}

export function performanceLogFileName(): string {
  return window.KanbanPerformanceMetrics?.logFileName()
    ?? "react-performance.json";
}
