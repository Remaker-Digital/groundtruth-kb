# F1: Spec Schema Enrichment — Implementation Proposal

**Feature:** F1 — Spec Schema Enrichment
**Target repo:** groundtruth-kb
**Tracker:** DOC-GTKB-SPEC-PIPELINE
**Corruption vectors addressed:** P1 (workaround calcification), P3 (assumption-driven implementation), P4 (weak tests from unclear specs)
**Dependencies:** None (foundational — all other features depend on this)
**Prior deliberations:** DELIB-0706 (GT-KB scope), DELIB-0707 (retroactive migration), DELIB-0708 (structured interview vision), DELIB-0710 (quality ranking criteria)

---

## Problem Statement

The current GT-KB `specifications` table has 16 columns. Agent Red has used this schema to store 2,105 specs across 285 sessions. Analysis of the corpus reveals structural gaps that enable the 5 corruption vectors identified by the owner (S286):

1. **No authority tier** — All specs have equal weight. An `implementation-derived` spec (615 in Agent Red, created by AI observing code) has the same authority as an `owner_directive` spec (757 in Agent Red, stated by the owner). When they conflict, the AI has no signal for which to prefer.

2. **No implementation constraints** — Specs say *what* to build but not *how much* or *what NOT to build*. The AI fills gaps with its own judgment, leading to over-engineering or arbitrary priority decisions (corruption vector P3).

3. **No provisional marking** — Temporary implementations (mock APIs during GUI dev, workaround code) are not distinguishable from permanent implementations. Over time, workarounds get documented as specs and exert bias on future work (corruption vector P1).

4. **No cross-cutting linkage** — Cross-cutting specs (ADR/DCL) have no structured way to declare which functional specs they affect. The ZK architecture spec (SPEC-1843) affects hundreds of other specs but has no explicit linkage to any of them (corruption vector P5, addressed primarily by F4 but requires schema support here).

5. **No testability signal** — 16.3% of Agent Red specs have no assertions. The remaining 83.7% are dominated by `grep` assertions (77.6%) — existence checks that prove code exists but not that it behaves correctly. There is no field indicating whether a spec is testable, and no scoring of assertion strength.

6. **No `type` column in GT-KB** — Agent Red added a `type` column locally (11 values: requirement, governance, architecture_decision, etc.). GT-KB lacks this, forcing projects to overload the `tags` field for type classification.

## Evidence from Agent Red

| Finding | Data | Implication |
|---------|------|-------------|
| 615 implementation-derived specs | 29% of corpus | Nearly 1/3 of specs document code, not intent — no authority signal to distinguish them |
| Priority field inconsistent | 342/2105 have priority (16.2%), using 10 different scales (P0-P4, high/medium/low, critical/deferred) | No standardized priority — AI cannot reliably sequence work |
| Scope field sparse | 270/2105 have scope (12.8%) | Most specs don't declare what they affect |
| Type field useful but local | 11 types, `requirement` = 95.4% | Type differentiation valuable (governance, ADR, DCL, protected_behavior) but not in GT-KB schema |
| Average 3.94 versions per spec | Version distribution: v1=48, v2=168, v3=265, v4=1119, v5=410 | Specs require multiple revisions — enriched metadata could reduce this by making intent clearer at creation |

**Counterfactual test:** If authority tiers had existed from session 1, the 615 implementation-derived specs would have been created with `authority=inferred` rather than equal authority to owner directives. When cross-cutting changes like ZK (S270+) required system-wide redesign, the AI would have known which specs were authoritative intent vs. which were just describing code that happened to exist — reducing the "substantial number of defects and bad outcomes" the owner observed.

## Proposed Schema Changes

Add the following columns to the `specifications` table in GT-KB:

### New Columns

| Column | Type | Default | Purpose |
|--------|------|---------|---------|
| `type` | TEXT | `'requirement'` | Spec classification. Enum: `requirement`, `governance`, `architecture_decision`, `design_constraint`, `protected_behavior`, `documentation`. Replaces tag-based type overloading. |
| `authority` | TEXT | `'stated'` | Who originated this spec and with what weight. Enum: `stated` (owner said it), `inferred` (AI derived from code/context), `provisional` (temporary, has expiration), `inherited` (derived from cross-cutting spec). |
| `constraints` | TEXT (JSON) | `NULL` | Implementation constraints as structured JSON. Schema: `{"complexity_ceiling": "simple|moderate|complex", "excluded_approaches": [...], "decision_authority": "owner|ai|either", "notes": "..."}` |
| `provisional_until` | TEXT | `NULL` | If authority=provisional, the spec ID that replaces this when implemented. e.g., a mock API spec is provisional_until=SPEC-NNNN (the real API spec). NULL means permanent. |
| `affected_by` | TEXT (JSON) | `NULL` | List of cross-cutting spec IDs (ADR/DCL) that constrain this spec. e.g., `["ADR-006", "DCL-002"]`. Populated by F4 (constraint propagation) but the column must exist first. |
| `testability` | TEXT | `NULL` | Testability classification. Enum: `automatable` (can be verified by assertion), `observable` (requires human/visual check), `structural` (verified by code existence), `untestable` (no known verification method). Populated by F3 (quality gate) but column must exist first. |

