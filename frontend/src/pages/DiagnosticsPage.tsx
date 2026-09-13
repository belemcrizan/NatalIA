import { useQuery } from "@tanstack/react-query";

import { api, sessionApiKey, setSessionApiKey } from "@/lib/api";
import type { SystemInfo } from "@/lib/types";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useQueryClient } from "@tanstack/react-query";

export function DiagnosticsPage() {
  const client = useQueryClient();
  const query = useQuery({
    queryKey: ["system"],
    queryFn: () => api<SystemInfo>("/api/system"),
  });
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">Diagnostics</h1>
      <p className="text-muted">
        Frontend {__APP_VERSION__} · built {__BUILD_TIME__}. Operational counts are not accuracy.
      </p>
      <div>
        <Label htmlFor="key">API key (distributed profile, memory only)</Label>
        <Input
          id="key"
          type="password"
          defaultValue={sessionApiKey() ?? ""}
          onBlur={(e) => {
            setSessionApiKey(e.target.value || null);
            client.clear();
          }}
        />
        <p className="text-xs text-muted">Not stored in localStorage.</p>
      </div>
      {query.isError ? <p role="alert">Could not load /api/system.</p> : null}
      {query.data ? (
        <pre className="overflow-x-auto rounded bg-surface-2 p-3 text-xs">{JSON.stringify(query.data, null, 2)}</pre>
      ) : null}
    </div>
  );
}
