import type { TextareaHTMLAttributes } from "react";

type TextareaProps = {
  label: string;
  value: string;
  setValue: (value: string) => void;
  errorMessage?: string;
  placeholder?: string;
  hasFixedSize?: boolean;
} & Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "value" | "onChange" | "placeholder">;

export function Textarea({
  label,
  value,
  setValue,
  errorMessage,
  placeholder = "",
  hasFixedSize = false,
  className,
  ...textareaProps
}: TextareaProps) {
  const hasError = Boolean(errorMessage);

  const textareaClassName = [
    "textarea",
    hasFixedSize && "has-fixed-size",
    hasError && "is-danger",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="field">
      <label className="label">{label}</label>

      <div className="control">
        <textarea
          {...textareaProps}
          className={textareaClassName}
          placeholder={placeholder}
          value={value}
          onChange={(event) => setValue(event.target.value)}
        />
      </div>

      {hasError && <p className="help is-danger">{errorMessage}</p>}
    </div>
  );
}