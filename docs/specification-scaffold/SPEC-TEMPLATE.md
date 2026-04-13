# Specification Template

This document defines the canonical format for specifications stored in the groundtruth-kb Knowledge Database.

## Database Fields

> **Storage schema — not API input shape.** This table describes how fields are stored in SQLite. When calling `db.insert_spec(...)` or `db.update_spec(...)` via the Python API, pass `tags` and `assertions` as Python lists (not JSON-encoded strings); `changed_at` is set automatically by the database layer and must not be passed as an argument. See the [Example Specification](#example-specification) and [Python API](#python-api) sections below for the correct call shape.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | TEXT | Yes | Unique identifier. Prefix determines type: `SPEC-*` (requirement), `GOV-*` (governance), `PB-*` (protected behavior), `ADR-*` (architecture decision), `DCL-*` (design constraint) |
| `version` | INTEGER | Yes | Auto-incremented. Each mutation creates a new version row (append-only). |
| `title` | TEXT | Yes | Concise summary of the requirement (< 120 characters) |
| `description` | TEXT | No | Detailed explanation of the requirement, acceptance criteria, and rationale |
| `priority` | TEXT | No | `P0` (blocker), `P1` (high), `P2` (medium), `P3` (low) |
| `scope` | TEXT | No | Component or area: `API`, `Admin`, `Widget`, `Infrastructure`, `Test`, etc. |
| `section` | TEXT | No | Organizational grouping within scope |
| `handle` | TEXT | No | Machine-readable slug for programmatic reference |
| `tags` | TEXT | No | **Stored as** JSON array string (e.g., `'["multi-tenant", "security"]'`). **Pass as** Python list to the API: `tags=["multi-tenant", "security"]` |
| `status` | TEXT | Yes | `specified`, `implemented`, `verified`, or `retired` |
| `type` | TEXT | No | See Type Taxonomy below |
| `assertions` | TEXT | No | **Stored as** JSON array string. **Pass as** Python list of dicts to the API: `assertions=[{"type": "grep", ...}]` |
| `changed_by` | TEXT | Yes | Author of this version (e.g., `owner`, `claude-session-277`) |
| `changed_at` | TEXT | DB-managed | ISO 8601 timestamp — set automatically by the database layer. **Do not pass to `insert_spec()` or `update_spec()`** |
| `change_reason` | TEXT | Yes | Explanation for the change (audit trail) |

## Type Taxonomy

| Type | ID Prefix | Purpose | Example |
|------|-----------|---------|---------|
| `requirement` | `SPEC-*` | Business or functional requirement | SPEC-1234: Widget must support SSE streaming |
| `governance` | `GOV-*` | Process rule governing development workflow | GOV-01: Spec-first — create spec before code |
| `protected_behavior` | `PB-*` | Behavior that must never regress | PB-001: Tenant data isolation |
| `architecture_decision` | `ADR-*` | Cross-cutting architectural choice with rationale | ADR-003: IntentRouter agent routing |
| `design_constraint` | `DCL-*` | Machine-checkable constraint derived from ADR | DCL-001: All API responses < 5s P99 |

## Assertions Format

Assertions are JSON arrays of machine-verifiable checks that run automatically at session start. Each assertion has a `type` and type-specific fields:

### grep — Pattern must exist in file(s)

```json
{
  "type": "grep",
  "pattern": "class TenantIsolationMiddleware",
  "file_pattern": "src/multi_tenant/*.py",
  "min_count": 1
}
```

### grep_absent — Pattern must NOT exist in file(s)

```json
{
  "type": "grep_absent",
  "pattern": "TODO.*HACK",
  "file_pattern": "src/**/*.py"
}
```

### glob — File path pattern must match at least one file

```json
{
  "type": "glob",
  "pattern": "tests/multi_tenant/test_tenant_isolation.py"
}
```

## Linking Model

Specifications are the hub of the artifact graph:

```
SPECIFICATION (id)
  |
  |-- tests.spec_id         (1:many) Tests that verify this spec
  |-- work_items.source_spec_id  (1:many) Work items that implement this spec
  |-- test_coverage.spec_id (1:many) Supplementary coverage mappings
```

- Every test MUST reference a `spec_id`
- Work items SHOULD reference a `source_spec_id` when the work derives from a spec
- Test coverage entries provide supplementary many-to-many mapping for analytical queries

## Example Specification

```python
# Use the Python API to create specs — not raw JSON.
# tags and assertions are Python lists, not JSON-encoded strings.
# changed_at is set automatically by the database layer; do not pass it.

db.insert_spec(
    id="SPEC-0100",
    title="Health endpoint returns structured readiness status",
    description="The /ready endpoint must return a JSON object with fields: status (healthy|degraded|unhealthy), checks (array of named check results with pass/fail), and timestamp. Returns HTTP 200 when healthy, 503 when degraded or unhealthy. Used by container orchestrator liveness probes and deployment verification scripts.",
    priority="P0",
    scope="API",
    section="Infrastructure",
    tags=["infrastructure", "health", "deployment"],
    status="specified",
    type="requirement",
    assertions=[
        {"type": "grep", "pattern": "@app.get.*ready", "file_pattern": "src/**/*.py", "min_count": 1},
        {"type": "glob", "pattern": "tests/**/test_health*.py"}
    ],
    changed_by="owner",
    change_reason="Initial specification for production readiness"
)
```

> **Note:** If you need to represent a spec as a raw JSON document (e.g., for `initial-specifications.json` import via `db.insert_spec(**spec)`), `tags` and `assertions` must be Python lists — **not** JSON-encoded strings. The `changed_at` field is managed by the database layer and must not be included in the payload.

## Python API

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB("groundtruth.db")

# Create a new spec
db.insert_spec(
    id="SPEC-0100",
    title="Health endpoint returns structured readiness status",
    description="...",
    priority="P0",
    scope="API",
    status="specified",
    type="requirement",
    assertions=[{"type": "grep", "pattern": "@app.get.*ready", "file_pattern": "src/**/*.py"}],
    changed_by="owner",
    change_reason="Initial specification"
)

# Update a spec (creates new version, preserves history)
db.update_spec(
    "SPEC-0100",
    status="implemented",
    changed_by="claude-session-42",
    change_reason="Implementation complete, tests passing"
)

# Query
spec = db.get_spec("SPEC-0100")          # Latest version
tests = db.get_tests_for_spec("SPEC-0100")  # All linked tests
specs = db.list_specs(status="specified")    # Filter by status
```

## Append-Only Change Control

All specification mutations create a NEW version row. No UPDATE or DELETE operations are permitted.

| Constraint | Enforcement |
|-----------|-------------|
| `UNIQUE(id, version)` | Each version is immutable once written |
| No UPDATE | API layer prevents in-place modification |
| No DELETE | API layer prevents removal |
| `current_specifications` view | Automatically surfaces latest version |
| Full audit trail | Every change includes `changed_by`, `changed_at`, `change_reason` |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
