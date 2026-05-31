# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
# All rights reserved.
"""Core application specification intake primitives."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from groundtruth_kb.db import KnowledgeDB

CompletionSource = Literal["owner_stated", "not_applicable"]


@dataclass(frozen=True)
class CoreSpecSlot:
    """One required core application specification slot."""

    name: str
    label: str
    prompt: str


BASELINE_SLOTS: tuple[CoreSpecSlot, ...] = (
    CoreSpecSlot(
        "product_identity",
        "Product identity",
        "What product or application are we building, and what should it be called?",
    ),
    CoreSpecSlot("application_type", "Application type", "What kind of application is it?"),
    CoreSpecSlot("tenancy", "Tenancy", "Who owns, hosts, and uses each deployment instance?"),
    CoreSpecSlot("users_roles", "Users and roles", "Who are the user roles and what can each role do?"),
    CoreSpecSlot(
        "data_classification", "Data classification", "What data classes will the application store or process?"
    ),
    CoreSpecSlot("compliance", "Compliance", "Which compliance, audit, or policy obligations apply?"),
    CoreSpecSlot("security_posture", "Security posture", "What authentication, authorization, and threat model apply?"),
    CoreSpecSlot(
        "reliability_posture", "Reliability posture", "What availability, durability, and recovery expectations apply?"
    ),
    CoreSpecSlot(
        "external_integrations", "External integrations", "Which external services, APIs, or systems are in scope?"
    ),
    CoreSpecSlot("ai_usage", "AI usage", "How, if at all, will AI models or AI assistance be used?"),
    CoreSpecSlot(
        "operational_release_path",
        "Operational and release path",
        "How will the application be built, tested, released, deployed, and operated?",
    ),
    CoreSpecSlot(
        "first_release_non_goals", "First-release non-goals", "What is explicitly out of scope for the first release?"
    ),
)

_VALID_SOURCES: set[str] = {"owner_stated", "not_applicable"}
_INTAKE_TAG = "core-spec-intake"
_ENROLLMENT_NOTES_KEY = "core_spec_intake_enabled"


def slot_names() -> tuple[str, ...]:
    """Return required slot names in baseline prompt order."""
    return tuple(slot.name for slot in BASELINE_SLOTS)


def project_id_for_name(project_name: str) -> str:
    """Return the MemBase project id used for a scaffolded adopter project."""
    return f"PROJECT-{_stable_slug(project_name)}"


def slot_spec_id(project_id: str, slot: str) -> str:
    """Return the stable MemBase spec id for a project/slot completion row."""
    return f"SPEC-CORE-INTAKE-{_stable_slug(project_id)}-{_stable_slug(slot)}"


def next_missing_slot(db: KnowledgeDB, project_id: str) -> str | None:
    """Return the next unanswered required slot in baseline order."""
    for slot in BASELINE_SLOTS:
        if _slot_completion(db, project_id, slot.name) is None:
            return slot.name
    return None


def mark_slot_complete(
    db: KnowledgeDB,
    project_id: str,
    slot: str,
    value: str,
    source: CompletionSource = "owner_stated",
) -> dict[str, object] | None:
    """Persist a completed core-spec slot as MemBase-backed evidence."""
    slot_def = _slot_for_name(slot)
    source_value = str(source)
    if source_value not in _VALID_SOURCES:
        raise ValueError(f"source must be one of {sorted(_VALID_SOURCES)}")
    if source_value == "owner_stated" and not value.strip():
        raise ValueError("owner_stated slot completions require a non-empty value")

    spec_id = slot_spec_id(project_id, slot_def.name)
    title = f"Core spec intake: {slot_def.label}"
    description = _slot_description(project_id, slot_def, value, source_value)
    tags = [_INTAKE_TAG, f"project:{project_id}", f"slot:{slot_def.name}", f"source:{source_value}"]
    current = db.get_spec(spec_id)
    if current is None:
        return db.insert_spec(
            id=spec_id,
            title=title,
            status="specified",
            changed_by="core-spec-intake",
            change_reason=f"Mark core spec intake slot {slot_def.name} complete",
            description=description,
            priority="P1",
            scope=project_id,
            section="Core Spec Intake",
            handle=f"core-spec-intake:{project_id}:{slot_def.name}",
            tags=tags,
            type="requirement",
            authority="stated",
            testability="observable",
        )
    return db.update_spec(
        id=spec_id,
        changed_by="core-spec-intake",
        change_reason=f"Update core spec intake slot {slot_def.name} completion",
        title=title,
        description=description,
        priority="P1",
        scope=project_id,
        section="Core Spec Intake",
        handle=f"core-spec-intake:{project_id}:{slot_def.name}",
        tags=tags,
        status="specified",
        type="requirement",
        authority="stated",
        testability="observable",
    )


def is_complete(db: KnowledgeDB, project_id: str) -> bool:
    """Return True when every required slot has persisted completion evidence."""
    return next_missing_slot(db, project_id) is None


def enroll_project_for_intake(db: KnowledgeDB, project_name: str) -> str:
    """Create or update the adopter project record with intake enabled."""
    project_id = project_id_for_name(project_name)
    current = db.get_project(project_id)
    notes = _enabled_notes(current.get("notes") if current else None)
    if current is None:
        db.insert_project(
            name=project_name,
            id=project_id,
            status="active",
            purpose="Adopter application core specification intake",
            target_outcome="Core application specification baseline captured",
            notes=notes,
            changed_by="core-spec-intake",
            change_reason="Enable core spec intake for new scaffolded project",
        )
    else:
        db.insert_project(
            name=current["name"],
            id=project_id,
            status=current["status"],
            rank=current.get("rank"),
            parent_project_id=current.get("parent_project_id"),
            purpose=current.get("purpose"),
            target_outcome=current.get("target_outcome"),
            scope_note=current.get("scope_note"),
            start_date=current.get("start_date"),
            target_date=current.get("target_date"),
            completed_at=current.get("completed_at"),
            notes=notes,
            source_project_name=current.get("source_project_name"),
            source_subproject_name=current.get("source_subproject_name"),
            changed_by="core-spec-intake",
            change_reason="Enable core spec intake for new scaffolded project",
        )
    return project_id


def render_initial_prompt(slot: str) -> str:
    """Render the first owner-visible prompt block for ``MEMORY.md``."""
    slot_def = _slot_for_name(slot)
    return (
        "\n## Pending Core Spec Intake\n\n"
        f"- Next slot: {slot_def.label} (`{slot_def.name}`)\n"
        f"- Prompt: {slot_def.prompt}\n"
        "- Completion: record the answer with owner_stated provenance, or mark the slot not_applicable.\n"
    )


def append_initial_prompt(memory_path: Path, slot: str) -> None:
    """Append the initial pending core-spec prompt to ``MEMORY.md`` once."""
    content = memory_path.read_text(encoding="utf-8")
    if "## Pending Core Spec Intake" in content:
        return
    if content and not content.endswith("\n"):
        content += "\n"
    memory_path.write_text(content + render_initial_prompt(slot), encoding="utf-8")


def _slot_completion(db: KnowledgeDB, project_id: str, slot: str) -> dict[str, object] | None:
    spec = db.get_spec(slot_spec_id(project_id, slot))
    if spec is None or spec.get("status") == "retired":
        return None
    tags = set(spec.get("tags_parsed") or [])
    if _INTAKE_TAG not in tags:
        return None
    if f"project:{project_id}" not in tags or f"slot:{slot}" not in tags:
        return None
    if not any(f"source:{source}" in tags for source in _VALID_SOURCES):
        return None
    return spec


def _slot_for_name(name: str) -> CoreSpecSlot:
    for slot in BASELINE_SLOTS:
        if slot.name == name:
            return slot
    raise ValueError(f"Unknown core spec intake slot: {name}")


def _slot_description(project_id: str, slot: CoreSpecSlot, value: str, source: str) -> str:
    normalized = value.strip() if value.strip() else "Not applicable."
    return f"Project: {project_id}\nSlot: {slot.name}\nSource: {source}\n\n{normalized}"


def _enabled_notes(existing: str | None) -> str:
    payload: dict[str, object]
    if existing:
        try:
            parsed = json.loads(existing)
            payload = parsed if isinstance(parsed, dict) else {"previous_notes": existing}
        except json.JSONDecodeError:
            payload = {"previous_notes": existing}
    else:
        payload = {}
    payload[_ENROLLMENT_NOTES_KEY] = True
    return json.dumps(payload, sort_keys=True)


def _stable_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.upper()).strip("-")
    return slug or "UNNAMED"
