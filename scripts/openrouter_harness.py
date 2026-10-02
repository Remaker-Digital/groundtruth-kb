#!/usr/bin/env python3
"""Stdlib OpenRouter harness shim for GT-KB Phase 1.

Re-based (cloud-harness template slice 2, WI-5078) onto the shared, config-driven
``cloud_harness_base`` runtime per ``ADR-CLOUD-HARNESS-TEMPLATE-001``. This module is
now the OpenRouter *adopter*: it declares the OpenRouter :class:`AdopterProfile`
(direct-cloud endpoint, ``GTKB_OPENROUTER_API_KEY`` token auth via an Authorization header, falling back to the
conventional ``OPENROUTER_API_KEY``,
``openai-chat`` dialect, guard-adapter hook tier) and provides the CLI entry point.
All connection/retry/guard/author-metadata/tool-loop machinery lives in
``cloud_harness_base``; the thin wrappers below preserve this module's historical public
surface (used by the OpenRouter regression tests) while delegating to the base.
"""

from __future__ import annotations

import argparse
import json  # noqa: F401  (re-exported: tests monkeypatch/reference `openrouter_harness.json`)
import os
import ssl  # noqa: F401  (re-exported: tests reference `openrouter_harness.ssl`)
import sys
import time  # noqa: F401  (re-exported: tests monkeypatch `openrouter_harness.time`)
import urllib.error  # noqa: F401  (re-exported: tests build/patch `openrouter_harness.urllib`)
import urllib.request  # noqa: F401
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    import cloud_harness_base as base
except ModuleNotFoundError:  # pragma: no cover
    from scripts import cloud_harness_base as base

# --- Re-exported machinery + shared types (preserve the historical public surface) ---
OpenRouterHarnessError = base.CloudHarnessError
FileScanLimitExceeded = base.FileScanLimitExceeded
ModelRoute = base.ModelRoute
RoutingConfig = base.RoutingConfig
ModelMetadata = base.ModelMetadata
GuardExecutionResult = base.GuardExecutionResult
GuardRunner = base.GuardRunner
ChatFunc = base.ChatFunc
CommandRunner = base.CommandRunner

infer_model_version = base.infer_model_version
resolve_model = base.resolve_model
resolve_runtime_limits = base.resolve_runtime_limits
resolve_project_root = base.resolve_project_root
ensure_utf8_output_streams = base.ensure_utf8_output_streams
build_tool_schemas = base.build_tool_schemas
_relative_path = base._relative_path
_relative_path_or_none = base._relative_path_or_none
_iter_text_files = base._iter_text_files
_iter_bounded_paths = base._iter_bounded_paths
_metadata_from_response = None  # defined as a profile-bound wrapper below

# --- Re-exported constants ---
DEFAULT_TIMEOUT_SECONDS = base.DEFAULT_TIMEOUT_SECONDS
DEFAULT_SESSION_TIMEOUT_SECONDS = base.DEFAULT_SESSION_TIMEOUT_SECONDS
DEFAULT_MAX_TURNS = base.DEFAULT_MAX_TURNS
CHAT_MAX_ATTEMPTS = base.CHAT_MAX_ATTEMPTS
CHAT_RETRY_BACKOFF_SECONDS = base.CHAT_RETRY_BACKOFF_SECONDS
RETRYABLE_HTTP_STATUS = base.RETRYABLE_HTTP_STATUS
RETRYABLE_PROVIDER_TRANSPORT_MARKERS = base.RETRYABLE_PROVIDER_TRANSPORT_MARKERS
MAX_TOOL_OUTPUT_CHARS = base.MAX_TOOL_OUTPUT_CHARS
MAX_GREP_RESULTS = base.MAX_GREP_RESULTS
MAX_GLOB_RESULTS = base.MAX_GLOB_RESULTS
MAX_FILE_SCAN_ENTRIES = base.MAX_FILE_SCAN_ENTRIES
MAX_REPEATED_TOOL_SIGNATURE_TURNS = base.MAX_REPEATED_TOOL_SIGNATURE_TURNS
SKIPPED_SCAN_DIR_NAMES = base.SKIPPED_SCAN_DIR_NAMES
CANONICAL_TOOLS = base.CANONICAL_TOOLS
MUTATING_TOOLS = base.MUTATING_TOOLS
ROUTING_CONFIG_PATH = Path(".harness-baseline-configuration/routing.toml")
NATIVE_HOOK_SETTINGS_PATH = Path(".api-harness/openrouter/settings.json")

BRIDGE_WRITE_GUARDS = base.BRIDGE_WRITE_GUARDS
BRIDGE_EDIT_GUARDS = base.BRIDGE_EDIT_GUARDS
WRITE_EDIT_GUARDS = base.WRITE_EDIT_GUARDS
BASH_GUARDS = base.BASH_GUARDS

# --- OpenRouter adopter specifics (the varying axes) ---
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1"
AUTHOR_IDENTITY = "OpenRouter F"
AUTHOR_HARNESS_ID = "F"
_OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://github.com/mike-remakerdigital/groundtruth-kb",
    "X-Title": "GT-KB OpenRouter Harness",
}

