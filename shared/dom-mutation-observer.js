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

  function startMeasurement() {
    const currentObserver = ensureObserver();

    if (!currentObserver) {
      return null;
    }

    currentObserver.takeRecords();

    activeMeasurement = {
      id: nextMeasurementId,
      records: [],
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

    activeMeasurement = null;

    return summary;
  }

  function summarizeRecords(records) {
    const relevantRecords = records.filter(
      (record) =>
        record.type !== "attributes" ||
        record.attributeName !== "data-testid",
    );

    let textChanges = 0;
    let attributeChanges = 0;
    let addedElements = 0;
    let removedElements = 0;
    for (const record of relevantRecords) {
      if (record.type === "childList") {
        for (const node of record.addedNodes) {
          addedElements += countElementNodes(node);
        }

        for (const node of record.removedNodes) {
          removedElements += countElementNodes(node);
        }
      } else if (record.type === "attributes") {
        attributeChanges += 1;
      } else if (record.type === "characterData") {
        textChanges += 1;
      }
    }

    return {
      mutationRecords: relevantRecords.length,
      textChanges,
      attributeChanges,
      addedElements,
      removedElements,
    };
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
      mutationRecords: 0,
      textChanges: 0,
      attributeChanges: 0,
      addedElements: 0,
      removedElements: 0,
    };
  }

  window[GLOBAL_NAME] = {
    startMeasurement,
    finishMeasurement,
  };
})();
