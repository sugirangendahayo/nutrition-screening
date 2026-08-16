import { apiClient, unwrap } from "@/lib/apiClient";
import type { DashboardSummary } from "@/types";

export function getDashboardSummary() {
  return unwrap<DashboardSummary>(apiClient.get("/dashboard"));
}
