#!/usr/bin/env python3
"""Headless Cursor Agent harness shim for GT-KB bridge dispatch."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any

from groundtruth_kb.local_env import load_env_local

DEFAULT_TIMEOUT_SECONDS = 600.0
TIMEOUT_EXIT_CODE = 124
LOYAL_OPPOSITION_BRIDGE_SKILLS = frozenset({"bridge-review", "verification"})
# WI-4933: the harness-registry Cursor invocation surfaces pass canonical
# Loyal Opposition route keys ('bridge-review', 'verification'), but no SKILL.md
# exists under those names. Resolve them to the real skill directories so
# headless LO dispatch loads the bridge/verification contracts instead of
# failing closed or loading a generic review memo contract.
_SKILL_ROUTE_ALIASES = {
    "bridge-review": "proposal-review",
    "verification": "verify",
}
_CURSOR_GUI_LAUNCHER_NAMES = {"cursor", "cursor.cmd", "cursor.exe"}
_STANDALONE_AGENT_NAMES = ("agent", "cursor-agent")
_STANDALONE_AGENT_EXECUTABLE_NAMES = {
    "agent",
    "agent.cmd",
    "agent.exe",
    "cursor-agent",
    "cursor-agent.cmd",
    "cursor-agent.exe",
}
_WINDOWS_SHELL_WRAPPER_SUFFIXES = {".bat", ".cmd", ".ps1"}
_CURSOR_AGENT_HELP_TIMEOUT_SECONDS = 10.0
_CURSOR_AUTH_ENV_KEYS = ("CURSOR_API_KEY",)
_CURSOR_ADAPTATION_VERSION = "cursor-native-cli-v1"
_TIMEOUT_CAPTURE_LIMIT_BYTES = 4000
_TIMEOUT_CAPTURE_SECRET_PATTERNS = (
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*([A-Za-z0-9._~+/=-]{8,})"),
)


class CursorHarnessError(RuntimeError):
    """Raised for fail-closed Cursor harness errors."""


def _windows_no_window_creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def _cursor_supports_agent_subcommand(cursor_executable: str) -> bool:
    executable_name = Path(cursor_executable).name.lower()
    if executable_name in _CURSOR_GUI_LAUNCHER_NAMES:
        return False
    if executable_name not in _STANDALONE_AGENT_EXECUTABLE_NAMES:
        return False
    try:
        completed = subprocess.run(
            [cursor_executable, "agent", "--help"],
            capture_output=True,
            text=True,
            timeout=_CURSOR_AGENT_HELP_TIMEOUT_SECONDS,
            check=False,
            creationflags=_windows_no_window_creationflags(),
        )
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
            raise CursorHarnessError(
                "Cursor Agent CLI not found. CURSOR_AGENT_BIN points at a Cursor GUI launcher; set it to "
                "a standalone `agent` or `cursor-agent` executable."
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
    for wrapper_candidate in _windows_cursor_agent_candidates():
        if wrapper_candidate.is_file():
            return [str(wrapper_candidate)]
    raise CursorHarnessError(
        "Cursor Agent CLI not found. Ensure standalone `agent` or `cursor-agent` is on PATH, or set "
        "CURSOR_AGENT_BIN to a standalone agent executable."
    )


def _skill_system_prompt(skill: str | None, *, project_root: Path | None = None) -> str | None:
    if not skill:
        return None
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", skill):
        raise CursorHarnessError("invalid skill route")
    names = ("bridge", _SKILL_ROUTE_ALIASES[skill]) if skill in _SKILL_ROUTE_ALIASES else (skill,)
    skills_root = (project_root or Path.cwd()) / ".cursor" / "skills"
    instructions = []
    for name in names:
        skill_path = skills_root / name / "SKILL.md"
        if (
            skills_root.is_symlink()
            or skills_root.is_junction()
            or not skill_path.resolve().is_relative_to(skills_root.absolute())
        ):
            raise CursorHarnessError("skill route leaves this harness's skill directory")
        try:
            content = skill_path.read_text(encoding="utf-8")
            if not content.strip():
                raise CursorHarnessError(f"empty skill route {name!r}; refresh this harness's projection")
            instructions.append(content)
        except (OSError, UnicodeError) as exc:
            raise CursorHarnessError(
                f"unknown or unreadable skill route {name!r}; refresh this harness's projection"
            ) from exc
    return "\n\n".join(instructions)


def _build_prompt(user_prompt: str, skill: str | None, *, project_root: Path | None = None) -> str:
    system_prompt = _skill_system_prompt(skill, project_root=project_root)
    prompt = user_prompt
    if system_prompt:
        prompt = (
            "Follow the GT-KB skill contract below, then execute the user task.\n\n"
            f"{system_prompt}\n\n---\n\n{user_prompt}"
        )
    return prompt


def _sha256_file(path: Path) -> str:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "missing"


def cursor_adaptation_metadata(project_root: Path | None = None) -> dict[str, Any]:
    """Return content-free identities of the selected shim and loaded implementation."""

    shim_path = (project_root or Path.cwd()) / "scripts" / "cursor_harness.py"
    return {
        "harness_id": "E",
        "adaptation_label": "cursor-native-cli",
        "adaptation_version": _CURSOR_ADAPTATION_VERSION,
        "skill_route_aliases": dict(sorted(_SKILL_ROUTE_ALIASES.items())),
        "input_fingerprints": {
            "scripts/cursor_harness.py": _sha256_file(shim_path),
            "groundtruth_kb/cursor_harness.py": _sha256_file(Path(__file__)),
            "groundtruth_kb/local_env.py": _sha256_file(Path(__file__).with_name("local_env.py")),
            "skill-route-aliases": "sha256:"
            + hashlib.sha256(
                json.dumps(_SKILL_ROUTE_ALIASES, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
        },
        "raw_prompt_included": False,
    }


def _build_command(
    prompt: str,
    project_root: Path,
    *,
    output_format: str,
    mode: str | None = None,
) -> list[str]:
    command = _resolve_agent_command()
    command.extend(
        [
            "-p",
            "--trust",
            "--workspace",
            str(project_root),
            "--output-format",
            output_format,
        ]
    )
    if mode is not None:
        command.extend(["--mode", mode])
    command.append(prompt)
    return command


def _requires_bridge_output(skill: str | None) -> bool:
    return skill in LOYAL_OPPOSITION_BRIDGE_SKILLS


# WI-6541: the local envelope-marker prefix tuple was removed with the local
# head parser. Envelope-marker recognition now lives solely in
# ``groundtruth_kb.bridge.versioned_files.parse_bridge_header_block``.


def _cursor_agent_env(*, project_root: Path) -> dict[str, str]:
    """Build the Cursor Agent subprocess environment without logging secrets."""

    env = os.environ.copy()
    try:
        env_values = load_env_local(check_only=True, env_file=project_root / ".env.local")
    except Exception:  # noqa: BLE001  # intentional-catch: auth injection must never block launch
        env_values = {}
    for key in _CURSOR_AUTH_ENV_KEYS:
        value = env_values.get(key, "")
        if value and not env.get(key):
            env[key] = value
    env.setdefault("GTKB_HARNESS_NAME", "cursor")
    env.setdefault("GTKB_HARNESS_ID", "E")
    env.setdefault("GTKB_AUTHOR_MODEL", "Composer")
    env.setdefault("GTKB_AUTHOR_MODEL_VERSION", "cursor-agent")
    env.setdefault(
        "GTKB_AUTHOR_MODEL_CONFIGURATION",
        "Cursor headless dispatch; cursor_harness.py; bridge author metadata runtime envelope",
    )
    return env


def _timeout_capture_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _redact_timeout_capture(text: str) -> str:
    redacted = text
    for pattern in _TIMEOUT_CAPTURE_SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}=[REDACTED]", redacted)
    return redacted


def _bounded_timeout_capture(value: object, *, label: str) -> str:
    text = _redact_timeout_capture(_timeout_capture_text(value))
    if not text:
        return ""
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= _TIMEOUT_CAPTURE_LIMIT_BYTES:
        return text
    truncated = encoded[:_TIMEOUT_CAPTURE_LIMIT_BYTES].decode("utf-8", errors="replace")
    return (
        f"{truncated}\n"
        f"[cursor_harness: partial {label} truncated to {_TIMEOUT_CAPTURE_LIMIT_BYTES} "
        f"bytes from {len(encoded)} bytes]\n"
    )


def _timeout_stdout(exc: subprocess.TimeoutExpired) -> object:
    return getattr(exc, "stdout", None) if getattr(exc, "stdout", None) is not None else getattr(exc, "output", None)


def _timeout_diagnostic(
    *,
    timeout_seconds: float,
    skill: str | None,
    output_format: str,
    mode: str | None,
    command: list[str],
    stdout_text: str,
    stderr_text: str,
) -> str:
    executable = Path(command[0]).name if command else "<unknown>"
    stdout_bytes = len(stdout_text.encode("utf-8", errors="replace"))
    stderr_bytes = len(stderr_text.encode("utf-8", errors="replace"))
    return (
        "cursor_harness: Cursor Agent timed out "
        f"after {timeout_seconds:g}s; exit={TIMEOUT_EXIT_CODE}; executable={executable}; "
        f"skill={skill or '<none>'}; output_format={output_format}; mode={mode or '<default>'}; "
        f"partial_stdout_bytes={stdout_bytes}; partial_stderr_bytes={stderr_bytes}"
    )


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
    parser.add_argument(
        "--mode",
        choices=["plan", "ask"],
        help="Optional read-only Cursor execution mode.",
    )
    return parser


def _load_project_env_local(*, project_root: Path) -> None:
    load_env_local(project_root=project_root)


def main(argv: list[str] | None = None, *, project_root: Path | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    project_root = (project_root or Path.cwd()).resolve()
    # intentional-catch: retain optional environment-loading failure behavior at startup.
    with suppress(Exception):
        _load_project_env_local(project_root=project_root)
    effective_output_format, effective_mode = args.output_format, args.mode
    try:
        prompt = _build_prompt(args.prompt, args.skill, project_root=project_root)
        command = _build_command(
            prompt,
            project_root,
            output_format=effective_output_format,
            mode=effective_mode,
        )
        env = _cursor_agent_env(project_root=project_root)
        completed = subprocess.run(
            command,
            cwd=str(project_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
            creationflags=_windows_no_window_creationflags(),
        )
    except CursorHarnessError as exc:
        sys.stderr.write(f"cursor_harness: {exc}\n")
        return 1
    except subprocess.TimeoutExpired as exc:
        stdout_text = _bounded_timeout_capture(_timeout_stdout(exc), label="stdout")
        stderr_text = _bounded_timeout_capture(getattr(exc, "stderr", None), label="stderr")
        if stdout_text:
            sys.stdout.write(stdout_text)
            if not stdout_text.endswith("\n"):
                sys.stdout.write("\n")
        if stderr_text:
            sys.stderr.write(stderr_text)
            if not stderr_text.endswith("\n"):
                sys.stderr.write("\n")
        sys.stderr.write(
            _timeout_diagnostic(
                timeout_seconds=float(args.timeout),
                skill=args.skill,
                output_format=effective_output_format,
                mode=effective_mode,
                command=command,
                stdout_text=stdout_text,
                stderr_text=stderr_text,
            )
            + "\n"
        )
        return TIMEOUT_EXIT_CODE
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    if completed.returncode != 0:
        if completed.stdout:
            sys.stdout.write(completed.stdout)
        return completed.returncode
    if _requires_bridge_output(args.skill) and not (completed.stdout or "").strip():
        sys.stderr.write(
            f"cursor_harness: Cursor Agent produced no stdout for Loyal Opposition bridge skill {args.skill!r}\n"
        )
        return 1
    sys.stdout.write(completed.stdout)
    return 0
