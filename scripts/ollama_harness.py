#!/usr/bin/env python3
"""Stdlib Ollama harness shim for GT-KB Phase 1."""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
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
ROUTING_CONFIG_PATH = Path(".api-harness") / "ollama" / "routing.toml"
MAX_TOOL_OUTPUT_CHARS = 6000
MAX_GREP_RESULTS = 50
MAX_GLOB_RESULTS = 100
MAX_REPEATED_TOOL_SIGNATURE_TURNS = 4
LOYAL_OPPOSITION_BRIDGE_SKILLS = frozenset({"bridge-review", "verification"})


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
    dialect=base.DIALECT_OLLAMA_NATIVE,
)


BRIDGE_WRITE_GUARDS = (
    ROUTING_CONFIG_PATH.parent / Path("hooks/credential-scan.py"),
    ROUTING_CONFIG_PATH.parent / Path("hooks/scanner-safe-writer.py"),
    Path("scripts/implementation_start_gate.py"),
)
BRIDGE_EDIT_GUARDS = (
    ROUTING_CONFIG_PATH.parent / Path("hooks/credential-scan.py"),
    ROUTING_CONFIG_PATH.parent / Path("hooks/scanner-safe-writer.py"),
    Path("scripts/implementation_start_gate.py"),
)
WRITE_EDIT_GUARDS = (
    ROUTING_CONFIG_PATH.parent / Path("hooks/credential-scan.py"),
    ROUTING_CONFIG_PATH.parent / Path("hooks/scanner-safe-writer.py"),
    Path("scripts/implementation_start_gate.py"),
)
BASH_GUARDS = (
    ROUTING_CONFIG_PATH.parent / Path("hooks/destructive-gate.py"),
    Path("scripts/implementation_start_gate.py"),
)


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
    native_context_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class GuardExecutionResult:
    returncode: int
    stdout: str
    stderr: str = ""
    timed_out: bool = False


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


