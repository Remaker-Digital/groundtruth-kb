"""Deterministic authority resolution and worker-path decontamination.

The service preserves historical records while ensuring that only current or
explicitly generated artifacts can enter an active worker-loading path. It
derives repository facts from existing GT-KB registries rather than creating a
second authority registry.
"""

from __future__ import annotations

import ast
import json
import re
import tomllib
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

CURRENT_STATES = frozenset({"active", "current"})
HISTORICAL_STATES = frozenset({"archive", "deprecated", "historical", "retired", "superseded"})
PROJECTION_STATES = frozenset({"generated"})
VALID_STATES = CURRENT_STATES | HISTORICAL_STATES | PROJECTION_STATES
NON_LOADING_STARTUP_VISIBILITY = frozenset({"none", "warning_if_referenced"})

_SETTINGS_ENTRYPOINTS = (
    ".claude/settings.json",
    ".codex/hooks.json",
    ".cursor/hooks.json",
)
_COMMAND_ENTRYPOINTS = ("groundtruth-kb/pyproject.toml",)
_DIRECT_STARTUP_ENTRYPOINTS = ("scripts/session_self_initialization.py",)
_READ_METHODS = frozenset({"read_bytes", "read_text"})
_ROOT_NAMES = frozenset({"project_dir", "project_root", "repo_root", "root", "workspace_root"})

_STARTUP_ROW = re.compile(
    r"^\|\s*(?P<label>[^|]+?)\s*\|\s*`(?P<path>[^`]+)`\s*\|\s*"
    r"(?P<lifecycle>active|archive|deprecated|generated|historical|retired|superseded)\s*\|",
    re.IGNORECASE,
)
_WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")


class ArtifactLifecycleError(ValueError):
    """Raised when lifecycle input cannot be normalized safely."""


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    """One current, projected, or historical artifact declaration."""

    logical_id: str
    path: str
    lifecycle: str
    source: str
    version: int = 1
    superseded_by: str | None = None
    scope: str = "exact"

    def normalized(self) -> ArtifactRecord:
        lifecycle = self.lifecycle.strip().lower()
        if lifecycle not in VALID_STATES:
            raise ArtifactLifecycleError(f"{self.logical_id}: unsupported lifecycle {self.lifecycle!r}")
        if not self.logical_id.strip():
            raise ArtifactLifecycleError("logical_id must not be empty")
        if not self.source.strip():
            raise ArtifactLifecycleError(f"{self.logical_id}: source must not be empty")
        if not isinstance(self.version, int) or self.version < 1:
            raise ArtifactLifecycleError(f"{self.logical_id}: version must be a positive integer")
        scope = self.scope.strip().lower()
        if scope not in {"exact", "tree"}:
            raise ArtifactLifecycleError(f"{self.logical_id}: scope must be exact or tree")
        return ArtifactRecord(
            logical_id=self.logical_id.strip(),
            path=normalize_repository_path(self.path),
            lifecycle=lifecycle,
            source=self.source.strip(),
            version=self.version,
            superseded_by=self.superseded_by.strip() if self.superseded_by else None,
            scope=scope,
        )


@dataclass(frozen=True, slots=True)
class WorkerReference:
    """An exact artifact path loaded by a startup, activity, or worker surface."""

    path: str
    source: str
    purpose: str = "worker_load"
    logical_id: str | None = None

    def normalized(self) -> WorkerReference:
        if not self.source.strip():
            raise ArtifactLifecycleError("worker reference source must not be empty")
        return WorkerReference(
            path=normalize_repository_path(self.path),
            source=self.source.strip(),
            purpose=self.purpose.strip() or "worker_load",
            logical_id=self.logical_id.strip() if self.logical_id else None,
        )


@dataclass(frozen=True, slots=True)
class EffectiveEntrypoint:
    """One executable root selected by a production registration surface."""

    path: str
    source: str
    kind: str


@dataclass(frozen=True, slots=True)
class EffectiveLoadEdge:
    """One statically exact repository artifact read by an executable root."""

    entrypoint: str
    path: str
    source: str
    line: int
    loader: str


