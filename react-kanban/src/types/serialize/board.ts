import { createId } from "../utility";
import {
  createColumn,
  createDefaultColumns,
  type Column,
  ColumnType,
  columnTypes,
  type RawColumn,
} from "./column";

export type BoardId = string;

export type AllBoards = {
  boards: Board[];
  currentBoardId: BoardId | null;
};

export type Board = {
  id: BoardId;
  title: string;
  columns: Column[];
};

export type RawAllBoards = {
  boards?: RawBoard[];
  currentBoardId?: BoardId | null;
};

export type RawBoard = {
  id?: BoardId;
  title: string;
  columns?: RawColumn[];
};

export function createBoard(title: string): Board {
  return {
    id: createId(),
    title,
    columns: columnTypes.map((columnType) => createColumn(columnType, null)),
  };
}

export function createDefaultBoard(): Board {
  return {
    id: createId(),
    title: "Kanban Board",
    columns: createDefaultColumns(),
  };
}

export { createDefaultColumns, ColumnType };
