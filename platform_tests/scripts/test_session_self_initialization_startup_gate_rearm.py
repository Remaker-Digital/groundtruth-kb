# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-5083 regression: the SessionStart startup-input gate must not re-arm on a
mid-session continuation (resume/compact).

Root cause (verified): session_start_dispatch_core.main() invoked the startup
service on EVERY SessionStart -- including mid-session compaction/resume
re-fires -- and the arm's idempotency check was defeated by a fresh-timestamp
guard_id, so `discard_next_user_prompt` was re-armed mid-session. The gate is
cleared only by a subsequent UserPromptSubmit, so a re-arm followed by a tool
call or AUQ answer left the gate armed and blocked tool use.

Spec linkage: GOV-RELIABILITY-FAST-LANE-001; PB-SESSION-STARTUP-GOVERNANCE-
DISCLOSURE-001; DCL-SESSION-STARTUP-TOKEN-BUDGET-001.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_self_initialization.py"


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("session_self_initialization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_self_initialization"] = module
    spec.loader.exec_module(module)
    return module


def test_is_session_continuation_source_classifies_resume_and_compact():
    m = _load_module()
    assert m._is_session_continuation_source("resume") is True
    assert m._is_session_continuation_source("compact") is True
    assert m._is_session_continuation_source("Resume") is True  # case-insensitive
    assert m._is_session_continuation_source(" compact ") is True  # trimmed
    assert m._is_session_continuation_source("startup") is False
    assert m._is_session_continuation_source("clear") is False
    assert m._is_session_continuation_source("") is False
    assert m._is_session_continuation_source(None) is False


def _consumed_session_state() -> dict:
    """Guard state for an active session that already consumed its fresh-start
    gate (a normal prompt passed through)."""
    return {
        "discard_next_user_prompt": False,
        "startup_prompt_discarded": False,
        "startup_response_pending": False,
        "startup_gate_no_match_passed_through": True,
        "startup_guard_id": "prior-fresh-start",
        "armed_source": "startup",
    }


def test_continuation_source_does_not_rearm_active_gate(tmp_path):
    """The headline regression: a mid-session resume must NOT re-arm the gate."""
    m = _load_module()
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(json.dumps(_consumed_session_state()) + "\n", encoding="utf-8")

    armed = m._maybe_arm_startup_interaction_guard(
        guard_path,
        "mid-session-refire",
        suppress_next_wrapup=True,
        current_subject="gtkb_infrastructure",
        session_start_source="resume",
    )

    assert armed is False
    state = json.loads(guard_path.read_text(encoding="utf-8"))
    # Pre-fix, the re-arm would have flipped this True and blocked tool use.
    assert state["discard_next_user_prompt"] is False
    assert state["startup_gate_no_match_passed_through"] is True


def test_compact_source_does_not_rearm_active_gate(tmp_path):
    m = _load_module()
    guard_path = tmp_path / "guard.json"
    guard_path.write_text(json.dumps(_consumed_session_state()) + "\n", encoding="utf-8")

    armed = m._maybe_arm_startup_interaction_guard(
        guard_path, "mid-session-refire", suppress_next_wrapup=True, session_start_source="compact"
    )

    assert armed is False
    assert json.loads(guard_path.read_text(encoding="utf-8"))["discard_next_user_prompt"] is False


def test_fresh_source_arms_gate_and_records_armed_source(tmp_path):
    m = _load_module()
    guard_path = tmp_path / "guard.json"

    armed = m._maybe_arm_startup_interaction_guard(
        guard_path, "fresh-start", suppress_next_wrapup=True, session_start_source="startup"
    )

    assert armed is True
    state = json.loads(guard_path.read_text(encoding="utf-8"))
    assert state["discard_next_user_prompt"] is True
    assert state["armed_source"] == "startup"


def test_absent_source_arms_gate_default_armed_source(tmp_path):
    m = _load_module()
    guard_path = tmp_path / "guard.json"

    armed = m._maybe_arm_startup_interaction_guard(
        guard_path, "fresh-start", suppress_next_wrapup=False, session_start_source=None
    )

    assert armed is True
    assert json.loads(guard_path.read_text(encoding="utf-8"))["armed_source"] == "startup"
