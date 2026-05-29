NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-2026-05-29-project-id-prefix-idempotent-fix-post-impl
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code session environment

# Post-Implementation Report - Idempotent Project-ID Prefix Fix (WI-3411)

bridge_kind: implementation_report
Document: gtkb-project-id-prefix-idempotent-fix
Version: 004 (NEW; post-implementation report following Codex GO at -003)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Responds to GO: bridge/gtkb-project-id-prefix-idempotent-fix-003.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3411
Implementation-Start Packet Hash: sha256:6ca40b424a4af41d6353195d3771e7beb6f82336274f44ebbd7c81480559a3a6
GO File: bridge/gtkb-project-id-prefix-idempotent-fix-003.md

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "platform_tests/scripts/test_project_id_from_names_idempotent.py"]

Recommended commit type: fix:

## Summary

The idempotent project-id prefix fix is implemented and verified. `_project_id_from_names` in `groundtruth-kb/src/groundtruth_kb/db.py` is now idempotent with respect to the `PROJECT-` prefix: bare names are still prefixed (`"GTKB-X"` -> `"PROJECT-GTKB-X"`); already-qualified ids pass through unchanged (`"PROJECT-GTKB-X"` -> `"PROJECT-GTKB-X"`). The new regression test file at `platform_tests/scripts/test_project_id_from_names_idempotent.py` contains 6 tests (T1-T6) that exhaustively cover the proposal's verification matrix. All 6 tests PASS.

Scope discipline preserved: this fix touches one derivation function plus one new test file. The existing phantom `PROJECT-PROJECT-*` projects and their mis-filed membership rows are NOT reconciled by this implementation; that reconciliation is the deferred follow-on tracked under WI-3355.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this report follows the post-implementation -> VERIFIED workflow; bridge/INDEX.md updated with new top entry for this report.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section + the Spec-to-Test Mapping below provide spec linkage carried forward into post-implementation evidence.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the Spec-to-Test Mapping maps every carried-forward spec to executed test commands + observed results.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project/WI/PAUTH header lines present; WI-3411 active in PROJECT-GTKB-RELIABILITY-FIXES.
- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING - covers this work item by active project membership; impl-start packet hash above ties this report to a live latest-GO authorization.
- GOV-STANDING-BACKLOG-001 - cited because the proposal references work items and backlog membership. NOT a bulk operation: one derivation function + one regression test; no work_items/projects/memberships mutation of existing rows. The deferred phantom-membership reconciliation remains tracked under WI-3355 with its own scope packet.
- GOV-ARTIFACT-APPROVAL-001 - this fix creates no canonical artifact (no MemBase spec/GOV/ADR/DCL/PB row, no protected narrative file). Out of scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - cited because the proposal references owner decisions, requirements, work items, and backlog.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - fix delivered as durable source change + regression test; preserves traceability.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - touching db.py triggered matching test artifact addition.

## Implementation Evidence

### IP-1 - db.py change

`_project_id_from_names` body (groundtruth-kb/src/groundtruth_kb/db.py, function at module-level) was replaced exactly as the proposal specified. Before:

```python
def _project_id_from_names(project_name: str, subproject_name: str | None = None) -> str:
    base = f"PROJECT-{_stable_slug(project_name)}"
    if subproject_name and subproject_name.strip():
        return f"{base}-{_stable_slug(subproject_name)}"
    return base
```

After:

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

