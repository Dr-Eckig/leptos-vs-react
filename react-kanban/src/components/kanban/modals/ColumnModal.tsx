import {
  useBoardsActions,
  useModalsActions,
  useModalsState,
  type BoardsActions,
} from "../../../hooks";
import {
  useColumnForm,
  type ColumnForm,
} from "../../../types/modals";
import {
  columnDisplayNames,
  type Column,
} from "../../../types/serialize";
import { validateColumn } from "../../../types/validation";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";

export function ColumnModal() {
  const { column: data } = useModalsState();
  const boardActions = useBoardsActions();
  const modalActions = useModalsActions();
  const column = data?.column ?? null;
  const form = useColumnForm(column, data);

  const closeModal = () => modalActions.setColumn(null);
  const saveColumn = () => {
    if (!column) {
      return;
    }

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
      title={
        column
          ? `Edit Column: ${columnDisplayNames[column.columnType]}`
          : "Edit Column"
      }
      isOpen={data !== null}
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
