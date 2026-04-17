# NO-GO: F1 Spec Schema Enrichment Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f1-001.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The feature direction is aligned with the GroundTruth KB vision: richer specification metadata should reduce assumption-driven implementation and make owner intent easier to preserve. The proposal is not implementation-ready because it is stale against the current `groundtruth-kb` checkout, would duplicate an existing `type` field, uses an unsafe authority default for legacy data, and treats priority normalization as an additive change even though it is not additive in SQLite or in the current project contract.

## Findings

### 1. Blocking: `type` is already present in GT-KB

**Claim:** The proposal says GT-KB lacks a `type` column and proposes adding one.

**Evidence:**
- Proposal states "No `type` column in GT-KB" at bridge/gtkb-spec-pipeline-f1-001.md:26.
- Proposal lists `type` as a new column at bridge/gtkb-spec-pipeline-f1-001.md:48 and includes `ALTER TABLE specifications ADD COLUMN type TEXT DEFAULT 'requirement'` at bridge/gtkb-spec-pipeline-f1-001.md:66.
- Current GT-KB already migrates `specifications.type` in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:517.
- Current `insert_spec()` accepts `type` in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:579 and writes it in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:618.
- Current `list_specs()` already accepts `type` in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:788 and filters it in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:793.
- Current docs describe recognized spec types in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/method/02-specifications.md:46.
- Command result from a fresh `KnowledgeDB`: `column_count 16` and `columns rowid,id,version,title,description,priority,scope,section,handle,tags,status,assertions,changed_by,changed_at,change_reason,type`.
- Command result from the checked-in `groundtruth.db`: same column list ending in `type`.
- `python -m pytest tests/test_db.py::TestSpecifications::test_auto_detect_spec_type -q --tb=short` passed: `1 passed, 1 warning`.

**Risk/impact:** A literal implementation of the proposed migration can fail on any database already opened by current GT-KB with `duplicate column name: type`. It also risks replacing established type behavior, docs, seed data, and gates instead of extending them.

**Required action:** Revise F1 to treat `type` as existing GT-KB functionality. If F1 needs a new `documentation` type, specify it as an extension to the existing type set with docs, tests, and compatibility behavior.

### 2. Blocking: `authority DEFAULT 'stated'` over-authorizes legacy data

**Claim:** The migration default would classify every existing row as owner-stated before enrichment.

**Evidence:**
- Proposal defines `authority` default as `'stated'` at bridge/gtkb-spec-pipeline-f1-001.md:49 and migration line `ADD COLUMN authority TEXT DEFAULT 'stated'` at bridge/gtkb-spec-pipeline-f1-001.md:67.
- The proposal's own counterfactual says implementation-derived specs should have been `authority=inferred`, not equal authority, at bridge/gtkb-spec-pipeline-f1-001.md:38.
- Agent Red enrichment is deferred to Phase E after all features ship at bridge/gtkb-spec-pipeline-f1-001.md:73.

**Risk/impact:** Existing unknown or implementation-derived specs would temporarily, and possibly permanently for non-Agent-Red consumers, be treated as highest-authority owner statements. That recreates the exact corruption vector the feature is meant to reduce.

**Required action:** Add `authority` as nullable or default `unknown`/`unspecified` for migrations. If the API should default new specs to owner-stated, separate "new insert default" from "legacy migration default". Trust-ranking logic must treat unknown authority conservatively until explicit enrichment occurs.

### 3. Blocking: Priority CHECK constraint is not additive and conflicts with current semantics

**Claim:** The proposal includes priority normalization inside F1 while also claiming an additive migration.

**Evidence:**
- Proposal requests `priority` CHECK values at bridge/gtkb-spec-pipeline-f1-001.md:59.
- Proposal says the schema change is additive and no destructive changes are needed at bridge/gtkb-spec-pipeline-f1-001.md:63.
- The migration sequence only lists `ALTER TABLE ... ADD COLUMN` steps at bridge/gtkb-spec-pipeline-f1-001.md:65.
- Current docs say priority is project-defined in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/docs/method/04-work-items.md:92.
- Current API accepted and stored an arbitrary priority in a fresh DB test: `stored_priority urgent-now`.

**Risk/impact:** SQLite cannot add a CHECK constraint to an existing column with a simple `ALTER TABLE ADD COLUMN`; enforcing this requires a table rebuild and a compatibility decision for existing values. If implemented partially, the code and docs will disagree about whether priority is project-defined or standardized.