_OPENROUTER_PROFILE = base.AdopterProfile(
    display_name="OpenRouter",
    author_identity=AUTHOR_IDENTITY,
    author_harness_id=AUTHOR_HARNESS_ID,
    default_endpoint=DEFAULT_ENDPOINT,
    auth_env_key="GTKB_OPENROUTER_API_KEY",
    provider_routing_key="openrouter",
    routing_config_path=ROUTING_CONFIG_PATH,
    native_hook_settings_path=NATIVE_HOOK_SETTINGS_PATH,
    dialect=base.DIALECT_OPENAI_CHAT,
    hook_tier=base.HOOK_TIER_NATIVE_FULL,
    extra_headers=_OPENROUTER_HEADERS,
)


def load_routing_config(project_root: Path) -> RoutingConfig:
    return base.load_routing_config(project_root, provider_key="openrouter", config_path=ROUTING_CONFIG_PATH)


def call_openrouter_chat(
    endpoint: str, api_key: str, payload: dict[str, Any], timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> dict[str, Any]:
    """The OpenRouter ``openai-chat`` dialect binding of the shared transport."""
    return base.openai_chat_completion(
        endpoint, api_key, payload, timeout, label="OpenRouter", extra_headers=_OPENROUTER_HEADERS
    )


def set_author_metadata_env(
    env: Mapping[str, str],
    model_id: str,
    model_version: str,
    endpoint: str = DEFAULT_ENDPOINT,
    model_configuration: str | None = None,
    *,
    native_context_id: str,
) -> dict[str, str]:
    return base.set_author_metadata_env(
        env,
        model_id,
        model_version,
        _OPENROUTER_PROFILE,
        endpoint,
        model_configuration,
        native_context_id=native_context_id,
    )


def _metadata_from_response(metadata: ModelMetadata, response: Mapping[str, Any]) -> ModelMetadata:  # noqa: F811
    return base.metadata_from_response(metadata, response, _OPENROUTER_PROFILE)


def invoke_guard_adapter(
    tool_name: str,
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    *,
    guard_runner: GuardRunner | None = None,
    guard_paths: Sequence[Path] | None = None,
    timeout: float = 10.0,
) -> None:
    base.invoke_guard_adapter(
        tool_name,
        arguments,
        model_metadata,
        project_root,
        _OPENROUTER_PROFILE,
        guard_runner=guard_runner,
        guard_paths=guard_paths,
        timeout=timeout,
    )


def dispatch_tool_call(
    tool_name: str,
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    *,
    guard_runner: GuardRunner | None = None,
    command_runner: CommandRunner | None = None,
) -> str:
    # Thread this module's (monkeypatchable) collaborators so tests that patch
    # ``openrouter_harness._relative_path`` / ``._iter_text_files`` still take effect.
    return base.dispatch_tool_call(
        tool_name,
        arguments,
        model_metadata,
        project_root,
        _OPENROUTER_PROFILE,
        guard_runner=guard_runner,
        command_runner=command_runner,
        relative_path=_relative_path,
        iter_text_files=_iter_text_files,
        iter_bounded_paths=_iter_bounded_paths,
    )


def run_tool_loop(
    prompt: str,
    model_route: ModelRoute,
    endpoint: str,
    api_key: str,
    max_turns: int,
    project_root: Path,
    *,
    bridge_document: str | None = None,
    bridge_version: int | None = None,
    system_prompt: str | None = None,
    chat_func: ChatFunc | None = None,
    guard_runner: GuardRunner | None = None,
    native_hook_runner: base.NativeHookRunner | None = None,
    command_runner: CommandRunner | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    session_timeout: float = DEFAULT_SESSION_TIMEOUT_SECONDS,
    telemetry: Any | None = None,
    guard_log: base.GuardDecisionLog | None = None,
    native_context_id: str | None = None,
    binding: Mapping[str, Any] | None = None,
) -> str:
    return base.run_tool_loop(
        prompt,
        model_route,
        endpoint,
        api_key,
        max_turns,
        project_root,
        _OPENROUTER_PROFILE,
        bridge_document=bridge_document,
        bridge_version=bridge_version,
        system_prompt=system_prompt,
        chat_func=chat_func or call_openrouter_chat,
        guard_runner=guard_runner,
        native_hook_runner=native_hook_runner,
        command_runner=command_runner,
        timeout=timeout,
        session_timeout=session_timeout,
        telemetry=telemetry,
        guard_log=guard_log,
        native_context_id=native_context_id,
        binding=binding,
    )


def build_system_prompt(project_root: Path) -> str:
    """Load the shared root instructions; a role is never loaded from a launch argument (c123, WP2 2.1)."""
    root_source = project_root / "AGENTS.md"
    if not root_source.resolve().is_relative_to(project_root.resolve()):
        raise OpenRouterHarnessError("Shared root instructions resolve outside the project root")
    try:
        root_instructions = root_source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise OpenRouterHarnessError("Shared root instructions are unavailable: AGENTS.md") from exc
    if not root_instructions.strip():
        raise OpenRouterHarnessError("Shared root instructions are unavailable: empty AGENTS.md")
    return root_instructions


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB OpenRouter harness shim.")
    parser.add_argument("-p", "--prompt", required=True, help="User prompt to send to OpenRouter.")
    parser.add_argument("--model", help="Routing model key from .harness-baseline-configuration/routing.toml.")
    parser.add_argument(
        "--init", help="The exact init line; the launcher binds the context with it before the first provider call."
    )
    parser.add_argument(
        "--endpoint", default=DEFAULT_ENDPOINT, help="OpenRouter endpoint; default is https://openrouter.ai/api/v1."
    )
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS, help="Maximum tool loop turns.")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, help="HTTP/guard/subprocess timeout.")
    parser.add_argument(
        "--session-timeout",
        type=float,
        default=DEFAULT_SESSION_TIMEOUT_SECONDS,
        help="Maximum wall-clock seconds for the whole harness tool loop.",
    )
    parser.add_argument("--bridge-document", help="Assigned canonical bridge document.")
    parser.add_argument("--bridge-version", type=int, help="Exact successor version this task must deliver.")
    parser.add_argument("--report", help="Write the run report (JSON) to this path.")
    parser.add_argument("--guard-log", help="Append the guard decisions (JSONL) to this path; else GTKB_GUARD_LOG.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one OpenRouter harness launch (c123, batch design WP2 items 9 and 10: guard log, report, exit codes).

    Exit codes: 0 final answer; 3 bridge delivery incomplete; 4 the --init bind failed (c123, WP2 2.1, no provider
    call made); 5 interrupted; 1 every other failure.
    """
    ensure_utf8_output_streams()
    base.install_break_handler()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_arg_parser()
    args = parser.parse_args(raw_argv)
    project_root = resolve_project_root(Path.cwd())
    native_context_id = str(uuid4())
    guard_log = base.GuardDecisionLog(base.guard_log_path(args.guard_log), native_context_id)
    report = base.RunReport(
        harness="openrouter",
        native_context_id=native_context_id,
        route_key=args.model,
        requested_model=None,
        endpoint=args.endpoint,
        guard_log=guard_log,
    )
    exit_code, error = 1, None
    try:
        exit_code, error = _run(args, raw_argv, project_root, native_context_id, guard_log, report)
    except KeyboardInterrupt:
        print("openrouter_harness: interrupted", file=sys.stderr)
        exit_code, error = base.EXIT_INTERRUPTED, "interrupted"
        if report.data["stop_reason"] is None:
            report.finish("interrupted")
    finally:
        report.write(Path(args.report) if args.report else None, exit_code=exit_code, error=error)
    return exit_code


def _run(
    args: argparse.Namespace,
    raw_argv: list[str],
    project_root: Path,
    native_context_id: str,
    guard_log: base.GuardDecisionLog,
    report: base.RunReport,
) -> tuple[int, str | None]:
    try:
        from scripts._env import load_env_local

        load_env_local()
    except ImportError:
        try:
            from _env import load_env_local

            load_env_local()
        except ImportError:
            pass

    # GT-KB's own named credential (.env.local, GOV-ENV-LOCAL-AUTHORITY-001) first; the conventional name as fallback.
    api_key = os.environ.get("GTKB_OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        message = (
            "openrouter_harness: GTKB_OPENROUTER_API_KEY is not set, and the OPENROUTER_API_KEY environment variable "
            "is not set."
        )
        print(message, file=sys.stderr)
        return 1, message

    try:
        config = load_routing_config(project_root)
        model_route = resolve_model(config, args.model)
        report.data["route_key"] = model_route.key
        report.data["requested_model"] = model_route.model_id
        operation_timeout, session_timeout, max_turns = resolve_runtime_limits(
            config,
            raw_argv,
            cli_timeout=args.timeout,
            cli_session_timeout=args.session_timeout,
            cli_max_turns=args.max_turns,
        )
        system_prompt = build_system_prompt(project_root)
        print(f"openrouter_harness: native_context_id={native_context_id}", file=sys.stderr)
        base.check_launch_inputs(project_root, _OPENROUTER_PROFILE, args.bridge_document, args.bridge_version)
        try:
            binding = base.bind_for_run(args.init, native_context_id, project_root, report)
        except base.NativeBindFailed as exc:
            print(f"openrouter_harness: {exc}", file=sys.stderr)
            return base.EXIT_BIND_FAILED, str(exc)
        text = run_tool_loop(
            args.prompt,
            model_route,
            args.endpoint,
            api_key,
            max_turns,
            project_root,
            bridge_document=args.bridge_document,
            bridge_version=args.bridge_version,
            system_prompt=system_prompt,
            timeout=operation_timeout,
            session_timeout=session_timeout,
            telemetry=report,
            guard_log=guard_log,
            native_context_id=native_context_id,
            binding=binding,
        )
    except OpenRouterHarnessError as exc:
        print(f"openrouter_harness: {exc}", file=sys.stderr)
        incomplete = isinstance(exc, base.CloudHarnessIncomplete)
        return (base.EXIT_DELIVERY_INCOMPLETE if incomplete else 1), str(exc)
    print(text)
    return 0, None


if __name__ == "__main__":
    raise SystemExit(main())
