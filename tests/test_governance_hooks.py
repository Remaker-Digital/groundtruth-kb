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
USERPROMPTSUBMIT_HOOKS = ["delib-search-gate.py"]
POSTTOOLUSE_HOOKS = ["delib-search-tracker.py"]


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
# Credential scan: canonical vs. fallback catalog sourcing
# ---------------------------------------------------------------------------
#
# GO ``bridge/gtkb-credential-patterns-canonical-008.md`` Condition 5 requires
# that the hook test asserts which catalog path was used when the hook denied
# a credential sample. The hook writes one of two markers to stderr:
#
#   CANONICAL_CATALOG_USED   — imported groundtruth_kb.governance.credential_patterns
#   FALLBACK_CATALOG_USED    — fell back to the inline catalog
#
# Both modes MUST deny an equivalent credential payload.


def _fallback_isolated_copy(tmp_path: Path) -> Path:
    """Copy credential-scan.py to an isolated directory for fallback-mode runs.

    No sidecar file is copied (per GO-008 Condition 1: fallback is inline).
    """
    import shutil

    isolated = tmp_path / "isolated"
    isolated.mkdir()
    shutil.copy(HOOKS_DIR / "credential-scan.py", isolated / "credential-scan.py")
    return isolated


_CRED_SAMPLE_PAYLOAD = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",
    # Split literal to keep source file scanner-safe; the runtime value is the
    # full sk-ant-api03-<payload> credential string.
    "tool_input": {"command": "echo " + "sk-" + "ant-api" + "03-" + "a" * 16},
    "session_id": "test",
    "cwd": "/fake",
}


def _canonical_env() -> dict[str, str]:
    """Subprocess env that makes the local ``src/`` directory importable.

    pytest injects ``src/`` into ``sys.path`` via
    ``[tool.pytest.ini_options] pythonpath = ["src"]``, but subprocesses
    spawned via ``subprocess.run`` inherit only ``PYTHONPATH``. Without this
    helper the subprocess would import the installed GT-KB wheel (if any)
    instead of the local source, potentially landing on the inline fallback.
    """
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_dir) + (os.pathsep + existing if existing else "")
    return env


def test_credential_scan_canonical_mode_self_test_uses_canonical_catalog():
    """Running the hook with ``groundtruth_kb`` importable must use the canonical
    catalog and must still deny the credential sample.
    """
    result = _run_hook("credential-scan.py", args=["--self-test"], env=_canonical_env())
    assert result.returncode == 0, f"self-test exited {result.returncode}: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny", (
        "Canonical-mode self-test must deny the credential sample"
    )
    assert "CANONICAL_CATALOG_USED" in result.stderr, (
        "Canonical mode must emit CANONICAL_CATALOG_USED marker on stderr. Got stderr: " + repr(result.stderr)
    )
    assert "FALLBACK_CATALOG_USED" not in result.stderr, "Canonical mode must NOT emit fallback marker"


