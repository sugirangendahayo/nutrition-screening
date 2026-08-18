import { AlertTriangle, ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import type { LabelConfidence } from "@/types";

/**
 * Some raw MICS6 predictor codes could not be matched to a confirmed
 * human-readable label/category set (the training notebook never printed
 * the dataset's SPSS value labels, and no codebook was available at
 * integration time - see docs/MODEL_INTEGRATION.md). Rather than guessing,
 * those fields are visibly flagged here so users and administrators know
 * exactly which fields still need verification against the MICS6 CAR
 * codebook.
 */
export function LabelConfidenceBadge({ confidence }: { confidence: LabelConfidence }) {
  if (confidence === "confirmed") return null;

  if (confidence === "unverified") {
    return (
      <Badge tone="warning" icon={<AlertTriangle className="size-3" />}>
        Unverified label
      </Badge>
    );
  }

  return (
    <Badge tone="neutral" icon={<ShieldCheck className="size-3" />}>
      Standard convention
    </Badge>
  );
}
