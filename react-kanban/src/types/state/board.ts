import { ColumnType } from "../serialize";
import { createId } from "../utility";
import {
  canColumnAcceptTaskFrom,
  columnTypes,
  createColumn,
  type Column,
} from "./column";
import type { Task, TaskId } from "./task";

export type BoardId = string;

export type Board = {
  id: BoardId;
  title: string;
  columns: Column[];
};

type MoveTaskContext = {
  sourceColumn: Column;
  targetColumn: Column;
  movingTask: Task;
};

export function createBoard(title: string): Board {
  return {
    id: createId(),
    title,
    columns: columnTypes.map((columnType) => createColumn(columnType, null)),
  };
}

export function addTaskToBoardColumn(
  board: Board,
  columnType: ColumnType,
  task: Task,
): Board {
  return {
    ...board,
    columns: board.columns.map((column) =>
      column.columnType === columnType
        ? { ...column, tasks: [...column.tasks, task] }
        : column,
    ),
  };
}

export function updateBoardTask(board: Board, taskId: TaskId, nextTask: Task): Board {
  let changed = false;
  const columns = board.columns.map((column) => {
    let columnChanged = false;
    const tasks = column.tasks.map((task) => {
      if (task.id !== taskId) {
        return task;
      }

      columnChanged = true;
      changed = true;
      return nextTask;
    });

    return columnChanged ? { ...column, tasks } : column;
  });

  return changed ? { ...board, columns } : board;
}

export function deleteBoardTask(board: Board, taskId: TaskId): Board {
  let changed = false;
  const columns = board.columns.map((column) => {
    const tasks = column.tasks.filter((task) => task.id !== taskId);

    if (tasks.length === column.tasks.length) {
      return column;
    }

    changed = true;
    return { ...column, tasks };
  });

  return changed ? { ...board, columns } : board;
}

export function canMoveBoardTask(
  board: Board,
  taskId: TaskId,
  toColumnType: ColumnType,
  beforeTaskId: TaskId | null,
): boolean {
  return getMoveTaskContext(board, taskId, toColumnType, beforeTaskId) !== null;
}

export function moveBoardTask(
  board: Board,
  taskId: TaskId,
  toColumnType: ColumnType,
  beforeTaskId: TaskId | null,
): Board {
  const moveContext = getMoveTaskContext(
    board,
    taskId,
    toColumnType,
    beforeTaskId,
  );
  if (!moveContext) {
    return board;
  }

  const { sourceColumn, targetColumn, movingTask } = moveContext;

  const columns = board.columns.map((column) => {
    if (column.id !== sourceColumn.id && column.id !== targetColumn.id) {
      return column;
    }

    let tasks = column.tasks;

    if (column.id === sourceColumn.id) {
      tasks = tasks.filter((task) => task.id !== taskId);
    }

    if (column.id === targetColumn.id) {
      const insertIndex = beforeTaskId
        ? tasks.findIndex((task) => task.id === beforeTaskId)
        : -1;
      const normalizedInsertIndex =
        insertIndex >= 0 ? insertIndex : tasks.length;

      tasks = [
        ...tasks.slice(0, normalizedInsertIndex),
        movingTask,
        ...tasks.slice(normalizedInsertIndex),
      ];
    }

    return { ...column, tasks };
  });

  return { ...board, columns };
}

function getMoveTaskContext(
  board: Board,
  taskId: TaskId,
  toColumnType: ColumnType,
  beforeTaskId: TaskId | null,
): MoveTaskContext | null {
  if (beforeTaskId === taskId) {
    return null;
  }

  const sourceColumn = board.columns.find((column) =>
    column.tasks.some((task) => task.id === taskId),
  );
  const targetColumn = board.columns.find(
    (column) => column.columnType === toColumnType,
  );

  if (!sourceColumn || !targetColumn) {
    return null;
  }

  if (!canColumnAcceptTaskFrom(targetColumn, sourceColumn.columnType)) {
    return null;
  }

  const movingTask = sourceColumn.tasks.find((task) => task.id === taskId);
  if (!movingTask) {
    return null;
  }

  return {
    sourceColumn,
    targetColumn,
    movingTask,
  };
}
