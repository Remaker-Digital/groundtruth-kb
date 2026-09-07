"""Strict topic-envelope command parser and router."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from groundtruth_kb.activity.ops import render_ops_activity_context
from groundtruth_kb.activity.profiles import ActivityProfile, ActivityProfileError, load_activity_profiles
from groundtruth_kb.session.envelope import (
    TOPIC_TYPE_ALIASES,
    TOPIC_TYPES,
    EnvelopeError,
    close_current_topic,
    close_topic,
    normalize_topic_type,
    open_topic,
    utc_now_iso,
)

# Aliases first: harmless under fullmatch, but correct if this is ever changed
# to re.match, where "ops" would otherwise shadow "operations".
_TOPIC_TYPE_PATTERN = "|".join((*TOPIC_TYPE_ALIASES, *TOPIC_TYPES))
TOPIC_OPEN_RE = re.compile(rf"^::open (?P<topic>{_TOPIC_TYPE_PATTERN})$")
# Single-active (SPEC-TOPIC-ENVELOPE-ROUTER-001 v3 / DCL-TOPIC-ENVELOPE-ROUTING-001
# v3 clause 7): bare ``::close`` and the typed ``::close <type>`` are both accepted.
TOPIC_CLOSE_RE = re.compile(rf"^::close( (?P<topic>{_TOPIC_TYPE_PATTERN}))?$")
_STARTUP_BRIEFING_STANCES = frozenset({"implement-within-scope"})


@dataclass(frozen=True)
class TopicCommand:
    action: Literal["open", "close"]
    topic_type: str | None
    raw: str


def first_non_blank_line(prompt: str) -> str:
    for line in prompt.splitlines():
        if line.strip():
            return line
    return ""


def parse_topic_command(prompt: str) -> TopicCommand | None:
    line = first_non_blank_line(prompt)
    open_match = TOPIC_OPEN_RE.fullmatch(line)
    if open_match:
        return TopicCommand(action="open", topic_type=normalize_topic_type(open_match.group("topic")), raw=line)
    close_match = TOPIC_CLOSE_RE.fullmatch(line)
    if close_match:
        # ``topic`` group is None for bare ``::close`` (close the current topic).
        return TopicCommand(action="close", topic_type=normalize_topic_type(close_match.group("topic")), raw=line)
    return None


def handle_topic_command(
    project_root: Path,
    command: TopicCommand,
    *,
    harness_name: str = "codex",
    harness_id: str | None = None,
) -> dict[str, object]:
    if command.action == "open":
        if command.topic_type not in TOPIC_TYPES:
            raise EnvelopeError(f"Unsupported topic type: {command.topic_type}")
        topic = open_topic(project_root, command.topic_type, harness_name=harness_name, harness_id=harness_id)
    elif command.topic_type is None:
        # Bare ``::close``: close the single currently-open topic (single-active).
        topic = close_current_topic(project_root, harness_name=harness_name, harness_id=harness_id)
    else:
        if command.topic_type not in TOPIC_TYPES:
            raise EnvelopeError(f"Unsupported topic type: {command.topic_type}")
        topic = close_topic(project_root, command.topic_type, harness_name=harness_name, harness_id=harness_id)
    result = {
        "action": command.action,
        "topic_type": command.topic_type,
        "accepted_at": utc_now_iso(),
        "project_root": str(project_root),
        "topic": topic,
    }
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


def _load_glossary_module(project_root: Path):
    root_text = str(project_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    from scripts import startup_glossary_load  # noqa: PLC0415

    return startup_glossary_load


def _truncate_definition(value: str, limit: int = 180) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3].rstrip()}..."


def _render_activity_terminology(project_root: Path, profile) -> str:
    try:
        glossary = _load_glossary_module(project_root)
        resolved = glossary.resolve_glossary_terms(project_root, list(profile.terminology))
    except Exception as exc:  # noqa: BLE001 - terminology context must not block routing.
        return "\n".join(
            [
                "## Activity Terminology",
                "",
                "- status: unavailable",
                f"- reason: {exc}",
            ]
        )
    lines = [
        "## Activity Terminology",
        "",
        f"- source: `{glossary.GLOSSARY_RELATIVE_PATH}`",
        f"- activity: {profile.name}",
    ]
    for label in profile.terminology:
        entry = resolved.get(label)
        if not isinstance(entry, dict):
            lines.append(f"- **{label}**: (see canonical glossary)")
            continue
        definition = _truncate_definition(str(entry.get("definition") or ""))
        if definition:
            lines.append(f"- **{label}**: {definition}")
        else:
            lines.append(f"- **{label}**: (see canonical glossary)")
    return "\n".join(lines)


def _render_activity_skill_advisory(topic_type: str) -> str:
    try:
        from scripts.skill_usage_router import suggest_for_activity
    except Exception as exc:  # noqa: BLE001 - advisory surface must not block routing.
        return "\n".join(
            [
                "## Activity Skill Advisory",
                "",
                "- status: unavailable",
                f"- reason: {exc}",
            ]
        )
    suggestion = suggest_for_activity(topic_type)
    if suggestion.is_empty:
        return ""
    lines = [
        "## Activity Skill Advisory",
        "",
        f"- scenario: {suggestion.scenario}",
        f"- recommended: {_format_sequence(suggestion.recommended)}",
        f"- rationale: {suggestion.rationale}",
    ]
    return "\n".join(lines)


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
    project_root = _project_root_from_result(result)
    extra_sections: list[str] = []
    if project_root is not None:
        extra_sections.append(_render_activity_terminology(project_root, profile))
    extra_sections.append(_render_activity_skill_advisory(profile.name))
    profile_block = "\n".join(lines)
    rendered_extra = "\n\n".join(section for section in extra_sections if section)
    if rendered_extra:
        return f"{profile_block}\n\n{rendered_extra}"
    return profile_block


def _project_root_from_result(result: dict[str, object]) -> Path | None:
    raw_root = result.get("project_root")
    if not isinstance(raw_root, str) or not raw_root.strip():
        return None
    try:
        return Path(raw_root).expanduser().resolve()
    except OSError:
        return None


def _activity_profile_for_operator_context(result: dict[str, object]) -> ActivityProfile | None:
    topic_type = result.get("topic_type")
    if result.get("action") != "open" or not isinstance(topic_type, str):
        return None
    try:
        return load_activity_profiles().get(topic_type)
    except ActivityProfileError:
        return None


def _uses_startup_briefing(profile: ActivityProfile | None) -> bool:
    if profile is None:
        return True
    return profile.direction.get("stance") in _STARTUP_BRIEFING_STANCES


def _render_activity_stance_operator_context(profile: ActivityProfile) -> str:
    lines = [
        "## Open Activity Operator Context",
        "",
        "- context_source: activity_disposition_profile",
        f"- activity: {profile.name}",
        f"- headless_eligibility: {profile.headless_eligibility}",
    ]
    lines.extend(_format_history_state(profile.history_state))
    lines.extend(_format_direction(profile.direction))
    return "\n".join(lines)


def _render_startup_briefing_live_query(profile: ActivityProfile) -> str:
    """Express the startup briefing as a named live-query route, not an inline payload.

    S6: the marker render path must not import or execute the startup service.
    The operator receives a route to the briefing; the briefing is computed on
    demand by the packet composer's live-query mechanism.
    """
    return "\n".join(
        [
            "### Session Startup Briefing",
            "",
            "- delivery: live_query_descriptor",
            "- reason: computed on demand; not inlined on the marker render path",
            f"- activity: {profile.name}",
            "- route: `gt session envelope packet --kind activity`",
        ]
    )


def _render_open_operator_context(result: dict[str, object]) -> str:
    if result.get("action") != "open":
        return ""
    profile = _activity_profile_for_operator_context(result)
    if profile is None:
        return "\n".join(
            [
                "## Open Activity Operator Context",
                "",
                "- status: unavailable",
                "- reason: activity disposition profile unavailable",
            ]
        )
    sections = [_render_activity_stance_operator_context(profile)]
    if _uses_startup_briefing(profile):
        sections.append(_render_startup_briefing_live_query(profile))
    return "\n\n".join(sections)


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
    topic_type = result.get("topic_type")
    # Bare ``::close`` (single-active) carries no topic_type; echo the command
    # without the ``None`` literal and report the closed topic as "current".
    command_echo = f"::{result['action']} {topic_type}" if topic_type else f"::{result['action']}"
    base = "\n".join(
        [
            "# GroundTruth-KB Topic Envelope Command",
            "",
            f"`{command_echo}` accepted.",
            f"- action: {result['action']}",
            f"- topic_type: {topic_type if topic_type else 'current'}",
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
