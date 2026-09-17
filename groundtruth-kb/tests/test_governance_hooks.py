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
    "bridge-compliance-gate.py",
    "kb-not-markdown.py",
    "destructive-gate.py",
    "credential-scan.py",
]

PRETOOLUSE_HOOKS = [
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


def _native_spec_effect_probe(tmp_path: Path, payload: str) -> subprocess.CompletedProcess:
    """Preserve decoy data while checking the one native effect adapter."""
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "spec-test"},
    )
    assert result.returncode == 0 and not result.stderr
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before
    return result


def test_native_spec_effect_no_source_paths(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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
    result = _native_spec_effect_probe(tmp_path, payload)
    assert result.returncode == 0
    # The native checker returns an explicit denial; fixture metadata grants no claim.
    output = json.loads(result.stdout)
    assert isinstance(output, dict)


def test_native_spec_effect_match(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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
    result = _native_spec_effect_probe(tmp_path, payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_native_spec_effect_no_match(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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
    result = _native_spec_effect_probe(tmp_path, payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_native_spec_effect_non_source_file(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
    payload = json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "docs/guide.md", "content": "# Guide"},
            "session_id": "test",
            "cwd": str(tmp_path),
        }
    )
    result = _native_spec_effect_probe(tmp_path, payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_native_spec_effect_match_via_migrated_db(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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
    result = _native_spec_effect_probe(tmp_path, payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_native_spec_effect_platform_tests_match_via_bridge_evidence(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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
    result = _native_spec_effect_probe(tmp_path, payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_native_spec_effect_platform_tests_unmapped_bridge_evidence_denies(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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
    result = _native_spec_effect_probe(tmp_path, payload)
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


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


def _run_platform_native_effect(tmp_path: Path) -> dict:
    result = _native_spec_effect_probe(tmp_path, _platform_test_payload(tmp_path))
    assert result.returncode == 0
    return json.loads(result.stdout)


def test_native_spec_effect_platform_tests_target_paths_only_does_not_grant_claim(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
    _seed_platform_spec_db(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        'NEW\n\ntarget_paths: ["platform_tests/groundtruth_kb/test_auth.py"]\n\nProse body.\n',
        encoding="utf-8",
    )

    assert _run_platform_native_effect(tmp_path)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_native_spec_effect_platform_tests_mapping_only_does_not_grant_claim(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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

    assert _run_platform_native_effect(tmp_path)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_native_spec_effect_platform_tests_prose_only_bridge_mention_denies(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
    _seed_platform_spec_db(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "platform-test-coverage-001.md").write_text(
        "GO\n\n# Proposal\n\nThis prose mentions platform_tests/groundtruth_kb/test_auth.py but does not map it.\n",
        encoding="utf-8",
    )

    output = _run_platform_native_effect(tmp_path)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.mark.parametrize("latest_status", ["NO-GO", "WITHDRAWN", "DEFERRED", "ADVISORY"])
def test_native_spec_effect_platform_tests_latest_non_coverage_status_denies(tmp_path, latest_status):
    """SQLite and loose files never establish a current native effect claim."""
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

    output = _run_platform_native_effect(tmp_path)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


def test_native_spec_effect_platform_tests_latest_go_over_older_nogo_does_not_grant_claim(tmp_path):
    """SQLite and loose files never establish a current native effect claim."""
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

    assert _run_platform_native_effect(tmp_path)["hookSpecificOutput"]["permissionDecision"] == "deny"


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


def test_bridge_compliance_go_entry(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_no_frontmatter(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_new_entry_match(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert output["hookSpecificOutput"]["permissionDecisionReason"]
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_ask_has_additionalContext(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecisionReason"]
    assert output["hookSpecificOutput"]["additionalContext"]
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_nogo_entry(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_nogo_ask_has_additionalContext(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["additionalContext"] == output["hookSpecificOutput"]["permissionDecisionReason"]
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_revised_over_nogo(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    reason = output["hookSpecificOutput"]["permissionDecisionReason"]
    assert reason
    assert "pending Codex review" not in reason
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_go_over_nogo(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


def test_bridge_compliance_multi_doc_partial_match(tmp_path):
    """Loose bridge files never grant a native effect claim."""
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
    result = _run_hook(
        "bridge-compliance-gate.py",
        stdin_data=payload,
        env={"GT_AUTHORITY_URL": "http://127.0.0.1:1", "GTKB_NATIVE_CONTEXT_ID": "test"},
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "src/feature.py").exists()
    assert not (tmp_path / "src/auth.py").exists()


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


def _bridge_content_checkpoint(tmp_path: Path, content: str) -> dict:
    """Validate current metadata without treating narrative wording as authority."""
    decoy = tmp_path / "groundtruth.db"
    decoy.write_bytes(b"unrelated application data")
    status = content.splitlines()[0]
    header = (
        f"::init gtkb lo\n::open build\n{status}\n"
        "bridge_kind: implementation_proposal\nDocument: probe\nVersion: 1\nDate: 2026-09-13\n"
        "author_identity: test\nauthor_harness_id: test\nauthor_session_context_id: SENV-test\n"
        "author_model: test-model\nrecipient_role: loyal-opposition\n"
        "Project: PROJECT-1\nWork Item: WI-1\nwork_item_version: 1\n"
        'target_paths: ["src/feature.py"]\ntest_artifact_targets: ["tests/test_feature.py"]\n'
        'spec_versions: {"SPEC-1": 1}\n\n'
    )
    result = subprocess.run(
        [
            sys.executable,
            "-P",
            "-c",
            "import json,sys; from groundtruth_kb.bridge.native import parse_authored_message; "
            "print(json.dumps(parse_authored_message(sys.stdin.read())))",
        ],
        input=header + content,
        cwd=tmp_path,
        env=_canonical_env(),
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert decoy.read_bytes() == b"unrelated application data"
    assert sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()) == ["groundtruth.db"]
    return json.loads(result.stdout)


@pytest.mark.parametrize("status", ["NEW", "REVISED"])
@pytest.mark.parametrize(
    "body",
    [
        "This implementation inserts a new GOV version record into MemBase.",
        "This implementation writes formal artifact approval evidence for a new GOV version.",
        "This implementation writes a narrative-artifact approval-packet for AGENTS.md.",
        "This proposal explains prior MemBase defects but performs no MemBase mutation.",
        "This proposal explains prior approval packet defects but performs no approval packet work.",
    ],
)
def test_bridge_content_does_not_demand_retired_authority_carriers(tmp_path, status, body):
    # Legacy wording is inert text here, never permission or a request to create a packet.
    content = (
        f"{status}\nbridge_kind: implementation_proposal\n"
        'target_paths: ["src/feature.py"]\n'
        f"{body}\n\n## Specification Links\n"
        "- DCL-ARTIFACT-APPROVAL-HOOK-001\n"
    )
    assert _bridge_content_checkpoint(tmp_path, content)["status"] == status


@pytest.mark.parametrize("status", ["NEW", "REVISED"])
def test_bridge_content_heading_does_not_override_canonical_metadata(tmp_path, status):
    content = (
        f"{status}\nbridge_kind: implementation_proposal\n"
        'target_paths: ["src/feature.py"]\n'
        "## Specification Links (current sources)\n"
        "- DCL-ARTIFACT-APPROVAL-HOOK-001\n"
    )
    parsed = _bridge_content_checkpoint(tmp_path, content)
    assert parsed["status"] == status
    assert parsed["metadata"]["project"] == "PROJECT-1"
    assert parsed["spec_versions"] == {"SPEC-1": 1}
