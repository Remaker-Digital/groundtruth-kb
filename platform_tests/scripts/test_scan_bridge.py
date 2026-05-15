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
