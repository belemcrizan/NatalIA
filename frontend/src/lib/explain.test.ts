import { describe, expect, it } from "vitest";

import { conclusionTitle, guaranteeNote } from "@/lib/explain";
import type { RunDocument } from "@/lib/types";

describe("result semantics", () => {
  it("does not treat operational failure as a scientific refutation", () => {
    const run: RunDocument = {
      id: "x",
      verdict: "ABSTAIN",
      job_status: "failed",
      guarantee_level: "UNAVAILABLE",
    };
    expect(conclusionTitle(run)).toContain("Operational state");
    expect(guaranteeNote("SMT_RELATIVE")).toContain("Not an independent kernel certificate");
  });
});
