"use strict";
const $ = (id) => document.getElementById(id);
const DRAFT_KEY = "natalia.draft.v2";
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
  ABSTAIN: "ABSTAIN",
  SMT_RELATIVE: "SMT_RELATIVE",
  EXACT_WITNESS_CHECKED: "EXACT_WITNESS_CHECKED",
  KERNEL_CHECKED: "KERNEL_CHECKED",
  ADVISORY: "ADVISORY",
  STATIC_COMPILE: "STATIC_COMPILE",
  certified: "CERTIFIED",
  refuted: "REFUTED",
  unknown: "OPEN",
  invalid: "INVALID",
  succeeded: "JOB SUCCEEDED",
  failed: "OPERATIONAL FAILURE",
  cancelled: "CANCELLED",
  timed_out: "TIMED OUT",
  rejected: "REJECTED (CAPACITY)",
  queued: "QUEUED",
  running: "RUNNING",
};
const titles = {
  ACCEPTED: "Obligations closed in the supported fragment.",
  REFUTED: "A checked rational counterexample refutes the claim.",
  INVALID: "The formalization needs revision before any solver runs.",
  ABSTAIN: "The available evidence does not close the investigation.",
};
const descriptions = {
  ACCEPTED:
    "Every declared obligation closed in the supported fragment. The result refers to the explicit formalization and its assumptions — not to a paper, a plot, or informal text.",
  REFUTED:
    "A rational assignment satisfies the assumptions and violates at least one claim. The evaluation was checked with exact arithmetic.",
  INVALID:
    "Static compilation found an illegal expression or dimension. No solver was dispatched.",
  ABSTAIN:
    "The evidence cannot close the investigation. Timeouts, cancellation, and operational failure also appear here and are not refutations.",
};
const LIMITATIONS = {
  ACCEPTED:
    "This does not establish that the formalization matches a document, experiment, or intended physics. Fast acceptance is SMT-relative unless the guarantee is KERNEL_CHECKED.",
  REFUTED: "This does not classify every point in the domain. One witness is enough to reject a universal claim.",
  INVALID: "This does not attempt a proof. Fix dimensions or syntax and review again.",
  ABSTAIN: "This is not a proof of undecidability. It records a fragment, domain, or evidence gap.",
};
const NEXT = {
  ACCEPTED: "Inspect the guarantee badge, then open Advanced evidence if you need SMT-LIB or hashes.",
  REFUTED: "Inspect the counterexample and decide whether the domain was the intended one.",
  INVALID: "Revise an assumption, unit, or expression, then review again.",
  ABSTAIN: "Try a guided example in a supported fragment, or add a missing domain restriction.",
};
const OPS = ["==", "!=", ">", ">=", "<", "<="];
let currentRun = null,
  examples = [],
  investigations = [],
  offset = 0,
  activePage = "home",
  activeInvestigationId = "",
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
  const box = $("error");
  if (!box) return;
  box.textContent = message;
  box.hidden = !message;
}
function announce(text) {
  document.title = text ? `${text} · NatalIA` : "NatalIA · Scientific verification laboratory";
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
      /* Keep fallback. */
    }
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.json();
}
function parseHash() {
  const raw = decodeURIComponent(location.hash.replace(/^#/, ""));
  if (raw.startsWith("investigate/"))
    return { page: "investigate", id: raw.slice("investigate/".length) };
  return { page: raw || "home", id: "" };
}
function showPage(page, investigationId) {
  const pages = [
    "home",
    "laboratory",
    "library",
    "investigate",
    "history",
    "evaluation",
    "observability",
    "scope",
  ];
  if (!pages.includes(page)) page = "home";
  activePage = page;
  activeInvestigationId = investigationId || "";
  document
    .querySelectorAll(".page")
    .forEach((node) => (node.hidden = node.id !== `page-${page}`));
  document.querySelectorAll(".nav-item").forEach((node) =>
    node.classList.toggle(
      "active",
      node.dataset.page === page || (page === "investigate" && node.dataset.page === "library"),
    ),
  );
  if (page === "history") loadHistory();
  if (page === "observability") loadStats();
  if (page === "home") loadHome();
  if (page === "library") loadLibrary();
  if (page === "evaluation") loadBench();
  if (page === "investigate") renderInvestigation(activeInvestigationId);
}
document.querySelectorAll("[data-page]").forEach((node) =>
  node.addEventListener("click", () => {
    location.hash = node.dataset.page;
  }),
);
window.addEventListener("hashchange", () => {
  const parsed = parseHash();
  showPage(parsed.page, parsed.id);
});
function emptyDimension() {
  return ["0", "0", "0", "0", "0", "0", "0"];
}
function addVariable(name = "", dimension = emptyDimension()) {
  const row = element("div", "row");
  const nameInput = element("input");
  nameInput.placeholder = "name";
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
  dims.setAttribute("aria-label", "Dimension exponents");
  const match = Object.values(PRESETS).find((item) => item.join(",") === dimension.join(","));
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
  lhs.placeholder = "left";
  const op = element("select");
  OPS.forEach((value) => op.append(element("option", "", value)));
  op.value = item.op || "==";
  const rhs = element("input");
  rhs.value = item.rhs;
  rhs.placeholder = "right";
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
  const claim = item || { kind: "relation", id: "claim", lhs: "", op: ">=", rhs: "0" };
  const box = element("div", "claim-card");
  const kind = element("select");
  ["relation", "limit", "proof_hole"].forEach((value) => kind.append(element("option", "", value)));
  kind.value = claim.kind || "relation";
  const id = element("input");
  id.value = claim.id || "claim";
  id.placeholder = "id";
  const body = element("div", "claim-body");
  function renderBody() {
    body.replaceChildren();
    if (kind.value === "relation") {
      const lhs = element("input");
      lhs.value = claim.lhs || "";
      lhs.placeholder = "left";
      const op = element("select");
      OPS.forEach((value) => op.append(element("option", "", value)));
      op.value = claim.op || "==";
      const rhs = element("input");
      rhs.value = claim.rhs || "";
      rhs.placeholder = "right";
      [lhs, op, rhs].forEach((node) => node.addEventListener("input", onGuidedEdit));
      op.addEventListener("change", onGuidedEdit);
      body.append(lhs, op, rhs);
    } else if (kind.value === "limit") {
      const expr = element("input");
      expr.value = claim.expression || "";
      expr.placeholder = "expression";
      const variable = element("input");
      variable.value = claim.variable || "";
      variable.placeholder = "variable";
      const expected = element("input");
      expected.value = claim.expected || "0";
      expected.placeholder = "expected";
      [expr, variable, expected].forEach((node) => node.addEventListener("input", onGuidedEdit));
      body.append(expr, variable, expected);
    } else {
      const description = element("input");
      description.value = claim.description || "";
      description.placeholder = "explicit gap";
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
    title: $("title").value || "Untitled investigation",
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
  const missing = Object.keys(payload.variables || {}).length ? "" : "No variables declared. ";
  const lines = [
    `Title: ${payload.title}`,
    `${missing}Variables: ${Object.keys(payload.variables || {}).join(", ") || "none"}`,
    `Assumptions: ${(payload.assumptions || []).map((a) => `${a.lhs} ${a.op} ${a.rhs}`).join("; ") || "none"}`,
    `Claims: ${(payload.claims || []).map((c) => c.id).join(", ") || "none"}`,
    `Mode: ${payload.verification_mode || "fast"} · budget ${payload.budget_ms} ms`,
    "Source text is not verified. Confirming review does not prove semantic fidelity.",
  ];
  $("review-summary").textContent = lines.join("\n");
  if (payloadFingerprint(payload) !== reviewedFingerprint) $("reviewed").checked = false;
  $("budget-label").textContent = `Maximum budget: ${(payload.budget_ms ?? 5000) / 1000} s`;
  return payload;
}
function persistDraft() {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ mode, payload: refreshReview() }));
  } catch {
    /* Quota or private mode. */
  }
}
function onGuidedEdit() {
  try {
    $("dsl").value = JSON.stringify(readGuided(), null, 2);
  } catch {
    /* Incomplete form. */
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
      error(`Advanced JSON does not fit the form and was preserved. ${e.message}`);
      fillGuided(
        {
          title: "Advanced formalization",
          source_latex: "",
          variables: { x: { dimension: emptyDimension() } },
          assumptions: [],
          claims: [{ kind: "relation", id: "claim", lhs: "x", op: "==", rhs: "x" }],
          budget_ms: 5000,
        },
        "Advanced content preserved in JSON. It was not discarded.",
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
  $("reviewed").checked = true;
  reviewedFingerprint = payloadFingerprint(readGuided());
  error("");
  persistDraft();
}
$("example").addEventListener("change", loadExample);
function markCustomEditor(label = "Edited formalization") {
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
  refreshReview();
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
function safeMath(mathml) {
  const wrap = element("div", "eq-preview");
  if (typeof mathml === "string" && mathml.startsWith("<math") && !/<script/i.test(mathml))
    wrap.innerHTML = mathml;
  else wrap.textContent = mathml || "";
  return wrap;
}
function lineChart(spec) {
  const series = spec.series
    ? spec.series
    : [{ name: spec.y_label || "value", samples: spec.samples || [] }];
  const points = series.flatMap((s) => s.samples || []);
  const xs = points.map((p) => Number(p.t ?? p.x ?? p.v ?? 0));
  const ys = points.map((p) => Number(p.E ?? p.V ?? p.y ?? p.Ek ?? 0));
  const minX = Math.min(...xs, 0);
  const maxX = Math.max(...xs, 1);
  const minY = Math.min(...ys, 0);
  const maxY = Math.max(...ys, 1);
  const w = 520;
  const h = 220;
  const pad = 36;
  const sx = (x) => pad + ((x - minX) / (maxX - minX || 1)) * (w - 2 * pad);
  const sy = (y) => h - pad - ((y - minY) / (maxY - minY || 1)) * (h - 2 * pad);
  const colors = ["#2c4f45", "#8f3b32"];
  let paths = "";
  series.forEach((s, i) => {
    const d = (s.samples || [])
      .map((p, idx) => {
        const x = Number(p.t ?? p.x ?? p.v ?? 0);
        const y = Number(p.E ?? p.V ?? p.y ?? p.Ek ?? 0);
        return `${idx ? "L" : "M"} ${sx(x)} ${sy(y)}`;
      })
      .join(" ");
    paths += `<path d="${d}" fill="none" stroke="${colors[i % colors.length]}" stroke-width="2"/>`;
  });
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", spec.title);
  svg.innerHTML = `<line x1="${pad}" y1="${h - pad}" x2="${w - pad}" y2="${h - pad}" stroke="#cfc8b8"/>
    <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${h - pad}" stroke="#cfc8b8"/>
    ${paths}
    <text x="${w / 2}" y="${h - 8}" text-anchor="middle" font-size="11" fill="#5e6864">${spec.x_label || ""}</text>`;
  return svg;
}
function unitsChart(spec) {
  const table = element("table", "data-table");
  const head = element("tr");
  ["Quantity", "Familiar unit", "Dimension vector"].forEach((h) => head.append(element("th", "", h)));
  table.append(head);
  for (const row of spec.rows || []) {
    const tr = element("tr");
    tr.append(element("td", "", row.quantity), element("td", "", row.unit), element("td", "", row.vector));
    table.append(tr);
  }
  return table;
}
function renderChart(spec) {
  const box = element("figure", "chart-block");
  box.append(element("h3", "", spec.title));
  if (spec.kind === "units") box.append(unitsChart(spec));
  else box.append(lineChart(spec));
  box.append(element("figcaption", "chart-caption", `${spec.subtitle} Role: ${spec.role}.`));
  const table = element("table", "data-table");
  table.append(element("caption", "", "Chart data (accessible alternative)"));
  const samples = spec.samples || (spec.series || []).flatMap((s) =>
    (s.samples || []).map((p) => ({ ...p, series: s.name })),
  );
  if (samples.length) {
    const keys = Object.keys(samples[0]);
    const head = element("tr");
    keys.forEach((k) => head.append(element("th", "", k)));
    table.append(head);
    samples.forEach((row) => {
      const tr = element("tr");
      keys.forEach((k) => tr.append(element("td", "", String(row[k]))));
      table.append(tr);
    });
    box.append(table);
  }
  return box;
}
function renderRun(run, target) {
  currentRun = run;
  const empty = $("result-empty");
  if (empty) empty.hidden = true;
  const out = target || $("result");
  out.hidden = false;
  $("export").disabled = false;
  out.replaceChildren();
  const operational = run.job_status && run.job_status !== "succeeded";
  const conclusion = operational ? run.job_status : run.conclusion || run.verdict;
  const row = element("div", "verdict-row");
  row.append(
    badge(conclusion),
    element("span", "muted", `${((run.duration_ms || 0) / 1000).toFixed(2)} s`),
  );
  if (run.guarantee_level) row.append(badge(run.guarantee_level));
  if (run.verification_mode)
    row.append(element("span", "muted", `${run.verification_mode} mode`));
  if (operational)
    row.append(element("span", "muted", "Operational state ≠ conclusion about the obligation"));
  out.append(
    row,
    element("h3", "result-title", titles[run.verdict] || "Run finished without a scientific conclusion."),
    element("p", "result-description", descriptions[run.verdict] || run.reason || ""),
    element("p", "", LIMITATIONS[run.verdict] || "A completed job does not by itself imply a proved claim."),
  );
  const answers = element("ol", "answers");
  const items = [
    ["Assumptions used", (run.submission?.assumptions || []).map((a) => `${a.lhs} ${a.op} ${a.rhs}`).join("; ") || "none declared"],
    [
      "Evidence",
      (run.obligations || []).map((o) => `${o.id}: ${o.status} (${o.trust || o.oracle})`).join("; ") ||
        "No persisted obligation.",
    ],
    ["What this does not establish", LIMITATIONS[run.verdict] || "See the trust contract."],
    ["Next suggested action", NEXT[run.verdict] || "Open a guided example or Advanced Mode."],
  ];
  for (const [q, a] of items) {
    const li = element("li");
    li.append(element("strong", "", q + ": "), document.createTextNode(a));
    answers.append(li);
  }
  out.append(answers);
  for (const item of run.obligations || []) {
    const card = element("article", "obligation");
    const top = element("div", "obligation-top");
    top.append(element("strong", "", item.id), badge(item.status));
    card.append(top, element("span", "oracle-name", item.oracle || item.adapter_id || ""), element("p", "", item.reason));
    if (item.counterexample) {
      const values = Object.entries(item.counterexample)
        .map(([k, v]) => `${k} = ${v}`)
        .join(" · ");
      const evaluation = item.evaluation || {};
      card.append(
        element(
          "div",
          "witness",
          `Values: ${values}\nAssumptions: checked in the independent evaluation.\nSubstitution: ${evaluation.lhs} ${evaluation.op} ${evaluation.rhs} → false\nMethod: exact rational arithmetic on the SMT witness`,
        ),
      );
    }
    if (item.cas_result !== undefined)
      card.append(
        element(
          "div",
          "witness",
          `CAS: ${item.cas_result} · expected: ${item.expected}\nAdvisory result, not a kernel certificate.`,
        ),
      );
    if (item.artifacts && item.artifacts.certificate)
      card.append(details("Kernel certificate", JSON.stringify(item.artifacts.certificate, null, 2)));
    out.append(card);
  }
  const advanced = element("details");
  advanced.append(element("summary", "", "Inspect advanced evidence"));
  advanced.append(
    details("Executed formalization", JSON.stringify(run.submission || {}, null, 2)),
    details(
      "Hashes, timings, versions",
      JSON.stringify(
        {
          reason: run.reason,
          guarantee: run.guarantee,
          guarantee_level: run.guarantee_level,
          versions: run.versions,
          job_status: run.job_status,
          input_sha256: run.input_sha256,
          spans: run.spans,
        },
        null,
        2,
      ),
    ),
  );
  const actions = element("div", "result-actions");
  const dup = element("button", "secondary-button", "Revise in Claim Builder");
  dup.type = "button";
  dup.addEventListener("click", () => {
    if (!run.submission) return;
    $("dsl").value = JSON.stringify(run.submission, null, 2);
    fillGuided(run.submission);
    markCustomEditor("Copy of investigation");
    $("reviewed").checked = false;
    location.hash = "laboratory";
  });
  const rec = element("button", "secondary-button", "Recheck certificate");
  rec.type = "button";
  rec.addEventListener("click", async () => {
    const cert = (run.obligations || []).find((o) => o.artifacts && o.artifacts.certificate);
    if (!cert) {
      error("This run has no kernel certificate to recheck.");
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
          ? `Independent recheck: accepted (${checked.guarantee_level}).`
          : `Recheck rejected: ${checked.reason}`,
      );
    } catch (e) {
      error(e.message);
    }
  });
  actions.append(dup, rec);
  out.append(advanced, actions);
  announce(labels[run.verdict] || "Result available");
}
function currentPayload() {
  if (mode === "advanced") return JSON.parse($("dsl").value);
  if (!$("reviewed").checked)
    throw new Error("Review the formalization and confirm before running.");
  const payload = readGuided();
  $("dsl").value = JSON.stringify(payload, null, 2);
  return payload;
}
function setBusy(on) {
  busy = on;
  $("run").disabled = on;
  $("example").disabled = on;
  $("cancel").hidden = !on;
  $("run").textContent = on ? "Verifying…" : "Run verification";
  const extra = $("investigate-run");
  if (extra) extra.disabled = on;
}
$("cancel").addEventListener("click", async () => {
  if (abortController) abortController.abort();
  if (activeJobId) {
    try {
      await api(`/api/jobs/${activeJobId}/cancel`, { method: "POST" });
    } catch {
      /* Job may already have finished. */
    }
  }
});
async function executePayload(payload, resultNode) {
  error("");
  setBusy(true);
  $("export").disabled = true;
  if ($("result")) $("result").hidden = true;
  if ($("result-empty")) {
    $("result-empty").hidden = false;
    $("result-empty").querySelector("h3").textContent = "Investigating the formalization…";
    $("result-empty").querySelector("p").textContent =
      "The job is persisted before computation. You can cancel; operational state is not a verdict.";
  }
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
    renderRun(run, $("result"));
    if (resultNode && resultNode !== $("result")) renderRun(run, resultNode);
    await loadStats();
  } catch (e) {
    if (e.name === "AbortError")
      error("The HTTP request was interrupted. If computation continues, use Cancel.");
    else error(`Could not finish: ${e.message}`);
    if (currentRun) renderRun(currentRun, resultNode || $("result"));
  } finally {
    setBusy(false);
    activeJobId = null;
    abortController = null;
  }
}
$("run").addEventListener("click", async () => {
  if (busy) return;
  let payload;
  try {
    payload = currentPayload();
  } catch (e) {
    error(mode === "advanced" || e instanceof SyntaxError ? `Invalid JSON: ${e.message}` : e.message);
    return;
  }
  await executePayload(payload);
});
async function waitForJob(id) {
  if (window.EventSource) {
    const run = await new Promise((resolve, reject) => {
      const source = new EventSource(`/api/jobs/${id}/events`);
      const timer = setTimeout(() => {
        source.close();
        reject(new Error("SSE wait exceeded the interface timeout."));
      }, 75000);
      source.addEventListener("job", async (ev) => {
        const body = JSON.parse(ev.data);
        if ($("result-empty"))
          $("result-empty").querySelector("p").textContent =
            `Job state: ${body.job_status}. This describes execution, not truth of the claim.`;
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
    if (job.document) return job.document;
    if (["failed", "cancelled", "timed_out", "rejected"].includes(job.job_status) && !job.document)
      throw new Error(`Job ${job.job_status}: ${job.operational_reason || "no document"}`);
    await new Promise((resolve) => {
      pollTimer = setTimeout(resolve, 250);
    });
  }
  throw new Error("Progress polling exceeded the interface timeout.");
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
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
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
    $("history-total").textContent = `${history.total} records`;
    $("nav-count").textContent = history.total;
    if (!history.items.length) {
      $("history").append(element("p", "helper", "No runs on this page yet. Start from a guided example."));
    } else {
      const table = element("table"),
        head = element("thead"),
        tr = element("tr");
      ["", "Investigation", "Job", "Conclusion", "Duration", ""].forEach((x) => tr.append(element("th", "", x)));
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
        title.append(element("small", "", new Date(run.created_at).toLocaleString("en-GB")));
        const job = element("td");
        job.append(badge(run.job_status || "succeeded"));
        const verdictCell = element("td");
        if (run.verdict) verdictCell.append(badge(run.verdict));
        else verdictCell.append(element("span", "muted", "no conclusion"));
        const action = element("td"),
          open = element("button", "text-button", "Open"),
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
            markCustomEditor("Reopened from history");
            renderRun(full.document || full);
            location.hash = "laboratory";
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
          markCustomEditor("Copy of investigation");
          $("reviewed").checked = false;
          location.hash = "laboratory";
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
    $("history").replaceChildren(element("p", "error-box", `History unavailable: ${e.message}`));
  }
}
$("compare").addEventListener("click", async () => {
  const ids = [...document.querySelectorAll("#history input[type=checkbox]:checked")].map(
    (node) => node.dataset.id,
  );
  if (ids.length !== 2) {
    $("compare-view").hidden = false;
    $("compare-view").textContent = "Select exactly two investigations.";
    return;
  }
  const [a, b] = await Promise.all(ids.map((id) => api(`/api/runs/${id}`)));
  const left = a.submission || {},
    right = b.submission || {};
  $("compare-view").hidden = false;
  $("compare-view").replaceChildren(
    element("h2", "", "Comparison"),
    element(
      "pre",
      "",
      [
        `A: ${left.title} → ${a.verdict} (${a.job_status || "succeeded"})`,
        `B: ${right.title} → ${b.verdict} (${b.job_status || "succeeded"})`,
        `Assumptions A: ${JSON.stringify(left.assumptions)}`,
        `Assumptions B: ${JSON.stringify(right.assumptions)}`,
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
      ["Runs with a conclusion", stats.total, "Persisted scientific history"],
      ["Average duration", `${(stats.average_duration_ms / 1000).toFixed(2)} s`, "Includes worker start"],
      ["Abstentions", stats.verdicts.ABSTAIN || 0, "Still-open obligations"],
      ["Active workers", stats.active_runs, "In this API process"],
      ["Queue", stats.queued ?? 0, "Queued jobs waiting for an atomic claim"],
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
      label.append(element("span", "", labels[verdict]), element("span", "", String(count)));
      const progress = element("progress");
      progress.max = Math.max(stats.total, 1);
      progress.value = count;
      progress.setAttribute("aria-label", labels[verdict]);
      row.append(label, progress);
      $("distribution").append(row);
    }
    if ($("system-detail") && !$("system-detail").dataset.loaded) {
      try {
        const info = await api("/api/system");
        $("system-detail").dataset.loaded = "1";
        $("system-detail").replaceChildren(
          element("p", "", `Version ${info.version} · schema ${info.schema_version}`),
          element(
            "p",
            "helper",
            `Executor: ${info.executor.active} active, ${info.executor.queued} queued. Lean: ${
              info.adapters.lean.available ? "detected" : "not installed (optional)"
            }. Model translation: unavailable.`,
          ),
        );
      } catch {
        $("system-detail").textContent = "System endpoint not available.";
      }
    }
  } catch (e) {
    $("stats").replaceChildren(element("p", "error-box", `Metrics unavailable: ${e.message}`));
  }
}
function cardFor(item) {
  const card = element("article", "inv-card");
  card.tabIndex = 0;
  card.setAttribute("role", "button");
  const meta = element("div", "card-meta");
  [item.domain, item.difficulty, item.expected_label, `${item.learning_minutes} min`, item.verification_mode].forEach(
    (t) => meta.append(element("span", "pill", t)),
  );
  card.append(element("h3", "", item.title), meta, element("p", "", item.question));
  if (item.equations?.[0]) card.append(safeMath(item.equations[0].mathml));
  card.append(element("p", "helper", `Educational model · expected ${item.expected_verdict}`));
  const open = () => {
    location.hash = `investigate/${item.id}`;
  };
  card.addEventListener("click", open);
  card.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      open();
    }
  });
  return card;
}
async function loadHome() {
  const featured = $("featured");
  const recent = $("recent");
  if (!featured) return;
  featured.replaceChildren();
  const starters = investigations.filter((item) => item.tier === 1);
  if (!starters.length) featured.append(element("p", "helper", "Guided examples are still loading."));
  starters.forEach((item) => featured.append(cardFor(item)));
  try {
    const history = await api("/api/runs?limit=5&offset=0");
    recent.replaceChildren();
    if (!history.items.length)
      recent.append(element("p", "helper", "No verifications on this computer yet."));
    for (const run of history.items) {
      const row = element("button", "recent-row");
      row.type = "button";
      row.append(element("span", "", run.title), badge(run.verdict || run.job_status));
      row.addEventListener("click", () => {
        location.hash = "history";
      });
      recent.append(row);
    }
  } catch (e) {
    recent.replaceChildren(element("p", "error-box", e.message));
  }
}
function applyLibraryFilters() {
  const q = ($("library-search")?.value || "").toLowerCase();
  const domain = $("filter-domain")?.value || "";
  const difficulty = $("filter-difficulty")?.value || "";
  const verdict = $("filter-verdict")?.value || "";
  const guarantee = $("filter-guarantee")?.value || "";
  return investigations.filter((item) => {
    const text = `${item.title} ${item.question} ${item.domain}`.toLowerCase();
    return (
      (!q || text.includes(q)) &&
      (!domain || item.domain === domain) &&
      (!difficulty || item.difficulty === difficulty) &&
      (!verdict || item.expected_verdict === verdict) &&
      (!guarantee || item.guarantee_level === guarantee)
    );
  });
}
function loadLibrary() {
  const root = $("library");
  if (!root) return;
  const domain = $("filter-domain");
  if (domain && !domain.dataset.ready) {
    [...new Set(investigations.map((i) => i.domain))].forEach((name) => {
      const option = element("option", "", name);
      option.value = name;
      domain.append(option);
    });
    const diff = $("filter-difficulty");
    ["Foundations", "Intermediate", "Advanced", "Research Boundary"].forEach((name) => {
      const option = element("option", "", name);
      option.value = name;
      diff.append(option);
    });
    domain.dataset.ready = "1";
    ["library-search", "filter-domain", "filter-difficulty", "filter-verdict", "filter-guarantee"].forEach(
      (id) => $(id)?.addEventListener("input", loadLibrary),
    );
    $("filter-domain")?.addEventListener("change", loadLibrary);
    $("filter-difficulty")?.addEventListener("change", loadLibrary);
    $("filter-verdict")?.addEventListener("change", loadLibrary);
    $("filter-guarantee")?.addEventListener("change", loadLibrary);
  }
  root.replaceChildren();
  const items = applyLibraryFilters();
  if (!items.length) root.append(element("p", "helper", "No example matches these filters."));
  items.forEach((item) => root.append(cardFor(item)));
}
function applySubmission(submission, label) {
  $("dsl").value = JSON.stringify(submission, null, 2);
  fillGuided(submission);
  markCustomEditor(label);
  $("reviewed").checked = true;
  reviewedFingerprint = payloadFingerprint(readGuided());
}
function renderInvestigation(ident) {
  const root = $("investigate-root");
  const item = investigations.find((x) => x.id === ident);
  if (!root) return;
  if (!item) {
    root.replaceChildren(element("p", "helper", "Investigation not found. Return to the library."));
    return;
  }
  const steps = [
    ["question", "The question"],
    ["why", "Why it matters"],
    ["model", "The model"],
    ["equations", "The equations"],
    ["explore", "Explore the behavior"],
    ["verify-what", "What NatalIA will verify"],
    ["run", "Run verification"],
    ["result", "Understand the result"],
    ["advanced", "Inspect advanced evidence"],
  ];
  const nav = element("nav", "stepper");
  nav.setAttribute("aria-label", "Investigation sections");
  steps.forEach(([id, label]) => {
    const a = element("a", "", label);
    a.href = `#investigate/${item.id}`;
    a.dataset.section = id;
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      $(`sec-${id}`)?.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    });
    nav.append(a);
  });
  const article = element("article", "narrative");
  const addSec = (id, title, build) => {
    const sec = element("section");
    sec.id = `sec-${id}`;
    sec.append(element("h2", "", title));
    build(sec);
    article.append(sec);
  };
  addSec("question", "The question", (sec) => {
    sec.append(element("p", "eyebrow", `${item.domain} · ${item.difficulty} · educational model`));
    sec.append(element("p", "lede", item.question));
  });
  addSec("why", "Why it matters", (sec) => sec.append(element("p", "", item.why_it_matters)));
  addSec("model", "The model", (sec) => {
    sec.append(element("p", "", item.model));
    const list = element("ul", "var-list");
    for (const v of item.variables_explained || [])
      list.append(element("li", "", `${v.name}: ${v.meaning} [${v.unit}]`));
    sec.append(list);
    sec.append(element("p", "helper", `Assumptions in the formalization: ${(item.submission.assumptions || []).map((a) => `${a.lhs} ${a.op} ${a.rhs}`).join("; ") || "none"}.`));
  });
  addSec("equations", "The equations", (sec) => {
    for (const eq of item.equations || []) {
      const block = element("div", "equation-block");
      block.append(safeMath(eq.mathml));
      block.append(element("p", "helper", eq.caption));
      const actions = element("div", "equation-actions");
      const copyPlain = element("button", "text-button", "Copy plain text");
      copyPlain.type = "button";
      copyPlain.addEventListener("click", () => navigator.clipboard?.writeText(eq.plain));
      const copyTex = element("button", "text-button", "Copy LaTeX");
      copyTex.type = "button";
      copyTex.addEventListener("click", () => navigator.clipboard?.writeText(eq.latex));
      actions.append(copyPlain, copyTex);
      block.append(actions);
      sec.append(block);
    }
    sec.append(
      element(
        "p",
        "helper",
        "Rendered notation matches the captions on this page. It is verified only insofar as it corresponds to the submitted formalization below.",
      ),
    );
  });
  addSec("explore", "Explore the behavior", (sec) => {
    if (!item.charts?.length) {
      sec.append(element("p", "", "No chart is needed beyond the equations for this case."));
      return;
    }
    item.charts.forEach((chart) => sec.append(renderChart(chart)));
  });
  addSec("verify-what", "What NatalIA will verify", (sec) => {
    sec.append(element("p", "", item.obligation_english));
    sec.append(element("p", "helper", `Expected conclusion: ${item.expected_label}. Guarantee: ${item.guarantee_level}.`));
    sec.append(element("p", "", item.limitations));
  });
  const resultHost = element("div");
  resultHost.id = "investigate-result";
  addSec("run", "Run verification", (sec) => {
    const run = element("button", "primary-button", `Run ${item.verification_mode} verification`);
    run.id = "investigate-run";
    run.type = "button";
    run.addEventListener("click", async () => {
      applySubmission(item.submission, item.title);
      await executePayload(item.submission, resultHost);
      $("sec-result")?.scrollIntoView({ behavior: "smooth" });
    });
    sec.append(element("p", "", `Budget ${item.submission.budget_ms} ms. Mode: ${item.verification_mode}.`));
    sec.append(run);
    if (item.companion_submission) {
      const alt = element("button", "secondary-button", "Load companion with x ≠ 0");
      alt.type = "button";
      alt.addEventListener("click", () => {
        applySubmission(item.companion_submission, "Domain-restricted companion");
        location.hash = "laboratory";
      });
      sec.append(alt);
    }
  });
  addSec("result", "Understand the result", (sec) => {
    sec.append(element("p", "helper", "The conclusion appears after you run verification. A succeeded job is not itself a proof."));
    sec.append(resultHost);
  });
  addSec("advanced", "Inspect advanced evidence", (sec) => {
    sec.append(details("JSON DSL to be submitted", JSON.stringify(item.submission, null, 2)));
    sec.append(element("p", "helper", item.source.note));
    if (item.planned?.length) sec.append(element("p", "", `Planned: ${item.planned.join("; ")}.`));
  });
  root.replaceChildren();
  const layout = element("div", "investigate-layout");
  layout.append(nav, article);
  root.append(layout);
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
      element("p", "helper", `${data.count} instances · calibration: unavailable`),
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
    const preview = $("import-preview");
    preview.hidden = false;
    try {
      const parsed = JSON.parse(await file.text());
      const body = Array.isArray(parsed) ? { records: parsed, dry_run: true } : { ...parsed, dry_run: true };
      preview.textContent = JSON.stringify(
        await api("/api/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }),
        null,
        2,
      );
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
    location.hash = "investigate/inv-01-kinetic";
  });
}
let wizardStep = 0;
function setWizard(step) {
  wizardStep = Math.max(0, Math.min(5, step));
  document.querySelectorAll("#wizard-steps li").forEach((node) => {
    node.classList.toggle("active", Number(node.dataset.step) === wizardStep);
  });
  document.querySelectorAll(".wizard-pane").forEach((node) => {
    node.hidden = Number(node.dataset.pane) !== Math.min(wizardStep, 4);
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
    if (!result.ok && result.errors?.length) error(result.errors.map((item) => item.message).join("\n"));
    else if (!busy) error("");
  } catch {
    /* Incomplete payload is expected while typing. */
  }
}
async function init() {
  try {
    const [ex, inv] = await Promise.all([api("/api/examples"), api("/api/investigations")]);
    examples = ex;
    investigations = inv.items;
    $("example").replaceChildren();
    for (const item of examples) {
      const option = element("option", "", item.submission.title);
      option.value = item.id;
      $("example").append(option);
    }
    const draft = localStorage.getItem(DRAFT_KEY);
    if (draft) {
      const parsedDraft = JSON.parse(draft);
      $("dsl").value = JSON.stringify(parsedDraft.payload, null, 2);
      fillGuided(parsedDraft.payload);
      markCustomEditor("Recovered local draft");
    } else loadExample();
    $("run").disabled = false;
  } catch (e) {
    error(`Could not load examples: ${e.message}`);
    $("run").disabled = false;
  }
  const parsed = parseHash();
  showPage(parsed.page, parsed.id);
  await Promise.allSettled([loadStats(), loadHome()]);
  try {
    if (!localStorage.getItem("natalia.onboard.v1") && $("onboard")?.showModal) $("onboard").showModal();
  } catch {
    /* dialog not supported */
  }
}
window.addEventListener("error", () => {
  const fail = $("js-fail");
  if (fail) fail.hidden = false;
});
init();
setInterval(() => {
  if (activePage === "observability") loadStats();
}, 10000);
