"""Shared formal-artifact approval packet construction and validation."""

from __future__ import annotations

import hashlib
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


@dataclass(frozen=True)
class ValidationResult:
    """Formal approval packet validation result."""

    is_valid: bool
    errors: tuple[str, ...]


def content_hash(content: str) -> str:
    """Return the formal packet SHA-256 hash for a native content string."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# WI-3313: project-authorization spec-amendment approval-packet helpers
# (DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001).
# The filename portion permits path separators so traversal citations are
# matched (and then rejected by the caller's in-root check); non-greedy so it
# stops at the first ``.json``.
_PACKET_PATH_RE = re.compile(
    r"\.groundtruth[/\\]formal-artifact-approvals[/\\][\w./\\-]+?\.json"
)


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
        return False, (
            f"packet does not mention project {project_id} or "
            f"authorization {authorization_id}"
        )
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
    if expires_at:
        packet["expires_at"] = expires_at
    return packet
