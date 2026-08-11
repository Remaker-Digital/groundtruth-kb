# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Canonical operation-time evaluation of project-authorization envelopes."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any

TAXONOMY_RELATIVE_PATH = Path("config/governance/project-authorization-operation-taxonomy.toml")


class TaxonomyError(ValueError):
    """Raised when the permanent operation taxonomy is absent or malformed."""


@dataclass(frozen=True)
class TaxonomyPathRule:
    pattern: str
    mutation_class: str


@dataclass(frozen=True)
class OperationTaxonomy:
    evaluator_id: str
    evaluator_version: str
    taxonomy_version: str
    mutation_class_aliases: Mapping[str, str]
    operation_aliases: Mapping[str, str]
    canonical_mutation_classes: frozenset[str]
    path_rules: tuple[TaxonomyPathRule, ...]
    source_path: str
    source_sha256: str


def _default_project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _taxonomy_path(project_root: Path | None = None) -> Path:
    return (project_root or _default_project_root()).resolve() / TAXONOMY_RELATIVE_PATH


def _registered_aliases(entries: object, *, entry_kind: str) -> tuple[dict[str, str], frozenset[str]]:
    if not isinstance(entries, list) or not entries:
        raise TaxonomyError(f"Taxonomy {entry_kind} entries must be a non-empty list")
    aliases: dict[str, str] = {}
    canonical: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise TaxonomyError(f"Taxonomy {entry_kind} entry must be a table")
        name = normalize_token(str(entry.get("name") or ""))
        raw_aliases = entry.get("aliases")
        if not name or not isinstance(raw_aliases, list):
            raise TaxonomyError(f"Taxonomy {entry_kind} entry requires name and aliases")
        canonical.add(name)
        for value in [name, *raw_aliases]:
            token = normalize_token(str(value))
            if not token:
                raise TaxonomyError(f"Taxonomy {entry_kind} alias must be non-empty")
            previous = aliases.setdefault(token, name)
            if previous != name:
                raise TaxonomyError(f"Taxonomy alias {token!r} maps to multiple {entry_kind} entries")
    return aliases, frozenset(canonical)


def _registered_path_rules(
    entries: object,
    *,
    canonical_classes: frozenset[str],
) -> tuple[TaxonomyPathRule, ...]:
    if entries is None:
        return ()
    if not isinstance(entries, list):
        raise TaxonomyError("Taxonomy path-rule entries must be a list")

    rules: list[TaxonomyPathRule] = []
    seen_patterns: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise TaxonomyError("Taxonomy path-rule entry must be a table")
        raw_pattern = entry.get("pattern")
        raw_class = entry.get("mutation_class")
        if not isinstance(raw_pattern, str) or not isinstance(raw_class, str):
            raise TaxonomyError("Taxonomy path-rule entry requires pattern and mutation_class strings")

        pattern = raw_pattern.strip().lower()
        mutation_class = normalize_token(raw_class)
        path_parts = pattern.split("/")
        if (
            not pattern
            or pattern.startswith(("/", "./"))
            or "\\" in pattern
            or any(part in {"", ".", ".."} for part in path_parts)
        ):
            raise TaxonomyError(
                f"Taxonomy path-rule pattern must be canonical root-relative POSIX syntax: {raw_pattern!r}"
            )
        if mutation_class not in canonical_classes:
            raise TaxonomyError(f"Taxonomy path-rule mutation class is not canonical: {raw_class!r}")
        if pattern in seen_patterns:
            raise TaxonomyError(f"Taxonomy path-rule pattern is registered more than once: {pattern!r}")
        seen_patterns.add(pattern)
        rules.append(TaxonomyPathRule(pattern=pattern, mutation_class=mutation_class))

    return tuple(sorted(rules, key=lambda rule: (rule.pattern, rule.mutation_class)))


