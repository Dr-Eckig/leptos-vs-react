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
    let textChanges = 0;
    let attributeChanges = 0;
    let addedElements = 0;
    let removedElements = 0;
    const affectedDomAreas = new Set();

    for (const record of records) {
      addAffectedDomArea(affectedDomAreas, record.target);

      if (record.type === "childList") {
        for (const node of record.addedNodes) {
          addedElements += countElementNodes(node);
          addAffectedDomArea(affectedDomAreas, node);
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
      mutationRecords: records.length,
      textChanges,
      attributeChanges,
      addedElements,
      removedElements,
      affectedDomAreas: Array.from(affectedDomAreas).sort(),
    };
  }

  function addAffectedDomArea(affectedDomAreas, node) {
    const element = elementFromNode(node);

    if (!element) {
      return;
    }

    affectedDomAreas.add(describeDomArea(element));
  }

  function elementFromNode(node) {
    if (!node) {
      return null;
    }

    if (node.nodeType === Node.ELEMENT_NODE) {
      return node;
    }

    return node.parentElement || null;
  }

  function describeDomArea(element) {
    const testArea = element.closest("[data-testid]");

    if (testArea) {
      return `[data-testid="${testArea.getAttribute("data-testid")}"]`;
    }

    if (element.id) {
      return `#${element.id}`;
    }

    if (element.classList.length > 0) {
      return `${element.tagName.toLowerCase()}.${Array.from(element.classList).join(".")}`;
    }

    return element.tagName.toLowerCase();
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
      affectedDomAreas: [],
    };
  }

  window[GLOBAL_NAME] = {
    startMeasurement,
    finishMeasurement,
  };
})();
