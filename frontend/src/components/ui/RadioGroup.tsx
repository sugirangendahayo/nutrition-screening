import type { ReactNode } from "react";

interface RadioGroupProps {
  label: string;
  labelBadge?: ReactNode;
  name: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  required?: boolean;
  error?: string;
  helpText?: string;
}

export function RadioGroup({
  label,
  labelBadge,
  name,
  value,
  onChange,
  options,
  required,
  error,
  helpText,
}: RadioGroupProps) {
  return (
    <fieldset className="flex flex-col gap-1.5">
      <legend className="flex items-center gap-2 text-sm font-medium text-ink-800">
        {label} {required && <span className="text-danger-500">*</span>}
        {labelBadge}
      </legend>
      <div className="flex flex-wrap gap-4 pt-1">
        {options.map((option) => (
          <label
            key={option.value}
            className="inline-flex items-center gap-2 text-sm text-ink-700"
          >
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              className="size-4 accent-brand-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500"
            />
            {option.label}
          </label>
        ))}
      </div>
      {error ? (
        <p className="text-sm text-danger-600">{error}</p>
      ) : helpText ? (
        <p className="text-sm text-ink-500">{helpText}</p>
      ) : null}
    </fieldset>
  );
}
