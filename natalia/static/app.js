"use strict";
const $ = (id) => document.getElementById(id);
const DRAFT_KEY = "natalia.draft.v1";
const PRESETS = {
  dimensionless: ["0", "0", "0", "0", "0", "0", "0"],
  mass: ["1", "0", "0", "0", "0", "0", "0"],
  length: ["0", "1", "0", "0", "0", "0", "0"],
  time: ["0", "0", "1", "0", "0", "0", "0"],
  velocity: ["0", "1", "-1", "0", "0", "0", "0"],
  energy: ["1", "2", "-2", "0", "0", "0", "0"],
};
const labels = {
  ACCEPTED: "ACCEPTED",
  REFUTED: "REFUTED",
  INVALID: "INVALID",
  ABSTAIN: "INCONCLUSIVE",
  SMT_RELATIVE: "SMT RELATIVE",
  EXACT_WITNESS_CHECKED: "EXACT WITNESS",
  KERNEL_CHECKED: "KERNEL CHECKED",
  ADVISORY: "ADVISORY",
  STATIC_COMPILE: "STATIC COMPILE",
  certified: "VERIFIED",
  refuted: "REFUTED",
  unknown: "OPEN",
  invalid: "INVALID",
  succeeded: "COMPLETED",
  failed: "OPERATIONAL FAILURE",
  cancelled: "CANCELLED",
  timed_out: "TIMEOUT",
  rejected: "CAPACITY REJECTED",
  queued: "QUEUED",
  running: "RUNNING",
};
const titles = {
  ACCEPTED: "Obligations verified in supported fragment.",
  REFUTED: "Validated rational counterexample found.",
  INVALID: "Formalization requires correction.",
  ABSTAIN: "Formal obligations remain open or unverified.",
};
const descriptions = {
  ACCEPTED:
    "All declared obligations were discharged within the supported SMT fragment. The conclusion applies strictly to the explicit formalization and stated assumptions — not to the informal source text.",
  REFUTED:
    "An exact rational assignment satisfies all declared assumptions while violating at least one claim. The violation was independently checked using exact arithmetic.",
  INVALID:
    "Static compilation detected an invalid expression, unhandled symbol, or dimensional mismatch. No automated solvers were dispatched.",
  ABSTAIN:
    "The available evidence cannot close the investigation. Timeouts, cancellations, and unhandled operators appear here, without counting as refutations.",
};
const OPS = ["==", "!=", ">", ">=", "<", "<="];
let currentRun = null,
  examples = [],
  offset = 0,
  activePage = "home",
  busy = false,
  mode = "guided",
  activeJobId = null,
  pollTimer = null,
  abortController = null,
  reviewedFingerprint = "";

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function badge(status) {
  return element("span", `badge ${status}`, labels[status] || status);
}

function error(message) {
  const errNode = $("error");
  if (!errNode) return;
  errNode.textContent = message;
  errNode.hidden = !message;
}

function announce(text) {
  const live = $("result-empty");
  if (live) live.setAttribute("aria-live", "polite");
  document.title = text ? `${text} · NatalIA` : "NatalIA · Scientific Verification Workbench";
}

async function api(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = "Service unavailable.";
    try {
      const body = await response.json();
      detail = Array.isArray(body.detail)
        ? body.detail.map((x) => `${x.loc.join(".")}: ${x.msg}`).join("\n")
        : typeof body.detail === "object"
          ? body.detail.detail || JSON.stringify(body.detail)
          : body.detail || detail;
    } catch {
      /* Fallback string kept. */
    }
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.json();
}

function showPage(page) {
  const pages = [
    "home",
    "laboratory",
    "library",
    "history",
    "evaluation",
    "observability",
    "scope",
  ];
  if (!pages.includes(page)) page = "home";
  activePage = page;
  document
    .querySelectorAll(".page")
    .forEach((node) => (node.hidden = node.id !== `page-${page}`));
  document
    .querySelectorAll(".nav-item")
    .forEach((node) =>
      node.classList.toggle("active", node.dataset.page === page),
    );
  if (page === "history") loadHistory();
  if (page === "observability") loadStats();
  if (page === "home") loadHome();
  if (page === "library") loadLibrary();
  if (page === "evaluation") loadBench();
}

document.querySelectorAll("[data-page]").forEach((node) =>
  node.addEventListener("click", () => {
    location.hash = node.dataset.page;
  }),
);

window.addEventListener("hashchange", () => showPage(location.hash.slice(1)));

function emptyDimension() {
  return ["0", "0", "0", "0", "0", "0", "0"];
}

function addVariable(name = "", dimension = emptyDimension()) {
  const row = element("div", "row");
  const nameInput = element("input");
  nameInput.placeholder = "variable name (e.g. x, m)";
  nameInput.value = name;
  nameInput.maxLength = 24;
  const preset = element("select");
  for (const [key, value] of Object.entries(PRESETS)) {
    const option = element("option", "", key);
    option.value = value.join(",");
    preset.append(option);
  }
  const custom = element("option", "", "custom");
  custom.value = "custom";
  preset.append(custom);
  const dims = element("input");
  dims.value = dimension.join(",");
  dims.setAttribute("aria-label", "Dimensional exponents [M,L,T,I,Theta,N,J]");
  const match = Object.values(PRESETS).find(
    (item) => item.join(",") === dimension.join(","),
  );
  preset.value = match ? match.join(",") : "custom";
  preset.addEventListener("change", () => {
    if (preset.value !== "custom") dims.value = preset.value;
    onGuidedEdit();
  });
  const remove = element("button", "text-button", "Remove");
  remove.type = "button";
  remove.addEventListener("click", () => {
    row.remove();
    onGuidedEdit();
  });
  nameInput.addEventListener("input", onGuidedEdit);
  dims.addEventListener("input", onGuidedEdit);
  row.append(nameInput, preset, dims, remove);
  $("variables").append(row);
}

