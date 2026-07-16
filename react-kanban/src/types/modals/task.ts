import { useState } from "react";
import { formatDateToString } from "../date";
import { Priority, type ColumnType, type Task } from "../serialize";
import type { TaskValidationError, UserTask } from "../validation";

export type OpenTaskModal = {
  columnType: ColumnType | null;
  task: Task | null;
};

export function openTaskModal(columnType: ColumnType | null): OpenTaskModal {
  return {
    columnType,
    task: null,
  };
}

export function openTaskModalWithTask(
  columnType: ColumnType,
  task: Task,
): OpenTaskModal {
  return {
    columnType,
    task,
  };
}

export function useTaskForm(task: Task | null) {
  const [title, setTitle] = useState(task?.title ?? "");
  const [description, setDescription] = useState(task?.description ?? "");
  const [priority, setPriority] = useState<Priority>(
    task?.priority ?? Priority.Medium,
  );
  const [dueDate, setDueDate] = useState(
    task?.dueDate ? formatDateToString(task.dueDate) : "",
  );
  const [titleError, setTitleError] = useState<string>();
  const [priorityError, setPriorityError] = useState<string>();
  const [dueDateError, setDueDateError] = useState<string>();

  const userTask = (): UserTask => ({ title, description, priority, dueDate });
  const clearErrors = () => {
    setTitleError(undefined);
    setPriorityError(undefined);
    setDueDateError(undefined);
  };
  const setValidationError = (error: TaskValidationError) => {
    if (error === "TitleTooLong") {
      setTitleError("Please enter a title with at most 200 characters.");
    } else if (error === "EmptyTitle") {
      setTitleError("The title must not be empty.");
    } else if (error === "InvalidDueDate") {
      setDueDateError("Please enter a valid date.");
    } else {
      setPriorityError("Please select a valid priority.");
    }
  };

  return {
    title,
    setTitle,
    description,
    setDescription,
    priority,
    setPriority,
    dueDate,
    setDueDate,
    titleError,
    priorityError,
    dueDateError,
    userTask,
    clearErrors,
    setValidationError,
  };
}

export type TaskForm = ReturnType<typeof useTaskForm>;
