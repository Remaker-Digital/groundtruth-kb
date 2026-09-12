# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for governance hook templates."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from groundtruth_kb import get_templates_dir

HOOKS_DIR = get_templates_dir() / "hooks"

ALL_HOOKS = [
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

WORK_INTENT_SESSION_ENV_VARS = (
    "GTKB_BRIDGE_POLLER_RUN_ID",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "GTKB_INHERITED_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "ANTIGRAVITY_SESSION_ID",
    "GTKB_SESSION_ID",
)


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
    try:
        payload = json.loads(stdin_data or "{}")
    except json.JSONDecodeError:
        payload = {}
    session_id = str(payload.get("session_id") or "test")
    for env_var in WORK_INTENT_SESSION_ENV_VARS:
        run_env[env_var] = session_id
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
# Credential catalog availability and refusal.


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
    """Child hooks use the same source or installed package as the parent."""
    import groundtruth_kb

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(groundtruth_kb.__file__).resolve().parent.parent)
    return env


def test_credential_scan_canonical_mode_self_test_uses_canonical_catalog():
    result = _run_hook("credential-scan.py", args=["--self-test"], env=_canonical_env())
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "credential_detected" in output["permissionDecisionReason"]


def test_credential_scan_missing_catalog_refuses_without_echoing_input(tmp_path):
    isolated = _fallback_isolated_copy(tmp_path)
    result = subprocess.run(
        [sys.executable, "-S", "-I", str(isolated / "credential-scan.py")],
        input=json.dumps(_CRED_SAMPLE_PAYLOAD),
        capture_output=True,
        text=True,
        cwd=isolated,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    assert "credential_catalog_unavailable" in output["permissionDecisionReason"]
    assert _CRED_SAMPLE_PAYLOAD["tool_input"]["command"] not in result.stdout + result.stderr


@pytest.mark.parametrize("mode", ["canonical", "unavailable"])
def test_credential_scan_both_modes_deny_same_sample(tmp_path, mode):
    payload = json.dumps(_CRED_SAMPLE_PAYLOAD)
    if mode == "canonical":
        result = _run_hook("credential-scan.py", stdin_data=payload, env=_canonical_env())
    else:
        isolated = _fallback_isolated_copy(tmp_path)
        result = subprocess.run(
            [sys.executable, "-S", "-I", str(isolated / "credential-scan.py")],
            input=payload,
            capture_output=True,
            text=True,
            cwd=isolated,
        )
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    expected = "credential_detected" if mode == "canonical" else "credential_catalog_unavailable"
    assert expected in output["permissionDecisionReason"]
    assert _CRED_SAMPLE_PAYLOAD["tool_input"]["command"] not in result.stdout + result.stderr


# ---------------------------------------------------------------------------
# Deliberation search gate
# ---------------------------------------------------------------------------


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


def test_spec_before_code_platform_tests_match_via_bridge_evidence(tmp_path):
    """platform_tests path with explicit bridge evidence passes without matching source_paths."""
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-001",
        title="Platform test coverage",
        status="specified",
        changed_by="test",
        change_reason="test",
        source_paths=["src/other.py"],
    )
    db.close()

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        "NEW\n\n"
        'target_paths: ["platform_tests/groundtruth_kb/test_auth.py"]\n\n'
        "## Spec-to-Test Mapping\n\n"
        "| Spec | Verification |\n"
        "| --- | --- |\n"
        "| `SPEC-001` | `platform_tests/groundtruth_kb/test_auth.py` |\n",
        encoding="utf-8",
    )

    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "platform_tests/groundtruth_kb/test_auth.py",
                "content": "def test_auth(): pass",
            },
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("spec-before-code.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output == {}


def test_spec_before_code_platform_tests_unmapped_bridge_evidence_warns(tmp_path):
    """Unrelated platform_tests path still warns when bridge evidence maps another file."""
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-001",
        title="Platform test coverage",
        status="specified",
        changed_by="test",
        change_reason="test",
        source_paths=["src/other.py"],
    )
    db.close()

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        "NEW\n\n"
        'target_paths: ["platform_tests/groundtruth_kb/test_other.py"]\n\n'
        "## Spec-to-Test Mapping\n\n"
        "| `SPEC-001` | `platform_tests/groundtruth_kb/test_other.py` |\n",
        encoding="utf-8",
    )

    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "platform_tests/groundtruth_kb/test_auth.py",
                "content": "def test_auth(): pass",
            },
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _run_hook("spec-before-code.py", stdin_data=payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output
    assert "No specification found covering" in output["hookSpecificOutput"]["additionalContext"]


def _seed_platform_spec_db(tmp_path: Path) -> None:
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_spec(
        id="SPEC-001",
        title="Platform test coverage",
        status="specified",
        changed_by="test",
        change_reason="test",
        source_paths=["src/other.py"],
    )
    db.close()


def _platform_test_payload(tmp_path: Path, file_path: str = "platform_tests/groundtruth_kb/test_auth.py") -> str:
    return json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": file_path,
                "content": "def test_auth(): pass",
            },
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )


