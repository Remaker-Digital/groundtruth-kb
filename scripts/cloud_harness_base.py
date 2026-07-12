#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared, config-driven cloud-harness runtime base (GT-KB cloud-harness template, slice 2).

Implements ``ADR-CLOUD-HARNESS-TEMPLATE-001``: a single framework-free base runtime
that cloud harnesses instantiate by configuration, replacing the per-harness
hand-rolled shims. The base owns connection/transport, bounded retry/backoff, the
fail-closed guard-adapter enforcement (generalizing the ``DCL-OLLAMA-TOOL-PARITY-GATE-001``
enforcement mechanism), author-metadata injection, and the framework-free tool-call loop.
Adopters supply only the varying axes via an :class:`AdopterProfile`:

* ``endpoint`` — the direct-cloud base URL (no local-service bridge).
* ``auth_env_key`` — token auth via an Authorization header keyed on an env var NAME
  (``GOV-ENV-LOCAL-AUTHORITY-001``); the token value is never embedded in source.
* ``dialect`` — ``openai-chat`` (slice 2) and ``anthropic-messages`` (slice 3) are
  implemented concretely; ``ollama-native`` is the remaining seam point (implemented with
  the Ollama re-base in slice 4) and raises :class:`NotImplementedError` if selected.
* ``model`` routing — the adopter's ``.api-harness/routing.toml`` provider key.
* ``hook_tier`` — ``guard-adapter-floor`` (the enforced mechanism) or ``native-full-hooks``
  (the Claude-style hook lifecycle from ``.claude/settings.json``; the floor is still
  enforced for this tier).

The dialect abstraction (slice 3) makes ``run_tool_loop`` dialect-agnostic: each dialect
strategy owns request-build, tool-schema shaping, and response-parse, while the loop's
control flow, tool dispatch, fail-closed guard enforcement, and session-timeout are shared.
OpenRouter (openai-chat) re-bases onto this module as the first-adopter proof; Alibaba Cloud
Studio and Ollama (anthropic-messages / ollama-native) adopt in slice 4.