def normalize_repository_path(raw_path: str) -> str:
    """Return one canonical root-relative path, rejecting aliases and escapes."""

    value = raw_path.strip().strip("`").replace("\\", "/")
    if not value:
        raise ArtifactLifecycleError("artifact path must not be empty")
    if _WINDOWS_ABSOLUTE.match(value) or value.startswith("/"):
        raise ArtifactLifecycleError(f"artifact path must be root-relative: {raw_path}")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise ArtifactLifecycleError(f"artifact path contains an unsafe alias: {raw_path}")
    path = PurePosixPath(value)
    return path.as_posix()


def _path_key(path: str) -> str:
    """Use Windows-compatible case-insensitive identity for repository paths."""

    return normalize_repository_path(path).casefold()


def _record_sort_key(record: ArtifactRecord) -> tuple[str, int, str, str, str, str]:
    return (
        record.logical_id.casefold(),
        record.version,
        _path_key(record.path),
        record.lifecycle,
        record.scope,
        record.source.casefold(),
    )


class ArtifactAuthorityIndex:
    """Immutable deterministic index over artifact lifecycle declarations."""

    def __init__(self, records: Iterable[ArtifactRecord]):
        normalized = set(record.normalized() for record in records)
        self.records = tuple(sorted(normalized, key=_record_sort_key))
        self._by_logical_id: dict[str, list[ArtifactRecord]] = {}
        self._by_path: dict[str, list[ArtifactRecord]] = {}
        for record in self.records:
            self._by_logical_id.setdefault(record.logical_id.casefold(), []).append(record)
            self._by_path.setdefault(_path_key(record.path), []).append(record)

    def resolve(self, logical_id: str) -> dict[str, Any]:
        """Resolve a logical artifact to exactly one current authority."""

        candidates = self._by_logical_id.get(logical_id.strip().casefold(), [])
        current = [record for record in candidates if record.lifecycle in CURRENT_STATES]
        history = [record for record in candidates if record.lifecycle in HISTORICAL_STATES]
        projections = [record for record in candidates if record.lifecycle in PROJECTION_STATES]
        if len(current) == 1:
            status = "resolved"
        elif len(current) > 1:
            status = "ambiguous_current"
        else:
            status = "no_current"
        return {
            "logical_id": logical_id,
            "status": status,
            "current": asdict(current[0]) if len(current) == 1 else None,
            "current_candidates": [asdict(record) for record in current],
            "history": [asdict(record) for record in history],
            "projections": [asdict(record) for record in projections],
        }

    def path_status(self, path: str) -> dict[str, Any]:
        """Resolve one path using exact facts and historical tree boundaries."""

        normalized = normalize_repository_path(path)
        path_key = normalized.casefold()
        exact = self._by_path.get(path_key, [])
        ancestors = [
            record
            for record in self.records
            if record.scope == "tree" and path_key.startswith(_path_key(record.path) + "/")
        ]
        historical_ancestors = [record for record in ancestors if record.lifecycle in HISTORICAL_STATES]
        candidates = list(exact)
        if historical_ancestors:
            candidates.extend(historical_ancestors)
        elif not exact and ancestors:
            longest = max(len(_path_key(record.path)) for record in ancestors)
            candidates.extend(record for record in ancestors if len(_path_key(record.path)) == longest)
        candidates = sorted(set(candidates), key=_record_sort_key)
        classes = {_lifecycle_class(record.lifecycle) for record in candidates}
        if not candidates:
            status = "unknown"
        elif "current" in classes and "historical" in classes:
            status = "conflict"
        elif "current" in classes:
            status = "current"
        elif "historical" in classes:
            status = "historical"
        elif classes == {"projection"}:
            status = "generated"
        else:
            status = "conflict"
        return {
            "path": normalized,
            "status": status,
            "records": [asdict(record) for record in candidates],
        }

    def audit(self, worker_references: Iterable[WorkerReference]) -> dict[str, Any]:
        """Fail closed when authority is ambiguous or a worker path is contaminated."""

        references = tuple(
            sorted(
                {reference.normalized() for reference in worker_references},
                key=lambda item: (
                    _path_key(item.path),
                    (item.logical_id or "").casefold(),
                    item.source.casefold(),
                    item.purpose.casefold(),
                ),
            )
        )
        findings: list[dict[str, str]] = []
        for logical_id in sorted(self._by_logical_id):
            resolution = self.resolve(logical_id)
            if resolution["status"] == "ambiguous_current":
                findings.append(
                    {
                        "id": f"ambiguous:{logical_id}",
                        "severity": "P0",
                        "reason": "logical artifact has multiple current authorities",
                    }
                )

        resolved_references: list[dict[str, Any]] = []
        for reference in references:
            reference_status = self._reference_status(reference)
            resolved_references.append({**asdict(reference), "resolution": reference_status})
            if reference_status in {"historical", "conflict"}:
                findings.append(
                    {
                        "id": reference.path,
                        "severity": "P0",
                        "reason": (
                            "historical authority is present on an active worker-loading path"
                            if reference_status == "historical"
                            else "worker-loading path has conflicting lifecycle declarations"
                        ),
                    }
                )
            elif reference_status == "unknown":
                findings.append(
                    {
                        "id": reference.path,
                        "severity": "P1",
                        "reason": "worker-loading path has no lifecycle declaration",
                    }
                )

        findings.sort(key=lambda item: (item["severity"], item["id"], item["reason"]))
        return {
            "schema_version": 1,
            "status": "PASS" if not findings else "FAIL",
            "record_count": len(self.records),
            "worker_reference_count": len(references),
            "records": [asdict(record) for record in self.records],
            "worker_references": resolved_references,
            "findings": findings,
        }

    def _reference_status(self, reference: WorkerReference) -> str:
        """Resolve a worker route against its declared logical authority when available."""

        if not reference.logical_id:
            return str(self.path_status(reference.path)["status"])
        resolution = self.resolve(reference.logical_id)
        if resolution["status"] == "ambiguous_current":
            return "conflict"
        if resolution["status"] == "resolved":
            current = resolution["current"]
            return "current" if current and _path_key(current["path"]) == _path_key(reference.path) else "conflict"
        history = resolution["history"]
        projections = resolution["projections"]
        if history:
            return "historical"
        if projections:
            return "generated"
        return "unknown"


