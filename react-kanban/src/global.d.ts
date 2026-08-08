declare module "../../shared/dom-mutation-observer.js";
declare module "../../shared/performance-measurement.js";

type KanbanPerformanceMetrics = {
  initSession: (framework: string, targetId: string) => void;
  startMeasurement: (board: string, action: string) => number | null;
  finishMeasurement: (id: number | null) => void;
  logFileContent: () => string;
  logFileName: () => string;
};

interface Window {
  KanbanPerformanceMetrics?: KanbanPerformanceMetrics;
}
