#!/usr/bin/env python3
"""Headless Cursor Agent harness shim for GT-KB bridge dispatch."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    from scripts._env import load_env_local
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from _env import load_env_local

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TIMEOUT_SECONDS = 600.0
LOYAL_OPPOSITION_BRIDGE_SKILLS = frozenset({"bridge-review", "verification"})
# WI-4933: the harness-registry Cursor invocation surfaces pass canonical
# Loyal Opposition route keys ('bridge-review', 'verification'), but no SKILL.md
# exists under those names. Resolve them to the real skill directories so
# headless LO dispatch loads the bridge/verification contracts instead of
# failing closed or loading a generic review memo contract.
_SKILL_ROUTE_ALIASES = {
    "bridge-review": "bridge",
    "verification": "verify",
}
_CURSOR_GUI_LAUNCHER_NAMES = {"cursor", "cursor.cmd", "cursor.exe"}
_STANDALONE_AGENT_NAMES = ("agent", "cursor-agent")
_CURSOR_AGENT_PROCESS_NAMES = {"agent", "agent.exe", "cursor-agent", "cursor-agent.exe"}
_WINDOWS_SHELL_WRAPPER_SUFFIXES = {".bat", ".cmd", ".ps1"}
_CURSOR_AGENT_HELP_TIMEOUT_SECONDS = 10.0
_CURSOR_AUTH_ENV_KEYS = ("CURSOR_API_KEY",)
_PROVENANCE_DIR = Path(".gtkb-state") / "ops" / "dispatch-provenance"
_PROVENANCE_LEDGER_FILENAME = "dispatch-provenance.json"


class CursorHarnessError(RuntimeError):
    """Raised for fail-closed Cursor harness errors."""


def _windows_no_window_creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def _cursor_supports_agent_subcommand(cursor_executable: str) -> bool:
    try:
        run_kwargs = {
            "capture_output": True,
            "text": True,
            "timeout": _CURSOR_AGENT_HELP_TIMEOUT_SECONDS,
            "check": False,
        }
        creationflags = _windows_no_window_creationflags()
        if creationflags:
            run_kwargs["creationflags"] = creationflags
        completed = subprocess.run([cursor_executable, "agent", "--help"], **run_kwargs)
    except (OSError, subprocess.TimeoutExpired):
        return False
    help_text = f"{completed.stdout or ''}\n{completed.stderr or ''}".lower()
    return (
        completed.returncode == 0 and "--output-format" in help_text and ("--print" in help_text or "-p" in help_text)
    )


def _is_windows_shell_wrapper(path: str | Path) -> bool:
    return Path(path).suffix.lower() in _WINDOWS_SHELL_WRAPPER_SUFFIXES


def _windows_cursor_agent_candidates() -> tuple[Path, ...]:
    if os.name != "nt":
        return ()
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return ()
    root = Path(local_app_data) / "cursor-agent"
    return (
        root / "agent.cmd",
        root / "agent.CMD",
        root / "agent.exe",
        root / "agent.ps1",
        root / "cursor-agent.cmd",
        root / "cursor-agent.CMD",
        root / "cursor-agent.exe",
        root / "cursor-agent.ps1",
    )


def _windows_cursor_agent_direct_commands() -> tuple[list[str], ...]:
    if os.name != "nt":
        return ()
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return ()
    versions_root = Path(local_app_data) / "cursor-agent" / "versions"
    if not versions_root.is_dir():
        return ()
    candidates: list[tuple[float, str, Path, Path]] = []
    try:
        version_dirs = tuple(versions_root.iterdir())
    except OSError:
        return ()
    for version_dir in version_dirs:
        if not version_dir.is_dir():
            continue
        node = version_dir / "node.exe"
        index = version_dir / "index.js"
        if not (node.is_file() and index.is_file()):
            continue
        try:
            modified_at = version_dir.stat().st_mtime
        except OSError:
            modified_at = 0.0
        candidates.append((modified_at, version_dir.name, node, index))
    candidates.sort(reverse=True)
    return tuple([str(node), str(index)] for _modified_at, _name, node, index in candidates)


def _resolve_agent_command() -> list[str]:
    explicit = os.environ.get("CURSOR_AGENT_BIN")
    if explicit:
        if Path(explicit).name.lower() in _CURSOR_GUI_LAUNCHER_NAMES:
            if _cursor_supports_agent_subcommand(explicit):
                return [explicit, "agent"]
            raise CursorHarnessError(
                "Cursor Agent CLI not found. CURSOR_AGENT_BIN points at a Cursor launcher without an "
                "unambiguous headless `agent` subcommand; set it to a standalone `agent` executable or "
                "a Cursor CLI that supports `cursor agent --print --output-format`."
            )
        return [explicit]
    wrapper_fallbacks: list[str] = []
    for agent_name in _STANDALONE_AGENT_NAMES:
        candidate = shutil.which(agent_name)
        if candidate:
            if _is_windows_shell_wrapper(candidate):
                wrapper_fallbacks.append(candidate)
                continue
            return [candidate]
    for command in _windows_cursor_agent_direct_commands():
        return command
    if wrapper_fallbacks:
        return [wrapper_fallbacks[0]]
    for candidate in _windows_cursor_agent_candidates():
        if candidate.is_file():
            return [str(candidate)]
    for cursor_name in ("cursor", "cursor.cmd", "cursor.exe"):
        cursor_candidate = shutil.which(cursor_name)
        if cursor_candidate and _cursor_supports_agent_subcommand(cursor_candidate):
            return [cursor_candidate, "agent"]
    raise CursorHarnessError(
        "Cursor Agent CLI not found. Ensure standalone `agent` is on PATH, install a Cursor CLI that supports "
        "`cursor agent --print --output-format`, or set CURSOR_AGENT_BIN."
    )


def _skill_system_prompt(skill: str | None) -> str | None:
    if not skill:
        return None
    skill = _SKILL_ROUTE_ALIASES.get(skill, skill)
    skill_path = PROJECT_ROOT / ".cursor" / "skills" / skill / "SKILL.md"
    if not skill_path.is_file():
        skill_path = PROJECT_ROOT / ".codex" / "skills" / skill / "SKILL.md"
    if not skill_path.is_file():
        skill_path = PROJECT_ROOT / ".claude" / "skills" / skill / "SKILL.md"
    if not skill_path.is_file():
        raise CursorHarnessError(f"unknown skill route {skill!r}; no SKILL.md found")
    return skill_path.read_text(encoding="utf-8")


def _build_prompt(user_prompt: str, skill: str | None) -> str:
    system_prompt = _skill_system_prompt(skill)
    if not system_prompt:
        return user_prompt
    return (
        f"Follow the GT-KB skill contract below, then execute the user task.\n\n{system_prompt}\n\n---\n\n{user_prompt}"
    )


def _build_command(prompt: str, project_root: Path, *, output_format: str) -> list[str]:
    command = _resolve_agent_command()
    command.extend(
        [
            "-p",
            "--trust",
            "--workspace",
            str(project_root),
            "--output-format",
            output_format,
            prompt,
        ]
    )
    return command


def _requires_bridge_output(skill: str | None) -> bool:
    return skill in LOYAL_OPPOSITION_BRIDGE_SKILLS


def _dispatcher_run_id(env: dict[str, str] | None = None) -> str:
    env = os.environ if env is None else env
    return env.get("GTKB_BRIDGE_POLLER_RUN_ID", "") or env.get("GTKB_INHERITED_SESSION_ID", "")


def _normalized_for_process_match(value: object) -> str:
    return str(value).replace("/", "\\").lower()


def _cursor_agent_snapshot(project_root: Path) -> dict[tuple[int, float], dict[str, Any]]:
    """Return live Cursor agent processes tied to this workspace.

    The snapshot is best-effort runtime provenance. A missing psutil import or
    protected process just means no orphan-agent reap evidence is recorded.
    """

    try:
        import psutil  # type: ignore
    except Exception:  # noqa: BLE001 - optional runtime provenance dependency
        return {}

    root_marker = _normalized_for_process_match(project_root)
    out: dict[tuple[int, float], dict[str, Any]] = {}
    for proc in psutil.process_iter(["pid", "ppid", "name", "create_time", "cmdline"]):
        try:
            info = proc.info
            pid = int(info["pid"])
            create_time = float(info["create_time"])
        except Exception:  # noqa: BLE001 - process may exit or deny access mid-scan
            continue
        cmdline_parts = [str(part) for part in (info.get("cmdline") or [])]
        normalized_cmdline = _normalized_for_process_match(" ".join(cmdline_parts))
        if root_marker not in normalized_cmdline:
            continue
        process_names = {str(info.get("name") or "").lower()}
        process_names.update(Path(part).name.lower() for part in cmdline_parts if part)
        if not process_names.intersection(_CURSOR_AGENT_PROCESS_NAMES):
            continue
        out[(pid, create_time)] = {
            "pid": pid,
            "ppid": int(info.get("ppid") or 0),
            "name": str(info.get("name") or ""),
            "create_time_epoch": create_time,
        }
    return out


def _cursor_agent_provenance_records(
    before: dict[tuple[int, float], dict[str, Any]],
    after: dict[tuple[int, float], dict[str, Any]],
    *,
    dispatch_root_pid: int,
    started_at_epoch: float,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key, row in sorted(after.items()):
        if key in before:
            continue
        create_time = float(row["create_time_epoch"])
        if create_time < started_at_epoch - 2.0:
            continue
        records.append(
            {
                "pid": int(row["pid"]),
                "create_time_epoch": create_time,
                "dispatch_root_pid": int(dispatch_root_pid),
            }
        )
    return records


def _merge_cursor_agent_provenance(project_root: Path, records: list[dict[str, Any]]) -> None:
    if not records:
        return
    provenance_dir = project_root / _PROVENANCE_DIR
    ledger = provenance_dir / _PROVENANCE_LEDGER_FILENAME
    merged: dict[tuple[int, float], dict[str, Any]] = {}
    try:
        existing = json.loads(ledger.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        existing = []
    if isinstance(existing, list):
        for row in existing:
            if not isinstance(row, dict):
                continue
            try:
                record = {
                    "pid": int(row["pid"]),
                    "create_time_epoch": float(row["create_time_epoch"]),
                    "dispatch_root_pid": int(row["dispatch_root_pid"]),
                }
            except (KeyError, TypeError, ValueError):
                continue
            merged[(record["pid"], record["create_time_epoch"])] = record
    for row in records:
        record = {
            "pid": int(row["pid"]),
            "create_time_epoch": float(row["create_time_epoch"]),
            "dispatch_root_pid": int(row["dispatch_root_pid"]),
        }
        merged[(record["pid"], record["create_time_epoch"])] = record
    try:
        provenance_dir.mkdir(parents=True, exist_ok=True)
        ledger.write_text(
            json.dumps(list(merged.values()), sort_keys=True),
            encoding="utf-8",
        )
    except OSError:
        pass


def _record_new_cursor_agent_provenance(
    project_root: Path,
    before: dict[tuple[int, float], dict[str, Any]],
    *,
    dispatch_root_pid: int,
    started_at_epoch: float,
) -> None:
    after = _cursor_agent_snapshot(project_root)
    records = _cursor_agent_provenance_records(
        before,
        after,
        dispatch_root_pid=dispatch_root_pid,
        started_at_epoch=started_at_epoch,
    )
    _merge_cursor_agent_provenance(project_root, records)


def _cursor_agent_env() -> dict[str, str]:
    """Build the Cursor Agent subprocess environment without logging secrets."""

    env = os.environ.copy()
    try:
        env_values = load_env_local(check_only=True)
    except Exception:  # noqa: BLE001 - auth injection must never block launch
        env_values = {}
    for key in _CURSOR_AUTH_ENV_KEYS:
        value = env_values.get(key, "")
        if value and not env.get(key):
            env[key] = value
    env.setdefault("GTKB_HARNESS_NAME", "cursor")
    env.setdefault("GTKB_HARNESS_ID", "E")
    return env


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB Cursor Agent harness shim.")
    parser.add_argument("-p", "--prompt", required=True, help="Prompt to send to Cursor Agent.")
    parser.add_argument(
        "--skill",
        help="Optional skill route key (for example bridge-review or verification).",
    )
    parser.add_argument(
        "--output-format",
        default="text",
        choices=["text", "json", "stream-json"],
        help="Cursor Agent print-mode output format.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Subprocess timeout in seconds.",
    )
    return parser


def _load_project_env_local() -> None:
    try:
        from scripts._env import load_env_local
    except ImportError:
        from _env import load_env_local  # type: ignore[import-not-found]

    load_env_local()


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    project_root = PROJECT_ROOT
    dispatch_run_id = _dispatcher_run_id()
    dispatch_root_pid = os.getpid()
    cursor_agents_before: dict[tuple[int, float], dict[str, Any]] = {}
    cursor_agent_started_at = time.time()
    should_record_cursor_agents = False
    try:
        _load_project_env_local()
    except Exception:  # noqa: BLE001 - missing/unreadable .env.local must not block harness startup
        pass
    try:
        prompt = _build_prompt(args.prompt, args.skill)
        command = _build_command(prompt, project_root, output_format=args.output_format)
        env = _cursor_agent_env()
        should_record_cursor_agents = bool(dispatch_run_id)
        if should_record_cursor_agents:
            cursor_agents_before = _cursor_agent_snapshot(project_root)
            cursor_agent_started_at = time.time()
        run_kwargs = {
            "cwd": str(project_root),
            "env": env,
            "capture_output": True,
            "text": True,
            "timeout": args.timeout,
            "check": False,
        }
        creationflags = _windows_no_window_creationflags()
        if creationflags:
            run_kwargs["creationflags"] = creationflags
        completed = subprocess.run(command, **run_kwargs)
    except CursorHarnessError as exc:
        print(f"cursor_harness: {exc}", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        if should_record_cursor_agents:
            _record_new_cursor_agent_provenance(
                project_root,
                cursor_agents_before,
                dispatch_root_pid=dispatch_root_pid,
                started_at_epoch=cursor_agent_started_at,
            )
        print("cursor_harness: timed out waiting for Cursor Agent", file=sys.stderr)
        return 1
    if should_record_cursor_agents:
        _record_new_cursor_agent_provenance(
            project_root,
            cursor_agents_before,
            dispatch_root_pid=dispatch_root_pid,
            started_at_epoch=cursor_agent_started_at,
        )
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        if completed.stdout:
            sys.stdout.write(completed.stdout)
        return completed.returncode
    if _requires_bridge_output(args.skill) and not (completed.stdout or "").strip():
        print(
            f"cursor_harness: Cursor Agent produced no stdout for Loyal Opposition bridge skill {args.skill!r}",
            file=sys.stderr,
        )
        return 1
    sys.stdout.write(completed.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
