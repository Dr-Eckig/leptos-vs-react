import { createDefaultColumns, type AllBoards, type Board, type BoardId, type Column, type ColumnId, type Priority, type Task, type TaskId } from "./state";
import { parseDateFromString } from "./date";
import { createId } from "./utility";
import type { Temporal } from "@js-temporal/polyfill";

export enum ColumnType {
  Todo = "todo",
  InProgress = "in_progress",
  Done = "done",
}

export type RawAllBoards = {
  boards?: RawBoard[];
  currentBoardId?: BoardId | null;
};

type RawBoard = {
  id?: BoardId;
  title: string;
  columns?: RawColumn[];
};

type RawColumn = {
  id?: ColumnId;
  columnType?: ColumnType;
  tasks?: RawTask[];
  wipLimit?: number | null;
};

type RawTask = {
  id?: TaskId;
  title: string;
  description?: string | null;
  dueDate?: string | null;
  priority: Priority;
};

export function deserializeAllBoards(raw: RawAllBoards): AllBoards {
  const boards: Board[] = (raw.boards ?? []).map(deserializeBoard);
  const currentBoardId = raw.currentBoardId;
  const validCurrentBoardId =
    currentBoardId && boards.some((board) => board.id === currentBoardId)
      ? currentBoardId
      : boards[0]?.id ?? null;

  return {
    boards,
    currentBoardId: validCurrentBoardId,
  };
}

function deserializeBoard(raw: RawBoard): Board {
  return {
    id: raw.id ?? createId(),
    title: raw.title,
    columns: raw.columns
      ? raw.columns.map(deserializeColumn)
      : createDefaultColumns(),
  };
}

function deserializeColumn(raw: RawColumn): Column {
  return {
    id: raw.id ?? createId(),
    columnType: raw.columnType ?? ColumnType.Todo,
    tasks: (raw.tasks ?? []).map(deserializeTask),
    wipLimit: raw.wipLimit ?? null,
  };
}

function deserializeTask(raw: RawTask): Task {
  return {
    id: raw.id ?? createId(),
    title: raw.title,
    description: raw.description ?? null,
    dueDate: deserializeDueDate(raw.dueDate),
    priority: raw.priority,
  };
}

function deserializeDueDate(
  dueDate: string | null | undefined,
): Temporal.PlainDate | null {
  if (dueDate === null || dueDate === undefined) {
    return null;
  }

  const parsedDate = parseDateFromString(dueDate);
  if (!parsedDate) {
    throw new Error(`Invalid dueDate "${dueDate}".`);
  }

  return parsedDate;
}
