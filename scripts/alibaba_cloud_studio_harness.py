#!/usr/bin/env python3
"""Alibaba Cloud Studio H adopter for the shared cloud harness runtime.

This module intentionally supplies only the Alibaba-specific profile and CLI
binding. Transport, tool dispatch, guard enforcement, native-hook execution,
and retry behavior remain owned by :mod:`cloud_harness_base`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    import cloud_harness_base as base
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from scripts import cloud_harness_base as base


AlibabaCloudStudioHarnessError = base.CloudHarnessError
ModelRoute = base.ModelRoute
RoutingConfig = base.RoutingConfig
ModelMetadata = base.ModelMetadata
GuardExecutionResult = base.GuardExecutionResult
GuardRunner = base.GuardRunner
NativeHookRunner = base.NativeHookRunner
ChatFunc = base.ChatFunc
CommandRunner = base.CommandRunner

infer_model_version = base.infer_model_version
resolve_model = base.resolve_model
resolve_runtime_limits = base.resolve_runtime_limits
resolve_project_root = base.resolve_project_root
ensure_utf8_output_streams = base.ensure_utf8_output_streams

DEFAULT_TIMEOUT_SECONDS = base.DEFAULT_TIMEOUT_SECONDS
DEFAULT_SESSION_TIMEOUT_SECONDS = base.DEFAULT_SESSION_TIMEOUT_SECONDS
DEFAULT_MAX_TURNS = base.DEFAULT_MAX_TURNS
CANONICAL_TOOLS = base.CANONICAL_TOOLS

DEFAULT_ENDPOINT = "https://dashscope.aliyuncs.com/apps/anthropic"
ROUTING_CONFIG_PATH = Path(".harness-baseline-configuration/routing.toml")
NATIVE_HOOK_SETTINGS_PATH = Path(".api-harness/alibaba-cloud-studio/settings.json")
AUTHOR_IDENTITY = "Alibaba Cloud Studio H"
AUTHOR_HARNESS_ID = "H"
API_KEY_ENV = "ALIBABA_API_KEY"
ENDPOINT_ENV = "ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT"
DEFAULT_MODEL_ROUTE = "alibaba-deepseek-v4-pro"

_ALIBABA_PROFILE = base.AdopterProfile(
    display_name="Alibaba Cloud Studio",
    author_identity=AUTHOR_IDENTITY,
    author_harness_id=AUTHOR_HARNESS_ID,
    default_endpoint=DEFAULT_ENDPOINT,
    auth_env_key=API_KEY_ENV,
    provider_routing_key="alibaba-cloud-studio",
    routing_config_path=ROUTING_CONFIG_PATH,
    native_hook_settings_path=NATIVE_HOOK_SETTINGS_PATH,
    dialect=base.DIALECT_ANTHROPIC_MESSAGES,
    hook_tier=base.HOOK_TIER_NATIVE_FULL,
    auth_style=base.AUTH_STYLE_AUTHORIZATION_BEARER,
)


def load_routing_config(project_root: Path) -> RoutingConfig:
    """Load only the Alibaba Cloud Studio rows from the shared routing file."""
    return base.load_routing_config(
        project_root,
        provider_key=_ALIBABA_PROFILE.provider_routing_key,
        config_path=ROUTING_CONFIG_PATH,
    )


def call_alibaba_cloud_studio_chat(
    endpoint: str, api_key: str, payload: dict[str, Any], timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> dict[str, Any]:
    """Bind the Alibaba adopter to the Anthropic Messages bearer transport."""
    return base.anthropic_messages_completion(
        normalize_anthropic_endpoint(endpoint),
        api_key,
        payload,
        timeout,
        label=_ALIBABA_PROFILE.display_name,
        auth_style=_ALIBABA_PROFILE.auth_style,
    )


def normalize_anthropic_endpoint(endpoint: str) -> str:
    """Normalize Alibaba's SDK base URL to the Messages API version prefix."""
    normalized = endpoint.rstrip("/")
    return normalized if normalized.endswith("/v1") else f"{normalized}/v1"


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
        _ALIBABA_PROFILE,
        endpoint,
        model_configuration,
        native_context_id=native_context_id,
    )


def run_alibaba_native_hook(
    command: str,
    payload: dict[str, Any],
    env: Mapping[str, str],
    timeout: float,
) -> GuardExecutionResult:
    """Adapt native lifecycle no-ops without weakening mutating-tool guards."""
    result = base._default_native_hook_runner(command, payload, env, timeout)
    if payload.get("hook_event_name") == base.NATIVE_HOOK_PRE_TOOL_USE:
        return result
    if result.returncode == 0 and not result.timed_out:
        stdout = result.stdout.strip()
        if not stdout:
            return GuardExecutionResult(returncode=0, stdout="{}", stderr=result.stderr)
        try:
            json.loads(stdout)
        except json.JSONDecodeError:
            return GuardExecutionResult(
                returncode=0,
                stdout=json.dumps({"hookSpecificOutput": {"additionalContext": stdout}}),
                stderr=result.stderr,
            )
    return result


