REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-05-27-prime-builder-bridge-continuation
author_model: GPT-5
author_model_version: codex
author_model_configuration: reasoning=medium
author_metadata_source: session

# Revised Proposal - Canonicalize work_items.priority to P0/P1/P2/P3

bridge_kind: implementation_proposal
Document: gtkb-work-item-priority-canonical-p0p3-migration
Version: 003 (REVISED)
Date: 2026-05-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3396

target_paths: ["scripts/migrate_work_item_priority_canonical.py", "tests/scripts/test_migrate_work_item_priority_canonical.py", "groundtruth.db"]

## Revision Claim

This revision addresses the NO-GO findings in `bridge/gtkb-work-item-priority-canonical-p0p3-migration-002.md` by replacing stale out-of-root evidence with live in-root MemBase counts, correcting the migration count from 37 to 77 non-null non-canonical open rows, using the current `KnowledgeDB` API, and adding explicit bridge INDEX audit-trail evidence.

## Bridge INDEX Audit Trail

This artifact is filed under `bridge/`. The live `bridge/INDEX.md` entry for this document is the canonical queue state. This revision adds:

`REVISED: bridge/gtkb-work-item-priority-canonical-p0p3-migration-003.md`

No prior bridge versions are deleted or rewritten. The prior chain remains:

- `NO-GO: bridge/gtkb-work-item-priority-canonical-p0p3-migration-002.md`
- `NEW: bridge/gtkb-work-item-priority-canonical-p0p3-migration-001.md`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal is filed under `bridge/` and updates `bridge/INDEX.md` append-only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - MemBase `work_items` is a canonical artifact; the migration repairs legacy priority values to match the existing CLI schema.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each acceptance requirement to concrete tests and commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item are declared above.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner direction was recorded as prior AskUserQuestion evidence for the reliability data-hygiene lane.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - MemBase `work_items` remains the canonical backlog source of truth.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the change has no hook surface impact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the migration is append-only and records per-row change reasons.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - row updates are versioned through existing work-item lifecycle mechanics.

## Prior Deliberations

- `DELIB-2107` - bridge compliance and WI/project membership enforcement precedent.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - owner directive formalizing DB-backed backlog source of truth.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase `work_items` canonical pivot.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - post-migration steady state is MemBase only.
- `DELIB-1791` - prior LO scoping review for backlog source-of-truth work.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - spec-to-project-to-WI-to-bridge enforcement chain.

## Owner Decisions / Input

- `S363 AskUserQuestion answer 2026-05-27`: Owner selected "Address data hygiene (F2 + F3)" in response to the backlog prioritization and completeness report direction question.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`: active standing project authorization covers this reliability fast-lane data-hygiene work.

No new owner decision is required for this revision. The NO-GO findings concern proposal correctness and mandatory gate evidence, not owner intent.

## Live In-Root Reproduction Evidence

Command run from `E:\GT-KB` against `groundtruth.db`:

```powershell
@'
from collections import Counter
from pathlib import Path
from groundtruth_kb.db import KnowledgeDB

db = KnowledgeDB(Path('groundtruth.db'))
rows_open = db.list_work_items(resolution_status='open')
rows_nonterminal = db.get_open_work_items()
for label, rows in [('open', rows_open), ('nonterminal', rows_nonterminal)]:
    counts = Counter(row.get('priority') for row in rows)
    noncanon = {k: v for k, v in sorted(counts.items(), key=lambda item: (item[0] is None, str(item[0]))) if k not in {'P0','P1','P2','P3', None}}
    print(label, 'total', len(rows), 'counts', sorted(counts.items(), key=lambda item: (item[0] is None, str(item[0]))))
    print(label, 'noncanonical_nonnull', sum(noncanon.values()), sorted(noncanon.items(), key=lambda item: str(item[0])))
