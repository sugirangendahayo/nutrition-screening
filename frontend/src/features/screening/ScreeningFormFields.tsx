import { Input } from "@/components/ui/Input";
import { RadioGroup } from "@/components/ui/RadioGroup";
import { Select } from "@/components/ui/Select";
import type { FeatureField } from "@/types";
import type { FormValues } from "@/features/screening/formHelpers";

interface Props {
  fields: FeatureField[];
  values: FormValues;
  errors: Record<string, string>;
  onChange: (key: string, value: string) => void;
}

export function ScreeningFormFields({ fields, values, errors, onChange }: Props) {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
      {fields.map((field) => {
        const value = values[field.key] ?? "";
        const error = errors[field.key];

        if (field.inputType === "number") {
          return (
            <Input
              key={field.key}
              label={field.label}
              required={field.required}
              unit={field.unit ?? undefined}
              helpText={field.helpText ?? undefined}
              error={error}
              type="number"
              inputMode="decimal"
              step={field.step ?? undefined}
              min={field.min ?? undefined}
              max={field.max ?? undefined}
              value={value}
              onChange={(e) => onChange(field.key, e.target.value)}
            />
          );
        }

        if (field.inputType === "radio") {
          return (
            <RadioGroup
              key={field.key}
              name={field.key}
              label={field.label}
              required={field.required}
              helpText={field.helpText ?? undefined}
              error={error}
              value={value}
              onChange={(next) => onChange(field.key, next)}
              options={field.options}
            />
          );
        }

        return (
          <Select
            key={field.key}
            label={field.label}
            required={field.required}
            helpText={field.helpText ?? undefined}
            error={error}
            placeholder="Select..."
            value={value}
            onChange={(e) => onChange(field.key, e.target.value)}
            options={field.options}
          />
        );
      })}
    </div>
  );
}
