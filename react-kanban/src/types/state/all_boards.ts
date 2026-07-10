import type {
  AllBoards,
  Board,
  BoardId,
  ColumnId,
  ColumnType,
  Task,
  TaskId,
} from "../serialize";
import {
  addTaskToBoardColumn,
  canMoveBoardTask,
  deleteBoardTask,
  moveBoardTask,
  updateBoardTask,
} from "./board";

export function getCurrentBoard(allBoards: AllBoards): Board | null {
  return (
    allBoards.boards.find((board) => board.id === allBoards.currentBoardId) ??
    null
  );
}

export function setCurrentBoard(
  allBoards: AllBoards,
  boardId: BoardId,
): AllBoards {
  return {
    ...allBoards,
    currentBoardId: boardId,
  };
}

export function addBoardToAllBoards(
  allBoards: AllBoards,
  board: Board,
): AllBoards {
  return {
    boards: [...allBoards.boards, board],
    currentBoardId: board.id,
  };
}

export function updateAllBoardsBoardTitle(
  allBoards: AllBoards,
  boardId: BoardId,
  title: string,
): AllBoards {
  return {
    ...allBoards,
    boards: allBoards.boards.map((board) =>
      board.id === boardId ? { ...board, title } : board,
    ),
  };
}

export function updateCurrentBoardColumnWipLimit(
  allBoards: AllBoards,
  columnId: ColumnId,
  wipLimit: number | null,
): AllBoards {
  return updateCurrentBoard(allBoards, (board) => ({
    ...board,
    columns: board.columns.map((column) =>
      column.id === columnId ? { ...column, wipLimit } : column,
    ),
  }));
}

export function addTaskToCurrentBoard(
  allBoards: AllBoards,
  columnType: ColumnType,
  task: Task,
): AllBoards {
  return updateCurrentBoard(allBoards, (board) =>
    addTaskToBoardColumn(board, columnType, task),
  );
}

export function updateTaskOnCurrentBoard(
  allBoards: AllBoards,
  taskId: TaskId,
  task: Task,
): AllBoards {
  return updateCurrentBoard(allBoards, (board) =>
    updateBoardTask(board, taskId, task),
  );
}

export function deleteTaskFromCurrentBoard(
  allBoards: AllBoards,
  taskId: TaskId,
): AllBoards {
  return updateCurrentBoard(allBoards, (board) =>
    deleteBoardTask(board, taskId),
  );
}

export function canMoveTaskInCurrentBoard(
  allBoards: AllBoards,
  taskId: TaskId,
  toColumnType: ColumnType,
  beforeTaskId: TaskId | null,
): boolean {
  const board = getCurrentBoard(allBoards);

  return board
    ? canMoveBoardTask(board, taskId, toColumnType, beforeTaskId)
    : false;
}

export function moveTaskInCurrentBoard(
  allBoards: AllBoards,
  taskId: TaskId,
  toColumnType: ColumnType,
  beforeTaskId: TaskId | null,
): AllBoards {
  return updateCurrentBoard(allBoards, (board) =>
    moveBoardTask(board, taskId, toColumnType, beforeTaskId),
  );
}

function updateCurrentBoard(
  allBoards: AllBoards,
  updateBoard: (board: Board) => Board,
): AllBoards {
  let changed = false;
  const boards = allBoards.boards.map((board) => {
    if (board.id !== allBoards.currentBoardId) {
      return board;
    }

    const nextBoard = updateBoard(board);
    changed ||= nextBoard !== board;
    return nextBoard;
  });

  return changed ? { ...allBoards, boards } : allBoards;
}
