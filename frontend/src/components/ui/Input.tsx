import { forwardRef, useId, type InputHTMLAttributes, type ReactNode } from "react";

import { cn } from "@/lib/cn";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  labelBadge?: ReactNode;
  error?: string;
  helpText?: string;
  unit?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, labelBadge, error, helpText, unit, className, id, required, ...props }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const errorId = `${inputId}-error`;
    const helpId = `${inputId}-help`;

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="flex items-center gap-2 text-sm font-medium text-ink-800">
            {label} {required && <span className="text-danger-500">*</span>}
            {labelBadge}
          </label>
        )}
        <div className="relative">
          <input
            ref={ref}
            id={inputId}
            aria-invalid={!!error}
            aria-describedby={error ? errorId : helpText ? helpId : undefined}
            className={cn(
              "h-10 w-full rounded-md border bg-white px-3 text-sm text-ink-900 placeholder:text-ink-400",
              "focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20",
              error ? "border-danger-500" : "border-ink-300",
              unit && "pr-14",
              className
            )}
            {...props}
          />
          {unit && (
            <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-sm text-ink-400">
              {unit}
            </span>
          )}
        </div>
        {error ? (
          <p id={errorId} className="text-sm text-danger-600">
            {error}
          </p>
        ) : helpText ? (
          <p id={helpId} className="text-sm text-ink-500">
            {helpText}
          </p>
        ) : null}
      </div>
    );
  }
);
Input.displayName = "Input";