function addAssumption(item = { lhs: "", op: ">", rhs: "0" }) {
  const row = element("div", "row");
  const lhs = element("input");
  lhs.value = item.lhs;
  lhs.placeholder = "left expression";
  const op = element("select");
  OPS.forEach((value) => op.append(element("option", "", value)));
  op.value = item.op || "==";
  const rhs = element("input");
  rhs.value = item.rhs;
  rhs.placeholder = "right expression";
  const remove = element("button", "text-button", "Remove");
  remove.type = "button";
  remove.addEventListener("click", () => {
    row.remove();
    onGuidedEdit();
  });
  [lhs, op, rhs].forEach((node) => node.addEventListener("input", onGuidedEdit));
  op.addEventListener("change", onGuidedEdit);
  row.append(lhs, op, rhs, remove);
  $("assumptions").append(row);
}

function addClaim(item) {
  const claim =
    item || { kind: "relation", id: "claim", lhs: "", op: ">=", rhs: "0" };
  const box = element("div", "claim-card");
  const kind = element("select");
  ["relation", "limit", "proof_hole"].forEach((value) =>
    kind.append(element("option", "", value)),
  );
  kind.value = claim.kind || "relation";
  const id = element("input");
  id.value = claim.id || "claim";
  id.placeholder = "claim identifier";
  const body = element("div", "claim-body");
  function renderBody() {
    body.replaceChildren();
    if (kind.value === "relation") {
      const lhs = element("input");
      lhs.value = claim.lhs || "";
      lhs.placeholder = "left side (e.g. m*v**2/2)";
      const op = element("select");
      OPS.forEach((value) => op.append(element("option", "", value)));
      op.value = claim.op || "==";
      const rhs = element("input");
      rhs.value = claim.rhs || "";
      rhs.placeholder = "right side (e.g. 0)";
      [lhs, op, rhs].forEach((node) =>
        node.addEventListener("input", onGuidedEdit),
      );
      op.addEventListener("change", onGuidedEdit);
      body.append(lhs, op, rhs);
    } else if (kind.value === "limit") {
      const expr = element("input");
      expr.value = claim.expression || "";
      expr.placeholder = "expression (e.g. (2*x**2+1)/(x**2+3))";
      const variable = element("input");
      variable.value = claim.variable || "";
      variable.placeholder = "variable (e.g. x)";
      const expected = element("input");
      expected.value = claim.expected || "0";
      expected.placeholder = "expected value";
      [expr, variable, expected].forEach((node) =>
        node.addEventListener("input", onGuidedEdit),
      );
      body.append(expr, variable, expected);
    } else {
      const description = element("input");
      description.value = claim.description || "";
      description.placeholder = "explicit gap / unproven lemma description";
      description.addEventListener("input", onGuidedEdit);
      body.append(description);
    }
  }
  kind.addEventListener("change", () => {
    renderBody();
    onGuidedEdit();
  });
  id.addEventListener("input", onGuidedEdit);
  const remove = element("button", "text-button", "Remove");
  remove.type = "button";
  remove.addEventListener("click", () => {
    box.remove();
    onGuidedEdit();
  });
  box.append(kind, id, remove, body);
  $("claims").append(box);
  renderBody();
}

function readGuided() {
  const variables = {};
  for (const row of $("variables").children) {
    const inputs = row.querySelectorAll("input");
    const name = inputs[0].value.trim();
    if (!name) continue;
    const dimension = inputs[1].value.split(",").map((x) => x.trim());
    variables[name] = { dimension };
  }
  const assumptions = [...$("assumptions").children].map((row) => {
    const fields = [...row.querySelectorAll("input, select")];
    return { lhs: fields[0].value, op: fields[1].value, rhs: fields[2].value };
  });
  const claims = [...$("claims").children].map((card) => {
    const kind = card.querySelector("select").value;
    const id = card.querySelector("input").value;
    const fields = [...card.querySelector(".claim-body").querySelectorAll("input, select")];
    if (kind === "relation")
      return { kind, id, lhs: fields[0].value, op: fields[1].value, rhs: fields[2].value };
    if (kind === "limit")
      return {
        kind,
        id,
        expression: fields[0].value,
        variable: fields[1].value,
        target: "infinity",
        expected: fields[2].value,
      };
    return { kind, id, description: fields[0].value };
  });
  return {
    schema_version: "1.0",
    title: $("title").value || "Untitled Investigation",
    source_latex: $("source-latex").value,
    variables,
    assumptions,
    claims,
    budget_ms: Number($("budget").value) || 5000,
    verification_mode: $("mode-certified")?.checked ? "certified" : "fast",
    critical: Boolean($("critical")?.checked),
  };
}

