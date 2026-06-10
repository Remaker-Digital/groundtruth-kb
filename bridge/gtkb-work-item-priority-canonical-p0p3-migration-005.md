REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-backlog-data-hygiene-f3-revised-2-new-pauth
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Defect-Fix Proposal REVISED-2 - Canonicalize work_items.priority field values to P0/P1/P2/P3 schema (data hygiene migration)

bridge_kind: prime_proposal
Document: gtkb-work-item-priority-canonical-p0p3-migration
Version: 005 (REVISED-2)
Reviewed-against: bridge/gtkb-work-item-priority-canonical-p0p3-migration-004.md (NO-GO)
Carries-forward: bridge/gtkb-work-item-priority-canonical-p0p3-migration-003.md (REVISED-1, Codex-acting-Prime)
Date: 2026-05-27 UTC

Project Authorization: PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3396

target_paths: ["scripts/migrate_work_item_priority_canonical.py", "tests/scripts/test_migrate_work_item_priority_canonical.py", "groundtruth.db"]

## Revision Claim

REVISED-2 addresses NO-GO -004's two P1 findings while preserving the correctness improvements landed in REVISED-1 (-003):

- **NO-GO -004 P1 (Cited Standing Authorization Does Not Cover MemBase Mutation)**: this revision replaces the citation of PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (allowed_mutation_classes=["source","test_addition","hook_upgrade"], not covering data_migration) with the newly-authored sibling PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001, scoped to PROJECT-GTKB-RELIABILITY-FIXES with allowed_mutation_classes=["data_migration"] and included_work_item_ids=["WI-3396"]. Owner authorization for the new PAUTH was captured via AskUserQuestion at S363 (2026-05-27) and recorded as DELIB-2239 with formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-2239.json`.

- **NO-GO -004 P1 (WI-3396 Not Attached To The Cited Reliability Project)**: this revision clarifies that LO's check of `current_work_items.project_name` field reads the legacy compatibility column, not the canonical project-WI relationship. The canonical authority is `project_work_item_memberships`. Live evidence (S363, 2026-05-27): WI-3396 has an active membership row at `project_id='PROJECT-GTKB-RELIABILITY-FIXES'`, `status='active'`, `changed_at='2026-05-27T16:54:36+00:00'`, `change_reason='S363 hygiene fast-lane: F3 priority canonicalization WI attaches to standing reliability-fixes project'`. The legacy project_name field is NULL because `gt backlog add` was called without `--project-name` to avoid the known doubled-prefix bug (auto-memory `backlog_add_doubled_prefix_membership_bug`); membership was then established via `gt projects add-item PROJECT-GTKB-RELIABILITY-FIXES WI-3396 --change-reason ...`. Additionally, the new PAUTH includes WI-3396 in `included_work_item_ids` explicitly, providing per-WI authorization regardless of project-membership state.

The technical correctness revisions from -003 (live in-root counts, current KnowledgeDB API, canonical 77-row migration target, null preservation) are preserved.

## Bridge INDEX Audit Trail

This artifact is filed under `bridge/`. The live `bridge/INDEX.md` entry for this document is the canonical queue state. This revision adds:

`REVISED: bridge/gtkb-work-item-priority-canonical-p0p3-migration-005.md`

No prior bridge versions are deleted or rewritten. The prior chain remains:

- `NO-GO: bridge/gtkb-work-item-priority-canonical-p0p3-migration-004.md`
- `REVISED: bridge/gtkb-work-item-priority-canonical-p0p3-migration-003.md`
- `NO-GO: bridge/gtkb-work-item-priority-canonical-p0p3-migration-002.md`
- `NEW: bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal is filed under `bridge/` and updates `bridge/INDEX.md` append-only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - MemBase `work_items` is a canonical artifact; the migration repairs legacy priority values to match the existing CLI schema.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each acceptance requirement to concrete tests and commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item are declared above; new PAUTH cited grants explicit WI-3396 inclusion and data_migration authority.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization for the new PAUTH was captured via AskUserQuestion and recorded as DELIB-2239 with formal-artifact-approval packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - MemBase `work_items` remains the canonical backlog source of truth.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the change has no hook surface impact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the migration is append-only and records per-row change reasons.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - row updates are versioned through existing work-item lifecycle mechanics.

## Prior Deliberations

