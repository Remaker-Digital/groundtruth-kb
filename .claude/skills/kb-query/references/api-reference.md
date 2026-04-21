# Knowledge Database API Reference

All queries use the Python API at `tools/knowledge-db/db.py`. **Never edit the SQLite database directly.**

## Initialize

```python
import sys
sys.path.insert(0, "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement")
from tools.knowledge_db.db import KnowledgeDB
db = KnowledgeDB()
```

## Summary

```python
summary = db.get_summary()
# Returns: spec_total, spec_implemented, spec_verified, spec_specified, spec_retired,
#          test_procedure_count, operational_procedure_count,
#          assertions_total, assertions_passed, total_versions
```

## Specifications

```python
# List by status
db.list_specs(status="implemented")    # implemented, verified, specified, retired
db.list_specs(status="specified")

# Search by keyword
db.list_specs(search="rate limit")

# Filter by section, priority, tag, handle
db.list_specs(section="widget")
db.list_specs(priority="high")
db.list_specs(tag="infrastructure")

# Get specific spec
db.get_spec("SPEC-1803")

# Get version history
db.get_spec_history("SPEC-1803")

# Get children (hierarchical specs)
db.list_children("SPEC-245")        # All descendants
db.list_direct_children("SPEC-245") # One level only
```

## Tests

```python
# Tests for a spec (GOV-12 compliance)
db.get_tests_for_spec("SPEC-1803")

# List by type
db.list_tests(test_type="e2e")     # unit, integration, e2e, manual, assertion

# Find untested specs (drift detection)
db.get_untested_specs()
```

## Work Items

```python
# Open work items
db.get_open_work_items()

# Filter by origin/component/status
db.list_work_items(resolution_status="open")
db.list_work_items(origin="regression")
db.list_work_items(component="widget_frontend")
```

## Documents & Procedures

```python
# All documents
db.list_documents()
db.list_documents(category="cross-cutting-lessons")
db.list_documents(search="deployment")

# Specific document
db.get_document("DOC-cross-cutting-lessons")

# Operational procedures
db.list_op_procedures()
db.list_op_procedures(type="deployment")
```

## Assertions

```python
# Latest assertion run for a spec
db.get_latest_assertion_run("SPEC-1803")

# All latest assertion runs (quality dashboard)
db.get_all_latest_assertion_runs()
```

## Test Plans

```python
# Active test plan (PLAN-001)
db.get_active_test_plan()

# List phases
db.list_test_plan_phases("PLAN-001")
```

## Testable Elements

```python
# UI component inventory
db.list_testable_elements()
db.list_testable_elements(subsystem="widget")
```

## Write Operations

The KB is append-only. Every mutation creates a new version.

```python
# Create a spec
db.insert_spec(
    id="SPEC-XXXX", title="...", status="specified",
    description="...", changed_by="Claude", change_reason="S189: ..."
)

# Update a spec (creates new version)
db.update_spec(
    "SPEC-XXXX", changed_by="Claude", change_reason="...",
    status="implemented"
)

# Create a work item
db.insert_work_item(
    id="WI-XXXX", title="...", origin="defect", component="...",
    resolution_status="open", changed_by="Claude", change_reason="..."
)

# Record test result
db.update_test(
    "TEST-XXXX", changed_by="Claude", change_reason="...",
    last_result="pass", last_executed_at="2026-03-16T00:00:00Z"
)
```
