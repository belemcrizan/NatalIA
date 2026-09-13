import { useMutation } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { conclusionLimit, conclusionTitle, guaranteeNote, nextActions, obligationSummary } from "@/lib/explain";
import type { RunDocument, Verdict } from "@/lib/types";

function toneFor(value?: string | null) {
  if (value === "ACCEPTED" || value === "succeeded") return "ok" as const;
  if (value === "REFUTED" || value === "INVALID" || value === "failed") return "bad" as const;
  if (value === "ABSTAIN" || value === "timed_out" || value === "cancelled") return "warn" as const;
  return "muted" as const;
}

export function ResultView({
  run,
  onRevise,
}: {
  run: RunDocument;
  onRevise?: (run: RunDocument) => void;
}) {
  const recheck = useMutation({
    mutationFn: async () => {
      const cert = run.obligations?.find((item) => item.artifacts?.certificate);
      if (!cert) throw new Error("This run has no kernel certificate to recheck.");
      return api<{ accepted: boolean; reason?: string; guarantee_level?: string }>("/api/certificates/recheck", {
        method: "POST",
        body: JSON.stringify({ submission: run.submission, certificate: cert.artifacts?.certificate }),
      });
    },
  });

  const download = (digest: string) => {
    window.open(`/api/artifacts/${digest}`, "_blank", "noopener");
  };

  const exportJson = () => {
    const blob = new Blob([JSON.stringify(run, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `natalia-run-${run.id}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <article className="space-y-4" aria-live="polite">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={toneFor(run.job_status)}>{run.job_status ?? "unknown"}</Badge>
        <Badge tone={toneFor(run.conclusion ?? run.verdict)}>{run.conclusion ?? run.verdict}</Badge>
        {run.guarantee_level ? <Badge>{run.guarantee_level}</Badge> : null}
        {run.duration_ms != null ? (
          <span className="text-sm text-muted">{(run.duration_ms / 1000).toFixed(2)} s</span>
        ) : null}
      </div>
      <h2 className="text-xl font-semibold">{conclusionTitle(run)}</h2>
      <p>{guaranteeNote(run.guarantee_level)}</p>
      <p className="text-muted">{conclusionLimit((run.conclusion ?? run.verdict) as Verdict)}</p>
      <ol className="list-decimal space-y-2 pl-5 text-sm">
        <li>
          Assumptions:{" "}
          {(run.submission?.assumptions ?? []).map((item) => `${item.lhs} ${item.op} ${item.rhs}`).join("; ") ||
            "none declared"}
        </li>
        <li>Evidence: {(run.obligations ?? []).map(obligationSummary).join("; ") || "none persisted"}</li>
        <li>Next: {nextActions((run.conclusion ?? run.verdict) as Verdict)}</li>
      </ol>
      {(run.obligations ?? []).map((item) => (
        <section key={item.id} className="rounded-md border border-line p-3">
          <div className="flex flex-wrap items-center gap-2">
            <strong>{item.id}</strong>
            <Badge tone={toneFor(item.status)}>{item.status}</Badge>
            <span className="text-xs text-muted">{item.oracle || item.adapter_id}</span>
          </div>
          <p className="mt-2 text-sm">{obligationSummary(item)}</p>
          {item.counterexample ? (
            <div className="witness mt-2 rounded bg-red-50 p-2 text-sm">
              <p>
                Exact rational assignment:{" "}
                {Object.entries(item.counterexample)
                  .map(([key, value]) => `${key} = ${value}`)
                  .join(", ")}
              </p>
              {Object.entries(item.counterexample).map(([key, value]) => (
                <p key={key} className="text-muted">
                  Decimal approximation of {key}: {Number(value)}
                </p>
              ))}
              {item.evaluation ? (
                <p>
                  Substitution {item.evaluation.lhs} {item.evaluation.op} {item.evaluation.rhs} evaluated false
                  with exact rationals.
                </p>
              ) : null}
            </div>
          ) : null}
          {item.artifacts?.digest ? (
            <Button variant="secondary" size="sm" className="mt-2" onClick={() => download(String(item.artifacts?.digest))}>
              Download artifact
            </Button>
          ) : null}
        </section>
      ))}
      <details>
        <summary className="cursor-pointer text-sm font-medium">Advanced evidence</summary>
        <pre className="mt-2 overflow-x-auto rounded bg-surface-2 p-3 text-xs">
          {JSON.stringify(
            {
              reason: run.reason,
              guarantee: run.guarantee,
              versions: run.versions,
              input_sha256: run.input_sha256,
              request_id: run.request_id,
            },
            null,
            2,
          )}
        </pre>
      </details>
      <div className="flex flex-wrap gap-2">
        <Button variant="secondary" onClick={exportJson}>
          Export JSON
        </Button>
        {onRevise ? (
          <Button variant="secondary" onClick={() => onRevise(run)}>
            Revise in Claim Builder
          </Button>
        ) : null}
        <Button variant="secondary" onClick={() => recheck.mutate()} disabled={recheck.isPending}>
          Recheck certificate
        </Button>
      </div>
      {recheck.isError ? (
        <p role="alert" className="text-sm text-bad">
          {(recheck.error as Error).message}
        </p>
      ) : null}
      {recheck.data ? (
        <p role="status" className="text-sm">
          {recheck.data.accepted
            ? `Independent recheck accepted (${recheck.data.guarantee_level}).`
            : `Recheck rejected: ${recheck.data.reason}`}
        </p>
      ) : null}
    </article>
  );
}
