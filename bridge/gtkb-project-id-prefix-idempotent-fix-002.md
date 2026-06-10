REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 00d6b362-374c-4c5c-bf69-b7c23d0f2f58
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3411

# Idempotent Project-ID Prefix Fix - `_project_id_from_names` Doubled-Prefix Defect (REVISED-1)

bridge_kind: prime_proposal

Document: gtkb-project-id-prefix-idempotent-fix
Version: 002 (REVISED-1; self-corrected before review)
Date: 2026-05-29 UTC

## Revision Note (002)

REVISED-1 self-corrects a clause-preflight blocking gap detected on `-001` before any verdict: the mandatory clause preflight returned exit 5 on `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` because `-001` used the word "bulk" repeatedly (only to DISCLAIM bulk scope) without any of the detector's required evidence tokens. This is the known false-positive pattern. REVISED-1 adds an explicit `DECISION DEFERRED` marker and inventory/review-packet language to the Clause Scope Clarification so the gate recognizes the deferral. No scope, design, or target_paths change from `-001`.

## Summary

Fixes the doubled-prefix defect that mis-files work-item project memberships under phantom `PROJECT-PROJECT-*` projects. Root cause is a single function, `_project_id_from_names` in `groundtruth-kb/src/groundtruth_kb/db.py` (line 910): it unconditionally prepends `PROJECT-` to the slug of `project_name`. When a caller passes an already-qualified project id as `project_name`, the prefix doubles.

Reliability-fast-lane fix per the standing `PROJECT-GTKB-RELIABILITY-FIXES` convention: one function made idempotent, one focused regression test. The existing phantom projects + mis-filed memberships are a separate reconciliation concern, explicitly deferred (see Clause Scope Clarification).

## Live Evidence (reproduced this session)

```text
_stable_slug('GTKB-RELIABILITY-FIXES')              = 'GTKB-RELIABILITY-FIXES'
_project_id_from_names('GTKB-RELIABILITY-FIXES')    = 'PROJECT-GTKB-RELIABILITY-FIXES'   # correct
_stable_slug('PROJECT-GTKB-RELIABILITY-FIXES')      = 'PROJECT-GTKB-RELIABILITY-FIXES'
_project_id_from_names('PROJECT-GTKB-RELIABILITY-FIXES') = 'PROJECT-PROJECT-GTKB-RELIABILITY-FIXES'   # DEFECT
```

WI-3411 is itself a victim: it carries TWO active memberships in the live DB - the bogus `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` (source `work_items.project_name`, auto-created by the backfill) and the canonical `PROJECT-GTKB-RELIABILITY-FIXES` (source `gt projects add-item`, the manual workaround documented in `memory/feedback_backlog_add_doubled_prefix_membership_bug.md`).

The CLI (`cli_backlog_add.py`) does NOT separately prefix; it passes `project_name` straight to `insert_work_item` (line 198), which calls the backfill, which calls `_project_id_from_names`. Single root cause - both WI-3411 (CLI symptom) and WI-3355 (db.py root-cause diagnosis) trace here.

## Callers Verified (idempotent fix is safe for all)

```text
db.py:1055  _backfill_project_artifacts_from_work_items   project_id  = _project_id_from_names(project_name)
db.py:1090  _backfill_project_artifacts_from_work_items   subproject_id = _project_id_from_names(project_name, subproject_name)
db.py:3794  (project create path)                         project_id  = id or _project_id_from_names(name)
```

All three derive an id from a name. Idempotent normalization changes behavior only for already-`PROJECT-`-qualified inputs (which today produce the doubled-prefix bug); bare names are unchanged.

## Proposed Fix

`_project_id_from_names` becomes idempotent w.r.t. the `PROJECT-` prefix:

```python
def _project_id_from_names(project_name: str, subproject_name: str | None = None) -> str:
    slug = _stable_slug(project_name)
    # Idempotent prefix: a caller may pass either a bare project name
    # ("GTKB-RELIABILITY-FIXES") or an already-qualified project id
    # ("PROJECT-GTKB-RELIABILITY-FIXES"). Only prepend "PROJECT-" when the
    # slug does not already carry it, so an already-qualified id is not
    # doubled into "PROJECT-PROJECT-*".
    base = slug if slug.startswith("PROJECT-") else f"PROJECT-{slug}"
    if subproject_name and subproject_name.strip():
        return f"{base}-{_stable_slug(subproject_name)}"
    return base
```

