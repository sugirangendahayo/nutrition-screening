import { apiClient, unwrap } from "@/lib/apiClient";
import type { AssessmentDetail, TrendResult } from "@/types";

export interface ReportData {
  assessment: AssessmentDetail;
  inputSummary: Array<{ label: string; value: string | number; unit: string | null }>;
  trend: TrendResult;
}

export function getReport(assessmentId: string) {
  return unwrap<ReportData>(apiClient.get(`/reports/assessment/${assessmentId}`));
}

export function generateReport(assessmentId: string) {
  return unwrap<ReportData>(apiClient.post("/reports", { assessmentId }));
}

export interface ReportLogEntry {
  id: string;
  assessmentId: string;
  childCode: string | null;
  assessedAt: string | null;
  reportType: string;
  createdAt: string;
}

export function listReports() {
  return unwrap<{ reports: ReportLogEntry[] }>(apiClient.get("/reports"));
}
