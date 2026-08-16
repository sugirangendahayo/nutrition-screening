import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ExplanationList, ExplanationMethodLabel } from "@/features/results/ExplanationList";
import { formatProbability } from "@/lib/format";
import type { PredictionTarget, TargetExplanation, TargetPrediction } from "@/types";

const TARGET_LABELS: Record<PredictionTarget, string> = {
  stunting: "Stunting",
  underweight: "Underweight",
};

const TARGET_DESCRIPTIONS: Record<PredictionTarget, string> = {
  stunting: "Reflects low height-for-age, a marker of chronic undernutrition.",
  underweight: "Reflects low weight-for-age, a marker of acute or chronic undernutrition.",
};

export function TargetResultCard({
  prediction,
  explanation,
}: {
  prediction: TargetPrediction;
  explanation?: TargetExplanation;
}) {
  const barPercent = prediction.probability !== null ? Math.round(prediction.probability * 100) : null;

  return (
    <Card>
      <CardHeader className="flex items-start justify-between">
        <div>
          <CardTitle>{TARGET_LABELS[prediction.target]}</CardTitle>
          <p className="mt-1 text-sm text-ink-500">{TARGET_DESCRIPTIONS[prediction.target]}</p>
        </div>
        <RiskBadge label={prediction.predictedLabel} />
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <div>
          <div className="flex items-center justify-between text-sm text-ink-600">
            <span>Prediction probability</span>
            <span className="font-semibold text-ink-900">{formatProbability(prediction.probability)}</span>
          </div>
          {barPercent !== null && (
            <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-ink-100">
              <div
                className="h-full rounded-full bg-brand-600"
                style={{ width: `${barPercent}%` }}
                role="progressbar"
                aria-valuenow={barPercent}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            </div>
          )}
        </div>

        {explanation && (
          <div>
            <p className="mb-1 text-sm font-semibold text-ink-800">Why this result?</p>
            <p className="mb-3 text-xs text-ink-500">
              <ExplanationMethodLabel method={explanation.method} /> - {explanation.note}
            </p>
            <ExplanationList items={explanation.items} />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
