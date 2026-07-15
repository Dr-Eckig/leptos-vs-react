import type { FontawesomeIcon } from "./icons";
import { iconClasses } from "./icons";
import {
  type ButtonState,
  type Color,
  type Size,
  buttonStateClasses,
  colorClasses,
  sizeClasses,
} from "../../types/ui";

type ButtonProps = {
  text: string;
  icon?: FontawesomeIcon;
  color?: Color;
  size?: Size;
  state?: ButtonState;
  isFullwidth?: boolean;
  ariaLabel: string;
  dataTestId?: string;
  onClick: () => void;
};

export function Button({
  text,
  icon,
  color = "none",
  size = "normal",
  state = "normal",
  isFullwidth = false,
  ariaLabel,
  dataTestId,
  onClick,
}: ButtonProps) {
  const buttonClassName = [
    "button",
    colorClasses[color],
    sizeClasses[size],
    buttonStateClasses[state],
    isFullwidth && "is-fullwidth",
  ]
    .filter(Boolean)
    .join(" ");

  const iconClassName =
    icon &&
    [iconClasses[icon], sizeClasses[size]]
      .filter(Boolean)
      .join(" ");

  return (
    <button
      className={buttonClassName}
      disabled={state === "disabled"}
      onClick={onClick}
      aria-label={ariaLabel}
      data-testid={dataTestId}
    >
      {icon && (
        <span className="icon">
          <i className={iconClassName} />
        </span>
      )}

      <span>{text}</span>
    </button>
  );
}
