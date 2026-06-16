"""Bridge work-lane classifier - bridge scheduler Slice 5 (WI-3376).

Standalone, stdlib-only, pure-function module. It classifies a bridge entry
into one of four work lanes and maps each lane to a concurrency profile. The
bridge scheduler integration slice consumes it to pick a per-lane parallelism
policy on top of the Slice 4 per-role dispatch limit.

The module performs no filesystem access, holds no runtime state, imports no
dispatch code, and ``classify_lane`` never raises. The integration slice is
responsible for parsing a bridge thread into a ``LaneClassificationInput``;
this module only consumes that parsed context.

Implements WI-3376 per bridge/gtkb-bridge-scheduler-lanes-leases-slice-5-003.md
(Loyal Opposition GO at -004).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Work lanes --------------------------------------------------------------

LANE_REVIEW = "review"
LANE_IMPLEMENTATION = "implementation"
LANE_VERIFICATION = "verification"
LANE_GOVERNANCE = "governance"

CANONICAL_LANES = frozenset({LANE_REVIEW, LANE_IMPLEMENTATION, LANE_VERIFICATION, LANE_GOVERNANCE})

# --- Normalized bridge-kind vocabulary ---------------------------------------
# Real bridge files use many bridge_kind spellings (inventoried by the -002
# NO-GO review). ``_normalize_kind`` lowercases, strips, and unifies hyphen and
# underscore spelling, so each set below holds one canonical form per kind
# (e.g. the hyphenated ``post-implementation-report`` normalizes into
# ``post_implementation_report``).

PROPOSAL_KINDS = frozenset(
    {
        "implementation_proposal",
        "prime_implementation_proposal",
        "prime_builder_implementation_proposal",
    }
)

REPORT_KINDS = frozenset(
    {
        "implementation_report",
        "post_implementation_report",
        "post_implementation",
        "prime_implementation_report",
        "prime_builder_implementation_report",
    }
)

# VERDICT_KINDS is the recognized Loyal Opposition verdict vocabulary. A bridge
# entry whose top file is a verdict is lane-routed by its INDEX status
# (GO / NO-GO / VERIFIED), not by verdict-kind membership - see classify_lane
# step 2 - so this set is exported for completeness and downstream use.
VERDICT_KINDS = frozenset(
    {
        "loyal_opposition_verdict",
        "loyal_opposition_review",
        "verification_verdict",
        "proposal_review_verdict",
        "review_verdict",
    }
)

ADVISORY_KINDS = frozenset({"loyal_opposition_advisory"})

# Substrings that mark a bridge_kind value as formal-artifact / governance work.
_GOVERNANCE_KIND_SIGNALS = ("governance", "formal_artifact")


# --- Context object ----------------------------------------------------------


@dataclass(frozen=True)
class LaneClassificationInput:
    """Pure context for classifying one bridge entry into a work lane.

    The bridge scheduler integration slice populates this from a parsed bridge
    thread. This module does not parse bridge files; it consumes the context.

    Fields:
        latest_status: latest bridge lifecycle status (NEW / REVISED / GO / NO-GO /
            VERIFIED), or None if unknown.
        current_bridge_kind: bridge_kind header of the entry's current top
            file, or None.
        effective_prime_bridge_kind: bridge_kind of the latest Prime-authored
            NEW/REVISED version of the thread, or None. When the top file is a
            Loyal Opposition verdict, this carries the underlying Prime kind.
        mutates_membase: the work performs a MemBase write.
        formal_artifact_mutation: the work creates or versions a formal
            artifact (GOV / ADR / DCL / PB / SPEC / REQ / Deliberation Archive).
        owner_decision_sensitive: the work depends on an owner decision.
        explicit_batch_safe: the operation is explicitly declared batch-safe,
            which releases governance-class work from forced serialization.
        target_paths: optional authorized implementation paths.
        spec_links: optional cited specification ids.
    """

    latest_status: str | None = None
    current_bridge_kind: str | None = None
    effective_prime_bridge_kind: str | None = None
    mutates_membase: bool = False
    formal_artifact_mutation: bool = False
    owner_decision_sensitive: bool = False
    explicit_batch_safe: bool = False
    target_paths: tuple[str, ...] = ()
    spec_links: tuple[str, ...] = ()


# --- Normalization helpers ---------------------------------------------------


def _normalize_kind(kind: object) -> str:
    """Return a lowercased, hyphen-unified bridge_kind, or '' for bad input."""
    if not isinstance(kind, str):
        return ""
    return kind.strip().lower().replace("-", "_")


def _normalize_status(status: object) -> str:
    """Return an uppercased bridge status, or '' for bad input."""
    if not isinstance(status, str):
        return ""
    return status.strip().upper()


def _kind_has_governance_signal(normalized_kind: str) -> bool:
    """Return True when a normalized bridge_kind carries a governance signal."""
    return any(signal in normalized_kind for signal in _GOVERNANCE_KIND_SIGNALS)


# --- Classification ----------------------------------------------------------


def is_terminal(ctx: LaneClassificationInput) -> bool:
    """Return True when the entry is terminal (latest status VERIFIED).

    A terminal entry has no actionable bridge work. ``classify_lane`` still
    returns a lane for it (LANE_REVIEW) for completeness, but callers MUST keep
    the upstream actionability filter: a terminal entry is not dispatchable
    merely because it can be assigned a lane.
    """
    return _normalize_status(ctx.latest_status) == "VERIFIED"


def classify_lane(ctx: LaneClassificationInput) -> str:
    """Classify a bridge entry into one of CANONICAL_LANES. Pure; never raises.

    Order of resolution:
      1. Governance override - governance-class content (a formal-artifact
         mutation, owner-decision-sensitive work, or a MemBase write) routes to
         LANE_GOVERNANCE unless the operation is explicitly batch-safe; a
         loyal_opposition_advisory entry also routes to LANE_GOVERNANCE.
      2. Status-primary - a VERIFIED entry is terminal (LANE_REVIEW); a GO or
         NO-GO entry routes to LANE_IMPLEMENTATION (the pending work is Prime
         Builder), regardless of the top verdict file's own bridge_kind.
      3. Effective-kind - for NEW / REVISED / unknown status, the lane is
         resolved from effective_prime_bridge_kind (preferred) or
         current_bridge_kind: a report kind -> LANE_VERIFICATION, a proposal
         kind -> LANE_REVIEW, a governance-signal kind -> LANE_GOVERNANCE.
      4. Fail-soft default - LANE_REVIEW (the most conservative lane).
    """
    # 1. Governance override.
    if (
        ctx.formal_artifact_mutation or ctx.owner_decision_sensitive or ctx.mutates_membase
    ) and not ctx.explicit_batch_safe:
        return LANE_GOVERNANCE
    current_kind = _normalize_kind(ctx.current_bridge_kind)
    if current_kind in ADVISORY_KINDS:
        return LANE_GOVERNANCE

    # 2. Status-primary.
    status = _normalize_status(ctx.latest_status)
    if status == "VERIFIED":
        return LANE_REVIEW
    if status in ("GO", "NO-GO"):
        return LANE_IMPLEMENTATION

    # 3. Effective-kind (NEW / REVISED / unknown status).
    kind = _normalize_kind(ctx.effective_prime_bridge_kind) or current_kind
    if kind in REPORT_KINDS:
        return LANE_VERIFICATION
    if kind in PROPOSAL_KINDS:
        return LANE_REVIEW
    if kind and _kind_has_governance_signal(kind):
        return LANE_GOVERNANCE

    # 4. Fail-soft default.
    return LANE_REVIEW


# --- Concurrency profiles ----------------------------------------------------

_LANE_PROFILES: dict[str, dict[str, object]] = {
    LANE_VERIFICATION: {
        "parallelism": "aggressive",
        "max_concurrency": None,
        "verdict_writes_serialized": True,
    },
    LANE_REVIEW: {
        "parallelism": "moderate",
        "max_concurrency": None,
        "verdict_writes_serialized": True,
    },
    LANE_IMPLEMENTATION: {
        "parallelism": "limited",
        "max_concurrency": None,
        "verdict_writes_serialized": True,
    },
    LANE_GOVERNANCE: {
        "parallelism": "serialized",
        "max_concurrency": 1,
        "verdict_writes_serialized": True,
    },
}


def lane_concurrency_profile(lane: str) -> dict[str, object]:
    """Return the concurrency profile for a work lane.

    The returned dict carries ``lane``, ``parallelism``, ``max_concurrency``,
    and ``verdict_writes_serialized``. Raises ValueError for an unknown lane.
    """
    if lane not in _LANE_PROFILES:
        raise ValueError(f"unknown work lane: {lane!r}")
    profile: dict[str, object] = {"lane": lane}
    profile.update(_LANE_PROFILES[lane])
    return profile
