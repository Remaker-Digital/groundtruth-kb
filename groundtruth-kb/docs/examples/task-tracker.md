# Task Tracker Walkthrough

A step-by-step guide through the GroundTruth method using the bundled example
project. By the end, you will have explored every layer: specifications, tests,
governance, assertions, architecture decisions, work items, the review cycle,
CI/CD, and the upstream promotion model.

!!! tip "Source code"
    The example project lives at
    [`examples/task-tracker/`](https://github.com/Remaker-Digital/groundtruth-kb/tree/main/examples/task-tracker)
    in the repository.

## Prerequisites

- Python 3.11+
- `groundtruth-kb` installed (see [Start Here](../start-here.md))

## Step 1: Set up the project

```bash
# From the groundtruth-kb repo root, install the package first
pip install -e .

# Then install the example project
cd examples/task-tracker
pip install -e ".[dev]"
```

The database in this example is MemBase per ADR-0001: Three-Tier Memory Architecture.

## Step 2: Explore MemBase

```bash
gt --config groundtruth.toml summary
```

You should see: 7 specs (5 domain + 2 governance), 7 tests, 1 work item,
1 document. This database was pre-seeded by `seed_kb.py` to give you
something real to inspect.

## Step 3: Browse with the web UI

```bash
pip install -e ".[web]"  # from groundtruth-kb repo root
gt --config groundtruth.toml serve
```

Open [http://localhost:8090](http://localhost:8090). Browse the specs, tests,
and history tabs. Notice that every change has a version, author, and timestamp.

## Step 4: Read a specification

In the web UI, click on **SPEC-001** ("Users can create tasks with title and
description"). Notice:

- **Status:** implemented (code exists that satisfies this spec)
- **Description:** states the requirement in business terms, not implementation terms
- **Assertions:** a grep pattern checking that the API handler exists in `app.py`

This is the spec-first approach: the spec was recorded before the code was written.

## Step 5: Read the architecture decision

Browse to **ADR-001** ("Use in-memory dict store for task data"). This records:

- **Context:** why a data store was needed
- **Decision:** in-memory dict (not SQLite or PostgreSQL)
- **Trade-offs:** simpler setup, no persistence across restarts

Then look at **DCL-001** ("No external database dependency"). This is a
machine-checkable rule derived from ADR-001, with a `grep_absent` assertion
ensuring no `sqlalchemy`, `psycopg`, or `pymongo` imports appear in the
models file.

## Step 6: Run assertions

```bash
gt --config groundtruth.toml assert
```

All assertions should pass. These verify that the codebase still matches
the specs.

## Step 7: Run the tests

```bash
pytest tests/ -v
```

All 7 tests should pass. Each test class and method is named to match the
specification it verifies (TEST-001 → SPEC-001, etc.).

## Step 8: Start the API

```bash
cd src && uvicorn task_tracker.app:app --reload
```

Try some requests:

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'

# List tasks
curl http://localhost:8000/tasks

# Transition status
curl -X PATCH http://localhost:8000/tasks/TASK-0001 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

## Step 9: Simulate a regression

Edit `src/task_tracker/app.py` and temporarily rename the `create_task`
function to `_create_task_disabled`. Now run assertions:

```bash
gt --config groundtruth.toml assert
```

SPEC-001's assertion fails — the grep pattern no longer finds the handler.
This is a regression: something that was verified is now broken.

## Step 10: Create a work item

In a real project, you would now create a work item to track the fix:

```python
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB(db_path="groundtruth.db")
db.insert_work_item(
    "WI-002", "Restore create_task endpoint",
    origin="regression", component="api",
    resolution_status="open", changed_by="S2",
    change_reason="Assertion regression detected",
    source_spec_id="SPEC-001",
)
db.close()
```

## Step 11: Fix and re-verify

Undo the rename (restore `create_task`). Then:

```bash
gt --config groundtruth.toml assert   # should pass again
pytest tests/ -v                       # should pass again
```

Resolve the work item:

```python
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB(db_path="groundtruth.db")
db.update_work_item("WI-002", "S2", "Fixed regression",
                    resolution_status="resolved", stage="resolved")
db.close()
```

## Step 12: Understand the review cycle

The example includes a
[review example](https://github.com/Remaker-Digital/groundtruth-kb/blob/main/examples/task-tracker/REVIEW-EXAMPLE.md)
showing a complete Loyal Opposition review cycle:

1. Prime Builder submits work for review
2. Reviewer finds a defect (P2: unbounded title length)
3. Verdict: NO-GO
4. Work item WI-001 created
5. Fix applied (max_length=200)
6. Re-review → GO

This is the quality gate that catches issues before they reach production.

## Step 13: Understand the CI/CD pipeline

The example project includes three workflow files in `.github/workflows/`:

- **test.yml** — runs on every push: `pytest` + `ruff` + `gt assert`. If any
  assertion fails, the CI build fails.
- **build.yml** — runs on version tags (`v*`): builds a Docker image and pushes
  to a container registry.
- **deploy.yml** — manual trigger with environment selection. A parameterized
  stub to customize for your cloud provider.

## Step 14: Understand upstream promotion

This project consumes `groundtruth-kb` as a dependency. When a new version
of GroundTruth is released:

1. Update the dependency:
   ```bash
   pip install groundtruth-kb
   ```
2. Run assertions: `gt --config groundtruth.toml assert`
3. Run tests: `pytest tests/ -v`
4. If everything passes, you're on the new version

See the [Adoption guide](../method/09-adoption.md) for the full
upstream/downstream contract.

## What you've learned

- **Specifications** are decision logs, not build specs
- **Tests** are linked to specs for traceability
- **Assertions** continuously verify the codebase matches specs
- **Governance gates** enforce rules at lifecycle transitions
- **Architecture decisions** are traceable (ADR → DCL → assertion)
- **Work items** track gaps between specs and implementation
- **Review cycles** produce evidence-based GO/NO-GO verdicts
- **CI/CD** automates testing, building, and deployment
- **Upstream promotion** keeps your project aligned with the method

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
