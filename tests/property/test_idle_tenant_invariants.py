"""Property-based tests for idle tenant detection invariants (SPEC-1835/WI-1499).

Tests that idle classification is monotonic over time and threshold ordering
is consistent.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.multi_tenant.idle_tenant_detection import (
    classify_idle_state,
    should_update_activity,
    IDLE_THRESHOLDS,
    ACTIVITY_COALESCE_SECONDS,
)


# Canonical idle state severity ordering (least → most severe)
SEVERITY_ORDER = {
    "active": 0,
    "notification": 1,
    "downgrade_offer": 2,
    "auto_downgrade": 3,
    "archival_review": 4,
}


# ---------------------------------------------------------------------------
# Invariant 1: Idle classification is monotonic over time
# ---------------------------------------------------------------------------


@given(
    days_a=st.integers(min_value=0, max_value=365),
    days_b=st.integers(min_value=0, max_value=365),
)
@settings(max_examples=200, deadline=5000)
def test_idle_classification_is_monotonic(days_a: int, days_b: int) -> None:
    """A tenant idle for more days is classified at-least-as-severely idle."""
    assume(days_a != days_b)
    now = datetime.now(timezone.utc)
    activity_a = (now - timedelta(days=days_a)).isoformat()
    activity_b = (now - timedelta(days=days_b)).isoformat()

    state_a = classify_idle_state(activity_a, now=now)
    state_b = classify_idle_state(activity_b, now=now)

    sev_a = SEVERITY_ORDER[state_a]
    sev_b = SEVERITY_ORDER[state_b]

    if days_a > days_b:
        assert sev_a >= sev_b, (
            f"Idle {days_a}d → {state_a} should be >= idle {days_b}d → {state_b}"
        )
    else:
        assert sev_a <= sev_b, (
            f"Idle {days_a}d → {state_a} should be <= idle {days_b}d → {state_b}"
        )


# ---------------------------------------------------------------------------
# Invariant 2: Thresholds are strictly ordered
# ---------------------------------------------------------------------------


def test_thresholds_are_strictly_ordered() -> None:
    """IDLE_THRESHOLDS must be strictly increasing: notification < downgrade_offer < auto_downgrade < archival_review."""
    assert IDLE_THRESHOLDS["notification"] < IDLE_THRESHOLDS["downgrade_offer"]
    assert IDLE_THRESHOLDS["downgrade_offer"] < IDLE_THRESHOLDS["auto_downgrade"]
    assert IDLE_THRESHOLDS["auto_downgrade"] < IDLE_THRESHOLDS["archival_review"]


# ---------------------------------------------------------------------------
# Invariant 3: All threshold boundaries produce the correct classification
# ---------------------------------------------------------------------------


@given(days=st.sampled_from(list(IDLE_THRESHOLDS.values())))
@settings(max_examples=20, deadline=5000)
def test_exact_threshold_produces_expected_state(days: int) -> None:
    """At exactly the threshold day, the tenant enters the corresponding state."""
    now = datetime.now(timezone.utc)
    activity = (now - timedelta(days=days)).isoformat()
    state = classify_idle_state(activity, now=now)

    # Find which threshold this matches
    for name, threshold in sorted(IDLE_THRESHOLDS.items(), key=lambda x: -x[1]):
        if days >= threshold:
            assert state == name, f"At {days}d idle expected {name}, got {state}"
            break


# ---------------------------------------------------------------------------
# Invariant 4: None activity → archival_review
# ---------------------------------------------------------------------------


def test_none_activity_is_archival_review() -> None:
    """A tenant with no recorded activity should be classified as archival_review."""
    assert classify_idle_state(None) == "archival_review"


# ---------------------------------------------------------------------------
# Invariant 5: Active tenants are below all thresholds
# ---------------------------------------------------------------------------


@given(days=st.integers(min_value=0, max_value=29))
@settings(max_examples=30, deadline=5000)
def test_below_notification_threshold_is_active(days: int) -> None:
    """Tenants idle less than the notification threshold are 'active'."""
    now = datetime.now(timezone.utc)
    activity = (now - timedelta(days=days)).isoformat()
    assert classify_idle_state(activity, now=now) == "active"


# ---------------------------------------------------------------------------
# Invariant 6: Activity coalescing consistency
# ---------------------------------------------------------------------------


@given(seconds_ago=st.integers(min_value=0, max_value=7200))
@settings(max_examples=50, deadline=5000)
def test_activity_coalescing_boundary(seconds_ago: int) -> None:
    """should_update_activity returns True only when elapsed >= coalesce period."""
    now = datetime.now(timezone.utc)
    last = (now - timedelta(seconds=seconds_ago)).isoformat()
    result = should_update_activity(last, now=now)
    if seconds_ago >= ACTIVITY_COALESCE_SECONDS:
        assert result is True, f"Should update after {seconds_ago}s"
    else:
        assert result is False, f"Should NOT update after only {seconds_ago}s"


def test_none_activity_always_updates() -> None:
    """should_update_activity(None) must always return True."""
    assert should_update_activity(None) is True
