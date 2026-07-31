"""Shared formal-artifact approval packet construction and validation."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

REQUIRED_PACKET_FIELDS = {
    "artifact_type",
    "artifact_id",
    "action",
    "source_ref",
    "full_content",
    "full_content_sha256",
    "approval_mode",
    "presented_to_user",
    "transcript_captured",
    "explicit_change_request",
    "changed_by",
    "change_reason",
}

VALID_ARTIFACT_TYPES = {
    "deliberation",
    "governance",
    "requirement",
    "protected_behavior",
    "architecture_decision",
    "design_constraint",
}

VALID_APPROVAL_MODES = {"approve", "acknowledge", "edit-and-approve", "auto"}
VALID_CAPTURE_CONTEXTS = {"gap_state"}
POSTIMAGE_SCHEMA_VERSION = 1
POSTIMAGE_PACKET_FIELDS = {
    "postimage_schema_version",
    "postimage_fields",
    "postimage_sha256",
}


@dataclass(frozen=True)
class ValidationResult:
    """Formal approval packet validation result."""

    is_valid: bool
    errors: tuple[str, ...]


def content_hash(content: str) -> str:
    """Return the formal packet SHA-256 hash for a native content string."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _copy_json_native(value: object, *, path: str, active_containers: set[int] | None = None) -> object:
    """Return a detached JSON-native copy or raise for unsupported values."""

    active_containers = active_containers if active_containers is not None else set()
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} must not contain non-finite floats")
        return value
    if isinstance(value, list):
        container_id = id(value)
        if container_id in active_containers:
            raise ValueError(f"{path} must not contain reference cycles")
        active_containers.add(container_id)
        try:
            return [
                _copy_json_native(item, path=f"{path}[{index}]", active_containers=active_containers)
                for index, item in enumerate(value)
            ]
        finally:
            active_containers.remove(container_id)
    if isinstance(value, dict):
        container_id = id(value)
        if container_id in active_containers:
            raise ValueError(f"{path} must not contain reference cycles")
        active_containers.add(container_id)
        copied: dict[str, object] = {}
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError(f"{path} must contain only string object keys")
                copied[key] = _copy_json_native(
                    item,
                    path=f"{path}.{key}",
                    active_containers=active_containers,
                )
            return copied
        finally:
            active_containers.remove(container_id)
    raise ValueError(f"{path} contains unsupported JSON value type {type(value).__name__}")


