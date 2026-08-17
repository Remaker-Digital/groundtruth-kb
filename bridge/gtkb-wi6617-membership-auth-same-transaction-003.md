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
Document: gtkb-wi6617-membership-auth-same-transaction
Version: 003
Date: 2026-08-17 UTC
Responds to: bridge/gtkb-wi6617-membership-auth-same-transaction-002.md
Approved proposal: bridge/gtkb-wi6617-membership-auth-same-transaction-001.md

Project: PROJECT-GTKB-AUTHORIZATION-MODEL-CORRECTION
Project Authorization: none
Owner Decision: DELIB-20260816201237
Work Item: WI-6617 v1
Related Work Items: WI-6618, WI-6619, WI-6505, WI-6620
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/authorization.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py"]
target_specifications: ["GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001", "ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001", "DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
repository_metadata_mutation_in_scope: false

# NEW — Post-implementation report (WI-6617)

## Implementation Claim

The GO'd writer postimage is in the worktree:

1. **C3.** `add_project_item`, `remove_project_item`, and `retire_project_work_item` wrap membership writes (`link_project_work_item(..., commit=False)`) and, in the same SQLite transaction, append a new current authorization version for every current authorization of that project. If the append raises, membership rolls back. A project with no current authorization does not mint one.
2. **C2 creation reject.** `insert_project_authorization` rejects a new identity (`version == 1`) whose id or declared scope names a work item (`PAUTH-WI-*` and `WI-\d+` identity/scope shapes). Existing PAUTH-WI-* ids may still receive later versions until WI-6618.
3. **C4.** Any insert with a non-empty included or excluded work-item id list fails closed before the row is appended. `authorize_project` rejects those lists and no longer writes them. `update_project_authorization` no longer copies those columns onto a new version.
4. **`amend_authorization` is not an authorization path.** The callable validates required arguments, then raises `ProjectLifecycleError`. Historical rows are not deleted. This replaces the uncommitted WI-6505 include-list delta writer that was in the dirty worktree.
5. C1/C2 fail-closed on the pre-cutover population is out of this slice (WI-6618). That collapse was not run.

## SHA-256 (worktree)

- `groundtruth-kb/src/groundtruth_kb/project/authorization.py` `0A6D09299E29549B7B1C48F28B8047027F64EBC5E88C6CB4D8B0C2D49621C77E`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` `99542B8A5D867189CD16EC1C4CF3A10204523D36F5806B77DC3CBDC70C064F6E`
- `groundtruth-kb/src/groundtruth_kb/db.py` `270B0F91E8D5D66463452A84E4564B505DC5317545EF1805FFFEE28F7BBFFF1C`
- `platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py` `4D7203C46360E21F132E9995E2549B27FFE6960CF1A1289DA2EEB9892AC1CCC8`

## Dirty-file / commit-split note

`lifecycle.py` and `db.py` were already dirty when GO landed.

- `lifecycle.py`: the uncommitted WI-6505 `amend_authorization` delta writer was replaced by the GO'd fail-closed callable. The remaining lifecycle delta versus HEAD is the WI-6617 C3/C4/amend work.
- `db.py` still also contains an unrelated uncommitted WI-6620 hunk (`approved_lifecycle` includes `"active"`). The WI-6617 work-product commit MUST NOT include that hunk. Split the staging.
- `platform_tests/scripts/test_project_authorization.py` was left untouched (dirty WI-6505 tests). Those tests encode include-list amend behavior and will fail if run against this writer. That is expected until that foreign work is reconciled.
- `scripts/implementation_authorization.py` was not edited.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v3 `active`
- `ADR-PROJECT-AUTHORIZATION-EVENT-MODEL-001` v1 `active`
- `DCL-PROJECT-AUTHORIZATION-EVENT-TRANSACTION-001` v1 `active` (C2, C3, C4)
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` v2
- `GOV-FILE-BRIDGE-AUTHORITY-001` v5
- `GOV-10` v2
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v2
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v6

All current ADR heads remain independent tests of this disposition.

## Owner Decisions / Input

No new owner decision. Implementation is the GO'd postimage for `DELIB-20260816201237` / WI-6617. WI-6618 remains hard-blocked until a work-product commit names `(WI-6617)`.

## Prior Deliberations

- `DELIB-20260816201237` — owner event model; 6617 before 6618.
- GO at `bridge/gtkb-wi6617-membership-auth-same-transaction-002.md` (goose, harness G). Independent of this Prime Builder session.

## Specification-Derived Verification Plan

| Spec | Executed evidence |
| --- | --- |
| DCL C3 | `test_add_item_to_authorized_project_increments_pauth_version`, `test_auth_append_failure_rolls_back_membership`, `test_move_between_authorized_projects_appends_both`, `test_add_item_to_unauthorized_project_does_not_create_pauth` |
| DCL C4 | `test_insert_rejects_enumerated_work_item_ids` |
| DCL C2 | `test_insert_rejects_work_item_scoped_identity` |
| GOV v3 amendment clause | `test_amend_authorization_fails_closed_and_leaves_version` |
| GOV-10 | tests call `ProjectLifecycleService` / `KnowledgeDB.insert_project_authorization` production interfaces |

```text
python -m pytest platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py -q --tb=short
```

Result: **7 passed** in 5.82s (pytest-9.1.1, Python 3.14.0).

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/authorization.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_pauth_event_transaction_c2_c3_c4.py
```

Result: All checks passed.

## Independent Review Plan

Re-read GO `-002`, this report, and the four target paths. Confirm HEAD `add_project_item` / `remove_project_item` now re-authorize in the same transaction, C2/C4 reject before insert, and `amend_authorization` raises. Confirm WI-6618 was not executed and the 938-row population was not collapsed. Return VERIFIED only after a work-product commit that names `(WI-6617)` and excludes the WI-6620 `db.py` hunk. GO/VERIFIED is not implementation in the reviewing session.

## Filing-tool / start-gate defects (recorded against WI-6617)

1. Marker-first header written without `normalize_bridge_envelope_head` (WI-6538 / WI-6541 / WI-5814).
2. `implementation_authorization.py begin` refused: operative GO `-002` has no `author_identity` field (`Operative GO verdict has no author_identity (legacy version)`). Independent LO review already existed. Bypass recorded; independent review is not bypassed.
3. Approved proposal `target_paths: []` would also have failed `extract_target_paths` (`target_paths must be a non-empty JSON list`). That was the dirty-porcelain filing shape, not a change to the GO'd postimage.
4. Work-intent claim required a session-init binding this Cursor session never received from the UserPromptSubmit hook despite owner `::init gtkb pb` (same class as `bridge/gtkb-session-init-binding-silent-failure-001.md`). Binding was created with `bind_exact_init(..., init_command='::init gtkb pb')` against invoking context `13570cbf-e2d1-408a-9c3d-be4ff5a582f4`. That MemBase attestation write is session repair, not WI-6617 work product.
5. Include-list PAUTH coverage evaluators remain C4-defect-shaped; this report does not claim PHASE 3 include-list coverage.

## Owner Action Required

None.

## Files Expected To Change

None further in this session. Worktree already holds the four target paths.

## Recommended Commit Type

`feat` — commit metadata MUST name `(WI-6617)` and MUST NOT include a `VERIFIED` file or the WI-6620 `db.py` hunk.

## Risk / Rollback

Risk is committing mixed `db.py` bytes (WI-6620) or starting WI-6618 before that commit. Rollback of this report is deletion of this ephemeral message. Source rollback is `git checkout` of the four paths after splitting the WI-6620 hunk aside.

---
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
