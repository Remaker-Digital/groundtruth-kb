#!/usr/bin/env python3
"""Deterministic full-root reference migration planner for WI-5640.

``preflight``, ``plan``, and ``verify`` are observation modes.  ``apply`` and
``rollback`` are internally gated to the separately reviewed exact-plan child
thread; the main v4 GO can never authorize repository-consumer writes.
"""

from __future__ import annotations

import argparse
import ast
import csv
import ctypes
import fnmatch
import hashlib
import importlib.util
import io
import json
import os
import posixpath
import re
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
import tokenize
import tomllib
import unicodedata
import uuid
import zipfile
from collections import deque
from collections.abc import Iterator, Sequence
from contextlib import contextmanager, nullcontext
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POLICY = Path("config/file-reference-migration/wi5640.toml")
MAIN_BRIDGE_ID = "gtkb-file-move-rename-canonicalization-v4"
CHILD_BRIDGE_ID = "gtkb-file-move-rename-canonicalization-v4-plan-approval"
RUNTIME_RELATIVE = Path(".gtkb-state/file-reference-migration/wi5640")
_FULL_OBSERVATION_RELATIVE = RUNTIME_RELATIVE / "full-observation.jsonl"
_FULL_OBSERVATION_SUMMARY_RELATIVE = RUNTIME_RELATIVE / "full-observation-summary.json"
SCHEMA_VERSION = 2
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from _wrap_io import _atomic_write_bytes  # noqa: E402

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_AUTHOR_SESSION_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?author_session_context_id\s*:\s*[`\"']?([^`\"'\s]+)")
_BINDING_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?migration_plan_binding\s*:\s*(\{.*\})\s*$")
_BINDING_SHA_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?binding_sha256\s*:\s*[`\"']?(sha256:[0-9a-f]{64})")
_REVIEWED_SHA_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?reviewed_proposal_sha256\s*:\s*[`\"']?(sha256:[0-9a-f]{64})")
_REVIEWED_FILE_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?reviewed_proposal_file\s*:\s*[`\"']?([^`\"'\s]+)")
_TARGET_PATHS_RE = re.compile(r"(?im)^\s*target_paths\s*:\s*(\[[^\n]*\])\s*$")

