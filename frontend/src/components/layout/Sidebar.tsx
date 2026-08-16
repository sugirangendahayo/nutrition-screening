import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ClipboardPlus,
  History,
  FileBarChart,
  LineChart,
  Users,
  Settings,
  Activity,
} from "lucide-react";

import { NAV_ITEMS, type NavItem } from "@/components/layout/navConfig";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/cn";

const ICONS: Record<NavItem["icon"], typeof LayoutDashboard> = {
  dashboard: LayoutDashboard,
  screening: ClipboardPlus,
  history: History,
  reports: FileBarChart,
  model: LineChart,
  users: Users,
  settings: Settings,
};

export function Sidebar() {
  const { profile } = useAuth();
  const items = NAV_ITEMS.filter((item) => !profile || item.roles.includes(profile.role));

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-ink-200 bg-white">
      <div className="flex items-center gap-2 border-b border-ink-100 px-5 py-5">
        <div className="flex size-9 items-center justify-center rounded-md bg-brand-600 text-white">
          <Activity className="size-5" />
        </div>
        <div>
          <p className="text-sm font-semibold leading-tight text-ink-900">Nutrition DSS</p>
          <p className="text-xs leading-tight text-ink-500">Screening decision support</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4" aria-label="Primary">
        {items.map((item) => {
          const Icon = ICONS[item.icon];
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-ink-600 hover:bg-ink-100 hover:text-ink-900"
                )
              }
            >
              <Icon className="size-4.5" aria-hidden="true" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
