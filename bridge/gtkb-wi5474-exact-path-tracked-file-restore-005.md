REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata


bridge_kind: prime_proposal
Document: gtkb-wi5474-exact-path-tracked-file-restore
Version: 005
Responds to: bridge/gtkb-wi5474-exact-path-tracked-file-restore-004.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5474

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "platform_tests/scripts/test_git_lifecycle_exact_restore.py"]

# Revised Implementation Proposal - WI-5474 Exact-Path Restore Fail-Closed Completion

## Revision Claim

Prime Builder proposes one narrow correction to the implementation rejected by
version 004. `normalize_repo_path()` must reject repository-root pseudo-paths
such as `.` and `./.` with stable `OperationDenied("unsafe_scope_path", ...)`
before indexing `Path.parts`. The focused test module must cover those exact
spellings and equivalent root-only forms through the production CLI boundary.

The existing exact-path restore implementation remains quarantined candidate
work until this correction is independently approved, implemented under a new
claim and implementation-start packet, tested, and independently verified. The
other implemented behavior is unchanged.

## Requirement Sufficiency

Existing requirements sufficient.

The approved WI-5474 contract already requires every unsafe request to fail
before mutation with a stable actionable denial code. Version 004 identified a
missing edge case in that existing requirement; no new or revised requirement
is needed before implementation.

## Findings Addressed

### Version 004 F1 - Root pseudo-paths raise IndexError

Accepted. The current function strips leading `./` components, constructs
`Path(raw)`, and indexes `path.parts[0]`. For `.` and `./.`, `Path.parts` is
empty, so the boundary raises `IndexError` instead of the governed denial
required by the proposal.

The correction will add an explicit no-concrete-component condition before the
first index operation. It will not broaden accepted paths, add implicit refs,
change restore semantics, or catch arbitrary programming errors at the CLI.
The test suite will assert the stable denial code and absence of a traceback.

## Scope Changes

- Keep the original four-file target envelope so the eventual focused
  finalization can include the complete WI-5474 implementation and tests.
- Modify only
  `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py` and
  `platform_tests/scripts/test_git_lifecycle_exact_restore.py` for this
  correction.
- Preserve
  `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py` and
  `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py` byte-for-byte.
- Do not execute the restore service against the live GT-KB worktree during
  implementation or verification.
- Do not alter dispatcher configuration/runtime, TAFE state, leases, harness
  roles or eligibility, credentials, MemBase, Git staging/history, push,
  deployment, or release.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5474; TEST-11572; bridge/gtkb-wi5474-exact-path-tracked-file-restore-004.md",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; DCL-GIT-BRANCH-BINDING-PROMOTION-001; GOV-WORK-TREE-HYGIENE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m groundtruth_kb.git_lifecycle --json restore-deleted-path with one repository-relative path and one explicit source ref",
  "before_behavior": "Repository-root pseudo-paths reach an empty Path.parts tuple and crash with IndexError.",
  "after_behavior": "Every root-only or otherwise non-concrete path fails before mutation with stable unsafe_scope_path denial.",
  "self_descriptive_naming": "unsafe_scope_path continues to name the existing fail-closed path boundary without adding a second error vocabulary.",
  "obsolete_guidance_disposition": "No raw Git, broad restore, ad hoc copy, or exception-swallowing fallback is introduced.",
  "history_preservation": "The numbered bridge chain and existing candidate implementation remain append-only; only the normalization guard and focused tests change after GO.",
  "baseline": {
    "approved_proposal": "bridge/gtkb-wi5474-exact-path-tracked-file-restore-001.md",
    "no_go": "bridge/gtkb-wi5474-exact-path-tracked-file-restore-004.md",
    "linked_test": "TEST-11572",
    "declared_targets": 4,
    "correction_targets": 2
  },
  "expected_result": {
    "root_only_input": "Governed unsafe_scope_path denial, no traceback, no mutation.",
    "valid_file_input": "Existing normalization and exact restore behavior remain unchanged.",
    "live_repository": "No restore operation is performed against the live GT-KB checkout during implementation or verification."
  },
  "rollback": {
    "instructions": "Governed revert of only the exact WI-5474 correction hunk after preserving the bridge chain.",
    "verification": "Run the full exact-restore and frozen modernization Git-lifecycle modules."
  },
  "hard_invariants": [
    "Exactly one concrete normalized repository-relative file path.",
    "No indexing of an empty Path.parts tuple.",
    "Unsafe input fails before any filesystem or Git mutation.",
    "The two non-correction implementation targets remain byte-identical.",
    "No dispatcher, TAFE, MemBase, credential, push, deployment, or release mutation."
  ],
  "fail_closed_conditions": [
    "Empty or root-only normalized path.",
    "Absolute, escaping, .git, pathspec-like, or multi-path input.",
    "Unknown or ambiguous source ref.",
    "Any target or unrelated repository state change during validation."
  ],
  "essential_context_preservation": "Preserve the explicit source ref, selected source blob, exact target path, denial code, target state, unrelated status hashes, and operation outcome."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded defect-repair carrier while preserving every later bridge and
  implementation gate.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` keeps
  dispatcher configuration outside this correction.
- `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md` is the verified
  Git-lifecycle baseline extended by WI-5474.
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-004.md` is the
  independent NO-GO this revision addresses in full.

