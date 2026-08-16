import { Alert } from "@/components/ui/Alert";
import { TargetResultCard } from "@/features/results/TargetResultCard";
import { TrendPanel } from "@/features/results/TrendPanel";
import type { PredictionResponse } from "@/types";

export function PredictionResultView({ result }: { result: PredictionResponse }) {
  const explanationByTarget = new Map(result.explanations.map((e) => [e.target, e]));

  return (
    <div className="flex flex-col gap-6">
      {result.mode === "mock" && (
        <Alert tone="warning" title="Development mode result">
          This result was produced by a placeholder model for testing the screening workflow. It
          is not a validated nutrition-science prediction and must not be used for real screening
          decisions.
        </Alert>
      )}

      <Alert tone="info" title="Decision support only">
        This system assists screening decisions. It does not provide a medical diagnosis and does
        not replace the judgment of a qualified health professional.
      </Alert>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {result.targets.map((target) => (
          <TargetResultCard
            key={target.target}
            prediction={target}
            explanation={explanationByTarget.get(target.target)}
          />
        ))}
      </div>

      {result.trendPreview && <TrendPanel trend={result.trendPreview} />}
    </div>
  );
}
