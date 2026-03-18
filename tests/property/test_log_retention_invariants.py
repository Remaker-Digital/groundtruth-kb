"""Property-based tests for log retention invariants (SPEC-1837/WI-1499).

Tests that log retention cutoff dates are always in the past for valid
retention periods, and that archive paths are well-formed.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from src.multi_tenant.log_retention import (
    compute_cutoff_date,
    get_retention_days,
    build_archive_path,
    format_ndjson,
    DEFAULT_RETENTION_DAYS,
)


# ---------------------------------------------------------------------------
# Invariant 1: Cutoff date is always in the past for any valid retention_days
# ---------------------------------------------------------------------------


@given(retention_days=st.integers(min_value=1, max_value=3650))
@settings(max_examples=100, deadline=5000)
def test_cutoff_is_always_in_the_past(retention_days: int) -> None:
    """For any positive retention_days, the cutoff date must be before now."""
    now = datetime.now(timezone.utc)
    cutoff = compute_cutoff_date(retention_days, now=now)
    assert cutoff is not None, "Non-None retention_days must produce a cutoff"
    assert cutoff < now, f"Cutoff {cutoff} must be before now {now}"


@given(retention_days=st.integers(min_value=1, max_value=3650))
@settings(max_examples=100, deadline=5000)
def test_cutoff_delta_matches_retention_days(retention_days: int) -> None:
    """The cutoff date must be exactly retention_days before now."""
    now = datetime.now(timezone.utc)
    cutoff = compute_cutoff_date(retention_days, now=now)
    expected = now - timedelta(days=retention_days)
    assert cutoff == expected, f"Cutoff {cutoff} != expected {expected}"


def test_cutoff_is_none_for_unlimited() -> None:
    """Unlimited retention (None days) must produce None cutoff."""
    assert compute_cutoff_date(None) is None


# ---------------------------------------------------------------------------
# Invariant 2: Cutoff ordering is monotonic (more days → earlier cutoff)
# ---------------------------------------------------------------------------


@given(
    days_a=st.integers(min_value=1, max_value=3650),
    days_b=st.integers(min_value=1, max_value=3650),
)
@settings(max_examples=100, deadline=5000)
def test_cutoff_ordering_is_monotonic(days_a: int, days_b: int) -> None:
    """If days_a > days_b, then cutoff_a < cutoff_b (further in the past)."""
    assume(days_a != days_b)
    now = datetime.now(timezone.utc)
    cutoff_a = compute_cutoff_date(days_a, now=now)
    cutoff_b = compute_cutoff_date(days_b, now=now)
    if days_a > days_b:
        assert cutoff_a < cutoff_b
    else:
        assert cutoff_a > cutoff_b


# ---------------------------------------------------------------------------
# Invariant 3: get_retention_days returns consistent values
# ---------------------------------------------------------------------------


@given(
    collection=st.sampled_from(list(DEFAULT_RETENTION_DAYS.keys())),
    tier=st.sampled_from(["starter", "professional", "enterprise"]),
)
@settings(max_examples=50, deadline=5000)
def test_retention_days_are_positive_or_none(collection: str, tier: str) -> None:
    """Retention days must be a positive integer or None (unlimited)."""
    days = get_retention_days(collection, tier)
    assert days is None or days > 0, f"Invalid retention: {days}"


# ---------------------------------------------------------------------------
# Invariant 4: Archive paths are well-formed
# ---------------------------------------------------------------------------


@given(
    tenant_id=st.from_regex(r"^[a-z0-9\-]{5,40}$", fullmatch=True),
    collection=st.sampled_from(list(DEFAULT_RETENTION_DAYS.keys())),
)
@settings(max_examples=50, deadline=5000)
def test_archive_path_contains_all_segments(tenant_id: str, collection: str) -> None:
    """Archive path must contain tenant_id, collection, and .ndjson.gz suffix."""
    path = build_archive_path(tenant_id, collection)
    assert tenant_id in path, f"Path missing tenant_id: {path}"
    assert collection in path, f"Path missing collection: {path}"
    assert path.endswith(".ndjson.gz"), f"Path missing .ndjson.gz suffix: {path}"


# ---------------------------------------------------------------------------
# Invariant 5: NDJSON formatting is well-formed
# ---------------------------------------------------------------------------


@given(
    records=st.lists(
        st.fixed_dictionaries({"key": st.text(min_size=1, max_size=20)}),
        min_size=0,
        max_size=10,
    )
)
@settings(max_examples=50, deadline=5000)
def test_ndjson_line_count_matches_record_count(records: list) -> None:
    """NDJSON output has exactly one line per record."""
    output = format_ndjson(records)
    if not records:
        assert output == ""
    else:
        lines = output.split("\n")
        assert len(lines) == len(records), f"Expected {len(records)} lines, got {len(lines)}"
