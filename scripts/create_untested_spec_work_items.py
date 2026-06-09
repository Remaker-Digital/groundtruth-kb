"""Create work items for all untested specifications.

For each spec with no linked test artifact, creates a 'new' work item
requesting that a test be created. Skips retired specs.

Usage:
    python scripts/create_untested_spec_work_items.py          # dry run
    python scripts/create_untested_spec_work_items.py --execute # write to DB
"""

import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")
import db

# Section -> component mapping (from plan)
SECTION_TO_COMPONENT = {
    "ADMIN_UI": "customer_interface",
    "AUTH": "infrastructure_automation",
    "CONFIG": "tenant_administration",
    "WIDGET_UI": "customer_interface",
    "EMAIL": "external_integration",
    "AGENTS": "agent_implementation",
    "INFRA": "infrastructure_automation",
    "OPS": "infrastructure_automation",
    "TESTING": "test_harness",
}

# Status -> priority mapping
STATUS_TO_PRIORITY = {
    "verified": "P1",
    "implemented": "P1",
    "specified": "P2",
}

kdb = db.KnowledgeDB()

# Get untested specs
untested = kdb.get_untested_specs()
print(f"Total untested specs: {len(untested)}")

# Filter out retired
active = [s for s in untested if s.get("status") != "retired"]
retired = [s for s in untested if s.get("status") == "retired"]
print(f"Active (non-retired): {len(active)}")
print(f"Retired (skipped): {len(retired)}")

# Status breakdown
from collections import Counter

status_counts = Counter(s.get("status") for s in active)
print(f"\nStatus breakdown of untested active specs:")
for status, count in status_counts.most_common():
    print(f"  {status}: {count}")

# Section breakdown
section_counts = Counter(s.get("section", "(none)") for s in active)
print(f"\nSection breakdown:")
for section, count in section_counts.most_common():
    component = SECTION_TO_COMPONENT.get(section, "customer_interface")
    print(f"  {section}: {count} -> {component}")

# Generate work items
work_items = []
for i, spec in enumerate(active, start=1):
    wi_id = f"WI-{i:04d}"
    spec_title = spec.get("title", "Untitled")
    title = f"Create test for: {spec_title}"
    if len(title) > 120:
        title = title[:117] + "..."

    section = spec.get("section", "")
    component = SECTION_TO_COMPONENT.get(section, "customer_interface")
    # Governance specs (GOV-*) -> test_plan component
    if spec["id"].startswith("GOV-"):
        component = "test_plan"

    status = spec.get("status", "specified")
    priority = STATUS_TO_PRIORITY.get(status, "P2")

    work_items.append(
        {
            "id": wi_id,
            "title": title,
            "origin": "new",
            "component": component,
            "resolution_status": "open",
            "source_spec_id": spec["id"],
            "priority": priority,
            "description": f"Spec {spec['id']} ({status}) has no linked test artifact. "
            f"Create an appropriate test to verify: {spec_title}",
        }
    )

# Report
print(f"\n=== WORK ITEMS TO CREATE: {len(work_items)} ===")
# Component breakdown
comp_counts = Counter(wi["component"] for wi in work_items)
print(f"\nBy component:")
for comp, count in comp_counts.most_common():
    print(f"  {comp}: {count}")

# Priority breakdown
pri_counts = Counter(wi["priority"] for wi in work_items)
print(f"\nBy priority:")
for pri, count in pri_counts.most_common():
    print(f"  {pri}: {count}")

# Sample
print(f"\nSample (first 5):")
for wi in work_items[:5]:
    print(f"  {wi['id']} | {wi['component']} | {wi['priority']} | {wi['source_spec_id']} | {wi['title'][:60]}")

# Execute or dry run
if "--execute" not in sys.argv:
    print(f"\n[DRY RUN] Pass --execute to create {len(work_items)} work items in KB")
    kdb.close()
    sys.exit(0)

print(f"\n=== CREATING {len(work_items)} WORK ITEMS ===")
for wi in work_items:
    kdb.insert_work_item(
        id=wi["id"],
        title=wi["title"],
        origin=wi["origin"],
        component=wi["component"],
        resolution_status=wi["resolution_status"],
        changed_by="S115",
        change_reason="Create work item for untested spec (S115 Phase 2)",
        description=wi["description"],
        source_spec_id=wi["source_spec_id"],
        priority=wi["priority"],
    )

print(f"Done. {len(work_items)} work items created (WI-0001 through WI-{len(work_items):04d}).")
kdb.close()
