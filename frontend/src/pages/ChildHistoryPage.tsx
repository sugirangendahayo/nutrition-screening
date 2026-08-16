import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getChildHistory } from "@/api/children";
import { Alert } from "@/components/ui/Alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { PageSpinner } from "@/components/ui/Spinner";
import { TrendPanel } from "@/features/results/TrendPanel";
import { formatDateTime } from "@/lib/format";
import type { AssessmentSummary, Child, TrendResult } from "@/types";

export function ChildHistoryPage() {
  const { id } = useParams<{ id: string }>();
  const [child, setChild] = useState<Child | null>(null);
  const [assessments, setAssessments] = useState<AssessmentSummary[]>([]);
  const [trend, setTrend] = useState<TrendResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getChildHistory(id)
      .then((data) => {
        setChild(data.child);
        setAssessments(data.assessments);
        setTrend(data.trend);
      })
      .catch(() => setError("We couldn't load this child's history."))
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <PageSpinner label="Loading child history..." />;
  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!child || !trend) return null;

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Child {child.child_code}</CardTitle>
          <p className="mt-1 text-sm text-ink-500 capitalize">Sex: {child.sex}</p>
        </CardHeader>
      </Card>

      <TrendPanel trend={trend} />

      <Card>
        <CardHeader>
          <CardTitle>All Assessments</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink-100 text-left text-xs uppercase tracking-wide text-ink-400">
                <th className="px-5 py-3 font-medium">Date</th>
                <th className="px-5 py-3 font-medium">Stunting</th>
                <th className="px-5 py-3 font-medium">Underweight</th>
              </tr>
            </thead>
            <tbody>
              {assessments.map((item) => (
                <tr key={item.id} className="border-b border-ink-100 last:border-0 hover:bg-ink-50">
                  <td className="px-5 py-3 font-medium text-ink-900">
                    <Link to={`/assessments/${item.id}`} className="hover:text-brand-600 hover:underline">
                      {formatDateTime(item.assessedAt)}
                    </Link>
                  </td>
                  <td className="px-5 py-3">
                    <RiskBadge label={item.predictions.stunting?.predictedLabel} />
                  </td>
                  <td className="px-5 py-3">
                    <RiskBadge label={item.predictions.underweight?.predictedLabel} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
