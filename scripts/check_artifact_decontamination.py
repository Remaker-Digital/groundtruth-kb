#!/usr/bin/env python3
"""Audit artifact authority across the effective local Python import graph."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.artifact_lifecycle.decontamination import (  # noqa: E402
    HISTORICAL_STATES,
    PROJECTION_STATES,
    ArtifactLifecycleError,
    WorkerReference,
    _EffectiveLoadScanner,
    load_repository_snapshot,
)
from groundtruth_kb.artifact_lifecycle.decontamination import (  # noqa: E402
    discover_effective_loading_graph as discover_entrypoint_loading_graph,
)


@dataclass(frozen=True, slots=True)
class LocalImportEdge:
    """A statically resolved import between two repository-local modules."""

    importer: str
    imported: str
    module: str
    line: int
    source: str


@dataclass(frozen=True, slots=True)
class UnresolvedLocalImport:
    """An import that targets local code but cannot be resolved exactly."""

    importer: str
    module: str
    line: int
    reason: str
    source: str


@dataclass(frozen=True, slots=True)
class _ImportRequest:
    module: str
    line: int
    level: int = 0
    imported_names: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DeclaredDynamicImport:
    """A non-literal import confined to an explicit, reviewed plugin boundary."""

    function: str
    line: int
    reason: str


class _LocalImportResolver:
    """Resolve local modules from paths without importing or executing them."""

    def __init__(self, project_root: Path):
        self.root = project_root.resolve()
        self.package_src = self.root / "groundtruth-kb" / "src"

    def resolve(
        self,
        request: _ImportRequest,
        importer: Path,
    ) -> tuple[tuple[Path, ...], str | None, str]:
        module, error = self._absolute_module(request, importer)
        display = "." * request.level + request.module
        if error:
            return (), error, display

        resolved = self._resolve_module(module, importer)
        if not resolved:
            if request.level or self._has_local_prefix(module, importer):
                return (), "local module does not resolve to a repository file", display
            return (), None, display

        paths = list(resolved)
        final_path = resolved[-1]
        if final_path.name == "__init__.py":
            for name in request.imported_names:
                if name == "*":
                    continue
                child_module = f"{module}.{name}" if module else name
                child = self._resolve_module(child_module, importer)
                if child:
                    paths.extend(child)

        return tuple(dict.fromkeys(paths)), None, display

    def _absolute_module(self, request: _ImportRequest, importer: Path) -> tuple[str, str | None]:
        if request.level == 0:
            return request.module, None

        package = self._package_parts(importer)
        if package is None:
            return "", "relative import originates outside a Python package"
        parents_to_remove = request.level - 1
        if parents_to_remove > len(package):
            return "", "relative import escapes its Python package"
        base = package[: len(package) - parents_to_remove] if parents_to_remove else package
        suffix = tuple(part for part in request.module.split(".") if part)
        absolute = ".".join((*base, *suffix))
        if not absolute:
            return "", "relative import has no resolvable module"
        return absolute, None

    def _resolve_module(self, module: str, importer: Path) -> tuple[Path, ...]:
        if not module:
            return ()
        parts = tuple(module.split("."))
        for search_root in self._search_roots(importer):
            chain: list[Path] = []
            prefix = search_root
            for part in parts[:-1]:
                prefix /= part
                initializer = prefix / "__init__.py"
                if initializer.is_file():
                    chain.append(initializer.resolve())
                elif not prefix.is_dir():
                    break
            else:
                module_file = prefix / f"{parts[-1]}.py"
                package_file = prefix / parts[-1] / "__init__.py"
                if module_file.is_file():
                    return tuple((*chain, module_file.resolve()))
                if package_file.is_file():
                    return tuple((*chain, package_file.resolve()))
        return ()

    def _has_local_prefix(self, module: str, importer: Path) -> bool:
        if not module:
            return True
        top_level = module.split(".", 1)[0]
        for search_root in self._search_roots(importer):
            if (search_root / f"{top_level}.py").is_file() or (search_root / top_level).is_dir():
                return True
        return False

    def _search_roots(self, importer: Path) -> tuple[Path, ...]:
        candidates = [importer.parent]
        if self._is_relative_to(importer, self.package_src):
            candidates.append(self.package_src)
        candidates.extend((self.root, self.package_src))
        return tuple(dict.fromkeys(path.resolve() for path in candidates if path.is_dir()))

    def _package_parts(self, importer: Path) -> tuple[str, ...] | None:
        for search_root in (self.package_src, self.root):
            if not search_root.is_dir():
                continue
            try:
                relative = importer.resolve().relative_to(search_root)
            except ValueError:
                continue
            parent_parts = relative.parent.parts
            if all(
                (search_root.joinpath(*parent_parts[:index]) / "__init__.py").is_file()
                for index in range(1, len(parent_parts) + 1)
            ):
                return tuple(parent_parts)
        return None

    @staticmethod
    def _is_relative_to(path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
        except ValueError:
            return False
        return True


def _dynamic_import_contract(tree: ast.AST) -> dict[str, str]:
    contract: dict[str, str] = {}
    for node in getattr(tree, "body", ()):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(
            isinstance(target, ast.Name) and target.id == "__gtkb_dynamic_import_contract__" for target in targets
        ):
            continue
        value = node.value
        if not isinstance(value, ast.Dict):
            raise ArtifactLifecycleError("__gtkb_dynamic_import_contract__ must be a literal string mapping")
        for key, reason in zip(value.keys, value.values, strict=True):
            if not (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and isinstance(reason, ast.Constant)
                and isinstance(reason.value, str)
                and key.value.strip()
                and reason.value.strip()
            ):
                raise ArtifactLifecycleError("__gtkb_dynamic_import_contract__ entries must be non-empty strings")
            contract[key.value] = reason.value
    return contract


def _enclosing_function(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str | None:
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
        current = parents.get(current)
    return None


def _import_requests(
    tree: ast.AST,
) -> tuple[tuple[_ImportRequest, ...], tuple[DeclaredDynamicImport, ...]]:
    requests: set[_ImportRequest] = set()
    declared: set[DeclaredDynamicImport] = set()
    import_module_names: set[str] = set()
    importlib_names: set[str] = set()
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    dynamic_contract = _dynamic_import_contract(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                requests.add(_ImportRequest(alias.name, node.lineno))
                if alias.name == "importlib":
                    importlib_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            requests.add(
                _ImportRequest(
                    node.module or "",
                    node.lineno,
                    node.level,
                    tuple(alias.name for alias in node.names),
                )
            )
            if node.level == 0 and node.module == "importlib":
                import_module_names.update(
                    alias.asname or alias.name for alias in node.names if alias.name == "import_module"
                )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        is_dynamic_import = (isinstance(node.func, ast.Name) and node.func.id in import_module_names) or (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "import_module"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in importlib_names
        )
        if not is_dynamic_import:
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
            function_name = _enclosing_function(node, parents)
            if function_name in dynamic_contract:
                declared.add(DeclaredDynamicImport(function_name, node.lineno, dynamic_contract[function_name]))
                continue
            requests.add(_ImportRequest("<dynamic>", node.lineno, level=-1))
            continue
        requests.add(_ImportRequest(node.args[0].value, node.lineno))

    ordered_requests = tuple(
        sorted(requests, key=lambda item: (item.line, item.level, item.module, item.imported_names))
    )
    ordered_declared = tuple(sorted(declared, key=lambda item: (item.line, item.function, item.reason)))
    return ordered_requests, ordered_declared


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def discover_effective_loading_graph(project_root: Path) -> dict[str, Any]:
    """Return deterministic read and import closure for registered entrypoints."""

    root = project_root.resolve()
    entrypoint_graph = discover_entrypoint_loading_graph(root)
    entrypoint_paths = tuple(sorted({item["path"] for item in entrypoint_graph["entrypoints"]}, key=str.casefold))
    resolver = _LocalImportResolver(root)
    queue = deque(root / Path(path) for path in entrypoint_paths)
    queued = {path.resolve() for path in queue}
    visited: set[Path] = set()
    import_edges: set[LocalImportEdge] = set()
    unresolved: set[UnresolvedLocalImport] = set()
    declared_dynamic_imports: set[tuple[str, int, str, str]] = set()
    load_edges: dict[tuple[str, str, int, str, str], dict[str, Any]] = {}

    while queue:
        source_path = queue.popleft().resolve()
        queued.discard(source_path)
        if source_path in visited:
            continue
        visited.add(source_path)
        source = _relative(source_path, root)
        try:
            text = source_path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=source)
        except (OSError, SyntaxError, UnicodeError) as exc:
            raise ArtifactLifecycleError(f"cannot inspect reachable Python module {source}: {exc}") from exc

        scanner = _EffectiveLoadScanner(source, root)
        for edge in scanner.scan(tree):
            payload = asdict(edge)
            key = (
                str(payload["entrypoint"]).casefold(),
                str(payload["path"]).casefold(),
                int(payload["line"]),
                str(payload["loader"]),
                str(payload["source"]).casefold(),
            )
            load_edges[key] = payload

        import_requests, declared_dynamic = _import_requests(tree)
        declared_dynamic_imports.update((source, item.line, item.function, item.reason) for item in declared_dynamic)
        for request in import_requests:
            if request.level == -1:
                unresolved.add(
                    UnresolvedLocalImport(
                        source,
                        "<dynamic>",
                        request.line,
                        "dynamic import target is not a string literal",
                        f"{source}:{request.line}",
                    )
                )
                continue
            targets, error, display = resolver.resolve(request, source_path)
            if error:
                unresolved.add(UnresolvedLocalImport(source, display, request.line, error, f"{source}:{request.line}"))
                continue
            for target in targets:
                imported = _relative(target, root)
                import_edges.add(LocalImportEdge(source, imported, display, request.line, f"{source}:{request.line}"))
                if target not in visited and target not in queued:
                    queue.append(target)
                    queued.add(target)

    ordered_imports = sorted(
        import_edges,
        key=lambda item: (item.importer.casefold(), item.line, item.module.casefold(), item.imported.casefold()),
    )
    ordered_unresolved = sorted(
        unresolved,
        key=lambda item: (item.importer.casefold(), item.line, item.module.casefold(), item.reason),
    )
    ordered_modules = sorted((_relative(path, root) for path in visited), key=str.casefold)
    ordered_loads = [load_edges[key] for key in sorted(load_edges)]
    return {
        "schema_version": 2,
        "entrypoints": entrypoint_graph["entrypoints"],
        "python_modules": ordered_modules,
        "import_edges": [asdict(item) for item in ordered_imports],
        "unresolved_imports": [asdict(item) for item in ordered_unresolved],
        "declared_dynamic_imports": [
            {"source": source, "line": line, "function": function, "reason": reason}
            for source, line, function, reason in sorted(declared_dynamic_imports)
        ],
        "load_edges": ordered_loads,
    }


def audit_repository(project_root: Path) -> dict[str, Any]:
    """Audit reads against declared authority; filesystem existence grants none."""

    root = project_root.resolve()
    index, declared_references = load_repository_snapshot(root)
    graph = discover_effective_loading_graph(root)
    effective_references = tuple(
        WorkerReference(edge["path"], edge["source"], "effective_loader") for edge in graph["load_edges"]
    )
    audit = index.audit((*declared_references, *effective_references))
    findings = list(audit["findings"])
    findings.extend(
        {
            "id": f"unresolved-import:{item['source']}",
            "severity": "P1",
            "reason": f"unresolved local dependency {item['module']!r}: {item['reason']}",
        }
        for item in graph["unresolved_imports"]
    )
    findings.sort(key=lambda item: (item["severity"], item["id"], item["reason"]))
    audit["findings"] = findings
    audit["status"] = "PASS" if not findings else "FAIL"

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
    effective_findings = [
        item
        for item in audit["worker_references"]
        if item["purpose"] == "effective_loader" and item["resolution"] not in {"current", "generated"}
    ]
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
            bool(graph["entrypoints"])
            and bool(graph["load_edges"])
            and not graph["unresolved_imports"]
            and not effective_findings,
            {
                "entrypoints": len(graph["entrypoints"]),
                "reachable_python_modules": len(graph["python_modules"]),
                "import_edges": len(graph["import_edges"]),
                "effective_load_edges": len(graph["load_edges"]),
                "effective_source_declarations": 0,
                "unresolved_imports": graph["unresolved_imports"],
                "effective_loader_findings": effective_findings,
            },
        ),
        _assertion("MOD-AD-12", audit["status"] == "PASS", {"findings": findings}),
    ]
    return {
        "schema_version": 2,
        "status": "PASS" if all(item["status"] == "PASS" for item in assertions) else "FAIL",
        "assertions": assertions,
        "audit": audit,
        "effective_loading_graph": graph,
    }


def _assertion(assertion_id: str, passes: bool, evidence: Any) -> dict[str, Any]:
    return {"id": assertion_id, "status": "PASS" if passes else "FAIL", "evidence": evidence}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        report = audit_repository(args.project_root)
    except ArtifactLifecycleError as exc:
        print(f"ARTIFACT DECONTAMINATION: FAIL - {exc}", file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"ARTIFACT DECONTAMINATION: {report['status']}")
        for assertion in report["assertions"]:
            print(f"- {assertion['id']}: {assertion['status']}")
        for finding in report["audit"]["findings"]:
            print(f"- {finding['severity']} {finding['id']}: {finding['reason']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
