import type { SelectHTMLAttributes } from "react";

type SelectProps = {
  label: string;
  options: string[];
  value: string;
  setValue: (value: string) => void;
  errorMessage?: string;
} & Omit<SelectHTMLAttributes<HTMLSelectElement>, "value" | "onChange">;

export function Select({
  label,
  options,
  value,
  setValue,
  errorMessage,
  ...selectProps
}: SelectProps) {
  const hasError = Boolean(errorMessage);

  return (
    <div className="field">
      <label className="label">{label}</label>

      <div className="control">
        <div className={["select", hasError && "is-danger"].filter(Boolean).join(" ")}>
          <select
            {...selectProps}
            value={value}
            onChange={(event) => setValue(event.target.value)}
          >
            {options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>

      {hasError && <p className="help is-danger">{errorMessage}</p>}
    </div>
  );
}
