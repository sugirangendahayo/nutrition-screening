import { useEffect, useState } from "react";
import { Search, UserPlus } from "lucide-react";

import { listChildren } from "@/api/children";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/cn";
import type { Child } from "@/types";

interface Props {
  mode: "new" | "existing";
  onModeChange: (mode: "new" | "existing") => void;
  selectedChild: Child | null;
  onSelectChild: (child: Child | null) => void;
}

export function ChildSelector({ mode, onModeChange, selectedChild, onSelectChild }: Props) {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState<Child[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (mode !== "existing" || selectedChild) return;
    const timeout = setTimeout(() => {
      setIsSearching(true);
      listChildren(search || undefined)
        .then((data) => setResults(data.children))
        .finally(() => setIsSearching(false));
    }, 300);
    return () => clearTimeout(timeout);
  }, [search, mode, selectedChild]);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => onModeChange("new")}
          className={cn(
            "flex-1 rounded-md border px-4 py-3 text-left text-sm font-medium transition-colors",
            mode === "new" ? "border-brand-500 bg-brand-50 text-brand-800" : "border-ink-200 text-ink-600 hover:bg-ink-50"
          )}
        >
          <UserPlus className="mb-1 size-4" aria-hidden="true" />
          <div>New child</div>
          <p className="mt-0.5 font-normal text-ink-500">Create a new de-identified child record</p>
        </button>
        <button
          type="button"
          onClick={() => onModeChange("existing")}
          className={cn(
            "flex-1 rounded-md border px-4 py-3 text-left text-sm font-medium transition-colors",
            mode === "existing"
              ? "border-brand-500 bg-brand-50 text-brand-800"
              : "border-ink-200 text-ink-600 hover:bg-ink-50"
          )}
        >
          <Search className="mb-1 size-4" aria-hidden="true" />
          <div>Existing child</div>
          <p className="mt-0.5 font-normal text-ink-500">Add a follow-up screening for a known child</p>
        </button>
      </div>

      {mode === "existing" && (
        <div>
          {selectedChild ? (
            <div className="flex items-center justify-between rounded-md border border-brand-200 bg-brand-50 px-4 py-3">
              <div>
                <p className="text-sm font-medium text-brand-800">{selectedChild.child_code}</p>
                <p className="text-xs text-brand-700">Sex: {selectedChild.sex}</p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => onSelectChild(null)}>
                Change
              </Button>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <Input
                placeholder="Search by child code (e.g. CH-2024-00001)"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <div className="max-h-48 overflow-y-auto rounded-md border border-ink-200">
                {isSearching ? (
                  <p className="px-4 py-3 text-sm text-ink-500">Searching...</p>
                ) : results.length === 0 ? (
                  <p className="px-4 py-3 text-sm text-ink-500">No matching child records found.</p>
                ) : (
                  results.map((child) => (
                    <button
                      key={child.id}
                      type="button"
                      onClick={() => onSelectChild(child)}
                      className="flex w-full items-center justify-between border-b border-ink-100 px-4 py-2.5 text-left text-sm last:border-0 hover:bg-ink-50"
                    >
                      <span className="font-medium text-ink-900">{child.child_code}</span>
                      <span className="text-ink-500">{child.sex}</span>
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
