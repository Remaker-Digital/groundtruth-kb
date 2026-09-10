"""The disposition matrix derives its actionable sets from the vocabulary (WI-7705).

Spec: `SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clauses 1 and 5.

The defect this pins: `groundtruth_kb/bridge/disposition.py` restated the two
actionable-status sets as independent literals. They drifted — omitting `READY`
and `NOT-READY` while retaining retired `NO-ACTION` — which made every `READY`
thread unreachable from the Loyal Opposition queue and every `NOT-READY` thread
unreachable from the Prime queue. Fifteen threads were affected. The sets feed
`state_report`, `notify`, `dispatcher/scheduler` and the bridge scan helper, so
the shortfall reached every surface an agent uses to find work.

Why these assertions test IDENTITY rather than equality, which is the whole
point of the file: between the proposal and its review, someone corrected the
values by hand. Equality was restored; the second definition was not removed.
An equality assertion would have gone green while the drift class remained
entirely intact, and the sets would have been free to diverge again on the next
edit. Equality can be restored by hand. Identity cannot be faked.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge import disposition, vocabulary  # noqa: E402


def test_prime_actionable_set_is_the_vocabulary_object() -> None:
    assert disposition.PRIME_ACTIONABLE_STATUSES is vocabulary.PRIME_ACTIONABLE_STATUSES


def test_loyal_opposition_actionable_set_is_the_vocabulary_object() -> None:
    assert disposition.LOYAL_OPPOSITION_ACTIONABLE_STATUSES is vocabulary.LOYAL_OPPOSITION_ACTIONABLE_STATUSES


def test_post_go_statuses_are_actionable_to_the_right_role() -> None:
    """Covers clause 1: the ten-token vocabulary includes the post-GO pair."""
    assert "READY" in disposition.LOYAL_OPPOSITION_ACTIONABLE_STATUSES
    assert "NOT-READY" in disposition.PRIME_ACTIONABLE_STATUSES


def test_retired_tokens_are_absent_from_both_actionable_sets() -> None:
    """`NO-ACTION` and `DEFERRED` are retired with no alias and no crosswalk."""
    for retired in ("NO-ACTION", "DEFERRED"):
        assert retired not in disposition.PRIME_ACTIONABLE_STATUSES
        assert retired not in disposition.LOYAL_OPPOSITION_ACTIONABLE_STATUSES


def test_ready_is_dispatchable_and_both_statuses_resolve_to_a_role() -> None:
    """The consequence layer, not just the constants.

    `dispatchable_for_status` and the role resolver both read the sets above.
    Asserting the constants alone would not catch a caller that bypassed them,
    and role resolution returning None is how a status becomes nobody's work.
    """
    assert disposition.dispatchable_for_status("READY") is True
    assert disposition._action_role_for_status("READY") == disposition.LOYAL_OPPOSITION_ROLE
    assert disposition._action_role_for_status("NOT-READY") == disposition.PRIME_BUILDER_ROLE