def test_credential_scan_fallback_mode_uses_inline_catalog(tmp_path):
    """Running the hook with ``python -S -I`` in an isolated directory must
    force the inline fallback path (groundtruth_kb unimportable) and still
    deny an equivalent credential sample.
    """
    isolated = _fallback_isolated_copy(tmp_path)
    payload = json.dumps(_CRED_SAMPLE_PAYLOAD)

    # -S: skip site.py (site-packages); -I: isolated mode (also clears
    # PYTHONPATH, PYTHONHOME, user site). Net effect: groundtruth_kb cannot
    # be imported from anywhere.
    result = subprocess.run(
        [sys.executable, "-S", "-I", str(isolated / "credential-scan.py")],
        input=payload,
        capture_output=True,
        text=True,
        cwd=str(isolated),
    )
    assert result.returncode == 0, f"Fallback-mode run exited {result.returncode}: stderr={result.stderr!r}"
    assert "FALLBACK_CATALOG_USED" in result.stderr, (
        "Fallback mode must emit FALLBACK_CATALOG_USED marker on stderr. Got stderr: " + repr(result.stderr)
    )
    assert "CANONICAL_CATALOG_USED" not in result.stderr, (
        "Fallback mode must NOT emit canonical marker — isolation broke"
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.mark.parametrize("mode", ["canonical", "fallback"])
def test_credential_scan_both_modes_deny_same_sample(tmp_path, mode):
    """Parameterized equivalence test: canonical and fallback catalogs must
    deny the same credential sample with the same first-match description.
    """
    payload = json.dumps(_CRED_SAMPLE_PAYLOAD)

    if mode == "canonical":
        result = _run_hook("credential-scan.py", stdin_data=payload, env=_canonical_env())
        expected_marker = "CANONICAL_CATALOG_USED"
    else:
        isolated = _fallback_isolated_copy(tmp_path)
        result = subprocess.run(
            [sys.executable, "-S", "-I", str(isolated / "credential-scan.py")],
            input=payload,
            capture_output=True,
            text=True,
            cwd=str(isolated),
        )
        expected_marker = "FALLBACK_CATALOG_USED"

    assert result.returncode == 0, f"[{mode}] exited {result.returncode}: stderr={result.stderr!r}"
    assert expected_marker in result.stderr, (
        f"[{mode}] missing expected marker {expected_marker!r} on stderr. Got: {result.stderr!r}"
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny", (
        f"[{mode}] expected deny decision, got {output!r}"
    )
    reason = output["hookSpecificOutput"]["permissionDecisionReason"]
    # First-match description must mention Anthropic API key family — both
    # catalogs list it as the second Bash credential entry so the stripe sk-
    # family match earlier in the catalog does not apply to this payload.
    assert "Anthropic" in reason or "sk-ant-api" in reason, (
        f"[{mode}] expected first-match to identify Anthropic API key family. Reason: {reason!r}"
    )


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


# ---------------------------------------------------------------------------
# PostToolUse tracker event name
# ---------------------------------------------------------------------------


def test_hook_self_test_hookEventName_posttooluse():
    """delib-search-tracker emits {} (pass) on self-test — PostToolUse hook."""
    result = _self_test("delib-search-tracker.py")
    assert result.returncode == 0
    output = json.loads(result.stdout)
    # Tracker emits silent pass on self-test (no advisory needed)
    assert output == {}


# ---------------------------------------------------------------------------
# End-to-end: gate → tracker → gate lifecycle
# ---------------------------------------------------------------------------


def test_delib_gate_tracker_e2e_same_context(tmp_path):
    """Gate warns → tracker records search → gate passes for same bridge context and topic."""
    # Set up an active bridge document so both hooks compute the same key
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\nNEW: bridge/auth-refactor-001.md\n",
        encoding="utf-8",
    )

    # Step 1: Gate warns (no prior search)
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Let me propose changes to auth refactor middleware",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result1 = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result1.returncode == 0
    output1 = json.loads(result1.stdout)
    assert "hookSpecificOutput" in output1, "Gate should warn when no prior search"
    assert "additionalContext" in output1["hookSpecificOutput"]

    # Step 2: Tracker records a deliberation search (PostToolUse event) with result evidence
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'auth refactor'"},
            "tool_output": (
                "Found 3 deliberations\n"
                "DELIB-0628: auth middleware hook review\n"
                "DELIB-0629: auth cycle enforcement\n"
                "DELIB-0630: auth mutation coverage"
            ),
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result2 = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result2.returncode == 0

    # Verify log file was created with result evidence
    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    assert log_path.exists(), "Tracker should create log file"
    log_entries = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(log_entries) == 1
    assert log_entries[0]["doc_topic_hash"]
    assert log_entries[0]["active_bridge_docs"] == ["auth-refactor"]
    assert log_entries[0]["search_success"] is True
    assert log_entries[0]["result_count"] == 3
    assert "DELIB-0628" in log_entries[0]["delib_ids"]
    assert log_entries[0]["search_topics"]  # should contain normalized topic words
    assert log_entries[0]["source_event"] == "PostToolUse"

    # Step 3: Gate passes (matching search found — topic overlap on "auth"/"refactor")
    result3 = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result3.returncode == 0
    output3 = json.loads(result3.stdout)
    assert output3 == {}, f"Gate should pass after tracker recorded topically relevant search, got: {output3}"