Framework-free: standard library (``urllib``/``ssl``/``json``/``subprocess``) plus existing
GT-KB helpers only — no heavyweight agent framework, per ``ADR-OLLAMA-HARNESS-ADOPTION-001``.
"""

from __future__ import annotations

import contextlib
import fnmatch
import functools
import json
import os
import re
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

try:
    from gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id
except ModuleNotFoundError:  # pragma: no cover
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id

try:
    from sdk_bridge_bash_guard import bridge_bash_mutation_reason
except ModuleNotFoundError:  # pragma: no cover
    from scripts.sdk_bridge_bash_guard import bridge_bash_mutation_reason

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]


DEFAULT_TIMEOUT_SECONDS = 240.0
DEFAULT_SESSION_TIMEOUT_SECONDS = 540.0

# Bounded retry for transient cloud transport failures so a dispatched worker
# survives a transient hiccup and still produces output. Total backoff
# (1+2+4 = 7s) stays far under the worker-lifetime cap.
CHAT_MAX_ATTEMPTS = 3
CHAT_RETRY_BACKOFF_SECONDS = (1.0, 2.0, 4.0)
RETRYABLE_HTTP_STATUS = frozenset({429, 500, 502, 503, 504})
RETRYABLE_PROVIDER_TRANSPORT_MARKERS = frozenset(
    {
        "bad record mac",
        "sslv3_alert_bad_record_mac",
    }
)
# WI-5066: hard wall-clock grace (seconds) added when bounding a provider call on
# a worker thread. urlopen(timeout=) bounds socket connect/read but NOT
# getaddrinfo (DNS resolution), which runs before the socket exists, so the
# socket timeout can never fire during a DNS stall. Each attempt runs on a daemon
# worker thread joined for a hard wall-clock bound; the socket timeout is set this
# much shorter than the bound so a genuine socket stall raises an
# accurately-classified URLError before the join synthesizes a DNS-stall timeout.
PROVIDER_CALL_WALL_CLOCK_GRACE_SECONDS = 5.0
DEFAULT_MAX_TURNS = 40
BLANK_FINAL_RECOVERY_PROMPT = (
    "Your previous assistant response contained no text and no tool call. Continue the task. "
    "Use the available tools if work remains, or return a nonblank final response when complete."
)
MAX_TOOL_OUTPUT_CHARS = 6000
MAX_GREP_RESULTS = 50
MAX_GLOB_RESULTS = 100
MAX_FILE_SCAN_ENTRIES = 5000
MAX_REPEATED_TOOL_SIGNATURE_TURNS = 4
SKIPPED_SCAN_DIR_NAMES = frozenset(
    {
        ".git",
        ".gtkb-state",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
    }
)
LOYAL_OPPOSITION_BRIDGE_SKILLS = frozenset({"bridge-review", "verification"})
PUBLISH_BRIDGE_VERDICT_TOOL = "PublishBridgeVerdict"
CANONICAL_TOOLS = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash", PUBLISH_BRIDGE_VERDICT_TOOL})
MUTATING_TOOLS = frozenset({"Write", "Edit", "Bash"})
DISPATCH_KEYWORD_ROLES = {
    "::init gtkb lo": "loyal-opposition",
    "::init gtkb pb": "prime-builder",
}

# --- Dialect seam (slice 2: openai-chat; slice 3: + anthropic-messages; slice 4: + ollama-native) ---
DIALECT_OPENAI_CHAT = "openai-chat"
DIALECT_OLLAMA_NATIVE = "ollama-native"
DIALECT_ANTHROPIC_MESSAGES = "anthropic-messages"
SUPPORTED_DIALECTS = frozenset({DIALECT_OPENAI_CHAT, DIALECT_OLLAMA_NATIVE, DIALECT_ANTHROPIC_MESSAGES})
# After slice 3, anthropic-messages is implemented concretely; ollama-native remains the
# lone seam point (implemented with the Ollama re-base in slice 4).
SLICE4_DIALECT_SEAM = frozenset({DIALECT_OLLAMA_NATIVE})

# --- Auth styles (anthropic-messages dialect; per Ollama upstream issue #16922 some
# Anthropic-compatible cloud endpoints reject x-api-key and require Authorization: Bearer) ---
AUTH_STYLE_AUTHORIZATION_BEARER = "authorization-bearer"
AUTH_STYLE_X_API_KEY = "x-api-key"
SUPPORTED_AUTH_STYLES = frozenset({AUTH_STYLE_AUTHORIZATION_BEARER, AUTH_STYLE_X_API_KEY})

# --- Hook tiers (native-full-hooks runs the Claude-style lifecycle while keeping
# the fail-closed guard-adapter floor enforced for mutating tools).
HOOK_TIER_GUARD_ADAPTER_FLOOR = "guard-adapter-floor"
HOOK_TIER_NATIVE_FULL = "native-full-hooks"
SUPPORTED_HOOK_TIERS = frozenset({HOOK_TIER_GUARD_ADAPTER_FLOOR, HOOK_TIER_NATIVE_FULL})
NATIVE_HOOK_SETTINGS_PATH = Path(".claude/settings.json")
NATIVE_HOOK_SESSION_START = "SessionStart"
NATIVE_HOOK_USER_PROMPT_SUBMIT = "UserPromptSubmit"
NATIVE_HOOK_PRE_TOOL_USE = "PreToolUse"
NATIVE_HOOK_POST_TOOL_USE = "PostToolUse"
NATIVE_HOOK_STOP = "Stop"
NATIVE_HOOK_EVENTS = frozenset(
    {
        NATIVE_HOOK_SESSION_START,
        NATIVE_HOOK_USER_PROMPT_SUBMIT,
        NATIVE_HOOK_PRE_TOOL_USE,
        NATIVE_HOOK_POST_TOOL_USE,
        NATIVE_HOOK_STOP,
    }
)
DEFAULT_NATIVE_HOOK_TIMEOUT_SECONDS = 10.0
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_ANTHROPIC_MAX_TOKENS = 4096

# Generic GT-KB guard-adapter sequences (shared across adopters; not adopter-specific).
BRIDGE_WRITE_GUARDS = (
    Path(".claude/hooks/credential-scan.py"),
    Path(".claude/hooks/scanner-safe-writer.py"),
    Path(".claude/hooks/bridge-compliance-gate.py"),
    Path(".claude/hooks/narrative-artifact-approval-gate.py"),
    Path("scripts/implementation_start_gate.py"),
)
BRIDGE_EDIT_GUARDS = (
    Path(".claude/hooks/credential-scan.py"),
    Path(".claude/hooks/scanner-safe-writer.py"),
    Path(".claude/hooks/bridge-compliance-gate.py"),
    Path(".claude/hooks/narrative-artifact-approval-gate.py"),
    Path("scripts/implementation_start_gate.py"),
)
WRITE_EDIT_GUARDS = (
    Path(".claude/hooks/credential-scan.py"),
    Path(".claude/hooks/scanner-safe-writer.py"),
    Path(".claude/hooks/narrative-artifact-approval-gate.py"),
    Path("scripts/implementation_start_gate.py"),
)
BASH_GUARDS = (
    Path(".claude/hooks/destructive-gate.py"),
    Path(".claude/hooks/formal-artifact-approval-gate.py"),
    Path("scripts/implementation_start_gate.py"),
)


class CloudHarnessError(RuntimeError):
    """Raised for fail-closed cloud-harness errors."""


class FileScanLimitExceeded(CloudHarnessError):
    """Raised when a bounded filesystem tool scan reaches its entry cap."""

    def __init__(self, limit: int) -> None:
        super().__init__(f"scan truncated after {limit} entries; narrow the path or pattern")
        self.limit = limit


class _ProviderCallTimeout(TimeoutError):
    """A provider call exceeded its hard wall-clock bound (WI-5066).

    Subclasses ``TimeoutError`` so the existing transport-retry classifier
    (:func:`_is_retryable_provider_transport_error`) treats it as retryable and
    the bounded-retry loop absorbs it. Raised when the worker thread running a
    provider request is still alive after the wall-clock join elapses -- the
    signature of a DNS/connect stall that ``urlopen(timeout=)`` cannot bound.
    """


@dataclass(frozen=True)
class ModelRoute:
    key: str
    model_id: str
    model_version: str
    tool_calling_supported: bool
    allowed_tools: tuple[str, ...]
    omit_payload_model: bool = False


@dataclass(frozen=True)
class RoutingConfig:
    schema_version: int
    models: dict[str, ModelRoute]
    default_model: str
    skill_routes: dict[str, str]
    timeout_seconds: float | None = None
    session_timeout_seconds: float | None = None
    max_turns: int | None = None


@dataclass(frozen=True)
class ModelMetadata:
    model_id: str
    model_version: str
    endpoint: str
    route_key: str
    model_configuration: str | None = None
    requested_model_id: str | None = None


@dataclass(frozen=True)
class GuardExecutionResult:
    returncode: int
    stdout: str
    stderr: str = ""
    timed_out: bool = False


@dataclass(frozen=True)
class AdopterProfile:
    """The varying-axes configuration a cloud harness supplies to the base runtime."""

    display_name: str
    author_identity: str
    author_harness_id: str
    default_endpoint: str
    auth_env_key: str
    provider_routing_key: str
    routing_config_path: Path
    dialect: str = DIALECT_OPENAI_CHAT
    hook_tier: str = HOOK_TIER_GUARD_ADAPTER_FLOOR
    extra_headers: Mapping[str, str] = field(default_factory=dict)
    # anthropic-messages dialect axes (ignored by the openai-chat dialect; openai-safe defaults):
    auth_style: str = AUTH_STYLE_AUTHORIZATION_BEARER
    anthropic_version: str = DEFAULT_ANTHROPIC_VERSION
    max_tokens: int = DEFAULT_ANTHROPIC_MAX_TOKENS
    publish_bridge_verdict_tool: bool = False

    def __post_init__(self) -> None:
        if self.dialect not in SUPPORTED_DIALECTS:
            raise CloudHarnessError(f"unknown dialect {self.dialect!r}; expected one of {sorted(SUPPORTED_DIALECTS)}")
        if self.hook_tier not in SUPPORTED_HOOK_TIERS:
            raise CloudHarnessError(
                f"unknown hook_tier {self.hook_tier!r}; expected one of {sorted(SUPPORTED_HOOK_TIERS)}"
            )
        if self.auth_style not in SUPPORTED_AUTH_STYLES:
            raise CloudHarnessError(
                f"unknown auth_style {self.auth_style!r}; expected one of {sorted(SUPPORTED_AUTH_STYLES)}"
            )
        # Slice 2 direct-cloud invariant (SPEC-INTAKE-9ec893): an adopter must declare a
        # direct-cloud endpoint; the base has no local-service bridge path.
        if not self.default_endpoint or not str(self.default_endpoint).strip():
            raise CloudHarnessError("adopter profile requires a non-empty direct-cloud endpoint")
        if not self.auth_env_key or not str(self.auth_env_key).strip():
            raise CloudHarnessError(
                "adopter profile requires an auth_env_key (env-var NAME, per GOV-ENV-LOCAL-AUTHORITY-001)"
            )


GuardRunner = Callable[[Path, dict[str, Any], Mapping[str, str], float], GuardExecutionResult]
NativeHookRunner = Callable[[str, dict[str, Any], Mapping[str, str], float], GuardExecutionResult]
ChatFunc = Callable[[str, str, dict[str, Any], float], dict[str, Any]]
CommandRunner = Callable[[str, Path, Mapping[str, str], float], subprocess.CompletedProcess[str]]
RelativePathFunc = Callable[[Path, Path], str]
IterFilesFunc = Callable[..., Iterable[Path]]


def _remaining_timeout(deadline: float, message: str) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise CloudHarnessError(message)
    return remaining


def _sleep_with_budget(delay: float, deadline: float, message: str) -> None:
    if _remaining_timeout(deadline, message) < delay:
        raise CloudHarnessError(message)
    time.sleep(delay)


def ensure_utf8_output_streams(stdout: Any | None = None, stderr: Any | None = None) -> None:
    """Make harness output safe for Unicode verdict text on Windows consoles."""
    for stream in (stdout or sys.stdout, stderr or sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _retry_after_delay_seconds(exc: urllib.error.HTTPError) -> float | None:
    retry_after = exc.headers.get("Retry-After") if exc.headers else None
    if not retry_after:
        return None
    try:
        return max(0.0, float(retry_after))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(retry_after)
    except (TypeError, ValueError):
        return None
    return max(0.0, retry_at.timestamp() - time.time())


def _http_retry_delay_seconds(exc: urllib.error.HTTPError, attempt: int) -> float:
    if exc.code == 429:
        retry_after = _retry_after_delay_seconds(exc)
        if retry_after is not None:
            return retry_after
    return CHAT_RETRY_BACKOFF_SECONDS[attempt - 1]


def _provider_transport_error_summary(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__name__}: {exc}"


def _is_retryable_provider_transport_error(exc: BaseException) -> bool:
    if isinstance(exc, (urllib.error.URLError, ConnectionError, TimeoutError)):
        return True
    if isinstance(exc, ssl.SSLError):
        text = str(exc).lower()
        return any(marker in text for marker in RETRYABLE_PROVIDER_TRANSPORT_MARKERS)
    return False


def resolve_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    return current


def _as_list(value: Any, *, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise CloudHarnessError(f"{field} must be a list of strings")
    return value


def _as_non_empty_string(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise CloudHarnessError(f"{field} must be a non-empty string")
    return value


def _as_bool(value: Any, *, field: str, default: bool = False) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise CloudHarnessError(f"{field} must be a boolean")
    return value


def _as_optional_positive_float(value: Any, *, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise CloudHarnessError(f"{field} must be a positive number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise CloudHarnessError(f"{field} must be a positive number") from exc
    if parsed <= 0:
        raise CloudHarnessError(f"{field} must be a positive number")
    return parsed


def _as_optional_positive_int(value: Any, *, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise CloudHarnessError(f"{field} must be a positive integer")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
    else:
        raise CloudHarnessError(f"{field} must be a positive integer")
    if parsed <= 0:
        raise CloudHarnessError(f"{field} must be a positive integer")
    return parsed


def infer_model_version(model_id: str) -> str:
    """Return the tag or version portion from a model identifier."""
    if ":" in model_id:
        return model_id.rsplit(":", 1)[1] or "unversioned"
    if "/" in model_id:
        parts = model_id.split("/")
        if len(parts) > 1 and parts[-1]:
            return parts[-1]
    return "unversioned"


def _parse_skill_routes(routing: Mapping[str, Any], models: Mapping[str, ModelRoute]) -> dict[str, str]:
    skills_raw = routing.get("skills") or {}
    if not isinstance(skills_raw, dict):
        raise CloudHarnessError("routing.skills must be a table when present")
    skill_routes: dict[str, str] = {}
    for skill_name, route_spec in skills_raw.items():
        if not isinstance(skill_name, str) or not skill_name:
            raise CloudHarnessError("routing.skills entries must use non-empty skill names")
        if isinstance(route_spec, str):
            route_key = route_spec
        elif isinstance(route_spec, dict):
            route_key = route_spec.get("model")
        else:
            raise CloudHarnessError(f"routing.skills.{skill_name} must name a configured model")
        if not isinstance(route_key, str) or route_key not in models:
            raise CloudHarnessError(f"routing.skills.{skill_name} must name a configured model")
        skill_routes[skill_name] = route_key
    return skill_routes


def load_routing_config(project_root: Path, *, provider_key: str, config_path: Path) -> RoutingConfig:
    """Load ``.api-harness/routing.toml`` for one provider (cross-provider rows are ignored)."""
    resolved_config_path = project_root / config_path
    try:
        raw = tomllib.loads(resolved_config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CloudHarnessError(f"routing config is missing: {resolved_config_path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise CloudHarnessError(f"routing config is invalid TOML: {exc}") from exc

    if raw.get("schema_version") != 1:
        raise CloudHarnessError("routing config schema_version must be 1")
    models_raw = raw.get("models")
    if not isinstance(models_raw, dict) or not models_raw:
        raise CloudHarnessError("routing config must define [models.<key>] rows")

    models: dict[str, ModelRoute] = {}
    for key, row in models_raw.items():
        if not isinstance(key, str) or not key or not isinstance(row, dict):
            raise CloudHarnessError("model rows must be named TOML tables")

        # Only process rows for this adopter's provider (cross-provider isolation).
        if row.get("provider") != provider_key:
            continue

        model_id = _as_non_empty_string(row.get("model_id"), field=f"models.{key}.model_id")
        model_version = infer_model_version(model_id)
        allowed_tools = tuple(_as_list(row.get("allowed_tools"), field=f"models.{key}.allowed_tools"))
        if row.get("tool_calling_supported") is not True:
            raise CloudHarnessError(f"models.{key}.tool_calling_supported must be true")
        unknown_tools = sorted(set(allowed_tools) - CANONICAL_TOOLS)
        if unknown_tools:
            raise CloudHarnessError(f"models.{key}.allowed_tools contains noncanonical tools: {unknown_tools}")
        omit_payload_model = _as_bool(row.get("omit_payload_model"), field=f"models.{key}.omit_payload_model")
        models[key] = ModelRoute(key, model_id, model_version, True, allowed_tools, omit_payload_model)

    routing = raw.get("routing", {}).get(provider_key)
    if not isinstance(routing, dict):
        raise CloudHarnessError(f"routing config must define [routing.{provider_key}]")
    default_model = routing.get("default_model")
    if not isinstance(default_model, str) or default_model not in models:
        raise CloudHarnessError(f"routing.{provider_key}.default_model must name a configured {provider_key} model")
    return RoutingConfig(
        schema_version=1,
        models=models,
        default_model=default_model,
        skill_routes=_parse_skill_routes(routing, models),
        timeout_seconds=_as_optional_positive_float(
            routing.get("timeout_seconds"), field=f"routing.{provider_key}.timeout_seconds"
        ),
        session_timeout_seconds=_as_optional_positive_float(
            routing.get("session_timeout_seconds"), field=f"routing.{provider_key}.session_timeout_seconds"
        ),
        max_turns=_as_optional_positive_int(routing.get("max_turns"), field=f"routing.{provider_key}.max_turns"),
    )


def resolve_model(config: RoutingConfig, requested_model: str | None, skill: str | None = None) -> ModelRoute:
    if skill is not None and not skill:
        raise CloudHarnessError("skill route key must be a non-empty string")
    route_key = requested_model or (config.skill_routes.get(skill) if skill else None) or config.default_model
    try:
        return config.models[route_key]
    except KeyError as exc:
        raise CloudHarnessError(f"unknown model route: {route_key}") from exc


def _flag_was_supplied(argv: Sequence[str], flag: str) -> bool:
    prefix = f"{flag}="
    return any(item == flag or item.startswith(prefix) for item in argv)


def resolve_runtime_limits(
    config: RoutingConfig,
    argv: Sequence[str],
    *,
    cli_timeout: float,
    cli_session_timeout: float,
    cli_max_turns: int,
) -> tuple[float, float, int]:
    """Resolve explicit CLI limits over provider routing limits over CLI defaults."""
    operation_timeout = (
        float(cli_timeout)
        if _flag_was_supplied(argv, "--timeout") or config.timeout_seconds is None
        else config.timeout_seconds
    )
    session_timeout = (
        float(cli_session_timeout)
        if _flag_was_supplied(argv, "--session-timeout") or config.session_timeout_seconds is None
        else config.session_timeout_seconds
    )
    max_turns = (
        int(cli_max_turns) if _flag_was_supplied(argv, "--max-turns") or config.max_turns is None else config.max_turns
    )
    return operation_timeout, session_timeout, max_turns


def resolve_harness_session_id(environ: Mapping[str, str] | None = None) -> str:
    """Resolve the bridge work-intent session id used by guarded tools."""
    return resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ=environ)


def _default_config_label(profile: AdopterProfile, endpoint: str) -> str:
    return f"{profile.display_name} endpoint={endpoint}; routing=static {profile.routing_config_path.as_posix()}"


def metadata_configuration(
    metadata: ModelMetadata,
    profile: AdopterProfile,
    *,
    response_model_id: str | None = None,
) -> str:
    if metadata.model_configuration:
        return metadata.model_configuration
    if response_model_id:
        requested_model = metadata.requested_model_id or metadata.model_id
        override = "true" if response_model_id != requested_model else "false"
        return (
            f"{profile.display_name} endpoint={metadata.endpoint}; route={metadata.route_key}; "
            f"requested_model={requested_model}; model_source=response.model; "
            f"account_override={override}"
        )
    return _default_config_label(profile, metadata.endpoint)


def _response_model_id(response: Mapping[str, Any]) -> str | None:
    model = response.get("model")
    if isinstance(model, str) and model.strip():
        return model.strip()
    return None


def metadata_from_response(
    metadata: ModelMetadata, response: Mapping[str, Any], profile: AdopterProfile
) -> ModelMetadata:
    response_model_id = _response_model_id(response)
    if response_model_id is None:
        return metadata
    return ModelMetadata(
        model_id=response_model_id,
        model_version=infer_model_version(response_model_id),
        endpoint=metadata.endpoint,
        route_key=metadata.route_key,
        model_configuration=metadata_configuration(metadata, profile, response_model_id=response_model_id),
        requested_model_id=metadata.requested_model_id or metadata.model_id,
    )


def _schema(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


def build_tool_schemas(allowed_tools: Iterable[str]) -> list[dict[str, Any]]:
    schemas = {
        "Read": _schema(
            "Read",
            "Read a UTF-8 text file under the GT-KB project root.",
            {"path": {"type": "string"}, "max_chars": {"type": "integer", "minimum": 1}},
            ["path"],
        ),
        "Write": _schema(
            "Write",
            "Write a UTF-8 text file under the GT-KB project root after guard approval.",
            {"path": {"type": "string"}, "content": {"type": "string"}},
            ["path", "content"],
        ),
        "Edit": _schema(
            "Edit",
            "Replace exact text in a UTF-8 file under the GT-KB project root after guard approval.",
            {"path": {"type": "string"}, "old_string": {"type": "string"}, "new_string": {"type": "string"}},
            ["path", "old_string", "new_string"],
        ),
        "Grep": _schema(
            "Grep",
            "Search text files under the GT-KB project root with a regular expression.",
            {"pattern": {"type": "string"}, "path": {"type": "string"}, "max_results": {"type": "integer"}},
            ["pattern"],
        ),
        "Glob": _schema(
            "Glob",
            "List paths under the GT-KB project root that match a glob pattern.",
            {"pattern": {"type": "string"}, "path": {"type": "string"}, "max_results": {"type": "integer"}},
            ["pattern"],
        ),
        "Bash": _schema(
            "Bash",
            "Run a bounded local shell command after guards allow it; bridge artifact and retired-index mutations are denied.",
            {"command": {"type": "string"}, "timeout_seconds": {"type": "number", "minimum": 1}},
            ["command"],
        ),
        PUBLISH_BRIDGE_VERDICT_TOOL: _schema(
            PUBLISH_BRIDGE_VERDICT_TOOL,
            (
                "Publish a governed Loyal Opposition GO, NO-GO, or VERIFIED verdict. "
                "The runtime computes the next bridge path/version. VERIFIED also requires "
                "include_paths and commit_message; hunk_patch_paths is optional."
            ),
            {
                "slug": {"type": "string"},
                "verdict": {"type": "string", "enum": ["GO", "NO-GO", "VERIFIED"]},
                "content": {"type": "string"},
                "include_paths": {"type": "array", "items": {"type": "string"}},
                "hunk_patch_paths": {"type": "array", "items": {"type": "string"}},
                "commit_message": {"type": "string"},
            },
            ["slug", "verdict", "content"],
        ),
    }
    allowed = tuple(allowed_tools)
    unknown = sorted(set(allowed) - CANONICAL_TOOLS)
    if unknown:
        raise CloudHarnessError(f"unknown allowed tools: {unknown}")
    return [schemas[name] for name in allowed]


def allowed_tools_for_skill(
    allowed_tools: Iterable[str],
    skill: str | None,
    *,
    publish_bridge_verdict_tool: bool = False,
) -> tuple[str, ...]:
    allowed = tuple(allowed_tools)
    without_verdict = tuple(name for name in allowed if name != PUBLISH_BRIDGE_VERDICT_TOOL)
    if publish_bridge_verdict_tool and skill in LOYAL_OPPOSITION_BRIDGE_SKILLS:
        return (*without_verdict, PUBLISH_BRIDGE_VERDICT_TOOL)
    return without_verdict


def _call_with_wall_clock_bound(
    func: Callable[[], Any],
    bound_seconds: float,
    *,
    label: str,
    noun: str,
) -> Any:
    """Run ``func`` on a daemon worker thread bounded by a hard wall clock (WI-5066).

    ``urllib.request.urlopen(timeout=...)`` bounds socket connect/read but NOT
    ``getaddrinfo`` (DNS resolution), which runs before the socket exists. A DNS
    stall therefore escapes the socket timeout and blocks the caller with no
    socket and no output. Running the call on a worker thread and joining for a
    hard wall-clock bound caps the whole call (DNS + connect + TLS + read).

    On expiry a :class:`_ProviderCallTimeout` (a ``TimeoutError``) is raised so the
    caller's bounded-retry classifier treats it as retryable transport; the
    orphaned worker thread is a daemon and never blocks interpreter exit. Any
    exception raised inside ``func`` is re-raised to the caller unchanged.
    """
    result_box: list[Any] = []
    error_box: list[BaseException] = []

    def _runner() -> None:
        try:
            result_box.append(func())
        except BaseException as exc:  # noqa: BLE001 - propagated to the caller thread
            error_box.append(exc)

    worker = threading.Thread(target=_runner, name=f"{label}-{noun}-call", daemon=True)
    worker.start()
    worker.join(bound_seconds)
    if worker.is_alive():
        raise _ProviderCallTimeout(
            f"{label} {noun} call exceeded {bound_seconds:.1f}s wall-clock bound "
            "(DNS/connect/TLS stall not covered by the socket timeout)"
        )
    if error_box:
        raise error_box[0]
    if not result_box:
        raise CloudHarnessError(f"{label} {noun} call returned no result")
    return result_box[0]


def _post_json_with_bounded_retry(
    url: str,
    payload: dict[str, Any],
    timeout: float,
    *,
    label: str,
    noun: str,
    headers: Mapping[str, str],
) -> dict[str, Any]:
    """Shared framework-free POST-JSON transport with bounded retry/backoff.

    ``label`` names the provider and ``noun`` names the endpoint kind (``"completions"``
    for the openai-chat dialect, ``"messages"`` for anthropic-messages) so the two
    dialects share one transport while keeping dialect-accurate error text.
    """
    deadline = time.monotonic() + timeout
    body = json.dumps(payload).encode("utf-8")
    request_headers = dict(headers)
    last_error: Exception | None = None
    for attempt in range(1, CHAT_MAX_ATTEMPTS + 1):
        remaining = _remaining_timeout(deadline, f"{label} {noun} request timed out")
        # WI-5066: run the whole call (DNS + connect + TLS + read) under a hard
        # wall-clock bound so a getaddrinfo stall -- which urlopen(timeout=) cannot
        # bound -- becomes a bounded, retryable timeout. The socket timeout is set
        # a grace shorter than the wall-clock join so a genuine socket stall raises
        # an accurately-classified URLError before the join synthesizes a timeout.
        socket_timeout = max(0.1, remaining - PROVIDER_CALL_WALL_CLOCK_GRACE_SECONDS)

        def _urlopen_read(_timeout: float = socket_timeout) -> str:
            # Fresh Request per attempt so an orphaned worker thread from a prior
            # attempt (still stuck in getaddrinfo) never shares mutable Request state.
            request = urllib.request.Request(url, data=body, headers=dict(request_headers), method="POST")
            with urllib.request.urlopen(request, timeout=_timeout) as response:  # noqa: S310
                return response.read().decode("utf-8")

        try:
            data = _call_with_wall_clock_bound(_urlopen_read, remaining, label=label, noun=noun)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < CHAT_MAX_ATTEMPTS:
                _sleep_with_budget(
                    _http_retry_delay_seconds(exc, attempt),
                    deadline,
                    f"{label} {noun} request timed out before retry",
                )
                continue
            if exc.code == 429:
                retry_after = _retry_after_delay_seconds(exc)
                retry_after_suffix = f"; retry_after_seconds={retry_after:g}" if retry_after is not None else ""
                raise CloudHarnessError(
                    f"{label} rate limited (HTTP 429 provider backpressure) "
                    f"after {attempt} attempt(s){retry_after_suffix}: {exc}"
                ) from exc
            raise CloudHarnessError(
                f"{label} {noun} request failed (HTTP {exc.code}) after {attempt} attempt(s): {exc}"
            ) from exc
        except (urllib.error.URLError, ConnectionError, TimeoutError, ssl.SSLError) as exc:
            last_error = exc
            retryable = _is_retryable_provider_transport_error(exc)
            if retryable and attempt < CHAT_MAX_ATTEMPTS:
                _sleep_with_budget(
                    CHAT_RETRY_BACKOFF_SECONDS[attempt - 1],
                    deadline,
                    f"{label} {noun} request timed out before retry",
                )
                continue
            if isinstance(exc, ssl.SSLError):
                summary = _provider_transport_error_summary(exc)
                raise CloudHarnessError(
                    f"{label} provider transport failure after {attempt} attempt(s): {summary}"
                ) from exc
            raise CloudHarnessError(f"{label} {noun} request failed after {attempt} attempt(s): {exc}") from exc
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as exc:
            last_error = exc
            if attempt < CHAT_MAX_ATTEMPTS:
                _sleep_with_budget(
                    CHAT_RETRY_BACKOFF_SECONDS[attempt - 1],
                    deadline,
                    f"{label} {noun} request timed out before retry",
                )
                continue
            snippet = data[:200].replace("\n", " ")
            raise CloudHarnessError(
                f"{label} {noun} response was not JSON after {attempt} attempt(s) (body snippet: {snippet!r}): {exc}"
            ) from exc
        if not isinstance(parsed, dict):
            raise CloudHarnessError(f"{label} {noun} response must be a JSON object")
        return parsed
    raise CloudHarnessError(f"{label} {noun} request failed after {CHAT_MAX_ATTEMPTS} attempt(s): {last_error}")


def openai_chat_completion(
    endpoint: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    *,
    label: str,
    extra_headers: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """The ``openai-chat`` dialect transport: POST to ``<endpoint>/chat/completions``.

    ``label`` names the provider in error messages (e.g. ``"OpenRouter"``); token auth is
    sent via an ``Authorization`` header, keyed on the caller-supplied ``api_key`` value.
    """
    url = endpoint.rstrip("/") + "/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }
    if extra_headers:
        headers.update(extra_headers)
    return _post_json_with_bounded_retry(url, payload, timeout, label=label, noun="completions", headers=headers)


def anthropic_messages_completion(
    endpoint: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    *,
    label: str,
    extra_headers: Mapping[str, str] | None = None,
    auth_style: str = AUTH_STYLE_AUTHORIZATION_BEARER,
    anthropic_version: str = DEFAULT_ANTHROPIC_VERSION,
) -> dict[str, Any]:
    """The ``anthropic-messages`` dialect transport: POST to ``<endpoint>/messages``.

    Token auth is configurable by ``auth_style``: native Anthropic uses ``x-api-key``;
    Anthropic-compatible cloud endpoints that reject it (Ollama upstream issue #16922)
    use ``Authorization: Bearer``. The token value is keyed on the caller-supplied
    ``api_key`` (referenced by env-key NAME upstream, per GOV-ENV-LOCAL-AUTHORITY-001).
    """
    url = endpoint.rstrip("/") + "/messages"
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": anthropic_version,
    }
    if auth_style == AUTH_STYLE_X_API_KEY:
        headers["x-api-key"] = api_key
    else:
        headers["Authorization"] = "Bearer " + api_key
    if extra_headers:
        headers.update(extra_headers)
    return _post_json_with_bounded_retry(url, payload, timeout, label=label, noun="messages", headers=headers)


def _openai_build_payload(
    messages: list[dict[str, Any]], model_route: ModelRoute, tool_schemas: list[dict[str, Any]]
) -> dict[str, Any]:
    """openai-chat request payload (byte-identical to the slice-2 inline build)."""
    payload: dict[str, Any] = {"messages": messages, "stream": False}
    if not model_route.omit_payload_model:
        payload["model"] = model_route.model_id
    if tool_schemas:
        payload["tools"] = tool_schemas
    return payload


def _anthropic_build_tool_schemas(allowed_tools: Iterable[str]) -> list[dict[str, Any]]:
    """Anthropic tool schema: the same tool definitions under ``input_schema`` (no function wrapper)."""
    return [
        {
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "input_schema": schema["function"]["parameters"],
        }
        for schema in build_tool_schemas(allowed_tools)
    ]


def _anthropic_build_payload(
    messages: list[dict[str, Any]],
    model_route: ModelRoute,
    tool_schemas: list[dict[str, Any]],
    *,
    max_tokens: int,
) -> dict[str, Any]:
    """Translate the internal (openai-shaped) message history into an Anthropic Messages payload.

    system → top-level ``system``; assistant ``tool_calls`` → ``tool_use`` blocks; ``tool``
    results are coalesced into a following user message of ``tool_result`` blocks.
    """
    system_text: str | None = None
    out_messages: list[dict[str, Any]] = []
    pending_tool_results: list[dict[str, Any]] = []

    def _flush_tool_results() -> None:
        nonlocal pending_tool_results
        if pending_tool_results:
            out_messages.append({"role": "user", "content": pending_tool_results})
            pending_tool_results = []

    for message in messages:
        role = message.get("role")
        if role == "system":
            system_text = message.get("content") or ""
            continue
        if role == "tool":
            content = message.get("content")
            pending_tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": message.get("tool_call_id") or "",
                    "content": content if isinstance(content, str) else str(content),
                }
            )
            continue
        _flush_tool_results()
        if role == "user":
            out_messages.append({"role": "user", "content": message.get("content") or ""})
        elif role == "assistant":
            blocks: list[dict[str, Any]] = []
            text = message.get("content")
            if text:
                blocks.append({"type": "text", "text": text})
            for tool_call in message.get("tool_calls") or []:
                function = tool_call.get("function") or {}
                arguments = function.get("arguments")
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}
                if not isinstance(arguments, dict):
                    arguments = {}
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": tool_call.get("id") or "",
                        "name": function.get("name") or "",
                        "input": arguments,
                    }
                )
            out_messages.append({"role": "assistant", "content": blocks})
    _flush_tool_results()

    payload: dict[str, Any] = {
        "model": model_route.model_id,
        "max_tokens": max_tokens,
        "messages": out_messages,
    }
    if system_text:
        payload["system"] = system_text
    if tool_schemas:
        payload["tools"] = tool_schemas
    return payload


def _anthropic_parse_message(response: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize an Anthropic Messages response into the internal ``{content, tool_calls}`` shape."""
    content_blocks = response.get("content")
    if not isinstance(content_blocks, list):
        raise CloudHarnessError("Anthropic response missing content block list")
    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    for index, block in enumerate(content_blocks):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text = block.get("text")
            if isinstance(text, str):
                text_parts.append(text)
        elif block_type == "tool_use":
            name = block.get("name")
            if not isinstance(name, str) or not name:
                raise CloudHarnessError("Anthropic tool_use block missing name")
            tool_calls.append(
                {
                    "id": str(block.get("id") or f"tool_use_{index}"),
                    "function": {"name": name, "arguments": block.get("input") or {}},
                }
            )
    return {"content": "".join(text_parts), "tool_calls": tool_calls}


@dataclass(frozen=True)
class DialectStrategy:
    """Per-dialect request-build / tool-schema / response-parse / transport bundle."""

    build_tool_schemas: Callable[[Iterable[str]], list[dict[str, Any]]]
    build_payload: Callable[[list[dict[str, Any]], ModelRoute, list[dict[str, Any]]], dict[str, Any]]
    parse_message: Callable[[Mapping[str, Any]], dict[str, Any]]
    chat: ChatFunc


def resolve_dialect_strategy(profile: AdopterProfile) -> DialectStrategy:
    """Return the full dialect strategy for the profile's dialect.

    Slice 2 implemented ``openai-chat``; slice 3 adds ``anthropic-messages``. ``ollama-native``
    remains the lone seam point (implemented with the Ollama re-base in slice 4) and raises an
    explicit sentinel so a misconfigured adopter fails loudly rather than silently no-op.
    """
    if profile.dialect == DIALECT_OPENAI_CHAT:
        return DialectStrategy(
            build_tool_schemas=build_tool_schemas,
            build_payload=_openai_build_payload,
            parse_message=_message_from_response,
            chat=functools.partial(
                openai_chat_completion,
                label=profile.display_name,
                extra_headers=dict(profile.extra_headers),
            ),
        )
    if profile.dialect == DIALECT_ANTHROPIC_MESSAGES:
        return DialectStrategy(
            build_tool_schemas=_anthropic_build_tool_schemas,
            build_payload=functools.partial(_anthropic_build_payload, max_tokens=profile.max_tokens),
            parse_message=_anthropic_parse_message,
            chat=functools.partial(
                anthropic_messages_completion,
                label=profile.display_name,
                extra_headers=dict(profile.extra_headers),
                auth_style=profile.auth_style,
                anthropic_version=profile.anthropic_version,
            ),
        )
    if profile.dialect == DIALECT_OLLAMA_NATIVE:
        raise NotImplementedError(
            "dialect 'ollama-native' is a slice-4 seam point (implemented with the Ollama "
            "re-base in slice 4); not implemented in slice 3"
        )
    raise CloudHarnessError(f"unknown dialect {profile.dialect!r}")


def resolve_dialect_chat_func(profile: AdopterProfile) -> ChatFunc:
    """Return only the transport for the profile's dialect (compat shim over the strategy)."""
    return resolve_dialect_strategy(profile).chat


def _resolve_tool_path(project_root: Path, path_text: str, *, allow_missing: bool) -> Path:
    if not path_text or not path_text.strip():
        raise CloudHarnessError("tool path must be a non-empty string")
    raw = Path(path_text)
    candidate = raw if raw.is_absolute() else project_root / raw
    try:
        resolved = candidate.resolve(strict=not allow_missing)
    except FileNotFoundError as exc:
        if not allow_missing:
            raise CloudHarnessError(f"file not found: {path_text}") from exc
        resolved = candidate.resolve(strict=False)
    except OSError as exc:
        raise CloudHarnessError(f"tool path could not be resolved: {path_text}") from exc
    _ensure_under_root(project_root, resolved, path_text)
    return resolved


def _ensure_under_root(project_root: Path, resolved: Path, original: str) -> None:
    root = project_root.resolve()
    if resolved != root and root not in resolved.parents:
        raise CloudHarnessError(f"tool path escapes project root: {original}")


def _relative_path(project_root: Path, path: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def _relative_path_or_none(
    project_root: Path, path: Path, *, relative_path: RelativePathFunc = _relative_path
) -> str | None:
    try:
        return relative_path(project_root, path)
    except (OSError, ValueError):
        return None


def _is_bridge_markdown_path(project_root: Path, path: Path) -> bool:
    rel = _relative_path_or_none(project_root, path)
    return bool(rel and rel.startswith("bridge/") and rel.endswith(".md"))


def _first_nonblank_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _content_status_token(content: str) -> str:
    parts = _first_nonblank_line(content).split(maxsplit=1)
    return parts[0].upper() if parts else ""


def normalize_bridge_author_model_metadata(
    content: str,
    model_metadata: ModelMetadata,
    project_root: Path,
    path: Path,
    profile: AdopterProfile,
) -> str:
    if not _is_bridge_markdown_path(project_root, path):
        return content
    if _content_status_token(content) not in {"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED"}:
        return content

    replacements = {
        "author_model": model_metadata.model_id,
        "author_model_version": model_metadata.model_version,
        "author_model_configuration": metadata_configuration(model_metadata, profile),
    }
    lines = content.splitlines()
    changed = False
    for index, line in enumerate(lines):
        key, separator, _value = line.partition(":")
        normalized_key = key.strip().lower()
        if separator and normalized_key in replacements:
            lines[index] = f"{normalized_key}: {replacements[normalized_key]}"
            changed = True
    if not changed:
        return content
    normalized = "\n".join(lines)
    if content.endswith("\n"):
        normalized += "\n"
    return normalized


def set_author_metadata_env(
    env: Mapping[str, str],
    model_id: str,
    model_version: str,
    profile: AdopterProfile,
    endpoint: str | None = None,
    model_configuration: str | None = None,
) -> dict[str, str]:
    updated = dict(env)
    effective_endpoint = endpoint or profile.default_endpoint
    session_id = resolve_harness_session_id(env)
    updated.update(
        {
            "GTKB_AUTHOR_IDENTITY": profile.author_identity,
            "GTKB_AUTHOR_HARNESS_ID": profile.author_harness_id,
            "GTKB_AUTHOR_MODEL": model_id,
            "GTKB_AUTHOR_MODEL_VERSION": model_version,
            "GTKB_AUTHOR_MODEL_CONFIGURATION": model_configuration
            or _default_config_label(profile, effective_endpoint),
        }
    )
    if session_id:
        updated["GTKB_AUTHOR_SESSION_CONTEXT_ID"] = session_id
    return updated


def _default_guard_runner(
    guard_path: Path,
    payload: dict[str, Any],
    env: Mapping[str, str],
    timeout: float,
) -> GuardExecutionResult:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0
    try:
        completed = subprocess.run(
            [sys.executable, str(guard_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=str(payload.get("cwd") or Path.cwd()),
            env=dict(env),
            timeout=timeout,
            check=False,
            creationflags=creationflags,
        )
    except subprocess.TimeoutExpired as exc:
        return GuardExecutionResult(-1, exc.stdout or "", exc.stderr or "", timed_out=True)
    return GuardExecutionResult(completed.returncode, completed.stdout, completed.stderr)


def _expand_native_hook_command(command: str, env: Mapping[str, str]) -> str:
    expanded = command
    for key in ("CLAUDE_PROJECT_DIR", "GTKB_PROJECT_ROOT"):
        if key in env:
            expanded = expanded.replace(f"${{{key}}}", env[key])
            expanded = expanded.replace(f"${key}", env[key])
            expanded = expanded.replace(f"%{key}%", env[key])
    return expanded


def _default_native_hook_runner(
    command: str,
    payload: dict[str, Any],
    env: Mapping[str, str],
    timeout: float,
) -> GuardExecutionResult:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0
    expanded_command = _expand_native_hook_command(command, env)
    try:
        completed = subprocess.run(
            expanded_command,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=str(payload.get("cwd") or Path.cwd()),
            env=dict(env),
            timeout=timeout,
            check=False,
            shell=True,
            creationflags=creationflags,
        )
    except subprocess.TimeoutExpired as exc:
        return GuardExecutionResult(-1, exc.stdout or "", exc.stderr or "", timed_out=True)
    return GuardExecutionResult(completed.returncode, completed.stdout, completed.stderr)


def _decision_reason(data: dict[str, Any]) -> str | None:
    decision = str(data.get("decision") or "").lower()
    if decision in {"block", "deny", "ask", "checkpoint"}:
        return str(data.get("reason") or data.get("permissionDecisionReason") or f"guard decision: {decision}")
    hook = data.get("hookSpecificOutput")
    if isinstance(hook, dict):
        permission = str(hook.get("permissionDecision") or "").lower()
        if permission in {"deny", "block", "ask", "checkpoint"}:
            return str(
                hook.get("permissionDecisionReason")
                or hook.get("additionalContext")
                or f"guard permission decision: {permission}"
            )
    return None


def _native_hook_block_reason(data: Mapping[str, Any] | None) -> str | None:
    if not isinstance(data, dict):
        return None
    decision = str(data.get("decision") or "").lower()
    if decision == "block":
        return str(data.get("reason") or data.get("permissionDecisionReason") or "native hook blocked tool use")
    reason = _decision_reason(dict(data))
    return reason


def _load_native_hook_settings(project_root: Path) -> Mapping[str, Any]:
    settings_path = project_root / NATIVE_HOOK_SETTINGS_PATH
    if not settings_path.is_file():
        return {}
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CloudHarnessError(f"native hook settings malformed JSON: {NATIVE_HOOK_SETTINGS_PATH.as_posix()}") from exc
    if not isinstance(data, dict):
        raise CloudHarnessError(f"native hook settings must be a JSON object: {NATIVE_HOOK_SETTINGS_PATH.as_posix()}")
    hooks = data.get("hooks") or {}
    if not isinstance(hooks, dict):
        raise CloudHarnessError(
            f"native hook settings hooks must be a JSON object: {NATIVE_HOOK_SETTINGS_PATH.as_posix()}"
        )
    return hooks


def _native_hook_matcher_matches(matcher: Any, tool_name: str | None) -> bool:
    if matcher in (None, ""):
        return True
    if tool_name is None:
        return False
    if not isinstance(matcher, str):
        raise CloudHarnessError("native hook matcher must be a string")
    for token in (part.strip() for part in matcher.split("|")):
        if token and (token == tool_name or fnmatch.fnmatchcase(tool_name, token)):
            return True
    return False


def _native_hook_command_timeout(raw_timeout: Any) -> float:
    if raw_timeout in (None, ""):
        return DEFAULT_NATIVE_HOOK_TIMEOUT_SECONDS
    if isinstance(raw_timeout, bool):
        raise CloudHarnessError("native hook timeout must be a positive number")
    try:
        timeout = float(raw_timeout)
    except (TypeError, ValueError) as exc:
        raise CloudHarnessError("native hook timeout must be a positive number") from exc
    if timeout <= 0:
        raise CloudHarnessError("native hook timeout must be a positive number")
    return timeout


def _iter_native_hook_commands(
    hooks: Mapping[str, Any],
    event_name: str,
    tool_name: str | None,
) -> Iterable[tuple[str, float]]:
    registrations = hooks.get(event_name) or []
    if not isinstance(registrations, list):
        raise CloudHarnessError(f"native hook event {event_name} must be a list")
    for registration in registrations:
        if not isinstance(registration, dict):
            raise CloudHarnessError(f"native hook event {event_name} registration must be a JSON object")
        if not _native_hook_matcher_matches(registration.get("matcher"), tool_name):
            continue
        raw_hooks = registration.get("hooks") or []
        if not isinstance(raw_hooks, list):
            raise CloudHarnessError(f"native hook event {event_name} hooks must be a list")
        for hook in raw_hooks:
            if not isinstance(hook, dict):
                raise CloudHarnessError(f"native hook event {event_name} hook must be a JSON object")
            hook_type = str(hook.get("type") or "command")
            if hook_type != "command":
                raise CloudHarnessError(f"unsupported native hook type for {event_name}: {hook_type}")
            command = hook.get("command")
            if not isinstance(command, str) or not command.strip():
                raise CloudHarnessError(f"native hook event {event_name} command must be nonblank")
            yield command, _native_hook_command_timeout(hook.get("timeout"))


def _native_hook_env(
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
) -> dict[str, str]:
    env = set_author_metadata_env(
        os.environ,
        model_metadata.model_id,
        model_metadata.model_version,
        profile,
        model_metadata.endpoint,
        model_metadata.model_configuration,
    )
    env["CLAUDE_PROJECT_DIR"] = str(project_root)
    env["GTKB_PROJECT_ROOT"] = str(project_root)
    return env


def _native_hook_payload(
    event_name: str,
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    *,
    prompt: str | None = None,
    tool_name: str | None = None,
    tool_input: Mapping[str, Any] | None = None,
    tool_response: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "hook_event_name": event_name,
        "cwd": str(project_root),
        "project_root": str(project_root),
        "session_id": resolve_harness_session_id(os.environ),
        "transcript_path": "",
        "profile": {
            "display_name": profile.display_name,
            "author_identity": profile.author_identity,
            "author_harness_id": profile.author_harness_id,
            "hook_tier": profile.hook_tier,
            "dialect": profile.dialect,
        },
        "model_metadata": {
            "model_id": model_metadata.model_id,
            "model_version": model_metadata.model_version,
            "endpoint": model_metadata.endpoint,
            "route_key": model_metadata.route_key,
            "model_configuration": model_metadata.model_configuration,
            "requested_model_id": model_metadata.requested_model_id,
        },
    }
    if prompt is not None:
        payload["prompt"] = prompt
    if tool_name is not None:
        payload["tool_name"] = tool_name
    if tool_input is not None:
        payload["tool_input"] = dict(tool_input)
    if tool_response is not None:
        payload["tool_response"] = tool_response[:MAX_TOOL_OUTPUT_CHARS]
    return payload


def invoke_native_hooks(
    event_name: str,
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    *,
    prompt: str | None = None,
    tool_name: str | None = None,
    tool_input: Mapping[str, Any] | None = None,
    tool_response: str | None = None,
    native_hook_runner: NativeHookRunner | None = None,
) -> dict[str, Any] | None:
    if profile.hook_tier != HOOK_TIER_NATIVE_FULL:
        return None
    if event_name not in NATIVE_HOOK_EVENTS:
        raise CloudHarnessError(f"unsupported native hook event: {event_name}")

    hooks = _load_native_hook_settings(project_root)
    env = _native_hook_env(model_metadata, project_root, profile)
    payload = _native_hook_payload(
        event_name,
        model_metadata,
        project_root,
        profile,
        prompt=prompt,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_response=tool_response,
    )
    runner = native_hook_runner or _default_native_hook_runner
    last_output: dict[str, Any] | None = None
    post_tool_event = event_name == NATIVE_HOOK_POST_TOOL_USE
    for command, hook_timeout in _iter_native_hook_commands(hooks, event_name, tool_name):
        result = runner(command, payload, env, hook_timeout)
        command_label = command[:120]
        if result.timed_out:
            if post_tool_event:
                continue
            raise CloudHarnessError(f"native hook timed out: {event_name}: {command_label}")
        if result.returncode != 0:
            if post_tool_event:
                continue
            raise CloudHarnessError(f"native hook exited nonzero: {event_name}: {command_label} ({result.returncode})")
        stdout = (result.stdout or "").strip()
        if not stdout:
            continue
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError as exc:
            if post_tool_event:
                continue
            raise CloudHarnessError(f"native hook emitted malformed JSON: {event_name}: {command_label}") from exc
        if not isinstance(data, dict):
            if post_tool_event:
                continue
            raise CloudHarnessError(f"native hook output must be a JSON object: {event_name}: {command_label}")
        reason = _native_hook_block_reason(data)
        if reason:
            if event_name == NATIVE_HOOK_PRE_TOOL_USE:
                return {"decision": "block", "reason": reason}
            raise CloudHarnessError(f"native hook blocked {event_name}: {command_label}: {reason}")
        last_output = data
    return last_output or {}


def _guard_tool_input(tool_name: str, arguments: Mapping[str, Any], project_root: Path) -> dict[str, Any]:
    if tool_name == "Write":
        path = _resolve_tool_path(
            project_root, str(arguments.get("path") or arguments.get("file_path")), allow_missing=True
        )
        return {"file_path": str(path), "content": str(arguments.get("content", ""))}
    if tool_name == "Edit":
        path = _resolve_tool_path(
            project_root, str(arguments.get("path") or arguments.get("file_path")), allow_missing=False
        )
        return {
            "file_path": str(path),
            "old_string": str(arguments.get("old_string", "")),
            "new_string": str(arguments.get("new_string", "")),
        }
    if tool_name == "Bash":
        return {"command": str(arguments.get("command", ""))}
    raise CloudHarnessError(f"guard adapter does not support tool: {tool_name}")


def _guard_paths_for(tool_name: str, tool_input: Mapping[str, Any], project_root: Path) -> tuple[Path, ...]:
    if tool_name == "Bash":
        return BASH_GUARDS
    file_path = str(tool_input.get("file_path") or "")
    rel = _relative_path(project_root, Path(file_path))
    is_bridge_file = rel.startswith("bridge/") and rel.endswith(".md")
    if tool_name == "Write" and is_bridge_file:
        return BRIDGE_WRITE_GUARDS
    if tool_name == "Edit" and is_bridge_file:
        return BRIDGE_EDIT_GUARDS
    if tool_name in {"Write", "Edit"}:
        return WRITE_EDIT_GUARDS
    raise CloudHarnessError(f"unsupported guarded tool: {tool_name}")


def invoke_guard_adapter(
    tool_name: str,
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    *,
    guard_runner: GuardRunner | None = None,
    guard_paths: Sequence[Path] | None = None,
    timeout: float = 10.0,
) -> None:
    """Fail-closed guard-adapter enforcement (generalized DCL-OLLAMA-TOOL-PARITY-GATE-001).

    Runs the required guard sequence for a mutating tool; any guard denial, timeout,
    nonzero exit, empty/malformed output, or missing guard script fails closed.
    """
    if tool_name not in MUTATING_TOOLS:
        return
    tool_input = _guard_tool_input(tool_name, arguments, project_root)
    paths = tuple(guard_paths) if guard_paths is not None else _guard_paths_for(tool_name, tool_input, project_root)
    runner = guard_runner or _default_guard_runner
    env = set_author_metadata_env(
        os.environ,
        model_metadata.model_id,
        model_metadata.model_version,
        profile,
        model_metadata.endpoint,
        model_metadata.model_configuration,
    )
    payload = {
        "tool_name": tool_name,
        "tool_input": tool_input,
        "cwd": str(project_root),
        "project_root": str(project_root),
        "session_id": resolve_harness_session_id(os.environ),
    }
    for relative_guard_path in paths:
        guard_path = relative_guard_path if relative_guard_path.is_absolute() else project_root / relative_guard_path
        if not guard_path.is_file():
            raise CloudHarnessError(f"guard script is missing: {relative_guard_path.as_posix()}")
        result = runner(guard_path, payload, env, timeout)
        if result.timed_out:
            raise CloudHarnessError(f"guard timed out: {_relative_path(project_root, guard_path)}")
        if result.returncode != 0:
            raise CloudHarnessError(
                f"guard exited nonzero: {_relative_path(project_root, guard_path)} ({result.returncode})"
            )
        stdout = (result.stdout or "").strip()
        if not stdout:
            raise CloudHarnessError(f"guard emitted empty output: {_relative_path(project_root, guard_path)}")
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise CloudHarnessError(
                f"guard emitted malformed JSON: {_relative_path(project_root, guard_path)}"
            ) from exc
        if not isinstance(data, dict):
            raise CloudHarnessError(f"guard output must be a JSON object: {_relative_path(project_root, guard_path)}")
        reason = _decision_reason(data)
        if reason:
            raise CloudHarnessError(f"guard denied {tool_name}: {_relative_path(project_root, guard_path)}: {reason}")


def _require_string(arguments: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = arguments.get(name)
        if isinstance(value, str) and value:
            return value
    raise CloudHarnessError(f"missing required argument: {'/'.join(names)}")


def _positive_int_argument(arguments: Mapping[str, Any], name: str, default: int) -> int:
    if name not in arguments:
        return default

    value = arguments[name]
    parsed: int | None = None
    if isinstance(value, bool):
        parsed = None
    elif isinstance(value, int):
        parsed = value
    elif isinstance(value, float):
        parsed = int(value) if value.is_integer() else None
    elif isinstance(value, str):
        text = value.strip()
        if re.fullmatch(r"\d+(?:\.0+)?", text):
            parsed = int(text.split(".", 1)[0])

    if parsed is None or parsed <= 0:
        raise CloudHarnessError(f"{name} must be a positive integer")
    return parsed


def _string_list_argument(arguments: Mapping[str, Any], name: str) -> tuple[str, ...]:
    value = arguments.get(name, [])
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise CloudHarnessError(f"{name} must be an array of non-empty strings")
    return tuple(item.strip() for item in value)


def _load_provider_verdict_publisher(project_root: Path) -> Callable[..., Any]:
    root_text = str(project_root.resolve())
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    try:
        from scripts.gtkb_bridge_writer import publish_lo_verdict
    except ModuleNotFoundError as exc:
        raise CloudHarnessError(
            f"governed bridge verdict publisher is unavailable from project root {root_text}: {exc}"
        ) from exc
    return publish_lo_verdict


def ensure_dispatch_worker_role_document(project_root: Path, profile: AdopterProfile) -> None:
    keyword = os.environ.get("GTKB_BRIDGE_DISPATCH_KEYWORD", "").strip().lower()
    if not keyword:
        return
    role = DISPATCH_KEYWORD_ROLES.get(keyword)
    if role is None:
        raise CloudHarnessError(f"unsupported dispatcher init keyword for worker role authority: {keyword!r}")
    session_id = resolve_harness_session_id(os.environ)
    if not session_id:
        raise CloudHarnessError("dispatcher worker role authority requires a concrete dispatch session id")
    try:
        from groundtruth_kb.session.envelope import ensure_worker_session

        ensure_worker_session(
            project_root,
            harness_name=profile.provider_routing_key,
            harness_id=profile.author_harness_id,
            session_id=session_id,
            role=role,
            role_source="dispatcher_composition",
            init_keyword=keyword,
            dispatch_run_id=session_id,
        )
    except (ImportError, OSError, ValueError) as exc:
        raise CloudHarnessError(f"could not establish dispatcher worker role authority: {exc}") from exc


def _dispatch_read(arguments: Mapping[str, Any], project_root: Path) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=True)
    max_chars = _positive_int_argument(arguments, "max_chars", MAX_TOOL_OUTPUT_CHARS)
    try:
        return path.read_text(encoding="utf-8")[:max_chars]
    except FileNotFoundError:
        return f"Read failed: file not found: {_relative_path(project_root, path)}"
    except OSError as exc:
        return f"Read failed: {_relative_path(project_root, path)}: {exc}"


def _dispatch_write(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    guard_runner: GuardRunner | None,
) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=True)
    content = str(arguments.get("content", ""))
    content = normalize_bridge_author_model_metadata(content, model_metadata, project_root, path, profile)
    invoke_guard_adapter(
        "Write",
        {"path": str(path), "content": content},
        model_metadata,
        project_root,
        profile,
        guard_runner=guard_runner,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote {_relative_path(project_root, path)}"


def _dispatch_publish_bridge_verdict(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    *,
    skill: str | None,
) -> str:
    if not profile.publish_bridge_verdict_tool:
        raise CloudHarnessError("PublishBridgeVerdict is not enabled for this provider profile")
    if skill not in LOYAL_OPPOSITION_BRIDGE_SKILLS:
        raise CloudHarnessError("PublishBridgeVerdict is available only for bridge-review/verification skills")
    session_id = resolve_harness_session_id(os.environ)
    if not session_id:
        raise CloudHarnessError("PublishBridgeVerdict requires a concrete dispatcher session id")
    slug = _require_string(arguments, "slug")
    verdict = _require_string(arguments, "verdict")
    content = _require_string(arguments, "content")
    include_paths = _string_list_argument(arguments, "include_paths")
    hunk_patch_paths = _string_list_argument(arguments, "hunk_patch_paths")
    commit_message = str(arguments.get("commit_message") or "")

    try:
        publish_lo_verdict = _load_provider_verdict_publisher(project_root)
        published = publish_lo_verdict(
            slug,
            verdict,
            content,
            project_root,
            session_id=session_id,
            harness_name=profile.provider_routing_key,
            author_metadata={
                "author_identity": profile.author_identity,
                "author_harness_id": profile.author_harness_id,
                "author_session_context_id": session_id,
                "author_model": model_metadata.model_id,
                "author_model_version": model_metadata.model_version,
                "author_model_configuration": model_metadata.model_configuration
                or _default_config_label(profile, model_metadata.endpoint),
            },
            include_paths=include_paths,
            hunk_patch_paths=hunk_patch_paths,
            commit_message=commit_message,
        )
    except Exception as exc:
        raise CloudHarnessError(f"governed bridge verdict publication failed: {exc}") from exc
    return json.dumps(published.to_dict(), sort_keys=True)


def _dispatch_edit(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    guard_runner: GuardRunner | None,
) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=False)
    old_string = _require_string(arguments, "old_string")
    new_string = str(arguments.get("new_string", ""))
    invoke_guard_adapter(
        "Edit",
        {"path": str(path), "old_string": old_string, "new_string": new_string},
        model_metadata,
        project_root,
        profile,
        guard_runner=guard_runner,
    )
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CloudHarnessError(f"file not found: {_relative_path(project_root, path)}") from exc
    except OSError as exc:
        raise CloudHarnessError(f"failed to read file {_relative_path(project_root, path)}: {exc}") from exc

    if old_string not in content:
        raise CloudHarnessError(f"old_string not found in {_relative_path(project_root, path)}")

    try:
        path.write_text(content.replace(old_string, new_string, 1), encoding="utf-8")
    except OSError as exc:
        raise CloudHarnessError(f"failed to write file {_relative_path(project_root, path)}: {exc}") from exc
    return f"edited {_relative_path(project_root, path)}"


def _iter_bounded_paths(root: Path, *, max_entries: int = MAX_FILE_SCAN_ENTRIES) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    seen = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIPPED_SCAN_DIR_NAMES)
        for name in [*dirnames, *sorted(filenames)]:
            seen += 1
            if seen > max_entries:
                raise FileScanLimitExceeded(max_entries)
            yield Path(dirpath) / name


def _iter_text_files(root: Path, *, max_entries: int = MAX_FILE_SCAN_ENTRIES) -> Iterable[Path]:
    for path in _iter_bounded_paths(root, max_entries=max_entries):
        try:
            if path.is_file():
                yield path
        except OSError:
            continue


def _dispatch_grep(
    arguments: Mapping[str, Any],
    project_root: Path,
    *,
    relative_path: RelativePathFunc = _relative_path,
    iter_text_files: IterFilesFunc = _iter_text_files,
) -> str:
    pattern = _require_string(arguments, "pattern")
    base = _resolve_tool_path(project_root, str(arguments.get("path") or "."), allow_missing=False)
    max_results = _positive_int_argument(arguments, "max_results", MAX_GREP_RESULTS)
    regex = re.compile(pattern)
    matches: list[str] = []
    try:
        for file_path in iter_text_files(base):
            rel = _relative_path_or_none(project_root, file_path, relative_path=relative_path)
            if rel is None:
                continue
            try:
                for line_no, line in enumerate(
                    file_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
                ):
                    if regex.search(line):
                        matches.append(f"{rel}:{line_no}:{line[:300]}")
                        if len(matches) >= max_results:
                            return "\n".join(matches)
            except OSError:
                continue
    except FileScanLimitExceeded as exc:
        matches.append(f"[{exc}]")
    return "\n".join(matches)


def _dispatch_glob(
    arguments: Mapping[str, Any],
    project_root: Path,
    *,
    relative_path: RelativePathFunc = _relative_path,
    iter_bounded_paths: IterFilesFunc = _iter_bounded_paths,
) -> str:
    pattern = _require_string(arguments, "pattern")
    base = _resolve_tool_path(project_root, str(arguments.get("path") or "."), allow_missing=False)
    max_results = _positive_int_argument(arguments, "max_results", MAX_GLOB_RESULTS)
    matches: list[str] = []
    try:
        for path in iter_bounded_paths(base):
            rel = _relative_path_or_none(project_root, path, relative_path=relative_path)
            if rel is None:
                continue
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern):
                matches.append(rel)
                if len(matches) >= max_results:
                    break
    except FileScanLimitExceeded as exc:
        matches.append(f"[{exc}]")
    return "\n".join(sorted(matches))


def _default_command_runner(
    command: str,
    project_root: Path,
    env: Mapping[str, str],
    timeout: float,
) -> subprocess.CompletedProcess[str]:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        cwd=str(project_root),
        env=dict(env),
        timeout=timeout,
        shell=True,
        check=False,
        creationflags=creationflags,
    )


