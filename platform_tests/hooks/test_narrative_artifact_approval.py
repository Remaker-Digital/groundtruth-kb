"""Tests for the narrative-artifact PreToolUse approval gate.

Bridge:    bridge/gtkb-narrative-artifact-approval-extension-001-004.md (GO)
Specs:     GOV-ARTIFACT-APPROVAL-001 (extended), DCL-ARTIFACT-APPROVAL-HOOK-001 (extended)
Slice A of GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001.

Test coverage maps to acceptance criteria from the bridge proposal:
- T-A-pathset:                 path set covers role-and-governance-rules family
- T-A-block-without-packet:    Write to a protected path without packet is blocked
- T-A-allow-with-packet:       Write to a protected path WITH a valid packet allows
- T-A-exception-list:          hook-managed files exempted
- T-A-codex-template-parity:   parity template exists and is byte-equivalent
- T-A-existing-regression:     existing approval-gate suite still passes
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "narrative-artifact-approval-gate.py"
CODEX_TEMPLATE = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "narrative-artifact-approval-gate.py"
CONFIG_PATH = REPO_ROOT / "config" / "governance" / "narrative-artifact-approval.toml"


def _run_hook(payload: dict, env_overrides: dict | None = None, cwd: Path | None = None) -> dict:
    env = None
    if env_overrides is not None:
        import os

        env = os.environ.copy()
        # Strip any leaked approval env vars from the parent shell so the test
        # observes only what we set explicitly.
        for stale in (
            "GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET",
            "GTKB_FORMAL_APPROVAL_PACKET",
        ):
            env.pop(stale, None)
        env.update(env_overrides)
    result = subprocess.run(
        ["python", str(HOOK)],
        cwd=cwd or REPO_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _make_packet(target_path: str, full_content: str, **overrides) -> dict:
    base = {
        "artifact_type": "narrative_artifact",
        "artifact_id": "test-narrative-artifact",
        "action": "update",
        "target_path": target_path,
        "source_ref": "bridge/gtkb-narrative-artifact-approval-extension-001-004.md",
        "full_content": full_content,
        "full_content_sha256": hashlib.sha256(full_content.encode("utf-8")).hexdigest(),
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "Owner verbatim approval text recorded in transcript.",
        "changed_by": "claude/test",
        "change_reason": "test fixture",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# T-A-pathset
# ---------------------------------------------------------------------------


def test_a_pathset_includes_role_governance_family():
    """T-A-pathset: protected_artifacts includes the role-and-governance-rules family
    aligned with config/governance/protected-artifact-inventory-drift.toml."""
    import tomllib

    with CONFIG_PATH.open("rb") as fh:
        config = tomllib.load(fh)
    protected_blocks = config.get("protected_artifacts", [])
    assert protected_blocks, "narrative-artifact-approval.toml has no protected_artifacts blocks"
    patterns: list[str] = []
    for block in protected_blocks:
        patterns.extend(block.get("patterns", []))
    assert ".claude/rules/*.md" in patterns
    assert "AGENTS.md" in patterns
    assert "CLAUDE.md" in patterns
    assert "memory/work_list.md" in patterns

    # Per Codex GO -004 §3 baseline caveat: MEMORY.md and broad memory/*.md must be excluded.
    assert "MEMORY.md" not in patterns
    assert "memory/*.md" not in patterns

    # Per Codex GO -004 §3 baseline caveat: .toml control files are excluded by design.
    assert ".claude/rules/*.toml" not in patterns


# ---------------------------------------------------------------------------
# T-A-block-without-packet
# ---------------------------------------------------------------------------


def test_a_block_protected_path_without_packet(tmp_path):
    """T-A-block-without-packet: Write to .claude/rules/example.md without a packet is blocked."""
    target = REPO_ROOT / ".claude" / "rules" / "example.md"  # not real; path-pattern match only
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(target), "content": "new content\n"},
    }
    result = _run_hook(payload, env_overrides={})
    assert result.get("decision") == "block"
    assert ".claude/rules/example.md" in result.get("reason", "")
    assert "approval packet" in result.get("reason", "").lower()


def test_a_block_agents_md_without_packet():
    """T-A-block-without-packet: AGENTS.md is in the protected set per F2 fix."""
    target = REPO_ROOT / "AGENTS.md"
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(target), "content": "draft AGENTS.md content\n"},
    }
    result = _run_hook(payload, env_overrides={})
    assert result.get("decision") == "block"
    assert "AGENTS.md" in result.get("reason", "")


# ---------------------------------------------------------------------------
# T-A-allow-with-packet
# ---------------------------------------------------------------------------


def test_a_allow_with_valid_packet(tmp_path):
    """T-A-allow-with-packet: a valid approval packet allows the Write."""
    rel_target = ".claude/rules/example.md"
    target = REPO_ROOT / rel_target
    new_content = "new approved content\n"

    packet_path = tmp_path / "packet.json"
    packet = _make_packet(rel_target, new_content)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(target), "content": new_content},
    }
    result = _run_hook(
        payload,
        env_overrides={"GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET": str(packet_path)},
    )
    assert result == {}, f"expected allow (empty dict), got {result!r}"


def test_a_block_with_packet_target_mismatch(tmp_path):
    """A packet for a different target_path must not authorize an unrelated write."""
    rel_target = ".claude/rules/example.md"
    target = REPO_ROOT / rel_target
    new_content = "new content\n"

    # Packet says it's for memory/work_list.md, but the write targets .claude/rules/example.md
    packet_path = tmp_path / "packet.json"
    packet = _make_packet("memory/work_list.md", new_content)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(target), "content": new_content},
    }
    result = _run_hook(
        payload,
        env_overrides={"GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET": str(packet_path)},
    )
    assert result.get("decision") == "block"
    assert "target_path" in result.get("reason", "")


def test_a_block_with_packet_content_mismatch(tmp_path):
    """A packet whose full_content does not match the proposed Write content must block."""
    rel_target = ".claude/rules/example.md"
    target = REPO_ROOT / rel_target
    write_content = "actual write content\n"
    packet_content = "different content the owner approved\n"

    packet_path = tmp_path / "packet.json"
    packet = _make_packet(rel_target, packet_content)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(target), "content": write_content},
    }
    result = _run_hook(
        payload,
        env_overrides={"GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET": str(packet_path)},
    )
    assert result.get("decision") == "block"
    assert "full_content" in result.get("reason", "")


# ---------------------------------------------------------------------------
# T-A-exception-list
# ---------------------------------------------------------------------------


def test_a_hook_managed_pending_decisions_exempted():
    """T-A-exception-list: memory/pending-owner-decisions.md is hook-owned; exempted."""
    target = REPO_ROOT / "memory" / "pending-owner-decisions.md"
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(target), "content": "hook-managed content\n"},
    }
    result = _run_hook(payload, env_overrides={})
    assert result == {}, f"hook-managed exemption should pass, got {result!r}"


def test_a_local_override_files_exempted():
    """T-A-exception-list: .claude/rules/*.local.md files are local overrides; exempted."""
    target = REPO_ROOT / ".claude" / "rules" / "owner.local.md"
    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(target), "content": "local override content\n"},
    }
    result = _run_hook(payload, env_overrides={})
    assert result == {}


# ---------------------------------------------------------------------------
# T-A-non-protected
# ---------------------------------------------------------------------------


def test_a_non_protected_paths_allowed():
    """Paths outside the protected set should pass without an approval packet."""
    for rel in [
        "scripts/some_script.py",
        "tests/hooks/test_x.py",
        "MEMORY.md",  # explicitly excluded per Codex GO -004 answer 2
        ".claude/rules/canonical-terminology.toml",  # excluded per .toml-exclusion design decision
        "memory/feedback_x.md",  # broad memory/*.md excluded per Codex GO -004 answer 2
    ]:
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": str(REPO_ROOT / rel), "content": "x\n"},
        }
        result = _run_hook(payload, env_overrides={})
        assert result == {}, f"path {rel!r} should pass; got {result!r}"


# ---------------------------------------------------------------------------
# T-A-non-write-tool
# ---------------------------------------------------------------------------


def test_a_non_write_tool_passes():
    """Read/Bash/etc. tools should pass through unchanged."""
    payload = {"tool_name": "Read", "tool_input": {"file_path": str(REPO_ROOT / "AGENTS.md")}}
    result = _run_hook(payload, env_overrides={})
    assert result == {}


# ---------------------------------------------------------------------------
# T-A-codex-template-parity
# ---------------------------------------------------------------------------


def test_a_codex_template_parity_exists_and_matches():
    """T-A-codex-template-parity: forward-compatible Codex template exists and is byte-equivalent
    to the live Claude hook (per ADR-CODEX-HOOK-PARITY-FALLBACK-001).

    The template is NOT claimed as a live Windows interception boundary — Codex's `apply_patch`
    does not invoke it on Windows. It is filed for forward compatibility and adopter parity
    when distributed via gt project upgrade.
    """
    assert CODEX_TEMPLATE.exists(), f"Codex template missing at {CODEX_TEMPLATE}"
    claude_bytes = HOOK.read_bytes()
    template_bytes = CODEX_TEMPLATE.read_bytes()
    assert claude_bytes == template_bytes, "Codex template must be byte-equivalent to Claude hook"


def test_a_codex_hooks_json_does_not_claim_narrative_gate_on_windows():
    """Per ADR-CODEX-HOOK-PARITY-FALLBACK-001: .codex/hooks.json must NOT register the
    narrative-artifact-approval-gate.py as a live Codex hook on Windows. Slice A's hook
    is Claude-only; Slice C's pre-commit hook is the universal floor.
    """
    codex_hooks_path = REPO_ROOT / ".codex" / "hooks.json"
    if not codex_hooks_path.exists():
        pytest.skip(".codex/hooks.json not present in this checkout")
    text = codex_hooks_path.read_text(encoding="utf-8")
    assert "narrative-artifact-approval-gate" not in text, (
        ".codex/hooks.json must not register narrative-artifact-approval-gate.py "
        "as a live Codex hook (forward-compatible template only per "
        "ADR-CODEX-HOOK-PARITY-FALLBACK-001)"
    )


# ---------------------------------------------------------------------------
# T-A-self-test
# ---------------------------------------------------------------------------


def test_a_self_test_invocation():
    """The hook supports --self-test and exits cleanly."""
    result = subprocess.run(
        ["python", str(HOOK), "--self-test"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.returncode == 0
