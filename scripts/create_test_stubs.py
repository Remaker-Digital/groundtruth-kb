"""Create test stub artifacts for all untested specifications and wire them into test plan phases.

For each spec with no linked test artifact (excluding retired), creates a test stub
and assigns it to the appropriate phase based on the spec's section.

Usage:
    python scripts/create_test_stubs.py          # dry run
    python scripts/create_test_stubs.py --execute # write to DB
"""

import sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")
import db

from collections import Counter, defaultdict

# Section -> test_type mapping
SECTION_TO_TEST_TYPE = {
    "ADMIN_UI": "e2e",
    "WIDGET_UI": "e2e",
    "AUTH": "unit",
    "CONFIG": "unit",
    "EMAIL": "integration",
    "AGENTS": "unit",
    "INFRA": "unit",
    "OPS": "unit",
    "TESTING": "unit",
    "API": "integration",
    "BILLING": "unit",
    "CONVERSATIONS": "integration",
    "PROVISIONING": "integration",
    "KNOWLEDGE_BASE": "integration",
    "TEAM": "unit",
    "SHOPIFY": "integration",
    "DOCS": "unit",
    "GOVERNANCE": "unit",
    "GENERAL": "unit",
}

# Section -> default phase (matching wire_tests_to_phases.py logic)
SECTION_TO_PHASE = {
    "ADMIN_UI": "PHASE-012",
    "WIDGET_UI": "PHASE-012",
    "AUTH": "PHASE-002",
    "CONFIG": "PHASE-002",
    "EMAIL": "PHASE-002",
    "AGENTS": "PHASE-002",
    "INFRA": "PHASE-002",
    "OPS": "PHASE-001",
    "TESTING": "PHASE-002",
    "API": "PHASE-002",
    "BILLING": "PHASE-002",
    "CONVERSATIONS": "PHASE-002",
    "PROVISIONING": "PHASE-013",
    "KNOWLEDGE_BASE": "PHASE-002",
    "TEAM": "PHASE-002",
    "SHOPIFY": "PHASE-002",
    "DOCS": "PHASE-002",
    "GOVERNANCE": "PHASE-002",
    "GENERAL": "PHASE-002",
}


# Override phase for special spec types/titles
def infer_phase(spec):
    """Assign phase based on spec metadata. Mirrors wire_tests_to_phases.py logic."""
    section = spec.get("section", "")
    title = (spec.get("title") or "").lower()
    spec_id = spec.get("id", "")

    # GOV specs -> PHASE-002 (unit tests for governance)
    if spec_id.startswith("GOV-"):
        return "PHASE-002"

    # PB (Protected Behaviors) -> PHASE-003 (regression)
    if spec_id.startswith("PB-"):
        return "PHASE-003"

    # Security-related keywords
    if any(kw in title for kw in ["rate limit", "rate-limit", "throttl", "abuse", "dos "]):
        return "PHASE-007"
    if any(kw in title for kw in ["security", "adversarial", "injection", "xss", "csrf"]):
        return "PHASE-006"

    # Tenant isolation keywords
    if any(kw in title for kw in ["tenant isolation", "cross-tenant", "partition"]):
        return "PHASE-005"

    # Data integrity
    if any(kw in title for kw in ["data integrity", "backup", "repository"]):
        return "PHASE-008"

    # Resilience
    if any(kw in title for kw in ["resilience", "failover", "error handling"]):
        return "PHASE-009"

    # Quality
    if any(kw in title for kw in ["conversation quality", "quality score", "evaluation"]):
        return "PHASE-011"

    # Upgrade
    if any(kw in title for kw in ["upgrade", "migration"]):
        return "PHASE-014"

    # Performance / Load
    if any(kw in title for kw in ["performance", "load test", "concurren"]):
        return "PHASE-010"

    # Pre-flight
    if any(kw in title for kw in ["pre-flight", "preflight", "health check"]):
        return "PHASE-001"

    # Section-based default
    return SECTION_TO_PHASE.get(section, "PHASE-002")


kdb = db.KnowledgeDB()

# Get untested specs (excluding retired)
untested = kdb.get_untested_specs()
active = [s for s in untested if s.get("status") != "retired"]
print(f"Total untested specs: {len(untested)} (active: {len(active)})")