function fillGuided(submission, unsupported = "") {
  $("title").value = submission.title || "";
  $("source-latex").value = submission.source_latex || "";
  $("budget").value = submission.budget_ms ?? 5000;
  if ($("mode-certified")) $("mode-certified").checked = submission.verification_mode === "certified";
  if ($("mode-fast")) $("mode-fast").checked = submission.verification_mode !== "certified";
  if ($("critical")) $("critical").checked = Boolean(submission.critical);
  $("variables").replaceChildren();
  $("assumptions").replaceChildren();
  $("claims").replaceChildren();
  for (const [name, spec] of Object.entries(submission.variables || {}))
    addVariable(name, spec.dimension);
  for (const item of submission.assumptions || []) addAssumption(item);
  for (const item of submission.claims || []) addClaim(item);
  if (unsupported) error(unsupported);
  refreshReview();
}

function payloadFingerprint(payload) {
  return JSON.stringify(payload);
}

function refreshReview() {
  let payload;
  try {
    payload = mode === "guided" ? readGuided() : JSON.parse($("dsl").value);
  } catch (e) {
    $("review-summary").textContent = `Invalid JSON: ${e.message}`;
    return payload;
  }
  const lines = [
    `Title: ${payload.title}`,
    `Variables: ${Object.keys(payload.variables || {}).join(", ") || "none"}`,
    `Domains: ${Object.entries(payload.variables || {})
      .map(([name, spec]) =>
        spec.domain_min != null
          ? `${name} in [${spec.domain_min}, ${spec.domain_max ?? "inf"}]`
          : `${name} in R (unbounded)`,
      )
      .join("; ") || "none"}`,
    `Assumptions: ${(payload.assumptions || [])
      .map((a) => `${a.lhs} ${a.op} ${a.rhs}`)
      .join("; ") || "none"}`,
    `Claims: ${(payload.claims || [])
      .map((c) => c.id)
      .join(", ") || "none"}`,
    `Timeout Budget: ${payload.budget_ms} ms`,
    "Original source text is not verified by solvers. Review confirmation does not prove semantic fidelity.",
  ];
  $("review-summary").textContent = lines.join("\n");
  if (payloadFingerprint(payload) !== reviewedFingerprint) $("reviewed").checked = false;
  $("budget-label").textContent = `Max budget: ${(payload.budget_ms ?? 5000) / 1000} s`;
  return payload;
}

function persistDraft() {
  try {
    localStorage.setItem(
      DRAFT_KEY,
      JSON.stringify({ mode, payload: refreshReview() }),
    );
  } catch {
    /* Quota or private mode */
  }
}

function onGuidedEdit() {
  try {
    $("dsl").value = JSON.stringify(readGuided(), null, 2);
  } catch {
    /* Incomplete form */
  }
  refreshReview();
  persistDraft();
}

function setMode(next) {
  const fromGuided = mode === "guided";
  if (fromGuided && next === "advanced") {
    try {
      $("dsl").value = JSON.stringify(readGuided(), null, 2);
    } catch (e) {
      error(`Could not generate JSON: ${e.message}`);
    }
  }
  if (!fromGuided && next === "guided") {
    try {
      fillGuided(JSON.parse($("dsl").value));
    } catch (e) {
      error(
        `Advanced JSON does not fit standard form and was preserved. ${e.message}`,
      );
      fillGuided(
        {
          title: "Advanced Formalization",
          source_latex: "",
          variables: { x: { dimension: emptyDimension() } },
          assumptions: [],
          claims: [{ kind: "relation", id: "claim", lhs: "x", op: "==", rhs: "x" }],
          budget_ms: 5000,
        },
        "Advanced content preserved in JSON editor.",
      );
    }
  }
  mode = next;
  $("guided").hidden = mode !== "guided";
  $("advanced").hidden = mode !== "advanced";
  $("mode-guided").classList.toggle("active", mode === "guided");
  $("mode-advanced").classList.toggle("active", mode === "advanced");
  $("mode-guided").setAttribute("aria-pressed", String(mode === "guided"));
  $("mode-advanced").setAttribute("aria-pressed", String(mode === "advanced"));
  refreshReview();
}

$("mode-guided").addEventListener("click", () => setMode("guided"));
$("mode-advanced").addEventListener("click", () => setMode("advanced"));
$("add-var").addEventListener("click", () => {
  addVariable();
  onGuidedEdit();
});
$("add-assumption").addEventListener("click", () => {
  addAssumption();
  onGuidedEdit();
});
$("add-claim").addEventListener("click", () => {
  addClaim();
  onGuidedEdit();
});
$("title").addEventListener("input", onGuidedEdit);
$("source-latex").addEventListener("input", onGuidedEdit);
$("budget").addEventListener("input", onGuidedEdit);
$("reviewed").addEventListener("change", () => {
  if ($("reviewed").checked) reviewedFingerprint = payloadFingerprint(refreshReview());
});

function loadExample() {
  const selected = examples.find((x) => x.id === $("example").value);
  if (!selected) return;
  $("dsl").value = JSON.stringify(selected.submission, null, 2);
  fillGuided(selected.submission);
  const payload = mode === "guided" ? readGuided() : selected.submission;
  reviewedFingerprint = payloadFingerprint(payload);
  $("reviewed").checked = true;
  error("");
  persistDraft();
}

function updateBudget() {
  refreshReview();
}

$("example").addEventListener("change", loadExample);

function markCustomEditor(label = "Custom Formalization") {
  let option = $("example").querySelector('option[value="custom"]');
  if (!option) {
    option = element("option");
    option.value = "custom";
    $("example").prepend(option);
  }
  option.textContent = label;
  $("example").value = "custom";
}

