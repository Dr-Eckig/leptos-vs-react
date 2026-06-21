import { useEffect, useState } from "react";
import {
  useBoardsActions,
  useBoardsState,
  useModalsActions,
  useModalsState,
} from "../../../hooks";
import {
  PerformanceAction,
  performanceContextFromBoard,
  start as startPerformanceMeasurement,
} from "../../../performance";
import { columnDisplayNames, type Column } from "../../../types/state";
import { validateColumn } from "../../../types/validation";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";

export function ColumnModal() {
  const modals = useModalsState();
  const column = modals.column?.column ?? null;
  const isOpen = modals.column !== null;

  return <ColumnModalForm column={column} isOpen={isOpen} />;
}

type ColumnModalFormProps = {
  column: Column | null;
  isOpen: boolean;
};

function ColumnModalForm({ column, isOpen }: ColumnModalFormProps) {
  const boards = useBoardsActions();
  const { currentBoard } = useBoardsState();
  const modalActions = useModalsActions();
  const [wipLimit, setWipLimit] = useState("");
  const [limitError, setLimitError] = useState<string | undefined>();

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setWipLimit(column?.wipLimit?.toString() ?? "");
    setLimitError(undefined);
  }, [column, isOpen]);

  const closeModal = () => {
    const finishMeasurement = startPerformanceMeasurement(
      PerformanceAction.ModalClose,
      performanceContextFromBoard(currentBoard),
    );
    modalActions.setColumn(null);
    finishMeasurement();
  };

  const saveColumn = () => {
    if (!column) {
      modalActions.setColumn(null);
      return;
    }

    const result = validateColumn({
      columnType: column.columnType,
      wipLimit,
    });

    if (!result.ok) {
      setLimitError("Please enter a valid number.");
      return;
    }

    const finishMeasurement = startPerformanceMeasurement(
      PerformanceAction.ColumnEdit,
      performanceContextFromBoard(currentBoard),
    );
    boards.updateColumnWipLimit(column.id, result.column.wipLimit);
    modalActions.setColumn(null);
    finishMeasurement();
  };

  return (
    <Modal
      title={`Edit Column: ${column ? columnDisplayNames[column.columnType] : ""}`}
      isOpen={isOpen}
      onClose={closeModal}
      onSave={saveColumn}
    >
      <Input
        label="WIP Limit"
        value={wipLimit}
        setValue={setWipLimit}
        inputType="number"
        min={0}
        errorMessage={limitError}
      />
    </Modal>
  );
}