def test_delib_gate_tracker_e2e_same_doc_different_topic(tmp_path):
    """Same bridge doc, different topic → gate still warns (topic discrimination)."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-refactor\nNEW: bridge/auth-refactor-001.md\n",
        encoding="utf-8",
    )

    # Tracker records a search about "auth refactor" with successful output
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'auth refactor'"},
            "tool_output": "Found 2 deliberations\nDELIB-0628: auth middleware\nDELIB-0629: auth cycle",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_track = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result_track.returncode == 0

    # Gate with UNRELATED topic under the SAME bridge doc → should still warn
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Now investigate database migration policy for production",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_gate = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result_gate.returncode == 0
    output = json.loads(result_gate.stdout)
    assert "hookSpecificOutput" in output, (
        "Gate should warn when search topic (auth refactor) doesn't overlap "
        "with prompt topic (database migration policy)"
    )


def test_delib_gate_tracker_e2e_different_context(tmp_path):
    """Tracker records for topic-a → gate still warns for different topic-b (different bridge doc)."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()

    # Create bridge with topic-a active
    (bridge_dir / "INDEX.md").write_text(
        "Document: topic-a\nNEW: bridge/topic-a-001.md\n",
        encoding="utf-8",
    )

    # Tracker records search while topic-a is active
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'topic alpha'"},
            "tool_output": "Found 1 deliberation\nDELIB-0100: topic alpha review",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_track = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result_track.returncode == 0

    # Now change bridge context to topic-b
    (bridge_dir / "INDEX.md").write_text(
        "Document: topic-b\nNEW: bridge/topic-b-001.md\n",
        encoding="utf-8",
    )

    # Gate should warn — different active bridge doc means different key
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Working on topic-b now",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_gate = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result_gate.returncode == 0
    output = json.loads(result_gate.stdout)
    assert "hookSpecificOutput" in output, "Gate should warn for different bridge context"
    assert "additionalContext" in output["hookSpecificOutput"]


def test_delib_gate_no_active_bridge_docs(tmp_path):
    """No bridge/INDEX.md → gate and tracker still work with fallback key + topic match."""
    # No bridge directory — both hooks use _no_active_docs fallback

    # Tracker records with successful output about "deployment config"
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'deployment config'"},
            "tool_output": "0 results found",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_track = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result_track.returncode == 0

    # Gate should pass (same fallback key + overlapping topic "deployment")
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Check the deployment configuration",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_gate = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result_gate.returncode == 0
    output = json.loads(result_gate.stdout)
    assert output == {}, "Gate should pass when tracker used same fallback key with topical overlap"


