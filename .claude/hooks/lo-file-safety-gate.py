#!/usr/bin/env python3
"""PreToolUse hook: Loyal Opposition file-safety gate.

Blocks Loyal Opposition writes outside the approved additive/reporting surfaces
unless a content-exact owner authorization packet is present. Prime Builder
sessions pass through unchanged.

Bridge: bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-006.md (GO)
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001

Stdin: JSON hook payload.
Stdout: {} or a block decision JSON object.
Exit: always 0.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:  # pragma: no cover - Python <3.11 fallback
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

for _parent in Path(__file__).resolve().parents:
    if (_parent / "scripts" / "harness_roles.py").is_file():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        break

try:
    from scripts.harness_roles import is_loyal_opposition, is_prime_builder, load_role_assignments, resolved_harness_id
except Exception:  # pragma: no cover - fail-open fallback for partial installs
    is_loyal_opposition = None  # type: ignore[assignment]
    is_prime_builder = None  # type: ignore[assignment]
    load_role_assignments = None  # type: ignore[assignment]
    resolved_harness_id = None  # type: ignore[assignment]

try:
    from scripts.session_role_resolution import resolve_interactive_session_role
except Exception:  # pragma: no cover - fail-open fallback
    resolve_interactive_session_role = None  # type: ignore[assignment]

try:
    from scripts.gtkb_session_id import MARKER_CONTINUITY_ORDER, resolve_session_id
except Exception:  # pragma: no cover - fail-open fallback
    resolve_session_id = None  # type: ignore[assignment]
    MARKER_CONTINUITY_ORDER = None  # type: ignore[assignment]


CONFIG_RELATIVE_PATH = Path("config") / "governance" / "lo-file-safety.toml"
APPROVAL_ENV_VAR = "GTKB_LO_FILE_SAFETY_APPROVAL_PACKET"
APPROVAL_PACKET_TYPE = "lo_file_safety_authorization"
LO_STATUS_TOKENS = frozenset({"NO-GO", "GO", "VERIFIED", "ADVISORY"})
VERSIONED_BRIDGE_PATH_RE = re.compile(r"^bridge/.+-\d{3}\.md$")
NULL_SINKS = {"nul", "null", "$null", "/dev/null", "2>nul", "2>$null", "2>/dev/null"}
WRITEISH_COMMAND_RE = re.compile(
    r"\b("
    r"Set-Content|Add-Content|Out-File|Remove-Item|Move-Item|Copy-Item|"
    r"New-Item|rm|mv|cp|copy|del|erase|tee|git\s+restore|git\s+checkout"
    r")\b|(?<![:<>=!-])(?:\d?>|>>)",
    re.IGNORECASE,
)
_COMMAND_SEPARATORS = frozenset(";&|\n")
_GIT_RESTORE_OPTS_WITH_ARG = frozenset({"-s", "--source", "-C", "--conflict", "--pathspec-from-file"})
_GIT_CHECKOUT_OPTS_WITH_ARG = frozenset({"-b", "-B", "--conflict", "--orphan", "--pathspec-from-file"})


def _split_command_segment(command: str, start: int) -> str:
    end = len(command)
    for index in range(start, len(command)):
        if command[index] in _COMMAND_SEPARATORS:
            end = index
            break
    return command[start:end]


def _tokenize_argv(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char in ('"', "'"):
            quote = char
            end = index + 1
            while end < length and text[end] != quote:
                end += 1
            tokens.append(text[index + 1 : end])
            index = end + 1 if end < length else end
            continue
        end = index
        while end < length and not text[end].isspace() and text[end] not in "\"'":
            end += 1
        tokens.append(text[index:end])
        index = end
    return tokens


def _git_pathspecs(args: list[str], opts_with_arg: frozenset[str]) -> list[str]:
    pathspecs: list[str] = []
    after_dash_dash = False
    index = 0
    while index < len(args):
        token = args[index]
        if after_dash_dash:
            pathspecs.append(token)
            index += 1
            continue
        if token == "--":
            after_dash_dash = True
            index += 1
            continue
        if token.startswith("--"):
            if "=" in token:
                index += 1
                continue
            if token in opts_with_arg:
                index += 2
                continue
            index += 1
            continue
        if token.startswith("-") and len(token) >= 2:
            if token in opts_with_arg:
                index += 2
                continue
            index += 1
            continue
        pathspecs.append(token)
        index += 1
    return pathspecs


@dataclass(frozen=True)
class Change:
    operation: str
    rel_path: str
    abs_path: Path
    candidate_content: str | None = None


def _emit(decision: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(decision, sort_keys=True))


def _emit_pass() -> None:
    _emit({})


def _block(reason: str) -> dict[str, Any]:
    return {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
            "additionalContext": reason,
        },
    }


def _project_root(payload: dict[str, Any] | None = None) -> Path:
    payload = payload or {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return Path(str(root)).resolve()


def _load_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        return payload if isinstance(payload, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _load_config(root: Path) -> dict[str, Any]:
    path = root / CONFIG_RELATIVE_PATH
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return config if isinstance(config, dict) else {}


def _tool_name(payload: dict[str, Any]) -> str:
    value = payload.get("tool_name") or payload.get("tool") or ""
    return str(value)


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input")
    if isinstance(value, dict):
        return value
    arguments = payload.get("arguments")
    if isinstance(arguments, dict):
        return arguments
    return {}


def _normalize_rel_path(file_path: str, root: Path) -> tuple[str, Path] | None:
    if not file_path or file_path.startswith("<"):
        return file_path, root / file_path
    try:
        raw = Path(file_path)
        absolute = raw if raw.is_absolute() else root / raw
        resolved = absolute.resolve()
        rel = resolved.relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return None
    return rel, resolved


def _is_durable_lo_enforced(
    root: Path,
    *,
    harness_name: str | None,
    harness_id: str | None,
) -> bool:
    """Return the original durable-role gate decision with fail-open behavior."""
    if (
        load_role_assignments is None
        or resolved_harness_id is None
        or is_prime_builder is None
        or is_loyal_opposition is None
    ):
        return False
    try:
        resolved_id = resolved_harness_id(
            root,
            harness_id=str(harness_id) if harness_id else None,
            harness_name=str(harness_name) if harness_name else None,
        )
        document = load_role_assignments(root)
    except Exception:
        return False
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict) or not harnesses:
        return False
    record = harnesses.get(str(resolved_id)) if resolved_id else None
    if not isinstance(record, dict):
        return False
    if is_prime_builder(record):
        return False
    return bool(is_loyal_opposition(record))


def _is_lo_enforced(root: Path, payload: dict[str, Any]) -> bool:
    """Return True when the resolved session role is Loyal Opposition.

    Resolution order (per DCL-SESSION-ROLE-RESOLUTION-001):
    1. Session-role marker (if present, valid, and session-id verified) -> marker role.
    2. Durable role assignment (harness-state/harness-registry.json) as fallback.

    Missing/malformed role state is fail-open by design so startup repairs and
    fresh clones are not hard-blocked by an unavailable projection.
    """
    # --- Resolve harness_name (same heuristic as the prior durable-only path) ---
    harness_name = os.environ.get("GTKB_HARNESS_NAME") or payload.get("harness_name")
    if not harness_name and os.environ.get("CLAUDE_PROJECT_DIR"):
        harness_name = "claude"
    harness_id = (
        os.environ.get("GTKB_ACTIVE_HARNESS_ID")
        or os.environ.get("GTKB_HARNESS_ID")
        or payload.get("harness_id")
        or payload.get("active_harness_id")
    )
    if not harness_name and not harness_id:
        harness_name = "codex"

    # --- Preferred path: session role resolver (marker > durable) ---
    if resolve_interactive_session_role is not None and resolve_session_id is not None:
        try:
            payload_session_id = payload.get("session_id") or payload.get("active_session_id")
            current_session_id = (
                resolve_session_id(
                    payload_session_id,
                    order=MARKER_CONTINUITY_ORDER or (),
                )
                or None
            )
            resolved_role, _outcome = resolve_interactive_session_role(
                root,
                harness_name=str(harness_name) if harness_name else "claude",
                current_session_id=current_session_id,
            )
            if str(_outcome).startswith("durable_"):
                return _is_durable_lo_enforced(
                    root,
                    harness_name=str(harness_name) if harness_name else None,
                    harness_id=str(harness_id) if harness_id else None,
                )
            return resolved_role == "loyal-opposition"
        except Exception:  # noqa: BLE001 - fail-open on any resolver error
            pass

    # --- Fallback: durable-only resolution (original behavior) ---
    return _is_durable_lo_enforced(
        root,
        harness_name=str(harness_name) if harness_name else None,
        harness_id=str(harness_id) if harness_id else None,
    )


def _matches_any(patterns: list[str], rel_path: str) -> bool:
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)


def _allow_patterns(config: dict[str, Any]) -> list[str]:
    raw = config.get("allow_patterns") or []
    return [str(item).replace("\\", "/") for item in raw if isinstance(item, str)]


def _is_allowlisted(config: dict[str, Any], rel_path: str) -> bool:
    return _matches_any(_allow_patterns(config), rel_path)


def _first_nonblank_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _apply_edit(existing: str, old: str, new: str, *, replace_all: bool = False) -> str:
    if old == "":
        raise ValueError("old_string must be non-empty")
    if replace_all:
        if old not in existing:
            raise ValueError("old_string not found")
        return existing.replace(old, new)
    if existing.count(old) != 1:
        raise ValueError("old_string must match exactly once")
    return existing.replace(old, new, 1)


def _candidate_from_edit(tool_name: str, tool_input: dict[str, Any], file_path: Path) -> str | None:
    if tool_name == "Write":
        content = tool_input.get("content")
        return content if isinstance(content, str) else ""
    existing = _read_text(file_path)
    if tool_name == "Edit":
        return _apply_edit(
            existing,
            str(tool_input.get("old_string") or ""),
            str(tool_input.get("new_string") or ""),
            replace_all=bool(tool_input.get("replace_all")),
        )
    if tool_name == "MultiEdit":
        content = existing
        edits = tool_input.get("edits") or []
        if not isinstance(edits, list):
            raise ValueError("edits must be a list")
        for edit in edits:
            if not isinstance(edit, dict):
                raise ValueError("each edit must be an object")
            content = _apply_edit(
                content,
                str(edit.get("old_string") or ""),
                str(edit.get("new_string") or ""),
                replace_all=bool(edit.get("replace_all")),
            )
        return content
    return None


def _packet_ref(tool_input: dict[str, Any]) -> str | None:
    env_ref = os.environ.get(APPROVAL_ENV_VAR)
    if env_ref:
        return env_ref
    explicit = tool_input.get("lo_file_safety_approval_packet")
    return explicit if isinstance(explicit, str) and explicit else None


def _load_packet(packet_ref: str, root: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        path = Path(packet_ref).expanduser()
        if not path.is_absolute():
            path = root / path
        packet = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - convert all packet failures to block text
        return None, f"approval packet could not be read or parsed: {exc}"
    if not isinstance(packet, dict):
        return None, "approval packet root must be a JSON object"
    return packet, None


def _validate_packet(packet: dict[str, Any], rel_path: str, candidate_content: str) -> str | None:
    required = {
        "artifact_type",
        "target_path",
        "full_content",
        "full_content_sha256",
        "presented_to_user",
        "transcript_captured",
        "explicit_change_request",
        "changed_by",
        "change_reason",
        "approved_by",
    }
    missing = sorted(required - set(packet))
    if missing:
        return f"approval packet missing required fields: {', '.join(missing)}"
    if packet.get("artifact_type") != APPROVAL_PACKET_TYPE:
        return f"approval packet artifact_type must be {APPROVAL_PACKET_TYPE!r}"
    target = str(packet.get("target_path") or "").replace("\\", "/").lstrip("./")
    if target != rel_path:
        return f"approval packet target_path {target!r} does not match write target {rel_path!r}"
    full_content = packet.get("full_content")
    if not isinstance(full_content, str):
        return "approval packet full_content must be a string"
    expected_hash = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    if packet.get("full_content_sha256") != expected_hash:
        return "approval packet full_content_sha256 does not match full_content"
    if full_content != candidate_content:
        return "approval packet full_content does not match the proposed post-edit content"
    for flag_name in ("presented_to_user", "transcript_captured"):
        if packet.get(flag_name) is not True:
            return f"approval packet requires {flag_name}=true"
    if str(packet.get("approved_by") or "").strip().lower() != "owner":
        return "approval packet approved_by must be 'owner'"
    for field in ("explicit_change_request", "changed_by", "change_reason"):
        if not str(packet.get(field) or "").strip():
            return f"approval packet {field} must be non-empty"
    return None


def _packet_allows(tool_input: dict[str, Any], root: Path, rel_path: str, candidate_content: str) -> str | None:
    packet_ref = _packet_ref(tool_input)
    if not packet_ref:
        return "No LO file-safety approval packet was found."
    packet, parse_error = _load_packet(packet_ref, root)
    if packet is None:
        return parse_error or "approval packet did not load"
    return _validate_packet(packet, rel_path, candidate_content)


_RETIRED_BRIDGE_AGGREGATE_NAME = "INDEX.md"


def _is_retired_bridge_aggregate_path(rel_path: str) -> bool:
    path = Path(rel_path.replace("\\", "/"))
    parts = tuple(path.parts)
    return len(parts) >= 2 and parts[-2].lower() == "bridge" and parts[-1] == _RETIRED_BRIDGE_AGGREGATE_NAME


def _bridge_file_decision(change: Change, root: Path, tool_input: dict[str, Any]) -> dict[str, Any]:
    rel = change.rel_path
    if _is_retired_bridge_aggregate_path(rel):
        return _block("BLOCKED (GTKB-LO-FILE-SAFETY): retired bridge aggregate files are not live bridge artifacts.")
    if rel.startswith("bridge/") and rel.endswith(".md"):
        if change.operation == "Write" and not change.abs_path.exists() and change.candidate_content is not None:
            first_line = _first_nonblank_line(change.candidate_content)
            if first_line in LO_STATUS_TOKENS and VERSIONED_BRIDGE_PATH_RE.match(rel):
                return {}
            return _block(
                "BLOCKED (GTKB-LO-FILE-SAFETY): new bridge files written by Loyal Opposition must be "
                "GO, NO-GO, VERIFIED, or ADVISORY verdict/report files."
            )
        return _block(
            "BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition may not edit or overwrite existing bridge artifacts."
        )
    _ = root, tool_input
    return {}


def _change_decision(change: Change, root: Path, config: dict[str, Any], tool_input: dict[str, Any]) -> dict[str, Any]:
    rel = change.rel_path
    if rel.startswith("<"):
        return _block(
            "BLOCKED (GTKB-LO-FILE-SAFETY): unresolved or opaque shell mutation target requires a non-shell edit path."
        )
    if change.operation == "Delete":
        return _block(f"BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition may not delete {rel!r}.")
    if _is_retired_bridge_aggregate_path(rel) or (rel.startswith("bridge/") and rel.endswith(".md")):
        return _bridge_file_decision(change, root, tool_input)
    if _is_allowlisted(config, rel):
        return {}
    if change.candidate_content is None:
        return _block(
            f"BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition shell mutation to {rel!r} is outside the allow-list; "
            "use Write/Edit/MultiEdit with an owner approval packet for exceptional changes."
        )
    packet_error = _packet_allows(tool_input, root, rel, change.candidate_content)
    if packet_error is None:
        return {}
    return _block(
        f"BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition write to {rel!r} is outside the allow-list. "
        f"{packet_error} Reference a valid packet with {APPROVAL_ENV_VAR}=<path>."
    )


def _simple_changes_from_claude_payload(payload: dict[str, Any], root: Path) -> tuple[list[Change], dict[str, Any]]:
    tool_name = _tool_name(payload)
    tool_input = _tool_input(payload)
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        return [], tool_input
    normalized = _normalize_rel_path(file_path, root)
    if normalized is None:
        return [], tool_input
    rel, absolute = normalized
    try:
        candidate = _candidate_from_edit(tool_name, tool_input, absolute)
    except (OSError, ValueError) as exc:
        return [Change("Unknown", rel, absolute, None)], {"_reconstruction_error": str(exc), **tool_input}
    operation = "Write" if tool_name == "Write" else "Edit"
    return [Change(operation, rel, absolute, candidate)], tool_input


def _extract_command(payload: dict[str, Any]) -> str:
    tool_input = _tool_input(payload)
    for key in ("command", "script", "cmd"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def _clean_target_token(value: str) -> str:
    return value.strip().strip("\"'`").rstrip(";,)")


def _is_null_sink(path: str) -> bool:
    cleaned = _clean_target_token(path).replace("\\", "/").lower()
    return cleaned in NULL_SINKS or cleaned.endswith("/dev/null")


def _target_change(raw_path: str, root: Path, *, operation: str = "Write") -> Change | None:
    path = _clean_target_token(raw_path)
    if not path or path.startswith("-") or _is_null_sink(path):
        return None
    normalized = _normalize_rel_path(path, root)
    if normalized is None:
        return Change(operation, "<outside-project-root>", root / "<outside-project-root>", None)
    rel, absolute = normalized
    return Change(operation, rel, absolute, None)


def _powershell_targets(command: str, root: Path) -> list[Change]:
    changes: list[Change] = []
    write_cmd = r"(?:Set-Content|Add-Content|Out-File)"
    for match in re.finditer(
        rf"\b{write_cmd}\b(?P<body>[^;&|\n]*)",
        command,
        re.IGNORECASE,
    ):
        body = match.group("body")
        path_match = re.search(r"(?:-(?:LiteralPath|Path|FilePath)\s+)?(?P<path>\"[^\"]+\"|'[^']+'|[^\s]+)", body)
        if path_match:
            change = _target_change(path_match.group("path"), root)
            if change:
                changes.append(change)
    destructive = r"(?:Remove-Item|rm|del|erase)"
    for match in re.finditer(rf"\b{destructive}\b(?P<body>[^;&|\n]*)", command, re.IGNORECASE):
        body = match.group("body")
        path_match = re.search(r"(?:-(?:LiteralPath|Path)\s+)?(?P<path>\"[^\"]+\"|'[^']+'|[^\s]+)", body)
        if path_match:
            change = _target_change(path_match.group("path"), root, operation="Delete")
            if change:
                changes.append(change)
    move_copy = r"(?:Move-Item|Copy-Item|mv|cp|copy)"
    for match in re.finditer(rf"\b{move_copy}\b(?P<body>[^;&|\n]*)", command, re.IGNORECASE):
        tokens = re.findall(r"\"[^\"]+\"|'[^']+'|[^\s]+", match.group("body"))
        useful = [token for token in tokens if not token.startswith("-")]
        if useful:
            change = _target_change(useful[-1], root)
            if change:
                changes.append(change)
            if re.match(r"\s*(?:Move-Item|mv)\b", match.group(0), re.IGNORECASE) and len(useful) > 1:
                source = _target_change(useful[0], root, operation="Delete")
                if source:
                    changes.append(source)
    return changes


def _bash_targets(payload: dict[str, Any], root: Path) -> list[Change]:
    command = _extract_command(payload)
    if not command:
        return []
    changes: list[Change] = []
    if ("$(" in command or re.search(r"`[^`]+`", command)) and WRITEISH_COMMAND_RE.search(command):
        changes.append(Change("Write", "<opaque-command-substitution>", root / "<opaque-command-substitution>", None))
    for match in re.finditer(
        r"\bcat\b[^\n;&|]*?(?:>\s*|>>\s*)(?P<path>\"[^\"]+\"|'[^']+'|[^\s]+)\s*<<",
        command,
        re.IGNORECASE,
    ):
        change = _target_change(match.group("path"), root)
        if change:
            changes.append(change)
    for match in re.finditer(
        r"(?<![:<>=!-])(?:\d?>|>>)\s*(?P<path>\"[^\"]+\"|'[^']+'|[^\s;&|]+)",
        command,
    ):
        change = _target_change(match.group("path"), root)
        if change:
            changes.append(change)
    for match in re.finditer(r"\btee\s+(?P<path>\"[^\"]+\"|'[^']+'|[^\s;&|]+)", command, re.IGNORECASE):
        change = _target_change(match.group("path"), root)
        if change:
            changes.append(change)
    for match in re.finditer(r"\bgit\s+restore\b", command, re.IGNORECASE):
        args_text = _split_command_segment(command, match.end())
        pathspecs = _git_pathspecs(_tokenize_argv(args_text), _GIT_RESTORE_OPTS_WITH_ARG)
        for path in pathspecs:
            change = _target_change(path, root, operation="Delete")
            if change:
                changes.append(change)
    for match in re.finditer(r"\bgit\s+checkout\b", command, re.IGNORECASE):
        args_text = _split_command_segment(command, match.end())
        tokens = _tokenize_argv(args_text)
        if "--" not in tokens:
            continue
        dash_dash_index = tokens.index("--")
        for path in tokens[dash_dash_index + 1 :]:
            if not path:
                continue
            change = _target_change(path, root, operation="Delete")
            if change:
                changes.append(change)
    changes.extend(_powershell_targets(command, root))
    return changes


def _extract_patch_text(payload: dict[str, Any]) -> str:
    tool_input = _tool_input(payload)
    candidates: list[Any] = [
        tool_input.get("patch"),
        tool_input.get("input"),
        payload.get("input"),
        payload.get("patch"),
    ]
    arguments = tool_input.get("arguments")
    if isinstance(arguments, dict):
        candidates.extend([arguments.get("payload"), arguments.get("patch"), arguments.get("input")])
    for candidate in candidates:
        if isinstance(candidate, str) and "*** Begin Patch" in candidate:
            return candidate
    return ""


def _apply_patch_hunks(existing: str, hunk_lines: list[str]) -> str:
    lines = existing.splitlines()
    cursor = 0
    old_part: list[str] = []
    new_part: list[str] = []
    hunks: list[tuple[list[str], list[str]]] = []
    for line in hunk_lines:
        if line.startswith("@@"):
            if old_part or new_part:
                hunks.append((old_part, new_part))
            old_part = []
            new_part = []
            continue
        if line == "*** End of File":
            continue
        if not line:
            continue
        prefix = line[0]
        value = line[1:]
        if prefix == " ":
            old_part.append(value)
            new_part.append(value)
        elif prefix == "-":
            old_part.append(value)
        elif prefix == "+":
            new_part.append(value)
    if old_part or new_part:
        hunks.append((old_part, new_part))
    for old, new in hunks:
        if old:
            index = _find_subsequence(lines, old, cursor)
            if index < 0:
                raise ValueError("patch hunk context was not found")
            lines[index : index + len(old)] = new
            cursor = index + len(new)
        else:
            lines[cursor:cursor] = new
            cursor += len(new)
    return "\n".join(lines) + ("\n" if existing.endswith("\n") or hunk_lines else "")


def _find_subsequence(lines: list[str], needle: list[str], start: int) -> int:
    for index in range(start, len(lines) - len(needle) + 1):
        if lines[index : index + len(needle)] == needle:
            return index
    for index in range(0, len(lines) - len(needle) + 1):
        if lines[index : index + len(needle)] == needle:
            return index
    return -1


def _patch_changes(payload: dict[str, Any], root: Path) -> tuple[list[Change], dict[str, Any]]:
    patch = _extract_patch_text(payload)
    if not patch:
        return [], {}
    lines = patch.splitlines()
    changes: list[Change] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        add_match = re.match(r"^\*\*\* Add File:\s+(.+)$", line)
        update_match = re.match(r"^\*\*\* Update File:\s+(.+)$", line)
        delete_match = re.match(r"^\*\*\* Delete File:\s+(.+)$", line)
        if add_match:
            path = add_match.group(1).strip()
            content_lines: list[str] = []
            idx += 1
            while idx < len(lines) and not lines[idx].startswith("*** "):
                if lines[idx].startswith("+"):
                    content_lines.append(lines[idx][1:])
                idx += 1
            normalized = _normalize_rel_path(path, root)
            if normalized:
                rel, absolute = normalized
                content = "\n".join(content_lines) + ("\n" if content_lines else "")
                changes.append(Change("Write", rel, absolute, content))
            continue
        if update_match:
            path = update_match.group(1).strip()
            hunk_lines: list[str] = []
            move_to: str | None = None
            idx += 1
            while idx < len(lines) and not lines[idx].startswith("*** "):
                move_match = re.match(r"^\*\*\* Move to:\s+(.+)$", lines[idx])
                if move_match:
                    move_to = move_match.group(1).strip()
                else:
                    hunk_lines.append(lines[idx])
                idx += 1
            normalized = _normalize_rel_path(path, root)
            if normalized:
                rel, absolute = normalized
                try:
                    candidate = _apply_patch_hunks(_read_text(absolute), hunk_lines)
                except (OSError, ValueError):
                    candidate = None
                changes.append(Change("Edit", rel, absolute, candidate))
            if move_to:
                normalized_move = _normalize_rel_path(move_to, root)
                if normalized_move:
                    rel, absolute = normalized_move
                    changes.append(Change("Write", rel, absolute, None))
            continue
        if delete_match:
            path = delete_match.group(1).strip()
            normalized = _normalize_rel_path(path, root)
            if normalized:
                rel, absolute = normalized
                changes.append(Change("Delete", rel, absolute, None))
        idx += 1
    return changes, {}


def _changed_paths(payload: dict[str, Any], root: Path) -> tuple[list[Change], dict[str, Any]]:
    tool_name = _tool_name(payload)
    if tool_name in {"Write", "Edit", "MultiEdit"}:
        return _simple_changes_from_claude_payload(payload, root)
    if tool_name == "Bash":
        return _bash_targets(payload, root), _tool_input(payload)
    if tool_name in {"apply_patch", "functions.apply_patch"} or "*** Begin Patch" in json.dumps(payload):
        return _patch_changes(payload, root)
    return [], {}


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    root = _project_root(payload)
    if not _is_lo_enforced(root, payload):
        return {}
    config = _load_config(root)
    if not config:
        return {}
    changes, tool_input = _changed_paths(payload, root)
    for change in changes:
        decision = _change_decision(change, root, config, tool_input)
        if decision:
            return decision
    return {}


def main() -> int:
    if "--self-test" in sys.argv:
        _emit_pass()
        return 0
    payload = _load_payload()
    _emit(gate_decision(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