$("dsl").addEventListener("input", () => {
  updateBudget();
  markCustomEditor();
  persistDraft();
});

$("format").addEventListener("click", () => {
  try {
    $("dsl").value = JSON.stringify(JSON.parse($("dsl").value), null, 2);
    error("");
  } catch (e) {
    error(`Invalid JSON: ${e.message}`);
  }
});

function details(label, content) {
  const d = element("details");
  d.append(element("summary", "", label), element("pre", "", content));
  return d;
}

function renderRun(run) {
  currentRun = run;
  $("result-empty").hidden = true;
  $("result").hidden = false;
  $("export").disabled = false;
  const out = $("result");
  out.replaceChildren();
  const operational = run.job_status && run.job_status !== "succeeded";
  const row = element("div", "verdict-row");
  row.append(
    badge(operational ? run.job_status : run.conclusion || run.verdict),
    element("span", "muted", `${((run.duration_ms || 0) / 1000).toFixed(2)} s`),
  );
  if (run.guarantee_level) row.append(badge(run.guarantee_level));
  if (run.verification_mode)
    row.append(element("span", "muted", `mode: ${run.verification_mode}`));
  if (operational)
    row.append(element("span", "muted", "Operational status != claim conclusion"));
  out.append(
    row,
    element("h3", "result-title", titles[run.verdict] || "Execution completed without scientific verdict."),
    element("p", "result-description", descriptions[run.verdict] || run.reason || ""),
  );
  const answers = element("ol", "answers");
  const items = [
    ["What was evaluated?", run.submission?.title || run.title || "—"],
    [
      "Under which assumptions?",
      `${(run.submission?.assumptions || []).length} assumption(s); declared user domain.`,
    ],
    ["What conclusion was reached?", `${run.conclusion || run.verdict || "none"} · ${run.reason || ""}`],
    [
      "Which evidence supports it?",
      (run.obligations || [])
        .map((o) => `${o.id}: ${labels[o.status] || o.status} (${o.trust || o.oracle})`)
        .join("; ") || "No persisted obligations.",
    ],
    [
      "What remains open?",
      (run.proof_holes || []).join(", ") || "No open proof gaps declared.",
    ],
    [
      "What can you do next?",
      run.verdict === "REFUTED"
        ? "Inspect the counterexample assignment below and assess whether assumptions need refinement."
        : run.verdict === "INVALID"
          ? "Correct dimensions or expression syntax and re-verify."
          : (run.conclusion || run.verdict) === "ACCEPTED"
            ? run.guarantee_level === "KERNEL_CHECKED"
              ? "Acceptance is certified by the polynomial kernel, bound to the obligation digest."
              : "Acceptance is relative to the SMT solver; treated as mathematically sound within the supported fragment."
            : "Review domain constraints, simplify expressions, or choose an alternative solver.",
    ],
  ];
  for (const [q, a] of items) {
    const li = element("li");
    li.append(element("strong", "", q + " "), document.createTextNode(a));
    answers.append(li);
  }
  out.append(answers);
  const meta = element("div", "result-meta");
  for (const [label, value] of [
    [
      "VERIFIED OBLIGATIONS",
      `${(run.obligations || []).filter((o) => o.status === "certified").length} of ${(run.obligations || []).length}`,
    ],
    ["CALIBRATED CONFIDENCE", "Not available (uncalibrated)"],
    ["JOB STATUS", labels[run.job_status] || run.job_status || "COMPLETED"],
    ["GUARANTEE LEVEL", labels[run.guarantee_level] || run.guarantee_level || "unclassified"],
  ]) {
    const cell = element("div");
    cell.append(element("span", "", label), element("strong", "", value));
    meta.append(cell);
  }
  out.append(meta, element("p", "evidence-title", "EVIDENCE TRAIL"));
  for (const item of run.obligations || []) {
    const card = element("article", "obligation");
    const top = element("div", "obligation-top");
    top.append(element("strong", "", item.id), badge(item.status));
    card.append(
      top,
      element("span", "oracle-name", item.oracle || item.adapter_id || ""),
      element("p", "", item.reason),
    );
    if (item.counterexample) {
      const values = Object.entries(item.counterexample)
        .map(([k, v]) => `${k} = ${v}`)
        .join(" · ");
      const evaluation = item.evaluation || {};
      card.append(
        element(
          "div",
          "witness",
          `Witness values: ${values}\nAssumptions: confirmed to hold under independent check.\nEvaluation: ${evaluation.lhs} ${evaluation.op} ${evaluation.rhs} -> false\nMethod: exact rational arithmetic over SMT witness`,
        ),
      );
    }
    if (item.artifacts && item.artifacts.region) {
      card.append(
        element(
          "div",
          "witness",
          `Region: ${JSON.stringify(item.artifacts.region)}\nLeft enclosure: ${item.artifacts.lhs_enclosure}\nRight enclosure: ${item.artifacts.rhs_enclosure}\nRounding: ${item.artifacts.rounding} (exact enclosure)`,
        ),
      );
    }
    if (item.cas_result !== undefined)
      card.append(
        element(
          "div",
          "witness",
          `CAS limit: ${item.cas_result} · expected: ${item.expected}\nIndicative result without formal kernel certificate.`,
        ),
      );
    if (item.artifacts && item.artifacts.certificate)
      card.append(details("Kernel Certificate", JSON.stringify(item.artifacts.certificate, null, 2)));
    if (item.artifacts && item.artifacts.lean_export)
      card.append(details("Lean Export (not checked by Lean kernel)", item.artifacts.lean_export));
    if (item.obligation_hash)
      card.append(element("p", "trace-id", `obligation digest: ${item.obligation_hash}`));
    out.append(card);
  }
  const trace = element("details");
  trace.append(element("summary", "", "Execution Spans & Traceability"));
  for (const span of run.spans || []) {
    const line = element("div", "trace-item");
    line.append(
      element("span", "", `${span.name} / ${span.oracle}`),
      element("span", "", `${Number(span.duration_ms || 0).toFixed(2)} ms`),
    );
    trace.append(line);
  }
  trace.append(
    element("p", "trace-id", `trace_id: ${run.trace_id || ""}`),
    element("p", "trace-id", `input_sha256: ${run.input_sha256 || ""}`),
  );
  const actions = element("div", "result-actions");
  const dup = element("button", "secondary-button", "Duplicate Investigation");
  dup.type = "button";
  dup.addEventListener("click", () => {
    if (!run.submission) return;
    $("dsl").value = JSON.stringify(run.submission, null, 2);
    fillGuided(run.submission);
    markCustomEditor("Investigation Copy");
    $("reviewed").checked = false;
    location.hash = "laboratory";
    showPage("laboratory");
  });
  const rec = element("button", "secondary-button", "Recheck Certificate");
  rec.type = "button";
  rec.addEventListener("click", async () => {
    const cert = (run.obligations || []).find((o) => o.artifacts && o.artifacts.certificate);
    if (!cert) {
      error("This execution does not have a kernel certificate to recheck.");
      return;
    }
    try {
      const checked = await api("/api/certificates/recheck", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ submission: run.submission, certificate: cert.artifacts.certificate }),
      });
      error(
        checked.accepted
          ? `Independent recheck accepted (${checked.guarantee_level}).`
          : `Recheck rejected: ${checked.reason}`,
      );
    } catch (e) {
      error(e.message);
    }
  });
  actions.append(dup, rec);
  out.append(
    trace,
    actions,
    details("Executed Formalization", JSON.stringify(run.submission || {}, null, 2)),
    details(
      "Versions & Trust Boundaries",
      JSON.stringify(
        {
          reason: run.reason,
          scope: run.scope,
          guarantee: run.guarantee,
          versions: run.versions,
          job_status: run.job_status,
          operational_kind: run.operational_kind,
        },
        null,
        2,
      ),
    ),
  );
  announce(labels[run.verdict] || "Result available");
}