def test_delib_tracker_failed_search_not_recorded(tmp_path):
    """Failed searches (error output) are not recorded and cannot satisfy the gate."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: widget-fix\nNEW: bridge/widget-fix-001.md\n",
        encoding="utf-8",
    )

    # Tracker receives a failed search command
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'widget fix'"},
            "tool_output": "Error: database connection failed\nTraceback (most recent call last):\n  ...",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_track = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result_track.returncode == 0

    # Log should NOT have been created (failed search not recorded)
    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    if log_path.exists():
        entries = [json.loads(ln) for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(entries) == 0, "Failed search should not create log entry"

    # Gate should still warn — no successful search recorded
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Let me work on the widget fix",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result_gate = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result_gate.returncode == 0
    output = json.loads(result_gate.stdout)
    assert "hookSpecificOutput" in output, "Gate should warn when only failed searches exist"


def test_delib_tracker_empty_output_not_recorded(tmp_path):
    """Tracker with empty tool_output does not record (ambiguous success)."""
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'test'"},
            "tool_output": "",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    if log_path.exists():
        entries = [json.loads(ln) for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(entries) == 0, "Empty output should not create log entry"


def test_delib_tracker_result_evidence_fields(tmp_path):
    """Tracker log entries include auditable result evidence."""
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'auth middleware'"},
            "tool_output": "Found 2 deliberations\nDELIB-0628: auth hook review\nDELIB-0631: middleware review",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    assert log_path.exists()
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())

    # All required evidence fields present
    assert entry["search_success"] is True
    assert entry["result_count"] == 2
    assert sorted(entry["delib_ids"]) == ["DELIB-0628", "DELIB-0631"]
    assert entry["source_event"] == "PostToolUse"
    assert entry["search_query"] == "auth middleware"
    assert "auth" in entry["search_topics"]
    assert "middleware" in entry["search_topics"]
    assert entry["timestamp"] > 0
    assert entry["doc_topic_hash"]


# ---------------------------------------------------------------------------
# tool_response runtime-payload tests (documented PostToolUse contract)
# ---------------------------------------------------------------------------


def test_delib_tracker_tool_response_string(tmp_path):
    """Tracker parses tool_response when it is a plain string (runtime shape)."""
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'scaling policy'"},
            "tool_response": (
                "Found 2 deliberations\nDELIB-0700: scaling policy initial review\nDELIB-0701: scaling constraints"
            ),
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    assert log_path.exists(), "Tracker should record from tool_response string"
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["search_success"] is True
    assert entry["result_count"] == 2
    assert sorted(entry["delib_ids"]) == ["DELIB-0700", "DELIB-0701"]
    assert entry["source_event"] == "PostToolUse"


def test_delib_tracker_tool_response_dict_stdout(tmp_path):
    """Tracker parses tool_response when it is a dict with stdout (Bash shape)."""
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'auth hooks'"},
            "tool_response": {
                "stdout": (
                    "Found 3 deliberations\n"
                    "DELIB-0628: auth middleware hook review\n"
                    "DELIB-0631: middleware review\n"
                    "DELIB-0632: auth remediation"
                ),
                "stderr": "",
                "exitCode": 0,
                "success": True,
            },
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    assert log_path.exists(), "Tracker should record from tool_response dict with stdout"
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["search_success"] is True
    assert entry["result_count"] == 3
    assert sorted(entry["delib_ids"]) == ["DELIB-0628", "DELIB-0631", "DELIB-0632"]
    assert "auth" in entry["search_topics"]
    assert "hooks" in entry["search_topics"]


def test_delib_tracker_tool_response_failure_not_recorded(tmp_path):
    """Failed search via tool_response is not recorded (runtime negative test)."""
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'broken query'"},
            "tool_response": {
                "stdout": "Error: database connection failed\nTraceback (most recent call last):\n  File ...",
                "stderr": "connection refused",
                "exitCode": 1,
                "success": False,
            },
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    if log_path.exists():
        entries = [json.loads(ln) for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(entries) == 0, "Failed tool_response search should not create log entry"


def test_delib_tracker_tool_response_overrides_tool_output(tmp_path):
    """When both tool_response and tool_output are present, tool_response wins."""
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'priority test'"},
            # tool_response is primary — should be used
            "tool_response": "Found 1 deliberation\nDELIB-0800: priority check",
            # tool_output is fallback — should be ignored
            "tool_output": "Error: this should not be parsed",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    assert log_path.exists(), "tool_response should take priority over tool_output"
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["search_success"] is True
    assert entry["delib_ids"] == ["DELIB-0800"]


def test_delib_tracker_e2e_tool_response_gate_lifecycle(tmp_path):
    """Full gate lifecycle using documented tool_response payload shape."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: deploy-config\nNEW: bridge/deploy-config-001.md\n",
        encoding="utf-8",
    )

    # Step 1: Gate warns (no prior search)
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Let me review the deploy configuration changes",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result1 = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result1.returncode == 0
    output1 = json.loads(result1.stdout)
    assert "hookSpecificOutput" in output1, "Gate should warn before any search"

    # Step 2: Tracker records via tool_response (runtime payload shape)
    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'deploy configuration'"},
            "tool_response": {
                "stdout": "Found 2 deliberations\nDELIB-0628: deploy config review\nDELIB-0629: deploy constraints",
                "stderr": "",
                "exitCode": 0,
            },
            "tool_use_id": "toolu_01ABC123",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result2 = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result2.returncode == 0

    # Verify log recorded with evidence
    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    assert log_path.exists()
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["search_success"] is True
    assert entry["result_count"] == 2
    assert "DELIB-0628" in entry["delib_ids"]

    # Step 3: Gate passes (matching topic overlap on "deploy"/"configuration")
    result3 = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert result3.returncode == 0
    output3 = json.loads(result3.stdout)
    assert output3 == {}, f"Gate should pass after tool_response-based search, got: {output3}"


