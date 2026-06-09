"""Record GOV-15, GOV-16, SPEC-1615, and related work items.

S131: Owner directives on test fix approval, deployment approval,
and automated build/deploy pipeline specification.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
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
    # GOV-15: Test fix approval gate
    # ------------------------------------------------------------------
    print("Recording GOV-15...")
    kdb.insert_spec(
        id="GOV-15",
        title="Test fix approval gate — no autonomous fixes for failed tests",
        description=(
            "Claude MUST NOT initiate implementation of fixes for failed "
            "tests without explicit approval from the owner immediately "
            "prior to initiation. When tests fail, Claude must: (1) report "
            "the failures with diagnostic details, (2) propose a fix "
            "approach, (3) wait for explicit owner approval before making "
            "any code changes. This prevents unintended side effects from "
            "autonomous fixes and ensures the owner retains control over "
            "the correction strategy."
        ),
        status="verified",
        section="GOVERNANCE",
        type="governance",
        assertions=[
            {
                "id": "GOV-15-A1",
                "description": (
                    "Claude must not modify code to fix a failing test "
                    "without explicit owner approval in the same session"
                ),
                "type": "manual",
                "status": "verified",
            },
            {
                "id": "GOV-15-A2",
                "description": (
                    "When tests fail, Claude must report failures with diagnostic information before proposing fixes"
                ),
                "type": "manual",
                "status": "verified",
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner directive: no autonomous test fixes without explicit approval",
    )
    print("  GOV-15 recorded.")

    # ------------------------------------------------------------------
    # GOV-16: Deployment approval gate
    # ------------------------------------------------------------------
    print("Recording GOV-16...")
    kdb.insert_spec(
        id="GOV-16",
        title="Deployment approval gate — no autonomous deployments",
        description=(
            "Claude MUST NOT initiate a deployment to any environment "
            "(staging or production) without explicit approval from the "
            "owner immediately prior to initiation. This includes ACR "
            "Docker builds, container app updates, and any action that "
            "changes what is running in a deployed environment. Claude "
            "must present the deployment plan (version, target environment, "
            "changes included) and wait for explicit owner approval before "
            "proceeding."
        ),
        status="verified",
        section="GOVERNANCE",
        type="governance",
        assertions=[
            {
                "id": "GOV-16-A1",
                "description": (
                    "Claude must not execute az acr build, az containerapp "
                    "update, or equivalent deployment commands without "
                    "explicit owner approval"
                ),
                "type": "manual",
                "status": "verified",
            },
            {
                "id": "GOV-16-A2",
                "description": (
                    "Claude must present deployment plan (version, environment, "
                    "changes) and wait for owner approval before deploying"
                ),
                "type": "manual",
                "status": "verified",
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner directive: no autonomous deployments without explicit approval",
    )
    print("  GOV-16 recorded.")

    # ------------------------------------------------------------------
    # SPEC-1615: Automated build/deploy pipeline
    # ------------------------------------------------------------------
    print("Recording SPEC-1615...")
    kdb.insert_spec(
        id="SPEC-1615",
        title="Automated build/deploy pipeline — scripted, autonomous, no interaction required",
        description=(
            "The process of executing new builds and deployment of new "
            "builds to production or staging environments must be executed "
            "via a scripted, autonomous process which does not require any "
            "interaction with the owner or Claude during the deployment. "
            "When a deployment is completed, the scripted process must "
            "report SUCCESS or FAILURE and include any diagnostic "
            "information needed to identify issues and aid in resolution. "
            "The automated deployment must be tested and all failures must "
            "trigger the creation of DEFECT work items with the automation "
            "as the subject. All environment variables required for the "
            "scripted process to complete successfully must be set before "
            "the automated build/deploy process is initiated."
        ),
        status="specified",
        section="INFRASTRUCTURE",
        type="requirement",
        assertions=[
            {
                "id": "SPEC-1615-A1",
                "description": (
                    "A single script executes the full build/deploy pipeline "
                    "without requiring any human or AI interaction during execution"
                ),
                "type": "e2e",
                "status": "specified",
            },
            {
                "id": "SPEC-1615-A2",
                "description": (
                    "The pipeline reports SUCCESS or FAILURE at completion "
                    "with diagnostic information sufficient to identify issues"
                ),
                "type": "e2e",
                "status": "specified",
            },
            {
                "id": "SPEC-1615-A3",
                "description": (
                    "Pipeline failures trigger creation of DEFECT work items targeting the automation itself"
                ),
                "type": "manual",
                "status": "specified",
            },
            {
                "id": "SPEC-1615-A4",
                "description": (
                    "All required environment variables are validated before "
                    "the pipeline begins execution (fail-fast on missing config)"
                ),
                "type": "e2e",
                "status": "specified",
            },
            {
                "id": "SPEC-1615-A5",
                "description": ("The pipeline supports targeting staging or production environment via parameter"),
                "type": "e2e",
                "status": "specified",
            },
            {
                "id": "SPEC-1615-A6",
                "description": (
                    "The pipeline includes: frontend dist builds (4), ACR "
                    "Docker build, container app deployment, upgrade "
                    "verification, and config pipeline verification"
                ),
                "type": "e2e",
                "status": "specified",
            },
        ],
        changed_by=CHANGED_BY,
        change_reason="Owner specification: automated build/deploy pipeline with no interaction",
    )
    print("  SPEC-1615 recorded.")

    # ------------------------------------------------------------------
    # WI-0937: Implement automated build/deploy pipeline
    # ------------------------------------------------------------------
    print("Recording WI-0937...")
    kdb.insert_work_item(
        id="WI-0937",
        title="Implement automated build/deploy pipeline script",
        description=(
            "Create a single script (e.g., scripts/deploy.py or "
            "scripts/deploy.ps1) that executes the full build/deploy "
            "pipeline autonomously: (1) validate environment variables, "
            "(2) build 4 admin dists + widget, (3) ACR Docker build, "
            "(4) deploy to target environment, (5) run upgrade "
            "verification, (6) run config pipeline tests, (7) report "
            "SUCCESS/FAILURE with diagnostics. Must support --env "
            "staging|production parameter. Must not require interaction."
        ),
        source_spec_id="SPEC-1615",
        origin="new",
        component="infrastructure_automation",
        resolution_status="open",
        stage="created",
        changed_by=CHANGED_BY,
        change_reason="Automated build/deploy pipeline per owner specification",
    )
    print("  WI-0937 recorded.")

    # ------------------------------------------------------------------
    # TEST-2941: Test artifact for automated pipeline
    # ------------------------------------------------------------------
    print("Recording TEST-2941...")
    kdb.insert_test(
        id="TEST-2941",
        spec_id="SPEC-1615",
        title="Automated build/deploy pipeline verification",
        test_type="e2e",
        expected_outcome=(
            "Pipeline script executes full build/deploy cycle without "
            "interaction and reports SUCCESS/FAILURE with diagnostics"
        ),
        test_file="tests/integration/test_deploy_pipeline.py",
        description=(
            "End-to-end test verifying the automated build/deploy pipeline "
            "script: env var validation, build steps, deployment, "
            "verification, and result reporting."
        ),
        changed_by=CHANGED_BY,
        change_reason="Automated build/deploy pipeline test — SPEC-1615",
    )
    print("  TEST-2941 recorded.")

    # ------------------------------------------------------------------
    # Assign TEST-2941 to PHASE-003 (integration tests)
    # ------------------------------------------------------------------
    print("\nAssigning TEST-2941 to PHASE-003 (GOV-13)...")
    phase = kdb.get_test_plan_phase("PHASE-003")
    if phase:
        existing_ids = json.loads(phase["test_ids"]) if phase["test_ids"] else []
        if "TEST-2941" not in existing_ids:
            combined = existing_ids + ["TEST-2941"]
            kdb.update_test_plan_phase(
                id="PHASE-003",
                changed_by=CHANGED_BY,
                change_reason="Add TEST-2941 (automated build/deploy pipeline)",
                test_ids=combined,
            )
            print(f"  PHASE-003 updated: {len(existing_ids)} -> {len(combined)} test IDs")
        else:
            print("  TEST-2941 already in PHASE-003")
    else:
        print("  WARNING: PHASE-003 not found!")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  GOV-15:    Test fix approval gate (2 assertions, verified)")
    print(f"  GOV-16:    Deployment approval gate (2 assertions, verified)")
    print(f"  SPEC-1615: Automated build/deploy pipeline (6 assertions, specified)")
    print(f"  WI-0937:   Implement automated pipeline (open)")
    print(f"  TEST-2941: Pipeline verification test (PHASE-003)")
    print()


if __name__ == "__main__":
    main()
