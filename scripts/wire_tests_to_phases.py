"""Wire 1,868 test artifacts to their appropriate Master Test Plan phases.

Phase assignment rules based on file path, test type, and title keywords.
Each test is assigned to exactly one phase (primary match).
"""

import sys, io, json, re
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()
conn = kdb._get_conn()

# Get all current test artifacts
rows = conn.execute(
    "SELECT t.id, t.title, t.spec_id, t.test_type, t.test_file, t.test_class, t.test_function "
    "FROM tests t "
    "INNER JOIN (SELECT id, MAX(version) as max_v FROM tests GROUP BY id) m "
    "ON t.id = m.id AND t.version = m.max_v "
    "ORDER BY t.id"
).fetchall()

tests = [dict(r) for r in rows]
print(f"Total test artifacts to assign: {len(tests)}")


# Phase assignment rules (evaluated in order; first match wins)
# Each rule is: (phase_id, description, match_function)
def make_path_matcher(*fragments):
    """Match if any fragment appears in the file path (case-insensitive)."""

    def matcher(t):
        f = (t.get("test_file") or "").lower().replace("\\", "/")
        return any(frag in f for frag in fragments)

    return matcher


def make_path_and_title_matcher(path_frags=None, title_frags=None):
    """Match on path OR title fragments."""

    def matcher(t):
        f = (t.get("test_file") or "").lower().replace("\\", "/")
        title = (t.get("title") or "").lower()
        if path_frags and any(frag in f for frag in path_frags):
            return True
        if title_frags and any(frag in title for frag in title_frags):
            return True
        return False

    return matcher


# ============================================================
# PHASE ASSIGNMENT RULES
# Evaluated in order from most specific to least specific.
# Each test is assigned to exactly one phase (first match wins).
# ============================================================

rules = [
    # PHASE-001: Pre-flight Checks
    # Pre-flight scripts, environment validation, health checks
    (
        "PHASE-001",
        "Pre-flight Checks",
        make_path_and_title_matcher(
            path_frags=[
                "test_pre_flight",
                "test_health.py",
                "test_env_loader.py",
                "test_conftest_smoke.py",
                "test_conftest_fixtures.py",
            ],
            title_frags=[
                "pre-flight",
                "preflight",
                "health endpoint",
                "env loader",
                "conftest smoke",
                "conftest fixture",
            ],
        ),
    ),
    # PHASE-016: Widget Visual Regression
    # Visual regression tests for the widget
    ("PHASE-016", "Widget Visual Regression", make_path_matcher("tests/visual/")),
    # PHASE-010: Load Testing / Performance
    ("PHASE-010", "Load Testing", lambda t: t.get("test_type") == "performance"),
    # PHASE-003: Production Regression
    ("PHASE-003", "Production Regression", lambda t: t.get("test_type") == "regression"),
    # PHASE-007: Rate Limiting & DoS Resilience
    (
        "PHASE-007",
        "Rate Limiting & DoS Resilience",
        make_path_and_title_matcher(
            path_frags=["test_rate_limit", "test_abuse_detection"],
            title_frags=["rate limit", "rate-limit", "dos ", "abuse detection", "throttl"],
        ),
    ),
    # PHASE-005: Tenant Isolation (specific isolation tests)
    (
        "PHASE-005",
        "Tenant Isolation",
        make_path_and_title_matcher(
            path_frags=["test_multi_tenant_isolation", "test_tenant_isolation_live"],
            title_frags=["tenant isolation", "cross-tenant", "partition key isolation"],
        ),
    ),
    # PHASE-006: API Security & Penetration Testing
    ("PHASE-006", "API Security & Penetration Testing", lambda t: t.get("test_type") == "security"),
    # PHASE-008: Data Integrity & Backup Verification
    (
        "PHASE-008",
        "Data Integrity & Backup Verification",
        make_path_and_title_matcher(
            path_frags=[
                "test_data_integrity",
                "test_backup",
                "test_cosmos_repository",
                "test_repository_classes",
                "test_knowledge_repository",
                "test_preferences_repository",
            ],
            title_frags=["data integrity", "backup", "repository"],
        ),
    ),
    # PHASE-014: Upgrade Verification
    (
        "PHASE-014",
        "Upgrade Verification",
        make_path_and_title_matcher(
            path_frags=["test_upgrade", "test_config_pipeline_live"],
            title_frags=["upgrade verification", "config pipeline live"],
        ),
    ),
    # PHASE-011: Conversation Quality
    (
        "PHASE-011",
        "Conversation Quality",
        make_path_and_title_matcher(
            path_frags=["tests/evaluation/", "test_conversation_quality", "test_critic_supervisor"],
            title_frags=["conversation quality", "quality score", "critic supervisor", "evaluation"],
        ),
    ),
    # PHASE-009: Resilience & Failover
    (
        "PHASE-009",
        "Resilience & Failover",
        make_path_and_title_matcher(
            path_frags=["test_error_handling.py", "test_cross_module.py"],
            title_frags=["resilience", "failover", "error handling", "cross-module", "graceful"],
        ),
    ),
    # PHASE-004: External URL Reachability
    (
        "PHASE-004",
        "External URL Reachability",
        make_path_and_title_matcher(
            path_frags=["test_external_url", "test_reachab"], title_frags=["url reachab", "external url"]
        ),
    ),
    # PHASE-013: SPA Provisioning + Critical Path
    (
        "PHASE-013",
        "SPA Provisioning + Critical Path",
        make_path_and_title_matcher(
            path_frags=["test_seed_tenant", "test_provision", "test_activation_service"],
            title_frags=["provisioning", "seed tenant", "activation service", "critical path"],
        ),
    ),
    # PHASE-012: UI Regression (E2E page tests + widget E2E)
    (
        "PHASE-012",
        "UI Regression",
        make_path_and_title_matcher(path_frags=["tests/e2e/", "tests/widget/"], title_frags=[]),
    ),
    # PHASE-002: Unit & Integration Tests (everything else)
    # This is the catch-all for unit and integration tests not matched above
    ("PHASE-002", "Unit & Integration Tests (Thermal-Safe)", lambda t: t.get("test_type") in ("unit", "integration")),
]


