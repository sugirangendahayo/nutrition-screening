import { useState, type FormEvent } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Activity, LogIn } from "lucide-react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/context/AuthContext";

export function LoginPage() {
  const { session, signIn } = useAuth();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (session) {
    const from = (location.state as { from?: Location })?.from?.pathname ?? "/";
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await signIn(email, password);
    } catch {
      setError("The email or password you entered is incorrect. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen">
      <div className="hidden w-1/2 flex-col justify-between bg-brand-700 px-12 py-12 text-white lg:flex">
        <div className="flex items-center gap-2">
          <div className="flex size-10 items-center justify-center rounded-md bg-white/10">
            <Activity className="size-6" />
          </div>
          <span className="text-lg font-semibold">Nutrition DSS</span>
        </div>

        <div>
          <h1 className="text-3xl font-semibold leading-tight">
            Machine Learning Decision Support for Child Nutrition Screening
          </h1>
          <p className="mt-4 max-w-md text-brand-100">
            Supporting healthcare workers, nutrition officers, and researchers with data-driven
            stunting and underweight risk screening for children under five.
          </p>
        </div>

        <p className="text-sm text-brand-200">
          A decision-support tool - results assist, but do not replace, professional clinical
          judgment.
        </p>
      </div>

      <div className="flex w-full flex-col items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <div className="flex items-center gap-2 text-brand-700">
              <Activity className="size-6" />
              <span className="text-lg font-semibold">Nutrition DSS</span>
            </div>
          </div>

          <h2 className="text-2xl font-semibold text-ink-900">Welcome back</h2>
          <p className="mt-1 text-sm text-ink-500">Sign in to your account to continue.</p>

          {error && (
            <Alert tone="danger" className="mt-6">
              {error}
            </Alert>
          )}

          <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
            <Input
              label="Email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              label="Password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" size="lg" isLoading={isSubmitting} className="mt-2 w-full">
              <LogIn className="size-4" aria-hidden="true" />
              Sign in
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-500">
            Don't have an account? Contact your system administrator.
          </p>
        </div>
      </div>
    </div>
  );
}
