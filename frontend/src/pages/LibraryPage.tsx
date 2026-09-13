import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { InvestigationDiagram } from "@/components/diagrams/ScienceDiagrams";
import { Equation } from "@/components/math/Equation";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/select";
import { api } from "@/lib/api";
import type { Investigation, InvestigationList } from "@/lib/types";

const GROUPS = [
  { id: "Foundations", title: "1. Foundations" },
  { id: "Intermediate", title: "2. Applied models" },
  { id: "Advanced", title: "3. Advanced reasoning" },
  { id: "Research Boundary", title: "4. Research boundaries" },
];

export function LibraryPage() {
  const query = useQuery({
    queryKey: ["investigations"],
    queryFn: () => api<InvestigationList>("/api/investigations"),
  });
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [verdict, setVerdict] = useState("");
  const [objective, setObjective] = useState("");
  const [viz, setViz] = useState("");

  const items = useMemo(() => {
    return (query.data?.items ?? []).filter((item) => {
      const blob = `${item.title} ${item.question} ${item.domain}`.toLowerCase();
      if (search && !blob.includes(search.toLowerCase())) return false;
      if (domain && item.domain !== domain) return false;
      if (difficulty && item.difficulty !== difficulty) return false;
      if (verdict && item.expected_verdict !== verdict) return false;
      if (objective && item.educational_objective !== objective) return false;
      if (viz === "plot" && !(item.charts ?? []).length) return false;
      if (viz === "none" && (item.charts ?? []).length) return false;
      return true;
    });
  }, [query.data, search, domain, difficulty, verdict, objective, viz]);

  const grouped = GROUPS.map((group) => ({
    ...group,
    items: items.filter((item) => item.difficulty === group.id),
  }));

  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm font-semibold uppercase tracking-wide text-accent">Explore examples</p>
        <h1 className="text-2xl font-semibold">A progression of educational models</h1>
        <p className="text-muted">Reading times are editorial metadata, not solver predictions.</p>
      </header>
      <form className="grid gap-3 md:grid-cols-3 lg:grid-cols-6" aria-label="Filter examples">
        <div>
          <Label htmlFor="q">Search</Label>
          <Input id="q" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="domain">Domain</Label>
          <NativeSelect id="domain" value={domain} onChange={(e) => setDomain(e.target.value)}>
            <option value="">All</option>
            {(query.data?.domains ?? []).map((item) => (
              <option key={item}>{item}</option>
            ))}
          </NativeSelect>
        </div>
        <div>
          <Label htmlFor="diff">Difficulty</Label>
          <NativeSelect id="diff" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="">All</option>
            {(query.data?.difficulties ?? []).map((item) => (
              <option key={item}>{item}</option>
            ))}
          </NativeSelect>
        </div>
        <div>
          <Label htmlFor="mode">Expected outcome</Label>
          <NativeSelect id="mode" value={verdict} onChange={(e) => setVerdict(e.target.value)}>
            <option value="">All</option>
            <option>ACCEPTED</option>
            <option>REFUTED</option>
            <option>INVALID</option>
            <option>ABSTAIN</option>
          </NativeSelect>
        </div>
        <div>
          <Label htmlFor="obj">Educational objective</Label>
          <NativeSelect id="obj" value={objective} onChange={(e) => setObjective(e.target.value)}>
            <option value="">All</option>
            {[...new Set((query.data?.items ?? []).map((i) => i.educational_objective).filter(Boolean))].map(
              (item) => (
                <option key={item}>{item}</option>
              ),
            )}
          </NativeSelect>
        </div>
        <div>
          <Label htmlFor="viz">Visualization</Label>
          <NativeSelect id="viz" value={viz} onChange={(e) => setViz(e.target.value)}>
            <option value="">All</option>
            <option value="plot">Has illustration</option>
            <option value="none">No plot</option>
          </NativeSelect>
        </div>
      </form>
      {grouped.map((group) => (
        <section key={group.id}>
          <h2 className="mb-3 text-lg font-semibold">{group.title}</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {group.items.map((item) => (
              <LibraryCard key={item.id} item={item} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function LibraryCard({ item }: { item: Investigation }) {
  return (
    <Link to={`/investigate/${item.id}`} className="block">
      <Card className="h-full space-y-2 p-4">
        <InvestigationDiagram id={item.id} />
        <Equation latex={item.equations[0]?.latex ?? ""} display={false} />
        <h3 className="font-semibold">{item.title}</h3>
        <p>{item.question}</p>
        <p className="text-xs text-muted">
          {item.domain} · {item.difficulty} · {item.learning_minutes} min read · {item.guarantee_level}
        </p>
      </Card>
    </Link>
  );
}
