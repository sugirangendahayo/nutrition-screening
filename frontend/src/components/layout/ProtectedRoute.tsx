import { Navigate, Outlet, useLocation } from "react-router-dom";

import { PageSpinner } from "@/components/ui/Spinner";
import { useAuth } from "@/context/AuthContext";
import type { UserRole } from "@/types";

export function ProtectedRoute() {
  const { session, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <PageSpinner label="Checking your session..." />;

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export function RoleRoute({ allow }: { allow: UserRole[] }) {
  const { profile, isLoading } = useAuth();

  if (isLoading || !profile) return <PageSpinner label="Loading your profile..." />;

  if (!allow.includes(profile.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
