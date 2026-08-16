import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileBarChart } from "lucide-react";

import { listReports, type ReportLogEntry } from "@/api/reports";
import { Alert } from "@/components/ui/Alert";
import { Card, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageSpinner } from "@/components/ui/Spinner";
import { formatDateTime } from "@/lib/format";

export function ReportsPage() {
  const [reports, setReports] = useState<ReportLogEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listReports()
      .then((data) => setReports(data.reports))
      .catch(() => setError("We couldn't load the reports list."));
  }, []);

  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!reports) return <PageSpinner label="Loading reports..." />;

  if (reports.length === 0) {
    return (
      <EmptyState
        icon={<FileBarChart className="size-10" />}
        title="No reports generated yet"
        description="Generate a report from any screening result to see it listed here."
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
              <th className="px-5 py-3 font-medium">Assessment date</th>
              <th className="px-5 py-3 font-medium">Report generated</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((report) => (
              <tr key={report.id} className="border-b border-ink-100 last:border-0 hover:bg-ink-50">
                <td className="px-5 py-3 font-medium text-ink-900">
                  <Link to={`/reports/${report.assessmentId}`} className="hover:text-brand-600 hover:underline">
                    {report.childCode ?? "Unknown"}
                  </Link>
                </td>
                <td className="px-5 py-3 text-ink-500">{formatDateTime(report.assessedAt)}</td>
                <td className="px-5 py-3 text-ink-500">{formatDateTime(report.createdAt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
