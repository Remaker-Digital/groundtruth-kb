"""
GroundTruth KB — F5 Requirement Intake Pipeline.

Classifies owner intent, captures requirement candidates as deliberations,
and promotes confirmed candidates to KB specs.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from groundtruth_kb.db import KnowledgeDB

# ---------------------------------------------------------------------------
# Intent classification patterns
# ---------------------------------------------------------------------------

# Exploration markers take precedence over directive markers when present.
_EXPLORATION_PATTERNS = [
    re.compile(r"\b(maybe|perhaps|possibly)\b", re.IGNORECASE),
    re.compile(r"\b(what\s+if|wondering|could\s+we|might\s+we)\b", re.IGNORECASE),
    re.compile(r"\b(consider|explore|brainstorm|hypothetical)\b", re.IGNORECASE),
    re.compile(r"\b(think\s+about|thinking\s+about|just\s+something)\b", re.IGNORECASE),
]

# Constraint markers that override directive when "not" is present.
_CONSTRAINT_PATTERNS = [
    re.compile(r"\b(cannot|must\s+not|shall\s+not|should\s+not|may\s+not)\b", re.IGNORECASE),
    re.compile(r"\b(prohibited|forbidden|disallowed|banned)\b", re.IGNORECASE),
    re.compile(r"\b(limited\s+to|no\s+more\s+than|at\s+most|no\s+less\s+than|at\s+least)\b", re.IGNORECASE),
    re.compile(r"\b(maximum|minimum|cap(?:ped)?\s+at|within|exceed)\b", re.IGNORECASE),
]

_DIRECTIVE_PATTERNS = [
    re.compile(r"\b(must|shall|should)\b", re.IGNORECASE),
    re.compile(r"\b(require[sd]?|need[s]?\s+to|has\s+to|have\s+to)\b", re.IGNORECASE),
    re.compile(r"\b(implement|add|create|build|ensure|enforce|validate)\b", re.IGNORECASE),
    re.compile(r"^\s*\d+[\.\)]\s", re.MULTILINE),  # Numbered criteria
]

_PREFERENCE_PATTERNS = [
    re.compile(r"\b(prefer|would\s+like|it\s+would\s+be\s+nice|ideally)\b", re.IGNORECASE),
    re.compile(r"\b(rather|favor|lean\s+toward|nice\s+to\s+have)\b", re.IGNORECASE),
]

_QUESTION_PATTERNS = [
    re.compile(r"\?"),
    re.compile(r"\b(how\s+do|how\s+does|what\s+is|what\s+are|why\s+does|is\s+there)\b", re.IGNORECASE),
    re.compile(r"\b(can\s+we|could\s+you|would\s+you\s+mind)\b", re.IGNORECASE),
]


def _count_matches(text: str, patterns: list[re.Pattern[str]]) -> int:
    """Count total match occurrences across all patterns in a category."""
    total = 0
    for p in patterns:
        total += len(p.findall(text))
    return total


def _classify_intent(text: str) -> tuple[str, float]:
    """Classify owner intent from text.

    Returns (classification, confidence) where confidence is a float in [0.0, 1.0].

    Precedence rules:
      - Exploration markers ("maybe", "what if") dominate when present, because
        they signal non-commitment even if directive verbs appear.
      - Constraint markers ("must not", "cannot") dominate over directive when
        present, because the negation inverts the directive intent.
      - Question marks dominate over directive when directive count is low.
      - Otherwise, the category with the most pattern matches wins.
    """
    exploration_hits = _count_matches(text, _EXPLORATION_PATTERNS)
    constraint_hits = _count_matches(text, _CONSTRAINT_PATTERNS)
    directive_hits = _count_matches(text, _DIRECTIVE_PATTERNS)
    preference_hits = _count_matches(text, _PREFERENCE_PATTERNS)
    question_hits = _count_matches(text, _QUESTION_PATTERNS)

    # Rule 1: exploration markers dominate
    if exploration_hits >= 1:
        if exploration_hits >= 2:
            return "exploration", 0.4
        return "exploration", 0.3

    # Rule 2: constraint markers dominate over directive
    if constraint_hits >= 1:
        if constraint_hits >= 2:
            return "constraint", 0.9
        return "constraint", 0.7

    # Rule 3: question marks dominate when directive signal is weak
    if question_hits >= 1 and directive_hits <= question_hits:
        if question_hits >= 2:
            return "question", 0.9
        return "question", 0.7

    # Rule 4: directive wins by hit count
    if directive_hits >= 3:
        return "directive", 0.9
    if directive_hits == 2:
        return "directive", 0.85
    if directive_hits == 1:
        return "directive", 0.7

    # Rule 5: preference
    if preference_hits >= 2:
        return "preference", 0.9
    if preference_hits == 1:
        return "preference", 0.7

    # Rule 6: default exploration
    return "exploration", 0.3


def _find_related_specs(db: KnowledgeDB, text: str) -> list[dict[str, Any]]:
    """Find specs related to the text by section/scope/title keyword overlap."""
    words = set(re.findall(r"\b\w{4,}\b", text.lower()))
    if not words:
        return []

    scored: list[tuple[int, dict[str, Any]]] = []
    for spec in db.list_specs():
        score = 0
        for field in ("title", "section", "scope"):
            val = spec.get(field, "") or ""
            field_words = set(re.findall(r"\b\w{4,}\b", val.lower()))
            score += len(words & field_words)
        if score > 0:
            scored.append((score, spec))

    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:5]]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_INTAKE_TYPE = "requirement_candidate"
_now = None  # Lazy import


def _get_now() -> str:
    from groundtruth_kb.db import _now as db_now

    return db_now()


def _stable_work_item_id_for_spec(spec_id: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", spec_id.upper()).strip("-")
    return f"WI-AUTO-{slug}"


def _parsed_json_field(row: dict[str, Any], field: str, default: Any) -> Any:
    parsed = row.get(f"{field}_parsed")
    if parsed is not None:
        return parsed
    raw = row.get(field)
    if isinstance(raw, str) and raw.strip():
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return default
    return default


def _is_implementation_bearing_spec(spec: dict[str, Any]) -> bool:
    constraints = _parsed_json_field(spec, "constraints", {})
    tags = _parsed_json_field(spec, "tags", [])
    if isinstance(constraints, dict) and constraints.get("implementation_bearing") is True:
        return True
    if isinstance(constraints, dict) and constraints.get("implementation_bearing") is False:
        return False
    if isinstance(tags, list) and "implementation-bearing" in tags:
        return True

    spec_type = str(spec.get("type") or "requirement")
    if spec_type in {"architecture_decision", "design_constraint"}:
        return False
    return spec_type in {"requirement", "specification", "functional", "feature", "protected_behavior"}


def _active_work_items_for_spec(db: KnowledgeDB, spec_id: str) -> list[dict[str, Any]]:
    from groundtruth_kb.db import WORK_ITEM_TERMINAL_RESOLUTION_STATUSES

    return [
        item
        for item in db.list_work_items(source_spec_id=spec_id)
        if item.get("resolution_status") not in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES
    ]


def _explicit_project_ids_from_spec(db: KnowledgeDB, spec: dict[str, Any]) -> list[str]:
    project_ids: list[str] = []
    constraints = _parsed_json_field(spec, "constraints", {})
    if isinstance(constraints, dict):
        raw_ids = constraints.get("project_ids")
        if isinstance(raw_ids, list):
            project_ids.extend(str(value).strip() for value in raw_ids if str(value).strip())
        raw_id = constraints.get("project_id")
        if isinstance(raw_id, str) and raw_id.strip():
            project_ids.append(raw_id.strip())

    for link in db.list_project_artifact_links_for_artifact("spec", str(spec["id"])):
        project_id = str(link.get("project_id") or "").strip()
        if project_id:
            project_ids.append(project_id)

    active_ids: list[str] = []
    for project_id in dict.fromkeys(project_ids):
        project = db.get_project(project_id)
        if project and project.get("status") == "active":
            active_ids.append(project_id)
    return active_ids


def ensure_backlog_for_confirmed_spec(
    db: KnowledgeDB,
    spec: dict[str, Any],
    *,
    deliberation_id: str,
    changed_by: str,
) -> dict[str, Any]:
    """Create/link backlog work for one newly confirmed implementation-bearing spec."""
    if spec.get("status") != "specified":
        return {"action": "skipped", "reason": "spec status is not specified", "spec_id": spec.get("id")}
    if not _is_implementation_bearing_spec(spec):
        return {"action": "skipped", "reason": "spec is not implementation-bearing", "spec_id": spec.get("id")}

    active_items = _active_work_items_for_spec(db, str(spec["id"]))
    created = False
    if active_items:
        work_item = active_items[0]
        action = "linked_existing"
    else:
        work_item = db.insert_work_item(
            _stable_work_item_id_for_spec(str(spec["id"])),
            f"Implement {spec['id']}: {spec.get('title', 'Untitled')}",
            "new",
            "implementation_intake",
            "open",
            changed_by,
            f"Automatic backlog intake for confirmed implementation-bearing spec {spec['id']}",
            source_spec_id=str(spec["id"]),
            priority=spec.get("priority"),
            stage="backlogged",
            status_detail="unassigned implementation intake",
            source_deliberation_query=deliberation_id,
            related_deliberation_ids=json.dumps([deliberation_id]),
            related_spec_ids_at_creation=json.dumps([spec["id"]]),
            acceptance_summary=f"Implement and verify the behavior specified by {spec['id']}.",
        )
        if work_item is None:
            raise RuntimeError(f"auto backlog: insert_work_item returned None for {spec['id']}")
        created = True
        action = "created"

    db.link_deliberation_work_item(deliberation_id, str(work_item["id"]), role="auto_backlog")

    project_ids = _explicit_project_ids_from_spec(db, spec)
    attachment: dict[str, Any] = {"action": "unassigned", "reason": "no deterministic project fit"}
    if len(project_ids) == 1:
        membership = db.link_project_work_item(
            project_ids[0],
            str(work_item["id"]),
            changed_by,
            f"Automatic project attachment for confirmed spec {spec['id']}",
            source="spec-auto-backlog",
        )
        attachment = {"action": "attached", "project_id": project_ids[0], "membership": membership}
    elif len(project_ids) > 1:
        attachment = {"action": "unassigned", "reason": "ambiguous deterministic project fit", "project_ids": project_ids}

    return {
        "action": action,
        "created": created,
        "spec_id": spec["id"],
        "work_item": work_item,
        "project_attachment": attachment,
    }


def classify_requirement(
    db: KnowledgeDB,
    text: str,
) -> dict[str, Any]:
    """Classify owner intent and find related specs.

    Returns dict with classification, confidence, related_specs, raw_text.
    """
    classification, confidence = _classify_intent(text)
    related = _find_related_specs(db, text)

    return {
        "classification": classification,
        "confidence": confidence,
        "related_specs": [{"id": s["id"], "title": s["title"]} for s in related],
        "raw_text": text,
    }


def capture_requirement(
    db: KnowledgeDB,
    text: str,
    *,
    proposed_title: str,
    proposed_section: str,
    proposed_scope: str | None = None,
    proposed_type: str = "requirement",
    proposed_authority: str = "stated",
    changed_by: str = "intake-pipeline",
    change_reason: str = "Requirement captured via intake pipeline",
) -> dict[str, Any]:
    """Capture a requirement candidate as a deliberation.

    Classifies intent and stores the full candidate payload.

    The ``changed_by`` and ``change_reason`` keyword-only parameters
    default to the generic intake-pipeline attribution so existing
    callers (CLI, tests) preserve their behavior. Skill callers
    pass a skill-specific ``changed_by`` value to differentiate the
    audit trail (see ``templates/skills/spec-intake``).
    """
    classification, confidence = _classify_intent(text)
    related = _find_related_specs(db, text)

    content = {
        "intake_type": _INTAKE_TYPE,
        "intake_status": "pending",
        "raw_text": text,
        "classification": classification,
        "confidence": confidence,
        "related_specs": [s["id"] for s in related],
        "proposed_title": proposed_title,
        "proposed_section": proposed_section,
        "proposed_scope": proposed_scope,
        "proposed_type": proposed_type,
        "proposed_authority": proposed_authority,
        "captured_at": _get_now(),
        "confirmed_spec_id": None,
        "rejection_reason": None,
    }

    delib_id = f"INTAKE-{uuid.uuid4().hex[:8]}"
    delib = db.insert_deliberation(
        id=delib_id,
        title=f"Intake: {proposed_title}",
        summary=f"Requirement candidate: {classification} (confidence {confidence})",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="deferred",
        changed_by=changed_by,
        change_reason=change_reason,
        participants=["owner"],
    )

    if delib is None:
        raise RuntimeError("intake: insert_deliberation returned None (db bug)")
    return {"deliberation_id": delib["id"], "content": content}


def confirm_intake(
    db: KnowledgeDB,
    deliberation_id: str,
    *,
    changed_by: str = "intake-pipeline",
) -> dict[str, Any]:
    """Confirm an intake candidate — creates a KB spec and records confirmation.

    Returns the created spec, quality score, impact analysis, and constraints.

    The ``changed_by`` keyword-only parameter defaults to the generic
    intake-pipeline attribution so existing callers (CLI, tests)
    preserve their behavior. It is propagated to both the created
    spec and the confirmation deliberation so the skill actor is
    recorded on every governance row this function writes.
    """
    delib = db.get_deliberation(deliberation_id)
    if delib is None:
        return {"error": f"Deliberation {deliberation_id} not found"}

    raw_content = delib.get("content", "{}")
    try:
        content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
    except json.JSONDecodeError:
        content = {}

    if content.get("intake_type") != _INTAKE_TYPE:
        return {"error": "Not an intake candidate"}

    if content.get("intake_status") == "confirmed":
        return {"already_confirmed": True, "confirmed_spec_id": content.get("confirmed_spec_id")}

    # Create the spec
    spec_type = content.get("proposed_type", "requirement")
    authority = content.get("proposed_authority", "stated")
    provisional_until = None
    if authority == "provisional":
        provisional_until = "TBD"

    spec_id = f"SPEC-INTAKE-{uuid.uuid4().hex[:6]}"
    spec = db.insert_spec(
        id=spec_id,
        title=content.get("proposed_title", "Untitled"),
        status="specified",
        changed_by=changed_by,
        change_reason=f"Confirmed from intake {deliberation_id}",
        section=content.get("proposed_section"),
        scope=content.get("proposed_scope"),
        type=spec_type,
        authority=authority,
        provisional_until=provisional_until,
    )

    if spec is None:
        return {"error": "insert_spec returned None", "deliberation_id": deliberation_id}

    # Score quality
    created_spec = db.get_spec(spec["id"])
    quality = db.score_spec_quality(created_spec) if created_spec else {}

    # Impact analysis
    impact = db.compute_impact("add", created_spec) if created_spec else {}

    # Constraints
    constraints = db.check_constraints_for_spec(spec["id"]) if created_spec else []
    if created_spec:
        db.link_deliberation_spec(deliberation_id, spec["id"], role="originating_intake")
        auto_backlog = ensure_backlog_for_confirmed_spec(
            db,
            created_spec,
            deliberation_id=deliberation_id,
            changed_by=changed_by,
        )
    else:
        auto_backlog = {
            "action": "skipped",
            "reason": "confirmed spec could not be loaded",
            "spec_id": spec["id"],
        }

    # Update deliberation (new version — append-only)
    content["intake_status"] = "confirmed"
    content["confirmed_spec_id"] = spec["id"]
    content["quality_tier"] = quality.get("tier")
    content["quality_score"] = quality.get("overall")
    content["auto_backlog"] = auto_backlog
    db.insert_deliberation(
        id=deliberation_id,
        title=delib.get("title", f"Intake: {content.get('proposed_title', '')}"),
        summary=f"Confirmed → {spec['id']}",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="owner_decision",
        changed_by=changed_by,
        change_reason=f"Intake confirmed, created spec {spec['id']}",
    )

    return {
        "spec": spec,
        "quality": quality,
        "impact": impact,
        "constraints": constraints,
        "auto_backlog": auto_backlog,
        "confirmed_spec_id": spec["id"],
    }


def reject_intake(
    db: KnowledgeDB,
    deliberation_id: str,
    reason: str,
    *,
    changed_by: str = "intake-pipeline",
) -> dict[str, Any]:
    """Reject an intake candidate with a reason.

    The ``changed_by`` keyword-only parameter defaults to the generic
    intake-pipeline attribution so existing callers (CLI, tests)
    preserve their behavior. Skill callers pass a skill-specific
    value to differentiate the audit trail.
    """
    if not reason:
        raise ValueError("Rejection reason is required")

    delib = db.get_deliberation(deliberation_id)
    if delib is None:
        return {"error": f"Deliberation {deliberation_id} not found"}

    raw_content = delib.get("content", "{}")
    try:
        content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
    except (json.JSONDecodeError, TypeError):
        content = {}

    if not isinstance(content, dict) or content.get("intake_type") != _INTAKE_TYPE:
        return {"error": "Not an intake candidate"}

    content["intake_status"] = "rejected"
    content["rejection_reason"] = reason
    db.insert_deliberation(
        id=deliberation_id,
        title=delib.get("title", "Intake"),
        summary=f"Rejected: {reason[:80]}",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="no_go",
        changed_by=changed_by,
        change_reason=f"Intake rejected: {reason}",
    )

    return {"deliberation_id": deliberation_id, "rejected": True, "reason": reason}


def list_intakes(
    db: KnowledgeDB,
    *,
    pending_only: bool = False,
) -> list[dict[str, Any]]:
    """List intake candidates, filtering by intake_type discriminator.

    Skips non-intake and malformed deliberations deterministically.
    """
    all_delibs = db.list_deliberations(source_type="owner_conversation")
    result: list[dict[str, Any]] = []

    for d in all_delibs:
        raw = d.get("content", "")
        try:
            content = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(content, dict):
            continue
        if content.get("intake_type") != _INTAKE_TYPE:
            continue

        if pending_only and content.get("intake_status") != "pending":
            continue

        result.append(
            {
                "deliberation_id": d["id"],
                "intake_status": content.get("intake_status"),
                "classification": content.get("classification"),
                "confidence": content.get("confidence"),
                "proposed_title": content.get("proposed_title"),
                "proposed_section": content.get("proposed_section"),
                "confirmed_spec_id": content.get("confirmed_spec_id"),
                "rejection_reason": content.get("rejection_reason"),
            }
        )

    return result