- `DELIB-2239` - **owner_decision_deliberation_id for the new PAUTH**: S363 AskUserQuestion (2026-05-27) authorizing Path A "Author new PAUTH with data_migration class" for F3 NO-GO -004 resolution; formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-2239.json`.
- `DELIB-2107` - bridge compliance and WI/project membership enforcement precedent (gtkb-bridge-compliance-wi-project-membership VERIFIED).
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing DB-backed backlog source of truth.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase `work_items` canonical pivot.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - post-migration steady state is MemBase only.
- `DELIB-1791` - prior LO scoping review for backlog source-of-truth work.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - spec-to-project-to-WI-to-bridge enforcement chain.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane direction (parent of PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING); new PAUTH is sibling to this on the same project.

## Owner Decisions / Input

- **`S363 AskUserQuestion answer 2026-05-27 (DELIB-2239)`**: Owner selected "Author new PAUTH with data_migration class" in response to F3 NO-GO -004 path question. This decision authorized the new sibling PAUTH `PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001` with `allowed_mutation_classes=["data_migration"]` and `included_work_item_ids=["WI-3396"]`. Formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-2239.json`.
- **`S363 AskUserQuestion answer 2026-05-27 (earlier)`**: Owner selected "Address data hygiene (F2 + F3)" in response to the backlog prioritization+completeness report direction question, authorizing the F3 work as in-scope hygiene.
- **`PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001`**: active project authorization (created 2026-05-27T20:24:45Z via `gt projects authorize`, owner-decision=DELIB-2239) covers this F3 work; includes WI-3396 explicitly with data_migration mutation class.

## Requirement Sufficiency

Existing requirements sufficient. The canonical P0-P3 priority schema is already enforced by `gt backlog add --priority [P0|P1|P2|P3]` per the CLI source. This proposal migrates legacy non-canonical rows to comply with the existing enforced schema; no new requirement is created. The new PAUTH is an authorization scope artifact, not a new requirement.

## Live In-Root Reproduction Evidence

Carried forward from REVISED-1 (-003) with re-verification at REVISED-2 filing time:

```powershell
@'
from collections import Counter
from pathlib import Path
from groundtruth_kb.db import KnowledgeDB

db = KnowledgeDB(Path('groundtruth.db'))
rows_open = db.list_work_items(resolution_status='open')
for label, rows in [('open', rows_open)]:
    counts = Counter(row.get('priority') for row in rows)
    noncanon = {k: v for k, v in counts.items() if k not in {'P0','P1','P2','P3', None}}
    print(label, 'total', len(rows), 'counts', sorted(counts.items(), key=lambda item: (item[0] is None, str(item[0]))))
    print(label, 'noncanonical_nonnull', sum(noncanon.values()), sorted(noncanon.items(), key=lambda item: str(item[0])))
'@ | python -
```

Observed live output (S363, 2026-05-27, evidence preserved from REVISED-1):

```text
open total 191 counts [('HIGH', 2), ('LOW', 1), ('MEDIUM', 4), ('P0', 1), ('P1', 25), ('P2', 30), ('P3', 21), ('high', 7), ('low', 55), ('medium', 8), (None, 37)]
open noncanonical_nonnull 77 [('HIGH', 2), ('LOW', 1), ('MEDIUM', 4), ('high', 7), ('low', 55), ('medium', 8)]
```

WI-3396 membership state (live, S363, 2026-05-27):

```text
project_work_item_memberships WHERE work_item_id='WI-3396':
  project_id=PROJECT-GTKB-RELIABILITY-FIXES status=active changed_at=2026-05-27T16:54:36+00:00
  reason='S363 hygiene fast-lane: F3 priority canonicalization WI attaches to standing reliability-fixes project'

current_work_items WHERE id='WI-3396':
  project_name=NULL (legacy compatibility column; not the canonical authority)
  approval_state=auq_required (backfilled by parallel WI-3271 Slice 1 classifier; this proposal's authorization comes via the new PAUTH)
```

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:
- `scripts/migrate_work_item_priority_canonical.py`
- `tests/scripts/test_migrate_work_item_priority_canonical.py`
- `groundtruth.db`

## Proposed Scope

IP-1 - Canonical mapping function

Add `_canonical_mapping(value)` to `scripts/migrate_work_item_priority_canonical.py`:

- `P0`, `P1`, `P2`, and `P3` return identity.
- `low` and `LOW` return `P3`.
- `medium` and `MEDIUM` return `P2`.
- `high` and `HIGH` return `P1`.
- `None` and empty string return `None` (null preservation).
- Any other value raises `UnknownPriorityValueError(value)`.

IP-2 - Migration script

`scripts/migrate_work_item_priority_canonical.py` will:

- Read the intended scope with `KnowledgeDB.list_work_items(resolution_status='open')`.
- Preserve null priority values (no auto-fill).
- For each row whose current non-null priority differs from its canonical priority, insert a new work-item version with `KnowledgeDB.insert_work_item()`.
- Record `change_reason='S363 F3 priority canonicalization migration; original=<original> -> canonical=<canonical> per WI-3396 / DELIB-2239 / PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001'`.
- Use `changed_by='prime-builder/claude/B'` (or `prime-builder/codex/A` depending on which harness executes).
- Default to dry-run; require `--apply` for live mutation.
- Support `--json` for audit output.
- Be idempotent: a second applied run reports zero mutations.

IP-3 - Regression test

`tests/scripts/test_migrate_work_item_priority_canonical.py` will include:

1. `test_canonical_mapping_completeness` - table-driven test covering all known values + control unknown value asserting `UnknownPriorityValueError`.
2. `test_migration_idempotent` - run migration twice; second run reports zero mutations.
3. `test_post_migration_priority_invariant` - assert all `resolution_status='open'` work_items.priority values are in `{'P0','P1','P2','P3', None}`.

## Acceptance Criteria

1. All 77 live non-null non-canonical open-priority rows are migrated through append-only `insert_work_item` versions.
2. Null priority rows are preserved as null (no auto-fill).
3. Post-migration invariant: every current open work item has priority in `{'P0', 'P1', 'P2', 'P3', None}`.
4. Migration script is idempotent: a second applied run reports zero mutations and exits success.
5. All 3 regression tests PASS via `python -m pytest tests/scripts/test_migrate_work_item_priority_canonical.py -v`.
6. Live in-root post-migration MemBase query confirms no non-null non-canonical priority values remain for `resolution_status='open'`.
7. WI-3396 transitions to `resolved` upon VERIFIED.
8. PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001 may be marked completed via `gt projects complete-authorization` post-VERIFIED, leaving the standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING in place for other reliability work.

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_canonical_mapping_completeness` | `python -m pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_canonical_mapping_completeness -q` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_migration_idempotent` | `python -m pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_migration_idempotent -q` | PASS |
| `GOV-STANDING-BACKLOG-001` | `test_post_migration_priority_invariant` | `python -m pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_post_migration_priority_invariant -q` | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Sample history check | `python -m groundtruth_kb history --work-item <migrated-id>` | New version shows original and canonical priority in `change_reason` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | In-root live data probe | `python -c "from groundtruth_kb.db import KnowledgeDB; from pathlib import Path; print(len(KnowledgeDB(Path('groundtruth.db')).list_work_items(resolution_status='open')))"` | Reads in-root `groundtruth.db` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH covers WI-3396 with data_migration | `python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES` | Shows both PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING and PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001 active; latter includes WI-3396 with data_migration class |

## Risk And Rollback

Risk: `medium -> P2` and `high -> P1` may not reflect owner intent for a specific legacy item. Mitigation: each migrated row records the original priority in `change_reason`; an owner-directed follow-up can correct any specific item with another append-only version.

Risk: future non-CLI write paths may reintroduce drift. Mitigation: the invariant test will fail if drift returns.

Risk: PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001 was created in the same session as this revision; LO may want to verify the PAUTH record independently. Mitigation: PAUTH is queryable via `gt projects authorizations PROJECT-GTKB-RELIABILITY-FIXES` and the source DELIB-2239 + approval packet are in the standard locations.

Rollback: insert a new work-item version restoring the original priority for any affected row, citing the rollback reason in `change_reason`. The new PAUTH can be revoked via `gt projects revoke-authorization PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001` if needed.

## Required Revision Response

- **NO-GO -004 Finding P1 (PAUTH doesn't cover MemBase mutation)**: addressed by replacing standing PAUTH citation with new PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001 (allowed_mutation_classes=["data_migration"], included_work_item_ids=["WI-3396"]).
- **NO-GO -004 Finding P1 (WI-3396 not attached to project)**: addressed by clarifying that `project_work_item_memberships` (canonical authority) has an active row; legacy `project_name` field is NULL but not authoritative; new PAUTH includes WI-3396 in `included_work_item_ids` regardless.
- **NO-GO -004 Finding P2 (Correctness Revisions Accepted)**: preserved from REVISED-1 — live in-root counts (77 rows), current KnowledgeDB API, null preservation, idempotency commitment.
- **NO-GO -004 mandatory preflights**: this revision preserves the mandatory preflight pass observed in -004's review of -003.

## Files Expected To Change

- `scripts/migrate_work_item_priority_canonical.py` (NEW)
- `tests/scripts/test_migrate_work_item_priority_canonical.py` (NEW)
- `groundtruth.db` (mutating: append-only insert_work_item rows for 77 migrated items)

## Recommended Commit Type

`fix` - data-hygiene defect repair; no new capability surface beyond the migration script and its regression test.
