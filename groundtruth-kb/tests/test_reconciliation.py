# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for F8: Provenance Reconciliation over the native record shape.

Detector cases seed an in-memory ``SpecSource`` of native-shaped specification
records (the fields ``GET /v1/specifications`` returns).  ``NativeSpecSource``
cases drive the pager with a fake client.  The CLI cases run ``gt kb reconcile``
against the disposable native authority (``native_application`` fixture) and
prove the command reads with GET only and writes nothing.

Section layout:

    Orphan Detection                (13 tests)
    Plain-Text Assertion Safety      (4 tests)
    Authority Conflicts              (4 tests)
    Stale Detection                  (5 tests)
    Provenance                       (4 tests)
    Native specification source      (5 tests)
    Composition and text output      (3 tests)
    CLI                              (3 tests, two need the disposable authority)

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.reconciliation import (
    DETECTOR_CATEGORIES,
    NativeSpecSource,
    ReconciliationReport,
    find_authority_conflicts,
    find_duplicate_specs,
    find_expired_provisionals,
    find_orphaned_assertions,
    find_stale_specs,
    format_report_text,
    run_detectors,
)

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------


class InMemorySpecSource:
    """Native-shaped specification records held in memory; filters mirror the native list route."""

    def __init__(self, specs: list[dict[str, Any]] | None = None) -> None:
        self.specs = list(specs or [])
        self.calls: list[dict[str, str | None]] = []

    def add(self, spec: dict[str, Any]) -> None:
        self.specs.append(spec)

    def list_specs(self, *, status: str | None = None, authority: str | None = None) -> list[dict[str, Any]]:
        self.calls.append({"status": status, "authority": authority})
        return [
            dict(spec)
            for spec in self.specs
            if (status is None or spec.get("status") == status)
            and (authority is None or spec.get("authority") == authority)
        ]


def _spec(
    spec_id: str,
    *,
    assertions: list[Any] | str | None = None,
    section: str | None = "default",
    scope: str | None = None,
    authority: str | None = "stated",
    status: str = "active",
    title: str | None = None,
    provisional_until: str | None = None,
    changed_at: str | None = None,
    implementation_verified_at: str | None = None,
) -> dict[str, Any]:
    """One specification record in the native shape (the fields the detectors read)."""
    return {
        "id": spec_id,
        "version": 1,
        "title": title or f"Spec {spec_id}",
        "status": status,
        "section": section,
        "scope": scope,
        "authority": authority,
        "assertions": assertions,
        "provisional_until": provisional_until,
        "implementation_verified_at": implementation_verified_at,
        "changed_at": changed_at or "2026-01-01T00:00:00+00:00",
        "changed_by": "test",
        "change_reason": "test seed",
    }