def _dispatch_bash(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    guard_runner: GuardRunner | None,
    command_runner: CommandRunner | None,
) -> str:
    command = _require_string(arguments, "command")
    timeout = float(arguments.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS)
    bridge_denial = bridge_bash_mutation_reason(command)
    if bridge_denial:
        raise CloudHarnessError(bridge_denial)
    invoke_guard_adapter("Bash", {"command": command}, model_metadata, project_root, profile, guard_runner=guard_runner)
    env = set_author_metadata_env(
        os.environ,
        model_metadata.model_id,
        model_metadata.model_version,
        profile,
        model_metadata.endpoint,
        model_metadata.model_configuration,
    )
    runner = command_runner or _default_command_runner
    try:
        completed = runner(command, project_root, env, timeout)
    except subprocess.TimeoutExpired as exc:
        raise CloudHarnessError(f"Bash command timed out: {command}") from exc
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if completed.returncode != 0:
        output = "\n".join(
            [
                f"Bash command exited with return code {completed.returncode}.",
                f"Command: {command}",
                "STDOUT:",
                stdout,
                "STDERR:",
                stderr,
            ]
        )
        return output[:MAX_TOOL_OUTPUT_CHARS]
    return (stdout + stderr)[:MAX_TOOL_OUTPUT_CHARS]