**Required action:** Remove priority normalization from F1 or split it into a separate proposal with an explicit owner decision, legacy value mapping, table rebuild plan, docs changes, and tests.

### 4. Major: JSON metadata storage/query semantics are underspecified

**Claim:** `constraints` and `affected_by` are proposed as JSON text, but the current implementation pattern only serializes/parses selected JSON fields and uses approximate text matching for JSON containment.

**Evidence:**
- Proposal defines `constraints` JSON at bridge/gtkb-spec-pipeline-f1-001.md:50 and `affected_by` JSON at bridge/gtkb-spec-pipeline-f1-001.md:52.
- Proposal requires JSON validation at bridge/gtkb-spec-pipeline-f1-001.md:96.
- Current `insert_spec()` only JSON-serializes `assertions` and `tags` in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:614.
- Current `update_spec()` only has special carry-forward serialization logic for `tags` and `assertions` in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:696.
- Current `_row_to_dict()` parses a fixed list of JSON fields that does not include `constraints` or `affected_by` in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3735.
- Current tag filtering documents its approximate JSON `LIKE` limitation in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:809.

**Risk/impact:** Without explicit serialization and exact containment behavior, `affected_by` can produce false positives/negatives and `constraints` can become an unvalidated string dump. F4 constraint propagation would then rest on unreliable linkage.

**Required action:** Specify Python input/output types, validation rules, and query mechanics. At minimum, parse `constraints` and `affected_by` in `_row_to_dict()`, validate `constraints` against the declared schema, validate `affected_by` as `list[str]`, and use exact containment via SQLite JSON1 or Python parsing. If cross-cutting lookup is performance-sensitive, use a normalized relation table instead of JSON text.

### 5. Major: Provisional lifecycle invariants are not defined

**Claim:** The proposal adds provisional metadata but does not define enforceable invariants.

**Evidence:**
- Proposal defines `authority='provisional'` and `provisional_until` at bridge/gtkb-spec-pipeline-f1-001.md:49 and bridge/gtkb-spec-pipeline-f1-001.md:51.
- Proposal adds `get_provisional_specs()` for rows where `authority='provisional'` and `provisional_until` is set at bridge/gtkb-spec-pipeline-f1-001.md:88.
- `rg -n "authority|testability|provisional_until|get_provisional_specs|get_specs_affected_by|affected_by" src tests docs README.md` in the GT-KB checkout returned no current implementation matches.

**Risk/impact:** Rows can drift into invalid states: provisional without replacement, replacement set on permanent specs, typoed authority strings, or references to nonexistent specs. That weakens F8 provenance reconciliation before it starts.

**Required action:** Define and test invariants: allowed authority values, when `provisional_until` is required, whether it must reference an existing/current spec, whether non-provisional rows may set it, and whether the clearer name should be `replacement_spec_id`.

## Answers to Proposal Questions

1. Priority normalization should not be part of F1. It needs a separate compatibility proposal because current GT-KB treats priorities as project-defined and SQLite enforcement is not additive.
2. The authority taxonomy needs at least an `unknown`/`unspecified` legacy state. Consider separating `owner_stated`, `owner_approved`, `inferred_from_code`, `inherited`, and `provisional` if downstream ranking will distinguish direct owner language from later approval.
3. JSON is acceptable for low-volume `constraints` if schema validation is strict. `affected_by` is queryable relationship data; prefer a normalized table unless the implementation commits to exact JSON containment.
4. GT-KB currently recognizes five spec types. If `documentation` is added, make that an explicit extension. Closed validation is safer for core types, with a documented escape hatch only if project-specific types are truly required.

## Conditions For GO

1. Revise the proposal baseline so `type` is treated as existing functionality, not a new column.
2. Change the authority migration default away from `stated` for legacy rows, or provide a safe two-phase enrichment plan before any trust ranking consumes authority.
3. Remove priority CHECK normalization from F1 or split it into its own migration proposal.
4. Specify JSON serialization, validation, parsed output fields, and exact query behavior for `constraints` and `affected_by`.
5. Define provisional lifecycle invariants and tests.
6. Expand the test plan to include migration from a database that already has `type`, insertion/update carry-forward for all new metadata fields, exact `affected_by` matching, invalid JSON rejection, invalid enum rejection, and backward compatibility for existing callers.

