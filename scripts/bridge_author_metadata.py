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

try:
    from gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id
except ModuleNotFoundError:  # pragma: no cover
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id

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
# Retained one slice for out-of-band writers. WI-4522 removed the loader's READ
# of this shared file: as last-writer-wins mutable state it stamped a
# concurrently-dispatched headless worker with the previous harness's identity
# (the S389 GOV-DOCUMENT-AUTHOR-PROVENANCE-001 incident). `load_author_metadata`
# no longer reads it; a follow-on slice removes the constant + any write path
# once no readers remain.
AUTHOR_METADATA_RELATIVE_PATH = Path(".gtkb-state") / "bridge-author-metadata" / "current.json"

# Three-source harness-name resolution shares this env var with
# `scripts/_kb_attribution.ENV_VAR_HARNESS_NAME` (the canonical `changed_by`
# resolver); kept as a local constant so this module imports no attribution code
# at module scope (the durable-identity resolver imports locally to avoid a cycle).
ENV_VAR_HARNESS_NAME = "GTKB_HARNESS_NAME"

FIELD_ENV_NAMES: dict[str, tuple[str, ...]] = {
    "author_identity": ("GTKB_AUTHOR_IDENTITY", "GTKB_AUTHOR_NAME", "GTKB_HARNESS_NAME"),
    "author_harness_id": ("GTKB_AUTHOR_HARNESS_ID", "GTKB_HARNESS_ID", "CODEX_HARNESS_ID", "CLAUDE_HARNESS_ID"),
    "author_session_context_id": (
        "GTKB_AUTHOR_SESSION_CONTEXT_ID",
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_SESSION_ID",
        "CODEX_THREAD_ID",
        "GTKB_SESSION_ID",
        "CODEX_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
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
SYNTHETIC_SESSION_CONTEXT_IDS: frozenset[str] = frozenset(
    {
        "openrouter-harness-f",
        "ollama-harness-d",
    }
)
SYNTHETIC_SESSION_CONTEXT_RE = re.compile(r"^(?:openrouter|ollama)-harness-[a-z]$", re.IGNORECASE)


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


def is_synthetic_session_context_id(value: object) -> bool:
    """Return true for static bridge session placeholders, not real session ids."""
    if not metadata_value_is_valid(value):
        return False
    text = str(value).strip().strip("`")
    lowered = text.lower()
    return lowered in SYNTHETIC_SESSION_CONTEXT_IDS or SYNTHETIC_SESSION_CONTEXT_RE.fullmatch(text) is not None


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


def _runtime_session_context_id(environ: Mapping[str, str]) -> str:
    explicit = str(environ.get("GTKB_AUTHOR_SESSION_CONTEXT_ID") or "").strip()
    if metadata_value_is_valid(explicit):
        return explicit.strip("`")
    resolved = resolve_session_id(None, order=BRIDGE_WORK_INTENT_ORDER, environ=environ)
    if metadata_value_is_valid(resolved):
        return resolved.strip("`")
    return ""


def _replace_author_metadata_value(content: str, field: str, value: str) -> str:
    pattern = re.compile(rf"^(?P<key>{re.escape(field)}):\s*(?P<value>.*?)\s*$", re.IGNORECASE | re.MULTILINE)

    def replacement(match: re.Match[str]) -> str:
        return f"{match.group('key')}: {value}"

    return pattern.sub(replacement, content, count=1)


def _record_can_receive_dispatch(record: Mapping[str, object]) -> bool:
    """Return dispatchability for a projected harness role record."""
    if "can_receive_dispatch" in record:
        return record.get("can_receive_dispatch") is True
    return record.get("event_driven_hooks") is True


def _resolve_durable_identity_fields(
    project_root: Path,
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Resolve ONLY the two durable author-metadata fields from the harness registry.

    Returns ``{"author_identity": "<role>/<harness_name>", "author_harness_id":
    "<id>"}`` resolved per call from the filing harness's own durable identity,
    using the same ``<role>/<harness_name>`` label form as
    ``scripts/_kb_attribution.resolve_changed_by``. The filing harness is
    resolved with a two-source priority — ``GTKB_HARNESS_NAME`` env, then the
    active Prime Builder fallback in the registry projection at
    ``project_root``. If multiple active Prime Builders exist, fallback
    metadata resolves only when exactly one is dispatchable. ``project_root`` is
    threaded through the projection-backed loaders so callers (and tests) read
    the intended registry rather than a module-global root.

    Returns ``{}`` (never ``None``) when the filing harness cannot be resolved
    unambiguously — no ``GTKB_HARNESS_NAME`` and no unambiguous active
    Prime Builder fallback, no registry id for the resolved name, or no role
    assignment — so it contributes nothing rather than a wrong value, and an
    incomplete merged set fails closed in ``validate_author_metadata`` instead
    of inheriting another harness's values.

    It NEVER returns the four per-session runtime fields
    (``author_session_context_id``, ``author_model``, ``author_model_version``,
    ``author_model_configuration``): those have no durable GT-KB store and can
    only come from the filing harness's own runtime envelope (env/explicit).
    """
    # Local imports avoid a module import cycle (mirrors `_kb_attribution.py`).
    from scripts.harness_identity import load_harness_identities
    from scripts.harness_roles import (
        ROLE_ACTING_PRIME_BUILDER,
        ROLE_LOYAL_OPPOSITION,
        ROLE_PRIME_BUILDER,
        _normalize_role_field,
        is_prime_builder,
        load_role_assignments,
    )

    environ = env if env is not None else os.environ
    assignments = load_role_assignments(project_root).get("harnesses", {})
    identities = load_harness_identities(project_root).get("harnesses", {})

    harness_name = (environ.get(ENV_VAR_HARNESS_NAME) or "").strip()
    if not harness_name:
        prime_ids = [
            hid for hid, record in assignments.items() if isinstance(record, dict) and is_prime_builder(record)
        ]
        if len(prime_ids) > 1:
            prime_ids = [
                hid
                for hid in prime_ids
                if isinstance(assignments.get(hid), dict) and _record_can_receive_dispatch(assignments[hid])
            ]
        if len(prime_ids) != 1:
            return {}
        harness_name = next(
            (
                name
                for name, record in identities.items()
                if isinstance(record, dict) and record.get("id") == prime_ids[0]
            ),
            "",
        )
        if not harness_name:
            return {}

    identity_record = identities.get(harness_name)
    harness_id = identity_record.get("id") if isinstance(identity_record, dict) else None
    if not isinstance(harness_id, str) or not harness_id:
        return {}

    role_record = assignments.get(harness_id)
    if not isinstance(role_record, dict):
        return {}
    role_set = _normalize_role_field(role_record.get("role"))
    if ROLE_PRIME_BUILDER in role_set or ROLE_ACTING_PRIME_BUILDER in role_set:
        role = ROLE_PRIME_BUILDER
    elif ROLE_LOYAL_OPPOSITION in role_set:
        role = ROLE_LOYAL_OPPOSITION
    else:
        return {}

    return {"author_identity": f"{role}/{harness_name}", "author_harness_id": harness_id}


def load_author_metadata(
    project_root: Path | None = None,
    *,
    explicit: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Load required author metadata from the filing harness's own context.

    Precedence is explicit > environment runtime envelope > durable identity
    (the registry projection at ``project_root``). The two durable fields
    (``author_identity``, ``author_harness_id``) are resolved per call from the
    registry; the four per-session runtime fields come ONLY from the env runtime
    envelope or explicit values supplied by the filing harness — never from a
    shared on-disk baseline. A missing runtime envelope therefore fails closed in
    ``validate_author_metadata`` rather than inheriting another harness's cached
    values (WI-4522: removes the ``current.json`` shared-mutable provenance
    baseline; restores ``GOV-DOCUMENT-AUTHOR-PROVENANCE-001`` under concurrent
    headless filing). The returned mapping is validated and contains the required
    field names.
    """
    root = project_root or Path.cwd()
    environ = env or os.environ
    merged: dict[str, Any] = {}

    # Pre-populate only a stable session id for interactive sessions when it can
    # be resolved from the runtime envelope. Model identity must come from the
    # filing runtime, not from hardcoded guesses (WI-4885/WI-4939).
    interactive_defaults = {}
    harness_name = (environ.get(ENV_VAR_HARNESS_NAME) or "").strip()

    if harness_name:
        session_id = _runtime_session_context_id(environ)
        if session_id:
            interactive_defaults = {"author_session_context_id": session_id}

    env_copy = dict(environ)
    if harness_name and ENV_VAR_HARNESS_NAME not in env_copy:
        env_copy[ENV_VAR_HARNESS_NAME] = harness_name

    merged.update(interactive_defaults)
    merged.update(_resolve_durable_identity_fields(root, env=env_copy))
    merged.update(_metadata_from_env(environ))
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
            session_context_id = existing.get("author_session_context_id")
            runtime_session_id = _runtime_session_context_id(env or os.environ)
            if is_synthetic_session_context_id(session_context_id) and runtime_session_id:
                return _replace_author_metadata_value(content, "author_session_context_id", runtime_session_id)
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