def _run_platform_spec_before_code(tmp_path: Path) -> dict:
    result = _run_hook("spec-before-code.py", stdin_data=_platform_test_payload(tmp_path))
    assert result.returncode == 0
    return json.loads(result.stdout)


def test_spec_before_code_platform_tests_target_paths_only_suppresses(tmp_path):
    """Current structured target_paths bridge evidence suppresses the advisory."""
    _seed_platform_spec_db(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        'NEW\n\ntarget_paths: ["platform_tests/groundtruth_kb/test_auth.py"]\n\nProse body.\n',
        encoding="utf-8",
    )

    assert _run_platform_spec_before_code(tmp_path) == {}


def test_spec_before_code_platform_tests_mapping_only_suppresses(tmp_path):
    """Current structured Spec-to-Test Mapping bridge evidence suppresses the advisory."""
    _seed_platform_spec_db(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        "REVISED\n\n"
        "## Spec-to-Test Mapping\n\n"
        "| Spec | Verification |\n"
        "| --- | --- |\n"
        "| `SPEC-001` | `platform_tests/groundtruth_kb/test_auth.py` |\n",
        encoding="utf-8",
    )

    assert _run_platform_spec_before_code(tmp_path) == {}


def test_spec_before_code_platform_tests_prose_only_bridge_mention_warns(tmp_path):
    """A prose-only bridge mention is not structured coverage."""
    _seed_platform_spec_db(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        "GO\n\n# Proposal\n\nThis prose mentions platform_tests/groundtruth_kb/test_auth.py but does not map it.\n",
        encoding="utf-8",
    )

    output = _run_platform_spec_before_code(tmp_path)
    assert "hookSpecificOutput" in output
    assert "No specification found covering" in output["hookSpecificOutput"]["additionalContext"]


@pytest.mark.parametrize("latest_status", ["NO-GO", "WITHDRAWN", "DEFERRED", "ADVISORY"])
def test_spec_before_code_platform_tests_latest_non_coverage_status_warns(tmp_path, latest_status):
    """Earlier mapped versions do not count when latest bridge state is non-covering."""
    _seed_platform_spec_db(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        'NEW\n\ntarget_paths: ["platform_tests/groundtruth_kb/test_auth.py"]\n',
        encoding="utf-8",
    )
    (bridge_dir / "platform-test-coverage-002.md").write_text(
        f"{latest_status}\n\n"
        "## Spec-to-Test Mapping\n\n"
        "| `SPEC-001` | `platform_tests/groundtruth_kb/test_auth.py` |\n",
        encoding="utf-8",
    )

    output = _run_platform_spec_before_code(tmp_path)
    assert "hookSpecificOutput" in output
    assert "No specification found covering" in output["hookSpecificOutput"]["additionalContext"]


def test_spec_before_code_platform_tests_latest_go_over_older_nogo_suppresses(tmp_path):
    """Latest acceptable bridge evidence wins over older rejected history."""
    _seed_platform_spec_db(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        "NO-GO\n\nEarlier rejected bridge version.\n",
        encoding="utf-8",
    )
    (bridge_dir / "platform-test-coverage-002.md").write_text(
        "GO\n\n"
        "## Spec-Derived Verification Plan\n\n"
        "| Surface | Verification |\n"
        "| --- | --- |\n"
        "| `SPEC-001` | `platform_tests/groundtruth_kb/test_auth.py` |\n",
        encoding="utf-8",
    )

    assert _run_platform_spec_before_code(tmp_path) == {}


