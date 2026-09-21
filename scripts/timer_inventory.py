"""Deterministic observations of operational controls and unresolved numeric uses.

The inventory is evidence, not an authority or a proof of semantic completeness.
It never opens runtime databases, credentials, foreign checkouts or harness state.
The rendered inventory is derived local output under ``.groundtruth/derived/``
(the gitignored KB working directory); it is never committed, and ``--check`` is
a local operational diagnostic of those derived bytes, not a completeness verdict.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

from groundtruth_kb.project.operational_control_config import (
    CATALOG_RELATIVE_PATH,
    INVENTORY_GIT_PROBE_CONTROL,
    OperationalControlCatalog,
    OperationalControlConfigError,
    catalog_dict,
    control_value,
    load_operational_control_catalog,
    resolve_operational_controls,
)

EXTRACTION_SPEC_VERSION = 2
# Derived output lives under the gitignored KB working directory, not under
# config/governance/, which carries only the hand-authored control catalog
# (owner ruling D14, 2026-09-17: derived output is untracked and ignored).
GENERATED_ARTIFACT_REL = Path(".groundtruth/derived/timer-inventory.toml")
CONTROL_CLASSES = (
    "timer",
    "ttl",
    "expiry",
    "grace",
    "timeout",
    "wall_clock",
    "retry_count",
    "retry_interval",
    "backoff",
    "throttle",
    "rate_limit",
    "threshold",
    "fan_out",
    "concurrency_limit",
)
SCAN_ROOT_RELS = (
    "scripts",
    "groundtruth-kb/src",
    "groundtruth-kb/templates",
    "config",
    ".harness-baseline-configuration",
    ".githooks",
    ".github",
    "infrastructure",
    "applications",
    "docs",
)
TEST_ROOT_RELS = ("platform_tests", "tests", "groundtruth-kb/tests")
GENERATED_ROOT_RELS = (".agent", ".antigravity", ".api-harness", ".claude", ".codex", ".cursor", ".goose")
SCAN_EXTENSIONS = {
    ".py",
    ".toml",
    ".json",
    ".ps1",
    ".sql",
    ".md",
    ".mdc",
    ".txt",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".sh",
    ".bash",
    ".js",
    ".mjs",
    ".ts",
    ".tf",
    ".tfvars",
    ".hcl",
    ".j2",
    ".jinja",
    ".template",
    ".example",
}
_EXCLUDED_DIRS = {
    ".git",
    ".worktrees",
    "scratchpad",
    "bridge",
    ".gtkb-state",
    "harness-state",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "credentials",
    "secrets",
    "logs",
    "sessions",
    "runtime",
    "data",
    "backups",
    "wal_archive",
    "site-packages",
}
_PRIVATE = re.compile(
    r"(?i)(^\.env(?:\.|$)|pg_(?:service|pass)|password|secret|credential|private[_-]?key|(?:^|[_-])token(?:[_\-.]|$))"
)
_CONTROL_KEY_RE = re.compile(
    r"(?i)(timeout|ttl|expiry|expire|grace|retr|backoff|interval|throttle|rate_?limit|max_items|max_.*count|concurren|sleep|delay|deadline|poll|wait|threshold|budget|cap|limit|window|jitter)"
)
_NUMERIC = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
_TEXT_ASSIGNMENT = re.compile(
    r"""(?ix)(?P<key>[a-z_][a-z0-9_.-]*)["']?\s*[:=]\s*["']?(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+))(?![\w.])"""
)
_DURATION = re.compile(
    r"(?i)(?<![\w.])([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(milliseconds?|seconds?|minutes?|hours?|days?|ms|secs?)\b"
)


def _resolve_project_root(explicit: Path | None) -> Path:
    root = (explicit if explicit is not None else Path.cwd()).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("project root must be an existing directory")
    return root


def _git_head_sha(project_root: Path, catalog: OperationalControlCatalog | None) -> str | None:
    """Use this inventory operation's snapshot; metadata absence never starts Git."""
    marker = project_root / ".git"
    try:
        marker.lstat()
    except FileNotFoundError:
        return None
    if _linked(marker):
        raise ValueError("Git metadata marker must not be redirected")
    if catalog is None:
        raise OperationalControlConfigError("unavailable_catalog", "Git metadata probe requires validated controls")
    values = resolve_operational_controls(catalog, [INVENTORY_GIT_PROBE_CONTROL])
    timeout = float(control_value(values, INVENTORY_GIT_PROBE_CONTROL, unit="seconds"))
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(project_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    revision = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision):
        raise ValueError("Git revision probe did not return a valid revision")
    return revision


