# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""BridgeKind taxonomy definitions."""

from enum import StrEnum

from groundtruth_kb.bridge.vocabulary import (
    ADVISORY_STATUSES,
    OPERATIONAL_STATUSES,
    PROPOSAL_STATUSES,
    REPORT_STATUSES,
    REVIEW_STATUSES,
    VERDICT_STATUSES,
)


class BridgeKind(StrEnum):
    IMPLEMENTATION_PROPOSAL = "implementation_proposal"
    LO_VERDICT = "lo_verdict"
    IMPLEMENTATION_REPORT = "implementation_report"
    GOVERNANCE_REVIEW = "governance_review"
    GOVERNANCE_ADVISORY = "governance_advisory"
    OPERATIONAL_STATE_CHANGE = "operational_state_change"


# The status determines the message kind; neither field grants effect authority. The status groups come from the
# vocabulary module (c123, G17), so no status token is written here.
_STATUSES_BY_KIND: dict[BridgeKind, frozenset[str]] = {
    BridgeKind.IMPLEMENTATION_PROPOSAL: PROPOSAL_STATUSES,
    BridgeKind.LO_VERDICT: VERDICT_STATUSES,
    BridgeKind.IMPLEMENTATION_REPORT: REPORT_STATUSES,
    BridgeKind.GOVERNANCE_ADVISORY: ADVISORY_STATUSES,
    BridgeKind.GOVERNANCE_REVIEW: REVIEW_STATUSES,
    BridgeKind.OPERATIONAL_STATE_CHANGE: OPERATIONAL_STATUSES,
}
BRIDGE_KIND_BY_STATUS: dict[str, BridgeKind] = {
    status: kind for kind, statuses in _STATUSES_BY_KIND.items() for status in sorted(statuses)
}
