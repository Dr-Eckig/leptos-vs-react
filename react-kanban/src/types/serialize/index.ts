import type { Temporal } from "@js-temporal/polyfill";
import { parseDateFromString } from "../date";
import { createId } from "../utility";
import {
  createDefaultColumns,
  ColumnType,
  type Column,
  type RawColumn,
} from "./column";
import type { AllBoards, Board, RawAllBoards, RawBoard } from "./board";
import type { RawTask, Task } from "./task";

export {
  ColumnType,
  columnDisplayNames,
  columnTypes,
  createColumn,
  createDefaultColumns,
} from "./column";
export {
  createBoard,
  createDefaultBoard,
  type AllBoards,
  type Board,
  type BoardId,
  type RawAllBoards,
  type RawBoard,
} from "./board";
export {
  createTask,
  Priority,
  type RawTask,
  type Task,
  type TaskId,
} from "./task";
export type { Column, ColumnId, RawColumn } from "./column";

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
