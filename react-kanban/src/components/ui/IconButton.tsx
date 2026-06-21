import type { ButtonHTMLAttributes } from "react";
import type { FontawesomeIcon } from "./icons";
import {
  type ButtonState,
  type Color,
  type Size,
  colorClasses,
  sizeClasses,
  buttonStateClasses,
} from "../../types/ui";
import { iconClasses } from "./icons";

type IconButtonProps = {
  icon: FontawesomeIcon;
  color?: Color;
  size?: Size;
  state?: ButtonState;
  onClick: () => void;
  ariaLabel: string;
  dataTestId?: string;
} & Omit<ButtonHTMLAttributes<HTMLButtonElement>, "onClick">;

export function IconButton({
  icon,
  color = "none",
  size = "normal",
  state = "normal",
  onClick,
  ariaLabel,
  dataTestId,
  ...buttonProps
}: IconButtonProps) {
  const buttonClassName = [
    "button",
    colorClasses[color],
    sizeClasses[size],
    buttonStateClasses[state],
  ]
    .filter(Boolean)
    .join(" ");

  const iconClassName = [iconClasses[icon], sizeClasses[size]]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      {...buttonProps}
      className={buttonClassName}
      disabled={state === "disabled"}
      onClick={onClick}
      aria-label={ariaLabel}
      data-testid={dataTestId}
    >
      <span className="icon">
        <i className={iconClassName} />
      </span>
    </button>
  );
}
