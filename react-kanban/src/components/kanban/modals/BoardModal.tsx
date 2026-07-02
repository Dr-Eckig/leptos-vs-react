import { useEffect, useState } from "react";
import {
  useBoardsActions,
  useModalsActions,
  useModalsState,
} from "../../../hooks";
import { validateBoard } from "../../../types/validation";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";

export function BoardModal() {
  const modals = useModalsState();
  const board = modals.board?.board ?? null;
  const isOpen = modals.board !== null;

  const boards = useBoardsActions();
  const modalActions = useModalsActions();
  const [title, setTitle] = useState(board?.title ?? "");
  const [titleError, setTitleError] = useState<string | undefined>();

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setTitle(board?.title ?? "");
    setTitleError(undefined);
  }, [board, isOpen]);

  const closeModal = () => {
    modalActions.setBoard(null);
  };

  const saveBoard = () => {
    const result = validateBoard({ title });

    if (!result.ok) {
      if (result.error === "EmptyTitle") {
        setTitleError("The title must not be empty");
      } else {
        setTitleError("Please enter a title with at most 200 characters.");
      }
      return;
    }

    if (board) {
      boards.updateBoardTitle(board.id, result.board.title);
    } else {
      boards.addBoard(result.board);
    }

    modalActions.setBoard(null);
  };

  return (
    <Modal
      title={board ? "Edit Board" : "Add Board"}
      isOpen={isOpen}
      onClose={closeModal}
      onSave={saveBoard}
    >
      <Input
        label="Title"
        value={title}
        setValue={setTitle}
        errorMessage={titleError}
      />
    </Modal>
  );
}
