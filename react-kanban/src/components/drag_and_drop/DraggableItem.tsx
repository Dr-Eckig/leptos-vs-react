import { useState, type DragEvent, type ReactNode } from "react";
import { useDragAndDropActions } from "../../hooks";
import {
  DRAGGABLE_ITEM_MIME_TYPE,
  DRAGGABLE_ITEM_TEXT_FALLBACK,
  draggableItemToPayload,
  type DraggableItemDto,
} from "../../types/drag_and_drop";

type DraggableItemProps = {
  data: DraggableItemDto;
  dataTestId?: string;
  children: ReactNode;
};

export function DraggableItem({
  data,
  dataTestId,
  children,
}: DraggableItemProps) {
  const { setDraggedItem } = useDragAndDropActions();
  const [isDragging, setIsDragging] = useState(false);

  const htmlClass = `kanban-draggable-item ${isDragging ? "is-dragging" : ""}`;

  const handleDragStart = (event: DragEvent<HTMLDivElement>) => {
    setIsDragging(true);
    setDraggedItem(data);

    event.dataTransfer.effectAllowed = "move";

    const payload = draggableItemToPayload(data);
    if (payload) {
      event.dataTransfer.setData(DRAGGABLE_ITEM_MIME_TYPE, payload);
      event.dataTransfer.setData(DRAGGABLE_ITEM_TEXT_FALLBACK, payload);
    }
  };

  const handleDragEnd = () => {
    setIsDragging(false);
    setDraggedItem(null);
  };

  return (
    <div
      className={htmlClass}
      draggable={true}
      data-testid={dataTestId}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      { children }
    </div>
  );
}
