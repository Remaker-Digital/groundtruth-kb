"""Record KB artifacts for test & deploy automation overhaul.

GOV-17, SPEC-1616..1620, WI-0939..0944, TEST-2942..2947.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))

from db import KnowledgeDB  # noqa: E402

SESSION = "S131"
CHANGED_BY = f"claude/{SESSION}"


def main():
    kdb = KnowledgeDB()

    # ------------------------------------------------------------------
    # 1. GOV-17 — Automation script modification approval gate
    # ------------------------------------------------------------------
    print("Recording GOV-17...")
    kdb.insert_spec(
        id="GOV-17",
        title="Automation script modification approval gate",
        description=(
            "Claude MUST NOT alter testing or deployment automation scripts "
            "(scripts/test_pipeline.py, scripts/deploy_pipeline.py, "
            "scripts/pre_flight_checklist.py, scripts/upgrade_verification.py, "
            "scripts/run-tests-thermal-safe.ps1, scripts/_subprocess_stream.py, "
            "scripts/_defect_reporter.py) without notifying the owner in advance "
            "and requesting explicit approval. This directive exists because "
            "Claude has proven unreliable at executing fine-grained multi-step "
            "procedures manually — the scripts are the trustworthy execution layer "
            "and must not be silently modified."
        ),
        status="verified",
        section="governance",
        type="governance",
        assertions=[
            {
                "id": "GOV-17-A1",
                "type": "process",
                "status": "verified",
                "description": (
                    "Claude must request owner approval before modifying any automation script listed in GOV-17."
                ),
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner directive: automation scripts are the trustworthy execution layer",
    )
    print("  GOV-17 recorded.")

    # ------------------------------------------------------------------
    # 2. SPEC-1616 — Automated test pipeline (single invocation, all tests)
    # ------------------------------------------------------------------
    print("Recording SPEC-1616...")
    kdb.insert_spec(
        id="SPEC-1616",
        title="Automated test pipeline — single invocation, all tests",
        description=(
            "The process of testing production or staging environments must be "
            "executed via a scripted, autonomous process (scripts/test_pipeline.py) "
            "which DOES NOT require any interaction with the owner or Claude during "
            "execution. A single invocation runs ALL tests: local pytest suite, "
            "mocked E2E, KB assertions, live config pipeline, live E2E, upgrade "
            "verification, and governance checks. Supports --phase (local/live/"
            "governance/all) and --stop-on-fail flags."
        ),
        status="specified",
        section="infrastructure_automation",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1616-A1",
                "type": "functional",
                "status": "specified",
                "description": (
                    "scripts/test_pipeline.py runs all test phases without any human or Claude interaction."
                ),
            },
            {
                "id": "SPEC-1616-A2",
                "type": "functional",
                "status": "specified",
                "description": ("Exit code 0 = all PASS/WARN, exit code 1 = any FAIL."),
            },
            {
                "id": "SPEC-1616-A3",
                "type": "functional",
                "status": "specified",
                "description": (
                    "--phase local runs only Phases 0-4 (no live API calls). "
                    "--phase live runs Phases 5-7. --phase all runs all."
                ),
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner specification: scripted autonomous test process",
    )
    print("  SPEC-1616 recorded.")

    # ------------------------------------------------------------------
    # 3. SPEC-1617 — Test automation DEFECT auto-creation
    # ------------------------------------------------------------------
    print("Recording SPEC-1617...")
    kdb.insert_spec(
        id="SPEC-1617",
        title="Test automation DEFECT auto-creation",
        description=(
            "When the automated test pipeline completes, it must autonomously "
            "create DEFECT work items in the Knowledge Database for each failed "
            "phase. Each DEFECT WI includes: phase number, phase name, failure "
            "detail, environment, version, and links to the source specification."
        ),
        status="specified",
        section="infrastructure_automation",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1617-A1",
                "type": "functional",
                "status": "specified",
                "description": ("One DEFECT WI is created per failed phase in the test pipeline."),
            },
            {
                "id": "SPEC-1617-A2",
                "type": "functional",
                "status": "specified",
                "description": (
                    "DEFECT WIs include diagnostic information: phase, name, detail, environment, version."
                ),
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner specification: autonomous DEFECT WI creation on test failure",
    )
    print("  SPEC-1617 recorded.")

    # ------------------------------------------------------------------
    # 4. SPEC-1618 — Test automation environment fail-fast
    # ------------------------------------------------------------------
    print("Recording SPEC-1618...")
    kdb.insert_spec(
        id="SPEC-1618",
        title="Test automation environment fail-fast",
        description=(
            "All environment variables, tools, and prerequisites required for "
            "the test pipeline to execute must be validated BEFORE any test "
            "execution begins. Missing prerequisites cause immediate FAIL with "
            "specific diagnostic messages. Phase 0 validates: Python 3.12+, "
            "pytest, pytest-xdist, pytest-timeout, Playwright, Node.js, npm, "
            "admin/standalone/node_modules/. For live phases: .env.local, "
            "ENVIRONMENTS dict, /health reachability."
        ),
        status="specified",
        section="infrastructure_automation",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1618-A1",
                "type": "functional",
                "status": "specified",
                "description": ("Phase 0 fails immediately if Python < 3.12, pytest, or Playwright are not available."),
            },
            {
                "id": "SPEC-1618-A2",
                "type": "functional",
                "status": "specified",
                "description": (
                    "For --phase live/all: Phase 0 validates .env.local credentials and /health endpoint reachability."
                ),
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner specification: fail-fast environment validation",
    )
    print("  SPEC-1618 recorded.")

    # ------------------------------------------------------------------
    # 5. SPEC-1619 — Real-time subprocess output streaming
    # ------------------------------------------------------------------
    print("Recording SPEC-1619...")
    kdb.insert_spec(
        id="SPEC-1619",
        title="Real-time subprocess output streaming",
        description=(
            "All automation scripts (test_pipeline.py, deploy_pipeline.py, "
            "pre_flight_checklist.py) must produce textual output describing "
            "the result of each step/test as it completes, displayed to the "
            "owner in real time as the process proceeds. SHOW EVERYTHING — "
            "no filtering of subprocess output. Implementation: replace "
            "capture_output=True with Popen(stdout=PIPE, stderr=STDOUT) + "
            "threaded line-by-line streaming."
        ),
        status="specified",
        section="infrastructure_automation",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1619-A1",
                "type": "functional",
                "status": "specified",
                "description": (
                    "All subprocess output appears on stdout in real time, line by line, as subprocesses execute."
                ),
            },
            {
                "id": "SPEC-1619-A2",
                "type": "functional",
                "status": "specified",
                "description": ("Output is simultaneously captured for log files and result parsing."),
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner specification: SHOW EVERYTHING in real time",
    )
    print("  SPEC-1619 recorded.")

    # ------------------------------------------------------------------
    # 6. SPEC-1620 — Manual test elimination
    # ------------------------------------------------------------------
    print("Recording SPEC-1620...")
    kdb.insert_spec(
        id="SPEC-1620",
        title="Manual test elimination",
        description=(
            "ALL tests must be automated — no exceptions. Tests which cannot "
            "be scripted must be rewritten so that they are scriptable and may "
            "be executed autonomously. This includes converting GOV-14/15/16 "
            "manual governance checks into automated git diff/log analysis "
            "(producing WARN, not FAIL). The test pipeline Phase 8 automates "
            "governance checks that were previously manual."
        ),
        status="specified",
        section="infrastructure_automation",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1620-A1",
                "type": "functional",
                "status": "specified",
                "description": (
                    "GOV-14 (UI test maintenance) is automated as git diff analysis in test_pipeline.py Phase 8."
                ),
            },
            {
                "id": "SPEC-1620-A2",
                "type": "functional",
                "status": "specified",
                "description": (
                    "GOV-15 (test fix approval) and GOV-16 (deployment approval) "
                    "are automated as git log analysis in Phase 8."
                ),
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner specification: ALL TESTS MUST BE AUTOMATED",
    )
    print("  SPEC-1620 recorded.")

    # ------------------------------------------------------------------
    # 7. Work Items (WI-0939..0944)
    # ------------------------------------------------------------------
    work_items = [
        {
            "id": "WI-0939",
            "title": "Create scripts/test_pipeline.py (SPEC-1616)",
            "description": (
                "Create the 10-phase automated test pipeline orchestrator. "
                "Invokes existing scripts as subprocesses. Supports --env, "
                "--version, --phase, --stop-on-fail. Produces log file and "
                "summary table."
            ),
            "source_spec_id": "SPEC-1616",
            "origin": "new",
            "component": "infrastructure_automation",
        },
        {
            "id": "WI-0940",
            "title": "Add DEFECT auto-creation to pre_flight_checklist.py (SPEC-1617)",
            "description": (
                "Add DEFECT work item creation to pre_flight_checklist.py "
                "for each failed phase, using shared _defect_reporter module."
            ),
            "source_spec_id": "SPEC-1617",
            "origin": "new",
            "component": "infrastructure_automation",
        },
        {
            "id": "WI-0941",
            "title": "Add env var fail-fast to test_pipeline.py Phase 0 (SPEC-1618)",
            "description": (
                "Implement Phase 0 environment validation in test_pipeline.py: "
                "Python 3.12+, pytest, xdist, timeout, Playwright, Node, npm, "
                "node_modules, .env.local, ENVIRONMENTS, /health reachability."
            ),
            "source_spec_id": "SPEC-1618",
            "origin": "new",
            "component": "infrastructure_automation",
        },
        {
            "id": "WI-0942",
            "title": "Convert deploy_pipeline.py to real-time streaming (SPEC-1619)",
            "description": (
                "Replace _run() and _run_shell() in deploy_pipeline.py with "
                "stream_subprocess() from shared _subprocess_stream module. "
                "Extract _create_defect_work_item() to shared _defect_reporter."
            ),
            "source_spec_id": "SPEC-1619",
            "origin": "new",
            "component": "infrastructure_automation",
        },
        {
            "id": "WI-0943",
            "title": "Automate GOV-14/15/16 governance checks (SPEC-1620)",
            "description": (
                "Implement Phase 8 in test_pipeline.py: automated git diff/log "
                "analysis for GOV-14 (UI test maintenance), GOV-15 (test fix "
                "approval), GOV-16 (deployment approval). WARN, not FAIL."
            ),
            "source_spec_id": "SPEC-1620",
            "origin": "new",
            "component": "infrastructure_automation",
        },
        {
            "id": "WI-0944",
            "title": "Create shared helpers: _subprocess_stream.py + _defect_reporter.py",
            "description": (
                "Create two shared helper modules under scripts/: "
                "_subprocess_stream.py (real-time Popen streaming with "
                "simultaneous capture) and _defect_reporter.py (DEFECT WI "
                "creation extracted from deploy_pipeline.py). Both modules "
                "are used by test_pipeline.py, deploy_pipeline.py, and "
                "pre_flight_checklist.py."
            ),
            "source_spec_id": "SPEC-1619",
            "origin": "new",
            "component": "infrastructure_automation",
        },
    ]

    for wi in work_items:
        print(f"Recording {wi['id']}...")
        kdb.insert_work_item(
            id=wi["id"],
            title=wi["title"],
            description=wi["description"],
            source_spec_id=wi["source_spec_id"],
            origin=wi["origin"],
            component=wi["component"],
            resolution_status="open",
            stage="created",
            changed_by=CHANGED_BY,
            change_reason=f"Test & deploy automation overhaul ({SESSION})",
        )
        print(f"  {wi['id']} recorded.")

    # ------------------------------------------------------------------
    # 8. Test Artifacts (TEST-2942..2947) — GOV-12 compliance
    # ------------------------------------------------------------------
    tests = [
        {
            "id": "TEST-2942",
            "spec_id": "SPEC-1616",
            "title": "Test pipeline runs all phases without interaction",
            "description": (
                "Verify scripts/test_pipeline.py runs all 10 phases to "
                "completion without requiring human or Claude interaction. "
                "Exit code 0 on all-PASS, 1 on any FAIL."
            ),
            "expected_outcome": "Exit code 0 when all phases PASS/WARN, exit code 1 on any FAIL",
            "test_type": "integration",
        },
        {
            "id": "TEST-2943",
            "spec_id": "SPEC-1617",
            "title": "DEFECT WIs auto-created on test failure",
            "description": (
                "Verify that when test pipeline phases fail, DEFECT work items "
                "are automatically created in the Knowledge Database with "
                "diagnostic details."
            ),
            "expected_outcome": "One DEFECT WI per failed phase in KB with diagnostic details",
            "test_type": "integration",
        },
        {
            "id": "TEST-2944",
            "spec_id": "SPEC-1618",
            "title": "Phase 0 fails fast on missing prerequisites",
            "description": (
                "Verify that Phase 0 of the test pipeline validates all "
                "required tools and environment variables before any test "
                "execution begins, failing immediately with diagnostics."
            ),
            "expected_outcome": "Phase 0 FAIL with specific diagnostic when prerequisites missing",
            "test_type": "integration",
        },
        {
            "id": "TEST-2945",
            "spec_id": "SPEC-1619",
            "title": "Real-time subprocess output streaming works",
            "description": (
                "Verify that _subprocess_stream.stream_subprocess() outputs "
                "each line to stdout in real time while simultaneously "
                "capturing output for log files and parsing."
            ),
            "expected_outcome": "Lines appear on stdout in real time; captured buffer matches",
            "test_type": "unit",
        },
        {
            "id": "TEST-2946",
            "spec_id": "SPEC-1620",
            "title": "Governance checks automated in Phase 8",
            "description": (
                "Verify that Phase 8 of the test pipeline runs automated "
                "git diff/log analysis for GOV-14, GOV-15, and GOV-16, "
                "producing WARN (not FAIL) on detected issues."
            ),
            "expected_outcome": "Phase 8 produces WARN on governance drift, not FAIL",
            "test_type": "integration",
        },
        {
            "id": "TEST-2947",
            "spec_id": "GOV-17",
            "title": "GOV-17 automation script approval gate",
            "description": (
                "Process assertion: Claude must request owner approval "
                "before modifying any automation script listed in GOV-17."
            ),
            "expected_outcome": "Claude requests approval before modifying automation scripts",
            "test_type": "assertion",
        },
    ]

    # GOV-13: assign to test plan phase
    plan_phases = {
        "integration": "PHASE-002",  # Integration tests
        "unit": "PHASE-001",  # Unit tests
        "assertion": "PHASE-004",  # KB assertion checks
    }

    for t in tests:
        print(f"Recording {t['id']}...")
        kdb.insert_test(
            id=t["id"],
            spec_id=t["spec_id"],
            title=t["title"],
            test_type=t["test_type"],
            expected_outcome=t["expected_outcome"],
            description=t["description"],
            changed_by=CHANGED_BY,
            change_reason=f"GOV-12: WI creation triggers test creation ({SESSION})",
        )
        print(f"  {t['id']} recorded.")

    # Assign tests to plan phases (GOV-13)
    print("\nAssigning tests to plan phases (GOV-13)...")
    plan = kdb.get_active_test_plan()
    if plan:
        phases = kdb.list_test_plan_phases(plan["id"])
        phase_map = {p["id"]: p for p in phases}

        for t in tests:
            phase_id = plan_phases.get(t["test_type"], "PHASE-002")
            phase = phase_map.get(phase_id)
            if phase:
                existing_ids = phase.get("test_ids") or []
                if isinstance(existing_ids, str):
                    import json

                    existing_ids = json.loads(existing_ids)
                if t["id"] not in existing_ids:
                    existing_ids.append(t["id"])
                    kdb.update_test_plan_phase(
                        plan_id=plan["id"],
                        phase_id=phase_id,
                        changed_by=CHANGED_BY,
                        change_reason=f"GOV-13: assign {t['id']} to {phase_id}",
                        test_ids=existing_ids,
                    )
                    print(f"  {t['id']} → {phase_id}")
                else:
                    print(f"  {t['id']} already in {phase_id}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  GOV-17:         Recorded (verified)")
    print(f"  SPEC-1616..1620: 5 specifications recorded (specified)")
    print(f"  WI-0939..0944:  6 work items recorded (open)")
    print(f"  TEST-2942..2947: 6 test artifacts recorded")
    print(f"  Plan phases:    Tests assigned per GOV-13")
    print()


if __name__ == "__main__":
    main()