## Owner Decisions / Input

- The active singleton V2 project authorization carries
  `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`.
- Mike's standing cleanup goal requires restoration of missing tracked bridge
  predecessors without reset, clean, stash, or broad unrelated restoration.
- No new owner decision is required. This revision does not authorize a live
  restore operation; it authorizes only the source/test correction after GO,
  exact claim, and implementation-start approval.

## Pre-Filing Preflight Subsection

- Candidate-mode applicability preflight executed against the exact revision
  bytes supplied to the governed filer.
- Applicability result: `preflight_passed=true`,
  `missing_required_specs=[]`, `missing_advisory_specs=[]`,
  `blocking_errors=[]`, and `missing_parent_dirs=[]`.
- Candidate-mode mandatory clause preflight executed against the same exact
  revision bytes.
- Clause result: 5 evaluated, 4 `must_apply`, 1 `may_apply`, 0 evidence
  gaps, and 0 blocking gaps; mandatory mode exited 0.

## Specification-Derived Verification Plan

| Specification | Required executed verification |
| --- | --- |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001`; `GOV-WORK-TREE-HYGIENE-001`; TEST-11572 | Add `.` and `./.` plus equivalent root-only spellings to the production CLI denial matrix; assert exit is governed, JSON code is `unsafe_scope_path`, no traceback is emitted, and no repository path changes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; PAUTH constraints | Verify latest GO, exact claim, schema-v3 implementation-start packet, and operation-time authorization for all four declared targets before editing. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the full exact-restore module and frozen modernization Git-lifecycle module, then carry exact results into the implementation report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live applicability and mandatory clause preflights with no missing specs or blocking errors. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Keep every test repository under an in-root temporary directory and prove cleanup; never invoke restore against the live checkout. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Preserve WI-5474, TEST-11572, PAUTH, proposal, GO, report, and verdict linkage through terminal independent verification. |

Required commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
```

## Acceptance Criteria

- `.` and `./.` return governed `unsafe_scope_path` denial through the
  production CLI, with no traceback and no mutation.
- Equivalent root-only spellings cannot reach `path.parts[0]`.
- Every previously passing exact-restore case remains green.
- The change is limited to the explicit normalization guard and focused tests.
- The two preserved implementation targets remain byte-identical.
- No live GT-KB restore or unrelated repository, dispatcher, runtime, MemBase,
  harness, credential, push, deployment, or release operation occurs.

## Risk And Rollback

The correction is intentionally fail-closed: it can only reject inputs that do
not identify a concrete repository-relative file. The principal regression
risk is accidentally rejecting a valid dotted filename, so the existing valid
path cases remain mandatory and a normal path such as
`bridge/example-001.md` must continue to normalize unchanged.

Rollback is a separately governed revert of only the exact WI-5474 correction
hunk after preserving the numbered bridge chain. No rollback may remove the
existing exact-restore implementation, rewrite history, or affect unrelated
worktree bytes.

## Recommended Commit Type

`fix:`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
