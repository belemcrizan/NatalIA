import { z } from "zod";

import type { Claim, Submission, Variable } from "./types";

export const OPS = ["==", "!=", ">", ">=", "<", "<="] as const;

const namePattern = /^[A-Za-z][A-Za-z0-9_]{0,23}$/;
const claimIdPattern = /^[A-Za-z][A-Za-z0-9_-]{0,39}$/;
const rationalPattern = /^-?\d{1,6}(\/\d{1,6})?$/;

export const relationSchema = z.object({
  lhs: z.string().min(1).max(512),
  op: z.enum(OPS),
  rhs: z.string().min(1).max(512),
});

export const variableRowSchema = z.object({
  name: z.string().regex(namePattern, "Use a letter, then letters, digits or underscore."),
  unit: z.string(),
  dimension: z.string().min(1),
  domain_min: z.string().optional(),
  domain_max: z.string().optional(),
});

export const relationClaimSchema = z.object({
  kind: z.literal("relation"),
  id: z.string().regex(claimIdPattern),
  lhs: z.string().min(1).max(512),
  op: z.enum(OPS),
  rhs: z.string().min(1).max(512),
});

export const limitClaimSchema = z.object({
  kind: z.literal("limit"),
  id: z.string().regex(claimIdPattern),
  expression: z.string().min(1).max(512),
  variable: z.string().regex(namePattern),
  target: z.literal("infinity"),
  expected: z.string().regex(rationalPattern),
});

export const holeClaimSchema = z.object({
  kind: z.literal("proof_hole"),
  id: z.string().regex(claimIdPattern),
  description: z.string().min(1).max(1000),
});

export const guidedSchema = z.object({
  title: z.string().min(1).max(160),
  source_latex: z.string().max(8000),
  budget_ms: z.number().int().min(250).max(15000),
  verification_mode: z.enum(["fast", "certified"]),
  critical: z.boolean(),
  reviewed: z.boolean(),
  variables: z.array(variableRowSchema).min(1).max(20),
  assumptions: z.array(relationSchema).max(20),
  claims: z.array(z.discriminatedUnion("kind", [relationClaimSchema, limitClaimSchema, holeClaimSchema])).min(1).max(20),
});

export type GuidedValues = z.infer<typeof guidedSchema>;

export function parseDimension(text: string): string[] {
  const parts = text.split(",").map((part) => part.trim());
  if (parts.length !== 7 || parts.some((part) => !rationalPattern.test(part))) {
    throw new Error("Dimension must be seven rationals: M,L,T,I,Θ,N,J.");
  }
  return parts;
}

export function guidedToSubmission(values: GuidedValues): Submission {
  const variables: Record<string, Variable> = {};
  for (const row of values.variables) {
    const variable: Variable = { dimension: parseDimension(row.dimension) };
    if (row.domain_min) variable.domain_min = row.domain_min;
    if (row.domain_max) variable.domain_max = row.domain_max;
    variables[row.name] = variable;
  }
  return {
    schema_version: "1.0",
    title: values.title,
    source_latex: values.source_latex,
    variables,
    assumptions: values.assumptions,
    claims: values.claims as Claim[],
    budget_ms: values.budget_ms,
    verification_mode: values.verification_mode,
    critical: values.critical,
  };
}

export function submissionToGuided(submission: Submission, unitFor?: (dim: string[]) => string): GuidedValues {
  return {
    title: submission.title,
    source_latex: submission.source_latex ?? "",
    budget_ms: submission.budget_ms ?? 5000,
    verification_mode: submission.verification_mode ?? "fast",
    critical: Boolean(submission.critical),
    reviewed: false,
    variables: Object.entries(submission.variables).map(([name, spec]) => ({
      name,
      dimension: spec.dimension.join(","),
      unit: unitFor?.(spec.dimension) ?? "custom",
      domain_min: spec.domain_min ?? "",
      domain_max: spec.domain_max ?? "",
    })),
    assumptions: submission.assumptions ?? [],
    claims: submission.claims,
  };
}

export function guidedUnsupportedReason(submission: Submission): string | null {
  const extra = Object.keys(submission).filter(
    (key) =>
      ![
        "schema_version",
        "title",
        "source_latex",
        "variables",
        "assumptions",
        "claims",
        "budget_ms",
        "verification_mode",
        "critical",
      ].includes(key),
  );
  if (extra.length) {
    return `Advanced mode kept these fields the guided editor cannot represent: ${extra.join(", ")}.`;
  }
  return null;
}

export function expressionToLatex(expr: string): string {
  return expr
    .replaceAll("**", "^")
    .replaceAll("*", " \\cdot ")
    .replaceAll("!=", "\\neq")
    .replaceAll(">=", "\\geq")
    .replaceAll("<=", "\\leq");
}

export function emptyGuided(): GuidedValues {
  return {
    title: "Untitled claim",
    source_latex: "",
    budget_ms: 5000,
    verification_mode: "fast",
    critical: false,
    reviewed: false,
    variables: [{ name: "x", unit: "1", dimension: "0,0,0,0,0,0,0", domain_min: "", domain_max: "" }],
    assumptions: [],
    claims: [{ kind: "relation", id: "claim", lhs: "x**2", op: ">=", rhs: "0" }],
  };
}
