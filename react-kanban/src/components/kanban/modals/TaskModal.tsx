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
  type FinishPerformanceMeasurement,
} from "../../../performance";
import { Priority, type Task } from "../../../types/state";
import { validateTask } from "../../../types/validation";
import { formatDateToString } from "../../../types/date";
import { IconButton } from "../../ui/IconButton";
import { Input } from "../../ui/Input";
import { Modal } from "../../ui/Modal";
import { Select } from "../../ui/Select";
import { Textarea } from "../../ui/Textarea";
import type { ColumnType } from "../../../types/serialize";

const priorityOptions: Priority[] = Object.values(Priority);

export function TaskModal() {
  const modals = useModalsState();
  const data = modals.task ?? { columnType: null, task: null };
  const isOpen = modals.task !== null;

  return (
    <TaskModalForm
      task={data.task}
      columnType={data.columnType}
      isOpen={isOpen}
    />
  );
}

type TaskModalFormProps = {
  task: Task | null;
  columnType: ColumnType | null;
  isOpen: boolean;
};

function TaskModalForm({ task, columnType, isOpen }: TaskModalFormProps) {
  const boardActions = useBoardsActions();
  const { currentBoard } = useBoardsState();
  const modalActions = useModalsActions();
  const [title, setTitle] = useState(task?.title ?? "");
  const [description, setDescription] = useState(task?.description ?? "");
  const [priority, setPriority] = useState<Priority>(task?.priority ?? Priority.Medium);
  const [dueDate, setDueDate] = useState(
    task?.dueDate ? formatDateToString(task.dueDate) : "",
  );

  const [titleError, setTitleError] = useState<string | undefined>();
  const [priorityError, setPriorityError] = useState<string | undefined>();
  const [dueDateError, setDueDateError] = useState<string | undefined>();

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setTitle(task?.title ?? "");
    setDescription(task?.description ?? "");
    setPriority(task?.priority ?? Priority.Medium);
    setDueDate(task?.dueDate ? formatDateToString(task.dueDate) : "");
    setTitleError(undefined);
    setPriorityError(undefined);
    setDueDateError(undefined);
  }, [task, isOpen]);

  const closeModal = () => {
    modalActions.setTask(null);
  };

  const saveTask = () => {
    const result = validateTask({
      title,
      description,
      dueDate,
      priority,
    });

    if (!result.ok) {
      if (result.error === "TitleTooLong") {
        setTitleError("Please enter a title with at most 200 characters.");
      } else if (result.error === "EmptyTitle") {
        setTitleError("The title must not be empty.");
      } else if (result.error === "InvalidDueDate") {
        setDueDateError("Please enter a valid date.");
      } else {
        setPriorityError("Please select a valid priority.");
      }
      return;
    }

    let finishMeasurement: FinishPerformanceMeasurement | null = null;

    if (task) {
      finishMeasurement = startPerformanceMeasurement(
        PerformanceAction.TaskEdit,
        performanceContextFromBoard(currentBoard),
      );
      boardActions.updateTaskOnCurrentBoard(task.id, {
        ...result.task,
        id: task.id,
      });
    } else if (columnType) {
      finishMeasurement = startPerformanceMeasurement(
        PerformanceAction.TaskCreate,
        performanceContextFromBoard(currentBoard),
      );
      boardActions.addTaskToCurrentBoard(columnType, result.task);
    }

    modalActions.setTask(null);
    finishMeasurement?.();
  };

  const saveDataTestId = `save-button-${columnType ?? "unknown-column"}`;

  return (
    <Modal
      title={task ? "Edit Task" : "Add Task"}
      isOpen={isOpen}
      onClose={closeModal}
      onSave={saveTask}
      saveDataTestId={saveDataTestId}
    >
      <Input
        label="Title"
        value={title}
        setValue={setTitle}
        errorMessage={titleError}
        dataTestId="task-title-input"
      />

      <Textarea
        label="Description"
        value={description}
        setValue={setDescription}
      />

      <Select
        label="Priority"
        options={priorityOptions}
        value={priority}
        setValue={(value) => setPriority(value as Priority)}
        errorMessage={priorityError}
      />

      <div className="is-flex">
        <Input
          label="Due Date"
          value={dueDate}
          setValue={setDueDate}
          inputType="date"
          errorMessage={dueDateError}
        />

        <div className="is-flex is-align-items-end pl-2 mb-4">
          <IconButton
            icon="reset"
            color="light"
            size="small"
            onClick={() => setDueDate("")}
            ariaLabel="Reset due date"
          />
        </div>
      </div>
    </Modal>
  );
}
