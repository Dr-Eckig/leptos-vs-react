import { createColumn, type Column, type ColumnType } from "../serialize";

export type ColumnValidationError = "InvalidWipLimit";

export type UserColumn = {
  columnType: ColumnType;
  wipLimit: string;
};

const U32_MAX = 4_294_967_295;
const UNSIGNED_INTEGER_PATTERN = /^\d+$/;

export function validateColumn(userColumn: UserColumn):
  | { ok: true; column: Column }
  | { ok: false; error: ColumnValidationError } {
  const normalizedLimit = userColumn.wipLimit.trim();

  if (!normalizedLimit) {
    return {
      ok: true,
      column: createColumn(userColumn.columnType, null),
    };
  }

  if (!UNSIGNED_INTEGER_PATTERN.test(normalizedLimit)) {
    return { ok: false, error: "InvalidWipLimit" };
  }

  const parsedLimit = Number(normalizedLimit);

  if (
    !Number.isSafeInteger(parsedLimit) ||
    parsedLimit < 0 ||
    parsedLimit > U32_MAX
  ) {
    return { ok: false, error: "InvalidWipLimit" };
  }

  return {
    ok: true,
    column: createColumn(userColumn.columnType, parsedLimit),
  };
}
