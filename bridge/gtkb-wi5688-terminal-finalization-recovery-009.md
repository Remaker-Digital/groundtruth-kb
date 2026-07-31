REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# WI-5688 Terminal-Finalization Recovery — Authorized Frozen-Candidate Finalization

bridge_kind: prime_proposal
Document: gtkb-wi5688-terminal-finalization-recovery
Version: 009
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5688-terminal-finalization-recovery-008.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5688-TERMINAL-RECOVERY-20260729
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5688
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py", "bridge/gtkb-wi5688-doctor-crash-fastlane-001.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-002.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-003.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-004.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-005.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-006.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-011.md"]
observed_paths: ["bridge/gtkb-wi5688-terminal-finalization-recovery-001.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-002.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-003.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-004.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-005.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-006.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-007.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-008.md"]
terminal_finalization_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py", "bridge/gtkb-wi5688-doctor-crash-fastlane-001.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-002.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-003.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-004.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-005.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-006.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-001.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-002.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-003.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-004.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-005.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-006.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-007.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-008.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-009.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-010.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-011.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-012.md"]
implementation_scope: frozen-candidate-evidence-refresh-and-atomic-terminal-finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

This revision changes no source or test bytes and performs no MemBase,
dispatcher, index, Git-history, push, release, deployment, credential, or
external-system mutation. It requests a fresh independent GO for the exact
recovery lifecycle required by version 008 and the new owner-approved PAUTH.

## Revision Claim

Version 008 correctly invalidated GO-006 because the standing reliability PAUTH
denied every `bridge` target in the atomic recovery transaction. That sole
blocker is now cured by active
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5688-TERMINAL-RECOVERY-20260729`.
The replacement authorization is WI-5688-specific and covers only the two
frozen implementation paths, the six fast-lane predecessors, recovery versions
001 through 012, necessary governance evidence, and the exact local terminal
commit.

After a fresh GO, Prime Builder will acquire a new `go_implementation` claim
and schema-v3 start packet, re-prove the frozen hashes and accepted behavior
without editing either target, and file version 011 as the current
implementation report. Independent Loyal Opposition may then issue version 012
only through the governed atomic `VERIFIED` finalizer over the exact 20-path
inventory above.

## Findings Addressed

### F1 — P1 — GO-006 lacked bridge-class authority

**Resolved by owner authorization.** The new active PAUTH permits `source`,
`test`, `bridge`, and `governance_evidence` only for WI-5688's frozen cohort.
It expressly prohibits source/test byte changes and limits `git_commit` to the
governed exact terminal cohort after fresh REVISED, independent GO, claim,
implementation start, report, and independent terminal verification.

The authorization retains bans on dispatcher mutation, external-system
mutation, credential lifecycle work, destructive cleanup, push, history
rewrite, deployment, and release. Any operation-time denial fails closed.

## Frozen Candidate Evidence

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`: SHA-256
  `E20D1E7D5E15359A294527767B169F43750F77B0A7CFF7E791F782E0AB4960D7`,
  current diff 13 insertions and 2 deletions.
- `platform_tests/scripts/test_doctor_skill_rename_sweep.py`: SHA-256
  `3D7835AFAC9690BB6CCF68496FFE72173996FE06665A05D36B9E1DF1E85A7D61`,
  current diff 47 insertions and 0 deletions.
- The six fast-lane artifacts and recovery versions 001 through 008 remain
  untracked; the Git index is empty.
- Prior independent evidence reproduced seven focused tests, Ruff check and
  format, exact hashes, a live doctor `warning` rather than a crash, and the
  pre-fix Unicode failure.

Any candidate hash/diff drift, additional dirty target, nonempty index, partial
predecessor commit, changed technical result, or PAUTH denial is a stop
condition requiring another governed revision.

## Scope Changes

The source/test behavior, implementation bytes, and technical acceptance are
unchanged. The only change from versions 005 through 008 is the executable
authority and exact lifecycle:

1. version 009 REVISED proposal;
2. version 010 independent GO;
3. fresh exact claim and schema-v3 implementation start;
4. no byte changes; refresh all candidate and technical evidence;
5. version 011 NEW implementation report; and
6. version 012 helper-only atomic VERIFIED over exactly the declared 20 paths.