def dispatch_tool_call(
    tool_name: str,
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    profile: AdopterProfile,
    *,
    guard_runner: GuardRunner | None = None,
    command_runner: CommandRunner | None = None,
    relative_path: RelativePathFunc = _relative_path,
    iter_text_files: IterFilesFunc = _iter_text_files,
    iter_bounded_paths: IterFilesFunc = _iter_bounded_paths,
    skill: str | None = None,
) -> str:
    if tool_name not in CANONICAL_TOOLS:
        raise CloudHarnessError(f"unsupported tool: {tool_name}")
    if tool_name == "Read":
        return _dispatch_read(arguments, project_root)
    if tool_name == "Write":
        return _dispatch_write(arguments, model_metadata, project_root, profile, guard_runner)
    if tool_name == "Edit":
        return _dispatch_edit(arguments, model_metadata, project_root, profile, guard_runner)
    if tool_name == "Grep":
        return _dispatch_grep(arguments, project_root, relative_path=relative_path, iter_text_files=iter_text_files)
    if tool_name == "Glob":
        return _dispatch_glob(
            arguments, project_root, relative_path=relative_path, iter_bounded_paths=iter_bounded_paths
        )
    if tool_name == "Bash":
        return _dispatch_bash(arguments, model_metadata, project_root, profile, guard_runner, command_runner)
    if tool_name == PUBLISH_BRIDGE_VERDICT_TOOL:
        return _dispatch_publish_bridge_verdict(
            arguments,
            model_metadata,
            project_root,
            profile,
            skill=skill,
        )
    raise CloudHarnessError(f"unsupported tool: {tool_name}")