'@ | python -
```

Observed live output:

```text
open total 191 counts [('HIGH', 2), ('LOW', 1), ('MEDIUM', 4), ('P0', 1), ('P1', 25), ('P2', 30), ('P3', 21), ('high', 7), ('low', 55), ('medium', 8), (None, 37)]
open noncanonical_nonnull 77 [('HIGH', 2), ('LOW', 1), ('MEDIUM', 4), ('high', 7), ('low', 55), ('medium', 8)]
nonterminal total 194 counts [('HIGH', 2), ('LOW', 1), ('MEDIUM', 4), ('P0', 1), ('P1', 25), ('P2', 31), ('P3', 21), ('high', 7), ('low', 55), ('medium', 8), (None, 39)]
nonterminal noncanonical_nonnull 77 [('HIGH', 2), ('LOW', 1), ('MEDIUM', 4), ('high', 7), ('low', 55), ('medium', 8)]
```

## Proposed Scope

IP-1 - Canonical mapping function

Add `_canonical_mapping(value)` to `scripts/migrate_work_item_priority_canonical.py`:

- `P0`, `P1`, `P2`, and `P3` return identity.
- `low` and `LOW` return `P3`.
- `medium` and `MEDIUM` return `P2`.
- `high` and `HIGH` return `P1`.
- `None` and empty string return `None`.
- Any other value raises `UnknownPriorityValueError(value)`.

IP-2 - Migration script

`scripts/migrate_work_item_priority_canonical.py` will:

- Read the exact intended scope with `KnowledgeDB.list_work_items(resolution_status='open')`.
- Preserve null priority values.
- For each row whose current non-null priority differs from its canonical priority, insert a new work-item version with `KnowledgeDB.insert_work_item()`.
- Record `change_reason='S363 F3 priority canonicalization migration; original=<original> -> canonical=<canonical> per WI-3396'`.
- Use `changed_by='prime-builder/codex/A'`.
- Support dry-run by default and `--apply` for mutation.
- Support `--json` for audit output.
- Be idempotent: a second applied run reports zero mutations.

IP-3 - Regression test

`tests/scripts/test_migrate_work_item_priority_canonical.py` will include:

1. `test_canonical_mapping_completeness`.
2. `test_migration_idempotent`.
3. `test_post_migration_priority_invariant`.

## Acceptance Criteria

1. All 77 live non-null non-canonical open priority rows are migrated through append-only `insert_work_item` versions.
2. Null priority rows are preserved as null.
3. The authoritative post-migration invariant is that every current open work item has priority in `{'P0', 'P1', 'P2', 'P3', None}`.
4. The migration is idempotent: a second applied run reports zero mutations and exits success.
5. The regression test command passes.
6. A live in-root post-migration MemBase query confirms no non-null non-canonical priority values remain for `resolution_status='open'`.

## Specification-Derived Verification Plan

| Spec citation | Verification artifact | Command | Expected outcome |
|---|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_canonical_mapping_completeness` | `python -m pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_canonical_mapping_completeness -q` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_migration_idempotent` | `python -m pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_migration_idempotent -q` | PASS |
| `GOV-STANDING-BACKLOG-001` | `test_post_migration_priority_invariant` | `python -m pytest tests/scripts/test_migrate_work_item_priority_canonical.py::test_post_migration_priority_invariant -q` | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Sample history check | `python -m groundtruth_kb history --work-item <migrated-id>` | New version shows original and canonical priority in `change_reason` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | In-root live data probe | `python -c "from groundtruth_kb.db import KnowledgeDB; from pathlib import Path; print(len(KnowledgeDB(Path('groundtruth.db')).list_work_items(resolution_status='open')))"` | Reads in-root `groundtruth.db` |

## Risk And Rollback

Risk: `medium -> P2` and `high -> P1` may not reflect the owner intent for a specific legacy item. Mitigation: each migrated row records the original priority in `change_reason`; an owner-directed follow-up can correct any specific item with another append-only version.

Risk: future non-CLI write paths may reintroduce drift. Mitigation: the invariant test will fail if drift returns.

Rollback: insert a new work-item version restoring the original priority for any affected row, citing the rollback reason in `change_reason`.

## Required Revision Response

- Finding 1, bridge INDEX evidence: addressed by the `Bridge INDEX Audit Trail` section.
- Finding 2, row count undercount: addressed with live in-root counts and corrected acceptance criteria.
- Finding 3, API mismatch: addressed by specifying `KnowledgeDB.list_work_items(resolution_status='open')`.
- Finding 4, out-of-root stale evidence: addressed by replacing `C:/temp/backlog_open.json` with a live in-root `groundtruth.db` query.

## Pre-Filing Preflights

Prime will file this revision with the bridge helper so candidate applicability and ADR/DCL clause preflights run before the live `bridge/INDEX.md` update.
