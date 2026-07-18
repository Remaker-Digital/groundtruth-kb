NEW

# WI-5421: Stabilize the untracked production Git lifecycle package baseline

bridge_kind: prime_proposal
Document: gtkb-wi5421-git-lifecycle-package-baseline
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-17T03:33:10Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: desktop interactive Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5421

target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/quiescence.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/state.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt the exact current byte images of the eight-file
`groundtruth_kb.git_lifecycle` package as one independently reviewed baseline.
Committed modernization acceptance and implementation-start surfaces import
this package, but every package file is absent from `HEAD` and all Git history.
The current worktree is therefore the only carrier for a production dependency.

This slice makes no semantic edit. It gives the complete foreign package one
bounded owner so a later exact mechanical finalizer can add only these reviewed
bytes. The candidate spans branch binding, state and audit, scoped
preservation, bounded quiescence, local promotion, and hosted pull-request
promotion. It must be reviewed as a whole against the current Git lifecycle
requirements; passing imports alone is insufficient.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__init__.py` | 942 | `3DF6694CE7EB6098BB3BF60A64A496D3CC0D0794D60725B8C0324C5BBE51679E` |
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py` | 9,397 | `AB9A09206280D0931AC1A3CE3F2C1FF9B4A000938BE6C8762293A2DB7A1D4521` |
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py` | 1,323 | `72183BAC43A20C9E9BD83796F2A69CFA3EE0C30123DC26248B1B984C10A8D5FA` |
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/models.py` | 1,950 | `D8A0DE92FD65AAA7BB83E5F90BA95C916C7CEA97837B48AAB00514380CA3F969` |
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/quiescence.py` | 12,277 | `A4197C54911982BFE92670C5C100ADD36FF457B8F0ED4FF2D53CFF3B1F994D94` |
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py` | 5,507 | `BAEA9C96FD6BBF8F63AE990DACBCB32B64A2FE588DC47D897943A6183114FEDB` |
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py` | 116,214 | `B2EBF9DB4F3C8D188EF8B7036569E0121A40F1127E88A8BD97DDF79C934A2D2C` |
| `groundtruth-kb/src/groundtruth_kb/git_lifecycle/state.py` | 22,921 | `DAD8AADB463688482BC9F8B025E57092E33890F01E1433C4BCF8734FB08BA671` |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before protected implementation and VERIFIED before completion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the proposal to cite the complete applicable requirement set.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds this proposal to the active Tree Stabilization PAUTH and WI-5421.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent verification to execute the mapped checks.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not replace bridge GO, claim, or implementation-start authority.
- `GOV-STANDING-BACKLOG-001` - governs the hygiene backlog record and linked test.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the orphaned production dependency and its review evidence to become durable linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires traceability from the candidate bytes through WI-5421, TEST-11532, review, and finalization evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps the untracked candidate, reviewed baseline, implementation report, VERIFIED result, and final committed state distinct.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` - defines the complete branch, worktree, commit, promotion, quiescence, and fail-closed outcomes represented by the package.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - constrains binding, scoped preservation, integration, promotion, recovery, and bootstrap behavior.
- `DCL-DISPATCHER-QUIESCENCE-LEASE-001` - constrains the package's quiescence and drain behavior without granting live dispatcher authority.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact ownership and preservation of concurrent work rather than whole-tree absorption.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires measurable baseline/result/rollback evidence and preservation of existing behavior.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires current, complete, fail-closed evidence rather than import-only or metadata-only approval.

## Prior Deliberations

- `INTAKE-c5792b0c` - confirmed the governed Git lifecycle and bounded
  dispatcher-coordination requirement. This proposal does not widen that
  requirement; it gives the already-present implementation candidate a
  reviewable, exact-byte baseline.

## Owner Decisions / Input

The owner authorized the full modernization program and directed that every
discovered defect or enhancement opportunity be recorded as a hygiene backlog
item, while work authorization is project-scoped. The owner also requires
exact ownership and independently verified mechanical finalization of all
worktree dirt. No new owner decision is required to file or review this
baseline proposal. Protected implementation still requires independent GO,
matching claim/start authority, and later exact Git mechanical authority.

## Requirement Sufficiency

