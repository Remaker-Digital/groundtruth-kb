"""FAB-14 (WI-4426) HYG-047: narrative-approval-gate deterministic packet auto-discovery.

Asserts the gate can locate an owner-approved on-disk packet that matches the
exact write (target_path + content sha256) without an env var, and that it
rejects mismatches. Authority: DCL-ARTIFACT-APPROVAL-HOOK-001 (amended),
GOV-ARTIFACT-APPROVAL-001, DELIB-FAB14-REMEDIATION-20260610.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_HOOK = _ROOT / ".claude" / "hooks" / "narrative-artifact-approval-gate.py"
_spec = importlib.util.spec_from_file_location("_fab14_narrative_gate", _HOOK)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def _write_packet(approvals: Path, name: str, target_path: str, content: str) -> None:
    approvals.mkdir(parents=True, exist_ok=True)
    pkt = {
        "artifact_type": "narrative_artifact",
        "artifact_id": "RULE-FOO",
        "action": "edit",
        "target_path": target_path,
        "source_ref": "fab-14 test",
        "full_content": content,
        "full_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "test",
        "changed_by": "test",
        "change_reason": "fab14",
        "approved_by": "owner",
    }
    (approvals / name).write_text(json.dumps(pkt), encoding="utf-8")


def test_autodiscover_finds_matching_packet(tmp_path):
    content = "rule body v2\n"
    _write_packet(tmp_path / ".groundtruth" / "formal-artifact-approvals", "p1.json", ".claude/rules/foo.md", content)
    assert gate._autodiscover_packet(tmp_path, ".claude/rules/foo.md", content) is not None


def test_autodiscover_rejects_content_mismatch(tmp_path):
    _write_packet(tmp_path / ".groundtruth" / "formal-artifact-approvals", "p1.json", ".claude/rules/foo.md", "right\n")
    assert gate._autodiscover_packet(tmp_path, ".claude/rules/foo.md", "WRONG\n") is None


def test_autodiscover_rejects_path_mismatch(tmp_path):
    content = "rule body\n"
    _write_packet(tmp_path / ".groundtruth" / "formal-artifact-approvals", "p1.json", ".claude/rules/foo.md", content)
    assert gate._autodiscover_packet(tmp_path, ".claude/rules/bar.md", content) is None


def test_autodiscover_none_for_contentless_edit(tmp_path):
    assert gate._autodiscover_packet(tmp_path, ".claude/rules/foo.md", None) is None


def test_autodiscover_none_when_no_approvals_dir(tmp_path):
    assert gate._autodiscover_packet(tmp_path, ".claude/rules/foo.md", "x\n") is None


# --- WI-5509: _reconstruct_edit_content unit coverage ----------------------


def test_reconstruct_edit_content_unique_replacement(tmp_path):
    """A unique old_string is replaced once to reconstruct post-edit content."""
    target = tmp_path / "rule.md"
    target.write_text("hello world\n", encoding="utf-8")
    result = gate._reconstruct_edit_content(str(target), {"old_string": "world", "new_string": "there"})
    assert result == "hello there\n"


def test_reconstruct_edit_content_replace_all(tmp_path):
    """replace_all replaces every occurrence of old_string."""
    target = tmp_path / "rule.md"
    target.write_text("a b a b\n", encoding="utf-8")
    result = gate._reconstruct_edit_content(str(target), {"old_string": "a", "new_string": "X", "replace_all": True})
    assert result == "X b X b\n"


def test_reconstruct_edit_content_absent_old_text_returns_none(tmp_path):
    """old_string absent from the file fails closed (None)."""
    target = tmp_path / "rule.md"
    target.write_text("hello\n", encoding="utf-8")
    result = gate._reconstruct_edit_content(str(target), {"old_string": "nope", "new_string": "x"})
    assert result is None


def test_reconstruct_edit_content_ambiguous_without_replace_all_returns_none(tmp_path):
    """Repeated old_string without replace_all is ambiguous -> None."""
    target = tmp_path / "rule.md"
    target.write_text("dup dup\n", encoding="utf-8")
    result = gate._reconstruct_edit_content(str(target), {"old_string": "dup", "new_string": "x"})
    assert result is None


def test_reconstruct_edit_content_missing_or_nonstring_operands_returns_none(tmp_path):
    """Missing / non-string old_string or new_string fails closed (None)."""
    target = tmp_path / "rule.md"
    target.write_text("hello\n", encoding="utf-8")
    assert gate._reconstruct_edit_content(str(target), {"old_string": "", "new_string": "x"}) is None
    assert gate._reconstruct_edit_content(str(target), {"old_string": "hello", "new_string": 5}) is None
    assert gate._reconstruct_edit_content(str(target), {"new_string": "x"}) is None


def test_reconstruct_edit_content_missing_target_returns_none(tmp_path):
    """An unreadable / missing target file fails closed (None)."""
    missing = tmp_path / "does-not-exist.md"
    result = gate._reconstruct_edit_content(str(missing), {"old_string": "x", "new_string": "y"})
    assert result is None
