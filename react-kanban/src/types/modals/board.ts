import { useState } from "react";
import type { Board } from "../serialize";
import type { BoardValidationError, UserBoard } from "../validation";

export type OpenBoardModal = {
  board: Board | null;
};

export function openBoardModal(): OpenBoardModal {
  return { board: null };
}

export function openBoardModalWithBoard(board: Board): OpenBoardModal {
  return { board };
}

export function useBoardForm(board: Board | null) {
  const [title, setTitle] = useState(board?.title ?? "");
  const [titleError, setTitleError] = useState<string>();

  const userBoard = (): UserBoard => ({ title });
  const clearError = () => setTitleError(undefined);
  const setValidationError = (error: BoardValidationError) => {
    setTitleError(
      error === "EmptyTitle"
        ? "The title must not be empty"
        : "Please enter a title with at most 200 characters.",
    );
  };

  return {
    title,
    setTitle,
    titleError,
    userBoard,
    clearError,
    setValidationError,
  };
}

export type BoardForm = ReturnType<typeof useBoardForm>;
