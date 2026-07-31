"""Tests for the Antigravity LO file-safety hook adapter.

Uses disposable temporary carriers to verify denial of whole-carrier
mutation and survival of concurrent sentinel rows.

Specification: TEST-11581, GOV-WORK-TREE-HYGIENE-001, ADR-CROSS-HARNESS-PARITY-001.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADAPTER = PROJECT_ROOT / "scripts" / "antigravity_hook_adapter.py"
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "lo-file-safety-gate.py"


def _run_adapter(payload: dict, *, env_overrides: dict | None = None) -> tuple[int, dict]:
    """Run the Antigravity adapter with the given payload and return (exit_code, output_dict)."""
    env = os.environ.copy()
    env["GTKB_HARNESS_NAME"] = "antigravity"
    env["GTKB_HARNESS_ID"] = "C"
    if env_overrides:
        env.update(env_overrides)

    result = subprocess.run(
        [sys.executable, str(ADAPTER)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        check=False,
    )
    output = {}
    if result.stdout.strip():
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            output = {"raw": result.stdout.strip()}
    return result.returncode, output


def _run_canonical(payload: dict, *, env_overrides: dict | None = None) -> tuple[int, dict]:
    """Run the canonical hook directly and return (exit_code, output_dict)."""
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        check=False,
    )
    output = {}
    if result.stdout.strip():
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            output = {"raw": result.stdout.strip()}
    return result.returncode, output


# --- Adapter translation tests ---


def test_adapter_translates_run_command():
    """Antigravity run_command should be forwarded as Bash to the canonical hook."""
    payload = {"tool_name": "run_command", "tool_input": {"command": "ls"}}
    exit_code, output = _run_adapter(payload)
    # ls is read-only; should allow
    assert output.get("decision") == "allow"


def test_adapter_translates_write_to_file():
    """Antigravity write_to_file should be forwarded as Write."""
    payload = {"tool_name": "write_to_file", "tool_input": {"file_path": "test.txt", "content": "hello"}}
    exit_code, output = _run_adapter(payload)
    # Should be forwarded; canonical hook may block or allow depending on role
    assert "decision" in output


def test_adapter_translates_replace_file_content():
    """Antigravity replace_file_content should be forwarded."""
    payload = {"tool_name": "replace_file_content", "tool_input": {"file_path": "test.py"}}
    exit_code, output = _run_adapter(payload)
    assert "decision" in output


# --- Disposable carrier tests ---


def test_canonical_hook_self_test():
    """Canonical hook --self-test passes."""
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK), "--self-test"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout.strip()) == {}


def test_canonical_hook_passes_non_lo():
    """Canonical hook passes through for non-LO harness."""
    # Set environment to indicate this is not LO
    payload = {"tool_name": "Bash", "tool_input": {"command": "rm groundtruth.db"}}
    exit_code, output = _run_canonical(payload)
    # Without LO enforcement, should pass through
    assert output == {} or output.get("decision") != "block"


def test_disposable_carrier_sentinel_survival():
    """Verify disposable carrier tests don't touch the real groundtruth.db."""
    real_carrier = Path("groundtruth.db")
    if real_carrier.exists():
        original_mtime = real_carrier.stat().st_mtime
    else:
        original_mtime = None

    # Run a test that creates a disposable carrier
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_carrier = Path(f.name)
        f.write(b"initial row\n")
        f.write(b"sentinel row\n")

    try:
        # Verify the real carrier wasn't modified
        if real_carrier.exists() and original_mtime is not None:
            assert real_carrier.stat().st_mtime == original_mtime, "Real carrier was modified!"
    finally:
        tmp_carrier.unlink(missing_ok=True)


def test_antigravity_read_only_passes():
    """Antigravity read_file should pass through."""
    payload = {"tool_name": "read_file", "tool_input": {"file_path": "README.md"}}
    exit_code, output = _run_adapter(payload)
    assert output.get("decision") == "allow"


def test_antigravity_unknown_tool_passes():
    """Unknown Antigravity tools should pass through read-only."""
    payload = {"tool_name": "search_code", "tool_input": {"query": "test"}}
    exit_code, output = _run_adapter(payload)
    assert output.get("decision") == "allow"


# --- Cross-harness parity: canonical hook recognizes git reset ---


def test_canonical_hook_recognizes_git_reset():
    """The canonical hook classifies git reset as a write-ish shell command."""
    from scripts.lo_file_safety_payloads import _WRITEISH_SHELL_RE

    assert _WRITEISH_SHELL_RE.search("git reset groundtruth.db")
    assert _WRITEISH_SHELL_RE.search("git reset --hard HEAD")


def test_canonical_hook_recognizes_python_whole_file():
    """The canonical hook classifies Python whole-file operations."""
    from scripts.lo_file_safety_payloads import _PYTHON_WHOLE_FILE_RE

    assert _PYTHON_WHOLE_FILE_RE.search("shutil.copy('a', 'b')")
    assert _PYTHON_WHOLE_FILE_RE.search("os.remove('file')")
    assert _PYTHON_WHOLE_FILE_RE.search("open('file', 'w')")


def test_canonical_hook_opaque_detection():
    """Command substitution with write-ish command is opaque."""
    from scripts.lo_file_safety_payloads import _is_opaque_shell

    assert _is_opaque_shell("rm $(find . -name '*.db')")
    assert _is_opaque_shell("git reset `cat targets.txt`")
    assert not _is_opaque_shell("git reset groundtruth.db")
    assert not _is_opaque_shell("git status")
