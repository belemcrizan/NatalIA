"""Build the NatalIA requirements traceability matrix from the preserved annex."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNEX = ROOT / "docs" / "annex" / "ORIGINAL_CHECKLIST.md"
OUT_JSON = ROOT / "docs" / "TRACEABILITY.json"
OUT_MD = ROOT / "docs" / "TRACEABILITY.md"

TEAM_HYPOTHESIS = (
    "Estimates assume one software engineer plus intermittent scientific review, "
    "not a funded lab. They are not commitments of calendar time or budget."
)

NATURE_BY_SECTION = {
    "0": "pesquisa",
    "1.1": "pesquisa",
    "1.2": "engenharia",
    "1.3": "engenharia",
    "1.4": "engenharia",
    "1.5": "colaboração externa",
    "2.1": "pesquisa",
    "2.2": "pesquisa",
    "2.3": "pesquisa",
    "2.4": "pesquisa",
    "3.1": "engenharia",
    "3.2": "pesquisa",
    "3.3": "engenharia",
    "4.1": "pesquisa",
    "4.2": "pesquisa",
    "4.3": "pesquisa",
    "5.1": "engenharia",
    "5.2": "engenharia",
    "5.3": "engenharia",
    "5.4": "engenharia",
    "5.5": "engenharia",
    "5.6": "operação",
    "5.7": "engenharia",
    "6.1": "engenharia",
    "6.2": "engenharia",
    "6.3": "engenharia",
    "6.4": "engenharia",
    "6.5": "operação",
    "6.6": "engenharia",
    "6.7": "governança",
    "7.1": "operação",
    "7.2": "operação",
    "7.3": "operação",
    "7.4": "operação",
    "7.5": "operação",
    "8.1": "produto",
    "8.2": "engenharia",
    "8.3": "produto",
    "8.4": "produto",
    "9.1": "governança",
    "9.2": "colaboração externa",
    "9.3": "colaboração externa",
    "9.4": "colaboração externa",
    "9.5": "produto",
    "10": "governança",
    "11": "financiamento",
    "12": "colaboração externa",
    "13": "governança",
    "14": "produto",
    "15": "governança",
    "16": "governança",
    "resumo": "governança",
}

EFFORT = {
    "P0": {"optimistic_person_days": 3, "likely_person_days": 15, "pessimistic_person_days": 60},
    "P1": {"optimistic_person_days": 5, "likely_person_days": 25, "pessimistic_person_days": 90},
    "P2": {"optimistic_person_days": 8, "likely_person_days": 40, "pessimistic_person_days": 120},
    "P3": {"optimistic_person_days": 2, "likely_person_days": 10, "pessimistic_person_days": 40},
}

PREAMBLE = [
    ("ADD-01", "P0", "engenharia", "1. Contrato de preservação", "Gerar matriz de rastreabilidade com identificador estável para cada requisito, inclusive parágrafos, tabelas, riscos e conclusões."),
    ("ADD-02", "P0", "governança", "1. Contrato de preservação", "Preservar itens, nomes, alternativas tecnológicas, prioridades, números, cronogramas e ambições do anexo."),
    ("ADD-03", "P0", "governança", "1. Contrato de preservação", "Manter o anexo integral em controle de versão e verificar sua preservação."),
    ("ADD-04", "P0", "governança", "1. Contrato de preservação", "Identificar cada complemento do preâmbulo como requisito adicional."),
    ("ADD-05", "P0", "governança", "1. Contrato de preservação", "Estimativas informam hipóteses de equipe e faixas otimista/provável/pessimista, sem tratar prazos como fatos."),
    ("ADD-06", "P0", "engenharia", "2. Diagnóstico obrigatório", "Diagnosticar README, código, testes, CI, dependências, licenças, frontend, API, workers e documentação com evidências por caminho."),
    ("ADD-07", "P0", "engenharia", "2. Diagnóstico obrigatório", "Reproduzir inicialização e fluxo completo entrada → validação → job → execução → resultado → evidência → visualização."),
    ("ADD-08", "P0", "pesquisa", "2. Diagnóstico obrigatório", "Tratar notas numéricas e comparações institucionais do anexo como opiniões do autor, não auditoria independente."),
    ("ADD-09", "P0", "engenharia", "3. Semântica de resultados", "Preservar ACCEPTED, REFUTED, INVALID, ABSTAIN e separar estado lógico do estado operacional do job."),
    ("ADD-10", "P0", "engenharia", "3. Semântica de resultados", "Modelar FAST, CERTIFIED e AUTOFORMALIZED como dimensões com contratos explícitos."),
    ("ADD-11", "P0", "engenharia", "3. Semântica de resultados", "Implementar ao menos um caminho vertical real de certificação para um fragmento delimitado, sem enfraquecer a proposição."),
    ("ADD-12", "P0", "engenharia", "3. Esclarecimentos", "Falha de proof assistant não implica falsidade nem contraexemplo automático; classificar syntax/type/dependency/timeout/incomplete."),
    ("ADD-13", "P0", "engenharia", "3. Esclarecimentos", "Tratar `lean --check` como intenção de checagem obrigatória, não como garantia de flag CLI."),
    ("ADD-14", "P0", "pesquisa", "3. Esclarecimentos", "Núcleo pequeno não é correto por si; delimitar o que foi provado e o que permanece no TCB."),
    ("ADD-15", "P0", "engenharia", "4. Arquitetura evolutiva", "Manter três perfis documentados: local, distribuído de desenvolvimento e produção."),
    ("ADD-16", "P0", "engenharia", "4. Arquitetura evolutiva", "Escolher tecnologias centrais por ADR; preservar alternativas no registro sem instalar todas simultaneamente."),
    ("ADD-17", "P1", "engenharia", "4. Arquitetura evolutiva", "Definir migração SQLite/Postgres com corte, consistência e jobs em execução, sem escrita dupla improvisada."),
    ("ADD-18", "P0", "engenharia", "5. Segurança", "Modelar ameaças específicas e isolar execução de entrada não confiável."),
    ("ADD-19", "P0", "engenharia", "5. Segurança", "Obter tenant de identidade autenticada no servidor; não confiar em tenant_id do cliente."),
    ("ADD-20", "P0", "governança", "5. Segurança", "Não alegar SLSA/SOC2/ISO sem avaliação de versão, escopo e evidências."),
    ("ADD-21", "P1", "engenharia", "6. Autoformalização", "Pipeline versionado ingestão → extração → AST → fidelidade → obrigação → prova → checagem."),
    ("ADD-22", "P0", "pesquisa", "6. Autoformalização", "Registrar origem, licença e limitações de todo dataset; não redistribuir sem autorização."),
    ("ADD-23", "P1", "produto", "7. Interface", "Tela inicial com criar verificação, exemplo, importar, jobs e resultados; fluxo guiado."),
    ("ADD-24", "P2", "produto", "7. Interface", "Acessibilidade WCAG 2.2 AA, i18n, teclado e estados vazio/erro; certificação não pode ser simulada na UI."),
    ("ADD-25", "P0", "pesquisa", "8. Avaliação", "Toda meta vira protocolo mensurável; 99.9%, p95, 10k jobs/h e US$0.01 permanecem objetivos até medição."),
    ("ADD-26", "P0", "pesquisa", "9. Pesquisa", "Não fabricar teoremas, provas, parcerias, grants ou submissões; contatos externos exigem autorização humana."),
    ("ADD-27", "P0", "engenharia", "10. Etapas", "Etapa A — base reproduzível com gate de outra pessoa iniciar e conferir evidências."),
    ("ADD-28", "P0", "engenharia", "10. Etapas", "Etapa B — confiança demonstrável com fragmento certificado, testes negativos e limites documentados."),
    ("ADD-29", "P1", "engenharia", "10. Etapas", "Etapa C — distribuição e isolamento (Postgres, mensageria escolhida, API/worker, identidade, quotas)."),
    ("ADD-30", "P1", "produto", "10. Etapas", "Etapa D — produto e dados (UX guiada, catálogo, autoformalização delimitada)."),
    ("ADD-31", "P2", "operação", "10. Etapas", "Etapa E — produção (IaC, backups, canary, carga) sem confundir teste local com prontidão."),
    ("ADD-32", "P2", "governança", "10. Etapas", "Etapa F — programa contínuo científico, comunitário e de financiamento."),
    ("ADD-33", "P0", "produto", "11. Entregáveis", "README com limites de escala, Fast≠Certified, guia Windows PowerShell e Linux/macOS, Python 3.12/3.13."),
    ("ADD-34", "P0", "engenharia", "11. Entregáveis", "PR revisável com problema, mudanças, validação, riscos e pendências."),
    ("ADD-35", "P0", "engenharia", "11. Entregáveis", "Relatório final separa concluído e validado; implementado sem validação; planejado; bloqueado."),
]

OVERLAY_RULES = [
    ("Definir a tese científica central", "implementado sem validação", "README.md e docs/papers/POSITION_PAPER_DRAFT.md declaram a frase; não há publicação."),
    ("Escolher o nome do campo", "dependente de decisão", "Alternativas Verified Science e Formal Scientific Computing preservadas em docs/DECISIONS.md."),
    ("position paper", "implementado sem validação", "Rascunho em docs/papers/POSITION_PAPER_DRAFT.md; não submetido."),
    ("escopo negativo", "implementado sem validação", "README.md e docs/TRUST.md."),
    ("3 verticais iniciais", "implementado sem validação", "docs/papers/POSITION_PAPER_DRAFT.md."),
    ("3 verticais futuras", "implementado sem validação", "docs/papers/POSITION_PAPER_DRAFT.md."),
    ("open source puro, open core ou fundação", "dependente de decisão", "docs/DECISIONS.md ADR-licença."),
    ("Definir licença", "dependente de decisão", "Alternativas Apache 2.0, MIT, AGPL e dual rastreadas; repositório sem LICENSE raiz."),
    ("política de patentes", "dependente de decisão", "Nenhuma política registrada."),
    ("Substituir `natalia.kernel` por kernel externo", "não iniciado", "natalia/kernel.py permanece o checker certificado local."),
    ("Se mantiver kernel próprio, formalizar sua soundness", "não iniciado", "Kernel Python existe; não há prova de soundness em Lean/Coq."),
    ("menos de 5k linhas", "implementado sem validação", "natalia/kernel.py está bem abaixo de 5k linhas; isso não prova correção."),
    ("Publicar prova de soundness", "não iniciado", "Nenhuma submissão."),
    ("Reduzir TCB", "implementado sem validação", "docs/TRUST.md lista TCB; parser e runtime permanecem no TCB."),
    ("Formalizar o parser da DSL", "não iniciado", None),
    ("Formalizar o compilador AST→SMT", "não iniciado", None),
    ("Z3 → Alethe", "não iniciado", "docs/TRUST.md: Z3 5.x não é tratado como produtor Alethe neste fragmento."),
    ("checker Alethe", "não iniciado", None),
    ("Z3 → LFSC", "não iniciado", None),
    ("Z3 → Dedukti", "não iniciado", None),
    ("Exportação Lean com `lean --check`", "implementado sem validação", "natalia/lean.py exporta e classifica falhas; usa `lean <file>`, não a flag --check; CI não exige Lean."),
    ("Mathlib pinado", "não iniciado", "formal/ sem lakefile."),
    ("Prova de fidelidade AST→Lean", "não iniciado", "Testes diferenciais de kernel não substituem fidelidade Lean."),
    ("Contraexemplo automático se `lean --check` falhar", "implementado sem validação", "Falha Lean é classificada e não vira REFUTED; contraexemplo automático seria incorreto."),
    ("Assinar todo resultado com Sigstore", "não iniciado", None),
    ("in-toto/SLSA", "não iniciado", None),
    ("Postgres como store primário", "não iniciado", "API usa SQLite; Compose perfil distributed publica Postgres não usado."),
    ("Migração SQLite → Postgres", "não iniciado", None),
    ("NATS JetStream ou Kafka", "não iniciado", "NATS no Compose como companheiro; sem consumidor."),
    ("Redis para cache", "não iniciado", "Fingerprint de cache em natalia/engine.py sem Redis."),
    ("Cache por hash de entrada", "implementado sem validação", "cache_fingerprint em natalia/engine.py."),
    ("Workers stateless", "implementado sem validação", "natalia/worker.py processo descartável local, não HPA."),
    ("REST stateless", "implementado sem validação", "natalia/api.py FastAPI."),
    ("WebSocket/SSE", "implementado sem validação", "SSE em /api/jobs/{id}/events."),
    ("API keys com rotação", "implementado sem validação", "Bootstrap keys; sem rotação automática."),
    ("Isolamento de dados por tenant", "implementado sem validação", "tests/test_trust.py dois tenants; perfil distributed."),
    ("Quotas por tenant", "implementado sem validação", "NATALIA_TENANT_QUEUE."),
    ("Filesystem read-only", "implementado sem validação", "Dockerfile/Compose; não é o runtime nativo Windows."),
    ("Limites de CPU/memória/processos", "implementado sem validação", "Compose; nativo sem cgroups."),
    ("Limites de tempo", "validado", "budget_ms e worker timeout; tests/test_worker.py."),
    ("Runbook completo", "implementado sem validação", "docs/RUNBOOK.md cobre o perfil local, não on-call 24x7."),
    ("React/Next/Svelte", "não iniciado", "Frontend HTML/JS sem build por ADR."),
    ("SSE/WebSocket para progresso", "implementado sem validação", "natalia/static/app.js + API SSE."),
    ("Drafts no servidor", "não iniciado", "Rascunhos em localStorage."),
    ("SDK Python", "implementado sem validação", "Pacote natalia instalável; não há cliente versionado separado."),
    ("CLI robusta", "implementado sem validação", "scripts/*.ps1 e scripts/*.sh; não há CLI rica."),
    ("Documentação de DSL", "validado", "docs/DSL.md."),
    ("Documentação de API", "implementado sem validação", "OpenAPI /docs; docs/DSL.md."),
    ("Tutoriais", "implementado sem validação", "README jornada guiada."),
    ("Exemplos", "validado", "examples/ e natalia/examples/."),
    ("Licença clara", "dependente de decisão", "Sem LICENSE raiz."),
    ("Contributing guide", "validado", "CONTRIBUTING.md."),
    ("Code of conduct", "implementado sem validação", "CODE_OF_CONDUCT.md adicionado nesta fatia."),
    ("Issue templates", "implementado sem validação", ".github/ISSUE_TEMPLATE/."),
    ("PR templates", "implementado sem validação", ".github/pull_request_template.md."),
    ("Roadmap público", "implementado sem validação", "docs/ROADMAP.md."),
    ("Crescer para 100k+", "não iniciado", "193 instâncias públicas em natalia/bench_data/v0.1."),
    ("Split por família", "implementado sem validação", "PhysVerifyBench v0.1 25 famílias; não cobre as famílias físicas listadas no anexo."),
    ("Split por dificuldade", "não iniciado", None),
    ("miniF2F", "não iniciado", None),
    ("Ingestão de LaTeX", "não iniciado", "source_latex armazenado, não interpretado."),
    ("LLM propõe, verificador decide", "não iniciado", "Sem provedor de modelo."),
    ("OIDC/OAuth2", "não iniciado", None),
    ("RBAC", "implementado sem validação", "Papel na API key; sem OPA."),
    ("gVisor ou Firecracker", "não iniciado", None),
    ("OpenTelemetry de verdade", "não iniciado", "Spans locais em natalia/telemetry.py."),
    ("Definir SLO 99.9%", "não iniciado", "Meta não medida."),
    ("Benchmark de throughput", "implementado sem validação", "scripts/benchmark.py mede o corpus de 9 exemplos, não 10k jobs/h."),
    ("Custo por verificação < $0.01", "não iniciado", "Não medido."),
]


def annex_sha256() -> str:
    return hashlib.sha256(ANNEX.read_bytes()).hexdigest()


def parse_annex(text: str):
    items = []
    section = "0"
    heading = "Anexo"
    counters: dict[str, int] = {}
    checkbox = re.compile(r"^- \[ \] \*\*(P[0-3])\*\* (.+)$")
    heading_re = re.compile(r"^(#{2,3}) (.+)$")
    for raw in text.splitlines():
        line = raw.strip()
        if match := heading_re.match(line):
            heading = match.group(2).strip()
            if match.group(1) == "##":
                num = re.match(r"^(\d+)", heading)
                section = num.group(1) if num else heading.split()[0].lower()
                if heading.lower().startswith("resumo"):
                    section = "resumo"
            else:
                num = re.match(r"^(\d+\.\d+)", heading)
                section = num.group(1) if num else section
            continue
        if match := checkbox.match(line):
            counters[section] = counters.get(section, 0) + 1
            ident = f"ANN-{section}-{counters[section]:03d}"
            items.append(_record(ident, match.group(1), heading, match.group(2), "anexo-checklist"))
            continue
        if section.startswith("16") or heading.startswith("Meses"):
            if line.startswith("- ") and not line.startswith("- ["):
                counters[section] = counters.get(section, 0) + 1
                ident = f"ANN-{section}-{counters[section]:03d}"
                items.append(
                    _record(
                        ident,
                        "P0",
                        heading,
                        line[2:].strip(),
                        "anexo-cronograma",
                        status="não iniciado",
                        note="Cronograma aspiracional do anexo; não é compromisso desta entrega.",
                    )
                )
    return items


def _record(ident, priority, section, original, source, status="não iniciado", note=None):
    sec_key = ident.split("-")[1] if ident.startswith("ANN-") else "0"
    nature = NATURE_BY_SECTION.get(sec_key, "engenharia")
    effort = EFFORT.get(priority, EFFORT["P2"])
    implementable = nature in {"engenharia", "produto", "operação"}
    return {
        "id": ident,
        "original_text": original,
        "source_section": section,
        "source_kind": source,
        "original_priority": priority,
        "nature": nature,
        "implementable_in_code": implementable and "contratar" not in original.lower() and "paper" not in original.lower(),
        "status": status,
        "dependencies": [],
        "required_owner": "engenharia" if implementable else nature,
        "effort": {**effort, "team_hypothesis": TEAM_HYPOTHESIS},
        "cost": {
            "currency": "USD",
            "as_of": "not-estimated-as-fact",
            "optimistic": None,
            "likely": None,
            "pessimistic": None,
            "note": "No cloud spend or specialist rates are known. Do not treat zeros as measurements.",
        },
        "acceptance_criterion": original,
        "evidence": note or "",
        "blockers": [],
        "execution_stage": _stage(sec_key, priority),
    }


def _stage(section: str, priority: str) -> str:
    if section in {"0", "1.1", "1.3"} or section.startswith("8"):
        return "A-B"
    if section.startswith("5") or section.startswith("6") or section.startswith("7"):
        return "C-E"
    if section.startswith("3") or section.startswith("4"):
        return "D"
    if section in {"2.1", "9.4", "10", "11", "12", "13", "14", "16", "resumo"}:
        return "F"
    return "B" if priority == "P0" else "C"


def apply_overlays(items):
    for item in items:
        text = item["original_text"]
        for needle, status, evidence in OVERLAY_RULES:
            if needle.lower() in text.lower():
                item["status"] = status
                if evidence:
                    item["evidence"] = evidence
                if status == "dependente de decisão":
                    item["blockers"] = ["Human/institutional decision required"]
                if status == "não iniciado" and any(
                    word in text.lower() for word in ("contratar", "nsf", "erc", "mit csail", "grant")
                ):
                    item["status"] = "bloqueado"
                    item["blockers"] = ["Requires human authorization, eligibility check, or external funding"]
                break
        if item["source_kind"] == "anexo-cronograma":
            item["status"] = "não iniciado"
            item["blockers"] = ["Aspirational multi-year schedule; not a delivery promise of this PR"]
        low = item["original_text"].lower()
        if any(k in low for k in ("contratar auditoria", "bug bounty", "workshop em", "phd afiliado")):
            item["status"] = "bloqueado"
            item["blockers"] = ["External action, eligibility, or spend requires a human owner"]
            item["implementable_in_code"] = False


def preamble_items():
    rows = []
    for ident, priority, nature, section, text in PREAMBLE:
        row = _record(ident, priority, section, text, "preambulo")
        row["nature"] = nature
        row["execution_stage"] = "A" if ident <= "ADD-15" or ident in {"ADD-27", "ADD-28", "ADD-33", "ADD-34", "ADD-35"} else "B"
        rows.append(row)
    overlays = {
        "ADD-01": ("validado", "docs/TRACEABILITY.json gerado por scripts/build_traceability.py"),
        "ADD-02": ("validado", "docs/annex/ORIGINAL_CHECKLIST.md"),
        "ADD-03": ("validado", "tests/test_traceability.py verifica marcadores e SHA-256"),
        "ADD-04": ("validado", "IDs ADD-* nesta matriz"),
        "ADD-05": ("validado", "Campo effort.team_hypothesis em cada registro"),
        "ADD-06": ("validado", "docs/DIAGNOSIS.md"),
        "ADD-07": ("validado", "scripts/reproduce_flow.py e testes de API/jobs"),
        "ADD-08": ("validado", "docs/DIAGNOSIS.md rubrica; scores do anexo como opinião"),
        "ADD-09": ("validado", "natalia/trust.py e docs/TRUST.md"),
        "ADD-10": ("implementado sem validação", "FAST e CERTIFIED em natalia/trust.py; AUTOFORMALIZED ausente"),
        "ADD-11": ("validado", "natalia/kernel.py fragmento polinomial + tests/test_trust.py"),
        "ADD-12": ("validado", "natalia/lean.py classify_lean_output + tests/test_lean.py"),
        "ADD-13": ("validado", "natalia/lean.py CHECK_ARGV_TEMPLATE"),
        "ADD-14": ("validado", "docs/TRUST.md TCB"),
        "ADD-15": ("implementado sem validação", "README perfis local/distributed; produção só planejada"),
        "ADD-16": ("implementado sem validação", "docs/DECISIONS.md"),
        "ADD-18": ("implementado sem validação", "docs/AUDIT.md e testes de injeção; sem gVisor"),
        "ADD-19": ("validado", "natalia/identity.py; teste cross-tenant"),
        "ADD-23": ("implementado sem validação", "natalia/static/index.html início"),
        "ADD-27": ("implementado sem validação", "Gate A parcialmente: scripts de setup e testes; usabilidade com pessoas não medida"),
        "ADD-28": ("implementado sem validação", "Kernel polinomial + recheck; Lean não certifica"),
        "ADD-33": ("validado", "README.md e scripts/setup.ps1"),
        "ADD-34": ("em execução", "PR desta fatia"),
        "ADD-35": ("validado", "docs/DIAGNOSIS.md seções de estado"),
    }
    for row in rows:
        if row["id"] in overlays:
            row["status"], row["evidence"] = overlays[row["id"]]
    return rows


def paragraph_items():
    extras = []
    pillars = [
        "Certificação independente (Lean/Coq/Alethe).",
        "Autoformalização verificada (LLM + verifier-in-the-loop).",
        "Benchmark global (100k+ com leaderboard).",
        "Arquitetura distribuída real (Postgres + NATS + S3 + K8s).",
        "Multi-tenant e segurança (OIDC + RBAC + sandbox).",
        "Papers e teoria (CAV/ITP/CPP/NeurIPS).",
        "Comunidade e governança (Mathlib + fundação + conselho).",
        "Funding e talento (NSF/ERC + PhDs + pós-docs).",
    ]
    for i, text in enumerate(pillars, 1):
        extras.append(
            _record(f"PARA-PILLAR-{i:02d}", "P0", "Resumo brutal", text, "anexo-paragrafo")
        )
    extras.append(
        _record(
            "PARA-SCORES-01",
            "P3",
            "Resumo brutal",
            "O README já está em 9/10. O código, em 6/10. A ciência, em 2/10. A comunidade, em 1/10. A governança, em 0/10. O funding, em 0/10.",
            "anexo-paragrafo",
            status="não aplicável",
            note="Opinião avaliativa do autor do anexo, não auditoria independente. Ver rubrica em docs/DIAGNOSIS.md.",
        )
    )
    extras.append(
        _record(
            "PARA-SCORES-02",
            "P3",
            "Resumo brutal",
            "A média é 3/10.",
            "anexo-paragrafo",
            status="não aplicável",
            note="Opinião do anexo; não reutilizar como avaliação pública sem rubrica independente.",
        )
    )
    extras.append(
        _record(
            "PARA-FALLBACK-01",
            "P0",
            "Resumo brutal",
            "Se faltar um dos oito pilares, 7/10; dois, 5/10; três, projeto local bem-feito.",
            "anexo-paragrafo",
            status="não aplicável",
            note="Heurística narrativa do anexo, não critério de aceite de código.",
        )
    )
    return extras


def build():
    text = ANNEX.read_text(encoding="utf-8")
    items = preamble_items() + parse_annex(text) + paragraph_items()
    apply_overlays(items)
    seen = {}
    for item in items:
        if item["id"] in seen:
            raise SystemExit(f"duplicate id {item['id']}")
        seen[item["id"]] = True
    payload = {
        "schema": "natalia-traceability-1.0",
        "annex_path": str(ANNEX.relative_to(ROOT)).replace("\\", "/"),
        "annex_sha256": annex_sha256(),
        "team_hypothesis": TEAM_HYPOTHESIS,
        "count": len(items),
        "by_status": dict(Counter(i["status"] for i in items)),
        "by_priority": dict(Counter(i["original_priority"] for i in items)),
        "items": items,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Matriz de rastreabilidade NatalIA",
        "",
        "Matriz gerada a partir de `docs/annex/ORIGINAL_CHECKLIST.md` e dos requisitos adicionais do preâmbulo.",
        f"SHA-256 do anexo: `{payload['annex_sha256']}`.",
        f"Registros: **{payload['count']}**.",
        "",
        TEAM_HYPOTHESIS,
        "",
        "Prioridades P0–P3 são as do anexo. `execution_stage` (A–F) é ordem de dependência, não renumeração.",
        "",
        "## Contagens",
        "",
        "Por estado: " + ", ".join(f"{k}={v}" for k, v in sorted(payload["by_status"].items())),
        "",
        "Por prioridade original: " + ", ".join(f"{k}={v}" for k, v in sorted(payload["by_priority"].items())),
        "",
        "A tabela completa está em [TRACEABILITY.json](TRACEABILITY.json). Abaixo, um registro por identificador.",
        "",
        "| ID | P | Estado | Natureza | Seção | Texto original |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        text_cell = item["original_text"].replace("|", "\\|")
        lines.append(
            f"| `{item['id']}` | {item['original_priority']} | {item['status']} | {item['nature']} | {item['source_section']} | {text_cell} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    data = build()
    print(data["count"], data["annex_sha256"], data["by_status"])