_TEXT_SUFFIXES = {
    ".bat",
    ".cfg",
    ".cmd",
    ".css",
    ".csv",
    ".env",
    ".gitignore",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonl",
    ".jsx",
    ".md",
    ".mdc",
    ".ps1",
    ".psd1",
    ".psm1",
    ".py",
    ".pyi",
    ".rst",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
_GENERATED_PREFIXES = (
    ".agent/skills/",
    ".api-harness/skills/",
    ".codex/skills/",
    ".cursor/skills/",
    ".goose/skills/",
)
_BINDING_KEYS = frozenset(
    {
        "alias_occurrence_sha256",
        "catalog_sha256",
        "classification_sha256",
        "closure_fingerprint",
        "closure_inventory_sha256",
        "csv_sha256",
        "engine_sha256",
        "exception_sha256",
        "expected_final_closure_fingerprint",
        "generator_input_sha256",
        "git_index_sha256",
        "operation_manifest_sha256",
        "physical_inventory_sha256",
        "plan_sha256",
        "policy_sha256",
        "preimage_set_sha256",
        "projection_sha256",
        "proposed_write_sha256",
        "residual_sha256",
        "retained_source_sha256",
        "scanner_sha256",
        "schema_version",
        "structured_occurrence_sha256",
        "write_set_sha256",
    }
)

_REQUIRED_ALIAS_DISPOSITIONS = frozenset(
    {
        "rewrite",
        "generator-regenerate",
        "immutable-audit",
        "retained-compatibility",
        "external",
        "application-boundary",
        "unresolved",
    }
)
_TERMINAL_JOURNAL_EVENTS = frozenset({"applied", "rolled_back", "recovered", "aborted_before_mutation"})
_SQLITE_SIDECAR_SUFFIXES = frozenset(
    {".db-shm", ".db-wal", ".sqlite-shm", ".sqlite-wal", ".sqlite3-shm", ".sqlite3-wal"}
)
_JOURNAL_SCHEMA_VERSION = 1
_TRANSACTION_DIRECTORY = RUNTIME_RELATIVE / "transactions"
_LOCK_RELATIVE = RUNTIME_RELATIVE / "apply.lock"


class MigrationError(RuntimeError):
    """Fail-closed migration error with a stable reason code."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class MappingRow:
    mapping_id: str
    category: str
    source: str
    destination: str


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    entry_id: str
    source: str
    canonical: str
    origin: str
    authority: str
    match_mode: str
    forms: tuple[str, ...]
    retain_source: bool
    candidate_only: bool = False


@dataclass(frozen=True, slots=True)
class AliasCandidate:
    candidate_id: str
    source: str
    canonical: str
    inference_basis: str
    authority: str


@dataclass(frozen=True, slots=True)
class ReferenceOccurrence:
    entry_id: str
    path: str
    location: str
    variant: str
    token: str
    classification: str
    disposition: str
    load_bearing: bool
    container: str = "filesystem"


@dataclass(frozen=True, slots=True)
class StructuredLocation:
    entry_id: str
    path: str
    format: str
    node_path: str
    value: str
    disposition: str


@dataclass(frozen=True, slots=True)
class PhysicalOccurrence:
    entry_id: str
    source_path: str
    canonical_path: str
    entry_type: str
    classification: str
    disposition: str
    tracking_state: str
    source_identity: str
    source_sha256: str | None
    destination_state: str
    destination_sha256: str | None
    collision: str | None
    operation_id: str | None


@dataclass(frozen=True, slots=True)
class PlannedOperation:
    operation_id: str
    operation_type: str
    target_class: str
    source: str | None
    target: str
    disposition: str
    owner: str
    precondition: str
    retain_source: bool


@dataclass(frozen=True, slots=True)
class PathIdentity:
    volume_serial: int
    file_id: str
    attributes: int
    reparse_tag: int
    final_path: str


class MappingMatcher:
    """Aho-Corasick basename prefilter for the 90 migration mappings."""

    def __init__(self, mappings: Sequence[MappingRow]):
        self.mappings = {item.mapping_id: item for item in mappings}
        self.transitions: list[dict[str, int]] = [{}]
        self.failures: list[int] = [0]
        self.outputs: list[set[str]] = [set()]
        for mapping in mappings:
            pattern = _nfc(PurePosixPath(mapping.source).name).casefold()
            state = 0
            for character in pattern:
                next_state = self.transitions[state].get(character)
                if next_state is None:
                    next_state = len(self.transitions)
                    self.transitions[state][character] = next_state
                    self.transitions.append({})
                    self.failures.append(0)
                    self.outputs.append(set())
                state = next_state
            self.outputs[state].add(mapping.mapping_id)
        queue: deque[int] = deque()
        for state in self.transitions[0].values():
            queue.append(state)
        while queue:
            state = queue.popleft()
            for character, child in self.transitions[state].items():
                queue.append(child)
                failure = self.failures[state]
                while failure and character not in self.transitions[failure]:
                    failure = self.failures[failure]
                self.failures[child] = self.transitions[failure].get(character, 0)
                self.outputs[child].update(self.outputs[self.failures[child]])

    def candidates(self, text: str) -> list[MappingRow]:
        normalized = _nfc(_normalize_regex_notation(text)).casefold()
        state = 0
        found: set[str] = set()
        for character in normalized:
            while state and character not in self.transitions[state]:
                state = self.failures[state]
            state = self.transitions[state].get(character, 0)
            found.update(self.outputs[state])
        return [self.mappings[mapping_id] for mapping_id in sorted(found)]


@dataclass(frozen=True, slots=True)
class ClassificationRule:
    rule_id: str
    pattern: str
    classification: str
    priority: int
    comparison: str
    mutable: bool


@dataclass(frozen=True, slots=True)
class DecodedText:
    text: str
    encoding: str
    bom: str
    newline: str
    final_newline: bool


@dataclass(frozen=True, slots=True)
class InventoryRecord:
    path: str
    entry_type: str
    classification: str
    rule_id: str
    comparison: str
    size: int
    mode: int
    sha256: str | None = None
    encoding: str | None = None
    error: str | None = None
    fixed_root: str | None = None
    mtime_ns: int = 0
    boundary_target: str | None = None


@dataclass(frozen=True, slots=True)
class WorktreeRecord:
    path: str
    fields: tuple[tuple[str, str | None], ...]
    location: str
    exists: bool


@dataclass(frozen=True, slots=True)
class ReferenceHit:
    mapping_id: str
    path: str
    variant: str
    line: int
    column: int
    token: str
    replacement: str | None
    classification: str
    load_bearing: bool
    disposition: str


@dataclass(frozen=True, slots=True)
class ProposedWrite:
    path: str
    preimage_sha256: str | None
    postimage_sha256: str
    preimage_payload: str | None
    payload: str
    mode: int
    reasons: tuple[str, ...]


@dataclass(slots=True)
class ScannedFile:
    path: str
    native_path: str
    record: InventoryRecord
    raw: bytes
    decoded: DecodedText | None


@dataclass(slots=True)
class Analysis:
    root: Path
    policy_path: Path
    policy: dict[str, Any]
    mappings: list[MappingRow]
    catalog: list[CatalogEntry]
    alias_candidates: list[AliasCandidate]
    inventory: list[InventoryRecord]
    inventory_entry_count: int
    closure_inventory: list[dict[str, Any]]
    worktrees: list[WorktreeRecord]
    files: dict[str, ScannedFile]
    hits: list[ReferenceHit]
    alias_occurrences: list[ReferenceOccurrence]
    structured_occurrences: list[StructuredLocation]
    physical_inventory: list[PhysicalOccurrence]
    operation_manifest: list[PlannedOperation]
    retained_sources: list[dict[str, Any]]
    expected_final_closure: dict[str, Any]
    reconciliations: list[dict[str, Any]]
    writes: list[ProposedWrite]
    generator_actions: list[dict[str, Any]]
    sqlite_hits: list[dict[str, Any]]
    exceptions: list[dict[str, Any]]
    blockers: list[dict[str, Any]]
    hashes: dict[str, str]
    plan_sha256: str = ""
    binding: dict[str, Any] = field(default_factory=dict)


def _nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _canonical_value(value: Any) -> Any:
    if isinstance(value, str):
        return _nfc(value)
    if isinstance(value, dict):
        return {str(key): _canonical_value(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, float):
        raise MigrationError("NON_CANONICAL_NUMBER", "Floating-point values are forbidden in canonical migration JSON")
    return value


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(_canonical_value(value), ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def stable_hash(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _relative_under(root: Path, raw: str) -> str:
    candidate = os.path.abspath(raw)
    root_abs = os.path.abspath(str(root))
    try:
        common = os.path.commonpath([root_abs, candidate])
    except ValueError as exc:
        raise MigrationError("PATH_OUTSIDE_ROOT", f"Path is on another volume: {raw}") from exc
    if os.path.normcase(common) != os.path.normcase(root_abs):
        raise MigrationError("PATH_OUTSIDE_ROOT", f"Path is outside project root: {raw}")
    relative = os.path.relpath(candidate, root_abs).replace("\\", "/")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or relative in {"", "."}:
        raise MigrationError("UNSAFE_RELATIVE_PATH", f"Unsafe repository path: {relative!r}")
    return _nfc(path.as_posix())


def _path_identity(path: str) -> str:
    return _nfc(path.replace("\\", "/")).casefold()


def load_policy(root: Path, policy_path: Path) -> tuple[Path, dict[str, Any]]:
    resolved = policy_path if policy_path.is_absolute() else root / policy_path
    try:
        payload = tomllib.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise MigrationError("POLICY_INVALID", f"Cannot load policy {resolved}: {exc}") from exc
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise MigrationError("POLICY_SCHEMA_INVALID", f"WI-5640 policy must use schema_version = {SCHEMA_VERSION}")
    if payload.get("main_bridge_id") != MAIN_BRIDGE_ID or payload.get("child_bridge_id") != CHILD_BRIDGE_ID:
        raise MigrationError(
            "POLICY_BRIDGE_DRIFT", "Policy bridge identifiers do not match the hard-coded authority boundary"
        )
    payload["_policy_relative_path"] = _relative_under(root, str(resolved))
    return resolved, payload


def load_manifest(root: Path, policy: dict[str, Any]) -> list[MappingRow]:
    manifest = root / str(policy.get("manifest_path") or "")
    try:
        with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
            raw_rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise MigrationError("MANIFEST_INVALID", f"Cannot read migration CSV {manifest}: {exc}") from exc
    if len(raw_rows) != 90:
        raise MigrationError("MANIFEST_ROW_COUNT", f"Expected 90 manifest rows, found {len(raw_rows)}")
    rows: list[MappingRow] = []
    source_ids: set[str] = set()
    destination_ids: set[str] = set()
    counts = {"hooks": 0, "rules": 0, "agent-control": 0}
    for index, raw in enumerate(raw_rows, start=1):
        source = _relative_under(
            root,
            os.path.join(str(raw.get("Current home directory:") or ""), str(raw.get("Current file name:") or "")),
        )
        destination = _relative_under(
            root,
            os.path.join(str(raw.get("New home directory:") or ""), str(raw.get("New file name:") or "")),
        )
        source_id = _path_identity(source)
        destination_id = _path_identity(destination)
        if source_id == destination_id:
            raise MigrationError("MANIFEST_NOOP", f"Manifest row {index} is a no-op: {source}")
        if source_id in source_ids or destination_id in destination_ids:
            raise MigrationError("MANIFEST_DUPLICATE", f"Manifest row {index} duplicates a source or destination")
        source_ids.add(source_id)
        destination_ids.add(destination_id)
        if source.startswith(".claude/hooks/"):
            category = "hooks"
        elif source.startswith(".claude/rules/"):
            category = "rules"
        elif source.startswith("config/agent-control/"):
            category = "agent-control"
        else:
            raise MigrationError("MANIFEST_CATEGORY", f"Manifest row {index} has an unsupported source: {source}")
        counts[category] += 1
        source_path = root / source
        destination_path = root / destination
        if not source_path.is_file():
            raise MigrationError("MANIFEST_SOURCE_MISSING", f"Manifest source is missing or not a file: {source}")
        if not destination_path.is_file():
            raise MigrationError("MANIFEST_DESTINATION_MISSING", f"Manifest destination is missing: {destination}")
        rows.append(MappingRow(f"M{index:03d}", category, source, destination))
    if counts != {"hooks": 33, "rules": 38, "agent-control": 19}:
        raise MigrationError("MANIFEST_CATEGORY_COUNTS", f"Unexpected manifest category counts: {counts}")
    collisions = source_ids & destination_ids
    if collisions:
        raise MigrationError("MANIFEST_CROSS_COLLISION", f"Source/destination identity collision: {sorted(collisions)}")
    for identities, label in ((source_ids, "source"), (destination_ids, "destination")):
        ordered = sorted(identities)
        for index, value in enumerate(ordered):
            if any(other.startswith(value + "/") for other in ordered[index + 1 :]):
                raise MigrationError(
                    "MANIFEST_PREFIX_COLLISION", f"Manifest {label} component-prefix collision: {value}"
                )
    return rows


def _catalog_path(value: Any, *, field_name: str) -> str:
    raw = _nfc(str(value or "").replace("\\", "/").strip("/"))
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts or raw != path.as_posix() or "\x00" in raw or ":" in raw:
        raise MigrationError("ALIAS_CATALOG_PATH_INVALID", f"Invalid {field_name}: {value!r}")
    return raw


def _catalog_collision_check(entries: Sequence[CatalogEntry]) -> None:
    by_source: dict[str, CatalogEntry] = {}
    by_destination: dict[str, CatalogEntry] = {}
    for entry in entries:
        source_id = _path_identity(entry.source)
        destination_id = _path_identity(entry.canonical)
        prior_source = by_source.get(source_id)
        if prior_source and _path_identity(prior_source.canonical) != destination_id:
            raise MigrationError(
                "ALIAS_SOURCE_MULTI_TARGET",
                f"Catalog source {entry.source!r} maps to both {prior_source.canonical!r} and {entry.canonical!r}",
            )
        prior_destination = by_destination.get(destination_id)
        if prior_destination and _path_identity(prior_destination.source) != source_id:
            raise MigrationError(
                "ALIAS_DESTINATION_COLLISION",
                f"Catalog destination {entry.canonical!r} has multiple casefold/NFC sources",
            )
        by_source[source_id] = entry
        by_destination[destination_id] = entry
    ordered = sorted(by_source)
    for index, source in enumerate(ordered):
        for other in ordered[index + 1 :]:
            if other.startswith(source + "/"):
                shorter = by_source[source]
                longer = by_source[other]
                if shorter.match_mode != "longest-path-components" and longer.match_mode != "longest-path-components":
                    raise MigrationError(
                        "ALIAS_PREFIX_AMBIGUITY",
                        f"Overlapping catalog sources require explicit longest-match precedence: "
                        f"{shorter.source!r}, {longer.source!r}",
                    )


def _skill_alias_candidates(root: Path, explicit_sources: set[str]) -> list[AliasCandidate]:
    registry_path = root / "config/agent-control/gtkb-harness-capability-registry.toml"
    rename_path = root / "config/agent-control/skill-rename-map.toml"
    try:
        registry = tomllib.loads(registry_path.read_text(encoding="utf-8"))
        rename_map = tomllib.loads(rename_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise MigrationError("ALIAS_INFERENCE_AUTHORITY_INVALID", str(exc)) from exc
    renamed = {
        str(item.get("canonical_name") or "")
        for item in rename_map.get("skills", [])
        if isinstance(item, dict) and str(item.get("canonical_name") or "").startswith("gtkb-")
    }
    candidates: list[AliasCandidate] = []
    for capability in registry.get("capabilities", []):
        if not isinstance(capability, dict) or capability.get("kind") != "skill":
            continue
        canonical_source = str(capability.get("canonical_source") or "").replace("\\", "/")
        parts = PurePosixPath(canonical_source).parts
        if len(parts) < 4 or parts[:2] != (".claude", "skills") or not parts[2].startswith("gtkb-"):
            continue
        canonical_name = parts[2]
        if canonical_name not in renamed:
            continue
        old_name = canonical_name.removeprefix("gtkb-")
        source = f".claude/skills/{old_name}"
        canonical = f".claude/skills/{canonical_name}"
        if _path_identity(source) in explicit_sources or (root / source).exists() or not (root / canonical).is_dir():
            continue
        candidates.append(
            AliasCandidate(
                candidate_id=f"CAND-{canonical_name.upper().replace('-', '_')}",
                source=source,
                canonical=canonical,
                inference_basis=(
                    "canonical skill registry + governed rename metadata + absent non-prefixed directory + "
                    "present gtkb-prefixed directory"
                ),
                authority="candidate-only",
            )
        )
    return sorted(candidates, key=lambda item: _path_identity(item.source))


def load_obsolete_catalog(
    root: Path,
    policy: dict[str, Any],
    mappings: Sequence[MappingRow],
) -> tuple[list[CatalogEntry], list[AliasCandidate]]:
    alias_policy = policy.get("alias_catalog")
    if not isinstance(alias_policy, dict):
        raise MigrationError("ALIAS_CATALOG_POLICY_MISSING", "Policy has no [alias_catalog] table")
    dispositions = {str(item) for item in alias_policy.get("required_dispositions", [])}
    if dispositions != _REQUIRED_ALIAS_DISPOSITIONS:
        raise MigrationError("ALIAS_DISPOSITION_POLICY_DRIFT", "Alias disposition vocabulary is incomplete or drifted")
    entries = [
        CatalogEntry(
            entry_id=row.mapping_id,
            source=row.source,
            canonical=row.destination,
            origin="csv-manifest",
            authority="rewrite",
            match_mode="longest-path-components",
            forms=("direct", "absolute", "uri", "relative", "segmented", "glob", "regex", "sqlite"),
            retain_source=True,
        )
        for row in mappings
    ]
    explicit_ids: set[str] = set()
    for index, raw in enumerate(policy.get("obsolete_aliases", []), start=1):
        if not isinstance(raw, dict):
            raise MigrationError("ALIAS_CATALOG_ROW_INVALID", f"obsolete_aliases row {index} is not a table")
        entry_id = str(raw.get("id") or "")
        if not re.fullmatch(r"A\d{3}(?:-[A-Z0-9]+)?", entry_id) or entry_id in explicit_ids:
            raise MigrationError("ALIAS_CATALOG_ID_INVALID", f"Invalid or duplicate alias id: {entry_id!r}")
        explicit_ids.add(entry_id)
        authority = str(raw.get("authority") or "")
        if authority not in {"rewrite", "candidate-only", "retained-compatibility"}:
            raise MigrationError("ALIAS_AUTHORITY_INVALID", f"Alias {entry_id} has invalid authority {authority!r}")
        forms = tuple(sorted({str(item) for item in raw.get("forms", [])}))
        if not forms or not set(forms) <= {
            "absolute",
            "direct",
            "glob",
            "regex",
            "relative",
            "segmented",
            "sqlite",
            "structured",
            "uri",
        }:
            raise MigrationError("ALIAS_FORMS_INVALID", f"Alias {entry_id} has invalid forms")
        entries.append(
            CatalogEntry(
                entry_id=entry_id,
                source=_catalog_path(raw.get("source"), field_name=f"{entry_id}.source"),
                canonical=_catalog_path(raw.get("canonical"), field_name=f"{entry_id}.canonical"),
                origin=str(raw.get("origin") or "explicit-reviewed"),
                authority=authority,
                match_mode=str(raw.get("match_mode") or "longest-path-components"),
                forms=forms,
                retain_source=bool(raw.get("retain_source", True)),
                candidate_only=authority == "candidate-only",
            )
        )
    explicit_sources = {_path_identity(item.source) for item in entries}
    candidates = _skill_alias_candidates(root, explicit_sources)
    entries.extend(
        CatalogEntry(
            entry_id=item.candidate_id,
            source=item.source,
            canonical=item.canonical,
            origin="inferred-skill-prefix",
            authority="candidate-only",
            match_mode="longest-path-components",
            forms=("direct", "absolute", "uri", "relative", "segmented", "structured", "glob", "regex", "sqlite"),
            retain_source=True,
            candidate_only=True,
        )
        for item in candidates
    )
    _catalog_collision_check(entries)
    return sorted(entries, key=lambda item: (_path_identity(item.source), item.entry_id)), candidates


def classification_rules(policy: dict[str, Any]) -> list[ClassificationRule]:
    rules: list[ClassificationRule] = []
    for index, raw in enumerate(policy.get("classification_rules", []), start=1):
        try:
            rule = ClassificationRule(
                rule_id=str(raw["id"]),
                pattern=str(raw["pattern"]).replace("\\", "/"),
                classification=str(raw["class"]),
                priority=int(raw["priority"]),
                comparison=str(raw["comparison"]),
                mutable=bool(raw["mutable"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise MigrationError("CLASSIFICATION_POLICY_INVALID", f"Invalid classification row {index}") from exc
        rules.append(rule)
    if not rules:
        raise MigrationError("CLASSIFICATION_POLICY_EMPTY", "No classification rules are declared")
    return sorted(rules, key=lambda item: (-item.priority, item.rule_id))


def validate_policy_contract(policy: dict[str, Any], mappings: list[MappingRow]) -> None:
    scan_policy = policy.get("scan", {})
    if not isinstance(scan_policy, dict) or scan_policy.get("inventory_excluded_children", True) is not True:
        raise MigrationError(
            "FULL_ROOT_INVENTORY_DISABLED",
            "scan.inventory_excluded_children must be true so excluded-root descendants remain observable",
        )
    if policy.get("test_fixture") is not True and scan_policy.get("inventory_mode") != "artifact-registry":
        raise MigrationError(
            "SOT_INVENTORY_MODE_REQUIRED",
            "Production migration inventory must be derived from the registered artifact universe",
        )
    by_id = {row.mapping_id: row for row in mappings}
    rule_rows = policy.get("rule_projections", [])
    expected_rules = {(row.source, row.destination) for row in mappings if row.category == "rules"}
    declared_rules = {
        (str(row.get("source") or ""), str(row.get("canonical") or "")) for row in rule_rows if isinstance(row, dict)
    }
    if len(rule_rows) != 38 or declared_rules != expected_rules:
        raise MigrationError(
            "RULE_PROJECTION_POLICY_DRIFT", "Rule projection ledger does not equal the 38 manifest rule rows"
        )
    reconciliation = policy.get("content_reconciliation", [])
    if len(reconciliation) != 25:
        raise MigrationError(
            "CONTENT_RECONCILIATION_POLICY_DRIFT", "Policy must declare all 25 baseline byte divergences"
        )
    seen: set[str] = set()
    for item in reconciliation:
        mapping_id = str(item.get("mapping_id") or "")
        mapping = by_id.get(mapping_id)
        if mapping is None or mapping_id in seen:
            raise MigrationError("CONTENT_RECONCILIATION_POLICY_DRIFT", f"Invalid content row: {mapping_id!r}")
        seen.add(mapping_id)
        if item.get("source") != mapping.source or item.get("destination") != mapping.destination:
            raise MigrationError("CONTENT_RECONCILIATION_POLICY_DRIFT", f"Content row path drift: {mapping_id}")
        allowed_authorities = {
            "transformed_source",
            "transformed_source_with_known_adaptation",
            "transformed_source_with_manual_policy",
            "clean_source_all_manifest_transforms",
        }
        if item.get("authority") not in allowed_authorities or item.get("divergence") not in {
            "newline_only",
            "substantive",
        }:
            raise MigrationError("CONTENT_RECONCILIATION_POLICY_DRIFT", f"Invalid authority row: {mapping_id}")
    required_generators = {
        "codex-skills",
        "antigravity-skills",
        "api-skills",
        "goose-api-skills",
        "goose-manifest",
        "cursor-skills",
        "rule-compatibility",
        "harness-parity",
    }
    declared_generators = {
        str(item.get("id") or "") for item in policy.get("generator_checks", []) if isinstance(item, dict)
    }
    if declared_generators != required_generators:
        raise MigrationError("GENERATOR_POLICY_DRIFT", "Generator check ledger is incomplete or contains unknown rows")
    if policy.get("test_fixture") is not True:
        aliases = policy.get("obsolete_aliases", [])
        physical = policy.get("physical_alias_roots", [])
        if len(aliases) != 6 or len(physical) != 2:
            raise MigrationError(
                "ALIAS_POLICY_PROOF_CASE_MISSING",
                "Policy must declare six harness aliases and two physical roots",
            )
        baseline = policy.get("allowed_baseline_failures", {})
        cross = baseline.get("cross_harness", {}) if isinstance(baseline, dict) else {}
        cross_nodes = [str(item) for item in cross.get("node_ids", [])]
        if (
            len(cross_nodes) != 6
            or cross.get("head") != "ef6ba79c7527190606e41267bd45e6732c405e43"
            or cross.get("collected_node_count") != 209
            or cross.get("required_identical_runs") != 3
        ):
            raise MigrationError(
                "CROSS_HARNESS_BASELINE_POLICY_DRIFT",
                "Cross-harness frozen no-regression baseline drifted",
            )
        if "governance" in baseline:
            raise MigrationError(
                "GOVERNANCE_BASELINE_POLICY_DRIFT",
                "The obsolete WI-5648 governance failure allowance must not be present",
            )
        expected_governance_nodes = {
            "platform_tests/scripts/test_implementation_start_gate.py::test_work_intent_acquire_denial_creates_no_claim",
            "platform_tests/scripts/test_implementation_start_gate.py::test_work_intent_extension_denial_leaves_claim_unchanged",
            "platform_tests/scripts/test_implementation_start_gate.py::test_work_intent_reclassify_denial_leaves_draft_claim_unchanged",
            "platform_tests/scripts/test_implementation_start_gate.py::test_work_intent_renew_denial_leaves_go_claim_unchanged",
        }
        residuals = policy.get("observed_residual_failures", {})
        governance = residuals.get("governance", {}) if isinstance(residuals, dict) else {}
        governance_nodes = sorted(str(item) for item in governance.get("node_ids", []))
        governance_hash = "sha256:" + hashlib.sha256(("\n".join(governance_nodes) + "\n").encode("utf-8")).hexdigest()
        if (
            set(governance_nodes) != expected_governance_nodes
            or governance.get("node_list_lf_sha256") != governance_hash
            or governance.get("owner_work_item") != "WI-5178"
            or governance.get("owner_project") != "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS"
            or governance.get("observed_collected_node_count") != 475
            or governance.get("passing_node_count") != 471
            or governance.get("failing_node_count") != 4
            or governance.get("allowed_for_stage_b") is not False
            or governance.get("stage_b_requires_all_pass") is not True
        ):
            raise MigrationError(
                "GOVERNANCE_RESIDUAL_EVIDENCE_DRIFT",
                "The non-waiving WI-5178 residual evidence drifted",
            )
    retention = policy.get("retention", {})
    if (
        retention.get("retain_all_old_paths") is not True
        or retention.get("inert_source_count") != 52
        or retention.get("native_rule_projection_count") != 38
        or any(
            retention.get(key) is not False for key in ("allow_delete", "allow_move", "allow_rename", "allow_unlink")
        )
    ):
        raise MigrationError("RETENTION_POLICY_DRIFT", "Old-source retention policy is incomplete")
    mutation = policy.get("mutation", {})
    if not mutation.get("mutable_roots") or not isinstance(mutation.get("root_file_allowlist"), list):
        raise MigrationError("MUTATION_POLICY_DRIFT", "Mutation roots and root-file allowlist must be explicit")
    by_source = {str(row.get("source") or ""): row for row in rule_rows if isinstance(row, dict)}
    for source in (
        ".claude/rules/codex-loyal-opposition-runbook.md",
        ".claude/rules/codex-review-operating-contract.md",
    ):
        if source not in by_source:
            continue
        load_policy = str(by_source[source].get("load_policy") or "")
        if "exclude:build" not in load_policy:
            raise MigrationError("BUILD_ENVELOPE_POLICY_DRIFT", f"{source} must be excluded from build")


def write_path_allowed(policy: dict[str, Any], path: str) -> bool:
    mutation = policy.get("mutation", {})
    identity = _path_identity(path)
    for forbidden in mutation.get("forbidden_roots", []):
        forbidden_key = _path_identity(str(forbidden)).rstrip("/")
        if identity == forbidden_key or identity.startswith(forbidden_key + "/"):
            return False
    if "/" not in path:
        return path in {str(item) for item in mutation.get("root_file_allowlist", [])}
    for root in mutation.get("mutable_roots", []):
        root_key = _path_identity(str(root)).rstrip("/")
        if identity == root_key or identity.startswith(root_key + "/"):
            return True
    return False


def _pattern_matches(path: str, pattern: str) -> bool:
    path_key = _path_identity(path)
    pattern_key = _path_identity(pattern)
    candidates = [pattern_key]
    while candidates[-1].startswith("**/"):
        candidates.append(candidates[-1][3:])
    for candidate in candidates:
        if candidate.endswith("/**"):
            root_pattern = candidate[:-3].rstrip("/")
            if path_key == root_pattern or fnmatch.fnmatchcase(path_key, root_pattern):
                return True
        if fnmatch.fnmatchcase(path_key, candidate):
            return True
    return False


def _fixed_root(path: str, pattern: str) -> str:
    pattern_parts = PurePosixPath(pattern).parts
    path_parts = PurePosixPath(path).parts
    if "**" in pattern_parts:
        wildcard_index = pattern_parts.index("**")
        if wildcard_index:
            prefix = pattern_parts[:wildcard_index]
            if len(path_parts) >= len(prefix) and all(
                fnmatch.fnmatchcase(path_parts[index].casefold(), component.casefold())
                for index, component in enumerate(prefix)
            ):
                return PurePosixPath(*path_parts[:wildcard_index]).as_posix()
        suffix = [component for component in pattern_parts[wildcard_index + 1 :] if component != "**"]
        if suffix:
            for start in range(len(path_parts) - len(suffix) + 1):
                if all(
                    fnmatch.fnmatchcase(path_parts[start + index].casefold(), component.casefold())
                    for index, component in enumerate(suffix)
                ):
                    return PurePosixPath(*path_parts[: start + len(suffix)]).as_posix()
    elif len(path_parts) >= len(pattern_parts) and all(
        fnmatch.fnmatchcase(path_parts[index].casefold(), component.casefold())
        for index, component in enumerate(pattern_parts)
    ):
        return PurePosixPath(*path_parts[: len(pattern_parts)]).as_posix()
    return path


def _policy_classification(path: str, rules: list[ClassificationRule]) -> tuple[ClassificationRule | None, str | None]:
    matches = [rule for rule in rules if _pattern_matches(path, rule.pattern)]
    if not matches:
        return None, None
    top = matches[0]
    peers = [rule for rule in matches if rule.priority == top.priority and rule.rule_id != top.rule_id]
    incompatible = [
        rule
        for rule in peers
        if (rule.classification, rule.comparison, rule.mutable) != (top.classification, top.comparison, top.mutable)
    ]
    if incompatible:
        return None, "multiple classification rules at the same priority: " + ", ".join(
            [top.rule_id, *[p.rule_id for p in peers]]
        )
    return top, None


def _native_path(path: str | Path) -> str:
    absolute = os.path.abspath(str(path))
    if os.name != "nt" or absolute.startswith("\\\\?\\"):
        return absolute
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def decode_text(data: bytes, path: str, legacy_encodings: Sequence[str]) -> DecodedText | None:
    bom = "none"
    encoding: str | None = None
    payload = data
    if data.startswith(b"\xef\xbb\xbf"):
        bom, encoding, payload = "utf-8", "utf-8", data[3:]
    elif data.startswith(b"\xff\xfe"):
        bom, encoding, payload = "utf-16-le", "utf-16-le", data[2:]
    elif data.startswith(b"\xfe\xff"):
        bom, encoding, payload = "utf-16-be", "utf-16-be", data[2:]
    suffix = Path(path).suffix.casefold()
    text_name = Path(path).name.casefold()
    text_candidate = suffix in _TEXT_SUFFIXES or text_name in {
        ".dockerignore",
        ".editorconfig",
        ".env",
        ".gitattributes",
        ".gitignore",
        "dockerfile",
        "license",
        "makefile",
        "notice",
    }
    if encoding is None and b"\x00" in data:
        return None
    if encoding is None and path.casefold().endswith((".py", ".pyi")):
        try:
            encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
        except (SyntaxError, UnicodeError):
            encoding = None
    if encoding is None and not text_candidate:
        return None
    candidates = [encoding] if encoding else ["utf-8"]
    if text_candidate:
        candidates.extend(item for item in legacy_encodings if item not in candidates)
    text: str | None = None
    selected: str | None = None
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            text = payload.decode(candidate, errors="strict")
            selected = candidate
            break
        except (LookupError, UnicodeDecodeError):
            continue
    if text is None or selected is None:
        return None
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    cr = text.count("\r") - crlf
    if sum(value > 0 for value in (crlf, lf, cr)) > 1:
        newline = "mixed"
    elif crlf:
        newline = "CRLF"
    elif lf:
        newline = "LF"
    elif cr:
        newline = "CR"
    else:
        newline = "none"
    return DecodedText(text, selected, bom, newline, text.endswith(("\n", "\r")))


def encode_text(decoded: DecodedText, text: str) -> bytes:
    prefix = {"none": b"", "utf-8": b"\xef\xbb\xbf", "utf-16-le": b"\xff\xfe", "utf-16-be": b"\xfe\xff"}[decoded.bom]
    return prefix + text.encode(decoded.encoding, errors="strict")


def binary_reference_candidates(data: bytes, mappings: Sequence[MappingRow]) -> list[str]:
    """Detect manifest tokens in undecoded files so they cannot be silently skipped."""
    lowered = data.lower()
    found: list[str] = []
    for mapping in mappings:
        source = mapping.source.casefold()
        basename = PurePosixPath(mapping.source).name.casefold()
        forms = {
            source.encode("utf-8"),
            source.replace("/", "\\").encode("utf-8"),
            basename.encode("utf-8"),
            source.encode("utf-16-le"),
            source.encode("utf-16-be"),
            basename.encode("utf-16-le"),
            basename.encode("utf-16-be"),
        }
        if any(form and form in lowered for form in forms):
            found.append(mapping.mapping_id)
    return found


def git_worktrees(root: Path) -> tuple[list[WorktreeRecord], bytes]:
    process = subprocess.run(
        ["git", "-C", str(root), "worktree", "list", "--porcelain", "-z"],
        check=False,
        capture_output=True,
    )
    if process.returncode != 0:
        raise MigrationError(
            "GIT_WORKTREE_ENUMERATION_FAILED",
            process.stderr.decode("utf-8", errors="replace").strip() or "git worktree list failed",
        )
    records: list[WorktreeRecord] = []
    fields: list[tuple[str, str | None]] = []
    for token in process.stdout.split(b"\0"):
        if not token:
            if fields:
                records.append(_worktree_record(root, fields))
                fields = []
            continue
        decoded = token.decode("utf-8", errors="surrogateescape")
        key, separator, value = decoded.partition(" ")
        fields.append((key, value if separator else None))
    if fields:
        records.append(_worktree_record(root, fields))
    return sorted(records, key=lambda item: _path_identity(item.path)), process.stdout


def _worktree_record(root: Path, fields: list[tuple[str, str | None]]) -> WorktreeRecord:
    raw_path = next((value for key, value in fields if key == "worktree" and value), "")
    absolute = os.path.abspath(raw_path)
    root_abs = os.path.abspath(str(root))
    try:
        common = os.path.commonpath([root_abs, absolute])
        in_root = os.path.normcase(common) == os.path.normcase(root_abs)
    except ValueError:
        in_root = False
    if os.path.normcase(absolute) == os.path.normcase(root_abs):
        location = "main"
    elif in_root:
        location = "in_root"
    else:
        location = "external"
    return WorktreeRecord(
        _nfc(absolute.replace("\\", "/")), tuple(fields), location, os.path.exists(_native_path(absolute))
    )


def git_index_hash(root: Path) -> str:
    process = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        check=False,
        capture_output=True,
    )
    if process.returncode != 0:
        raise MigrationError("GIT_INDEX_ENUMERATION_FAILED", process.stderr.decode("utf-8", errors="replace").strip())
    return sha256_bytes(process.stdout)


def _builtin_classification(
    path: str,
    entry_type: str,
    mappings_by_source: dict[str, MappingRow],
    mappings_by_destination: dict[str, MappingRow],
    input_authorities: set[str],
) -> tuple[str, str, str]:
    key = _path_identity(path)
    if key in input_authorities:
        return "input_authority", "builtin-input-authority", "full"
    if key in mappings_by_source:
        mapping = mappings_by_source[key]
        if mapping.category == "rules":
            return "native_compatibility_projection", "manifest-rule-projection", "full"
        return "retained_obsolete_source", "manifest-source", "full"
    if key in mappings_by_destination:
        return "canonical_destination", "manifest-destination", "full"
    if entry_type == "file" and PurePosixPath(path).suffix.casefold() in _SQLITE_SIDECAR_SUFFIXES:
        return "runtime_non_authoritative", "builtin-sqlite-sidecar", "full"
    if any(path.casefold().startswith(prefix.casefold()) for prefix in _GENERATED_PREFIXES):
        return "generated_text", "generated-projection", "full"
    if entry_type == "reparse_point":
        return "reparse_point", "builtin-reparse", "fixed_root"
    if entry_type == "directory":
        return "directory", "builtin-directory", "full"
    return "mutable_candidate", "builtin-root-member", "full"


def walk_inventory(
    root: Path,
    policy: dict[str, Any],
    mappings: list[MappingRow],
    worktrees: list[WorktreeRecord],
) -> tuple[list[InventoryRecord], list[dict[str, Any]], dict[str, ScannedFile], list[dict[str, Any]], str, int]:
    rules = classification_rules(policy)
    source_map = {_path_identity(row.source): row for row in mappings}
    destination_map = {_path_identity(row.destination): row for row in mappings}
    input_authorities = {
        _path_identity(str(policy.get("manifest_path") or "")),
        _path_identity(str(policy.get("_policy_relative_path") or "")),
    }
    nested_worktrees = {
        _path_identity(_relative_under(root, item.path))
        for item in worktrees
        if item.location == "in_root" and item.exists
    }
    legacy = [str(item) for item in policy.get("scan", {}).get("legacy_encodings", [])]
    max_inline = int(policy.get("scan", {}).get("max_inline_text_bytes", 64 * 1024 * 1024))
    inventory_mode = str(policy.get("scan", {}).get("inventory_mode") or "filesystem")
    if inventory_mode not in {"artifact-registry", "filesystem"}:
        raise MigrationError("INVENTORY_MODE_INVALID", f"Unsupported inventory mode: {inventory_mode}")
    authoritative_files: set[str] = set()
    registry_findings: list[dict[str, Any]] = []
    if inventory_mode == "artifact-registry":
        authoritative_files, registry_findings = registered_artifact_paths(root)
    authoritative_file_ids = {_path_identity(item) for item in authoritative_files}
    authoritative_directory_ids: set[str] = set()
    for relative in authoritative_files:
        parent = PurePosixPath(relative).parent
        while parent.as_posix() not in {"", "."}:
            authoritative_directory_ids.add(_path_identity(parent.as_posix()))
            parent = parent.parent
    retain_observed_records = bool(policy.get("scan", {}).get("retain_observed_records", False))
    records: list[InventoryRecord] = []
    observed_records: list[InventoryRecord] = []
    fixed_records: dict[str, InventoryRecord] = {}
    files: dict[str, ScannedFile] = {}
    blockers: list[dict[str, Any]] = []
    blockers.extend(registry_findings)
    if inventory_mode == "artifact-registry":
        for mapping in mappings:
            if _path_identity(mapping.destination) not in authoritative_file_ids:
                blockers.append(
                    {
                        "code": "MANIFEST_DESTINATION_UNREGISTERED",
                        "mapping_id": mapping.mapping_id,
                        "path": mapping.destination,
                    }
                )
    observation_path = root / _FULL_OBSERVATION_RELATIVE
    observation_path.parent.mkdir(parents=True, exist_ok=True)
    observation_temp = observation_path.with_name(f"{observation_path.name}.tmp-{os.getpid()}")
    observation_handle = observation_temp.open("xb")
    observation_hash = hashlib.sha256()
    observation_count = 0
    observation_bytes = 0
    observation_errors = 0
    observation_classes: dict[str, dict[str, int]] = {}
    observed_path_ids: set[str] = set()

    def emit(record: InventoryRecord) -> None:
        nonlocal observation_count, observation_bytes, observation_errors
        line = canonical_bytes(asdict(record))
        observation_handle.write(line)
        observation_hash.update(line)
        observation_count += 1
        observation_bytes += record.size if record.entry_type == "file" else 0
        observation_errors += int(record.error is not None)
        observed_path_ids.add(_path_identity(record.path))
        class_summary = observation_classes.setdefault(
            record.classification, {"entries": 0, "files": 0, "bytes": 0, "errors": 0}
        )
        class_summary["entries"] += 1
        class_summary["files"] += int(record.entry_type == "file")
        class_summary["bytes"] += record.size if record.entry_type == "file" else 0
        class_summary["errors"] += int(record.error is not None)
        if retain_observed_records or not record.fixed_root or record.path == record.fixed_root:
            observed_records.append(record)
        if record.fixed_root:
            key = _path_identity(record.fixed_root)
            fixed_records.setdefault(
                key,
                InventoryRecord(
                    record.fixed_root,
                    "excluded_root",
                    record.classification,
                    record.rule_id,
                    "fixed_root",
                    0,
                    0,
                    fixed_root=record.fixed_root,
                    boundary_target=record.boundary_target,
                ),
            )
        else:
            records.append(record)

    for worktree in worktrees:
        line = canonical_bytes({"record_type": "registered_worktree", **asdict(worktree)})
        observation_handle.write(line)
        observation_hash.update(line)
    stack: list[tuple[str, str]] = [(_native_path(root), "")]
    while stack:
        native_dir, relative_dir = stack.pop()
        try:
            entries = sorted(os.scandir(native_dir), key=lambda item: _path_identity(item.name), reverse=True)
        except OSError as exc:
            path = relative_dir or "."
            record = InventoryRecord(
                path, "unreadable", "unreadable", "io-error", "full", 0, 0, error=f"{type(exc).__name__}: {exc}"
            )
            emit(record)
            blockers.append({"code": "UNREADABLE_DIRECTORY", "path": path, "detail": record.error})
            continue
        for entry in entries:
            relative = f"{relative_dir}/{entry.name}".strip("/").replace("\\", "/")
            relative_id = _path_identity(relative)
            if (
                inventory_mode == "artifact-registry"
                and relative_id not in authoritative_file_ids
                and relative_id not in authoritative_directory_ids
            ):
                continue
            if _path_identity(relative) == _path_identity(_FULL_OBSERVATION_RELATIVE.as_posix()) or _path_identity(
                relative
            ).startswith(_path_identity(_FULL_OBSERVATION_RELATIVE.as_posix()) + ".tmp-"):
                continue
            try:
                info = entry.stat(follow_symlinks=False)
                attributes = int(getattr(info, "st_file_attributes", 0))
                is_reparse = entry.is_symlink() or bool(
                    attributes & int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
                )
                boundary_target = None
                if is_reparse:
                    entry_type = "reparse_point"
                    try:
                        boundary_target = _nfc(os.readlink(entry.path).replace("\\", "/"))
                    except OSError:
                        boundary_target = "unreadable-target"
                elif stat.S_ISDIR(info.st_mode):
                    entry_type = "directory"
                elif stat.S_ISREG(info.st_mode):
                    entry_type = "file"
                else:
                    entry_type = "other"
            except OSError as exc:
                record = InventoryRecord(
                    relative, "unreadable", "unreadable", "io-error", "full", 0, 0, error=f"{type(exc).__name__}: {exc}"
                )
                emit(record)
                blockers.append({"code": "UNREADABLE_ENTRY", "path": relative, "detail": record.error})
                continue
            builtin_class, builtin_rule, builtin_comparison = _builtin_classification(
                relative, entry_type, source_map, destination_map, input_authorities
            )
            registered_worktree = _path_identity(relative) in nested_worktrees
            if registered_worktree:
                builtin_class, builtin_rule, builtin_comparison = (
                    "separate_worktree",
                    "registered-worktree-boundary",
                    "fixed_root",
                )
            exact_manifest_member = builtin_rule in {
                "manifest-source",
                "manifest-rule-projection",
                "manifest-destination",
            }
            policy_rule, classification_error = (
                (None, None)
                if exact_manifest_member or registered_worktree
                else _policy_classification(relative, rules)
            )
            if classification_error:
                record = InventoryRecord(
                    relative,
                    entry_type,
                    "unclassified",
                    "classification-conflict",
                    "full",
                    info.st_size,
                    stat.S_IMODE(info.st_mode),
                    error=classification_error,
                )
                emit(record)
                blockers.append({"code": "MULTIPLY_CLASSIFIED", "path": relative, "detail": classification_error})
                continue
            if policy_rule:
                classification = policy_rule.classification
                rule_id = policy_rule.rule_id
                comparison = policy_rule.comparison
            else:
                classification, rule_id, comparison = builtin_class, builtin_rule, builtin_comparison
            fixed_root = None
            if comparison == "fixed_root":
                fixed_root = _fixed_root(relative, policy_rule.pattern) if policy_rule else relative
            mode = stat.S_IMODE(info.st_mode)
            if entry_type == "directory":
                emit(
                    InventoryRecord(
                        relative,
                        entry_type,
                        classification,
                        rule_id,
                        comparison,
                        info.st_size,
                        mode,
                        fixed_root=fixed_root,
                        mtime_ns=info.st_mtime_ns,
                        boundary_target=boundary_target,
                    )
                )
                if (
                    relative_id not in nested_worktrees
                    and not is_reparse
                    and (inventory_mode != "artifact-registry" or relative_id in authoritative_directory_ids)
                ):
                    stack.append((entry.path, relative))
                continue
            if entry_type != "file":
                emit(
                    InventoryRecord(
                        relative,
                        entry_type,
                        classification,
                        rule_id,
                        comparison,
                        info.st_size,
                        mode,
                        fixed_root=fixed_root,
                        mtime_ns=info.st_mtime_ns,
                        boundary_target=boundary_target,
                    )
                )
                continue
            should_read = (
                exact_manifest_member
                or (
                    comparison != "fixed_root"
                    and classification not in {"immutable_audit", "runtime_non_authoritative", "separate_worktree"}
                )
            ) and info.st_size <= max_inline
            if not should_read:
                emit(
                    InventoryRecord(
                        relative,
                        entry_type,
                        classification,
                        rule_id,
                        comparison,
                        info.st_size,
                        mode,
                        fixed_root=fixed_root,
                        mtime_ns=info.st_mtime_ns,
                        boundary_target=boundary_target,
                    )
                )
                if info.st_size > max_inline and comparison != "fixed_root" and classification != "structured_sqlite":
                    blockers.append({"code": "LIVE_FILE_TOO_LARGE", "path": relative, "detail": str(info.st_size)})
                continue
            try:
                with open(entry.path, "rb") as handle:
                    descriptor_before = os.fstat(handle.fileno())
                    raw = handle.read()
                    descriptor_after = os.fstat(handle.fileno())
            except OSError as exc:
                record = InventoryRecord(
                    relative,
                    "unreadable",
                    "unreadable",
                    "io-error",
                    "full",
                    info.st_size,
                    mode,
                    error=f"{type(exc).__name__}: {exc}",
                    fixed_root=fixed_root,
                )
                emit(record)
                blockers.append({"code": "UNREADABLE_FILE", "path": relative, "detail": record.error})
                continue
            if (
                descriptor_before.st_size != descriptor_after.st_size
                or descriptor_before.st_mtime_ns != descriptor_after.st_mtime_ns
                or descriptor_before.st_ino != descriptor_after.st_ino
            ):
                blockers.append({"code": "FILE_CHANGED_DURING_READ", "path": relative})
            decoded = None if classification == "structured_sqlite" else decode_text(raw, relative, legacy)
            effective = classification
            if classification == "mutable_candidate":
                effective = "mutable_text" if decoded else "binary"
                if decoded is None:
                    for mapping_id in binary_reference_candidates(raw, mappings):
                        blockers.append(
                            {
                                "code": "UNDECODED_REFERENCE_BYTES",
                                "path": relative,
                                "mapping_id": mapping_id,
                            }
                        )
            record = InventoryRecord(
                relative,
                entry_type,
                effective,
                rule_id,
                comparison,
                len(raw),
                mode,
                sha256=sha256_bytes(raw),
                encoding=decoded.encoding if decoded else None,
                fixed_root=fixed_root,
                mtime_ns=info.st_mtime_ns,
                boundary_target=boundary_target,
            )
            emit(record)
            if decoded is not None or exact_manifest_member:
                files[relative] = ScannedFile(relative, entry.path, record, raw, decoded)
    observation_handle.flush()
    os.fsync(observation_handle.fileno())
    observation_handle.close()
    observation_sha = "sha256:" + observation_hash.hexdigest()
    os.replace(observation_temp, observation_path)
    observation_summary = {
        "schema_version": SCHEMA_VERSION,
        "entries": observation_count,
        "files": sum(item["files"] for item in observation_classes.values()),
        "bytes": observation_bytes,
        "errors": observation_errors,
        "classifications": {key: observation_classes[key] for key in sorted(observation_classes, key=str.casefold)},
        "full_observation_sha256": observation_sha,
    }
    _atomic_write_bytes(root / _FULL_OBSERVATION_SUMMARY_RELATIVE, canonical_bytes(observation_summary))
    if inventory_mode == "artifact-registry":
        for missing in sorted(authoritative_file_ids - observed_path_ids):
            blockers.append({"code": "REGISTERED_ARTIFACT_MISSING", "path": missing})
    records.extend(fixed_records.values())
    records.sort(key=lambda item: _path_identity(item.path))
    closure: list[dict[str, Any]] = []
    emitted_roots: set[str] = set()
    for record in records:
        if record.classification == "runtime_non_authoritative" and not record.fixed_root:
            continue
        if record.fixed_root:
            key = _path_identity(record.fixed_root)
            if key not in emitted_roots:
                fixed_item = {
                    "path": record.fixed_root,
                    "entry_type": "excluded_root",
                    "classification": record.classification,
                    "rule_id": record.rule_id,
                }
                if record.boundary_target is not None:
                    fixed_item["boundary_target"] = record.boundary_target
                closure.append(fixed_item)
                emitted_roots.add(key)
            continue
        item = {
            "path": record.path,
            "entry_type": record.entry_type,
            "classification": record.classification,
            "rule_id": record.rule_id,
        }
        if record.entry_type != "directory":
            item.update({"size": record.size, "sha256": record.sha256})
        closure.append(item)
    closure.sort(key=lambda item: _path_identity(str(item["path"])))
    observed_records.sort(key=lambda item: _path_identity(item.path))
    return observed_records, closure, files, blockers, observation_sha, observation_count


def iter_full_observation(root: Path) -> Iterator[InventoryRecord]:
    """Replay the complete inventory stream without retaining it in memory."""

    with (root / _FULL_OBSERVATION_RELATIVE).open("rb") as handle:
        for line_number, line in enumerate(handle, start=1):
            try:
                payload = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise MigrationError(
                    "FULL_OBSERVATION_INVALID",
                    f"Cannot parse full observation line {line_number}: {exc}",
                ) from exc
            if not isinstance(payload, dict) or "entry_type" not in payload:
                continue
            try:
                yield InventoryRecord(**payload)
            except TypeError as exc:
                raise MigrationError(
                    "FULL_OBSERVATION_INVALID",
                    f"Invalid inventory record at line {line_number}: {exc}",
                ) from exc


def _occurrence_disposition(entry: CatalogEntry, classification: str) -> str:
    if classification in {"immutable_audit", "input_authority", "separate_worktree"}:
        return "immutable-audit"
    if classification == "application_boundary":
        return "application-boundary"
    if classification in {"runtime_non_authoritative", "retained_obsolete_source"}:
        return "retained-compatibility"
    if classification == "generated_text":
        return "generator-regenerate"
    if entry.candidate_only or entry.authority == "candidate-only":
        return "unresolved"
    if entry.authority == "retained-compatibility":
        return "retained-compatibility"
    return "rewrite"


def _catalog_text_pattern(source: str) -> re.Pattern[str]:
    components = [re.escape(component) for component in PurePosixPath(source).parts]
    body = r"(?:[/\\]|\\\\)+".join(components)
    return re.compile(
        rf"(?<![A-Za-z0-9_.-])(?P<token>{body})(?=$|[/\\]|[^A-Za-z0-9_.-])",
        re.IGNORECASE,
    )


def _catalog_byte_pattern(source: str) -> re.Pattern[bytes]:
    components = [re.escape(component.encode("utf-8")) for component in PurePosixPath(source).parts]
    body = rb"(?:[/\\]|\\\\)+".join(components)
    return re.compile(
        rb"(?<![A-Za-z0-9_.-])(?P<token>" + body + rb")(?=$|[/\\]|[^A-Za-z0-9_.-])",
        re.IGNORECASE,
    )


def scan_catalog_occurrences(
    root: Path,
    policy: dict[str, Any],
    catalog: Sequence[CatalogEntry],
    inventory: Sequence[InventoryRecord],
) -> tuple[list[ReferenceOccurrence], list[dict[str, Any]]]:
    """Probe every observed file, including ignored/audit/runtime files.

    The migration runtime is inventoried but excluded from content closure so a
    newly-published plan cannot recursively change the next plan's evidence.
    """

    occurrences: list[ReferenceOccurrence] = []
    blockers: list[dict[str, Any]] = []
    probe_classifications = {str(item) for item in policy.get("scan", {}).get("catalog_probe_classifications", [])}
    if not probe_classifications:
        raise MigrationError(
            "CATALOG_PROBE_POLICY_MISSING",
            "scan.catalog_probe_classifications must explicitly identify content-bearing classes",
        )
    patterns = [(entry, _catalog_byte_pattern(entry.source)) for entry in catalog]
    entries_by_basename: dict[bytes, list[tuple[CatalogEntry, re.Pattern[bytes]]]] = {}
    for entry, pattern in patterns:
        basename = PurePosixPath(entry.source).name.casefold().encode("utf-8")
        entries_by_basename.setdefault(basename, []).append((entry, pattern))
    basename_pattern = re.compile(
        b"|".join(re.escape(item) for item in sorted(entries_by_basename, key=lambda value: (-len(value), value))),
        re.IGNORECASE,
    )
    self_runtime = _path_identity(RUNTIME_RELATIVE.as_posix()) + "/"
    max_bytes = int(policy.get("scan", {}).get("max_catalog_probe_bytes", 256 * 1024 * 1024))
    for record in inventory:
        if record.entry_type != "file":
            continue
        if record.classification not in probe_classifications:
            continue
        suffix = PurePosixPath(record.path).suffix.casefold()
        if record.classification == "structured_sqlite" or suffix in _SQLITE_SIDECAR_SUFFIXES | {".zip", ".whl"}:
            continue
        path_id = _path_identity(record.path)
        if path_id.startswith(self_runtime):
            continue
        target = root / record.path
        try:
            size = target.stat().st_size
            if size > max_bytes:
                blockers.append({"code": "CATALOG_PROBE_FILE_TOO_LARGE", "path": record.path, "size": size})
                continue
            data = target.read_bytes()
        except OSError as exc:
            blockers.append({"code": "CATALOG_PROBE_UNREADABLE", "path": record.path, "detail": str(exc)})
            continue
        matched_basenames = {match.group(0).lower() for match in basename_pattern.finditer(data)}
        for basename in matched_basenames:
            for entry, pattern in entries_by_basename.get(basename, []):
                for match in pattern.finditer(data):
                    disposition = _occurrence_disposition(entry, record.classification)
                    token = match.group("token").decode("utf-8", errors="backslashreplace")
                    occurrences.append(
                        ReferenceOccurrence(
                            entry.entry_id,
                            record.path,
                            f"byte:{match.start()}",
                            "component-path",
                            token,
                            record.classification,
                            disposition,
                            disposition in {"rewrite", "generator-regenerate", "unresolved"},
                        )
                    )
    unique = {stable_hash(asdict(item)): item for item in occurrences}
    return (
        sorted(unique.values(), key=lambda item: (_path_identity(item.path), item.location, item.entry_id)),
        blockers,
    )


def _walk_string_scalars(value: Any, prefix: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield prefix or "/", value
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_string_scalars(item, f"{prefix}/{index}")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            yield from _walk_string_scalars(item, f"{prefix}/{escaped}")


def _structured_payload(path: str, text: str) -> tuple[str, Any] | None:
    suffix = PurePosixPath(path).suffix.casefold()
    if suffix == ".json":
        return "json", json.loads(text)
    if suffix == ".toml":
        return "toml", tomllib.loads(text)
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise MigrationError("YAML_READER_UNAVAILABLE", "PyYAML is required for structured YAML scanning") from exc
        try:
            return "yaml", list(yaml.safe_load_all(text))
        except yaml.YAMLError as exc:
            raise MigrationError("YAML_PARSE_FAILED", str(exc)) from exc
    return None


def scan_structured_occurrences(
    files: dict[str, ScannedFile],
    catalog: Sequence[CatalogEntry],
) -> tuple[list[StructuredLocation], list[dict[str, Any]]]:
    locations: list[StructuredLocation] = []
    blockers: list[dict[str, Any]] = []
    patterns = [(entry, _catalog_text_pattern(entry.source)) for entry in catalog]
    for path, scanned in sorted(files.items(), key=lambda pair: _path_identity(pair[0])):
        if scanned.decoded is None or PurePosixPath(path).suffix.casefold() not in {".json", ".toml", ".yaml", ".yml"}:
            continue
        try:
            parsed = _structured_payload(path, scanned.decoded.text)
        except (MigrationError, json.JSONDecodeError, tomllib.TOMLDecodeError, ValueError) as exc:
            if any(pattern.search(scanned.decoded.text) for _entry, pattern in patterns):
                blockers.append({"code": "STRUCTURED_PARSE_FAILED", "path": path, "detail": str(exc)})
            continue
        if parsed is None:
            continue
        format_name, payload = parsed
        for node_path, value in _walk_string_scalars(payload):
            for entry, pattern in patterns:
                for _match in pattern.finditer(value):
                    disposition = _occurrence_disposition(entry, scanned.record.classification)
                    locations.append(
                        StructuredLocation(entry.entry_id, path, format_name, node_path, value, disposition)
                    )
    unique = {stable_hash(asdict(item)): item for item in locations}
    return sorted(
        unique.values(), key=lambda item: (_path_identity(item.path), item.node_path, item.entry_id)
    ), blockers


def scan_zip_occurrences(
    root: Path,
    catalog: Sequence[CatalogEntry],
    inventory: Sequence[InventoryRecord],
    probe_classifications: set[str] | None = None,
) -> tuple[list[ReferenceOccurrence], list[dict[str, Any]]]:
    occurrences: list[ReferenceOccurrence] = []
    blockers: list[dict[str, Any]] = []
    patterns = [(entry, _catalog_byte_pattern(entry.source)) for entry in catalog]
    for record in inventory:
        if (
            record.entry_type != "file"
            or (probe_classifications is not None and record.classification not in probe_classifications)
            or PurePosixPath(record.path).suffix.casefold() not in {".zip", ".whl"}
        ):
            continue
        try:
            with zipfile.ZipFile(root / record.path) as archive:
                names = archive.namelist()
                unsafe = [
                    name for name in names if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts
                ]
                duplicates = sorted({name for name in names if names.count(name) > 1})
                if (unsafe or duplicates) and record.classification != "immutable_audit":
                    blockers.append(
                        {
                            "code": "ZIP_STRUCTURE_UNSAFE",
                            "path": record.path,
                            "unsafe": unsafe,
                            "duplicates": duplicates,
                        }
                    )
                    continue
                for info in archive.infolist():
                    member_name = info.filename.encode("utf-8", errors="surrogatepass")
                    payload = b"" if info.is_dir() else archive.read(info)
                    for entry, pattern in patterns:
                        for location, data in (("member-name", member_name), ("member-bytes", payload)):
                            for match in pattern.finditer(data):
                                disposition = _occurrence_disposition(entry, record.classification)
                                occurrences.append(
                                    ReferenceOccurrence(
                                        entry.entry_id,
                                        record.path,
                                        f"zip:{info.filename}:{location}:{match.start()}",
                                        "zip-member",
                                        match.group("token").decode("utf-8", errors="backslashreplace"),
                                        record.classification,
                                        disposition,
                                        disposition in {"rewrite", "generator-regenerate", "unresolved"},
                                        container="zip",
                                    )
                                )
        except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
            if record.classification != "immutable_audit":
                blockers.append({"code": "ZIP_READ_FAILED", "path": record.path, "detail": str(exc)})
    unique = {stable_hash(asdict(item)): item for item in occurrences}
    return sorted(unique.values(), key=lambda item: (_path_identity(item.path), item.location, item.entry_id)), blockers


def _tracked_paths(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return {
        _path_identity(item.decode("utf-8", errors="surrogateescape")) for item in result.stdout.split(b"\0") if item
    }


def registered_artifact_paths(root: Path) -> tuple[set[str], list[dict[str, Any]]]:
    """Expand exactly the canonical SoT artifact registry."""

    package_root = root / "groundtruth-kb" / "src"
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    try:
        from groundtruth_kb.inventory.string_scan import registered_artifact_inventory
        from groundtruth_kb.project.registry_control_plane import (
            load_registry_snapshot,
            registry_currentness,
            require_current_registry_receipt,
        )
    except ImportError as exc:
        raise MigrationError("ARTIFACT_REGISTRY_READER_UNAVAILABLE", str(exc)) from exc

    try:
        snapshot = load_registry_snapshot(project_root=root)
        currentness = registry_currentness(snapshot, project_root=root, db_path=root / "groundtruth.db")
        if not currentness["current"]:
            raise MigrationError(
                "ARTIFACT_REGISTRY_STALE",
                json.dumps(currentness, sort_keys=True, separators=(",", ":")),
            )
        require_current_registry_receipt(snapshot, db_path=root / "groundtruth.db")
    except MigrationError:
        raise
    except Exception as exc:
        raise MigrationError("ARTIFACT_REGISTRY_AUTHORITY_INVALID", str(exc)) from exc

    _artifacts, by_path, missing, _expansions = registered_artifact_inventory(root, snapshot=snapshot)
    if missing:
        raise MigrationError("ARTIFACT_REGISTRY_INCOMPLETE", json.dumps(missing, sort_keys=True))
    paths = set(by_path)
    findings: list[dict[str, Any]] = []
    normalized: set[str] = set()
    for path in paths:
        try:
            normalized.add(_catalog_path(path, field_name="registered_artifact_path"))
        except MigrationError as exc:
            findings.append({"code": exc.code, "path": path, "detail": str(exc)})
    return normalized, findings


def build_physical_inventory(
    root: Path,
    policy: dict[str, Any],
    catalog: Sequence[CatalogEntry],
    inventory: Sequence[InventoryRecord],
) -> tuple[list[PhysicalOccurrence], list[PlannedOperation], list[dict[str, Any]]]:
    by_catalog = {item.entry_id: item for item in catalog}
    by_path = {_path_identity(item.path): item for item in inventory}
    tracked = _tracked_paths(root)
    occurrences: list[PhysicalOccurrence] = []
    operations: list[PlannedOperation] = []
    blockers: list[dict[str, Any]] = []
    for index, row in enumerate(policy.get("physical_alias_roots", []), start=1):
        if not isinstance(row, dict):
            raise MigrationError("PHYSICAL_ALIAS_POLICY_INVALID", f"physical_alias_roots row {index} is not a table")
        operation_id = str(row.get("id") or "")
        alias_id = str(row.get("alias_id") or "")
        if not re.fullmatch(r"PA\d{3}", operation_id) or alias_id not in by_catalog:
            raise MigrationError("PHYSICAL_ALIAS_POLICY_INVALID", f"Invalid physical alias row {index}")
        source_root = _catalog_path(row.get("source"), field_name=f"{operation_id}.source")
        canonical_root = _catalog_path(row.get("canonical"), field_name=f"{operation_id}.canonical")
        disposition = str(row.get("disposition") or "")
        operation_type = str(row.get("operation") or "")
        owner = str(row.get("owner") or "deterministic-migration-engine")
        if disposition not in _REQUIRED_ALIAS_DISPOSITIONS or operation_type not in {
            "materialize-copy",
            "generator-regenerate",
        }:
            raise MigrationError("PHYSICAL_ALIAS_POLICY_INVALID", f"Invalid disposition/operation for {operation_id}")
        operations.append(
            PlannedOperation(
                operation_id,
                operation_type,
                "repository-file",
                source_root,
                canonical_root,
                disposition,
                owner,
                "source identity/hash and destination absence or exact equivalence",
                bool(row.get("retain_source", True)),
            )
        )
        source_prefix = _path_identity(source_root)
        matched = [
            item
            for item in inventory
            if _path_identity(item.path) == source_prefix or _path_identity(item.path).startswith(source_prefix + "/")
        ]
        if not matched:
            blockers.append(
                {"code": "PHYSICAL_ALIAS_SOURCE_MISSING", "operation_id": operation_id, "path": source_root}
            )
            continue
        for source_record in matched:
            suffix = source_record.path[len(source_root) :].lstrip("/")
            canonical_path = canonical_root + (f"/{suffix}" if suffix else "")
            destination = by_path.get(_path_identity(canonical_path))
            destination_state = "absent" if destination is None else destination.entry_type
            collision: str | None = None
            if source_record.entry_type == "reparse_point" or (
                destination and destination.entry_type == "reparse_point"
            ):
                collision = "reparse-boundary"
            elif destination and destination.entry_type != source_record.entry_type:
                collision = "type-conflict"
            elif destination and source_record.entry_type == "file" and destination.sha256 != source_record.sha256:
                collision = "divergent-destination"
            if collision:
                blockers.append(
                    {
                        "code": "PHYSICAL_ALIAS_COLLISION",
                        "operation_id": operation_id,
                        "source": source_record.path,
                        "target": canonical_path,
                        "collision": collision,
                    }
                )
            source_identity = stable_hash(
                {
                    "path": source_record.path,
                    "entry_type": source_record.entry_type,
                    "size": source_record.size,
                    "mode": source_record.mode,
                    "mtime_ns": source_record.mtime_ns,
                }
            )
            occurrences.append(
                PhysicalOccurrence(
                    alias_id,
                    source_record.path,
                    canonical_path,
                    source_record.entry_type,
                    source_record.classification,
                    disposition,
                    "tracked" if _path_identity(source_record.path) in tracked else "untracked-or-ignored",
                    source_identity,
                    source_record.sha256,
                    destination_state,
                    destination.sha256 if destination else None,
                    collision,
                    operation_id,
                )
            )
    return (
        sorted(occurrences, key=lambda item: (_path_identity(item.source_path), item.operation_id or "")),
        sorted(operations, key=lambda item: item.operation_id),
        blockers,
    )


def _line_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    prior = text.rfind("\n", 0, offset)
    return line, offset - prior


def _direct_pattern(source: str) -> re.Pattern[str]:
    components = source.split("/")
    body = r"[\\/]+".join(re.escape(component) for component in components)
    return re.compile(rf"(?<![A-Za-z0-9_.-]){body}(?![A-Za-z0-9_.\\/-])", re.IGNORECASE)


def _replacement_for_match(destination: str, token: str) -> str:
    separator = re.search(r"[\\/]+", token)
    chosen = separator.group(0) if separator else "/"
    return chosen.join(destination.split("/"))


def apply_direct_mappings(
    text: str,
    mappings: Sequence[MappingRow],
    matcher: MappingMatcher | None = None,
) -> tuple[str, list[tuple[MappingRow, int, int, str, str]]]:
    candidates: list[tuple[int, int, MappingRow, str, str]] = []
    selected_mappings = (matcher or MappingMatcher(mappings)).candidates(text)
    for mapping in selected_mappings:
        for match in _direct_pattern(mapping.source).finditer(text):
            replacement = _replacement_for_match(mapping.destination, match.group(0))
            candidates.append((match.start(), match.end(), mapping, match.group(0), replacement))
    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2].mapping_id))
    selected: list[tuple[int, int, MappingRow, str, str]] = []
    cursor = -1
    for candidate in candidates:
        start, end = candidate[:2]
        if start < cursor:
            prior = selected[-1]
            if start == prior[0] and end == prior[1] and candidate[2].destination == prior[2].destination:
                continue
            raise MigrationError(
                "AMBIGUOUS_DIRECT_MATCH",
                f"Overlapping mapping hits {prior[2].mapping_id} and {candidate[2].mapping_id} at offset {start}",
            )
        selected.append(candidate)
        cursor = end
    rendered = text
    for start, end, _mapping, _token, replacement in reversed(selected):
        rendered = rendered[:start] + replacement + rendered[end:]
    return rendered, [(mapping, start, end, token, replacement) for start, end, mapping, token, replacement in selected]


def apply_referrer_relative_mappings(
    referring_path: str,
    text: str,
    mappings: Sequence[MappingRow],
    matcher: MappingMatcher | None = None,
) -> tuple[str, list[tuple[MappingRow, int, int, str, str]]]:
    parent = PurePosixPath(referring_path).parent.as_posix()
    candidates: list[tuple[int, int, MappingRow, str, str]] = []
    for mapping in (matcher or MappingMatcher(mappings)).candidates(text):
        basename = PurePosixPath(mapping.source).name
        resolved = posixpath.normpath(posixpath.join(parent, basename))
        if _path_identity(resolved) != _path_identity(mapping.source):
            continue
        replacement = posixpath.relpath(mapping.destination, parent)
        for match in re.finditer(
            rf"(?<![A-Za-z0-9_.-]){re.escape(basename)}(?![A-Za-z0-9_.\\/-])", text, re.IGNORECASE
        ):
            candidates.append((match.start(), match.end(), mapping, match.group(0), replacement))
    candidates.sort(key=lambda item: (item[0], item[1], item[2].mapping_id))
    rendered = text
    for start, end, _mapping, _token, replacement in reversed(candidates):
        rendered = rendered[:start] + replacement + rendered[end:]
    return rendered, [
        (mapping, start, end, token, replacement) for start, end, mapping, token, replacement in candidates
    ]


def _regex_notation_variants(source: str) -> list[str]:
    escaped_components = [component.replace(".", r"\.") for component in source.split("/")]
    variants: list[str] = []
    for separator in (r"[/\\]", r"[\\/]", r"(?:/|\\)"):
        variants.append(separator.join(escaped_components))
        variants.append(separator.join(source.split("/")))
    return sorted(set(variants), key=lambda value: (-len(value), value))


def _normalize_regex_notation(value: str) -> str:
    normalized = re.sub(r"\[[/\\\\]+\]", "/", value)
    normalized = re.sub(r"\(\?:/\|\\\\+\)", "/", normalized)
    normalized = re.sub(r"\(\?:\\\\+\|/\)", "/", normalized)
    return normalized.replace(r"\.", ".").replace("\\\\", "\\")


def _static_string(node: ast.AST, values: dict[str, str]) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return values.get(node.id)
    if isinstance(node, ast.JoinedStr):
        chunks: list[str] = []
        for value in node.values:
            if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
                return None
            chunks.append(value.value)
        return "".join(chunks)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _static_string(node.left, values), _static_string(node.right, values)
        return left + right if left is not None and right is not None else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left, right = _static_string(node.left, values), _static_string(node.right, values)
        return f"{left.rstrip('/\\')}/{right.lstrip('/\\')}" if left is not None and right is not None else None
    if isinstance(node, ast.Call):
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            pieces: list[str] = [node.func.attr]
            current = node.func.value
            while isinstance(current, ast.Attribute):
                pieces.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                pieces.append(current.id)
            name = ".".join(reversed(pieces))
        if name in {"Path", "PurePath", "PurePosixPath", "PureWindowsPath"} and len(node.args) == 1:
            return _static_string(node.args[0], values)
        if name in {"os.path.join", "posixpath.join", "ntpath.join"}:
            parts = [_static_string(arg, values) for arg in node.args]
            return (
                "/".join(part.strip("/\\") for part in parts if part is not None)
                if all(part is not None for part in parts)
                else None
            )
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"joinpath", "glob", "rglob"}:
            base = _static_string(node.func.value, values)
            parts = [_static_string(arg, values) for arg in node.args]
            if base is not None and all(part is not None for part in parts):
                return "/".join([base.rstrip("/\\"), *[part.strip("/\\") for part in parts if part is not None]])
    return None


def python_static_paths(text: str) -> list[tuple[int, int, str]]:
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    values: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value_node = node.value
            value = _static_string(value_node, values) if value_node else None
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if value is not None:
                for target in targets:
                    if isinstance(target, ast.Name):
                        values[target.id] = value
    results: list[tuple[int, int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.BinOp, ast.Call, ast.JoinedStr)):
            continue
        value = _static_string(node, values)
        if value is not None and ("/" in value or "\\" in value):
            results.append((int(getattr(node, "lineno", 1)), int(getattr(node, "col_offset", 0)) + 1, value))
    return sorted(set(results))


def powershell_static_paths(text: str) -> list[tuple[int, int, str]]:
    results: list[tuple[int, int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not re.search(r"\bJoin-Path\b", line, re.IGNORECASE):
            continue
        strings = [match.group(2) for match in re.finditer(r"(['\"])(.*?)\1", line)]
        if len(strings) >= 2:
            offset = line.casefold().find("join-path") + 1
            results.append((line_number, max(offset, 1), "/".join(part.strip("/\\") for part in strings)))
    return results


def _value_mapping_hits(
    value: str,
    mappings: Sequence[MappingRow],
    matcher: MappingMatcher | None = None,
) -> list[MappingRow]:
    normalized = _nfc(value.replace("\\", "/")).casefold()
    return [
        mapping
        for mapping in (matcher or MappingMatcher(mappings)).candidates(value)
        if _path_identity(mapping.source) in normalized
    ]


def scan_references(files: dict[str, ScannedFile], mappings: list[MappingRow]) -> list[ReferenceHit]:
    hits: list[ReferenceHit] = []
    matcher = MappingMatcher(mappings)
    for path, scanned in sorted(files.items(), key=lambda pair: _path_identity(pair[0])):
        if scanned.decoded is None:
            continue
        text = scanned.decoded.text
        classification = scanned.record.classification
        historical = classification in {
            "immutable_audit",
            "runtime_non_authoritative",
            "retained_obsolete_source",
            "separate_worktree",
            "input_authority",
            "application_boundary",
        }
        direct_ranges: dict[str, list[tuple[int, int]]] = {}
        candidate_mappings = matcher.candidates(text)
        for mapping in candidate_mappings:
            ranges: list[tuple[int, int]] = []
            for match in _direct_pattern(mapping.source).finditer(text):
                line, column = _line_column(text, match.start())
                replacement = _replacement_for_match(mapping.destination, match.group(0))
                disposition = (
                    "retained_exception"
                    if historical
                    else "generated_action"
                    if classification == "generated_text"
                    else "planned_write"
                )
                hits.append(
                    ReferenceHit(
                        mapping.mapping_id,
                        path,
                        "direct",
                        line,
                        column,
                        match.group(0),
                        replacement,
                        classification,
                        not historical,
                        disposition,
                    )
                )
                ranges.append((match.start(), match.end()))
            direct_ranges[mapping.mapping_id] = ranges
            for variant in _regex_notation_variants(mapping.source):
                start = 0
                while True:
                    offset = text.casefold().find(variant.casefold(), start)
                    if offset < 0:
                        break
                    line, column = _line_column(text, offset)
                    hits.append(
                        ReferenceHit(
                            mapping.mapping_id,
                            path,
                            "regex_expression",
                            line,
                            column,
                            text[offset : offset + len(variant)],
                            None,
                            classification,
                            not historical,
                            "retained_exception" if historical else "unresolved",
                        )
                    )
                    start = offset + len(variant)
            for line_number, line_text in enumerate(text.splitlines(), start=1):
                if _path_identity(mapping.source) not in _path_identity(_normalize_regex_notation(line_text)):
                    continue
                if not any(marker in line_text for marker in ("[/", "[\\", "(?:")):
                    continue
                hits.append(
                    ReferenceHit(
                        mapping.mapping_id,
                        path,
                        "regex_expression",
                        line_number,
                        1,
                        line_text.strip(),
                        None,
                        classification,
                        not historical,
                        "retained_exception" if historical else "unresolved",
                    )
                )
        all_direct_ranges = [item for ranges in direct_ranges.values() for item in ranges]
        families = {
            "FAMILY-hooks": (".claude/hooks", True),
            "FAMILY-rules": (".claude/rules", True),
            "FAMILY-agent-control": ("config/agent-control", False),
        }
        for family_id, (family, rewrite_required) in families.items():
            for match in _direct_pattern(family).finditer(text):
                if any(start <= match.start() < end for start, end in all_direct_ranges):
                    continue
                line, column = _line_column(text, match.start())
                line_text = text.splitlines()[line - 1] if text.splitlines() else ""
                family_variant = (
                    "family_glob"
                    if any(token in line_text for token in ("*", "glob", "rglob", "fnmatch"))
                    else "family_directory"
                )
                hits.append(
                    ReferenceHit(
                        family_id,
                        path,
                        family_variant,
                        line,
                        column,
                        match.group(0),
                        None,
                        classification,
                        not historical and rewrite_required,
                        "retained_exception"
                        if historical
                        else "unresolved"
                        if rewrite_required
                        else "directory_unchanged",
                    )
                )
        static_values: list[tuple[int, int, str, str]] = []
        if path.casefold().endswith((".py", ".pyi")):
            static_values.extend((*item, "python_static") for item in python_static_paths(text))
        if path.casefold().endswith((".ps1", ".psm1", ".psd1")):
            static_values.extend((*item, "powershell_join_path") for item in powershell_static_paths(text))
        for line, column, value, variant in static_values:
            for mapping in _value_mapping_hits(value, mappings, matcher):
                hits.append(
                    ReferenceHit(
                        mapping.mapping_id,
                        path,
                        variant,
                        line,
                        column,
                        value,
                        None,
                        classification,
                        not historical,
                        "retained_exception" if historical else "unresolved",
                    )
                )
        for mapping in candidate_mappings:
            basename = PurePosixPath(mapping.source).name
            if basename == PurePosixPath(mapping.destination).name:
                continue
            for match in re.finditer(
                rf"(?<![A-Za-z0-9_.\\/-]){re.escape(basename)}(?![A-Za-z0-9_.\\/-])",
                text,
                re.IGNORECASE,
            ):
                if any(start <= match.start() < end for start, end in direct_ranges[mapping.mapping_id]):
                    continue
                line, column = _line_column(text, match.start())
                parent = PurePosixPath(path).parent.as_posix()
                referrer_resolved = posixpath.normpath(posixpath.join(parent, match.group(0)))
                is_referrer_relative = _path_identity(referrer_resolved) == _path_identity(mapping.source)
                hits.append(
                    ReferenceHit(
                        mapping.mapping_id,
                        path,
                        "referrer_relative" if is_referrer_relative else "bare_filename",
                        line,
                        column,
                        match.group(0),
                        posixpath.relpath(mapping.destination, parent) if is_referrer_relative else None,
                        classification,
                        not historical,
                        "retained_exception"
                        if historical
                        else "planned_write"
                        if is_referrer_relative
                        else "unresolved",
                    )
                )
    unique = {stable_hash(asdict(hit)): hit for hit in hits}
    return sorted(
        unique.values(), key=lambda hit: (_path_identity(hit.path), hit.line, hit.column, hit.mapping_id, hit.variant)
    )


def scan_sqlite(
    root: Path, policy: dict[str, Any], mappings: list[MappingRow]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    hits: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    matcher = MappingMatcher(mappings)
    for row in policy.get("sqlite_scans", []):
        grouped.setdefault(str(row.get("path") or ""), []).append(row)
    for relative, scans in sorted(grouped.items()):
        database = root / relative
        try:
            connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
            connection.execute("PRAGMA query_only=ON")
            connection.execute("BEGIN")
            for scan in scans:
                cursor = connection.execute(str(scan["query"]))
                columns = [item[0] for item in cursor.description or []]
                identity_columns = [str(item) for item in scan.get("identity_columns", [])]
                text_columns = [str(item) for item in scan.get("text_columns", [])]
                for values in cursor:
                    record = dict(zip(columns, values, strict=True))
                    identity = {name: record.get(name) for name in identity_columns}
                    for column in text_columns:
                        value = record.get(column)
                        if not isinstance(value, str):
                            continue
                        for mapping in _value_mapping_hits(value, mappings, matcher):
                            hits.append(
                                {
                                    "scan_id": str(scan.get("id")),
                                    "path": relative,
                                    "identity": identity,
                                    "column": column,
                                    "mapping_id": mapping.mapping_id,
                                    "value": value,
                                    "history": bool(scan.get("history")),
                                    "load_bearing": not bool(scan.get("history")),
                                }
                            )
            connection.rollback()
            connection.close()
        except (OSError, sqlite3.Error, KeyError, ValueError) as exc:
            blockers.append({"code": "SQLITE_SCAN_FAILED", "path": relative, "detail": f"{type(exc).__name__}: {exc}"})
    hits.sort(
        key=lambda item: (
            item["path"],
            item["scan_id"],
            stable_hash(item["identity"]),
            item["column"],
            item["mapping_id"],
        )
    )
    return hits, blockers


def _normalize_lf(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _adapted_source(
    mapping: MappingRow,
    scanned: ScannedFile,
    policy: dict[str, Any],
    mappings: list[MappingRow],
    matcher: MappingMatcher,
) -> tuple[bytes, list[str], list[dict[str, Any]]]:
    if scanned.decoded is None:
        return scanned.raw, [], [{"code": "SOURCE_NOT_TEXT", "path": mapping.source, "mapping_id": mapping.mapping_id}]
    text, _ = apply_direct_mappings(scanned.decoded.text, mappings, matcher)
    reasons = [f"reconcile:{mapping.mapping_id}"]
    blockers: list[dict[str, Any]] = []
    for adaptation in policy.get("known_adaptations", []):
        if _path_identity(str(adaptation.get("path") or "")) != _path_identity(mapping.destination):
            continue
        kind = str(adaptation.get("kind") or "")
        old = str(adaptation.get("old") or "")
        new = str(adaptation.get("new") or "")
        if kind in {"literal_replace", "python_import"}:
            if old in text:
                text = text.replace(old, new)
            elif new not in text:
                blockers.append(
                    {
                        "code": "ADAPTATION_NOT_APPLICABLE",
                        "path": mapping.destination,
                        "adaptation_id": adaptation.get("id"),
                        "detail": f"neither {old!r} nor {new!r} is present",
                    }
                )
            reasons.append(f"adaptation:{adaptation.get('id')}")
        elif kind in {"manual_policy", "manifest_transform_from_clean_source"}:
            reasons.append(f"adaptation:{adaptation.get('id')}")
        else:
            blockers.append({"code": "UNKNOWN_ADAPTATION_KIND", "path": mapping.destination, "detail": kind})
    if mapping.category != "rules":
        text = _normalize_lf(text)
    return encode_text(scanned.decoded, text), reasons, blockers


def _load_script(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise MigrationError("GENERATOR_IMPORT_FAILED", f"Cannot import generator {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _projection_outputs(
    root: Path,
    policy_path: Path,
    policy: dict[str, Any],
    desired: dict[str, tuple[bytes, set[str], int]],
) -> tuple[dict[str, tuple[bytes, set[str], int]], list[dict[str, Any]], list[dict[str, Any]]]:
    actions: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    overrides = {path: value[0] for path, value in desired.items()}
    rule_module = _load_script(_SCRIPT_DIR / "generate_rule_compatibility_projections.py", "_wi5640_rule_projection")
    rows, rule_outputs = rule_module.render_outputs(root, policy_path=policy_path, canonical_overrides=overrides)
    for row in rows:
        projected = rule_outputs[row.source]
        source_path = root / row.source
        mode = stat.S_IMODE(source_path.stat().st_mode) if source_path.exists() else 0o644
        if not source_path.is_file() or source_path.read_bytes() != projected:
            desired[row.source] = (projected, {"generator:rule-compatibility"}, mode)
            actions.append({"generator": "scripts/generate_rule_compatibility_projections.py", "path": row.source})

    cursor_module = _load_script(_SCRIPT_DIR / "generate_cursor_skill_adapters.py", "_wi5640_cursor_projection")
    try:
        cursor_outputs, adapters, orphans = cursor_module.render_outputs(root, source_overrides=overrides)
    except UnicodeDecodeError as exc:
        blockers.append({"code": "CURSOR_SOURCE_NOT_UTF8", "detail": str(exc)})
        cursor_outputs, adapters, orphans = {}, [], []
    for relative, output in sorted(cursor_outputs.items(), key=lambda item: _path_identity(item[0])):
        target = root / relative
        mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
        if not target.is_file() or target.read_bytes() != output:
            reason = (
                "generator:cursor-skills-manifest" if relative.endswith("/MANIFEST.json") else "generator:cursor-skills"
            )
            desired[relative] = (output, {reason}, mode)
            actions.append({"generator": "scripts/generate_cursor_skill_adapters.py", "path": relative})
    for orphan in orphans:
        blockers.append({"code": "GENERATED_ORPHAN_REQUIRES_GOVERNED_CLEANUP", "path": orphan})
    del adapters
    return desired, sorted(actions, key=lambda item: (_path_identity(item["path"]), item["generator"])), blockers


def build_reconciliation_and_writes(
    root: Path,
    policy_path: Path,
    policy: dict[str, Any],
    mappings: list[MappingRow],
    catalog: list[CatalogEntry],
    files: dict[str, ScannedFile],
    hits: list[ReferenceHit],
    operation_manifest: list[PlannedOperation],
) -> tuple[list[dict[str, Any]], list[ProposedWrite], list[dict[str, Any]], list[dict[str, Any]], dict[str, bytes]]:
    desired: dict[str, tuple[bytes, set[str], int]] = {}
    blockers: list[dict[str, Any]] = []
    reconciliations: list[dict[str, Any]] = []
    content_authority = {str(item.get("mapping_id")): item for item in policy.get("content_reconciliation", [])}
    matcher = MappingMatcher(mappings)
    alias_mappings = [
        MappingRow(item.entry_id, "obsolete-alias", item.source, item.canonical)
        for item in catalog
        if item.entry_id.startswith("A") and item.authority == "rewrite" and not item.candidate_only
    ]
    alias_matcher = MappingMatcher(alias_mappings)
    for path, scanned in files.items():
        if scanned.decoded is None or scanned.record.classification not in {"mutable_text", "canonical_destination"}:
            continue
        try:
            rendered, matches = apply_direct_mappings(scanned.decoded.text, mappings, matcher)
            rendered, relative_matches = apply_referrer_relative_mappings(path, rendered, mappings, matcher)
            rendered, alias_matches = apply_direct_mappings(rendered, alias_mappings, alias_matcher)
            rendered, alias_relative_matches = apply_referrer_relative_mappings(
                path, rendered, alias_mappings, alias_matcher
            )
        except MigrationError as exc:
            blockers.append({"code": exc.code, "path": path, "detail": str(exc)})
            continue
        if matches or relative_matches or alias_matches or alias_relative_matches:
            output = encode_text(scanned.decoded, rendered)
            reasons = {f"direct:{item[0].mapping_id}" for item in matches}
            reasons.update(f"referrer-relative:{item[0].mapping_id}" for item in relative_matches)
            reasons.update(f"alias-direct:{item[0].mapping_id}" for item in alias_matches)
            reasons.update(f"alias-referrer-relative:{item[0].mapping_id}" for item in alias_relative_matches)
            desired[path] = (output, reasons, scanned.record.mode)
    for mapping in mappings:
        source = files.get(mapping.source)
        destination = files.get(mapping.destination)
        if source is None or destination is None:
            blockers.append({"code": "MAPPING_FILE_NOT_SCANNED", "mapping_id": mapping.mapping_id})
            continue
        transformed, reasons, adaptation_blockers = _adapted_source(mapping, source, policy, mappings, matcher)
        blockers.extend(adaptation_blockers)
        source_normalized = source.raw.replace(b"\r\n", b"\n")
        destination_normalized = destination.raw.replace(b"\r\n", b"\n")
        transformed_normalized = transformed.replace(b"\r\n", b"\n")
        declared = content_authority.get(mapping.mapping_id)
        authority = str(declared.get("authority")) if declared else "manifest_default_transformed_source"
        accepted = destination.raw == transformed
        preexisting_equal = source_normalized == destination_normalized
        if mapping.category == "rules":
            authority = "canonical_destination_with_retained_projection"
            accepted = True
            transformed = destination.raw
        if not accepted and destination_normalized == transformed_normalized:
            accepted = True
            authority = "transformed_source_newline_equivalent"
        may_write = False
        if not accepted and mapping.category != "rules":
            if (
                declared is None
                and preexisting_equal
                or authority
                in {
                    "transformed_source",
                    "transformed_source_with_known_adaptation",
                    "clean_source_all_manifest_transforms",
                }
            ):
                may_write = True
            elif authority == "transformed_source_with_manual_policy":
                blockers.append(
                    {
                        "code": "MANUAL_CONTENT_AUTHORITY_UNRESOLVED",
                        "mapping_id": mapping.mapping_id,
                        "source": mapping.source,
                        "destination": mapping.destination,
                    }
                )
            else:
                blockers.append(
                    {
                        "code": "UNREVIEWED_CONTENT_DIVERGENCE",
                        "mapping_id": mapping.mapping_id,
                        "source": mapping.source,
                        "destination": mapping.destination,
                    }
                )
        if may_write:
            if authority == "transformed_source_with_known_adaptation" and not any(
                reason.startswith("adaptation:") for reason in reasons
            ):
                blockers.append({"code": "DECLARED_ADAPTATION_NOT_EXECUTED", "mapping_id": mapping.mapping_id})
                may_write = False
        if may_write:
            prior_reasons = desired.get(mapping.destination, (b"", set(), destination.record.mode))[1]
            desired[mapping.destination] = (transformed, set(prior_reasons) | set(reasons), destination.record.mode)
        elif not accepted and not any(item.get("mapping_id") == mapping.mapping_id for item in blockers):
            blockers.append(
                {
                    "code": "UNREVIEWED_CONTENT_DIVERGENCE",
                    "mapping_id": mapping.mapping_id,
                    "source": mapping.source,
                    "destination": mapping.destination,
                }
            )
        reconciliations.append(
            {
                "mapping_id": mapping.mapping_id,
                "category": mapping.category,
                "source": mapping.source,
                "destination": mapping.destination,
                "source_sha256": sha256_bytes(source.raw),
                "destination_sha256": sha256_bytes(destination.raw),
                "transformed_source_sha256": sha256_bytes(transformed),
                "chosen_content_sha256": sha256_bytes(transformed),
                "authority": authority,
                "accepted": accepted or may_write,
            }
        )
    for operation in operation_manifest:
        if operation.operation_type not in {"materialize-copy", "generator-regenerate"} or not operation.source:
            continue
        source_root = root / operation.source
        if not source_root.is_dir():
            blockers.append({"code": "PHYSICAL_OPERATION_SOURCE_MISSING", "operation_id": operation.operation_id})
            continue
        for source_path in sorted(source_root.rglob("*"), key=lambda item: _path_identity(item.as_posix())):
            if not source_path.is_file() or _path_is_reparse(source_path):
                continue
            suffix = source_path.relative_to(source_root)
            target_relative = (PurePosixPath(operation.target) / PurePosixPath(suffix.as_posix())).as_posix()
            output = source_path.read_bytes()
            decoded = decode_text(
                output,
                source_path.as_posix(),
                [str(item) for item in policy.get("scan", {}).get("legacy_encodings", [])],
            )
            reasons = {f"physical:{operation.operation_id}"}
            if decoded is not None:
                rendered, alias_matches = apply_direct_mappings(decoded.text, alias_mappings, alias_matcher)
                rendered, csv_matches = apply_direct_mappings(rendered, mappings, matcher)
                if alias_matches:
                    reasons.update(f"alias-direct:{item[0].mapping_id}" for item in alias_matches)
                if csv_matches:
                    reasons.update(f"direct:{item[0].mapping_id}" for item in csv_matches)
                output = encode_text(decoded, rendered)
            prior = desired.get(target_relative)
            if prior is not None and prior[0] != output:
                blockers.append(
                    {
                        "code": "PHYSICAL_OPERATION_OUTPUT_CONFLICT",
                        "operation_id": operation.operation_id,
                        "path": target_relative,
                    }
                )
                continue
            mode = stat.S_IMODE(source_path.stat().st_mode)
            desired[target_relative] = (output, (prior[1] if prior else set()) | reasons, mode)
    desired, generator_actions, projection_blockers = _projection_outputs(root, policy_path, policy, desired)
    blockers.extend(projection_blockers)
    exact_generated = {
        _path_identity(path)
        for path in desired
        if any(path.casefold().startswith(prefix.casefold()) for prefix in _GENERATED_PREFIXES)
    }
    for hit in hits:
        if (
            hit.classification == "generated_text"
            and hit.load_bearing
            and _path_identity(hit.path) not in exact_generated
        ):
            generator_actions.append({"generator": "unresolved-generated-owner", "path": hit.path})
            blockers.append(
                {"code": "GENERATED_OUTPUT_NOT_MATERIALIZED", "path": hit.path, "mapping_id": hit.mapping_id}
            )
    writes: list[ProposedWrite] = []
    payload_by_path: dict[str, bytes] = {}
    for path, (postimage, reasons, mode) in sorted(desired.items(), key=lambda pair: _path_identity(pair[0])):
        target = root / path
        preimage = target.read_bytes() if target.is_file() else None
        if preimage == postimage:
            continue
        if not write_path_allowed(policy, path):
            blockers.append({"code": "WRITE_OUTSIDE_MUTATION_POLICY", "path": path})
            continue
        post_hash = sha256_bytes(postimage)
        payload = (RUNTIME_RELATIVE / "payload" / f"{post_hash.removeprefix('sha256:')}.bin").as_posix()
        pre_hash = sha256_bytes(preimage) if preimage is not None else None
        preimage_payload = (
            (RUNTIME_RELATIVE / "preimages" / f"{pre_hash.removeprefix('sha256:')}.bin").as_posix()
            if pre_hash
            else None
        )
        writes.append(
            ProposedWrite(
                path,
                pre_hash,
                post_hash,
                preimage_payload,
                payload,
                mode,
                tuple(sorted(reasons)),
            )
        )
        payload_by_path[path] = postimage
    return (
        sorted(reconciliations, key=lambda item: item["mapping_id"]),
        writes,
        sorted(
            {stable_hash(item): item for item in generator_actions}.values(),
            key=lambda item: (_path_identity(item["path"]), item["generator"]),
        ),
        blockers,
        payload_by_path,
    )


def _postimage_texts(root: Path, writes: list[ProposedWrite], files: dict[str, ScannedFile]) -> dict[str, str]:
    results: dict[str, str] = {}
    legacy = ["cp1252"]
    for write in writes:
        payload_path = root / write.payload
        if payload_path.is_file() and sha256_bytes(payload_path.read_bytes()) == write.postimage_sha256:
            raw = payload_path.read_bytes()
        else:
            continue
        decoded = decode_text(raw, write.path, legacy)
        if decoded:
            results[write.path] = decoded.text
    return results


def _hit_present_after(hit: ReferenceHit, post_text: str, mappings: dict[str, MappingRow]) -> bool:
    if hit.mapping_id.startswith("FAMILY-"):
        return _direct_pattern(hit.token.replace("\\", "/")).search(post_text) is not None
    mapping = mappings.get(hit.mapping_id)
    if mapping is None:
        return hit.token.casefold() in post_text.casefold()
    if hit.variant == "direct":
        return _direct_pattern(mapping.source).search(post_text) is not None
    if hit.variant == "regex_expression":
        return any(variant.casefold() in post_text.casefold() for variant in _regex_notation_variants(mapping.source))
    if hit.variant == "bare_filename":
        basename = PurePosixPath(mapping.source).name
        return (
            re.search(
                rf"(?<![A-Za-z0-9_.\\/-]){re.escape(basename)}(?![A-Za-z0-9_.\\/-])",
                post_text,
                re.IGNORECASE,
            )
            is not None
        )
    return _path_identity(mapping.source) in _nfc(post_text.replace("\\", "/")).casefold()


def classify_residuals(
    root: Path,
    mappings: list[MappingRow],
    files: dict[str, ScannedFile],
    hits: list[ReferenceHit],
    writes: list[ProposedWrite],
    sqlite_hits: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    write_by_path = {write.path: write for write in writes}
    mapping_by_id = {mapping.mapping_id: mapping for mapping in mappings}
    post_texts: dict[str, str] = {}
    for write in writes:
        payload = root / write.payload
        if not payload.is_file():
            continue
        decoded = decode_text(payload.read_bytes(), write.path, ["cp1252"])
        if decoded:
            post_texts[write.path] = decoded.text
    residuals: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for hit in hits:
        disposition = hit.disposition
        post_text = post_texts.get(hit.path)
        if not hit.load_bearing:
            disposition = "historical_or_retained"
        elif (
            hit.path in write_by_path
            and post_text is not None
            and not _hit_present_after(hit, post_text, mapping_by_id)
        ):
            disposition = "planned_write"
        elif disposition in {"planned_write", "generated_action"}:
            disposition = "unresolved"
        row = asdict(hit)
        row["disposition"] = disposition
        residuals.append(row)
        if disposition == "historical_or_retained":
            exceptions.append(
                {
                    "exception_id": f"EX-{stable_hash(row).removeprefix('sha256:')[:16]}",
                    "kind": hit.classification,
                    "path": hit.path,
                    "mapping_id": hit.mapping_id,
                    "variant": hit.variant,
                }
            )
        elif disposition == "unresolved":
            blockers.append(
                {
                    "code": "UNRESOLVED_LIVE_REFERENCE",
                    "path": hit.path,
                    "mapping_id": hit.mapping_id,
                    "variant": hit.variant,
                    "line": hit.line,
                    "column": hit.column,
                }
            )
    for item in sqlite_hits:
        disposition = "historical_or_retained" if not item["load_bearing"] else "unresolved"
        row = dict(item)
        row["variant"] = "sqlite_text"
        row["disposition"] = disposition
        residuals.append(row)
        if disposition == "historical_or_retained":
            exceptions.append(
                {
                    "exception_id": f"EX-{stable_hash(row).removeprefix('sha256:')[:16]}",
                    "kind": "sqlite_history",
                    "path": item["path"],
                    "mapping_id": item["mapping_id"],
                    "variant": "sqlite_text",
                }
            )
        else:
            blockers.append(
                {
                    "code": "LIVE_SQLITE_REFERENCE_REQUIRES_DOMAIN_API",
                    "path": item["path"],
                    "mapping_id": item["mapping_id"],
                    "identity": item["identity"],
                    "column": item["column"],
                }
            )
    residuals.sort(key=lambda item: stable_hash(item))
    exceptions = sorted(
        {stable_hash(item): item for item in exceptions}.values(), key=lambda item: item["exception_id"]
    )
    blockers.sort(key=stable_hash)
    return residuals, exceptions, blockers


def _generator_input_hash(root: Path) -> str:
    paths = [
        "scripts/generate_rule_compatibility_projections.py",
        "scripts/generate_cursor_skill_adapters.py",
        "scripts/generate_codex_skill_adapters.py",
        "scripts/generate_antigravity_skill_adapters.py",
        "scripts/generate_api_skill_adapters.py",
        "scripts/generate_goose_manifest.py",
        "config/agent-control/gtkb-harness-capability-registry.toml",
    ]
    material = []
    for relative in paths:
        path = root / relative
        material.append({"path": relative, "sha256": sha256_bytes(path.read_bytes()) if path.is_file() else None})
    return stable_hash(material)


def run_generator_checks(root: Path, policy: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not policy.get("generator_execution", {}).get("enabled_during_analysis", False):
        return [], []
    timeout = int(policy.get("generator_execution", {}).get("timeout_seconds", 120))
    results: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for row in policy.get("generator_checks", []):
        generator_id = str(row.get("id") or "")
        command = [str(item) for item in row.get("command", [])]
        disposition = str(row.get("disposition") or "")
        try:
            process = subprocess.run(
                command,
                cwd=root,
                check=False,
                capture_output=True,
                timeout=timeout,
                env=environment,
            )
            result = {
                "generator_check": generator_id,
                "command": command,
                "returncode": process.returncode,
                "stdout_sha256": sha256_bytes(process.stdout),
                "stderr_sha256": sha256_bytes(process.stderr),
                "stdout_tail": process.stdout.decode("utf-8", errors="replace")[-2000:],
                "stderr_tail": process.stderr.decode("utf-8", errors="replace")[-2000:],
                "disposition": disposition or "required_clean",
            }
        except (OSError, subprocess.TimeoutExpired) as exc:
            result = {
                "generator_check": generator_id,
                "command": command,
                "returncode": None,
                "error": f"{type(exc).__name__}: {exc}",
                "disposition": disposition or "required_clean",
            }
        results.append(result)
        returncode = result.get("returncode")
        planned_generator = generator_id in {"cursor-skills", "rule-compatibility"} and returncode == 1
        if returncode != 0 and not planned_generator:
            blockers.append(
                {
                    "code": "GENERATOR_CHECK_BLOCKED" if disposition else "GENERATOR_CHECK_FAILED",
                    "generator_check": generator_id,
                    "returncode": returncode,
                    "disposition": disposition or None,
                }
            )
    return results, blockers


def _operation_side_effects(physical: Sequence[PlannedOperation]) -> list[PlannedOperation]:
    operational = [
        PlannedOperation(
            "RT001",
            "runtime-lock",
            "runtime-state",
            None,
            _LOCK_RELATIVE.as_posix(),
            "retained-compatibility",
            "scripts/gtkb_file_reference_migration.py",
            "exclusive create bound to transaction id and journal",
            False,
        ),
        PlannedOperation(
            "RT002",
            "append-only-journal",
            "runtime-state",
            None,
            (_TRANSACTION_DIRECTORY / "<transaction-id>/journal.jsonl").as_posix(),
            "retained-compatibility",
            "scripts/gtkb_file_reference_migration.py",
            "hash-chained fsynced write-ahead events",
            False,
        ),
        PlannedOperation(
            "RT003",
            "transaction-report",
            "runtime-state",
            None,
            (_TRANSACTION_DIRECTORY / "<transaction-id>/transaction.json").as_posix(),
            "retained-compatibility",
            "scripts/gtkb_file_reference_migration.py",
            "terminal state derived from a validated journal",
            False,
        ),
        PlannedOperation(
            "RT004",
            "payload-materialization",
            "runtime-state",
            None,
            (RUNTIME_RELATIVE / "payload/<sha256>.bin").as_posix(),
            "retained-compatibility",
            "scripts/gtkb_file_reference_migration.py",
            "content-addressed exact postimage payload",
            False,
        ),
        PlannedOperation(
            "RT005",
            "preimage-materialization",
            "runtime-state",
            None,
            (RUNTIME_RELATIVE / "preimages/<sha256>.bin").as_posix(),
            "retained-compatibility",
            "scripts/gtkb_file_reference_migration.py",
            "content-addressed exact preimage payload",
            False,
        ),
        PlannedOperation(
            "PKT001",
            "implementation-packet-binding",
            "governance-evidence",
            None,
            ".gtkb-state/implementation-authorizations/by-bridge/gtkb-file-move-rename-canonicalization-v4-plan-approval.json",
            "retained-compatibility",
            "scripts/implementation_authorization.py",
            "child GO, claim, session, exact target list, and reviewed binding all match",
            False,
        ),
    ]
    return sorted([*physical, *operational], key=lambda item: item.operation_id)


def _retained_source_ledger(
    root: Path,
    mappings: Sequence[MappingRow],
    physical: Sequence[PhysicalOccurrence],
) -> list[dict[str, Any]]:
    paths = {item.source for item in mappings}
    paths.update(item.source_path for item in physical if item.entry_type == "file")
    ledger: list[dict[str, Any]] = []
    for path in sorted(paths, key=_path_identity):
        target = root / path
        if not target.is_file():
            raise MigrationError("RETAINED_SOURCE_MISSING", f"Required retained source is missing: {path}")
        data = target.read_bytes()
        ledger.append(
            {
                "path": path,
                "entry_type": "file",
                "sha256": sha256_bytes(data),
                "mode": stat.S_IMODE(target.stat().st_mode),
                "must_remain": True,
            }
        )
    return ledger


def _classification_for_new_file(policy: dict[str, Any], path: str) -> tuple[str, str]:
    rule, error = _policy_classification(path, classification_rules(policy))
    if error:
        raise MigrationError("EXPECTED_FINAL_CLASSIFICATION_AMBIGUOUS", f"{path}: {error}")
    if rule:
        return rule.classification, rule.rule_id
    if any(path.casefold().startswith(prefix.casefold()) for prefix in _GENERATED_PREFIXES):
        return "generated_text", "generated-projection"
    return "mutable_text", "builtin-root-member"


def _projected_closure_inventory(
    policy: dict[str, Any],
    closure_inventory: Sequence[dict[str, Any]],
    writes: Sequence[ProposedWrite],
    payload_by_path: dict[str, bytes],
) -> list[dict[str, Any]]:
    projected = {_path_identity(str(item["path"])): dict(item) for item in closure_inventory}
    for write in writes:
        data = payload_by_path[write.path]
        prior = projected.get(_path_identity(write.path))
        if prior is not None:
            classification = str(prior["classification"])
            rule_id = str(prior["rule_id"])
        else:
            classification, rule_id = _classification_for_new_file(policy, write.path)
        projected[_path_identity(write.path)] = {
            "path": write.path,
            "entry_type": "file",
            "classification": classification,
            "rule_id": rule_id,
            "size": len(data),
            "sha256": write.postimage_sha256,
        }
        parent = PurePosixPath(write.path).parent
        while parent.as_posix() not in {"", "."}:
            parent_path = parent.as_posix()
            parent_id = _path_identity(parent_path)
            if parent_id not in projected:
                parent_class, parent_rule = _classification_for_new_file(policy, parent_path)
                projected[parent_id] = {
                    "path": parent_path,
                    "entry_type": "directory",
                    "classification": "directory" if parent_class == "mutable_text" else parent_class,
                    "rule_id": "builtin-directory" if parent_class == "mutable_text" else parent_rule,
                }
            parent = parent.parent
    return sorted(projected.values(), key=lambda item: _path_identity(str(item["path"])))


def _expected_remaining_occurrences(
    policy: dict[str, Any],
    catalog: Sequence[CatalogEntry],
    occurrences: Sequence[ReferenceOccurrence],
    writes: Sequence[ProposedWrite],
    payload_by_path: dict[str, bytes],
) -> list[dict[str, Any]]:
    write_paths = {_path_identity(item.path) for item in writes}
    remaining = [asdict(item) for item in occurrences if _path_identity(item.path) not in write_paths]
    occurrence_classes = {_path_identity(item.path): item.classification for item in occurrences}
    for write in writes:
        data = payload_by_path[write.path]
        classification = occurrence_classes.get(_path_identity(write.path))
        if classification is None:
            classification, _rule_id = _classification_for_new_file(policy, write.path)
        for entry in catalog:
            for match in _catalog_byte_pattern(entry.source).finditer(data):
                disposition = _occurrence_disposition(entry, classification)
                remaining.append(
                    asdict(
                        ReferenceOccurrence(
                            entry.entry_id,
                            write.path,
                            f"postimage-byte:{match.start()}",
                            "component-path",
                            match.group("token").decode("utf-8", errors="backslashreplace"),
                            classification,
                            disposition,
                            disposition in {"rewrite", "generator-regenerate", "unresolved"},
                        )
                    )
                )
    return sorted(remaining, key=stable_hash)


def _normalized_occurrence_material(items: Sequence[ReferenceOccurrence | dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        raw = asdict(item) if isinstance(item, ReferenceOccurrence) else item
        normalized.append(
            {
                "entry_id": str(raw.get("entry_id") or ""),
                "path": str(raw.get("path") or ""),
                "token": _nfc(str(raw.get("token") or "").replace("\\", "/")).casefold(),
                "classification": str(raw.get("classification") or ""),
                "disposition": str(raw.get("disposition") or ""),
                "container": str(raw.get("container") or "filesystem"),
            }
        )
    return sorted(normalized, key=stable_hash)


def build_expected_final_closure(
    policy: dict[str, Any],
    catalog: Sequence[CatalogEntry],
    closure_inventory: Sequence[dict[str, Any]],
    occurrences: Sequence[ReferenceOccurrence],
    writes: Sequence[ProposedWrite],
    payload_by_path: dict[str, bytes],
    retained_sources: Sequence[dict[str, Any]],
    git_index_sha256: str,
) -> dict[str, Any]:
    projected_inventory = _projected_closure_inventory(policy, closure_inventory, writes, payload_by_path)
    remaining = _expected_remaining_occurrences(policy, catalog, occurrences, writes, payload_by_path)
    target_states = [{"path": item.path, "sha256": item.postimage_sha256, "mode": item.mode} for item in writes]
    material = {
        "schema_version": 1,
        "closure_inventory_sha256": stable_hash(projected_inventory),
        "remaining_occurrence_sha256": stable_hash(_normalized_occurrence_material(remaining)),
        "target_states": target_states,
        "retained_sources": list(retained_sources),
        "git_index_sha256": git_index_sha256,
    }
    material["fingerprint"] = stable_hash(material)
    return material


def analyze(root: Path, policy_path: Path = DEFAULT_POLICY) -> tuple[Analysis, list[dict[str, Any]]]:
    root = Path(os.path.abspath(str(root)))
    root_stat_before = root.stat()
    root_identity_before = (root_stat_before.st_dev, root_stat_before.st_ino)
    policy_candidate = policy_path if policy_path.is_absolute() else root / policy_path
    engine_bytes = Path(__file__).read_bytes()
    policy_bytes = policy_candidate.read_bytes()
    resolved_policy, policy = load_policy(root, policy_path)
    if resolved_policy.read_bytes() != policy_bytes:
        raise MigrationError("POLICY_CHANGED_DURING_PARSE", "Policy changed while it was being parsed")
    csv_path = root / str(policy["manifest_path"])
    csv_bytes = csv_path.read_bytes()
    mappings = load_manifest(root, policy)
    package_root = root / "groundtruth-kb" / "src"
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    from groundtruth_kb.project.registry_control_plane import load_registry_snapshot

    transition_snapshot = load_registry_snapshot(project_root=root)
    for mapping in mappings:
        for label, relative_path in (("source", mapping.source), ("destination", mapping.destination)):
            try:
                registered = transition_snapshot.resolver.resolve(relative_path)
            except Exception as exc:
                raise MigrationError("ARTIFACT_REGISTRY_MEMBERSHIP_INVALID", str(exc)) from exc
            if registered is None:
                raise MigrationError(
                    "ARTIFACT_REGISTRY_UNREGISTERED_TRANSITION",
                    f"Manifest {label} is not registered in the coherent generation: {relative_path}",
                )
    if csv_path.read_bytes() != csv_bytes:
        raise MigrationError("MANIFEST_CHANGED_DURING_PARSE", "CSV changed while it was being parsed")
    validate_policy_contract(policy, mappings)
    catalog, alias_candidates = load_obsolete_catalog(root, policy, mappings)
    worktrees, worktree_raw = git_worktrees(root)
    index_sha = git_index_hash(root)
    (root / RUNTIME_RELATIVE).mkdir(parents=True, exist_ok=True)
    inventory, closure_inventory, files, blockers, full_observation_sha, inventory_entry_count = walk_inventory(
        root, policy, mappings, worktrees
    )
    hits = scan_references(files, mappings)
    alias_occurrences, alias_probe_blockers = scan_catalog_occurrences(
        root, policy, catalog, iter_full_observation(root)
    )
    blockers.extend(alias_probe_blockers)
    structured_occurrences, structured_blockers = scan_structured_occurrences(files, catalog)
    blockers.extend(structured_blockers)
    probe_classifications = {str(item) for item in policy.get("scan", {}).get("catalog_probe_classifications", [])}
    zip_occurrences, zip_blockers = scan_zip_occurrences(
        root, catalog, iter_full_observation(root), probe_classifications
    )
    alias_occurrences.extend(zip_occurrences)
    alias_occurrences = sorted(
        {stable_hash(asdict(item)): item for item in alias_occurrences}.values(),
        key=lambda item: (_path_identity(item.path), item.location, item.entry_id),
    )
    blockers.extend(zip_blockers)
    physical_inventory, physical_operations, physical_blockers = build_physical_inventory(
        root, policy, catalog, inventory
    )
    blockers.extend(physical_blockers)
    operation_manifest = _operation_side_effects(physical_operations)
    catalog_mappings = [MappingRow(item.entry_id, "catalog", item.source, item.canonical) for item in catalog]
    sqlite_hits, sqlite_blockers = scan_sqlite(root, policy, catalog_mappings)
    blockers.extend(sqlite_blockers)
    reconciliations, writes, generator_actions, write_blockers, payload_bytes = build_reconciliation_and_writes(
        root, resolved_policy, policy, mappings, catalog, files, hits, operation_manifest
    )
    blockers.extend(write_blockers)
    for operation in operation_manifest:
        candidate_paths = [operation.target]
        if operation.source:
            candidate_paths.append(operation.source)
        for relative_path in candidate_paths:
            if transition_snapshot.resolver.resolve_operation_path(relative_path) is None:
                blockers.append({"code": "UNREGISTERED_OPERATION_PATH", "path": relative_path})
    for write in writes:
        if transition_snapshot.resolver.resolve_operation_path(write.path) is None:
            blockers.append({"code": "UNREGISTERED_WRITE_PATH", "path": write.path})
    runtime = root / RUNTIME_RELATIVE
    (runtime / "payload").mkdir(parents=True, exist_ok=True)
    desired_payloads: dict[str, bytes] = {}
    # A second pure build must be byte-for-byte identical before runtime
    # evidence is published.
    reconciliations_2, writes_2, generator_actions_2, write_blockers_2, payload_bytes_2 = (
        build_reconciliation_and_writes(
            root, resolved_policy, policy, mappings, catalog, files, hits, operation_manifest
        )
    )
    if (
        writes != writes_2
        or reconciliations != reconciliations_2
        or generator_actions != generator_actions_2
        or write_blockers != write_blockers_2
        or payload_bytes != payload_bytes_2
    ):
        blockers.append({"code": "NONDETERMINISTIC_PLAN_BUILDER", "detail": "two pure build passes disagreed"})
    generator_check_results, generator_check_blockers = run_generator_checks(root, policy)
    generator_actions.extend(generator_check_results)
    blockers.extend(generator_check_blockers)
    for write in writes:
        data = payload_bytes.get(write.path)
        if data is None or sha256_bytes(data) != write.postimage_sha256:
            blockers.append({"code": "POSTIMAGE_MATERIALIZATION_MISMATCH", "path": write.path})
            continue
        desired_payloads[write.payload] = data
    for relative, data in desired_payloads.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_bytes(target, data)
    for write in writes:
        if not write.preimage_payload or not write.preimage_sha256:
            continue
        current = root / write.path
        if not current.is_file():
            blockers.append({"code": "PREIMAGE_DISAPPEARED_DURING_PLAN", "path": write.path})
            continue
        raw = current.read_bytes()
        if sha256_bytes(raw) != write.preimage_sha256:
            blockers.append({"code": "PREIMAGE_CHANGED_DURING_PLAN", "path": write.path})
            continue
        preimage_target = root / write.preimage_payload
        preimage_target.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_bytes(preimage_target, raw)
    planned_paths = {_path_identity(item.path) for item in writes}
    for occurrence in alias_occurrences:
        if (
            occurrence.disposition in {"rewrite", "generator-regenerate"}
            and _path_identity(occurrence.path) not in planned_paths
        ):
            blockers.append(
                {
                    "code": "ALIAS_OCCURRENCE_NOT_MATERIALIZED",
                    "entry_id": occurrence.entry_id,
                    "path": occurrence.path,
                    "location": occurrence.location,
                    "disposition": occurrence.disposition,
                }
            )
        if occurrence.disposition == "unresolved":
            blockers.append(
                {
                    "code": "ALIAS_CANDIDATE_UNDISPOSITIONED",
                    "entry_id": occurrence.entry_id,
                    "path": occurrence.path,
                    "location": occurrence.location,
                }
            )
    residuals, exceptions, residual_blockers = classify_residuals(root, mappings, files, hits, writes, sqlite_hits)
    blockers.extend(residual_blockers)
    for relative, scanned in files.items():
        try:
            with open(scanned.native_path, "rb") as handle:
                current = handle.read()
        except OSError as exc:
            blockers.append({"code": "SNAPSHOT_FILE_DISAPPEARED", "path": relative, "detail": str(exc)})
            continue
        if current != scanned.raw:
            blockers.append({"code": "SNAPSHOT_FILE_DRIFT", "path": relative})
    if resolved_policy.read_bytes() != policy_bytes:
        blockers.append({"code": "POLICY_SNAPSHOT_DRIFT", "path": resolved_policy.relative_to(root).as_posix()})
    if csv_path.read_bytes() != csv_bytes:
        blockers.append({"code": "CSV_SNAPSHOT_DRIFT", "path": csv_path.relative_to(root).as_posix()})
    if git_index_hash(root) != index_sha:
        blockers.append({"code": "GIT_INDEX_CHANGED_DURING_PLAN"})
    _, worktree_raw_after = git_worktrees(root)
    if worktree_raw_after != worktree_raw:
        blockers.append({"code": "WORKTREE_REGISTRATION_CHANGED_DURING_PLAN"})
    root_stat_after = root.stat()
    if (root_stat_after.st_dev, root_stat_after.st_ino) != root_identity_before:
        blockers.append({"code": "ROOT_IDENTITY_CHANGED_DURING_PLAN"})
    if Path(__file__).read_bytes() != engine_bytes:
        blockers.append({"code": "ENGINE_CHANGED_DURING_PLAN"})
    (
        _inventory_after,
        closure_inventory_after,
        _files_after,
        closure_probe_blockers,
        full_observation_after,
        inventory_entry_count_after,
    ) = walk_inventory(root, policy, mappings, worktrees)
    blockers.extend(closure_probe_blockers)
    if closure_inventory_after != closure_inventory:
        before_by_path = {str(item["path"]): item for item in closure_inventory}
        after_by_path = {str(item["path"]): item for item in closure_inventory_after}
        changed_paths = [
            {
                "path": path,
                "change": "added"
                if path not in before_by_path
                else "removed"
                if path not in after_by_path
                else "changed",
                "before": before_by_path.get(path),
                "after": after_by_path.get(path),
            }
            for path in sorted(set(before_by_path) | set(after_by_path), key=str.casefold)
            if before_by_path.get(path) != after_by_path.get(path)
        ]
        blockers.append(
            {
                "code": "CLOSURE_INVENTORY_CHANGED_DURING_ANALYSIS",
                "before": stable_hash(closure_inventory),
                "after": stable_hash(closure_inventory_after),
                "changed_paths": changed_paths,
            }
        )
    del _inventory_after, _files_after
    classifications = [
        {"path": item["path"], "classification": item["classification"], "rule_id": item["rule_id"]}
        for item in closure_inventory
    ]
    projection_material = {
        "generator_actions": generator_actions,
        "rule_projection_count": len(policy.get("rule_projections", [])),
    }
    write_material = [asdict(write) for write in writes]
    preimages = [{"path": write.path, "sha256": write.preimage_sha256, "mode": write.mode} for write in writes]
    retained_sources = _retained_source_ledger(root, mappings, physical_inventory)
    expected_final_closure = build_expected_final_closure(
        policy,
        catalog,
        closure_inventory,
        alias_occurrences,
        writes,
        payload_bytes,
        retained_sources,
        index_sha,
    )
    engine_sha = sha256_bytes(engine_bytes)
    hashes = {
        "full_observation_sha256": full_observation_after,
        "initial_full_observation_sha256": full_observation_sha,
        "closure_inventory_sha256": stable_hash(
            {"inventory": closure_inventory, "worktree_registration_sha256": sha256_bytes(worktree_raw)}
        ),
        "classification_sha256": stable_hash(classifications),
        "residual_sha256": stable_hash(residuals),
        "exception_sha256": stable_hash(exceptions),
        "projection_sha256": stable_hash(projection_material),
        "proposed_write_sha256": stable_hash(write_material),
        "preimage_set_sha256": stable_hash(preimages),
        "write_set_sha256": stable_hash([write.path for write in writes]),
        "git_index_sha256": index_sha,
        "csv_sha256": sha256_bytes(csv_bytes),
        "policy_sha256": sha256_bytes(policy_bytes),
        "engine_sha256": engine_sha,
        "scanner_sha256": engine_sha,
        "generator_input_sha256": _generator_input_hash(root),
        "catalog_sha256": stable_hash([asdict(item) for item in catalog]),
        "alias_occurrence_sha256": stable_hash([asdict(item) for item in alias_occurrences]),
        "structured_occurrence_sha256": stable_hash([asdict(item) for item in structured_occurrences]),
        "physical_inventory_sha256": stable_hash([asdict(item) for item in physical_inventory]),
        "operation_manifest_sha256": stable_hash([asdict(item) for item in operation_manifest]),
        "retained_source_sha256": stable_hash(retained_sources),
        "expected_final_closure_fingerprint": str(expected_final_closure["fingerprint"]),
    }
    closure_material = {
        "schema_version": SCHEMA_VERSION,
        **{
            key: hashes[key]
            for key in (
                "csv_sha256",
                "policy_sha256",
                "scanner_sha256",
                "closure_inventory_sha256",
                "classification_sha256",
                "residual_sha256",
                "exception_sha256",
                "projection_sha256",
                "proposed_write_sha256",
                "git_index_sha256",
                "catalog_sha256",
                "alias_occurrence_sha256",
                "structured_occurrence_sha256",
                "physical_inventory_sha256",
                "operation_manifest_sha256",
                "retained_source_sha256",
                "expected_final_closure_fingerprint",
            )
        },
    }
    hashes["closure_fingerprint"] = stable_hash(closure_material)
    blocker_map = {stable_hash(item): item for item in blockers}
    blockers = sorted(blocker_map.values(), key=stable_hash)
    plan_material = {
        "schema_version": SCHEMA_VERSION,
        "migration_id": str(policy.get("migration_id")),
        "manifest": [asdict(item) for item in mappings],
        "obsolete_catalog": [asdict(item) for item in catalog],
        "alias_candidates": [asdict(item) for item in alias_candidates],
        "alias_occurrences": [asdict(item) for item in alias_occurrences],
        "structured_occurrences": [asdict(item) for item in structured_occurrences],
        "physical_inventory": [asdict(item) for item in physical_inventory],
        "operation_manifest": [asdict(item) for item in operation_manifest],
        "retained_sources": retained_sources,
        "expected_final_closure": expected_final_closure,
        "reconciliations": reconciliations,
        "writes": write_material,
        "generator_actions": generator_actions,
        "residuals": residuals,
        "exceptions": exceptions,
        "blockers": blockers,
        "hashes": {key: value for key, value in hashes.items() if "full_observation" not in key},
    }
    plan_sha = stable_hash(plan_material)
    binding = {
        "schema_version": SCHEMA_VERSION,
        "plan_sha256": plan_sha,
        **{key: hashes[key] for key in _BINDING_KEYS if key not in {"schema_version", "plan_sha256"}},
    }
    if set(binding) != _BINDING_KEYS or any(
        not _DIGEST_RE.fullmatch(str(value)) for key, value in binding.items() if key != "schema_version"
    ):
        raise MigrationError("BINDING_BUILD_FAILED", "Generated migration binding is incomplete or malformed")
    analysis = Analysis(
        root,
        resolved_policy,
        policy,
        mappings,
        catalog,
        alias_candidates,
        inventory,
        inventory_entry_count_after,
        closure_inventory,
        worktrees,
        files,
        hits,
        alias_occurrences,
        structured_occurrences,
        physical_inventory,
        operation_manifest,
        retained_sources,
        expected_final_closure,
        reconciliations,
        writes,
        generator_actions,
        sqlite_hits,
        exceptions,
        blockers,
        hashes,
        plan_sha,
        binding,
    )
    return analysis, residuals


def _plan_material(analysis: Analysis, residuals: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "migration_id": str(analysis.policy.get("migration_id")),
        "manifest": [asdict(item) for item in analysis.mappings],
        "obsolete_catalog": [asdict(item) for item in analysis.catalog],
        "alias_candidates": [asdict(item) for item in analysis.alias_candidates],
        "alias_occurrences": [asdict(item) for item in analysis.alias_occurrences],
        "structured_occurrences": [asdict(item) for item in analysis.structured_occurrences],
        "physical_inventory": [asdict(item) for item in analysis.physical_inventory],
        "operation_manifest": [asdict(item) for item in analysis.operation_manifest],
        "retained_sources": analysis.retained_sources,
        "expected_final_closure": analysis.expected_final_closure,
        "reconciliations": analysis.reconciliations,
        "writes": [asdict(item) for item in analysis.writes],
        "generator_actions": analysis.generator_actions,
        "residuals": residuals,
        "exceptions": analysis.exceptions,
        "blockers": analysis.blockers,
        "hashes": {key: value for key, value in analysis.hashes.items() if "full_observation" not in key},
    }


def report_payload(analysis: Analysis, residuals: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    unresolved = [item for item in residuals if item.get("disposition") == "unresolved"]
    status = (
        "clean"
        if not analysis.blockers and not analysis.writes and not unresolved
        else "blocked"
        if analysis.blockers
        else "pending_writes"
    )
    plan_material = _plan_material(analysis, residuals)
    if stable_hash(plan_material) != analysis.plan_sha256:
        raise MigrationError("PLAN_HASH_DRIFT", "Published plan material does not match the computed plan hash")
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "status": status,
        "migration_id": str(analysis.policy.get("migration_id")),
        "project_root": analysis.root.as_posix(),
        "summary": {
            "manifest_rows": len(analysis.mappings),
            "catalog_entries": len(analysis.catalog),
            "alias_candidates": len(analysis.alias_candidates),
            "alias_occurrences": len(analysis.alias_occurrences),
            "structured_occurrences": len(analysis.structured_occurrences),
            "physical_occurrences": len(analysis.physical_inventory),
            "planned_operations": len(analysis.operation_manifest),
            "inventory_entries": analysis.inventory_entry_count,
            "worktrees": len(analysis.worktrees),
            "reference_hits": len(analysis.hits) + len(analysis.sqlite_hits),
            "unresolved_residuals": len(unresolved),
            "exceptions": len(analysis.exceptions),
            "proposed_writes": len(analysis.writes),
            "blockers": len(analysis.blockers),
        },
        "hashes": analysis.hashes,
        "plan_sha256": analysis.plan_sha256,
        "binding": analysis.binding,
        "binding_sha256": sha256_bytes(canonical_bytes(analysis.binding)),
        "plan_material": plan_material,
        "worktrees": [asdict(item) for item in analysis.worktrees],
    }


def publish_evidence(analysis: Analysis, residuals: list[dict[str, Any]], mode: str) -> tuple[Path, dict[str, Any]]:
    runtime = analysis.root / RUNTIME_RELATIVE
    runtime.mkdir(parents=True, exist_ok=True)
    report = report_payload(analysis, residuals, mode)
    report_path = runtime / f"{mode}.json"
    _atomic_write_bytes(
        report_path, json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n"
    )
    _atomic_write_bytes(runtime / "binding.json", canonical_bytes(analysis.binding))
    return report_path, report


def _load_plan(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MigrationError("PLAN_INVALID", f"Cannot load plan {path}: {exc}") from exc
    material = payload.get("plan_material")
    plan_sha = payload.get("plan_sha256")
    if not isinstance(material, dict) or stable_hash(material) != plan_sha:
        raise MigrationError("PLAN_HASH_INVALID", "Plan material hash does not match plan_sha256")
    binding = payload.get("binding")
    if not isinstance(binding, dict) or binding.get("plan_sha256") != plan_sha:
        raise MigrationError("PLAN_BINDING_INVALID", "Plan binding is missing or names another plan")
    _validate_binding(binding)
    return payload, material


def _validate_binding(binding: dict[str, Any]) -> None:
    if set(binding) != _BINDING_KEYS or binding.get("schema_version") != SCHEMA_VERSION:
        raise MigrationError("BINDING_SCHEMA_INVALID", "Migration binding has missing or unknown keys")
    for key, value in binding.items():
        if key != "schema_version" and not _DIGEST_RE.fullmatch(str(value)):
            raise MigrationError("BINDING_DIGEST_INVALID", f"Migration binding field {key} is not a canonical digest")


def _exact_metadata_match(pattern: re.Pattern[str], text: str, field: str) -> str:
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise MigrationError("BRIDGE_METADATA_INVALID", f"Expected exactly one {field}, found {len(matches)}")
    return str(matches[0]).strip()


def _binding_from_bridge(text: str) -> tuple[dict[str, Any], str]:
    raw = _exact_metadata_match(_BINDING_RE, text, "migration_plan_binding")
    try:
        binding = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MigrationError("BRIDGE_BINDING_JSON_INVALID", str(exc)) from exc
    if not isinstance(binding, dict):
        raise MigrationError("BRIDGE_BINDING_JSON_INVALID", "migration_plan_binding is not an object")
    _validate_binding(binding)
    if canonical_bytes(binding) != raw.encode("utf-8") + b"\n":
        raise MigrationError("BRIDGE_BINDING_NONCANONICAL", "migration_plan_binding JSON is not canonical")
    binding_sha = _exact_metadata_match(_BINDING_SHA_RE, text, "binding_sha256")
    if sha256_bytes(canonical_bytes(binding)) != binding_sha:
        raise MigrationError("BRIDGE_BINDING_HASH_INVALID", "binding_sha256 does not hash the canonical binding")
    return binding, binding_sha


def _safe_write_set(material: dict[str, Any]) -> list[str]:
    paths = [str(item.get("path") or "") for item in material.get("writes", []) if isinstance(item, dict)]
    if paths != sorted(paths, key=str.casefold) or len(paths) != len(set(paths)):
        raise MigrationError("WRITE_SET_NOT_SORTED_UNIQUE", "Plan write set is not sorted and unique")
    identities: set[str] = set()
    for path in paths:
        normalized = PurePosixPath(path)
        if (
            not path
            or normalized.is_absolute()
            or ".." in normalized.parts
            or path != normalized.as_posix()
            or any(char in path for char in "*?[")
            or "\\" in path
            or _nfc(path) != path
        ):
            raise MigrationError("WRITE_SET_PATH_INVALID", f"Unsafe exact write path: {path!r}")
        identity = _path_identity(path)
        if identity in identities:
            raise MigrationError("WRITE_SET_CASE_COLLISION", f"Windows path identity collision: {path}")
        identities.add(identity)
    return paths


def active_session_context_id() -> str:
    candidates = [
        os.environ.get("CODEX_THREAD_ID", "").strip(),
        os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip(),
        os.environ.get("GTKB_SESSION_CONTEXT_ID", "").strip(),
    ]
    unique = {item for item in candidates if item}
    if len(unique) != 1:
        raise MigrationError(
            "ACTIVE_SESSION_ID_UNRESOLVED",
            "Exactly one canonical active session-context environment value is required",
        )
    return unique.pop()


def authorize_apply(
    root: Path,
    plan_payload: dict[str, Any],
    material: dict[str, Any],
    *,
    session_id: str,
    require_migration_extension: bool = True,
) -> dict[str, Any]:
    active_session = active_session_context_id()
    if session_id != active_session:
        raise MigrationError(
            "SESSION_ID_MISMATCH", "Caller session id does not equal the active harness session context"
        )
    try:
        import bridge_lifecycle_resolver
        import bridge_review_independence
        import bridge_work_intent_registry
        import implementation_authorization
        from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance
    except ImportError as exc:
        raise MigrationError("AUTHORITY_IMPORT_FAILED", str(exc)) from exc
    try:
        resolution = bridge_lifecycle_resolver.resolve_bridge_lifecycle(root, CHILD_BRIDGE_ID)
    except Exception as exc:
        raise MigrationError("CHILD_LIFECYCLE_INVALID", f"Strict child lifecycle is unavailable: {exc}") from exc
    if (
        not resolution.audit_versions
        or any(not item.is_strict for item in resolution.audit_versions)
        or resolution.quarantined_paths
        or resolution.blocking_diagnostics
        or resolution.latest_strict_state.status != "GO"
        or resolution.implementation_artifact is None
        or resolution.implementation_verdict is None
        or resolution.implementation_verdict.path != resolution.latest_strict_state.path
    ):
        raise MigrationError(
            "CHILD_LIFECYCLE_INVALID", "Child lifecycle is not a strict proposal-to-GO implementation authority"
        )
    try:
        provenance = resolve_worker_role_provenance(root, current_session_id=active_session, harness_name=None)
    except (EnvelopeError, OSError, ValueError) as exc:
        raise MigrationError("SESSION_PROVENANCE_INVALID", str(exc)) from exc
    if provenance.get("role") != "prime-builder":
        raise MigrationError("SESSION_ROLE_INVALID", "Active session provenance is not Prime Builder")
    proposal_rel = resolution.implementation_artifact.path.replace("\\", "/")
    go_rel = resolution.implementation_verdict.path.replace("\\", "/")
    try:
        proposal_bytes = (root / proposal_rel).read_bytes()
        go_bytes = (root / go_rel).read_bytes()
        proposal_text = proposal_bytes.decode("utf-8", errors="strict")
        go_text = go_bytes.decode("utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise MigrationError("CHILD_ARTIFACT_UNREADABLE", str(exc)) from exc
    proposal_session = _exact_metadata_match(_AUTHOR_SESSION_RE, proposal_text, "proposal author_session_context_id")
    go_session = _exact_metadata_match(_AUTHOR_SESSION_RE, go_text, "GO author_session_context_id")
    reason = bridge_review_independence.self_review_reason(go_session, proposal_session)
    if reason:
        raise MigrationError("REVIEW_INDEPENDENCE_INVALID", reason)
    if resolution.implementation_artifact.author_role != "prime-builder":
        raise MigrationError("PROPOSAL_ROLE_INVALID", "Child proposal was not authored as Prime Builder")
    if resolution.implementation_verdict.author_role != "loyal-opposition":
        raise MigrationError("GO_ROLE_INVALID", "Child GO was not authored as Loyal Opposition")
    proposal_binding, proposal_binding_sha = _binding_from_bridge(proposal_text)
    go_binding, go_binding_sha = _binding_from_bridge(go_text)
    if proposal_binding != go_binding or proposal_binding_sha != go_binding_sha:
        raise MigrationError("GO_BINDING_MISMATCH", "Proposal and GO do not echo the same canonical binding")
    if proposal_binding != plan_payload.get("binding"):
        raise MigrationError("PLAN_BINDING_MISMATCH", "Reviewed bridge binding does not match the loaded plan")
    reviewed_file = _exact_metadata_match(_REVIEWED_FILE_RE, go_text, "reviewed_proposal_file").replace("\\", "/")
    reviewed_sha = _exact_metadata_match(_REVIEWED_SHA_RE, go_text, "reviewed_proposal_sha256")
    if reviewed_file != proposal_rel or reviewed_sha != sha256_bytes(proposal_bytes):
        raise MigrationError("REVIEWED_PROPOSAL_MISMATCH", "GO does not bind the exact strict proposal bytes")
    try:
        proposal_targets = json.loads(_exact_metadata_match(_TARGET_PATHS_RE, proposal_text, "target_paths"))
    except json.JSONDecodeError as exc:
        raise MigrationError("PROPOSAL_TARGETS_INVALID", str(exc)) from exc
    write_set = _safe_write_set(material)
    if proposal_targets != write_set:
        raise MigrationError(
            "PROPOSAL_WRITE_SET_MISMATCH", "Child target_paths do not equal the exact sorted plan write set"
        )
    try:
        holder = bridge_work_intent_registry.current_holder(CHILD_BRIDGE_ID, project_root=root)
        main_holder = bridge_work_intent_registry.current_holder(MAIN_BRIDGE_ID, project_root=root)
    except Exception as exc:
        raise MigrationError("CLAIM_READ_FAILED", str(exc)) from exc
    if main_holder is not None:
        raise MigrationError("OVERLAPPING_STAGE_CLAIM", "The main Stage A claim is still active")
    if (
        not holder
        or holder.get("thread_slug") != CHILD_BRIDGE_ID
        or holder.get("session_id") != session_id
        or holder.get("claim_kind") != "go_implementation"
        or holder.get("acting_role") != "prime-builder"
    ):
        raise MigrationError(
            "CHILD_CLAIM_INVALID", "Current session does not hold the exact child GO-implementation claim"
        )
    try:
        packet = implementation_authorization.load_named_packet(root, CHILD_BRIDGE_ID)
    except Exception as exc:
        raise MigrationError("CHILD_PACKET_INVALID", str(exc)) from exc
    start = packet.get("implementation_start")
    if (
        packet.get("schema_version") != 3
        or not isinstance(start, dict)
        or packet.get("bridge_id") != CHILD_BRIDGE_ID
        or packet.get("latest_status") != "GO"
        or str(packet.get("proposal_file") or "").replace("\\", "/") != proposal_rel
        or str(packet.get("go_file") or "").replace("\\", "/") != go_rel
        or start.get("bridge_id") != CHILD_BRIDGE_ID
        or start.get("session_id") != session_id
    ):
        raise MigrationError(
            "CHILD_PACKET_BINDING_INVALID",
            "Named schema-v3 packet does not bind the strict child lifecycle and session",
        )
    packet_targets = [str(item) for item in packet.get("target_path_globs", [])]
    start_targets = [str(item) for item in start.get("target_path_globs", [])]
    if packet_targets != write_set or start_targets != write_set:
        raise MigrationError("PACKET_WRITE_SET_MISMATCH", "Packet target paths do not equal the exact plan write set")
    provenance = start.get("worker_role_provenance")
    if not isinstance(provenance, dict) or provenance.get("role") != "prime-builder":
        raise MigrationError("PACKET_ROLE_INVALID", "Implementation packet lacks Prime Builder worker provenance")
    claim_snapshot = start.get("work_intent_claim")
    required_claim_fields = (
        "thread_slug",
        "session_id",
        "acquired_at",
        "ttl_expires_at",
        "claim_kind",
        "acting_role",
        "project_id",
        "implementation_deadline",
        "implementation_grace_expires_at",
        "extensions_used",
        "extension_cap_seconds",
    )
    if not isinstance(claim_snapshot, dict) or any(
        claim_snapshot.get(key) != holder.get(key) for key in required_claim_fields
    ):
        raise MigrationError("PACKET_CLAIM_SNAPSHOT_STALE", "Packet claim snapshot differs from the live child claim")
    extension = packet.get("migration_apply_authorization")
    expected_extension = {
        "schema_version": 1,
        "proposal_sha256": sha256_bytes(proposal_bytes),
        "go_sha256": sha256_bytes(go_bytes),
        "binding_sha256": proposal_binding_sha,
    }
    if require_migration_extension and extension != expected_extension:
        raise MigrationError(
            "PACKET_MIGRATION_EXTENSION_INVALID", "Packet is not content-bound to the reviewed migration plan"
        )
    if extension is not None and extension != expected_extension:
        raise MigrationError("PACKET_MIGRATION_EXTENSION_INVALID", "Existing migration packet extension is incorrect")
    if not isinstance(packet.get("project_authorization"), dict):
        raise MigrationError(
            "ACTIVE_PAUTH_REQUIRED", "Migration apply requires a packet-bound active Project Authorization"
        )
    try:
        pauth = implementation_authorization.validate_packet_project_authorization_operation(
            root, packet, requested_operations=["protected_mutation"], target_paths=write_set
        )
    except Exception as exc:
        raise MigrationError("ACTIVE_PAUTH_INVALID", str(exc)) from exc
    if pauth is None:
        raise MigrationError("ACTIVE_PAUTH_REQUIRED", "Project Authorization validation returned no active authority")
    return {
        "proposal_file": proposal_rel,
        "go_file": go_rel,
        "proposal_sha256": sha256_bytes(proposal_bytes),
        "go_sha256": sha256_bytes(go_bytes),
        "binding_sha256": proposal_binding_sha,
        "packet_hash": packet.get("packet_hash"),
        "claim": {key: holder.get(key) for key in required_claim_fields},
        "write_set": write_set,
        "migration_apply_authorization": expected_extension,
    }


def bind_migration_packet(root: Path, plan_path: Path, *, session_id: str | None = None) -> dict[str, Any]:
    session_id = session_id or active_session_context_id()
    plan_payload, material = _load_plan(plan_path)
    with _operation_lock(root):
        authority = authorize_apply(
            root, plan_payload, material, session_id=session_id, require_migration_extension=False
        )
        try:
            import implementation_authorization

            packet = implementation_authorization.load_named_packet(root, CHILD_BRIDGE_ID)
            bound = dict(packet)
            bound.pop("packet_hash", None)
            bound["migration_apply_authorization"] = authority["migration_apply_authorization"]
            bound["packet_hash"] = implementation_authorization.packet_hash(bound)
            implementation_authorization.write_started_packets(root, [bound])
            implementation_authorization.load_named_packet(root, CHILD_BRIDGE_ID)
        except Exception as exc:
            raise MigrationError("PACKET_BIND_FAILED", str(exc)) from exc
        authorize_apply(root, plan_payload, material, session_id=session_id)
        return {
            "schema_version": 1,
            "status": "bound",
            "bridge_id": CHILD_BRIDGE_ID,
            "packet_hash": bound["packet_hash"],
            "migration_apply_authorization": authority["migration_apply_authorization"],
        }


def _path_is_reparse(path: Path) -> bool:
    info = path.lstat()
    attributes = int(getattr(info, "st_file_attributes", 0))
    return path.is_symlink() or bool(attributes & int(getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)))


class WindowsPathGuard:
    """Validate no-reparse ancestry and hold child locks during mutation."""

    DELETE = 0x00010000
    SYNCHRONIZE = 0x00100000
    GENERIC_READ = 0x80000000
    GENERIC_WRITE = 0x40000000
    FILE_READ_ATTRIBUTES = 0x0080
    FILE_WRITE_ATTRIBUTES = 0x0100
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    OPEN_EXISTING = 3
    CREATE_NEW = 1
    FILE_OPEN = 1
    FILE_CREATE = 2
    FILE_DIRECTORY_FILE = 0x00000001
    FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020
    FILE_NON_DIRECTORY_FILE = 0x00000040
    FILE_OPEN_REPARSE_POINT = 0x00200000
    OBJ_CASE_INSENSITIVE = 0x00000040
    OBJ_DONT_REPARSE = 0x00001000
    FILE_RENAME_INFORMATION = 10
    FILE_ATTRIBUTE_TEMPORARY = 0x00000100
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    FILE_FLAG_DELETE_ON_CLOSE = 0x04000000
    FILE_DELETE_ON_CLOSE = 0x00001000
    FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
    FILE_ID_INFO_CLASS = 18
    FILE_ATTRIBUTE_TAG_INFO_CLASS = 9
    FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400

    def __init__(self, root: Path):
        if os.name != "nt":
            raise MigrationError(
                "PLATFORM_SAFETY_UNSUPPORTED",
                "Repository mutation requires the Windows no-reparse handle adapter",
            )
        from ctypes import wintypes

        class FileId128(ctypes.Structure):
            _fields_ = [("Identifier", ctypes.c_ubyte * 16)]

        class FileIdInfo(ctypes.Structure):
            _fields_ = [("VolumeSerialNumber", ctypes.c_ulonglong), ("FileId", FileId128)]

        class FileAttributeTagInfo(ctypes.Structure):
            _fields_ = [("FileAttributes", wintypes.DWORD), ("ReparseTag", wintypes.DWORD)]

        class UnicodeString(ctypes.Structure):
            _fields_ = [
                ("Length", wintypes.USHORT),
                ("MaximumLength", wintypes.USHORT),
                ("Buffer", wintypes.LPWSTR),
            ]

        class ObjectAttributes(ctypes.Structure):
            _fields_ = [
                ("Length", wintypes.ULONG),
                ("RootDirectory", wintypes.HANDLE),
                ("ObjectName", ctypes.POINTER(UnicodeString)),
                ("Attributes", wintypes.ULONG),
                ("SecurityDescriptor", wintypes.LPVOID),
                ("SecurityQualityOfService", wintypes.LPVOID),
            ]

        class IosbValue(ctypes.Union):
            _fields_ = [("Status", ctypes.c_int32), ("Pointer", wintypes.LPVOID)]

        class IoStatusBlock(ctypes.Structure):
            _anonymous_ = ("value",)
            _fields_ = [("value", IosbValue), ("Information", ctypes.c_size_t)]

        class FileRenameHead(ctypes.Structure):
            _fields_ = [
                ("ReplaceIfExists", wintypes.BOOLEAN),
                ("RootDirectory", wintypes.HANDLE),
                ("FileNameLength", wintypes.ULONG),
            ]

        self._wintypes = wintypes
        self._FileIdInfo = FileIdInfo
        self._FileAttributeTagInfo = FileAttributeTagInfo
        self._UnicodeString = UnicodeString
        self._ObjectAttributes = ObjectAttributes
        self._IoStatusBlock = IoStatusBlock
        self._FileRenameHead = FileRenameHead
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        self._kernel32.CreateFileW.restype = wintypes.HANDLE
        self._kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._kernel32.GetFileInformationByHandleEx.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            wintypes.LPVOID,
            wintypes.DWORD,
        ]
        self._kernel32.GetFileInformationByHandleEx.restype = wintypes.BOOL
        self._kernel32.GetFinalPathNameByHandleW.argtypes = [
            wintypes.HANDLE,
            wintypes.LPWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
        ]
        self._kernel32.GetFinalPathNameByHandleW.restype = wintypes.DWORD
        self._kernel32.DuplicateHandle.argtypes = [
            wintypes.HANDLE,
            wintypes.HANDLE,
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.HANDLE),
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        ]
        self._kernel32.DuplicateHandle.restype = wintypes.BOOL
        self._kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        self._ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
        self._ntdll.NtCreateFile.argtypes = [
            ctypes.POINTER(wintypes.HANDLE),
            wintypes.DWORD,
            ctypes.POINTER(ObjectAttributes),
            ctypes.POINTER(IoStatusBlock),
            ctypes.c_void_p,
            wintypes.ULONG,
            wintypes.ULONG,
            wintypes.ULONG,
            wintypes.ULONG,
            ctypes.c_void_p,
            wintypes.ULONG,
        ]
        self._ntdll.NtCreateFile.restype = ctypes.c_int32
        self._ntdll.NtSetInformationFile.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(IoStatusBlock),
            ctypes.c_void_p,
            wintypes.ULONG,
            wintypes.ULONG,
        ]
        self._ntdll.NtSetInformationFile.restype = ctypes.c_int32
        self._ntdll.RtlNtStatusToDosError.argtypes = [ctypes.c_int32]
        self._ntdll.RtlNtStatusToDosError.restype = wintypes.ULONG
        if ctypes.sizeof(ctypes.c_void_p) != 8 or (
            ctypes.sizeof(UnicodeString),
            ctypes.sizeof(ObjectAttributes),
            ctypes.sizeof(IoStatusBlock),
        ) != (16, 48, 16):
            raise MigrationError("WINDOWS_ABI_UNSUPPORTED", "Handle-relative adapter requires the validated x64 ABI")
        if FileRenameHead.RootDirectory.offset != 8 or FileRenameHead.FileNameLength.offset != 16:
            raise MigrationError("WINDOWS_ABI_UNSUPPORTED", "FILE_RENAME_INFORMATION layout is unexpected")
        self.root = Path(os.path.abspath(str(root)))
        self._handles: dict[str, tuple[Any, PathIdentity]] = {}
        self._namespace_handles: list[tuple[Any, PathIdentity, str]] = []
        self._namespace_parents: set[str] = set()
        handle, identity = self._open(self.root, directory=True, deny_delete=True)
        self._handles[_path_identity(str(self.root))] = (handle, identity)
        if identity.reparse_tag or identity.attributes & self.FILE_ATTRIBUTE_REPARSE_POINT:
            self.close()
            raise MigrationError("ROOT_REPARSE_FORBIDDEN", "Project root is a reparse point")
        self.root_identity = identity
        self._root_final = self._normalize_final(identity.final_path)

    @staticmethod
    def _normalize_final(value: str) -> str:
        if value.startswith("\\\\?\\UNC\\"):
            value = "\\\\" + value[8:]
        elif value.startswith("\\\\?\\"):
            value = value[4:]
        return os.path.normcase(os.path.abspath(value))

    def _error(self, operation: str, path: Path) -> MigrationError:
        code = ctypes.get_last_error()
        return MigrationError("WIN32_PATH_GUARD_FAILED", f"{operation} failed for {path}: WinError {code}")

    def _nt_error(self, operation: str, status: int, leaf: str) -> MigrationError:
        unsigned = status & 0xFFFFFFFF
        winerror = int(self._ntdll.RtlNtStatusToDosError(status))
        return MigrationError(
            "WIN32_HANDLE_OPERATION_FAILED",
            f"{operation} failed for literal {leaf!r}: NTSTATUS 0x{unsigned:08X}, WinError {winerror}",
        )

    @staticmethod
    def _validate_leaf(leaf: str) -> None:
        if leaf in {"", ".", ".."} or any(character in leaf for character in ("/", "\\", ":", "\x00")):
            raise MigrationError("UNSAFE_LITERAL_PATH", f"Unsafe one-component path: {leaf!r}")

    def _nt_open_relative(
        self,
        parent_handle: Any,
        leaf: str,
        *,
        desired_access: int,
        share_access: int,
        disposition: int,
        directory: bool | None,
        file_attributes: int = 0,
        extra_options: int = 0,
        missing_ok: bool = False,
    ) -> tuple[Any, PathIdentity] | None:
        self._validate_leaf(leaf)
        encoded = leaf.encode("utf-16-le")
        buffer = ctypes.create_unicode_buffer(leaf)
        name = self._UnicodeString(len(encoded), len(encoded) + 2, ctypes.cast(buffer, self._wintypes.LPWSTR))
        attributes = self._ObjectAttributes(
            ctypes.sizeof(self._ObjectAttributes),
            parent_handle,
            ctypes.pointer(name),
            self.OBJ_CASE_INSENSITIVE | self.OBJ_DONT_REPARSE,
            None,
            None,
        )
        io_status = self._IoStatusBlock()
        handle = self._wintypes.HANDLE()
        options = self.FILE_OPEN_REPARSE_POINT | self.FILE_SYNCHRONOUS_IO_NONALERT | extra_options
        if directory is not None:
            options |= self.FILE_DIRECTORY_FILE if directory else self.FILE_NON_DIRECTORY_FILE
        status = int(
            self._ntdll.NtCreateFile(
                ctypes.byref(handle),
                desired_access | self.SYNCHRONIZE,
                ctypes.byref(attributes),
                ctypes.byref(io_status),
                None,
                file_attributes,
                share_access,
                disposition,
                options,
                None,
                0,
            )
        )
        if status < 0:
            winerror = int(self._ntdll.RtlNtStatusToDosError(status))
            if missing_ok and winerror in {2, 3}:
                return None
            raise self._nt_error("NtCreateFile", status, leaf)
        try:
            identity = self._identity(handle)
            if identity.reparse_tag or identity.attributes & self.FILE_ATTRIBUTE_REPARSE_POINT:
                raise MigrationError("REPARSE_OBJECT_FORBIDDEN", f"Reparse object is not a literal target: {leaf}")
            return handle, identity
        except BaseException:
            self._kernel32.CloseHandle(handle)
            raise

    def _parent_handle(self, target: Path) -> Any:
        self.guard_target(target)
        held = self._handles.get(_path_identity(str(target.parent)))
        if held is None:
            raise MigrationError("DIRECTORY_HANDLE_MISSING", f"No held parent handle for target: {target}")
        return held[0]

    def open_target_for_swap(self, target: Path) -> tuple[Any, PathIdentity]:
        opened = self._nt_open_relative(
            self._parent_handle(target),
            target.name,
            desired_access=self.GENERIC_READ | self.DELETE | self.FILE_READ_ATTRIBUTES,
            share_access=self.FILE_SHARE_READ,
            disposition=self.FILE_OPEN,
            directory=False,
        )
        assert opened is not None
        return opened

    def read_handle_bytes(self, handle: Any) -> bytes:
        import msvcrt

        duplicate = self._wintypes.HANDLE()
        process = self._kernel32.GetCurrentProcess()
        if not self._kernel32.DuplicateHandle(process, handle, process, ctypes.byref(duplicate), 0, False, 0x00000002):
            raise self._error("DuplicateHandle", self.root)
        descriptor = msvcrt.open_osfhandle(int(duplicate.value), os.O_RDONLY | os.O_BINARY)
        with os.fdopen(descriptor, "rb") as stream:
            stream.seek(0)
            return stream.read()

    def rename_handle(self, handle: Any, parent_handle: Any, destination_leaf: str) -> None:
        self._validate_leaf(destination_leaf)
        encoded = destination_leaf.encode("utf-16-le")
        filename_offset = self._FileRenameHead.FileNameLength.offset + ctypes.sizeof(self._wintypes.ULONG)
        payload = ctypes.create_string_buffer(filename_offset + len(encoded))
        header = self._FileRenameHead.from_buffer(payload)
        header.ReplaceIfExists = False
        header.RootDirectory = parent_handle
        header.FileNameLength = len(encoded)
        ctypes.memmove(ctypes.addressof(payload) + filename_offset, encoded, len(encoded))
        io_status = self._IoStatusBlock()
        status = int(
            self._ntdll.NtSetInformationFile(
                handle,
                ctypes.byref(io_status),
                payload,
                len(payload),
                self.FILE_RENAME_INFORMATION,
            )
        )
        if status < 0:
            raise self._nt_error("NtSetInformationFile(FileRenameInformation)", status, destination_leaf)

    def _identity(self, handle: Any) -> PathIdentity:
        file_info = self._FileIdInfo()
        if not self._kernel32.GetFileInformationByHandleEx(
            handle, self.FILE_ID_INFO_CLASS, ctypes.byref(file_info), ctypes.sizeof(file_info)
        ):
            raise self._error("GetFileInformationByHandleEx(FileIdInfo)", self.root)
        tag_info = self._FileAttributeTagInfo()
        if not self._kernel32.GetFileInformationByHandleEx(
            handle,
            self.FILE_ATTRIBUTE_TAG_INFO_CLASS,
            ctypes.byref(tag_info),
            ctypes.sizeof(tag_info),
        ):
            raise self._error("GetFileInformationByHandleEx(FileAttributeTagInfo)", self.root)
        buffer = ctypes.create_unicode_buffer(32768)
        length = self._kernel32.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0)
        if not length or length >= len(buffer):
            raise self._error("GetFinalPathNameByHandleW", self.root)
        return PathIdentity(
            int(file_info.VolumeSerialNumber),
            bytes(file_info.FileId.Identifier).hex(),
            int(tag_info.FileAttributes),
            int(tag_info.ReparseTag),
            buffer.value,
        )

    def _open(self, path: Path, *, directory: bool, deny_delete: bool) -> tuple[Any, PathIdentity]:
        share = self.FILE_SHARE_READ | self.FILE_SHARE_WRITE
        if not deny_delete:
            share |= 0x00000004
        flags = self.FILE_FLAG_OPEN_REPARSE_POINT | (self.FILE_FLAG_BACKUP_SEMANTICS if directory else 0)
        handle = self._kernel32.CreateFileW(
            _native_path(path),
            self.FILE_READ_ATTRIBUTES,
            share,
            None,
            self.OPEN_EXISTING,
            flags,
            None,
        )
        if handle == self._wintypes.HANDLE(-1).value:
            raise self._error("CreateFileW", path)
        try:
            identity = self._identity(handle)
        except BaseException:
            self._kernel32.CloseHandle(handle)
            raise
        return handle, identity

    def _assert_contained(self, identity: PathIdentity, path: Path) -> None:
        final = self._normalize_final(identity.final_path)
        try:
            common = os.path.commonpath([self._root_final, final])
        except ValueError as exc:
            raise MigrationError("HANDLE_PATH_OUTSIDE_ROOT", f"Handle path is on another volume: {path}") from exc
        if os.path.normcase(common) != self._root_final:
            raise MigrationError("HANDLE_PATH_OUTSIDE_ROOT", f"Handle resolved outside the project root: {path}")
        if identity.reparse_tag or identity.attributes & self.FILE_ATTRIBUTE_REPARSE_POINT:
            raise MigrationError("REPARSE_OBJECT_FORBIDDEN", f"Reparse object is not a literal mutation target: {path}")

    def guard_target(self, target: Path) -> None:
        try:
            relative = target.relative_to(self.root)
        except ValueError as exc:
            raise MigrationError("WRITE_OUTSIDE_ROOT", f"Write target escapes root: {target}") from exc
        if any(part in {"", ".", ".."} or "\x00" in part or ":" in part for part in relative.parts):
            raise MigrationError("UNSAFE_LITERAL_PATH", f"Unsafe literal target: {relative.as_posix()}")
        current = self.root
        parent_handle = self._handles[_path_identity(str(self.root))][0]
        complete_parent = True
        for part in relative.parts[:-1]:
            current /= part
            key = _path_identity(str(current))
            if key not in self._handles:
                opened = self._nt_open_relative(
                    parent_handle,
                    part,
                    desired_access=self.FILE_READ_ATTRIBUTES,
                    share_access=self.FILE_SHARE_READ | self.FILE_SHARE_WRITE | 0x00000004,
                    disposition=self.FILE_OPEN,
                    directory=True,
                    missing_ok=True,
                )
                if opened is None:
                    complete_parent = False
                    break
                handle, identity = opened
                try:
                    self._assert_contained(identity, current)
                except BaseException:
                    self._kernel32.CloseHandle(handle)
                    raise
                self._handles[key] = (handle, identity)
            else:
                handle, identity = self._handles[key]
                current_identity = self._identity(handle)
                if current_identity != identity:
                    raise MigrationError("ANCESTOR_IDENTITY_DRIFT", f"Ancestor identity changed: {current}")
            parent_handle = handle
        if complete_parent:
            opened = self._nt_open_relative(
                parent_handle,
                relative.parts[-1],
                desired_access=self.FILE_READ_ATTRIBUTES,
                share_access=self.FILE_SHARE_READ | self.FILE_SHARE_WRITE | 0x00000004,
                disposition=self.FILE_OPEN,
                directory=None,
                missing_ok=True,
            )
            if opened is None:
                return
            handle, identity = opened
            try:
                self._assert_contained(identity, target)
            finally:
                self._kernel32.CloseHandle(handle)

    def register_created_directory(self, directory: Path) -> PathIdentity:
        self.guard_target(directory / ".gtkb-register-probe")
        held = self._handles.get(_path_identity(str(directory)))
        if held is None:
            raise MigrationError("DIRECTORY_HANDLE_MISSING", f"Cannot register directory: {directory}")
        return held[1]

    def target_identity(self, target: Path) -> PathIdentity | None:
        self.guard_target(target)
        held = self._handles.get(_path_identity(str(target.parent)))
        if held is None:
            return None
        opened = self._nt_open_relative(
            held[0],
            target.name,
            desired_access=self.FILE_READ_ATTRIBUTES,
            share_access=self.FILE_SHARE_READ | self.FILE_SHARE_WRITE | 0x00000004,
            disposition=self.FILE_OPEN,
            directory=None,
            missing_ok=True,
        )
        if opened is None:
            return None
        handle, identity = opened
        try:
            self._assert_contained(identity, target)
            return identity
        finally:
            self._kernel32.CloseHandle(handle)

    def hold_namespace(self, target: Path) -> PathIdentity:
        """Lock a target parent and its ancestors with a delete-on-close child."""

        self.guard_target(target)
        parent = target.parent
        held = self._handles.get(_path_identity(str(parent)))
        if held is None:
            raise MigrationError("TARGET_PARENT_MISSING", f"Target parent does not exist: {parent}")
        return self._hold_directory_namespace(parent, held[0])

    def _hold_directory_namespace(self, parent: Path, parent_handle: Any) -> PathIdentity:
        key = _path_identity(str(parent))
        if key in self._namespace_parents:
            return self._identity(parent_handle)
        sentinel = f".gtkb-wi5640-guard-{uuid.uuid4().hex}.tmp"
        opened = self._nt_open_relative(
            parent_handle,
            sentinel,
            desired_access=self.DELETE | self.FILE_READ_ATTRIBUTES,
            share_access=self.FILE_SHARE_READ | self.FILE_SHARE_WRITE,
            disposition=self.FILE_CREATE,
            directory=False,
            file_attributes=self.FILE_ATTRIBUTE_TEMPORARY,
            extra_options=self.FILE_DELETE_ON_CLOSE,
        )
        assert opened is not None
        handle, identity = opened
        try:
            self._assert_contained(identity, parent / sentinel)
            final_parent = self._normalize_final(identity.final_path).rsplit(os.sep, 1)[0]
            if final_parent != os.path.normcase(os.path.abspath(str(parent))):
                raise MigrationError(
                    "NAMESPACE_PARENT_DRIFT", f"Namespace sentinel resolved under another parent: {parent}"
                )
            self._namespace_handles.append((handle, identity, key))
            self._namespace_parents.add(key)
            return identity
        except BaseException:
            self._kernel32.CloseHandle(handle)
            raise

    def release_directory(self, directory: Path, expected: PathIdentity) -> None:
        key = _path_identity(str(directory))
        held = self._handles.get(key)
        if held is None:
            raise MigrationError("DIRECTORY_HANDLE_MISSING", f"No held handle for created directory: {directory}")
        handle, original = held
        current = self._identity(handle)
        if original != expected or current != expected:
            raise MigrationError("DIRECTORY_IDENTITY_DRIFT", f"Created directory identity changed: {directory}")
        self._kernel32.CloseHandle(handle)
        del self._handles[key]

    def release_namespace(self, directory: Path) -> None:
        key = _path_identity(str(directory))
        retained: list[tuple[Any, PathIdentity, str]] = []
        found = False
        for handle, identity, parent_key in self._namespace_handles:
            if parent_key == key:
                self._kernel32.CloseHandle(handle)
                found = True
            else:
                retained.append((handle, identity, parent_key))
        self._namespace_handles = retained
        if found:
            self._namespace_parents.discard(key)

    def close(self) -> None:
        for handle, _identity, _parent_key in reversed(self._namespace_handles):
            self._kernel32.CloseHandle(handle)
        self._namespace_handles.clear()
        self._namespace_parents.clear()
        for handle, _identity in reversed(list(self._handles.values())):
            self._kernel32.CloseHandle(handle)
        self._handles.clear()

    def __enter__(self) -> WindowsPathGuard:
        return self

    def __exit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> None:
        self.close()


def _literal_read_bytes(path: Path) -> bytes | None:
    try:
        with open(_native_path(path), "rb") as handle:
            return handle.read()
    except FileNotFoundError:
        return None


def _fsync_directory(path: Path) -> None:
    if os.name != "nt":
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.FlushFileBuffers.argtypes = [wintypes.HANDLE]
    kernel32.FlushFileBuffers.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.CreateFileW(
        _native_path(path),
        0x0080,
        0x00000001 | 0x00000002 | 0x00000004,
        None,
        3,
        0x02000000 | 0x00200000,
        None,
    )
    if handle == wintypes.HANDLE(-1).value:
        raise MigrationError("DIRECTORY_FSYNC_OPEN_FAILED", f"Cannot open directory for durability flush: {path}")
    try:
        if not kernel32.FlushFileBuffers(handle):
            error = ctypes.get_last_error()
            # Windows exposes no portable directory-fsync primitive. NTFS
            # commonly returns ACCESS_DENIED for FlushFileBuffers on a directory
            # handle even though the file/journal handle itself was flushed.
            if error not in {1, 5, 6}:
                raise MigrationError("DIRECTORY_FSYNC_FAILED", f"FlushFileBuffers failed for {path}: WinError {error}")
    finally:
        kernel32.CloseHandle(handle)


def _durable_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=_native_path(path.parent))
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(_native_path(temporary), _native_path(path))
        _fsync_directory(path.parent)
    finally:
        if os.path.exists(_native_path(temporary)):
            os.unlink(_native_path(temporary))


class TransactionJournal:
    def __init__(self, root: Path, transaction_id: str, records: list[dict[str, Any]] | None = None):
        self.root = root
        self.transaction_id = transaction_id
        self.directory = root / _TRANSACTION_DIRECTORY / transaction_id
        self.path = self.directory / "journal.jsonl"
        self.report_path = self.directory / "transaction.json"
        self.records = records or []

    @classmethod
    def create(cls, root: Path, transaction_id: str, header: dict[str, Any]) -> TransactionJournal:
        journal = cls(root, transaction_id)
        journal.directory.mkdir(parents=True, exist_ok=False)
        _fsync_directory(journal.directory.parent)
        journal.append("prepared", header)
        return journal

    @classmethod
    def load(cls, root: Path, transaction_id: str) -> TransactionJournal:
        journal = cls(root, transaction_id)
        try:
            raw = journal.path.read_bytes()
        except OSError as exc:
            raise MigrationError("JOURNAL_UNREADABLE", f"Cannot read journal {journal.path}: {exc}") from exc
        if not raw or not raw.endswith(b"\n"):
            raise MigrationError("JOURNAL_TRUNCATED", f"Journal is empty or lacks a terminal LF: {journal.path}")
        records: list[dict[str, Any]] = []
        prior = "sha256:" + "0" * 64
        for sequence, line in enumerate(raw.splitlines(), start=0):
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise MigrationError("JOURNAL_JSON_INVALID", f"Journal record {sequence}: {exc}") from exc
            if (
                not isinstance(record, dict)
                or record.get("sequence") != sequence
                or record.get("previous_hash") != prior
            ):
                raise MigrationError("JOURNAL_CHAIN_INVALID", f"Journal sequence/hash link failed at record {sequence}")
            recorded_hash = record.get("record_hash")
            material = dict(record)
            material.pop("record_hash", None)
            if recorded_hash != stable_hash(material):
                raise MigrationError("JOURNAL_HASH_INVALID", f"Journal record hash failed at record {sequence}")
            prior = str(recorded_hash)
            records.append(record)
        journal.records = records
        return journal

    @property
    def terminal(self) -> bool:
        return bool(self.records and self.records[-1].get("event") in _TERMINAL_JOURNAL_EVENTS)

    @property
    def header(self) -> dict[str, Any]:
        if not self.records or self.records[0].get("event") != "prepared":
            raise MigrationError("JOURNAL_HEADER_INVALID", "Journal does not start with prepared")
        payload = self.records[0].get("payload")
        if not isinstance(payload, dict):
            raise MigrationError("JOURNAL_HEADER_INVALID", "Prepared journal record has no object payload")
        return payload

    def append(self, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.terminal:
            raise MigrationError("JOURNAL_TERMINAL", f"Cannot append {event!r} after a terminal journal event")
        sequence = len(self.records)
        material = {
            "schema_version": _JOURNAL_SCHEMA_VERSION,
            "transaction_id": self.transaction_id,
            "sequence": sequence,
            "event": event,
            "previous_hash": self.records[-1]["record_hash"] if self.records else "sha256:" + "0" * 64,
            "payload": payload,
        }
        record = {**material, "record_hash": stable_hash(material)}
        self.directory.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(_native_path(self.path), os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try:
            os.write(descriptor, canonical_bytes(record))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        _fsync_directory(self.directory)
        self.records.append(record)
        return record

    def write_report(self, payload: dict[str, Any]) -> Path:
        report = {
            **payload,
            "schema_version": 2,
            "transaction_id": self.transaction_id,
            "journal_sha256": sha256_bytes(self.path.read_bytes()),
            "journal_terminal_event": self.records[-1]["event"] if self.records else None,
        }
        _durable_write(self.report_path, json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n")
        _durable_write(
            root_report := self.root / RUNTIME_RELATIVE / "transaction.json",
            json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n",
        )
        return root_report


def _fault(point: str) -> None:
    configured = os.environ.get("GTKB_MIGRATION_FAULT", "")
    if configured == f"raise:{point}":
        raise MigrationError("INJECTED_FAULT", point)
    if configured == f"os_exit:{point}":
        os._exit(97)


def _lock_payload(root: Path) -> dict[str, Any] | None:
    path = root / _LOCK_RELATIVE
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MigrationError("LOCK_INVALID", f"Migration lock is unreadable: {exc}") from exc
    if not isinstance(payload, dict) or not payload.get("transaction_id") or not payload.get("journal"):
        raise MigrationError("LOCK_INVALID", "Migration lock lacks transaction/journal identity")
    return payload


def _assert_no_incomplete_transaction(root: Path) -> None:
    lock = _lock_payload(root)
    if lock is not None:
        transaction_id = str(lock["transaction_id"])
        journal = TransactionJournal.load(root, transaction_id)
        state = journal.records[-1]["event"]
        raise MigrationError(
            "RECOVERY_REQUIRED",
            f"Transaction {transaction_id} has lock state {state!r}; run the explicit recover command",
        )
    transactions = root / _TRANSACTION_DIRECTORY
    if not transactions.is_dir():
        return
    for directory in sorted(transactions.iterdir(), key=lambda item: item.name):
        if not directory.is_dir() or not (directory / "journal.jsonl").is_file():
            continue
        journal = TransactionJournal.load(root, directory.name)
        if not journal.terminal:
            raise MigrationError(
                "RECOVERY_REQUIRED",
                f"Transaction {directory.name} is nonterminal without a lock; run recover --transaction-id {directory.name}",
            )


@contextmanager
def _operation_lock(root: Path, journal: TransactionJournal, *, recovery: bool = False) -> Iterator[None]:
    path = root / _LOCK_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not recovery:
        raise MigrationError("APPLY_LOCK_HELD", f"Migration operation lock already exists: {path}")
    if path.exists() and recovery:
        existing = _lock_payload(root)
        if existing is None or existing.get("transaction_id") != journal.transaction_id:
            raise MigrationError("RECOVERY_LOCK_MISMATCH", "Existing lock names another transaction")
        path.unlink()
        _fsync_directory(path.parent)
    payload = {
        "schema_version": 2,
        "migration_id": "WI-5640",
        "pid": os.getpid(),
        "session_id": active_session_context_id(),
        "transaction_id": journal.transaction_id,
        "journal": journal.path.relative_to(root).as_posix(),
    }
    descriptor = os.open(_native_path(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, canonical_bytes(payload))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)
    try:
        yield
    finally:
        if journal.terminal and path.exists():
            path.unlink()
            _fsync_directory(path.parent)


def _ensure_parent_directories(
    root: Path,
    target: Path,
    guard: WindowsPathGuard,
    journal: TransactionJournal,
) -> list[dict[str, Any]]:
    guard.guard_target(target)
    created: list[dict[str, Any]] = []
    current = root
    parent_handle = guard._handles[_path_identity(str(root))][0]
    for part in target.relative_to(root).parts[:-1]:
        directory = current / part
        key = _path_identity(str(directory))
        held = guard._handles.get(key)
        if held is not None:
            parent_handle = held[0]
            current = directory
            continue
        guard._hold_directory_namespace(current, parent_handle)
        relative = directory.relative_to(root).as_posix()
        journal.append("directory_intent", {"path": relative})
        _fault("after_directory_intent")
        opened = guard._nt_open_relative(
            parent_handle,
            part,
            desired_access=guard.FILE_READ_ATTRIBUTES,
            share_access=guard.FILE_SHARE_READ | guard.FILE_SHARE_WRITE | 0x00000004,
            disposition=guard.FILE_CREATE,
            directory=True,
        )
        assert opened is not None
        handle, identity = opened
        try:
            guard._assert_contained(identity, directory)
        except BaseException:
            guard._kernel32.CloseHandle(handle)
            raise
        guard._handles[key] = (handle, identity)
        guard._hold_directory_namespace(directory, handle)
        item = {"path": relative, "identity": asdict(identity)}
        journal.append("directory_created", item)
        created.append(item)
        _fault("after_directory_created")
        parent_handle = handle
        current = directory
    return created


def _atomic_compare_replace(
    root: Path,
    target: Path,
    data: bytes,
    *,
    expected_preimage_sha256: str | None,
    mode: int,
    guard: WindowsPathGuard,
    operation_token: str | None = None,
) -> PathIdentity:
    guard.hold_namespace(target)
    _fault("after_namespace_lock")
    token = operation_token or uuid.uuid4().hex
    if not re.fullmatch(r"[A-Za-z0-9-]+", token):
        raise MigrationError("UNSAFE_OPERATION_TOKEN", f"Unsafe atomic-operation token: {token!r}")
    temporary = target.parent / f".{target.name}.wi5640-{token}.tmp"
    backup = target.parent / f".{target.name}.wi5640-{token}.bak"
    descriptor = os.open(_native_path(temporary), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    temporary_handle: Any | None = None
    preimage_handle: Any | None = None
    backup_moved = False
    installed = False
    preserve_artifacts = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(_native_path(temporary), mode)
        temporary_handle, _temporary_identity = guard.open_target_for_swap(temporary)
        if sha256_bytes(guard.read_handle_bytes(temporary_handle)) != sha256_bytes(data):
            raise MigrationError("TEMPORARY_PAYLOAD_DRIFT", f"Temporary payload changed before install: {target}")
        _fault("after_atomic_temp_ready")
        parent_handle = guard._parent_handle(target)
        current_hash: str | None
        if expected_preimage_sha256 is None:
            current = _literal_read_bytes(target)
            current_hash = sha256_bytes(current) if current is not None else None
        else:
            try:
                preimage_handle, _preimage_identity = guard.open_target_for_swap(target)
            except MigrationError as exc:
                raise MigrationError("PREIMAGE_DRIFT", f"Preimage disappeared before swap: {target}") from exc
            current_hash = sha256_bytes(guard.read_handle_bytes(preimage_handle))
        if current_hash != expected_preimage_sha256:
            raise MigrationError("PREIMAGE_DRIFT", f"Preimage changed immediately before replace: {target}")
        if preimage_handle is not None:
            if os.path.lexists(_native_path(backup)):
                raise MigrationError("ATOMIC_BACKUP_COLLISION", f"Atomic backup already exists: {backup}")
            guard.rename_handle(preimage_handle, parent_handle, backup.name)
            backup_moved = True
            _fsync_directory(target.parent)
            _fault("after_atomic_backup")
        guard.rename_handle(temporary_handle, parent_handle, target.name)
        installed = True
        _fsync_directory(target.parent)
        _fault("after_atomic_install")
        if sha256_bytes(guard.read_handle_bytes(temporary_handle)) != sha256_bytes(data):
            raise MigrationError(
                "POSTIMAGE_VERIFY_FAILED", f"Installed handle does not contain planned bytes: {target}"
            )
        identity = guard._identity(temporary_handle)
        guard._assert_contained(identity, target)
        if preimage_handle is not None:
            guard._kernel32.CloseHandle(preimage_handle)
            preimage_handle = None
            os.unlink(_native_path(backup))
            backup_moved = False
            _fsync_directory(target.parent)
        return identity
    except BaseException as exc:
        compensation_errors: list[str] = []
        if installed and temporary_handle is not None:
            try:
                guard.rename_handle(temporary_handle, guard._parent_handle(target), temporary.name)
                installed = False
            except BaseException as compensation_exc:
                compensation_errors.append(f"postimage quarantine failed: {compensation_exc}")
        if backup_moved and preimage_handle is not None:
            try:
                guard.rename_handle(preimage_handle, guard._parent_handle(target), target.name)
                backup_moved = False
            except BaseException as compensation_exc:
                compensation_errors.append(f"preimage restoration failed: {compensation_exc}")
        if compensation_errors:
            preserve_artifacts = True
            raise MigrationError(
                "ATOMIC_COMPENSATION_FAILED",
                f"{type(exc).__name__}: {exc}; " + "; ".join(compensation_errors),
            ) from exc
        raise
    finally:
        if temporary_handle is not None:
            guard._kernel32.CloseHandle(temporary_handle)
        if preimage_handle is not None:
            guard._kernel32.CloseHandle(preimage_handle)
        if not preserve_artifacts and os.path.exists(_native_path(temporary)):
            os.unlink(_native_path(temporary))


def _rollback_applied(
    root: Path,
    writes: list[dict[str, Any]],
    applied: list[str],
    *,
    guard: WindowsPathGuard | None = None,
    journal: TransactionJournal | None = None,
) -> list[dict[str, Any]]:
    by_path = {str(item["path"]): item for item in writes}
    validations: list[tuple[str, dict[str, Any], str, bytes | None]] = []
    outcomes: list[dict[str, Any]] = []
    for path in reversed(applied):
        operation = by_path[path]
        target = root / path
        current = _literal_read_bytes(target)
        current_hash = sha256_bytes(current) if current is not None else None
        preimage_hash = operation.get("preimage_sha256")
        if current_hash == preimage_hash:
            outcomes.append({"path": path, "status": "already_restored"})
            continue
        if current_hash != operation["postimage_sha256"]:
            outcomes.append({"path": path, "status": "concurrent_postimage_drift"})
            continue
        preimage_payload = operation.get("preimage_payload")
        if preimage_hash is None:
            validations.append((path, operation, "restore_absence", None))
            continue
        if not preimage_payload:
            outcomes.append({"path": path, "status": "preimage_payload_missing"})
            continue
        preimage = (root / preimage_payload).read_bytes()
        if sha256_bytes(preimage) != preimage_hash:
            outcomes.append({"path": path, "status": "preimage_payload_hash_mismatch"})
            continue
        postimage = root / str(operation["payload"])
        postimage_data = _literal_read_bytes(postimage)
        if postimage_data is None or sha256_bytes(postimage_data) != operation["postimage_sha256"]:
            outcomes.append({"path": path, "status": "postimage_payload_hash_mismatch"})
            continue
        validations.append((path, operation, "restore_preimage", preimage))
    if any(item["status"] not in {"already_restored"} for item in outcomes):
        return outcomes
    if guard is None:
        guard_context: Any = WindowsPathGuard(root)
    else:
        guard_context = nullcontext(guard)
    failed_path = "<guard-initialization>"
    try:
        with guard_context as active_guard:
            for rollback_index, (path, operation, action, preimage) in enumerate(validations):
                failed_path = path
                target = root / path
                active_guard.guard_target(target)
                current = _literal_read_bytes(target)
                current_hash = sha256_bytes(current) if current is not None else None
                if current_hash != operation["postimage_sha256"]:
                    outcomes.append({"path": path, "status": "concurrent_postimage_drift"})
                    break
                if journal:
                    operation_token = f"{journal.transaction_id}-rollback-{rollback_index:04d}"
                    journal.append(
                        "rollback_intent",
                        {
                            "path": path,
                            "action": action,
                            "expected_postimage_sha256": current_hash,
                            "operation_token": operation_token,
                        },
                    )
                else:
                    operation_token = f"rollback-{rollback_index:04d}-{uuid.uuid4().hex[:8]}"
                _fault("after_rollback_intent")
                if action == "restore_absence":
                    os.unlink(_native_path(target))
                    _fsync_directory(target.parent)
                    status = "restored_absence"
                else:
                    assert preimage is not None
                    _atomic_compare_replace(
                        root,
                        target,
                        preimage,
                        expected_preimage_sha256=operation["postimage_sha256"],
                        mode=int(operation["mode"]),
                        guard=active_guard,
                        operation_token=operation_token,
                    )
                    status = "restored_preimage"
                _fault("after_rollback_replace_before_completion")
                if journal:
                    journal.append("rollback_complete", {"path": path, "status": status})
                outcomes.append({"path": path, "status": status})
    except BaseException as exc:
        outcomes.append(
            {
                "path": failed_path,
                "status": "rollback_mutation_failed",
                "detail": f"{type(exc).__name__}: {exc}",
            }
        )
    return outcomes


def observe_final_closure(
    root: Path,
    policy_path: Path,
    material: dict[str, Any],
) -> dict[str, Any]:
    """Recompute final state from disk without trusting the transaction log."""

    _resolved, policy = load_policy(root, policy_path)
    mappings = load_manifest(root, policy)
    catalog, _candidates = load_obsolete_catalog(root, policy, mappings)
    worktrees, _worktree_raw = git_worktrees(root)
    inventory, closure, _files, blockers, _observation, _count = walk_inventory(root, policy, mappings, worktrees)
    occurrences, occurrence_blockers = scan_catalog_occurrences(root, policy, catalog, iter_full_observation(root))
    probe_classifications = {str(item) for item in policy.get("scan", {}).get("catalog_probe_classifications", [])}
    zip_occurrences, zip_blockers = scan_zip_occurrences(
        root, catalog, iter_full_observation(root), probe_classifications
    )
    occurrences.extend(zip_occurrences)
    blockers.extend(occurrence_blockers)
    blockers.extend(zip_blockers)
    if blockers:
        raise MigrationError("FINAL_SCAN_BLOCKED", f"Independent final scan found {len(blockers)} blocker(s)")
    target_states: list[dict[str, Any]] = []
    for expected in material.get("expected_final_closure", {}).get("target_states", []):
        path = str(expected["path"])
        target = root / path
        data = _literal_read_bytes(target)
        if data is None or sha256_bytes(data) != expected["sha256"]:
            raise MigrationError("FINAL_TARGET_MISMATCH", f"Final target does not match reviewed postimage: {path}")
        mode = stat.S_IMODE(os.stat(_native_path(target)).st_mode)
        if mode != int(expected["mode"]):
            raise MigrationError("FINAL_ATTRIBUTE_MISMATCH", f"Final target mode does not match plan: {path}")
        target_states.append({"path": path, "sha256": expected["sha256"], "mode": mode})
    retained_sources: list[dict[str, Any]] = []
    for expected in material.get("retained_sources", []):
        path = str(expected["path"])
        data = _literal_read_bytes(root / path)
        if data is None or sha256_bytes(data) != expected["sha256"]:
            raise MigrationError("RETAINED_SOURCE_DRIFT", f"Retained obsolete source changed or disappeared: {path}")
        retained_sources.append(dict(expected))
    observed = {
        "schema_version": 1,
        "closure_inventory_sha256": stable_hash(closure),
        "remaining_occurrence_sha256": stable_hash(_normalized_occurrence_material(occurrences)),
        "target_states": target_states,
        "retained_sources": retained_sources,
        "git_index_sha256": git_index_hash(root),
    }
    observed["fingerprint"] = stable_hash(observed)
    return observed


def _require_exact_final_closure(observed: dict[str, Any], expected: dict[str, Any]) -> None:
    if observed != expected:
        raise MigrationError(
            "FINAL_CLOSURE_MISMATCH",
            f"Observed {observed.get('fingerprint')} != reviewed {expected.get('fingerprint')}",
        )


def _remove_created_directories(
    root: Path,
    created: Sequence[dict[str, Any]],
    guard: WindowsPathGuard,
    journal: TransactionJournal,
) -> list[dict[str, Any]]:
    outcomes: list[dict[str, Any]] = []
    for item in reversed(created):
        path = root / str(item["path"])
        expected = PathIdentity(**item["identity"])
        current = guard.target_identity(path)
        if current is None:
            outcomes.append({"path": item["path"], "status": "already_absent"})
            continue
        if current != expected:
            outcomes.append({"path": item["path"], "status": "directory_identity_drift"})
            continue
        journal.append("directory_remove_intent", {"path": item["path"], "identity": item["identity"]})
        guard.release_namespace(path)
        guard.release_directory(path, expected)
        try:
            os.rmdir(_native_path(path))
            _fsync_directory(path.parent)
            status = "removed"
        except OSError as exc:
            status = "not_empty_or_unremovable"
            outcomes.append({"path": item["path"], "status": status, "detail": str(exc)})
            continue
        journal.append("directory_remove_complete", {"path": item["path"], "status": status})
        outcomes.append({"path": item["path"], "status": status})
    return outcomes


def apply_plan(root: Path, plan_path: Path, policy_path: Path, *, session_id: str | None = None) -> dict[str, Any]:
    session_id = session_id or active_session_context_id()
    _assert_no_incomplete_transaction(root)
    plan_payload, material = _load_plan(plan_path)
    writes = [item for item in material.get("writes", []) if isinstance(item, dict)]
    write_set = _safe_write_set(material)
    source_categories = {
        _path_identity(str(item["source"])): str(item.get("category") or "") for item in material.get("manifest", [])
    }
    if any(source_categories.get(_path_identity(path)) not in {None, "rules"} for path in write_set):
        raise MigrationError("RETAINED_SOURCE_WRITE_FORBIDDEN", "Plan attempts to mutate a retained obsolete source")
    _, live_policy = load_policy(root, policy_path)
    if any(not write_path_allowed(live_policy, path) for path in write_set):
        raise MigrationError("WRITE_OUTSIDE_MUTATION_POLICY", "Plan write set escapes the live mutation policy")
    if material.get("blockers"):
        raise MigrationError("BLOCKED_PLAN_CANNOT_APPLY", "Plan contains unresolved blockers")
    first_authority = authorize_apply(root, plan_payload, material, session_id=session_id)
    live, live_residuals = analyze(root, policy_path)
    live_report = report_payload(live, live_residuals, "apply-precheck")
    if live_report["binding"] != plan_payload["binding"] or live.plan_sha256 != plan_payload["plan_sha256"]:
        raise MigrationError("LIVE_PLAN_DRIFT", "Live migration state no longer matches the reviewed plan")
    second_authority = authorize_apply(root, plan_payload, material, session_id=session_id)
    if first_authority != second_authority:
        raise MigrationError(
            "AUTHORITY_CHANGED_BEFORE_WRITE", "Lifecycle, claim, packet, or PAUTH changed during validation"
        )
    for operation in writes:
        target = root / str(operation["path"])
        current = _literal_read_bytes(target)
        current_hash = sha256_bytes(current) if current is not None else None
        if current_hash != operation.get("preimage_sha256"):
            raise MigrationError("PREIMAGE_DRIFT", f"Preimage changed before apply: {operation['path']}")
        payload = _literal_read_bytes(root / str(operation["payload"]))
        if payload is None or sha256_bytes(payload) != operation.get("postimage_sha256"):
            raise MigrationError(
                "POSTIMAGE_PAYLOAD_INVALID", f"Postimage payload is missing or corrupt: {operation['path']}"
            )
    index_before = git_index_hash(root)
    if index_before != plan_payload["binding"]["git_index_sha256"]:
        raise MigrationError("GIT_INDEX_DRIFT", "Git index changed after plan review")
    transaction_id = f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:12]}"
    header = {
        "migration_id": "WI-5640",
        "mode": "apply",
        "plan_path": plan_path.relative_to(root).as_posix(),
        "plan_sha256": plan_payload["plan_sha256"],
        "binding_sha256": sha256_bytes(canonical_bytes(plan_payload["binding"])),
        "session_id": session_id,
        "authority_sha256": stable_hash(second_authority),
        "git_index_sha256": index_before,
        "writes": writes,
        "operation_manifest": material.get("operation_manifest", []),
        "expected_final_closure": material.get("expected_final_closure"),
    }
    journal = TransactionJournal.create(root, transaction_id, header)
    applied: list[str] = []
    created_directories: list[dict[str, Any]] = []
    with _operation_lock(root, journal):  # noqa: SIM117 - lock must enter before opening root handles
        with WindowsPathGuard(root) as guard:
            try:
                for operation_index, operation in enumerate(writes):
                    path = str(operation["path"])
                    target = root / path
                    operation_token = f"{transaction_id}-{operation_index:04d}"
                    temporary_path = target.parent / f".{target.name}.wi5640-{operation_token}.tmp"
                    backup_path = target.parent / f".{target.name}.wi5640-{operation_token}.bak"
                    created_directories.extend(_ensure_parent_directories(root, target, guard, journal))
                    guard.guard_target(target)
                    pre_identity = guard.target_identity(target)
                    journal.append(
                        "write_intent",
                        {
                            "path": path,
                            "preimage_sha256": operation.get("preimage_sha256"),
                            "postimage_sha256": operation["postimage_sha256"],
                            "mode": int(operation["mode"]),
                            "preimage_identity": asdict(pre_identity) if pre_identity else None,
                            "operation_token": operation_token,
                            "temporary_path": temporary_path.relative_to(root).as_posix(),
                            "backup_path": backup_path.relative_to(root).as_posix(),
                        },
                    )
                    _fault("after_write_intent")
                    payload = _literal_read_bytes(root / str(operation["payload"]))
                    assert payload is not None
                    identity = _atomic_compare_replace(
                        root,
                        target,
                        payload,
                        expected_preimage_sha256=operation.get("preimage_sha256"),
                        mode=int(operation["mode"]),
                        guard=guard,
                        operation_token=operation_token,
                    )
                    _fault("after_replace_before_completion")
                    current = _literal_read_bytes(target)
                    if current is None or sha256_bytes(current) != operation["postimage_sha256"]:
                        raise MigrationError(
                            "POSTIMAGE_VERIFY_FAILED", f"Atomic write did not produce planned bytes: {path}"
                        )
                    journal.append("write_complete", {"path": path, "postimage_identity": asdict(identity)})
                    applied.append(path)
                if git_index_hash(root) != index_before:
                    raise MigrationError("GIT_INDEX_MUTATED", "Migration apply changed the Git index")
                journal.append("verification_intent", {"expected": material["expected_final_closure"]["fingerprint"]})
                _fault("during_final_verification")
                observed_final = observe_final_closure(root, policy_path, material)
                _require_exact_final_closure(observed_final, material["expected_final_closure"])
                journal.append("verification_complete", {"observed": observed_final})
                journal.append("applied", {"writes": applied, "observed_final": observed_final})
                report = {
                    "status": "applied",
                    "plan_sha256": plan_payload["plan_sha256"],
                    "binding_sha256": header["binding_sha256"],
                    "writes": applied,
                    "authority": second_authority,
                    "git_index_sha256": index_before,
                    "observed_final": observed_final,
                }
                journal.write_report(report)
                return report
            except BaseException as exc:
                if not journal.terminal:
                    journal.append("rollback_started", {"reason": f"{type(exc).__name__}: {exc}", "applied": applied})
                rollback = _rollback_applied(root, writes, applied, guard=guard, journal=journal)
                directory_outcomes = _remove_created_directories(root, created_directories, guard, journal)
                allowed = {"restored_preimage", "restored_absence", "already_restored"}
                rollback_ok = all(item["status"] in allowed for item in rollback)
                directories_ok = all(item["status"] in {"removed", "already_absent"} for item in directory_outcomes)
                report = {
                    "status": "rolled_back_after_failure" if rollback_ok and directories_ok else "recovery_required",
                    "error": f"{type(exc).__name__}: {exc}",
                    "applied": applied,
                    "rollback": rollback,
                    "directories": directory_outcomes,
                    "plan_sha256": plan_payload["plan_sha256"],
                }
                if rollback_ok and directories_ok:
                    journal.append("rolled_back", report)
                    journal.write_report(report)
                    raise
                journal.append("recovery_required", report)
                journal.write_report(report)
                raise MigrationError(
                    "PARTIAL_ROLLBACK_FAILED",
                    f"Transaction {transaction_id} requires explicit recovery",
                ) from exc


def rollback_plan(root: Path, plan_path: Path, *, session_id: str | None = None) -> dict[str, Any]:
    session_id = session_id or active_session_context_id()
    _assert_no_incomplete_transaction(root)
    plan_payload, material = _load_plan(plan_path)
    writes = [item for item in material.get("writes", []) if isinstance(item, dict)]
    authority = authorize_apply(root, plan_payload, material, session_id=session_id)
    transaction_id = f"rollback-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:12]}"
    journal = TransactionJournal.create(
        root,
        transaction_id,
        {
            "migration_id": "WI-5640",
            "mode": "rollback",
            "plan_path": plan_path.relative_to(root).as_posix(),
            "plan_sha256": plan_payload["plan_sha256"],
            "session_id": session_id,
            "authority_sha256": stable_hash(authority),
            "writes": writes,
        },
    )
    with _operation_lock(root, journal):  # noqa: SIM117 - lock must enter before opening root handles
        with WindowsPathGuard(root) as guard:
            outcomes = _rollback_applied(
                root, writes, [str(item["path"]) for item in writes], guard=guard, journal=journal
            )
            allowed = {"restored_preimage", "restored_absence", "already_restored"}
            if any(item["status"] not in allowed for item in outcomes):
                journal.append("recovery_required", {"outcomes": outcomes})
                raise MigrationError("ROLLBACK_VALIDATION_FAILED", f"Transaction {transaction_id} requires recovery")
            report = {"status": "rolled_back", "plan_sha256": plan_payload["plan_sha256"], "outcomes": outcomes}
            journal.append("rolled_back", report)
            journal.write_report(report)
            return report


def _select_recovery_transaction(root: Path, transaction_id: str | None) -> str:
    if transaction_id:
        return transaction_id
    lock = _lock_payload(root)
    if lock:
        return str(lock["transaction_id"])
    transactions = root / _TRANSACTION_DIRECTORY
    candidates: list[str] = []
    if transactions.is_dir():
        for directory in transactions.iterdir():
            if directory.is_dir() and (directory / "journal.jsonl").is_file():
                journal = TransactionJournal.load(root, directory.name)
                if not journal.terminal:
                    candidates.append(directory.name)
    if len(candidates) != 1:
        raise MigrationError(
            "RECOVERY_TRANSACTION_AMBIGUOUS", f"Expected one incomplete transaction, found {len(candidates)}"
        )
    return candidates[0]


def _atomic_intents(journal: TransactionJournal) -> dict[str, dict[str, Any]]:
    return {
        str(record["payload"]["path"]): dict(record["payload"])
        for record in journal.records
        if record.get("event") == "write_intent"
        and isinstance(record.get("payload"), dict)
        and record["payload"].get("path")
    }


def _prepare_interrupted_atomic_writes(
    root: Path,
    writes: Sequence[dict[str, Any]],
    journal: TransactionJournal,
    guard: WindowsPathGuard,
) -> list[dict[str, Any]]:
    intents = _atomic_intents(journal)
    outcomes: list[dict[str, Any]] = []
    for operation in writes:
        path = str(operation["path"])
        intent = intents.get(path)
        if not intent or not intent.get("temporary_path") or not intent.get("backup_path"):
            continue
        target = root / path
        temporary = root / str(intent["temporary_path"])
        backup = root / str(intent["backup_path"])
        target_data = _literal_read_bytes(target)
        temporary_data = _literal_read_bytes(temporary)
        backup_data = _literal_read_bytes(backup)
        target_hash = sha256_bytes(target_data) if target_data is not None else None
        temporary_hash = sha256_bytes(temporary_data) if temporary_data is not None else None
        backup_hash = sha256_bytes(backup_data) if backup_data is not None else None
        preimage_hash = operation.get("preimage_sha256")
        postimage_hash = operation["postimage_sha256"]
        if temporary_hash not in {None, postimage_hash}:
            outcomes.append({"path": path, "status": "unknown_temporary_artifact"})
            continue
        if backup_hash not in {None, preimage_hash}:
            outcomes.append({"path": path, "status": "unknown_backup_artifact"})
            continue
        if target_hash is None and preimage_hash is not None:
            if backup_hash != preimage_hash:
                outcomes.append({"path": path, "status": "missing_target_and_verified_backup"})
                continue
            guard.hold_namespace(target)
            journal.append("recovery_backup_restore_intent", {"path": path, "backup_path": intent["backup_path"]})
            os.rename(_native_path(backup), _native_path(target))
            _fsync_directory(target.parent)
            journal.append("recovery_backup_restored", {"path": path})
            outcomes.append({"path": path, "status": "preimage_restored_from_backup"})
            continue
        if target_hash not in {preimage_hash, postimage_hash}:
            outcomes.append({"path": path, "status": "unknown_target_artifact"})
            continue
        outcomes.append({"path": path, "status": "atomic_state_classified"})
    return outcomes


def _cleanup_atomic_artifacts(
    root: Path,
    writes: Sequence[dict[str, Any]],
    journal: TransactionJournal,
    guard: WindowsPathGuard,
) -> list[dict[str, Any]]:
    intents = _atomic_intents(journal)
    outcomes: list[dict[str, Any]] = []
    for operation in writes:
        path = str(operation["path"])
        intent = intents.get(path)
        if not intent:
            continue
        target = root / path
        for artifact_field, expected_hash in (
            ("temporary_path", operation["postimage_sha256"]),
            ("backup_path", operation.get("preimage_sha256")),
        ):
            relative = intent.get(artifact_field)
            if not relative:
                continue
            artifact = root / str(relative)
            data = _literal_read_bytes(artifact)
            if data is None:
                continue
            if expected_hash is None or sha256_bytes(data) != expected_hash:
                outcomes.append({"path": path, "artifact": str(relative), "status": "artifact_hash_drift"})
                continue
            guard.hold_namespace(target)
            journal.append("recovery_artifact_remove_intent", {"path": path, "artifact": str(relative)})
            os.unlink(_native_path(artifact))
            _fsync_directory(artifact.parent)
            journal.append("recovery_artifact_removed", {"path": path, "artifact": str(relative)})
            outcomes.append({"path": path, "artifact": str(relative), "status": "removed"})
    return outcomes


def recover_transaction(
    root: Path,
    policy_path: Path,
    *,
    transaction_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    session_id = session_id or active_session_context_id()
    selected = _select_recovery_transaction(root, transaction_id)
    journal = TransactionJournal.load(root, selected)
    if journal.terminal:
        lock = _lock_payload(root)
        if lock and lock.get("transaction_id") == selected:
            (root / _LOCK_RELATIVE).unlink()
            _fsync_directory((root / _LOCK_RELATIVE).parent)
        return {"status": "already_terminal", "transaction_id": selected, "event": journal.records[-1]["event"]}
    header = journal.header
    plan_path = root / str(header.get("plan_path") or "")
    plan_payload, material = _load_plan(plan_path)
    authorize_apply(root, plan_payload, material, session_id=session_id)
    writes = [item for item in header.get("writes", []) if isinstance(item, dict)]
    created = [
        dict(record["payload"])
        for record in journal.records
        if record.get("event") == "directory_created" and isinstance(record.get("payload"), dict)
    ]
    with _operation_lock(root, journal, recovery=True):  # noqa: SIM117 - recovery owns the stale lock first
        with WindowsPathGuard(root) as guard:
            for item in created:
                path = root / str(item["path"])
                if os.path.isdir(_native_path(path)):
                    identity = guard.target_identity(path)
                    if identity == PathIdentity(**item["identity"]):
                        try:
                            guard.register_created_directory(path)
                        except MigrationError:
                            pass
            artifact_preparation = _prepare_interrupted_atomic_writes(root, writes, journal, guard)
            if any(
                item["status"] not in {"atomic_state_classified", "preimage_restored_from_backup"}
                for item in artifact_preparation
            ):
                journal.append("recovery_blocked", {"atomic_artifacts": artifact_preparation})
                journal.write_report({"status": "recovery_blocked", "atomic_artifacts": artifact_preparation})
                raise MigrationError("RECOVERY_ATOMIC_STATE_UNKNOWN", f"Recovery stopped for transaction {selected}")
            outcomes = _rollback_applied(
                root, writes, [str(item["path"]) for item in writes], guard=guard, journal=journal
            )
            allowed = {"restored_preimage", "restored_absence", "already_restored"}
            if any(item["status"] not in allowed for item in outcomes):
                journal.append("recovery_blocked", {"outcomes": outcomes})
                journal.write_report({"status": "recovery_blocked", "outcomes": outcomes})
                raise MigrationError("RECOVERY_CONCURRENT_DRIFT", f"Recovery stopped for transaction {selected}")
            directory_outcomes = _remove_created_directories(root, created, guard, journal)
            if any(item["status"] not in {"removed", "already_absent"} for item in directory_outcomes):
                journal.append("recovery_blocked", {"directories": directory_outcomes})
                journal.write_report({"status": "recovery_blocked", "directories": directory_outcomes})
                raise MigrationError("RECOVERY_DIRECTORY_DRIFT", f"Recovery stopped for transaction {selected}")
            artifact_cleanup = _cleanup_atomic_artifacts(root, writes, journal, guard)
            if any(item["status"] != "removed" for item in artifact_cleanup):
                journal.append("recovery_blocked", {"atomic_artifacts": artifact_cleanup})
                journal.write_report({"status": "recovery_blocked", "atomic_artifacts": artifact_cleanup})
                raise MigrationError("RECOVERY_ARTIFACT_DRIFT", f"Recovery stopped for transaction {selected}")
            report = {
                "status": "recovered",
                "transaction_id": selected,
                "outcomes": outcomes,
                "directories": directory_outcomes,
                "artifact_preparation": artifact_preparation,
                "artifact_cleanup": artifact_cleanup,
            }
            journal.append("recovered", report)
            journal.write_report(report)
            return report


def run_observation(mode: str, root: Path, policy_path: Path) -> int:
    analysis, residuals = analyze(root, policy_path)
    report_path, report = publish_evidence(analysis, residuals, mode)
    summary = report["summary"]
    print(
        f"WI-5640 {mode}: {report['status']} | inventory={summary['inventory_entries']} "
        f"hits={summary['reference_hits']} unresolved={summary['unresolved_residuals']} "
        f"writes={summary['proposed_writes']} blockers={summary['blockers']}"
    )
    print(f"plan_sha256={report['plan_sha256']}")
    print(f"closure_fingerprint={report['hashes']['closure_fingerprint']}")
    print(f"report={report_path.relative_to(root).as_posix()}")
    if mode == "verify":
        return 0 if report["status"] == "clean" else 2
    return 0 if not analysis.blockers else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preflight", "plan", "verify"):
        child = subparsers.add_parser(command)
        child.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
        child.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    for command in ("apply", "rollback", "bind-packet", "verify-final"):
        child = subparsers.add_parser(command)
        child.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
        child.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
        child.add_argument("--plan", type=Path, default=RUNTIME_RELATIVE / "plan.json")
    recover = subparsers.add_parser("recover")
    recover.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    recover.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    recover.add_argument("--transaction-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(os.path.abspath(str(args.project_root)))
    policy = args.policy if args.policy.is_absolute() else root / args.policy
    try:
        if args.command in {"preflight", "plan", "verify"}:
            return run_observation(args.command, root, policy)
        if args.command == "recover":
            result = recover_transaction(root, policy, transaction_id=args.transaction_id)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        plan = args.plan if args.plan.is_absolute() else root / args.plan
        if args.command == "apply":
            result = apply_plan(root, plan, policy)
        elif args.command == "rollback":
            result = rollback_plan(root, plan)
        elif args.command == "bind-packet":
            result = bind_migration_packet(root, plan)
        elif args.command == "verify-final":
            _payload, material = _load_plan(plan)
            result = observe_final_closure(root, policy, material)
            _require_exact_final_closure(result, material.get("expected_final_closure", {}))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except MigrationError as exc:
        print(json.dumps({"status": "failed", "code": exc.code, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    except Exception as exc:
        print(
            json.dumps(
                {"status": "failed", "code": "UNEXPECTED_FAILURE", "message": f"{type(exc).__name__}: {exc}"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
