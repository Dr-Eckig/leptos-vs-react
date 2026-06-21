import { useEffect, useState } from "react";
import {
  useBoardsActions,
  useBoardsState,
  useModalsActions,
  useModalsState,
} from "../../../hooks";
import {
  PerformanceAction,
  performanceContextFromBoard,
  start as startPerformanceMeasurement,
} from "../../../performance";
import type { Board } from "../../../types/state";
import { validateBoard } from "../../../types/validation";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";

export function BoardModal() {
  const modals = useModalsState();
  const board = modals.board?.board ?? null;
  const isOpen = modals.board !== null;

  return <BoardModalForm board={board} isOpen={isOpen} />;
}

type BoardModalFormProps = {
  board: Board | null;
  isOpen: boolean;
};

function BoardModalForm({ board, isOpen }: BoardModalFormProps) {
  const boards = useBoardsActions();
  const { currentBoard } = useBoardsState();
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
    const finishMeasurement = startPerformanceMeasurement(
      PerformanceAction.ModalClose,
      performanceContextFromBoard(currentBoard),
    );
    modalActions.setBoard(null);
    finishMeasurement();
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

    const finishMeasurement = startPerformanceMeasurement(
      board ? PerformanceAction.BoardEdit : PerformanceAction.BoardCreate,
      performanceContextFromBoard(currentBoard),
    );

    if (board) {
      boards.updateBoardTitle(board.id, result.board.title);
    } else {
      boards.addBoard(result.board);
    }

    modalActions.setBoard(null);
    finishMeasurement();
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
