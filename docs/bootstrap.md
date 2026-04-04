# Getting Started with groundtruth-kb

A step-by-step walkthrough for adding the GroundTruth knowledge database and governance toolkit to your project. By the end, you will have a knowledge database with specifications, tests, and governance rules — all verified by assertions.

## What this guide covers (and does not)

**This guide covers** setting up the core groundtruth-kb toolkit:
install, init, seed, specifications, tests, assertions, web UI,
process templates, and CI/CD.

**This guide does NOT cover** full project scaffolding, infrastructure
provisioning, dual-agent runtime configuration, bridge setup, or cloud
deployment.  Those capabilities are planned for a separate
[groundtruth-project-kit](architecture/product-split.md) package.

## Prerequisites

- Python 3.11 or later
- A project you want to manage with traceable specifications
- Git (for version control and CI/CD)

## Step 1: Install GroundTruth

```bash
pip install "groundtruth-kb @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.1.1"
```

Verify the installation:

```bash
gt --version
```

## Step 2: Initialize your project

```bash
gt init my-project
cd my-project
```

This creates two files:

- `groundtruth.toml` — project configuration
- `groundtruth.db` — empty knowledge database

## Step 3: Seed governance rules

```bash
gt seed
```

This populates the database with 5 governance specifications (GOV-01 through GOV-05) that define the core method rules. To also add 3 example domain specs:

```bash
gt seed --example
```

Verify what was created:

```bash
gt summary
```

## Step 4: Write your first specification

Open a Python shell or script and create a spec for your project:

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB(db_path="groundtruth.db")

db.insert_spec(
    "SPEC-001",
    "Users can create tasks with a title and description",
    status="specified",
    changed_by="S1",
    change_reason="Initial requirement from project kickoff",
    description="The API must accept POST /tasks with title (required) "
                "and description (optional) fields.",
)

print(db.get_spec("SPEC-001"))
db.close()
```

## Step 5: Create a linked test

Every specification should have at least one test:

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB(db_path="groundtruth.db")

db.insert_test(
    "TEST-001",
    "POST /tasks creates a task and returns 201",
    spec_id="SPEC-001",
    test_type="e2e",
    expected_outcome="POST /tasks with valid title returns 201 and "
                     "the response body includes the task ID",
    changed_by="S1",
    change_reason="Test for SPEC-001",
)

db.close()
```

## Step 6: Add assertions to a spec

Assertions are machine-checkable rules that verify the codebase matches the specification. Add assertions when your spec reaches "implemented":

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB(db_path="groundtruth.db")

db.update_spec(
    "SPEC-001",
    changed_by="S1",
    change_reason="Add assertion + promote to implemented",
    status="implemented",
    assertions=[
        {
            "type": "grep",
            "file": "src/api.py",
            "pattern": "POST.*tasks",
            "description": "API handler for task creation exists",
        }
    ],
)

db.close()
```

## Step 7: Run assertions

```bash
gt assert
```

If the assertion passes (the file and pattern exist), you'll see a passing result. If not, you've caught a gap between spec and implementation.

## Step 8: Browse with the web UI

The web UI requires the `[web]` extra:

```bash
pip install "groundtruth-kb[web] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.1.1"
gt serve
```

Open http://localhost:8090 to browse specs, tests, history, and assertion results.

## Step 9: Set up process templates (optional)

Copy the reference templates into your project for AI-assisted development:

```bash
TEMPLATES=$(python -c "from groundtruth_kb import get_templates_dir; print(get_templates_dir())")

# Project rules and state files
cp "$TEMPLATES/CLAUDE.md" ./CLAUDE.md
cp "$TEMPLATES/MEMORY.md" ./MEMORY.md

# Hooks for Claude Code
mkdir -p .claude/hooks .claude/rules
cp "$TEMPLATES/hooks/"*.py .claude/hooks/
cp "$TEMPLATES/rules/"*.md .claude/rules/
```

Edit `CLAUDE.md` and `MEMORY.md` to replace the `{{PLACEHOLDER}}` values with your project's details.

## Step 10: Set up CI/CD (optional)

Copy the CI workflow templates:

```bash
mkdir -p .github/workflows
cp "$TEMPLATES/ci/test.yml" .github/workflows/test.yml
```

This gives you a GitHub Actions workflow that runs pytest, ruff, and `gt assert` on every push.

## What's next

- Read the [Method Overview](method/01-overview.md) to understand the full GroundTruth workflow
- Read the [Specifications guide](method/02-specifications.md) to learn how to write effective specs
- Read the [Adoption guide](method/09-adoption.md) to understand the upstream/downstream model
- Read the [Product Architecture](architecture/product-split.md) to see how groundtruth-kb fits into the broader ecosystem
- Add more specifications as your project grows — the knowledge database scales with you
