# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Governance hook runtime utilities."""

from groundtruth_kb.governance.approval_packet import (
    ValidationResult,
    construct_approval_packet,
    validate_packet,
)

__all__ = ["ValidationResult", "construct_approval_packet", "validate_packet"]