def parse_startup_inventory(text: str, *, source: str) -> tuple[list[ArtifactRecord], list[WorkerReference]]:
    """Parse only structured startup inventory rows; narrative mentions are inert."""

    records: list[ArtifactRecord] = []
    references: list[WorkerReference] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = _STARTUP_ROW.match(line)
        if not match:
            continue
        declaration = _repository_path_declaration(match.group("path"))
        if declaration is None:
            continue
        path, scope = declaration
        lifecycle = match.group("lifecycle").lower()
        logical_id = "startup:" + _slug(match.group("label"))
        record_source = f"{source}:{line_number}"
        records.append(
            ArtifactRecord(
                logical_id,
                path,
                lifecycle,
                record_source,
                scope=scope,
            )
        )
        if lifecycle in CURRENT_STATES | PROJECTION_STATES:
            references.append(WorkerReference(path, record_source, "startup_inventory", logical_id))
    return records, references


def load_repository_snapshot(project_root: Path) -> tuple[ArtifactAuthorityIndex, tuple[WorkerReference, ...]]:
    """Build an index from existing GT-KB authority and worker-context registries."""

    root = project_root.resolve()
    records: list[ArtifactRecord] = []
    references: list[WorkerReference] = []

    sot_path = root / "config" / "registry" / "sot-artifacts.toml"
    sot = _load_toml(sot_path)
    for row in sot.get("artifacts", []):
        raw_path = row.get("storage_path")
        declaration = _repository_path_declaration(raw_path) if isinstance(raw_path, str) else None
        if declaration is not None:
            path, scope = declaration
            records.append(
                ArtifactRecord(
                    logical_id=f"sot:{row.get('id', '')}",
                    path=path,
                    lifecycle=str(row.get("lifecycle", "")),
                    source=_relative_source(sot_path, root),
                    scope=scope,
                )
            )

    control_path = root / "config" / "agent-control" / "SESSION-STARTUP-CONTROL-MAP.md"
    control_records, control_references = parse_startup_inventory(
        control_path.read_text(encoding="utf-8"),
        source=_relative_source(control_path, root),
    )
    records.extend(control_records)
    references.extend(control_references)

    system_path = root / "config" / "agent-control" / "system-interface-map.toml"
    system_map = _load_toml(system_path)
    for row in system_map.get("systems", []):
        lifecycle = str(row.get("lifecycle_state", "")).lower()
        raw_path = row.get("authoritative_source")
        if not isinstance(raw_path, str) or not _is_exact_repository_path(raw_path):
            continue
        # Lifecycle declarations and loading declarations are separate facts.
        # Keep historical rows in the index, then model every actually visible
        # startup route as a worker reference so stale authority cannot vanish
        # merely because its registry row says "retired".
        records.append(
            ArtifactRecord(
                logical_id=f"interface:{row.get('id', '')}",
                path=raw_path,
                lifecycle=lifecycle,
                source=_relative_source(system_path, root),
                scope="tree" if raw_path.endswith(("/", "\\")) else "exact",
            )
        )
        startup_visibility = str(row.get("startup_visibility", "none")).strip().lower()
        if startup_visibility not in NON_LOADING_STARTUP_VISIBILITY:
            references.append(
                WorkerReference(
                    raw_path,
                    _relative_source(system_path, root),
                    "interface_startup",
                    f"interface:{row.get('id', '')}",
                )
            )

    context_path = root / "config" / "registry" / "context-manifests.toml"
    context = _load_toml(context_path)
    for row in context.get("items", []):
        raw_path = row.get("source_path")
        if not isinstance(raw_path, str) or not _is_exact_repository_path(raw_path):
            continue
        records.append(
            ArtifactRecord(
                logical_id=f"context:{row.get('source_id', row.get('id', ''))}",
                path=raw_path,
                lifecycle=str(row.get("lifecycle", "")),
                source=_relative_source(context_path, root),
            )
        )
        references.append(
            WorkerReference(
                raw_path,
                _relative_source(context_path, root),
                "context_manifest",
                f"context:{row.get('source_id', row.get('id', ''))}",
            )
        )

    sharding_path = root / "config" / "agent-control" / "activity-envelope-sharding.toml"
    sharding = _load_toml(sharding_path)
    classes = sharding.get("classes", {})
    declared_surfaces = list(classes.get("global_baseline", {}).get("allowed_surfaces", []))
    declared_surfaces.extend(classes.get("activity_only", {}).get("deferred_surfaces", []))
    for raw_path in declared_surfaces:
        if not isinstance(raw_path, str) or not _is_exact_repository_path(raw_path):
            continue
        records.append(
            ArtifactRecord(
                logical_id=f"sharding:{raw_path}",
                path=raw_path,
                lifecycle="current",
                source=_relative_source(sharding_path, root),
            )
        )
        references.append(
            WorkerReference(
                raw_path,
                _relative_source(sharding_path, root),
                "context_sharding",
                f"sharding:{raw_path}",
            )
        )

    return ArtifactAuthorityIndex(records), tuple(references)


