# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Session-start ORIENT block validation and prior-session doctor checks."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

OrientDoctorStatus = Literal["pass", "fail", "warning", "info"]

ORIENT_HEADER_RE = re.compile(r"^ORIENT S(\d+) @ (\d{2}:\d{2}Z)\s*$", re.MULTILINE)
ORIENT_ITEM_RE = re.compile(r"^\s*(\d+)\s+(\w+):\s*(.+)$", re.MULTILINE)
UNKNOWN_STRUCTURED_RE = re.compile(r"UNKNOWN:([a-z0-9-]+)")
ORIENT_ITEM_LABELS = ("bridge", "branch", "worktree", "wrap", "blockers", "refresh", "next")
ORIENT_ITEM_COUNT = 7

KNOWN_UNKNOWN_CATEGORIES = frozenset(
    {
        "no-remote-access",
        "first-session",
        "transcript-unavailable",
        "permission-denied",
        "source-missing",
        "harness-unavailable",
        "ci-unavailable",
        "dashboard-unavailable",
    }
)


@dataclass(frozen=True)
class OrientValidationResult:
    valid: bool
    reason: str
    item_count: int = 0
    has_header: bool = False


def encode_claude_project_hash(project_root: Path) -> str:
    """Encode a project root path the way Claude Code names transcript directories."""
    resolved = project_root.resolve()
    drive = resolved.drive
    if drive:
        prefix = drive.rstrip(":").upper() + "--"
        remainder = str(resolved)[len(drive) :].replace("\\", "-").replace("/", "-").strip("-")
        return prefix + remainder
    return str(resolved).replace("\\", "-").replace("/", "-").strip("-")


def resolve_transcript_dir(target: Path) -> tuple[Path | None, str | None]:
    """Resolve the harness transcript directory for *target* using env overrides first."""
    explicit_path = os.environ.get("CLAUDE_TRANSCRIPT_PATH")
    if explicit_path:
        path = Path(explicit_path)
        if path.is_file():
            return path.parent, None
        if path.is_dir():
            return path, None
        return None, f"CLAUDE_TRANSCRIPT_PATH does not exist: {explicit_path}"

    base = Path(os.environ.get("CLAUDE_TRANSCRIPT_DIR", Path.home() / ".claude" / "projects"))
    project_hash = os.environ.get("CLAUDE_PROJECT_HASH") or encode_claude_project_hash(target)
    transcript_dir = base / project_hash
    if not transcript_dir.is_dir():
        return None, None
    return transcript_dir, None


def read_transcript_tail(path: Path, max_events: int = 500) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    tail_lines = lines[-max_events:] if len(lines) > max_events else lines
    events: list[dict[str, Any]] = []
    for line in tail_lines:
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _extract_text_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
                elif "text" in block:
                    parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content) if content is not None else ""


def extract_last_assistant_text(events: list[dict[str, Any]]) -> str:
    for event in reversed(events):
        if event.get("type") != "assistant":
            continue
        message = event.get("message") or {}
        text = _extract_text_content(message.get("content"))
        if text.strip():
            return text
    return ""


def find_latest_transcript(transcript_dir: Path) -> Path | None:
    if not transcript_dir.is_dir():
        return None
    candidates = [
        path for path in transcript_dir.glob("*.jsonl") if path.is_file() and not path.name.startswith("agent-")
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def find_orient_block(text: str) -> str | None:
    match = ORIENT_HEADER_RE.search(text)
    if not match:
        return None
    return text[match.start() :]


def validate_orient_block(text: str) -> OrientValidationResult:
    block = find_orient_block(text)
    if block is None:
        return OrientValidationResult(valid=False, reason="missing ORIENT header", item_count=0, has_header=False)

    if not ORIENT_HEADER_RE.search(block):
        return OrientValidationResult(valid=False, reason="malformed ORIENT header", item_count=0, has_header=False)

    items = ORIENT_ITEM_RE.findall(block)
    if len(items) != ORIENT_ITEM_COUNT:
        return OrientValidationResult(
            valid=False,
            reason=f"expected {ORIENT_ITEM_COUNT} numbered items, found {len(items)}",
            item_count=len(items),
            has_header=True,
        )

    seen_numbers: set[int] = set()
    seen_labels: list[str] = []
    for number_text, label, _value in items:
        number = int(number_text)
        if number in seen_numbers:
            return OrientValidationResult(
                valid=False,
                reason=f"duplicate item number {number}",
                item_count=len(items),
                has_header=True,
            )
        seen_numbers.add(number)
        seen_labels.append(label)

    if seen_numbers != set(range(1, ORIENT_ITEM_COUNT + 1)):
        return OrientValidationResult(
            valid=False,
            reason="item numbers must be exactly 1..7",
            item_count=len(items),
            has_header=True,
        )

    if list(seen_labels) != list(ORIENT_ITEM_LABELS):
        return OrientValidationResult(
            valid=False,
            reason=f"item labels must be {list(ORIENT_ITEM_LABELS)}",
            item_count=len(items),
            has_header=True,
        )

    for _number_text, _label, value in items:
        if "UNKNOWN" in value and not UNKNOWN_STRUCTURED_RE.search(value):
            return OrientValidationResult(
                valid=False,
                reason="UNKNOWN values must use structured tags like UNKNOWN:no-remote-access",
                item_count=len(items),
                has_header=True,
            )

    return OrientValidationResult(valid=True, reason="well-formed ORIENT block", item_count=len(items), has_header=True)


def check_session_wrap_had_orient(target: Path) -> tuple[OrientDoctorStatus, str]:
    transcript_dir, dir_error = resolve_transcript_dir(target)
    if dir_error:
        return "warning", f"prior-session ORIENT check skipped: {dir_error}"
    if transcript_dir is None:
        return "info", "no prior session transcript directory found (first-ever session on this machine)"

    try:
        latest = find_latest_transcript(transcript_dir)
    except OSError as exc:
        return "warning", f"prior-session ORIENT check skipped: transcript access failed ({exc})"

    if latest is None:
        return "info", "no prior session transcript found (first-ever session on this machine)"

    try:
        events = read_transcript_tail(latest)
    except OSError as exc:
        return "warning", f"prior-session ORIENT check skipped: transcript read failed ({exc})"

    assistant_text = extract_last_assistant_text(events)
    if not assistant_text.strip():
        return "warning", f"prior session transcript {latest.name} has no assistant text to inspect"

    validation = validate_orient_block(assistant_text)
    if validation.valid:
        return "pass", f"prior session produced a well-formed ORIENT block ({latest.name})"
    if not validation.has_header:
        return "fail", f"prior session ended without an ORIENT block ({latest.name})"
    return "warning", f"prior session ORIENT block malformed: {validation.reason} ({latest.name})"
