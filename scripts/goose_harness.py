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
import subprocess
import sys
import time
from collections.abc import Sequence
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
DEFAULT_MAX_TURNS = 40
DEFAULT_TIMEOUT_SECONDS = 3600.0
DEFAULT_SESSION_TIMEOUT_SECONDS = 5400.0
GOOSE_CLI = "goose"


class GooseHarnessError(RuntimeError):
    """Raised for fail-closed harness errors."""


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
    parser.add_argument("--model", help="Routing model key from .api-harness/routing.toml.")
    parser.add_argument("--skill", help="Skill or task route key from .api-harness/routing.toml.")
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


def build_system_prompt(skill: str | None) -> str | None:
    """Build additional system instructions for the given skill."""
    if not skill:
        return None

    skill_prompts = {
        "bridge-review": (
            "You are acting as Loyal Opposition for GT-KB bridge review. "
            "Your task is to review bridge proposals and file GO/NO-GO/VERIFIED verdicts. "
            "Follow the file-bridge-protocol.md: read the proposal, evaluate it, "
            "run verification, and write a verdict file in bridge/ with the appropriate status token. "
            "Be thorough, evidence-based, and fail-closed when uncertain."
        ),
        "verification": (
            "You are acting as Loyal Opposition for GT-KB verification. "
            "Your task is to verify implementation reports against their proposals. "
            "Run pytest, ruff, and other verification commands. "
            "File VERIFIED or NO-GO verdicts with evidence."
        ),
        "implementation": (
            "You are acting as Prime Builder for GT-KB implementation. "
            "Your task is to implement approved proposals. "
            "Follow the bridge GO conditions, write implementation reports, "
            "and run verification before filing."
        ),
    }
    return skill_prompts.get(skill)


def _load_floor_config(project_root: Path) -> ExecutionFloorConfig:
    """Load the execution reliability floor configuration."""
    config_path = project_root / "config" / "agent-control" / "goose-execution-floor.toml"
    return ExecutionFloorConfig.from_toml(config_path)


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_arg_parser()
    args = parser.parse_args(raw_argv)

    project_root = Path(args.project_root).resolve() if args.project_root else resolve_project_root()

    # WI-5831: Export live model configuration before spawning the child.
    # This ensures the child environment carries the spawn model identity
    # for provenance-guard comparison.
    export_model_configuration(args.model or "")

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

    # Inject skill-specific system instructions
    system_prompt = build_system_prompt(args.skill)
    if system_prompt:
        cmd.extend(["--system", system_prompt])

    # Override model if specified
    if args.model:
        cmd.extend(["--model", args.model])

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
    floor_config = _load_floor_config(project_root)
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
