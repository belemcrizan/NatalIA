import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _mod():
    path = ROOT / "scripts" / "build_traceability.py"
    spec = importlib.util.spec_from_file_location("build_traceability", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_annex_is_preserved():
    mod = _mod()
    text = mod.ANNEX.read_text(encoding="utf-8")
    assert "<!-- BEGIN ORIGINAL TEXT -->" in text
    assert "<!-- END ORIGINAL TEXT -->" in text
    assert "Checklist completo para 10/10 — NatalIA" in text
    assert "A média é 3/10." in text
    assert len(mod.annex_sha256()) == 64


def test_checkbox_inventory_is_complete():
    mod = _mod()
    text = mod.ANNEX.read_text(encoding="utf-8")
    marked = [line for line in text.splitlines() if line.strip().startswith("- [ ] **P")]
    parsed = mod.parse_annex(text)
    checkboxes = [item for item in parsed if item["source_kind"] == "anexo-checklist"]
    assert len(checkboxes) == len(marked)
    assert len(marked) >= 400
    schedule = [item for item in parsed if item["source_kind"] == "anexo-cronograma"]
    assert len(schedule) >= 20


def test_matrix_contains_preamble_and_unique_ids():
    mod = _mod()
    payload = mod.build()
    ids = [item["id"] for item in payload["items"]]
    assert len(ids) == len(set(ids))
    assert any(i.startswith("ADD-") for i in ids)
    assert any(i.startswith("ANN-") for i in ids)
    assert any(i.startswith("PARA-") for i in ids)
    assert payload["annex_sha256"] == mod.annex_sha256()
    lean = next(item for item in payload["items"] if "lean --check" in item["original_text"])
    assert "lean" in lean["evidence"].lower()
