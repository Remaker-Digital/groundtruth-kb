"""Spec-derived tests for ``_check_external_harness_exec_boundary`` doctor check.

Implements the spec-to-test mapping in
``bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`` for:

- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`` (spec-derived test coverage).
- ``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` (project-artifact root invariant
  preserved while the bounded external-harness-exec exception is enforced).
- ``.claude/rules/project-root-boundary.md`` (the External Harness Executable
  Resolution Exception; this check is the deterministic bound).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.project.doctor import _check_external_harness_exec_boundary

_PARAMETRIZED_TRIGGER = '''"""Stub trigger; parametrized command from registry projection."""
import shutil
import subprocess


def dispatch(command):
    resolved = shutil.which(command[0])
    return subprocess.Popen(command)
'''

_PARAMETRIZED_VERIFY = '''"""Stub verifier; parametrized command from registry projection."""
import shutil
import subprocess


def _resolve(cmd):
    return shutil.which(cmd[0])


def run(cmd):
    return subprocess.run(cmd, capture_output=True)
'''

_LITERAL_VIOLATION_TRIGGER = '''"""Stub trigger with a non-harness literal exec resolution."""
import subprocess


def evil():
    return subprocess.run(["wget", "https://example.com"], capture_output=True)
'''


def _build_project(
    tmp_path: Path,
    *,
    harness_argv: dict[str, str] | None,
    trigger_text: str | None,
    verify_text: str | None,
) -> Path:
    """Construct a synthetic project root with optional registry + scan files."""
    (tmp_path / "scripts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "harness-state").mkdir(parents=True, exist_ok=True)
    if harness_argv is not None:
        registry: dict[str, object] = {"harnesses": []}
        harnesses: list[dict[str, object]] = []
        for hid, cmd in harness_argv.items():
            harnesses.append(
                {
                    "id": hid,
                    "invocation_surfaces": {
                        "headless": {"argv": [cmd, "--bridge"]},
                    },
                }
            )
        registry["harnesses"] = harnesses
        (tmp_path / "harness-state" / "harness-registry.json").write_text(
            json.dumps(registry, indent=2),
            encoding="utf-8",
        )
    if trigger_text is not None:
        (tmp_path / "scripts" / "cross_harness_bridge_trigger.py").write_text(
            trigger_text,
            encoding="utf-8",
        )
    if verify_text is not None:
        (tmp_path / "scripts" / "verify_antigravity_dispatch.py").write_text(
            verify_text,
            encoding="utf-8",
        )
    return tmp_path


def test_pass_when_only_registry_enumerated_harness_commands_resolve_out_of_root(
    tmp_path: Path,
) -> None:
    """Case (a): PASS when only registry-enumerated harness commands resolve out-of-root.

    Synthesizes a minimal project containing a harness registry with three
    enumerated harness commands (codex, claude, gemini) and stub scan files
    that resolve commands via parametrized (non-literal) lookups. Expected:
    the check passes and the report names the registry-enumerated commands.
    """
    project = _build_project(
        tmp_path,
        harness_argv={"A": "codex", "B": "claude", "C": "gemini"},
        trigger_text=_PARAMETRIZED_TRIGGER,
        verify_text=_PARAMETRIZED_VERIFY,
    )

    result = _check_external_harness_exec_boundary(project)

    assert result.status == "pass", (
        f"expected pass; got {result.status}: {result.message}"
    )
    assert result.found is True
    assert "codex" in result.message
    assert "claude" in result.message
    assert "gemini" in result.message
    assert "3 enumerated" in result.message


def test_fail_when_non_harness_literal_subprocess_call_introduced(
    tmp_path: Path,
) -> None:
    """Case (b): FAIL when a synthetic non-harness out-of-root project dependency is introduced.

    Same registry as case (a), but the trigger stub adds a literal
    ``subprocess.run(["wget", ...])`` call. Expected: FAIL with a message
    that names the violating command and the offending file.
    """
    project = _build_project(
        tmp_path,
        harness_argv={"A": "codex", "B": "claude", "C": "gemini"},
        trigger_text=_LITERAL_VIOLATION_TRIGGER,
        verify_text=_PARAMETRIZED_VERIFY,
    )

    result = _check_external_harness_exec_boundary(project)

    assert result.status == "fail", (
        f"expected fail; got {result.status}: {result.message}"
    )
    assert "wget" in result.message
    assert "cross_harness_bridge_trigger.py" in result.message
    assert "non-harness" in result.message.lower()


def test_warn_when_harness_registry_missing(tmp_path: Path) -> None:
    """Case (c): WARN on the registry-missing path.

    The proposal specifies a WARN severity for the registry-missing case
    (a harness resolution mechanism is present but the registry cannot
    enumerate the eligible commands). Expected: WARN with a message that
    cites the missing registry path.
    """
    project = _build_project(
        tmp_path,
        harness_argv=None,  # registry file deliberately absent
        trigger_text=_PARAMETRIZED_TRIGGER,
        verify_text=_PARAMETRIZED_VERIFY,
    )

    result = _check_external_harness_exec_boundary(project)

    assert result.status == "warning", (
        f"expected warning; got {result.status}: {result.message}"
    )
    assert "harness-registry.json" in result.message


def test_check_is_deterministic_and_read_only(tmp_path: Path) -> None:
    """Case (d): the check is deterministic and read-only.

    Calling the check twice on identical inputs must yield identical
    ``status`` and ``message``. No filesystem state may be mutated by
    either invocation (verified by snapshotting mtimes before and after).
    """
    project = _build_project(
        tmp_path,
        harness_argv={"A": "codex", "B": "claude", "C": "gemini"},
        trigger_text=_PARAMETRIZED_TRIGGER,
        verify_text=_PARAMETRIZED_VERIFY,
    )

    files_before = {
        path: path.stat().st_mtime_ns
        for path in project.rglob("*")
        if path.is_file()
    }

    result_first = _check_external_harness_exec_boundary(project)
    result_second = _check_external_harness_exec_boundary(project)

    files_after = {
        path: path.stat().st_mtime_ns
        for path in project.rglob("*")
        if path.is_file()
    }

    assert result_first.status == result_second.status
    assert result_first.message == result_second.message
    assert files_before == files_after, (
        "check mutated filesystem state — must be strictly read-only"
    )
