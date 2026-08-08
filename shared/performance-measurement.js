(function () {
  const GLOBAL_NAME = "KanbanPerformanceMetrics";

  if (typeof window === "undefined" || window[GLOBAL_NAME]) {
    return;
  }

  let nextMeasurementId = 1;
  let session = null;
  const measurements = new Map();

  function initSession(framework, targetId) {
    session = {
      framework,
      targetId,
      logPrefix: `[${targetId}-kanban-performance]`,
      fileName: createLogFileName(targetId),
      entries: [],
    };
    measurements.clear();
  }

  function startMeasurement(board, action) {
    if (!session || !window.performance) {
      return null;
    }

    const id = nextMeasurementId;
    nextMeasurementId += 1;

    const safeBoard = sanitizeLogSegment(board);
    const label = `${id} - ${safeBoard} - ${action}`;
    const startMark = `${session.targetId}-kanban:${id}:start`;
    const endMark = `${session.targetId}-kanban:${id}:end`;

    try {
      window.performance.mark(startMark);
    } catch {
      return null;
    }

    measurements.set(id, {
      id,
      session,
      label,
      board: safeBoard,
      action,
      startMark,
      endMark,
      domMutationMeasurementId:
        window.KanbanDomMutationMetrics?.startMeasurement() ?? null,
      finishing: false,
    });
    return id;
  }

  function finishMeasurement(id) {
    const measurement = measurements.get(id);
    if (!measurement || measurement.finishing) {
      return;
    }

    measurement.finishing = true;
    afterDomUpdate(() => completeMeasurement(measurement));
  }

  function completeMeasurement(measurement) {
    measurements.delete(measurement.id);

    let duration;
    try {
      window.performance.mark(measurement.endMark);
      duration = window.performance.measure(
        measurement.label,
        measurement.startMark,
        measurement.endMark,
      ).duration;
    } catch {
      window.KanbanDomMutationMetrics?.finishMeasurement(
        measurement.domMutationMeasurementId,
      );
      clearPerformanceEntries(measurement);
      return;
    }

    const performance = `${duration.toFixed(2)} ms`;
    const domMutations =
      window.KanbanDomMutationMetrics?.finishMeasurement(
        measurement.domMutationMeasurementId,
      ) ?? emptyDomMutationSummary();

    console.log(
      `${measurement.session.logPrefix} ${measurement.label} - ${performance} - ${domMutationConsoleSummary(domMutations)}`,
    );

    measurement.session.entries.push({
      id: `${measurement.session.logPrefix} ${measurement.id}`,
      framework: measurement.session.framework,
      board: measurement.board,
      action: measurement.action,
      performance,
      domMutations,
    });
    clearPerformanceEntries(measurement);
  }

  function afterDomUpdate(callback) {
    if (typeof MessageChannel === "undefined") {
      callback();
      return;
    }

    const channel = new MessageChannel();
    channel.port1.onmessage = () => {
      channel.port1.close();
      channel.port2.close();

      // The task runs after current microtasks. The layout read also includes
      // pending style and layout work without waiting for another frame.
      void document.documentElement.clientHeight;
      callback();
    };
    channel.port2.postMessage(undefined);
  }

  function clearPerformanceEntries(measurement) {
    try {
      window.performance.clearMarks(measurement.startMark);
    } catch {
      // Ignore unavailable or already cleared entries.
    }
    try {
      window.performance.clearMarks(measurement.endMark);
    } catch {
      // Ignore unavailable or already cleared entries.
    }
    try {
      window.performance.clearMeasures(measurement.label);
    } catch {
      // Ignore unavailable or already cleared entries.
    }
  }

  function logFileContent() {
    try {
      return JSON.stringify(session?.entries ?? [], null, 2);
    } catch {
      return "[]";
    }
  }

  function logFileName() {
    return session?.fileName ?? createLogFileName("kanban");
  }

  function createLogFileName(targetId) {
    const date = new Date();
    return [
      targetId,
      `${padDatePart(date.getFullYear(), 4)}-${padDatePart(date.getMonth() + 1)}-${padDatePart(date.getDate())}`,
      `${padDatePart(date.getHours())}.${padDatePart(date.getMinutes())}.${padDatePart(date.getSeconds())}.json`,
    ].join(" - ");
  }

  function padDatePart(value, length = 2) {
    return value.toString().padStart(length, "0");
  }

  function sanitizeLogSegment(value) {
    return value.replace(/[\n\r]/g, "_");
  }

  function emptyDomMutationSummary() {
    return {
      mutationRecords: 0,
      textChanges: 0,
      attributeChanges: 0,
      addedElements: 0,
      removedElements: 0,
    };
  }

  function domMutationConsoleSummary(domMutations) {
    return [
      "dom:",
      `records=${domMutations.mutationRecords}`,
      `text=${domMutations.textChanges}`,
      `attributes=${domMutations.attributeChanges}`,
      `added=${domMutations.addedElements}`,
      `removed=${domMutations.removedElements}`,
    ].join(" ");
  }

  window[GLOBAL_NAME] = {
    initSession,
    startMeasurement,
    finishMeasurement,
    logFileContent,
    logFileName,
  };
})();