def _load_operation_taxonomy(path: Path) -> OperationTaxonomy:
    try:
        source_bytes = path.read_bytes()
        payload = tomllib.loads(source_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise TaxonomyError(f"Cannot load canonical operation taxonomy {path}: {exc}") from exc
    if payload.get("schema_version") != 1:
        raise TaxonomyError("Canonical operation taxonomy schema_version must be 1")
    mutation_aliases, canonical_classes = _registered_aliases(
        payload.get("mutation_class"), entry_kind="mutation-class"
    )
    operation_aliases, _ = _registered_aliases(payload.get("operation"), entry_kind="operation")
    path_rules = _registered_path_rules(payload.get("path_rule"), canonical_classes=canonical_classes)
    evaluator_id = str(payload.get("evaluator_id") or "")
    evaluator_version = str(payload.get("evaluator_version") or "")
    taxonomy_version = str(payload.get("taxonomy_version") or "")
    if not evaluator_id or not evaluator_version or not taxonomy_version:
        raise TaxonomyError("Canonical operation taxonomy evaluator and version fields are required")
    return OperationTaxonomy(
        evaluator_id=evaluator_id,
        evaluator_version=evaluator_version,
        taxonomy_version=taxonomy_version,
        mutation_class_aliases=mutation_aliases,
        operation_aliases=operation_aliases,
        canonical_mutation_classes=canonical_classes,
        path_rules=path_rules,
        source_path=str(path),
        source_sha256=hashlib.sha256(source_bytes).hexdigest().upper(),
    )


def load_operation_taxonomy(project_root: Path | None = None) -> OperationTaxonomy:
    """Load the exact root-bound permanent operation taxonomy."""
    return _load_operation_taxonomy(_taxonomy_path(project_root))


@dataclass(frozen=True)
class ClassifiedTarget:
    path: str
    mutation_class: str


@dataclass(frozen=True)
class EnvelopeDecision:
    allowed: bool
    reason_code: str
    reason: str
    authorization_id: str
    authorization_version: int | None
    normalized_envelope_hash: str
    normalized_operation: str | None
    classified_targets: tuple[ClassifiedTarget, ...]
    evaluator_id: str
    evaluator_version: str
    evaluator_sha256: str
    taxonomy_version: str
    taxonomy_sha256: str
    decision_time: str
    recovery: str

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["classified_targets"] = [asdict(item) for item in self.classified_targets]
        return payload


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def evaluator_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper()


def normalize_operation(value: str, taxonomy: OperationTaxonomy | None = None) -> str | None:
    active = taxonomy or load_operation_taxonomy()
    return active.operation_aliases.get(normalize_token(value))


def normalize_mutation_class(value: str, taxonomy: OperationTaxonomy | None = None) -> str | None:
    active = taxonomy or load_operation_taxonomy()
    return active.mutation_class_aliases.get(normalize_token(value))


def mutation_class_families(values: Sequence[str], taxonomy: OperationTaxonomy | None = None) -> set[str]:
    """Return only explicitly registered canonical target families."""
    active = taxonomy or load_operation_taxonomy()
    return {canonical for value in values if (canonical := normalize_mutation_class(value, active)) is not None}


def classify_target(path_text: str, taxonomy: OperationTaxonomy | None = None) -> ClassifiedTarget:
    active = taxonomy or load_operation_taxonomy()
    path = path_text.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    path = path.lstrip("/")
    lowered = path.lower()
    first = lowered.split("/", 1)[0]
    governed_classes = {rule.mutation_class for rule in active.path_rules if fnmatchcase(lowered, rule.pattern)}

    if len(governed_classes) == 1:
        mutation_class = next(iter(governed_classes))
    elif len(governed_classes) > 1:
        mutation_class = "unclassified"
    elif re.fullmatch(r"\.gtkb-index-[a-z0-9_]{8}/index", path):
        mutation_class = "repository_metadata"
    elif first == "bridge":
        mutation_class = "bridge"
    elif lowered == "groundtruth.db" or first == ".groundtruth":
        mutation_class = "metadata"
    elif first in {".gtkb-state", "harness-state"}:
        mutation_class = "runtime_state"
    elif lowered in {".gitattributes", ".gitignore", ".gitmodules"} or first == ".git":
        mutation_class = "repository_metadata"
    elif (
        first in {"platform_tests", "tests"}
        or lowered.startswith("groundtruth-kb/tests/")
        or lowered == "groundtruth-kb/tests"
    ):
        mutation_class = "test"
    elif (
        first
        in {
            ".agent",
            ".api-harness",
            ".claude",
            ".codex",
            ".cursor",
            ".github",
            ".goose",
            "config",
        }
        or lowered
        in {
            ".dockerignore",
            ".env",
            "agents.md",
            "claude.md",
            "docker-compose.yml",
            "dockerfile",
            "dockerfile.test",
            "dockerfile.ui",
            "env.local",
            "groundtruth.toml",
            "pyproject.toml",
            "shopify.app.toml",
        }
        or lowered.endswith((".toml", ".yaml", ".yml"))
    ):
        mutation_class = "configuration"
    elif (
        first in {"docs", "independent-progress-assessments", "memory"}
        or lowered.startswith("groundtruth-kb/docs/")
        or lowered == "groundtruth-kb/docs"
    ):
        mutation_class = "documentation"
    elif (
        first in {"scripts", "applications"}
        or lowered.startswith("groundtruth-kb/src/")
        or lowered == "groundtruth-kb/src"
        or lowered == "groundtruth-kb/templates"
        or first == "dashboard"
        or lowered.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".ps1", ".sh", ".csv"))
    ):
        mutation_class = "source"
    elif lowered.endswith((".md", ".json", ".jsonl")):
        mutation_class = "governance_evidence"
    else:
        mutation_class = "unclassified"
    if mutation_class not in active.canonical_mutation_classes:
        mutation_class = "unclassified"
    return ClassifiedTarget(path=path_text, mutation_class=mutation_class)


def _normalized_list(
    values: object,
    *,
    normalizer: Any = normalize_token,
) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return []
    return sorted(normalizer(str(value)) or normalize_token(str(value)) for value in values)


