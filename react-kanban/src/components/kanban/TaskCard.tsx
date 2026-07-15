import { useState } from "react";
import { useBoardsState } from "../../hooks";
import {
  PerformanceAction,
  performanceContextFromBoard,
  start as startPerformanceMeasurement,
} from "../../performance";
import { formatDateToDisplay } from "../../types/date";
import { Dropdown } from "../ui/Dropdown";
import { IconText } from "../ui/IconText";
import { Tag } from "../ui/Tag";
import { Priority, type Task } from "../../types/serialize";

type TaskCardProps = {
  task: Task;
  columnName: string;
  taskIndex: number;
  onEdit: () => void;
  onDelete: () => void;
};

export function TaskCard({
  task,
  columnName,
  taskIndex,
  onEdit,
  onDelete,
}: TaskCardProps) {
  return (
    <div className={`card m-4 ${priorityBorderClass(task.priority)}`}>
      <TaskCardHeader
        task={task}
        columnName={columnName}
        taskIndex={taskIndex}
        onEdit={onEdit}
        onDelete={onDelete}
      />
      <TaskCardContent task={task} />
    </div>
  );
}

function TaskCardHeader({
  task,
  columnName,
  taskIndex,
  onEdit,
  onDelete,
}: TaskCardProps) {
  return (
    <header className="card-header">
      <p className="card-header-title">
        <span className="pr-2">{task.title}</span>
      </p>
      <TaskActionsDropdown
        columnName={columnName}
        taskIndex={taskIndex}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    </header>
  );
}

type TaskActionsDropdownProps = Pick<
  TaskCardProps,
  "columnName" | "taskIndex" | "onEdit" | "onDelete"
>;

function TaskActionsDropdown({
  columnName,
  taskIndex,
  onEdit,
  onDelete,
}: TaskActionsDropdownProps) {
  const { currentBoard } = useBoardsState();
  const [isVisible, setIsVisible] = useState(false);
  const dataTestId = `${columnName}-task-dropdown-${taskIndex}`;

  const editTask = () => {
    onEdit();
    setIsVisible(false);
  };
  const deleteTask = () => {
    const finishMeasurement = startPerformanceMeasurement(
      PerformanceAction.TaskDelete,
      performanceContextFromBoard(currentBoard),
    );
    onDelete();
    setIsVisible(false);
    finishMeasurement();
  };

  return (
    <Dropdown
      isVisible={isVisible}
      setIsVisible={setIsVisible}
      alignment="right"
      trigger={
        <button
          className="card-header-icon"
          aria-label="options"
          data-testid={dataTestId}
          onClick={() => setIsVisible((visible) => !visible)}
        >
          <span className="icon">
            <i className="fa-solid fa-ellipsis-vertical" />
          </span>
        </button>
      }
    >
      <button
        className="dropdown-item"
        data-testid={`${dataTestId}-edit`}
        onClick={editTask}
      >
        <IconText icon="edit" text="Edit" color="warning" />
      </button>
      <button
        className="dropdown-item"
        data-testid={`${dataTestId}-delete`}
        onClick={deleteTask}
      >
        <IconText icon="trash" text="Delete" color="danger" />
      </button>
    </Dropdown>
  );
}

function TaskCardContent({ task }: Pick<TaskCardProps, "task">) {
  const dueDateText = task.dueDate ? formatDateToDisplay(task.dueDate) : null;

  return (
    <div className="card-content">
      <div className="tags mb-2">
        <Tag text={task.priority} color={priorityColor(task.priority)} />
        {dueDateText && <Tag text={dueDateText} />}
      </div>
      <p>{task.description ?? ""}</p>
    </div>
  );
}

function priorityColor(priority: Priority): "success" | "warning" | "danger" {
  switch (priority) {
    case Priority.Low:
      return "success";
    case Priority.Medium:
      return "warning";
    case Priority.High:
      return "danger";
  }
}

function priorityBorderClass(priority: Priority): string {
  switch (priority) {
    case Priority.Low:
      return "border-color-success";
    case Priority.Medium:
      return "border-color-warning";
    case Priority.High:
      return "border-color-danger";
  }
}
