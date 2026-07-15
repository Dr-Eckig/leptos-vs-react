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
};

export function Tag({
  text,
  color = "none",
  size = "normal",
  isRounded = false,
  isLight = false,
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
    <span className={className}>
      {text}
    </span>
  );
}
