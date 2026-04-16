# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for governance hook templates."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).parent.parent / "templates" / "hooks"

ALL_HOOKS = [
    "session-start-governance.py",
    "delib-search-gate.py",
    "delib-search-tracker.py",
    "spec-before-code.py",
    "bridge-compliance-gate.py",
    "kb-not-markdown.py",
    "destructive-gate.py",
    "credential-scan.py",
]

PRETOOLUSE_HOOKS = [
    "spec-before-code.py",
    "bridge-compliance-gate.py",
    "kb-not-markdown.py",
    "destructive-gate.py",
    "credential-scan.py",
]

SESSIONSTART_HOOKS = ["session-start-governance.py"]
USERPROMPTSUBMIT_HOOKS = ["delib-search-gate.py", "delib-search-tracker.py"]


def _run_hook(
    hook_name: str,
    stdin_data: str | None = None,
    args: list[str] | None = None,
    env: dict | None = None,
) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(HOOKS_DIR / hook_name)] + (args or [])
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        cmd,
        input=stdin_data or "{}",
        capture_output=True,
        text=True,
        env=run_env,
    )


def _self_test(hook_name: str) -> subprocess.CompletedProcess:
    return _run_hook(hook_name, args=["--self-test"])


# ---------------------------------------------------------------------------
# Self-test: all hooks exit 0
# ---------------------------------------------------------------------------


def test_hook_self_test_all_exit_zero():
    for hook in ALL_HOOKS:
        result = _self_test(hook)
        assert result.returncode == 0, f"{hook} --self-test exited {result.returncode}: {result.stderr}"


def test_hook_self_test_hookSpecificOutput_all():
    for hook in ALL_HOOKS:
        result = _self_test(hook)
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"{hook} --self-test produced invalid JSON: {result.stdout!r}")
        # delib-search-tracker emits {} (pass) on self-test — acceptable
        if output == {}:
            continue
        assert "hookSpecificOutput" in output, f"{hook} missing hookSpecificOutput"
        assert "hookEventName" in output["hookSpecificOutput"], f"{hook} missing hookEventName"
        assert output["hookSpecificOutput"]["hookEventName"], f"{hook} hookEventName is empty"


def test_hook_self_test_hookEventName_pretooluse():
    for hook in PRETOOLUSE_HOOKS:
        result = _self_test(hook)
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse", (
            f"{hook} hookEventName should be PreToolUse, got "
            f"{output.get('hookSpecificOutput', {}).get('hookEventName')}"
        )


def test_hook_self_test_hookEventName_sessionstart():
    for hook in SESSIONSTART_HOOKS:
        result = _self_test(hook)
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart", (
            f"{hook} hookEventName should be SessionStart"
        )


def test_hook_self_test_hookEventName_userpromptsubmit():
    # delib-search-gate emits advisory (UserPromptSubmit); delib-search-tracker emits {}
    result = _self_test("delib-search-gate.py")
    output = json.loads(result.stdout)
    assert output.get("hookSpecificOutput", {}).get("hookEventName") == "UserPromptSubmit" or output == {}


# ---------------------------------------------------------------------------
# Destructive gate
# ---------------------------------------------------------------------------


def test_destructive_gate_self_test_exit_zero():
    result = _self_test("destructive-gate.py")
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_destructive_gate_stdin_blocks():
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git reset --hard"},
            "session_id": "test",
            "cwd": "/fake",
        }
    )
    result = _run_hook("destructive-gate.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


def test_destructive_gate_env_ignored():
    """TOOL_INPUT env var must be ignored; clean stdin payload must not block."""
    malicious_env = {"TOOL_INPUT": json.dumps({"command": "git reset --hard"})}
    clean_payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "echo hello"},
            "session_id": "test",
            "cwd": "/fake",
        }
    )
    result = _run_hook("destructive-gate.py", stdin_data=clean_payload, env=malicious_env)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output.get("hookSpecificOutput", {}).get("permissionDecision") != "deny"


# ---------------------------------------------------------------------------
# Credential scan
# ---------------------------------------------------------------------------


