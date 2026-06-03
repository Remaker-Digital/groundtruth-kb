"""Author/runtime metadata helpers for bridge artifacts.

Bridge artifacts are audit records. The model/session that authored them must
carry accurate identity and model configuration metadata; helpers fail closed
when that metadata is unavailable rather than guessing.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

BRIDGE_AUTHOR_METADATA_STATUSES: frozenset[str] = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED"}
)
REQUIRED_AUTHOR_METADATA_FIELDS: tuple[str, ...] = (
    "author_identity",
    "author_harness_id",
    "author_session_context_id",
    "author_model",
    "author_model_version",
    "author_model_configuration",
)
OPTIONAL_AUTHOR_METADATA_FIELDS: tuple[str, ...] = (
    "author_model_context_window",
    "author_metadata_source",
)
AUTHOR_METADATA_RELATIVE_PATH = Path(".gtkb-state") / "bridge-author-metadata" / "current.json"

FIELD_ENV_NAMES: dict[str, tuple[str, ...]] = {
    "author_identity": ("GTKB_AUTHOR_IDENTITY", "GTKB_AUTHOR_NAME", "GTKB_HARNESS_NAME"),
    "author_harness_id": ("GTKB_AUTHOR_HARNESS_ID", "GTKB_HARNESS_ID", "CODEX_HARNESS_ID", "CLAUDE_HARNESS_ID"),
    "author_session_context_id": (
        "GTKB_AUTHOR_SESSION_CONTEXT_ID",
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "CLAUDE_SESSION_ID",
    ),
    "author_model": ("GTKB_AUTHOR_MODEL", "GTKB_MODEL", "CODEX_MODEL", "CLAUDE_MODEL"),
    "author_model_version": (
        "GTKB_AUTHOR_MODEL_VERSION",
        "GTKB_MODEL_VERSION",
        "CODEX_MODEL_VERSION",
        "CLAUDE_MODEL_VERSION",
    ),
    "author_model_configuration": (
        "GTKB_AUTHOR_MODEL_CONFIGURATION",
        "GTKB_MODEL_CONFIGURATION",
        "GTKB_REASONING_EFFORT",
        "CODEX_MODEL_CONFIGURATION",
        "CLAUDE_MODEL_CONFIGURATION",
    ),
    "author_model_context_window": (
        "GTKB_AUTHOR_MODEL_CONTEXT_WINDOW",
        "GTKB_MODEL_CONTEXT_WINDOW",
        "CODEX_MODEL_CONTEXT_WINDOW",
        "CLAUDE_MODEL_CONTEXT_WINDOW",
    ),
    "author_metadata_source": ("GTKB_AUTHOR_METADATA_SOURCE",),
}

FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "author_identity": ("author_identity", "identity", "author", "harness_name"),
    "author_harness_id": ("author_harness_id", "harness_id"),
    "author_session_context_id": (
        "author_session_context_id",
        "author_session_id",
        "session_context_id",
        "session_id",
    ),
    "author_model": ("author_model", "model", "model_name"),
    "author_model_version": ("author_model_version", "model_version", "version"),
    "author_model_configuration": (
        "author_model_configuration",
        "model_configuration",
        "configuration",
        "reasoning_effort",
    ),
    "author_model_context_window": (
        "author_model_context_window",
        "model_context_window",
        "context_window",
    ),
    "author_metadata_source": ("author_metadata_source", "metadata_source", "source"),
}

AUTHOR_METADATA_LINE_RE = re.compile(
    r"^(?P<key>author_[a-z0-9_]+):\s*(?P<value>.*?)\s*$",
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


class BridgeAuthorMetadataError(RuntimeError):
    """Raised when required bridge author metadata is absent or not credible."""


def first_nonblank_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def bridge_artifact_status(content: str) -> str | None:
    first_line = first_nonblank_line(content).lstrip("\ufeff")
    return first_line if first_line in BRIDGE_AUTHOR_METADATA_STATUSES else None


def metadata_value_is_valid(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip().strip("`")
    return text.lower() not in PLACEHOLDER_VALUES


def _field_value(data: Mapping[str, Any], field: str) -> str | None:
    aliases = FIELD_ALIASES.get(field, (field,))
    lowered = {str(key).lower(): value for key, value in data.items()}
    for alias in aliases:
        value = lowered.get(alias.lower())
        if metadata_value_is_valid(value):
            return str(value).strip().strip("`")
    return None


def normalize_author_metadata(data: Mapping[str, Any] | None) -> dict[str, str]:
    if not data:
        return {}
    normalized: dict[str, str] = {}
    for field in (*REQUIRED_AUTHOR_METADATA_FIELDS, *OPTIONAL_AUTHOR_METADATA_FIELDS):
        value = _field_value(data, field)
        if value is not None:
            normalized[field] = value
    return normalized


def extract_author_metadata(content: str) -> dict[str, str]:
    return {
        match.group("key").lower(): match.group("value").strip() for match in AUTHOR_METADATA_LINE_RE.finditer(content)
    }


def author_metadata_gaps(metadata: Mapping[str, Any]) -> list[str]:
    normalized = normalize_author_metadata(metadata)
    gaps: list[str] = []
    for field in REQUIRED_AUTHOR_METADATA_FIELDS:
        raw_value = metadata.get(field)
        if field not in normalized:
            if raw_value is None:
                gaps.append(field)
            else:
                gaps.append(f"{field} (placeholder/invalid)")
    return gaps


def author_metadata_gaps_for_content(content: str) -> list[str]:
    if bridge_artifact_status(content) is None:
        return []
    return author_metadata_gaps(extract_author_metadata(content))


def validate_author_metadata(metadata: Mapping[str, Any]) -> dict[str, str]:
    normalized = normalize_author_metadata(metadata)
    gaps = author_metadata_gaps(metadata)
    if gaps:
        raise BridgeAuthorMetadataError(
            "bridge author metadata is missing or invalid: "
            + ", ".join(gaps)
            + ". Required fields: "
            + ", ".join(REQUIRED_AUTHOR_METADATA_FIELDS)
        )
    return normalized


def _load_json_metadata(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BridgeAuthorMetadataError(f"invalid bridge author metadata JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BridgeAuthorMetadataError(f"bridge author metadata JSON must be an object: {path}")
    return data


def _metadata_from_env(env: Mapping[str, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for field, names in FIELD_ENV_NAMES.items():
        for name in names:
            value = env.get(name)
            if metadata_value_is_valid(value):
                values[field] = str(value).strip().strip("`")
                break
    return values


def load_author_metadata(
    project_root: Path | None = None,
    *,
    explicit: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Load required author metadata from session file, environment, and explicit values.

    Precedence is explicit > environment > project-local session file. The
    returned mapping is validated and contains the required field names.
    """
    root = project_root or Path.cwd()
    merged: dict[str, Any] = {}
    merged.update(normalize_author_metadata(_load_json_metadata(root / AUTHOR_METADATA_RELATIVE_PATH)))
    merged.update(_metadata_from_env(env or os.environ))
    if explicit:
        merged.update(normalize_author_metadata(explicit))
    return validate_author_metadata(merged)