def discover_effective_loading_graph(project_root: Path) -> dict[str, Any]:
    """Discover exact artifact reads reachable from registered production entrypoints.

    This deliberately avoids a repository-wide text scan. Roots come from
    structured startup, hook-settings, and console-command registrations, and
    edges come only from Python AST read operations whose paths can be resolved
    exactly relative to the repository root.
    """

    root = project_root.resolve()
    entrypoints = _discover_effective_entrypoints(root)
    edges: set[EffectiveLoadEdge] = set()
    for entrypoint in entrypoints:
        source_path = root / Path(entrypoint.path)
        try:
            text = source_path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=entrypoint.path)
        except (OSError, SyntaxError, UnicodeError) as exc:
            raise ArtifactLifecycleError(f"cannot inspect effective entrypoint {entrypoint.path}: {exc}") from exc
        scanner = _EffectiveLoadScanner(entrypoint.path, root)
        edges.update(scanner.scan(tree))

    ordered_edges = tuple(
        sorted(
            edges,
            key=lambda item: (
                item.entrypoint.casefold(),
                _path_key(item.path),
                item.line,
                item.loader,
                item.source.casefold(),
            ),
        )
    )
    return {
        "schema_version": 1,
        "entrypoints": [asdict(item) for item in entrypoints],
        "load_edges": [asdict(item) for item in ordered_edges],
    }