function currentPayload() {
  if (mode === "advanced") return JSON.parse($("dsl").value);
  if (!$("reviewed").checked)
    throw new Error("Please review the formalization and check confirmation before verifying.");
  const payload = readGuided();
  $("dsl").value = JSON.stringify(payload, null, 2);
  return payload;
}

function setBusy(on) {
  busy = on;
  $("run").disabled = on;
  $("example").disabled = on;
  $("cancel").hidden = !on;
  $("run").textContent = on ? "Verifying…" : "Verify Claim ↗";
}

$("cancel").addEventListener("click", async () => {
  if (abortController) abortController.abort();
  if (activeJobId) {
    try {
      await api(`/api/jobs/${activeJobId}/cancel`, { method: "POST" });
    } catch {
      /* Job may have completed already */
    }
  }
});

$("run").addEventListener("click", async () => {
  if (busy) return;
  let payload;
  try {
    payload = currentPayload();
  } catch (e) {
    error(mode === "advanced" || e instanceof SyntaxError ? `Invalid JSON: ${e.message}` : e.message);
    return;
  }
  error("");
  setBusy(true);
  $("export").disabled = true;
  $("result").hidden = true;
  $("result-empty").hidden = false;
  $("result-empty").classList.add("loading");
  $("result-empty").querySelector("h3").textContent = "Verifying formalization…";
  $("result-empty").querySelector("p").textContent =
    "The job was persisted to storage before solving. You can cancel; operational status is distinct from a scientific verdict.";
  abortController = new AbortController();
  try {
    const job = await api("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: abortController.signal,
    });
    activeJobId = job.id;
    const run = await waitForJob(job.id);
    renderRun(run);
    await loadStats();
  } catch (e) {
    if (e.name === "AbortError") error("HTTP request aborted. If computation continues in background, use Cancel.");
    else error(`Verification could not complete: ${e.message}`);
    if (currentRun) renderRun(currentRun);
    else {
      $("result-empty").querySelector("h3").textContent = "Execution could not complete.";
      $("result-empty").querySelector("p").textContent =
        "Review the error notification. Operational failures do not imply mathematical refutation.";
    }
  } finally {
    setBusy(false);
    activeJobId = null;
    abortController = null;
    $("result-empty").classList.remove("loading");
  }
});

