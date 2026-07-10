import { useState } from "react";
import {
  useBoardsActions,
  useBoardsState,
  useModalsActions,
} from "../../hooks";
import {
  PerformanceAction,
  performanceContextFromBoard,
  start as startPerformanceMeasurement,
} from "../../performance";
import { openTaskModalWithTask } from "../../types/modals";
import { formatDateToDisplay } from "../../types/date";
import { Dropdown } from "../ui/Dropdown";
import { IconText } from "../ui/IconText";
import { Tag } from "../ui/Tag";
import { Priority, type ColumnType, type Task } from "../../types/serialize";

type TaskCardProps = {
  task: Task;
  columnType: ColumnType;
  taskIndex: number;
};

const priorityColors: Record<Priority, "success" | "warning" | "danger"> = {
  [Priority.Low]: "success",
  [Priority.Medium]: "warning",
  [Priority.High]: "danger",
};

const priorityBorderClasses: Record<Priority, string> = {
  [Priority.Low]: "border-color-success",
  [Priority.Medium]: "border-color-warning",
  [Priority.High]: "border-color-danger",
};

export function TaskCard({
  task,
  columnType,
  taskIndex,
}: TaskCardProps) {
  const boardActions = useBoardsActions();
  const { currentBoard } = useBoardsState();
  const modals = useModalsActions();
  const [isDropdownVisible, setIsDropdownVisible] = useState(false);
  const formattedDueDate = task.dueDate ? formatDateToDisplay(task.dueDate) : null;
  const dropdownDataTestId = `${columnType}-task-dropdown-${taskIndex}`;

  const editTask = () => {
    modals.setTask(openTaskModalWithTask(columnType, task));
    setIsDropdownVisible(false);
  };

  const deleteTask = () => {
    const finishMeasurement = startPerformanceMeasurement(
      PerformanceAction.TaskDelete,
      performanceContextFromBoard(currentBoard),
    );
    boardActions.deleteTaskFromCurrentBoard(task.id);
    setIsDropdownVisible(false);
    finishMeasurement();
  };

  return (
    <div className={`card m-4 ${priorityBorderClasses[task.priority]}`}>
      <header className="card-header">
        <p className="card-header-title">
          <span className="pr-2">{task.title}</span>
        </p>

        <Dropdown
          isVisible={isDropdownVisible}
          setIsVisible={setIsDropdownVisible}
          alignment="right"
          trigger={
            <button
              className="card-header-icon"
              aria-label="options"
              data-testid={dropdownDataTestId}
              onClick={() => setIsDropdownVisible((current) => !current)}
            >
              <span className="icon">
                <i className="fa-solid fa-ellipsis-vertical" />
              </span>
            </button>
          }
        >
          <button
            className="dropdown-item"
            data-testid={`${dropdownDataTestId}-edit`}
            onClick={editTask}
          >
            <IconText icon="edit" text="Edit" color="warning" />
          </button>
          <button
            className="dropdown-item"
            data-testid={`${dropdownDataTestId}-delete`}
            onClick={deleteTask}
          >
            <IconText icon="trash" text="Delete" color="danger" />
          </button>
        </Dropdown>
      </header>

      <div className="card-content">
        <div className="tags mb-2">
          <Tag text={task.priority} color={priorityColors[task.priority]} />
          {formattedDueDate && <Tag text={formattedDueDate} />}
        </div>

        <p>{task.description ?? ""}</p>
      </div>
    </div>
  );
}
