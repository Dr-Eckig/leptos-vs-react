import type { Temporal } from "@js-temporal/polyfill";
import { createId } from "../utility";

export type TaskId = string;

export enum Priority {
  Low = "Low",
  Medium = "Medium",
  High = "High",
}

export type Task = {
  id: TaskId;
  title: string;
  description: string | null;
  dueDate: Temporal.PlainDate | null;
  priority: Priority;
};

export type RawTask = {
  id?: TaskId;
  title: string;
  description?: string | null;
  dueDate?: string | null;
  priority: Priority;
};

export function createTask(
  title: string,
  description: string | null,
  dueDate: Temporal.PlainDate | null,
  priority: Priority,
): Task {
  return {
    id: createId(),
    title,
    description,
    dueDate,
    priority,
  };
}
