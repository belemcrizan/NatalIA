import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { ClaimBuilder } from "@/components/builder/ClaimBuilder";
import { ScientificChart } from "@/components/charts/ScientificChart";
import { InvestigationDiagram } from "@/components/diagrams/ScienceDiagrams";
import { Equation } from "@/components/math/Equation";
import { ResultView } from "@/components/result/ResultView";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { streamJobEvents } from "@/lib/sse";
import type { Investigation, JobPublic, RunDocument } from "@/lib/types";
import { newIdempotencyKey } from "@/lib/utils";

export function InvestigationPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const query = useQuery({
    queryKey: ["investigation", id],
    queryFn: () => api<Investigation>(`/api/investigations/${id}`),
    enabled: Boolean(id),
  });
  const [run, setRun] = useState<RunDocument | null>(null);
  const [stale, setStale] = useState(false);
  const [mass, setMass] = useState(2);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [error, setError] = useState("");

  const item = query.data;
  const verify = useMutation({
    mutationFn: async () => {
      if (!item) throw new Error("Missing investigation");
      const created = await api<JobPublic>("/api/jobs", {
        method: "POST",
        headers: { "Idempotency-Key": newIdempotencyKey() },
        body: JSON.stringify(item.submission),
      });
      const controller = new AbortController();
      await streamJobEvents(created.id, (update) => {
        if (update.document) setRun(update.document);
      }, controller.signal);
      const latest = await api<JobPublic>(`/api/jobs/${created.id}`);
      if (latest.document) setRun(latest.document);
      setStale(false);
    },
    onError: (err) => setError(err instanceof Error ? err.message : "Verification failed"),
  });

  if (query.isLoading) return <p>Loading investigation…</p>;
  if (query.isError || !item) return <p role="alert">Investigation not found.</p>;

  return (
    <article className="mx-auto max-w-3xl space-y-6">
      <p className="text-sm text-muted">
        {item.domain} · {item.difficulty} · {item.capability ?? "runnable"} · {item.learning_minutes} min read
      </p>
      <h1 className="text-2xl font-semibold">{item.question}</h1>
      <InvestigationDiagram id={item.id} />
      <section>
        <h2 className="text-lg font-semibold">1. The real-world question</h2>
        <p>{item.why_it_matters}</p>
      </section>
      <section>
        <h2 className="text-lg font-semibold">2. The simplified model</h2>
        <p>{item.model}</p>
        <p className="text-sm text-muted">{item.measured_vs_model ?? "Idealized educational model. Not experimentally validated."}</p>
        {item.prerequisites?.length ? (
          <p className="text-sm text-muted">Prerequisites: {item.prerequisites.join("; ")}</p>
        ) : null}
      </section>
      <section>
        <h2 className="text-lg font-semibold">3. Variables and units</h2>
        <ul className="list-disc pl-5">
          {item.variables_explained.map((v) => (
            <li key={v.name}>
              {v.name}: {v.meaning} ({v.unit})
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="text-lg font-semibold">4. Assumptions</h2>
        <ul className="list-disc pl-5">
          {item.submission.assumptions.map((a, i) => (
            <li key={i}>
              {a.lhs} {a.op} {a.rhs}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="text-lg font-semibold">5. Equations</h2>
        {item.equations.map((eq) => (
          <Equation key={eq.latex} latex={eq.latex} plain={eq.plain} caption={eq.caption} />
        ))}
      </section>
      {(item.charts ?? []).length ? (
        <section>
          <h2 className="text-lg font-semibold">6. Interactive illustration</h2>
          {item.id === "inv-01-kinetic" ? (
            <div className="mb-3">
              <Label htmlFor="mass">Mass m (kg), illustration only</Label>
              <Input
                id="mass"
                type="range"
                min={1}
                max={5}
                value={mass}
                onChange={(e) => {
                  setMass(Number(e.target.value));
                  if (run) setStale(true);
                }}
              />
              <p className="text-sm text-muted">Displayed model uses m = {mass} kg. Changing it does not alter the submitted claim.</p>
            </div>
          ) : null}
          {item.charts.map((chart) => (
            <ScientificChart key={chart.id} spec={chart} />
          ))}
        </section>
      ) : null}
      <section>
        <h2 className="text-lg font-semibold">7. Exact claim submitted</h2>
        <p>{item.obligation_english}</p>
        <Button onClick={() => verify.mutate()} disabled={verify.isPending}>
          Run verification
        </Button>
        {item.companion_submission ? (
          <Button
            variant="secondary"
            className="ml-2"
            onClick={() => navigate("/builder", { state: { submission: item.companion_submission } })}
          >
            Open companion claim
          </Button>
        ) : null}
      </section>
      <section>
        <h2 className="text-lg font-semibold">8. Result and interpretation</h2>
        {stale && run ? (
          <p role="status" className="text-warn">
            Illustration parameters changed after verification. The certificate below belongs to the earlier
            submission. Re-run to check the declared claim again. Charts are not connected to a stale certificate.
          </p>
        ) : null}
        {error ? <p role="alert">{error}</p> : null}
        {run ? <ResultView run={run} onRevise={(doc) => navigate("/builder", { state: { submission: doc.submission } })} /> : (
          <p className="text-muted">Expected educational outcome: {item.expected_label} with {item.guarantee_level}.</p>
        )}
        <p className="text-sm text-muted">{item.limitations}</p>
        {item.expected_by_mode ? (
          <ul className="mt-2 list-disc pl-5 text-sm">
            {Object.entries(item.expected_by_mode).map(([mode, text]) => (
              <li key={mode}>
                {mode}: {text}
              </li>
            ))}
          </ul>
        ) : null}
        {item.common_mistakes?.length ? (
          <p className="text-sm">Common mistakes: {item.common_mistakes.join(" ")}</p>
        ) : null}
      </section>
      <section>
        <h2 className="text-lg font-semibold">9. Advanced evidence</h2>
        <Button variant="ghost" onClick={() => setShowAdvanced((v) => !v)}>
          {showAdvanced ? "Hide JSON" : "Show submitted JSON"}
        </Button>
        {showAdvanced ? <ClaimBuilder initial={item.submission} /> : null}
      </section>
      <p className="text-xs text-muted">
        Sources (offline registry): {(item.source_ids ?? []).join(", ") || item.source?.note}. Related:{" "}
        {item.related.map((rel) => (
          <Link key={rel} className="text-accent underline" to={`/investigate/${rel}`}>
            {rel}
          </Link>
        ))}
      </p>
    </article>
  );
}
