import { useState } from "react";
import { ChevronDown, LogOut, UserCircle } from "lucide-react";

import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/cn";

const ROLE_LABELS: Record<string, string> = {
  administrator: "Administrator",
  healthcare_worker: "Healthcare Worker",
  nutrition_officer: "Nutrition Officer",
  researcher: "Researcher",
};

export function Topbar({ title }: { title: string }) {
  const { profile, signOut } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-ink-200 bg-white px-6">
      <h1 className="text-lg font-semibold text-ink-900">{title}</h1>

      <div className="relative">
        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-expanded={menuOpen}
          aria-haspopup="menu"
          className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-ink-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500"
        >
          <UserCircle className="size-6 text-ink-500" aria-hidden="true" />
          <span className="text-left">
            <span className="block font-medium text-ink-900">{profile?.full_name ?? "Loading..."}</span>
            <span className="block text-xs text-ink-500">
              {profile ? ROLE_LABELS[profile.role] : ""}
            </span>
          </span>
          <ChevronDown className="size-4 text-ink-400" aria-hidden="true" />
        </button>

        <div
          role="menu"
          className={cn(
            "absolute right-0 z-10 mt-1 w-44 overflow-hidden rounded-md border border-ink-200 bg-white shadow-lg",
            menuOpen ? "block" : "hidden"
          )}
        >
          <button
            type="button"
            role="menuitem"
            onClick={() => signOut()}
            className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-ink-700 hover:bg-ink-50"
          >
            <LogOut className="size-4" aria-hidden="true" />
            Sign out
          </button>
        </div>
      </div>
    </header>
  );
}
