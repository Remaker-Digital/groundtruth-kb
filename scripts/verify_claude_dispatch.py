#!/usr/bin/env python3
"""Bounded Claude launch checks using the selected native installation record.

Passing these checks establishes neither dispatchability nor complete harness
qualification. An actual prompt launch is opt-in with --live.

c123 (batch design WP2 2.4; owner decisions B1 and B5): the static checks also
read the dispatched permission posture from the registered headless argv
(``permission_posture_problems``: exactly one ``--permission-mode
bypassPermissions``, ``--strict-mcp-config``, no ``--dangerously-skip-permissions``,
WebFetch and WebSearch disallowed, ``--setting-sources project``, and no flag
that skips the hooks) and require every projected ``.claude/settings.json``
hook command to name an interpreter that exists under the root and to run the
Claude hook adapter (``check_projected_hooks``). Under that mode the GT-KB hooks
are the only decider, and a hook that cannot start, or fails without the
adapter, is a non-blocking error in Claude Code: the tool would run unguarded.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError
from groundtruth_kb.harness_invocation import InvocationError, render

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

HARNESS_ID = "B"
HARNESS_NAME = "claude"
HARNESS_TYPE = "claude"
DEFAULT_LIVE_PROMPT = "Reply with READY only."
DEFAULT_TIMEOUT_SECONDS = 60.0

# c123 (owner decision B1): the dispatched permission posture, with owner decision B5's setting sources, spelled as
# `claude --help` lists the flags on Claude Code 2.1.281. Under bypassPermissions the GT-KB hooks decide every governed
# effect; --strict-mcp-config without --mcp-config loads no MCP server; the bare tool names remove WebFetch and
# WebSearch from the session; and --setting-sources project keeps the operator's user and local settings files (their
# hooks, permission rules, plugin entries and instructions) out of a dispatched session. --dangerously-skip-permissions
# is the same mode under a second spelling, and --bare and --safe-mode skip the hooks.
PERMISSION_MODE_FLAG = "--permission-mode"
BYPASS_PERMISSION_MODE = "bypassPermissions"
STRICT_MCP_FLAG = "--strict-mcp-config"
SKIP_PERMISSIONS_FLAG = "--dangerously-skip-permissions"
DISALLOWED_TOOLS_FLAGS = ("--disallowedTools", "--disallowed-tools")
NETWORK_TOOLS = ("WebFetch", "WebSearch")
SETTING_SOURCES_FLAG = "--setting-sources"
DISPATCHED_SETTING_SOURCES = frozenset({"project"})
HOOK_SKIPPING_FLAGS = ("--bare", "--safe-mode")

# c123 (batch design WP2 2.4): the projected hook registration this root's Claude sessions load.
SETTINGS_RELATIVE_PATH = Path(".claude") / "settings.json"
PROJECT_DIR_VARIABLES = ("${CLAUDE_PROJECT_DIR}", "$CLAUDE_PROJECT_DIR")
HOOK_ADAPTER = "scripts/claude_hook_adapter.py"
# c123 (batch design WP2 2.4): the projector's form, "<interpreter>" -B "<adapter>" --deadline N <target> ...
_COMMAND_HEAD = re.compile(r'^\s*"([^"]+)"(?:\s+-B\s+"([^"]+)")?')


class VerificationError(RuntimeError):
    """Raised when Claude readiness cannot be evaluated."""


def _option_values(arguments: Sequence[str], flag: str) -> list[str | None]:
    """The value of every ``flag VALUE`` or ``flag=VALUE``; None for a flag that ends the arguments."""
    values: list[str | None] = []
    for index, part in enumerate(arguments):
        if part == flag:
            values.append(arguments[index + 1] if index + 1 < len(arguments) else None)
        elif part.startswith(flag + "="):
            values.append(part[len(flag) + 1 :])
    return values


def _disallowed_tools(arguments: Sequence[str]) -> tuple[set[str], list[str]]:
    """The tool names the deny lists give, and the placeholders a list takes as tool names.

    The list option is variadic: it takes every following argument up to the next option, so a placeholder there
    (the prompt, the root) would be read as a tool name and never reach Claude Code as itself.
    """
    names: set[str] = set()
    taken: list[str] = []
    for index, part in enumerate(arguments):
        values: list[str] = []
        if part in DISALLOWED_TOOLS_FLAGS:
            for value in arguments[index + 1 :]:
                if value.startswith("-"):
                    break
                values.append(value)
        elif any(part.startswith(flag + "=") for flag in DISALLOWED_TOOLS_FLAGS):
            values.append(part.split("=", 1)[1])
        for value in values:
            if "{{" in value:
                taken.append(value)
            names.update(name for name in re.split(r"[,\s]+", value) if name)
    return names, taken


def permission_posture_problems(argv: Sequence[str]) -> list[str]:
    """What a dispatched Claude argv lacks of the owner-decided posture (B1, B5); empty when it carries all of it."""
    arguments = list(argv[1:])
    problems: list[str] = []
    modes = _option_values(arguments, PERMISSION_MODE_FLAG)
    if not modes:
        problems.append(f"no {PERMISSION_MODE_FLAG} {BYPASS_PERMISSION_MODE}")
    elif len(modes) > 1:
        problems.append(f"{PERMISSION_MODE_FLAG} is given {len(modes)} times")
    elif modes[0] != BYPASS_PERMISSION_MODE:
        problems.append(f"{PERMISSION_MODE_FLAG} is {modes[0]!r}, not {BYPASS_PERMISSION_MODE}")
    if STRICT_MCP_FLAG not in arguments:
        problems.append(f"no {STRICT_MCP_FLAG}")
    if SKIP_PERMISSIONS_FLAG in arguments:
        problems.append(
            f"{SKIP_PERMISSIONS_FLAG} is given (the posture is {PERMISSION_MODE_FLAG} {BYPASS_PERMISSION_MODE} alone)"
        )
    names, taken = _disallowed_tools(arguments)
    missing = [tool for tool in NETWORK_TOOLS if tool not in names]
    if missing:
        verb = "is" if len(missing) == 1 else "are"
        problems.append(
            f"{' and '.join(missing)} {verb} not disallowed ({DISALLOWED_TOOLS_FLAGS[0]} {','.join(NETWORK_TOOLS)})"
        )
    if taken:
        problems.append(f"the {DISALLOWED_TOOLS_FLAGS[0]} list takes {', '.join(taken)} (end it with another option)")
    sources = _option_values(arguments, SETTING_SOURCES_FLAG)
    if not sources:
        problems.append(f"no {SETTING_SOURCES_FLAG} project")
    elif len(sources) > 1:
        problems.append(f"{SETTING_SOURCES_FLAG} is given {len(sources)} times")
    elif {part.strip() for part in (sources[0] or "").split(",") if part.strip()} != DISPATCHED_SETTING_SOURCES:
        problems.append(f"{SETTING_SOURCES_FLAG} is {sources[0]!r}, not project")
    problems.extend(f"{flag} skips the GT-KB hooks" for flag in HOOK_SKIPPING_FLAGS if flag in arguments)
    return problems


def _hook_commands(settings: Any) -> list[str]:
    hooks = settings.get("hooks") if isinstance(settings, dict) else None
    commands: list[str] = []
    for groups in hooks.values() if isinstance(hooks, dict) else []:
        for group in groups if isinstance(groups, list) else []:
            handlers = group.get("hooks") if isinstance(group, dict) else None
            for handler in handlers if isinstance(handlers, list) else []:
                command = handler.get("command") if isinstance(handler, dict) else None
                if isinstance(command, str):
                    commands.append(command)
    return commands


def _root_path(text: str, project_root: Path) -> Path:
    for variable in PROJECT_DIR_VARIABLES:
        text = text.replace(variable, str(project_root))
    path = Path(text)
    return path if path.is_absolute() else project_root / path


def check_projected_hooks(project_root: Path) -> dict[str, Any]:
    """Whether the root's projected Claude hooks can start and fail closed (c123; batch design WP2 2.4).

    Every hook command of ``.claude/settings.json`` must name an interpreter that exists (the projector renders
    ``"$CLAUDE_PROJECT_DIR/groundtruth-kb/.venv/Scripts/pythonw.exe"``, two levels up under an application) and must run
    the Claude hook adapter, which exists. A hook that cannot start, or one that fails without the adapter, is a
    non-blocking error in Claude Code: the tool then runs, unguarded under the dispatched permission mode.
    """
    settings_path = project_root / SETTINGS_RELATIVE_PATH
    report: dict[str, Any] = {
        "settings": str(settings_path),
        "commands": 0,
        "interpreters": [],
        "missing_interpreters": [],
        "unreadable_commands": 0,
        "interpreter_ok": False,
        "adapters": [],
        "missing_adapters": [],
        "without_adapter": 0,
        "adapter_ok": False,
    }
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        report["error"] = "the root has no readable projected .claude/settings.json"
        return report
    commands = _hook_commands(settings)
    report["commands"] = len(commands)
    if not commands:
        report["error"] = "the projected .claude/settings.json registers no hook command"
        return report
    interpreters: set[str] = set()
    adapters: set[str] = set()
    unreadable = without = 0
    for command in commands:
        match = _COMMAND_HEAD.match(command)
        if match is None:
            unreadable += 1
            without += 1
            continue
        interpreters.add(str(_root_path(match.group(1), project_root)))
        script = match.group(2)
        if script is None or not script.replace("\\", "/").endswith("/" + HOOK_ADAPTER):
            without += 1
        else:
            adapters.add(str(_root_path(script, project_root)))
    missing = [path for path in sorted(interpreters) if not Path(path).is_file()]
    missing_adapters = [path for path in sorted(adapters) if not Path(path).is_file()]
    report.update(
        interpreters=sorted(interpreters),
        missing_interpreters=missing,
        unreadable_commands=unreadable,
        interpreter_ok=not missing and not unreadable,
        adapters=sorted(adapters),
        missing_adapters=missing_adapters,
        without_adapter=without,
        adapter_ok=not without and not missing_adapters,
    )
    return report


def _hooks_detail(report: dict[str, Any], *, part: str) -> str:
    """Why the projected hooks fail one part of the check, for first_failed_check."""
    if report.get("error"):
        return str(report["error"])
    if part == "interpreter":
        if report["unreadable_commands"]:
            return (
                f"{report['unreadable_commands']} of {report['commands']} hook commands do not start with a quoted "
                "interpreter path"
            )
        return f"missing {', '.join(report['missing_interpreters'])}"
    if report["without_adapter"]:
        return f"{report['without_adapter']} of {report['commands']} hook commands do not run {HOOK_ADAPTER}"
    return f"missing {', '.join(report['missing_adapters'])}"


def _load_harness_record(project_root: Path, recipient: str = HARNESS_ID) -> dict[str, Any]:
    if not recipient or recipient != recipient.strip():
        raise VerificationError("An exact native installation ID is required")
    try:
        config = GTConfig.load(project_root.resolve() / "groundtruth.toml", discover=False)
        if not config.authority_url:
            raise VerificationError("native_authority_not_configured")
        record = AuthorityClient(config.authority_url, timeout=10).request(
            "GET", f"/v1/harnesses/{quote(recipient, safe='')}"
        )
    except (OSError, GTConfigError, ValueError) as exc:
        raise VerificationError("invalid_selected_configuration") from exc
    except AuthorityClientError as exc:
        raise VerificationError(f"native_harness_read_failed: {exc.code}") from exc
    if not isinstance(record, dict) or record.get("id") != recipient:
        raise VerificationError("invalid_native_harness_response")
    return record


def _headless_argv(record: dict[str, Any]) -> list[str]:
    surfaces = record.get("invocation_surfaces")
    headless = surfaces.get("headless", {}) if isinstance(surfaces, dict) else {}
    argv = headless.get("argv", []) if isinstance(headless, dict) else []
    return argv if isinstance(argv, list) and argv and all(isinstance(part, str) and part for part in argv) else []


def _hidden_process_kwargs() -> dict[str, int]:
    if sys.platform.startswith("win"):
        return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    return {}


def _render_headless_command(
    argv: list[str],
    *,
    project_root: Path,
    prompt: str,
    resolved_executable: str | None,
) -> list[str]:
    # c123 (batch design WP2 2.1): the contract's renderer refuses an unknown or unfilled placeholder. A live probe
    # fills only the prompt and the root, so a template that needs a binding or a bridge item is refused, not guessed.
    command = render(argv, {"PROMPT": prompt, "PROJECT_ROOT": str(project_root)})
    if command and resolved_executable:
        command[0] = resolved_executable
    return command


def _run_live_probe(
    command: list[str],
    *,
    project_root: Path,
    timeout: float,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    active_runner = runner or subprocess.run
    completed = active_runner(
        command,
        cwd=project_root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        **_hidden_process_kwargs(),
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    return {
        "ok": completed.returncode == 0 and bool(stdout.strip()),
        "returncode": completed.returncode,
        "stderr_bytes": len(stderr.encode("utf-8")),
        "stdout_bytes": len(stdout.encode("utf-8")),
    }


def evaluate_readiness(
    *,
    project_root: Path,
    recipient: str = HARNESS_ID,
    require_executable: bool = True,
    executable_resolver: Callable[[str], str | None] | None = None,
    require_live: bool = False,
    live_prompt: str = DEFAULT_LIVE_PROMPT,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    live_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> dict[str, Any]:
    if not math.isfinite(timeout) or timeout <= 0:
        raise VerificationError("timeout must be finite and positive")
    record = _load_harness_record(project_root, recipient)
    if record.get("harness_type") != HARNESS_TYPE:
        raise VerificationError(f"recipient {recipient} is not {HARNESS_TYPE}: {record.get('harness_type')!r}")

    argv = _headless_argv(record)
    resolver = executable_resolver or shutil.which
    resolved_executable = resolver(argv[0]) if argv else None
    executable_ok = bool(resolved_executable) if require_executable else True
    # c123 (batch design WP2 2.4): the registered posture (owner decisions B1 and B5), then the hooks it relies on.
    posture = permission_posture_problems(argv) if argv else []
    hooks = check_projected_hooks(project_root)
    checks = [
        {"name": "headless argv", "passed": bool(argv)},
        {"name": "headless executable", "passed": executable_ok},
        {"name": "permission posture", "passed": bool(argv) and not posture},
        {"name": "hook interpreter", "passed": hooks["interpreter_ok"]},
        {"name": "hook adapter", "passed": hooks["adapter_ok"]},
    ]
    static_ok = all(check["passed"] for check in checks)
    live_probe: dict[str, Any] | None = None
    live_ok = True
    live_detail = ""
    if require_live and static_ok:
        try:
            command = _render_headless_command(
                argv,
                project_root=project_root,
                prompt=live_prompt,
                resolved_executable=resolved_executable,
            )
            live_probe = _run_live_probe(
                command,
                project_root=project_root,
                timeout=timeout,
                runner=live_runner,
            )
            live_ok = bool(live_probe["ok"])
            live_detail = f"returncode={live_probe['returncode']}; stdout_bytes={live_probe['stdout_bytes']}"
        except (InvocationError, OSError, subprocess.SubprocessError, subprocess.TimeoutExpired) as exc:
            live_probe = {"ok": False, "error": type(exc).__name__}
            live_ok = False
            live_detail = live_probe["error"]
    elif require_live:
        live_ok = False
        live_detail = "skipped because static readiness failed"
    if require_live:
        checks.append({"name": "live claude prompt probe", "passed": live_ok})
    probe_passed = static_ok and live_ok
    first_failed_check = ""
    if not argv:
        first_failed_check = "headless argv: missing"
    elif not executable_ok:
        first_failed_check = "headless executable: unresolved"
    elif posture:
        first_failed_check = f"permission posture: {'; '.join(posture)}"
    elif not hooks["interpreter_ok"]:
        first_failed_check = f"hook interpreter: {_hooks_detail(hooks, part='interpreter')}"
    elif not hooks["adapter_ok"]:
        first_failed_check = f"hook adapter: {_hooks_detail(hooks, part='adapter')}"
    elif require_live and not live_ok:
        first_failed_check = f"live claude prompt probe: {live_detail or 'failed'}"
    return {
        "probe_scope": "launch_prerequisites_and_bounded_prompt" if require_live else "launch_prerequisites",
        "harness_qualification": "unqualified",
        "authority_source": "native_harness_record",
        "checks": checks,
        "executable_ok": executable_ok,
        "first_failed_check": first_failed_check,
        "harness_id": recipient,
        "harness_name": record.get("harness_name"),
        "live_probe": live_probe,
        "permission_posture": {"ok": bool(argv) and not posture, "problems": posture},
        "probe_passed": probe_passed,
        "projected_hooks": hooks,
        "require_executable": require_executable,
        "require_live": require_live,
        "resolved_executable": resolved_executable,
        "static_ok": static_ok,
        "status": record.get("status"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipient", default=HARNESS_ID)
    parser.add_argument("--project-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--no-require-executable", action="store_true")
    parser.add_argument("--live", action="store_true", help="Run a bounded non-mutating Claude prompt probe.")
    parser.add_argument("--prompt", default=DEFAULT_LIVE_PROMPT)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = evaluate_readiness(
            project_root=args.project_root.resolve(),
            recipient=args.recipient,
            require_executable=not args.no_require_executable,
            require_live=args.live,
            live_prompt=args.prompt,
            timeout=args.timeout,
        )
    except VerificationError as exc:
        payload = {"error": str(exc), "harness_id": args.recipient, "static_ok": False}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"static_ok={result['static_ok']}")
        print(f"probe_passed={result['probe_passed']}")
        print(f"first_failed_check={result['first_failed_check']}")
        print(f"harness_qualification={result['harness_qualification']}")
        print(f"resolved_executable={result['resolved_executable']}")
    return 0 if result["probe_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
