"""
S114 Data Migration: Populate tests table and test_plans/test_plan_phases from legacy data.

Migration 1: test_coverage → tests table
  - Each unique (test_file, test_class, test_function) → one TEST-NNNN artifact
  - spec_id = primary spec (highest confidence, or first by rowid)
  - test_type inferred from file path
  - test_coverage table retained as many-to-many supplement

Migration 2: Master Test Plan markdown → test_plans + test_plan_phases
  - One test plan: PLAN-001 "Master Test Plan 1.0 GA"
  - 16 phases from the markdown document

Migration 3: Operational procedures from markdown → operational_procedures table
  - Only procedures not already in the DB

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import io
import json
from pathlib import Path

# Windows UTF-8 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add knowledge-db to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB

CHANGED_BY = "S114-migration"


def infer_test_type(test_file: str) -> str:
    """Infer test type from file path."""
    path = test_file.replace("\\", "/")
    if "/unit/" in path:
        return "unit"
    if "/e2e/" in path:
        return "e2e"
    if "/regression/" in path:
        return "regression"
    if "/security/" in path:
        return "security"
    if "/performance/" in path:
        return "performance"
    if "/visual/" in path:
        return "e2e"
    if "/integration/" in path or "/integrations/" in path:
        return "integration"
    if "/widget/" in path:
        return "unit"  # source inspection tests
    # Default for multi_tenant, agents, chat, persistent_memory
    if "/multi_tenant/" in path or "/agents/" in path:
        return "unit"
    if "/chat/" in path or "/persistent_memory/" in path:
        return "integration"
    return "unit"


def make_title(test_file: str, test_class: str | None, test_function: str) -> str:
    """Create a human-readable title from test location."""
    module = Path(test_file).stem.replace("test_", "").replace("_", " ").title()
    fn = test_function.replace("test_", "").replace("_", " ")
    if test_class:
        cls = test_class.replace("Test", "").replace("_", " ")
        return f"{module}: {cls} — {fn}"
    return f"{module}: {fn}"


def migrate_tests(db: KnowledgeDB, *, dry_run: bool = False) -> int:
    """Migration 1: test_coverage → tests table."""
    conn = db._get_conn()

    # Check if already migrated
    existing = conn.execute("SELECT COUNT(*) FROM current_tests").fetchone()[0]
    if existing > 0:
        print(f"  ⚠ tests table already has {existing} entries — skipping migration 1")
        return 0

    # Get unique test functions with their primary spec
    # Primary = highest confidence first, then lowest rowid (earliest mapping)
    rows = conn.execute("""
        SELECT test_file, test_class, test_function, spec_id, confidence,
               MIN(rowid) as first_rowid
        FROM test_coverage
        GROUP BY test_file, test_class, test_function
        ORDER BY
            CASE confidence WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            MIN(rowid)
    """).fetchall()

    # For functions that appear multiple times (different specs), pick the best one
    seen = {}  # (file, class, func) → best row
    for r in rows:
        key = (r["test_file"], r["test_class"], r["test_function"])
        if key not in seen:
            seen[key] = dict(r)

    # Now get ALL mappings to find the primary spec for each test function
    # (highest confidence, then earliest rowid)
    all_mappings = conn.execute("""
        SELECT test_file, test_class, test_function, spec_id, confidence, rowid
        FROM test_coverage
        ORDER BY
            test_file, test_class, test_function,
            CASE confidence WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            rowid
    """).fetchall()

    primary_spec = {}  # (file, class, func) → best spec_id
    for r in all_mappings:
        key = (r["test_file"], r["test_class"], r["test_function"])
        if key not in primary_spec:
            primary_spec[key] = r["spec_id"]

    unique_tests = sorted(primary_spec.keys())
    print(f"  Found {len(unique_tests)} unique test functions to migrate")

    if dry_run:
        print("  [DRY RUN] Would create test artifacts — skipping")
        return len(unique_tests)

    count = 0
    for i, (test_file, test_class, test_function) in enumerate(unique_tests, 1):
        test_id = f"TEST-{i:04d}"
        spec_id = primary_spec[(test_file, test_class, test_function)]
        test_type = infer_test_type(test_file)
        title = make_title(test_file, test_class, test_function)

        db.insert_test(
            id=test_id,
            title=title,
            spec_id=spec_id,
            test_type=test_type,
            expected_outcome="PASS — test function completes without assertion error",
            changed_by=CHANGED_BY,
            change_reason="Migrated from test_coverage table (S114)",
            test_file=test_file,
            test_class=test_class,
            test_function=test_function,
        )
        count += 1

        if count % 200 == 0:
            print(f"    ... migrated {count}/{len(unique_tests)} tests")

    print(f"  ✓ Created {count} test artifacts (TEST-0001 through TEST-{count:04d})")
    return count


def migrate_test_plan(db: KnowledgeDB, *, dry_run: bool = False) -> int:
    """Migration 2: Master Test Plan markdown → test_plans + test_plan_phases."""
    conn = db._get_conn()

    # Check if already migrated
    existing = conn.execute("SELECT COUNT(*) FROM current_test_plans").fetchone()[0]
    if existing > 0:
        print(f"  ⚠ test_plans table already has {existing} entries — skipping migration 2")
        return 0

    if dry_run:
        print("  [DRY RUN] Would create test plan + 16 phases — skipping")
        return 1

    # Create the Master Test Plan
    db.insert_test_plan(
        id="PLAN-001",
        title="Master Test Plan — Agent Red 1.0 GA",
        status="active",
        changed_by=CHANGED_BY,
        change_reason="Migrated from docs/MASTER-TEST-PLAN-1.0.md (S114)",
        description=(
            "Single canonical test plan for the Agent Red Customer Experience 1.0 release. "
            "Synthesizes all testable requirements from 8 source documents into 16 ordered "
            "execution phases. All phases must pass for the release gate to clear."
        ),
    )

    # Define the 16 phases from the Master Test Plan
    phases = [
        {
            "id": "PHASE-001",
            "order": 1,
            "title": "Pre-flight Checks",
            "description": "Verify environment readiness: Python/pytest installed, API Gateway healthy/ready, test collection count.",
            "gate": "4/4 checks pass",
        },
        {
            "id": "PHASE-002",
            "order": 2,
            "title": "Unit & Integration Tests (Thermal-Safe)",
            "description": "Full Python test suite via thermal-safe harness. 5 batches: core-a (~2400), core-b (~700), agents-chat (~600), integrations (~400), sequential (~100).",
            "gate": "0 failures across all batches, coverage >= 70%",
        },
        {
            "id": "PHASE-003",
            "order": 3,
            "title": "Production Regression",
            "description": "Regression suites against live production: migration compat (30), T0 core API (18), T1 comprehensive (28), T2 performance (10).",
            "gate": "86/86 PASS (MC 30 + T0 18 + T1 28 + T2 10)",
        },
        {
            "id": "PHASE-004",
            "order": 4,
            "title": "External URL Reachability",
            "description": "Verify all 37 external URLs (API endpoints, admin SPAs, widget JS, docs site, storefront) are reachable and return expected content.",
            "gate": "37/37 PASS",
        },
        {
            "id": "PHASE-005",
            "order": 5,
            "title": "Tenant Isolation",
            "description": "Verify two tenants (remaker-digital-001, test-customer-001) cannot read/modify/delete each other's data across all API endpoints.",
            "gate": "30/30 PASS",
        },
        {
            "id": "PHASE-006",
            "order": 6,
            "title": "API Security & Penetration Testing",
            "description": "Auth bypass, injection, header manipulation, CORS, rate limit enforcement, privilege escalation across 45 test cases.",
            "gate": "45/45 PASS",
        },
        {
            "id": "PHASE-007",
            "order": 7,
            "title": "Rate Limiting & DoS Resilience",
            "description": "Per-tier rate limit enforcement (professional: 50 rpm, starter: 10 rpm), burst handling, graceful 429 responses.",
            "gate": "18+ PASS, 0 FAIL (RL-02/RL-05 may SKIP due to window state)",
        },
        {
            "id": "PHASE-008",
            "order": 8,
            "title": "Data Integrity & Backup Verification",
            "description": "Cosmos DB data consistency, partition key isolation, document schema compliance, backup policy across all tenant containers.",
            "gate": "25/25 PASS",
        },
        {
            "id": "PHASE-009",
            "order": 9,
            "title": "Resilience & Failover",
            "description": "Graceful degradation when Azure OpenAI, Cosmos DB, Key Vault, NATS, and Stripe are unavailable or degraded.",
            "gate": "29/29 PASS + 6 SKIP (infrastructure dependencies not simulatable in production)",
        },
        {
            "id": "PHASE-010",
            "order": 10,
            "title": "Load Testing",
            "description": "50 concurrent simulated users. SLA thresholds: P95 <= 2000ms admin, P95 <= 5000ms chat, error rate < 1%, zero 500s from auth/config.",
            "gate": "All SLA thresholds met",
        },
        {
            "id": "PHASE-011",
            "order": 11,
            "title": "Conversation Quality",
            "description": "25 golden conversation scenarios against live AI pipeline. Scored on faithfulness, relevancy, tone, overall (1-5 scale).",
            "gate": "Pilot VERDICT = PASS (Faithfulness >= 3.5, Relevancy >= 3.5, Tone >= 3.0, Overall >= 3.5), pipeline errors <= 2",
        },
        {
            "id": "PHASE-012",
            "order": 12,
            "title": "UI Regression",
            "description": "917 browser-automated tests: standalone admin (780), provider admin (23), Shopify embedded (76 + 38 deferred).",
            "gate": ">= 793 PASS, 0 FAIL (SOFT-PASS <= 5 and SKIP <= 62 accepted)",
        },
        {
            "id": "PHASE-013",
            "order": 13,
            "title": "SPA Provisioning + Critical Path",
            "description": "Full tenant lifecycle: SPA provisioning (CP.P1-P4) then merchant first-use journey (CP.1-CP.21). 25 total steps.",
            "gate": "25/25 PASS (4 provisioning + 21 critical path)",
        },
        {
            "id": "PHASE-014",
            "order": 14,
            "title": "Upgrade Verification",
            "description": "Deploy no-change version bump, verify 35 post-deployment assertions match pre-deployment snapshot. Validates release plan Step 6.",
            "gate": "35/35 assertions match",
        },
        {
            "id": "PHASE-015",
            "order": 15,
            "title": "Manual Verification",
            "description": "8 items: Lighthouse widget impact, Chrome incognito, plan upgrade/downgrade, screencast, app icon, screenshots, privacy policy, testing instructions.",
            "gate": "8/8 documented with evidence",
        },
        {
            "id": "PHASE-016",
            "order": 16,
            "title": "Widget Visual Regression",
            "description": "Automated structural and CSS property tests. Layer 1: DOM structure (~16 assertions), Layer 2: CSS properties (~14 assertions). Playwright headless browser.",
            "gate": ">= 30 PASS, 0 FAIL",
        },
    ]

    for phase in phases:
        db.insert_test_plan_phase(
            id=phase["id"],
            plan_id="PLAN-001",
            phase_order=phase["order"],
            title=phase["title"],
            gate_criteria=phase["gate"],
            changed_by=CHANGED_BY,
            change_reason="Migrated from docs/MASTER-TEST-PLAN-1.0.md (S114)",
            description=phase["description"],
        )

    print(f"  ✓ Created test plan PLAN-001 with {len(phases)} phases")
    return 1


def migrate_operational_procedures(db: KnowledgeDB, *, dry_run: bool = False) -> int:
    """Migration 3: Remaining operational procedures from markdown → DB."""
    conn = db._get_conn()

    existing_ids = {r["id"] for r in conn.execute("SELECT id FROM current_operational_procedures").fetchall()}
    print(f"  Existing operational procedures: {existing_ids}")

    # Procedures from REPEATABLE-PROCEDURES.md not yet in the DB
    # (4 already exist: build-deploy, initialization, seed-tenant, upgrade-verification)
    new_procedures = [
        {
            "id": "deploy-rollback",
            "title": "Production Rollback Procedure",
            "type": "deploy",
            "steps": [
                {"step": 1, "action": "Identify previous stable revision", "verify": "az containerapp revision list"},
                {"step": 2, "action": "Activate previous revision", "verify": "az containerapp revision activate"},
                {"step": 3, "action": "Deactivate failing revision", "verify": "Health check returns 200"},
            ],
        },
        {
            "id": "external-url-reachability",
            "title": "External URL Reachability Procedure",
            "type": "test",
            "steps": [
                {"step": 1, "action": "Test 37 external URLs", "verify": "All return expected status codes"},
            ],
        },
        {
            "id": "chrome-ui-test",
            "title": "Chrome-Automated UI Test Procedure",
            "type": "test",
            "steps": [
                {"step": 1, "action": "Run 917 browser-automated tests", "verify": ">= 793 PASS, 0 FAIL"},
            ],
        },
        {
            "id": "session-wrap-up",
            "title": "Session Wrap-Up Procedure",
            "type": "operational",
            "steps": [
                {"step": 1, "action": "Update KB/MEMORY/CLAUDE", "verify": "All files current"},
                {"step": 2, "action": "Verify procedures", "verify": "No stale references"},
                {"step": 3, "action": "External updates", "verify": "Wiki/docs current"},
                {"step": 4, "action": "Staging deploy (risk gate)", "verify": "If applicable"},
                {"step": 5, "action": "Generate handoff prompt", "verify": "session_prompts table updated"},
            ],
        },
        {
            "id": "pre-flight-deployment",
            "title": "Pre-Flight Deployment Checklist",
            "type": "deploy",
            "steps": [
                {"step": 1, "action": "Phase A: Environment checks", "verify": "All green"},
                {"step": 2, "action": "Phase B: Build verification", "verify": "All builds pass"},
                {"step": 3, "action": "Phase C: Platform checks (10 assertions)", "verify": "10/10 PASS"},
                {"step": 4, "action": "Phase D: Tenant provisioning (18 assertions)", "verify": "18/18 PASS"},
                {"step": 5, "action": "Phase E: Final gate", "verify": "Approve for deploy"},
            ],
        },
        {
            "id": "catastrophic-recovery",
            "title": "Azure Environment Catastrophic Recovery Runbook",
            "type": "operational",
            "steps": [
                {"step": 1, "action": "Recreate Azure resources from Terraform", "verify": "All resources provisioned"},
                {"step": 2, "action": "Restore Cosmos DB from backup", "verify": "Data integrity verified"},
                {"step": 3, "action": "Redeploy Container App", "verify": "Health/ready endpoints pass"},
            ],
        },
        {
            "id": "agntcy-platform-adoption",
            "title": "AGNTCY Platform Adoption Procedure",
            "type": "operational",
            "steps": [
                {"step": 1, "action": "Review AGNTCY public repo for changes", "verify": "Change log reviewed"},
                {"step": 2, "action": "Assess impact on Agent Red agent modules", "verify": "Impact documented"},
            ],
        },
    ]

    count = 0
    for proc in new_procedures:
        if proc["id"] in existing_ids:
            print(f"    ⚠ {proc['id']} already exists — skipping")
            continue
        if dry_run:
            print(f"    [DRY RUN] Would create {proc['id']}")
            count += 1
            continue
        db.insert_op_procedure(
            id=proc["id"],
            title=proc["title"],
            changed_by=CHANGED_BY,
            change_reason="Migrated from REPEATABLE-PROCEDURES.md (S114)",
            type=proc["type"],
            steps=proc["steps"],
        )
        count += 1
        print(f"    ✓ Created operational procedure: {proc['id']}")

    print(f"  ✓ Created {count} new operational procedures")
    return count


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN MODE ===\n")

    db = KnowledgeDB()

    print("=" * 60)
    print("S114 Artifact Migration")
    print("=" * 60)

    # Migration 1: tests
    print("\n--- Migration 1: test_coverage → tests table ---")
    test_count = migrate_tests(db, dry_run=dry_run)

    # Migration 2: test plan
    print("\n--- Migration 2: Master Test Plan → test_plans + test_plan_phases ---")
    plan_count = migrate_test_plan(db, dry_run=dry_run)

    # Migration 3: operational procedures
    print("\n--- Migration 3: Operational procedures ---")
    op_count = migrate_operational_procedures(db, dry_run=dry_run)

    # Summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"  Test artifacts created:        {test_count}")
    print(f"  Test plans created:            {plan_count}")
    print(f"  Operational procedures added:  {op_count}")

    if not dry_run:
        summary = db.get_summary()
        print(f"\n  Post-migration DB summary:")
        print(f"    Specifications:     {summary['spec_total']}")
        print(f"    Test artifacts:     {summary['test_artifact_count']}")
        print(f"    Test plans:         {summary['test_plan_count']}")
        print(f"    Test plan phases:   {summary['test_plan_phase_count']}")
        print(f"    Test procedures:    {summary['test_procedure_count']}")
        print(f"    Op procedures:      {summary['op_procedure_count']}")
        print(f"    Documents:          {summary['document_count']}")
        print(f"    Assertions:         {summary['assertions_passed']}/{summary['assertions_total']} PASS")

    db.close()
    print("\n✓ Migration complete.")


if __name__ == "__main__":
    main()