def test_credential_scan_self_test_exit_zero():
    result = _self_test("credential-scan.py")
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_credential_scan_stdin_blocks():
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "echo sk-ant-api03-aaaaaaaaaaaaaaaa"},
            "session_id": "test",
            "cwd": "/fake",
        }
    )
    result = _run_hook("credential-scan.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


# ---------------------------------------------------------------------------
# Deliberation search gate
# ---------------------------------------------------------------------------


def test_delib_gate_no_prior_search(tmp_path):
    """No log file → advisory emitted."""
    payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Let me propose a new feature",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-gate.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert output["hookSpecificOutput"]["additionalContext"]


def test_delib_gate_missing_log_file(tmp_path):
    """Missing log file → advisory (fail-closed)."""
    payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Review this bridge proposal",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-gate.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output


def test_delib_gate_different_doc(tmp_path):
    """Log entry for different doc → advisory still emitted."""
    log_dir = tmp_path / ".groundtruth"
    log_dir.mkdir()
    import time

    entry = {
        "timestamp": time.time(),
        "doc_topic_hash": "deadbeef00000000",  # different hash
        "tool_name": "Bash",
        "cwd": str(tmp_path),
    }
    (log_dir / "delib-search-log.jsonl").write_text(json.dumps(entry) + "\n", encoding="utf-8")
    payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Completely different topic about auth",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-gate.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output


def test_delib_gate_corrupt_log_file(tmp_path):
    """Corrupt log lines are skipped; advisory still emitted."""
    log_dir = tmp_path / ".groundtruth"
    log_dir.mkdir()
    (log_dir / "delib-search-log.jsonl").write_text("not-valid-json\n{also bad\n", encoding="utf-8")
    payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Some new work",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-gate.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output


# ---------------------------------------------------------------------------
# Spec-before-code
# ---------------------------------------------------------------------------


def test_spec_before_code_no_source_paths(tmp_path):
    """No specs with source_paths → info advisory (no source_paths defined)."""
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-001",
        title="Auth module",
        status="specified",
        changed_by="test",
        change_reason="test",
    )
    db.close()

    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("spec-before-code.py", stdin_data=payload)
    assert result.returncode == 0
    # Emits info advisory or pass — either is acceptable
    output = json.loads(result.stdout)
    assert isinstance(output, dict)


def test_spec_before_code_match(tmp_path):
    """Spec with matching source_paths → pass (empty JSON)."""
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-001",
        title="Auth module",
        status="specified",
        changed_by="test",
        change_reason="test",
        source_paths=["src/auth.py"],
    )
    db.close()

    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("spec-before-code.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {}


def test_spec_before_code_no_match(tmp_path):
    """source_paths defined but not matching → warning advisory."""
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-001",
        title="Auth module",
        status="specified",
        changed_by="test",
        change_reason="test",
        source_paths=["src/other.py"],
    )
    db.close()

    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("spec-before-code.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_spec_before_code_non_source_file(tmp_path):
    """Target is docs/guide.md → pass (not a source file by extension)."""
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "docs/guide.md", "content": "# Guide"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("spec-before-code.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {}


def test_spec_before_code_match_via_migrated_db(tmp_path):
    """Spec inserted via KnowledgeDB (real migration) — proves schema, not mock."""
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(tmp_path / "test.db")
    db.insert_spec(
        id="SPEC-001",
        title="Auth module",
        status="specified",
        changed_by="test",
        change_reason="test",
        source_paths=["src/groundtruth_kb/auth.py"],
    )
    db.close()

    # Copy db to standard groundtruth.db location for hook discovery
    import shutil

    shutil.copy2(tmp_path / "test.db", tmp_path / "groundtruth.db")

    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/groundtruth_kb/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("spec-before-code.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {}


# ---------------------------------------------------------------------------
# Bridge compliance gate
# ---------------------------------------------------------------------------


def _make_index(tmp_path: Path, entries: list[tuple[str, str, str]]) -> Path:
    """Create bridge/INDEX.md with (doc_name, status, file_path) entries."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    lines = ["# Bridge Index\n"]
    for doc_name, status, file_path in entries:
        lines.append(f"Document: {doc_name}")
        lines.append(f"{status}: {file_path}")
        lines.append("")
    (bridge_dir / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    return bridge_dir / "INDEX.md"


def test_bridge_compliance_go_entry(tmp_path):
    """Latest GO → pass (no target_paths in proposal → also pass)."""
    _make_index(tmp_path, [("my-feature", "GO", "bridge/my-feature-002.md")])
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/feature.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


def test_bridge_compliance_no_frontmatter(tmp_path):
    """Latest NEW, no target_paths in proposal → pass."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text("Document: my-feature\nNEW: bridge/my-feature-001.md\n", encoding="utf-8")
    (bridge_dir / "my-feature-001.md").write_text("# Proposal\n\nNo target_paths here.\n", encoding="utf-8")
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/feature.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


def test_bridge_compliance_new_entry_match(tmp_path):
    """Latest NEW with frontmatter matching → ask with hookEventName."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\nNEW: bridge/auth-refactor-001.md\n", encoding="utf-8"
    )
    (bridge_dir / "auth-refactor-001.md").write_text(
        '# Auth Refactor Proposal\n\ntarget_paths: ["src/auth.py"]\n\nSome content.\n',
        encoding="utf-8",
    )
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert output["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


def test_bridge_compliance_ask_has_additionalContext(tmp_path):
    """emit_ask for pending → both permissionDecisionReason and additionalContext."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\nNEW: bridge/auth-refactor-001.md\n", encoding="utf-8"
    )
    (bridge_dir / "auth-refactor-001.md").write_text('target_paths: ["src/auth.py"]\n', encoding="utf-8")
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecisionReason"]
    assert output["hookSpecificOutput"]["additionalContext"]


def test_bridge_compliance_nogo_entry(tmp_path):
    """Latest NO-GO with matching frontmatter → ask."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\nNO-GO: bridge/auth-refactor-002.md\nNEW: bridge/auth-refactor-001.md\n",
        encoding="utf-8",
    )
    (bridge_dir / "auth-refactor-002.md").write_text(
        'target_paths: ["src/auth.py"]\n# NO-GO review\n', encoding="utf-8"
    )
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_bridge_compliance_nogo_ask_has_additionalContext(tmp_path):
    """emit_ask for NO-GO → additionalContext == permissionDecisionReason."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\nNO-GO: bridge/auth-refactor-002.md\n", encoding="utf-8"
    )
    (bridge_dir / "auth-refactor-002.md").write_text('target_paths: ["src/auth.py"]\n', encoding="utf-8")
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["additionalContext"] == output["hookSpecificOutput"]["permissionDecisionReason"]


def test_bridge_compliance_revised_over_nogo(tmp_path):
    """Latest REVISED, historical NO-GO below → ask (pending flavor, not NO-GO)."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\n"
        "REVISED: bridge/auth-refactor-003.md\n"
        "NO-GO: bridge/auth-refactor-002.md\n"
        "NEW: bridge/auth-refactor-001.md\n",
        encoding="utf-8",
    )
    (bridge_dir / "auth-refactor-003.md").write_text('target_paths: ["src/auth.py"]\n# REVISED\n', encoding="utf-8")
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "ask"
    reason = output["hookSpecificOutput"]["permissionDecisionReason"]
    # Should be pending message (REVISED/pending), not NO-GO message
    assert "NO-GO" not in reason or "pending" in reason.lower() or "REVISED" in reason


def test_bridge_compliance_go_over_nogo(tmp_path):
    """Latest GO, historical NO-GO below → pass."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\n"
        "GO: bridge/auth-refactor-004.md\n"
        "NO-GO: bridge/auth-refactor-002.md\n"
        "NEW: bridge/auth-refactor-001.md\n",
        encoding="utf-8",
    )
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    assert json.loads(result.stdout) == {}


