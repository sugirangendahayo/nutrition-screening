import { useState, type FormEvent } from "react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/context/AuthContext";
import { useModelInfo } from "@/context/ModelInfoContext";
import { supabase } from "@/lib/supabaseClient";
import { formatRoleLabel } from "@/lib/format";

export function SettingsPage() {
  const { profile } = useAuth();
  const { modelInfo } = useModelInfo();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<{ tone: "success" | "danger"; text: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleChangePassword(event: FormEvent) {
    event.preventDefault();
    setMessage(null);

    if (password.length < 8) {
      setMessage({ tone: "danger", text: "Password must be at least 8 characters." });
      return;
    }
    if (password !== confirmPassword) {
      setMessage({ tone: "danger", text: "Passwords do not match." });
      return;
    }

    setIsSubmitting(true);
    const { error } = await supabase.auth.updateUser({ password });
    setIsSubmitting(false);

    if (error) {
      setMessage({ tone: "danger", text: "We couldn't update your password. Please try again." });
    } else {
      setMessage({ tone: "success", text: "Your password has been updated." });
      setPassword("");
      setConfirmPassword("");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
          <div>
            <p className="text-ink-500">Full name</p>
            <p className="font-medium text-ink-900">{profile?.full_name}</p>
          </div>
          <div>
            <p className="text-ink-500">Role</p>
            <p className="font-medium text-ink-900">{profile ? formatRoleLabel(profile.role) : "-"}</p>
          </div>
          <div>
            <p className="text-ink-500">Facility</p>
            <p className="font-medium text-ink-900">{profile?.facility ?? "Not set"}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Change password</CardTitle>
        </CardHeader>
        <CardContent>
          {message && (
            <Alert tone={message.tone} className="mb-4">
              {message.text}
            </Alert>
          )}
          <form className="flex max-w-sm flex-col gap-4" onSubmit={handleChangePassword}>
            <Input
              label="New password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Input
              label="Confirm new password"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            <Button type="submit" isLoading={isSubmitting} className="w-fit">
              Update password
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>System</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
          <div>
            <p className="text-ink-500">Prediction model mode</p>
            <p className="font-medium capitalize text-ink-900">{modelInfo?.mode ?? "unknown"}</p>
          </div>
          {modelInfo?.targets &&
            Object.entries(modelInfo.targets).map(([target, info]) => (
              <div key={target}>
                <p className="text-ink-500 capitalize">{target} model</p>
                <p className="font-medium text-ink-900">
                  {info.algorithm} ({info.version})
                </p>
              </div>
            ))}
        </CardContent>
      </Card>
    </div>
  );
}
