"""Tests for scripts/wrap_scan_reconciliation.py.

The current wrap scanner is report-only: it surfaces status counts from
status-bearing numbered bridge files and always exits 0.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))
import wrap_scan_reconciliation as wsr  # noqa: E402


def test_build_reconciliation_findings_reports_status_rollup() -> None:
    findings = wsr.build_reconciliation_findings({"GO": 2, "NEW": 1})

    assert len(findings) == 1
    rollup = findings[0]
    assert rollup["check"] == "bridge_status_rollup"
    assert rollup["severity"] == wsr.SEVERITY_INFORMATIONAL
    assert rollup["report_only"] is True
    assert rollup["bridge_document_total"] == 3
    assert rollup["bridge_status_counts"] == {"GO": 2, "NEW": 1}


def test_zero_status_counts_still_informational() -> None:
    findings = wsr.build_reconciliation_findings({})

    assert len(findings) == 1
    only = findings[0]
    assert only["check"] == "bridge_status_rollup"
    assert only["severity"] == wsr.SEVERITY_INFORMATIONAL
    assert only["report_only"] is True
    assert only["bridge_document_total"] == 0
    assert only["bridge_status_counts"] == {}


def test_finding_shape_matches_contract() -> None:
    for finding in wsr.build_reconciliation_findings({"VERIFIED": 1}):
        assert {"check", "severity", "report_only", "message"}.issubset(finding.keys())
        assert finding["severity"] == wsr.SEVERITY_INFORMATIONAL
        assert finding["report_only"] is True
        assert isinstance(finding["message"], str) and finding["message"]


def test_determinism_same_input_same_output() -> None:
    first = wsr.build_reconciliation_findings({"GO": 1, "VERIFIED": 2})
    second = wsr.build_reconciliation_findings({"GO": 1, "VERIFIED": 2})

    assert first == second
    report = {
        "scanner_id": wsr.SCANNER_ID,
        "generated_at": "2026-01-01T00:00:00Z",
        "report_only": True,
        "severity_model": wsr.SEVERITY_INFORMATIONAL,
        "finding_count": len(first),
        "findings": first,
        "bridge_status_counts": {"GO": 1, "VERIFIED": 2},
    }
    assert wsr.render_json(report) == wsr.render_json(report)


def test_scan_counts_versioned_bridge_files_readonly(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True)
    first = bridge_dir / "sample-thread-001.md"
    second = bridge_dir / "sample-thread-002.md"
    first.write_text("NEW\n\nInitial proposal.\n", encoding="utf-8")
    second.write_text("VERIFIED\n\nVerified sample thread.\n", encoding="utf-8")
    first_before = first.read_bytes()
    second_before = second.read_bytes()

    report = wsr.scan(root, generated_at="2026-01-01T00:00:00Z")

    assert report["scanner_id"] == wsr.SCANNER_ID
    assert report["finding_count"] == 1
    assert report["bridge_status_counts"] == {"VERIFIED": 1}
    assert report["findings"][0]["bridge_document_total"] == 1
    assert first.read_bytes() == first_before
    assert second.read_bytes() == second_before


def test_main_exit_code_always_zero(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setattr(wsr, "_bridge_status_counts", lambda *_args, **_kwargs: {})
    assert wsr.main(["--project-root", str(tmp_path), "--stdout"]) == wsr.EXIT_OK
    clean_out = json.loads(capsys.readouterr().out)
    assert clean_out["finding_count"] == 1
    assert clean_out["bridge_status_counts"] == {}

    monkeypatch.setattr(wsr, "_bridge_status_counts", lambda *_args, **_kwargs: {"NO-GO": 4})
    assert wsr.main(["--project-root", str(tmp_path), "--stdout"]) == wsr.EXIT_OK
    dirty_out = json.loads(capsys.readouterr().out)
    assert dirty_out["bridge_status_counts"] == {"NO-GO": 4}
    assert dirty_out["findings"][0]["bridge_document_total"] == 4


def test_main_writes_report_files(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(wsr, "_bridge_status_counts", lambda *_args, **_kwargs: {"REVISED": 1})
    out_dir = tmp_path / "wrap-scan-out"

    rc = wsr.main(["--project-root", str(tmp_path), "--output-dir", str(out_dir)])

    assert rc == wsr.EXIT_OK
    json_path = out_dir / f"{wsr.REPORT_STEM}.json"
    md_path = out_dir / f"{wsr.REPORT_STEM}.md"
    assert json_path.exists() and md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["scanner_id"] == wsr.SCANNER_ID
    assert payload["bridge_status_counts"] == {"REVISED": 1}
    assert "REVISED: 1" in md_path.read_text(encoding="utf-8")


def test_no_mutation_surface_ast() -> None:
    source = Path(wsr.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)
            imported_names.update(alias.name for alias in node.names)
    assert "groundtruth_kb.db" not in imported_modules
    assert "KnowledgeDB" not in imported_names
    assert "bridge_reconciliation_audit" not in imported_modules
    assert "run_audit" not in imported_names

    forbidden = {
        "insert_spec",
        "update_spec",
        "insert_work_item",
        "update_work_item",
        "resolve_work_item",
        "insert_deliberation",
        "insert_test",
        "insert_document",
        "commit",
        "executescript",
        "execute",
        "executemany",
    }
    called: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                called.add(func.attr)
            elif isinstance(func, ast.Name):
                called.add(func.id)
    assert forbidden.isdisjoint(called), f"forbidden mutation calls present: {forbidden & called}"
