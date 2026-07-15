import { useState } from "react";
import {
  useBoardsActions,
  useModalsActions,
  useModalsState,
  type BoardsActions,
} from "../../../hooks";
import type { OpenBoardModal } from "../../../types/modals";
import type { Board } from "../../../types/serialize";
import {
  validateBoard,
  type BoardValidationError,
} from "../../../types/validation";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";

export function BoardModal() {
  const { board } = useModalsState();

  return board ? <BoardModalContent data={board} /> : null;
}

type BoardModalContentProps = {
  data: OpenBoardModal;
};

function BoardModalContent({ data }: BoardModalContentProps) {
  const boardActions = useBoardsActions();
  const modalActions = useModalsActions();
  const board = data.board;
  const form = useBoardForm(board);

  const closeModal = () => modalActions.setBoard(null);
  const saveBoard = () => {
    form.clearError();

    const result = validateBoard(form.userBoard());
    if (!result.ok) {
      form.setValidationError(result.error);
      return;
    }

    saveValidatedBoard(boardActions, board, result.board);
    closeModal();
  };

  const modalTitle = board ? "Edit Board" : "Add Board";

  return (
    <Modal
      title={modalTitle}
      isOpen={true}
      close={closeModal}
      onSave={saveBoard}
    >
      <BoardFormFields form={form} />
    </Modal>
  );
}

function useBoardForm(board: Board | null) {
  const [title, setTitle] = useState(board?.title ?? "");
  const [titleError, setTitleError] = useState<string>();

  const userBoard = () => ({ title });
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

type BoardForm = ReturnType<typeof useBoardForm>;

function BoardFormFields({ form }: { form: BoardForm }) {
  return (
    <Input
      label="Title"
      value={form.title}
      setValue={form.setTitle}
      errorMessage={form.titleError}
    />
  );
}

function saveValidatedBoard(
  boardActions: BoardsActions,
  editedBoard: Board | null,
  validatedBoard: Board,
) {
  if (editedBoard) {
    updateBoard(boardActions, editedBoard, validatedBoard);
  } else {
    boardActions.addBoard(validatedBoard);
  }
}

function updateBoard(
  boardActions: BoardsActions,
  board: Board,
  validatedBoard: Board,
) {
  boardActions.updateBoardTitle(board.id, validatedBoard.title);
}
