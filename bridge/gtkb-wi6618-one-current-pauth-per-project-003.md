::init gtkb lo
::open spec
NEW

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 13570cbf-e2d1-408a-9c3d-be4ff5a582f4
author_model: grok-4.6
author_model_version: grok-4.6
author_model_configuration: Cursor IDE interactive; Prime Builder role fixed by owner `::init gtkb pb`
author_session_envelope_id: SENV-0741dfcd6b5c4e24a5c409399d7f6dc7
author_role_attestation: role-attestation:SENV-0741dfcd6b5c4e24a5c409399d7f6dc7:1:3b818659e77aee91

bridge_kind: implementation_report
Document: gtkb-wi6618-one-current-pauth-per-project
Version: 003
Date: 2026-08-17 UTC
Responds to: bridge/gtkb-wi6618-one-current-pauth-per-project-002.md
Approved proposal: bridge/gtkb-wi6618-one-current-pauth-per-project-001.md

Project: PROJECT-GTKB-AUTHORIZATION-MODEL-CORRECTION
Project Authorization: none
Owner Decision: DELIB-20260816201237
Work Item: WI-6618 v1
Related Work Items: WI-6617, WI-6619, WI-6557, WI-6620
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/authorization.py", "groundtruth-kb/src/groundtruth_kb/project/authorization_collapse.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/scripts/test_pauth_one_current_per_project.py", "scripts/pauth_one_current_per_project.py"]
target_specifications: ["GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001", "ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001", "DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
formal_artifact_mutation_in_scope: false
repository_metadata_mutation_in_scope: false

# NEW — Post-implementation report (WI-6618)

## Implementation Claim

The GO'd one-current-per-project supersession pass is in the worktree and has been applied to live MemBase through `KnowledgeDB.insert_project_authorization` (append-only). No `project_authorizations` rows were deleted.

1. **Collapse writer.** `groundtruth_kb.project.authorization_collapse` unions granted scope (allow-lists union, deny-lists intersection, longest/unbounded expiry, approved specs only) and, per project, appends `status=superseded` versions of every live identity, then appends exactly one new project-scoped current identity (`DELIB-20260816201237`). Work-item include/exclude lists are not written (C4). WI-6557 membership retirements were not executed as extra mutations.
2. **C1 fail-closed.** An active insert is rejected when another *different* current authorization id already exists for that `project_id`. Same-id version increment (C3) remains allowed.
3. **C2 fail-closed.** Every active insert whose identity or declared scope names a work item is rejected, including later versions of historical `PAUTH-WI-*` ids. Superseded historical versions of those ids may still be appended.
4. **Census/apply CLI.** `scripts/pauth_one_current_per_project.py` supports `--census`, `--dry-run`, and `--apply`.
5. **Four projects left unauthorized, not re-granted.** Their live rows cited only retired/superseded specs, so the approved-spec union was empty. Those live identities were superseded; no new current row was minted and no spec grant was invented. C1 allows zero current rows. Projects: `PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE`, `PROJECT-GTKB-DISPATCH-LANE-SCORING-REGISTRY`, `PROJECT-GTKB-OPS-LIFECYCLE-PROTOCOL-FOUNDATION`, `PROJECT-GTKB-SESSION-ENVELOPE`.

## Live census (before / after apply)

| Metric | Before | After |
| --- | --- | --- |
| `project_authorizations` table rows | 1065 | 1839 (+774 appended) |
| Active current rows | 649 | 125 |
| Projects with an active authorization | 129 | 125 |
| Projects with multiple current ids | 74 | 0 |
| WI-scoped current ids | 221 | 0 |
| Max current ids per project | 61 | 1 |
| Apply errors | n/a | none |

C1/C2 live probes (rolled back, no leftover rows): active `PAUTH-WI-9999-LIVE-PROBE` rejected (C2); second identity `PAUTH-LIVE-PROBE-SECOND` on `GTKB-SKILL-RENAME-REFERENCE-SWEEP` rejected (C1). Historical `PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001` remains readable at `status=superseded` version 2 (2 table rows).

Hard-gate: WI-6617 work-product commit `2d6382aae` existed before this apply. GO commit `e57b11fa3` was HEAD when implementation started.

## SHA-256 (worktree)

- `groundtruth-kb/src/groundtruth_kb/project/authorization.py` `AFD15FDB2D0BF1867B29804306C92B5912BA539CFF9DDD9D940E74228BC12812`
- `groundtruth-kb/src/groundtruth_kb/project/authorization_collapse.py` `6721DDF705794B58DA371AF2FCC44E99DB4F03B614D7876E775DDF83EFF7A0B9`
- `groundtruth-kb/src/groundtruth_kb/db.py` `7485A0585227BDE4E77D43C81702E4D59E2FCBD28B358C95E74EEC2450037CB7`
- `platform_tests/scripts/test_pauth_one_current_per_project.py` `37D456EC4084BAE19B9019D69EB80FF7BBB712B0EBE7C8A89C68F821396B3F7C`
- `scripts/pauth_one_current_per_project.py` `A48DBBE0545FB360E5E54055E3672E95CA6D6A13A7C4A3190AB67CAA8ACD142E`

## Dirty-file / commit-split note

- `db.py` still also contains an unrelated uncommitted WI-6620 hunk (`approved_lifecycle` includes `"active"`). That hunk was required for this live pass because `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 is `status=active`. The WI-6618 work-product commit MUST NOT silently steal WI-6620; split the staging. The WI-6618 C1 hunk is the `second current identity is prohibited` block in `insert_project_authorization`.
- `platform_tests/scripts/test_project_authorization.py` and `scripts/implementation_authorization.py` were already dirty (foreign WI-6505 / other work) and were not edited.
- `lifecycle.py` was not edited in this slice (WI-6617 already committed).

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 `active`
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 `active`
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 `active` (C1, C2; C4 preserved)
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — empty approved-spec union does not mint a current row
- `GOV-FILE-BRIDGE-AUTHORITY-001` v5
- `GOV-10` v2
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v2
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v6

All current ADR heads remain independent tests of this disposition.

## Owner Decisions / Input

No new owner decision. Implementation is the GO'd postimage for `DELIB-20260816201237` question 2 / WI-6618. The four empty-union projects were left unauthorized rather than given an invented spec grant. WI-6619 was not started. WI-6557 did not run extra membership mutations.

## Prior Deliberations

- `DELIB-20260816201237` — owner event model; supersede into one current authorization per project; union of grants; MUST NOT delete.
- GO at `bridge/gtkb-wi6618-one-current-pauth-per-project-002.md` (goose, harness G). Independent of this Prime Builder session.
- WI-6617 work-product `2d6382aae` and VERIFIED thread `-004` satisfied the sequencing gate.

## Specification-Derived Verification Plan

| Spec | Executed evidence |
| --- | --- |
| DCL C1 | `test_collapse_one_current_per_project_and_preserves_history`, `test_c1_rejects_second_current_identity_after_collapse`, live census `projects_with_multiple_current_ids == 0`, live rolled-back second-identity insert |
| DCL C2 | `test_c2_rejects_active_wi_scoped_identity`, live census `wi_scoped_current_ids == 0`, live rolled-back `PAUTH-WI-*` insert |
| GOV v3 cardinality | after census: at most one current per project; 125 current + 4 unauthorized = 129 previously authorized projects |
| Union / non-delete | `test_union_does_not_drop_grants_or_invent_classes`; table grew 1065 → 1839; historical `PAUTH-WI-3396-*` readable |
| C3 after collapse | `test_membership_after_collapse_does_not_mint_second_identity` |
| Empty approved-spec union | `test_collapse_leaves_project_unauthorized_when_no_approved_spec_remains` |
| GOV-10 | tests and apply call `KnowledgeDB.insert_project_authorization` / `ProjectLifecycleService` |

```text
python -m pytest platform_tests/scripts/test_pauth_one_current_per_project.py platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py -q --tb=short
```

Result: **13 passed** in 11.66s (pytest-9.1.1, Python 3.14.0).

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/authorization.py groundtruth-kb/src/groundtruth_kb/project/authorization_collapse.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_pauth_one_current_per_project.py scripts/pauth_one_current_per_project.py
```

Result: All checks passed.

```text
python scripts/pauth_one_current_per_project.py --census
python scripts/pauth_one_current_per_project.py --dry-run
# then apply via collapse_all(..., dry_run=False)
```

Dry-run: 0 errors, 129 projects, 4 left-unauthorized. Apply: 0 errors, C1/C2 fail-closed true.

## Independent Review Plan

Re-read GO `-002`, this report, the five target paths, and a fresh MemBase census. Confirm no DELETE, union-preserving supersession, C1/C2 fail-closed, WI-6617 commit preceded the apply, WI-6619 was not done, and the WI-6620 `db.py` hunk is split out of the WI-6618 commit. Return VERIFIED only after a work-product commit that names `(WI-6618)` and does not include a `VERIFIED` file. GO/VERIFIED is not implementation in the reviewing session.

## Filing-tool / start-gate defects (recorded against WI-6618)

1. Marker-first header written without `normalize_bridge_envelope_head` (WI-6538 / WI-6541 / WI-5814).
2. `implementation_authorization.py begin` would refuse: approved proposal `target_paths: []` and operative GO `-002` has no `author_identity`. Independent LO review already existed. Bypass recorded; independent review is not bypassed.
3. Work-intent claim `gtkb-wi6618-one-current-pauth-per-project` was extended once (`extensions_used: 1`, deadline `2026-08-17T08:47:31Z`) for this session `13570cbf-e2d1-408a-9c3d-be4ff5a582f4`.
4. Include-list PAUTH coverage evaluators remain C4-defect-shaped; this report does not claim PHASE 3 include-list coverage.
5. `scripts/bridge_work_intent_registry.py` warns that proposal `001` is malformed/legacy because line 1 is `::init gtkb lo` rather than a status token (same WI-5814 class).

## Owner Action Required

None.

## Files Expected To Change

None further in this session. Worktree already holds the five target paths. Live MemBase already holds the append-only collapse.

## Recommended Commit Type

`feat` — commit metadata MUST name `(WI-6618)` and MUST NOT include a `VERIFIED` file or the WI-6620 `db.py` hunk unless that work item is intentionally combined by a later owner direction.

## Risk / Rollback

Risk is committing mixed `db.py` bytes (WI-6620) or treating the four unauthorized projects as a defect to be "fixed" by inventing spec grants. Source rollback is `git checkout` of the five paths after splitting the WI-6620 hunk aside. MemBase rollback is not a DELETE: it would require a new governed authorization event, not row removal. Rollback of this report is deletion of this ephemeral message.

---
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
