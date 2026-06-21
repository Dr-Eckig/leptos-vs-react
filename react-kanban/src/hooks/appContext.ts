import {
  createContext,
  useContext,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";
import type { DraggableItemDto } from "../types/drag_and_drop";
import type { OpenBoardModal, OpenColumnModal, OpenTaskModal } from "../types/modals";
import type {
  AllBoards,
  Board,
  BoardId,
  ColumnId,
  Task,
  TaskId,
} from "../types/state";
import type { ColumnType } from "../types/serialize";

export type ModalState = {
  board: OpenBoardModal | null;
  column: OpenColumnModal | null;
  task: OpenTaskModal | null;
};

export type ModalActions = {
  setBoard: Dispatch<SetStateAction<OpenBoardModal | null>>;
  setColumn: Dispatch<SetStateAction<OpenColumnModal | null>>;
  setTask: Dispatch<SetStateAction<OpenTaskModal | null>>;
};

export type BoardsState = {
  boards: Board[];
  currentBoardId: BoardId | null;
  currentBoard: Board | null;
};

export type BoardsActions = {
  setCurrentBoard: (boardId: BoardId) => void;
  addBoard: (board: Board) => void;
  updateBoardTitle: (boardId: BoardId, title: string) => void;
  updateColumnWipLimit: (columnId: ColumnId, wipLimit: number | null) => void;
  addTaskToCurrentBoard: (columnType: ColumnType, task: Task) => void;
  updateTaskOnCurrentBoard: (taskId: TaskId, task: Task) => void;
  deleteTaskFromCurrentBoard: (taskId: TaskId) => void;
  moveTaskInCurrentBoard: (
    taskId: TaskId,
    toColumnType: ColumnType,
    beforeTaskId: TaskId | null,
  ) => boolean;
};

export type DragAndDropState = {
  draggedItem: DraggableItemDto | null;
};

export type DragAndDropActions = {
  setDraggedItem: Dispatch<SetStateAction<DraggableItemDto | null>>;
};

export type AppContextValue = {
  boards: BoardsState & BoardsActions;
  modals: ModalState & ModalActions;
  dragAndDrop: DragAndDropState & DragAndDropActions;
};

export type AppContextProviderProps = {
  initialBoards: AllBoards;
  children: ReactNode;
};

export const BoardsStateContext = createContext<BoardsState | null>(null);
export const BoardsActionsContext = createContext<BoardsActions | null>(null);
export const ModalsStateContext = createContext<ModalState | null>(null);
export const ModalsActionsContext = createContext<ModalActions | null>(null);
export const DragAndDropStateContext =
  createContext<DragAndDropState | null>(null);
export const DragAndDropActionsContext =
  createContext<DragAndDropActions | null>(null);

export function useBoardsState(): BoardsState {
  return requiredContext(useContext(BoardsStateContext), "BoardsStateContext");
}

export function useBoardsActions(): BoardsActions {
  return requiredContext(useContext(BoardsActionsContext), "BoardsActionsContext");
}

export function useModalsState(): ModalState {
  return requiredContext(useContext(ModalsStateContext), "ModalsStateContext");
}

export function useModalsActions(): ModalActions {
  return requiredContext(useContext(ModalsActionsContext), "ModalsActionsContext");
}

export function useDragAndDropState(): DragAndDropState {
  return requiredContext(
    useContext(DragAndDropStateContext),
    "DragAndDropStateContext",
  );
}

export function useDragAndDropActions(): DragAndDropActions {
  return requiredContext(
    useContext(DragAndDropActionsContext),
    "DragAndDropActionsContext",
  );
}

export function useAppContext(): AppContextValue {
  return {
    boards: {
      ...useBoardsState(),
      ...useBoardsActions(),
    },
    modals: {
      ...useModalsState(),
      ...useModalsActions(),
    },
    dragAndDrop: {
      ...useDragAndDropState(),
      ...useDragAndDropActions(),
    },
  };
}

function requiredContext<T>(context: T | null, name: string): T {
  if (!context) {
    throw new Error(`${name} is not available`);
  }

  return context;
}