async function waitForJob(id) {
  if (window.EventSource) {
    const run = await new Promise((resolve, reject) => {
      const source = new EventSource(`/api/jobs/${id}/events`);
      const timer = setTimeout(() => {
        source.close();
        reject(new Error("SSE event stream timed out."));
      }, 75000);
      source.addEventListener("job", async (ev) => {
        const body = JSON.parse(ev.data);
        $("result-empty").querySelector("p").textContent =
          `Job status: ${labels[body.job_status] || body.job_status}. This tracks execution lifecycle, not claim truth.`;
        if (["succeeded", "failed", "cancelled", "timed_out", "rejected"].includes(body.job_status)) {
          clearTimeout(timer);
          source.close();
          try {
            const job = await api(`/api/jobs/${id}`);
            if (job.document) resolve(job.document);
            else reject(new Error(`Job ${job.job_status}: ${job.operational_reason || "no document"}`));
          } catch (err) {
            reject(err);
          }
        }
      });
      source.onerror = () => {
        clearTimeout(timer);
        source.close();
        reject(new Error("sse_fallback"));
      };
    }).catch(() => null);
    if (run) return run;
  }
  for (let i = 0; i < 300; i++) {
    const job = await api(`/api/jobs/${id}`);
    $("result-empty").querySelector("p").textContent =
      `Job status: ${labels[job.job_status] || job.job_status}. This tracks execution lifecycle, not claim truth.`;
    if (job.document) return job.document;
    if (["failed", "cancelled", "timed_out", "rejected"].includes(job.job_status) && !job.document)
      throw new Error(`Job ${job.job_status}: ${job.operational_reason || "no document"}`);
    await new Promise((resolve) => {
      pollTimer = setTimeout(resolve, 250);
    });
  }
  throw new Error("Progress polling timed out.");
}

$("export").addEventListener("click", () => {
  if (!currentRun) return;
  const payload = {
    replay_schema: "natalia-replay-1.0",
    natalia_version: currentRun.versions?.natalia,
    input_sha256: currentRun.input_sha256,
    submission: currentRun.submission,
    obligations: currentRun.obligations,
    verdict: currentRun.verdict,
    report: currentRun,
  };
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }),
  );
  const link = element("a");
  link.href = url;
  link.download = `natalia-${currentRun.id}.json`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

async function loadHistory() {
  try {
    const query = encodeURIComponent($("history-query")?.value || "");
    const verdict = $("history-verdict")?.value || "";
    const history = await api(
      `/api/runs?limit=10&offset=${offset}&q=${query}${verdict ? `&verdict=${verdict}` : ""}`,
    );
    $("history").replaceChildren();
    $("history-total").textContent = `${history.total} verifications recorded`;
    $("nav-count").textContent = history.total;
    if (!history.items.length) {
      $("history").append(
        element(
          "p",
          "table-empty",
          "No verification runs recorded on this page. Start in the workbench.",
        ),
      );
    } else {
      const table = element("table"),
        head = element("thead"),
        tr = element("tr");
      ["", "INVESTIGATION", "JOB STATUS", "VERDICT", "DURATION", "ACTIONS"].forEach((x) =>
        tr.append(element("th", "", x)),
      );
      head.append(tr);
      table.append(head);
      const body = element("tbody");
      for (const run of history.items) {
        const row = element("tr"),
          pick = element("td"),
          check = element("input");
        check.type = "checkbox";
        check.dataset.id = run.id;
        pick.append(check);
        const title = element("td", "", run.title);
        title.append(
          element("small", "", new Date(run.created_at).toLocaleString("en-US")),
        );
        const job = element("td");
        job.append(badge(run.job_status || "succeeded"));
        const verdictCell = element("td");
        if (run.verdict) verdictCell.append(badge(run.verdict));
        else verdictCell.append(element("span", "muted", "no verdict"));
        const action = element("td"),
          open = element("button", "text-button", "Open ↗"),
          dup = element("button", "text-button", "Duplicate");
        open.setAttribute("aria-label", `Open ${run.title}`);
        open.addEventListener("click", async () => {
          open.disabled = true;
          try {
            const full = await api(`/api/runs/${run.id}`);
            const submission = full.submission || full.document?.submission;
            if (submission) {
              $("dsl").value = JSON.stringify(submission, null, 2);
              fillGuided(submission);
            }
            markCustomEditor("Reopened from History");
            renderRun(full.document || full);
            location.hash = "laboratory";
            showPage("laboratory");
            error("");
          } catch (e) {
            open.textContent = `Error: ${e.message}`;
          } finally {
            open.disabled = false;
          }
        });
        dup.addEventListener("click", async () => {
          const full = await api(`/api/runs/${run.id}`);
          const submission = full.submission || full.document?.submission;
          if (!submission) return;
          $("dsl").value = JSON.stringify(submission, null, 2);
          fillGuided(submission);
          markCustomEditor("Investigation Copy");
          $("reviewed").checked = false;
          location.hash = "laboratory";
          showPage("laboratory");
        });
        action.append(open, dup);
        row.append(
          pick,
          title,
          job,
          verdictCell,
          element("td", "", `${((run.duration_ms || 0) / 1000).toFixed(2)} s`),
          action,
        );
        body.append(row);
      }
      table.append(body);
      $("history").append(table);
    }
    $("prev").disabled = offset === 0;
    $("next").disabled = offset + 10 >= history.total;
    $("page-number").textContent = `Page ${Math.floor(offset / 10) + 1}`;
  } catch (e) {
    $("history").replaceChildren(
      element("p", "error-box", `History unavailable: ${e.message}`),
    );
  }
}

