import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Printer } from "lucide-react";

import { generateReport, type ReportData } from "@/api/reports";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { PageSpinner } from "@/components/ui/Spinner";
import { ExplanationList, ExplanationMethodLabel } from "@/features/results/ExplanationList";
import { formatDateTime, formatProbability } from "@/lib/format";

const TARGET_LABELS: Record<string, string> = { stunting: "Stunting", underweight: "Underweight" };

export function ReportViewPage() {
  const { assessmentId } = useParams<{ assessmentId: string }>();
  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!assessmentId) return;
    generateReport(assessmentId)
      .then(setReport)
      .catch(() => setError("We couldn't generate this report."));
  }, [assessmentId]);

  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!report) return <PageSpinner label="Preparing report..." />;

  const { assessment, inputSummary, trend } = report;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="no-print flex justify-end">
        <Button onClick={() => window.print()}>
          <Printer className="size-4" aria-hidden="true" />
          Print / Save as PDF
        </Button>
      </div>

      <div className="rounded-lg border border-ink-200 bg-white p-8 print:border-0 print:shadow-none">
        <header className="mb-6 border-b border-ink-200 pb-6">
          <h1 className="text-xl font-semibold text-ink-900">Nutrition Screening Report</h1>
          <p className="mt-1 text-sm text-ink-500">Generated {formatDateTime(new Date().toISOString())}</p>
        </header>

        <section className="mb-6 grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-ink-500">Child ID</p>
            <p className="font-medium text-ink-900">{assessment.child.child_code}</p>
          </div>
          <div>
            <p className="text-ink-500">Sex</p>
            <p className="font-medium capitalize text-ink-900">{assessment.child.sex}</p>
          </div>
          <div>
            <p className="text-ink-500">Assessment date</p>
            <p className="font-medium text-ink-900">{formatDateTime(assessment.assessedAt)}</p>
          </div>
          <div>
            <p className="text-ink-500">Assessed by</p>
            <p className="font-medium text-ink-900">{assessment.performedByName ?? "Not available"}</p>
          </div>
        </section>

        <section className="mb-6">
          <h2 className="mb-3 text-base font-semibold text-ink-900">Screening Results</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {Object.entries(assessment.predictions).map(([target, prediction]) => (
              <div key={target} className="rounded-md border border-ink-200 p-4">
                <div className="flex items-center justify-between">
                  <p className="font-medium text-ink-900">{TARGET_LABELS[target] ?? target}</p>
                  <RiskBadge label={prediction.predictedLabel} />
                </div>
                <p className="mt-2 text-sm text-ink-600">
                  Probability: {formatProbability(prediction.probability)}
                </p>
                <p className="mt-1 text-xs text-ink-500">
                  Model: {prediction.modelVersion} ({prediction.algorithm})
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-6">
          <h2 className="mb-3 text-base font-semibold text-ink-900">Input Summary</h2>
          <table className="w-full text-sm">
            <tbody>
              {inputSummary.map((item) => (
                <tr key={item.label} className="border-b border-ink-100 last:border-0">
                  <td className="py-1.5 pr-4 text-ink-500">{item.label}</td>
                  <td className="py-1.5 font-medium text-ink-900">
                    {item.value}
                    {item.unit ? ` ${item.unit}` : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="mb-6">
          <h2 className="mb-3 text-base font-semibold text-ink-900">Prediction Explanation</h2>
          {assessment.explanations.map((explanation) => (
            <div key={explanation.target} className="mb-4">
              <p className="mb-1 text-sm font-medium text-ink-800">
                {TARGET_LABELS[explanation.target] ?? explanation.target}
              </p>
              <p className="mb-2 text-xs text-ink-500">
                <ExplanationMethodLabel method={explanation.method} />
              </p>
              <ExplanationList items={explanation.items} />
            </div>
          ))}
        </section>

        <section className="mb-6">
          <h2 className="mb-3 text-base font-semibold text-ink-900">Previous Assessment / Trend</h2>
          {trend.status === "insufficient_data" ? (
            <p className="text-sm text-ink-500">Insufficient historical data for a trend.</p>
          ) : (
            <p className="text-sm text-ink-700">
              Overall trend: <span className="font-medium capitalize">{trend.overall.replace("_", " ")}</span>
            </p>
          )}
        </section>

        <footer className="border-t border-ink-200 pt-4 text-xs text-ink-500">
          This report is generated by a machine learning-based decision support system. It is
          intended to assist nutrition screening decisions and does not constitute a medical
          diagnosis. Findings should be reviewed by a qualified health professional.
        </footer>
      </div>
    </div>
  );
}
