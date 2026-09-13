import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { api } from "@/lib/api";
import type { SystemInfo } from "@/lib/types";

export function HealthDot() {
  const query = useQuery({
    queryKey: ["system"],
    queryFn: () => api<SystemInfo>("/api/system"),
    refetchInterval: 10000,
    retry: 1,
  });
  const ok = query.data?.api === "ready";
  return (
    <Link to="/diagnostics" className="flex items-center gap-2 text-xs text-muted">
      <span
        className={`inline-block h-2.5 w-2.5 rounded-full ${ok ? "bg-ok" : "bg-warn"}`}
        aria-hidden
      />
      <span className="hidden md:inline">{ok ? "Environment ready" : "Diagnostics"}</span>
    </Link>
  );
}
