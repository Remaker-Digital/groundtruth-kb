# Debt-Inventory Method (Slice 1.5 Schema Specification)

**Authority:** `bridge/gtkb-push-gate-design-governance-review-004.md` (Codex GO on REVISED-3)
**Companion thread:** `bridge/gtkb-push-gate-slice-1-5-debt-audit-001.md` (Slice 1.5 NEW; minimum-viable implementation; currently NO-GO at `-002` pending Slice 0 sequencing resolution + mechanical fixes)
**Purpose:** Specify the JSON schema for the Slice 1.5 audit-only mode output, harmonized for forward-compatibility with the canonical `gt push-gate audit` CLI's eventual schema.

## Output Layout

For a single audit run with `--output-dir .gtkb-state/push-gate/audits/<run-id>/`:

```
.gtkb-state/push-gate/audits/<run-id>/
├── debt-inventory.json         # Aggregate union of all layer reports
├── SUMMARY.md                  # Human-readable summary (counts, prioritization)
├── layer-A1-ruff.json          # Ruff lint layer detail
├── layer-A2-mypy.json          # Mypy type-check layer detail
├── layer-A3-pytest.json        # Pytest collection layer detail
├── layer-A4-applicability.json # Applicability preflight layer detail
└── layer-A5-clause.json        # Clause preflight layer detail
```

`<run-id>` is either an explicit override (`--run-id initial-2026-05-28`) or a UTC timestamp (`audit-2026-05-28T15-11Z`).

The directory tree lives under `.gtkb-state/` which is gitignored. Per Codex's NO-GO-002 P2-003 finding (evidence-authority inconsistency in Slice 1.5 NEW-001), the audit JSON is **runtime-only**, NOT durable governed evidence. The post-implementation bridge report must capture durable counts, hashes, paths, and command output summaries in the bridge file itself; the bridge file IS the durable governed evidence.

## Top-Level `debt-inventory.json` Schema

```json
{
  "schema_version": "1.0",
  "run_id": "string",
  "generated_at_utc": "ISO-8601 timestamp",
  "audit_tool_versions": {
    "ruff": "x.y.z",
    "mypy": "x.y.z",
    "pytest": "x.y.z",
    "gt_applicability_preflight": "commit-sha",
    "gt_clause_preflight": "commit-sha"
  },
  "repo_state": {
    "branch": "string",
    "commit_sha": "string",
    "is_dirty": "boolean",
    "untracked_count": "integer"
  },
  "layers": {
    "A1": { /* see layer-A1-ruff.json schema below */ },
    "A2": { /* layer-A2-mypy.json schema */ },
    "A3": { /* layer-A3-pytest.json schema */ },
    "A4": { /* layer-A4-applicability.json schema */ },
    "A5": { /* layer-A5-clause.json schema */ }
  },
  "aggregate": {
    "total_findings": "integer",
    "by_severity": {"blocking": "integer", "advisory": "integer"},
    "by_layer": {"A1": "integer", "A2": "integer", "A3": "integer", "A4": "integer", "A5": "integer"}
  }
}
```

## Per-Layer Schemas

### Layer A1 — Ruff Lint

```json
{
  "layer_id": "A1",
  "layer_name": "ruff-lint",
  "command": "ruff check --output-format=json --no-cache <repo>",
  "tool_version": "x.y.z",
  "ran_at_utc": "ISO-8601",
  "duration_seconds": "number",
  "total_violations": "integer",
  "per_rule_code": {"E501": 42, "F401": 12, ...},
  "per_file": [
    {"path": "scripts/x.py", "violations": 5, "rule_codes": {"E501": 3, "F401": 2}}
  ],
  "infrastructure_error": "null | string"
}
```

### Layer A2 — Mypy Type-Check

```json
{
  "layer_id": "A2",
  "layer_name": "mypy-typecheck",
  "command": "mypy --show-error-codes --no-pretty <repo>",
  "tool_version": "x.y.z",
  "ran_at_utc": "ISO-8601",
  "duration_seconds": "number",
  "total_errors": "integer",
  "per_error_code": {"arg-type": 8, "attr-defined": 3, ...},
  "per_file": [
    {"path": "groundtruth-kb/src/x.py", "errors": 2, "error_codes": {"arg-type": 2}}
  ],
  "infrastructure_error": "null | string"
}
```

