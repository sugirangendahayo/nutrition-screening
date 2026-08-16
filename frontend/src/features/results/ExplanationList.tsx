import { ArrowDownRight, ArrowUpRight } from "lucide-react";

import type { ExplanationItem, ExplanationMethod } from "@/types";

const METHOD_LABELS: Record<ExplanationMethod, string> = {
  shap_local: "Local explanation (SHAP)",
  global_importance: "Model Feature Importance",
  development_mock: "Development placeholder explanation",
  unavailable: "Explanation unavailable",
};

export function ExplanationMethodLabel({ method }: { method: ExplanationMethod }) {
  return <span>{METHOD_LABELS[method]}</span>;
}

export function ExplanationList({ items }: { items: ExplanationItem[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-ink-500">No explanation data is available for this result.</p>;
  }

  const maxAbs = Math.max(...items.map((item) => Math.abs(item.contribution)), 0.0001);

  return (
    <ul className="flex flex-col gap-3">
      {items.map((item) => {
        const widthPercent = Math.max(6, (Math.abs(item.contribution) / maxAbs) * 100);
        const increases = item.direction === "increases_risk";
        return (
          <li key={item.featureKey} className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium text-ink-800">{item.featureLabel}</span>
              <span
                className={
                  "flex items-center gap-1 text-xs font-medium " +
                  (increases ? "text-warning-600" : item.direction === "decreases_risk" ? "text-success-700" : "text-ink-500")
                }
              >
                {increases ? (
                  <ArrowUpRight className="size-3.5" aria-hidden="true" />
                ) : item.direction === "decreases_risk" ? (
                  <ArrowDownRight className="size-3.5" aria-hidden="true" />
                ) : null}
                {increases ? "Increases risk" : item.direction === "decreases_risk" ? "Decreases risk" : "Neutral"}
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-ink-100">
              <div
                className={"h-full rounded-full " + (increases ? "bg-warning-500" : "bg-success-500")}
                style={{ width: `${widthPercent}%` }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
