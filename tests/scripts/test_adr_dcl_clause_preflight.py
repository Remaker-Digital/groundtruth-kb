"""Tests for the ADR/DCL clause-test preflight (Slice 1, advisory mode).

Per ``bridge/gtkb-adr-dcl-clause-test-enforcement-001.md`` Change 3 (GO at -002):

1. Schema parse test — TOML loads, all 5 fixtures parse with required fields.
2. Applicability discovery — true positive (in-root boundary triggers).
3. Applicability discovery — true negative (no boundary keywords).
4. Evidence detection — true positive (in-root output paths declared).
5. Evidence detection — true negative (out-of-root path → gap).
6. Advisory-mode exit code — CLI returns 0 even when blocking clauses gap.

Linked specs under verification:
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- (Slice-1 scope) read-only discipline + advisory-mode exit

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "adr_dcl_clause_preflight.py"
CLAUSES_CONFIG = REPO_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"


def _load_module():
    spec = importlib.util.spec_from_file_location("adr_dcl_clause_preflight", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["adr_dcl_clause_preflight"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def preflight():
    return _load_module()


def _stage_bridge(tmp_path: Path, bridge_id: str, content: str) -> tuple[Path, Path, Path]:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    bridge_file = bridge_dir / f"{bridge_id}-001.md"
    bridge_file.write_text(content, encoding="utf-8")
    index = bridge_dir / "INDEX.md"
    index.write_text(
        f"# Bridge Index\n\nDocument: {bridge_id}\nNEW: bridge/{bridge_id}-001.md\n",
        encoding="utf-8",
    )
    return bridge_file, index, bridge_dir


def test_schema_parses_with_five_fixtures(preflight):
    """Schema parse test — TOML loads, all 5 fixtures parse with required fields."""
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    assert len(clauses) == 5, f"expected 5 fixtures; got {len(clauses)}"
    required_spec_ids = {
        "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
        "GOV-FILE-BRIDGE-AUTHORITY-001",
        "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
        "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
        "GOV-STANDING-BACKLOG-001",
    }
    actual_spec_ids = {c.spec_id for c in clauses}
    assert actual_spec_ids == required_spec_ids, f"spec_id set mismatch: {actual_spec_ids} != {required_spec_ids}"
    for c in clauses:
        assert c.clause_id, f"missing clause_id on {c}"
        assert c.description, f"missing description on {c.clause_id}"
        assert c.severity in ("blocking", "advisory"), f"invalid severity on {c.clause_id}"
        assert c.enforcement_mode == "advisory_only_in_slice_1", (
            f"Slice 1 contract violation: clause {c.clause_id} has enforcement_mode={c.enforcement_mode}"
        )


def test_applicability_discovery_true_positive(preflight, tmp_path):
    """True positive: bridge content fires the in-root boundary clause's content trigger."""
    content = (
        "# Test bridge\n\n"
        "## Specification Links\n\n"
        "- ADR-ISOLATION-APPLICATION-PLACEMENT-001\n\n"
        "All artifacts must be in-root under E:\\GT-KB per the project root boundary.\n"
    )
    bridge_file, index, bridge_dir = _stage_bridge(tmp_path, "test-true-positive", content)
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    in_root_clause = next(c for c in clauses if "CLAUSE-IN-ROOT" in c.clause_id)
    applicability, reasons = preflight.evaluate_applicability(
        in_root_clause, content, "test-true-positive", [f"bridge/{bridge_file.name}"]
    )
    assert applicability == "must_apply", f"expected must_apply; got {applicability}; reasons: {reasons}"


def test_applicability_discovery_true_negative(preflight, tmp_path):
    """True negative: bridge content with no boundary keywords + non-bridge path → not_applicable."""
    content = (
        "# Test bridge\n\n"
        "## Specification Links\n\n"
        "- SPEC-EXAMPLE-001\n\n"
        "This bridge concerns user-interface widget styling decisions only.\n"
    )
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    in_root_clause = next(c for c in clauses if "CLAUSE-IN-ROOT" in c.clause_id)
    applicability, reasons = preflight.evaluate_applicability(
        in_root_clause, content, "test-widget-styling", ["docs/widget.md"]
    )
    assert applicability != "must_apply", (
        f"expected not_applicable or may_apply (no boundary keywords); got must_apply; reasons: {reasons}"
    )


def test_evidence_detection_true_positive(preflight):
    """True positive: bridge text contains in-root output paths → evidence_found = True."""
    content = (
        "## Files Changed\n\n"
        "- scripts/foo.py (new, under E:\\GT-KB\\scripts\\)\n"
        "- bridge/test-001.md (under E:\\GT-KB\\bridge\\)\n"
        "All outputs reside in-root under E:\\GT-KB per ADR-ISOLATION-APPLICATION-PLACEMENT-001.\n"
    )
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    in_root_clause = next(c for c in clauses if "CLAUSE-IN-ROOT" in c.clause_id)
    found, reasons, gap = preflight.evaluate_evidence(in_root_clause, content)
    assert found is True, f"expected evidence_found=True; got False; reasons: {reasons}; gap: {gap}"
    assert gap is None


def test_evidence_detection_true_negative_with_gap_summary(preflight):
    """True negative: bridge references an out-of-root path → evidence_found=False with gap summary."""
    content = (
        "## Files Changed\n\n"
        "- C:\\Users\\example\\foo.py (new)\n"
        "Outputs go to a sandbox path: out-of-root location.\n"
    )
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    in_root_clause = next(c for c in clauses if "CLAUSE-IN-ROOT" in c.clause_id)
    found, reasons, gap = preflight.evaluate_evidence(in_root_clause, content)
    assert found is False, f"expected evidence_found=False; got {found}; reasons: {reasons}"
    assert gap is not None and len(gap) > 0, f"expected non-empty gap_summary; got {gap}"


def test_cli_advisory_mode_always_exits_zero(preflight, tmp_path, capsys):
    """Advisory-mode contract: CLI exits 0 even when a blocking clause has an evidence gap."""
    bridge_id = "test-advisory-exit"
    content = (
        "# Test bridge\n\n"
        "Implementation will write outputs under C:\\Users\\evil\\out (out-of-root).\n"
        "This bridge concerns the project root boundary E:\\GT-KB.\n"
    )
    bridge_file, index, bridge_dir = _stage_bridge(tmp_path, bridge_id, content)
    out = tmp_path / "report.md"
    rc = preflight.main(
        [
            "--bridge-id", bridge_id,
            "--clauses-config", str(CLAUSES_CONFIG),
            "--bridge-dir", str(bridge_dir),
            "--index", str(index),
            "--out", str(out),
        ]
    )
    assert rc == 0, f"Slice 1 advisory contract: CLI must exit 0; got {rc}"
    report = out.read_text(encoding="utf-8")
    assert "Slice 1 mode: advisory" in report
    assert "Evidence Gaps" in report or "Evidence gaps in must_apply clauses: 0" in report
