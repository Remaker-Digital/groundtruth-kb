"""Unit tests for .claude/skills/bridge/helpers/scan_bridge.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = PROJECT_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "scan_bridge.py"


def _load_helper():
    import sys

    spec = importlib.util.spec_from_file_location("scan_bridge", HELPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["scan_bridge"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def helper():
    return _load_helper()


def test_t1_empty_index_yields_empty_actionable(helper) -> None:
    result = helper.scan(role="prime-builder", index_text="")
    assert result["actionable"] == []
    assert result["terminal_verified"] == []
    assert result["summary"] == {}
    assert result["role"] == "prime-builder"


def test_t2_latest_new_actionable_for_lo_not_prime(helper) -> None:
    index = """\
Document: gtkb-foo
NEW: bridge/gtkb-foo-001.md
"""
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    prime_result = helper.scan(role="prime-builder", index_text=index)
    assert len(lo_result["actionable"]) == 1
    assert lo_result["actionable"][0]["document"] == "gtkb-foo"
    assert lo_result["actionable"][0]["latest_status"] == "NEW"
    assert prime_result["actionable"] == []


def test_t3_latest_go_actionable_for_prime_not_lo(helper) -> None:
    index = """\
Document: gtkb-foo
GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(prime_result["actionable"]) == 1
    assert prime_result["actionable"][0]["latest_status"] == "GO"
    assert lo_result["actionable"] == []


def test_t4_latest_nogo_actionable_for_prime_not_lo(helper) -> None:
    index = """\
Document: gtkb-foo
NO-GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(prime_result["actionable"]) == 1
    assert prime_result["actionable"][0]["latest_status"] == "NO-GO"
    assert lo_result["actionable"] == []


def test_t5_latest_revised_actionable_for_lo_not_prime(helper) -> None:
    index = """\
Document: gtkb-foo
REVISED: bridge/gtkb-foo-003.md
NO-GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    prime_result = helper.scan(role="prime-builder", index_text=index)
    assert len(lo_result["actionable"]) == 1
    assert lo_result["actionable"][0]["latest_status"] == "REVISED"
    assert prime_result["actionable"] == []


def test_t6_latest_verified_in_terminal_not_actionable(helper) -> None:
    index = """\
Document: gtkb-foo
VERIFIED: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    for role in ("prime-builder", "loyal-opposition"):
        result = helper.scan(role=role, index_text=index)
        assert result["actionable"] == []
        assert len(result["terminal_verified"]) == 1
        assert result["terminal_verified"][0]["latest_status"] == "VERIFIED"


def test_t7_mixed_index_partitions_correctly(helper) -> None:
    index = """\
Document: gtkb-a
GO: bridge/gtkb-a-002.md
NEW: bridge/gtkb-a-001.md

Document: gtkb-b
NEW: bridge/gtkb-b-001.md

Document: gtkb-c
VERIFIED: bridge/gtkb-c-003.md
GO: bridge/gtkb-c-002.md
NEW: bridge/gtkb-c-001.md

Document: gtkb-d
NO-GO: bridge/gtkb-d-002.md
NEW: bridge/gtkb-d-001.md

Document: gtkb-e
REVISED: bridge/gtkb-e-003.md
NO-GO: bridge/gtkb-e-002.md
NEW: bridge/gtkb-e-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)

    prime_docs = {t["document"] for t in prime_result["actionable"]}
    lo_docs = {t["document"] for t in lo_result["actionable"]}

    assert prime_docs == {"gtkb-a", "gtkb-d"}  # GO + NO-GO
    assert lo_docs == {"gtkb-b", "gtkb-e"}  # NEW + REVISED

    assert {t["document"] for t in prime_result["terminal_verified"]} == {"gtkb-c"}
    assert prime_result["summary"] == {"GO": 1, "NEW": 1, "VERIFIED": 1, "NO-GO": 1, "REVISED": 1}


def test_t8_comment_header_skipped(helper) -> None:
    index = """\
# Bridge Index

<!-- Prime inserts new document entries at the top of the list below. -->
<!-- Codex scans for NEW/REVISED statuses and adds GO/NO-GO/VERIFIED versions. -->

Document: gtkb-foo
NEW: bridge/gtkb-foo-001.md
"""
    result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(result["actionable"]) == 1
    assert result["actionable"][0]["document"] == "gtkb-foo"


def test_invalid_role_raises(helper) -> None:
    with pytest.raises(ValueError):
        helper.scan(role="other", index_text="")


def test_version_chain_preserves_order(helper) -> None:
    """Version chain reports versions latest-first per INDEX convention."""
    index = """\
Document: gtkb-foo
REVISED: bridge/gtkb-foo-005.md
NO-GO: bridge/gtkb-foo-004.md
REVISED: bridge/gtkb-foo-003.md
NO-GO: bridge/gtkb-foo-002.md
NEW: bridge/gtkb-foo-001.md
"""
    result = helper.scan(role="loyal-opposition", index_text=index)
    chain = result["actionable"][0]["version_chain"]
    assert [v["status"] for v in chain] == ["REVISED", "NO-GO", "REVISED", "NO-GO", "NEW"]
    assert chain[0]["path"] == "bridge/gtkb-foo-005.md"