$("compare").addEventListener("click", async () => {
  const ids = [...document.querySelectorAll("#history input[type=checkbox]:checked")].map(
    (node) => node.dataset.id,
  );
  if (ids.length !== 2) {
    $("compare-view").hidden = false;
    $("compare-view").textContent = "Please select exactly two investigations to compare.";
    return;
  }
  const [a, b] = await Promise.all(ids.map((id) => api(`/api/runs/${id}`)));
  const left = a.submission || {},
    right = b.submission || {};
  $("compare-view").hidden = false;
  $("compare-view").replaceChildren(
    element("h2", "", "Investigation Comparison"),
    element(
      "pre",
      "",
      [
        `A: ${left.title} -> ${a.verdict} (${a.job_status || "succeeded"})`,
        `B: ${right.title} -> ${b.verdict} (${b.job_status || "succeeded"})`,
        `Assumptions A: ${JSON.stringify(left.assumptions)}`,
        `Assumptions B: ${JSON.stringify(right.assumptions)}`,
        `Domain A: ${JSON.stringify(left.variables)}`,
        `Domain B: ${JSON.stringify(right.variables)}`,
      ].join("\n"),
    ),
  );
});

$("history-query").addEventListener("input", () => {
  offset = 0;
  loadHistory();
});
$("history-verdict").addEventListener("change", () => {
  offset = 0;
  loadHistory();
});
$("prev").addEventListener("click", () => {
  offset = Math.max(0, offset - 10);
  loadHistory();
});
$("next").addEventListener("click", () => {
  offset += 10;
  loadHistory();
});
$("refresh-history").addEventListener("click", loadHistory);

async function loadStats() {
  try {
    const stats = await api("/api/stats");
    $("nav-count").textContent = stats.total;
    $("stats").replaceChildren();
    for (const [label, value, note] of [
      ["Total Verifications", stats.total, "Persisted scientific history"],
      [
        "Average Duration",
        `${(stats.average_duration_ms / 1000).toFixed(2)} s`,
        "Includes worker initialization",
      ],
      ["Inconclusive (Abstain)", stats.verdicts.ABSTAIN || 0, "Unclosed formal obligations"],
      ["Active Workers", stats.active_runs, "In current API server process"],
      ["Queued Tasks", stats.queued ?? 0, "Queued jobs awaiting worker claim"],
    ]) {
      const card = element("div", "stat");
      card.append(
        element("div", "stat-label", label),
        element("div", "stat-value", String(value)),
        element("div", "stat-note", note),
      );
      $("stats").append(card);
    }
    $("distribution").replaceChildren();
    for (const verdict of ["ACCEPTED", "REFUTED", "ABSTAIN", "INVALID"]) {
      const row = element("div", "bar-row"),
        label = element("div", "bar-label"),
        count = stats.verdicts[verdict] || 0;
      label.append(
        element("span", "", labels[verdict]),
        element("span", "", String(count)),
      );
      const progress = element("progress");
      progress.max = Math.max(stats.total, 1);
      progress.value = count;
      progress.setAttribute("aria-label", labels[verdict]);
      row.append(label, progress);
      $("distribution").append(row);
    }
  } catch (e) {
    $("stats").replaceChildren(
      element("p", "error-box", `Metrics unavailable: ${e.message}`),
    );
  }
}

async function health() {
  try {
    const caps = await api("/api/capabilities");
    $("health-label").replaceChildren(
      document.createTextNode("Environment Ready"),
      element("small", "", `Local · v${caps.version || "0.5.0"}`),
    );
    $("health-dot").className = "tiny-dot";
  } catch {
    try {
      await api("/health/ready");
      $("health-label").textContent = "Environment Ready";
    } catch {
      $("health-label").textContent = "Environment Unavailable";
      $("health-dot").className = "";
    }
  }
}

async function init() {
  showPage(location.hash.slice(1));
  try {
    examples = await api("/api/examples");
    $("example").replaceChildren();
    for (const item of examples) {
      const option = element("option", "", item.submission.title);
      option.value = item.id;
      $("example").append(option);
    }
    const draft = localStorage.getItem(DRAFT_KEY);
    if (draft) {
      const parsed = JSON.parse(draft);
      $("dsl").value = JSON.stringify(parsed.payload, null, 2);
      fillGuided(parsed.payload);
      markCustomEditor("Restored Local Draft");
    } else loadExample();
    $("run").disabled = false;
  } catch (e) {
    error(`Failed to load examples: ${e.message}`);
    $("run").disabled = false;
  }
  await Promise.allSettled([health(), loadStats(), loadHome()]);
  try {
    if (!localStorage.getItem("natalia.onboard.v1") && $("onboard")?.showModal) {
      $("onboard").showModal();
    }
  } catch {
    /* Dialog unsupported */
  }
}

setInterval(() => {
  health();
  if (activePage === "observability") loadStats();
}, 10000);

let wizardStep = 0;
let catalog = [];

function setWizard(step) {
  wizardStep = Math.max(0, Math.min(5, step));
  document.querySelectorAll("#wizard-steps li").forEach((node) => {
    node.classList.toggle("active", Number(node.dataset.step) === wizardStep);
  });
  document.querySelectorAll(".wizard-pane").forEach((node) => {
    node.hidden = Number(node.dataset.pane) !== wizardStep;
  });
}

if ($("wizard-next")) {
  $("wizard-next").addEventListener("click", () => {
    setWizard(wizardStep + 1);
    previewCompile();
  });
  $("wizard-prev").addEventListener("click", () => setWizard(wizardStep - 1));
  setWizard(0);
}

async function previewCompile() {
  try {
    const payload = mode === "guided" ? readGuided() : JSON.parse($("dsl").value);
    const result = await api("/api/compile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!result.ok && result.errors?.length) {
      error(result.errors.map((item) => item.message).join("\n"));
    } else if (!busy) error("");
  } catch {
    /* Expected while typing incomplete payload */
  }
}