def _tool_call_parts(call: Any, index: int) -> tuple[str, dict[str, Any], str]:
    if not isinstance(call, dict):
        raise CloudHarnessError("tool_call entries must be JSON objects")

    call_id = str(call.get("id") or f"tool_call_{index}")
    function = call.get("function")
    if not isinstance(function, dict):
        raise CloudHarnessError("tool_call is missing function details")

    name = function.get("name")
    if not isinstance(name, str) or not name:
        raise CloudHarnessError("tool_call is missing function name")

    raw_arguments = function.get("arguments", {})
    if isinstance(raw_arguments, str):
        try:
            parsed = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError as exc:
            raise CloudHarnessError("tool_call arguments string must be JSON") from exc
        raw_arguments = parsed
    if not isinstance(raw_arguments, dict):
        raise CloudHarnessError("tool_call arguments must be an object")
    return name, raw_arguments, call_id


def run_diagnostic(project_root: Path, *, harness_id: str) -> dict[str, Any]:
    """Return the shared local diagnostic contract for a cloud harness.

    Cloud adapters inherit this read-only surface; diagnostic mode never opens
    a provider connection and derives role provenance from the worker document.
    """
    from groundtruth_kb.harness_diagnostic import diagnose_harness

    return diagnose_harness(project_root, harness_id)


