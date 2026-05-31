"""Narrative-artifact approval packet construction and validation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

NARRATIVE_ARTIFACT_TYPE = "narrative_artifact"

REQUIRED_PACKET_FIELDS = {
    "artifact_type",
    "artifact_id",
    "action",
    "target_path",
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

VALID_ACTIONS = {"create", "update", "delete"}
VALID_APPROVAL_MODES = {"approve", "acknowledge", "edit-and-approve", "auto"}


@dataclass(frozen=True)
class NarrativeValidationResult:
    """Narrative-artifact approval packet validation result."""

    is_valid: bool
    errors: tuple[str, ...]


def normalize_lf(content: str) -> str:
    """Return content with CRLF and bare CR normalized to LF."""

    return content.replace("\r\n", "\n").replace("\r", "\n")


def read_lf_normalized(path: Path) -> str:
    """Read UTF-8 content from path and normalize line endings to LF."""

    return normalize_lf(path.read_bytes().decode("utf-8"))


def content_hash(content: str) -> str:
    """Return the SHA-256 hash used by narrative-artifact packets."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def project_relative_path(path: Path, project_root: Path) -> str:
    """Return path relative to project_root as a forward-slash string."""

    resolved_root = project_root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise ValueError(f"path must be inside project root: {resolved_path}") from exc


def validate_narrative_packet(
    packet: Mapping[str, object],
    *,
    rel_path: str | None = None,
    proposed_content: str | None = None,
) -> NarrativeValidationResult:
    """Validate a narrative-artifact approval packet.

    The checks intentionally mirror the narrative-artifact PreToolUse hook so
    CLI-generated packets stay compatible with both the hook and the universal
    pre-commit evidence floor.
    """

    errors: list[str] = []
    missing = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing:
        errors.append(f"approval packet missing required fields: {', '.join(missing)}")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    if packet.get("artifact_type") != NARRATIVE_ARTIFACT_TYPE:
        errors.append(
            f"approval packet artifact_type must be {NARRATIVE_ARTIFACT_TYPE!r} "
            f"for narrative-artifact gate; got {packet.get('artifact_type')!r}"
        )
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    action = packet.get("action")
    if action not in VALID_ACTIONS:
        errors.append(f"action must be one of {sorted(VALID_ACTIONS)}, got {action!r}")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    approval_mode = packet.get("approval_mode")
    if approval_mode not in VALID_APPROVAL_MODES:
        errors.append(f"approval_mode must be one of {sorted(VALID_APPROVAL_MODES)}, got {approval_mode!r}")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    target = packet.get("target_path")
    if not isinstance(target, str) or not target.strip():
        errors.append("approval packet target_path must be a non-empty string")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))
    if rel_path is not None and Path(target).as_posix() != rel_path:
        errors.append(f"approval packet target_path {target!r} does not match write target {rel_path!r}")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    full_content = packet.get("full_content")
    if not isinstance(full_content, str) or not full_content:
        errors.append("approval packet full_content must be a non-empty string")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    expected_hash = content_hash(full_content)
    if packet.get("full_content_sha256") != expected_hash:
        errors.append("approval packet full_content_sha256 does not match full_content")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    if proposed_content is not None and normalize_lf(proposed_content) != full_content:
        errors.append("approval packet full_content does not match the proposed content")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    for flag_name in ("presented_to_user", "transcript_captured"):
        if packet.get(flag_name) is not True:
            errors.append(f"approval packet requires {flag_name}=true")
            return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    explicit_change = packet.get("explicit_change_request")
    if not isinstance(explicit_change, str) or not explicit_change.strip():
        errors.append("approval packet explicit_change_request must be non-empty")
        return NarrativeValidationResult(is_valid=False, errors=tuple(errors))

    return NarrativeValidationResult(is_valid=True, errors=())


def build_narrative_packet(
    *,
    project_root: Path,
    target_path: Path,
    artifact_id: str,
    action: str,
    source_ref: str,
    approval_mode: str,
    explicit_change_request: str,
    changed_by: str,
    change_reason: str,
) -> dict[str, object]:
    """Build a narrative-artifact approval packet from a target file."""

    full_content = read_lf_normalized(target_path)
    packet: dict[str, object] = {
        "artifact_type": NARRATIVE_ARTIFACT_TYPE,
        "artifact_id": artifact_id,
        "action": action,
        "target_path": project_relative_path(target_path, project_root),
        "source_ref": source_ref,
        "full_content": full_content,
        "full_content_sha256": content_hash(full_content),
        "approval_mode": approval_mode,
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": explicit_change_request,
        "changed_by": changed_by,
        "change_reason": change_reason,
    }
    if approval_mode in {"approve", "edit-and-approve"}:
        packet["approved_by"] = "owner"
    elif approval_mode == "acknowledge":
        packet["acknowledged_by"] = "owner"
    elif approval_mode == "auto":
        packet["auto_approval_scope"] = f"source_ref:{source_ref}"
        packet["auto_approval_activated_by"] = "owner"
    return packet


def packet_json(packet: Mapping[str, object]) -> str:
    """Return deterministic JSON text for an approval packet."""

    return json.dumps(packet, indent=2, sort_keys=True) + "\n"


def write_packet(packet: Mapping[str, object], out_path: Path) -> None:
    """Write an approval packet with LF JSON newlines on every platform."""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(packet_json(packet).encode("utf-8"))
