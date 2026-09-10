# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Read-only citation diagnostics and their baseline hook adapter.

Raw file publication and header-repair assertions are retired. Native delivery
validates current claim, scope and author provenance independently.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from scripts.verdict_evidence_anchor_preflight import (
    build_packet,
    validate_verdict_evidence_anchors,
    verdict_status,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = PROJECT_ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"


def _write_op(tmp_path: Path, rel: str, lines: list[str]) -> None:
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mark_project_root(tmp_path: Path) -> None:
    (tmp_path / "groundtruth.toml").write_text("[project]\nname = 'verdict-anchor-fixture'\n", encoding="utf-8")


def _verdict(body: str, *, status: str = "NO-GO", reviewed: str | None = "bridge/foo-001.md") -> str:
    head = status + "\n"
    if reviewed is not None:
        head += f"Responds to: {reviewed}\n"
    return head + "\n" + body + "\n"


def _kinds(violations) -> set[str]:
    return {violation.kind for violation in violations}


# --- Item 1: valid operative citation + quote passes ------------------------


def test_valid_operative_line_and_quote_passes(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan", "the widget must validate input", "tail"])
    content = _verdict('Concern: line 4 reads "must validate input" and `bridge/foo-001.md:4` is in range.')
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


# --- Item 2: missing operative file fails -----------------------------------


def test_missing_operative_file_fails(tmp_path: Path) -> None:
    content = _verdict("Problem at `bridge/ghost-001.md:10`.", reviewed="bridge/ghost-001.md")
    assert "missing_file" in _kinds(validate_verdict_evidence_anchors(content, project_root=tmp_path))


# --- Item 3: operative line out of range fails ------------------------------


def test_operative_line_out_of_range_fails(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan"])
    content = _verdict("See `bridge/foo-001.md:86`.")
    assert "line_out_of_range" in _kinds(validate_verdict_evidence_anchors(content, project_root=tmp_path))


# --- Item 4: hallucinated quoted string fails (WI-4520 shape) ----------------


def test_hallucinated_quoted_string_fails(tmp_path: Path) -> None:
    # Line 3 EXISTS ('## Implementation Plan'); the verdict quotes a placeholder
    # that is nowhere in the operative document -- exactly the WI-4520 failure.
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Implementation Plan", "real content", "tail"])
    content = _verdict('F1: cites a placeholder at line 3 ("Helper-suggested candidates placeholder").')
    assert "string_not_found" in _kinds(validate_verdict_evidence_anchors(content, project_root=tmp_path))


def test_valid_quoted_string_at_line_passes(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Implementation Plan", "real content", "tail"])
    content = _verdict('F1: line 3 reads "## Implementation Plan" as expected.')
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


# --- Item 5: operative path-separator normalization -------------------------


def test_operative_windows_separator_normalizes(tmp_path: Path) -> None:
    _write_op(tmp_path, "scripts/foo.py", ["alpha", "beta", "gamma"])
    content = _verdict(r"Issue at `scripts\foo.py:2`.", reviewed="scripts/foo.py")
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


# --- Item 6: opt-out and absence markers skip -------------------------------


def test_inference_marker_skips(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan"])
    content = _verdict("See `bridge/foo-001.md:86` [inference].")
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_no_exact_anchor_marker_skips(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan", "x", "y"])
    content = _verdict('Near line 3 citing "ghost placeholder text" [no exact anchor].')
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_absence_keyword_skips(tmp_path: Path) -> None:
    content = _verdict("The file `bridge/ghost-001.md:10` is missing.", reviewed="bridge/ghost-001.md")
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_absent_marker_skips(tmp_path: Path) -> None:
    content = _verdict("Citation `bridge/ghost-001.md:10` [absent].", reviewed="bridge/ghost-001.md")
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


# --- Item 7: multi-line explicit ranges -------------------------------------


def test_multiline_range_within_bounds_passes(tmp_path: Path) -> None:
    _write_op(tmp_path, "scripts/foo.py", ["a", "b", "c", "d", "e"])
    content = _verdict("Range `scripts/foo.py:2-4` is relevant.", reviewed="scripts/foo.py")
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_multiline_range_exceeding_length_fails(tmp_path: Path) -> None:
    _write_op(tmp_path, "scripts/foo.py", ["a", "b", "c", "d", "e"])
    content = _verdict("Range `scripts/foo.py:3-99` is wrong.", reviewed="scripts/foo.py")
    assert "line_out_of_range" in _kinds(validate_verdict_evidence_anchors(content, project_root=tmp_path))


# --- Operative-scoping invariants (false-positive hardening) -----------------


def test_non_operative_citation_not_checked(tmp_path: Path) -> None:
    # A citation to a file that is NOT the operative document is never checked,
    # even with a wild line number -- it may be a retired, moved, or proposed file.
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan"])
    content = _verdict("Compare to `scripts/other_module.py:9999` for context.")
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_bare_line_without_quote_not_range_checked(tmp_path: Path) -> None:
    # A bare "line N" referring to source code (no quote) must not be attributed
    # to the operative bridge file's length.
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan"])
    content = _verdict("The handler at lines 588-590 is the relevant logic.")
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_no_operative_header_means_no_check(tmp_path: Path) -> None:
    content = _verdict("Issue at `bridge/whatever-001.md:999`.", reviewed=None)
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_quote_attributed_to_named_source_not_flagged(tmp_path: Path) -> None:
    # Quotes tied to a spec/doc (no adjacent bare operative line) are not checked.
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan", "x", "y"])
    content = _verdict('GOV-EXAMPLE-001 states that "all projects retire collectively" per policy.')
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


# --- Gating: only NO-GO/VERIFIED are checked --------------------------------


def test_non_gated_status_is_not_checked(tmp_path: Path) -> None:
    content = "GO\nResponds to: bridge/foo-001.md\n\nApproved; see `bridge/foo-001.md:9999`.\n"
    assert verdict_status(content) is None
    assert validate_verdict_evidence_anchors(content, project_root=tmp_path) == []


def test_verified_status_is_gated(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["a", "b"])
    content = _verdict("Verified at `bridge/foo-001.md:99`.", status="VERIFIED")
    assert verdict_status(content) == "VERIFIED"
    assert "line_out_of_range" in _kinds(validate_verdict_evidence_anchors(content, project_root=tmp_path))


def test_build_packet_reports_violations(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Plan"])
    packet = build_packet(content=_verdict("See `bridge/foo-001.md:86`."), project_root=tmp_path)
    assert packet["gated"] is True
    assert packet["violation_count"] >= 1
    assert "Verdict Evidence Anchors" in packet["markdown"]


# --- Item 8: write_bridge_file integration (helper-routed chokepoint) --------


# --- Item 9: bridge-compliance-gate hook integration (Write-tool chokepoint) -


def _load_hook():
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate_under_test", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_hook_blocks_fabricated_nogo(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Implementation Plan", "tail"])
    hook = _load_hook()
    bad = _verdict("F1: bad citation at `bridge/foo-001.md:99`.")
    reason = hook._verdict_evidence_anchor_deny_reason(bad, tmp_path)
    assert reason is not None
    assert "WI-4520" in reason


def test_hook_allows_valid_nogo(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Implementation Plan", "real anchored text"])
    hook = _load_hook()
    good = _verdict("F1: `bridge/foo-001.md:4` is in range.")
    assert hook._verdict_evidence_anchor_deny_reason(good, tmp_path) is None


# --- WI-5437: unsupported exact-path removal claims ------------------------


def test_unsupported_removal_claim_fails(tmp_path: Path) -> None:
    """A verdict asserting report removal of a path with no such statement fails."""
    _mark_project_root(tmp_path)
    _write_op(
        tmp_path,
        "bridge/foo-001.md",
        [
            "REVISED",
            "## Files Changed",
            "- `scripts/helper.py` (modified)",
            "No bridge files were removed.",
        ],
    )
    verdict = _verdict(
        "F1: the report promised removal of `scripts/per_thread_finalization_repair.py`.",
        reviewed="bridge/foo-001.md",
    )
    violations = validate_verdict_evidence_anchors(verdict, project_root=tmp_path)
    assert "unsupported_removal_claim" in _kinds(violations)


def test_supported_removal_claim_passes(tmp_path: Path) -> None:
    """A verdict grounded in a real positive same-path removal statement passes."""
    _mark_project_root(tmp_path)
    _write_op(
        tmp_path,
        "bridge/foo-001.md",
        [
            "REVISED",
            "## Files Changed",
            "- `scripts/per_thread_finalization_repair.py` (removed)",
        ],
    )
    verdict = _verdict(
        "F1: the report claimed removal of `scripts/per_thread_finalization_repair.py`.",
        reviewed="bridge/foo-001.md",
    )
    violations = validate_verdict_evidence_anchors(verdict, project_root=tmp_path)
    assert "unsupported_removal_claim" not in _kinds(violations)


def test_removal_assertion_without_operative_header_is_not_flagged(tmp_path: Path) -> None:
    """No operative document header means no WI-5437 removal-claim check."""
    _mark_project_root(tmp_path)
    verdict = _verdict(
        "F1: the report promised removal of `scripts/helper.py`.",
        reviewed=None,
    )
    violations = validate_verdict_evidence_anchors(verdict, project_root=tmp_path)
    assert "unsupported_removal_claim" not in _kinds(violations)
