"""Insert test_coverage mappings for Batch 3 (59 OPS specs): seed_tenant, upgrade_verification, pre_flight, hooks.

Session S112 — Phase C coverage insertion.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB  # noqa: E402

db = KnowledgeDB()
c = db._get_conn()

CREATED_BY = "S112-batch3-coverage"
MAPPINGS: list[tuple[str, str, str | None, str, str, str]] = [
    # (spec_id, test_file, test_class, test_function, confidence, match_reason)

    # ── SEED TENANT (26 specs) ────────────────────────────────────────────
    ("SPEC-1430", "tests/ops/test_seed_tenant_specs.py", "TestDryRunBehavior", "test_phase_0_dry_run_result", "high", "Dry-run partition cleanup"),
    ("SPEC-1431", "tests/ops/test_seed_tenant_specs.py", "TestConstants", "test_tenant_containers_includes_conversations", "high", "Conversations in cleanup list"),
    ("SPEC-1432", "tests/ops/test_seed_tenant_specs.py", "TestPhase5Removed", "test_seed_does_not_call_phase_5", "high", "KB seeding removed"),
    ("SPEC-1433", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_0_exists_and_is_async", "high", "Phase 0 function existence"),
    ("SPEC-1434", "tests/ops/test_seed_tenant_specs.py", "TestOrchestratorOrder", "test_phase_1_runs_before_phase_0", "high", "Phase 1 before Phase 0"),
    ("SPEC-1435", "tests/ops/test_seed_tenant_specs.py", "TestOrchestratorOrder", "test_phase_0_conceptually_precedes_data_creation", "high", "Phase 0 before data phases"),
    ("SPEC-1436", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_0_header", "high", "Phase 0 header text"),
    ("SPEC-1437", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_1_exists_and_is_async", "high", "Phase 1 function existence"),
    ("SPEC-1438", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_1_header", "high", "Phase 1 header text"),
    ("SPEC-1439", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_2_exists_and_is_async", "high", "Phase 2 function existence"),
    ("SPEC-1440", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_2_header", "high", "Phase 2 header text"),
    ("SPEC-1441", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_3_exists_and_is_async", "high", "Phase 3 function existence"),
    ("SPEC-1442", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_3_header", "high", "Phase 3 header text"),
    ("SPEC-1443", "tests/ops/test_seed_tenant_specs.py", "TestPhase2WidgetKey", "test_phase_2_generates_widget_key", "high", "Widget key generation"),
    ("SPEC-1444", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_4_exists_and_is_async", "high", "Phase 4 function existence"),
    ("SPEC-1445", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_4_header", "high", "Phase 4 header text"),
    ("SPEC-1446", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_5_exists_and_is_async", "high", "Phase 5 function existence"),
    ("SPEC-1447", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_5_header", "high", "Phase 5 header text"),
    ("SPEC-1448", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_6_exists_and_is_async", "high", "Phase 6 function existence"),
    ("SPEC-1449", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_6_header", "high", "Phase 6 header text"),
    ("SPEC-1450", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_7_exists_and_is_async", "high", "Phase 7 function existence"),
    ("SPEC-1451", "tests/ops/test_seed_tenant_specs.py", "TestPhaseHeaders", "test_phase_7_header", "high", "Phase 7 header text"),
    ("SPEC-1452", "tests/ops/test_seed_tenant_specs.py", "TestPhaseFunctions", "test_phase_8_exists_and_is_sync", "high", "Phase 8 function existence"),
    ("SPEC-1453", "tests/ops/test_seed_tenant_specs.py", "TestPrintSeparator", "test_phase_8_prints_separator_lines", "high", "Print separator lines"),
    ("SPEC-1454", "tests/ops/test_seed_tenant_specs.py", "TestPhase5Removed", "test_seed_source_has_phase_5_removal_comment", "high", "KB removal comment"),
    ("SPEC-1455", "tests/ops/test_seed_tenant_specs.py", "TestOrchestratorOrder", "test_phase_4_runs_after_phase_7", "high", "Phase 4 after Phase 7"),

    # ── UPGRADE VERIFICATION (9 specs) ───────────────────────────────────
    ("SPEC-1456", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseAAndC", "test_phase_a_exists", "high", "Phase A+C existence"),
    ("SPEC-1457", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseASnapshot", "test_phase_a_returns_dict", "high", "Phase A snapshot dict"),
    ("SPEC-1458", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseAHeader", "test_phase_a_prints_header", "high", "Phase A header text"),
    ("SPEC-1459", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseCVerification", "test_phase_c_returns_list", "high", "Phase C returns list"),
    ("SPEC-1460", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseCCallCount", "test_phase_c_makes_many_api_calls", "high", "Phase C API call count"),
    ("SPEC-1461", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseCHeader", "test_phase_c_prints_header", "high", "Phase C header text"),
    ("SPEC-1462", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseASnapshotJSON", "test_snapshot_is_json_serializable", "high", "Snapshot JSON format"),
    ("SPEC-1463", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseAIteratesTenants", "test_all_tenants_includes_extra", "high", "Phase A multi-tenant"),
    ("SPEC-1464", "tests/ops/test_upgrade_verification_specs.py", "TestPhaseCIteratesTenants", "test_all_tenants_preserves_fqdn", "high", "Phase C multi-tenant"),

    # ── PRE-FLIGHT CHECKLIST (22 specs) ──────────────────────────────────
    ("SPEC-1465", "tests/ops/test_pre_flight_specs.py", "TestPhaseASourceLevel", "test_phase_a_is_callable", "high", "Phase A callable"),
    ("SPEC-1466", "tests/ops/test_pre_flight_specs.py", "TestPhaseDSSE", "test_httpx_available_flag_exists", "high", "SSE streaming flag"),
    ("SPEC-1467", "tests/ops/test_pre_flight_specs.py", "TestPhaseAPreBuild", "test_phase_a_version_match", "high", "Phase A version check"),
    ("SPEC-1468", "tests/ops/test_pre_flight_specs.py", "TestPhaseCPostDeploy", "test_phase_c_is_callable", "high", "Phase C callable"),
    ("SPEC-1469", "tests/ops/test_pre_flight_specs.py", "TestPhaseASnapshotCheck", "test_c10_skip_when_no_snapshot", "high", "Snapshot existence check"),
    ("SPEC-1470", "tests/ops/test_pre_flight_specs.py", "TestPhaseASnapshotCheck", "test_c10_skip_when_no_snapshot", "medium", "Snapshot path reference"),
    ("SPEC-1471", "tests/ops/test_pre_flight_specs.py", "TestPhaseCApiCallCount", "test_phase_c_makes_multiple_api_calls", "high", "C.1-C.10 API call count"),
    ("SPEC-1472", "tests/ops/test_pre_flight_specs.py", "TestPhaseDProvisioning", "test_phase_d_is_callable", "high", "Phase D callable"),
    ("SPEC-1473", "tests/ops/test_pre_flight_specs.py", "TestPhaseDWithoutCredentials", "test_d1_failure_skips_remaining", "high", "D.1 failure cascades"),
    ("SPEC-1474", "tests/ops/test_pre_flight_specs.py", "TestPhaseDSummary", "test_d18_summary_result", "high", "D.18 summary computation"),
    ("SPEC-1475", "tests/ops/test_pre_flight_specs.py", "TestVerdictPhaseA", "test_a_failure_blocks_deployment", "high", "Phase A failure verdict"),
    ("SPEC-1476", "tests/ops/test_pre_flight_specs.py", "TestVerdictPhaseC", "test_c_failure_requires_rollback", "high", "Phase C failure verdict"),
    ("SPEC-1477", "tests/ops/test_pre_flight_specs.py", "TestVerdictPhaseD", "test_d_failure_is_defective", "high", "Phase D failure verdict"),
    ("SPEC-1478", "tests/ops/test_pre_flight_specs.py", "TestPhaseDEnvKey", "test_spa_key_from_environment", "high", "SPA key from env"),
    ("SPEC-1479", "tests/ops/test_pre_flight_specs.py", "TestPhaseSelection", "test_default_phases_include_a", "high", "Phase A in default"),
    ("SPEC-1480", "tests/ops/test_pre_flight_specs.py", "TestPhaseBManual", "test_phase_b_prints_manual_reminder", "high", "Phase B manual reminder"),
    ("SPEC-1481", "tests/ops/test_pre_flight_specs.py", "TestPhaseBLabel", "test_phase_b_labeled_build_deploy", "high", "Phase B label"),
    ("SPEC-1482", "tests/ops/test_pre_flight_specs.py", "TestPhaseBExecution", "test_phase_b_mentions_manual_execution", "high", "Phase B manual note"),
    ("SPEC-1483", "tests/ops/test_pre_flight_specs.py", "TestPhaseASnapshotIntegration", "test_phase_a_references_upgrade_verification", "high", "Snapshot integration"),
    ("SPEC-1484", "tests/ops/test_pre_flight_specs.py", "TestPhaseSelection", "test_default_phases_include_c", "high", "Phase C in default"),
    ("SPEC-1485", "tests/ops/test_pre_flight_specs.py", "TestPhaseSelection", "test_default_phases_include_d", "high", "Phase D in default"),
    ("SPEC-1486", "tests/ops/test_pre_flight_specs.py", "TestPhaseDRequiresSPAKey", "test_phase_d_requires_spa_key", "high", "SPA key required"),

    # ── HOOKS (2 specs) ──────────────────────────────────────────────────
    ("SPEC-1487", "tests/ops/test_hooks_specs.py", "TestAssertionCheckHook", "test_hook_file_exists", "high", "Hook file existence"),
    ("SPEC-1488", "tests/ops/test_hooks_specs.py", "TestSchedulerHook", "test_hook_file_exists", "high", "Hook file existence"),
]


def main() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    skipped = 0

    for spec_id, test_file, test_class, test_func, confidence, reason in MAPPINGS:
        existing = c.execute(
            "SELECT 1 FROM test_coverage WHERE spec_id = ? AND test_function = ?",
            (spec_id, test_func),
        ).fetchone()
        if existing:
            skipped += 1
            continue

        c.execute(
            """INSERT INTO test_coverage
               (spec_id, test_file, test_class, test_function, confidence, match_reason, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (spec_id, test_file, test_class, test_func, confidence, reason, now, CREATED_BY),
        )
        inserted += 1

    c.commit()

    total_coverage = c.execute(
        "SELECT COUNT(DISTINCT spec_id) FROM test_coverage"
    ).fetchone()[0]
    total_specs = c.execute(
        "SELECT COUNT(DISTINCT id) FROM specifications WHERE status != 'retired'"
    ).fetchone()[0]

    print(f"Inserted: {inserted}, Skipped (already exist): {skipped}")
    print(f"Total coverage: {total_coverage}/{total_specs} specs ({100*total_coverage/total_specs:.1f}%)")


if __name__ == "__main__":
    main()