# Find the highest existing test ID to continue the sequence
conn = kdb._get_conn()
max_test_row = conn.execute("SELECT id FROM tests ORDER BY rowid DESC LIMIT 1").fetchone()
if max_test_row:
    # Extract numeric part from "TEST-NNNN"
    max_num = int(max_test_row[0].replace("TEST-", ""))
else:
    max_num = 0
print(f"Highest existing test ID: TEST-{max_num:04d}")
next_num = max_num + 1

# Generate test stubs
test_stubs = []
phase_new_tests = defaultdict(list)  # phase_id -> [test_id, ...]

for spec in active:
    test_id = f"TEST-{next_num:04d}"
    next_num += 1

    section = spec.get("section", "")
    test_type = SECTION_TO_TEST_TYPE.get(section, "unit")
    phase_id = infer_phase(spec)

    spec_title = spec.get("title", "Untitled")
    title = f"Verify: {spec_title}"
    if len(title) > 200:
        title = title[:197] + "..."

    expected_outcome = f"PASS confirms {spec_title} is correctly implemented"
    if len(expected_outcome) > 300:
        expected_outcome = expected_outcome[:297] + "..."

    stub = {
        "id": test_id,
        "title": title,
        "spec_id": spec["id"],
        "test_type": test_type,
        "expected_outcome": expected_outcome,
        "phase_id": phase_id,
    }
    test_stubs.append(stub)
    phase_new_tests[phase_id].append(test_id)

# Report
print(f"\n=== TEST STUBS TO CREATE: {len(test_stubs)} ===")
print(f"ID range: TEST-{max_num + 1:04d} through TEST-{next_num - 1:04d}")

# Type breakdown
type_counts = Counter(t["test_type"] for t in test_stubs)
print(f"\nBy test_type:")
for tp, count in type_counts.most_common():
    print(f"  {tp}: {count}")

# Phase breakdown
print(f"\nBy phase:")
for phase_id in sorted(phase_new_tests.keys()):
    count = len(phase_new_tests[phase_id])
    print(f"  {phase_id}: {count} new test stubs")

# Sample
print(f"\nSample (first 5):")
for t in test_stubs[:5]:
    print(f"  {t['id']} | {t['test_type']} | {t['phase_id']} | {t['spec_id']} | {t['title'][:60]}")

# Execute or dry run
if "--execute" not in sys.argv:
    print(f"\n[DRY RUN] Pass --execute to create {len(test_stubs)} test stubs and update phases")
    kdb.close()
    sys.exit(0)

# === CREATE TEST STUBS ===
print(f"\n=== CREATING {len(test_stubs)} TEST STUBS ===")
for t in test_stubs:
    kdb.insert_test(
        id=t["id"],
        title=t["title"],
        spec_id=t["spec_id"],
        test_type=t["test_type"],
        expected_outcome=t["expected_outcome"],
        changed_by="S115",
        change_reason="Test stub for untested spec (S115 Phase 3)",
        # test_file, test_class, test_function = NULL (stub)
    )
print(f"Created {len(test_stubs)} test stubs.")

# === UPDATE PHASE LINKAGES ===
print(f"\n=== UPDATING PHASE LINKAGES ===")
phases = kdb.list_test_plan_phases("PLAN-001")
for phase in phases:
    phase_id = phase["id"]
    new_ids = phase_new_tests.get(phase_id, [])
    if not new_ids:
        print(f"  {phase_id}: no new stubs to add")
        continue

    # Get existing test_ids and merge
    existing_ids = json.loads(phase["test_ids"]) if phase.get("test_ids") else []
    merged_ids = sorted(set(existing_ids + new_ids))

    # Pass raw list — update_test_plan_phase handles json.dumps internally
    kdb.update_test_plan_phase(
        phase_id,
        changed_by="S115",
        change_reason=f"Add {len(new_ids)} test stubs from untested specs (S115 Phase 3)",
        test_ids=merged_ids,
    )
    print(f"  {phase_id}: {len(existing_ids)} existing + {len(new_ids)} new = {len(merged_ids)} total")

# Final counts
total_tests_in_phases = 0
for phase in kdb.list_test_plan_phases("PLAN-001"):
    ids = json.loads(phase["test_ids"]) if phase.get("test_ids") else []
    total_tests_in_phases += len(ids)

print(f"\nDone. {len(test_stubs)} test stubs created. Total tests in phases: {total_tests_in_phases}")
kdb.close()
