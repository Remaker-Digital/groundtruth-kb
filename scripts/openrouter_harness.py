#!/usr/bin/env python3
"""Stdlib OpenRouter harness shim for GT-KB Phase 1.

Re-based (cloud-harness template slice 2, WI-5078) onto the shared, config-driven
``cloud_harness_base`` runtime per ``ADR-CLOUD-HARNESS-TEMPLATE-001``. This module is
now the OpenRouter *adopter*: it declares the OpenRouter :class:`AdopterProfile`
(direct-cloud endpoint, ``OPENROUTER_API_KEY`` token auth via an Authorization header,
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
resolve_project_root = base.resolve_project_root
ensure_utf8_output_streams = base.ensure_utf8_output_streams
build_tool_schemas = base.build_tool_schemas
_content_status_token = base._content_status_token
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
LOYAL_OPPOSITION_BRIDGE_SKILLS = base.LOYAL_OPPOSITION_BRIDGE_SKILLS
CANONICAL_TOOLS = base.CANONICAL_TOOLS
MUTATING_TOOLS = base.MUTATING_TOOLS
BRIDGE_WRITE_GUARDS = base.BRIDGE_WRITE_GUARDS
BRIDGE_EDIT_GUARDS = base.BRIDGE_EDIT_GUARDS
WRITE_EDIT_GUARDS = base.WRITE_EDIT_GUARDS
BASH_GUARDS = base.BASH_GUARDS

# --- OpenRouter adopter specifics (the varying axes) ---
DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1"
ROUTING_CONFIG_PATH = Path(".api-harness") / "routing.toml"
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
    auth_env_key="OPENROUTER_API_KEY",
    provider_routing_key="openrouter",
    routing_config_path=ROUTING_CONFIG_PATH,
    dialect=base.DIALECT_OPENAI_CHAT,
    hook_tier=base.HOOK_TIER_GUARD_ADAPTER_FLOOR,
    extra_headers=_OPENROUTER_HEADERS,
)


def resolve_openrouter_session_id(environ: Mapping[str, str] | None = None) -> str:
    """Resolve the bridge work-intent session id used by guarded OpenRouter tools."""
    return base.resolve_harness_session_id(environ)


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
) -> dict[str, str]:
    return base.set_author_metadata_env(
        env, model_id, model_version, _OPENROUTER_PROFILE, endpoint, model_configuration
    )


def _metadata_from_response(metadata: ModelMetadata, response: Mapping[str, Any]) -> ModelMetadata:  # noqa: F811
    return base.metadata_from_response(metadata, response, _OPENROUTER_PROFILE)


def _normalize_bridge_author_model_metadata(
    content: str,
    model_metadata: ModelMetadata,
    project_root: Path,
    path: Path,
) -> str:
    return base.normalize_bridge_author_model_metadata(content, model_metadata, project_root, path, _OPENROUTER_PROFILE)


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
    system_prompt: str | None = None,
    chat_func: ChatFunc | None = None,
    guard_runner: GuardRunner | None = None,
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
        _OPENROUTER_PROFILE,
        system_prompt=system_prompt,
        chat_func=chat_func or call_openrouter_chat,
        guard_runner=guard_runner,
        command_runner=command_runner,
        timeout=timeout,
        session_timeout=session_timeout,
    )


def build_system_prompt(skill: str | None, model_route: ModelRoute) -> str | None:
    """Return role context for OpenRouter skill routes that need GT-KB bridge behavior."""
    if skill not in LOYAL_OPPOSITION_BRIDGE_SKILLS:
        return None
    allowed_tools = ", ".join(model_route.allowed_tools)
    session_id = resolve_openrouter_session_id(os.environ) or "<dispatch-session-id-required>"
    return f"""You are OpenRouter harness F operating as Loyal Opposition for GT-KB.

Before you can write any bridge verdict, you MUST acquire the work-intent claim: python scripts\\bridge_claim_cli.py claim <document-slug>. If the claim command reports an existing holder, treat that JSON output as claim evidence — not as a harness crash. Do not proceed to Write until the claim command returns success.

