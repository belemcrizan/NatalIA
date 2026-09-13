import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useRef, useState } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Equation } from "@/components/math/Equation";
import { ResultView } from "@/components/result/ResultView";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/select";
import { api } from "@/lib/api";
import { streamJobEvents } from "@/lib/sse";
import {
  emptyGuided,
  expressionToLatex,
  guidedSchema,
  guidedToSubmission,
  guidedUnsupportedReason,
  submissionToGuided,
  type GuidedValues,
} from "@/lib/submission";
import type { CompilePreview, ExampleCase, JobPublic, RunDocument, Submission } from "@/lib/types";
import { UNIT_PRESETS, dimensionForUnit, unitIdFor } from "@/lib/units";
import { newIdempotencyKey } from "@/lib/utils";

const STEPS = ["Question", "Variables", "Assumptions", "Claim", "Review"] as const;
const OPS = ["+", "-", "*", "/", "**", "(", ")"];

type Props = {
  initial?: Submission;
  lockAdvanced?: string | null;
};

export function ClaimBuilder({ initial, lockAdvanced }: Props) {
  const [step, setStep] = useState(0);
  const [mode, setMode] = useState<"guided" | "advanced">(lockAdvanced ? "advanced" : "guided");
  const [dsl, setDsl] = useState("");
  const [dslError, setDslError] = useState("");
  const [run, setRun] = useState<RunDocument | null>(null);
  const [job, setJob] = useState<JobPublic | null>(null);
  const [formError, setFormError] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const idempotency = useRef(newIdempotencyKey());

  const form = useForm<GuidedValues>({
    resolver: zodResolver(guidedSchema),
    defaultValues: initial ? submissionToGuided(initial, unitIdFor) : emptyGuided(),
    mode: "onBlur",
  });
  const variables = useFieldArray({ control: form.control, name: "variables" });
  const assumptions = useFieldArray({ control: form.control, name: "assumptions" });
  const claims = useFieldArray({ control: form.control, name: "claims" });

  const examples = useQuery({
    queryKey: ["examples"],
    queryFn: () => api<ExampleCase[]>("/api/examples"),
  });

  useEffect(() => {
    const payload = initial ?? guidedToSubmission(form.getValues());
    setDsl(JSON.stringify(payload, null, 2));
    if (lockAdvanced) setMode("advanced");
    // form methods are stable; avoid resetting DSL on every keystroke
  }, [initial, lockAdvanced]);

  const watched = form.watch();
  const previewLatex = useMemo(() => {
    const claim = watched.claims?.[0];
    if (!claim || claim.kind !== "relation") return "";
    return `${expressionToLatex(claim.lhs)} ${claim.op} ${expressionToLatex(claim.rhs)}`;
  }, [watched.claims]);

  const compile = useMutation({
    mutationFn: (payload: Submission) =>
      api<CompilePreview>("/api/compile", { method: "POST", body: JSON.stringify(payload) }),
  });

  const currentPayload = (): Submission => {
    if (mode === "advanced") {
      try {
        return JSON.parse(dsl) as Submission;
      } catch (err) {
        throw new Error(`Invalid JSON: ${err instanceof Error ? err.message : "parse error"}`);
      }
    }
    if (!form.getValues("reviewed")) throw new Error("Review the formalization and confirm before running.");
    return guidedToSubmission(form.getValues());
  };

  const applyExample = (id: string) => {
    const selected = examples.data?.find((item) => item.id === id);
    if (!selected) return;
    const reason = guidedUnsupportedReason(selected.submission);
    form.reset(submissionToGuided(selected.submission, unitIdFor));
    setDsl(JSON.stringify(selected.submission, null, 2));
    setRun(null);
    if (reason) {
      setMode("advanced");
      setFormError(reason);
    } else {
      setMode("guided");
      setFormError("");
    }
  };

  const switchMode = (next: "guided" | "advanced") => {
    try {
      if (next === "advanced") {
        const payload = guidedToSubmission(form.getValues());
        setDsl(JSON.stringify(payload, null, 2));
        setMode("advanced");
        return;
      }
      const parsed = JSON.parse(dsl) as Submission;
      const reason = guidedUnsupportedReason(parsed);
      if (reason) {
        setFormError(reason);
        setMode("advanced");
        return;
      }
      form.reset(submissionToGuided(parsed, unitIdFor));
      setMode("guided");
      setFormError("");
    } catch (err) {
      setDslError(err instanceof Error ? err.message : "Invalid JSON");
      setMode("advanced");
    }
  };

  const runVerification = async () => {
    setFormError("");
    setDslError("");
    let payload: Submission;
    try {
      payload = currentPayload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Invalid submission");
      return;
    }
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    const key = idempotency.current;
    try {
      const created = await api<JobPublic>(
        "/api/jobs",
        {
          method: "POST",
          headers: { "Idempotency-Key": key },
          body: JSON.stringify(payload),
        },
        abortRef.current.signal,
      );
      setJob(created);
      await streamJobEvents(
        created.id,
        (update) => {
          setJob(update);
          if (update.document) setRun(update.document);
        },
        abortRef.current.signal,
      );
      const latest = await api<JobPublic>(`/api/jobs/${created.id}`);
      setJob(latest);
      if (latest.document) setRun(latest.document);
      idempotency.current = newIdempotencyKey();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Verification failed";
      setFormError(message);
    }
  };

  const cancel = async () => {
    abortRef.current?.abort();
    if (job?.id) {
      try {
        await api(`/api/jobs/${job.id}/cancel`, { method: "POST" });
      } catch {
        /* finished */
      }
    }
  };

  const insertOp = (token: string) => {
    const claim = form.getValues("claims.0");
    if (claim && claim.kind === "relation") {
      form.setValue("claims.0.lhs", `${claim.lhs}${token}`);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <section aria-label="Submission">
        <div className="mb-4 flex gap-2" role="group" aria-label="Editing mode">
          <Button variant={mode === "guided" ? "default" : "secondary"} onClick={() => switchMode("guided")}>
            Guided
          </Button>
          <Button variant={mode === "advanced" ? "default" : "secondary"} onClick={() => switchMode("advanced")}>
            Advanced DSL
          </Button>
        </div>
        <Label htmlFor="example">Template</Label>
        <NativeSelect id="example" className="mb-4" onChange={(e) => applyExample(e.target.value)} defaultValue="">
          <option value="">Choose a regression example…</option>
          {(examples.data ?? []).map((item) => (
            <option key={item.id} value={item.id}>
              {item.submission.title}
            </option>
          ))}
        </NativeSelect>
        {mode === "guided" ? (
          <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
            <ol className="flex flex-wrap gap-2 text-xs" aria-label="Steps">
              {STEPS.map((label, index) => (
                <li key={label} className={index === step ? "font-semibold text-accent" : "text-muted"}>
                  {index + 1}. {label}
                </li>
              ))}
            </ol>
            {step === 0 ? (
              <>
                <Label htmlFor="title">Title</Label>
                <Input id="title" {...form.register("title")} />
                <Label htmlFor="source">Scientific domain note (not verified)</Label>
                <textarea
                  id="source"
                  className="min-h-24 w-full rounded-md border border-line p-2 text-sm"
                  {...form.register("source_latex")}
                />
                <p className="text-sm text-muted">
                  There is no natural-language or LaTeX autoformalization. A rendered equation is a preview of the
                  structured fields.
                </p>
              </>
            ) : null}
            {step === 1 ? (
              <div className="space-y-3">
                {variables.fields.map((field, index) => (
                  <div key={field.id} className="grid gap-2 md:grid-cols-5">
                    <Input aria-label="Variable name" {...form.register(`variables.${index}.name`)} />
                    <NativeSelect
                      aria-label="Unit"
                      value={form.watch(`variables.${index}.unit`)}
                      onChange={(e) => {
                        form.setValue(`variables.${index}.unit`, e.target.value);
                        const dim = dimensionForUnit(e.target.value);
                        if (dim) form.setValue(`variables.${index}.dimension`, dim.join(","));
                      }}
                    >
                      {UNIT_PRESETS.map((unit) => (
                        <option key={unit.id} value={unit.id}>
                          {unit.label}
                        </option>
                      ))}
                      <option value="custom">custom vector</option>
                    </NativeSelect>
                    <Input aria-label="Dimension vector" {...form.register(`variables.${index}.dimension`)} />
                    <Input aria-label="Domain min" placeholder="min" {...form.register(`variables.${index}.domain_min`)} />
                    <Input aria-label="Domain max" placeholder="max" {...form.register(`variables.${index}.domain_max`)} />
                  </div>
                ))}
                <Button type="button" variant="ghost" onClick={() => variables.append({ name: "y", unit: "1", dimension: "0,0,0,0,0,0,0" })}>
                  Add variable
                </Button>
              </div>
            ) : null}
            {step === 2 ? (
              <div className="space-y-3">
                {assumptions.fields.map((field, index) => (
                  <div key={field.id} className="grid grid-cols-[1fr_auto_1fr] gap-2">
                    <Input aria-label="Assumption left" {...form.register(`assumptions.${index}.lhs`)} />
                    <NativeSelect {...form.register(`assumptions.${index}.op`)}>
                      {["==", "!=", ">", ">=", "<", "<="].map((op) => (
                        <option key={op}>{op}</option>
                      ))}
                    </NativeSelect>
                    <Input aria-label="Assumption right" {...form.register(`assumptions.${index}.rhs`)} />
                  </div>
                ))}
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => assumptions.append({ lhs: "x", op: ">", rhs: "0" })}
                >
                  Add assumption
                </Button>
              </div>
            ) : null}
            {step === 3 ? (
              <div className="space-y-3">
                {claims.fields.map((field, index) => {
                  const kind = form.watch(`claims.${index}.kind`);
                  return (
                    <div key={field.id} className="space-y-2 rounded-md border border-line p-3">
                      <div className="grid grid-cols-2 gap-2">
                        <NativeSelect {...form.register(`claims.${index}.kind`)}>
                          <option value="relation">relation</option>
                          <option value="limit">limit</option>
                          <option value="proof_hole">proof hole</option>
                        </NativeSelect>
                        <Input aria-label="Claim id" {...form.register(`claims.${index}.id`)} />
                      </div>
                      {kind === "relation" ? (
                        <>
                          <div className="flex flex-wrap gap-1">
                            {OPS.map((op) => (
                              <Button key={op} type="button" size="sm" variant="secondary" onClick={() => insertOp(op)}>
                                {op}
                              </Button>
                            ))}
                          </div>
                          <p className="text-xs text-muted">Examples: m*v**2/2 · x**2 · k*x**2/2</p>
                          <div className="grid grid-cols-[1fr_auto_1fr] gap-2">
                            <Input aria-label="Claim left" {...form.register(`claims.${index}.lhs`)} />
                            <NativeSelect {...form.register(`claims.${index}.op`)}>
                              {["==", "!=", ">", ">=", "<", "<="].map((op) => (
                                <option key={op}>{op}</option>
                              ))}
                            </NativeSelect>
                            <Input aria-label="Claim right" {...form.register(`claims.${index}.rhs`)} />
                          </div>
                        </>
                      ) : null}
                      {kind === "limit" ? (
                        <>
                          <Input aria-label="Limit expression" {...form.register(`claims.${index}.expression`)} />
                          <Input aria-label="Limit variable" {...form.register(`claims.${index}.variable`)} />
                          <Input aria-label="Expected value" {...form.register(`claims.${index}.expected`)} />
                        </>
                      ) : null}
                      {kind === "proof_hole" ? (
                        <Input aria-label="Hole description" {...form.register(`claims.${index}.description`)} />
                      ) : null}
                    </div>
                  );
                })}
                <Equation latex={previewLatex} caption="Live preview of the first relation. Not evidence that arbitrary LaTeX can be parsed." />
              </div>
            ) : null}
            {step === 4 ? (
              <>
                <Label htmlFor="budget">Budget (ms)</Label>
                <Input id="budget" type="number" {...form.register("budget_ms", { valueAsNumber: true })} />
                <fieldset className="space-y-1">
                  <legend className="text-sm font-medium">Verification mode</legend>
                  <label className="flex gap-2 text-sm">
                    <input type="radio" value="fast" {...form.register("verification_mode")} /> Fast · SMT-relative
                  </label>
                  <label className="flex gap-2 text-sm">
                    <input type="radio" value="certified" {...form.register("verification_mode")} /> Certified · kernel
                  </label>
                </fieldset>
                <label className="flex gap-2 text-sm">
                  <input type="checkbox" {...form.register("critical")} /> Critical obligation
                </label>
                <label className="flex gap-2 text-sm">
                  <input type="checkbox" {...form.register("reviewed")} /> I reviewed the formal object.
                </label>
                <pre className="overflow-x-auto rounded bg-surface-2 p-3 text-xs">
                  {JSON.stringify(guidedToSubmission(form.getValues()), null, 2)}
                </pre>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => compile.mutate(guidedToSubmission(form.getValues()))}
                >
                  Compile preview
                </Button>
                {compile.data ? (
                  <p className="text-sm" role="status">
                    {compile.data.ok ? compile.data.note : compile.data.errors.map((e) => e.message).join("; ")}
                  </p>
                ) : null}
              </>
            ) : null}
            <div className="flex gap-2">
              <Button type="button" variant="secondary" disabled={step === 0} onClick={() => setStep((s) => s - 1)}>
                Previous
              </Button>
              <Button type="button" variant="secondary" disabled={step === 4} onClick={() => setStep((s) => s + 1)}>
                Next
              </Button>
            </div>
          </form>
        ) : (
          <div>
            {lockAdvanced ? <p className="mb-2 text-sm text-warn">{lockAdvanced}</p> : null}
            <Label htmlFor="dsl">Explicit formalization · JSON</Label>
            <textarea
              id="dsl"
              spellCheck={false}
              className="min-h-72 w-full rounded-md border border-line p-2 font-mono text-sm"
              value={dsl}
              onChange={(e) => {
                setDsl(e.target.value);
                try {
                  JSON.parse(e.target.value);
                  setDslError("");
                } catch (err) {
                  setDslError(err instanceof Error ? `Invalid JSON: ${err.message}` : "Invalid JSON");
                }
              }}
            />
            {dslError ? (
              <p role="alert" className="text-sm text-bad">
                {dslError}
              </p>
            ) : (
              <p className="text-sm text-muted">Syntax looks like JSON. Backend validation remains authoritative.</p>
            )}
          </div>
        )}
        {(formError || Object.keys(form.formState.errors).length > 0) && (
          <p role="alert" className="mt-3 text-sm text-bad">
            {formError || "Check highlighted fields. Client checks assist; the API decides."}
          </p>
        )}
        <div className="mt-4 flex gap-2">
          <Button onClick={runVerification}>Run verification</Button>
          <Button variant="secondary" onClick={cancel}>
            Cancel
          </Button>
        </div>
        {job ? (
          <p className="mt-2 text-sm text-muted">
            Job {job.job_status}
            {job.operational_reason ? ` · ${job.operational_reason}` : ""}
          </p>
        ) : null}
      </section>
      <section aria-label="Result">
        {run ? (
          <ResultView
            run={run}
            onRevise={(doc) => {
              if (doc.submission) {
                form.reset(submissionToGuided(doc.submission, unitIdFor));
                setDsl(JSON.stringify(doc.submission, null, 2));
                setMode("guided");
              }
            }}
          />
        ) : (
          <p className="text-muted">The result will explain the conclusion first. Guarantee and evidence follow.</p>
        )}
      </section>
    </div>
  );
}
