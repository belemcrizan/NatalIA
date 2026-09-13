import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { InvestigationDiagram } from "@/components/diagrams/ScienceDiagrams";
import { Equation } from "@/components/math/Equation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { api } from "@/lib/api";
import type { HistoryPage, InvestigationList } from "@/lib/types";

export function HomePage() {
  const investigations = useQuery({
    queryKey: ["investigations"],
    queryFn: () => api<InvestigationList>("/api/investigations"),
  });
  const history = useQuery({
    queryKey: ["runs", { limit: 5 }],
    queryFn: () => api<HistoryPage>("/api/runs?limit=5"),
  });
  const featured = (investigations.data?.items ?? []).filter((item) => item.tier === 1).slice(0, 4);

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <header className="space-y-3">
        <p className="text-sm font-semibold uppercase tracking-wide text-accent">Start an investigation</p>
        <h1 className="text-3xl font-semibold">Check a declared claim, then read the evidence.</h1>
        <p className="max-w-2xl text-muted">
          NatalIA verifies structured formalizations of mathematics and physics. It does not read papers,
          autoformalize LaTeX, or turn a plot into a proof.
        </p>
        <div className="flex flex-wrap gap-3">
          <Button asChild>
            <Link to="/builder">Start an investigation</Link>
          </Button>
          <Button asChild variant="secondary">
            <Link to="/library">Explore examples</Link>
          </Button>
        </div>
      </header>
      <section>
        <h2 className="mb-3 text-lg font-semibold">Foundational examples</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {featured.map((item) => (
            <Link key={item.id} to={`/investigate/${item.id}`} className="block">
              <Card className="h-full space-y-2 p-4 hover:border-accent">
                <InvestigationDiagram id={item.id} />
                <Equation latex={item.equations[0]?.latex ?? ""} display={false} />
                <p className="font-medium">{item.question}</p>
                <p className="text-xs text-muted">
                  {item.domain} · {item.difficulty} · {item.guarantee_level}
                </p>
              </Card>
            </Link>
          ))}
        </div>
      </section>
      {history.data && history.data.total > 0 ? (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Continue your work</h2>
          <ul className="space-y-2">
            {history.data.items.map((item) => (
              <li key={item.id}>
                <Link className="text-accent underline" to={`/history/${item.id}`}>
                  {item.title} · {item.job_status} · {item.verdict ?? "pending"}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : (
        <p className="text-sm text-muted">No previous runs in this environment yet.</p>
      )}
    </div>
  );
}
