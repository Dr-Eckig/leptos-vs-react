import { useState } from "react";
import type { OpenBoardModal, OpenColumnModal, OpenTaskModal } from "../types/modals";
import {
  addBoardToAllBoards,
  addTaskToCurrentBoard as addTaskToCurrentBoardState,
  deleteTaskFromCurrentBoard as deleteTaskFromCurrentBoardState,
  getCurrentBoard,
  moveTaskInCurrentBoard as moveTaskInCurrentBoardState,
  setCurrentBoard as setCurrentBoardState,
  updateAllBoardsBoardTitle,
  updateCurrentBoardColumnWipLimit,
  updateTaskOnCurrentBoard as updateTaskOnCurrentBoardState,
} from "../types/state/all_boards";
import type {
  Board,
  BoardId,
  ColumnId,
  ColumnType,
  Task,
  TaskId,
} from "../types/serialize";
import {
  BoardsActionsContext,
  BoardsStateContext,
  DragAndDropActionsContext,
  DragAndDropStateContext,
  ModalsActionsContext,
  ModalsStateContext,
  type AppContextProviderProps,
  type BoardsActions,
  type BoardsState,
  type DragAndDropActions,
  type DragAndDropState,
  type ModalActions,
  type ModalState,
} from "./appContext";
import type { DraggableItemDto } from "../types/drag_and_drop";

export function AppContextProvider({
  initialBoards,
  children,
}: AppContextProviderProps) {
  const [allBoards, setAllBoards] = useState(initialBoards);
  const [boardModal, setBoardModal] = useState<OpenBoardModal | null>(null);
  const [columnModal, setColumnModal] = useState<OpenColumnModal | null>(null);
  const [taskModal, setTaskModal] = useState<OpenTaskModal | null>(null);
  const [draggedItem, setDraggedItem] = useState<DraggableItemDto | null>(null);

  const currentBoard = getCurrentBoard(allBoards);

  const setCurrentBoard = (boardId: BoardId) => {
    setAllBoards((current) => setCurrentBoardState(current, boardId));
  };

  const addBoard = (board: Board) => {
    setAllBoards((current) => addBoardToAllBoards(current, board));
  };

  const updateBoardTitle = (boardId: BoardId, title: string) => {
    setAllBoards((current) =>
      updateAllBoardsBoardTitle(current, boardId, title),
    );
  };

  const updateColumnWipLimit = (columnId: ColumnId, wipLimit: number | null) => {
    setAllBoards((current) =>
      updateCurrentBoardColumnWipLimit(current, columnId, wipLimit),
    );
  };

  const addTaskToCurrentBoard = (columnType: ColumnType, task: Task) => {
    setAllBoards((current) =>
      addTaskToCurrentBoardState(current, columnType, task),
    );
  };

  const updateTaskOnCurrentBoard = (taskId: TaskId, task: Task) => {
    setAllBoards((current) =>
      updateTaskOnCurrentBoardState(current, taskId, task),
    );
  };

  const deleteTaskFromCurrentBoard = (taskId: TaskId) => {
    setAllBoards((current) =>
      deleteTaskFromCurrentBoardState(current, taskId),
    );
  };

  const moveTaskInCurrentBoard = (
    taskId: TaskId,
    toColumnType: ColumnType,
    beforeTaskId: TaskId | null,
  ) => {
    const nextAllBoards = moveTaskInCurrentBoardState(
      allBoards,
      taskId,
      toColumnType,
      beforeTaskId,
    );

    if (nextAllBoards === allBoards) {
      return false;
    }

    setAllBoards(nextAllBoards);

    return true;
  };

  const boardsState: BoardsState = {
    boards: allBoards.boards,
    currentBoardId: allBoards.currentBoardId,
    currentBoard,
  };

  const boardsActions: BoardsActions = {
    setCurrentBoard,
    addBoard,
    updateBoardTitle,
    updateColumnWipLimit,
    addTaskToCurrentBoard,
    updateTaskOnCurrentBoard,
    deleteTaskFromCurrentBoard,
    moveTaskInCurrentBoard,
  };

  const modalsState: ModalState = {
    board: boardModal,
    column: columnModal,
    task: taskModal,
  };

  const modalsActions: ModalActions = {
    setBoard: setBoardModal,
    setColumn: setColumnModal,
    setTask: setTaskModal,
  };

  const dragAndDropState: DragAndDropState = {
    draggedItem,
  };

  const dragAndDropActions: DragAndDropActions = {
    setDraggedItem,
  };

  return (
    <BoardsActionsContext.Provider value={boardsActions}>
      <BoardsStateContext.Provider value={boardsState}>
        <DragAndDropActionsContext.Provider value={dragAndDropActions}>
          <DragAndDropStateContext.Provider value={dragAndDropState}>
            <ModalsActionsContext.Provider value={modalsActions}>
              <ModalsStateContext.Provider value={modalsState}>
                {children}
              </ModalsStateContext.Provider>
            </ModalsActionsContext.Provider>
          </DragAndDropStateContext.Provider>
        </DragAndDropActionsContext.Provider>
      </BoardsStateContext.Provider>
    </BoardsActionsContext.Provider>
  );
}
