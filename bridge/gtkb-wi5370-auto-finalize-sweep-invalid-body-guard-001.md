NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - WI-5370 Auto-Finalization Sweep Invalid-Body Guard

bridge_kind: prime_proposal
Document: gtkb-wi5370-auto-finalize-sweep-invalid-body-guard
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["scripts/auto_finalize_sweep.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py", ".claude/rules/auto-finalization-sweep.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Harden the Stop-hook auto-finalization sweep so it cannot keep attempting pathspec commits for terminal `VERIFIED` files that the current canonical finalizer/checker rejects, and so a blocked commit subprocess cannot hold `.git/index.lock` indefinitely during the repo-wide finalization reconciliation.

This is a support slice for `WI-5370`. It does not finalize any bridge thread, does not remove any bridge file, does not reset the Git index, and does not alter dispatcher routing. It only proposes safer eligibility and timeout behavior for the existing sweep actuator.

## First-Line Role Eligibility Check

- Active transcript-defined role: Prime Builder via `::init gtkb pb`.
- Status authored here: `NEW`, a Prime Builder proposal status.
- This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, and does not mutate the proposed protected source paths.

## Current Evidence

Fresh reconciliation evidence shows the current `scripts/auto_finalize_sweep.py` actuator is now part of the sprawl failure mode:

- Live process: `pythonw "E:\GT-KB/scripts/auto_finalize_sweep.py"` with PID `27692`.
- Child process: `git -C E:\GT-KB commit -m "chore(bridge): finalize Cursor-LO gtkb-wi5353-implementation-start-harness-selector VERIFIED verdict (-004)" -- bridge/gtkb-wi5353-implementation-start-harness-selector-004.md`.
- Fresh `.git/index.lock`: created `2026-07-16 16:45:49` and last written `2026-07-16 16:47:44` local time while the sweep commit process remained active.
- Staged paths observed while the lock was present:
  - `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md`
  - `bridge/gtkb-wi5353-implementation-start-harness-selector-004.md`
- Recent sweep audit entries report repeated `commit blocked/failed` events for terminal `VERIFIED` bridge threads including `gtkb-wi5241-wi5219-pauth-registered-vocabulary`, `gtkb-wi5249-prime-no-action-claim-filer`, `gtkb-wi5254-pauth-amendment-packet-preflight`, `gtkb-wi5316-frozen-modernization-rc-contract`, and `gtkb-wi5318-modified-terminal-verdict-provenance`.
- The updated WI-5116/WI-5370 planner classifies these same shapes as blocked (`terminal_verified_blocked_invalid_verdict_body`, `terminal_verified_blocked_missing_scope`, or `mixed_provenance_stop`), not direct finalization candidates.

The current sweep predates the stricter helper/checker floor. It only checks independence and clean implementation target paths before attempting `git add` and `git commit -- <chain>`. It does not ask whether the terminal verdict body would be accepted by `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`, nor whether the protected-commit authorization checker would reject the staged terminal verdict for lacking helper-generated `## Commit Finalization Evidence`.

## Proposed Scope

1. Add a fail-closed eligibility check before `_commit_chain()`:
   - Skip the candidate if `write_verdict.validate_verified_body()` rejects the terminal `VERIFIED` body.
   - Skip the candidate if the protected commit authorization checker would reject the exact pathspec commit because the terminal `VERIFIED` file lacks helper-compatible same-transaction finalization evidence.
   - Audit these skips with a distinct reason, for example `canonical_finalizer_rejects_verdict_body` or `protected_commit_authorization_rejects_terminal_verdict`.
2. Add a bounded timeout to Git subprocesses launched by the sweep, especially `git commit`, so the Stop hook cannot indefinitely hold `.git/index.lock`.
3. Preserve the existing cheap gate, dry-run behavior, audit log, independence check, and clean-target check.
4. Update the rule document to state that the sweep is a narrow legacy bridge-verdict drain only when the current canonical finalization/checker floor accepts the candidate. It must not fight the per-thread repair planner during a commingled tree reconciliation.
5. Add focused tests that:
   - A terminal `VERIFIED` body missing `Recommended commit type` is skipped before `git add` / `git commit`.
   - A checker-rejected terminal verdict is skipped and audit-logged.
   - A commit timeout is reported as an error and does not spin.
   - Existing no-op, self-review, dirty-target, planner-error, dry-run, audit-log, and registration tests continue passing.

## Explicit Non-Goals

- Do not stage, unstage, reset, delete, or commit any current dirty worktree path.
- Do not kill or restart the currently running sweep process from this proposal.
- Do not change dispatcher routing, leases, or the separate WI-5320/WI-5328/WI-5330 dispatcher-starvation program.
- Do not authorize Prime Builder to write any replacement `VERIFIED` verdict.
- Do not broaden the sweep into source/test finalization or hunk attribution.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `bridge/gtkb-wi5027-worktree-finalization-commit-discipline-lapse-*` - resolved precedent for avoiding broad finalization commits during repo-wide bridge/source sprawl.
- `bridge/gtkb-wi5116-per-thread-finalization-repair-001.md` through `-004.md` - current per-thread planner/runbook precedent.
- `bridge/gtkb-wi5370-finalizer-body-validation-classification-001.md` through `-003.md` - active planner hardening slice that classifies invalid terminal `VERIFIED` bodies as blocked instead of direct repair candidates.
- `bridge/gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue-001.md` and `bridge/gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue-*` - active per-thread invalid terminal verdict reissue repair examples.

## Requirement Sufficiency

Existing requirements are sufficient. The problem is not a new product behavior requirement; it is an actuator safety correction so the existing Stop-hook sweep follows the stricter bridge finalization/checker floor now enforced by the repo.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `python -m pytest platform_tests/hooks/test_auto_finalize_verified_verdicts.py -q --tb=short`; confirm tests prove no `git add` or `git commit` for invalid/checker-rejected candidates. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests and implementation show the sweep does not author verdicts and only considers already-authored bridge files after stricter eligibility gates. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests cover a terminal `VERIFIED` body missing `Recommended commit type` and prove canonical finalizer validation blocks it. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-auto-finalize-sweep-invalid-body-guard` must pass. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This proposal and implementation report retain PAUTH, project, work item, and exact target path metadata. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Existing registration parity test must continue passing; this slice changes behavior, not hook registration. |

## Acceptance Criteria

- Invalid terminal `VERIFIED` bodies are skipped before any sweep staging or commit attempt.
- Protected-checker-rejected terminal verdicts are skipped before any sweep staging or commit attempt.
- Git commit subprocesses launched by the sweep are bounded by a timeout and audit-log timeout failures without spinning.
- Existing eligible-sweep behavior remains covered by tests, unless implementation discovers that helper/checker compatibility makes all current legacy pathspec commits unsafe; in that case the report must state the resulting report-only behavior explicitly for LO review.
- `python -m pytest platform_tests/hooks/test_auto_finalize_verified_verdicts.py -q --tb=short` passes.

## Risk And Rollback

Risk is moderate because this touches a Stop-hook actuator. The least-regret behavior is fail-closed: skipping an unsafe candidate preserves the untracked verdict for the per-thread repair planner, while an unsafe pathspec commit or stuck lock can block all later atomic finalization.

Rollback is a revert of the three target paths. No current worktree path is staged, unstaged, committed, deleted, or reset by this proposal.

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
