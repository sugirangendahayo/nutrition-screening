import type { ReactNode } from "react";
import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";

import { cn } from "@/lib/cn";

type Tone = "info" | "success" | "warning" | "danger";

const toneConfig: Record<Tone, { classes: string; icon: ReactNode }> = {
  info: { classes: "bg-brand-50 text-brand-800 border-brand-200", icon: <Info className="size-5" /> },
  success: {
    classes: "bg-success-50 text-success-700 border-success-500/30",
    icon: <CheckCircle2 className="size-5" />,
  },
  warning: {
    classes: "bg-warning-50 text-warning-600 border-warning-500/30",
    icon: <AlertTriangle className="size-5" />,
  },
  danger: {
    classes: "bg-danger-50 text-danger-600 border-danger-500/30",
    icon: <XCircle className="size-5" />,
  },
};

interface AlertProps {
  tone?: Tone;
  title?: string;
  children?: ReactNode;
  className?: string;
}

export function Alert({ tone = "info", title, children, className }: AlertProps) {
  const config = toneConfig[tone];
  return (
    <div
      role={tone === "danger" ? "alert" : "status"}
      className={cn("flex gap-3 rounded-md border px-4 py-3 text-sm", config.classes, className)}
    >
      <div className="mt-0.5 shrink-0">{config.icon}</div>
      <div>
        {title && <p className="font-semibold">{title}</p>}
        {children && <div className={cn(title && "mt-0.5")}>{children}</div>}
      </div>
    </div>
  );
}
