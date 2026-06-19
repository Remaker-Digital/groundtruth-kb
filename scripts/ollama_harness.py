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
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id
except ModuleNotFoundError:  # pragma: no cover - exercised when imported as scripts.ollama_harness.
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id

try:
    from sdk_bridge_bash_guard import bridge_bash_mutation_reason
except ModuleNotFoundError:  # pragma: no cover - exercised when imported as scripts.ollama_harness.
    from scripts.sdk_bridge_bash_guard import bridge_bash_mutation_reason

try:
    import tomllib
except ImportError:  # pragma: no cover - Python <3.11 fallback is not expected in CI.
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]


DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_TIMEOUT_SECONDS = 240.0
DEFAULT_MAX_TURNS = 24
ROUTING_CONFIG_PATH = Path(".api-harness") / "routing.toml"
MAX_TOOL_OUTPUT_CHARS = 6000
MAX_GREP_RESULTS = 50
MAX_GLOB_RESULTS = 100
LOYAL_OPPOSITION_BRIDGE_SKILLS = frozenset({"bridge-review", "verification"})
CANONICAL_TOOLS = frozenset({"Read", "Write", "Edit", "Grep", "Glob", "Bash"})
MUTATING_TOOLS = frozenset({"Write", "Edit", "Bash"})
AUTHOR_IDENTITY = "Ollama D"
AUTHOR_HARNESS_ID = "D"


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


class OllamaHarnessError(RuntimeError):
    """Raised for fail-closed harness errors."""


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


@dataclass(frozen=True)
class ModelMetadata:
    model_id: str
    model_version: str
    endpoint: str
    route_key: str


@dataclass(frozen=True)
class GuardExecutionResult:
    returncode: int
    stdout: str
    stderr: str = ""
    timed_out: bool = False


GuardRunner = Callable[[Path, dict[str, Any], Mapping[str, str], float], GuardExecutionResult]
ChatFunc = Callable[[str, dict[str, Any], float], dict[str, Any]]
CommandRunner = Callable[[str, Path, Mapping[str, str], float], subprocess.CompletedProcess[str]]


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


def load_routing_config(project_root: Path, advertised_model_ids: Iterable[str] | None = None) -> RoutingConfig:
    config_path = project_root / ROUTING_CONFIG_PATH
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
        # WI-4473: provider-scoped loading. Only load provider=="ollama" rows so the
        # shared .api-harness/routing.toml's openrouter rows are not validated against
        # the local Ollama /api/tags inventory (mirrors the provider filter in
        # scripts/openrouter_harness.py:load_routing_config). An absent provider
        # defaults to "ollama" for backward compatibility with single-provider configs
        # that predate the multi-provider schema.
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