def normalized_envelope_hash(authorization: Mapping[str, Any], taxonomy: OperationTaxonomy | None = None) -> str:
    active = taxonomy or load_operation_taxonomy()
    fields = {
        "id": authorization.get("id"),
        "version": authorization.get("version"),
        "project_id": authorization.get("project_id"),
        "status": authorization.get("status"),
        "owner_decision_deliberation_id": authorization.get("owner_decision_deliberation_id"),
        "expires_at": authorization.get("expires_at"),
        "supersedes": authorization.get("supersedes"),
        "superseded_by": authorization.get("superseded_by"),
        "allowed_mutation_classes": _normalized_list(
            authorization.get("allowed_mutation_classes"),
            normalizer=lambda value: normalize_mutation_class(value, active),
        ),
        "forbidden_operations": _normalized_list(
            authorization.get("forbidden_operations"),
            normalizer=lambda value: normalize_operation(value, active),
        ),
        "included_work_item_ids": _normalized_list(authorization.get("included_work_item_ids")),
        "excluded_work_item_ids": _normalized_list(authorization.get("excluded_work_item_ids")),
        "included_spec_ids": _normalized_list(authorization.get("included_spec_ids")),
        "excluded_spec_ids": _normalized_list(authorization.get("excluded_spec_ids")),
    }
    encoded = json.dumps(fields, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest().upper()


def evaluate_envelope(
    authorization: Mapping[str, Any],
    *,
    requested_operation: str,
    target_paths: Sequence[str],
    decision_time: datetime | None = None,
    taxonomy: OperationTaxonomy | None = None,
) -> EnvelopeDecision:
    """Evaluate operation and target-class bounds with forbidden precedence."""
    active = taxonomy or load_operation_taxonomy()
    authorization_id = str(authorization.get("id") or "")
    version = authorization.get("version")
    envelope_hash = normalized_envelope_hash(authorization, active)
    classified = tuple(classify_target(path, active) for path in target_paths)
    requested_operation_token = normalize_token(requested_operation)
    normalized_operation = normalize_operation(requested_operation, active)
    timestamp = (decision_time or datetime.now(UTC)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    recovery = "Correct the current PAUTH envelope or requested operation, then reevaluate before side effects."

    def decision(allowed: bool, reason_code: str, reason: str) -> EnvelopeDecision:
        return EnvelopeDecision(
            allowed=allowed,
            reason_code=reason_code,
            reason=reason,
            authorization_id=authorization_id,
            authorization_version=version if isinstance(version, int) else None,
            normalized_envelope_hash=envelope_hash,
            normalized_operation=normalized_operation,
            classified_targets=classified,
            evaluator_id=active.evaluator_id,
            evaluator_version=active.evaluator_version,
            evaluator_sha256=evaluator_sha256(),
            taxonomy_version=active.taxonomy_version,
            taxonomy_sha256=active.source_sha256,
            decision_time=timestamp,
            recovery=recovery,
        )

    if not authorization_id:
        return decision(False, "missing_authorization_id", "Authorization ID is required.")
    raw_forbidden = [value for value in authorization.get("forbidden_operations") or [] if isinstance(value, str)]
    forbidden = {normalize_operation(value, active) or normalize_token(value) for value in raw_forbidden}
    operation_for_comparison = normalized_operation or requested_operation_token
    if operation_for_comparison in forbidden:
        return decision(False, "forbidden_operation", f"Operation {operation_for_comparison!r} is forbidden.")
    unknown_forbidden = [value for value in raw_forbidden if normalize_operation(value, active) is None]
    if unknown_forbidden:
        return decision(
            False,
            "unknown_forbidden_operation",
            "Unregistered forbidden operation(s): " + ", ".join(unknown_forbidden),
        )
    if normalized_operation is None:
        return decision(False, "unknown_operation", f"Operation {requested_operation!r} is not registered.")

    allowed = [str(value) for value in authorization.get("allowed_mutation_classes") or []]
    if not allowed:
        return decision(False, "missing_allowed_mutation_classes", "No allowed mutation classes are recorded.")
    unknown_classes = [value for value in allowed if normalize_mutation_class(value, active) is None]
    if unknown_classes:
        return decision(
            False,
            "unknown_mutation_class",
            "Unregistered allowed mutation class(es): " + ", ".join(unknown_classes),
        )
    allowed_families = mutation_class_families(allowed, active)
    denied = [item for item in classified if item.mutation_class not in allowed_families]
    if denied:
        detail = ", ".join(f"{item.path} ({item.mutation_class})" for item in denied)
        return decision(False, "target_mutation_class_not_allowed", detail)
    return decision(True, "allowed", "The requested operation and every target class are PAUTH-allowed.")


__all__ = [
    "EnvelopeDecision",
    "OperationTaxonomy",
    "TAXONOMY_RELATIVE_PATH",
    "TaxonomyPathRule",
    "TaxonomyError",
    "classify_target",
    "evaluate_envelope",
    "evaluator_sha256",
    "load_operation_taxonomy",
    "mutation_class_families",
    "normalize_mutation_class",
    "normalize_operation",
    "normalize_token",
    "normalized_envelope_hash",
]
