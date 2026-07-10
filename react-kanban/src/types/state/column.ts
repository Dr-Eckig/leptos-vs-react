import type { Column, ColumnType } from "../serialize";

export function canColumnAcceptTaskFrom(
  column: Column,
  sourceColumnType: ColumnType,
): boolean {
  if (column.columnType === sourceColumnType) {
    return true;
  }

  return !isColumnWipLimitReached(column);
}

export function isColumnWipLimitReached(column: Column): boolean {
  return column.wipLimit !== null && column.tasks.length >= column.wipLimit;
}