@pytest.fixture
def source() -> InMemorySpecSource:
    """Empty in-memory specification source."""
    return InMemorySpecSource()


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Project root used for orphan resolution.

    Creates an empty ``src/`` directory but intentionally does NOT seed any
    files — individual tests opt in to specific files.
    """
    root = tmp_path / "project"
    (root / "src").mkdir(parents=True)
    return root


def _touch(root: Path, rel: str) -> None:
    """Create an empty file at ``root / rel`` (making parents as needed)."""
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("")


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


# ===========================================================================
# Section 1: Orphan Detection (13 tests)
# ===========================================================================


class TestOrphanDetection:
    """Orphan detection reuses the shared assertion-target extractor."""

    # 1
    def test_grep_literal_exists_not_orphaned(self, source, project_root):
        _touch(project_root, "src/app.py")
        source.add(_spec("SPEC-1", assertions=[{"type": "grep", "file": "src/app.py", "pattern": "def"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert report.findings == []

    # 2
    def test_grep_literal_missing_orphaned(self, source, project_root):
        source.add(_spec("SPEC-1", assertions=[{"type": "grep", "file": "src/missing.py", "pattern": "x"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding["spec_id"] == "SPEC-1"
        assert finding["assertion_type"] == "grep"
        assert finding["file_target"] == "src/missing.py"

    # 3 — alias: `path` in place of `file`
    def test_grep_path_alias(self, source, project_root):
        source.add(_spec("SPEC-2", assertions=[{"type": "grep", "path": "src/ghost.py", "pattern": "x"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["file_target"] == "src/ghost.py"

    # 4 — alias: `target` in place of `file`
    def test_grep_target_alias(self, source, project_root):
        _touch(project_root, "src/real.py")
        source.add(_spec("SPEC-3", assertions=[{"type": "grep", "target": "src/real.py", "pattern": "x"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert report.findings == []

    # 5
    def test_glob_assertion_with_matches_not_orphaned(self, source, project_root):
        _touch(project_root, "src/a.py")
        _touch(project_root, "src/b.py")
        source.add(_spec("SPEC-4", assertions=[{"type": "glob", "pattern": "src/*.py"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert report.findings == []

    # 6
    def test_glob_zero_matches_orphaned(self, source, project_root):
        source.add(_spec("SPEC-5", assertions=[{"type": "glob", "pattern": "src/ghosts/*.py"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding["assertion_type"] == "glob"
        assert finding["file_target"] == "src/ghosts/*.py"
        assert finding["file_is_glob"] is True

    # 7
    def test_grep_file_glob_with_matches_not_orphaned(self, source, project_root):
        _touch(project_root, "src/one.py")
        source.add(_spec("SPEC-6", assertions=[{"type": "grep", "file": "src/*.py", "pattern": "def"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert report.findings == []

    # 8
    def test_grep_file_glob_zero_matches_orphaned(self, source, project_root):
        source.add(_spec("SPEC-7", assertions=[{"type": "grep", "file": "src/none/*.py", "pattern": "def"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "grep"
        assert report.findings[0]["file_is_glob"] is True

    # 9
    def test_grep_absent_file_glob_zero_matches_orphaned(self, source, project_root):
        source.add(_spec("SPEC-8", assertions=[{"type": "grep_absent", "file": "src/missing/*.py", "pattern": "BAD"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "grep_absent"

    # 10
    def test_count_file_glob_zero_matches_orphaned(self, source, project_root):
        source.add(
            _spec(
                "SPEC-9",
                assertions=[
                    {"type": "count", "file": "src/vanished/*.py", "pattern": "TODO", "operator": ">=", "expected": 1}
                ],
            )
        )
        report = find_orphaned_assertions(source, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "count"

    # 11 — file_exists with `*` in name → literal resolution path
    def test_file_exists_literal_star_orphaned(self, source, project_root):
        # file_exists does NOT treat `*` as a glob; the literal filename
        # containing an asterisk cannot exist as a real file, so the
        # detector must report it as orphaned via the literal-resolve path.
        source.add(_spec("SPEC-10", assertions=[{"type": "file_exists", "file": "src/a*b.py"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert len(report.findings) == 1
        assert report.findings[0]["assertion_type"] == "file_exists"
        assert report.findings[0]["file_target"] == "src/a*b.py"
        assert report.findings[0]["file_is_glob"] is False

    # 12 — composition: mixed children → per-child reporting
    def test_all_of_composition_mixed_children(self, source, project_root):
        _touch(project_root, "src/keep.py")
        source.add(
            _spec(
                "SPEC-11",
                assertions=[
                    {
                        "type": "all_of",
                        "assertions": [
                            {"type": "grep", "file": "src/keep.py", "pattern": "def"},
                            {"type": "grep", "file": "src/gone.py", "pattern": "def"},
                        ],
                    }
                ],
            )
        )
        report = find_orphaned_assertions(source, project_root=project_root)
        # Only the second leaf is orphaned → exactly one finding.
        assert len(report.findings) == 1
        assert report.findings[0]["file_target"] == "src/gone.py"
        assert report.findings[0]["spec_id"] == "SPEC-11"

    # 13 — native lifecycle: only the active corpus is inspected
    def test_retired_and_superseded_specs_are_not_inspected(self, source, project_root):
        source.add(_spec("SPEC-RET", status="retired", assertions=[{"type": "file_exists", "file": "src/old.py"}]))
        source.add(_spec("SPEC-SUP", status="superseded", assertions=[{"type": "glob", "pattern": "src/x/*.py"}]))
        source.add(_spec("SPEC-ACT", assertions=[{"type": "file_exists", "file": "src/new.py"}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert [f["spec_id"] for f in report.findings] == ["SPEC-ACT"]
        assert source.calls == [{"status": "active", "authority": None}]


# ===========================================================================
# Section 2: Plain-Text Assertion Safety (4 tests)
# ===========================================================================


class TestPlainTextAssertionSafety:
    """Plain-text (non-dict) assertion children must be silently skipped."""

    # 14
    def test_top_level_plain_text_skipped(self, source, project_root):
        source.add(_spec("SPEC-TXT-1", assertions=["All forms must be WCAG 2.1 AA compliant."]))
        # Must not crash and must not produce any finding for the text.
        report = find_orphaned_assertions(source, project_root=project_root)
        assert report.findings == []
        assert isinstance(report, ReconciliationReport)

    # 15
    def test_all_of_with_plain_text_child(self, source, project_root):
        source.add(
            _spec(
                "SPEC-TXT-2",
                assertions=[
                    {
                        "type": "all_of",
                        "assertions": ["Owner review required", {"type": "grep", "file": "src/bye.py", "pattern": "x"}],
                    }
                ],
            )
        )
        report = find_orphaned_assertions(source, project_root=project_root)
        # Text child silently dropped; dict child produces a single
        # orphan finding (the file does not exist).
        assert len(report.findings) == 1
        assert report.findings[0]["file_target"] == "src/bye.py"

    # 16
    def test_non_machine_dict_child_skipped(self, source, project_root):
        source.add(_spec("SPEC-TXT-3", assertions=[{"type": "visual", "description": "Widget renders red button."}]))
        report = find_orphaned_assertions(source, project_root=project_root)
        # Unknown type -> extractor drops it, no orphan finding.
        assert report.findings == []

    # 17 — a JSON string is decoded; a null or non-list shape yields nothing
    def test_json_string_and_null_assertions(self, source, project_root):
        source.add(_spec("SPEC-STR", assertions=json.dumps([{"type": "file_exists", "file": "src/nope.py"}])))
        source.add(_spec("SPEC-NULL", assertions=None))
        source.add(_spec("SPEC-BAD", assertions="not json"))
        report = find_orphaned_assertions(source, project_root=project_root)
        assert [(f["spec_id"], f["file_target"]) for f in report.findings] == [("SPEC-STR", "src/nope.py")]


# ===========================================================================
# Section 3: Authority Conflicts (4 tests)
# ===========================================================================


class TestAuthorityConflicts:
    """Stated-vs-inferred structural overlap within the same section/scope."""

    # 18 — alias overlap (different alias keys, same resolved file_target)
    def test_alias_overlap(self, source):
        source.add(
            _spec(
                "SPEC-S",
                section="auth",
                scope="login",
                authority="stated",
                assertions=[{"type": "grep", "file": "src/auth.py", "pattern": "login"}],
            )
        )
        source.add(
            _spec(
                "SPEC-I",
                section="auth",
                scope="login",
                authority="inferred",
                assertions=[{"type": "grep", "path": "src/auth.py", "pattern": "login"}],
            )
        )
        report = find_authority_conflicts(source)
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding["stated_spec"] == "SPEC-S"
        assert finding["inferred_spec"] == "SPEC-I"
        assert "src/auth.py" in finding["overlapping_targets"]

    # 19 — composition overlap
    def test_composition_overlap(self, source):
        source.add(
            _spec(
                "SPEC-STATED",
                section="billing",
                scope="invoice",
                authority="stated",
                assertions=[
                    {"type": "all_of", "assertions": [{"type": "grep", "file": "src/bill.py", "pattern": "invoice"}]}
                ],
            )
        )
        source.add(
            _spec(
                "SPEC-INFERRED",
                section="billing",
                scope="invoice",
                authority="inferred",
                assertions=[{"type": "grep", "file": "src/bill.py", "pattern": "pay"}],
            )
        )
        report = find_authority_conflicts(source)
        assert len(report.findings) == 1
        assert report.findings[0]["overlapping_targets"] == ["src/bill.py"]

    # 20 — glob-string overlap
    def test_glob_string_overlap(self, source):
        source.add(
            _spec(
                "SPEC-GS",
                section="widget",
                scope="ui",
                authority="stated",
                assertions=[{"type": "glob", "pattern": "src/widgets/*.tsx"}],
            )
        )
        source.add(
            _spec(
                "SPEC-GI",
                section="widget",
                scope="ui",
                authority="inferred",
                assertions=[{"type": "glob", "pattern": "src/widgets/*.tsx"}],
            )
        )
        report = find_authority_conflicts(source)
        assert len(report.findings) == 1
        assert "src/widgets/*.tsx" in report.findings[0]["overlapping_targets"]

    # 21 — same target in a different scope, or in a retired stated spec, is not a conflict
    def test_other_scope_or_inactive_pair_is_not_a_conflict(self, source):
        assertion = [{"type": "glob", "pattern": "src/widgets/*.tsx"}]
        source.add(_spec("SPEC-I", section="widget", scope="ui", authority="inferred", assertions=assertion))
        source.add(_spec("SPEC-S-OTHER", section="widget", scope="api", authority="stated", assertions=assertion))
        source.add(
            _spec(
                "SPEC-S-RET", section="widget", scope="ui", authority="stated", status="retired", assertions=assertion
            )
        )
        report = find_authority_conflicts(source)
        assert report.findings == []
        assert source.calls == [
            {"status": "active", "authority": "stated"},
            {"status": "active", "authority": "inferred"},
        ]


# ===========================================================================
# Section 4: Stale Detection (5 tests)
# ===========================================================================


class TestStaleDetection:
    """``changed_at`` windows over the active corpus (the only native path)."""

    # 22 — positive: aged spec, fresh same-section activity
    def test_stale_fallback_with_section_activity(self, source):
        now = datetime.now(UTC)
        source.add(_spec("SPEC-AGED", section="fallback", changed_at=_iso(now - timedelta(days=120))))
        source.add(_spec("SPEC-FRESH", section="fallback", changed_at=_iso(now - timedelta(days=5))))
        report = find_stale_specs(source)
        ids = [f["spec_id"] for f in report.findings]
        assert "SPEC-AGED" in ids
        assert "SPEC-FRESH" not in ids  # the active spec itself isn't stale
        aged = next(f for f in report.findings if f["spec_id"] == "SPEC-AGED")
        assert aged["reason"] == "changed_at"
        assert aged["section"] == "fallback"
        assert aged["threshold_days"] == 90 and aged["section_activity_days"] == 30

    # 23 — negative: same-section activity outside the activity window
    def test_stale_fallback_no_section_activity(self, source):
        now = datetime.now(UTC)
        source.add(_spec("SPEC-AGED", section="dormant", changed_at=_iso(now - timedelta(days=120))))
        # Same-section activity happened 200 days ago → NOT within 30 days.
        source.add(_spec("SPEC-ALSO-OLD", section="dormant", changed_at=_iso(now - timedelta(days=200))))
        report = find_stale_specs(source)
        assert [f["spec_id"] for f in report.findings] == []

    # 24 — a section with a single aged spec is quiet, not stale
    def test_stale_spec_alone_in_section_not_reported(self, source):
        now = datetime.now(UTC)
        source.add(_spec("SPEC-ALONE", section="quiet", changed_at=_iso(now - timedelta(days=400))))
        source.add(_spec("SPEC-ELSEWHERE", section="busy", changed_at=_iso(now - timedelta(days=1))))
        report = find_stale_specs(source)
        assert report.findings == []

    # 25 — no section, unparseable changed_at, or an inactive record: never reported
    def test_stale_skips_unsectioned_undated_and_inactive_specs(self, source):
        now = datetime.now(UTC)
        source.add(_spec("SPEC-FRESH", section="core", changed_at=_iso(now - timedelta(days=2))))
        source.add(_spec("SPEC-NOSECTION", section=None, changed_at=_iso(now - timedelta(days=400))))
        source.add(_spec("SPEC-UNDATED", section="core", changed_at="not a timestamp"))
        source.add(_spec("SPEC-RETIRED", section="core", status="retired", changed_at=_iso(now - timedelta(days=400))))
        report = find_stale_specs(source)
        assert report.findings == []

    # 26 — thresholds and the clock are explicit inputs
    def test_stale_thresholds_and_clock_are_configurable(self, source):
        now = datetime(2026, 6, 1, tzinfo=UTC)
        source.add(_spec("SPEC-A", section="core", changed_at=_iso(now - timedelta(days=20))))
        source.add(_spec("SPEC-B", section="core", changed_at=_iso(now - timedelta(days=3))))
        default = find_stale_specs(source, now=now)
        assert default.findings == []  # 20 days is not stale at the 90-day default
        tight = find_stale_specs(source, staleness_threshold_days=10, section_activity_days=7, now=now)
        assert [f["spec_id"] for f in tight.findings] == ["SPEC-A"]
        assert tight.findings[0]["threshold_days"] == 10
        assert tight.findings[0]["section_activity_days"] == 7
        assert tight.findings[0]["changed_at"] == _iso(now - timedelta(days=20))


# ===========================================================================
# Section 5: Provenance (4 tests)
# ===========================================================================


class TestProvenance:
    """Expired-provisional reconciliation + duplicate-title detection."""

    # 27 — positive: the replacement carries implementation_verified_at
    def test_expired_provisional_with_implemented_replacement_reported(self, source):
        source.add(
            _spec(
                "SPEC-P",
                title="Provisional",
                authority="provisional",  # source: provisional (an AUTHORITY value, never a STATUS)
                provisional_until="SPEC-R",  # reference to replacement
            )
        )
        source.add(
            _spec(
                "SPEC-R",
                title="Replacement",
                authority="stated",
                implementation_verified_at="2026-02-01T00:00:00+00:00",  # the replacement shipped
            )
        )
        report = find_expired_provisionals(source)
        assert [f["spec_id"] for f in report.findings] == ["SPEC-P"]
        finding = report.findings[0]
        assert finding["replacement_spec_id"] == "SPEC-R"
        assert finding["replacement_status"] == "active"
        assert finding["replacement_implementation_verified_at"] == "2026-02-01T00:00:00+00:00"

    # 28 — negative discriminator: the replacement is not verified yet
    def test_provisional_with_specified_replacement_NOT_reported(self, source):
        source.add(_spec("SPEC-P", title="Provisional", authority="provisional", provisional_until="SPEC-R"))
        source.add(_spec("SPEC-R", title="Replacement", authority="stated", implementation_verified_at=None))
        report = find_expired_provisionals(source)
        assert not any(f["spec_id"] == "SPEC-P" for f in report.findings)

    # 29 — a dangling reference or a retired provisional is not an expiration
    def test_dangling_or_inactive_provisional_not_reported(self, source):
        source.add(_spec("SPEC-P1", authority="provisional", provisional_until="SPEC-MISSING"))
        source.add(
            _spec("SPEC-P2", authority="provisional", provisional_until="SPEC-R", status="retired"),
        )
        source.add(_spec("SPEC-R", implementation_verified_at="2026-02-01T00:00:00+00:00"))
        report = find_expired_provisionals(source)
        assert report.findings == []

    # 30 — duplicate spec detection (>=90% title token overlap)
    def test_duplicate_specs_90pct_title_overlap_reported(self, source):
        source.add(_spec("SPEC-D1", title="User authentication flow with password reset"))
        source.add(_spec("SPEC-D2", title="User authentication flow with password reset"))
        source.add(_spec("SPEC-OTHER", title="Completely unrelated admin panel settings"))
        report = find_duplicate_specs(source)
        pairs = {(f["spec_a"], f["spec_b"]) for f in report.findings}
        assert ("SPEC-D1", "SPEC-D2") in pairs
        # Unrelated spec must not appear in any pair.
        flat = {s for pair in pairs for s in pair}
        assert "SPEC-OTHER" not in flat


# ===========================================================================
# Section 6: Native specification source (5 tests)
# ===========================================================================


class _FakeAuthority:
    """Serve canned ``GET /v1/specifications`` pages keyed by the ``after`` cursor."""

    def __init__(self, pages: dict[str | None, Any]) -> None:
        self.pages = pages
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def request(self, method: str, path: str, *, body: Any = None, query: dict[str, Any] | None = None) -> Any:
        self.calls.append((method, path, dict(query or {})))
        return self.pages[(query or {}).get("after")]


class TestNativeSpecSource:
    """Paging, filters and refusals of the authority-backed source."""

    def test_pages_until_next_after_is_null_with_the_status_filter(self):
        authority = _FakeAuthority(
            {
                None: {"records": [_spec("SPEC-1"), _spec("SPEC-2")], "next_after": "SPEC-2"},
                "SPEC-2": {"records": [_spec("SPEC-3")], "next_after": None},
            }
        )
        records = NativeSpecSource(authority).list_specs(status="active")
        assert [r["id"] for r in records] == ["SPEC-1", "SPEC-2", "SPEC-3"]
        assert [(m, p) for m, p, _ in authority.calls] == [("GET", "/v1/specifications")] * 2
        assert [q.get("after") for _, _, q in authority.calls] == [None, "SPEC-2"]
        assert all(q["status"] == "active" and q["limit"] == NativeSpecSource.page_size for _, _, q in authority.calls)

    def test_authority_filter_is_applied_client_side(self):
        authority = _FakeAuthority(
            {
                None: {
                    "records": [
                        _spec("SPEC-1", authority="stated"),
                        _spec("SPEC-2", authority="inferred"),
                        _spec("SPEC-3", authority=None),
                    ],
                    "next_after": None,
                }
            }
        )
        native = NativeSpecSource(authority)
        assert [r["id"] for r in native.list_specs(authority="inferred")] == ["SPEC-2"]
        assert [r["id"] for r in native.list_specs(authority="stated")] == ["SPEC-1"]
        assert [r["id"] for r in native.list_specs()] == ["SPEC-1", "SPEC-2", "SPEC-3"]
        # The list route accepts no ``authority`` query field; every query omits it.
        assert all("authority" not in q for _, _, q in authority.calls)

    def test_each_status_listing_is_read_once(self):
        records = [_spec("SPEC-1", authority="stated"), _spec("SPEC-2", status="retired")]
        authority = _FakeAuthority({None: {"records": records, "next_after": None}})
        native = NativeSpecSource(authority)
        native.list_specs(status="active", authority="stated")
        native.list_specs(status="active", authority="inferred")
        native.list_specs(status="active")
        assert len(authority.calls) == 1
        native.list_specs()
        assert len(authority.calls) == 2
        assert [q.get("status") for _, _, q in authority.calls] == ["active", None]

    @pytest.mark.parametrize(
        "page",
        [
            {"records": []},  # no cursor field
            {"records": {"not": "a list"}, "next_after": None},
            {"records": [{"title": "no identity"}], "next_after": None},
            {"records": [_spec("SPEC-1"), _spec("SPEC-1")], "next_after": None},  # duplicate identity
            ["not", "an", "object"],
        ],
    )
    def test_malformed_page_is_invalid_response(self, page):
        native = NativeSpecSource(_FakeAuthority({None: page}))
        with pytest.raises(AuthorityClientError) as refused:
            native.list_specs()
        assert refused.value.code == "invalid_response"

    def test_non_advancing_cursor_is_invalid_response(self):
        looping = _FakeAuthority(
            {
                None: {"records": [_spec("SPEC-1")], "next_after": "SPEC-1"},
                "SPEC-1": {"records": [_spec("SPEC-2")], "next_after": "SPEC-1"},
            }
        )
        with pytest.raises(AuthorityClientError) as refused:
            NativeSpecSource(looping).list_specs()
        assert refused.value.code == "invalid_response"
        empty_tail = _FakeAuthority({None: {"records": [], "next_after": "SPEC-9"}})
        with pytest.raises(AuthorityClientError):
            NativeSpecSource(empty_tail).list_specs()


# ===========================================================================
# Section 7: Composition and text output (3 tests)
# ===========================================================================


class TestComposition:
    """``run_detectors`` selection/order and the text rendering the CLI prints."""

    def test_run_detectors_runs_the_selection_in_canonical_order(self, source, project_root):
        source.add(_spec("SPEC-D1", title="Same title twice"))
        source.add(_spec("SPEC-D2", title="Same title twice"))
        reports = run_detectors(source, ["duplicate_specs", "orphaned_assertions"], project_root=project_root)
        assert [r.category for r in reports] == ["orphaned_assertions", "duplicate_specs"]
        assert len(reports[1].findings) == 1
        everything = run_detectors(source, DETECTOR_CATEGORIES, project_root=project_root)
        assert [r.category for r in everything] == list(DETECTOR_CATEGORIES)

    def test_run_detectors_rejects_unknown_category(self, source):
        with pytest.raises(ValueError, match="Unknown reconciliation detector"):
            run_detectors(source, ["orphaned_assertions", "snapshots"])

    def test_format_report_text_blocks_and_total(self):
        many = [{"type": "duplicate_spec", "spec_a": f"SPEC-{i:03d}", "spec_b": "SPEC-999"} for i in range(52)]
        text = format_report_text(
            [
                ReconciliationReport("orphaned_assertions", []),
                ReconciliationReport("duplicate_specs", many),
            ]
        )
        lines = text.splitlines()
        assert lines[0] == "" and lines[1] == "[orphaned_assertions] 0 finding(s)"
        assert lines[2] == "" and lines[3] == "[duplicate_specs] 52 finding(s)"
        assert lines[4] == '  - SPEC-000: {"spec_a":"SPEC-000","spec_b":"SPEC-999","type":"duplicate_spec"}'
        assert lines[54] == "  ... (2 more)"
        assert lines[-1] == "Total findings across 2 detector(s): 52"
        assert text.endswith("\n")


# ===========================================================================
# Section 8: CLI (gt kb reconcile is a native, read-only command)
# ===========================================================================


def _put_spec(client: AuthorityClient, spec_id: str, fields: dict[str, Any]) -> None:
    client.request(
        "PUT",
        f"/v1/specifications/{spec_id}",
        body={"expected_version": 0, "actor": "qualification", "reason": "Reconciliation seed", "fields": fields},
    )


@pytest.mark.integration
@pytest.mark.timeout(300)
class TestReconcileCLI:
    """``gt kb reconcile`` dispatches to every detector over the selected authority and never writes."""

    def test_gt_kb_reconcile_all_runs_every_detector(self, native_application, monkeypatch):
        """`gt kb reconcile --all` exits 0 against the native authority, names every
        detector category and the total line, reads with GET only and changes no record."""
        client = native_application.client
        _put_spec(client, "SPEC-1", {"title": "Registry present", "status": "active"})
        _put_spec(
            client,
            "SPEC-2",
            {
                "title": "Ghost module",
                "status": "active",
                "assertions": [{"type": "file_exists", "file": "src/ghost.py"}],
            },
        )
        before = native_application.facts()
        calls: list[tuple[str, str]] = []
        original_request = AuthorityClient.request

        def transport(self, method, path, *, body=None, query=None):
            calls.append((method, path))
            return original_request(self, method, path, body=body, query=query)

        with monkeypatch.context() as patched:
            patched.setattr(AuthorityClient, "request", transport)
            result = native_application.invoke(
                "kb", "reconcile", "--all", "--project-root", str(native_application.host)
            )
        assert result.exit_code == 0, f"stdout={result.output}\n\nexc={result.exception}"
        output = result.output
        assert "[orphaned_assertions]" in output
        assert "[stale_specs]" in output
        assert "[authority_conflicts]" in output
        assert "[duplicate_specs]" in output
        assert "[expired_provisionals]" in output
        assert "Total findings across 5 detector(s):" in output
        assert calls and all(method == "GET" and path == "/v1/specifications" for method, path in calls)
        assert native_application.facts() == before

    def test_gt_kb_reconcile_json_reports_a_seeded_orphan(self, native_application):
        """`--orphans --json` emits the report object; a seeded missing target is the one finding."""
        client = native_application.client
        present = [{"type": "file_exists", "file": "applications/registry.toml"}]
        _put_spec(client, "SPEC-KEEP", {"title": "Registry file", "status": "active", "assertions": present})
        gone = [{"type": "grep", "file": "src/gone.py", "pattern": "x"}]
        _put_spec(client, "SPEC-GONE", {"title": "Missing module", "status": "active", "assertions": gone})
        old = [{"type": "file_exists", "file": "src/old.py"}]
        _put_spec(client, "SPEC-RETIRED", {"title": "Retired module", "status": "retired", "assertions": old})
        result = native_application.invoke("kb", "reconcile", "--orphans", "--json")
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert set(payload) == {"project_root", "reports", "total_findings"}
        assert Path(payload["project_root"]) == native_application.host.resolve()
        assert [r["category"] for r in payload["reports"]] == ["orphaned_assertions"]
        report = payload["reports"][0]
        assert report["finding_count"] == payload["total_findings"] == 1
        assert report["findings"][0]["spec_id"] == "SPEC-GONE"
        assert report["findings"][0]["file_target"] == "src/gone.py"

    def test_gt_kb_reconcile_refuses_without_an_authority_url(self, tmp_path, runner):
        """No SQLite fallback: a configuration without authority_url is refused, not opened locally."""
        from groundtruth_kb.cli import main

        config = tmp_path / "groundtruth.toml"
        config.write_text('[groundtruth]\nproject_root = "."\n', encoding="utf-8")
        result = runner.invoke(main, ["--config", str(config), "kb", "reconcile", "--all"])
        assert result.exit_code == 1, result.output
        assert "No authority_url is configured" in result.output
        assert not list(tmp_path.glob("*.db"))