def _detached_json_object(value: object, *, path: str) -> dict[str, object]:
    copied = _copy_json_native(value, path=path)
    if not isinstance(copied, dict):
        raise ValueError(f"{path} must be a JSON object")
    canonical = json.dumps(
        copied,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    detached = json.loads(canonical)
    if not isinstance(detached, dict):
        raise ValueError(f"{path} must be a JSON object")
    return detached


def _postimage_hash(
    *,
    artifact_type: object,
    artifact_id: object,
    action: object,
    source_ref: object,
    full_content_sha256: object,
    fields: dict[str, object],
) -> str:
    envelope = {
        "schema_version": POSTIMAGE_SCHEMA_VERSION,
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "action": action,
        "source_ref": source_ref,
        "full_content_sha256": full_content_sha256,
        "fields": fields,
    }
    canonical = json.dumps(
        envelope,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return content_hash(canonical)


def _validate_postimage(packet: Mapping[str, object]) -> str | None:
    present = POSTIMAGE_PACKET_FIELDS & set(packet)
    if not present:
        return None
    if present != POSTIMAGE_PACKET_FIELDS:
        missing = sorted(POSTIMAGE_PACKET_FIELDS - present)
        return f"approval packet postimage extension missing required fields: {', '.join(missing)}"

    schema_version = packet.get("postimage_schema_version")
    if type(schema_version) is not int or schema_version != 1:
        return "approval packet postimage_schema_version must be integer 1"

    fields = packet.get("postimage_fields")
    if not isinstance(fields, dict) or not fields:
        return "approval packet postimage_fields must be a non-empty JSON object"
    try:
        detached = _detached_json_object(fields, path="postimage_fields")
        expected_hash = _postimage_hash(
            artifact_type=packet.get("artifact_type"),
            artifact_id=packet.get("artifact_id"),
            action=packet.get("action"),
            source_ref=packet.get("source_ref"),
            full_content_sha256=packet.get("full_content_sha256"),
            fields=detached,
        )
    except (TypeError, ValueError) as exc:
        return f"approval packet postimage_fields must be JSON-native: {exc}"

    postimage_sha256 = packet.get("postimage_sha256")
    if (
        not isinstance(postimage_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", postimage_sha256) is None
        or postimage_sha256 != expected_hash
    ):
        return "approval packet postimage_sha256 does not match the canonical postimage envelope"
    return None


# WI-3313: project-authorization spec-amendment approval-packet helpers
# (DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001).
# The filename portion permits path separators so traversal citations are
# matched (and then rejected by the caller's in-root check); non-greedy so it
# stops at the first ``.json``.
_PACKET_PATH_RE = re.compile(r"\.groundtruth[/\\]formal-artifact-approvals[/\\][\w./\\-]+?\.json")


def parse_packet_path_from_change_reason(change_reason: str) -> str | None:
    """Return the relative formal-artifact-approval packet path cited in a
    ``change_reason`` string, normalized to forward slashes, or None when no
    such path is present.

    Resolution of the relative path against the project root is the caller's
    responsibility (so this helper stays free of filesystem assumptions).
    """
    match = _PACKET_PATH_RE.search(change_reason or "")
    if match is None:
        return None
    return match.group(0).replace("\\", "/")


def packet_covers_amendment(
    packet: Mapping[str, object],
    project_id: str,
    authorization_id: str,
    added_specs: set[str],
    removed_specs: set[str],
) -> tuple[bool, str]:
    """Return ``(covers, reason)`` for whether an approval packet covers a
    project-authorization spec amendment.

    A packet covers the amendment when its textual fields mention the project
    id (or the authorization id) AND every added and removed spec id. ``reason``
    explains the gap when ``covers`` is False.
    """
    packet_text = "\n".join(
        str(packet.get(field, "") or "")
        for field in ("artifact_id", "full_content", "explicit_change_request", "change_reason")
    )
    if project_id not in packet_text and authorization_id not in packet_text:
        return False, (f"packet does not mention project {project_id} or authorization {authorization_id}")
    amended = sorted(added_specs | removed_specs)
    missing = [spec_id for spec_id in amended if spec_id not in packet_text]
    if missing:
        return False, f"packet does not mention amended spec id(s): {', '.join(missing)}"
    return True, "covered"


def validate_packet(packet: Mapping[str, object]) -> ValidationResult:
    """Validate a formal-artifact approval packet.

    The rule order mirrors the original formal-artifact PreToolUse hook so
    callers can preserve existing block messages while sharing the same policy.
    """

    errors: list[str] = []
    missing = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing:
        errors.append(f"approval packet missing required fields: {', '.join(missing)}")
        return ValidationResult(is_valid=False, errors=tuple(errors))

    artifact_type = packet.get("artifact_type")
    if artifact_type not in VALID_ARTIFACT_TYPES:
        errors.append(
            f"approval packet artifact_type must be one of {sorted(VALID_ARTIFACT_TYPES)}, got {artifact_type!r}"
        )
        return ValidationResult(is_valid=False, errors=tuple(errors))

    approval_mode = packet.get("approval_mode")
    if approval_mode not in VALID_APPROVAL_MODES:
        errors.append(f"approval_mode must be one of {sorted(VALID_APPROVAL_MODES)}, got {approval_mode!r}")
        return ValidationResult(is_valid=False, errors=tuple(errors))

    full_content = packet.get("full_content")
    if not isinstance(full_content, str) or not full_content.strip():
        errors.append("approval packet full_content must be a non-empty string")
        return ValidationResult(is_valid=False, errors=tuple(errors))

    expected_hash = content_hash(full_content)
    if packet.get("full_content_sha256") != expected_hash:
        errors.append("approval packet full_content_sha256 does not match full_content")
        return ValidationResult(is_valid=False, errors=tuple(errors))

    postimage_error = _validate_postimage(packet)
    if postimage_error is not None:
        errors.append(postimage_error)
        return ValidationResult(is_valid=False, errors=tuple(errors))

    for flag_name in ("presented_to_user", "transcript_captured"):
        if packet.get(flag_name) is not True:
            errors.append(f"approval packet requires {flag_name}=true")
            return ValidationResult(is_valid=False, errors=tuple(errors))

    explicit_change = packet.get("explicit_change_request")
    if not isinstance(explicit_change, str) or not explicit_change.strip():
        errors.append("approval packet explicit_change_request must be a non-empty string")
        return ValidationResult(is_valid=False, errors=tuple(errors))

    if approval_mode == "auto":
        if not packet.get("auto_approval_scope"):
            errors.append("auto approval requires auto_approval_scope")
            return ValidationResult(is_valid=False, errors=tuple(errors))
        if packet.get("auto_approval_activated_by") != "owner":
            errors.append("auto approval requires auto_approval_activated_by='owner'")
            return ValidationResult(is_valid=False, errors=tuple(errors))
    elif not (packet.get("approved_by") or packet.get("acknowledged_by")):
        errors.append("manual approval requires approved_by or acknowledged_by")
        return ValidationResult(is_valid=False, errors=tuple(errors))

    expires_at = packet.get("expires_at")
    if expires_at:
        try:
            expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=UTC)
            if expiry < datetime.now(UTC):
                errors.append("approval packet is expired")
                return ValidationResult(is_valid=False, errors=tuple(errors))
        except ValueError:
            errors.append("approval packet expires_at must be ISO-8601 when present")
            return ValidationResult(is_valid=False, errors=tuple(errors))

    capture_context = packet.get("capture_context")
    if capture_context is not None:
        if capture_context not in VALID_CAPTURE_CONTEXTS:
            errors.append(f"capture_context must be one of {sorted(VALID_CAPTURE_CONTEXTS)}, got {capture_context!r}")
            return ValidationResult(is_valid=False, errors=tuple(errors))
        if capture_context == "gap_state":
            for field_name in ("gap_state_bridge_id", "gap_state_reason"):
                value = packet.get(field_name)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"gap_state capture requires non-empty {field_name}")
                    return ValidationResult(is_valid=False, errors=tuple(errors))
            operation = packet.get("intended_db_operation")
            if not isinstance(operation, Mapping) or not operation.get("method"):
                errors.append("gap_state capture requires intended_db_operation with method")
                return ValidationResult(is_valid=False, errors=tuple(errors))

    return ValidationResult(is_valid=True, errors=())


def construct_approval_packet(
    *,
    artifact_type: str,
    artifact_id: str,
    action: str,
    source_ref: str,
    full_content: str,
    approval_mode: str,
    presented_to_user: bool,
    transcript_captured: bool,
    explicit_change_request: str,
    changed_by: str,
    change_reason: str,
    approved_by: str | None = None,
    acknowledged_by: str | None = None,
    auto_approval_scope: str | None = None,
    auto_approval_activated_by: str | None = None,
    capture_context: str | None = None,
    gap_state_bridge_id: str | None = None,
    gap_state_reason: str | None = None,
    intended_db_operation: Mapping[str, object] | None = None,
    postimage_fields: Mapping[str, object] | None = None,
    expires_at: str | None = None,
) -> dict[str, object]:
    """Construct a formal approval packet dictionary with a bound content hash."""

    packet: dict[str, object] = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "action": action,
        "source_ref": source_ref,
        "full_content": full_content,
        "full_content_sha256": content_hash(full_content),
        "approval_mode": approval_mode,
        "presented_to_user": presented_to_user,
        "transcript_captured": transcript_captured,
        "explicit_change_request": explicit_change_request,
        "changed_by": changed_by,
        "change_reason": change_reason,
    }
    if approved_by:
        packet["approved_by"] = approved_by
    if acknowledged_by:
        packet["acknowledged_by"] = acknowledged_by
    if auto_approval_scope:
        packet["auto_approval_scope"] = auto_approval_scope
    if auto_approval_activated_by:
        packet["auto_approval_activated_by"] = auto_approval_activated_by
    if capture_context:
        packet["capture_context"] = capture_context
    if gap_state_bridge_id:
        packet["gap_state_bridge_id"] = gap_state_bridge_id
    if gap_state_reason:
        packet["gap_state_reason"] = gap_state_reason
    if intended_db_operation:
        packet["intended_db_operation"] = dict(intended_db_operation)
    if postimage_fields is not None:
        detached = _detached_json_object(dict(postimage_fields), path="postimage_fields")
        packet["postimage_schema_version"] = POSTIMAGE_SCHEMA_VERSION
        packet["postimage_fields"] = detached
        packet["postimage_sha256"] = _postimage_hash(
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            action=action,
            source_ref=source_ref,
            full_content_sha256=packet["full_content_sha256"],
            fields=detached,
        )
    if expires_at:
        packet["expires_at"] = expires_at
    return packet
