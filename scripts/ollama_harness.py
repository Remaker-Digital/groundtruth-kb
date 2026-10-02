#!/usr/bin/env python3
"""Stdlib Ollama harness shim for GT-KB Phase 1."""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    import cloud_harness_base as base
    from sdk_bridge_bash_guard import (
        BridgeDeliveryIncomplete,
        bridge_bash_mutation_reason,
        bridge_completion_target,
        verify_bridge_completion,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised when imported as scripts.ollama_harness.
    from scripts import cloud_harness_base as base
    from scripts.sdk_bridge_bash_guard import (
        BridgeDeliveryIncomplete,
        bridge_bash_mutation_reason,
        bridge_completion_target,
        verify_bridge_completion,
    )

try:
    import tomllib
except ImportError:  # pragma: no cover - Python <3.11 fallback is not expected in CI.
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]


DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_TIMEOUT_SECONDS = 240.0
DEFAULT_SESSION_TIMEOUT_SECONDS = 540.0
ROUTING_SESSION_TIMEOUT_GRACE_SECONDS = 60.0

# WI-4817: bounded retry for transient cloud transport failures so a dispatched
# LO worker survives a transient hiccup and still produces a verdict. Total
# backoff (1+2+4 = 7s) stays far under the 600s worker-lifetime cap (WI-4806).
CHAT_MAX_ATTEMPTS = 3
CHAT_RETRY_BACKOFF_SECONDS = (1.0, 2.0, 4.0)
RETRYABLE_HTTP_STATUS = frozenset({429, 500, 502, 503, 504})
# WI-4734: full bridge verification can exceed the old 24-turn ceiling.
DEFAULT_MAX_TURNS = 80
ROUTING_CONFIG_PATH = Path(".harness-baseline-configuration/routing.toml")
NATIVE_HOOK_SETTINGS_PATH = Path(".api-harness/ollama/settings.json")
MAX_TOOL_OUTPUT_CHARS = 6000
MAX_GREP_RESULTS = 50
MAX_GLOB_RESULTS = 100
MAX_REPEATED_TOOL_SIGNATURE_TURNS = 4


CANONICAL_TOOLS = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash"})
MUTATING_TOOLS = frozenset({"Write", "Edit", "Bash"})
AUTHOR_IDENTITY = "Ollama D"
AUTHOR_HARNESS_ID = "D"

_OLLAMA_HOOK_PROFILE = base.NativeHookProfile(
    display_name="Ollama",
    author_identity=AUTHOR_IDENTITY,
    author_harness_id=AUTHOR_HARNESS_ID,
    default_endpoint=DEFAULT_ENDPOINT,
    routing_config_path=ROUTING_CONFIG_PATH,
    native_hook_settings_path=NATIVE_HOOK_SETTINGS_PATH,
    dialect=base.DIALECT_OLLAMA_NATIVE,
)


BRIDGE_WRITE_GUARDS = base.BRIDGE_WRITE_GUARDS
BRIDGE_EDIT_GUARDS = base.BRIDGE_EDIT_GUARDS
WRITE_EDIT_GUARDS = base.WRITE_EDIT_GUARDS
BASH_GUARDS = base.BASH_GUARDS


class OllamaHarnessError(RuntimeError):
    """Raised for fail-closed harness errors."""


class OllamaHarnessIncomplete(OllamaHarnessError):
    code = "bridge_delivery_incomplete"


@dataclass(frozen=True)
class ModelRoute:
    key: str
    model_id: str
    model_version: str
    tool_calling_supported: bool
    allowed_tools: tuple[str, ...]


@dataclass(frozen=True)
class RoutingConfig:
    schema_version: int
    models: dict[str, ModelRoute]
    default_model: str
    timeout_seconds: float | None = None
    session_timeout_seconds: float | None = None
    max_turns: int | None = None


@dataclass(frozen=True)
class ModelMetadata:
    model_id: str
    model_version: str
    endpoint: str
    route_key: str
    native_context_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class GuardExecutionResult:
    returncode: int
    stdout: str
    stderr: str = ""
    timed_out: bool = False
    duration_ms: int = 0  # c123 (batch design WP2, item 9)


GuardRunner = Callable[[Path, dict[str, Any], Mapping[str, str], float], GuardExecutionResult]
ChatFunc = Callable[[str, dict[str, Any], float], dict[str, Any]]
CommandRunner = Callable[[str, Path, Mapping[str, str], float], subprocess.CompletedProcess[str]]


def _remaining_timeout(deadline: float, message: str) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise OllamaHarnessError(message)
    return remaining


def _sleep_with_budget(delay: float, deadline: float, message: str) -> None:
    if _remaining_timeout(deadline, message) < delay:
        raise OllamaHarnessError(message)
    time.sleep(delay)


def resolve_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    return current


