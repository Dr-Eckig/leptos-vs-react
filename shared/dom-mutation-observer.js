(function () {
  const GLOBAL_NAME = "KanbanDomMutationMetrics";

  if (typeof window === "undefined" || window[GLOBAL_NAME]) {
    return;
  }

  let nextMeasurementId = 1;
  let observer = null;
  let activeMeasurement = null;

  function ensureObserver() {
    if (observer || typeof MutationObserver === "undefined") {
      return observer;
    }

    observer = new MutationObserver((records) => {
      if (!activeMeasurement) {
        return;
      }

      activeMeasurement.records.push(...records);
    });

    observer.observe(document.body, {
      attributes: true,
      characterData: true,
      childList: true,
      subtree: true,
    });

    return observer;
  }

  function startMeasurement(action, board) {
    const currentObserver = ensureObserver();

    if (!currentObserver) {
      return null;
    }

    currentObserver.takeRecords();

    activeMeasurement = {
      id: nextMeasurementId,
      action,
      board,
      records: [],
      startedAt: performance.now(),
    };
    nextMeasurementId += 1;

    return activeMeasurement.id;
  }

  function finishMeasurement(id) {
    if (!activeMeasurement || activeMeasurement.id !== id || !observer) {
      return emptySummary();
    }

    activeMeasurement.records.push(...observer.takeRecords());

    const summary = summarizeRecords(activeMeasurement.records);
    summary.measurementId = activeMeasurement.id;
    summary.action = activeMeasurement.action;
    summary.board = activeMeasurement.board;
    summary.duration = `${(performance.now() - activeMeasurement.startedAt).toFixed(2)} ms`;

    activeMeasurement = null;

    return summary;
  }

  function summarizeRecords(records) {
    let childListMutations = 0;
    let attributeMutations = 0;
    let characterDataMutations = 0;
    let addedNodes = 0;
    let addedElementNodes = 0;
    let removedNodes = 0;
    let removedElementNodes = 0;
    const changedElements = new Set();

    for (const record of records) {
      if (record.type === "childList") {
        childListMutations += 1;

        for (const node of record.addedNodes) {
          addedNodes += countNodes(node);
          addedElementNodes += countElementNodes(node);
        }

        for (const node of record.removedNodes) {
          removedNodes += countNodes(node);
          removedElementNodes += countElementNodes(node);
        }
      } else if (record.type === "attributes") {
        attributeMutations += 1;
        addChangedElement(changedElements, record.target);
      } else if (record.type === "characterData") {
        characterDataMutations += 1;
        addChangedElement(changedElements, record.target.parentElement);
      }
    }

    const changedElementNodes = changedElements.size;

    return {
      mutationRecords: records.length,
      childListMutations,
      attributeMutations,
      characterDataMutations,
      addedNodes,
      addedElementNodes,
      removedNodes,
      removedElementNodes,
      changedElementNodes,
      rerenderedNodeEstimate:
        addedElementNodes + removedElementNodes + changedElementNodes,
    };
  }

  function addChangedElement(changedElements, node) {
    if (node && node.nodeType === Node.ELEMENT_NODE) {
      changedElements.add(node);
    }
  }

  function countNodes(node) {
    let count = 1;

    for (const child of node.childNodes) {
      count += countNodes(child);
    }

    return count;
  }

  function countElementNodes(node) {
    let count = node.nodeType === Node.ELEMENT_NODE ? 1 : 0;

    for (const child of node.childNodes) {
      count += countElementNodes(child);
    }

    return count;
  }

  function emptySummary() {
    return {
      measurementId: null,
      action: null,
      board: null,
      duration: "0.00 ms",
      mutationRecords: 0,
      childListMutations: 0,
      attributeMutations: 0,
      characterDataMutations: 0,
      addedNodes: 0,
      addedElementNodes: 0,
      removedNodes: 0,
      removedElementNodes: 0,
      changedElementNodes: 0,
      rerenderedNodeEstimate: 0,
    };
  }

  window[GLOBAL_NAME] = {
    startMeasurement,
    finishMeasurement,
  };
})();
