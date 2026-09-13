import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/select";
import { api } from "@/lib/api";
import type { HistoryPage, JobPublic } from "@/lib/types";

export function HistoryPage() {
  const [q, setQ] = useState("");
  const [verdict, setVerdict] = useState("");
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState<string[]>([]);
  const [compare, setCompare] = useState<JobPublic[] | null>(null);
  const limit = 20;
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (q) params.set("q", q);
  if (verdict) params.set("verdict", verdict);

  const query = useQuery({
    queryKey: ["runs", params.toString()],
    queryFn: () => api<HistoryPage>(`/api/runs?${params}`),
  });

  const jobs = useQuery({
    queryKey: ["jobs", limit, offset],
    queryFn: () => api<HistoryPage>(`/api/jobs?limit=${limit}&offset=${offset}`),
  });

  const merged = useMemo(() => {
    const extra = new Map((jobs.data?.items ?? []).map((item) => [item.id, item]));
    return (query.data?.items ?? []).map((item) => ({ ...item, ...extra.get(item.id) }));
  }, [query.data, jobs.data]);

  const importFile = async (file: File) => {
    const text = await file.text();
    const payload = JSON.parse(text);
    await api("/api/import", { method: "POST", body: JSON.stringify({ dry_run: true, confirm: false, records: payload }) });
  };

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-accent">History</p>
          <h1 className="text-2xl font-semibold">Inspectable runs</h1>
        </div>
        <Button variant="secondary" onClick={() => query.refetch()}>
          Refresh
        </Button>
      </header>
      <form className="flex flex-wrap gap-3" onSubmit={(e) => e.preventDefault()}>
        <div>
          <Label htmlFor="hq">Search title</Label>
          <Input id="hq" value={q} onChange={(e) => { setQ(e.target.value); setOffset(0); }} />
        </div>
        <div>
          <Label htmlFor="hv">Conclusion</Label>
          <NativeSelect id="hv" value={verdict} onChange={(e) => { setVerdict(e.target.value); setOffset(0); }}>
            <option value="">All</option>
            <option>ACCEPTED</option>
            <option>REFUTED</option>
            <option>INVALID</option>
            <option>ABSTAIN</option>
          </NativeSelect>
        </div>
        <div>
          <Label htmlFor="imp">Import JSON (preview)</Label>
          <Input id="imp" type="file" accept="application/json" onChange={(e) => e.target.files?.[0] && importFile(e.target.files[0])} />
        </div>
      </form>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr>
              <th />
              <th>Title</th>
              <th>Timestamp</th>
              <th>State</th>
              <th>Conclusion</th>
              <th>Guarantee</th>
              <th>Duration</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {merged.map((item) => (
              <tr key={item.id} className="border-t border-line">
                <td>
                  <input
                    type="checkbox"
                    aria-label={`Select ${item.title}`}
                    checked={selected.includes(item.id)}
                    onChange={(e) =>
                      setSelected((cur) => (e.target.checked ? [...cur, item.id] : cur.filter((id) => id !== item.id)))
                    }
                  />
                </td>
                <td className="py-2">{item.title}</td>
                <td>{item.created_at}</td>
                <td>
                  <Badge>{item.job_status}</Badge>
                </td>
                <td>{item.conclusion ?? item.verdict ?? "—"}</td>
                <td>{item.guarantee_level ?? "—"}</td>
                <td>{item.duration_ms != null ? `${(item.duration_ms / 1000).toFixed(2)} s` : "—"}</td>
                <td>
                  <Link className="text-accent underline" to={`/history/${item.id}`}>
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center gap-3">
        <Button variant="secondary" disabled={offset === 0} onClick={() => setOffset((v) => Math.max(0, v - limit))}>
          Previous
        </Button>
        <span>
          {offset + 1}–{Math.min(offset + limit, query.data?.total ?? 0)} of {query.data?.total ?? 0}
        </span>
        <Button
          variant="secondary"
          disabled={offset + limit >= (query.data?.total ?? 0)}
          onClick={() => setOffset((v) => v + limit)}
        >
          Next
        </Button>
        <Button
          variant="secondary"
          disabled={selected.length !== 2}
          onClick={async () => {
            const docs = await Promise.all(selected.map((id) => api<JobPublic>(`/api/jobs/${id}`)));
            setCompare(docs);
          }}
        >
          Compare selected
        </Button>
      </div>
      {compare ? (
        <pre className="overflow-x-auto rounded bg-surface-2 p-3 text-xs">{JSON.stringify(compare.map((c) => ({ id: c.id, title: c.title, verdict: c.verdict, guarantee_level: c.guarantee_level })), null, 2)}</pre>
      ) : null}
    </div>
  );
}
