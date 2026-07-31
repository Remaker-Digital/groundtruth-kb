REVISED

# WI-5298 Finalization-Readiness Correction

bridge_kind: operational_state_change
Document: gtkb-wi5298-codex-snapshot-git-window-containment
Version: 005
Responds to: bridge/gtkb-wi5298-codex-snapshot-git-window-containment-004.md
Approved proposal: bridge/gtkb-wi5298-codex-snapshot-git-window-containment-001.md
GO verdict: bridge/gtkb-wi5298-codex-snapshot-git-window-containment-002.md
Implementation report: bridge/gtkb-wi5298-codex-snapshot-git-window-containment-003.md
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5298
target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "scripts/ops/harness_storm_watchdog_launcher.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: finalization_readiness_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

The sole blocker in version 004 was finalization sequencing, not implementation
correctness. That blocker is now resolved by committed current state. Commit
`42a252ab` contains all four WI-5298 implementation targets, versions 001-004
of this bridge chain, and the finalizer, bridge-writer, and review-independence
machinery that version 004 found dirty. Every one of those paths is now clean
relative to HEAD.

The current committed finalizer builds a disposable index from HEAD and
explicitly tolerates unrelated paths in the shared real index. Therefore the
old clean-shared-staging precondition cited by version 004 no longer applies.
No source or test byte changed for this revision. The request is limited to a
fresh independent terminal review of the already-verified implementation and
focused finalization of the correction/verdict chain.

This revision does not claim an owner by-reference waiver and does not treat
the broad sweep commit as new implementation work. It records that the exact
preconditions ordered by the finalization-scoped NO-GO have become true.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-202666274` authorizes the modernization program while preserving the
  bridge, implementation-start, independent verification, and Git gates.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` requires background automation
  to avoid visible console windows.
- `DELIB-20260715-WINDOW-NOT-A-WITHHOLD-REASON` establishes that console
  visibility is never a reason to disable or withhold a harness.
- `DELIB-202666320` keeps WI-5113 finalizer subprocess scope distinct from the
  interactive Codex Desktop snapshot path repaired here.
- Version 004 independently verified the four-target implementation as
  substantively correct and requested only committed finalization machinery
  plus an interactive, isolated finalization path.

## Owner Decisions / Input

No new owner decision is required. The owner already required the only
acceptable behavior: fix visible windows without disabling, suppressing,
deprioritizing, or otherwise impairing a harness or bridge automation. This
revision performs no dispatcher, TAFE, harness, eligibility, process-lifecycle,
credential, deployment, release, push, or destructive-cleanup operation.

## Findings Addressed

### F1 - Governance machinery was dirty and unreviewed

Response: resolved in committed state. `git log --` shows `42a252ab` as the
current commit for `.claude/skills/verify/helpers/write_verdict.py`,
`scripts/gtkb_bridge_writer.py`, and `scripts/bridge_review_independence.py`.
`git status --short --` for those files is empty.

### F2 - The shared real staging area was not clean

Response: the committed finalizer now creates a disposable index with
`GIT_INDEX_FILE`, reads HEAD into it, stages only the declared verified set and
verdict, checks the exact temporary staged set, commits without a pathspec, and
realigns the shared index afterward. Its contract explicitly tolerates
unrelated paths already staged by other sessions. Current shared-index dirt is
therefore isolated rather than captured.

### F3 - Re-dispatch would repeat the same finalization failure

Response: the premise has changed. All four implementation targets and bridge
versions 001-004 are tracked and clean at HEAD, the finalizer machinery is
tracked and clean, and the current helper has the isolated-index behavior that
the version-004 reviewer required. A fresh review no longer encounters the
recorded blocker.

## Scope Changes

No implementation scope change. The four approved implementation paths remain
byte-identical to `42a252ab`. This revision adds only current-state evidence
that the finalization blocker has cleared.

## Pre-Filing Preflight Subsection

- Applicability preflight: PASS; pending-content packet
  `sha256:c785536b6af90e0dae44a090674f94427b468fa422719035303b335fcbe3d782`;
  `missing_required_specs: []`; `missing_advisory_specs: []`.
- Mandatory clause preflight: PASS; five clauses evaluated; three
  `must_apply`; zero blocking gaps; observed exit 0.
- Exact target state: PASS; all four approved paths are tracked and clean at
  HEAD.
- Finalizer machinery state: PASS; the finalizer, bridge writer, and review
  independence helper are tracked and clean at HEAD.

## Verification Plan

| Requirement | Executed evidence | Result |
| --- | --- | --- |
| Hide-only implementation remains correct | `python -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short` | PASS: 27 passed; one pre-existing `asyncio_mode` warning |
| Source quality | `python -m ruff check` on the exact four targets | PASS: all checks passed |
| Formatting | `python -m ruff format --check` on the exact four targets | PASS: four files formatted |
| Import/compile integrity | `python -m py_compile` on the exact four targets | PASS |
| Runtime presence | Read-only process census for `codex_snapshot_window_hider.py` | PASS: one persistent two-process `pythonw.exe` interpreter chain is live |
| Commit coverage | `git show --name-status 42a252ab --` on the four targets and versions 001-004 | PASS: exact implementation and chain are present in HEAD |
| Finalizer readiness | Static inspection of committed `finalize_verified_commit` plus clean-path status | PASS: disposable-index exact-set transaction is active and clean |

Version 004 already independently executed the same focused tests and found the
implementation VERIFIED-worthy on substance. The fresh run above confirms no
regression after commit `42a252ab`.

## Files Changed

No implementation files changed in this revision. The implementation reviewed
for terminal disposition remains:

- `scripts/ops/codex_snapshot_window_hider.py`
- `scripts/ops/harness_storm_watchdog_launcher.py`
- `platform_tests/scripts/test_codex_snapshot_window_hider.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`

## Requested Loyal Opposition Action

Independently confirm that the version-004 finalization blockers are closed and
that the four-target implementation still satisfies the carried-forward
specification-to-test mapping. If so, issue terminal VERIFIED through the
governed finalization path. The terminal commit must remain focused on this
thread's untracked correction/verdict chain and must not capture unrelated
shared-index or worktree changes.

## Risk And Rollback

The revision changes no runtime or implementation behavior. Its only risk is a
false readiness claim; that fails closed through independent review, exact
clean-path checks, and the finalizer's disposable-index staged-set assertion.
If any premise is stale, return NO-GO and leave the implementation untouched.
Rollback of this revision is append-only bridge correction, not source or
runtime mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
