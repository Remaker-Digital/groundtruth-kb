"""Worker-safe bridge dispatch context packet facade."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "gtkb.dispatch.worker_context_packet.v1"
STATE_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller" / "dispatch-state.json"
BRIDGE_VERSION_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3,})\.md$")
BRIDGE_SLUG_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$")
STATUS_TOKENS = {
    "NEW",
    "REVISED",
    "GO",
    "NO-GO",
    "NO-ACTION",
    "VERIFIED",
    "ADVISORY",
    "WITHDRAWN",
    "SUPERSEDED",
    "RETIRED",
}
DISPATCH_ENV_KEYS = (
    "GTKB_DISPATCH_ID",
    "GTKB_BRIDGE_POLLER_RUN_ID",
    "GTKB_WORK_INTENT_SESSION_ID",
)

_WORK_ITEM_RE = re.compile(r"^Work Item:\s*`?(?P<value>WI-[A-Za-z0-9-]+)", re.IGNORECASE | re.MULTILINE)
_PROJECT_RE = re.compile(r"^Project:\s*`?(?P<value>[A-Za-z0-9_-]+)", re.IGNORECASE | re.MULTILINE)
_PROJECT_AUTH_RE = re.compile(
    r"^Project Authorization:\s*`?(?P<value>PAUTH-[A-Za-z0-9-]+)",
    re.IGNORECASE | re.MULTILINE,
)
_TARGET_PATHS_RE = re.compile(r"^target_paths:\s*(?P<value>\[.*\])\s*$", re.IGNORECASE | re.MULTILINE)
_SPEC_LINK_RE = re.compile(r"`(?P<value>(?:ADR|DCL|GOV|SPEC)-[A-Z0-9-]+)`")


class WorkerContextError(RuntimeError):
    """Raised when a worker-context packet cannot be resolved safely."""


@dataclass(frozen=True)
class BridgeFile:
    path: str
    version: int
    status: str | None
    content: str


def build_worker_context_packet(
    project_root: Path,
    *,
    dispatch_id: str | None = None,
    self_only: bool = False,
    environ: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic assigned-content packet for one dispatched worker."""

    root = project_root.resolve()
    effective_dispatch_id = (dispatch_id or "").strip()
    if self_only and not effective_dispatch_id:
        effective_dispatch_id = _dispatch_id_from_environment(environ)
    if not effective_dispatch_id:
        raise WorkerContextError(
            "--dispatch-id is required unless --self can resolve a dispatch id from the environment"
        )

    state = _read_state(root)
    launch = _find_dispatch_launch(state, effective_dispatch_id)
    slugs = _assigned_document_slugs(launch)
    if not slugs:
        raise WorkerContextError(f"Dispatch {effective_dispatch_id!r} has no assigned bridge documents")

    assigned_content: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []
    governing_specs: list[str] = []
    target_paths: list[str] = []
    citations: list[dict[str, str]] = []
    current_statuses: dict[str, str | None] = {}
    work_item_ids: list[str] = []
    project_ids: list[str] = []
    project_authorization_ids: list[str] = []

    for slug in slugs:
        bridge_files = _bridge_files(root, slug)
        if not bridge_files:
            blockers.append({"code": "assigned_bridge_file_missing", "document_name": slug})
            assigned_content.append({"document_name": slug, "current_status": None, "bridge_files": []})
            current_statuses[slug] = None
            continue

        current_status = bridge_files[-1].status
        current_statuses[slug] = current_status
        assigned_content.append(
            {
                "document_name": slug,
                "current_status": current_status,
                "bridge_files": [
                    {
                        "path": item.path,
                        "version": item.version,
                        "status": item.status,
                        "content": item.content,
                    }
                    for item in bridge_files
                ],
            }
        )
        for item in bridge_files:
            citations.append({"kind": "bridge_file", "path": item.path})
            metadata = _metadata_from_text(item.content)
            _extend_unique(target_paths, metadata["target_paths"])
            _extend_unique(governing_specs, metadata["governing_specs"])
            _append_unique(work_item_ids, metadata["work_item_id"])
            _append_unique(project_ids, metadata["project_id"])
            _append_unique(project_authorization_ids, metadata["project_authorization_id"])

    role = _role_from_launch(launch)
    packet = {
        "schema_version": SCHEMA_VERSION,
        "dispatch_id": effective_dispatch_id,
        "current_worker_only": bool(self_only),
        "assigned_content": assigned_content,
        "governing_specs": governing_specs,
        "target_paths": target_paths,
        "allowed_actions": _allowed_actions(role, current_statuses),
        "blockers": blockers,
        "preflight_state": {
            "status": "BLOCKED" if blockers else "PASS",
            "read_only": True,
            "dispatch_id_found": True,
            "assignment_count": len(slugs),
            "assigned_documents_resolved": not blockers,
            "bridge_statuses": current_statuses,
            "checks": [
                {
                    "name": "dispatch_assignment_resolved",
                    "status": "PASS",
                },
                {
                    "name": "assigned_bridge_files_resolved",
                    "status": "FAIL" if blockers else "PASS",
                },
                {
                    "name": "ordinary_worker_boundary",
                    "status": "PASS",
                },
            ],
        },
        "citations": _dedupe_citations(citations),
        "provenance": {
            "facade": "bridge_dispatch_worker_context",
            "dispatch_id": effective_dispatch_id,
            "recipient": _safe_string(launch.get("recipient")),
            "role": role,
            "harness_id": _harness_id_from_launch(launch),
            "session_id": _session_id_from_launch(launch),
            "work_item_ids": work_item_ids,
            "project_ids": project_ids,
            "project_authorization_ids": project_authorization_ids,
        },
    }
    return packet


