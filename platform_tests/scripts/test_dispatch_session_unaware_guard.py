# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression guard: dispatch substrates remain session/UI-unaware (WI-4858)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DISPATCH_SCRIPTS = (
    REPO_ROOT / "scripts" / "cross_harness_bridge_trigger.py",
    REPO_ROOT / "scripts" / "single_harness_bridge_dispatcher.py",
    REPO_ROOT / "scripts" / "single_harness_bridge_automation.py",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"active_session_heartbeat"),
    re.compile(r"active-\{role\}-session\.lock"),
    re.compile(r"active-[a-z]+-session\.lock"),
    re.compile(r"active_session_suppressed"),
    re.compile(r"check_target_active"),
    re.compile(r"check_counterpart_active"),
    re.compile(r"HEARTBEAT_LOCK_TEMPLATE"),
    re.compile(r"active_session_lock_name"),
    re.compile(r"_foreground_session_active"),
    re.compile(r"GTKB_ACTIVE_SESSION_SANITY_TTL"),
)


def test_dispatch_scripts_contain_no_active_session_awareness() -> None:
    violations: list[str] = []
    for path in DISPATCH_SCRIPTS:
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                violations.append(f"{path.relative_to(REPO_ROOT)}:{line_no}: {match.group()}")
    assert not violations, "Active-session awareness found in dispatch code:\n" + "\n".join(violations)