def _discover_effective_entrypoints(project_root: Path) -> tuple[EffectiveEntrypoint, ...]:
    discovered: set[EffectiveEntrypoint] = set()

    startup_map = project_root / "config" / "agent-control" / "SESSION-STARTUP-CONTROL-MAP.md"
    if startup_map.is_file():
        records, _ = parse_startup_inventory(
            startup_map.read_text(encoding="utf-8"),
            source=_relative_source(startup_map, project_root),
        )
        for record in records:
            if record.lifecycle in CURRENT_STATES and _is_python_entrypoint(project_root, record.path):
                discovered.add(EffectiveEntrypoint(record.path, record.source, "startup_inventory"))

    for relative_path in _DIRECT_STARTUP_ENTRYPOINTS:
        if _is_python_entrypoint(project_root, relative_path):
            discovered.add(EffectiveEntrypoint(relative_path, relative_path, "startup_service"))

    for relative_path in _SETTINGS_ENTRYPOINTS:
        settings_path = project_root / Path(relative_path)
        if not settings_path.is_file():
            continue
        try:
            payload = json.loads(settings_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError, UnicodeError) as exc:
            raise ArtifactLifecycleError(f"cannot inspect hook settings {relative_path}: {exc}") from exc
        for command in _hook_commands(payload):
            for entrypoint_path in _command_repository_paths(command, project_root):
                if _is_python_entrypoint(project_root, entrypoint_path):
                    discovered.add(EffectiveEntrypoint(entrypoint_path, relative_path, "hook_settings"))

    for relative_path in _COMMAND_ENTRYPOINTS:
        pyproject_path = project_root / Path(relative_path)
        if not pyproject_path.is_file():
            continue
        pyproject = _load_toml(pyproject_path)
        scripts = pyproject.get("project", {}).get("scripts", {})
        if not isinstance(scripts, dict):
            raise ArtifactLifecycleError(f"{relative_path}: project.scripts must be a table")
        for command_name, target in sorted(scripts.items(), key=lambda item: str(item[0]).casefold()):
            if not isinstance(target, str) or ":" not in target:
                raise ArtifactLifecycleError(f"{relative_path}: invalid console entrypoint {command_name!r}")
            module = target.partition(":")[0].strip()
            module_path = "groundtruth-kb/src/" + module.replace(".", "/") + ".py"
            package_path = "groundtruth-kb/src/" + module.replace(".", "/") + "/__init__.py"
            candidates = (module_path, package_path)
            resolved = next((candidate for candidate in candidates if (project_root / candidate).is_file()), None)
            if resolved is None:
                raise ArtifactLifecycleError(
                    f"{relative_path}: console entrypoint {command_name!r} does not resolve inside groundtruth-kb/src"
                )
            discovered.add(EffectiveEntrypoint(resolved, relative_path, "console_command"))

    return tuple(sorted(discovered, key=lambda item: (item.path.casefold(), item.kind, item.source.casefold())))


def _hook_commands(payload: Any) -> tuple[str, ...]:
    if not isinstance(payload, dict):
        raise ArtifactLifecycleError("hook settings root must be an object")
    hooks = payload.get("hooks", {})
    if not isinstance(hooks, dict):
        raise ArtifactLifecycleError("hook settings hooks must be an object")
    commands: set[str] = set()
    for registrations in hooks.values():
        if not isinstance(registrations, list):
            raise ArtifactLifecycleError("hook settings event registrations must be arrays")
        for registration in registrations:
            if not isinstance(registration, dict):
                raise ArtifactLifecycleError("hook settings registration must be an object")
            configured_hooks = registration.get("hooks", [])
            if not isinstance(configured_hooks, list):
                raise ArtifactLifecycleError("hook settings registration hooks must be an array")
            for configured_hook in configured_hooks:
                if not isinstance(configured_hook, dict):
                    raise ArtifactLifecycleError("configured hook must be an object")
                command = configured_hook.get("command")
                if isinstance(command, str) and command.strip():
                    commands.add(command.strip())
    return tuple(sorted(commands, key=str.casefold))


