import {
  useBoardsActions,
  useBoardsState,
  useDragAndDropState,
  useModalsActions,
} from "../../hooks";
import {
  PerformanceAction,
  performanceContextFromBoard,
  start as startPerformanceMeasurement,
} from "../../performance";
import {
  openColumnModalWithColumn,
  openTaskModal,
} from "../../types/modals";
import {
  canColumnAcceptTaskFrom,
  columnDisplayNames,
  isColumnWipLimitReached,
  type Column as ColumnState,
} from "../../types/state";
import {
  createDraggableItemDto,
  type DraggableItemDto,
} from "../../types/drag_and_drop";
import { DraggableItem, DropZone } from "../drag_and_drop";
import { IconButton } from "../ui/IconButton";
import { Tag } from "../ui/Tag";
import { TaskCard } from "./TaskCard";

type ColumnProps = {
  column: ColumnState;
};

export function TaskColumn({ column }: ColumnProps) {
  const boardActions = useBoardsActions();
  const { currentBoard } = useBoardsState();
  const { draggedItem } = useDragAndDropState();
  const modals = useModalsActions();

  const columnTitle = columnDisplayNames[column.columnType];
  const taskCount = column.tasks.length;
  const isWipLimitReached = isColumnWipLimitReached(column);
  const tagText = column.wipLimit !== null
    ? `${taskCount} / ${column.wipLimit}`
    : `${taskCount}`;
  const dropAllowed = draggedItem
    ? canColumnAcceptTaskFrom(column, draggedItem.sourceColumnType)
    : true;

  const moveTaskToColumnEnd = (droppedItem: DraggableItemDto) => {
    const action =
      droppedItem.sourceColumnType === column.columnType
        ? PerformanceAction.TaskMoveWithinColumn
        : PerformanceAction.TaskMoveBetweenColumns;
    const finishMeasurement = startPerformanceMeasurement(
      action,
      performanceContextFromBoard(currentBoard),
    );

    if (
      !boardActions.moveTaskInCurrentBoard(
        droppedItem.taskId,
        column.columnType,
        null,
      )
    ) {
      return;
    }

    finishMeasurement();
  };

  return (
    <div className="column is-flex is-flex-direction-column">
      <DropZone
        className="kanban-column-drop-zone box is-radiusless full-height scrollable p-0"
        onDrop={moveTaskToColumnEnd}
        dropAllowed={dropAllowed}
      >
        <div className="is-flex is-justify-content-space-between is-align-items-center is-sticky p-4">
          <div className="is-flex is-align-items-center">
            <Tag
              text={tagText}
              color={isWipLimitReached ? "danger" : "light"}
              isRounded
            />
            <p className="title is-4 pl-2"> { columnTitle } </p>
          </div>

          <div className="buttons">
            <IconButton
              icon="edit"
              color="warning"
              size="small"
              onClick={() => {
                const finishMeasurement = startPerformanceMeasurement(
                  PerformanceAction.ModalOpen,
                  performanceContextFromBoard(currentBoard),
                );
                modals.setColumn(openColumnModalWithColumn(column));
                finishMeasurement();
              }}
              ariaLabel="Edit column"
            />
            <IconButton
              icon="plus"
              color="link"
              size="small"
              state={isWipLimitReached ? "disabled" : "normal"}
              onClick={() => {
                const finishMeasurement = startPerformanceMeasurement(
                  PerformanceAction.ModalOpen,
                  performanceContextFromBoard(currentBoard),
                );
                modals.setTask(openTaskModal(column.columnType));
                finishMeasurement();
              }}
              ariaLabel="Add task"
              dataTestId={`add-task-button-${column.columnType}`}
            />
          </div>
        </div>

        {column.tasks.map((task, taskIndex) => (
          <DropZone
            key={task.id}
            className="kanban-task-drop-target"
            onDrop={(droppedItem) => {
              const action =
                droppedItem.sourceColumnType === column.columnType
                  ? PerformanceAction.TaskMoveWithinColumn
                  : PerformanceAction.TaskMoveBetweenColumns;
              const finishMeasurement = startPerformanceMeasurement(
                action,
                performanceContextFromBoard(currentBoard),
              );

              if (
                !boardActions.moveTaskInCurrentBoard(
                  droppedItem.taskId,
                  column.columnType,
                  task.id,
                )
              ) {
                return;
              }

              finishMeasurement();
            }}
            dropAllowed={dropAllowed}
          >
            <DraggableItem
              data={createDraggableItemDto(task.id, column.columnType)}
            >
              <TaskCard
                task={task}
                columnType={column.columnType}
                taskIndex={taskIndex}
              />
            </DraggableItem>
          </DropZone>
        ))}
      </DropZone>
    </div>
  );
}
