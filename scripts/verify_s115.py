"""S115 verification script — checks all 6 post-execution conditions."""

import sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()
conn = kdb._get_conn()
errors = []

# === CHECK 1: Work item counts ===
print("=== CHECK 1: Work Item Counts ===")
summary = kdb.get_summary()
wi_count = summary.get("work_item_total", 0)
print(f"  Work items: {wi_count}")
if wi_count == 765:
    print("  PASS: 765 work items created")
else:
    errors.append(f"CHECK 1 FAIL: Expected 765 work items, got {wi_count}")
    print(f"  FAIL: Expected 765, got {wi_count}")

# === CHECK 2: All work items are open ===
print("\n=== CHECK 2: All Work Items Open ===")
open_items = kdb.get_open_work_items()
print(f"  Open work items: {len(open_items)}")
if len(open_items) == 765:
    print("  PASS: All 765 work items are open")
else:
    errors.append(f"CHECK 2 FAIL: Expected 765 open, got {len(open_items)}")
    print(f"  FAIL: Expected 765 open, got {len(open_items)}")

# === CHECK 3: Total test artifacts ===
print("\n=== CHECK 3: Total Test Artifacts ===")
test_count_row = conn.execute("SELECT COUNT(DISTINCT id) FROM tests").fetchone()
total_tests = test_count_row[0]
print(f"  Total distinct test IDs: {total_tests}")
if total_tests == 2633:
    print("  PASS: 1,868 + 765 = 2,633 test artifacts")
else:
    errors.append(f"CHECK 3 FAIL: Expected 2633 tests, got {total_tests}")
    print(f"  FAIL: Expected 2633, got {total_tests}")

# === CHECK 4: Phase linkage totals ===
print("\n=== CHECK 4: Phase Linkage Totals ===")
phases = kdb.list_test_plan_phases("PLAN-001")
total_in_phases = 0
unique_in_phases = set()
for phase in phases:
    ids = json.loads(phase["test_ids"]) if phase.get("test_ids") else []
    total_in_phases += len(ids)
    unique_in_phases.update(ids)
    print(f"  {phase['id']}: {len(ids)} tests")

print(f"\n  Sum of phase test_ids: {total_in_phases}")
print(f"  Unique test IDs across phases: {len(unique_in_phases)}")
if len(unique_in_phases) == 2633:
    print("  PASS: All 2,633 tests are in phases")
else:
    errors.append(f"CHECK 4 FAIL: Expected 2633 unique in phases, got {len(unique_in_phases)}")
    print(f"  FAIL: Expected 2633 unique, got {len(unique_in_phases)}")

# Check for duplicates across phases
if total_in_phases != len(unique_in_phases):
    dup_count = total_in_phases - len(unique_in_phases)
    errors.append(f"CHECK 4 WARN: {dup_count} duplicate assignments across phases")
    print(f"  WARN: {dup_count} tests appear in multiple phases")
else:
    print("  PASS: No duplicate assignments across phases")

# === CHECK 5: Untested specs ===
print("\n=== CHECK 5: Untested Specs ===")
untested = kdb.get_untested_specs()
# Should be only the 2 retired specs
active_untested = [s for s in untested if s.get("status") != "retired"]
retired_untested = [s for s in untested if s.get("status") == "retired"]
print(f"  Total untested: {len(untested)}")
print(f"  Retired untested: {len(retired_untested)}")
print(f"  Active untested: {len(active_untested)}")
if len(active_untested) == 0:
    print("  PASS: All active specs have at least one test")
else:
    errors.append(f"CHECK 5 FAIL: {len(active_untested)} active specs still untested")
    print(f"  FAIL: {len(active_untested)} active specs still untested")
    for s in active_untested[:5]:
        print(f"    {s['id']}: {s.get('title', '?')[:60]}")

# === CHECK 6: KB assertions ===
print("\n=== CHECK 6: KB Assertions ===")
assertion_results = kdb.get_all_latest_assertion_runs()
total_assertions = len(assertion_results)
passed = sum(1 for r in assertion_results if r.get("overall_passed") == 1)
failed = sum(1 for r in assertion_results if r.get("overall_passed") == 0)
print(f"  Total assertions: {total_assertions}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
if passed == 70 and failed == 0:
    print("  PASS: 70/70 assertions pass")
else:
    errors.append(f"CHECK 6 FAIL: {passed}/{total_assertions} passed, {failed} failed")
    print(f"  FAIL: {passed}/{total_assertions} passed, {failed} failed")
    for r in assertion_results:
        if r.get("overall_passed") == 0:
            print(f"    FAIL: {r.get('spec_id', '?')} - {r.get('title', '?')[:60]}")

# === SUMMARY ===
print("\n" + "=" * 60)
if not errors:
    print("ALL 6 CHECKS PASSED")
else:
    print(f"{len(errors)} CHECK(S) FAILED:")
    for e in errors:
        print(f"  {e}")
print("=" * 60)

kdb.close()
