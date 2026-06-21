import { ColumnType } from "../serialize";
import { createId } from "../utility";
import type { Task } from "./task";

export type ColumnId = string;

export type Column = {
  id: ColumnId;
  columnType: ColumnType;
  tasks: Task[];
  wipLimit: number | null;
};

export const columnTypes: ColumnType[] = [
  ColumnType.Todo,
  ColumnType.InProgress,
  ColumnType.Done,
];

export const columnDisplayNames: Record<ColumnType, string> = {
  [ColumnType.Todo]: "To Do",
  [ColumnType.InProgress]: "In Progress",
  [ColumnType.Done]: "Done",
};

export function createColumn(
  columnType: ColumnType,
  wipLimit: number | null,
): Column {
  return {
    id: createId(),
    columnType,
    tasks: [],
    wipLimit,
  };
}

export function createDefaultColumns(): Column[] {
  return [
    {
      id: createId(),
      columnType: ColumnType.Todo,
      tasks: [],
      wipLimit: null,
    },
    {
      id: createId(),
      columnType: ColumnType.InProgress,
      tasks: [],
      wipLimit: null,
    },
    {
      id: createId(),
      columnType: ColumnType.Done,
      tasks: [],
      wipLimit: null,
    },
  ];
}

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