# ---------------------------------------------------------------------------
# Bridge compliance gate
# ---------------------------------------------------------------------------


def _make_bridge_thread(tmp_path: Path, entries: list[tuple[str, str, str]]) -> Path:
    """Create status-bearing versioned bridge files for hook routing."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    for _doc_name, status, file_path in entries:
        path = tmp_path / file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(f"{status}\n\n", encoding="utf-8")
    return bridge_dir


def _write_bridge_version(tmp_path: Path, slug: str, version: int, status: str) -> Path:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    path = bridge_dir / f"{slug}-{version:03d}.md"
    path.write_text(f"{status}\n\n", encoding="utf-8")
    return path


def test_bridge_compliance_go_entry(tmp_path):
    """Latest GO → pass (no target_paths in proposal → also pass)."""
    _make_bridge_thread(tmp_path, [("my-feature", "GO", "bridge/my-feature-002.md")])
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
    (bridge_dir / "my-feature-001.md").write_text("NEW\n\n# Proposal\n\nNo target_paths here.\n", encoding="utf-8")
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
    (bridge_dir / "auth-refactor-001.md").write_text(
        'NEW\n\n# Auth Refactor Proposal\n\ntarget_paths: ["src/auth.py"]\n\nSome content.\n',
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
    (bridge_dir / "auth-refactor-001.md").write_text('NEW\n\ntarget_paths: ["src/auth.py"]\n', encoding="utf-8")
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
    (bridge_dir / "auth-refactor-001.md").write_text('NEW\n\ntarget_paths: ["src/auth.py"]\n', encoding="utf-8")
    (bridge_dir / "auth-refactor-002.md").write_text("NO-GO\n\n# NO-GO review\n", encoding="utf-8")
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
    (bridge_dir / "auth-refactor-001.md").write_text('NEW\n\ntarget_paths: ["src/auth.py"]\n', encoding="utf-8")
    (bridge_dir / "auth-refactor-002.md").write_text("NO-GO\n\n# NO-GO review\n", encoding="utf-8")
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
    (bridge_dir / "auth-refactor-001.md").write_text('NEW\n\ntarget_paths: ["src/auth.py"]\n', encoding="utf-8")
    (bridge_dir / "auth-refactor-002.md").write_text("NO-GO\n\n# NO-GO review\n", encoding="utf-8")
    (bridge_dir / "auth-refactor-003.md").write_text(
        'REVISED\n\ntarget_paths: ["src/auth.py"]\n# REVISED\n', encoding="utf-8"
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
    reason = output["hookSpecificOutput"]["permissionDecisionReason"]
    # Should be pending message (REVISED/pending), not NO-GO message
    assert "NO-GO" not in reason or "pending" in reason.lower() or "REVISED" in reason


def test_bridge_compliance_go_over_nogo(tmp_path):
    """Latest GO, historical NO-GO below → pass."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "auth-refactor-001.md").write_text('NEW\n\ntarget_paths: ["src/auth.py"]\n', encoding="utf-8")
    (bridge_dir / "auth-refactor-002.md").write_text("NO-GO\n\n# NO-GO review\n", encoding="utf-8")
    (bridge_dir / "auth-refactor-004.md").write_text("GO\n\n# GO review\n", encoding="utf-8")
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
    (bridge_dir / "auth-refactor-001.md").write_text('NEW\n\ntarget_paths: ["src/auth.py"]\n', encoding="utf-8")
    (bridge_dir / "unrelated-work-001.md").write_text('NEW\n\ntarget_paths: ["src/other.py"]\n', encoding="utf-8")
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


# ---------------------------------------------------------------------------
# Hook payload field tests
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PostToolUse tracker event name
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# End-to-end: gate → tracker → gate lifecycle
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# tool_response runtime-payload tests (documented PostToolUse contract)
# ---------------------------------------------------------------------------
