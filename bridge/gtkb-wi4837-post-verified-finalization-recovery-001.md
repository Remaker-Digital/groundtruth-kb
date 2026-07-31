NEW

# WI-4837 Post-VERIFIED Prime-Side Finalization Recovery

bridge_kind: prime_proposal
Document: gtkb-wi4837-post-verified-finalization-recovery
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; interactive build envelope; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4837-BATCH-A1-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4837

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: source/test/cli-gate
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4837 closes the authorization deadlock that appears after a bridge thread reaches a legitimate `VERIFIED` state but the verified implementation/report/verdict path set remains uncommitted because finalization was skipped or file-only. The normal implementation-start path correctly treats latest `VERIFIED` as terminal and rejects fresh source work; however, that also leaves no sanctioned Prime-side route for an owner-waived finalization-only commit of already-verified files.

This proposal adds a narrow post-`VERIFIED` finalization-recovery authorization mode. The mode must require explicit owner-waiver deliberation evidence, exact include paths, a live Prime work-intent claim, and a latest `VERIFIED` bridge chain. It must authorize only staging/commit-style finalization of the exact verified path set, not file edits, cleanup, backlog/database mutation, deletion, stash handling, worktree pruning, or new implementation work. The proposal also locks in the already-partial cross-session repair by adding regression coverage that a peer thread's report snapshot under review does not globally freeze unrelated sessions and disjoint target paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - terminal bridge state, recovery authority, and implementation reports must continue to flow through numbered bridge files and role-correct statuses.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A1 PAUTH authorizes this bounded gate/source/test work but does not itself permit protected mutations.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization cannot bypass bridge `GO`, work-intent claims, or implementation-start packets; this slice creates a governed packet type for a missing recovery case.
- `GOV-WORK-TREE-HYGIENE-001` - file-only verified work left uncommitted is stale worktree state that must be recoverable through explicit evidence rather than ad hoc commits.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - recovery packets must prove owner waiver evidence and avoid confusing Prime finalization with Loyal Opposition review authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - packet validation must read live bridge chains, live work-intent state, and current deliberation records rather than cached startup summaries.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links concrete governing specs and exact target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable PAUTH, project, work-item, and target path metadata are present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map the new recovery packet behavior and cross-session snapshot behavior to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4837 must terminalize through durable bridge evidence rather than remaining as repeated operational friction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all mutations stay inside the GT-KB platform root and do not touch Agent Red application surfaces.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner waivers, bridge state, packet evidence, and verification results must remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - finalization recovery should be a deterministic artifact path, not chat-only operational memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - file-only `VERIFIED` state is a lifecycle trigger for a bounded recovery action.

## Prior Deliberations

