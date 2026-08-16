import type { FeatureField, ModelSchema } from "@/types";

export type FormValues = Record<string, string>;

export function groupFieldsBySection(schema: ModelSchema): Map<string, FeatureField[]> {
  const grouped = new Map<string, FeatureField[]>();
  for (const section of [...schema.sections].sort((a, b) => a.order - b.order)) {
    grouped.set(
      section.key,
      schema.fields.filter((field) => field.section === section.key)
    );
  }
  return grouped;
}

export function initialValues(schema: ModelSchema): FormValues {
  const values: FormValues = {};
  for (const field of schema.fields) {
    values[field.key] = "";
  }
  return values;
}

export function validateField(field: FeatureField, rawValue: string): string | null {
  const isMissing = rawValue === "" || rawValue === undefined || rawValue === null;

  if (isMissing) {
    return field.required ? `${field.label} is required.` : null;
  }

  if (field.inputType === "number") {
    const value = Number(rawValue);
    if (Number.isNaN(value)) {
      return `Please enter a valid number for ${field.label.toLowerCase()}.`;
    }
    if (field.min !== null && value < field.min) {
      return `${field.label} must be at least ${field.min}${field.unit ? ` ${field.unit}` : ""}.`;
    }
    if (field.max !== null && value > field.max) {
      return `${field.label} must be no more than ${field.max}${field.unit ? ` ${field.unit}` : ""}.`;
    }
    return null;
  }

  const validValues = new Set(field.options.map((option) => option.value));
  if (!validValues.has(rawValue)) {
    return `Please select a valid option for ${field.label.toLowerCase()}.`;
  }
  return null;
}

export function validateForm(schema: ModelSchema, values: FormValues): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const field of schema.fields) {
    const error = validateField(field, values[field.key] ?? "");
    if (error) errors[field.key] = error;
  }
  return errors;
}

export function toInputData(schema: ModelSchema, values: FormValues): Record<string, string | number> {
  const result: Record<string, string | number> = {};
  for (const field of schema.fields) {
    const raw = values[field.key];
    if (raw === "" || raw === undefined) continue;
    result[field.key] = field.inputType === "number" ? Number(raw) : raw;
  }
  return result;
}
