import { apiClient, unwrap } from "@/lib/apiClient";
import type { ManagedUser, UserRole } from "@/types";

export function listUsers() {
  return unwrap<{ users: ManagedUser[] }>(apiClient.get("/users"));
}

export function createUser(payload: {
  email: string;
  fullName: string;
  role: UserRole;
  facility?: string;
}) {
  return unwrap<{ id: string; email: string; fullName: string; role: UserRole; temporaryPassword: string }>(
    apiClient.post("/users", payload)
  );
}

export function updateUser(
  id: string,
  payload: Partial<{ role: UserRole; isActive: boolean; fullName: string; facility: string }>
) {
  return unwrap<ManagedUser>(apiClient.patch(`/users/${id}`, payload));
}
