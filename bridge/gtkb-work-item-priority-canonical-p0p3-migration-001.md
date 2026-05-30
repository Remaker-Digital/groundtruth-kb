NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-backlog-data-hygiene-f3-priority-canonical
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Defect-Fix Proposal - Canonicalize work_items.priority field values to P0/P1/P2/P3 schema (data hygiene migration)

bridge_kind: implementation_proposal
Document: gtkb-work-item-priority-canonical-p0p3-migration
Version: 001 (NEW)
Date: 2026-05-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3396

target_paths: ["scripts/migrate_work_item_priority_canonical.py", "tests/scripts/test_migrate_work_item_priority_canonical.py", "groundtruth.db"]

## Claim

The `work_items.priority` field contains four incompatible vocabularies that prevent reliable sorting, filtering, or governance signal across the live MemBase backlog: P-style (`P0/P1/P2/P3`, 73 rows), lowercase (`low/medium/high`, 70 rows), UPPERCASE (`LOW/MEDIUM/HIGH`, 7 rows), and null/`(none)` (41 rows), across 191 open work items. The `gt backlog add` CLI already enforces `[P0|P1|P2|P3]` as canonical with default `P3` (see `groundtruth-kb/src/groundtruth_kb/cli/backlog.py` `--priority` option). The canonical schema decision is therefore already made by the existing CLI surface; this proposal is a one-shot append-only data migration to bring legacy rows into compliance, plus a regression assertion to prevent future drift.

## Defect / Reproduction

Live data state probe (S363 backlog review, 2026-05-27):

```
$ python -c "import json; from collections import Counter; b=json.load(open('C:/temp/backlog_open.json')); print(sorted(Counter(wi.get('priority') for wi in b).items(), key=lambda x: (x[0] is None, str(x[0]))))"
[('HIGH', 2), ('LOW', 1), ('MEDIUM', 4), ('P0', 1), ('P1', 25), ('P2', 28), ('P3', 19), ('high', 7), ('low', 55), ('medium', 8), (None, 41)]

$ python -m groundtruth_kb backlog add --help 2>&1 | grep -i priority
  --priority [P0|P1|P2|P3]        Candidate priority.  [default: P3]
```

CLI canonical schema (`P0|P1|P2|P3`) and live data state (11 distinct values spanning 4 vocabularies) are inconsistent. New writes via the CLI are canonical; legacy writes via direct DB paths drifted.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `scripts/migrate_work_item_priority_canonical.py`
- `tests/scripts/test_migrate_work_item_priority_canonical.py`
- `groundtruth.db`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal follows NEW/REVISED/GO/NO-GO/VERIFIED workflow
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - MemBase work_items is a canonical artifact; migration brings legacy data into compliance with the CLI's already-enforced schema
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant cross-cutting specs in this section
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan section below maps acceptance criteria to specific test commands
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header lines satisfied above with active PAUTH
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision captured via AskUserQuestion (recorded in Owner Decisions section)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths within `E:\GT-KB` per In-Root Placement Evidence section
- `GOV-STANDING-BACKLOG-001` - work_items is canonical backlog source-of-truth; this proposal preserves and improves backlog signal quality
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - data-only change with no hook surface impact; parity preserved
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - creates two durable artifacts (migration script + regression test); append-only audit trail for migrated rows
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - migration triggers `insert_work_item` per-row append-only versioning with `change_reason` traceability

## Prior Deliberations

