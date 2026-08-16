import type { ReactNode } from "react";
import { Minus, TrendingDown, TrendingUp, HelpCircle } from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import type { TrendStatus } from "@/types";

const config: Record<TrendStatus, { label: string; tone: "success" | "warning" | "neutral"; icon: ReactNode }> = {
  improving: { label: "Improving", tone: "success", icon: <TrendingDown className="size-3.5" /> },
  worsening: { label: "Worsening", tone: "warning", icon: <TrendingUp className="size-3.5" /> },
  stable: { label: "Stable", tone: "neutral", icon: <Minus className="size-3.5" /> },
  insufficient_data: {
    label: "Insufficient data",
    tone: "neutral",
    icon: <HelpCircle className="size-3.5" />,
  },
};

export function TrendBadge({ status }: { status: TrendStatus }) {
  const { label, tone, icon } = config[status];
  return (
    <Badge tone={tone} icon={icon}>
      {label}
    </Badge>
  );
}
