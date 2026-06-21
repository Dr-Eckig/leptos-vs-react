export type FontawesomeIcon =
  | "circlePlus"
  | "download"
  | "edit"
  | "ellipsis"
  | "ellipsisVertical"
  | "plus"
  | "trash"
  | "reset";

export const iconClasses: Record<FontawesomeIcon, string> = {
  circlePlus: "fa-solid fa-circle-plus",
  download: "fa-solid fa-circle-down",
  edit: "fa-solid fa-pen",
  ellipsis: "fa-solid fa-ellipsis",
  ellipsisVertical: "fa-solid fa-ellipsis-vertical",
  plus: "fa-solid fa-plus",
  trash: "fa-solid fa-trash-can",
  reset: "fa-solid fa-arrow-rotate-left",
};
