export type Verdict = "ACCEPTED" | "REFUTED" | "INVALID" | "ABSTAIN";
export type JobStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled"
  | "timed_out"
  | "rejected";
export type GuaranteeLevel =
  | "SMT_RELATIVE"
  | "EXACT_WITNESS_CHECKED"
  | "INTERVAL_ENCLOSURE"
  | "KERNEL_CHECKED"
  | "STATIC_COMPILE"
  | "ADVISORY"
  | "UNAVAILABLE";

export type Relation = {
  lhs: string;
  op: "==" | "!=" | ">" | ">=" | "<" | "<=";
  rhs: string;
};

export type Variable = {
  dimension: string[];
  domain_min?: string | null;
  domain_max?: string | null;
};

export type RelationClaim = Relation & { kind: "relation"; id: string };
export type LimitClaim = {
  kind: "limit";
  id: string;
  expression: string;
  variable: string;
  target: "infinity";
  expected: string;
};
export type HoleClaim = { kind: "proof_hole"; id: string; description: string };
export type Claim = RelationClaim | LimitClaim | HoleClaim;

export type Submission = {
  schema_version: "1.0";
  title: string;
  source_latex: string;
  variables: Record<string, Variable>;
  assumptions: Relation[];
  claims: Claim[];
  budget_ms: number;
  verification_mode: "fast" | "certified" | "lean";
  critical?: boolean;
};

export type ExampleCase = {
  id: string;
  expected_verdict: Verdict;
  submission: Submission;
};

export type ChartSample = Record<string, string>;

export type InvestigationChart = {
  id: string;
  kind: string;
  role: string;
  title: string;
  subtitle?: string;
  x_label?: string;
  y_label?: string;
  highlight?: string;
  samples?: ChartSample[];
  series?: { name: string; samples: ChartSample[] }[];
  rows?: { quantity: string; unit: string; vector: string }[];
};

export type Investigation = {
  id: string;
  example_id: string | null;
  title: string;
  domain: string;
  difficulty: string;
  tier: number;
  learning_minutes: number;
  question: string;
  why_it_matters: string;
  model: string;
  obligation_english: string;
  expected_verdict: Verdict;
  expected_label: string;
  guarantee_level: GuaranteeLevel;
  limitations: string;
  variables_explained: { name: string; meaning: string; unit: string }[];
  equations: { latex: string; plain: string; mathml?: string; caption: string }[];
  charts: InvestigationChart[];
  submission: Submission;
  companion_submission?: Submission;
  related: string[];
  planned: string[];
  educational_model: boolean;
  real_world_validated: boolean;
  educational_objective?: string;
  visualization?: string;
  source: Record<string, string>;
  capability?: string;
  prerequisites?: string[];
  application_context?: string;
  measured_vs_model?: string;
  common_mistakes?: string[];
  variation?: string;
  source_ids?: string[];
  expected_by_mode?: Record<string, string>;
  content_review?: string;
  validation_method?: string;
};

export type InvestigationList = {
  schema: string;
  content_version: string;
  count: number;
  domains: string[];
  difficulties: string[];
  items: Investigation[];
};

export type HistoryItem = {
  id: string;
  created_at: string;
  title: string;
  verdict: Verdict | null;
  duration_ms: number | null;
  job_status: JobStatus;
  content_hash?: string;
  guarantee_level?: GuaranteeLevel | null;
  conclusion?: Verdict | null;
  verification_mode?: string | null;
};

export type HistoryPage = { items: HistoryItem[]; total: number };

export type JobPublic = HistoryItem & {
  updated_at?: string;
  operational_reason?: string | null;
  document?: RunDocument | null;
  trace_id?: string;
};

export type Obligation = {
  id: string;
  status: string;
  reason?: string;
  oracle?: string;
  adapter_id?: string;
  trust?: string;
  counterexample?: Record<string, string>;
  evaluation?: { lhs: string; op: string; rhs: string };
  cas_result?: string;
  expected?: string;
  artifacts?: { certificate?: unknown; digest?: string };
};

export type RunDocument = {
  id: string;
  verdict: Verdict;
  conclusion?: Verdict;
  guarantee_level?: GuaranteeLevel;
  job_status?: JobStatus;
  duration_ms?: number;
  reason?: string;
  verification_mode?: string;
  submission?: Submission;
  obligations?: Obligation[];
  versions?: Record<string, string>;
  input_sha256?: string;
  spans?: unknown[];
  guarantee?: unknown;
  request_id?: string;
};

export type CompilePreview = {
  ok: boolean;
  errors: { path: string; message: string }[];
  obligations: { id: string; kind: string; status: string }[];
  supported_fragment: boolean;
  note?: string;
};

export type Capabilities = {
  version: string;
  mode: string;
  trust_contract: string;
  auth: string;
  max_budget_ms: number;
  calibration: null;
};

export type SystemInfo = {
  version: string;
  schema_version: number;
  profile: string;
  trust_contract: string;
  api: string;
  tenant_id: string;
  executor: Record<string, unknown>;
  adapters: Record<string, unknown>;
  stats: {
    total: number;
    verdicts: Record<string, number>;
    job_statuses: Record<string, number>;
    average_duration_ms: number;
    note: string;
  };
  effective_config: Record<string, unknown>;
};

export type ApiError = {
  status: number;
  message: string;
  requestId?: string;
  retryAfter?: string;
  details?: unknown;
};
