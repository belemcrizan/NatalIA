import { useLocation } from "react-router-dom";

import { ClaimBuilder } from "@/components/builder/ClaimBuilder";
import type { Submission } from "@/lib/types";

export function BuilderPage() {
  const location = useLocation();
  const submission = (location.state as { submission?: Submission } | null)?.submission;
  return (
    <div className="space-y-4">
      <header>
        <p className="text-sm font-semibold uppercase tracking-wide text-accent">Claim builder</p>
        <h1 className="text-2xl font-semibold">Declare a structured formalization</h1>
        <p className="text-muted">
          Guided fields serialize to the NatalIA DSL. There is no natural-language autoformalization.
        </p>
      </header>
      <ClaimBuilder initial={submission} />
    </div>
  );
}
