import {
  useBoardsActions,
  useBoardsState,
  useModalsActions,
  useModalsState,
  type BoardsActions,
  type BoardsState,
} from "../../../hooks";
import {
  PerformanceAction,
  performanceContextFromBoard,
  start as startPerformanceMeasurement,
  type FinishPerformanceMeasurement,
} from "../../../performance";
import { Priority, type ColumnType, type Task, type TaskId } from "../../../types/serialize";
import { validateTask } from "../../../types/validation";
import {
  useTaskForm,
  type OpenTaskModal,
  type TaskForm,
} from "../../../types/modals";
import { IconButton } from "../../ui/IconButton";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";
import { Select } from "../../ui/Select";
import { Textarea } from "../../ui/Textarea";

const priorityOptions: Priority[] = Object.values(Priority);

export function TaskModal() {
  const { task } = useModalsState();

  return task ? <TaskModalContent data={task} /> : null;
}

type TaskModalContentProps = {
  data: OpenTaskModal;
};

function TaskModalContent({ data }: TaskModalContentProps) {
  const boardActions = useBoardsActions();
  const { currentBoard } = useBoardsState();
  const modalActions = useModalsActions();
  const form = useTaskForm(data.task);

  const closeModal = () => modalActions.setTask(null);
  const saveTask = () => {
    form.clearErrors();

    const result = validateTask(form.userTask());
    if (!result.ok) {
      form.setValidationError(result.error);
      return;
    }

    const finishMeasurement = saveValidatedTask(
      boardActions,
      currentBoard,
      data.task,
      data.columnType,
      result.task,
    );
    closeModal();
    finishMeasurement?.();
  };

  const modalTitle = data.task ? "Edit Task" : "Add Task";
  const saveDataTestId = `save-button-${data.columnType ?? "unknown-column"}`;

  return (
    <Modal
      title={modalTitle}
      isOpen={true}
      close={closeModal}
      onSave={saveTask}
      saveDataTestId={saveDataTestId}
    >
      <TaskFormFields form={form} />
    </Modal>
  );
}

function TaskFormFields({ form }: { form: TaskForm }) {
  return (
    <>
      <Input
        label="Title"
        value={form.title}
        setValue={form.setTitle}
        errorMessage={form.titleError}
        dataTestId="task-title-input"
      />

      <Textarea
        label="Description"
        value={form.description}
        setValue={form.setDescription}
      />

      <Select
        label="Priority"
        options={priorityOptions}
        value={form.priority}
        setValue={(value) => form.setPriority(value as Priority)}
        errorMessage={form.priorityError}
      />

      <div className="is-flex">
        <Input
          label="Due Date"
          value={form.dueDate}
          setValue={form.setDueDate}
          inputType="date"
          errorMessage={form.dueDateError}
        />

        <div className="is-flex is-align-items-end pl-2 mb-4">
          <IconButton
            icon="reset"
            color="light"
            size="small"
            ariaLabel="Reset due date"
            onClick={() => form.setDueDate("")}
          />
        </div>
      </div>
    </>
  );
}

function saveValidatedTask(
  boardActions: BoardsActions,
  currentBoard: BoardsState["currentBoard"],
  editedTask: Task | null,
  columnType: ColumnType | null,
  validatedTask: Task,
): FinishPerformanceMeasurement | null {
  if (editedTask) {
    const finishMeasurement = startTaskMeasurement(
      currentBoard,
      PerformanceAction.TaskEdit,
    );
    updateTask(boardActions, editedTask.id, validatedTask);
    return finishMeasurement;
  }

  if (columnType) {
    const finishMeasurement = startTaskMeasurement(
      currentBoard,
      PerformanceAction.TaskCreate,
    );
    boardActions.addTaskToCurrentBoard(columnType, validatedTask);
    return finishMeasurement;
  }

  return null;
}

function updateTask(
  boardActions: BoardsActions,
  taskId: TaskId,
  validatedTask: Task,
) {
  boardActions.updateTaskOnCurrentBoard(taskId, {
    ...validatedTask,
    id: taskId,
  });
}

function startTaskMeasurement(
  currentBoard: BoardsState["currentBoard"],
  action: PerformanceAction,
): FinishPerformanceMeasurement {
  return startPerformanceMeasurement(
    action,
    performanceContextFromBoard(currentBoard),
  );
}
