import { createId } from "../utility";
import type { RawTask, Task } from "./task";

export type ColumnId = string;

export type Column = {
  id: ColumnId;
  columnType: ColumnType;
  tasks: Task[];
  wipLimit: number | null;
};

export enum ColumnType {
  Todo = "todo",
  InProgress = "in_progress",
  Done = "done",
}

export type RawColumn = {
  id?: ColumnId;
  columnType?: ColumnType;
  tasks?: RawTask[];
  wipLimit?: number | null;
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
    createColumn(ColumnType.Todo, null),
    createColumn(ColumnType.InProgress, null),
    createColumn(ColumnType.Done, null),
  ];
}