Design choice: WI-3355 lists three options - reject already-prefixed input, normalize it, or accept an explicit project id. Normalization is chosen because (a) reject would break the already-in-use prefixed-input calling convention; (b) the explicit-id path already exists at the project-create layer (line 3794 `id or ...`) but the backfill path cannot supply it; (c) normalization is backward-compatible with both bare-name and qualified-id callers and is the minimal-risk repair. The guard keys on the literal `"PROJECT-"` prefix (with hyphen), so a degenerate project literally named "project" still maps to `PROJECT-PROJECT` - that is not the defect and is left unchanged.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is canonical workflow state. This REVISED version is filed at -002, inserted at top of the existing INDEX entry, append-only (the -001 NEW version is preserved).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section satisfies the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate. WI-3411 has an active canonical membership in PROJECT-GTKB-RELIABILITY-FIXES.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps the fix behavior to executable tests.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 - covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (active; the standing reliability vehicle; WI-3411 is a member of PROJECT-GTKB-RELIABILITY-FIXES). After GO, Prime runs `python scripts/implementation_authorization.py begin --bridge-id gtkb-project-id-prefix-idempotent-fix` before the source edit.
- GOV-STANDING-BACKLOG-001 - cited because the proposal references work items and backlog membership. NOT a bulk operation; see Clause Scope Clarification.
- GOV-ARTIFACT-APPROVAL-001 - this fix creates no canonical artifact (no MemBase spec/GOV/ADR/DCL/PB row, no protected narrative file). Out of scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - cited because the proposal references owner decisions, requirements, work items, and backlog.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - cited because the fix touches MemBase membership artifacts and preserves traceability; it changes one derivation function and adds a test.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - cited because the deferred follow-on references retiring phantom projects; this proposal transitions no lifecycle state.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal changes ONE derivation function and adds ONE regression test. It performs no work_items insert/update/retire, no project create/retire, no membership row insert/delete, no authorization change, and no inventory mutation of existing rows.

DECISION DEFERRED: the phantom-membership reconciliation - the only bulk-scope action in this defect's vicinity - is deferred to a separate follow-on proposal (captured in WI-3355). When that follow-on is filed, it will carry its own inventory artifact and review packet enumerating every phantom `PROJECT-PROJECT-*` project and mis-filed membership to be reconciled, plus the deferred-decision marker for owner sequencing. This code fix produces no such inventory and reconciles no existing row; it only stops new drift at the source. Evidence tokens for the non-bulk classification of THIS proposal: single derivation function, one regression test, no existing-row mutation, deferred bulk reconciliation.

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. The doubled-prefix behavior is an unambiguous defect (it silently mis-files memberships and produces wi-not-found-in-project compliance-gate blocks); the fix restores the obviously-intended idempotent derivation. No requirement specifies that an already-qualified project id should be re-qualified.

## target_paths

- `groundtruth-kb/src/groundtruth_kb/db.py` (the single-function fix to `_project_id_from_names`)
- `platform_tests/scripts/test_project_id_from_names_idempotent.py` (new regression test)

No other path is authorized. No CLI change (the CLI does not prefix). No schema migration. No membership reconciliation. No bridge/INDEX.md mutation by the implementation itself.

### KB-Mutation Statement (target_paths completeness checkpoint)

This proposal performs NO canonical KB/MemBase mutation, so `groundtruth.db` is intentionally absent from target_paths. The fix edits a pure Python derivation function in `db.py` source. The regression test exercises `insert_work_item` against an isolated temporary database created by the test fixture (never the canonical `groundtruth.db`). No row in the canonical store is inserted, updated, retired, or deleted by this change. The phantom-membership reconciliation that WOULD mutate canonical rows is the deferred follow-on, explicitly out of scope here.

## Spec-Derived Verification Plan

Per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, the new test file asserts:

| # | Behavior | Test |
|---|---|---|
| 1 | Bare name unchanged: `_project_id_from_names("GTKB-X")` == `"PROJECT-GTKB-X"` | `test_bare_name_prefixed` |
| 2 | Already-qualified NOT doubled: `_project_id_from_names("PROJECT-GTKB-X")` == `"PROJECT-GTKB-X"` | `test_qualified_id_not_doubled` |
| 3 | Subproject, bare project: `(...,"SUB")` == `"PROJECT-GTKB-X-SUB"` | `test_subproject_bare` |
| 4 | Subproject, qualified project: `("PROJECT-GTKB-X","SUB")` == `"PROJECT-GTKB-X-SUB"` | `test_subproject_qualified_not_doubled` |
| 5 | Idempotence: `f(f(x)) == f(x)` for representative inputs | `test_idempotent` |
| 6 | Integration: `insert_work_item(project_name="PROJECT-GTKB-X")` files membership under `PROJECT-GTKB-X`, not `PROJECT-PROJECT-GTKB-X` | `test_insert_work_item_no_doubled_membership` |

Execution commands (at implementation report time):

```text
python -m pytest platform_tests/scripts/test_project_id_from_names_idempotent.py -q
```

## Recommended Commit Type

`fix:` - repairs broken behavior (silent membership mis-filing) with no new capability surface. Diff is one function body + one new test file.

## Prior Deliberations

- WI-3355 - the root-cause diagnosis work item (orphan; documents the db.py defect site and the three fix options, with normalization as primary). Its phantom-cleanup follow-up remains the deferred reconciliation item.
- WI-3411 - the CLI-symptom work item (member of PROJECT-GTKB-RELIABILITY-FIXES); records the `gt projects add-item` workaround and 2026-05-27 instances.
- `memory/feedback_backlog_add_doubled_prefix_membership_bug.md` - the operational note flagging this as an upstream-fix candidate (3+ observed instances in S363 alone).
- `memory/feedback_layer0_layer1_audit_parser_cross_layer.md` - the cross-layer discipline applied here: confirmed the CLI does not separately prefix, so the fix is a single Layer-0 root-cause repair, not a per-layer patch.
- `memory/feedback_bulk_ops_clause_false_positive_s342.md` - the known false-positive that this REVISED-1 addresses with the DECISION DEFERRED marker.
- S356 (2026-05-16): a prior work item reproduced the defect and produced Codex NO-GO F1 on `gtkb-governance-hook-worktree-root-resolution-002.md`; the S356 repair used the `link_project_work_item` workaround.

## Owner Decisions / Input

This proposal proceeds on owner AskUserQuestion approvals captured this session (conversation `00d6b362-374c-4c5c-bf69-b7c23d0f2f58`):

1. DECISION-0758 (resolved this session): "start the triage".
2. Triage scope choice (AUQ): "Implementation gaps (Recommended)".
3. Next-step choice (AUQ): "Pick up Gap 2 (doubled-prefix fix)" - owner selected via AskUserQuestion; durable evidence is the AUQ tool record. Authorizes this fix filing.

Reliability fast-lane: per the standing PROJECT-GTKB-RELIABILITY-FIXES authorization convention, this small defect fix does not require a per-fix deliberation or focused PAUTH; it attaches to `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` via WI-3411's project membership. No new owner decision is required to review this proposal.

## Risk and Rollback

- Risk: a caller relies on the doubled-prefix behavior. Mitigation: verified all three callers derive an id from a name and none expect doubling; the doubled output is the defect, not a contract.
- Risk: changing id derivation orphans future lookups. Mitigation: the fix makes derivation MATCH the canonical id that `gt projects add-item` already produces, so it converges callers onto the real project id rather than diverging.
- Risk: scope creep into phantom reconciliation. Mitigation: target_paths is two files; the impl-start packet fails closed outside it; reconciliation is explicitly deferred.
- Rollback: revert the two-file commit; derivation returns to prior behavior. No existing rows are mutated by this fix, so there is no data migration to unwind.

## Codex Review Asks

1. Confirm idempotent normalization (vs reject / explicit-id) is the right minimal fix.
2. Confirm the two-file target_paths is complete.
3. Confirm deferring the phantom reconciliation to a separate proposal is the correct scope boundary.
4. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
