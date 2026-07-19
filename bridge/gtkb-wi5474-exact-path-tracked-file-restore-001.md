NEW
::init gtkb lo
::open build

# WI-5474 Governed Exact-Path Tracked-File Restore

bridge_kind: prime_proposal
Document: gtkb-wi5474-exact-path-tracked-file-restore
Version: 001
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5474-BRIDGE-PREDECESSOR-RESTORE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5474
Related Work Items: WI-5421, WI-5362
Related Test Artifacts: TEST-11572

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "platform_tests/scripts/test_git_lifecycle_exact_restore.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add one exact-path `restore-deleted-path` operation to the adopted
`groundtruth_kb.git_lifecycle` package. The operation restores the worktree
bytes for exactly one tracked repository-relative path from one explicitly
resolved committed source ref, but only when that path is an unstaged
deletion and every fail-closed precondition passes.

The operation must preserve the index and all unrelated staged, modified,
deleted, and untracked paths. It emits the selected source commit and blob,
the restored worktree blob, and matching before/after hashes of unrelated Git
status evidence.

This proposal adds the capability and verifies it only in isolated temporary
repositories. It does not authorize running the new operation against the
live GT-KB worktree or any bridge predecessor.

## Claim

The production Git-lifecycle package has no exact-path tracked-file restore
surface. When an append-only numbered bridge predecessor is deleted from a
shared worktree, a worker can diagnose the deletion but cannot restore the
committed bytes through the governed package without resorting to raw Git,
whole-tree restoration, or an ad hoc file copy.

WI-5362 exposed the gap when its committed version-002 predecessor was absent.
That immediate predecessor was later restored and WI-5362 advanced to a
revised implementation report, but the reusable governed capability remains
absent. WI-5474 closes that durable gap without reopening or absorbing the
WI-5362 implementation.

## Defect Reproduction

Current package behavior is deterministic:

- `groundtruth_kb.git_lifecycle.__main__` provides branch creation, attachment,
  validation, scoped preservation, promotion, close, resume, recovery, and
  dispatcher-drain commands, but no exact-file restore command.
- `GitRepository` can read status and execute constrained Git commands, but it
  has no source-blob lookup or worktree-only exact-path restore primitive.
- `GitLifecycleService` therefore cannot validate one deletion, bind it to an
  explicit committed blob, preserve unrelated status, restore it, and verify
  the result as one operation.

The unsafe alternatives are intentionally excluded:

- broad `git restore`, `git checkout`, or reset operations;
- enumerating or restoring multiple paths;
- writing bytes through an ad hoc copy path;
- changing the index while restoring the worktree;
- accepting modified, staged, renamed, untracked, or ambiguous input;
- using an implicit or unresolved source ref.

## Current Preconditions

- WI-5421 is independently `VERIFIED` at
  `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md`.
- Its adopted package targets are tracked and clean.
- The three existing WI-5474 source targets have current SHA-256 values:
  - `__main__.py`:
    `ab9a09206280d0931ac1a3ce3f2c1ff9b4a000938be6c8762293a2db7a1d4521`
  - `repository.py`:
    `baea9c96fd6bbf8f63ae990dacbcb32b64a2fe588dc47d897943a6183114fedb`
  - `service.py`:
    `b2ebf9db4f3c8d188ef8b7036569e0121a40f1127e88a8bd97ddf79c934a2d2c`
- `platform_tests/scripts/test_git_lifecycle_exact_restore.py` does not yet
  exist.
- The active V2 PAUTH uses only registered forbidden-operation tokens. Its
  V1 predecessor was revoked before proposal filing because V1 carried
  noncanonical operation names.

## Hard Implementation-Start Gates

Even after independent GO, Prime Builder must not edit any target until:

1. The V2 PAUTH remains active and is selected for WI-5474.
2. This thread remains latest `GO`.
3. All three existing source targets remain clean at the recorded baseline or
   a freshly reviewed clean baseline.
4. The proposed test target remains absent or clean and unowned.
5. An exact `go_implementation` claim and schema-v3 implementation-start
   packet authorize all four paths.
6. Operation-time validation returns authorized for each path immediately
   before mutation.

Any target drift, foreign ownership, unexpected predecessor state, or PAUTH
selection mismatch requires renewed review. No foreign-hunk adoption is
authorized.

## Proposed Scope

- Add a `restore-deleted-path` CLI command with exactly:
  - one `--path` argument;
  - one required `--source-ref` argument;
  - the existing global `--json` output behavior.
- Normalize `--path` through the existing exact repository-relative path
  validator. Pathspecs, absolute paths, `..`, `.git`, wildcard-like syntax,
  and multi-path input remain impossible.
