#!/usr/bin/env python3
"""
Claude Code PreToolUse hook -- Formal artifact approval gate.

Blocks inferred writes to formal GroundTruth-KB artifacts unless the command
references an approval packet that proves full native-format presentation and
approval, acknowledgement, or scoped auto-approval evidence.

Protected by:
- DELIB-0835
- GOV-ARTIFACT-APPROVAL-001
- PB-ARTIFACT-APPROVAL-001
- ADR-ARTIFACT-FORMALIZATION-GATE-001
- DCL-ARTIFACT-APPROVAL-HOOK-001

Stdin:  JSON {"tool_name": "Bash", "tool_input": {"command": "..."}, ...}
Stdout: JSON {"decision": "block", "reason": "..."} or {}
Exit:   Always 0
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _PROJECT_ROOT / "groundtruth-kb" / "src"
if _PACKAGE_SRC.is_dir() and str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

try:
    from groundtruth_kb.governance.approval_packet import validate_packet as _shared_validate_packet
except Exception:  # noqa: BLE001 - hook must preserve fallback behavior during bootstrap
    _shared_validate_packet = None

APPROVAL_ENV_NAMES = (
    "GTKB_FORMAL_APPROVAL_PACKET",
    "GTKB_ARTIFACT_APPROVAL_PACKET",
    "GTKB_FORMAL_ARTIFACT_APPROVAL_PACKET",
)

APPROVAL_FLAG_PATTERNS = (
    re.compile(r"--formal-approval-packet(?:=|\s+)(?P<path>\"[^\"]+\"|'[^']+'|[^\s;]+)", re.IGNORECASE),
    re.compile(r"--artifact-approval-packet(?:=|\s+)(?P<path>\"[^\"]+\"|'[^']+'|[^\s;]+)", re.IGNORECASE),
)

FORMAL_MUTATION_PATTERNS = [
    re.compile(r"\b(?:gt|python\s+-m\s+groundtruth_kb)\s+deliberations\s+(?:add|upsert|link)\b", re.IGNORECASE),
    re.compile(r"\b(?:insert_spec|update_spec|insert_deliberation|upsert_deliberation_source)\s*\(", re.IGNORECASE),
    re.compile(r"\blink_deliberation_(?:spec|work_item)\s*\(", re.IGNORECASE),
    re.compile(
        r"\bgroundtruth\.db\b.*\b(?:INSERT|UPDATE|DELETE)\b.*\b"
        r"(?:specifications|deliberations|current_deliberations)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"\bscripts[/\\]archive[/\\]record_[A-Za-z0-9_ -]+\.py\b", re.IGNORECASE),
]

SCRIPT_MUTATION_POLICIES = {
    "harvest_session_deliberations.py": "requires_apply",
    "archive_claude_design_handoff.py": "invocation",
    "backfill_lo_reports.py": "invocation",
}
SCRIPT_HELP_FLAGS = {"-h", "--help"}
COMMAND_SEPARATORS = {";", "&&", "||", "|"}
PYTHON_RUNNERS = {"python", "python.exe", "python3", "python3.exe", "py", "py.exe"}

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


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _extract_packet_path(command: str) -> str | None:
    for name in APPROVAL_ENV_NAMES:
        match = re.search(rf"(?:^|[\s;]){re.escape(name)}\s*=\s*(?P<path>\"[^\"]+\"|'[^']+'|[^\s;]+)", command)
        if match:
            return _strip_quotes(match.group("path"))

    for pattern in APPROVAL_FLAG_PATTERNS:
        match = pattern.search(command)
        if match:
            return _strip_quotes(match.group("path"))

    for name in APPROVAL_ENV_NAMES:
        value = os.environ.get(name)
        if value:
            return value

    return None


def _is_formal_mutation(command: str) -> bool:
    return any(pattern.search(command) for pattern in FORMAL_MUTATION_PATTERNS) or _has_mutating_script_invocation(
        command
    )


def _command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return re.findall(r"""[^\s"']+|"[^"]*"|'[^']*'""", command)


def _clean_token(token: str) -> str:
    return token.strip().strip("'\"`").strip()


def _token_basename(token: str) -> str:
    cleaned = _clean_token(token).rstrip(";,)")
    normalized = cleaned.replace("\\", "/")
    return normalized.rsplit("/", 1)[-1].lower()


def _is_command_separator(token: str) -> bool:
    cleaned = _clean_token(token)
    return cleaned in COMMAND_SEPARATORS or cleaned.endswith(";")


def _is_script_invocation(tokens: list[str], index: int) -> bool:
    if index == 0:
        return True
    previous = [_token_basename(token) for token in tokens[max(0, index - 4) : index]]
    if any(token in PYTHON_RUNNERS for token in previous):
        return True
    return _is_command_separator(tokens[index - 1])


def _script_args(tokens: list[str], index: int) -> list[str]:
    args: list[str] = []
    for token in tokens[index + 1 :]:
        if _is_command_separator(token):
            break
        args.append(_clean_token(token))
    return args


def _has_mutating_script_invocation(command: str) -> bool:
    tokens = _command_tokens(command)
    for index, token in enumerate(tokens):
        script_name = _token_basename(token)
        policy = SCRIPT_MUTATION_POLICIES.get(script_name)
        if policy is None or not _is_script_invocation(tokens, index):
            continue
        args = _script_args(tokens, index)
        if any(arg in SCRIPT_HELP_FLAGS for arg in args):
            continue
        if policy == "requires_apply":
            return "--apply" in args
        return True
    return False


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _load_packet(path_text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        packet_path = Path(path_text).expanduser()
        if not packet_path.is_absolute():
            project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
            packet_path = Path(project_dir) / packet_path
        data = json.loads(packet_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - hook must convert every failure to a block reason
        return None, f"approval packet could not be read or parsed: {exc}"
    return data, None


def _fallback_validate_packet(packet: dict[str, Any]) -> str | None:
    missing = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing:
        return f"approval packet missing required fields: {', '.join(missing)}"

    artifact_type = packet.get("artifact_type")
    if artifact_type not in VALID_ARTIFACT_TYPES:
        return f"approval packet artifact_type must be one of {sorted(VALID_ARTIFACT_TYPES)}, got {artifact_type!r}"

    approval_mode = packet.get("approval_mode")
    if approval_mode not in VALID_APPROVAL_MODES:
        return f"approval_mode must be one of {sorted(VALID_APPROVAL_MODES)}, got {approval_mode!r}"

    full_content = packet.get("full_content")
    if not isinstance(full_content, str) or not full_content.strip():
        return "approval packet full_content must be a non-empty string"

    expected_hash = _content_hash(full_content)
    if packet.get("full_content_sha256") != expected_hash:
        return "approval packet full_content_sha256 does not match full_content"

    for flag_name in ("presented_to_user", "transcript_captured"):
        if packet.get(flag_name) is not True:
            return f"approval packet requires {flag_name}=true"

    explicit_change = packet.get("explicit_change_request")
    if not isinstance(explicit_change, str) or not explicit_change.strip():
        return "approval packet explicit_change_request must be a non-empty string"

    if approval_mode == "auto":
        if not packet.get("auto_approval_scope"):
            return "auto approval requires auto_approval_scope"
        if packet.get("auto_approval_activated_by") != "owner":
            return "auto approval requires auto_approval_activated_by='owner'"
    elif not (packet.get("approved_by") or packet.get("acknowledged_by")):
        return "manual approval requires approved_by or acknowledged_by"

    expires_at = packet.get("expires_at")
    if expires_at:
        try:
            expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=UTC)
            if expiry < datetime.now(UTC):
                return "approval packet is expired"
        except ValueError:
            return "approval packet expires_at must be ISO-8601 when present"

    return None


def _validate_packet(packet: dict[str, Any]) -> str | None:
    if _shared_validate_packet is not None:
        result = _shared_validate_packet(packet)
        if result.is_valid:
            return None
        return result.errors[0] if result.errors else "approval packet failed validation"
    return _fallback_validate_packet(packet)


def _block(reason: str) -> None:
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": (
                    "BLOCKED (GOV-ARTIFACT-APPROVAL-001): formal artifact mutation "
                    f"requires full native-format display and approval evidence. {reason}"
                ),
            }
        )
    )


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception as exc:  # noqa: BLE001
        _block(f"Hook input could not be parsed: {exc}")
        return

    if data.get("tool_name") != "Bash":
        print(json.dumps({}))
        return

    command = data.get("tool_input", {}).get("command", "")
    if not command or not _is_formal_mutation(command):
        print(json.dumps({}))
        return

    packet_path = _extract_packet_path(command)
    if not packet_path:
        _block(
            "Command matches a formal artifact write path but does not reference "
            "GTKB_FORMAL_APPROVAL_PACKET or --formal-approval-packet."
        )
        return

    packet, load_error = _load_packet(packet_path)
    if load_error:
        _block(load_error)
        return

    assert packet is not None
    validation_error = _validate_packet(packet)
    if validation_error:
        _block(validation_error)
        return

    print(json.dumps({}))


if __name__ == "__main__":
    main()
