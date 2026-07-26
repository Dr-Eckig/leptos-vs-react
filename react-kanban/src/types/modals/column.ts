import { useState } from "react";
import type { Column } from "../serialize";
import type { UserColumn } from "../validation";

export type OpenColumnModal = {
  column: Column;
};

export function openColumnModalWithColumn(column: Column): OpenColumnModal {
  return { column };
}

export function useColumnForm(
  column: Column | null,
  modalData: OpenColumnModal | null,
) {
  const [formModalData, setFormModalData] = useState(modalData);
  const [wipLimit, setWipLimit] = useState(column?.wipLimit?.toString() ?? "");
  const [limitError, setLimitError] = useState<string>();

  if (modalData !== formModalData) {
    setFormModalData(modalData);
    setWipLimit(column?.wipLimit?.toString() ?? "");
    setLimitError(undefined);
  }

  const userColumn = (currentColumn: Column): UserColumn => ({
    columnType: currentColumn.columnType,
    wipLimit,
  });
  const clearError = () => setLimitError(undefined);
  const setValidationError = () => {
    setLimitError("Please enter a valid number.");
  };

  return {
    wipLimit,
    setWipLimit,
    limitError,
    userColumn,
    clearError,
    setValidationError,
  };
}

export type ColumnForm = ReturnType<typeof useColumnForm>;
