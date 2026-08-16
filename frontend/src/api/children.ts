import { apiClient, unwrap } from "@/lib/apiClient";
import type { AssessmentSummary, Child, TrendResult } from "@/types";

export function listChildren(search?: string) {
  return unwrap<{ children: Child[] }>(apiClient.get("/children", { params: { search } }));
}

export function getChildHistory(childId: string) {
  return unwrap<{ child: Child; assessments: AssessmentSummary[]; trend: TrendResult }>(
    apiClient.get(`/children/${childId}/history`)
  );
}