Before final Write/Edit of any bridge verdict, assemble a draft verdict body
with the required status token and sections, then run the shared verify helper:
python .claude/skills/verify/helpers/write_verdict.py --slug <document-slug> --body-file <draft-body-file>
Review and prune the helper-seeded Prior Deliberations before writing the next
numbered bridge verdict file. If the helper cannot run, preserve its failure
output in the verdict evidence instead of silently omitting Prior Deliberations.

Use the GT-KB file bridge as the authoritative workflow surface. Read the full
versioned bridge-file chain for the target document before acting, and use
gt bridge dispatch config, gt bridge dispatch status, and gt bridge dispatch
health for dispatcher topology and readiness. Respond to latest NEW or REVISED
bridge entries by writing the next numbered bridge verdict file through the
guarded bridge writer path. Do not stop with prose when a bridge verdict is
required.
Use harness-state/harness-registry.json through the canonical role reader as the role source
of truth. Do not treat harness-local operating-role.md files as live role authority.

For proposal reviews, write GO or NO-GO. For post-implementation reports, write VERIFIED or
NO-GO. Run preflight checks and include their raw output in the verdict as advisory context for the Prime Builder. A nonzero preflight exit is a note to attach to the verdict body, not a rejection criterion. Your verdict (GO / NO-GO / VERIFIED) evaluates the substantive quality of the proposal or implementation report being reviewed — not whether every applicable cross-cutting spec appears in the linked specs list.

For a positive post-implementation VERIFIED verdict, do not write the bridge
file directly. Use the reviewed verdict body with the atomic finalization helper:
python .claude/skills/verify/helpers/write_verdict.py --slug <document-slug> --body-file <reviewed-verdict-body> --finalize-verified --no-prepopulate --commit-message "<type(scope): message>" --include <verified-path> [--include <verified-path> ...]
The helper must create the local commit containing the verified path set and the
new VERIFIED verdict artifact. If you cannot identify the verified path set or
the helper cannot commit, fail closed and report NO-GO/blocker evidence instead
of leaving a terminal VERIFIED file in the worktree.

Run the preflight checks with Bash:
python scripts\\bridge_applicability_preflight.py --bridge-id <document-slug>
python scripts\\adr_dcl_clause_preflight.py --bridge-id <document-slug>

Do not use Bash to create, edit, overwrite, remove, or index bridge/*.md files
or the retired bridge index. The harness hard-denies shell bridge mutations;
use guarded Write/Edit dispatch or the deterministic bridge writer/helper path
for bridge artifacts. Treat any helper that requires the retired bridge index
as defective and report that defect instead of following stale instructions.

Bridge verdict author metadata to include:
author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: {session_id}
author_model: {model_route.model_id}
author_model_version: {model_route.model_version}
author_model_configuration: OpenRouter harness shim; route {model_route.key}; skill {skill}; guarded tools {allowed_tools}

Stay within E:\\GT-KB. Preserve guard decisions exactly; if a guarded tool is denied, report the
denial and do not invent a successful bridge action."""


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB OpenRouter harness shim.")
    parser.add_argument("-p", "--prompt", required=True, help="User prompt to send to OpenRouter.")
    parser.add_argument("--model", help="Routing model key from .api-harness/routing.toml.")
    parser.add_argument("--skill", help="Skill or task route key from .api-harness/routing.toml.")
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    ensure_utf8_output_streams()
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    project_root = resolve_project_root(Path.cwd())

    try:
        from scripts._env import load_env_local

        load_env_local()
    except ImportError:
        try:
            from _env import load_env_local

            load_env_local()
        except ImportError:
            pass

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("openrouter_harness: OPENROUTER_API_KEY environment variable is not set.", file=sys.stderr)
        return 1

    try:
        config = load_routing_config(project_root)
        model_route = resolve_model(config, args.model, skill=args.skill)
        system_prompt = build_system_prompt(args.skill, model_route)
        text = run_tool_loop(
            args.prompt,
            model_route,
            args.endpoint,
            api_key,
            args.max_turns,
            project_root,
            system_prompt=system_prompt,
            timeout=args.timeout,
            session_timeout=args.session_timeout,
        )
    except OpenRouterHarnessError as exc:
        print(f"openrouter_harness: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
