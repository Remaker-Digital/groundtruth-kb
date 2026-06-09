#!/usr/bin/env python3
"""
S117 Migration: Create work items, tests, and wire to test plan for untested specs.

Operations:
  1. Create work items (WI-0767..0770) for 4 active untested specs lacking WIs
  2. Create test artifacts (TEST-2634..2638) for all 5 active untested specs
  3. Wire new tests into appropriate PLAN-001 phases
  4. Resolve 765 open work items whose source specs now have tests

Idempotent: checks for existing artifacts before creating.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))

import db

CHANGED_BY = "S117-migration"
SESSION = "S117"

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Work Items for untested specs
# ─────────────────────────────────────────────────────────────────────────────

WORK_ITEMS = [
    {
        "id": "WI-0767",
        "title": "Create test for GOV-09: Owner Input Classification Rule",
        "origin": "new",
        "component": "test_harness",
        "source_spec_id": "GOV-09",
        "priority": "P2",
        "description": (
            "GOV-09 specifies that Claude must detect specification language in owner "
            "input before proceeding to implementation. The spec-classifier.py hook "
            "implements this mechanically. Test needs to verify the hook exists and "
            "correctly classifies spec-like vs non-spec inputs."
        ),
    },
    {
        "id": "WI-0768",
        "title": "Create test for SPEC-1501: Live E2E validates real production data",
        "origin": "new",
        "component": "test_harness",
        "source_spec_id": "SPEC-1501",
        "priority": "P2",
        "description": (
            "SPEC-1501 requires live E2E tests validate against real production tenant "
            "data (not fixtures or mocks). Test needs to verify the live test files "
            "assert against real values."
        ),
    },
    {
        "id": "WI-0769",
        "title": "Create test for SPEC-1502: Live E2E visual CSS and responsive layout",
        "origin": "new",
        "component": "test_harness",
        "source_spec_id": "SPEC-1502",
        "priority": "P2",
        "description": (
            "SPEC-1502 requires live E2E tests verify visual CSS properties using "
            "page.evaluate() + getComputedStyle() and test at 3 viewport sizes. "
            "Test needs to verify test_visual_live.py and test_responsive_live.py "
            "meet these requirements."
        ),
    },
    {
        "id": "WI-0770",
        "title": "Create test for SPEC-1503: Live E2E end-to-end user flows",
        "origin": "new",
        "component": "test_harness",
        "source_spec_id": "SPEC-1503",
        "priority": "P2",
        "description": (
            "SPEC-1503 requires live E2E tests exercise multi-step user flows against "
            "the live backend: navigation, draft save, team page loads. Test needs to "
            "verify the live test files include these flow tests."
        ),
    },
]

# SPEC-1500 already has WI-0766 (resolved for a different reason: bug fix).
# We create WI for the "needs test" gap tracking purpose for GOV-09, 1501, 1502, 1503.

# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Test artifacts for untested specs
# ─────────────────────────────────────────────────────────────────────────────

TESTS = [
    {
        "id": "TEST-2634",
        "title": "GOV-09: spec-classifier hook detects specification language",
        "spec_id": "GOV-09",
        "test_type": "unit",
        "test_file": "tests/hooks/test_spec_classifier.py",
        "test_class": "TestSpecClassifier",
        "test_function": "test_detects_must_include_language",
        "description": (
            "Verifies .claude/hooks/spec-classifier.py exists and correctly classifies "
            "owner input: (1) 'must include' phrases trigger the GOV-01 reminder, "
            "(2) simple commands/questions do not trigger, (3) short messages are skipped."
        ),
        "expected_outcome": (
            "Hook file exists with detect_specification_language() function. "
            "Spec-like prompts (containing 'must include', 'should have', numbered "
            "requirements) return True. Non-spec prompts (commands, questions, short "
            "messages) return False."
        ),
    },
    {
        "id": "TEST-2635",
        "title": "SPEC-1500: Live E2E tests use real API integration (no mocks)",
        "spec_id": "SPEC-1500",
        "test_type": "unit",
        "test_file": "tests/e2e_live/test_live_infrastructure.py",
        "test_class": "TestLiveInfrastructure",
        "test_function": "test_no_mocked_api_responses",
        "description": (
            "Source inspection: reads all test_*_live.py files and verifies they do not "
            "use page.route() to mock API responses (except conftest route handlers "
            "for non-API resources). Confirms tests connect through Vite proxy to "
            "the production API gateway."
        ),
        "expected_outcome": (
            "Live E2E test files (test_*_live.py) exist in tests/e2e_live/. "
            "No test file uses page.route() to intercept /api/ endpoints with mock "
            "responses. conftest.py configures real API proxy connection."
        ),
    },
    {
        "id": "TEST-2636",
        "title": "SPEC-1501: Live E2E tests validate real production data",
        "spec_id": "SPEC-1501",
        "test_type": "unit",
        "test_file": "tests/e2e_live/test_live_infrastructure.py",
        "test_class": "TestLiveDataValidation",
        "test_function": "test_assertions_use_real_values",
        "description": (
            "Source inspection: verifies live E2E tests assert against real production "
            "data from remaker-digital-001 tenant. Tests should reference actual brand "
            "name, actual config values — not fixture data or hardcoded mock strings."
        ),
        "expected_outcome": (
            "Live E2E tests contain assertions against real tenant data. No test "
            "file in tests/e2e_live/ uses MOCK_CONFIG or fixture constants for "
            "assertion values."
        ),
    },
    {
        "id": "TEST-2637",
        "title": "SPEC-1502: Live E2E visual CSS and responsive layout tests exist",
        "spec_id": "SPEC-1502",
        "test_type": "unit",
        "test_file": "tests/e2e_live/test_live_infrastructure.py",
        "test_class": "TestVisualCSSInfrastructure",
        "test_function": "test_visual_tests_use_computed_styles_and_viewports",
        "description": (
            "Source inspection: verifies test_visual_live.py uses page.evaluate() + "
            "getComputedStyle() for CSS verification, and test_responsive_live.py "
            "tests at 3 distinct viewport sizes using set_viewport_size()."
        ),
        "expected_outcome": (
            "test_visual_live.py exists and contains page.evaluate() calls with "
            "getComputedStyle. test_responsive_live.py exists and calls "
            "set_viewport_size() with at least 3 different viewport dimensions."
        ),
    },
    {
        "id": "TEST-2638",
        "title": "SPEC-1503: Live E2E end-to-end user flow tests exist",
        "spec_id": "SPEC-1503",
        "test_type": "unit",
        "test_file": "tests/e2e_live/test_live_infrastructure.py",
        "test_class": "TestEndToEndFlows",
        "test_function": "test_multi_step_flows_exist",
        "description": (
            "Source inspection: verifies live E2E test suite includes multi-step user "
            "flow tests — navigation between admin pages, form interactions, "
            "and page load verification against the live backend."
        ),
        "expected_outcome": (
            "tests/e2e_live/ contains test files exercising: navigation across all "
            "admin pages (test_navigation_live.py), configuration interactions "
            "(test_configuration_live.py), team page loads (test_team_live.py), "
            "and dashboard data (test_dashboard_live.py)."
        ),
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Wire tests into test plan phases
# ─────────────────────────────────────────────────────────────────────────────

# GOV-09 test → Phase 1 (Pre-flight Checks) — governance hooks
# SPEC-1500..1503 tests → Phase 3 (Production Regression) — live verification

PHASE_ASSIGNMENTS = {
    "PHASE-001": ["TEST-2634"],  # GOV-09 → Pre-flight
    "PHASE-003": ["TEST-2635", "TEST-2636", "TEST-2637", "TEST-2638"],  # Live E2E → Prod Regression
}


def phase_1_create_work_items(kdb: db.KnowledgeDB) -> int:
    """Create work items for untested specs that lack them."""
    created = 0
    for wi_def in WORK_ITEMS:
        existing = kdb.get_work_item(wi_def["id"])
        if existing:
            print(f"  SKIP {wi_def['id']}: already exists")
            continue

        kdb.insert_work_item(
            id=wi_def["id"],
            title=wi_def["title"],
            origin=wi_def["origin"],
            component=wi_def["component"],
            resolution_status="open",
            changed_by=CHANGED_BY,
            change_reason=f"{SESSION}: create WI for untested spec {wi_def['source_spec_id']}",
            description=wi_def.get("description"),
            source_spec_id=wi_def.get("source_spec_id"),
            priority=wi_def.get("priority"),
        )
        print(f"  CREATED {wi_def['id']}: {wi_def['title']}")
        created += 1
    return created


def phase_2_create_tests(kdb: db.KnowledgeDB) -> int:
    """Create test artifacts for all active untested specs."""
    created = 0
    for test_def in TESTS:
        existing = kdb.get_test(test_def["id"])
        if existing:
            print(f"  SKIP {test_def['id']}: already exists")
            continue

        kdb.insert_test(
            id=test_def["id"],
            title=test_def["title"],
            spec_id=test_def["spec_id"],
            test_type=test_def["test_type"],
            expected_outcome=test_def["expected_outcome"],
            changed_by=CHANGED_BY,
            change_reason=f"{SESSION}: create test for untested spec {test_def['spec_id']}",
            test_file=test_def.get("test_file"),
            test_class=test_def.get("test_class"),
            test_function=test_def.get("test_function"),
            description=test_def.get("description"),
        )
        print(f"  CREATED {test_def['id']}: {test_def['title']}")
        created += 1
    return created


def phase_3_wire_to_plan(kdb: db.KnowledgeDB) -> int:
    """Add new tests to existing test plan phases."""
    updated = 0
    for phase_id, new_test_ids in PHASE_ASSIGNMENTS.items():
        phase = kdb.get_test_plan_phase(phase_id)
        if not phase:
            print(f"  ERROR: Phase {phase_id} not found!")
            continue

        existing_ids = json.loads(phase["test_ids"]) if phase.get("test_ids") else []
        already_present = [t for t in new_test_ids if t in existing_ids]
        to_add = [t for t in new_test_ids if t not in existing_ids]

        if already_present:
            print(f"  {phase_id}: already has {already_present}")
        if not to_add:
            print(f"  SKIP {phase_id}: all tests already wired")
            continue

        merged_ids = existing_ids + to_add
        kdb.update_test_plan_phase(
            id=phase_id,
            changed_by=CHANGED_BY,
            change_reason=f"{SESSION}: add {len(to_add)} tests for untested specs",
            test_ids=merged_ids,
        )
        print(f"  UPDATED {phase_id}: added {to_add} ({len(existing_ids)} -> {len(merged_ids)} tests)")
        updated += 1
    return updated


def phase_4_resolve_covered_wis(kdb: db.KnowledgeDB) -> int:
    """Resolve open work items whose source specs now have tests."""
    open_wis = kdb.list_work_items(resolution_status="open")
    resolved = 0
    batch_size = 50  # Progress reporting interval

    for i, wi in enumerate(open_wis):
        spec_id = wi.get("source_spec_id")
        if not spec_id:
            continue

        tests = kdb.get_tests_for_spec(spec_id)
        if not tests:
            continue  # Spec still has no tests — keep WI open

        # Spec now has tests — resolve the WI
        kdb.update_work_item(
            id=wi["id"],
            changed_by=CHANGED_BY,
            change_reason=f"{SESSION}: spec {spec_id} now has {len(tests)} test(s) — gap closed",
            resolution_status="resolved",
        )
        resolved += 1

        if resolved % batch_size == 0:
            print(f"    ... resolved {resolved} WIs so far ...")

    return resolved


def main() -> None:
    kdb = db.KnowledgeDB()

    print("=" * 70)
    print(f"S117 Migration: Tests for Untested Specs")
    print("=" * 70)

    # Phase 1: Work Items
    print("\n--- Phase 1: Create Work Items ---")
    wi_count = phase_1_create_work_items(kdb)
    print(f"  Total created: {wi_count}")

    # Phase 2: Tests
    print("\n--- Phase 2: Create Test Artifacts ---")
    test_count = phase_2_create_tests(kdb)
    print(f"  Total created: {test_count}")

    # Phase 3: Wire to plan
    print("\n--- Phase 3: Wire Tests to Plan Phases ---")
    phase_count = phase_3_wire_to_plan(kdb)
    print(f"  Total phases updated: {phase_count}")

    # Phase 4: Resolve covered WIs
    print("\n--- Phase 4: Resolve Covered Work Items ---")
    resolved_count = phase_4_resolve_covered_wis(kdb)
    print(f"  Total resolved: {resolved_count}")

    # Verification
    print("\n--- Verification ---")
    untested = kdb.get_untested_specs()
    active_untested = [s for s in untested if s["status"] != "retired"]
    open_wis = kdb.get_open_work_items()
    all_tests = kdb.list_tests()

    print(f"  Untested specs (total): {len(untested)}")
    print(f"  Untested specs (active, non-retired): {len(active_untested)}")
    print(f"  Open work items: {len(open_wis)}")
    print(f"  Total tests: {len(all_tests)}")

    if active_untested:
        print(f"  WARNING: {len(active_untested)} active specs still lack tests:")
        for s in active_untested:
            print(f"    {s['id']}: {s['title']}")

    # Summary
    print("\n" + "=" * 70)
    print(
        f"SUMMARY: {wi_count} WIs created, {test_count} tests created, "
        f"{phase_count} phases updated, {resolved_count} WIs resolved"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
