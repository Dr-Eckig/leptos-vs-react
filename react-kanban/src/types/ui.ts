export type Color =
  | "none"
  | "primary"
  | "link"
  | "info"
  | "success"
  | "warning"
  | "danger"
  | "white"
  | "light"
  | "dark"
  | "black"
  | "text"
  | "ghost";

export type Size = "small" | "normal" | "medium" | "large";

export type ButtonState = "normal" | "loading" | "disabled";

export type Alignment = "left" | "right";

export type InputType = "text" | "date" | "email" | "password" | "number";

export const DEFAULT_COLOR: Color = "none";
export const DEFAULT_SIZE: Size = "normal";
export const DEFAULT_BUTTON_STATE: ButtonState = "normal";
export const DEFAULT_ALIGNMENT: Alignment = "left";
export const DEFAULT_INPUT_TYPE: InputType = "text";

export const colorClasses: Record<Color, string> = {
  none: "",
  primary: "is-primary",
  link: "is-link",
  info: "is-info",
  success: "is-success",
  warning: "is-warning",
  danger: "is-danger",
  white: "is-white",
  light: "is-light",
  dark: "is-dark",
  black: "is-black",
  text: "is-text",
  ghost: "is-ghost",
};

export const textColorClasses: Record<Color, string> = {
  none: "",
  primary: "has-text-primary",
  link: "has-text-link",
  info: "has-text-info",
  success: "has-text-success",
  warning: "has-text-warning",
  danger: "has-text-danger",
  white: "has-text-white",
  light: "has-text-light",
  dark: "has-text-dark",
  black: "has-text-black",
  text: "",
  ghost: "",
};

export const sizeClasses: Record<Size, string> = {
  small: "is-small",
  normal: "",
  medium: "is-medium",
  large: "is-large",
};

export const buttonStateClasses: Record<ButtonState, string> = {
  normal: "",
  loading: "is-loading",
  disabled: "",
};

export const alignmentClasses: Record<Alignment, string> = {
  left: "",
  right: "is-right",
};

export const inputHtmlTypes: Record<InputType, string> = {
  text: "text",
  date: "date",
  email: "email",
  password: "password",
  number: "number",
};