def _message_from_response(response: Mapping[str, Any]) -> dict[str, Any]:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise CloudHarnessError("provider response missing choices list")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise CloudHarnessError("provider choice must be an object")

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise CloudHarnessError("provider response missing message object in choices[0]")
    return dict(message)


def _final_text_from_message(message: Mapping[str, Any]) -> str:
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise CloudHarnessError("assistant final message must contain nonblank text content")
    return content


def run_tool_loop(
    prompt: str,
    model_route: ModelRoute,
    endpoint: str,
    api_key: str,
    max_turns: int,
    project_root: Path,
    profile: AdopterProfile,
    *,
    skill: str | None = None,
    system_prompt: str | None = None,
    chat_func: ChatFunc | None = None,
    guard_runner: GuardRunner | None = None,
    native_hook_runner: NativeHookRunner | None = None,
    command_runner: CommandRunner | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    session_timeout: float = DEFAULT_SESSION_TIMEOUT_SECONDS,
    telemetry: Any | None = None,
) -> str:
    """Framework-free tool-call loop shared across cloud harnesses (dialect-agnostic).

    The dialect strategy (resolved from the profile via :func:`resolve_dialect_strategy`)
    owns request-build, tool-schema shaping, and response-parse; ``chat_func`` overrides
    only the transport (used by tests). The loop's control flow, tool dispatch, guard
    enforcement, no-progress dedup, and session-timeout are shared across dialects.
    """
    if max_turns < 1:
        raise CloudHarnessError("max_turns must be at least 1")
    if session_timeout <= 0:
        raise CloudHarnessError("session_timeout must be positive")
    ensure_dispatch_worker_role_document(project_root, profile)
    strategy = resolve_dialect_strategy(profile)
    schemas = strategy.build_tool_schemas(
        allowed_tools_for_skill(
            model_route.allowed_tools,
            skill,
            publish_bridge_verdict_tool=profile.publish_bridge_verdict_tool,
        )
    )
    chat = chat_func or strategy.chat
    metadata = ModelMetadata(
        model_route.model_id,
        model_route.model_version,
        endpoint,
        model_route.key,
        requested_model_id=model_route.model_id,
    )
    if telemetry is None:
        try:
            from groundtruth_kb.shim_dispatch_telemetry import create_dispatch_telemetry_observer

            telemetry = create_dispatch_telemetry_observer(
                project_root,
                harness_id=profile.author_harness_id,
                harness_name=profile.display_name.lower().replace(" ", "-"),
                provider=profile.provider_routing_key,
                model_id=model_route.model_id,
                model_version=model_route.model_version,
                turn_budget=max_turns,
            )
        except (ImportError, OSError, ValueError):
            telemetry = None
    session_deadline = time.monotonic() + session_timeout
    native_hooks_started = False
    if profile.hook_tier == HOOK_TIER_NATIVE_FULL:
        invoke_native_hooks(
            NATIVE_HOOK_SESSION_START,
            metadata,
            project_root,
            profile,
            native_hook_runner=native_hook_runner,
        )
        native_hooks_started = True

    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if profile.hook_tier == HOOK_TIER_NATIVE_FULL:
        invoke_native_hooks(
            NATIVE_HOOK_USER_PROMPT_SUBMIT,
            metadata,
            project_root,
            profile,
            prompt=prompt,
            native_hook_runner=native_hook_runner,
        )
    messages.append({"role": "user", "content": prompt})

    previous_tool_signature: str | None = None
    repeated_tool_signature_turns = 0

    stop_reason = "process_error"
    try:
        for _turn in range(max_turns):
            payload = strategy.build_payload(messages, model_route, schemas)

            operation_timeout = min(
                timeout,
                _remaining_timeout(session_deadline, "session timeout exceeded before provider chat turn"),
            )
            response = chat(endpoint, api_key, payload, operation_timeout)

            if "error" in response:
                stop_reason = "provider_error"
                error_details = response["error"]
                error_message = error_details.get("message") if isinstance(error_details, dict) else str(error_details)
                raise CloudHarnessError(f"provider API returned error: {error_message}")

            metadata = metadata_from_response(metadata, response, profile)
            if telemetry is not None:
                with contextlib.suppress(Exception):
                    telemetry.set_model(metadata.model_id, metadata.model_version)
            message = strategy.parse_message(response)
            tool_calls = message.get("tool_calls") or []

            tool_names = []
            if isinstance(tool_calls, list):
                for call in tool_calls:
                    function = call.get("function") if isinstance(call, dict) else None
                    tool_name = function.get("name") if isinstance(function, dict) else None
                    if isinstance(tool_name, str) and tool_name in CANONICAL_TOOLS:
                        tool_names.append(tool_name)
            if telemetry is not None:
                with contextlib.suppress(Exception):
                    telemetry.record_turn(_turn + 1, tool_names, provider_response=response)

            if not tool_calls:
                content = message.get("content")
                if isinstance(content, str) and content.strip():
                    stop_reason = "final_response"
                    return content
                messages.append({"role": "user", "content": BLANK_FINAL_RECOVERY_PROMPT})
                continue

            if not isinstance(tool_calls, list):
                raise CloudHarnessError("tool_calls must be a list")

            tool_signature = json.dumps(tool_calls, sort_keys=True, default=str)
            if tool_signature == previous_tool_signature:
                repeated_tool_signature_turns += 1
            else:
                previous_tool_signature = tool_signature
                repeated_tool_signature_turns = 1
            if repeated_tool_signature_turns > MAX_REPEATED_TOOL_SIGNATURE_TURNS:
                raise CloudHarnessError("repeated no-progress tool loop before final assistant text")

            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": message.get("content") or "",
                "tool_calls": tool_calls,
            }
            messages.append(assistant_message)

            for index, call in enumerate(tool_calls):
                tool_name, arguments, call_id = _tool_call_parts(call, index)
                if tool_name == "Bash":
                    arguments = dict(arguments)
                    requested_timeout = float(arguments.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS)
                    arguments["timeout_seconds"] = min(
                        requested_timeout,
                        _remaining_timeout(session_deadline, "session timeout exceeded before Bash tool call"),
                    )
                block = invoke_native_hooks(
                    NATIVE_HOOK_PRE_TOOL_USE,
                    metadata,
                    project_root,
                    profile,
                    tool_name=tool_name,
                    tool_input=arguments,
                    native_hook_runner=native_hook_runner,
                )
                block_reason = _native_hook_block_reason(block)
                if block_reason:
                    result = f"ERROR: native hook blocked {tool_name}: {block_reason}"
                else:
                    try:
                        result = dispatch_tool_call(
                            tool_name,
                            arguments,
                            metadata,
                            project_root,
                            profile,
                            guard_runner=guard_runner,
                            command_runner=command_runner,
                            skill=skill,
                        )
                    except CloudHarnessError as tool_err:
                        result = f"ERROR: {tool_err}"
                invoke_native_hooks(
                    NATIVE_HOOK_POST_TOOL_USE,
                    metadata,
                    project_root,
                    profile,
                    tool_name=tool_name,
                    tool_input=arguments,
                    tool_response=result,
                    native_hook_runner=native_hook_runner,
                )
                messages.append(
                    {
                        "role": "tool",
                        "name": tool_name,
                        "tool_call_id": call_id,
                        "content": result[:MAX_TOOL_OUTPUT_CHARS],
                    }
                )
        stop_reason = "max_turn_exhaustion"
        raise CloudHarnessError("max-turn exhaustion before final assistant text")
    except CloudHarnessError as exc:
        message = str(exc).lower()
        if "max-turn" in message:
            stop_reason = "max_turn_exhaustion"
        elif "repeated no-progress" in message:
            stop_reason = "no_progress_loop"
        elif "session timeout" in message:
            stop_reason = "session_timeout"
        elif any(marker in message for marker in ("provider", "request", "http", "api returned", "rate limit")):
            stop_reason = "provider_error"
        elif "guard" in message or "native hook" in message:
            stop_reason = "guard_error"
        raise
    finally:
        if telemetry is not None:
            with contextlib.suppress(Exception):
                telemetry.finish(stop_reason=stop_reason)
        if native_hooks_started:
            invoke_native_hooks(
                NATIVE_HOOK_STOP,
                metadata,
                project_root,
                profile,
                native_hook_runner=native_hook_runner,
            )
