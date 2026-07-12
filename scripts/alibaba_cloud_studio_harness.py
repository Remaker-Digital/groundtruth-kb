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
LOYAL_OPPOSITION_BRIDGE_SKILLS = base.LOYAL_OPPOSITION_BRIDGE_SKILLS
CANONICAL_TOOLS = base.CANONICAL_TOOLS

DEFAULT_ENDPOINT = "https://dashscope.aliyuncs.com/apps/anthropic"
ROUTING_CONFIG_PATH = Path(".api-harness") / "routing.toml"
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
    dialect=base.DIALECT_ANTHROPIC_MESSAGES,
    hook_tier=base.HOOK_TIER_NATIVE_FULL,
    auth_style=base.AUTH_STYLE_AUTHORIZATION_BEARER,
    publish_bridge_verdict_tool=True,
)


def resolve_alibaba_cloud_studio_session_id(environ: Mapping[str, str] | None = None) -> str:
    """Resolve the bridge work-intent session id used by guarded tools."""
    return base.resolve_harness_session_id(environ)


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
) -> dict[str, str]:
    return base.set_author_metadata_env(env, model_id, model_version, _ALIBABA_PROFILE, endpoint, model_configuration)


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
    skill: str | None = None,
    system_prompt: str | None = None,
    chat_func: ChatFunc | None = None,
    guard_runner: GuardRunner | None = None,
    native_hook_runner: NativeHookRunner | None = None,
    command_runner: CommandRunner | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    session_timeout: float = DEFAULT_SESSION_TIMEOUT_SECONDS,
) -> str:
    return base.run_tool_loop(
        prompt,
        model_route,
        endpoint,
        api_key,
        max_turns,
        project_root,
        _ALIBABA_PROFILE,
        skill=skill,
        system_prompt=system_prompt,
        chat_func=chat_func or call_alibaba_cloud_studio_chat,
        guard_runner=guard_runner,
        native_hook_runner=native_hook_runner or run_alibaba_native_hook,
        command_runner=command_runner,
        timeout=timeout,
        session_timeout=session_timeout,
    )


def build_system_prompt(skill: str | None, model_route: ModelRoute) -> str | None:
    """Supply the bridge guardrails needed for dispatched Loyal Opposition work."""
    if skill not in LOYAL_OPPOSITION_BRIDGE_SKILLS:
        return None
    session_id = resolve_alibaba_cloud_studio_session_id(os.environ) or "<dispatch-session-id-required>"
    tools = ", ".join(model_route.allowed_tools)
    return (
        "You are Alibaba Cloud Studio harness H operating as Loyal Opposition for GT-KB. "
        "Use the versioned bridge-file chain as authoritative and acquire the required "
        "bridge work-intent claim before any bridge verdict write. "
        "Publish every GO, NO-GO, or VERIFIED only with PublishBridgeVerdict; never use Write, Edit, "
        "or Bash for a numbered bridge artifact. The verdict tool computes path/version and VERIFIED "
        "requires include_paths plus commit_message (and hunk_patch_paths when reviewed shared-file "
        "hunks must be isolated). Preserve every guard decision exactly. "
        f"Bridge author metadata: identity={AUTHOR_IDENTITY}; harness_id={AUTHOR_HARNESS_ID}; "
        f"session_id={session_id}; model={model_route.model_id}; allowed_tools={tools}."
    )


def configure_lo_readonly_environment(skill: str | None) -> None:
    """Configure full hooks for H's non-interactive bridge-review worker."""
    if skill in LOYAL_OPPOSITION_BRIDGE_SKILLS:
        os.environ["LOYAL_OPPOSITION_READONLY"] = "1"
        os.environ["GTKB_NO_AXIS_2_SURFACE"] = "1"
        os.environ["GTKB_NO_PROJECT_COMPLETION_SURFACE"] = "1"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB Alibaba Cloud Studio H harness.")
    parser.add_argument("-p", "--prompt", required=True, help="User prompt to send to Alibaba Cloud Studio.")
    parser.add_argument(
        "--model", default=DEFAULT_MODEL_ROUTE, help="Routing model key from .api-harness/routing.toml."
    )
    parser.add_argument("--skill", help="Skill or task route key from .api-harness/routing.toml.")
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS, help="Maximum tool loop turns.")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, help="HTTP/guard/subprocess timeout.")
    parser.add_argument(
        "--session-timeout",
        type=float,
        default=DEFAULT_SESSION_TIMEOUT_SECONDS,
        help="Maximum wall-clock seconds for the whole harness tool loop.",
    )
    return parser


def _load_env_local() -> None:
    try:
        from scripts._env import load_env_local
    except ImportError:  # pragma: no cover - direct script execution fallback
        from _env import load_env_local
    load_env_local()


def main(argv: Sequence[str] | None = None) -> int:
    ensure_utf8_output_streams()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = build_arg_parser().parse_args(raw_argv)
    project_root = resolve_project_root(Path.cwd())

    try:
        _load_env_local()
    except ImportError:
        pass
    configure_lo_readonly_environment(args.skill)

    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        print(f"alibaba_cloud_studio_harness: {API_KEY_ENV} environment variable is not set.", file=sys.stderr)
        return 1
    endpoint = os.environ.get(ENDPOINT_ENV)
    if not endpoint:
        print(f"alibaba_cloud_studio_harness: {ENDPOINT_ENV} environment variable is not set.", file=sys.stderr)
        return 1

    try:
        config = load_routing_config(project_root)
        model_route = resolve_model(config, args.model, skill=args.skill)
        operation_timeout, session_timeout, max_turns = resolve_runtime_limits(
            config,
            raw_argv,
            cli_timeout=args.timeout,
            cli_session_timeout=args.session_timeout,
            cli_max_turns=args.max_turns,
        )
        text = run_tool_loop(
            args.prompt,
            model_route,
            endpoint,
            api_key,
            max_turns,
            project_root,
            skill=args.skill,
            system_prompt=build_system_prompt(args.skill, model_route),
            timeout=operation_timeout,
            session_timeout=session_timeout,
        )
    except AlibabaCloudStudioHarnessError as exc:
        print(f"alibaba_cloud_studio_harness: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