- Resolve `--source-ref` to one unambiguous commit before mutation.
- Require the path to be tracked and to exist as a blob in the selected
  source commit.
- Require the current path state to be exactly one unstaged worktree deletion
  with no staged change. Reject staged deletion, modification, rename,
  untracked state, clean state, conflict state, or multiple status records.
- Capture the complete status surface before mutation and derive a stable
  hash for all records unrelated to the exact target.
- Restore only the worktree copy from the selected commit. Do not update,
  reset, stage, or otherwise mutate the index.
- Re-read the restored worktree blob and require exact equality with the
  selected committed source blob.
- Recompute unrelated status evidence and require exact before/after equality.
  Any mismatch returns a hard failure with the observed evidence.
- Return a structured result containing the normalized path, source ref,
  resolved source commit, source blob, restored blob, target status before and
  after, and unrelated-status hashes before and after.
- Add focused integration tests in isolated temporary Git repositories.
- Preserve every existing Git-lifecycle command and all WI-5421 behavior.
- Do not execute the operation against the live GT-KB worktree.
- Do not mutate bridge files, Git index/history, dispatcher/TAFE
  configuration, runtime state, MemBase, credentials, external systems,
  deployment, or release state during implementation or verification.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-FILE-BRIDGE-AUTHORITY-001` requires the numbered bridge chain to remain
append-only and canonical. `DCL-GIT-BRANCH-BINDING-PROMOTION-001` establishes
the governed Git-lifecycle package as the production boundary for constrained
Git effects. `GOV-WORK-TREE-HYGIENE-001` and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` require exact scope and preservation
of unrelated state. WI-5474 and TEST-11572 define the missing operation and its
verification contract. No new owner choice or formal requirement is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5474; TEST-11572; WI-5362 finalization diagnosis; WI-5421 adopted package",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; DCL-GIT-BRANCH-BINDING-PROMOTION-001; GOV-WORK-TREE-HYGIENE-001",
  "primary_route": "python -m groundtruth_kb.git_lifecycle --json restore-deleted-path --path <repository-relative-path> --source-ref <commit-ref>",
  "before_behavior": "The governed Git-lifecycle package cannot restore one deleted tracked predecessor without raw Git or ad hoc copying.",
  "after_behavior": "One self-descriptive command validates one deletion, restores the exact selected committed blob to the worktree, verifies it, and proves unrelated status preservation.",
  "self_descriptive_naming": "restore-deleted-path, source-ref, source-commit, source-blob, restored-blob, and unrelated-status-hash describe the exact operation and evidence.",
  "obsolete_guidance_disposition": "Raw Git, whole-tree restoration, and ad hoc file copies are not accepted governed recovery routes.",
  "history_preservation": "The index and commit history are unchanged; only one deleted worktree path is restored.",
  "baseline": {
    "predecessor": "WI-5421 VERIFIED v004",
    "linked_test": "TEST-11572",
    "existing_source_targets": 3,
    "new_test_targets": 1
  },
  "expected_result": {
    "success": "The restored worktree blob equals the explicitly selected committed source blob and unrelated status evidence is unchanged.",
    "denial": "No target or unrelated path changes.",
    "live_repository": "No production invocation is performed by WI-5474 implementation or verification."
  },
  "rollback": {
    "instructions": "Governed revert of only the four WI-5474 implementation targets.",
    "verification": "Run the focused exact-restore module plus the existing frozen Git-lifecycle acceptance activity."
  },
  "hard_invariants": [
    "Exactly one normalized repository-relative path.",
    "Exactly one explicitly resolved source commit and blob.",
    "Input path state is unstaged deletion only.",
    "Index and unrelated worktree state remain unchanged.",
    "No live GT-KB restore is part of implementation or verification."
  ],
  "fail_closed_conditions": [
    "Unsafe, empty, absolute, escaping, .git, pathspec-like, or multi-path input.",
    "Unknown or ambiguous source ref.",
    "Path is untracked or absent from the selected commit.",
    "Path state is not exactly an unstaged deletion.",
    "Restored blob differs from source blob.",
    "Unrelated status evidence changes."
  ],
  "essential_context_preservation": "The result retains normalized path, requested ref, resolved commit, source and restored blobs, target status transition, unrelated status hashes, and operation outcome."
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

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded
  carriers and proposals for defects discovered while driving the fleet and
  black-box program, while preserving every later implementation gate.
- `bridge/gtkb-wi5421-git-lifecycle-package-baseline-004.md` independently
  verifies and adopts the production package that WI-5474 extends.
