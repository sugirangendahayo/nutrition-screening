import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ClipboardList } from "lucide-react";

import { listAssessments } from "@/api/assessments";
import { Alert } from "@/components/ui/Alert";
import { Card, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { PageSpinner } from "@/components/ui/Spinner";
import { formatDateTime } from "@/lib/format";
import type { AssessmentSummary } from "@/types";

export function HistoryPage() {
  const [assessments, setAssessments] = useState<AssessmentSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listAssessments()
      .then((data) => setAssessments(data.assessments))
      .catch(() => setError("We couldn't load the prediction history."));
  }, []);

  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!assessments) return <PageSpinner label="Loading history..." />;

  if (assessments.length === 0) {
    return (
      <EmptyState
        icon={<ClipboardList className="size-10" />}
        title="No previous assessments found"
        description="Screenings you run and save will appear here."
      />
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-ink-100 text-left text-xs uppercase tracking-wide text-ink-400">
              <th className="px-5 py-3 font-medium">Child</th>
              <th className="px-5 py-3 font-medium">Sex</th>
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
                    {item.childCode}
                  </Link>
                </td>
                <td className="px-5 py-3 text-ink-500 capitalize">{item.sex}</td>
                <td className="px-5 py-3 text-ink-500">{formatDateTime(item.assessedAt)}</td>
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
  );
}