def dispatch_tool_call(
    tool_name: str,
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    *,
    guard_runner: GuardRunner | None = None,
    command_runner: CommandRunner | None = None,
) -> str:
    return base.dispatch_tool_call(
        tool_name,
        arguments,
        model_metadata,
        project_root,
        _ALIBABA_PROFILE,
        guard_runner=guard_runner,
        command_runner=command_runner,
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
    native_hook_runner: NativeHookRunner | None = None,
    command_runner: CommandRunner | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    session_timeout: float = DEFAULT_SESSION_TIMEOUT_SECONDS,
    telemetry: Any | None = None,
    guard_log: base.GuardDecisionLog | None = None,
    native_context_id: str | None = None,
    binding: Mapping[str, Any] | None = None,
) -> str:
    """H's tool loop (c123, batch design WP2: it forwards the run report, the guard log, the context id and the bind)."""
    return base.run_tool_loop(
        prompt,
        model_route,
        endpoint,
        api_key,
        max_turns,
        project_root,
        _ALIBABA_PROFILE,
        bridge_document=bridge_document,
        bridge_version=bridge_version,
        system_prompt=system_prompt,
        chat_func=chat_func or call_alibaba_cloud_studio_chat,
        guard_runner=guard_runner,
        native_hook_runner=native_hook_runner or run_alibaba_native_hook,
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
        raise AlibabaCloudStudioHarnessError("Shared root instructions resolve outside the project root")
    try:
        root_instructions = root_source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AlibabaCloudStudioHarnessError("Shared root instructions are unavailable: AGENTS.md") from exc
    if not root_instructions.strip():
        raise AlibabaCloudStudioHarnessError("Shared root instructions are unavailable: empty AGENTS.md")
    return root_instructions


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB Alibaba Cloud Studio H harness.")
    parser.add_argument("-p", "--prompt", required=True, help="User prompt to send to Alibaba Cloud Studio.")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_ROUTE,
        help="Routing model key from .harness-baseline-configuration/routing.toml.",
    )
    parser.add_argument(
        "--init", help="The exact init line; the launcher binds the context with it before the first provider call."
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


def _load_env_local() -> None:
    try:
        from scripts._env import load_env_local
    except ImportError:  # pragma: no cover - direct script execution fallback
        from _env import load_env_local
    load_env_local()


def main(argv: Sequence[str] | None = None) -> int:
    """Run one H launch (c123, batch design WP2 items 9 and 10: guard log, report, exit codes).

    Exit codes: 0 final answer; 3 bridge delivery incomplete; 4 the --init bind failed (c123, WP2 2.1, no provider
    call made); 5 interrupted; 1 every other failure.
    """
    ensure_utf8_output_streams()
    base.install_break_handler()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = build_arg_parser().parse_args(raw_argv)
    project_root = resolve_project_root(Path.cwd())
    native_context_id = str(uuid4())
    guard_log = base.GuardDecisionLog(base.guard_log_path(args.guard_log), native_context_id)
    report = base.RunReport(
        harness="alibaba_cloud_studio",
        native_context_id=native_context_id,
        route_key=args.model,
        requested_model=None,
        endpoint=os.environ.get(ENDPOINT_ENV),
        guard_log=guard_log,
    )
    exit_code, error = 1, None
    try:
        exit_code, error = _run(args, raw_argv, project_root, native_context_id, guard_log, report)
    except KeyboardInterrupt:
        print("alibaba_cloud_studio_harness: interrupted", file=sys.stderr)
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
        _load_env_local()
    except ImportError:
        pass

    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        message = f"alibaba_cloud_studio_harness: {API_KEY_ENV} environment variable is not set."
        print(message, file=sys.stderr)
        return 1, message
    endpoint = os.environ.get(ENDPOINT_ENV)
    if not endpoint:
        message = f"alibaba_cloud_studio_harness: {ENDPOINT_ENV} environment variable is not set."
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
        print(f"alibaba_cloud_studio_harness: native_context_id={native_context_id}", file=sys.stderr)
        base.check_launch_inputs(project_root, _ALIBABA_PROFILE, args.bridge_document, args.bridge_version)
        try:
            binding = base.bind_for_run(args.init, native_context_id, project_root, report)
        except base.NativeBindFailed as exc:
            print(f"alibaba_cloud_studio_harness: {exc}", file=sys.stderr)
            return base.EXIT_BIND_FAILED, str(exc)
        text = run_tool_loop(
            args.prompt,
            model_route,
            endpoint,
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
    except AlibabaCloudStudioHarnessError as exc:
        print(f"alibaba_cloud_studio_harness: {exc}", file=sys.stderr)
        incomplete = isinstance(exc, base.CloudHarnessIncomplete)
        return (base.EXIT_DELIVERY_INCOMPLETE if incomplete else 1), str(exc)
    print(text)
    return 0, None


if __name__ == "__main__":
    raise SystemExit(main())
