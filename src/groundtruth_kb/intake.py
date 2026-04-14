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
) -> dict[str, Any]:
    """Capture a requirement candidate as a deliberation.

    Classifies intent and stores the full candidate payload.
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
        changed_by="intake-pipeline",
        change_reason="Requirement captured via intake pipeline",
        participants=["owner"],
    )

    return {"deliberation_id": delib["id"], "content": content}


def confirm_intake(
    db: KnowledgeDB,
    deliberation_id: str,
) -> dict[str, Any]:
    """Confirm an intake candidate — creates a KB spec and records confirmation.

    Returns the created spec, quality score, impact analysis, and constraints.
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
        changed_by="intake-pipeline",
        change_reason=f"Confirmed from intake {deliberation_id}",
        section=content.get("proposed_section"),
        scope=content.get("proposed_scope"),
        type=spec_type,
        authority=authority,
        provisional_until=provisional_until,
    )

    # Score quality
    created_spec = db.get_spec(spec["id"])
    quality = db.score_spec_quality(created_spec) if created_spec else {}

    # Impact analysis
    impact = db.compute_impact("add", created_spec) if created_spec else {}

    # Constraints
    constraints = db.check_constraints_for_spec(spec["id"]) if created_spec else []

    # Update deliberation (new version — append-only)
    content["intake_status"] = "confirmed"
    content["confirmed_spec_id"] = spec["id"]
    content["quality_tier"] = quality.get("tier")
    content["quality_score"] = quality.get("overall")
    db.insert_deliberation(
        id=deliberation_id,
        title=delib.get("title", f"Intake: {content.get('proposed_title', '')}"),
        summary=f"Confirmed → {spec['id']}",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="owner_decision",
        changed_by="intake-pipeline",
        change_reason=f"Intake confirmed, created spec {spec['id']}",
    )

    return {
        "spec": spec,
        "quality": quality,
        "impact": impact,
        "constraints": constraints,
        "confirmed_spec_id": spec["id"],
    }


def reject_intake(
    db: KnowledgeDB,
    deliberation_id: str,
    reason: str,
) -> dict[str, Any]:
    """Reject an intake candidate with a reason."""
    if not reason:
        raise ValueError("Rejection reason is required")

    delib = db.get_deliberation(deliberation_id)
    if delib is None:
        return {"error": f"Deliberation {deliberation_id} not found"}

    raw_content = delib.get("content", "{}")
    try:
        content = json.loads(raw_content) if isinstance(raw_content, str) else raw_content
    except json.JSONDecodeError:
        content = {}

    content["intake_status"] = "rejected"
    content["rejection_reason"] = reason
    db.insert_deliberation(
        id=deliberation_id,
        title=delib.get("title", "Intake"),
        summary=f"Rejected: {reason[:80]}",
        content=json.dumps(content),
        source_type="owner_conversation",
        outcome="no_go",
        changed_by="intake-pipeline",
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