def _diagnostic(diagnostics: list[dict[str, Any]], file: str, code: str, detail: str) -> None:
    diagnostics.append({"file": file, "code": code, "detail": detail})


def _linked(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )


def _safe_file(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    current = root
    for part in rel.parts:
        current /= part
        if _linked(current):
            return False
    return stat.S_ISREG(path.lstat().st_mode)


def _excluded(rel: str) -> bool:
    parts = PurePosixPath(rel).parts
    document_data = (
        parts[0] == "applications"
        and "docs" in parts
        and PurePosixPath(rel).suffix in {".json", ".jsonl", ".csv", ".tsv"}
    )
    conversation = bool(re.search(r"(?i)(owner[-_]messages|transcript|conversation[-_]history|handoff)", parts[-1]))
    return (
        document_data
        or conversation
        or any(part in _EXCLUDED_DIRS for part in parts)
        or bool(_PRIVATE.search(parts[-1]))
    )


def _eligible(path: Path) -> bool:
    return path.suffix.lower() in SCAN_EXTENSIONS or not path.suffix


def _discover(root: Path, diagnostics: list[dict[str, Any]]) -> tuple[dict[str, str], list[dict[str, str]], list[str]]:
    paths: dict[str, str] = {}
    excluded: list[dict[str, str]] = [{"path": GENERATED_ARTIFACT_REL.as_posix(), "reason": "inventory_output"}]
    absent: list[str] = []

    def visit(path: Path, surface: str) -> None:
        rel = path.relative_to(root).as_posix()
        if _excluded(rel):
            excluded.append({"path": rel, "reason": "private_or_runtime_boundary"})
            return
        try:
            if _linked(path):
                _diagnostic(diagnostics, rel, "redirected_path", "No linked path or descendant was read")
                return
            if path.is_dir():
                with os.scandir(path) as entries:
                    children = sorted((Path(e.path) for e in entries), key=lambda p: p.name)
                for child in children:
                    visit(child, surface)
            elif path.is_file() and _eligible(path):
                if rel == GENERATED_ARTIFACT_REL.as_posix():
                    return
                else:
                    test = surface == "test" or bool(set(path.relative_to(root).parts) & {"tests", "test", "fixtures"})
                    bundled = rel.startswith("applications/") and bool(
                        set(path.relative_to(root).parts) & {"dist", "build", "assets"}
                    )
                    paths[rel] = "test" if test else "derived" if bundled else surface
            elif path.is_file():
                excluded.append({"path": rel, "reason": "unsupported_extension"})
            else:
                _diagnostic(diagnostics, rel, "nonregular_path", "Unsupported filesystem object was not opened")
        except OSError as exc:
            _diagnostic(diagnostics, rel, "path_unavailable", type(exc).__name__)

    for rel, surface in [(p, "production") for p in SCAN_ROOT_RELS] + [(p, "test") for p in TEST_ROOT_RELS]:
        path = root / rel
        try:
            path.lstat()
        except FileNotFoundError:
            absent.append(rel)
            continue
        except OSError as exc:
            _diagnostic(diagnostics, rel, "path_unavailable", type(exc).__name__)
            continue
        visit(path, surface)
    # Root-level documentation, scripts and declarations are also visible; never recurse into unselected roots.
    with os.scandir(root) as entries:
        top = sorted((Path(e.path) for e in entries), key=lambda p: p.name)
    for path in top:
        try:
            if not path.is_dir() and _eligible(path):
                visit(path, "production")
        except OSError as exc:
            _diagnostic(diagnostics, path.name, "path_unavailable", type(exc).__name__)
    generated_roots = set(GENERATED_ROOT_RELS)
    profile_path = root / "scripts/harness_projection/profiles.toml"
    if profile_path.exists():
        try:
            if not _safe_file(profile_path, root):
                raise ValueError("unsafe projection profiles")
            profiles = tomllib.loads(profile_path.read_text(encoding="utf-8"))
            configured = set()
            for profile in profiles["harnesses"].values():
                if profile.get("status") == "profile_pending":
                    continue
                name = profile["config_dir"]
                if (
                    not isinstance(name, str)
                    or "\\" in name
                    or ":" in name
                    or any(p in {"", ".", ".."} for p in name.split("/"))
                    or PurePosixPath(name).parts[0] not in GENERATED_ROOT_RELS
                ):
                    raise ValueError("unsafe projection destination")
                configured.add(name)
            generated_roots -= {
                base for base in GENERATED_ROOT_RELS if any(name.startswith(base + "/") for name in configured)
            }
            generated_roots.update(configured)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            _diagnostic(
                diagnostics,
                "scripts/harness_projection/profiles.toml",
                "invalid_projection_profiles",
                type(exc).__name__,
            )
    for rel in sorted(generated_roots):
        directory = root / rel
        try:
            directory.lstat()
        except FileNotFoundError:
            absent.append(rel)
            continue
        manifest = directory / ".projection-manifest.json"
        try:
            if not _safe_file(manifest, root):
                raise ValueError("unsafe projection manifest")
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            if (
                not isinstance(payload, dict)
                or payload.get("engine") != "scripts/harness_projection/project_harness.py"
                or payload.get("baseline_root") != ".harness-baseline-configuration"
                or not isinstance(payload.get("paths"), list)
            ):
                raise ValueError("invalid projection manifest")
            paths[manifest.relative_to(root).as_posix()] = "derived"
            declared = payload["paths"]
            for name in declared:
                if (
                    not isinstance(name, str)
                    or "\\" in name
                    or ":" in name
                    or any(ord(c) < 32 for c in name)
                    or any(p in {"", ".", ".."} for p in name.split("/"))
                    or not name.startswith(rel + "/")
                ):
                    raise ValueError("invalid projection path")
            for name in sorted(set(declared)):
                if _excluded(name):
                    excluded.append({"path": name, "reason": "private_or_runtime_boundary"})
                elif not _safe_file(root / name, root):
                    raise ValueError("projection manifest entry is not a regular unlinked file")
                else:
                    visit(root / name, "derived")
            excluded.append(
                {"path": rel, "reason": "only_manifest_declared_outputs_read; other harness contents are private"}
            )
        except (OSError, ValueError, TypeError) as exc:
            _diagnostic(
                diagnostics, manifest.relative_to(root).as_posix(), "projection_unavailable", type(exc).__name__
            )
    return (
        dict(sorted(paths.items())),
        sorted(excluded, key=lambda item: (item["path"], item["reason"])),
        sorted(absent),
    )


def _classify_control(key_hint: str, name: str, category_hint: str) -> tuple[str, str, str]:
    lowered = (key_hint + " " + name).lower()
    if "timeout" in lowered or "deadline" in lowered:
        control = "timeout"
    elif any(w in lowered for w in ("ttl", "expiry", "expire")):
        control = "ttl" if "ttl" in lowered else "expiry"
    elif "grace" in lowered:
        control = "grace"
    elif any(w in lowered for w in ("retry_count", "max_retr", "retries", "retry_total")):
        control = "retry_count"
    elif any(w in lowered for w in ("retry_interval", "backoff", "retry_delay")):
        control = "backoff" if "backoff" in lowered else "retry_interval"
    elif "rate_limit" in lowered or "throttle" in lowered:
        control = "throttle" if "throttle" in lowered else "rate_limit"
    elif any(w in lowered for w in ("concurrency", "concurrent", "max_items", "fan_out")):
        control = (
            "concurrency_limit" if "concurren" in lowered else ("fan_out" if "fan_out" in lowered else "threshold")
        )
    elif any(w in lowered for w in ("threshold", "budget", "cap", "limit", "max_")):
        control = "threshold"
    elif any(w in lowered for w in ("interval", "poll", "sleep", "wait", "window")):
        control = "wall_clock"
    else:
        control = "unclassified"
    category = next(
        (
            word
            for word in (
                "claim",
                "lock",
                "poll",
                "watchdog",
                "session",
                "dispatcher",
                "queue",
                "provider",
                "harness",
                "project",
                "role",
            )
            if word in (category_hint + " " + lowered).lower()
        ),
        "global",
    )
    return control, category, category


def _record(
    rel: str,
    line: int,
    column: int,
    symbol: str,
    value: Any,
    surface: str,
    form: str,
    *,
    status: str | None = None,
    unit: str | None = None,
    control_id: str | None = None,
) -> dict[str, Any]:
    control, category, scope = _classify_control(symbol, symbol, rel)
    if status is None:
        status = "candidate_control" if _CONTROL_KEY_RE.search(symbol) else "unclassified_numeric"
    if unit is None and status == "candidate_control":
        unit = (
            "seconds"
            if control in {"timer", "timeout", "ttl", "expiry", "grace", "wall_clock", "retry_interval", "backoff"}
            else "count"
        )
    canonical = status == "canonical_value"
    return {
        "identity": f"{rel}:{line}:{column}:{symbol}",
        "file": rel,
        "line": line,
        "column": column,
        "symbol": symbol,
        "value": str(value) if value is not None else None,
        "unit": unit,
        "unit_evidence": "canonical"
        if canonical
        else ("explicit" if form == "duration_text" else "name_heuristic" if unit else "unknown"),
        "control_class": control,
        "category": category,
        "scope": scope,
        "value_form": form,
        "current_authority": CATALOG_RELATIVE_PATH.as_posix() if canonical else "unresolved",
        "hard_coded": not canonical and status not in {"control_reference", "unresolved_reference"},
        "surface": surface,
        "classification": status,
        "control_id": control_id,
        "centralization_candidate": CATALOG_RELATIVE_PATH.as_posix(),
        "migration_priority": "unassessed",
        "relaxed_first_candidate": None,
        "failure_count": None,
        "success_count": None,
        "censor_count": None,
        "right_censored": None,
        "observed_failure_evidence": None,
        "coupling": [],
    }


def _node_name(node: ast.AST) -> str:
    """Identify a source use without copying string arguments into diagnostics."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _node_name(node.value) + "." + node.attr
    if isinstance(node, ast.Call):
        return _node_name(node.func) + "()"
    if isinstance(node, ast.Subscript):
        return _node_name(node.value) + "[]"
    if isinstance(node, (ast.List, ast.Tuple)):
        return "(" + ",".join(_node_name(item) for item in node.elts) + ")"
    return type(node).__name__


def _numeric_source(lines: list[bytes], node: ast.expr) -> str:
    """AST columns are UTF-8 byte offsets; avoid rescanning a file per literal."""
    end_line = node.end_lineno or node.lineno
    end_column = node.end_col_offset if node.end_col_offset is not None else len(lines[end_line - 1])
    if end_line == node.lineno:
        return lines[node.lineno - 1][node.col_offset : end_column].decode("utf-8")
    return (
        lines[node.lineno - 1][node.col_offset :]
        + b"".join(lines[node.lineno : end_line - 1])
        + lines[end_line - 1][:end_column]
    ).decode("utf-8")


def _python_records(
    text: str, rel: str, surface: str, keys: set[str], diagnostics: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        _diagnostic(diagnostics, rel, "syntax_error", f"Python line {exc.lineno}; content omitted")
        return []
    lines = [line.encode("utf-8") for line in text.splitlines(keepends=True)]
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    records = []
    seen = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or isinstance(node.value, bool):
            continue
        parent = parents.get(node)
        symbol = "numeric_literal"
        current: ast.AST = node
        # The nearest assignment/argument/default determines the observed use. No semantic exemption is inferred.
        while current in parents:
            ancestor = parents[current]
            if isinstance(ancestor, ast.keyword):
                symbol = ancestor.arg or "keyword_unpack"
                break
            if isinstance(ancestor, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                target = ancestor.targets[0] if isinstance(ancestor, ast.Assign) else ancestor.target
                symbol = _node_name(target)
                break
            if isinstance(ancestor, ast.Call):
                symbol = _node_name(ancestor.func)
                if not isinstance(node.value, str) or not _NUMERIC.fullmatch(node.value):
                    break
            if isinstance(ancestor, ast.arguments):
                positional = ancestor.posonlyargs + ancestor.args
                defaults = (
                    dict(zip(ancestor.defaults, positional[-len(ancestor.defaults) :])) if ancestor.defaults else {}
                )
                defaults.update(
                    {value: arg for arg, value in zip(ancestor.kwonlyargs, ancestor.kw_defaults) if value is not None}
                )
                if current in defaults:
                    symbol = defaults[current].arg
                break
            if isinstance(ancestor, ast.Dict):
                for k, v in zip(ancestor.keys, ancestor.values):
                    if v is current and isinstance(k, ast.Constant) and isinstance(k.value, str):
                        symbol = k.value
                        break
                if symbol != "numeric_literal":
                    break
            current = ancestor
        if _PRIVATE.search(symbol):
            continue
        value = node.value
        if isinstance(value, str):
            if value in keys or (
                re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z0-9_]+){2,}", value) and _CONTROL_KEY_RE.search(value)
            ):
                identity = (node.lineno, node.col_offset, value)
                if identity not in seen:
                    seen.add(identity)
                    records.append(
                        _record(
                            rel,
                            node.lineno,
                            node.col_offset,
                            value,
                            None,
                            surface,
                            "control_key_reference",
                            status="control_reference" if value in keys else "unresolved_reference",
                            control_id=value,
                        )
                    )
                continue
            if not _NUMERIC.fullmatch(value) or not (
                _CONTROL_KEY_RE.search(symbol) or isinstance(parent, ast.Call) and _node_name(parent.func) == "Decimal"
            ):
                continue
        elif not isinstance(value, (int, float, complex)):
            continue
        literal: ast.expr = node
        if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, (ast.USub, ast.UAdd)):
            literal = parent
        rendered = _numeric_source(lines, literal)
        if isinstance(value, str):
            rendered = value
        identity = (node.lineno, node.col_offset, symbol)
        if identity not in seen:
            seen.add(identity)
            records.append(
                _record(
                    rel,
                    node.lineno,
                    node.col_offset,
                    symbol,
                    rendered,
                    surface,
                    "numeric_string" if isinstance(value, str) else "python_literal",
                )
            )
    return records


def _structured_records(payload: Any, rel: str, surface: str) -> list[dict[str, Any]]:
    records = []

    def visit(value: Any, parts: list[str]) -> None:
        symbol = ".".join(parts)
        if any(_PRIVATE.search(part) for part in parts):
            return
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, [*parts, str(key)])
        elif isinstance(value, list):
            for i, child in enumerate(value):
                visit(child, [*parts, str(i)])
        elif not isinstance(value, bool) and (
            isinstance(value, (int, float))
            or isinstance(value, str)
            and _NUMERIC.fullmatch(value)
            and _CONTROL_KEY_RE.search(symbol)
        ):
            records.append(_record(rel, 0, 0, symbol, value, surface, "json_toml_configuration"))

    visit(payload, [])
    return records


def _text_records(text: str, rel: str, surface: str) -> list[dict[str, Any]]:
    records = []
    for index, line in enumerate(text.splitlines(), 1):
        # Do not emit excerpts or values from secret-shaped assignments.
        if _PRIVATE.search(line):
            continue
        for match in _TEXT_ASSIGNMENT.finditer(line):
            records.append(
                _record(rel, index, match.start(), match["key"], match["value"], surface, "lexical_assignment")
            )
        for match in _DURATION.finditer(line):
            records.append(
                _record(
                    rel,
                    index,
                    match.start(),
                    "duration",
                    match[1],
                    surface,
                    "duration_text",
                    status="candidate_control",
                    unit=match[2].lower(),
                )
            )
    return records


def build_inventory(project_root: Path | None = None) -> dict[str, Any]:
    root = _resolve_project_root(project_root)
    diagnostics: list[dict[str, Any]] = []
    paths, excluded, absent = _discover(root, diagnostics)
    catalog = None
    if CATALOG_RELATIVE_PATH.as_posix() in paths:
        try:
            catalog = load_operational_control_catalog(root)
        except (OperationalControlConfigError, OSError) as exc:
            _diagnostic(diagnostics, CATALOG_RELATIVE_PATH.as_posix(), "invalid_control_catalog", type(exc).__name__)
    else:
        _diagnostic(
            diagnostics,
            CATALOG_RELATIVE_PATH.as_posix(),
            "missing_control_catalog",
            "Live control artifact is absent from the selected root",
        )
    try:
        generating_commit = _git_head_sha(root, catalog)
    except (OperationalControlConfigError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        generating_commit = None
        _diagnostic(diagnostics, ".git", "git_metadata_unavailable", type(exc).__name__)
    keys = set(catalog.definitions) if catalog is not None else set()
    records: list[dict[str, Any]] = []
    tests: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []
    scanned = []
    for rel, surface in paths.items():
        path = root / rel
        try:
            if not _safe_file(path, root):
                raise ValueError("redirected or nonregular source")
            content = path.read_bytes()
            text = content.decode("utf-8-sig")
        except (OSError, UnicodeError, ValueError) as exc:
            _diagnostic(diagnostics, rel, "source_unavailable", type(exc).__name__)
            continue
        scanned.append(
            {
                "path": rel,
                "surface": surface,
                "sha256": hashlib.sha256(content).hexdigest(),
                "extractor": "python_ast"
                if path.suffix == ".py"
                else "structured"
                if path.suffix in {".json", ".toml"}
                else "lexical",
            }
        )
        if rel == CATALOG_RELATIVE_PATH.as_posix():
            if catalog is None:
                continue
            if "sha256:" + hashlib.sha256(content).hexdigest() != catalog.catalog_sha256:
                _diagnostic(diagnostics, rel, "catalog_changed", "Live control artifact changed while inventorying")
                continue
            current = []
            for key, definition in catalog.definitions.items():
                row = _record(
                    rel,
                    0,
                    0,
                    key,
                    definition.value,
                    surface,
                    "canonical_control",
                    status="canonical_value",
                    unit=definition.unit,
                    control_id=key,
                )
                row.update(
                    scope=definition.scope,
                    category=definition.category,
                    consumers=list(definition.consumers),
                    migration_state=definition.migration_state,
                    catalog_sha256=catalog.catalog_sha256,
                    coupling=[
                        i.invariant_id for i in catalog.invariants if key in {i.left_control_id, i.right_control_id}
                    ],
                )
                current.append(row)
        elif path.suffix == ".py":
            current = _python_records(text, rel, surface, keys, diagnostics)
        elif path.suffix in {".toml", ".json"}:
            try:
                payload = tomllib.loads(text) if path.suffix == ".toml" else json.loads(text)
                current = _structured_records(payload, rel, surface)
            except (ValueError, TypeError):
                _diagnostic(diagnostics, rel, "syntax_error", "Structured input could not be parsed; content omitted")
                current = _text_records(text, rel, surface)
        else:
            current = _text_records(text, rel, surface)
        (tests if surface == "test" else derived if surface == "derived" else records).extend(current)
    for group in (records, tests, derived):
        group.sort(key=lambda r: r["identity"])
    class_counts = {c: sum(r["control_class"] == c for r in records) for c in (*CONTROL_CLASSES, "unclassified")}
    spec_meta = {
        "version": EXTRACTION_SPEC_VERSION,
        "control_classes": list(CONTROL_CLASSES),
        "production_roots": list(SCAN_ROOT_RELS),
        "test_roots": list(TEST_ROOT_RELS),
        "generated_roots": list(GENERATED_ROOT_RELS),
        "extensions": sorted(SCAN_EXTENSIONS),
        "excluded_directories": sorted(_EXCLUDED_DIRS),
    }
    return {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "extraction_spec": spec_meta,
        "extraction_spec_digest": hashlib.sha256(json.dumps(spec_meta, sort_keys=True).encode()).hexdigest(),
        "generating_commit": generating_commit,
        "scan_roots": list(SCAN_ROOT_RELS),
        "surface_roots": list(TEST_ROOT_RELS),
        "include_extensions": sorted(SCAN_EXTENSIONS),
        "summary": {
            "production_record_count": len(records),
            "test_record_count": len(tests),
            "derived_record_count": len(derived),
            "production_class_counts": class_counts,
            "unclassified_or_ambiguous_count": sum(
                r["classification"] in {"unclassified_numeric", "unresolved_reference"} for r in records
            ),
            "canonical_control_count": len(keys),
            "diagnostic_count": len(diagnostics),
        },
        "coverage": {
            "status": "partial" if diagnostics else "declared_inputs_read",
            "semantic_completeness": "unproven",
            "scanned_files": scanned,
            "excluded_paths": excluded,
            "absent_roots": absent,
            "diagnostics": sorted(diagnostics, key=lambda d: (d["file"], d["code"], d["detail"])),
            "limits": [
                "Python numeric literals and named control references are observations, not proof of dataflow.",
                "Names cannot prove whether a numeric literal is operational; unclassified uses require semantic review.",
                "Non-Python text extraction is lexical; generated and source evidence are reported separately.",
                "Private/runtime paths are deliberately not opened; manifests select generated output paths but confer no authority.",
                "This inventory does not prove all controls migrated, calibrated or executable TEST-linked.",
            ],
        },
        "catalog": catalog_dict(catalog) if catalog is not None else None,
        "records": records,
        "test_records": tests,
        "derived_records": derived,
    }


def _toml_escape(value: Any) -> str:
    if value is None:
        raise ValueError("TOML has no null value; omit unavailable optional keys")
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_escape(v) for v in value) + "]"
    if isinstance(value, dict):
        return (
            "{"
            + ", ".join(f"{json.dumps(str(k))} = {_toml_escape(v)}" for k, v in sorted(value.items()) if v is not None)
            + "}"
        )
    return json.dumps(str(value), ensure_ascii=False)


def render_toml(inventory: dict[str, Any]) -> str:
    lines = [
        "# Generated by scripts/timer_inventory.py. Do not hand-edit.",
        "# Observations only: semantic completeness and calibration are not established.",
    ]
    for field in ("records", "test_records", "derived_records"):
        if not inventory[field]:
            lines.append(f"{field} = []")
    lines.extend(
        [
            "",
            "[metadata]",
            f"schema_version = {inventory['schema_version']}",
            f"extraction_spec_version = {inventory['extraction_spec']['version']}",
            f"extraction_spec_digest = {_toml_escape(inventory['extraction_spec_digest'])}",
        ]
    )
    if inventory["generating_commit"] is not None:
        lines.append(f"generating_commit = {_toml_escape(inventory['generating_commit'])}")
    for field in ("summary", "coverage"):
        lines.extend(["", f"[{field}]"])
        for key, value in inventory[field].items():
            if value is not None:
                lines.append(f"{key} = {_toml_escape(value)}")
    for field in ("records", "test_records", "derived_records"):
        for row in inventory[field]:
            lines.extend(["", f"[[{field}]]"])
            for key, value in row.items():
                if value is not None:
                    lines.append(f"{key} = {_toml_escape(value)}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Observe control values and unresolved numeric uses without claiming semantic completeness."
    )
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument(
        "--write", action="store_true", help="Derive the inventory artifact; never change runtime values."
    )
    parser.add_argument(
        "--check", action="store_true", help="Check derived bytes match; this is not a completeness verdict."
    )
    parser.add_argument("--json", action="store_true", help="Emit complete observations and coverage diagnostics.")
    args = parser.parse_args(argv)
    try:
        root = _resolve_project_root(args.project_root)
        inventory = build_inventory(root)
        if args.json:
            print(json.dumps(inventory, indent=2, sort_keys=True))
            return 0 if inventory["coverage"]["status"] != "partial" else 1
        rendered = render_toml(inventory)
        artifact = root / GENERATED_ARTIFACT_REL
        # Check parents before deriving; no generated artifact may redirect the writer.
        for path in (artifact, *artifact.parents):
            if path == root:
                break
            if path.exists() or path.is_symlink():
                if _linked(path):
                    raise ValueError("inventory output path must not be redirected")
        if args.write:
            artifact.parent.mkdir(parents=True, exist_ok=True)
            artifact.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"wrote {artifact}; semantic completeness remains unproven")
        elif args.check:
            if not artifact.is_file() or artifact.read_text(encoding="utf-8") != rendered:
                print("timer inventory is out of date; regenerate with --write", file=sys.stderr)
                return 2
            print("timer inventory bytes are current; semantic completeness remains unproven")
        else:
            print(rendered, end="")
        return 0 if inventory["coverage"]["status"] != "partial" else 1
    except (OSError, ValueError) as exc:
        print(f"timer inventory unavailable ({type(exc).__name__}); inspect the selected root", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
