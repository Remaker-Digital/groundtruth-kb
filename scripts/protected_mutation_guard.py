"""Protected Mutation Guard decision module for GT-KB.

This module evaluates proposed mutations against project authorization boundaries,
harness roles, and bridge intent claims.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple

from scripts import bridge_work_intent_registry
from scripts.harness_projection_reader import id_for_name, load_harness_projection, role_set_for_id
from scripts.implementation_authorization import (
    AuthorizationError,
    _validate_packet,
    normalize_relative_path,
    packet_path_for_bridge,
    path_authorized,
)

PROTECTED_EXACT = {
    ".claude/settings.json",
    ".codex/hooks.json",
    "pyproject.toml",
    "groundtruth.toml",
    # Environment & Credentials
    ".env",
    "env.local",
    "env.staging",
    # Cloud & Deployment Configs
    "Dockerfile",
    "Dockerfile.test",
    "Dockerfile.ui",
    ".dockerignore",
    "docker-compose.yml",
    "shopify.app.toml",
}

PROTECTED_PREFIXES = (
    "scripts/",
    "groundtruth-kb/src/",
    "groundtruth-kb/tests/",
    "platform_tests/",
    "tests/",
    ".claude/hooks/",
    ".claude/rules/",
    ".codex/gtkb-hooks/",
    "config/",
    ".github/",
)

ALLOWED_WRITE_PREFIXES = (
    "bridge/",
    "independent-progress-assessments/",
)

DIAGNOSTIC_WRITE_PREFIXES = (
    ".groundtruth/session/snapshots/",
    ".gtkb-state/",
)


class GuardResult(NamedTuple):
    allowed: bool
    reason_code: str
    details: str


def _preserve_dot_prefixed_relative_path(relative_path: str) -> str:
    rel = relative_path.replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def is_protected_path(relative_path: str) -> bool:
    """Return True if relative_path is a protected workspace path."""
    rel = _preserve_dot_prefixed_relative_path(relative_path)
    if rel in PROTECTED_EXACT:
        return True
    if rel == ".env" or rel.startswith(".env.") or rel == "env.local" or rel == "env.staging":
        return True
    if rel.startswith(ALLOWED_WRITE_PREFIXES):
        return False
    if rel.startswith(DIAGNOSTIC_WRITE_PREFIXES):
        return False
    return any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def evaluate_mutation(
    project_root: str | Path,
    targets: Iterable[str | Path],
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    session_id: str | None = None,
    tool_name: str | None = None,
    command: str | None = None,
) -> GuardResult:
    """Evaluate a proposed mutation attempt and return a GuardResult."""
    root = Path(project_root).resolve()

    # 1. Normalize and validate all target paths against the project root boundary
    normalized_targets: list[str] = []
    for target in targets:
        try:
            norm = normalize_relative_path(root, str(target))
            normalized_targets.append(norm)
        except (AuthorizationError, ValueError, KeyError):
            return GuardResult(
                allowed=False,
                reason_code="target_outside_project_root",
                details=f"Target path escapes project root: {target}",
            )

    # 2. Check for forbidden operations (e.g. recreating bridge/INDEX.md)
    for target in normalized_targets:
        if target == "bridge/INDEX.md":
            return GuardResult(
                allowed=False,
                reason_code="forbidden_operation",
                details="Recreating or modifying bridge/INDEX.md is forbidden",
            )

    forbidden_kws = ("deploy", "credential", "key_vault", "bypass", "force")
    if command and any(kw in command.lower() for kw in forbidden_kws):
        return GuardResult(
            allowed=False,
            reason_code="forbidden_operation",
            details=f"Command contains forbidden operation keyword: {command}",
        )
    if tool_name and any(kw in tool_name.lower() for kw in forbidden_kws):
        return GuardResult(
            allowed=False,
            reason_code="forbidden_operation",
            details=f"Tool name contains forbidden operation keyword: {tool_name}",
        )

    # 3. Filter target paths to find only protected targets
    protected_targets = [t for t in normalized_targets if is_protected_path(t)]
    if not protected_targets:
        return GuardResult(
            allowed=True,
            reason_code="not_protected",
            details="No protected paths modified",
        )

    # 4. Harness identity and role context validation
    projection = load_harness_projection(root)
    resolved_id = harness_id
    if not resolved_id and harness_name:
        resolved_id = id_for_name(projection, harness_name)

    if not resolved_id:
        return GuardResult(
            allowed=False,
            reason_code="forbidden_operation",
            details="Harness identity could not be resolved from registry projection",
        )

    roles = role_set_for_id(projection, resolved_id)
    if not ("prime-builder" in roles or "acting-prime-builder" in roles):
        return GuardResult(
            allowed=False,
            reason_code="forbidden_operation",
            details=f"Harness {resolved_id} with roles {list(roles)} is not authorized as a Prime Builder",
        )

    # 5. Query the active work-intent claim for the session
    if not session_id:
        return GuardResult(
            allowed=False,
            reason_code="missing_or_stale_claim",
            details="Session ID is missing or empty",
        )

    bridge_id = bridge_work_intent_registry.current_claimed_bridge_id(session_id, project_root=root)
    if not bridge_id:
        return GuardResult(
            allowed=False,
            reason_code="missing_or_stale_claim",
            details=f"No active work-intent claim found for session ID {session_id}",
        )

    holder = bridge_work_intent_registry.current_holder(bridge_id, project_root=root)
    if not holder or holder.get("session_id") != session_id:
        return GuardResult(
            allowed=False,
            reason_code="missing_or_stale_claim",
            details=f"Work-intent claim for bridge {bridge_id} is not held by session ID {session_id}",
        )

    # 6. Load the authorization packet
    packet_path = packet_path_for_bridge(root, bridge_id)
    if not packet_path.is_file():
        return GuardResult(
            allowed=False,
            reason_code="missing_implementation_packet",
            details=f"Implementation authorization packet for bridge {bridge_id} not found",
        )

    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return GuardResult(
            allowed=False,
            reason_code="missing_implementation_packet",
            details=f"Implementation authorization packet for bridge {bridge_id} is corrupt: {exc}",
        )

    # 7. Validate the packet using the standard validator
    try:
        _validate_packet(root, packet)
    except AuthorizationError as exc:
        msg = str(exc)
        if "expired" in msg:
            return GuardResult(
                allowed=False,
                reason_code="stale_implementation_packet",
                details=msg,
            )
        elif "hash mismatch" in msg:
            return GuardResult(
                allowed=False,
                reason_code="missing_implementation_packet",
                details=msg,
            )
        elif any(
            token in msg
            for token in ("status changed", "not found in chain", "Newer GO", "review", "VERIFIED", "DEFERRED")
        ):
            return GuardResult(
                allowed=False,
                reason_code="missing_bridge_go",
                details=msg,
            )
        else:
            return GuardResult(
                allowed=False,
                reason_code="missing_implementation_packet",
                details=msg,
            )

    # 8. Check target path globs match targets
    unauthorized_targets = [t for t in protected_targets if not path_authorized(packet, t)]
    if unauthorized_targets:
        return GuardResult(
            allowed=False,
            reason_code="target_out_of_scope",
            details=f"Protected target path(s) outside packet scope: {unauthorized_targets}",
        )

    return GuardResult(
        allowed=True,
        reason_code="authorized",
        details="Mutation is fully authorized",
    )
