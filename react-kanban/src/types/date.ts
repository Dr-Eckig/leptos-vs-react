import { Temporal } from "@js-temporal/polyfill";

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

export function parseDateFromString(input: string): Temporal.PlainDate | null {
  if (!DATE_PATTERN.test(input)) {
    return null;
  }

  try {
    return Temporal.PlainDate.from(input, { overflow: "reject" });
  } catch {
    return null;
  }
}

export function formatDateToString(date: Temporal.PlainDate): string {
  return date.toString();
}

export function formatDateToDisplay(date: Temporal.PlainDate): string {
  return [
    formatDatePart(date.day),
    formatDatePart(date.month),
    String(date.year).padStart(4, "0"),
  ].join(".");
}

function formatDatePart(value: number): string {
  return String(value).padStart(2, "0");
}
