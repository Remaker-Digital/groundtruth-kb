# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression lock for Slice E — Loyal Opposition startup text + authority.

GTKB-STARTUP-REFRACTOR-001 Slice E (WI-4273), advisory findings F5 + F6.

Both findings were already resolved in the live code when the slice landed:
- F6: the startup generator's fresh-session input semantics are role-conditional
  (the Loyal Opposition branch does not reference Prime-Builder session-focus
  choices).
- F5: the Loyal Opposition startup task auto-processes the actionable bridge
  queue by default (``ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001``),
  with advisory mode as the opt-in that asks — mirrored in ``AGENTS.md``.

Per Codex verdict ``-004`` (NO-GO F1), this test pins the behavior at the
**render** level: it calls the generator's rendering functions with a Loyal
Opposition model and a Prime Builder model and asserts on the rendered output,
rather than searching source text (a source-string check could pass while the
rendered Loyal Opposition disclosure regresses).

Owner decision (2026-06-03 AUQ): Loyal Opposition processes the actionable queue
without asking; advisory mode is the opt-in that asks.

Authority: ``bridge/gtkb-startup-refractor-slice-e-lo-startup-text-authority-002.md``
(GO); ``GOV-SESSION-SELF-INITIALIZATION-001``; ``GOV-SESSION-ROLE-AUTHORITY-001``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts import session_self_initialization as ssi  # noqa: E402

_AGENTS = _ROOT / "AGENTS.md"


def _model(assumed_role: str) -> dict:
    """Minimal model shape exercised by the rendered startup functions."""
    return {
        "role": {"assumed_role": assumed_role},
        "metrics": {"contention": {"raw_review_queue_count": 0}},
    }


def test_f6_rendered_lo_input_semantics_omits_session_focus() -> None:
    rendered = ssi._render_fresh_session_input_semantics(_model("Loyal Opposition"))
    assert "session-focus choices" not in rendered, rendered
    assert "Loyal Opposition startup action" in rendered, rendered


def test_f6_rendered_pb_input_semantics_retains_session_focus() -> None:
    rendered = ssi._render_fresh_session_input_semantics(_model("Prime Builder"))
    assert "session-focus choices" in rendered, rendered


def test_f5_rendered_lo_startup_task_auto_processes_by_default() -> None:
    rendered = ssi._render_loyal_opposition_startup_task(_model("Loyal Opposition"))
    low = rendered.lower()
    # Auto-process-by-default authority (F5), tied to the governing ADR.
    assert "auto-process" in low, rendered
    assert "ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001" in rendered, rendered
    # Advisory mode is the opt-in that asks; the default path does not ask.
    assert "advisory mode opt-in" in low, rendered


def test_f5_agents_md_narrative_matches_auto_process_default() -> None:
    low = _AGENTS.read_text(encoding="utf-8").lower()
    assert "oldest-to-newest by default" in low
    assert "advisory mode is opt-in" in low
    assert "only advisory mode" in low