The `observed_paths` are immutable predecessor evidence, not mutation targets
for Prime Builder. The current proposal, future GO, report, and verdict enter
the terminal inventory only because all untracked numbered predecessors must be
committed atomically. No other path or operation is authorized.

## Requirement Sufficiency

**Existing requirements sufficient.** Version 008 accepted the technical
design and required only corrected operation-time authority. The new exact
owner-approved PAUTH supplies that authority without changing the doctor fix,
test design, or terminal-finalization requirements.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-07`
- `GOV-15`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-20260729-WI5688-NARROW-RECOVERY-PAUTH-APPROVAL` — owner approval of
  the exact WI-5688 source/test/bridge/governance-evidence recovery envelope.
- `DELIB-202667528` — reliability-fixes routing does not silently widen the
  standing PAUTH; the new authorization is explicit and separate.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — fast-lane work retains all
  ordinary authority, review, claim, evidence, and finalization gates.
- `DELIB-202666552` and `DELIB-202666673` — invalid terminal artifacts require
  governed recovery and real commit evidence.
- `bridge/gtkb-wi5688-terminal-finalization-recovery-007.md` and `-008.md` —
  non-executable GO correction and independent confirmation of the sole PAUTH
  blocker.

## Owner Decisions / Input

- `DELIB-20260729-WI5688-NARROW-RECOVERY-PAUTH-APPROVAL` authorizes the narrow
  PAUTH cited above while expressly preserving the fresh lifecycle and
  source/test byte freeze.

No new owner or source-design decision is required.

## Specification-Derived Verification Plan

| Governing requirement | Fresh evidence after GO | Required result |
| --- | --- | --- |
| Project authorization and operation-time enforcement | Exact claim plus schema-v3 start under the new PAUTH | `allowed=true` for the declared recovery envelope; exact PAUTH ID. |
| Source-of-truth freshness and hygiene | SHA-256, scoped status/numstat/diff, HEAD and empty-index checks | Both hashes and diff shapes remain exact; no foreign or staged path. |
| Doctor regression requirements | Focused doctor sweep test module plus live doctor invocation | Seven focused tests pass; live doctor warns rather than crashes; non-string/Unicode boundary remains covered. |
| Separate quality gates | Ruff check and Ruff format check on both Python targets; scoped `git diff --check` | All pass without changing candidate bytes. |
| Bridge/spec linkage | Candidate and live applicability/clause preflights | Zero missing specifications and zero blocking gaps. |
| Atomic terminal durability | Helper-only finalizer over exact 20-path inventory | One local commit, exact committed-path equality, real finalization evidence, no push. |

## Acceptance Criteria

1. Version 010 independently grants GO against this exact recovery plan.
2. Prime Builder obtains a fresh exact claim and schema-v3 start before
   refreshing implementation evidence.
3. Both implementation candidates remain byte-identical and all focused,
   live-doctor, Ruff, format, diff, hash, and hygiene checks pass.
4. Version 011 records current commands/results and the exact 20-path terminal
   cohort without staging or claiming a commit.
5. Version 012 is produced only by the governed atomic finalizer and commits
   exactly the declared cohort. Any denial or path mismatch fails closed.

## Pre-Filing Preflight Subsection

Both mandatory preflights ran against this completed candidate through their
`--content-file` surfaces before filing.

- Applicability preflight: exit `0`; `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; no missing parent or unclassified target paths;
  candidate packet hash
  `sha256:39aa099af3581e469c87173e8d5dc13f88d34ead0c93e2657e071c36c2bd8ba6`.
  Draft-only author-metadata warnings are expected; the governed revision
  helper inserts authoritative metadata before publication.
- Clause preflight: exit `0`; five clauses evaluated; three `must_apply`, two
  `may_apply`, zero must-apply evidence gaps, and zero blocking gaps.

The governed helper must re-run these gates after authoritative author metadata
is inserted. Any version race, claim loss, authorization denial, missing
specification, or blocking clause gap aborts filing.

## Risk And Rollback

The principal risks are another file-only terminal verdict, partial adoption
of the frozen implementation, and inclusion of foreign worktree bytes. Exact
hash binding, the no-byte-change PAUTH, fresh start evidence, a complete
predecessor inventory, and helper-only independent finalization constrain those
risks. This proposal changes no implementation byte; rollback is a later
append-only bridge disposition. History rewrite is forbidden.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
