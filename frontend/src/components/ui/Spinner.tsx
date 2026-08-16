import { Loader2 } from "lucide-react";

import { cn } from "@/lib/cn";

export function Spinner({ label, className }: { label?: string; className?: string }) {
  return (
    <div className={cn("flex items-center gap-2 text-sm text-ink-500", className)} role="status">
      <Loader2 className="size-4 animate-spin" aria-hidden="true" />
      <span>{label ?? "Loading..."}</span>
    </div>
  );
}

export function PageSpinner({ label }: { label?: string }) {
  return (
    <div className="flex h-64 w-full items-center justify-center">
      <Spinner label={label} />
    </div>
  );
}
