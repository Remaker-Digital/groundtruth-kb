#!/usr/bin/env python3
"""Post-action audit receipt contract and evidence correlation helpers."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

RECEIPT_SCHEMA_VERSION = 1
RECEIPTS_RELATIVE_DIR = Path(".gtkb-state/post-action-receipts")
IMPLEMENTATION_PACKETS_RELATIVE_DIR = Path(".gtkb-state/implementation-authorizations")
FORMAL_APPROVALS_RELATIVE_DIR = Path(".groundtruth/formal-artifact-approvals")

MUTATION_CLASSES = frozenset(
    {
        "file",
        "config",
        "bridge",
        "membase",
        "cloud_deployment",
        "external_service",
    }
)

REQUIRED_TEXT_FIELDS = (
    "receipt_id",
    "generated_at",
    "mutation_class",
    "action_summary",
    "initiating_authority",
    "bridge_thread",
    "bridge_version",
    "work_item",
    "commit_push_rationale",
    "author_identity",
    "author_harness_id",
    "author_session_context_id",
    "author_model",
)
REQUIRED_SEQUENCE_FIELDS = (
    "target_paths",
    "commands_run",
    "verification_evidence",
    "residual_dirty_tree",
)
SAFE_RECEIPT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ReceiptValidationError(ValueError):
    """Raised when a post-action receipt cannot be treated as valid evidence."""


@dataclass(frozen=True)
class PostActionReceipt:
    """Durable evidence record emitted after a governed mutation."""

    receipt_id: str
    generated_at: str
    mutation_class: str
    action_summary: str
    initiating_authority: str
    bridge_thread: str
    bridge_version: str
    work_item: str
    target_paths: tuple[str, ...]
    commands_run: tuple[Any, ...]
    verification_evidence: tuple[Any, ...]
    residual_dirty_tree: tuple[str, ...]
    commit_push_recommended: bool
    commit_push_rationale: str
    author_identity: str
    author_harness_id: str
    author_session_context_id: str
    author_model: str
    schema_version: int = RECEIPT_SCHEMA_VERSION
    evidence_sources: Mapping[str, Any] = field(default_factory=dict)


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def now_iso() -> str:
    return now_utc().isoformat().replace("+00:00", "Z")


def _parse_generated_at(value: str) -> datetime:
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def new_receipt_id(prefix: str, *, generated_at: str | None = None, nonce: str | None = None) -> str:
    """Return a stable, path-safe receipt id for a new post-action record."""

    stamp = (generated_at or now_iso()).replace(":", "").replace("+00:00", "Z")
    digest_source = f"{prefix}|{stamp}|{nonce or uuid.uuid4().hex}"
    digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:12]
    safe_prefix = re.sub(r"[^A-Za-z0-9._-]+", "-", prefix).strip("-._") or "receipt"
    return f"{safe_prefix}-{stamp}-{digest}"


def receipt_to_dict(receipt: PostActionReceipt | Mapping[str, Any]) -> dict[str, Any]:
    """Return a JSON-ready dictionary for ``receipt``."""

    if dataclasses.is_dataclass(receipt):
        data = dataclasses.asdict(receipt)
    else:
        data = dict(receipt)
    for key in REQUIRED_SEQUENCE_FIELDS:
        if key in data and isinstance(data[key], tuple):
            data[key] = list(data[key])
    if "evidence_sources" in data and isinstance(data["evidence_sources"], Mapping):
        data["evidence_sources"] = dict(data["evidence_sources"])
    data.setdefault("schema_version", RECEIPT_SCHEMA_VERSION)
    return data


def validate_receipt(receipt: PostActionReceipt | Mapping[str, Any]) -> list[str]:
    """Return validation errors for ``receipt`` without mutating anything."""

    errors: list[str] = []
    data = receipt_to_dict(receipt)

    if data.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {RECEIPT_SCHEMA_VERSION}")

    for field_name in REQUIRED_TEXT_FIELDS:
        value = data.get(field_name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field_name} must be a non-empty string")

    receipt_id = data.get("receipt_id")
    if isinstance(receipt_id, str) and receipt_id.strip() and not SAFE_RECEIPT_ID_RE.fullmatch(receipt_id):
        errors.append("receipt_id must be path-safe")

    generated_at = data.get("generated_at")
    if isinstance(generated_at, str) and generated_at.strip():
        try:
            _parse_generated_at(generated_at)
        except ValueError:
            errors.append("generated_at must be ISO-8601")

    if data.get("mutation_class") not in MUTATION_CLASSES:
        errors.append(f"mutation_class must be one of {sorted(MUTATION_CLASSES)}")

    if not isinstance(data.get("commit_push_recommended"), bool):
        errors.append("commit_push_recommended must be a boolean")

    for field_name in REQUIRED_SEQUENCE_FIELDS:
        value = data.get(field_name)
        if not isinstance(value, list | tuple):
            errors.append(f"{field_name} must be a list")

    target_paths = data.get("target_paths")
    if isinstance(target_paths, list | tuple):
        if not target_paths:
            errors.append("target_paths must include at least one path")
        for index, target in enumerate(target_paths):
            if not isinstance(target, str) or not target.strip():
                errors.append(f"target_paths[{index}] must be a non-empty string")

    residual_dirty_tree = data.get("residual_dirty_tree")
    if isinstance(residual_dirty_tree, list | tuple):
        for index, target in enumerate(residual_dirty_tree):
            if not isinstance(target, str):
                errors.append(f"residual_dirty_tree[{index}] must be a string")

    try:
        json.dumps(data, sort_keys=True)
    except (TypeError, ValueError) as exc:
        errors.append(f"receipt must be JSON-serializable: {exc}")

    return errors


def require_valid_receipt(receipt: PostActionReceipt | Mapping[str, Any]) -> None:
    errors = validate_receipt(receipt)
    if errors:
        raise ReceiptValidationError("; ".join(errors))


def _project_root(project_root: str | Path | None) -> Path:
    return Path(project_root).resolve() if project_root else Path.cwd().resolve()


def _receipt_date(receipt: PostActionReceipt | Mapping[str, Any]) -> str:
    data = receipt_to_dict(receipt)
    generated_at = str(data["generated_at"])
    return _parse_generated_at(generated_at).date().isoformat()


def _write_without_replacing(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
    try:
        with tmp_path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(tmp_path, target)
        except FileExistsError as exc:
            raise FileExistsError(f"receipt already exists: {target}") from exc
        except OSError:
            # Some filesystems disallow hard links. Keep the no-overwrite
            # guarantee via exclusive create even when the final write is not
            # link-atomic.
            with target.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
    finally:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass


def write_receipt(receipt: PostActionReceipt | Mapping[str, Any], *, project_root: str | Path | None = None) -> Path:
    """Validate and write ``receipt`` under ``.gtkb-state/post-action-receipts``."""

    require_valid_receipt(receipt)
    data = receipt_to_dict(receipt)
    root = _project_root(project_root)
    receipt_dir = root / RECEIPTS_RELATIVE_DIR / _receipt_date(data)
    target = receipt_dir / f"{data['receipt_id']}.json"
    content = json.dumps(data, indent=2, sort_keys=True) + "\n"
    _write_without_replacing(target, content)
    return target


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _implementation_packet(root: Path, bridge_thread: str | None) -> dict[str, Any] | None:
    packets_dir = root / IMPLEMENTATION_PACKETS_RELATIVE_DIR
    candidates: list[Path] = []
    if bridge_thread:
        candidates.append(packets_dir / "by-bridge" / f"{bridge_thread}.json")
    candidates.append(packets_dir / "current.json")
    for path in candidates:
        packet = _read_json(path)
        if not packet:
            continue
        if bridge_thread and packet.get("bridge_id") not in {bridge_thread, None}:
            continue
        return packet
    return None


def _work_intent_claim(root: Path, bridge_thread: str | None) -> dict[str, Any] | None:
    if not bridge_thread:
        return None
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        import bridge_work_intent_registry

        return bridge_work_intent_registry.current_holder(bridge_thread, project_root=root)
    except Exception:
        return None


def _formal_approval_packets(root: Path, target_paths: list[str]) -> list[dict[str, Any]]:
    approvals_dir = root / FORMAL_APPROVALS_RELATIVE_DIR
    if not approvals_dir.is_dir():
        return []
    normalized_targets = {target.replace("\\", "/").lstrip("./") for target in target_paths}
    matches: list[dict[str, Any]] = []
    for path in sorted(approvals_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        packet = _read_json(path)
        if not packet:
            continue
        target = str(packet.get("target_path") or "").replace("\\", "/").lstrip("./")
        if target and target in normalized_targets:
            matches.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "artifact_id": packet.get("artifact_id"),
                    "artifact_type": packet.get("artifact_type"),
                    "target_path": packet.get("target_path"),
                    "full_content_sha256": packet.get("full_content_sha256"),
                }
            )
    return matches


def _git_dirty_paths(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _bridge_version_from_packet(packet: Mapping[str, Any] | None) -> str:
    if not packet:
        return ""
    go_file = str(packet.get("go_file") or "")
    match = re.search(r"-(\d{3,})\.md$", go_file)
    return match.group(1) if match else ""


def gather_evidence(
    *,
    project_root: str | Path | None = None,
    bridge_thread: str | None = None,
    mutation_class: str = "file",
    action_summary: str = "",
    initiating_authority: str | None = None,
    work_item: str | None = None,
    target_paths: list[str] | tuple[str, ...] | None = None,
    commands_run: list[Any] | tuple[Any, ...] | None = None,
    verification_evidence: list[Any] | tuple[Any, ...] | None = None,
    commit_push_recommended: bool = False,
    commit_push_rationale: str = "Pending final commit-scope review.",
    author_identity: str = "",
    author_harness_id: str = "",
    author_session_context_id: str = "",
    author_model: str = "",
    receipt_id: str | None = None,
    generated_at: str | None = None,
) -> PostActionReceipt:
    """Assemble a candidate receipt from existing evidence without mutation."""

    root = _project_root(project_root)
    packet = _implementation_packet(root, bridge_thread)
    packet_auth = packet.get("project_authorization") if packet else None
    packet_auth = packet_auth if isinstance(packet_auth, dict) else {}
    claim = _work_intent_claim(root, bridge_thread)

    resolved_bridge = bridge_thread or (str(packet.get("bridge_id") or "") if packet else "")
    if target_paths is not None:
        resolved_targets = list(target_paths)
    elif packet:
        resolved_targets = list(packet.get("target_path_globs") or [])
    else:
        resolved_targets = []
    normalized_targets = [str(target).replace("\\", "/").lstrip("./") for target in resolved_targets]
    dirty_paths = _git_dirty_paths(root)
    formal_packets = _formal_approval_packets(root, normalized_targets)

    evidence_items: list[Any] = list(verification_evidence or [])
    if packet:
        evidence_items.append(
            {
                "kind": "implementation_authorization_packet",
                "bridge_id": packet.get("bridge_id"),
                "go_file": packet.get("go_file"),
                "packet_hash": packet.get("packet_hash"),
            }
        )
    if claim:
        evidence_items.append(
            {
                "kind": "work_intent_claim",
                "claim_kind": claim.get("claim_kind"),
                "session_id": claim.get("session_id"),
                "ttl_expires_at": claim.get("ttl_expires_at"),
            }
        )
    for formal_packet in formal_packets:
        evidence_items.append({"kind": "formal_artifact_approval_packet", **formal_packet})

    generated = generated_at or now_iso()
    return PostActionReceipt(
        receipt_id=receipt_id or new_receipt_id(resolved_bridge or "post-action-receipt", generated_at=generated),
        generated_at=generated,
        mutation_class=mutation_class,
        action_summary=action_summary,
        initiating_authority=initiating_authority or str(packet_auth.get("id") or ""),
        bridge_thread=resolved_bridge,
        bridge_version=_bridge_version_from_packet(packet),
        work_item=work_item or str(packet_auth.get("work_item_id") or ""),
        target_paths=tuple(normalized_targets),
        commands_run=tuple(commands_run or ()),
        verification_evidence=tuple(evidence_items),
        residual_dirty_tree=tuple(dirty_paths),
        commit_push_recommended=commit_push_recommended,
        commit_push_rationale=commit_push_rationale,
        author_identity=author_identity,
        author_harness_id=author_harness_id,
        author_session_context_id=author_session_context_id,
        author_model=author_model,
        evidence_sources={
            "implementation_packet_present": packet is not None,
            "work_intent_claim_present": claim is not None,
            "formal_approval_packet_count": len(formal_packets),
            "dirty_tree_count": len(dirty_paths),
        },
    )


__all__ = [
    "MUTATION_CLASSES",
    "PostActionReceipt",
    "ReceiptValidationError",
    "gather_evidence",
    "new_receipt_id",
    "receipt_to_dict",
    "require_valid_receipt",
    "validate_receipt",
    "write_receipt",
]
