"""Tests for scripts/wrap_scan_reconciliation.py (WI-4238 routine wrap-scan check).

Per bridge/gtkb-bridge-reconciliation-wrap-scan-check-002.md (GO at -002).

The scanner is report-only: it surfaces deviation counts by class from the
VERIFIED ``run_audit`` detector and always exits 0. These tests exercise the
pure transform, the always-zero exit contract, the read-only integration with
the real detector, determinism, finding-shape conformance, and an AST/text
guard proving the module carries no MemBase/bridge mutation surface.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(_SCRIPTS))
# bridge_reconciliation_audit puts groundtruth-kb/src on sys.path at import.
import bridge_reconciliation_audit  # noqa: E402,F401
import wrap_scan_reconciliation as wsr  # noqa: E402
from groundtruth_kb.db import KnowledgeDB  # noqa: E402


def _audit_result(counts_by_class: dict[str, int], *, generated_at: str = "2026-01-01T00:00:00Z") -> dict:
    """Build a synthetic ``run_audit``-shaped result for pure-transform tests."""
    issues: list[dict] = []
    for deviation_class, count in counts_by_class.items():
        for index in range(count):
            issues.append(
                {
                    "class": deviation_class,
                    "type": f"{deviation_class}_type",
                    "subject": f"WI-{index}",
                    "severity": "P2",
                    "evidence": {},
                    "recommended_action": "n/a",
                }
            )
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "issue_count": len(issues),
        "counts_by_class": dict(counts_by_class),
        "issues": issues,
    }


# --- Pure transform: one finding per non-zero class + roll-up -----------------


def test_findings_one_per_nonzero_class() -> None:
    audit = _audit_result({"verified_bridge_backlog": 2, "stale_backlog_status": 1, "healthy_zero": 0})
    findings = wsr.build_reconciliation_findings(audit)
    per_class = [f for f in findings if f["check"] == "reconciliation_deviation_class"]
    # zero-count classes must not produce a finding
    assert len(per_class) == 2
    surfaced = {f["deviation_class"] for f in per_class}
    assert surfaced == {"verified_bridge_backlog", "stale_backlog_status"}
    # per-class findings are sorted by class name for determinism
    assert [f["deviation_class"] for f in per_class] == sorted(surfaced)


def test_rollup_finding_totals() -> None:
    audit = _audit_result({"verified_bridge_backlog": 2, "stale_backlog_status": 3})
    findings = wsr.build_reconciliation_findings(audit)
    rollup = [f for f in findings if f["check"] == "reconciliation_rollup"]
    assert len(rollup) == 1
    assert rollup[0]["deviation_total"] == 5
    assert rollup[0]["class_count"] == 2
    assert rollup[0]["counts_by_class"] == {"stale_backlog_status": 3, "verified_bridge_backlog": 2}
    # roll-up is last
    assert findings[-1] is rollup[0]


def test_verified_bridge_backlog_class_surfaced() -> None:
    """A verified_bridge_backlog deviation is surfaced as its own per-class finding."""
    audit = _audit_result({"verified_bridge_backlog": 1})
    findings = wsr.build_reconciliation_findings(audit)
    classes = [f.get("deviation_class") for f in findings if f["check"] == "reconciliation_deviation_class"]
    assert "verified_bridge_backlog" in classes


def test_zero_deviations_informational() -> None:
    """Empty audit -> single informational clean finding (never an error)."""
    findings = wsr.build_reconciliation_findings(_audit_result({}))
    assert len(findings) == 1
    only = findings[0]
    assert only["check"] == "reconciliation_clean"
    assert only["severity"] == wsr.SEVERITY_INFORMATIONAL
    assert only["report_only"] is True
    assert only["deviation_total"] == 0


def test_counts_fallback_from_issues_when_counts_key_absent() -> None:
    """When counts_by_class is absent, counts are derived from the issues list."""
    audit = {
        "issues": [
            {"class": "stale_backlog_status"},
            {"class": "stale_backlog_status"},
            {"class": "bridge_index_drift"},
        ]
    }
    counts = wsr._counts_by_class(audit)
    assert counts == {"bridge_index_drift": 1, "stale_backlog_status": 2}


# --- Finding-shape / contract conformance -------------------------------------


def test_finding_shape_matches_contract() -> None:
    audit = _audit_result({"stale_backlog_status": 1})
    for finding in wsr.build_reconciliation_findings(audit):
        assert set(("check", "severity", "report_only", "message")).issubset(finding.keys())
        assert finding["severity"] == wsr.SEVERITY_INFORMATIONAL
        assert finding["report_only"] is True
        assert isinstance(finding["message"], str) and finding["message"]


# --- Determinism --------------------------------------------------------------


def test_determinism_same_input_same_output() -> None:
    audit = _audit_result({"verified_bridge_backlog": 2, "stale_backlog_status": 1})
    first = wsr.build_reconciliation_findings(audit)
    second = wsr.build_reconciliation_findings(audit)
    assert first == second
    # report-level byte-identical output when generated_at is injected/equal
    report = {
        "scanner_id": wsr.SCANNER_ID,
        "generated_at": "2026-01-01T00:00:00Z",
        "report_only": True,
        "severity_model": wsr.SEVERITY_INFORMATIONAL,
        "finding_count": len(first),
        "findings": first,
        "counts_by_class": wsr._counts_by_class(audit),
    }
    assert wsr.render_json(report) == wsr.render_json(report)


# --- Always-zero exit contract ------------------------------------------------


def test_main_exit_code_always_zero(monkeypatch, capsys) -> None:
    # clean
    monkeypatch.setattr(wsr, "run_audit", lambda **_: _audit_result({}))
    assert wsr.main(["--stdout"]) == wsr.EXIT_OK
    clean_out = json.loads(capsys.readouterr().out)
    assert clean_out["finding_count"] == 1

    # with deviations -> still exit 0
    monkeypatch.setattr(wsr, "run_audit", lambda **_: _audit_result({"verified_bridge_backlog": 4}))
    assert wsr.main(["--stdout"]) == wsr.EXIT_OK
    dirty_out = json.loads(capsys.readouterr().out)
    assert dirty_out["counts_by_class"] == {"verified_bridge_backlog": 4}
    assert any(f["check"] == "reconciliation_rollup" for f in dirty_out["findings"])


def test_main_writes_report_files(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(wsr, "run_audit", lambda **_: _audit_result({"stale_backlog_status": 1}))
    out_dir = tmp_path / "wrap-scan-out"
    rc = wsr.main(["--output-dir", str(out_dir)])
    assert rc == wsr.EXIT_OK
    json_path = out_dir / f"{wsr.REPORT_STEM}.json"
    md_path = out_dir / f"{wsr.REPORT_STEM}.md"
    assert json_path.exists() and md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["scanner_id"] == wsr.SCANNER_ID
    assert "stale_backlog_status" in md_path.read_text(encoding="utf-8")


# --- Read-only integration with the real VERIFIED detector --------------------


def _build_fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True)
    (bridge_dir / "INDEX.md").write_text(
        "Document: sample-thread\nVERIFIED: bridge/sample-thread-001.md\n",
        encoding="utf-8",
    )
    # First non-blank line is the canonical status token; body has no WI id, so
    # the detector surfaces a verified_bridge_without_backlog_match deviation.
    (bridge_dir / "sample-thread-001.md").write_text(
        "VERIFIED\n\nVerified sample thread with no backlog linkage.\n",
        encoding="utf-8",
    )
    # Empty MemBase (schema auto-created on construction).
    KnowledgeDB(root / "groundtruth.db").close()
    return root


def test_scan_invokes_run_audit_readonly(tmp_path) -> None:
    root = _build_fixture_root(tmp_path)
    index_path = root / "bridge" / "INDEX.md"
    thread_path = root / "bridge" / "sample-thread-001.md"
    index_before = index_path.read_bytes()
    thread_before = thread_path.read_bytes()

    report = wsr.scan(root, generated_at="2026-01-01T00:00:00Z")

    # Integration: the detector surfaced the no-backlog-evidence deviation.
    assert report["scanner_id"] == wsr.SCANNER_ID
    assert report["finding_count"] >= 1
    assert "verified_bridge_without_backlog_match" in report["counts_by_class"]
    assert any(f["check"] == "reconciliation_deviation_class" for f in report["findings"])

    # Read-only: bridge inputs are byte-identical and no backlog row was created.
    assert index_path.read_bytes() == index_before
    assert thread_path.read_bytes() == thread_before
    db = KnowledgeDB(root / "groundtruth.db")
    try:
        assert db.list_work_items() == []
    finally:
        db.close()


# --- No mutation surface (AST/text guard) -------------------------------------


def test_no_mutation_surface_ast() -> None:
    """The module must not carry any MemBase/bridge mutation surface."""
    source = Path(wsr.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    # No import of the mutation-capable MemBase API.
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

    # No call to a known mutation method.
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

    # The module's only data source is the public run_audit surface.
    assert "run_audit" in imported_names
    assert not any(name.startswith("_") and name != "_atomic_write_text" for name in imported_names)
