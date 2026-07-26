import {
  useBoardsActions,
  useModalsActions,
  useModalsState,
  type BoardsActions,
} from "../../../hooks";
import {
  useBoardForm,
  type BoardForm,
} from "../../../types/modals";
import type { Board } from "../../../types/serialize";
import { validateBoard } from "../../../types/validation";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";

export function BoardModal() {
  const { board: data } = useModalsState();
  const boardActions = useBoardsActions();
  const modalActions = useModalsActions();
  const board = data?.board ?? null;
  const form = useBoardForm(board, data);

  const closeModal = () => modalActions.setBoard(null);
  const saveBoard = () => {
    if (!data) {
      return;
    }

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
      isOpen={data !== null}
      close={closeModal}
      onSave={saveBoard}
    >
      <BoardFormFields form={form} />
    </Modal>
  );
}

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