def _command_repository_paths(command: str, project_root: Path) -> tuple[str, ...]:
    normalized_command = command.replace("\\", "/")
    root_text = project_root.as_posix().rstrip("/")
    normalized_command = re.sub(
        r"\$(?:CLAUDE_PROJECT_DIR|CODEX_PROJECT_DIR|PROJECT_ROOT)",
        root_text,
        normalized_command,
    )
    token_pattern = re.compile(r'"([^"]+)"|\'([^\']+)\'|(\S+)')
    paths: set[str] = set()
    for match in token_pattern.finditer(normalized_command):
        token = next(group for group in match.groups() if group is not None).strip()
        token = token.rstrip(",;)")
        candidate = Path(token)
        if not candidate.is_absolute() or not candidate.is_relative_to(project_root):
            continue
        relative = candidate.relative_to(project_root).as_posix()
        if _is_exact_repository_path(relative):
            paths.add(relative)
    return tuple(sorted(paths, key=str.casefold))


def _is_python_entrypoint(project_root: Path, relative_path: str) -> bool:
    if not _is_exact_repository_path(relative_path):
        return False
    path = project_root / Path(relative_path)
    if not path.is_file():
        return False
    return path.suffix.casefold() == ".py" or path.suffix == ""


class _EffectiveLoadScanner:
    """AST scanner for exact read edges within one registered entrypoint."""

    def __init__(self, entrypoint: str, project_root: Path):
        self.entrypoint = entrypoint
        self.project_root = project_root
        self.helpers: set[str] = set()

    def scan(self, tree: ast.Module) -> tuple[EffectiveLoadEdge, ...]:
        self.helpers = self._loader_helpers(tree)
        module_environment = self._environment(tree.body, {})
        module_statements = [
            node for node in tree.body if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        edges = set(self._edges(module_statements, module_environment))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_environment = dict(module_environment)
                for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                    if self._is_root_name(argument.arg):
                        function_environment[argument.arg] = ()
                function_environment.update(self._environment(node.body, function_environment))
                edges.update(self._edges(node.body, function_environment))
        return tuple(edges)

    def _loader_helpers(self, tree: ast.Module) -> set[str]:
        helpers: set[str] = set()
        changed = True
        while changed:
            changed = False
            for node in tree.body:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name in helpers:
                    continue
                parameter_names = {
                    item.arg for item in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                }
                for call in (item for item in ast.walk(node) if isinstance(item, ast.Call)):
                    if self._call_reads_parameter(call, parameter_names, helpers):
                        helpers.add(node.name)
                        changed = True
                        break
        return helpers

    @staticmethod
    def _call_reads_parameter(call: ast.Call, parameter_names: set[str], helpers: set[str]) -> bool:
        if isinstance(call.func, ast.Attribute) and call.func.attr in _READ_METHODS | {"open"}:
            return isinstance(call.func.value, ast.Name) and call.func.value.id in parameter_names
        if isinstance(call.func, ast.Name) and call.func.id == "open" and call.args:
            return isinstance(call.args[0], ast.Name) and call.args[0].id in parameter_names
        if isinstance(call.func, ast.Name) and call.func.id in helpers and call.args:
            return isinstance(call.args[0], ast.Name) and call.args[0].id in parameter_names
        return False

    def _environment(
        self,
        statements: list[ast.stmt],
        seed: dict[str, tuple[str, ...]],
    ) -> dict[str, tuple[str, ...]]:
        environment = dict(seed)
        for statement in statements:
            if isinstance(statement, ast.Assign):
                targets = statement.targets
                value = statement.value
            elif isinstance(statement, ast.AnnAssign):
                targets = [statement.target]
                value = statement.value
            else:
                continue
            if value is None:
                continue
            resolved = self._resolve_path(value, environment)
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                if self._is_root_name(target.id):
                    resolved = ()
                if resolved is not None:
                    environment[target.id] = resolved
        return environment

    def _edges(
        self,
        statements: list[ast.stmt],
        environment: dict[str, tuple[str, ...]],
    ) -> tuple[EffectiveLoadEdge, ...]:
        edges: set[EffectiveLoadEdge] = set()
        for statement in statements:
            for call in (item for item in ast.walk(statement) if isinstance(item, ast.Call)):
                resolved: tuple[str, ...] | None = None
                loader = ""
                if isinstance(call.func, ast.Attribute) and call.func.attr in _READ_METHODS:
                    resolved = self._resolve_path(call.func.value, environment)
                    loader = call.func.attr
                elif isinstance(call.func, ast.Attribute) and call.func.attr == "open":
                    if self._open_is_read(call):
                        resolved = self._resolve_path(call.func.value, environment)
                        loader = "open"
                elif isinstance(call.func, ast.Name) and call.func.id == "open" and call.args:
                    if self._open_is_read(call):
                        resolved = self._resolve_path(call.args[0], environment)
                        loader = "open"
                elif isinstance(call.func, ast.Name) and call.func.id in self.helpers and call.args:
                    resolved = self._resolve_path(call.args[0], environment)
                    loader = call.func.id
                if not resolved:
                    continue
                try:
                    path = normalize_repository_path("/".join(resolved))
                except ArtifactLifecycleError:
                    continue
                edges.add(
                    EffectiveLoadEdge(
                        self.entrypoint,
                        path,
                        f"{self.entrypoint}:{call.lineno}",
                        call.lineno,
                        loader,
                    )
                )
        return tuple(edges)

    @staticmethod
    def _open_is_read(call: ast.Call) -> bool:
        mode_node: ast.AST | None = call.args[1] if len(call.args) > 1 else None
        for keyword in call.keywords:
            if keyword.arg == "mode":
                mode_node = keyword.value
        if mode_node is None:
            return True
        return (
            isinstance(mode_node, ast.Constant)
            and isinstance(mode_node.value, str)
            and not any(marker in mode_node.value for marker in ("a", "w", "x", "+"))
        )

    def _resolve_path(
        self,
        node: ast.AST,
        environment: dict[str, tuple[str, ...]],
    ) -> tuple[str, ...] | None:
        if isinstance(node, ast.Name):
            if node.id in environment:
                return environment[node.id]
            return () if self._is_root_name(node.id) else None
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return self._constant_path(node.value)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left = self._resolve_path(node.left, environment)
            right = self._resolve_path(node.right, environment)
            if left is None or right is None:
                return None
            return left + right
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "Path" and node.args:
                return self._resolve_path(node.args[0], environment)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"absolute", "resolve"}:
                return self._resolve_path(node.func.value, environment)
            if isinstance(node.func, ast.Attribute) and node.func.attr == "joinpath":
                base = self._resolve_path(node.func.value, environment)
                parts = [self._resolve_path(argument, environment) for argument in node.args]
                if base is None or any(part is None for part in parts):
                    return None
                return base + tuple(segment for part in parts if part for segment in part)
        return None

    def _constant_path(self, value: str) -> tuple[str, ...] | None:
        normalized = value.strip().replace("\\", "/")
        if not normalized:
            return None
        candidate = Path(normalized)
        if candidate.is_absolute():
            try:
                normalized = candidate.relative_to(self.project_root).as_posix()
            except ValueError:
                return None
        if not _is_exact_repository_path(normalized):
            return None
        return tuple(PurePosixPath(normalized).parts)

    @staticmethod
    def _is_root_name(name: str) -> bool:
        normalized = name.strip("_").casefold()
        return normalized in _ROOT_NAMES or normalized.endswith("_project_root")


