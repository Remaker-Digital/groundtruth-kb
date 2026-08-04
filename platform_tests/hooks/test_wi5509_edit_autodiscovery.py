"""WI-5509: hook-level Edit payload autodiscovery coverage.

Proves that a governed narrative-artifact packet matching the exact
reconstructed post-edit content allows an Edit call without an environment
packet reference, while a mismatched packet and an ambiguous Edit both block.
Fixtures use a temporary project root and never write packet records into the
live repository.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOK = _REPO_ROOT / ".claude" / "hooks" / "narrative-artifact-approval-gate.py"


def _run_hook(payload: dict, cwd: Path | None = None) -> dict:
    result = subprocess.run(
        ["python", str(_HOOK)],
        cwd=cwd or _REPO_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _write_packet(approvals: Path, name: str, target_path: str, content: str) -> Path:
    approvals.mkdir(parents=True, exist_ok=True)
    pkt = {
        "artifact_type": "narrative_artifact",
        "artifact_id": "RULE-FOO",
        "action": "edit",
        "target_path": target_path,
        "source_ref": "bridge/gtkb-wi5509-test-fixture-001.md",
        "full_content": content,
        "full_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "test",
        "changed_by": "test",
        "change_reason": "wi5509 fixture",
        "approved_by": "owner",
    }
    path = approvals / name
    path.write_text(json.dumps(pkt), encoding="utf-8")
    return path


@pytest.fixture
def fake_root(tmp_path: Path) -> Path:
    root = tmp_path / "gtkb"
    root.mkdir()
    (root / ".groundtruth").mkdir(parents=True, exist_ok=True)
    # Provide the canonical approval-gate config so _is_protected resolves the
    # .claude/rules/*.md protected family within the isolated fixture root.
    cfg = root / "config" / "governance"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "narrative-artifact-approval.toml").write_text(
        (_REPO_ROOT / "config" / "governance" / "narrative-artifact-approval.toml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return root


def _edit_payload(file_path: Path, old_string: str, new_string: str, replace_all: bool = False) -> dict:
    tool_input = {
        "file_path": str(file_path),
        "old_string": old_string,
        "new_string": new_string,
    }
    if replace_all:
        tool_input["replace_all"] = True
    return {"tool_name": "Edit", "tool_input": tool_input}


def test_edit_allowed_with_matching_packet(fake_root: Path) -> None:
    """An Edit whose reconstructed post-edit content matches a packet allows."""
    # The protected path must be under the rule-governance family for the hook.
    target = fake_root / ".claude" / "rules" / "foo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("hello world\n", encoding="utf-8")
    post_edit = "hello there\n"
    _write_packet(
        fake_root / ".groundtruth" / "formal-artifact-approvals",
        "p1.json",
        ".claude/rules/foo.md",
        post_edit,
    )
    result = _run_hook(
        _edit_payload(target, "world", "there"),
        cwd=fake_root,
    )
    # A pass emits an empty object (no block decision).
    assert result.get("decision") is None, f"expected pass, got {result}"


def test_edit_blocked_with_mismatched_packet(fake_root: Path) -> None:
    """An Edit whose reconstructed content mismatches the packet blocks."""
    target = fake_root / ".claude" / "rules" / "foo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("hello world\n", encoding="utf-8")
    # Packet is for different post-edit content.
    _write_packet(
        fake_root / ".groundtruth" / "formal-artifact-approvals",
        "p1.json",
        ".claude/rules/foo.md",
        "different content\n",
    )
    result = _run_hook(
        _edit_payload(target, "world", "there"),
        cwd=fake_root,
    )
    assert result.get("decision") == "block", f"expected block, got {result}"


def test_edit_blocked_when_ambiguous(fake_root: Path) -> None:
    """An ambiguous Edit (repeated old_string without replace_all) blocks."""
    target = fake_root / ".claude" / "rules" / "foo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("dup dup\n", encoding="utf-8")
    # Even a matching packet must not allow an ambiguous reconstruction.
    _write_packet(
        fake_root / ".groundtruth" / "formal-artifact-approvals",
        "p1.json",
        ".claude/rules/foo.md",
        "x dup\n",
    )
    result = _run_hook(
        _edit_payload(target, "dup", "x"),
        cwd=fake_root,
    )
    assert result.get("decision") == "block", f"expected block, got {result}"


def test_edit_leave_live_approval_dir_unchanged(fake_root: Path) -> None:
    """Hook-level Edit fixtures do not write records into the live repository."""
    live_approvals = _REPO_ROOT / ".groundtruth" / "formal-artifact-approvals"
    before = set()
    if live_approvals.is_dir():
        before = set(str(p) for p in live_approvals.glob("*.json"))
    target = fake_root / ".claude" / "rules" / "foo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("hello world\n", encoding="utf-8")
    _write_packet(
        fake_root / ".groundtruth" / "formal-artifact-approvals",
        "p1.json",
        ".claude/rules/foo.md",
        "hello there\n",
    )
    _run_hook(_edit_payload(target, "world", "there"), cwd=fake_root)
    after = set()
    if live_approvals.is_dir():
        after = set(str(p) for p in live_approvals.glob("*.json"))
    assert after == before, "live approval directory changed"