- `bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-008.md` records the
  deleted-predecessor finalization diagnosis that exposed the missing
  operation.
- `bridge/gtkb-wi5362-parity-entrypoint-import-shadowing-009.md` records that
  the immediate predecessor was restored and asks for finalization retry; it
  does not add a reusable production restore surface.
- No prior Deliberation Archive record found rejects a single-path,
  worktree-only, explicit-commit restore operation.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner
  decision behind the active singleton V2 PAUTH.
- The build envelope is case-authorized only for the four declared source/test
  targets after independent GO and implementation-start authorization.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` remains
  binding. This proposal neither requires nor authorizes dispatcher
  configuration or runtime-state mutation.
- No new owner decision is required.

## Specification-Derived Verification Plan

| Specification | Required executed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; TEST-11572 | In a temporary repository, delete one tracked numbered bridge file, run the production CLI boundary, and prove the restored blob equals the explicit source blob. |
| `DCL-GIT-BRANCH-BINDING-PROMOTION-001` | Exercise the new service and repository primitives through `python -m groundtruth_kb.git_lifecycle`, not by calling raw Git from the test as the operation under test. |
| `GOV-WORK-TREE-HYGIENE-001` | Seed unrelated staged, modified, deleted, and untracked fixtures; prove their porcelain records and index blobs are unchanged after success. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the existing frozen Git-lifecycle acceptance activity and confirm every pre-existing command remains green. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Verify the active singleton V2 PAUTH, latest GO, exact claim, schema-v3 start packet, and per-path authorization before editing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live applicability preflights with no missing specifications, project-linkage errors, or blocking errors. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the report with executed focused, denial-matrix, adjacent, Ruff, format, compile, and diff-check results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every fixture under a temporary in-root test directory and prove no external repository or live GT-KB target is mutated. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify WI-5474, TEST-11572, PAUTH V2, proposal, GO, implementation report, and independent verdict remain linked and WI-5474 stays open until VERIFIED. |

Required focused cases:

- success from `HEAD` with exact blob and unrelated-status preservation;
- success from a different explicit committed source ref;
- unsafe path, path escape, `.git`, pathspec-like, and multi-path denial;
- unknown, noncommit, and ambiguous source-ref denial;
- untracked, clean, modified, staged modification, staged deletion, rename,
  and conflict-state denial;
- source ref missing the path;
- restored-blob mismatch and unrelated-status-drift detection;
- JSON and human-readable CLI result/denial behavior.

Required command evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_exact_restore.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py platform_tests/scripts/test_git_lifecycle_exact_restore.py
```

## Acceptance Criteria

- One command accepts exactly one safe repository-relative path and one
  explicit source ref.
- Success is possible only from an unstaged deletion of a tracked path.
- The selected ref resolves to one commit and the path resolves to one source
  blob before mutation.
- The worktree file after restoration hashes to the selected source blob.
- The index is byte-for-byte unchanged for the target and unrelated paths.
- Every unrelated status record remains exactly unchanged.
- Every denied request fails before mutation with a stable actionable code.
- Structured output carries the complete commit/blob/status evidence.
- Existing Git-lifecycle behavior and tests remain green.
- All implementation and tests are confined to the four declared targets and
  isolated temporary repositories.
- No live restore, dispatcher/TAFE configuration or runtime-state mutation,
  Git staging/commit/history rewrite/push, credential action, deployment, or
  release occurs.

## Risks / Rollback

The primary risk is accidentally converting a narrow recovery command into a
general overwrite surface. Exact path normalization, explicit commit
resolution, tracked-blob proof, deletion-only status, index preservation, and
post-restore blob/status verification constrain that risk.

A second risk is false preservation evidence from line-oriented status
parsing. The implementation must use NUL-delimited porcelain output or an
equivalent structured exact-record representation and compare all unrelated
records, including staged and untracked entries.

A third risk is silently changing existing Git-lifecycle behavior. The frozen
WI-5421 acceptance activity and full adjacent tests remain mandatory.

Rollback is a separately governed revert of only the four WI-5474
implementation targets. It must not execute the restore operation, alter
package files owned by WI-5421, rewrite the bridge chain, or touch unrelated
worktree/index state.

## Cross-Harness Disposition

No managed harness prompt, skill, hook, adapter, or generated projection is
changed. The production Python package and focused platform tests are shared
platform surfaces; no cross-harness projection is required.

## Recommended Commit Type

`feat:`

The change adds a new governed exact-path recovery capability while preserving
all existing Git-lifecycle commands.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
