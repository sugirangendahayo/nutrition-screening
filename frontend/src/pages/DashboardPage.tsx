import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Baby, ClipboardList, PlusCircle, TrendingUp } from "lucide-react";

import { getDashboardSummary } from "@/api/dashboard";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { PageSpinner } from "@/components/ui/Spinner";
import { StatCard } from "@/components/ui/StatCard";
import { useAuth } from "@/context/AuthContext";
import type { DashboardSummary } from "@/types";
import { formatDateTime } from "@/lib/format";

export function DashboardPage() {
  const { profile } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getDashboardSummary()
      .then(setSummary)
      .catch(() => setError("We couldn't load the dashboard. Please try refreshing the page."))
      .finally(() => setIsLoading(false));
  }, []);

  const canScreen =
    profile && ["administrator", "healthcare_worker", "nutrition_officer"].includes(profile.role);

  if (isLoading) return <PageSpinner label="Loading dashboard..." />;
  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!summary) return null;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-500">
          Overview of nutrition screening activity across the system.
        </p>
        {canScreen && (
          <Link to="/screening/new">
            <Button>
              <PlusCircle className="size-4" aria-hidden="true" />
              New Screening
            </Button>
          </Link>
        )}
      </div>

      {!summary.hasData ? (
        <EmptyState
          icon={<ClipboardList className="size-10" />}
          title="No data yet"
          description="Once nutrition screenings are recorded, summary statistics and recent activity will appear here."
          action={
            canScreen && (
              <Link to="/screening/new">
                <Button variant="outline">Run the first screening</Button>
              </Link>
            )
          }
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Children Assessed"
              value={summary.childrenAssessed}
              icon={<Baby className="size-5" />}
              tone="brand"
            />
            <StatCard
              label="Assessments This Month"
              value={summary.assessmentsThisMonth}
              icon={<ClipboardList className="size-5" />}
            />
            <StatCard
              label="Stunting At Risk (This Month)"
              value={summary.stuntingAtRiskThisMonth}
              icon={<TrendingUp className="size-5" />}
              tone="warning"
            />
            <StatCard
              label="Underweight At Risk (This Month)"
              value={summary.underweightAtRiskThisMonth}
              icon={<TrendingUp className="size-5" />}
              tone="warning"
            />
          </div>

          <Card>
            <CardHeader className="flex items-center justify-between">
              <CardTitle>Recent Screenings</CardTitle>
              <Link to="/history" className="text-sm font-medium text-brand-600 hover:underline">
                View all
              </Link>
            </CardHeader>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-ink-100 text-left text-xs uppercase tracking-wide text-ink-400">
                    <th className="px-5 py-3 font-medium">Child</th>
                    <th className="px-5 py-3 font-medium">Date</th>
                    <th className="px-5 py-3 font-medium">Stunting</th>
                    <th className="px-5 py-3 font-medium">Underweight</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.recentAssessments.map((item) => (
                    <tr key={item.id} className="border-b border-ink-100 last:border-0">
                      <td className="px-5 py-3 font-medium text-ink-900">
                        <Link to={`/assessments/${item.id}`} className="hover:text-brand-600 hover:underline">
                          {item.childCode}
                        </Link>
                      </td>
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
        </>
      )}
    </div>
  );
}
