---
name: kb-work-item
description: Create a work item with automatic test creation and backlog assignment. Enforces GOV-12 (WI triggers tests) and GOV-13 (phase assignment) in a single invocation.
argument-hint: [title] [--spec SPEC-ID] [--origin regression|defect|new|hygiene]
allowed-tools: Bash, Read, Grep
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: knowledge-management
  governance: GOV-12, GOV-13
  references:
    - references/taxonomy.md
---

# Create Work Item (with Linked Test + Backlog)

Single-invocation skill enforcing the full GOV-12 chain: **Work Item -> Test -> Phase Assignment -> Backlog**.

**Arguments:** `$ARGUMENTS` = title and optional flags.

## Step 1: Determine Next IDs

Query KB for next WI and TEST IDs via `db.list_work_items()` and `db.list_tests()`.

## Step 2: Classify the Work Item

See `references/taxonomy.md` for the full origin taxonomy (regression/defect/new/hygiene), component taxonomy (13 components), and PLAN-001 phase assignment table.

## Step 3: Create the Work Item

```python
wi = db.insert_work_item(
    id=f"WI-{next_wi}", title="...",
    origin="new", component="...",
    resolution_status="open",
    changed_by="Claude", change_reason="SXXX: ...",
    description="...", source_spec_id="SPEC-XXXX",
    priority="medium",
)
```

## Step 4: Create Linked Test (GOV-12 -- MANDATORY)

> **GOV-12:** Work item creation triggers test creation. This step is NOT optional.

Test types: `assertion` (preferred), `e2e`, `integration`, `unit`, `manual`.

```python
test = db.insert_test(
    id=f"TEST-{next_test}", title="Verify: ...",
    spec_id="SPEC-XXXX", test_type="assertion",
    expected_outcome="...",
    changed_by="Claude", change_reason=f"GOV-12: Test for WI-{next_wi}",
)
```

**Quality rules:** GOV-03 (unambiguous PASS/FAIL), GOV-18 (meaningful, no rubber-stamp), GOV-10 (production interfaces).

## Step 5: Assign to PLAN-001 Phase (GOV-13 -- MANDATORY)

> **GOV-13:** Every test assigned to a PLAN-001 phase at creation. No orphans.

See `references/taxonomy.md` for the phase assignment table (14 phases).

## Step 6: Report Summary

```
Work Item Created
  WI:    WI-XXXX -- [title]
  Origin: [origin] | Component: [component]
  Spec:  SPEC-XXXX
  Test:  TEST-XXXXX -- [test title]
  Phase: PLAN-001 Phase [N]
  Status: open -> ready for backlog prioritization
```
