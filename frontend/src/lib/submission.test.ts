import { describe, expect, it } from "vitest";

import { emptyGuided, guidedToSubmission, submissionToGuided } from "@/lib/submission";
import { unitIdFor } from "@/lib/units";

describe("guided serialization", () => {
  it("round-trips a relation claim into a backend submission", () => {
    const guided = emptyGuided();
    guided.title = "Non-negative kinetic energy";
    guided.variables = [
      { name: "m", unit: "kg", dimension: "1,0,0,0,0,0,0" },
      { name: "v", unit: "m/s", dimension: "0,1,-1,0,0,0,0" },
    ];
    guided.assumptions = [{ lhs: "m", op: ">", rhs: "0" }];
    guided.claims = [{ kind: "relation", id: "kinetic-energy", lhs: "m*v**2/2", op: ">=", rhs: "0" }];
    const payload = guidedToSubmission(guided);
    expect(payload.schema_version).toBe("1.0");
    expect(payload.variables.m.dimension).toEqual(["1", "0", "0", "0", "0", "0", "0"]);
    const back = submissionToGuided(payload, unitIdFor);
    expect(back.claims[0]).toMatchObject({ id: "kinetic-energy", lhs: "m*v**2/2" });
  });
});
