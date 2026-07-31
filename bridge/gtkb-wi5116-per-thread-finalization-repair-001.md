NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; transcript role ::init gtkb pb; Default mode; PowerShell; project root E:\GT-KB
author_metadata_source: explicit current Codex session metadata plus gt harness roles check

# WI-5116 - Per-thread finalization repair tool and runbook

bridge_kind: prime_proposal
Document: gtkb-wi5116-per-thread-finalization-repair
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5116

target_paths: ["scripts/per_thread_finalization_repair.py", "platform_tests/scripts/test_per_thread_finalization_repair.py", "docs/procedures/per-thread-finalization-repair.md"]

implementation_scope: source, focused tests, and documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Create a bounded, report-first per-thread finalization repair tool and operator runbook for the current worktree-finalization sprawl. The tool must classify terminal and in-flight bridge/thread dirt into exact per-thread next actions, emit pathspec-limited or hunk-scoped repair instructions, and fail closed whenever source ownership, target paths, or thread status are ambiguous.

This is not a bulk drain proposal. It is not permission to run `git add -A`, sweep-commit the tree, delete untracked files, mutate dispatcher state, or perform git commits from the new tool. Actual finalization commits remain separate per-thread operations through the existing VERIFIED finalization helper or an independently reviewed equivalent path.

## Claim

The 2026-07-16 worktree state shows a renewed repo-wide uncommitted-file sprawl, but the existing WI-5027/WI-4979 tooling stops at classification and the auto-finalization sweep correctly refuses every current terminal VERIFIED candidate. A narrow repair planner/runbook is needed to convert that read-only classification into safe, per-thread operator instructions without authorizing broad mutation.

## Defect / Reproduction

Fresh read-only baseline from 2026-07-16:

- `python scripts/wrap_scan_hygiene.py --report-format markdown` reported `WARN (1310)` findings, dominated by uncommitted tracked paths and untracked bridge files.
- Git porcelain snapshot showed `1492` dirty paths at one read (`1273` untracked, `212` modified, `7` deleted), and the subsequent canonical planner saw `1495` dirty paths, confirming concurrent drift.
- `python scripts/worktree_finalization_triage.py --format markdown` / `groundtruth_kb.hygiene.auto_resolve.build_plan` reported `candidate_actions_only: true`, `read_only: true`, and action counts: `manual_owner_review=1420`, `safe_commit=9`, `skip=37`, `auto_ignore=24`, `auto_drop_byte_identical=5`.
- `scripts.auto_finalize_sweep.sweep(dry_run=True)` reported `finalized: []`, `errors: []`, and skipped all nine numbered untracked terminal `VERIFIED` verdicts because implementation targets were dirty/uncommitted or target paths were not parseable.
- `gt bridge state-report --json` reported dispatcher health `PASS` and only three LO-actionable current threads: WI-5328, WI-5330, and WI-5337. WI-5328/WI-5330 are excluded from this proposal because they belong to the separate dispatcher-starvation handoff program.
- `gt project doctor` was invoked as requested but produced no stdout after several minutes; this proposal does not rely on stale doctor output and keeps doctor behavior out of implementation scope unless later reproduced under a separate WI.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/per_thread_finalization_repair.py`, `platform_tests/scripts/test_per_thread_finalization_repair.py`, and `docs/procedures/per-thread-finalization-repair.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status authority remains the numbered bridge chain and TAFE/dispatcher state; the tool must not invent statuses or author LO-only verdicts.
- `GOV-WORK-TREE-HYGIENE-001` - finalization repair must preserve exact ownership, avoid unrelated dirty files, and fail closed on commingled work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation stays inside the active Tree Stabilization PAUTH and remains GO/start gated.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the PAUTH forbids git commits, destructive cleanup, dispatcher mutation, pushes, release, and deployment; the new tool must honor that envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal declares project authorization, project, work item, and target paths explicitly.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing requirements it affects.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused tests must prove the planner refuses unsafe finalization classes and emits exact instructions only for supported classes.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no implementation may start without independent GO, matching work-intent claim, and implementation-start packet.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-authored bridge filing uses the governed helper path and must not bypass bridge compliance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the sprawl is preserved as a governed repair artifact instead of being collapsed into an opaque cleanup commit.

## Prior Deliberations

- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - precedent for this exact failure class; concluded the tree was not safely bulk-committable and added read-only triage instead of sweeping.
- `bridge/gtkb-wi4979-worktree-hygiene-auto-resolve-actuator-006.md` - established the canonical `groundtruth_kb.hygiene.auto_resolve` planner, report-only behavior, and evidence requirements.
- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - records that auto-finalization sweep fires but fail-safe-skips on metadata/scope rather than guessing.
- `bridge/gtkb-wi5116-bridge-finalization-backlog-diagnosis-drain-002.md` - NO-GO for the stale broad 365-file drain, recommending either withdrawal or a narrow residual proposal with reproduction and targeted tests.
- `bridge/gtkb-wi5116-bridge-finalization-backlog-diagnosis-drain-003.md` - Prime withdrawal of the stale broad drain without replacement implementation authority.
- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-005.md` - verified hunk-scoped finalization precedent for commingled worktrees.
- `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` - current terminal-verdict provenance guard precedent; modified terminal verdicts require exact provenance before any safe-commit classification.

## Owner Decisions / Input

- `DELIB-202666274` backs `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` for active Tree Stabilization work.
- User directive in Codex session `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: "Open a bridge proposal for a bounded per-thread finalization-repair tool/runbook."

