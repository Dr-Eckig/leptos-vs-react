type TextareaProps = {
  label: string;
  value: string;
  setValue: (value: string) => void;
  errorMessage?: string;
  placeholder?: string;
  hasFixedSize?: boolean;
};

export function Textarea({
  label,
  value,
  setValue,
  errorMessage,
  placeholder = "",
  hasFixedSize = false,
}: TextareaProps) {
  const hasError = Boolean(errorMessage);

  const textareaClassName = [
    "textarea",
    hasFixedSize && "has-fixed-size",
    hasError && "is-danger",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="field">
      <label className="label">{label}</label>

      <div className="control">
        <textarea
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