### Layer A3 — Pytest Collection

```json
{
  "layer_id": "A3",
  "layer_name": "pytest-collection",
  "command": "pytest --collect-only --quiet",
  "tool_version": "x.y.z",
  "ran_at_utc": "ISO-8601",
  "duration_seconds": "number",
  "total_tests_collected": "integer",
  "per_directory": {"tests/": 312, "platform_tests/": 89, ...},
  "deselected_count": "integer",
  "skipped_count": "integer",
  "collection_errors": [
    {"file": "tests/x.py", "error": "ImportError: ..."}
  ],
  "infrastructure_error": "null | string"
}
```

### Layer A4 — Applicability Preflight Inventory

```json
{
  "layer_id": "A4",
  "layer_name": "applicability-preflight",
  "command": "python scripts/bridge_applicability_preflight.py --bridge-id <id> --json (per bridge)",
  "ran_at_utc": "ISO-8601",
  "duration_seconds": "number",
  "bridges_inspected": [
    {
      "bridge_id": "string",
      "operative_file": "path",
      "preflight_passed": "boolean",
      "missing_required_specs": ["SPEC-XXX-001"],
      "missing_advisory_specs": ["DCL-XXX-001"]
    }
  ],
  "aggregate_missing_required": "integer",
  "aggregate_missing_advisory": "integer",
  "infrastructure_error": "null | string"
}
```

### Layer A5 — Clause Preflight Inventory

```json
{
  "layer_id": "A5",
  "layer_name": "clause-preflight",
  "command": "python scripts/adr_dcl_clause_preflight.py --bridge-id <id> (per bridge)",
  "ran_at_utc": "ISO-8601",
  "duration_seconds": "number",
  "bridges_inspected": [
    {
      "bridge_id": "string",
      "operative_file": "path",
      "clauses_evaluated": "integer",
      "must_apply": "integer",
      "evidence_gaps_in_must_apply": "integer",
      "blocking_gaps": "integer",
      "blocking_clauses": [
        {"clause_id": "SPEC-XXX-001/CLAUSE-XYZ", "evidence_found": "boolean"}
      ]
    }
  ],
  "aggregate_blocking_gaps": "integer",
  "infrastructure_error": "null | string"
}
```

## Forward Compatibility

The canonical `gt push-gate audit` CLI (Slice 1) will extend this schema with:

- Layers 6 (governance integrity) and Layer 7 (release-readiness).
- Per-layer cache hits/misses (content-addressed cache; see `design-contract-draft.md` § Caching Substrate).
- Mode flag (`audit` vs `gate`) — Slice 1.5 hardcodes `mode: "audit"`; canonical CLI accepts both.
- Optional findings JSON-pointer references for IDE integration (Slice 7).

Adding fields is forward-compatible; existing field semantics are stable.

## Schema Stability Pledge

`schema_version: 1.0` of this schema is the Slice 1.5 baseline. Breaking changes to the schema require a major version bump (`schema_version: 2.0`) and a schema-migration note in the next bridge thread that touches the audit code. The audit-script's `--schema-version-only` flag SHOULD print the schema version without executing the audit, enabling consumers to verify schema compatibility.

## Exit-Code Semantics

- **Exit 0:** Audit completed successfully (regardless of finding count). This is audit-only mode; no gating.
- **Exit 1:** Infrastructure failure (tool not installed, repo not a git repo, invalid `--output-dir`, etc.). Audit did not complete.
- **Exit 2:** Schema invariant violation (would only fire if a layer report fails to conform to schema). Audit completed but output is suspect.

The canonical `gt push-gate` CLI's gating mode (Slice 4+) will repurpose exit codes for PASS/FAIL semantics; this is forward-compatible because `gt push-gate audit` retains exit 0 for completion.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
