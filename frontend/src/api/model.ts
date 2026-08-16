import { apiClient, unwrap } from "@/lib/apiClient";
import type { ModelInfo, ModelVersionRecord } from "@/types";

export function getModelInfo() {
  return unwrap<ModelInfo>(apiClient.get("/model/info"));
}

export function getModelPerformance() {
  return unwrap<{ versions: ModelVersionRecord[] }>(apiClient.get("/model/performance"));
}
