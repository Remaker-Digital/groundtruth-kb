# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""BridgeKind taxonomy definitions."""

from enum import StrEnum


class BridgeKind(StrEnum):
    PRIME_PROPOSAL = "prime_proposal"
    LO_VERDICT = "lo_verdict"
    IMPLEMENTATION_REPORT = "implementation_report"
    GOVERNANCE_ADVISORY = "governance_advisory"
    INDEX_RECONCILIATION = "index_reconciliation"
    OPERATIONAL_STATE_CHANGE = "operational_state_change"
