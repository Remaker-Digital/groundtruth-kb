"""Operating-mode transaction component (Slice 1).

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` and bridge thread
``gtkb-operating-mode-transaction-001``. Provides a deterministic component
for bridge-configuration and operating-mode switch requests with:

- Pre-write validation against authoritative role, bridge, and session-state
  artifacts (``validation``).
- Atomic application of role/topology changes with audit-trail records
  (``transaction``, ``audit``).
- Next-session-effective deferral via a pending-transaction queue
  (``pending``).
- Pure topology derivation from a role map (``derive``).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

from groundtruth_kb.mode_switch.derive import topology_from_role_map
from groundtruth_kb.mode_switch.validation import (
    ValidationResult,
    validate_bridge_artifact,
    validate_bridge_substrate,
    validate_role_artifact,
    validate_session_state_artifact,
)

__all__ = [
    "ValidationResult",
    "topology_from_role_map",
    "validate_bridge_artifact",
    "validate_role_artifact",
    "validate_session_state_artifact",
    "validate_bridge_substrate",
]
