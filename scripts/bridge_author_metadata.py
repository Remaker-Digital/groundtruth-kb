"""Author/runtime metadata helpers for bridge artifacts.

Bridge artifacts are audit records. The model/session that authored them must
carry accurate identity and model configuration metadata; helpers fail closed
when that metadata is unavailable rather than guessing.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    from gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id
except ModuleNotFoundError:  # pragma: no cover
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id

BRIDGE_AUTHOR_METADATA_STATUSES: frozenset[str] = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED", "NO-ACTION"}
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
    "author_session_envelope_id",
    "author_role_attestation",
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
CODEX_TURN_METADATA_SOURCE = "x-codex-turn-metadata"
CURSOR_CONVERSATION_METADATA_SOURCE = "cursor-conversation-metadata"
_EXACT_SESSION_METADATA_SOURCE_BY_HARNESS: dict[str, str] = {
    "codex": CODEX_TURN_METADATA_SOURCE,
    "cursor": CURSOR_CONVERSATION_METADATA_SOURCE,
}

# Three-source harness-name resolution shares this env var with
# `scripts/_kb_attribution.ENV_VAR_HARNESS_NAME` (the canonical `changed_by`
# resolver); kept as a local constant so this module imports no attribution code
# at module scope (the durable-identity resolver imports locally to avoid a cycle).
ENV_VAR_HARNESS_NAME = "GTKB_HARNESS_NAME"

FIELD_ENV_NAMES: dict[str, tuple[str, ...]] = {
    # GTKB_HARNESS_NAME is a harness-identity hint, never an author-role source.
    "author_identity": ("GTKB_AUTHOR_IDENTITY", "GTKB_AUTHOR_NAME"),
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
    "author_session_envelope_id": ("author_session_envelope_id", "session_envelope_id"),
    "author_role_attestation": ("author_role_attestation", "acting_role_attestation"),
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
DISPATCH_RUN_ID_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<role>acting-prime-builder|loyal-opposition|prime-builder)-"
    r"(?P<harness_id>[A-Za-z][A-Za-z0-9]*)-"
    r"(?P<suffix>[0-9a-fA-F]{6})$"
)


class BridgeAuthorMetadataError(RuntimeError):
    """Raised when required bridge author metadata is absent or not credible."""


def resolve_author_metadata(project_root: Path | None = None) -> dict[str, str]:
    """Resolve author metadata through the exact-init authority boundary."""
    return load_author_metadata(project_root)


def _emit_metadata(project_root: Path | None = None) -> int:
    """CLI mode: emit resolved metadata as YAML-like frontmatter lines."""
    try:
        resolved = resolve_author_metadata(project_root)
    except BridgeAuthorMetadataError as exc:
        print(f"bridge author metadata unavailable: {exc}", file=sys.stderr)
        return 1
    for field_name in sorted(resolved):
        print(f"{field_name}: {resolved[field_name]}")
    return 0


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
    identity = normalized.get("author_identity")
    if identity:
        from scripts.bridge_lifecycle_resolver import _author_role

        if _author_role(identity) not in {"prime-builder", "loyal-opposition"}:
            gaps.append("author_identity (missing exact session role)")
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


def _harness_name_from_identity_fields(identity_fields: Mapping[str, str]) -> str:
    identity = identity_fields.get("author_identity", "")
    if "/" not in identity:
        return ""
    return identity.rsplit("/", 1)[-1].strip().lower()


def _metadata_from_exact_session_envelope(
    project_root: Path,
    *,
    environ: Mapping[str, str],
    explicit: Mapping[str, str],
    identity_fields: Mapping[str, str],
) -> dict[str, str]:
    """Load author model metadata only from the exact validated session document."""
    from groundtruth_kb.session.envelope import EnvelopeError, load_worker_session

    session_id = explicit.get("author_session_context_id") or _runtime_session_context_id(environ)
    harness_name = (environ.get(ENV_VAR_HARNESS_NAME) or "").strip().lower()
    if not harness_name:
        harness_name = _harness_name_from_identity_fields(identity_fields)
    harness_id = identity_fields.get("author_harness_id", "")
    if not session_id or not harness_name or not harness_id:
        return {}
    expected_metadata_source = _EXACT_SESSION_METADATA_SOURCE_BY_HARNESS.get(harness_name)
    if expected_metadata_source is None:
        return {}

    try:
        envelope = load_worker_session(project_root, harness_name, session_id)
        if envelope is None:
            return {}
        if envelope.get("session_id") != session_id:
            raise BridgeAuthorMetadataError("exact session author metadata has a mismatched session id")
        if envelope.get("harness_name") != harness_name or envelope.get("harness_id") != harness_id:
            raise BridgeAuthorMetadataError("exact session author metadata has mismatched harness identity")
        if envelope.get("status") != "open":
            raise BridgeAuthorMetadataError("exact session author metadata requires an open session envelope")
        if envelope.get("model_metadata_source") != expected_metadata_source:
            raise BridgeAuthorMetadataError(
                f"exact session author metadata is not attested by {expected_metadata_source}"
            )
    except EnvelopeError as exc:
        raise BridgeAuthorMetadataError(f"exact session author metadata is invalid: {exc}") from exc

    candidate = normalize_author_metadata(
        {
            "author_session_context_id": session_id,
            "author_model": envelope.get("model_id"),
            "author_model_version": envelope.get("model_version"),
            "author_model_configuration": envelope.get("model_configuration"),
            "author_metadata_source": envelope.get("model_metadata_source"),
        }
    )
    return candidate


def _replace_author_metadata_value(content: str, field: str, value: str) -> str:
    pattern = re.compile(rf"^(?P<key>{re.escape(field)}):\s*(?P<value>.*?)\s*$", re.IGNORECASE | re.MULTILINE)

    def replacement(match: re.Match[str]) -> str:
        return f"{match.group('key')}: {value}"

    return pattern.sub(replacement, content, count=1)


def _dispatch_harness_id_from_run_id(value: object) -> str | None:
    """Return the durable harness id from a dispatcher run id, if well-formed."""
    if not metadata_value_is_valid(value):
        return None
    match = DISPATCH_RUN_ID_RE.fullmatch(str(value).strip().strip("`"))
    if match is None:
        return None
    return match.group("harness_id").upper()


def _declared_harness_name(author_identity: str) -> str:
    """Extract only a harness label from caller-declared author identity."""

    value = str(author_identity or "").strip().strip("`")
    if not value:
        return ""
    parts = [part.strip() for part in value.split("/") if part.strip()]
    if parts and parts[0].lower() in {"prime-builder", "loyal-opposition", "acting-prime-builder"}:
        return parts[1].lower() if len(parts) > 1 else ""
    return value.lower()


def _resolve_harness_identity_fields(
    project_root: Path,
    *,
    env: Mapping[str, str] | None = None,
    declared_identity: str = "",
    declared_harness_id: str = "",
) -> dict[str, str]:
    """Resolve the acting harness name/ID without consulting any role field."""

    from scripts.harness_identity import load_harness_identities

    environ = env if env is not None else os.environ
    identities = load_harness_identities(project_root).get("harnesses", {})

    harness_name = (environ.get(ENV_VAR_HARNESS_NAME) or "").strip().lower()
    if not harness_name and environ.get("CURSOR_AGENT") == "1" and environ.get("CURSOR_CONVERSATION_ID"):
        harness_name = "cursor"
    if not harness_name:
        dispatch_harness_id = _dispatch_harness_id_from_run_id(environ.get("GTKB_BRIDGE_POLLER_RUN_ID"))
        if dispatch_harness_id:
            harness_name = next(
                (
                    name
                    for name, record in identities.items()
                    if isinstance(record, dict) and record.get("id") == dispatch_harness_id
                ),
                "",
            )
            if not harness_name:
                return {}

    declared_harness_name = _declared_harness_name(declared_identity)
    if harness_name and declared_harness_name and declared_harness_name != harness_name:
        raise BridgeAuthorMetadataError(
            f"declared author harness {declared_harness_name!r} conflicts with the acting harness {harness_name!r}"
        )
    if not harness_name:
        harness_name = declared_harness_name

    if not harness_name and declared_harness_id:
        harness_name = next(
            (
                name
                for name, record in identities.items()
                if isinstance(record, dict) and record.get("id") == declared_harness_id
            ),
            "",
        )

    if not harness_name:
        try:
            from groundtruth_kb.session.envelope import EnvelopeError, resolve_acting_harness_identity

            harness_name, _resolved_harness_id = resolve_acting_harness_identity(project_root)
        except (EnvelopeError, ImportError):
            return {}

    identity_record = identities.get(harness_name)
    harness_id = identity_record.get("id") if isinstance(identity_record, dict) else None
    if not isinstance(harness_id, str) or not harness_id:
        harness_id = declared_harness_id
    if not harness_id:
        return {}
    if declared_harness_id and declared_harness_id != harness_id:
        raise BridgeAuthorMetadataError(
            f"declared author_harness_id {declared_harness_id!r} conflicts with "
            f"the owner-assigned identity {harness_id!r} for {harness_name!r}"
        )

    return {"harness_name": harness_name, "author_harness_id": harness_id}


def _resolve_attested_authority_fields(
    project_root: Path,
    *,
    session_context_id: str,
    harness_name: str,
    supplied: Mapping[str, str],
) -> dict[str, str]:
    """Resolve author role only from this context's immutable exact-init binding."""

    try:
        from groundtruth_kb.session.attestation.service import (
            RoleAttestationError,
            binding_for_context,
        )

        binding = binding_for_context(
            project_root / "groundtruth.db",
            session_context_id,
        )
    except (ImportError, RoleAttestationError) as exc:
        raise BridgeAuthorMetadataError(f"exact-init author session binding is unavailable: {exc}") from exc
    role = str(binding.role or "").strip().lower()
    if role not in {"prime-builder", "loyal-opposition"}:
        raise BridgeAuthorMetadataError(f"unsupported exact-init author role: {role or '<missing>'}")

    declared_identity = str(supplied.get("author_identity") or "").strip()
    if declared_identity and "/" in declared_identity:
        declared_role = declared_identity.split("/", 1)[0].strip().lower()
        if declared_role != role:
            raise BridgeAuthorMetadataError(
                f"declared author role {declared_role!r} conflicts with exact-init role {role!r}"
            )

    resolved = {
        "author_identity": f"{role}/{harness_name}",
        "author_session_context_id": session_context_id,
        "author_session_envelope_id": binding.session_context_id,
        "author_role_attestation": binding.evidence_reference,
    }
    for field in ("author_session_envelope_id", "author_role_attestation"):
        declared = str(supplied.get(field) or "").strip()
        if declared and declared != resolved[field]:
            raise BridgeAuthorMetadataError(f"declared {field} conflicts with exact-init binding evidence")
    return resolved


