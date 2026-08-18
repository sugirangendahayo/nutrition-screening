import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { FileText, History } from "lucide-react";

import { getAssessment } from "@/api/assessments";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { PageSpinner } from "@/components/ui/Spinner";
import { PredictionResultView } from "@/features/results/PredictionResultView";
import { formatDateTime } from "@/lib/format";
import type { AssessmentDetail } from "@/types";

export function AssessmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<AssessmentDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    getAssessment(id)
      .then(setDetail)
      .catch(() => setError("We couldn't load this assessment."))
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <PageSpinner label="Loading assessment..." />;
  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!detail) return null;

  const result = {
    mode: detail.mode ?? "mock",
    generatedAt: detail.assessedAt,
    targets: Object.values(detail.predictions),
    explanations: detail.explanations,
    inputData: detail.inputData,
    trendPreview: detail.trend,
  };

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle>Child {detail.child.child_code}</CardTitle>
            <p className="mt-1 text-sm text-ink-500">Screened on {formatDateTime(detail.assessedAt)}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate(`/children/${detail.child.id}`)}>
              <History className="size-4" aria-hidden="true" />
              Child History
            </Button>
            <Link to={`/reports/${detail.id}`}>
              <Button>
                <FileText className="size-4" aria-hidden="true" />
                View Report
              </Button>
            </Link>
          </div>
        </CardHeader>
        {detail.notes && (
          <CardContent>
            <p className="text-sm text-ink-600">
              <span className="font-medium text-ink-800">Notes: </span>
              {detail.notes}
            </p>
          </CardContent>
        )}
      </Card>

      <PredictionResultView result={result} />
    </div>
  );
}
