import { apiClient, unwrap } from "@/lib/apiClient";
import type { AssessmentDetail, AssessmentSummary } from "@/types";

export function saveAssessment(payload: {
  childId?: string;
  inputData: Record<string, string | number>;
  notes?: string;
}) {
  return unwrap<AssessmentDetail>(apiClient.post("/assessments", payload));
}

export function listAssessments(params?: { childId?: string; mine?: boolean }) {
  return unwrap<{ assessments: AssessmentSummary[] }>(
    apiClient.get("/assessments", { params: { childId: params?.childId, mine: params?.mine } })
  );
}

export function getAssessment(id: string) {
  return unwrap<AssessmentDetail>(apiClient.get(`/assessments/${id}`));
}
