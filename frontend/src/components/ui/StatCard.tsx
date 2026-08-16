import type { ReactNode } from "react";

import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

interface StatCardProps {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
  hint?: string;
  tone?: "neutral" | "brand" | "warning";
}

const iconToneClasses: Record<NonNullable<StatCardProps["tone"]>, string> = {
  neutral: "bg-ink-100 text-ink-600",
  brand: "bg-brand-50 text-brand-600",
  warning: "bg-warning-50 text-warning-600",
};

export function StatCard({ label, value, icon, hint, tone = "neutral" }: StatCardProps) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-ink-500">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-ink-900">{value}</p>
          {hint && <p className="mt-1 text-xs text-ink-400">{hint}</p>}
        </div>
        {icon && (
          <div className={cn("rounded-md p-2", iconToneClasses[tone])} aria-hidden="true">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
