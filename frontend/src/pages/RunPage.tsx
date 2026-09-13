import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";

import { ResultView } from "@/components/result/ResultView";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { JobPublic } from "@/lib/types";

export function RunPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const query = useQuery({
    queryKey: ["job", id],
    queryFn: () => api<JobPublic>(`/api/jobs/${id}`),
    enabled: Boolean(id),
  });
  const replay = useMutation({
    mutationFn: () => api("/api/replay", { method: "POST", body: JSON.stringify(query.data?.document ?? {}) }),
  });

  if (query.isLoading) return <p>Loading run…</p>;
  if (query.isError) return <p role="alert">Missing record.</p>;
  const job = query.data;
  if (!job) return null;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-2xl font-semibold">{job.title}</h1>
      {job.document ? (
        <ResultView run={job.document} onRevise={(doc) => navigate("/builder", { state: { submission: doc.submission } })} />
      ) : (
        <p>Operational state {job.job_status}. No scientific document yet.</p>
      )}
      <Button variant="secondary" onClick={() => replay.mutate()} disabled={!job.document}>
        Replay evidence
      </Button>
      {replay.data ? <pre className="overflow-x-auto text-xs">{JSON.stringify(replay.data, null, 2)}</pre> : null}
    </div>
  );
}