## Requirement Sufficiency

Existing requirements are sufficient. The work is a tool/runbook implementation under Tree Stabilization, bounded by existing file-bridge authority, worktree-hygiene, project-authorization, bridge-linkage, and verified-testing requirements. No new governance rule is needed because the proposal does not change finalization authority; it makes the current refusal and repair paths deterministic and operator-readable.

## Proposed Scope

Implement a deterministic, read-only-by-default CLI at `scripts/per_thread_finalization_repair.py` that consumes current git status, numbered bridge chains, and the canonical auto-resolve planner. It should produce a per-thread plan with these classes:

- `terminal_verified_repair_candidate`: terminal VERIFIED chain where target paths are parseable and all implementation/report paths can be proven clean or separately pathspec/hunk scoped.
- `terminal_verified_blocked_dirty_targets`: terminal VERIFIED chain where one or more implementation targets are still dirty or untracked.
- `terminal_verified_blocked_missing_scope`: terminal VERIFIED chain whose proposal/report lacks parseable target paths or response linkage.
- `terminal_withdrawn_or_nonverified_documentation`: terminal non-VERIFIED bridge documentation that may be document-only but still requires protocol review before commit.
- `in_flight_bridge_chain`: NEW, GO, NO-GO, REVISED, NO-ACTION, ADVISORY, or DEFERRED chain that must not be finalized as implementation work.
- `excluded_active_program`: WI-5320/WI-5328/WI-5330 dispatcher-starvation program paths or other explicitly excluded active handoff scopes.
- `mixed_provenance_stop`: any source/test/config path or tracked terminal verdict whose ownership cannot be attributed to one thread.

The CLI may emit exact suggested commands or checklist rows for a human/operator, but it must not stage, commit, delete, revert, push, mutate dispatcher state, update PAUTH, or alter bridge status files.

Add `docs/procedures/per-thread-finalization-repair.md` as the runbook. The runbook must state the invariant: one thread, one finalization commit, exact target paths plus verdict artifact, using `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` or an approved hunk-scoped equivalent. It must also state the STOP conditions for mixed provenance, in-flight bridge status, missing target paths, and active external handoff scope.

## Explicit Non-Scope

- No broad bridge drain.
- No `git add -A`, whole-worktree commit, sweep commit, or bulk status mutation.
- No direct finalization of WI-5320, WI-5328, WI-5330, or other active dispatcher-starvation handoff artifacts.
- No deletion of untracked files or runtime state.
- No modification to `.claude/rules/auto-finalization-sweep.md` in this slice.
- No changes to `scripts/auto_finalize_sweep.py`, `groundtruth_kb.hygiene.auto_resolve`, `write_verdict.py`, `groundtruth.db`, `harness-state/*.json`, or dispatcher/TAFE state unless a later REVISED proposal adds exact target paths and receives GO.

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Unit fixtures with numbered bridge chains in each status class | The planner derives status from versioned files and never treats in-flight NEW/GO/NO-GO/REVISED/NO-ACTION as finalizable implementation work. |
| `GOV-WORK-TREE-HYGIENE-001` | Unit fixtures with dirty implementation targets, missing target paths, clean terminal candidates, and mixed shared source files | Dirty or ambiguous paths become blocked/STOP outcomes; only exact terminal candidates get suggested repair instructions. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Static test or CLI fixture proving apply/commit/delete flags are absent or refused | The tool cannot stage, commit, delete, push, mutate dispatcher state, or perform destructive cleanup. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short` | Focused tests pass. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge applicability and clause preflight against this proposal/report | No missing required specs or blocking clause gaps. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Filing evidence from helper-mediated Codex bridge write path | Proposal is written through `propose_bridge_codex_non_bypass`, not `apply_patch`. |

Expected implementation verification commands:

```text
python -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short
python -m ruff check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
python -m ruff format --check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
python scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330
```

## Acceptance Criteria

- The tool reports a current per-thread repair plan without mutating git, bridge files, database state, dispatcher state, runtime state, or PAUTH records.
- The plan distinguishes terminal VERIFIED candidates, blocked terminal VERIFIED cases, terminal non-VERIFIED documentation, in-flight bridge chains, excluded active programs, and mixed-provenance STOP cases.
- Current nine numbered untracked terminal VERIFIED files are not reported as directly finalizable unless their implementation target paths are clean and parseable at run time.
- WI-5320, WI-5328, and WI-5330 are excluded by default or by required explicit option in the runbook, preserving the separate dispatcher-starvation handoff.
- The runbook gives an operator a one-thread-at-a-time procedure and explicitly forbids broad staging/committing.
- Tests prove the unsafe classes fail closed and that the output is deterministic.

## Risks / Rollback

Risk is moderate because incorrect planner wording could encourage unsafe finalization. The implementation must therefore be report-only, use explicit STOP labels, and avoid convenience flags that perform mutation.

Rollback is a scoped revert of `scripts/per_thread_finalization_repair.py`, `platform_tests/scripts/test_per_thread_finalization_repair.py`, and `docs/procedures/per-thread-finalization-repair.md`. Bridge files are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/per_thread_finalization_repair.py`
- `platform_tests/scripts/test_per_thread_finalization_repair.py`
- `docs/procedures/per-thread-finalization-repair.md`

## Recommended Commit Type

`fix`