### Modified Columns

| Column | Change | Rationale |
|--------|--------|-----------|
| `priority` | Add CHECK constraint: `P0, P1, P2, P3, P4, deferred` | Standardize the 10 inconsistent values found in Agent Red |

### Migration Path

The schema change is additive — all new columns have defaults or allow NULL. Existing data is preserved. No destructive changes.

**GT-KB migration:**
1. `ALTER TABLE specifications ADD COLUMN type TEXT DEFAULT 'requirement'`
2. `ALTER TABLE specifications ADD COLUMN authority TEXT DEFAULT 'stated'`
3. `ALTER TABLE specifications ADD COLUMN constraints TEXT`
4. `ALTER TABLE specifications ADD COLUMN provisional_until TEXT`
5. `ALTER TABLE specifications ADD COLUMN affected_by TEXT`
6. `ALTER TABLE specifications ADD COLUMN testability TEXT`

**Agent Red retroactive enrichment (Phase E, after all features ship):**
1. Populate `authority` from existing tags: specs tagged `owner_directive` → `stated`, specs tagged `implementation-derived` → `inferred`
2. Populate `type` from Agent Red's existing type column (already populated for all 2,105 specs)
3. Populate `constraints` for specs where the implementation history reveals over-engineering or assumption-driven choices
4. Mark known provisional specs (mock APIs, workaround code) with `provisional_until` linking to their permanent replacement
5. Populate `affected_by` for all specs in ZK/security/RBAC scope using F4's propagation logic
6. Populate `testability` using F3's quality gate scoring

## API Changes

The GT-KB Python API (`KnowledgeDB` class) needs:

1. **`insert_spec()`** — Accept new columns as optional parameters. Existing callers unaffected (all new fields have defaults).
2. **`update_spec()`** — Accept new columns for enrichment updates.
3. **`list_specs()`** — Accept new filter parameters: `type=`, `authority=`, `testability=`. Already accepts keyword filters; just needs new column awareness.
4. **`get_provisional_specs()`** — New method. Returns all specs where `authority='provisional'` and `provisional_until` is set. Used by F8 (provenance reconciliation).
5. **`get_specs_affected_by(spec_id)`** — New method. Returns all specs where `affected_by` contains the given spec ID. Used by F4 (constraint propagation).

## Test Plan

1. **Schema migration test** — Verify ALTER TABLE succeeds on existing databases without data loss
2. **API backward compatibility** — All existing `insert_spec()` calls work without new parameters
3. **Filter tests** — `list_specs(type='governance')`, `list_specs(authority='provisional')` return correct results
4. **JSON validation** — `constraints` and `affected_by` fields validate as well-formed JSON on insert
5. **Retroactive enrichment dry run** — Verify Agent Red tag-to-authority mapping produces expected results on a sample of 100 specs

## Implementation Sequence

1. Add columns to GT-KB schema DDL
2. Write migration helper for existing databases
3. Update `insert_spec()` and `update_spec()` to accept new fields
4. Update `list_specs()` with new filter parameters
5. Add new query methods (`get_provisional_specs`, `get_specs_affected_by`)
6. Write tests (schema, API compat, filters, JSON validation)
7. Bump GT-KB version (0.4.0 — minor version for additive schema change)
8. Update Agent Red's `requirements-local.txt` to use new GT-KB version
9. Run retroactive enrichment on Agent Red's 2,105 specs (Phase E)

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Schema migration breaks existing GT-KB consumers | All columns are additive with defaults; no breaking changes |
| `constraints` JSON becomes a dumping ground | Define strict schema in GT-KB docs; validate on insert |
| `authority` enum is too coarse | Start with 4 values; add `contested` or `superseded` later if needed |
| Retroactive enrichment introduces errors | Dry-run on 100-spec sample first; owner reviews before full migration |

## Open Questions for Codex Review

1. Should `priority` normalization (the CHECK constraint) be part of F1 or a separate cleanup task?
2. Is the `authority` enum complete? Are there provenance categories beyond stated/inferred/provisional/inherited?
3. Should `constraints` be a JSON column or separate normalized fields? JSON is more flexible but harder to query.
4. Should the `type` enum be closed (only the 6 listed values) or open (any string)?

---

*Submitted by: S286-Prime*
*Date: 2026-04-12*
*Tracker: DOC-GTKB-SPEC-PIPELINE, Feature F1*