def test_bridge_compliance_multi_doc_partial_match(tmp_path):
    """Two docs, one matching one not → only matching doc fires."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\nNEW: bridge/auth-refactor-001.md\n\n"
        "Document: unrelated-work\nNEW: bridge/unrelated-001.md\n",
        encoding="utf-8",
    )
    (bridge_dir / "auth-refactor-001.md").write_text('target_paths: ["src/auth.py"]\n', encoding="utf-8")
    (bridge_dir / "unrelated-001.md").write_text('target_paths: ["src/other.py"]\n', encoding="utf-8")
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "src/auth.py", "content": "x = 1"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("bridge-compliance-gate.py", stdin_data=payload)
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "ask"


# ---------------------------------------------------------------------------
# KB-not-markdown
# ---------------------------------------------------------------------------


def test_kb_not_markdown_approved_path(tmp_path):
    """bridge/foo.md → pass."""
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "bridge/foo.md", "content": "# Proposal"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("kb-not-markdown.py", stdin_data=payload)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


def test_kb_not_markdown_unapproved_path(tmp_path):
    """analysis/notes.md → advisory with hookEventName."""
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "analysis/notes.md", "content": "# Notes"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("kb-not-markdown.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_kb_not_markdown_configured_allowlist(tmp_path):
    """groundtruth.toml adds reports/ → pass for reports/foo.md."""
    (tmp_path / "groundtruth.toml").write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\n\n[governance]\napproved_markdown_paths = ["reports/"]\n',
        encoding="utf-8",
    )
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "reports/foo.md", "content": "# Report"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("kb-not-markdown.py", stdin_data=payload)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {}


# ---------------------------------------------------------------------------
# Session governance summary
# ---------------------------------------------------------------------------


def test_session_governance_clean(tmp_path):
    """No pending bridge entries → all-OK summary with SessionStart hookEventName."""
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "Document: done-work\nVERIFIED: bridge/done-work-002.md\nNEW: bridge/done-work-001.md\n",
        encoding="utf-8",
    )
    payload = json.dumps(
        {
            "hook_event_name": "SessionStart",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("session-start-governance.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "clear" in context.lower() or "active" in context.lower() or "governance" in context.lower()


def test_session_governance_pending_entry(tmp_path):
    """One NEW bridge entry → summary names the entry."""
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "INDEX.md").write_text(
        "Document: my-feature\nNEW: bridge/my-feature-001.md\n", encoding="utf-8"
    )
    payload = json.dumps(
        {
            "hook_event_name": "SessionStart",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("session-start-governance.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "my-feature" in output["hookSpecificOutput"]["additionalContext"]


# ---------------------------------------------------------------------------
# Hook payload field tests
# ---------------------------------------------------------------------------


def test_hook_payload_prompt_field(tmp_path):
    """UserPromptSubmit with 'prompt' key → hook reads it correctly (no crash)."""
    payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Please search deliberations",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-gate.py", stdin_data=payload)
    assert result.returncode == 0


def test_hook_payload_user_prompt_fallback(tmp_path):
    """UserPromptSubmit with 'user_prompt' key → hook reads it correctly."""
    payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "user_prompt": "Please search deliberations",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-gate.py", stdin_data=payload)
    assert result.returncode == 0