def ensure_utf8_output_streams(stdout: Any | None = None, stderr: Any | None = None) -> None:
    """Make harness output safe for Unicode verdict text on Windows consoles."""
    for stream in (stdout or sys.stdout, stderr or sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        with contextlib.suppress(ValueError, OSError):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _as_list(value: Any, *, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise OllamaHarnessError(f"{field} must be a list of strings")
    return value


def _as_non_empty_string(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise OllamaHarnessError(f"{field} must be a non-empty string")
    return value


def _as_optional_positive_float(value: Any, *, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise OllamaHarnessError(f"{field} must be a positive number")
    if isinstance(value, (int, float)):
        parsed = float(value)
    elif isinstance(value, str):
        try:
            parsed = float(value)
        except ValueError as exc:
            raise OllamaHarnessError(f"{field} must be a positive number") from exc
    else:
        raise OllamaHarnessError(f"{field} must be a positive number")
    if parsed <= 0:
        raise OllamaHarnessError(f"{field} must be a positive number")
    return parsed


def _as_optional_positive_int(value: Any, *, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise OllamaHarnessError(f"{field} must be a positive integer")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
    else:
        raise OllamaHarnessError(f"{field} must be a positive integer")
    if parsed <= 0:
        raise OllamaHarnessError(f"{field} must be a positive integer")
    return parsed


def infer_model_version(model_id: str) -> str:
    """Return the Ollama tag portion from a model id such as ``name:tag``."""
    if ":" not in model_id:
        return "unversioned"
    return model_id.rsplit(":", 1)[1] or "unversioned"


def validate_advertised_models(config: RoutingConfig, advertised_model_ids: Iterable[str]) -> None:
    advertised: set[str] = set()
    for model_id in advertised_model_ids:
        if not isinstance(model_id, str) or not model_id:
            raise OllamaHarnessError("advertised model inventory must contain non-empty strings")
        advertised.add(model_id)
    configured = {route.model_id for route in config.models.values()}
    missing = sorted(configured - advertised)
    if missing:
        raise OllamaHarnessError(f"configured model_id values are not advertised locally: {missing}")


def call_ollama_tags(endpoint: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> tuple[str, ...]:
    url = endpoint.rstrip("/") + "/api/tags"
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            data = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise OllamaHarnessError(f"Ollama model inventory request failed: {exc}") from exc
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        raise OllamaHarnessError(f"Ollama model inventory response was not JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise OllamaHarnessError("Ollama model inventory response must be a JSON object")
    models = parsed.get("models")
    if not isinstance(models, list):
        raise OllamaHarnessError("Ollama model inventory response missing models list")
    model_ids: list[str] = []
    for index, row in enumerate(models):
        if not isinstance(row, dict):
            raise OllamaHarnessError("Ollama model inventory entries must be JSON objects")
        model_id = row.get("name") or row.get("model")
        if not isinstance(model_id, str) or not model_id:
            raise OllamaHarnessError(f"Ollama model inventory entry {index} is missing name/model")
        model_ids.append(model_id)
    return tuple(model_ids)


def resolve_configuration_path(project_root: Path, relative: Path) -> Path:
    if relative.anchor or ".." in relative.parts:
        raise OllamaHarnessError("configuration path must be relative to the selected project")
    candidate = project_root.resolve() / relative
    if candidate.resolve() != candidate:
        raise OllamaHarnessError(f"configuration path is redirected: {relative.as_posix()}")
    return candidate


def load_routing_config(project_root: Path, advertised_model_ids: Iterable[str] | None = None) -> RoutingConfig:
    config_path = resolve_configuration_path(project_root, ROUTING_CONFIG_PATH)
    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OllamaHarnessError(f"routing config is missing: {config_path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise OllamaHarnessError(f"routing config is invalid TOML: {exc}") from exc

    if raw.get("schema_version") != 1:
        raise OllamaHarnessError("routing config schema_version must be 1")
    models_raw = raw.get("models")
    if not isinstance(models_raw, dict) or not models_raw:
        raise OllamaHarnessError("routing config must define [models.<key>] rows")

    models: dict[str, ModelRoute] = {}
    for key, row in models_raw.items():
        if not isinstance(key, str) or not key or not isinstance(row, dict):
            raise OllamaHarnessError("model rows must be named TOML tables")
        # Only this provider's model rows can become selectable routes.
        provider = row.get("provider", "ollama")
        if provider != "ollama":
            continue
        model_id = _as_non_empty_string(row.get("model_id"), field=f"models.{key}.model_id")
        model_version = infer_model_version(model_id)
        allowed_tools = tuple(_as_list(row.get("allowed_tools"), field=f"models.{key}.allowed_tools"))
        if row.get("tool_calling_supported") is not True:
            raise OllamaHarnessError(f"models.{key}.tool_calling_supported must be true")
        unknown_tools = sorted(set(allowed_tools) - CANONICAL_TOOLS)
        if unknown_tools:
            raise OllamaHarnessError(f"models.{key}.allowed_tools contains noncanonical tools: {unknown_tools}")
        models[key] = ModelRoute(key, model_id, model_version, True, allowed_tools)

    routing = raw.get("routing", {}).get("ollama")
    if not isinstance(routing, dict):
        raise OllamaHarnessError("routing config must define [routing.ollama]")
    default_model = routing.get("default_model")
    if not isinstance(default_model, str) or default_model not in models:
        raise OllamaHarnessError("routing.default_model must name a configured model")
    if "skills" in routing:
        # c123 (batch design WP2 2.1): a role skill no longer selects D's model; its registration names --model.
        raise OllamaHarnessError(f"routing.ollama.skills: {base.RETIRED_SKILL_TABLES}")
    config = RoutingConfig(
        schema_version=1,
        models=models,
        default_model=default_model,
        timeout_seconds=_as_optional_positive_float(
            routing.get("timeout_seconds"),
            field="routing.ollama.timeout_seconds",
        ),
        session_timeout_seconds=_as_optional_positive_float(
            routing.get("session_timeout_seconds"),
            field="routing.ollama.session_timeout_seconds",
        ),
        max_turns=_as_optional_positive_int(
            routing.get("max_turns"),
            field="routing.ollama.max_turns",
        ),
    )
    if advertised_model_ids is not None:
        validate_advertised_models(config, advertised_model_ids)
    return config


def resolve_model(config: RoutingConfig, requested_model: str | None) -> ModelRoute:
    route_key = requested_model or config.default_model
    try:
        return config.models[route_key]
    except KeyError as exc:
        raise OllamaHarnessError(f"unknown model route: {route_key}") from exc


def build_system_prompt(project_root: Path) -> str:
    """Load the shared root instructions; a role is never loaded from a launch argument (c123, WP2 2.1)."""
    root_source = project_root / "AGENTS.md"
    if not root_source.resolve().is_relative_to(project_root.resolve()):
        raise OllamaHarnessError("Shared root instructions resolve outside the project root")
    try:
        root_instructions = root_source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise OllamaHarnessError("Shared root instructions are unavailable: AGENTS.md") from exc
    if not root_instructions.strip():
        raise OllamaHarnessError("Shared root instructions are unavailable: empty AGENTS.md")
    return root_instructions


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
            "Read a UTF-8 text file under the GT-KB project root with character-offset pagination.",
            {
                "path": {"type": "string"},
                "offset": {"type": "integer", "minimum": 0},
                "max_chars": {"type": "integer", "minimum": 1},
            },
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
            base.bash_tool_description(),  # c123 (batch design WP2, item 8): names the shell that runs it
            {"command": {"type": "string"}, "timeout_seconds": {"type": "number", "minimum": 1}},
            ["command"],
        ),
    }
    allowed = tuple(allowed_tools)
    unknown = sorted(set(allowed) - CANONICAL_TOOLS)
    if unknown:
        raise OllamaHarnessError(f"unknown allowed tools: {unknown}")
    return [schemas[name] for name in allowed]


def call_ollama_chat(
    endpoint: str, payload: dict[str, Any], timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> dict[str, Any]:
    url = endpoint.rstrip("/") + "/api/chat"
    deadline = time.monotonic() + timeout
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(1, CHAT_MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(
                request,
                timeout=_remaining_timeout(deadline, "Ollama chat request timed out"),
            ) as response:  # noqa: S310
                data = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in RETRYABLE_HTTP_STATUS and attempt < CHAT_MAX_ATTEMPTS:
                _sleep_with_budget(
                    CHAT_RETRY_BACKOFF_SECONDS[attempt - 1],
                    deadline,
                    "Ollama chat request timed out before retry",
                )
                continue
            raise OllamaHarnessError(
                f"Ollama chat request failed (HTTP {exc.code}) after {attempt} attempt(s): {exc}"
            ) from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < CHAT_MAX_ATTEMPTS:
                _sleep_with_budget(
                    CHAT_RETRY_BACKOFF_SECONDS[attempt - 1],
                    deadline,
                    "Ollama chat request timed out before retry",
                )
                continue
            raise OllamaHarnessError(f"Ollama chat request failed after {attempt} attempt(s): {exc}") from exc
        except TimeoutError as exc:
            last_error = exc
            if attempt < CHAT_MAX_ATTEMPTS:
                _sleep_with_budget(
                    CHAT_RETRY_BACKOFF_SECONDS[attempt - 1],
                    deadline,
                    "Ollama chat request timed out before retry",
                )
                continue
            raise OllamaHarnessError(f"Ollama chat request timed out after {attempt} attempt(s): {exc}") from exc
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as exc:
            raise OllamaHarnessError(f"Ollama chat response was not JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise OllamaHarnessError("Ollama chat response must be a JSON object")
        return parsed
    raise OllamaHarnessError(f"Ollama chat request failed after {CHAT_MAX_ATTEMPTS} attempt(s): {last_error}")


def _resolve_tool_path(project_root: Path, path_text: str, *, allow_missing: bool) -> Path:
    if not isinstance(path_text, str) or not path_text.strip():
        raise OllamaHarnessError("tool path must be a non-empty string")
    raw = Path(path_text)
    candidate = raw if raw.is_absolute() else project_root / raw
    try:
        resolved = candidate.resolve(strict=not allow_missing)
    except FileNotFoundError as exc:
        if not allow_missing:
            raise OllamaHarnessError(f"file not found: {path_text}") from exc
        resolved = candidate.resolve(strict=False)
    except OSError as exc:
        raise OllamaHarnessError(f"tool path could not be resolved: {path_text}") from exc
    _ensure_under_root(project_root, resolved, path_text)
    return resolved


def _ensure_under_root(project_root: Path, resolved: Path, original: str) -> None:
    root = project_root.resolve()
    if resolved != root and root not in resolved.parents:
        raise OllamaHarnessError(f"tool path escapes project root: {original}")


def _relative_path(project_root: Path, path: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()


def _relative_path_or_none(project_root: Path, path: Path) -> str | None:
    try:
        return _relative_path(project_root, path)
    except (OSError, ValueError):
        return None


def set_author_metadata_env(
    env: Mapping[str, str],
    model_id: str,
    model_version: str,
    endpoint: str = DEFAULT_ENDPOINT,
    *,
    native_context_id: str,
) -> dict[str, str]:
    updated = dict(env)
    # A native runtime identity is not the canonical binding returned by the CLI.
    updated.pop("GTKB_AUTHOR_SESSION_CONTEXT_ID", None)
    updated.update(
        {
            "GTKB_AUTHOR_IDENTITY": AUTHOR_IDENTITY,
            "GTKB_AUTHOR_HARNESS_ID": AUTHOR_HARNESS_ID,
            "GTKB_NATIVE_CONTEXT_ID": native_context_id,
            "GTKB_AUTHOR_MODEL": model_id,
            "GTKB_AUTHOR_MODEL_VERSION": model_version,
            "GTKB_AUTHOR_MODEL_CONFIGURATION": f"Ollama endpoint={endpoint}; routing=static .harness-baseline-configuration/routing.toml",
        }
    )
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
            [sys.executable, "-B", str(guard_path)],
            input=json.dumps(payload),
            text=True,
            encoding="utf-8",
            errors="replace",
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
    raise OllamaHarnessError(f"guard adapter does not support tool: {tool_name}")


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
    raise OllamaHarnessError(f"unsupported guarded tool: {tool_name}")


def invoke_guard_adapter(
    tool_name: str,
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    *,
    guard_runner: GuardRunner | None = None,
    guard_paths: Sequence[Path] | None = None,
    timeout: float = 10.0,
    decision_log: base.DecisionLogFunc | None = None,
) -> None:
    """D's fail-closed guard adapter; c123 (batch design WP2, item 9): each guard's decision goes to decision_log."""
    if tool_name not in MUTATING_TOOLS:
        return
    tool_input = _guard_tool_input(tool_name, arguments, project_root)
    paths = tuple(guard_paths) if guard_paths is not None else _guard_paths_for(tool_name, tool_input, project_root)
    runner = guard_runner or _default_guard_runner
    env = set_author_metadata_env(
        os.environ,
        model_metadata.model_id,
        model_metadata.model_version,
        model_metadata.endpoint,
        native_context_id=model_metadata.native_context_id,
    )
    payload = {
        "tool_name": tool_name,
        "tool_input": tool_input,
        "cwd": str(project_root),
        "project_root": str(project_root),
        "session_id": model_metadata.native_context_id,
    }
    env["GTKB_PROJECT_ROOT"] = str(project_root)
    for relative_guard_path in paths:
        guard_path = (
            relative_guard_path
            if relative_guard_path.is_absolute()
            else resolve_configuration_path(project_root, relative_guard_path)
        )
        if not guard_path.is_file():
            raise OllamaHarnessError(f"guard script is missing: {relative_guard_path.as_posix()}")
        started = time.monotonic()
        result = runner(guard_path, payload, env, timeout)
        if isinstance(result, GuardExecutionResult) and not result.duration_ms:
            result = dataclasses.replace(result, duration_ms=int((time.monotonic() - started) * 1000))
        label = base._bounded_native_hook_diagnostic_token(guard_path.name, fallback="guard")
        refusal: str | None = None
        reason: str | None = None
        data: Any = None
        if result.timed_out:
            refusal = f"guard timed out: {_relative_path(project_root, guard_path)}"
        elif result.returncode != 0:
            refusal = f"guard exited nonzero: {_relative_path(project_root, guard_path)} ({result.returncode})"
        elif not (result.stdout or "").strip():
            refusal = f"guard emitted empty output: {_relative_path(project_root, guard_path)}"
        else:
            try:
                data = json.loads((result.stdout or "").strip())
            except json.JSONDecodeError:
                refusal = f"guard emitted malformed JSON: {_relative_path(project_root, guard_path)}"
            if refusal is None and not isinstance(data, dict):
                refusal = f"guard output must be a JSON object: {_relative_path(project_root, guard_path)}"
            if refusal is None:
                reason = _decision_reason(data)
                if reason:
                    refusal = f"guard denied {tool_name}: {_relative_path(project_root, guard_path)}: {reason}"
        base._log_decision(
            decision_log,
            "guard_adapter",
            tool_name,
            label,
            result,
            allowed=refusal is None,
            reason=reason or refusal,
            reason_code=base._reason_code(data) if isinstance(data, dict) else None,
        )
        if refusal is not None:
            raise OllamaHarnessError(refusal)


def _require_string(arguments: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = arguments.get(name)
        if isinstance(value, str) and value:
            return value
    raise OllamaHarnessError(f"missing required argument: {'/'.join(names)}")


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
        raise OllamaHarnessError(f"{name} must be a positive integer")
    return parsed


def _nonnegative_int_argument(arguments: Mapping[str, Any], name: str, default: int) -> int:
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

    if parsed is None or parsed < 0:
        raise OllamaHarnessError(f"{name} must be a nonnegative integer")
    return parsed


def _bounded_read_result(content: str, offset: int, max_chars: int) -> str:
    end = min(len(content), offset + max_chars, offset + MAX_TOOL_OUTPUT_CHARS)
    if end >= len(content):
        return content[offset:end]

    while True:
        marker = (
            f"\n\n[Read truncated: returned characters [{offset}, {end}) of {len(content)}. "
            f"Continue with offset={end}.]"
        )
        bounded_end = min(end, offset + max(0, MAX_TOOL_OUTPUT_CHARS - len(marker)))
        if bounded_end == end:
            return content[offset:end] + marker
        end = bounded_end


def _string_list_argument(arguments: Mapping[str, Any], name: str) -> tuple[str, ...]:
    value = arguments.get(name, [])
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise OllamaHarnessError(f"{name} must be an array of non-empty strings")
    return tuple(item.strip() for item in value)


def _dispatch_read(arguments: Mapping[str, Any], project_root: Path) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=True)
    offset = _nonnegative_int_argument(arguments, "offset", 0)
    max_chars = _positive_int_argument(arguments, "max_chars", MAX_TOOL_OUTPUT_CHARS)
    try:
        return _bounded_read_result(path.read_text(encoding="utf-8"), offset, max_chars)
    except FileNotFoundError:
        return f"Read failed: file not found: {_relative_path(project_root, path)}"
    except OSError as exc:
        return f"Read failed: {_relative_path(project_root, path)}: {exc}"


def _dispatch_write(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    guard_runner: GuardRunner | None,
    *,
    decision_log: base.DecisionLogFunc | None = None,
) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=True)
    content = str(arguments.get("content", ""))
    invoke_guard_adapter(
        "Write",
        {"path": str(path), "content": content},
        model_metadata,
        project_root,
        guard_runner=guard_runner,
        decision_log=decision_log,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    return f"wrote {_relative_path(project_root, path)}"


def _dispatch_edit(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    guard_runner: GuardRunner | None,
    *,
    decision_log: base.DecisionLogFunc | None = None,
) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=False)
    old_string = _require_string(arguments, "old_string")
    new_string = str(arguments.get("new_string", ""))
    invoke_guard_adapter(
        "Edit",
        {"path": str(path), "old_string": old_string, "new_string": new_string},
        model_metadata,
        project_root,
        guard_runner=guard_runner,
        decision_log=decision_log,
    )
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise OllamaHarnessError(f"file not found: {_relative_path(project_root, path)}") from exc
    except OSError as exc:
        raise OllamaHarnessError(f"failed to read file {_relative_path(project_root, path)}: {exc}") from exc

    if old_string not in content:
        raise OllamaHarnessError(f"old_string not found in {_relative_path(project_root, path)}")

    try:
        path.write_text(content.replace(old_string, new_string, 1), encoding="utf-8", newline="")
    except OSError as exc:
        raise OllamaHarnessError(f"failed to write file {_relative_path(project_root, path)}: {exc}") from exc
    return f"edited {_relative_path(project_root, path)}"


def _dispatch_grep(arguments: Mapping[str, Any], project_root: Path) -> str:
    """D's Grep, through the shared bounded walker (c123; batch design WP2, item 11).

    D walked the whole tree with rglob, with no skip and no entry limit, the other contexts' scratch and checkouts
    among it; the shared walker skips .git, .venv, caches and the shared context parents, and stops at its limit.
    D's own _relative_path still decides whether a match lies under the root, so a match that resolves outside it
    is skipped as before.
    """
    try:
        return base._dispatch_grep(arguments, project_root, relative_path=_relative_path)
    except base.CloudHarnessError as exc:
        raise OllamaHarnessError(str(exc)) from exc


def _dispatch_glob(arguments: Mapping[str, Any], project_root: Path) -> str:
    """D's Glob, through the shared bounded walker (c123; batch design WP2, item 11), with D's own _relative_path."""
    try:
        return base._dispatch_glob(arguments, project_root, relative_path=_relative_path)
    except base.CloudHarnessError as exc:
        raise OllamaHarnessError(str(exc)) from exc


def _default_command_runner(
    command: str,
    project_root: Path,
    env: Mapping[str, str],
    timeout: float,
) -> subprocess.CompletedProcess[str]:
    """D's Bash runner is the shared one (c123; batch design WP2, item 8): a named shell, UTF-8 with replacement, the
    process tree ended on a timeout or an interrupt."""
    return base._default_command_runner(command, project_root, env, timeout)


def _dispatch_bash(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
    guard_runner: GuardRunner | None,
    command_runner: CommandRunner | None,
    *,
    decision_log: base.DecisionLogFunc | None = None,
) -> str:
    command = _require_string(arguments, "command")
    timeout = float(arguments.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS)
    bridge_denial = bridge_bash_mutation_reason(command)
    if bridge_denial:
        base._log_decision(
            decision_log, "bridge_shell", "Bash", "bridge_shell", None, allowed=False, reason=bridge_denial
        )
        raise OllamaHarnessError(bridge_denial)
    invoke_guard_adapter(
        "Bash", {"command": command}, model_metadata, project_root, guard_runner=guard_runner, decision_log=decision_log
    )
    env = set_author_metadata_env(
        os.environ,
        model_metadata.model_id,
        model_metadata.model_version,
        model_metadata.endpoint,
        native_context_id=model_metadata.native_context_id,
    )
    runner = command_runner or _default_command_runner
    try:
        completed = runner(command, project_root, env, timeout)
    except subprocess.TimeoutExpired as exc:
        raise OllamaHarnessError(f"Bash command timed out: {command}") from exc
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
    *,
    guard_runner: GuardRunner | None = None,
    command_runner: CommandRunner | None = None,
    decision_log: base.DecisionLogFunc | None = None,
) -> str:
    if tool_name not in CANONICAL_TOOLS:
        raise OllamaHarnessError(f"unsupported tool: {tool_name}")
    if tool_name == "Read":
        return _dispatch_read(arguments, project_root)
    if tool_name == "Write":
        return _dispatch_write(arguments, model_metadata, project_root, guard_runner, decision_log=decision_log)
    if tool_name == "Edit":
        return _dispatch_edit(arguments, model_metadata, project_root, guard_runner, decision_log=decision_log)
    if tool_name == "Grep":
        return _dispatch_grep(arguments, project_root)
    if tool_name == "Glob":
        return _dispatch_glob(arguments, project_root)
    if tool_name == "Bash":
        return _dispatch_bash(
            arguments, model_metadata, project_root, guard_runner, command_runner, decision_log=decision_log
        )
    raise OllamaHarnessError(f"unsupported tool: {tool_name}")


def _tool_call_parts(call: Any, index: int) -> tuple[str, dict[str, Any], str]:
    if not isinstance(call, dict):
        raise OllamaHarnessError("tool_call entries must be JSON objects")
    function = call.get("function")
    if isinstance(function, dict):
        name = function.get("name") or call.get("name")
        raw_arguments = function.get("arguments", call.get("arguments", {}))
    else:
        name = call.get("name")
        raw_arguments = call.get("arguments", {})
    if not isinstance(name, str) or not name:
        raise OllamaHarnessError("tool_call is missing function name")
    if isinstance(raw_arguments, str):
        try:
            parsed = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError as exc:
            raise OllamaHarnessError("tool_call arguments string must be JSON") from exc
        raw_arguments = parsed
    if not isinstance(raw_arguments, dict):
        raise OllamaHarnessError("tool_call arguments must be an object")
    return name, raw_arguments, str(call.get("id") or f"tool_call_{index}")


def _message_from_response(response: Mapping[str, Any]) -> dict[str, Any]:
    message = response.get("message")
    if not isinstance(message, dict):
        raise OllamaHarnessError("Ollama response missing message object")
    return dict(message)


def _final_text_from_message(message: Mapping[str, Any]) -> str:
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise OllamaHarnessError("assistant final message must contain nonblank text content")
    return content


def run_tool_loop(
    prompt: str,
    model_route: ModelRoute,
    endpoint: str,
    max_turns: int,
    project_root: Path,
    *,
    bridge_document: str | None = None,
    bridge_version: int | None = None,
    system_prompt: str | None = None,
    chat_func: ChatFunc | None = None,
    guard_runner: GuardRunner | None = None,
    command_runner: CommandRunner | None = None,
    native_hook_runner: base.NativeHookRunner | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    session_timeout: float = DEFAULT_SESSION_TIMEOUT_SECONDS,
    telemetry: Any | None = None,
    guard_log: base.GuardDecisionLog | None = None,
    native_context_id: str | None = None,
    binding: Mapping[str, Any] | None = None,
) -> str:
    try:
        completion_target = bridge_completion_target(bridge_document, bridge_version)
    except BridgeDeliveryIncomplete as exc:
        raise OllamaHarnessIncomplete(str(exc)) from exc
    if max_turns < 1:
        raise OllamaHarnessError("max_turns must be at least 1")
    if session_timeout <= 0:
        raise OllamaHarnessError("session_timeout must be positive")
    metadata = ModelMetadata(
        model_route.model_id,
        model_route.model_version,
        endpoint,
        model_route.key,
        # c123 (batch design WP2, item 10): the launcher names the id it printed before the first provider call.
        **({"native_context_id": native_context_id} if native_context_id else {}),
    )
    # c123 (batch design WP2, item 9): each guard decision goes to the guard log.
    decision_log = guard_log.record if guard_log is not None else None
    hook_metadata = base.ModelMetadata(
        metadata.model_id,
        metadata.model_version,
        endpoint,
        metadata.route_key,
        native_context_id=metadata.native_context_id,
    )

    def invoke(event, **kwargs):
        try:
            return base.invoke_native_hooks(
                event,
                hook_metadata,
                project_root,
                _OLLAMA_HOOK_PROFILE,
                native_hook_runner=native_hook_runner,
                **kwargs,
            )
        except base.CloudHarnessError as exc:
            raise OllamaHarnessError(str(exc)) from exc

    invoke(base.NATIVE_HOOK_SESSION_START)
    invoke(base.NATIVE_HOOK_USER_PROMPT_SUBMIT, prompt=prompt)
    if binding is not None:
        # c123 (batch design WP2 2.1): the launcher bound the context with its --init line; state the bound facts.
        identity = base.bound_identity(metadata.native_context_id, binding, completion_target)
    else:
        identity = (
            f"Native context identifier: {metadata.native_context_id}. "
            "Bind only the exact init marker supplied in the task through gt session bind. "
            "The response has an initialization status and an immutable binding object. "
            "Use the binding object for authored provenance; initialization status grants no bridge action."
        )
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": "\n\n".join(part for part in (identity, system_prompt) if part)}
    ]
    messages.append({"role": "user", "content": prompt})
    allowed_tools = tuple(model_route.allowed_tools)
    chat = chat_func or call_ollama_chat
    session_deadline = time.monotonic() + session_timeout
    previous_tool_signature: str | None = None
    repeated_tool_signature_turns = 0
    native_stop_blocks = 0
    native_stop_completed = False

    stop_reason = "process_error"
    try:
        for _turn in range(max_turns):
            schemas = build_tool_schemas(allowed_tools)
            payload = {"model": model_route.model_id, "messages": messages, "tools": schemas, "stream": False}
            operation_timeout = min(
                timeout,
                _remaining_timeout(session_deadline, "session timeout exceeded before Ollama chat turn"),
            )
            response = chat(endpoint, payload, operation_timeout)
            message = _message_from_response(response)
            tool_calls = message.get("tool_calls") or response.get("tool_calls") or []
            tool_names = []
            if isinstance(tool_calls, list):
                for call in tool_calls:
                    function = call.get("function") if isinstance(call, dict) else None
                    tool_name = (
                        function.get("name")
                        if isinstance(function, dict)
                        else (call.get("name") if isinstance(call, dict) else None)
                    )
                    if isinstance(tool_name, str) and tool_name in CANONICAL_TOOLS:
                        tool_names.append(tool_name)
            if telemetry is not None:
                with contextlib.suppress(Exception):
                    telemetry.record_turn(_turn + 1, tool_names, provider_response=response)
            if not tool_calls:
                block_reason = base._invoke_native_stop_hooks_nonmasking(
                    hook_metadata,
                    project_root,
                    _OLLAMA_HOOK_PROFILE,
                    native_hook_runner,
                )
                if block_reason:
                    native_stop_blocks += 1
                    if native_stop_blocks >= base.MAX_NATIVE_STOP_BLOCKS:
                        native_stop_completed = True
                        raise OllamaHarnessError(
                            f"native Stop hook blocked completion {base.MAX_NATIVE_STOP_BLOCKS} consecutive times"
                        )
                    messages.append({"role": "assistant", "content": _final_text_from_message(message)})
                    messages.append(
                        {"role": "user", "content": base.NATIVE_STOP_CONTINUATION_PROMPT.format(reason=block_reason)}
                    )
                    continue
                native_stop_completed = True
                try:
                    verify_bridge_completion(
                        completion_target,
                        metadata.native_context_id,
                        project_root,
                        session_deadline - time.monotonic(),
                        command_runner,
                    )
                except BridgeDeliveryIncomplete as exc:
                    stop_reason = "bridge_delivery_incomplete"
                    raise OllamaHarnessIncomplete(str(exc)) from exc
                stop_reason = "final_response"
                return _final_text_from_message(message)
            if not isinstance(tool_calls, list):
                raise OllamaHarnessError("tool_calls must be a list")

            tool_signature = json.dumps(tool_calls, sort_keys=True, default=str)
            if tool_signature == previous_tool_signature:
                repeated_tool_signature_turns += 1
            else:
                previous_tool_signature = tool_signature
                repeated_tool_signature_turns = 1
            if repeated_tool_signature_turns > MAX_REPEATED_TOOL_SIGNATURE_TURNS:
                raise OllamaHarnessError("repeated no-progress tool loop before final assistant text")

            messages.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": tool_calls})
            for index, call in enumerate(tool_calls):
                try:
                    tool_name, arguments, call_id = _tool_call_parts(call, index)
                except OllamaHarnessError as parse_err:
                    call_id = str(call.get("id")) if isinstance(call, dict) else f"tool_call_{index}"
                    function = call.get("function") if isinstance(call, dict) else None
                    parsed_name = function.get("name") if isinstance(function, dict) else None
                    if not (isinstance(parsed_name, str) and parsed_name) and isinstance(call, dict):
                        parsed_name = call.get("name")
                    tool_name = parsed_name if isinstance(parsed_name, str) and parsed_name else "<malformed_tool_call>"
                    messages.append(
                        {
                            "role": "tool",
                            "name": tool_name,
                            "tool_call_id": call_id,
                            "content": f"ERROR: {parse_err}",
                        }
                    )
                    continue
                if tool_name == "Bash":
                    arguments = dict(arguments)
                    requested_timeout = float(arguments.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS)
                    arguments["timeout_seconds"] = min(
                        requested_timeout,
                        _remaining_timeout(session_deadline, "session timeout exceeded before Bash tool call"),
                    )
                block = invoke(
                    base.NATIVE_HOOK_PRE_TOOL_USE, tool_name=tool_name, tool_input=arguments, decision_log=decision_log
                )
                block_reason = base._native_hook_block_reason(block)
                if block_reason:
                    result = f"ERROR: native hook blocked {tool_name}: {block_reason}"
                else:
                    try:
                        result = dispatch_tool_call(
                            tool_name,
                            arguments,
                            metadata,
                            project_root,
                            guard_runner=guard_runner,
                            command_runner=command_runner,
                            decision_log=decision_log,
                        )
                    except OllamaHarnessError as tool_err:
                        result = f"ERROR: {tool_err}"
                invoke(base.NATIVE_HOOK_POST_TOOL_USE, tool_name=tool_name, tool_input=arguments, tool_response=result)
                messages.append(
                    {
                        "role": "tool",
                        "name": tool_name,
                        "tool_call_id": call_id,
                        "content": result[:MAX_TOOL_OUTPUT_CHARS],
                    }
                )
        stop_reason = "max_turn_exhaustion"
        raise OllamaHarnessError("max-turn exhaustion before final assistant text")
    except KeyboardInterrupt:
        # c123 (batch design WP2, item 10): Ctrl+C or CTRL_BREAK (raised as the same interrupt) is classified.
        stop_reason = "interrupted"
        raise
    except OllamaHarnessError as exc:
        message = str(exc).lower()
        if isinstance(exc, OllamaHarnessIncomplete):
            stop_reason = exc.code
        elif "max-turn" in message:
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
        if not native_stop_completed:
            with contextlib.suppress(Exception):
                invoke(base.NATIVE_HOOK_STOP)
        if telemetry is not None:
            with contextlib.suppress(Exception):
                telemetry.finish(stop_reason=stop_reason)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB Ollama harness shim.")
    parser.add_argument("-p", "--prompt", required=True, help="User prompt to send to Ollama.")
    parser.add_argument("--model", help="Routing model key from .harness-baseline-configuration/routing.toml.")
    parser.add_argument(
        "--init", help="The exact init line; the launcher binds the context with it before the first model call."
    )
    parser.add_argument("--bridge-document", help="Assigned canonical bridge document.")
    parser.add_argument("--bridge-version", type=int, help="Exact successor version this task must deliver.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Ollama endpoint; default is localhost.")
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS, help="Maximum tool loop turns.")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, help="HTTP/guard/subprocess timeout.")
    parser.add_argument(
        "--session-timeout",
        type=float,
        default=DEFAULT_SESSION_TIMEOUT_SECONDS,
        help="Maximum wall-clock seconds for the whole harness tool loop.",
    )
    parser.add_argument("--report", help="Write the run report (JSON) to this path.")
    parser.add_argument("--guard-log", help="Append the guard decisions (JSONL) to this path; else GTKB_GUARD_LOG.")
    return parser


def _flag_was_supplied(argv: Sequence[str], flag: str) -> bool:
    prefix = f"{flag}="
    return any(item == flag or item.startswith(prefix) for item in argv)


def derive_session_timeout_from_route_timeout(timeout_seconds: float) -> float:
    return timeout_seconds + ROUTING_SESSION_TIMEOUT_GRACE_SECONDS


def resolve_runtime_timeouts(
    args: argparse.Namespace,
    config: RoutingConfig,
    argv: Sequence[str],
) -> tuple[float, float]:
    timeout_explicit = _flag_was_supplied(argv, "--timeout")
    session_timeout_explicit = _flag_was_supplied(argv, "--session-timeout")

    operation_timeout = (
        float(args.timeout) if config.timeout_seconds is None or timeout_explicit else config.timeout_seconds
    )
    if session_timeout_explicit:
        session_timeout = float(args.session_timeout)
    elif config.session_timeout_seconds is not None:
        session_timeout = config.session_timeout_seconds
    elif config.timeout_seconds is not None and not timeout_explicit:
        session_timeout = derive_session_timeout_from_route_timeout(config.timeout_seconds)
    else:
        session_timeout = float(args.session_timeout)
    return operation_timeout, session_timeout


def resolve_runtime_max_turns(
    args: argparse.Namespace,
    config: RoutingConfig,
    argv: Sequence[str],
) -> int:
    if config.max_turns is None or _flag_was_supplied(argv, "--max-turns"):
        return int(args.max_turns)
    return config.max_turns


def main(argv: Sequence[str] | None = None) -> int:
    """Run one D launch (c123, batch design WP2 items 9 and 10: guard log, report, exit codes).

    Exit codes: 0 final answer; 3 bridge delivery incomplete; 4 the --init bind failed (c123, WP2 2.1, no model call
    made); 5 interrupted; 1 every other failure.
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
        harness="ollama",
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
        print("ollama_harness: interrupted", file=sys.stderr)
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
        config = load_routing_config(project_root)
        operation_timeout, session_timeout = resolve_runtime_timeouts(args, config, raw_argv)
        max_turns = resolve_runtime_max_turns(args, config, raw_argv)
        advertised_model_ids = call_ollama_tags(args.endpoint, operation_timeout)
        validate_advertised_models(config, advertised_model_ids)
        model_route = resolve_model(config, args.model)
        report.data["route_key"] = model_route.key
        report.data["requested_model"] = model_route.model_id
        system_prompt = build_system_prompt(project_root)
        print(f"ollama_harness: native_context_id={native_context_id}", file=sys.stderr)
        try:
            base.check_launch_inputs(project_root, _OLLAMA_HOOK_PROFILE, args.bridge_document, args.bridge_version)
        except base.CloudHarnessIncomplete as exc:
            raise OllamaHarnessIncomplete(str(exc)) from exc
        except base.CloudHarnessError as exc:
            raise OllamaHarnessError(str(exc)) from exc
        try:
            binding = base.bind_for_run(args.init, native_context_id, project_root, report)
        except base.NativeBindFailed as exc:
            print(f"ollama_harness: {exc}", file=sys.stderr)
            return base.EXIT_BIND_FAILED, str(exc)
        text = run_tool_loop(
            args.prompt,
            model_route,
            args.endpoint,
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
    except OllamaHarnessError as exc:
        print(f"ollama_harness: {exc}", file=sys.stderr)
        incomplete = isinstance(exc, OllamaHarnessIncomplete)
        return (base.EXIT_DELIVERY_INCOMPLETE if incomplete else 1), str(exc)
    print(text)
    return 0, None


if __name__ == "__main__":
    raise SystemExit(main())