def _parse_skill_routes(routing: Mapping[str, Any], models: Mapping[str, ModelRoute]) -> dict[str, str]:
    skills_raw = routing.get("skills") or {}
    if not isinstance(skills_raw, dict):
        raise OllamaHarnessError("routing.skills must be a table when present")
    skill_routes: dict[str, str] = {}
    for skill_name, route_spec in skills_raw.items():
        if not isinstance(skill_name, str) or not skill_name:
            raise OllamaHarnessError("routing.skills entries must use non-empty skill names")
        if isinstance(route_spec, str):
            route_key = route_spec
        elif isinstance(route_spec, dict):
            route_key = route_spec.get("model")
        else:
            raise OllamaHarnessError(f"routing.skills.{skill_name} must name a configured model")
        if not isinstance(route_key, str) or route_key not in models:
            raise OllamaHarnessError(f"routing.skills.{skill_name} must name a configured model")
        skill_routes[skill_name] = route_key
    return skill_routes


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
    config = RoutingConfig(
        schema_version=1,
        models=models,
        default_model=default_model,
        skill_routes=_parse_skill_routes(routing, models),
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


def resolve_model(config: RoutingConfig, requested_model: str | None, skill: str | None = None) -> ModelRoute:
    if skill is not None and not skill:
        raise OllamaHarnessError("skill route key must be a non-empty string")
    route_key = requested_model or (config.skill_routes.get(skill) if skill else None) or config.default_model
    try:
        return config.models[route_key]
    except KeyError as exc:
        raise OllamaHarnessError(f"unknown model route: {route_key}") from exc


def build_system_prompt(skill: str | None, project_root: Path) -> str | None:
    """Load current neutral bridge instructions without assigning a runtime role."""
    if skill not in LOYAL_OPPOSITION_BRIDGE_SKILLS:
        return None
    selected = "gtkb-proposal-review" if skill == "bridge-review" else "gtkb-verify"
    sources = [
        project_root / ".harness-baseline-configuration" / "skills" / name / "SKILL.md"
        for name in ("gtkb-bridge", selected)
    ]
    try:
        instructions = [path.read_text(encoding="utf-8") for path in sources]
    except (OSError, UnicodeError) as exc:
        raise OllamaHarnessError("Current canonical bridge skill instructions are unavailable") from exc
    if any(not text.strip() for text in instructions):
        raise OllamaHarnessError("Current canonical bridge skill instructions are unavailable: empty source")
    return "\n\n".join(instructions)


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
            "Run a bounded local shell command after guards allow it; bridge artifact and retired-index mutations are denied.",
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
            "GTKB_AUTHOR_MODEL_CONFIGURATION": f"Ollama endpoint={endpoint}; routing=static .api-harness/ollama/routing.toml",
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
            [sys.executable, str(guard_path)],
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
) -> None:
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
        result = runner(guard_path, payload, env, timeout)
        if result.timed_out:
            raise OllamaHarnessError(f"guard timed out: {_relative_path(project_root, guard_path)}")
        if result.returncode != 0:
            raise OllamaHarnessError(
                f"guard exited nonzero: {_relative_path(project_root, guard_path)} ({result.returncode})"
            )
        stdout = (result.stdout or "").strip()
        if not stdout:
            raise OllamaHarnessError(f"guard emitted empty output: {_relative_path(project_root, guard_path)}")
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise OllamaHarnessError(
                f"guard emitted malformed JSON: {_relative_path(project_root, guard_path)}"
            ) from exc
        if not isinstance(data, dict):
            raise OllamaHarnessError(f"guard output must be a JSON object: {_relative_path(project_root, guard_path)}")
        reason = _decision_reason(data)
        if reason:
            raise OllamaHarnessError(f"guard denied {tool_name}: {_relative_path(project_root, guard_path)}: {reason}")


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
) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=True)
    content = str(arguments.get("content", ""))
    invoke_guard_adapter(
        "Write", {"path": str(path), "content": content}, model_metadata, project_root, guard_runner=guard_runner
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    return f"wrote {_relative_path(project_root, path)}"


def _dispatch_edit(
    arguments: Mapping[str, Any],
    model_metadata: ModelMetadata,
    project_root: Path,
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
        guard_runner=guard_runner,
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


def _iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def _dispatch_grep(arguments: Mapping[str, Any], project_root: Path) -> str:
    pattern = _require_string(arguments, "pattern")
    base = _resolve_tool_path(project_root, str(arguments.get("path") or "."), allow_missing=False)
    max_results = _positive_int_argument(arguments, "max_results", MAX_GREP_RESULTS)
    regex = re.compile(pattern)
    roots = [base] if base.is_file() else list(_iter_text_files(base))
    matches: list[str] = []
    for file_path in roots:
        rel = _relative_path_or_none(project_root, file_path)
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
    return "\n".join(matches)


def _dispatch_glob(arguments: Mapping[str, Any], project_root: Path) -> str:
    pattern = _require_string(arguments, "pattern")
    base = _resolve_tool_path(project_root, str(arguments.get("path") or "."), allow_missing=False)
    max_results = _positive_int_argument(arguments, "max_results", MAX_GLOB_RESULTS)
    matches: list[str] = []
    for path in base.rglob("*"):
        rel = _relative_path_or_none(project_root, path)
        if rel is None:
            continue
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern):
            matches.append(rel)
            if len(matches) >= max_results:
                break
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
        encoding="utf-8",
        errors="replace",
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
    guard_runner: GuardRunner | None,
    command_runner: CommandRunner | None,
) -> str:
    command = _require_string(arguments, "command")
    timeout = float(arguments.get("timeout_seconds") or DEFAULT_TIMEOUT_SECONDS)
    bridge_denial = bridge_bash_mutation_reason(command)
    if bridge_denial:
        raise OllamaHarnessError(bridge_denial)
    invoke_guard_adapter("Bash", {"command": command}, model_metadata, project_root, guard_runner=guard_runner)
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
    skill: str | None = None,
) -> str:
    if tool_name not in CANONICAL_TOOLS:
        raise OllamaHarnessError(f"unsupported tool: {tool_name}")
    if tool_name == "Read":
        return _dispatch_read(arguments, project_root)
    if tool_name == "Write":
        return _dispatch_write(arguments, model_metadata, project_root, guard_runner)
    if tool_name == "Edit":
        return _dispatch_edit(arguments, model_metadata, project_root, guard_runner)
    if tool_name == "Grep":
        return _dispatch_grep(arguments, project_root)
    if tool_name == "Glob":
        return _dispatch_glob(arguments, project_root)
    if tool_name == "Bash":
        return _dispatch_bash(arguments, model_metadata, project_root, guard_runner, command_runner)
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
    skill: str | None = None,
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
) -> str:
    try:
        completion_target = bridge_completion_target(prompt, skill, bridge_document, bridge_version)
    except BridgeDeliveryIncomplete as exc:
        raise OllamaHarnessIncomplete(str(exc)) from exc
    if max_turns < 1:
        raise OllamaHarnessError("max_turns must be at least 1")
    if session_timeout <= 0:
        raise OllamaHarnessError("session_timeout must be positive")
    metadata = ModelMetadata(model_route.model_id, model_route.model_version, endpoint, model_route.key)
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
    identity = (
        f"Native context identifier: {metadata.native_context_id}. "
        "Bind only the exact init marker supplied in the task through gt session bind. "
        "Use its returned canonical session binding for authored provenance."
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
                block = invoke(base.NATIVE_HOOK_PRE_TOOL_USE, tool_name=tool_name, tool_input=arguments)
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
                            skill=skill,
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
    parser.add_argument("--model", help="Routing model key from .api-harness/ollama/routing.toml.")
    parser.add_argument("--skill", help="Skill or task route key from .api-harness/ollama/routing.toml.")
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
    ensure_utf8_output_streams()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_arg_parser()
    args = parser.parse_args(raw_argv)
    project_root = resolve_project_root(Path.cwd())
    try:
        config = load_routing_config(project_root)
        operation_timeout, session_timeout = resolve_runtime_timeouts(args, config, raw_argv)
        max_turns = resolve_runtime_max_turns(args, config, raw_argv)
        advertised_model_ids = call_ollama_tags(args.endpoint, operation_timeout)
        validate_advertised_models(config, advertised_model_ids)
        model_route = resolve_model(config, args.model, skill=args.skill)
        system_prompt = build_system_prompt(args.skill, project_root)
        text = run_tool_loop(
            args.prompt,
            model_route,
            args.endpoint,
            max_turns,
            project_root,
            skill=args.skill,
            bridge_document=args.bridge_document,
            bridge_version=args.bridge_version,
            system_prompt=system_prompt,
            timeout=operation_timeout,
            session_timeout=session_timeout,
        )
    except OllamaHarnessError as exc:
        print(f"ollama_harness: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
