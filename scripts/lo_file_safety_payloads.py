"""Shared Loyal Opposition file-safety payload normalization layer.

Converts harness-native PreToolUse payloads into a typed, side-effect-free
internal representation consumed by the canonical LO file-safety gate.

Supported harnesses: Claude (A), Codex (B), Antigravity (C), Cursor (E).

Specifications: GOV-WORK-TREE-HYGIENE-001, GOV-FILE-BRIDGE-AUTHORITY-001,
    ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Harness(str, Enum):
    CLAUDE = "claude"
    CODEX = "codex"
    ANTIGRAVITY = "antigravity"
    CURSOR = "cursor"
    UNKNOWN = "unknown"


class MutationClass(str, Enum):
    WRITE = "write"
    EDIT = "edit"
    DELETE = "delete"
    SHELL = "shell"
    APPLY_PATCH = "apply_patch"
    OPAQUE = "opaque"
    READ_ONLY = "read_only"


@dataclass(frozen=True)
class NormalizedPayload:
    """Typed, side-effect-free representation of a harness PreToolUse payload."""

    harness: Harness
    tool_name: str
    mutation_class: MutationClass
    target_paths: list[str] = field(default_factory=list)
    command: str = ""
    candidate_content: str | None = None
    is_opaque: bool = False
    opaque_reason: str = ""
    raw_payload: dict[str, Any] = field(default_factory=dict)


# --- Recognised mutation-capable shell patterns ---

_WRITEISH_SHELL_RE = re.compile(
    r"\b("
    r"Set-Content|Add-Content|Out-File|Remove-Item|Move-Item|Copy-Item|"
    r"New-Item|rm|mv|cp|copy|del|erase|tee|"
    r"git\s+restore|git\s+checkout|git\s+reset"
    r")\b|(?<![:<>=!-])(?:\d?>|>>)",
    re.IGNORECASE,
)

_QUOTE = chr(39) + chr(34)  # ' and "

_PYTHON_WHOLE_FILE_RE = re.compile(
    r"\b("
    r"shutil\.(copy|copy2|copyfile|move|rmtree)|"
    r"os\.(remove|unlink|rename|replace)|"
    r"pathlib\.Path\([^)]*\)\.(write_text|read_text|unlink|rename|replace)|"
    r"open\([^)]*,\s*[" + _QUOTE + r"]w[" + _QUOTE + r"]"
    r")(?:\b|$|\s|\))",
    re.IGNORECASE,
)

_GIT_RESET_RE = re.compile(r"\bgit\s+reset\b", re.IGNORECASE)

_LIVE_CARRIER = "groundtruth.db"


def _is_opaque_shell(command: str) -> bool:
    """Return True when a shell command is mutation-capable but opaque."""
    if not command.strip():
        return False
    if _WRITEISH_SHELL_RE.search(command):
        if "$(" in command or "`" in command:
            return True
    return False


def _extract_shell_targets(command: str) -> list[str]:
    """Extract likely target paths from a shell command string."""
    if not command.strip():
        return []
    targets: list[str] = []
    # git reset paths
    for match in _GIT_RESET_RE.finditer(command):
        rest = command[match.end() :].strip()
        # git reset [--soft|--mixed|--hard] [<commit>] [--] [<path>...]
        tokens = rest.split()
        paths = [
            t
            for t in tokens
            if not t.startswith("-") and t not in ("--soft", "--mixed", "--hard", "HEAD", "HEAD~", "HEAD~1")
        ]
        targets.extend(paths)
    # git restore / checkout paths
    for match in re.finditer(r"\bgit\s+(?:restore|checkout)\b", command, re.IGNORECASE):
        rest = command[match.end() :].strip()
        tokens = rest.split()
        if "--" in tokens:
            idx = tokens.index("--")
            targets.extend(tokens[idx + 1 :])
    # redirect targets
    for match in re.finditer(r"(?<![:<>=!-])(?:\d?>|>>)\s*(\S+)", command):
        targets.append(match.group(1))
    return targets


def _classify_shell(command: str) -> tuple[MutationClass, bool, str]:
    """Classify a shell command string."""
    if not command.strip():
        return MutationClass.READ_ONLY, False, ""
    if _is_opaque_shell(command):
        return MutationClass.OPAQUE, True, "command substitution in mutation-capable shell command"
    if _WRITEISH_SHELL_RE.search(command):
        return MutationClass.SHELL, False, ""
    if _PYTHON_WHOLE_FILE_RE.search(command):
        return MutationClass.SHELL, False, ""
    return MutationClass.READ_ONLY, False, ""


def normalize_claude(payload: dict[str, Any]) -> NormalizedPayload:
    """Normalize a Claude Code PreToolUse payload."""
    tool_name = str(payload.get("tool_name") or payload.get("tool") or "")
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}

    if tool_name in ("Write", "Edit", "MultiEdit"):
        file_path = str(tool_input.get("file_path") or "")
        return NormalizedPayload(
            harness=Harness.CLAUDE,
            tool_name=tool_name,
            mutation_class=MutationClass.WRITE if tool_name == "Write" else MutationClass.EDIT,
            target_paths=[file_path] if file_path else [],
            raw_payload=payload,
        )

    if tool_name == "Bash":
        command = str(tool_input.get("command") or "")
        mc, opaque, reason = _classify_shell(command)
        targets = _extract_shell_targets(command) if mc in (MutationClass.SHELL, MutationClass.OPAQUE) else []
        return NormalizedPayload(
            harness=Harness.CLAUDE,
            tool_name="Bash",
            mutation_class=mc,
            target_paths=targets,
            command=command,
            is_opaque=opaque,
            opaque_reason=reason,
            raw_payload=payload,
        )

    if tool_name in ("apply_patch", "functions.apply_patch"):
        return NormalizedPayload(
            harness=Harness.CLAUDE,
            tool_name=tool_name,
            mutation_class=MutationClass.APPLY_PATCH,
            target_paths=[],
            raw_payload=payload,
        )

    return NormalizedPayload(
        harness=Harness.CLAUDE,
        tool_name=tool_name,
        mutation_class=MutationClass.READ_ONLY,
        raw_payload=payload,
    )


def normalize_codex(payload: dict[str, Any]) -> NormalizedPayload:
    """Normalize a Codex PreToolUse payload."""
    tool_name = str(payload.get("tool_name") or payload.get("tool") or "")
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}

    if tool_name in ("Write", "Edit", "MultiEdit"):
        file_path = str(tool_input.get("file_path") or "")
        return NormalizedPayload(
            harness=Harness.CODEX,
            tool_name=tool_name,
            mutation_class=MutationClass.WRITE if tool_name == "Write" else MutationClass.EDIT,
            target_paths=[file_path] if file_path else [],
            raw_payload=payload,
        )

    if tool_name == "Bash":
        command = str(tool_input.get("command") or tool_input.get("cmd") or "")
        mc, opaque, reason = _classify_shell(command)
        targets = _extract_shell_targets(command) if mc in (MutationClass.SHELL, MutationClass.OPAQUE) else []
        return NormalizedPayload(
            harness=Harness.CODEX,
            tool_name="Bash",
            mutation_class=mc,
            target_paths=targets,
            command=command,
            is_opaque=opaque,
            opaque_reason=reason,
            raw_payload=payload,
        )

    if tool_name in ("apply_patch", "functions.apply_patch"):
        return NormalizedPayload(
            harness=Harness.CODEX,
            tool_name=tool_name,
            mutation_class=MutationClass.APPLY_PATCH,
            target_paths=[],
            raw_payload=payload,
        )

    return NormalizedPayload(
        harness=Harness.CODEX,
        tool_name=tool_name,
        mutation_class=MutationClass.READ_ONLY,
        raw_payload=payload,
    )


def normalize_antigravity(payload: dict[str, Any]) -> NormalizedPayload:
    """Normalize an Antigravity PreToolUse payload."""
    tool_name = str(payload.get("tool_name") or payload.get("tool") or "")
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}

    if tool_name == "run_command":
        command = str(tool_input.get("command") or "")
        mc, opaque, reason = _classify_shell(command)
        targets = _extract_shell_targets(command) if mc in (MutationClass.SHELL, MutationClass.OPAQUE) else []
        return NormalizedPayload(
            harness=Harness.ANTIGRAVITY,
            tool_name="run_command",
            mutation_class=mc,
            target_paths=targets,
            command=command,
            is_opaque=opaque,
            opaque_reason=reason,
            raw_payload=payload,
        )

    if tool_name in ("write_to_file", "replace_file_content"):
        file_path = str(tool_input.get("file_path") or tool_input.get("path") or "")
        return NormalizedPayload(
            harness=Harness.ANTIGRAVITY,
            tool_name=tool_name,
            mutation_class=MutationClass.WRITE if tool_name == "write_to_file" else MutationClass.EDIT,
            target_paths=[file_path] if file_path else [],
            candidate_content=str(tool_input.get("content") or "") if tool_name == "write_to_file" else None,
            raw_payload=payload,
        )

    if tool_name == "multi_replace_file_content":
        file_path = str(tool_input.get("file_path") or "")
        return NormalizedPayload(
            harness=Harness.ANTIGRAVITY,
            tool_name=tool_name,
            mutation_class=MutationClass.EDIT,
            target_paths=[file_path] if file_path else [],
            raw_payload=payload,
        )

    return NormalizedPayload(
        harness=Harness.ANTIGRAVITY,
        tool_name=tool_name,
        mutation_class=MutationClass.READ_ONLY,
        raw_payload=payload,
    )


def normalize_cursor(payload: dict[str, Any]) -> NormalizedPayload:
    """Normalize a Cursor PreToolUse payload."""
    tool_name = str(payload.get("tool_name") or payload.get("toolName") or payload.get("tool") or "")
    tool_input = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
    if not tool_input:
        raw_input = payload.get("toolInput")
        tool_input = raw_input if isinstance(raw_input, dict) else {}
    file_path = str(tool_input.get("file_path") or tool_input.get("path") or payload.get("path") or "")

    if tool_name == "Write":
        return NormalizedPayload(
            harness=Harness.CURSOR,
            tool_name=tool_name,
            mutation_class=MutationClass.WRITE,
            target_paths=[file_path] if file_path else [],
            raw_payload=payload,
        )
    if tool_name in ("StrReplace", "Edit", "MultiEdit"):
        return NormalizedPayload(
            harness=Harness.CURSOR,
            tool_name=tool_name,
            mutation_class=MutationClass.EDIT,
            target_paths=[file_path] if file_path else [],
            raw_payload=payload,
        )
    if tool_name == "Delete":
        return NormalizedPayload(
            harness=Harness.CURSOR,
            tool_name=tool_name,
            mutation_class=MutationClass.DELETE,
            target_paths=[file_path] if file_path else [],
            raw_payload=payload,
        )

    if tool_name in ("Shell", "Bash"):
        command = str(tool_input.get("command") or payload.get("command") or "")
        mc, opaque, reason = _classify_shell(command)
        targets = _extract_shell_targets(command) if mc in (MutationClass.SHELL, MutationClass.OPAQUE) else []
        return NormalizedPayload(
            harness=Harness.CURSOR,
            tool_name=tool_name,
            mutation_class=mc,
            target_paths=targets,
            command=command,
            is_opaque=opaque,
            opaque_reason=reason,
            raw_payload=payload,
        )

    glob_dir = str(tool_input.get("target_directory") or "")
    read_path = file_path or glob_dir
    return NormalizedPayload(
        harness=Harness.CURSOR,
        tool_name=tool_name,
        mutation_class=MutationClass.READ_ONLY,
        target_paths=[read_path] if read_path else [],
        raw_payload=payload,
    )


def normalize(payload: dict[str, Any], harness: str | Harness | None = None) -> NormalizedPayload:
    """Normalize any harness payload to a typed internal representation.

    If harness is not provided, attempts to detect from payload fields.
    """
    if isinstance(harness, Harness):
        h = harness
    elif harness:
        try:
            h = Harness(harness.lower())
        except ValueError:
            h = Harness.UNKNOWN
    else:
        h = Harness.UNKNOWN

    if h == Harness.CLAUDE:
        return normalize_claude(payload)
    if h == Harness.CODEX:
        return normalize_codex(payload)
    if h == Harness.ANTIGRAVITY:
        return normalize_antigravity(payload)
    if h == Harness.CURSOR:
        return normalize_cursor(payload)

    # Auto-detect
    tool_name = str(payload.get("tool_name") or payload.get("tool") or "")
    if tool_name in ("run_command", "write_to_file", "replace_file_content", "multi_replace_file_content"):
        return normalize_antigravity(payload)
    if tool_name in ("Shell",):
        return normalize_cursor(payload)
    return normalize_claude(payload)


def targets_include_live_carrier(normalized: NormalizedPayload, carrier: str = _LIVE_CARRIER) -> bool:
    """Check whether any target path matches the live carrier."""
    carrier_lower = carrier.lower()
    for path in normalized.target_paths:
        cleaned = path.strip().strip("\"'").rstrip("/\\")
        if (
            cleaned.lower() == carrier_lower
            or cleaned.lower().endswith(f"/{carrier_lower}")
            or cleaned.lower().endswith(f"\\{carrier_lower}")
        ):
            return True
    return False


def is_mutation_payload(normalized: NormalizedPayload) -> bool:
    """Return True if the normalized payload is capable of mutation."""
    return normalized.mutation_class in (
        MutationClass.WRITE,
        MutationClass.EDIT,
        MutationClass.DELETE,
        MutationClass.SHELL,
        MutationClass.APPLY_PATCH,
        MutationClass.OPAQUE,
    )
