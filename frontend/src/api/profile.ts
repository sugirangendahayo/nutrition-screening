import { apiClient, unwrap } from "@/lib/apiClient";
import type { Profile } from "@/types";

export function getProfile() {
  return unwrap<Profile>(apiClient.get("/profile"));
}
