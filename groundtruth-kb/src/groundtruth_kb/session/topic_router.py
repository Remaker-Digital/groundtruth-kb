"""Strict topic-envelope command parser and router."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from groundtruth_kb.activity.ops import render_ops_activity_context
from groundtruth_kb.activity.profiles import ActivityProfileError, load_activity_profiles
from groundtruth_kb.session.envelope import (
    TOPIC_TYPES,
    EnvelopeError,
    close_topic,
    open_topic,
    utc_now_iso,
)

_TOPIC_TYPE_PATTERN = "|".join(TOPIC_TYPES)
TOPIC_COMMAND_RE = re.compile(rf"^::(?P<action>open|close) (?P<topic>{_TOPIC_TYPE_PATTERN})$")


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
    return TopicCommand(action=match.group("action"), topic_type=match.group("topic"), raw=line)  # type: ignore[arg-type]


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
        "project_root": str(project_root),
        "topic": topic,
    }
    log_dir = project_root / ".gtkb-state" / "topic-envelope-router"
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, sort_keys=True) + "\n")
    return result  # type: ignore[return-value]


def _format_sequence(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _format_history_state(history_state: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    sources = history_state.get("sources")
    if isinstance(sources, list):
        lines.append(f"- history_state.sources: {_format_sequence([str(item) for item in sources])}")
    else:
        lines.append("- history_state.sources: none")
    return lines


def _format_direction(direction: dict[str, Any]) -> list[str]:
    lines = [f"- direction.stance: {direction.get('stance') or 'n/a'}"]
    guardrails = direction.get("guardrails")
    if isinstance(guardrails, list):
        lines.append(f"- direction.guardrails: {_format_sequence([str(item) for item in guardrails])}")
    else:
        lines.append("- direction.guardrails: none")
    manipulates = direction.get("manipulates")
    if isinstance(manipulates, list):
        lines.append(f"- direction.manipulates: {_format_sequence([str(item) for item in manipulates])}")
    else:
        lines.append("- direction.manipulates: none")
    return lines


def _render_activity_profile(result: dict[str, object]) -> str:
    if result.get("action") != "open":
        return ""
    topic_type = result.get("topic_type")
    if not isinstance(topic_type, str):
        return ""
    try:
        profile = load_activity_profiles().get(topic_type)
    except ActivityProfileError as exc:
        return "\n".join(
            [
                "## Activity Disposition Profile",
                "",
                "- status: unavailable",
                f"- reason: {exc}",
            ]
        )
    if profile is None:
        return "\n".join(
            [
                "## Activity Disposition Profile",
                "",
                "- status: unavailable",
                f"- reason: no profile configured for activity {topic_type!r}",
            ]
        )
    lines = [
        "## Activity Disposition Profile",
        "",
        f"- name: {profile.name}",
        f"- version: {profile.version}",
        f"- headless_eligibility: {profile.headless_eligibility}",
        f"- skills: {_format_sequence(profile.skills)}",
        f"- terminology: {_format_sequence(profile.terminology)}",
    ]
    lines.extend(_format_history_state(profile.history_state))
    lines.extend(_format_direction(profile.direction))
    return "\n".join(lines)


def _project_root_from_result(result: dict[str, object]) -> Path | None:
    raw_root = result.get("project_root")
    if not isinstance(raw_root, str) or not raw_root.strip():
        return None
    try:
        return Path(raw_root).expanduser().resolve()
    except OSError:
        return None


def _load_startup_module(project_root: Path):
    root_text = str(project_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts import session_self_initialization as startup  # noqa: PLC0415

    return startup


def _render_open_operator_context(result: dict[str, object]) -> str:
    if result.get("action") != "open":
        return ""
    project_root = _project_root_from_result(result)
    if project_root is None:
        return "\n".join(
            [
                "## Open Activity Operator Context",
                "",
                "- status: unavailable",
                "- reason: project root unavailable in topic-router result",
            ]
        )
    try:
        startup = _load_startup_module(project_root)
        model = startup.build_startup_model(project_root, role_profile="prime-builder", fast_hook=True)
        dashboard = startup.GRAFANA_DASHBOARD_URL
        active_work_subject = startup.render_active_work_subject(
            project_root,
            snapshot=model.get("workstream_focus"),
            overlay_status=model.get("session_overlay") or {},
            include_counterpart=True,
            include_overlay_note=False,
            include_operational_instructions=False,
        )
        startup_briefing = startup._render_session_startup_briefing(model)
        top_priorities = startup._render_top_priority_actions_section(model)
    except Exception as exc:  # noqa: BLE001 - topic-open context must not block routing.
        return "\n".join(
            [
                "## Open Activity Operator Context",
                "",
                "- status: unavailable",
                f"- reason: {exc}",
            ]
        )
    return "\n".join(
        [
            "## Open Activity Operator Context",
            "",
            f"- Dashboard: GroundTruth-KB Project Dashboard: {dashboard}",
            "",
            "### Active Work Subject",
            "",
            active_work_subject,
            "",
            "### Session Startup Briefing",
            "",
            startup_briefing,
            "",
            top_priorities,
        ]
    )


def _render_ops_context(result: dict[str, object]) -> str:
    if result.get("action") != "open" or result.get("topic_type") != "ops":
        return ""
    project_root = _project_root_from_result(result)
    if project_root is None:
        return "\n".join(
            [
                "## Ops Activity Status And AUQ Options",
                "",
                "- status: unavailable",
                "- reason: project root unavailable in topic-router result",
            ]
        )
    try:
        return render_ops_activity_context(project_root)
    except Exception as exc:  # noqa: BLE001 - ops context must not block topic routing.
        return "\n".join(
            [
                "## Ops Activity Status And AUQ Options",
                "",
                "- status: unavailable",
                f"- reason: {exc}",
            ]
        )


def render_topic_context(result: dict[str, object]) -> str:
    topic = result.get("topic") if isinstance(result.get("topic"), dict) else {}
    route_target = topic.get("route_target") if isinstance(topic, dict) else None
    base = "\n".join(
        [
            "# GroundTruth-KB Topic Envelope Command",
            "",
            f"`::{result['action']} {result['topic_type']}` accepted.",
            f"- action: {result['action']}",
            f"- topic_type: {result['topic_type']}",
            f"- route_target: {route_target or 'n/a'}",
        ]
    )
    activity_profile = _render_activity_profile(result)
    ops_context = _render_ops_context(result)
    operator_context = _render_open_operator_context(result)
    extra_sections = "\n\n".join(section for section in (activity_profile, ops_context, operator_context) if section)
    if extra_sections:
        return f"{base}\n\n{extra_sections}"
    return base
