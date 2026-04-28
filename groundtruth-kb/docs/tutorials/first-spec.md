# Your First Specification

<!-- © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. -->

A hands-on walkthrough of the GOV-01 spec-first workflow using the bundled
task-tracker example. By the end you will have written a specification, created
a linked work item, run assertions, and seen the method in action.

!!! info "Living reference"
    The task-tracker project used throughout this tutorial lives in
    [`examples/task-tracker/`](https://github.com/Remaker-Digital/groundtruth-kb/tree/main/examples/task-tracker).
    Open it alongside this tutorial.

## Prerequisites

- `groundtruth-kb` installed (`pip install groundtruth-kb`)
- A project directory (use `gt project init my-tasks --profile local-only` if
  you do not have one yet)

---

## Step 1: Understand GOV-01 — Spec First

GOV-01 is the foundational rule: **before you write a line of code, write a
specification.** A specification is an agreement between you and the system
about what must be true. It is not a build plan — it is a decision log.

> "Users can create tasks with a title and priority."

That one sentence is a specification. It answers *what* the system must do,
not *how* to build it.

---

## Step 2: Create Your First Specification

Open a Python shell in your project directory:

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB(db_path="groundtruth.db")

db.insert_spec(
    "SPEC-100",
    "Users can create tasks with a title and priority",
    status="specified",
    changed_by="tutorial-s1",
    change_reason="Initial requirement from project kickoff",
    description=(
        "The create_task() function must accept a title (required string) "
        "and a priority (optional: 'low', 'medium', 'high', default 'medium'). "
        "It returns a dict with at least: id, title, priority, status='open'."
    ),
)

print(db.get_spec("SPEC-100"))
db.close()
```

Verify it was stored:

```bash
gt summary
```

You should now see one more specification in the count.

---

## Step 3: Create a Linked Test

Every specification should have at least one test. A test records *how you
will verify* the spec — it does not have to be executable code right now.

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB(db_path="groundtruth.db")

db.insert_test(
    "TEST-100",
    "create_task() returns a dict with status='open'",
    spec_id="SPEC-100",
    test_type="unit",
    expected_outcome=(
        "Calling create_task('Buy milk') returns a dict where "
        "d['status'] == 'open' and d['title'] == 'Buy milk'."
    ),
    changed_by="tutorial-s1",
    change_reason="Test for SPEC-100",
)

db.close()
```

---

## Step 4: Add an Assertion

Once you know what you will implement, add a machine-checkable assertion to
the spec. Assertions are checked by `gt assert`.

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB(db_path="groundtruth.db")

db.update_spec(
    "SPEC-100",
    changed_by="tutorial-s1",
    change_reason="Add assertion — promote to implemented",
    status="implemented",
    assertions=[
        {
            "type": "grep",
            "file": "src/tasks.py",
            "pattern": "def create_task",
            "description": "create_task function exists in tasks module",
        },
        {
            "type": "grep",
            "file": "src/tasks.py",
            "pattern": "status.*=.*['\"]open['\"]",
            "description": "create_task sets status to open",
        },
    ],
)

db.close()
```

---

## Step 5: Write the Implementation

Create `src/tasks.py` in your project:

```python
# src/tasks.py


def create_task(
    title: str,
    priority: str = "medium",
) -> dict:
    """Create a task with the given title and priority."""
    return {
        "id": 1,
        "title": title,
        "priority": priority,
        "status": "open",
    }
```

---

## Step 6: Run Assertions

```bash
gt assert
```

Both assertions should pass:

```
PASSED: 2
FAILED: 0
```

Congratulations — you have completed the spec-first workflow loop:
**specify → test → implement → assert**.

---

## Step 7: Create a Work Item for a Gap

Suppose you notice the spec says priority defaults to `"medium"` but the
assertion does not verify it. Create a work item to track the gap:

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB(db_path="groundtruth.db")

db.insert_work_item(
    "WI-100",
    "Add assertion for default priority = medium in create_task()",
    origin="defect",
    component="api",
    spec_id="SPEC-100",
    changed_by="tutorial-s1",
    change_reason="Gap found during tutorial walkthrough",
)

db.close()
```

The work item is now tracked in the KB alongside the spec and test. Nothing
falls through the cracks.

---

## What's Next

- See the full example in [`examples/task-tracker/`](https://github.com/Remaker-Digital/groundtruth-kb/tree/main/examples/task-tracker)
- Read the [Dual-Agent Setup](dual-agent-setup.md) tutorial to add a Loyal
  Opposition reviewer to your workflow
- Read the [Method: Specifications](../method/02-specifications.md) guide
  for a deeper look at the spec lifecycle