def test_generated_at_iso_format(helper) -> None:
    result = helper.scan(role="prime-builder", index_text="")
    assert result["generated_at"].endswith("Z")
    assert "T" in result["generated_at"]


# --- Terminal-kind GO filtering (WI-4278; gtkb-manual-bridge-scan-terminal-go-filter) ---


def _write_bridge_thread(bridge_dir: Path, slug: str, operative_kind: str, latest_status: str) -> None:
    """Write the operative Prime proposal file for a thread.

    Only the operative (NEW) file needs to exist; classification reads
    ``bridge_kind`` from the operative Prime version, not the verdict file.
    """
    operative = bridge_dir / f"{slug}-001.md"
    operative.write_text(
        f"NEW\n\nbridge_kind: {operative_kind}\nDocument: {slug}\nVersion: 001\n",
        encoding="utf-8",
    )


def test_terminal_kind_go_excluded_from_prime(helper, tmp_path) -> None:
    """A latest GO with terminal-kind bridge_kind is excluded from Prime work,
    while a non-terminal GO and a terminal-kind NO-GO are preserved."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge_thread(bridge_dir, "gtkb-gov", "governance_review", "GO")
    _write_bridge_thread(bridge_dir, "gtkb-impl", "implementation_proposal", "GO")
    _write_bridge_thread(bridge_dir, "gtkb-gov-nogo", "governance_review", "NO-GO")
    index = (
        "Document: gtkb-gov\n"
        "GO: bridge/gtkb-gov-002.md\n"
        "NEW: bridge/gtkb-gov-001.md\n"
        "\n"
        "Document: gtkb-impl\n"
        "GO: bridge/gtkb-impl-002.md\n"
        "NEW: bridge/gtkb-impl-001.md\n"
        "\n"
        "Document: gtkb-gov-nogo\n"
        "NO-GO: bridge/gtkb-gov-nogo-002.md\n"
        "NEW: bridge/gtkb-gov-nogo-001.md\n"
    )
    index_path = bridge_dir / "INDEX.md"
    index_path.write_text(index, encoding="utf-8")

    prime = helper.scan(role="prime-builder", index_text=index, index_path=index_path)
    prime_docs = {t["document"] for t in prime["actionable"]}

    # Terminal-kind GO excluded; non-terminal GO and terminal-kind NO-GO kept.
    assert prime_docs == {"gtkb-impl", "gtkb-gov-nogo"}
    assert "gtkb-gov" not in prime_docs


def test_terminal_kind_does_not_affect_lo(helper, tmp_path) -> None:
    """Loyal Opposition actionability (NEW/REVISED) is unaffected by kind."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    _write_bridge_thread(bridge_dir, "gtkb-gov", "governance_review", "NEW")
    index = "Document: gtkb-gov\nNEW: bridge/gtkb-gov-001.md\n"
    index_path = bridge_dir / "INDEX.md"
    index_path.write_text(index, encoding="utf-8")

    lo = helper.scan(role="loyal-opposition", index_text=index, index_path=index_path)
    assert {t["document"] for t in lo["actionable"]} == {"gtkb-gov"}


def test_unreadable_operative_go_stays_actionable(helper, tmp_path) -> None:
    """Fail-open: a GO whose operative file is missing stays Prime-actionable."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    # No operative file written -> classification fails open to actionable.
    index = "Document: gtkb-ghost\nGO: bridge/gtkb-ghost-002.md\nNEW: bridge/gtkb-ghost-001.md\n"
    index_path = bridge_dir / "INDEX.md"
    index_path.write_text(index, encoding="utf-8")

    prime = helper.scan(role="prime-builder", index_text=index, index_path=index_path)
    assert {t["document"] for t in prime["actionable"]} == {"gtkb-ghost"}


def test_terminal_tokens_parity_with_canonical_notify(helper) -> None:
    """The mirrored terminal-token set must match the canonical notify set to
    prevent classifier drift."""
    from groundtruth_kb.bridge import notify

    assert set(helper._KIND_TERMINAL_TOKENS) == set(notify._KIND_TERMINAL_TOKENS)


def test_advisory_actionable_for_prime_not_lo(helper) -> None:
    """ADVISORY status entries surface in the Prime actionable list (so manual
    `/bridge` scans show them for owner-deliberation/UAQ disposition) but never
    surface for Loyal Opposition. Per gtkb-advisory-prime-actionability-
    surfacing-002 (Codex GO 2026-06-14) Condition 1.
    """
    index = """\
Document: gtkb-foo-advisory
ADVISORY: bridge/gtkb-foo-advisory-001.md
"""
    prime_result = helper.scan(role="prime-builder", index_text=index)
    lo_result = helper.scan(role="loyal-opposition", index_text=index)
    assert len(prime_result["actionable"]) == 1
    assert prime_result["actionable"][0]["document"] == "gtkb-foo-advisory"
    assert prime_result["actionable"][0]["latest_status"] == "ADVISORY"
    assert lo_result["actionable"] == []
