"""Strict topic-envelope command parser and router."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from groundtruth_kb.session.envelope import (
    TOPIC_TYPES,
    EnvelopeError,
    close_topic,
    open_topic,
    utc_now_iso,
)

TOPIC_COMMAND_RE = re.compile(r"^::(?P<action>open|close) (?P<topic>spec|build|test|deliberation|project)$")


@dataclass(frozen=True)
class TopicCommand:
    action: Literal["open", "close"]
    topic_type: str
    raw: str


def first_non_blank_line(prompt: str) -> str:
    for line in prompt.splitlines():
        if line.strip():
            return line
    return ""


def parse_topic_command(prompt: str) -> TopicCommand | None:
    line = first_non_blank_line(prompt)
    match = TOPIC_COMMAND_RE.fullmatch(line)
    if not match:
        return None
    return TopicCommand(action=match.group("action"), topic_type=match.group("topic"), raw=line)


def handle_topic_command(
    project_root: Path,
    command: TopicCommand,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
) -> dict[str, object]:
    if command.topic_type not in TOPIC_TYPES:
        raise EnvelopeError(f"Unsupported topic type: {command.topic_type}")
    if command.action == "open":
        topic = open_topic(project_root, command.topic_type, harness_name=harness_name, harness_id=harness_id)
    else:
        topic = close_topic(project_root, command.topic_type, harness_name=harness_name, harness_id=harness_id)
    result = {
        "action": command.action,
        "topic_type": command.topic_type,
        "accepted_at": utc_now_iso(),
        "topic": topic,
    }
    log_dir = project_root / ".gtkb-state" / "topic-envelope-router"
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, sort_keys=True) + "\n")
    return result


def render_topic_context(result: dict[str, object]) -> str:
    topic = result.get("topic") if isinstance(result.get("topic"), dict) else {}
    route_target = topic.get("route_target") if isinstance(topic, dict) else None
    return "\n".join(
        [
            "# GroundTruth-KB Topic Envelope Command",
            "",
            f"`::{result['action']} {result['topic_type']}` accepted.",
            f"- action: {result['action']}",
            f"- topic_type: {result['topic_type']}",
            f"- route_target: {route_target or 'n/a'}",
        ]
    )
