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
  openTaskModalWithTask,
} from "../../types/modals";
import {
  canColumnAcceptTaskFrom,
  isColumnWipLimitReached,
} from "../../types/state/column";
import {
  columnDisplayNames,
  type Column as ColumnState,
  type ColumnType,
  type Task,
  type TaskId,
} from "../../types/serialize";
import {
  createDraggableItemDto,
  type DraggableItemDto,
} from "../../types/drag_and_drop";
import type { BoardsActions, BoardsState } from "../../hooks";
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
  const columnName = column.columnType;

  const dropAllowed = draggedItem
    ? canColumnAcceptTaskFrom(column, draggedItem.sourceColumnType)
    : true;

  const moveTaskToColumnEnd = (draggedItem: DraggableItemDto) => {
    moveTask(boardActions, currentBoard, column.columnType, draggedItem, null);
  };

  return (
    <div className="column is-flex is-flex-direction-column">
      <DropZone
        className="kanban-column-drop-zone box is-radiusless full-height scrollable p-0"
        dataTestId={`${column.columnType}-column-drop-zone`}
        onDrop={moveTaskToColumnEnd}
        dropAllowed={dropAllowed}
      >
        <TaskColumnHeader column={column} />

        {column.tasks.map((task, taskIndex) => (
          <TaskDropTarget
            key={task.id}
            column={column}
            task={task}
            taskIndex={taskIndex}
            columnName={columnName}
            dropAllowed={dropAllowed}
          />
        ))}
      </DropZone>
    </div>
  );
}

function TaskColumnHeader({ column }: ColumnProps) {
  const modals = useModalsActions();

  const columnTitle = columnDisplayNames[column.columnType];
  const taskCount = column.tasks.length;
  const isWipLimitReached = isColumnWipLimitReached(column);
  const tagText = column.wipLimit !== null
    ? `${taskCount} / ${column.wipLimit}`
    : `${taskCount}`;

  return (
    <div className="is-flex is-justify-content-space-between is-align-items-center is-sticky p-4">
      <div className="is-flex is-align-items-center">
        <Tag
          text={tagText}
          color={isWipLimitReached ? "danger" : "light"}
          isRounded={true}
        />
        <p className="title is-4 pl-2"> {columnTitle} </p>
      </div>
      <div className="buttons">
        <IconButton
          icon="edit"
          color="warning"
          size="small"
          ariaLabel="Edit column"
          onClick={() => {
            modals.setColumn(openColumnModalWithColumn(column));
          }}
        />
        <IconButton
          icon="plus"
          color="link"
          size="small"
          state={isWipLimitReached ? "disabled" : "normal"}
          ariaLabel="Add task"
          dataTestId={`add-task-button-${column.columnType}`}
          onClick={() => {
            modals.setTask(openTaskModal(column.columnType));
          }}
        />
      </div>
    </div>
  );
}

type TaskDropTargetProps = ColumnProps & {
  task: Task;
  taskIndex: number;
  columnName: string;
  dropAllowed: boolean;
};

function TaskDropTarget({
  column,
  task,
  taskIndex,
  columnName,
  dropAllowed,
}: TaskDropTargetProps) {
  const boardActions = useBoardsActions();
  const { currentBoard } = useBoardsState();
  const modals = useModalsActions();

  const onDrop = (draggedItem: DraggableItemDto) => {
    moveTask(
      boardActions,
      currentBoard,
      column.columnType,
      draggedItem,
      task.id,
    );
  };

  return (
    <DropZone
      className="kanban-task-drop-target"
      dataTestId={`${column.columnType}-task-drop-target-${taskIndex}`}
      onDrop={onDrop}
      dropAllowed={dropAllowed}
    >
      <DraggableItem
        data={createDraggableItemDto(task.id, column.columnType)}
        dataTestId={`${column.columnType}-task-draggable-${taskIndex}`}
      >
        <TaskCard
          task={task}
          columnName={columnName}
          taskIndex={taskIndex}
          onEdit={() => {
            modals.setTask(openTaskModalWithTask(column.columnType, task));
          }}
          onDelete={() => {
            boardActions.deleteTaskFromCurrentBoard(task.id);
          }}
        />
      </DraggableItem>
    </DropZone>
  );
}

function moveTask(
  boardActions: BoardsActions,
  currentBoard: BoardsState["currentBoard"],
  targetColumnType: ColumnType,
  draggedItem: DraggableItemDto,
  beforeTaskId: TaskId | null,
) {
  const finishMeasurement = startPerformanceMeasurement(
    movePerformanceAction(draggedItem.sourceColumnType, targetColumnType),
    performanceContextFromBoard(currentBoard),
  );

  if (
    boardActions.moveTaskInCurrentBoard(
      draggedItem.taskId,
      targetColumnType,
      beforeTaskId,
    )
  ) {
    finishMeasurement();
  }
}

function movePerformanceAction(
  sourceColumnType: ColumnType,
  targetColumnType: ColumnType,
): PerformanceAction {
  return sourceColumnType === targetColumnType
    ? PerformanceAction.TaskMoveWithinColumn
    : PerformanceAction.TaskMoveBetweenColumns;
}
