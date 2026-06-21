import type { InputHTMLAttributes } from "react";
import {
  type InputType,
  inputHtmlTypes,
} from "../../types/ui";

type InputProps = {
  label?: string;
  value: string;
  setValue: (value: string) => void;
  errorMessage?: string;
  inputType?: InputType;
  min?: number;
  placeholder?: string;
  dataTestId?: string;
} & Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "value" | "onChange" | "type" | "min" | "placeholder"
>;

export function Input({
  label,
  value,
  setValue,
  errorMessage,
  inputType = "text",
  min,
  placeholder = "",
  dataTestId,
  ...inputProps
}: InputProps) {
  const hasError = Boolean(errorMessage);

  return (
    <div className="field">
      {label && <label className="label">{label}</label>}

      <div className="control">
        <input
          {...inputProps}
          style={inputType === "date" ? { width: "auto" } : undefined}
          className={["input", hasError && "is-danger"]
            .filter(Boolean)
            .join(" ")}
          type={inputHtmlTypes[inputType]}
          placeholder={placeholder}
          min={min}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          data-testid={dataTestId}
        />
      </div>

      {hasError && <p className="help is-danger">{errorMessage}</p>}
    </div>
  );
}