def format_worker_context_packet(packet: dict[str, Any]) -> str:
    """Render a compact human summary for interactive use."""

    provenance = packet.get("provenance") if isinstance(packet.get("provenance"), dict) else {}
    lines = [
        f"Worker context packet: {packet.get('dispatch_id')}",
        f"Role: {provenance.get('role') or 'unknown'}",
        f"Assigned documents: {len(packet.get('assigned_content') or [])}",
        f"Preflight: {packet.get('preflight_state', {}).get('status')}",
    ]
    blockers = packet.get("blockers")
    if blockers:
        lines.append("Blockers:")
        for blocker in blockers:
            lines.append(f"- {blocker.get('code')}: {blocker.get('document_name')}")
    return "\n".join(lines)


def _read_state(root: Path) -> dict[str, Any]:
    path = root / STATE_RELATIVE_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkerContextError("Dispatch state is unavailable for worker-context lookup") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkerContextError(f"Dispatch state cannot be read: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkerContextError("Dispatch state is not a JSON object")
    return payload


def _find_dispatch_launch(state: dict[str, Any], dispatch_id: str) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for launch in _iter_launches(state):
        if str(launch.get("dispatch_id") or "").strip() == dispatch_id:
            matches.append(launch)
    if not matches:
        raise WorkerContextError(f"Dispatch {dispatch_id!r} was not found")
    first = matches[0]
    if any(match != first for match in matches[1:]):
        raise WorkerContextError(f"Dispatch {dispatch_id!r} has ambiguous launch records")
    return first


def _iter_launches(state: dict[str, Any]) -> Iterable[dict[str, Any]]:
    recipients = state.get("recipients")
    if not isinstance(recipients, dict):
        return
    for recipient in recipients.values():
        if not isinstance(recipient, dict):
            continue
        last_launch = recipient.get("last_launch")
        if isinstance(last_launch, dict):
            yield last_launch
        ledger = recipient.get("launch_ledger")
        if not isinstance(ledger, dict):
            continue
        groups: list[Any] = []
        if isinstance(ledger.get("active"), dict) or isinstance(ledger.get("completed"), dict):
            groups.extend(group for group in (ledger.get("active"), ledger.get("completed")) if isinstance(group, dict))
        else:
            groups.append(ledger)
        for group in groups:
            if not isinstance(group, dict):
                continue
            for launch in group.values():
                if isinstance(launch, dict):
                    yield launch


def _assigned_document_slugs(launch: dict[str, Any]) -> list[str]:
    slugs: list[str] = []
    _append_slug(slugs, launch.get("primary_bridge_id"))
    for key in ("selected_documents", "document_names", "work_intent_slugs", "document_lease_slugs"):
        values = launch.get(key)
        if isinstance(values, list):
            for value in values:
                _append_slug(slugs, value)
    handles = launch.get("document_lease_handles")
    if isinstance(handles, list):
        for handle in handles:
            if isinstance(handle, dict):
                _append_slug(slugs, handle.get("doc_slug"))
    top_files = launch.get("selected_top_files")
    if isinstance(top_files, list):
        for value in top_files:
            slug = _slug_from_bridge_path(value)
            if slug:
                _append_slug(slugs, slug)
    return slugs


def _bridge_files(root: Path, slug: str) -> list[BridgeFile]:
    if not BRIDGE_SLUG_RE.fullmatch(slug):
        return []
    bridge_dir = root / "bridge"
    versions: list[tuple[int, Path]] = []
    for path in bridge_dir.glob(f"{slug}-*.md"):
        match = BRIDGE_VERSION_RE.fullmatch(path.name)
        if match and match.group("slug") == slug:
            versions.append((int(match.group("version")), path))
    result: list[BridgeFile] = []
    for version, path in sorted(versions):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        result.append(
            BridgeFile(
                path=_relative_path(root, path),
                version=version,
                status=_status_token(content),
                content=content,
            )
        )
    return result


def _metadata_from_text(text: str) -> dict[str, Any]:
    work_item = _WORK_ITEM_RE.search(text)
    project = _PROJECT_RE.search(text)
    authorization = _PROJECT_AUTH_RE.search(text)
    target_paths: list[str] = []
    target_match = _TARGET_PATHS_RE.search(text)
    if target_match:
        try:
            decoded = json.loads(target_match.group("value"))
        except json.JSONDecodeError:
            decoded = []
        if isinstance(decoded, list):
            target_paths = [str(item) for item in decoded if isinstance(item, str) and item.strip()]
    return {
        "work_item_id": work_item.group("value").upper() if work_item else None,
        "project_id": project.group("value") if project else None,
        "project_authorization_id": authorization.group("value") if authorization else None,
        "target_paths": target_paths,
        "governing_specs": sorted({match.group("value") for match in _SPEC_LINK_RE.finditer(text)}),
    }


def _allowed_actions(role: str | None, statuses: dict[str, str | None]) -> list[str]:
    actions: list[str] = []
    values = {status for status in statuses.values() if status}
    if role == "prime-builder":
        if "GO" in values:
            actions.extend(["implement_approved_target_paths", "file_prime_implementation_report"])
        if "NO-GO" in values:
            actions.append("file_prime_revised_response")
    elif role == "loyal-opposition":
        if values & {"NEW", "REVISED", "NO-ACTION"}:
            actions.append("file_loyal_opposition_review_verdict")
        if "NEW" in values:
            actions.append("verify_prime_implementation_report_when_applicable")
    if not actions:
        actions.append("inspect_assigned_bridge_content")
    return actions


def _dispatch_id_from_environment(environ: dict[str, str] | None) -> str:
    env = os.environ if environ is None else environ
    for key in DISPATCH_ENV_KEYS:
        value = str(env.get(key) or "").strip()
        if value:
            return value
    return ""


def _role_from_launch(launch: dict[str, Any]) -> str | None:
    role = _safe_string(launch.get("needed_role_label"))
    if role:
        return role
    recipient = _safe_string(launch.get("recipient"))
    if recipient and ":" in recipient:
        return recipient.split(":", 1)[0]
    return None


def _harness_id_from_launch(launch: dict[str, Any]) -> str | None:
    context = launch.get("trusted_worker_context")
    if isinstance(context, dict):
        harness_id = _safe_string(context.get("harness_id"))
        if harness_id:
            return harness_id
    recipient = _safe_string(launch.get("recipient"))
    if recipient and ":" in recipient:
        return recipient.split(":", 1)[1]
    return None


def _session_id_from_launch(launch: dict[str, Any]) -> str | None:
    for key in ("work_intent_session_id", "session_id"):
        value = _safe_string(launch.get(key))
        if value:
            return value
    context = launch.get("trusted_worker_context")
    if isinstance(context, dict):
        return _safe_string(context.get("session_id"))
    return None


def _append_slug(slugs: list[str], value: Any) -> None:
    if not isinstance(value, str):
        return
    slug = value.strip()
    if BRIDGE_SLUG_RE.fullmatch(slug) and slug not in slugs:
        slugs.append(slug)


def _slug_from_bridge_path(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = BRIDGE_VERSION_RE.fullmatch(Path(value).name)
    return match.group("slug") if match else None


def _status_token(text: str) -> str | None:
    for line in text.splitlines():
        token = line.strip()
        if not token:
            continue
        return token if token in STATUS_TOKENS else None
    return None


def _safe_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _append_unique(values: list[str], value: str | None) -> None:
    if value and value not in values:
        values.append(value)


def _extend_unique(values: list[str], incoming: Iterable[str]) -> None:
    for value in incoming:
        if value not in values:
            values.append(value)


def _dedupe_citations(citations: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, str]] = []
    for citation in citations:
        key = (citation.get("kind", ""), citation.get("path", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(citation)
    return result


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
