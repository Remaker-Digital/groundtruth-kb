#!/usr/bin/env python3
"""Headless Goose dispatch harness for GT-KB.

Wraps `goose run` CLI to provide a provider-harness-compatible interface
for the Alibaba-hosted DeepSeek V4 Pro model via the Goose desktop CLI.

Phase 1: thin CLI wrapper. Phase 2 target: direct Alibaba API harness.
WI-5831 (Goose Execution Reliability Floor): integrates the execution guard
for write verification, leak detection, and provenance-drift detection.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import tomllib
from collections.abc import Mapping, Sequence
from pathlib import Path

from goose_execution_guard import (
    ExecutionFloorConfig,
    RunDiagnostic,
    evaluate_run,
    export_model_configuration,
)
from windows_subprocess import no_window_subprocess_kwargs

AUTHOR_IDENTITY = "Goose G"
AUTHOR_HARNESS_ID = "G"
# GT-KB context identity is owned by the Goose host (its own session id reaches the
# hooks); a value inherited from the launching process is never passed on.
CONTEXT_IDENTITY_VARIABLES = ("GTKB_AUTHOR_SESSION_CONTEXT_ID", "GTKB_NATIVE_CONTEXT_ID")
DEFAULT_MAX_TURNS = 40
DEFAULT_TIMEOUT_SECONDS = 3600.0
DEFAULT_SESSION_TIMEOUT_SECONDS = 5400.0
GOOSE_CLI = "goose"
# Canonical execution-floor contract (neutral baseline); there is no second
# configuration tree and no silent fallback when the file is absent.
FLOOR_CONFIG_RELATIVE_PATH = Path(".harness-baseline-configuration") / "goose-execution-floor.toml"
PROFILES_RELATIVE_PATH = Path("scripts") / "harness_projection" / "profiles.toml"
ROUTING_RELATIVE_PATH = Path(".harness-baseline-configuration") / "routing.toml"


class GooseHarnessError(RuntimeError):
    """Raised for fail-closed harness errors."""


def child_environment(env: Mapping[str, str] | None = None) -> dict[str, str]:
    """Environment for the Goose child: harness and model metadata, no inherited context identity, no role."""
    child = dict(os.environ if env is None else env)
    for name in CONTEXT_IDENTITY_VARIABLES:
        child.pop(name, None)
    return child


def _find_goose_cli() -> str:
    """Locate the goose CLI binary."""
    # Try the known install path first
    known = Path("C:/Users/micha/OneDrive/Desktop/goose-dist-windows/resources/bin/goose.exe")
    if known.exists():
        return str(known)
    # Fall back to PATH
    return GOOSE_CLI


def resolve_project_root(start: Path | None = None) -> Path:
    start = Path(start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "groundtruth.toml").exists():
            return candidate
    return start


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB Goose harness shim (Alibaba DeepSeek V4 Pro).")
    parser.add_argument("-p", "--prompt", required=True, help="User prompt to send to Goose.")
    parser.add_argument(
        "--model",
        help="Routing model key from .harness-baseline-configuration/routing.toml; its model_id reaches goose run.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=DEFAULT_MAX_TURNS,
        help="Maximum tool loop turns.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Subprocess timeout in seconds.",
    )
    parser.add_argument(
        "--session-timeout",
        type=float,
        default=DEFAULT_SESSION_TIMEOUT_SECONDS,
        help="Maximum wall-clock seconds for the whole harness run.",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Project root directory (default: auto-detect).",
    )
    return parser


def resolve_goose_model(project_root: Path, route_key: str) -> str:
    """The model_id Goose receives for a registered route key (c123; batch design WP2 2.2).

    The key must name a [models.<key>] row of routing.toml whose provider is goose; any other key fails closed, as the
    API launchers' resolve_model does, so a free-text name never reaches ``goose run --model``. The role-specific
    system prompts this shim used to inject are gone (WP2 2.1): a role comes only from the context's binding.
    """
    try:
        routing = tomllib.loads((project_root / ROUTING_RELATIVE_PATH).read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise GooseHarnessError(f"routing config is unreadable: {exc}") from exc
    models = routing.get("models")
    row = models.get(route_key) if isinstance(models, dict) else None
    if not isinstance(row, dict) or row.get("provider") != "goose":
        raise GooseHarnessError(f"unknown model route: {route_key}")
    model_id = row.get("model_id")
    if not isinstance(model_id, str) or not model_id:
        raise GooseHarnessError(f"models.{route_key}.model_id must be a non-empty string")
    return model_id


def _load_floor_config(project_root: Path) -> ExecutionFloorConfig:
    """Load the execution reliability floor from the canonical baseline file.

    The harness refuses to run without the file: the guard's built-in values are
    schema defaults for absent keys, not a substitute for the contract.
    """
    config_path = project_root / FLOOR_CONFIG_RELATIVE_PATH
    if not config_path.is_file():
        raise GooseHarnessError(f"execution floor configuration is absent: {config_path}")
    return ExecutionFloorConfig.from_toml(config_path)


def require_hook_interpreter(project_root: Path, env: Mapping[str, str]) -> str:
    """Resolve the Goose profile's declared hook interpreter on the child's PATH (observer B74).

    Goose runs every GT-KB hook command through it. When it is missing every hook fails at spawn and Goose 1.45.0
    lets each tool call run, before any GT-KB code could answer, so a session started without it would be unenforced.
    The launcher refuses instead.
    """
    try:
        profiles = tomllib.loads((project_root / PROFILES_RELATIVE_PATH).read_text(encoding="utf-8"))
        interpreter = profiles["harnesses"]["goose"].get("hook_interpreter")
    except (OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        raise GooseHarnessError(f"the Goose projection profile is unreadable: {exc}") from exc
    if not isinstance(interpreter, str) or not interpreter:
        raise GooseHarnessError("the Goose projection profile declares no hook interpreter")
    path = next((value for key, value in env.items() if key.upper() == "PATH"), "")
    resolved = shutil.which(interpreter, path=path)
    if resolved is None:
        raise GooseHarnessError(
            f"Goose runs GT-KB's hooks through {interpreter!r}, which is not on PATH; without it every hook fails and "
            "every tool call would run unenforced, so the session is refused (on Windows, Git for Windows' usr\\bin "
            f"supplies {interpreter}.exe)"
        )
    return resolved


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_arg_parser()
    args = parser.parse_args(raw_argv)

    project_root = Path(args.project_root).resolve() if args.project_root else resolve_project_root()

    # WI-5831: Resolve the execution reliability floor before spawning the
    # child so an absent contract fails here, not after a model run.
    try:
        floor_config = _load_floor_config(project_root)
        # Observer B74: refuse a session whose hooks could not run, before any model call.
        require_hook_interpreter(project_root, child_environment())
        # c123 (batch design WP2 2.2): a registered --model is a routing key; Goose receives its model_id.
        model_id = resolve_goose_model(project_root, args.model) if args.model else None
    except GooseHarnessError as exc:
        print(f"goose_harness: {exc}", file=sys.stderr)
        return 1

    # WI-5831: Export live model configuration before spawning the child.
    # This ensures the child environment carries the spawn model identity
    # for provenance-guard comparison.
    export_model_configuration(model_id or "")

    goose_cli = _find_goose_cli()

    # Build the goose run command
    cmd = [
        goose_cli,
        "run",
        "--no-session",
        "--quiet",
        "--output-format",
        "json",
        "--max-turns",
        str(args.max_turns),
        "--text",
        args.prompt,
    ]

    # Override model if specified (the routing row's model_id; no role-specific system prompt is injected).
    if model_id:
        cmd.extend(["--model", model_id])

    # WI-5831: Record the spawn window start for run-window sweep and
    # provenance-guard time-bounding.
    window_start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            cwd=str(project_root),
            env=child_environment(),
            # WI-5071: goose (harness G) is a dispatch target; a console-less
            # dispatched grandchild would otherwise pop a visible console for
            # the goose CLI. Every sibling harness launcher applies this.
            **no_window_subprocess_kwargs(),
        )
    except subprocess.TimeoutExpired:
        print(
            f"goose_harness: timed out after {args.timeout}s",
            file=sys.stderr,
        )
        return 1
    except FileNotFoundError:
        print(
            f"goose_harness: goose CLI not found at {goose_cli}",
            file=sys.stderr,
        )
        return 1

    # WI-5831: Record the spawn window end.
    window_end = time.time()

    if result.returncode != 0:
        print(
            f"goose_harness: goose run exited {result.returncode}: {result.stderr[:500]}",
            file=sys.stderr,
        )
        return 1

    # Parse JSON output and extract final assistant text
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(
            f"goose_harness: failed to parse goose output: {exc}",
            file=sys.stderr,
        )
        return 1

    messages = data.get("messages", [])
    if not messages:
        print("goose_harness: no messages in goose output", file=sys.stderr)
        return 1

    # WI-5831: Run the execution reliability floor guard after payload parsing
    # but before returning. This runs every enabled check and emits structured
    # diagnostics on stderr if findings are detected.
    diagnostic: RunDiagnostic = evaluate_run(
        data,
        project_root,
        floor_config,
        window_start=window_start,
        window_end=window_end,
        max_turns=args.max_turns,
    )

    if diagnostic.findings:
        print(diagnostic.to_json(), file=sys.stderr)
        # Still extract and print assistant text so the caller sees the content,
        # but exit with the diagnostic's non-zero code.
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", [])
                text_blocks = [
                    block.get("text", "")
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if text_blocks:
                    print("\n".join(text_blocks))
                    break
        return diagnostic.exit_code

    # Extract the final assistant text message
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            content = msg.get("content", [])
            text_blocks = [
                block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
            ]
            if text_blocks:
                print("\n".join(text_blocks))
                return 0

    print("goose_harness: no assistant text in goose output", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
