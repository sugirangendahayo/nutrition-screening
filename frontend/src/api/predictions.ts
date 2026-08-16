import { apiClient, unwrap } from "@/lib/apiClient";
import type { PredictionResponse } from "@/types";

export function runPrediction(inputData: Record<string, string | number>, childId?: string) {
  return unwrap<PredictionResponse>(
    apiClient.post("/predictions", { inputData, childId })
  );
}
