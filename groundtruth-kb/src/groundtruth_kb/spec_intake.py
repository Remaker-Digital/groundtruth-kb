"""Direct requirement intake: temporary candidates, one explicit canonical write, discard on rejection.

The persisted intake queue (deliberation rows at ``outcome='deferred'`` and ``gt intake list/confirm/reject``)
is retired under O-7 R24. A candidate is a temporary extraction held by the caller, optionally as a JSON file
under the application's runtime directory; it is not a canonical record and grants nothing. Confirmation
writes exactly one specification through the native authority with ``expected_version`` 0 and reads it back;
a second confirmation of the same identity is refused by the authority without changing data. Rejection
discards the candidate and writes nothing; retiring an existing specification is an explicit canonical
amendment, never a rejection side effect.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.governance.credential_patterns import Scope, scan

CANDIDATE_KIND = "requirement-candidate"
CANDIDATE_FIELDS = (
    "kind",
    "candidate_id",
    "raw_text",
    "classification",
    "confidence",
    "proposed_title",
    "proposed_section",
    "proposed_scope",
    "proposed_type",
    "proposed_authority",
    "captured_at",
)
NON_IMPLEMENTATION_TYPES = frozenset({"architecture_decision", "design_constraint", "governance", "protected_behavior"})

# Exploration markers take precedence over directive markers when present.
_EXPLORATION_PATTERNS = [
    re.compile(r"\b(maybe|perhaps|possibly)\b", re.IGNORECASE),
    re.compile(r"\b(what\s+if|wondering|could\s+we|might\s+we)\b", re.IGNORECASE),
    re.compile(r"\b(consider|explore|brainstorm|hypothetical)\b", re.IGNORECASE),
    re.compile(r"\b(think\s+about|thinking\s+about|just\s+something)\b", re.IGNORECASE),
]
# Constraint markers override directive when a negation is present.
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
    re.compile(r"^\s*\d+[\.\)]\s", re.MULTILINE),
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


class IntakeError(ValueError):
    """A candidate or argument is unusable; nothing was written."""


def _count_matches(text: str, patterns: list[re.Pattern[str]]) -> int:
    return sum(len(pattern.findall(text)) for pattern in patterns)


def classify_intent(text: str) -> tuple[str, float]:
    """Classify owner intent; exploration and negated constraints dominate directive verbs."""
    exploration_hits = _count_matches(text, _EXPLORATION_PATTERNS)
    constraint_hits = _count_matches(text, _CONSTRAINT_PATTERNS)
    directive_hits = _count_matches(text, _DIRECTIVE_PATTERNS)
    preference_hits = _count_matches(text, _PREFERENCE_PATTERNS)
    question_hits = _count_matches(text, _QUESTION_PATTERNS)
    if exploration_hits >= 1:
        return "exploration", 0.4 if exploration_hits >= 2 else 0.3
    if constraint_hits >= 1:
        return "constraint", 0.9 if constraint_hits >= 2 else 0.7
    if question_hits >= 1 and directive_hits <= question_hits:
        return "question", 0.9 if question_hits >= 2 else 0.7
    if directive_hits >= 3:
        return "directive", 0.9
    if directive_hits == 2:
        return "directive", 0.85
    if directive_hits == 1:
        return "directive", 0.7
    if preference_hits >= 2:
        return "preference", 0.9
    if preference_hits == 1:
        return "preference", 0.7
    return "exploration", 0.3


def is_implementation_bearing(spec_type: str | None, constraints: Any = None, tags: Any = None) -> bool:
    """Whether a confirmed specification describes implementation work (explicit markers win over type)."""
    if isinstance(constraints, dict) and isinstance(constraints.get("implementation_bearing"), bool):
        return bool(constraints["implementation_bearing"])
    if isinstance(tags, list) and "implementation-bearing" in tags:
        return True
    return (spec_type or "requirement") not in NON_IMPLEMENTATION_TYPES


def sensitive_values(text: str) -> list[str]:
    """Names of credential or PII patterns found in the text; the matched values are never returned."""
    return sorted({match.name for match in scan(text, Scope.DB)})


def capture_candidate(
    text: str,
    *,
    proposed_title: str,
    proposed_section: str,
    proposed_scope: str | None = None,
    proposed_type: str = "requirement",
    proposed_authority: str = "stated",
    candidate_dir: Path | None = None,
) -> dict[str, Any]:
    """Extract a temporary candidate; nothing canonical is read or written."""
    if not text.strip() or not proposed_title.strip() or not proposed_section.strip():
        raise IntakeError("A candidate needs the owner's text, a title and a section")
    if proposed_authority not in {"stated", "provisional", "derived"}:
        raise IntakeError("proposed_authority must be stated, provisional or derived")
    classification, confidence = classify_intent(text)
    candidate = {
        "kind": CANDIDATE_KIND,
        "candidate_id": f"CAND-{uuid.uuid4().hex[:12]}",
        "raw_text": text,
        "classification": classification,
        "confidence": confidence,
        # Credential- or PII-shaped values are named (never echoed) so the owner rewords before confirmation.
        "sensitive": sensitive_values(text),
        "proposed_title": proposed_title,
        "proposed_section": proposed_section,
        "proposed_scope": proposed_scope,
        "proposed_type": proposed_type,
        "proposed_authority": proposed_authority,
        "captured_at": datetime.now(UTC).isoformat(),
        "path": None,
    }
    if candidate_dir is not None:
        candidate_dir.mkdir(parents=True, exist_ok=True)
        path = candidate_dir / f"{candidate['candidate_id']}.json"
        candidate["path"] = str(path)
        path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    return candidate


def load_candidate(path: Path) -> dict[str, Any]:
    """Read a temporary candidate file; anything else is refused."""
    try:
        candidate = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise IntakeError(f"Unreadable candidate file: {path}") from error
    return validate_candidate(candidate)


def validate_candidate(candidate: Any) -> dict[str, Any]:
    """Refuse anything that is not a candidate from this module before any canonical effect."""
    if not isinstance(candidate, dict) or candidate.get("kind") != CANDIDATE_KIND:
        raise IntakeError("Not an intake candidate")
    missing = [field for field in CANDIDATE_FIELDS if field not in candidate]
    if missing or not str(candidate["raw_text"]).strip() or not str(candidate["proposed_title"]).strip():
        raise IntakeError("Malformed intake candidate: " + (", ".join(missing) or "empty text or title"))
    return candidate


def confirm_candidate(
    client: AuthorityClient,
    candidate: dict[str, Any],
    *,
    actor: str,
    spec_id: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Write exactly one new specification from the candidate and read it back; refuse an existing identity."""
    validate_candidate(candidate)
    if not actor.strip():
        raise IntakeError("Confirmation requires an actor")
    sensitive = sensitive_values(str(candidate["raw_text"]))
    if sensitive:
        # A canonical record never stores a credential or PII value; the legacy archive redacted, this path refuses.
        raise IntakeError(
            "Candidate text contains credential- or PII-shaped values ("
            + ", ".join(sensitive)
            + "); reword it before confirming"
        )
    identity = spec_id or f"SPEC-INTAKE-{candidate['candidate_id'].removeprefix('CAND-')[:8]}"
    fields = {
        "title": candidate["proposed_title"],
        "description": candidate["raw_text"],
        "status": "active",
        "type": candidate["proposed_type"],
        "section": candidate["proposed_section"],
        "scope": candidate["proposed_scope"],
        "authority": candidate["proposed_authority"],
    }
    body = {
        "expected_version": 0,
        "actor": actor,
        "reason": reason or f"Confirmed from intake candidate {candidate['candidate_id']}",
        "fields": {key: value for key, value in fields.items() if value is not None},
    }
    written = client.request("PUT", f"/v1/specifications/{identity}", body=body)
    record = client.request("GET", f"/v1/specifications/{identity}")
    if record != written or record["version"] != 1:
        raise IntakeError(f"Readback of {identity} differs from the written record")
    path = candidate.get("path")
    if path and Path(path).is_file():
        Path(path).unlink()
    return {
        "confirmed_spec_id": identity,
        "spec": record,
        "implementation_bearing": is_implementation_bearing(
            record.get("type"), record.get("constraints"), record.get("tags")
        ),
        "backlog": {
            "created": False,
            "reason": (
                "Implementation work requires a specification and an executable test in an active plan phase; "
                "record it with `gt backlog record` when the test exists."
            ),
        },
        "canonical_writes": 1,
    }


def reject_candidate(candidate: dict[str, Any], reason: str) -> dict[str, Any]:
    """Discard a candidate with a reason; no canonical record is read or written."""
    validate_candidate(candidate)
    if not reason or not reason.strip():
        raise IntakeError("Rejection requires a reason")
    path = candidate.get("path")
    discarded = False
    if path and Path(path).is_file():
        Path(path).unlink()
        discarded = True
    return {
        "rejected": True,
        "candidate_id": candidate["candidate_id"],
        "reason": reason.strip(),
        "discarded_file": discarded,
        "canonical_writes": 0,
    }
