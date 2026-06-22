# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared bridge dispatch role-state constants."""

from __future__ import annotations

ROLE_STATE_KEYS: tuple[str, str] = ("prime-builder", "loyal-opposition")
BRIDGE_AGENT_TO_RECIPIENT: dict[str, str] = {
    "claude": "prime-builder",
    "codex": "loyal-opposition",
}
