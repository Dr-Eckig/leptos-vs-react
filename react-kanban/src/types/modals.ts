import type { Board, Column, ColumnType, Task } from "./serialize";

export type OpenTaskModal = {
  columnType: ColumnType | null;
  task: Task | null;
};

export function openTaskModal(columnType: ColumnType | null): OpenTaskModal {
  return {
    columnType,
    task: null,
  };
}

export function openTaskModalWithTask(
  columnType: ColumnType,
  task: Task,
): OpenTaskModal {
  return {
    columnType,
    task,
  };
}

export type OpenColumnModal = {
  column: Column;
};

export function openColumnModalWithColumn(column: Column): OpenColumnModal {
  return { column };
}

export type OpenBoardModal = {
  board: Board | null;
};

export function openBoardModal(): OpenBoardModal {
  return { board: null };
}

export function openBoardModalWithBoard(board: Board): OpenBoardModal {
  return { board };
}
