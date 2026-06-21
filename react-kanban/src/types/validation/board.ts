import { createBoard } from "../state";
import type { Board } from "../state";

export type BoardValidationError = "EmptyTitle" | "TitleTooLong";

export type UserBoard = {
  title: string;
};

export function validateBoard(userBoard: UserBoard):
  | { ok: true; board: Board }
  | { ok: false; error: BoardValidationError } {
  const title = userBoard.title.trim();

  if (!title) {
    return { ok: false, error: "EmptyTitle" };
  }

  if (title.length > 200) {
    return { ok: false, error: "TitleTooLong" };
  }

  return {
    ok: true,
    board: createBoard(title),
  };
}
