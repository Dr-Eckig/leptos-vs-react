import type { FontawesomeIcon } from "./icons";
import { iconClasses } from "./icons";
import {
  type Color,
  textColorClasses,
} from "../../types/ui";

type IconTextProps = {
  icon: FontawesomeIcon;
  text: string;
  color?: Color;
  textColor?: boolean;
};

export function IconText({
  icon,
  text,
  color = "none",
  textColor = false,
}: IconTextProps) {
  const textColorClass = textColor ? textColorClasses[color] : "";

  const iconTextClassName = [
    "icon-text",
    textColorClass,
  ]
    .filter(Boolean)
    .join(" ");

  const iconClassName = [
    "icon",
    textColorClasses[color],
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={iconTextClassName}>
      <span className={iconClassName}>
        <i className={iconClasses[icon]} />
      </span>

      <span>{text}</span>
    </div>
  );
}