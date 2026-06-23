# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Host-dependent integration coverage for spawned Claude worker delivery."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py"
_CLAUDE_INVOCATION_SURFACES = {
    "headless": {"argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]}
}
_READINESS_MARKER = "WORKER_READY"


def _load_trigger() -> ModuleType:
    module_name = "cross_harness_bridge_trigger_worker_delivery_subject"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _run_worker_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
) -> tuple[int | None, str, str]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        return None, stdout, stderr
    return process.returncode, stdout, stderr


def _readiness_text(stdout: str) -> str:
    raw = stdout.strip()
    if not raw:
        return ""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if not isinstance(parsed, dict):
        return raw
    fields = [
        parsed.get("result"),
        parsed.get("response"),
        parsed.get("message"),
        parsed.get("content"),
    ]
    return "\n".join(str(field) for field in fields if field is not None)


def _skip_if_headless_claude_unavailable(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    code, stdout, stderr = _run_worker_command(command, cwd=cwd, env=env, timeout=25)
    if code is None:
        pytest.skip("claude headless invocation timed out during readiness probe")
    if code != 0:
        pytest.skip(f"claude headless invocation unavailable: exit={code}; stderr={stderr[-500:]}")
    if stdout.strip():
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and parsed.get("is_error") is True:
            pytest.skip(f"claude headless invocation unavailable: {parsed}")
    readiness = _readiness_text(stdout)
    if _READINESS_MARKER not in readiness:
        pytest.skip(
            "claude headless invocation did not return readiness marker; "
            f"stdout={stdout[-500:]!r}; stderr={stderr[-500:]!r}"
        )


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.timeout(180)
def test_spawned_claude_worker_can_edit_authorized_file(tmp_path: Path) -> None:
    """Spawn a real Claude headless worker and require an authorized edit.

    The lane is closure evidence only on hosts where the `claude` executable is
    present. CI or developer hosts without that executable skip explicitly.
    """
    claude = shutil.which("claude")
    if claude is None:
        pytest.skip("claude executable unavailable")

    project = tmp_path / "synthetic-gtkb"
    project.mkdir()
    target_dir = project / "authorized"
    target_dir.mkdir()
    target_file = target_dir / "worker-output.txt"
    target_file.write_text("before\n", encoding="utf-8")

    (project / "groundtruth.toml").write_text(
        '[project]\nproject_name = "WorkerDeliveryFixture"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    bridge_dir = project / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "worker-delivery-001.md").write_text(
        "\n".join(
            [
                "NEW",
                "",
                "# Fixture Proposal",
                "",
                'target_paths: ["authorized/worker-output.txt"]',
                "",
                "## Requirement Sufficiency",
                "",
                "Existing requirements sufficient.",
                "",
                "## Specification Links",
                "",
                "- GOV-FILE-BRIDGE-AUTHORITY-001",
                "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (bridge_dir / "worker-delivery-002.md").write_text("GO\n\nFixture GO.\n", encoding="utf-8")
    (bridge_dir / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: worker-delivery\nGO: bridge/worker-delivery-002.md\nNEW: bridge/worker-delivery-001.md\n",
        encoding="utf-8",
    )

    prompt = "\n".join(
        [
            "::init gtkb pb",
            "",
            "You are a spawned Prime Builder worker in a synthetic test fixture.",
            "Edit exactly `authorized/worker-output.txt` so its full content is:",
            "WORKER_DELIVERED",
            "Do not ask the owner for input. Do not modify any other file.",
        ]
    )
    trigger = _load_trigger()
    target = trigger.DispatchTarget(
        needed_role_label="prime-builder",
        harness_id="B",
        command_handle="claude",
        canonical_mode="pb",
        invocation_surfaces=_CLAUDE_INVOCATION_SURFACES,
    )
    env = dict(os.environ)
    env["GTKB_PROJECT_ROOT"] = str(project)
    env["GTKB_BRIDGE_POLLER_RUN_ID"] = "pytest-worker-delivery"
    env["GTKB_BRIDGE_DISPATCH_KEYWORD"] = "::init gtkb pb"
    env.pop(trigger.LOOP_PREVENTION_ENV_VAR, None)

    readiness_command = trigger._harness_command(target, f"Return only {_READINESS_MARKER}.", project)
    assert readiness_command is not None
    _skip_if_headless_claude_unavailable(readiness_command, cwd=project, env=env)

    command = trigger._harness_command(target, prompt, project)
    assert command is not None
    assert command[command.index("--permission-mode") + 1] == "acceptEdits"
    assert command[command.index("--allowed-tools") + 1] == trigger.CLAUDE_WORKER_ALLOWED_TOOLS

    code, stdout, stderr = _run_worker_command(command, cwd=project, env=env, timeout=150)

    combined_output = f"{stdout}\n{stderr}".lower()
    assert code is not None, (
        f"claude worker command timed out: {command!r}; stdout={stdout[-2000:]}; stderr={stderr[-2000:]}"
    )
    assert code == 0, f"claude exited {code}; stdout={stdout}; stderr={stderr}"
    assert not ("permission" in combined_output and "denied" in combined_output), combined_output
    if stdout.strip():
        parsed = json.loads(stdout)
        assert parsed.get("is_error") is not True, parsed
    actual = target_file.read_text(encoding="utf-8").strip()
    assert actual == "WORKER_DELIVERED", (
        f"spawned worker did not edit the authorized file; actual={actual!r}; "
        f"command={command!r}; stdout={stdout!r}; stderr={stderr!r}"
    )
