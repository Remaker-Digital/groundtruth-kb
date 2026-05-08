#!/usr/bin/env python3
"""
Claude Code PreToolUse hook -- Narrative-artifact approval gate.

Blocks Write/Edit on narrative-artifact paths (rule files, AGENTS.md,
CLAUDE*.md, memory/work_list.md) unless the call references a valid
approval packet that proves owner-visible packet display per DELIB-0835.

Slice A of GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001.
Bridge:    bridge/gtkb-narrative-artifact-approval-extension-001-004.md (GO)
Specs:     GOV-ARTIFACT-APPROVAL-001 (extended), DCL-ARTIFACT-APPROVAL-HOOK-001 (extended)

Harness scope: Claude only (PreToolUse on Write|Edit). Codex template parity at
groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py is
forward-compatible-only per ADR-CODEX-HOOK-PARITY-FALLBACK-001; it is NOT a
live Windows interception boundary. Slice C's pre-commit hook is the
universal enforcement floor.

Stdin:  JSON {"tool_name": "Write|Edit", "tool_input": {"file_path": "...", ...}, ...}
Stdout: JSON {"decision": "block", "reason": "..."} or {} (allow)
Exit:   Always 0 (Claude Code hook contract: hook always returns 0; decision is in stdout)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover - older Python fallback
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

WRITE_TOOLS = {"Write", "Edit"}

DEFAULT_CONFIG_PATH = "config/governance/narrative-artifact-approval.toml"

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

VALID_APPROVAL_MODES = {"approve", "acknowledge", "edit-and-approve", "auto"}

NARRATIVE_ARTIFACT_TYPE = "narrative_artifact"


def _project_root() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def _emit(decision: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(decision))


def _emit_pass() -> None:
    _emit({})


def _emit_block(reason: str) -> None:
    _emit({"decision": "block", "reason": reason})


def _load_config(root: Path) -> dict[str, Any] | None:
    config_path = root / DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return None
    try:
        return tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None


def _normalise_relative(file_path: str, root: Path) -> str | None:
    """Convert tool_input.file_path to a forward-slash relative path under root.

    Returns None if the path is outside the project root (caller treats as out-of-scope).
    """
    try:
        absolute = Path(file_path).resolve()
    except (OSError, ValueError):
        return None
    try:
        rel = absolute.relative_to(root)
    except ValueError:
        return None
    return rel.as_posix()


def _matches_any(patterns: list[str], rel_path: str) -> bool:
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)


def _is_protected(rel_path: str, config: dict[str, Any]) -> bool:
    """True iff the relative path matches any protected pattern AND no exemption."""
    protected_blocks = config.get("protected_artifacts", []) or []
    exemption_blocks = config.get("exemptions", []) or []

    protected_patterns: list[str] = []
    for block in protected_blocks:
        protected_patterns.extend(block.get("patterns", []) or [])

    exempted_patterns: list[str] = []
    for block in exemption_blocks:
        exempted_patterns.extend(block.get("patterns", []) or [])

    if not _matches_any(protected_patterns, rel_path):
        return False
    return not (exempted_patterns and _matches_any(exempted_patterns, rel_path))


def _resolve_packet_path(tool_input: dict[str, Any], config: dict[str, Any], root: Path) -> str | None:
    detection = config.get("hook_detection", {}) or {}
    env_names = detection.get("env_var_names", []) or []
    for name in env_names:
        value = os.environ.get(name)
        if value:
            return value
    # tool_input may carry an explicit packet hint passed by an authoring caller
    explicit = tool_input.get("narrative_artifact_approval_packet")
    if isinstance(explicit, str) and explicit:
        return explicit
    return None


def _load_packet(packet_ref: str, root: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        path = Path(packet_ref).expanduser()
        if not path.is_absolute():
            path = root / path
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - convert any failure to a block reason
        return None, f"approval packet could not be read or parsed: {exc}"
    if not isinstance(data, dict):
        return None, "approval packet root must be a JSON object"
    return data, None


def _validate_packet(
    packet: dict[str, Any],
    rel_path: str,
    new_content: str | None,
) -> str | None:
    missing = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing:
        return f"approval packet missing required fields: {', '.join(missing)}"

    if packet.get("artifact_type") != NARRATIVE_ARTIFACT_TYPE:
        return (
            f"approval packet artifact_type must be {NARRATIVE_ARTIFACT_TYPE!r} for narrative-artifact gate; "
            f"got {packet.get('artifact_type')!r}"
        )

    approval_mode = packet.get("approval_mode")
    if approval_mode not in VALID_APPROVAL_MODES:
        return f"approval_mode must be one of {sorted(VALID_APPROVAL_MODES)}, got {approval_mode!r}"

    target = packet.get("target_path", "")
    if not isinstance(target, str) or not target.strip():
        return "approval packet target_path must be a non-empty string"
    if Path(target).as_posix() != rel_path:
        return f"approval packet target_path {target!r} does not match write target {rel_path!r}"

    full_content = packet.get("full_content")
    if not isinstance(full_content, str) or not full_content:
        return "approval packet full_content must be a non-empty string"

    expected_hash = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    if packet.get("full_content_sha256") != expected_hash:
        return "approval packet full_content_sha256 does not match full_content"

    # When the tool call carries the proposed write content, ensure the packet
    # describes the same content. Edit operations may not include full content
    # in tool_input; we only enforce when content is present.
    if new_content is not None and new_content != full_content:
        return (
            "approval packet full_content does not match the proposed Write/Edit content "
            "(packet must be regenerated when the content changes)"
        )

    for flag_name in ("presented_to_user", "transcript_captured"):
        if packet.get(flag_name) is not True:
            return f"approval packet requires {flag_name}=true"

    explicit_change = packet.get("explicit_change_request")
    if not isinstance(explicit_change, str) or not explicit_change.strip():
        return "approval packet explicit_change_request must be non-empty"

    return None


def _block_reason(rel_path: str, detail: str) -> str:
    return (
        f"[Governance] Narrative-artifact write to {rel_path!r} requires an owner-visible approval packet "
        f"per GOV-ARTIFACT-APPROVAL-001 (extended to narrative artifacts by GTKB-NARRATIVE-ARTIFACT-"
        f"APPROVAL-EXTENSION-001 Slice A). {detail} "
        f"Generate a packet under .groundtruth/formal-artifact-approvals/ with artifact_type='narrative_artifact' "
        f"and reference it via env var GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET=<path>. "
        f"(Hard-block per DCL-ARTIFACT-APPROVAL-HOOK-001 extended scope.)"
    )


def main() -> None:
    if "--self-test" in sys.argv:
        _emit_pass()
        return

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        _emit_pass()
        return

    tool_name = payload.get("tool_name", "")
    if tool_name not in WRITE_TOOLS:
        _emit_pass()
        return

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    if not isinstance(file_path, str) or not file_path:
        _emit_pass()
        return

    root = _project_root()
    rel_path = _normalise_relative(file_path, root)
    if rel_path is None:
        _emit_pass()
        return

    config = _load_config(root)
    if config is None:
        _emit_pass()
        return

    if not _is_protected(rel_path, config):
        _emit_pass()
        return

    packet_ref = _resolve_packet_path(tool_input, config, root)
    if not packet_ref:
        _emit_block(_block_reason(rel_path, "No approval-packet reference was found."))
        return

    packet, parse_error = _load_packet(packet_ref, root)
    if parse_error or packet is None:
        _emit_block(_block_reason(rel_path, parse_error or "approval packet did not load"))
        return

    new_content = tool_input.get("content") if tool_name == "Write" else None
    if new_content is not None and not isinstance(new_content, str):
        new_content = None

    error = _validate_packet(packet, rel_path, new_content)
    if error:
        _emit_block(_block_reason(rel_path, error))
        return

    _emit_pass()


if __name__ == "__main__":
    main()
