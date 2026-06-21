import { useRef, useState, type DragEvent, type ReactNode } from "react";
import {
  DRAGGABLE_ITEM_MIME_TYPE,
  DRAGGABLE_ITEM_TEXT_FALLBACK,
  draggableItemFromPayload,
  type DraggableItemDto,
} from "../../types/drag_and_drop";

type DropZoneProps = {
  className?: string;
  onDrop: (draggedItem: DraggableItemDto) => void;
  dropAllowed?: boolean;
  children: ReactNode;
};

export function DropZone({
  className = "",
  onDrop,
  dropAllowed = true,
  children,
}: DropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const dragCounter = useRef(0);

  const htmlClass = `${className} kanban-drop-zone ${isDragOver ? "is-drag-over" : ""} ${
    isDragOver && !dropAllowed ? "disabled-drop" : ""
  }`.trim();

  const readDraggedItem = (event: DragEvent<HTMLDivElement>) => {
    const payload =
      event.dataTransfer.getData(DRAGGABLE_ITEM_MIME_TYPE) ||
      event.dataTransfer.getData(DRAGGABLE_ITEM_TEXT_FALLBACK);

    return payload ? draggableItemFromPayload(payload) : null;
  };

  const handleDragEnter = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    dragCounter.current += 1;
    setIsDragOver(true);
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    event.dataTransfer.dropEffect = dropAllowed ? "move" : "none";
  };

  const handleDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDragOver(false);
    }
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    dragCounter.current = 0;
    setIsDragOver(false);

    const draggedItem = readDraggedItem(event);
    if (draggedItem && dropAllowed) {
      onDrop(draggedItem);
    }
  };

  return (
    <div
      className={htmlClass}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {children}
    </div>
  );
}