def load_author_metadata(
    project_root: Path | None = None,
    *,
    explicit: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Load author metadata with role fixed by the exact-init attestation.

    Harness identity and model data remain attribution inputs. Neither can
    supply, override, or repair the running session's role.
    """
    root = project_root or Path.cwd()
    environ = env or os.environ
    merged: dict[str, Any] = {}
    explicit_metadata = normalize_author_metadata(explicit)
    environment_metadata = _metadata_from_env(environ)

    supplied_runtime_fields = {
        **environment_metadata,
        **explicit_metadata,
    }
    session_context_id = str(supplied_runtime_fields.get("author_session_context_id") or "").strip()
    if not session_context_id:
        session_context_id = _runtime_session_context_id(environ)
    declared_identity = str(supplied_runtime_fields.get("author_identity") or "").strip()
    declared_harness_id = str(supplied_runtime_fields.get("author_harness_id") or "").strip()
    harness_identity = _resolve_harness_identity_fields(
        root,
        env=environ,
        declared_identity=declared_identity,
        declared_harness_id=declared_harness_id,
    )
    harness_name = str(harness_identity.get("harness_name") or "").strip()
    if not session_context_id or not harness_name:
        raise BridgeAuthorMetadataError(
            "exact bridge author context requires both an invoking session id and acting harness identity"
        )
    authority_fields = _resolve_attested_authority_fields(
        root,
        session_context_id=session_context_id,
        harness_name=harness_name,
        supplied=supplied_runtime_fields,
    )
    identity_fields = {
        "author_identity": authority_fields["author_identity"],
        "author_harness_id": harness_identity["author_harness_id"],
    }
    runtime_fields = {
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    }
    runtime_model_fields = {
        "author_model",
        "author_model_version",
        "author_model_configuration",
        "author_model_context_window",
        "author_metadata_source",
    }
    required_runtime_model_fields = {
        "author_model",
        "author_model_version",
        "author_model_configuration",
    }
    supplied_runtime_model_fields = runtime_model_fields.intersection(supplied_runtime_fields)
    if supplied_runtime_model_fields and not required_runtime_model_fields.issubset(supplied_runtime_fields):
        missing = sorted(required_runtime_model_fields.difference(supplied_runtime_fields))
        raise BridgeAuthorMetadataError(
            "partial runtime model metadata is invalid; missing required fields: " + ", ".join(missing)
        )

    merged.update(identity_fields)
    if not runtime_fields.issubset(supplied_runtime_fields):
        merged.update(
            _metadata_from_exact_session_envelope(
                root,
                environ=environ,
                explicit=explicit_metadata,
                identity_fields=identity_fields,
            )
        )
    merged.update(environment_metadata)
    merged.update(explicit_metadata)
    # Caller/env values can describe model or harness identity, but never role,
    # session binding, or attestation evidence.
    merged.update(identity_fields)
    merged.update(authority_fields)
    return validate_author_metadata(merged)


def render_author_metadata_lines(metadata: Mapping[str, Any]) -> list[str]:
    normalized = validate_author_metadata(metadata)
    lines = [f"{field}: {normalized[field]}\n" for field in REQUIRED_AUTHOR_METADATA_FIELDS]
    for field in OPTIONAL_AUTHOR_METADATA_FIELDS:
        value = normalized.get(field)
        if metadata_value_is_valid(value):
            lines.append(f"{field}: {value}\n")
    return lines


def _insert_missing_optional_metadata(
    content: str,
    *,
    existing: Mapping[str, str],
    explicit: Mapping[str, Any] | None,
) -> str:
    """Add trusted optional fields to otherwise-complete existing metadata."""

    supplied = normalize_author_metadata(explicit)
    additions = [
        (field, supplied[field])
        for field in OPTIONAL_AUTHOR_METADATA_FIELDS
        if field in supplied and not metadata_value_is_valid(existing.get(field))
    ]
    if not additions:
        return content

    lines = content.splitlines(keepends=True)
    metadata_indices = [
        index for index, line in enumerate(lines) if AUTHOR_METADATA_LINE_RE.fullmatch(line.rstrip("\r\n")) is not None
    ]
    insert_idx = max(metadata_indices) + 1 if metadata_indices else 1
    newline = "\r\n" if "\r\n" in content else "\n"
    lines[insert_idx:insert_idx] = [f"{field}: {value}{newline}" for field, value in additions]
    return "".join(lines)


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
                content = _replace_author_metadata_value(content, "author_session_context_id", runtime_session_id)
                existing = extract_author_metadata(content)
            return _insert_missing_optional_metadata(content, existing=existing, explicit=explicit)
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


if __name__ == "__main__":
    raise SystemExit(_emit_metadata())
