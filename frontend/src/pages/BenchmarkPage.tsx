import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";

export function BenchmarkPage() {
  const query = useQuery({
    queryKey: ["bench"],
    queryFn: () => api<Record<string, unknown>>("/api/benchmark/manifest"),
  });
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">PhysVerifyBench</h1>
      <p className="text-muted">Public, versioned corpus. Calibration remains unavailable.</p>
      {query.data ? <pre className="overflow-x-auto rounded bg-surface-2 p-3 text-xs">{JSON.stringify(query.data, null, 2)}</pre> : null}
    </div>
  );
}
