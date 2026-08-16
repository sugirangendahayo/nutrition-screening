import { AlertCircle, CheckCircle2 } from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import type { PredictedLabel } from "@/types";

export function RiskBadge({ label }: { label: PredictedLabel | null | undefined }) {
  if (!label) {
    return <Badge tone="neutral">No result</Badge>;
  }
  if (label === "at_risk") {
    return (
      <Badge tone="warning" icon={<AlertCircle className="size-3.5" />}>
        At Risk
      </Badge>
    );
  }
  return (
    <Badge tone="success" icon={<CheckCircle2 className="size-3.5" />}>
      Not At Risk
    </Badge>
  );
}