The change is body-only; signature, return type, and module-level placement are unchanged. The three call sites at `db.py:1055`, `db.py:1090`, and `db.py:3794` (per the proposal's caller inventory) are unaffected by the signature; they continue to derive a project id from a name. The idempotent guard keys on the literal `"PROJECT-"` slug prefix; bare-name behavior is preserved for every input that does not already start with that prefix.

### IP-2 - new test file

Created `platform_tests/scripts/test_project_id_from_names_idempotent.py` (108 lines). The file mirrors the existing `test_cli_backlog_add.py` import pattern (REPO_ROOT path bootstrapping, no-conftest dependency) and contains 6 tests matching the GO'd proposal's verification matrix exactly. Tests T1-T5 are unit-level against `_project_id_from_names`. Test T6 is the integration test: it inserts a work item with `project_name="PROJECT-GTKB-RELIABILITY-FIXES"` against a temp database, runs `_backfill_project_artifacts_from_work_items()` explicitly to reproduce the original defect manifest path (the same path that produced the WI-3411 and WI-3447 doubled-prefix memberships in the canonical store), and asserts the resulting membership row uses `PROJECT-GTKB-RELIABILITY-FIXES`, NOT `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES`.

### Test execution evidence

```text
$ python -m pytest platform_tests/scripts/test_project_id_from_names_idempotent.py -q
......                                                                   [100%]
6 passed in 0.43s
```

All 6 tests PASS. No regressions.

## Specification-Derived Verification (executed)

Per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, the proposal's 6-test matrix maps directly to executable evidence:

| # | Behavior | Test | Result |
|---|---|---|---|
| 1 | Bare name unchanged: `_project_id_from_names("GTKB-X")` == `"PROJECT-GTKB-X"` | `test_bare_name_prefixed` | PASS |
| 2 | Already-qualified NOT doubled: `_project_id_from_names("PROJECT-GTKB-X")` == `"PROJECT-GTKB-X"` | `test_qualified_id_not_doubled` | PASS |
| 3 | Subproject, bare project: `(...,"SUB")` == `"PROJECT-GTKB-X-SUB"` | `test_subproject_bare` | PASS |
| 4 | Subproject, qualified project: `("PROJECT-GTKB-X","SUB")` == `"PROJECT-GTKB-X-SUB"` | `test_subproject_qualified_not_doubled` | PASS |
| 5 | Idempotence: `f(f(x)) == f(x)` for representative inputs | `test_idempotent` | PASS |
| 6 | Integration: `insert_work_item(project_name="PROJECT-GTKB-X")` followed by backfill files membership under `PROJECT-GTKB-X`, not `PROJECT-PROJECT-GTKB-X` | `test_insert_work_item_no_doubled_membership` | PASS |

Verification command executed (per GO Implementation Constraint 3):

```text
python -m pytest platform_tests/scripts/test_project_id_from_names_idempotent.py -q
```

Observed result: `6 passed in 0.43s`.

## Acceptance Criteria Satisfaction

- [x] IP-1 landed; `_project_id_from_names` is idempotent per the proposal's exact code block.
- [x] IP-2 landed; 6 new tests PASS.
- [x] GO Implementation Constraint 1 satisfied: implementation-start packet was created via `python scripts/implementation_authorization.py begin --bridge-id gtkb-project-id-prefix-idempotent-fix` before any source edit (packet hash recorded in header).
- [x] GO Implementation Constraint 2 satisfied: edits stayed within the approved `target_paths` (db.py + new test file only).
- [x] GO Implementation Constraint 3 satisfied: exact regression command + observed result included in this report.
- [x] GO Implementation Constraint 4 satisfied: NO existing `PROJECT-PROJECT-*` rows were reconciled by this implementation. The phantom reconciliation remains deferred to WI-3355's follow-on proposal.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/db.py` (modified; one function body, ~6 lines net change at the `_project_id_from_names` definition site).
- `platform_tests/scripts/test_project_id_from_names_idempotent.py` (new file; 108 lines).

Mixed-owner working-tree note: db.py also carries unrelated edits from parallel-session work (KPI views, schema column additions). The commit for this implementation will stage ONLY the idempotent-fix hunk in db.py plus the new test file; parallel-session changes remain in the working tree for their owning thread(s) to commit separately. Inspect-staged-index discipline (`git diff --cached --name-only` plus `--stat` blob inspection) applies at commit time.

## Owner Decisions / Input

This implementation proceeded on the durable owner-decision evidence cited in the GO'd proposal (-002):

- DECISION-0758 (this session): "start the triage" - AskUserQuestion approval recorded.
- Triage scope choice (AUQ): "Implementation gaps (Recommended)" - AskUserQuestion approval.
- Next-step choice (AUQ): "Pick up Gap 2 (doubled-prefix fix)" - AskUserQuestion approval; durable evidence is the AUQ tool record.
- Standing pre-approval: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3411 by active project membership.

No new blocking owner decision was required for this verification round. The work item appears on the active session's owner-approved implementation list per the prompt directive that opened this session.

## Risk / Open Items

- Behavior change for already-qualified-id callers: the only such callers are the three derivation sites the proposal inventoried, all of which derive an id from a name and none of which expect doubling. The doubled output was the defect, not a contract.
- The phantom `PROJECT-PROJECT-*` projects and mis-filed membership rows that already exist in the canonical store are NOT cleaned up by this fix; the source has stopped producing them, but the historical drift remains. WI-3355 carries the deferred reconciliation scope.
- Mixed-owner working tree (~668 dirty files at implementation time): inspect-staged-index discipline applies at commit time.

## Prior Deliberations

- WI-3355 - the root-cause diagnosis work item (orphan; documents the db.py defect site and the three fix options, with normalization as primary). Phantom-cleanup follow-up remains deferred.
- WI-3411 - the CLI-symptom work item (active member of PROJECT-GTKB-RELIABILITY-FIXES); records the `gt projects add-item` workaround.
- WI-3447 - the freshly-captured S369+ instance of the same defect (filed earlier this session under the reliability fast-lane); also doubled-prefix mis-filed; re-linked via add-item; demonstrates the defect's continuing manifestation pre-fix.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - owner-decision source for the standing PAUTH covering this work.
- bridge/gtkb-project-id-prefix-idempotent-fix-001.md (NEW), -002.md (REVISED-1), -003.md (Codex GO) - the proposal thread this report responds to.

## Loyal Opposition Asks

1. Confirm the implementation matches the proposal's exact code block (no design drift, no unspecified narrowing per the operating-model anti-pattern).
2. Confirm the 6 tests adequately cover the spec-derived verification matrix.
3. Confirm the integration-test pattern (explicit `_backfill_project_artifacts_from_work_items()` call) faithfully reproduces the defect's original manifest path.
4. Confirm VERIFIED is appropriate based on the above evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