- `DELIB-2107` - bridge thread `gtkb-bridge-compliance-wi-project-membership` VERIFIED, 10 versions; established the mechanical enforcement chain for new WI writes that this proposal supplements with priority schema compliance
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing standing backlog as DB-backed source-of-truth; this proposal contributes priority field data quality to that backlog
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase work_items is canonical backlog; this proposal preserves canonical pivot
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - owner decision: post-migration steady state is MemBase only; this work strengthens that steady state
- `DELIB-1791` - prior LO scoping review for GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH; this proposal addresses a downstream data-quality gap noted in that scoping
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive: spec to project to WI to bridge mechanical enforcement; this proposal extends the enforcement surface to include priority schema

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27`: Owner selected "Address data hygiene (F2 + F3)" in response to backlog prioritization+completeness report direction question. This answer authorizes F3 (this proposal) as in-scope hygiene work; recorded in this turn's transcript.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization covers F3 as reliability fast-lane data hygiene; verified via `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES`.

## Requirement Sufficiency

Existing requirements sufficient. The canonical P0-P3 priority schema is already enforced by `gt backlog add --priority [P0|P1|P2|P3]` per the CLI source. This proposal migrates legacy non-canonical rows to comply with the existing enforced schema; no new requirement is created. Optional follow-on (out of this scope): formalize the schema as `DCL-WORK-ITEM-PRIORITY-CANONICAL-P0-P3` with formal-artifact-approval packet, sibling thread.

## Proposed Scope

IP-1 - Canonical mapping function

Add `_canonical_mapping(value)` to `scripts/migrate_work_item_priority_canonical.py`. Behavior:
- `'P0' | 'P1' | 'P2' | 'P3'` returns identity (no change needed)
- `'low' | 'LOW'` returns `'P3'`
- `'medium' | 'MEDIUM'` returns `'P2'`
- `'high' | 'HIGH'` returns `'P1'`
- `None` returns `None` (null preserved; migration does NOT auto-fill nulls)
- Empty string returns `None`
- Any other value raises `UnknownPriorityValueError(value)` with the offending value (fail-loud)

Scope refinement: 37 rows have non-canonical non-null values requiring migration. 41 null rows are preserved as-is (owner can backfill priorities individually if intent was a specific level).

IP-2 - Migration script

`scripts/migrate_work_item_priority_canonical.py` operates as follows:
- Read all open `work_items` rows via `KnowledgeDB.list_work_items(status_filter=None)`
- For each row where current priority != canonical priority, call `KnowledgeDB.insert_work_item()` with new version recording `change_reason='S363 F3 priority canonicalization migration; original=<original> -> canonical=<canonical> per WI-3396'` and `changed_by='prime-builder/claude/B'`
- Append-only - original versions preserved per ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- Idempotent: subsequent runs detect that all priorities are canonical and exit cleanly with zero mutations
- Dry-run flag (`--dry-run`): emits mapping plan as JSON, no DB writes
- JSON output flag (`--json`): emits per-row migration result for audit

IP-3 - Regression test

`tests/scripts/test_migrate_work_item_priority_canonical.py` adds three tests:
1. `test_canonical_mapping_completeness` - table-driven test over all known canonical and legacy values plus a control unknown value that asserts `UnknownPriorityValueError`
2. `test_migration_idempotent` - run migration twice against a fixture DB; second run reports zero mutations
3. `test_post_migration_priority_invariant` - assert all open work_items.priority values are in `{'P0','P1','P2','P3', None}` after migration

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (canonical schema compliance) | test_canonical_mapping_completeness | pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_canonical_mapping_completeness -v | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (idempotency) | test_migration_idempotent | pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_migration_idempotent -v | PASS |
| GOV-STANDING-BACKLOG-001 (post-migration invariant) | test_post_migration_priority_invariant | pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_post_migration_priority_invariant -v | PASS |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (append-only audit trail) | Manual sample inspection via gt history | python -m groundtruth_kb history --work-item WI-XXXX (any migrated WI) | shows new version with change_reason citing this WI-3396 |

## Acceptance Criteria

1. All 37 non-null non-canonical priority rows (`low/LOW/medium/MEDIUM/high/HIGH`) are migrated to canonical `P0/P1/P2/P3` via append-only `insert_work_item`; original versions preserved.
2. Migration script is idempotent: re-running produces zero mutations and exits success.
3. All 3 regression tests PASS via `pytest tests/scripts/test_migrate_work_item_priority_canonical.py -v`.
4. Post-migration probe `python -c "import json; from collections import Counter; b=json.load(open('backlog_dump.json')); print(Counter(wi.get('priority') for wi in b))"` shows only `P0|P1|P2|P3|None` values.
5. WI-3396 transitions to `resolved` upon VERIFIED via the standard post-impl flow.

## Risks / Rollback

- Risk: mapping `medium -> P2` may not preserve owner intent for individual items where the informal "medium" meant something different. Mitigation: per-row change_reason documents the mapping; owner can issue a corrective `insert_work_item` to set a different priority for any specific row.
- Risk: future writes via paths that bypass the CLI may re-introduce drift. Mitigation: regression test asserts the invariant on every test run; future drift surfaced as test failure rather than silent corruption.
- Risk: null rows (41) remain unprioritized which may obscure work selection. Mitigation: null preservation is intentional in this scope; a separate proposal can address null backfill with owner AUQ per group.
- Rollback: revert to pre-migration version via `insert_work_item` with the original priority value and `change_reason='rollback of S363 F3 migration per <reason>'`. Append-only audit trail preserves every state for the rollback.

## Files Expected To Change

- `scripts/migrate_work_item_priority_canonical.py` (NEW)
- `tests/scripts/test_migrate_work_item_priority_canonical.py` (NEW)
- `groundtruth.db` (mutating: append-only insert_work_item rows for migrated items)

## Recommended Commit Type

`fix` - data-hygiene defect repair; no new capability surface beyond the migration script and its regression test.