- `DELIB-20266123` - owner decision waiving Loyal Opposition atomic commit for WI-4813's file-only `VERIFIED` thread and authorizing Prime-side finalization of exactly four verified paths.
- `DELIB-20266102` - owner decision prioritizing WI-4813 and the implementation scope that later exposed this finalization gap.
- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` - owner approved Batch A1, including WI-4837, under explicit forbidden operations.
- `bridge/gtkb-wi4893-false-verified-finalization-recovery-004.md` - VERIFIED false-terminal recovery precedent: finalization gates must fail closed while preserving explicit by-reference waiver behavior.
- `bridge/gtkb-wi5004-verified-finalization-include-set-repair-006.md` - VERIFIED include-set repair/no-action disposition preserving by-reference waiver and helper parity lessons.
- `platform_tests/scripts/test_implementation_authorization.py` - existing post-GO `NO-GO` resume and terminal `VERIFIED` fail-closed coverage that this slice should extend, not weaken.
- `platform_tests/scripts/test_implementation_start_gate.py` - existing session-aware packet lookup and cross-claim collision coverage proving the current cross-session direction is already partially implemented.

## Owner Decisions / Input

No new owner decision is required for proposal filing.

Carried-forward authorization:

- `DELIB-20260705-HIGH-PRIORITY-BATCH-A1-APPROVAL` / `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4837-BATCH-A1-20260705` authorize this WI through the normal bridge process.
- `DELIB-20266123` is an example owner waiver the implementation must be able to validate for a post-`VERIFIED` finalization-recovery packet; the implementation must not assume that this single deliberation authorizes unrelated threads.
- The PAUTH forbids credential lifecycle, deploy, force-push, secret disclosure, destructive bulk cleanup, broad bulk status mutation, stash drop, branch/worktree prune, untracked file deletion, and committing another session's stale work without specific apply evidence.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4837's backlog text, the Batch A1 PAUTH, `DELIB-20266123`, and the governing bridge/authorization/worktree hygiene specs define the needed behavior. A new formal GOV/ADR/DCL is not required for this implementation slice because the recovery path is an implementation-start authorization refinement, not a new role authority model.

## Proposed Scope

- Add a dedicated post-`VERIFIED` finalization-recovery packet path to `scripts/implementation_authorization.py`, exposed as a CLI subcommand or flag with equivalent semantics.
- Require `--bridge-id`, `--owner-waiver-deliberation-id`, and one or more exact `--include` paths for recovery packet creation.
- Validate that the bridge thread's latest status is `VERIFIED`, that the pinned terminal chain is still live, and that normal `begin` without recovery mode continues to fail on terminal `VERIFIED`.
- Validate that the owner-waiver deliberation is an owner decision and names the same bridge/work item or otherwise clearly scopes the same exact finalization action.
- Normalize and store the exact include paths as the packet's authorized target set, with a packet mode such as `post_verified_finalization_recovery`.
- Update `scripts/implementation_start_gate.py` so a recovery packet authorizes only finalization-style git staging/commit commands for the exact path set and refuses raw file writes, `apply_patch`, delete/restore/clean/stash/prune operations, and broad commands.
- Preserve existing session-aware named-packet lookup and cross-claim path-collision behavior.
- Add regression coverage proving a different session's post-implementation report under review blocks only that session/claimed overlapping target scope, not unrelated target paths for another session's valid packet.

## Explicit Non-Scope

- Do not perform the WI-4813 finalization commit in this slice.
- Do not resolve WI-4813, WI-4837, or any work item directly from implementation code.
- Do not change Loyal Opposition `VERIFIED` helper semantics or cross-harness helper copies.
- Do not authorize new edits after a thread is terminal `VERIFIED`.
- Do not mutate `groundtruth.db`, project authorizations, deliberation rows, credentials, deployment files, or dispatcher configuration.
- Do not delete untracked files, drop stashes, prune worktrees, or perform broad dirty-worktree cleanup.

## Spec-Derived Verification Plan

| Governing surface | Required implementation behavior | Verification |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Normal implementation-start packets still require latest `GO` or resumable post-report `NO-GO`; terminal `VERIFIED` remains closed unless finalization-recovery mode is explicitly requested. | Extend `platform_tests/scripts/test_implementation_authorization.py` with terminal `VERIFIED` negative controls and a positive recovery-packet fixture. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Recovery packets require live work-intent ownership, project authorization metadata, and owner-waiver evidence; PAUTH alone is not enough. | Add tests for missing claim, wrong-session claim, missing/invalid owner waiver, and successful same-session recovery packet creation. |
| `GOV-WORK-TREE-HYGIENE-001` | Recovery packet target paths are exact, bounded finalization paths; no destructive cleanup or another session's stale work is authorized. | Add tests proving delete/stash/prune/clean/broad commands are denied and exact include paths are normalized. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Owner-waiver evidence is validated as owner-decision provenance and tied to the correct bridge/work item. | Add deliberation fixture tests for wrong source type, wrong outcome, wrong bridge/work-item scope, and valid waiver. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Recovery validation reads live bridge files, live claim registry, and live deliberation rows at packet creation and validation. | Add drift tests: terminal file changes, newer bridge status appears, packet expiry, and deliberation mismatch fail closed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report maps each new behavior to executed tests and exact command output. | Implementation report must include focused pytest, ruff check, and ruff format evidence for the changed files. |
| Cross-session snapshot behavior from WI-4837 | A peer session's report awaiting review does not globally block unrelated sessions or disjoint targets, while overlapping active claims remain blocked. | Extend `platform_tests/scripts/test_implementation_start_gate.py` with disjoint peer-awaiting-review allow coverage and overlapping active-claim block coverage. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All source/test edits remain inside GT-KB root and outside adopter paths. | Applicability and clause preflights plus target-path inspection must pass. |

Minimum verification commands after implementation:

```text
python -m pytest platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts\implementation_authorization.py scripts\implementation_start_gate.py platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_start_gate.py
python -m ruff format --check scripts\implementation_authorization.py scripts\implementation_start_gate.py platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_implementation_start_gate.py
```

## Acceptance Criteria

- A normal `begin --bridge-id <verified-thread>` still fails with the existing terminal `VERIFIED` denial.
- A recovery-mode packet succeeds only with a live same-session work-intent claim, a valid owner-waiver deliberation, latest `VERIFIED` bridge state, and exact include paths.
- Recovery-mode packets cannot authorize raw source/test edits, `apply_patch`, destructive cleanup, stash drop, worktree prune, untracked deletion, or broad status mutation.
- Recovery-mode packets can authorize only finalization-style git staging/commit commands for the exact include path set.
- A peer thread's report snapshot under review does not freeze unrelated sessions and disjoint target paths.
- Existing post-GO `NO-GO` resume, named-packet fallback, same-session overlapping claim, and cross-session overlapping claim behavior remains intact.

## Risk / Rollback

Risk is moderate because this code sits directly on the protected mutation gate. The main failure modes are accidentally reopening terminal `VERIFIED` for new implementation edits, accepting a weak owner waiver, or over-blocking independent sessions. The mitigation is to model recovery as a separate packet mode with exact path and operation restrictions plus negative tests.

Rollback is a revert of the implementation commit touching `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, and the focused tests. Bridge files are append-only and should remain as audit evidence.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4837-post-verified-finalization-recovery`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the implementation repairs an authorization deadlock and prevents verified work from being stranded without broadening terminal bridge authority.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