def audit_repository(project_root: Path) -> dict[str, Any]:
    """Audit the live repository and emit the frozen twelve-assertion contract."""

    root = project_root.resolve()
    index, declared_references = load_repository_snapshot(root)
    effective_graph = discover_effective_loading_graph(root)
    effective_references = tuple(
        WorkerReference(
            edge["path"],
            edge["source"],
            "effective_loader",
        )
        for edge in effective_graph["load_edges"]
    )
    references = declared_references + effective_references
    audit = index.audit(references)
    path_states = {index.path_status(record.path)["status"] for record in index.records}
    resolutions = {record.logical_id: index.resolve(record.logical_id) for record in index.records}
    historical_paths = sorted(
        {
            record.path
            for record in index.records
            if record.lifecycle in HISTORICAL_STATES and index.path_status(record.path)["status"] == "historical"
        },
        key=str.casefold,
    )
    generated_ids = sorted(
        {record.logical_id for record in index.records if record.lifecycle in PROJECTION_STATES}, key=str.casefold
    )
    worker_states = {item["resolution"] for item in audit["worker_references"]}
    contaminated_history = sorted(
        item["path"] for item in audit["worker_references"] if item["resolution"] in {"historical", "conflict"}
    )
    assertions = [
        _assertion("MOD-AD-01", bool(index.records), {"records": len(index.records)}),
        _assertion("MOD-AD-02", "current" in path_states, {"path_states": sorted(path_states)}),
        _assertion("MOD-AD-03", "historical" in path_states, {"historical_paths": historical_paths}),
        _assertion(
            "MOD-AD-04",
            all(result["status"] != "ambiguous_current" for result in resolutions.values()),
            {"logical_artifacts": len(resolutions)},
        ),
        _assertion(
            "MOD-AD-05",
            all(item["resolution"] != "historical" for item in audit["worker_references"]),
            {"worker_states": sorted(worker_states)},
        ),
        _assertion(
            "MOD-AD-06",
            all(item["resolution"] != "conflict" for item in audit["worker_references"]),
            {"worker_states": sorted(worker_states)},
        ),
        _assertion(
            "MOD-AD-07",
            all(item["resolution"] != "unknown" for item in audit["worker_references"]),
            {"worker_states": sorted(worker_states)},
        ),
        _assertion(
            "MOD-AD-08",
            all(index.resolve(logical_id)["status"] == "no_current" for logical_id in generated_ids),
            {"generated_logical_ids": generated_ids},
        ),
        _assertion(
            "MOD-AD-09",
            bool(historical_paths) and not contaminated_history,
            {
                "historical_paths_are_indexed": len(historical_paths),
                "historical_paths_on_live_worker_routes": contaminated_history,
            },
        ),
        _assertion(
            "MOD-AD-10",
            all(index.path_status(path)["status"] == "historical" for path in historical_paths),
            {"exact_historical_resolution": len(historical_paths)},
        ),
        _assertion(
            "MOD-AD-11",
            bool(effective_graph["entrypoints"])
            and bool(effective_graph["load_edges"])
            and all(
                item["resolution"] in {"current", "generated"}
                for item in audit["worker_references"]
                if item["purpose"] == "effective_loader"
            ),
            {
                "entrypoints": len(effective_graph["entrypoints"]),
                "effective_load_edges": len(effective_graph["load_edges"]),
                "effective_source_declarations": 0,
                "effective_loader_findings": [
                    item
                    for item in audit["worker_references"]
                    if item["purpose"] == "effective_loader" and item["resolution"] not in {"current", "generated"}
                ],
            },
        ),
        _assertion("MOD-AD-12", audit["status"] == "PASS", {"findings": audit["findings"]}),
    ]
    return {
        "schema_version": 1,
        "status": "PASS" if all(item["status"] == "PASS" for item in assertions) else "FAIL",
        "assertions": assertions,
        "audit": audit,
        "effective_loading_graph": effective_graph,
    }


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    """Serialize reports deterministically for repeatability evidence."""

    return (json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ArtifactLifecycleError(f"cannot load {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ArtifactLifecycleError(f"{path}: TOML root must be a table")
    return payload


def _is_exact_repository_path(raw_path: str) -> bool:
    if not raw_path or "*" in raw_path or " and " in raw_path or ":" in raw_path or " " in raw_path:
        return False
    try:
        normalize_repository_path(raw_path)
    except ArtifactLifecycleError:
        return False
    return True


def _repository_path_declaration(raw_path: str) -> tuple[str, str] | None:
    """Normalize an exact path or an explicitly trailing-slash tree root."""

    value = raw_path.strip()
    scope = "tree" if value.endswith(("/", "\\")) else "exact"
    candidate = value.rstrip("/\\") if scope == "tree" else value
    if not _is_exact_repository_path(candidate):
        return None
    return normalize_repository_path(candidate), scope


def _lifecycle_class(lifecycle: str) -> str:
    if lifecycle in CURRENT_STATES:
        return "current"
    if lifecycle in HISTORICAL_STATES:
        return "historical"
    return "projection"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def _relative_source(path: Path, project_root: Path) -> str:
    return path.resolve().relative_to(project_root).as_posix()


def _assertion(assertion_id: str, passes: bool, evidence: Any) -> dict[str, Any]:
    return {"id": assertion_id, "status": "PASS" if passes else "FAIL", "evidence": evidence}
