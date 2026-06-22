# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the WI-4520 verdict-evidence-anchor preflight.

Covers the spec-derived verification plan of
bridge/gtkb-antigravity-lo-hallucination-prevention-005.md, as implemented under
the operative-file-scoped, false-positive-hardened design documented in the
post-implementation report (0 false positives across the real verdict corpus):

Unit (reusable module):
  1. Valid NO-GO citing a real operative line + real quoted string passes.
  2. Missing operative file fails.
  3. Cited operative line out of range fails.
  4. Hallucinated quoted string (WI-4520 shape: in-range line, absent quote) fails.
  5. Operative path-form normalization (Windows/Unix) resolves to the same file.
  6. [inference] / [no exact anchor] / absence-keyword / [absent] lines skip.
  7. Multi-line explicit range within bounds passes; out of bounds fails.
  Plus operative-scoping invariants: non-operative citations are not checked, a
  bare "line N" without a quote never drives a range check, no operative header
  means no check, and quotes attributed to a named source (not adjacent to a
  bare operative line) are not flagged.

Integration -- governed verdict-writing paths:
  8. scripts.gtkb_bridge_writer.write_bridge_file raises a BridgeError subclass
     on a fabricated anchor and writes on a valid one (helper-routed chokepoint).
  9. The bridge-compliance-gate hook emits a deny reason on a fabricated anchor
     and passes a valid one (proposal-review Write-tool chokepoint).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from scripts.gtkb_bridge_writer import BridgeError, BridgeEvidenceAnchorError, write_bridge_file
from scripts.verdict_evidence_anchor_preflight import (
    build_packet,
    validate_verdict_evidence_anchors,
    verdict_status,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _write_op(tmp_path: Path, rel: str, lines: list[str]) -> None:
    target = tmp_path / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


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


def test_write_bridge_file_blocks_fabricated_nogo(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Implementation Plan", "tail"])
    bad = _verdict("F1: bad citation at `bridge/foo-001.md:99`.")
    with pytest.raises(BridgeEvidenceAnchorError):
        write_bridge_file("nogo-thread", 2, bad, tmp_path, require_author_metadata=False)
    assert not (tmp_path / "bridge" / "nogo-thread-002.md").exists()


def test_write_bridge_file_error_is_bridge_error_subclass() -> None:
    assert issubclass(BridgeEvidenceAnchorError, BridgeError)


def test_write_bridge_file_allows_valid_nogo(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Implementation Plan", "real anchored text"])
    good = _verdict('F1: line 4 reads "real anchored text"; `bridge/foo-001.md:4` is in range.')
    path = write_bridge_file("nogo-thread", 2, good, tmp_path, require_author_metadata=False)
    assert path.exists()


def test_write_bridge_file_allows_non_verdict(tmp_path: Path) -> None:
    # A NEW proposal is not a gated verdict; a forward citation to a proposed
    # (not-yet-created) file:line must not be blocked.
    proposal = "NEW\n\nWill create `scripts/new_module.py:10`.\n"
    path = write_bridge_file("propthing", 1, proposal, tmp_path, require_author_metadata=False)
    assert path.exists()


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


def test_hook_deny_reason_for_content_blocks_fabricated_nogo(tmp_path: Path) -> None:
    _write_op(tmp_path, "bridge/foo-001.md", ["NEW", "", "## Implementation Plan", "tail"])
    hook = _load_hook()
    bad = (
        "NO-GO\n"
        "bridge_kind: lo_verdict\n"
        "Responds to: bridge/foo-001.md\n"
        "\n"
        "F1: fabricated citation at `bridge/foo-001.md:99`.\n"
    )
    reason = hook._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path="bridge/foo-002.md",
        content=bad,
        run_pending_preflight=False,
    )
    assert reason is not None
    assert "evidence anchors" in reason
