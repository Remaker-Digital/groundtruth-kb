"""Tests for the ADR/DCL clause-test preflight (Slice 2, mandatory gate).

Per ``bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md``
(GO at ``-004``):

Slice-1-carried-forward (5 tests):
1. Schema parse test — TOML loads, all 5 fixtures parse with required fields.
   Modified per Slice 2: enforcement_mode assertion uses VALID_ENFORCEMENT_MODES set
   instead of literal-equality with the retired Slice-1 sentinel.
2. Applicability discovery — true positive (in-root boundary triggers).
3. Applicability discovery — true negative (no boundary keywords).
4. Evidence detection — true positive (in-root output paths declared).
5. Evidence detection — true negative (out-of-root path → gap).

Slice-1 advisory-exit test deleted: ``test_cli_advisory_mode_always_exits_zero``
encoded the retired Slice-1 contract (CLI always exits 0 even when blocking
clauses gap). Slice 2 retires that contract; the new tests below cover the
replacement default-invocation exit-code semantics plus the diagnostic-only
``--report-only`` behavior.

Slice 2 added (7 tests):
6.  test_all_slice_1_fixtures_promoted_to_blocking — F1: every fixture has
    enforcement_mode == "blocking" after promotion.
7.  test_mixed_enforcement_modes_supported — F1: loader accepts mixed
    enforcement_mode values for future Slice-4 ratchet adoption.
8.  test_blocking_evidence_gap_exits_nonzero — Change 2: default invocation
    exits 5 when must_apply blocking clause has no evidence.
9.  test_blocking_evidence_present_exits_zero — Change 2: default invocation
    exits 0 when evidence found.
10. test_report_only_flag_does_not_change_exit_code — F2: --report-only
    returns the same exit code as default invocation.
11. test_report_only_emits_non_authorization_banner — F2: --report-only
    output contains the non-authorization banner text.
12. test_explicit_owner_waiver_clears_blocking_gap — Change 2: bridge content
    with an explicit owner-waiver line satisfies the gate without evidence.

Linked specs under verification:
- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- (Slice-2 scope) mandatory gate exit-code semantics + --report-only diagnostic mode

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

VALID_ENFORCEMENT_MODES = {"blocking", "advisory"}


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
        assert c.enforcement_mode in VALID_ENFORCEMENT_MODES, (
            f"clause {c.clause_id} has invalid enforcement_mode={c.enforcement_mode!r}; "
            f"expected one of {VALID_ENFORCEMENT_MODES}"
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
        "## Files Changed\n\n- C:\\Users\\example\\foo.py (new)\nOutputs go to a sandbox path: out-of-root location.\n"
    )
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    in_root_clause = next(c for c in clauses if "CLAUSE-IN-ROOT" in c.clause_id)
    found, reasons, gap = preflight.evaluate_evidence(in_root_clause, content)
    assert found is False, f"expected evidence_found=False; got {found}; reasons: {reasons}"
    assert gap is not None and len(gap) > 0, f"expected non-empty gap_summary; got {gap}"


# Slice 2 added tests below: the retired Slice-1 advisory-mode test
# (``test_cli_advisory_mode_always_exits_zero``) was deleted because it
# encoded the contract that this slice intentionally retires. Replacement
# coverage is provided by ``test_blocking_evidence_gap_exits_nonzero``,
# ``test_blocking_evidence_present_exits_zero``, and
# ``test_report_only_flag_does_not_change_exit_code`` below.


def test_all_slice_1_fixtures_promoted_to_blocking(preflight):
    """F1 positive: every Slice-1 fixture spec_id has enforcement_mode == 'blocking'
    after Slice 2 promotion (the original 5 fixtures stay at blocking).
    """
    clauses = preflight.load_clauses(CLAUSES_CONFIG)
    slice_1_spec_ids = {
        "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
        "GOV-FILE-BRIDGE-AUTHORITY-001",
        "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
        "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
        "GOV-STANDING-BACKLOG-001",
    }
    promoted = [c for c in clauses if c.spec_id in slice_1_spec_ids]
    assert len(promoted) == len(slice_1_spec_ids)
    for c in promoted:
        assert c.enforcement_mode == "blocking", (
            f"Slice 2 promotion: clause {c.clause_id} should be enforcement_mode='blocking'; got {c.enforcement_mode!r}"
        )


def test_mixed_enforcement_modes_supported(preflight, tmp_path):
    """F1 mixed-mode coexistence: the loader accepts both 'blocking' and 'advisory'
    enforcement_mode values, supporting Slice-4 ratchet adoption (new clauses begin
    advisory before owner-promoted to blocking).
    """
    config = tmp_path / "mixed-modes.toml"
    config.write_text(
        "[[clauses]]\n"
        'clause_id = "TEST-001/blocking"\n'
        'spec_id = "TEST-001"\n'
        'description = "Blocking-mode fixture."\n'
        'applies_when_path = ["**/*"]\n'
        "applies_when_doc_name = []\n"
        'applies_when_content = ["test"]\n'
        'evidence_required = "any"\n'
        'evidence_pattern = "evidence"\n'
        'failure_condition = "any"\n'
        'severity = "blocking"\n'
        'waiver_policy = "explicit_owner_waiver_required_in_bridge"\n'
        'enforcement_mode = "blocking"\n\n'
        "[[clauses]]\n"
        'clause_id = "TEST-002/advisory"\n'
        'spec_id = "TEST-002"\n'
        'description = "Advisory-mode fixture (Slice-4 ratchet pattern)."\n'
        'applies_when_path = ["**/*"]\n'
        "applies_when_doc_name = []\n"
        'applies_when_content = ["test"]\n'
        'evidence_required = "any"\n'
        'evidence_pattern = "evidence"\n'
        'failure_condition = "any"\n'
        'severity = "blocking"\n'
        'waiver_policy = "advisory_only"\n'
        'enforcement_mode = "advisory"\n',
        encoding="utf-8",
    )
    clauses = preflight.load_clauses(config)
    assert len(clauses) == 2
    by_id = {c.clause_id: c for c in clauses}
    assert by_id["TEST-001/blocking"].enforcement_mode == "blocking"
    assert by_id["TEST-002/advisory"].enforcement_mode == "advisory"


def test_blocking_evidence_gap_exits_nonzero(preflight, tmp_path):
    """Change 2: default invocation exits 5 when a must_apply blocking clause
    has no satisfying evidence and no owner-waiver line.
    """
    bridge_id = "test-blocking-gap"
    # Content fires the in-root clause's content trigger BUT references an
    # out-of-root output path, so evidence_pattern fails AND failure_pattern
    # matches. No owner-waiver line.
    content = (
        "# Test bridge\n\n"
        "## Specification Links\n\n"
        "- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — project root boundary\n\n"
        "Implementation will write outputs under C:\\Users\\evil\\out (out-of-root).\n"
    )
    _bridge_file, index, bridge_dir = _stage_bridge(tmp_path, bridge_id, content)
    out = tmp_path / "report.md"
    rc = preflight.main(
        [
            "--bridge-id",
            bridge_id,
            "--clauses-config",
            str(CLAUSES_CONFIG),
            "--bridge-dir",
            str(bridge_dir),
            "--index",
            str(index),
            "--out",
            str(out),
        ]
    )
    assert rc == preflight.EXIT_BLOCKING_GAP, (
        f"Slice 2 mandatory gate: CLI must exit {preflight.EXIT_BLOCKING_GAP} on blocking gap; got {rc}"
    )
    report = out.read_text(encoding="utf-8")
    assert "Blocking Gaps" in report, "Slice 2 report must include the Blocking Gaps subsection on gate failure"


def test_blocking_evidence_present_exits_zero(preflight, tmp_path):
    """Change 2: default invocation exits 0 when must_apply blocking clauses
    have satisfying evidence.
    """
    bridge_id = "test-blocking-pass"
    content = (
        "# Test bridge\n\n"
        "## Specification Links\n\n"
        "- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — project root boundary\n\n"
        "## Files Changed\n\n"
        "- scripts/foo.py (new, under E:\\GT-KB\\scripts\\)\n"
        "All outputs reside in-root under E:\\GT-KB per ADR-ISOLATION-APPLICATION-PLACEMENT-001.\n"
    )
    _bridge_file, index, bridge_dir = _stage_bridge(tmp_path, bridge_id, content)
    out = tmp_path / "report.md"
    rc = preflight.main(
        [
            "--bridge-id",
            bridge_id,
            "--clauses-config",
            str(CLAUSES_CONFIG),
            "--bridge-dir",
            str(bridge_dir),
            "--index",
            str(index),
            "--out",
            str(out),
        ]
    )
    assert rc == 0, f"Slice 2 mandatory gate: CLI must exit 0 when evidence is present; got {rc}"


def test_report_only_flag_does_not_change_exit_code(preflight, tmp_path):
    """F2: --report-only preserves the default invocation's exit code. Same
    bridge content + flag yields exit 5 with gap, exit 0 without.
    """
    # Reuse the gap fixture from test_blocking_evidence_gap_exits_nonzero.
    bridge_id = "test-report-only-gap"
    content = (
        "# Test bridge\n\n"
        "## Specification Links\n\n"
        "- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — project root boundary\n\n"
        "Implementation will write outputs under C:\\Users\\evil\\out (out-of-root).\n"
    )
    _bridge_file, index, bridge_dir = _stage_bridge(tmp_path, bridge_id, content)
    out = tmp_path / "report.md"
    rc = preflight.main(
        [
            "--bridge-id",
            bridge_id,
            "--clauses-config",
            str(CLAUSES_CONFIG),
            "--bridge-dir",
            str(bridge_dir),
            "--index",
            str(index),
            "--out",
            str(out),
            "--report-only",
        ]
    )
    assert rc == preflight.EXIT_BLOCKING_GAP, (
        f"--report-only must NOT silently bypass the gate; expected exit {preflight.EXIT_BLOCKING_GAP}, got {rc}"
    )


def test_report_only_emits_non_authorization_banner(preflight, tmp_path):
    """F2: --report-only output contains the unconditional non-authorization banner."""
    bridge_id = "test-report-only-banner"
    content = (
        "# Test bridge\n\n"
        "## Specification Links\n\n"
        "- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — project root boundary\n\n"
        "## Files Changed\n\n"
        "- scripts/foo.py (new, under E:\\GT-KB\\scripts\\)\n"
        "All outputs reside in-root under E:\\GT-KB per ADR-ISOLATION-APPLICATION-PLACEMENT-001.\n"
    )
    _bridge_file, index, bridge_dir = _stage_bridge(tmp_path, bridge_id, content)
    out = tmp_path / "report.md"
    rc = preflight.main(
        [
            "--bridge-id",
            bridge_id,
            "--clauses-config",
            str(CLAUSES_CONFIG),
            "--bridge-dir",
            str(bridge_dir),
            "--index",
            str(index),
            "--out",
            str(out),
            "--report-only",
        ]
    )
    assert rc == 0, f"clean-evidence + --report-only must exit 0; got {rc}"
    report = out.read_text(encoding="utf-8")
    assert "DIAGNOSTIC ONLY" in report, "--report-only output must include the non-authorization banner"
    assert "CANNOT satisfy GO/VERIFIED" in report
    assert "Owner waiver:" in report  # The banner advertises the bypass mechanism.


def test_explicit_owner_waiver_clears_blocking_gap(preflight, tmp_path):
    """Change 2: an explicit ``Owner waiver: <clause_id> — <DELIB-ID> — <reason>``
    line in the bridge content satisfies the gate without satisfying-evidence text.
    """
    bridge_id = "test-owner-waiver"
    # Same out-of-root content that would fail without the waiver.
    content = (
        "# Test bridge\n\n"
        "## Specification Links\n\n"
        "- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — project root boundary\n\n"
        "Implementation will write outputs under C:\\Users\\evil\\out (out-of-root).\n\n"
        "## Owner Decisions / Input\n\n"
        "Owner waiver: ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT — DELIB-S336-TEST-WAIVER — "
        "explicit owner approval for sandbox output path during this verification fixture.\n"
    )
    _bridge_file, index, bridge_dir = _stage_bridge(tmp_path, bridge_id, content)
    out = tmp_path / "report.md"
    rc = preflight.main(
        [
            "--bridge-id",
            bridge_id,
            "--clauses-config",
            str(CLAUSES_CONFIG),
            "--bridge-dir",
            str(bridge_dir),
            "--index",
            str(index),
            "--out",
            str(out),
        ]
    )
    assert rc == 0, f"explicit owner-waiver line for the offending clause must clear the blocking gap; got exit {rc}"
