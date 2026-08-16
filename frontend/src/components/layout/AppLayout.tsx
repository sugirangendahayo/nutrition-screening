import { Outlet, useLocation } from "react-router-dom";

import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { DevModeBanner } from "@/components/layout/DevModeBanner";

const TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/screening/new": "New Nutrition Screening",
  "/history": "Prediction History",
  "/reports": "Reports",
  "/model-performance": "Model Performance",
  "/users": "Users",
  "/settings": "Settings",
};

function resolveTitle(pathname: string): string {
  if (TITLES[pathname]) return TITLES[pathname];
  if (pathname.startsWith("/children/")) return "Child Nutrition History";
  if (pathname.startsWith("/assessments/")) return "Screening Result";
  if (pathname.startsWith("/reports/")) return "Nutrition Screening Report";
  return "Nutrition DSS";
}

export function AppLayout() {
  const location = useLocation();

  return (
    <div className="flex h-screen bg-ink-50">
      <div className="no-print">
        <Sidebar />
      </div>
      <div className="flex min-w-0 flex-1 flex-col">
        <div className="no-print">
          <Topbar title={resolveTitle(location.pathname)} />
        </div>
        <DevModeBanner />
        <main className="flex-1 overflow-y-auto px-6 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
