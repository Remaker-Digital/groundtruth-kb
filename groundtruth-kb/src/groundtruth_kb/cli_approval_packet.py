"""Implementation for the ``gt generate-approval-packet`` command."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.governance.approval_packet import construct_approval_packet, validate_packet
from groundtruth_kb.governance.narrative_artifact_packet import (
    build_narrative_packet,
    normalize_lf,
    project_relative_path,
    read_lf_normalized,
    validate_narrative_packet,
    write_packet,
)


class GenerateApprovalPacketError(Exception):
    """Raised when approval-packet generation cannot safely proceed."""


@dataclass(frozen=True)
class GenerateApprovalPacketRequest:
    kind: str
    target: Path | None
    artifact_id: str
    action: str
    source_ref: str
    explicit_change_request: str
    change_reason: str
    approval_mode: str
    changed_by: str
    out: Path | None
    stage: bool
    validate_after: bool
    artifact_type: str | None
    content_file: Path | None


def _default_packet_path(project_root: Path, artifact_id: str) -> Path:
    date_prefix = datetime.now(UTC).strftime("%Y-%m-%d")
    return project_root / ".groundtruth" / "formal-artifact-approvals" / f"{date_prefix}-{artifact_id}.json"


def _resolve_output_path(project_root: Path, request: GenerateApprovalPacketRequest) -> Path:
    if request.out is None:
        return _default_packet_path(project_root, request.artifact_id)
    if request.out.is_absolute():
        return request.out
    return project_root / request.out


def _require_text(value: str, option_name: str) -> None:
    if not value.strip():
        raise GenerateApprovalPacketError(f"{option_name} must be non-empty")


def _stage_paths(project_root: Path, paths: list[Path]) -> None:
    rel_paths: list[str] = []
    for path in paths:
        rel_paths.append(project_relative_path(path, project_root))
    try:
        subprocess.run(["git", "add", "--", *rel_paths], cwd=project_root, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise GenerateApprovalPacketError(f"git add failed: {detail}") from exc


def _approval_identity_fields(approval_mode: str, source_ref: str) -> dict[str, str]:
    if approval_mode in {"approve", "edit-and-approve"}:
        return {"approved_by": "owner"}
    if approval_mode == "acknowledge":
        return {"acknowledged_by": "owner"}
    if approval_mode == "auto":
        return {
            "auto_approval_scope": f"source_ref:{source_ref}",
            "auto_approval_activated_by": "owner",
        }
    return {}


def _build_formal_packet(project_root: Path, request: GenerateApprovalPacketRequest) -> dict[str, object]:
    if request.content_file is None:
        raise GenerateApprovalPacketError("--content-file is required when --kind formal")
    if request.artifact_type is None:
        raise GenerateApprovalPacketError("--artifact-type is required when --kind formal")

    content_path = request.content_file if request.content_file.is_absolute() else project_root / request.content_file
    try:
        project_relative_path(content_path, project_root)
    except ValueError as exc:
        raise GenerateApprovalPacketError("--content-file must be inside the project root") from exc
    if not content_path.exists():
        raise GenerateApprovalPacketError(f"--content-file does not exist: {content_path}")

    full_content = normalize_lf(read_lf_normalized(content_path))
    packet = construct_approval_packet(
        artifact_type=request.artifact_type,
        artifact_id=request.artifact_id,
        action=request.action,
        source_ref=request.source_ref,
        full_content=full_content,
        approval_mode=request.approval_mode,
        presented_to_user=True,
        transcript_captured=True,
        explicit_change_request=request.explicit_change_request,
        changed_by=request.changed_by,
        change_reason=request.change_reason,
        **_approval_identity_fields(request.approval_mode, request.source_ref),
    )
    validation = validate_packet(packet)
    if not validation.is_valid:
        raise GenerateApprovalPacketError("; ".join(validation.errors))
    return packet


def _validate_formal_packet_file(out_path: Path) -> None:
    try:
        packet = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GenerateApprovalPacketError(f"written approval packet could not be read back: {exc}") from exc
    if not isinstance(packet, dict):
        raise GenerateApprovalPacketError("written approval packet root must be a JSON object")
    validation = validate_packet(packet)
    if not validation.is_valid:
        raise GenerateApprovalPacketError("; ".join(validation.errors))


def _build_narrative_packet(project_root: Path, request: GenerateApprovalPacketRequest) -> dict[str, object]:
    if request.target is None:
        raise GenerateApprovalPacketError("--target is required when --kind narrative")

    target_path = request.target if request.target.is_absolute() else project_root / request.target
    try:
        rel_path = project_relative_path(target_path, project_root)
    except ValueError as exc:
        raise GenerateApprovalPacketError("--target must be inside the project root") from exc
    if not target_path.exists():
        raise GenerateApprovalPacketError(f"--target does not exist: {target_path}")

    packet = build_narrative_packet(
        project_root=project_root,
        target_path=target_path,
        artifact_id=request.artifact_id,
        action=request.action,
        source_ref=request.source_ref,
        approval_mode=request.approval_mode,
        explicit_change_request=request.explicit_change_request,
        changed_by=request.changed_by,
        change_reason=request.change_reason,
    )
    validation = validate_narrative_packet(packet, rel_path=rel_path)
    if not validation.is_valid:
        raise GenerateApprovalPacketError("; ".join(validation.errors))
    return packet


def _validate_narrative_packet_file(out_path: Path, rel_path: str) -> None:
    try:
        packet = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GenerateApprovalPacketError(f"written approval packet could not be read back: {exc}") from exc
    if not isinstance(packet, dict):
        raise GenerateApprovalPacketError("written approval packet root must be a JSON object")
    validation = validate_narrative_packet(packet, rel_path=rel_path)
    if not validation.is_valid:
        raise GenerateApprovalPacketError("; ".join(validation.errors))


def run_generate_approval_packet(config: GTConfig, request: GenerateApprovalPacketRequest) -> dict[str, Any]:
    """Generate an approval packet and optionally stage it with its target."""

    _require_text(request.artifact_id, "--artifact-id")
    _require_text(request.source_ref, "--source-ref")
    _require_text(request.explicit_change_request, "--explicit-change-request")
    _require_text(request.change_reason, "--change-reason")
    _require_text(request.changed_by, "--changed-by")

    project_root = config.project_root.resolve()
    out_path = _resolve_output_path(project_root, request).resolve()
    if out_path.exists():
        raise GenerateApprovalPacketError(f"approval packet already exists: {out_path}")

    if request.kind == "narrative":
        if request.target is None:
            raise GenerateApprovalPacketError("--target is required when --kind narrative")
        target_path = request.target if request.target.is_absolute() else project_root / request.target
        try:
            narrative_rel_path = project_relative_path(target_path, project_root)
        except ValueError as exc:
            raise GenerateApprovalPacketError("--target must be inside the project root") from exc
        packet = _build_narrative_packet(project_root, request)
        stage_targets = [target_path]
    elif request.kind == "formal":
        packet = _build_formal_packet(project_root, request)
        narrative_rel_path = None
        stage_targets = []
    else:
        raise GenerateApprovalPacketError("--kind must be one of: narrative, formal")

    write_packet(packet, out_path)
    if request.validate_after:
        if request.kind == "narrative":
            if narrative_rel_path is None:
                raise GenerateApprovalPacketError("internal error: narrative target path was not resolved")
            _validate_narrative_packet_file(out_path, narrative_rel_path)
        else:
            _validate_formal_packet_file(out_path)

    staged = False
    staged_paths: list[str] = []
    if request.stage:
        paths_to_stage = [*stage_targets, out_path]
        _stage_paths(project_root, paths_to_stage)
        staged = True
        staged_paths = [project_relative_path(path, project_root) for path in paths_to_stage]

    return {
        "kind": request.kind,
        "artifact_id": request.artifact_id,
        "approval_packet_path": str(out_path),
        "approval_packet": packet,
        "staged": staged,
        "staged_paths": staged_paths,
    }


def format_result(result: dict[str, Any], *, json_output: bool) -> str:
    """Format command output for humans or machines."""

    if json_output:
        return json.dumps(result, indent=2, sort_keys=True)
    return str(result["approval_packet_path"])
