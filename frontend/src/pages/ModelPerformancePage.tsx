import { useEffect, useState } from "react";
import { BarChart3 } from "lucide-react";

import { getModelPerformance } from "@/api/model";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageSpinner } from "@/components/ui/Spinner";
import { formatDateTime } from "@/lib/format";
import type { ModelVersionRecord } from "@/types";

function MetricsTable({ metrics }: { metrics: NonNullable<ModelVersionRecord["metrics"]> }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {(["stunting", "underweight"] as const).map((target) => {
        const m = metrics[target];
        if (!m) return null;
        return (
          <div key={target} className="rounded-md border border-ink-200 p-4">
            <p className="mb-2 font-medium capitalize text-ink-900">{target}</p>
            <dl className="grid grid-cols-2 gap-2 text-sm">
              <dt className="text-ink-500">Accuracy</dt>
              <dd className="text-right font-medium">{(m.accuracy * 100).toFixed(1)}%</dd>
              <dt className="text-ink-500">Precision</dt>
              <dd className="text-right font-medium">{(m.precision * 100).toFixed(1)}%</dd>
              <dt className="text-ink-500">Recall</dt>
              <dd className="text-right font-medium">{(m.recall * 100).toFixed(1)}%</dd>
              <dt className="text-ink-500">F1-score</dt>
              <dd className="text-right font-medium">{(m.f1 * 100).toFixed(1)}%</dd>
              <dt className="text-ink-500">ROC-AUC</dt>
              <dd className="text-right font-medium">{m.rocAuc.toFixed(3)}</dd>
            </dl>
          </div>
        );
      })}
    </div>
  );
}

export function ModelPerformancePage() {
  const [versions, setVersions] = useState<ModelVersionRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getModelPerformance()
      .then((data) => setVersions(data.versions))
      .catch(() => setError("We couldn't load model performance data."));
  }, []);

  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!versions) return <PageSpinner label="Loading model performance..." />;

  return (
    <div className="flex flex-col gap-6">
      <Alert tone="info">
        Chapter 3 of the research compares Logistic Regression, Decision Tree, Random Forest, and
        Support Vector Machine using accuracy, precision, recall, F1-score, and ROC-AUC. Metrics
        below are populated once a model has been trained and evaluated offline - values are never
        invented.
      </Alert>

      {versions.length === 0 ? (
        <EmptyState
          icon={<BarChart3 className="size-10" />}
          title="No evaluation results recorded yet"
          description="Once a model is trained and evaluated, its metrics will appear here."
        />
      ) : (
        versions.map((version) => (
          <Card key={version.id}>
            <CardHeader className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <CardTitle>{version.version}</CardTitle>
                <p className="mt-1 text-sm text-ink-500">
                  {version.trained_at ? `Trained ${formatDateTime(version.trained_at)}` : "Training date not recorded"}
                </p>
              </div>
              <div className="flex gap-2">
                <Badge tone={version.mode === "real" ? "brand" : "warning"}>{version.mode}</Badge>
                {version.is_active && <Badge tone="success">Active</Badge>}
              </div>
            </CardHeader>
            <CardContent>
              {version.metrics ? (
                <MetricsTable metrics={version.metrics} />
              ) : (
                <p className="text-sm text-ink-500">
                  No evaluation metrics have been recorded for this model version yet.
                </p>
              )}
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}
