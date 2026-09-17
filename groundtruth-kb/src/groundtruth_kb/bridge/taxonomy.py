# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""BridgeKind taxonomy definitions."""

from enum import StrEnum


class BridgeKind(StrEnum):
    IMPLEMENTATION_PROPOSAL = "implementation_proposal"
    LO_VERDICT = "lo_verdict"
    IMPLEMENTATION_REPORT = "implementation_report"
    GOVERNANCE_REVIEW = "governance_review"
    GOVERNANCE_ADVISORY = "governance_advisory"
    OPERATIONAL_STATE_CHANGE = "operational_state_change"


# The status determines the message kind; neither field grants effect authority.
BRIDGE_KIND_BY_STATUS: dict[str, BridgeKind] = {
    "NEW": BridgeKind.IMPLEMENTATION_PROPOSAL,
    "REVISED": BridgeKind.IMPLEMENTATION_PROPOSAL,
    "GO": BridgeKind.LO_VERDICT,
    "NO-GO": BridgeKind.LO_VERDICT,
    "NOT-READY": BridgeKind.LO_VERDICT,
    "VERIFIED": BridgeKind.LO_VERDICT,
    "SUPERSEDED": BridgeKind.LO_VERDICT,
    "READY": BridgeKind.IMPLEMENTATION_REPORT,
    "ADVISORY": BridgeKind.GOVERNANCE_ADVISORY,
    "VERDICT-REJECTED": BridgeKind.GOVERNANCE_REVIEW,
    "BLOCKED": BridgeKind.OPERATIONAL_STATE_CHANGE,
    "WITHDRAWN": BridgeKind.OPERATIONAL_STATE_CHANGE,
}
