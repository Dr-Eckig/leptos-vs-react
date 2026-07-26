import {
  useBoardsActions,
  useModalsActions,
  useModalsState,
  type BoardsActions,
} from "../../../hooks";
import {
  useColumnForm,
  type ColumnForm,
  type OpenColumnModal,
} from "../../../types/modals";
import {
  columnDisplayNames,
  type Column,
} from "../../../types/serialize";
import { validateColumn } from "../../../types/validation";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";

export function ColumnModal() {
  const { column } = useModalsState();

  return column ? <ColumnModalContent data={column} /> : null;
}

type ColumnModalContentProps = {
  data: OpenColumnModal;
};

function ColumnModalContent({ data }: ColumnModalContentProps) {
  const boardActions = useBoardsActions();
  const modalActions = useModalsActions();
  const column = data.column;
  const form = useColumnForm(column);

  const closeModal = () => modalActions.setColumn(null);
  const saveColumn = () => {
    form.clearError();

    const result = validateColumn(form.userColumn(column));
    if (!result.ok) {
      form.setValidationError();
      return;
    }

    updateColumn(boardActions, column, result.column.wipLimit);
    closeModal();
  };

  return (
    <Modal
      title={`Edit Column: ${columnDisplayNames[column.columnType]}`}
      isOpen={true}
      close={closeModal}
      onSave={saveColumn}
    >
      <ColumnFormFields form={form} />
    </Modal>
  );
}

function ColumnFormFields({ form }: { form: ColumnForm }) {
  return (
    <Input
      label="WIP Limit"
      value={form.wipLimit}
      setValue={form.setWipLimit}
      inputType="number"
      errorMessage={form.limitError}
      min={0}
    />
  );
}

function updateColumn(
  boardActions: BoardsActions,
  column: Column,
  wipLimit: number | null,
) {
  boardActions.updateColumnWipLimit(column.id, wipLimit);
}
