"""Regression guard for the focus-menu role-awareness (Slice 5; verify-only).

bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-001.md
(Codex GO at -002).

Slice 5 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE is verification-only:
the behavior it was scoped to deliver - the session focus menu following the
resolved session role - is already delivered by Slice 1's dual-cache plus the
existing role branch in scripts/session_self_initialization.py. This module
locks in that role-branching so it cannot silently regress.

Governing specs:
- ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 1: full session override
  includes the focus menu.
- DCL-SESSION-ROLE-RESOLUTION-001: the focus menu follows the resolved role.

The key contract: a Loyal Opposition session SUPPRESSES the numbered Prime
Builder session-focus menu (it is a Prime Builder startup control), per
session_self_initialization._render_loyal_opposition_startup_task. A Prime
Builder session shows it.

These are pure-function assertions over a minimal model dict, so the test stays
fast and non-flaky (no heavy build_startup_model render path - the Slice 1
flaky-test lesson).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.session_self_initialization as ssi  # noqa: E402

_FOCUS_SUPPRESSION_LINE = "Session-focus menu: not presented in Loyal Opposition mode"

# Minimal model accepted by _render_loyal_opposition_startup_task: it embeds a
# file-bridge scan that reads model["metrics"]["contention"]. An empty
# contention dict yields the "0 latest NEW/REVISED" branch. Keeping the model
# minimal avoids the heavy build_startup_model render path (Slice 1 flaky-test
# lesson).
_MIN_MODEL = {"metrics": {"contention": {}}}


def test_is_loyal_opposition_model_discriminates() -> None:
    """The role discriminator selects LO rendering only for an LO model."""
    assert ssi._is_loyal_opposition_model({"role": {"assumed_role": "Loyal Opposition"}}) is True
    assert ssi._is_loyal_opposition_model({"role": {"assumed_role": "Prime Builder"}}) is False
    # Absent / empty role -> not LO (defaults to the Prime-side rendering).
    assert ssi._is_loyal_opposition_model({}) is False
    assert ssi._is_loyal_opposition_model({"role": {}}) is False


def test_lo_startup_task_suppresses_focus_menu() -> None:
    """In Loyal Opposition mode the numbered Prime focus menu is suppressed.

    This is the literal focus-menu role-awareness contract: the LO startup task
    declares the session-focus menu is not presented in LO mode.
    """
    task = ssi._render_loyal_opposition_startup_task(_MIN_MODEL)
    assert _FOCUS_SUPPRESSION_LINE in task


def test_pb_and_lo_role_rendering_differs() -> None:
    """The LO role rendering is non-empty role-specific content.

    The LO startup task is the role-specific block that the -lo startup cache
    carries and the -pb cache does not; its presence is what makes the rendered
    disclosure (and its focus-menu treatment) role-aware. It must not contain the
    Prime-only numbered focus menu invitation.
    """
    task = ssi._render_loyal_opposition_startup_task(_MIN_MODEL)
    assert task.strip()
    assert "Loyal Opposition" in task
    # The LO task explicitly frames the numbered focus menu as a Prime control,
    # so it must not invite the owner to pick a numbered focus option as PB would.
    assert "Reply with A, B, C" not in task
