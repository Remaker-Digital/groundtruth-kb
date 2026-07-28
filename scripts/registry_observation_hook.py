#!/usr/bin/env python3
"""Consume one capability-bound post-tool registry observation event."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.project.registry_control_plane import (  # noqa: E402
    RegistryAuthorizationError,
    RegistryControlPlaneError,
    consume_observation_capability,
    load_registry_snapshot,
)


def event_binding(payload: dict[str, Any]) -> tuple[str, str]:
    session_id = str(
        payload.get("session_id") or payload.get("sessionId") or os.environ.get("GTKB_SESSION_ID") or ""
    ).strip()
    event_id = str(
        payload.get("tool_use_id")
        or payload.get("toolUseID")
        or payload.get("tool_event_id")
        or payload.get("event_id")
        or ""
    ).strip()
    if not session_id or not event_id:
        raise RegistryAuthorizationError("post-tool observation requires session and tool event identifiers")
    return session_id, event_id


def intent_path(project_root: Path, session_id: str, event_id: str) -> Path:
    binding = hashlib.sha256(f"{session_id}\0{event_id}".encode()).hexdigest()
    return project_root / ".gtkb-state" / "sot-registry" / "observation-intents" / f"{binding}.json"


def _tool_succeeded(payload: dict[str, Any]) -> bool:
    response = payload.get("tool_response", payload.get("tool_result", payload.get("result", {})))
    if isinstance(response, dict):
        if response.get("is_error") is True or response.get("success") is False:
            return False
        exit_code = response.get("exit_code", response.get("returncode"))
        if exit_code is not None:
            try:
                return int(exit_code) == 0
            except (TypeError, ValueError):
                return False
    return payload.get("error") in {None, ""}


def consume_payload(payload: dict[str, Any], *, project_root: Path = PROJECT_ROOT) -> tuple[str, ...]:
    session_id, event_id = event_binding(payload)
    path = intent_path(project_root, session_id, event_id)
    if not path.exists():
        raise RegistryAuthorizationError(
            "no authorized observation intent exists for this session/tool event; registered writes remain stale"
        )
    intent = json.loads(path.read_text(encoding="utf-8"))
    if intent.get("session_id") != session_id or intent.get("tool_event_id") != event_id:
        raise RegistryAuthorizationError("observation intent file binding mismatch")
    try:
        return consume_observation_capability(
            capability=str(intent.get("capability") or ""),
            target_paths=list(intent.get("target_paths") or ()),
            preimage_digests=dict(intent.get("preimage_digests") or {}),
            session_id=session_id,
            tool_event_id=event_id,
            bridge_id=str(intent.get("bridge_id") or ""),
            start_packet_hash=str(intent.get("start_packet_hash") or ""),
            operation=str(intent.get("operation") or ""),
            tool_succeeded=_tool_succeeded(payload),
            tool_result=payload.get("tool_response", payload.get("tool_result", payload.get("result"))),
            changed_by=f"registry-observer/{session_id}",
            change_reason=str(intent.get("change_reason") or "authorized post-tool observation"),
            project_root=project_root,
            db_path=project_root / "groundtruth.db",
        )
    finally:
        path.unlink(missing_ok=True)


def _registered_intent_required(payload: dict[str, Any], project_root: Path) -> bool | None:
    try:
        snapshot = load_registry_snapshot(project_root=project_root, db_path=project_root / "groundtruth.db")
    except (RegistryControlPlaneError, FileNotFoundError):
        return None
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return False
    candidates = [tool_input.get(key) for key in ("file_path", "path", "target_path")]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            path = Path(candidate)
            if path.is_absolute():
                try:
                    path = path.resolve().relative_to(project_root.resolve())
                except ValueError:
                    continue
            if snapshot.resolver.resolve(path.as_posix()) is not None:
                return True
    return False


def _record_audit_gap(payload: dict[str, Any], *, code: str, detail: str) -> dict[str, Any]:
    row = {
        "schema_version": 1,
        "kind": "registry_observation_gap",
        "code": code,
        "detail": detail,
        "session_id": str(payload.get("session_id") or payload.get("sessionId") or "") or None,
        "tool_event_id": str(
            payload.get("tool_use_id")
            or payload.get("toolUseID")
            or payload.get("tool_event_id")
            or payload.get("event_id")
            or ""
        )
        or None,
        "observed_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    try:
        target = PROJECT_ROOT / ".gtkb-state" / "sot-registry" / "audit-gaps.jsonl"
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
    except OSError:
        pass
    return row


def main() -> int:
    payload: dict[str, Any] = {}
    try:
        raw = sys.stdin.read()
        decoded = json.loads(raw) if raw.strip() else {}
        if not isinstance(decoded, dict):
            raise RegistryAuthorizationError("post-tool payload must be a JSON object")
        payload = decoded
        try:
            revisions = consume_payload(payload)
        except RegistryAuthorizationError as exc:
            required = _registered_intent_required(payload, PROJECT_ROOT)
            if required is False:
                print(json.dumps({"registry_observation": "not_required", "detail": str(exc)}, sort_keys=True))
                return 0
            gap = _record_audit_gap(
                payload,
                code="missing_or_invalid_observation_intent",
                detail=str(exc),
            )
            print(json.dumps({"registry_observation": "audit_gap", "gap": gap}, sort_keys=True))
            return 0
        print(json.dumps({"registry_observation": "consumed", "revision_ids": revisions}, sort_keys=True))
        return 0
    except (RegistryControlPlaneError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        gap = _record_audit_gap(
            payload,
            code="observation_hook_failure",
            detail=f"{type(exc).__name__}: {exc}",
        )
        print(json.dumps({"registry_observation": "audit_gap", "gap": gap}, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
