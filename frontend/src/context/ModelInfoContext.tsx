import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { getModelInfo } from "@/api/model";
import { useAuth } from "@/context/AuthContext";
import type { ModelInfo } from "@/types";

interface ModelInfoContextValue {
  modelInfo: ModelInfo | null;
  isLoading: boolean;
  refresh: () => Promise<void>;
}

const ModelInfoContext = createContext<ModelInfoContextValue | undefined>(undefined);

export function ModelInfoProvider({ children }: { children: ReactNode }) {
  const { session } = useAuth();
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function refresh() {
    try {
      const info = await getModelInfo();
      setModelInfo(info);
    } catch {
      setModelInfo(null);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (session) {
      refresh();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session]);

  return (
    <ModelInfoContext.Provider value={{ modelInfo, isLoading, refresh }}>
      {children}
    </ModelInfoContext.Provider>
  );
}

export function useModelInfo() {
  const context = useContext(ModelInfoContext);
  if (!context) throw new Error("useModelInfo must be used within a ModelInfoProvider");
  return context;
}
