import { createTask, Priority, type Task } from "../serialize";
import { parseDateFromString } from "../date";

export type TaskValidationError =
  | "EmptyTitle"
  | "TitleTooLong"
  | "InvalidDueDate"
  | "InvalidPriority";

export type UserTask = {
  title: string;
  description: string;
  dueDate: string;
  priority: string;
};

const validPriorities = new Set<Priority>(Object.values(Priority));

export function validateTask(userTask: UserTask):
  | { ok: true; task: Task }
  | { ok: false; error: TaskValidationError } {
  const title = userTask.title.trim();

  if (!title) {
    return { ok: false, error: "EmptyTitle" };
  }

  if (title.length > 200) {
    return { ok: false, error: "TitleTooLong" };
  }

  const dueDate = userTask.dueDate.trim();
  const parsedDueDate = dueDate ? parseDateFromString(dueDate) : null;
  if (dueDate && !parsedDueDate) {
    return { ok: false, error: "InvalidDueDate" };
  }

  if (!validPriorities.has(userTask.priority as Priority)) {
    return { ok: false, error: "InvalidPriority" };
  }

  return {
    ok: true,
    task: createTask(
      title,
      userTask.description.trim() ? userTask.description.trim() : null,
      parsedDueDate,
      userTask.priority as Priority,
    ),
  };
}
