import type { ColumnType } from "./serialize";
import type { TaskId } from "./state";

export const DRAGGABLE_ITEM_MIME_TYPE = "application/x-kanban-task+json";
export const DRAGGABLE_ITEM_TEXT_FALLBACK = "text/plain";

export type DraggableItemDto = {
  taskId: TaskId;
  sourceColumnType: ColumnType;
};

export function createDraggableItemDto(
  taskId: TaskId,
  sourceColumnType: ColumnType,
): DraggableItemDto {
  return {
    taskId,
    sourceColumnType,
  };
}

export function draggableItemFromPayload(
  payload: string,
): DraggableItemDto | null {
  try {
    const parsed = JSON.parse(payload) as Partial<DraggableItemDto>;

    if (!parsed.taskId || !parsed.sourceColumnType) {
      return null;
    }

    return {
      taskId: parsed.taskId,
      sourceColumnType: parsed.sourceColumnType,
    };
  } catch {
    return null;
  }
}

export function draggableItemToPayload(data: DraggableItemDto): string | null {
  try {
    return JSON.stringify(data);
  } catch {
    return null;
  }
}