# ============================================================
# EXECUTE ASSIGNMENT
# ============================================================

phase_assignments = defaultdict(list)  # phase_id -> [test_id, ...]
unassigned = []

for t in tests:
    assigned = False
    for phase_id, phase_name, matcher in rules:
        if matcher(t):
            phase_assignments[phase_id].append(t["id"])
            assigned = True
            break
    if not assigned:
        unassigned.append(t)

# Report
print("\n=== PHASE ASSIGNMENT RESULTS ===")
total_assigned = 0
for phase_id in [f"PHASE-{i:03d}" for i in range(1, 17)]:
    count = len(phase_assignments.get(phase_id, []))
    total_assigned += count
    # Get phase title
    phase = None
    for pid, pname, _ in rules:
        if pid == phase_id:
            phase = pname
            break
    print(f"  {phase_id}: {count:5d} tests  ({phase or '?'})")

print(f"\n  Total assigned: {total_assigned}")
print(f"  Unassigned: {len(unassigned)}")
if unassigned:
    print("\n  Unassigned tests:")
    for t in unassigned[:10]:
        print(f"    {t['id']} | type={t['test_type']} | file={t.get('test_file', '?')}")

# ============================================================
# DRY RUN vs EXECUTE
# ============================================================

if "--execute" not in sys.argv:
    print("\n[DRY RUN] Pass --execute to write phase linkages to DB")
    kdb.close()
    sys.exit(0)

print("\n=== WRITING PHASE LINKAGES ===")
phases = kdb.list_test_plan_phases("PLAN-001")
for phase in phases:
    phase_id = phase["id"]
    test_ids = sorted(phase_assignments.get(phase_id, []))
    if test_ids:
        # Pass raw list — update_test_plan_phase handles json.dumps internally
        kdb.update_test_plan_phase(
            phase_id,
            changed_by="S115",
            change_reason=f"Wire {len(test_ids)} test artifacts to phase (S115 linkage, corrected)",
            test_ids=test_ids,
        )
        print(f"  {phase_id}: linked {len(test_ids)} tests")
    else:
        print(f"  {phase_id}: no tests to link (operational phase)")

print("\nDone. Phase linkage complete.")
kdb.close()