def test_delib_tracker_failed_cmd_with_zero_results_stdout_not_recorded(tmp_path):
    """Failed command (success=false, exitCode=1) with '0 results found' stdout must not satisfy gate.

    Regression test for the case where structured tool_response metadata indicates
    failure but stdout contains an explicit zero-results marker that would otherwise
    be treated as a successful empty search.
    """
    # Set up an active bridge doc so the gate would warn
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-hooks\nNEW: bridge/auth-hooks-001.md\n",
        encoding="utf-8",
    )

    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'auth hooks'"},
            "tool_response": {
                "stdout": "0 results found",
                "stderr": "fatal: database unavailable",
                "exitCode": 1,
                "success": False,
            },
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    if log_path.exists():
        entries = [json.loads(ln) for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(entries) == 0, (
            "Failed command (success=false, exitCode=1) must not create log entry "
            "even when stdout says '0 results found'"
        )

    # Verify gate still warns (the failed search did not satisfy it)
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Let me review auth hooks",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    gate_result = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert gate_result.returncode == 0
    gate_output = json.loads(gate_result.stdout)
    assert "hookSpecificOutput" in gate_output, (
        "Gate must still warn after a failed search — the failed command must not satisfy the gate"
    )


def test_delib_tracker_ambiguous_output_not_recorded(tmp_path):
    """Ambiguous non-empty output without auditable evidence must not satisfy gate.

    Output like 'Search complete' that contains no DELIB IDs, no result count,
    and no explicit zero-results marker is not evidentiary and must not create
    a log entry.
    """
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "INDEX.md").write_text(
        "Document: auth-hooks\nNEW: bridge/auth-hooks-001.md\n",
        encoding="utf-8",
    )

    tracker_payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m groundtruth_kb deliberations search 'auth hooks'"},
            "tool_response": {
                "stdout": "Search complete",
                "stderr": "",
                "exitCode": 0,
                "success": True,
            },
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("delib-search-tracker.py", stdin_data=tracker_payload)
    assert result.returncode == 0

    log_path = tmp_path / ".groundtruth" / "delib-search-log.jsonl"
    if log_path.exists():
        entries = [json.loads(ln) for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(entries) == 0, (
            "Ambiguous output 'Search complete' without DELIB IDs or result count must not create a log entry"
        )

    # Verify gate still warns
    gate_payload = json.dumps(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Let me review auth hooks",
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    gate_result = _run_hook("delib-search-gate.py", stdin_data=gate_payload)
    assert gate_result.returncode == 0
    gate_output = json.loads(gate_result.stdout)
    assert "hookSpecificOutput" in gate_output, "Gate must still warn after ambiguous non-evidentiary output"