def build_system_prompt(skill: str | None, model_route: ModelRoute) -> str | None:
    """Return role context for Ollama skill routes that need GT-KB bridge behavior."""
    if skill not in LOYAL_OPPOSITION_BRIDGE_SKILLS:
        return None
    allowed_tools = ", ".join(model_route.allowed_tools)
    return f"""You are Ollama harness D operating as Loyal Opposition for GT-KB.

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

Run the preflight checks with Bash:
python scripts\\bridge_applicability_preflight.py --bridge-id <document-slug>
python scripts\\adr_dcl_clause_preflight.py --bridge-id <document-slug>

Do not use Bash to create, edit, overwrite, remove, or index bridge/*.md files
or the retired bridge index. The harness hard-denies shell bridge mutations;
use guarded Write/Edit dispatch or the deterministic bridge writer/helper path
for bridge artifacts. Treat any helper that requires the retired bridge index
as defective and report that defect instead of following stale instructions.

Bridge verdict author metadata to include:
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: ollama-harness-d
author_model: {model_route.model_id}
author_model_version: {model_route.model_version}
author_model_configuration: Ollama harness shim; route {model_route.key}; skill {skill}; guarded tools {allowed_tools}

Stay within E:\\GT-KB. Preserve guard decisions exactly; if a guarded tool is denied, report the
denial and do not invent a successful bridge action."""


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
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            data = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise OllamaHarnessError(f"Ollama chat request failed: {exc}") from exc
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        raise OllamaHarnessError(f"Ollama chat response was not JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise OllamaHarnessError("Ollama chat response must be a JSON object")
    return parsed


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


def set_author_metadata_env(
    env: Mapping[str, str],
    model_id: str,
    model_version: str,
    endpoint: str = DEFAULT_ENDPOINT,
) -> dict[str, str]:
    updated = dict(env)
    updated.update(
        {
            "GTKB_AUTHOR_IDENTITY": AUTHOR_IDENTITY,
            "GTKB_AUTHOR_HARNESS_ID": AUTHOR_HARNESS_ID,
            "GTKB_AUTHOR_MODEL": model_id,
            "GTKB_AUTHOR_MODEL_VERSION": model_version,
            "GTKB_AUTHOR_MODEL_CONFIGURATION": f"Ollama endpoint={endpoint}; routing=static .ollama/routing.toml",
        }
    )
    return updated


def resolve_ollama_session_id(environ: Mapping[str, str] | None = None) -> str:
    """Resolve the bridge work-intent session id used by guarded Ollama tools."""
    return resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ=environ)


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
        os.environ, model_metadata.model_id, model_metadata.model_version, model_metadata.endpoint
    )
    payload = {
        "tool_name": tool_name,
        "tool_input": tool_input,
        "cwd": str(project_root),
        "project_root": str(project_root),
        "session_id": resolve_ollama_session_id(os.environ) or "ollama-harness-d",
    }
    for relative_guard_path in paths:
        guard_path = relative_guard_path if relative_guard_path.is_absolute() else project_root / relative_guard_path
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
    guard_runner: GuardRunner | None,
) -> str:
    path = _resolve_tool_path(project_root, _require_string(arguments, "path", "file_path"), allow_missing=True)
    content = str(arguments.get("content", ""))
    invoke_guard_adapter(
        "Write", {"path": str(path), "content": content}, model_metadata, project_root, guard_runner=guard_runner
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
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
        path.write_text(content.replace(old_string, new_string, 1), encoding="utf-8")
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
        try:
            for line_no, line in enumerate(
                file_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
            ):
                if regex.search(line):
                    matches.append(f"{_relative_path(project_root, file_path)}:{line_no}:{line[:300]}")
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
        rel = _relative_path(project_root, path)
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
        os.environ, model_metadata.model_id, model_metadata.model_version, model_metadata.endpoint
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


def run_tool_loop(
    prompt: str,
    model_route: ModelRoute,
    endpoint: str,
    max_turns: int,
    project_root: Path,
    *,
    system_prompt: str | None = None,
    chat_func: ChatFunc | None = None,
    guard_runner: GuardRunner | None = None,
    command_runner: CommandRunner | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    if max_turns < 1:
        raise OllamaHarnessError("max_turns must be at least 1")
    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    schemas = build_tool_schemas(model_route.allowed_tools)
    chat = chat_func or call_ollama_chat
    metadata = ModelMetadata(model_route.model_id, model_route.model_version, endpoint, model_route.key)
    for _turn in range(max_turns):
        payload = {"model": model_route.model_id, "messages": messages, "tools": schemas, "stream": False}
        response = chat(endpoint, payload, timeout)
        message = _message_from_response(response)
        tool_calls = message.get("tool_calls") or response.get("tool_calls") or []
        if not tool_calls:
            content = message.get("content")
            if not isinstance(content, str):
                raise OllamaHarnessError("assistant final message must contain text content")
            return content
        if not isinstance(tool_calls, list):
            raise OllamaHarnessError("tool_calls must be a list")
        messages.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": tool_calls})
        for index, call in enumerate(tool_calls):
            tool_name, arguments, call_id = _tool_call_parts(call, index)
            try:
                result = dispatch_tool_call(
                    tool_name,
                    arguments,
                    metadata,
                    project_root,
                    guard_runner=guard_runner,
                    command_runner=command_runner,
                )
            except OllamaHarnessError as tool_err:
                # Guard denial or other tool error: return error as tool result
                # instead of crashing the loop. Model sees the denial and can
                # try a different path.
                result = f"ERROR: {tool_err}"
            messages.append(
                {
                    "role": "tool",
                    "name": tool_name,
                    "tool_call_id": call_id,
                    "content": result[:MAX_TOOL_OUTPUT_CHARS],
                }
            )
    raise OllamaHarnessError("max-turn exhaustion before final assistant text")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the GT-KB Ollama harness shim.")
    parser.add_argument("-p", "--prompt", required=True, help="User prompt to send to Ollama.")
    parser.add_argument("--model", help="Routing model key from .ollama/routing.toml.")
    parser.add_argument("--skill", help="Skill or task route key from .ollama/routing.toml.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Ollama endpoint; default is localhost.")
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS, help="Maximum tool loop turns.")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, help="HTTP/guard/subprocess timeout.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    ensure_utf8_output_streams()
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    project_root = resolve_project_root(Path.cwd())
    try:
        config = load_routing_config(project_root)
        advertised_model_ids = call_ollama_tags(args.endpoint, args.timeout)
        validate_advertised_models(config, advertised_model_ids)
        model_route = resolve_model(config, args.model, skill=args.skill)
        system_prompt = build_system_prompt(args.skill, model_route)
        text = run_tool_loop(
            args.prompt,
            model_route,
            args.endpoint,
            args.max_turns,
            project_root,
            system_prompt=system_prompt,
            timeout=args.timeout,
        )
    except OllamaHarnessError as exc:
        print(f"ollama_harness: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