Existing requirements sufficient - the governed Git lifecycle requirement,
branch/promotion and quiescence DCLs, worktree-hygiene GOV, modernization
non-impairment GOV, and bridge/project authorization rules fully define this
exact-byte baseline adoption. This proposal creates no new runtime behavior.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5421 worktree ownership audit at HEAD 42a252ab57b5a203e9406b626c741d897e8fb196",
  "canonical_authority": "MemBase project, work-item, PAUTH, bridge, claim, and verification state plus Git HEAD for reviewed implementation bytes",
  "primary_route": "Independent bridge review of one exact eight-file package baseline followed by the governed implementation-report and VERIFIED finalizer path",
  "before_behavior": "Committed modernization acceptance imports a package whose eight implementation files exist only as untracked worktree bytes",
  "after_behavior": "The same independently reviewed eight byte images are present in Git HEAD as one bounded baseline dependency with no semantic edits",
  "self_descriptive_naming": "WI-5421 and gtkb-wi5421-git-lifecycle-package-baseline explicitly name the production dependency and baseline-only scope",
  "obsolete_guidance_disposition": "No guidance is added, removed, or reactivated by this exact-byte baseline",
  "history_preservation": "All existing Git, bridge, MemBase, and concurrent worktree history remains intact; no prior artifact is rewritten",
  "baseline": "Eight absent-from-HEAD files totaling 170531 bytes, bound to the SHA-256 values in this proposal",
  "expected_result": "Exact hashes remain unchanged, Ruff and compilation pass, frozen Git lifecycle acceptance passes, and only the eight target paths become finalizable",
  "rollback": "A separately authorized governed rollback removes only the exact baseline commit while preserving all unrelated work and evidence",
  "hard_invariants": "No direct harness contact, no manual routing, no live dispatcher mutation, no groundtruth.db finalization, no unrelated staging, no history rewrite, and no false PASS from missing or partial evidence",
  "fail_closed_conditions": "Any hash drift, missing target, unexpected extra path, test failure, stale authority, incomplete requirement coverage, or inability to isolate exact bytes blocks GO, VERIFIED, and finalization",
  "essential_context_preservation": "The review retains the full Git lifecycle, promotion, quiescence, recovery, and non-impairment requirement context despite the baseline-only implementation shape"
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact WI-5421 target identity; `GOV-WORK-TREE-HYGIENE-001` | Recompute SHA-256 and byte length for every declared target; compare to the table above; run `git status --short -- <eight targets>` | All eight values match exactly; all eight are untracked before adoption; no ninth path is in scope. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`; `DCL-GIT-BRANCH-BINDING-PROMOTION-001`; `DCL-DISPATCHER-QUIESCENCE-LEASE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_git_lifecycle.py -q --tb=short --timeout=750` | PASS, including all 26 frozen Git lifecycle assertions exercised by the checker. |
| Python integrity and production importability | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/git_lifecycle` and `groundtruth-kb/.venv/Scripts/python.exe -m compileall -q groundtruth-kb/src/groundtruth_kb/git_lifecycle` | Both exit 0. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Run the current hard-invariant/non-impairment check required by the modernization RC gate, then inspect the exact checker assertion ledger | No hard-invariant regression; missing, skipped, stale, or unsupported evidence cannot pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; artifact-oriented governance/lifecycle specs | Validate current PAUTH, latest independent GO, matching work intent, implementation-start packet, linked WI-5421/TEST-11532 artifacts, and independent post-implementation verdict through governed CLI surfaces | Every authority and artifact transition is current, linked, and scope-exact; no proposal or project authorization is treated as a substitute. |
| Exact finalization scope | After separate mechanical authority, inspect the resulting commit tree and parent diff | Exactly the eight declared files are added at the reviewed hashes; no database, bridge, harness, dispatcher, test, config, or unrelated source path is included. |

## Risk / Rollback

The primary risk is adopting a large candidate that contains incomplete or
unsafe lifecycle semantics merely because committed tests import it. Independent
review must therefore assess the complete package against the cited requirement
and DCLs and issue NO-GO for any P0/P1 defect, missing evaluator coverage, or
scope ambiguity. Hash drift after review invalidates the approval.

Implementation is byte-preserving and additive. It does not execute any Git
lifecycle operation, acquire quiescence, contact GitHub, mutate dispatcher
state, or stage/commit files. A later exact finalizer requires separate
mechanical authority. Rollback, if authorized later, is limited to the one
baseline commit and must preserve unrelated worktree state.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-wi5421-git-lifecycle-package-baseline`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore` - the eventual bounded diff adopts an existing production dependency
baseline without changing its semantics.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