async function loadHome() {
  const featured = $("featured");
  const recent = $("recent");
  const sys = $("home-system");
  if (!featured) return;
  featured.replaceChildren();
  try {
    const items = await api("/api/catalog/featured");
    if (!items.length) featured.append(element("p", "helper", "No featured examples found."));
    for (const item of items) {
      const card = element("article", "case-card");
      card.append(
        element("h3", "", item.title),
        element("p", "", item.question),
        element("p", "helper", item.recommended_reason),
      );
      const go = element("button", "secondary-button", "Use This Problem");
      go.type = "button";
      go.addEventListener("click", () => openCase(item));
      card.append(go);
      featured.append(card);
    }
  } catch (e) {
    featured.append(element("p", "error-box", e.message));
  }
  try {
    const history = await api("/api/runs?limit=5&offset=0");
    recent.replaceChildren();
    if (!history.items.length)
      recent.append(
        element("p", "helper", "No verifications logged yet on this computer."),
      );
    for (const run of history.items) {
      const row = element("button", "text-button", `${run.title} · ${labels[run.verdict] || run.verdict || labels[run.job_status] || run.job_status}`);
      row.type = "button";
      row.addEventListener("click", () => {
        location.hash = "history";
      });
      recent.append(row);
    }
  } catch (e) {
    recent.replaceChildren(element("p", "error-box", e.message));
  }
  try {
    const info = await api("/api/system");
    sys.replaceChildren(
      element("p", "", `NatalIA v${info.version} · Schema v${info.schema_version}`),
      element(
        "p",
        "helper",
        `Engine: ${info.executor.active} active worker(s), ${info.executor.queued} queued. Lean: ${info.adapters.lean.available ? "installed" : "optional (not installed)"}. Translation: manual DSL.`,
      ),
    );
  } catch (e) {
    sys.replaceChildren(element("p", "helper", "Environment not responding yet."));
  }
}

function openCase(item) {
  $("dsl").value = JSON.stringify(item.submission, null, 2);
  fillGuided(item.submission);
  markCustomEditor(item.title);
  const payload = mode === "guided" ? readGuided() : item.submission;
  reviewedFingerprint = payloadFingerprint(payload);
  $("reviewed").checked = true;
  location.hash = "laboratory";
  showPage("laboratory");
}

async function loadLibrary() {
  const root = $("library");
  if (!root) return;
  try {
    const data = await api("/api/catalog");
    catalog = data.items;
    const filter = $("theme-filter");
    if (filter && !filter.dataset.ready) {
      filter.append(element("option", "", "All Themes"));
      filter.querySelector("option").value = "";
      for (const theme of data.themes) {
        const option = element("option", "", theme);
        option.value = theme;
        filter.append(option);
      }
      filter.dataset.ready = "1";
      filter.addEventListener("change", () => loadLibrary());
    }
    const theme = $("theme-filter")?.value;
    root.replaceChildren();
    const items = theme ? catalog.filter((item) => item.theme === theme) : catalog;
    if (!items.length)
      root.append(element("p", "helper", "No cases found for this theme."));
    for (const item of items) {
      const card = element("article", "case-card");
      card.append(
        element("h3", "", item.title),
        element("p", "", item.question),
        element("p", "helper", `${item.theme} · Expected: ${labels[item.expected_verdict] || item.expected_verdict}`),
        element("p", "", item.context),
      );
      const go = element("button", "primary-button", "Inspect in Workbench");
      go.type = "button";
      go.addEventListener("click", () => openCase(item));
      card.append(go);
      root.append(card);
    }
  } catch (e) {
    root.replaceChildren(element("p", "error-box", e.message));
  }
}

async function loadBench() {
  const root = $("bench-manifest");
  if (!root) return;
  try {
    const data = await api("/api/benchmark/manifest");
    if (!data.available) {
      root.textContent = data.reason;
      return;
    }
    root.replaceChildren(
      element("h2", "", data.manifest.id),
      element("p", "", data.manifest.holdout_note),
      element("p", "helper", `${data.count} instances · Calibration: unavailable`),
      element("pre", "", JSON.stringify(data.manifest.families, null, 2)),
    );
  } catch (e) {
    root.textContent = e.message;
  }
}

if ($("import-file")) {
  $("import-file").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const text = await file.text();
    const preview = $("import-preview");
    preview.hidden = false;
    try {
      const parsed = JSON.parse(text);
      const body = Array.isArray(parsed) ? { records: parsed, dry_run: true } : { ...parsed, dry_run: true };
      const result = await api("/api/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      preview.textContent = JSON.stringify(result, null, 2);
    } catch (e) {
      preview.textContent = e.message;
    }
  });
}

function dismissOnboard() {
  try {
    localStorage.setItem("natalia.onboard.v1", "1");
  } catch {
    /* ignore */
  }
  $("onboard")?.close();
}

if ($("onboard-skip")) $("onboard-skip").addEventListener("click", dismissOnboard);
if ($("onboard-run")) {
  $("onboard-run").addEventListener("click", async () => {
    dismissOnboard();
    location.hash = "laboratory";
    showPage("laboratory");
    const energy = examples.find((item) => item.id === "01-energy") || examples[0];
    if (energy) {
      $("example").value = energy.id;
      loadExample();
      $("run").click();
    }
  });
}

init();
const _origInit = init;
void _origInit;
