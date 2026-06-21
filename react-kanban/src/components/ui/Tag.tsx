import type { HTMLAttributes } from "react";
import {
  type Color,
  type Size,
  colorClasses,
  sizeClasses,
} from "../../types/ui";

type TagProps = {
  text: string;
  color?: Color;
  size?: Size;
  isRounded?: boolean;
  isLight?: boolean;
} & HTMLAttributes<HTMLSpanElement>;

export function Tag({
  text,
  color = "none",
  size = "normal",
  isRounded = false,
  isLight = false,
  ...spanProps
}: TagProps) {
  const className = [
    "tag",
    colorClasses[color],
    sizeClasses[size],
    isRounded && "is-rounded",
    isLight && "is-light",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <span {...spanProps} className={className}>
      {text}
    </span>
  );
}