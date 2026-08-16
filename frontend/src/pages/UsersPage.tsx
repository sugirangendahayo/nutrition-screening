import { useEffect, useState, type FormEvent } from "react";
import { UserPlus } from "lucide-react";

import { createUser, listUsers, updateUser } from "@/api/users";
import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { PageSpinner } from "@/components/ui/Spinner";
import { formatDateTime } from "@/lib/format";
import type { ManagedUser, UserRole } from "@/types";

const ROLE_OPTIONS: { value: UserRole; label: string }[] = [
  { value: "healthcare_worker", label: "Healthcare Worker" },
  { value: "nutrition_officer", label: "Nutrition Officer" },
  { value: "researcher", label: "Researcher" },
  { value: "administrator", label: "Administrator" },
];

export function UsersPage() {
  const [users, setUsers] = useState<ManagedUser[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formState, setFormState] = useState({ email: "", fullName: "", role: "healthcare_worker" as UserRole, facility: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [createdCredentials, setCreatedCredentials] = useState<{ email: string; temporaryPassword: string } | null>(null);

  function refresh() {
    listUsers()
      .then((data) => setUsers(data.users))
      .catch(() => setError("We couldn't load the users list."));
  }

  useEffect(refresh, []);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setFormError(null);
    setIsSubmitting(true);
    try {
      const result = await createUser(formState);
      setCreatedCredentials({ email: result.email, temporaryPassword: result.temporaryPassword });
      setFormState({ email: "", fullName: "", role: "healthcare_worker", facility: "" });
      refresh();
    } catch {
      setFormError("We couldn't create this account. Check the details and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRoleChange(userId: string, role: UserRole) {
    await updateUser(userId, { role });
    refresh();
  }

  async function handleToggleActive(user: ManagedUser) {
    await updateUser(user.id, { isActive: !user.is_active });
    refresh();
  }

  if (error) return <Alert tone="danger">{error}</Alert>;
  if (!users) return <PageSpinner label="Loading users..." />;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-end">
        <Button
          onClick={() => {
            setCreatedCredentials(null);
            setFormError(null);
            setIsModalOpen(true);
          }}
        >
          <UserPlus className="size-4" aria-hidden="true" />
          Add User
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink-100 text-left text-xs uppercase tracking-wide text-ink-400">
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Role</th>
                <th className="px-5 py-3 font-medium">Facility</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Joined</th>
                <th className="px-5 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-ink-100 last:border-0">
                  <td className="px-5 py-3 font-medium text-ink-900">{user.full_name}</td>
                  <td className="px-5 py-3">
                    <Select
                      className="h-9 w-48"
                      value={user.role}
                      options={ROLE_OPTIONS}
                      onChange={(e) => handleRoleChange(user.id, e.target.value as UserRole)}
                    />
                  </td>
                  <td className="px-5 py-3 text-ink-500">{user.facility ?? "-"}</td>
                  <td className="px-5 py-3">
                    <Badge tone={user.is_active ? "success" : "neutral"}>
                      {user.is_active ? "Active" : "Deactivated"}
                    </Badge>
                  </td>
                  <td className="px-5 py-3 text-ink-500">{formatDateTime(user.created_at)}</td>
                  <td className="px-5 py-3">
                    <Button variant="outline" size="sm" onClick={() => handleToggleActive(user)}>
                      {user.is_active ? "Deactivate" : "Reactivate"}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add a new user">
        {createdCredentials ? (
          <div className="flex flex-col gap-4">
            <Alert tone="success" title="Account created">
              Share these temporary credentials with {createdCredentials.email} securely. They
              should change their password after first sign-in.
            </Alert>
            <div className="rounded-md bg-ink-100 px-4 py-3 font-mono text-sm">
              {createdCredentials.temporaryPassword}
            </div>
            <Button onClick={() => setIsModalOpen(false)}>Done</Button>
          </div>
        ) : (
          <form className="flex flex-col gap-4" onSubmit={handleCreate}>
            {formError && <Alert tone="danger">{formError}</Alert>}
            <Input
              label="Full name"
              required
              value={formState.fullName}
              onChange={(e) => setFormState((s) => ({ ...s, fullName: e.target.value }))}
            />
            <Input
              label="Email"
              type="email"
              required
              value={formState.email}
              onChange={(e) => setFormState((s) => ({ ...s, email: e.target.value }))}
            />
            <Select
              label="Role"
              required
              options={ROLE_OPTIONS}
              value={formState.role}
              onChange={(e) => setFormState((s) => ({ ...s, role: e.target.value as UserRole }))}
            />
            <Input
              label="Facility (optional)"
              value={formState.facility}
              onChange={(e) => setFormState((s) => ({ ...s, facility: e.target.value }))}
            />
            <Button type="submit" isLoading={isSubmitting} className="mt-2">
              Create account
            </Button>
          </form>
        )}
      </Modal>
    </div>
  );
}
