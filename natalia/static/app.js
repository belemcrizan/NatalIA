"use strict";
const $ = (id) => document.getElementById(id);
const labels = {
  ACCEPTED: "ACEITO · SMT",
  REFUTED: "REFUTADO",
  INVALID: "INVÁLIDO",
  ABSTAIN: "ABSTENÇÃO",
  certified: "VERIFICADO",
  refuted: "REFUTADO",
  unknown: "EM ABERTO",
  invalid: "INVÁLIDO",
};
const titles = {
  ACCEPTED: "Obrigações verificadas.",
  REFUTED: "Encontramos um contraexemplo.",
  INVALID: "A formalização precisa de revisão.",
  ABSTAIN: "Há questões em aberto.",
};
const descriptions = {
  ACCEPTED:
    "Todas as obrigações declaradas foram fechadas no fragmento SMT suportado. O resultado se refere à formalização explícita e às suas premissas.",
  REFUTED:
    "Uma atribuição racional satisfaz as premissas e viola pelo menos uma afirmação. A avaliação foi conferida com aritmética exata.",
  INVALID:
    "A compilação estática encontrou uma expressão ou dimensão incompatível. Revise a evidência abaixo antes de executar novamente.",
  ABSTAIN:
    "A evidência disponível não permite encerrar a investigação. Revise as lacunas, o domínio e os recursos do verificador.",
};
let currentRun = null,
  examples = [],
  offset = 0,
  activePage = "laboratory",
  busy = false;
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
  $("error").textContent = message;
  $("error").hidden = !message;
}
async function api(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = "Serviço indisponível.";
    try {
      const body = await response.json();
      detail = Array.isArray(body.detail)
        ? body.detail.map((x) => `${x.loc.join(".")}: ${x.msg}`).join("\n")
        : body.detail || detail;
    } catch {
      /* Keep fallback. */
    }
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.json();
}
function showPage(page) {
  if (!["laboratory", "history", "observability", "scope"].includes(page))
    page = "laboratory";
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
}
document.querySelectorAll("[data-page]").forEach((node) =>
  node.addEventListener("click", () => {
    location.hash = node.dataset.page;
  }),
);
window.addEventListener("hashchange", () => showPage(location.hash.slice(1)));
function loadExample() {
  const selected = examples.find((x) => x.id === $("example").value);
  if (!selected) return;
  $("dsl").value = JSON.stringify(selected.submission, null, 2);
  updateBudget();
  error("");
}
function updateBudget() {
  try {
    $("budget-label").textContent =
      `Orçamento máximo: ${(JSON.parse($("dsl").value).budget_ms ?? 5000) / 1000} s`;
  } catch {
    $("budget-label").textContent = "Revise o JSON antes de executar";
  }
}
$("example").addEventListener("change", loadExample);
function markCustomEditor(label = "Formalização editada") {
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
});
$("format").addEventListener("click", () => {
  try {
    $("dsl").value = JSON.stringify(JSON.parse($("dsl").value), null, 2);
    error("");
  } catch (e) {
    error(`JSON inválido: ${e.message}`);
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
  const row = element("div", "verdict-row");
  row.append(
    badge(run.verdict),
    element("span", "muted", `${(run.duration_ms / 1000).toFixed(2)} s`),
  );
  out.append(
    row,
    element("h3", "result-title", titles[run.verdict]),
    element("p", "result-description", descriptions[run.verdict]),
  );
  const meta = element("div", "result-meta");
  for (const [label, value] of [
    [
      "OBRIGAÇÕES CERTIFICADAS",
      `${run.obligations.filter((o) => o.status === "certified").length} de ${run.obligations.length}`,
    ],
    ["CONFIANÇA CALIBRADA", "Não disponível"],
  ]) {
    const cell = element("div");
    cell.append(element("span", "", label), element("strong", "", value));
    meta.append(cell);
  }
  out.append(meta, element("p", "evidence-title", "RASTRO DE EVIDÊNCIAS"));
  for (const item of run.obligations) {
    const card = element("article", "obligation");
    const top = element("div", "obligation-top");
    top.append(element("strong", "", item.id), badge(item.status));
    card.append(
      top,
      element("span", "oracle-name", item.oracle),
      element("p", "", item.reason),
    );
    if (item.counterexample) {
      const values = Object.entries(item.counterexample)
        .map(([k, v]) => `${k} = ${v}`)
        .join(" · ");
      const evaluation = item.evaluation;
      card.append(
        element(
          "div",
          "witness",
          `${values}\nAfirmação: ${evaluation.lhs} ${evaluation.op} ${evaluation.rhs} → falso`,
        ),
      );
    }
    if (item.cas_result !== undefined)
      card.append(
        element(
          "div",
          "witness",
          `CAS: ${item.cas_result} · esperado: ${item.expected}\nResultado indicativo, sem certificado do kernel.`,
        ),
      );
    if (item.smtlib)
      card.append(details("Inspecionar problema SMT-LIB", item.smtlib));
    out.append(card);
  }
  const trace = element("details");
  trace.append(element("summary", "", "Tempos e rastreabilidade"));
  for (const span of run.spans) {
    const line = element("div", "trace-item");
    line.append(
      element("span", "", `${span.name} / ${span.oracle}`),
      element("span", "", `${span.duration_ms.toFixed(2)} ms`),
    );
    trace.append(line);
  }
  trace.append(
    element("p", "trace-id", `trace_id: ${run.trace_id}`),
    element("p", "trace-id", `SHA-256: ${run.input_sha256}`),
  );
  out.append(
    trace,
    details("Formalização executada", JSON.stringify(run.submission, null, 2)),
    details(
      "Versões e limites de confiança",
      JSON.stringify(
        {
          reason: run.reason,
          scope: run.scope,
          guarantee: run.guarantee,
          versions: run.versions,
        },
        null,
        2,
      ),
    ),
  );
}
$("run").addEventListener("click", async () => {
  if (busy) return;
  let payload;
  try {
    payload = JSON.parse($("dsl").value);
  } catch (e) {
    error(`JSON inválido: ${e.message}`);
    return;
  }
  error("");
  busy = true;
  $("run").disabled = true;
  $("example").disabled = true;
  $("export").disabled = true;
  $("run").textContent = "Verificando…";
  $("result").hidden = true;
  $("result-empty").hidden = false;
  $("result-empty").classList.add("loading");
  $("result-empty").querySelector("h3").textContent =
    "Investigando a formalização…";
  $("result-empty").querySelector("p").textContent =
    "Compilando dimensões e consultando os oráculos dentro do orçamento definido.";
  try {
    const run = await api("/api/runs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    renderRun(run);
    await loadStats();
  } catch (e) {
    error(`Não foi possível concluir: ${e.message}`);
    if (currentRun) renderRun(currentRun);
    else {
      $("result-empty").querySelector("h3").textContent =
        "A execução não foi concluída.";
      $("result-empty").querySelector("p").textContent =
        "Veja a mensagem junto ao editor e tente novamente.";
    }
  } finally {
    busy = false;
    $("run").disabled = false;
    $("example").disabled = false;
    $("run").textContent = "Verificar hipótese ↗";
    $("result-empty").classList.remove("loading");
  }
});
$("export").addEventListener("click", () => {
  if (!currentRun) return;
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(currentRun, null, 2)], {
      type: "application/json",
    }),
  );
  const link = element("a");
  link.href = url;
  link.download = `natalia-${currentRun.id}.json`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
async function loadHistory() {
  try {
    const history = await api(`/api/runs?limit=10&offset=${offset}`);
    $("history").replaceChildren();
    $("history-total").textContent = `${history.total} execuções`;
    $("nav-count").textContent = history.total;
    if (!history.items.length) {
      $("history").append(
        element(
          "p",
          "table-empty",
          "Nenhuma execução nesta página. Comece pelo laboratório.",
        ),
      );
    } else {
      const table = element("table"),
        head = element("thead"),
        tr = element("tr");
      ["INVESTIGAÇÃO", "VEREDITO", "DURAÇÃO", ""].forEach((x) =>
        tr.append(element("th", "", x)),
      );
      head.append(tr);
      table.append(head);
      const body = element("tbody");
      for (const run of history.items) {
        const row = element("tr"),
          title = element("td", "", run.title);
        title.append(
          element(
            "small",
            "",
            new Date(run.created_at).toLocaleString("pt-BR"),
          ),
        );
        const verdict = element("td");
        verdict.append(badge(run.verdict));
        const action = element("td"),
          button = element("button", "text-button", "Abrir ↗");
        button.setAttribute("aria-label", `Abrir ${run.title}`);
        button.addEventListener("click", async () => {
          button.disabled = true;
          try {
            const full = await api(`/api/runs/${run.id}`);
            $("dsl").value = JSON.stringify(full.submission, null, 2);
            markCustomEditor("Execução reaberta do histórico");
            updateBudget();
            renderRun(full);
            location.hash = "laboratory";
            showPage("laboratory");
            error("");
          } catch (e) {
            button.textContent = `Erro: ${e.message}`;
          } finally {
            button.disabled = false;
          }
        });
        action.append(button);
        row.append(
          title,
          verdict,
          element("td", "", `${(run.duration_ms / 1000).toFixed(2)} s`),
          action,
        );
        body.append(row);
      }
      table.append(body);
      $("history").append(table);
    }
    $("prev").disabled = offset === 0;
    $("next").disabled = offset + 10 >= history.total;
    $("page-number").textContent = `Página ${Math.floor(offset / 10) + 1}`;
  } catch (e) {
    $("history").replaceChildren(
      element("p", "error-box", `Histórico indisponível: ${e.message}`),
    );
  }
}
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
      ["Execuções", stats.total, "Histórico persistido"],
      [
        "Duração média",
        `${(stats.average_duration_ms / 1000).toFixed(2)} s`,
        "Inclui inicialização do worker",
      ],
      ["Abstenções", stats.verdicts.ABSTAIN || 0, "Obrigações ainda abertas"],
      ["Workers ativos", stats.active_runs, "Neste processo da API"],
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
      element("p", "error-box", `Métricas indisponíveis: ${e.message}`),
    );
  }
}
async function health() {
  try {
    await api("/health/ready");
    $("health-label").replaceChildren(
      document.createTextNode("Ambiente disponível"),
      element("small", "", "Local · v0.1.0"),
    );
    $("health-dot").className = "tiny-dot";
  } catch {
    $("health-label").textContent = "Ambiente indisponível";
    $("health-dot").className = "";
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
    loadExample();
    $("run").disabled = false;
  } catch (e) {
    error(`Não foi possível carregar exemplos: ${e.message}`);
    $("run").disabled = false;
  }
  await Promise.allSettled([health(), loadStats()]);
}
setInterval(() => {
  health();
  if (activePage === "observability") loadStats();
}, 10000);
init();
