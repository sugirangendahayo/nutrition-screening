import { useState, type FormEvent } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { Activity, LogIn } from "lucide-react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/context/AuthContext";

// Free-to-use (Unsplash License) photo of a healthcare worker caring for a
// child. Swap this for your own licensed photo before a real presentation -
// just replace this one URL. Prefer imagery that conveys care/support (a
// health worker with a child, a checkup) over imagery of a child in visible
// distress: it represents the same subject matter respectfully, and avoids
// the consent/dignity and copyright risks of using photos of real,
// identifiable, vulnerable children found via a generic image search.
const LOGIN_HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1639401122139-68a5840cb3bd?auto=format&fit=crop&w=1600&q=80";

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
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden px-12 py-12 text-white lg:flex">
        {/* Background photo */}
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url('${LOGIN_HERO_IMAGE_URL}')` }}
          aria-hidden="true"
        />
        {/* Brand-tinted gradient overlay: darkest where text sits (top/bottom),
            lighter in the middle so the photo still reads as a photo. Keeps
            white text legible over any part of the image. */}
        <div
          className="absolute inset-0 bg-gradient-to-b from-brand-900/90 via-brand-900/55 to-brand-900/90"
          aria-hidden="true"
        />

        <div className="relative z-10 flex items-center gap-2">
          <div className="flex size-10 items-center justify-center rounded-md bg-white/10 backdrop-blur-sm">
            <Activity className="size-6" />
          </div>
          <span className="text-lg font-semibold">Nutrition DSS</span>
        </div>

        {/* Frosted-glass card behind the headline for guaranteed contrast,
            regardless of what's directly behind it in the photo. */}
        <div className="relative z-10 rounded-2xl border border-white/10 bg-white/10 p-6 shadow-lg backdrop-blur-md">
          <h1 className="text-3xl font-semibold leading-tight">
            Machine Learning Decision Support for Child Nutrition Screening
          </h1>
          <p className="mt-4 max-w-md text-brand-100">
            Supporting healthcare workers, nutrition officers, and researchers with data-driven
            stunting and underweight risk screening for children under five.
          </p>
        </div>

        <p className="relative z-10 text-sm text-brand-100">
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