def render_author_metadata_lines(metadata: Mapping[str, Any]) -> list[str]:
    normalized = validate_author_metadata(metadata)
    lines = [f"{field}: {normalized[field]}\n" for field in REQUIRED_AUTHOR_METADATA_FIELDS]
    for field in OPTIONAL_AUTHOR_METADATA_FIELDS:
        value = normalized.get(field)
        if metadata_value_is_valid(value):
            lines.append(f"{field}: {value}\n")
    return lines


def ensure_author_metadata(
    content: str,
    *,
    project_root: Path | None = None,
    explicit: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    """Return bridge artifact content with required author metadata present.

    If the content is not a recognized bridge artifact status, it is returned
    unchanged. If the artifact already has complete metadata, it is also
    returned unchanged. Partial/placeholder author metadata is rejected so the
    helper never silently masks inaccurate audit fields.
    """
    if bridge_artifact_status(content) is None:
        return content

    existing = extract_author_metadata(content)
    if existing:
        gaps = author_metadata_gaps(existing)
        if not gaps:
            return content
        raise BridgeAuthorMetadataError(
            "bridge artifact contains partial or invalid author metadata: " + ", ".join(gaps)
        )

    metadata = load_author_metadata(project_root, explicit=explicit, env=env)
    metadata_lines = render_author_metadata_lines(metadata)
    lines = content.splitlines(keepends=True)
    if not lines:
        return "".join(metadata_lines)

    insert_idx = 0
    for idx, line in enumerate(lines):
        if line.strip():
            insert_idx = idx + 1
            if not line.endswith(("\n", "\r")):
                lines[idx] = line + "\n"
            break
    if insert_idx >= len(lines) or lines[insert_idx].strip():
        metadata_lines.append("\n")
    lines[insert_idx:insert_idx] = metadata_lines
    return "".join(lines)
