# Task Tracker — Example GroundTruth Project

A minimal task-tracker API demonstrating all six layers of the GroundTruth method:

1. **Method concepts** — spec-first workflow, governance, review cycles
2. **KB tooling** — knowledge database with specs, tests, work items, ADRs
3. **Process templates** — CLAUDE.md, MEMORY.md, hooks, rules
4. **CI/CD** — GitHub Actions test + build + deploy workflows
5. **Bootstrap** — pre-seeded KB, ready to explore immediately
6. **Reference implementation** — this project itself

## Quick start

```bash
cd examples/task-tracker
pip install -e ".[dev]"

# Explore the knowledge database
gt --config groundtruth.toml summary

# Run tests
pytest tests/ -v

# Run assertions
gt --config groundtruth.toml assert

# Start the API
cd src && uvicorn task_tracker.app:app --reload
```

## Full walkthrough

See [WALKTHROUGH.md](WALKTHROUGH.md) for a 14-step guided tour through every
layer of the GroundTruth method.

## What's in the KB

| Artifact | Count | Details |
|----------|-------|---------|
| Specifications | 7 | 5 domain (SPEC-001–005) + 2 governance (GOV-01, GOV-03) |
| Tests | 7 | Each linked to a spec, all passing |
| Architecture | 2 | ADR-001 (in-memory store) + DCL-001 (no external DB) |
| Work items | 1 | WI-001 (title validation defect, resolved) |
| Backlog | 1 | BL-001 (initial review defects) |
| Documents | 1 | DOC-001 (Session S1 record) |

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /tasks | Create a task |
| GET | /tasks | List all tasks |
| GET | /tasks/{id} | Get a task |
| PATCH | /tasks/{id} | Update fields or transition status |
| DELETE | /tasks/{id} | Delete a task |
| GET | /health | Health check |
