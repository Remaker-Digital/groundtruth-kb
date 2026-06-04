"""Document artifact author provenance helpers.

The document-author provenance contract applies to newly-created Markdown
artifacts on governed documentation surfaces. Existing files are grandfathered;
this module only validates candidate content when a caller asks it to.
"""

from __future__ import annotations

import fnmatch
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_AUTHOR_FIELDS: tuple[str, ...] = (
    "author_identity",
    "author_harness_id",
    "author_session_context_id",
    "author_model",
    "author_model_version",
    "author_model_configuration",
)
OPTIONAL_AUTHOR_FIELDS: tuple[str, ...] = (
    "author_model_context_window",
    "author_metadata_source",
)
AUTHOR_METADATA_LINE_RE = re.compile(
    r"^(?P<key>author_[a-z0-9_]+):\s*(?P<value>.*?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
WAIVER_RE = re.compile(
    r"^document_author_provenance_waiver:\s*(?P<value>DELIB-[A-Z0-9_.-]+\s+.+)$",
    re.IGNORECASE | re.MULTILINE,
)
PLACEHOLDER_VALUES: frozenset[str] = frozenset(
    {
        "",
        "-",
        "--",
        "n/a",
        "na",
        "none",
        "null",
        "tbd",
        "todo",
        "unknown",
        "unspecified",
        "<unknown>",
        "<tbd>",
        "[unknown]",
        "[tbd]",
    }
)
DEFAULT_GOVERNED_SURFACES: tuple[str, ...] = (
    "bridge/**/*.md",
    ".claude/rules/**/*.md",
    "independent-progress-assessments/**/*.md",
    "memory/**/*.md",
    "docs/**/*.md",
)
DEFAULT_EXCLUSIONS: tuple[str, ...] = (
    "bridge/INDEX.md",
    ".claude/worktrees/**",
    ".gtkb-state/**",
    "archive/**",
    "**/superseded-*/**",
)


def normalize_rel_text(path_text: str) -> str:
    normalized = path_text.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


@dataclass(frozen=True)
class ValidationResult:
    """Structured validation result for document author metadata."""

    is_valid: bool
    metadata: dict[str, str]
    missing_fields: tuple[str, ...]
    invalid_fields: tuple[str, ...]
    waiver: str | None = None

    @property
    def gaps(self) -> tuple[str, ...]:
        return (*self.missing_fields, *self.invalid_fields)


@dataclass(frozen=True)
class DocumentAuthorConfig:
    """Configuration for governed document surfaces."""

    governed_surfaces: tuple[str, ...] = DEFAULT_GOVERNED_SURFACES
    exclusions: tuple[str, ...] = DEFAULT_EXCLUSIONS


def metadata_value_is_valid(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip().strip("`")
    return text.lower() not in PLACEHOLDER_VALUES


def parse_author_metadata(text: str) -> dict[str, str]:
    return {
        match.group("key").lower(): match.group("value").strip() for match in AUTHOR_METADATA_LINE_RE.finditer(text)
    }


def find_waiver(text: str) -> str | None:
    match = WAIVER_RE.search(text)
    if not match:
        return None
    value = match.group("value").strip()
    return value if metadata_value_is_valid(value) else None


def validate_author_metadata(text: str) -> ValidationResult:
    waiver = find_waiver(text)
    metadata = parse_author_metadata(text)
    missing: list[str] = []
    invalid: list[str] = []
    for field in REQUIRED_AUTHOR_FIELDS:
        if field not in metadata:
            missing.append(field)
        elif not metadata_value_is_valid(metadata[field]):
            invalid.append(f"{field} (placeholder/invalid)")
    return ValidationResult(
        is_valid=bool(waiver) or (not missing and not invalid),
        metadata=metadata,
        missing_fields=tuple(missing),
        invalid_fields=tuple(invalid),
        waiver=waiver,
    )


def format_author_metadata(metadata: Mapping[str, Any]) -> str:
    lines: list[str] = []
    for field in REQUIRED_AUTHOR_FIELDS:
        value = metadata.get(field)
        if not metadata_value_is_valid(value):
            raise ValueError(f"{field} is required and must not be a placeholder")
        lines.append(f"{field}: {str(value).strip().strip('`')}")
    for field in OPTIONAL_AUTHOR_FIELDS:
        value = metadata.get(field)
        if metadata_value_is_valid(value):
            lines.append(f"{field}: {str(value).strip().strip('`')}")
    return "\n".join(lines) + "\n"


def relative_path(project_root: Path, path: Path | str) -> str:
    path_obj = Path(path)
    resolved = path_obj if path_obj.is_absolute() else project_root / path_obj
    try:
        return resolved.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return normalize_rel_text(str(path))


def _match_any(rel_path: str, patterns: tuple[str, ...]) -> bool:
    normalized = normalize_rel_text(rel_path)
    for pattern in patterns:
        candidate = normalize_rel_text(pattern)
        if fnmatch.fnmatch(normalized, candidate):
            return True
        if "/**/" in candidate and fnmatch.fnmatch(normalized, candidate.replace("/**/", "/")):
            return True
    return False


def is_governed_document_path(rel_path: str, config: DocumentAuthorConfig | None = None) -> bool:
    selected = config or DocumentAuthorConfig()
    normalized = normalize_rel_text(rel_path)
    if not normalized.endswith(".md"):
        return False
    if _match_any(normalized, selected.exclusions):
        return False
    return _match_any(normalized, selected.governed_surfaces)
