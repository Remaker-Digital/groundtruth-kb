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


# WI-5665 Cursor Fallback Test Repair — Authorized Terminal Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5665-cursor-fallback-hardening-test-repair
Version: 009
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-008.md

Project Authorization: PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5665-FINALIZATION-20260729
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5665
target_paths: ["platform_tests/skills/test_verified_finalization_validation_hardening.py"]
terminal_finalization_paths: ["platform_tests/skills/test_verified_finalization_validation_hardening.py", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-001.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-002.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-003.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-004.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-005.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-006.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-007.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-008.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-009.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-010.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-011.md", "bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-012.md"]
implementation_scope: frozen-candidate-evidence-refresh-and-atomic-terminal-finalization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: test:

This revision performs no test-byte, source, configuration, MemBase,
dispatcher, index, Git-history, release, deployment, credential, or external-
system mutation. It requests a fresh independent GO for the exact recovery
lifecycle required by version 008 and the newly approved narrow PAUTH.

## Revision Claim

Version 008 independently found the implementation technically green and
blocked terminal verification only because the prior project authorization
excluded the bridge artifacts required by the atomic finalizer. The owner has
now approved
`PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5665-FINALIZATION-20260729`, which covers
only the frozen one-test candidate, bridge versions 001 through 012, necessary
governance evidence, and the local exact-cohort `git_commit`.

After a fresh GO, Prime Builder will acquire a new exact
`go_implementation` claim and schema-v3 implementation-start packet, prove the
candidate remains byte-identical, rerun the accepted verification surface, and
file version 011 as a fresh implementation report. Independent Loyal
Opposition may then issue version 012 only through the governed atomic
`VERIFIED` finalizer. No test or production behavior change is proposed.

## Findings Addressed

### F1 — P1 — Prior PAUTH denied the bridge cohort

**Resolved by owner authorization.** The active replacement authorization is
specific to WI-5665 and permits `test`, `bridge`, and `governance_evidence`
mutations for exactly the frozen test target and this numbered thread through
version 012. It explicitly permits the required local terminal `git_commit`
while retaining prohibitions on dispatcher mutation, external-system mutation,
credential lifecycle work, push, history rewrite, deployment, release, and
destructive cleanup.

The complete unavoidable terminal cohort is declared above. The finalizer may
not omit a predecessor, adopt another dirty path, or advance beyond version
012 under this proposal.

## Frozen Candidate Evidence

- Target: `platform_tests/skills/test_verified_finalization_validation_hardening.py`.
- HEAD blob: `5b628709a504c73e546a4753382ef46945d2f990`.
- Current candidate SHA-256:
  `3CB6C0C05598C09E32D4309957E391D14A4F3BA3124E5778165F769942DB708B`.
- Current diff relative to HEAD: exactly 30 insertions and 2 deletions in the
  one declared test path.
- Previously observed focused result: 22 passed with one pre-existing pytest
  configuration warning; Ruff check, Ruff format check, and scoped diff check
  passed.
- Version 008 independently reproduced the same hash, diff, tests, and static
  checks and reported no technical finding.

Any test-byte drift, new path, changed diff shape, nonempty index, missing
predecessor, or PAUTH denial is a stop condition and requires another revision.

## Scope Changes

The implementation behavior and one-test target are unchanged from versions
005 through 008. The only scope change is governance authority for an exact
append-only recovery sequence:

1. version 009 REVISED proposal;
2. version 010 independent GO;
3. fresh claim and schema-v3 implementation start for the one test target;
4. no byte mutation; candidate/hash and verification refresh;
5. version 011 NEW implementation report; and
6. version 012 independent atomic VERIFIED finalization over exactly the
   declared terminal cohort.

No source, adapter, registry, manifest, placeholder Cursor surface, MemBase,
dispatcher, release, deployment, push, or external-system work is in scope.

## Requirement Sufficiency

**Existing requirements sufficient.** Version 008 accepted the behavioral
implementation and test evidence. The owner-approved narrow finalization PAUTH
supplies the missing operation-time authority without changing the Cursor
fallback requirement or implementation design.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `SPEC-AUQ-POLICY-ENGINE-001`

## Prior Deliberations

- `DELIB-202667104` — Cursor's verify surface is intentionally absent and is
  governed by the declared fallback contract rather than a placeholder.
- `DELIB-202667193` and `DELIB-202667194` — bounded skill-rename recovery and
  exact-byte isolation.
- `DELIB-202667286` — terminal evidence must bind to a reproducible candidate.
- `DELIB-20260729-WI5665-NARROW-FINALIZATION-PAUTH-APPROVAL` — owner approval
  of the exact WI-5665 test/bridge/finalizer envelope.
- `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-007.md` and
  `-008.md` — frozen implementation report and independent technical-positive,
  authorization-negative terminal review.
- `bridge/gtkb-wi5662-canonical-doc-reference-recovery-015.md` and `-016.md` —
  preserve this candidate as foreign to WI-5662 until terminal finalization.

## Owner Decisions / Input

- `DELIB-20260729-WI5665-NARROW-FINALIZATION-PAUTH-APPROVAL` authorizes the
  narrow PAUTH named above and preserves every fresh proposal, review, claim,
  implementation-start, report, and atomic-verification gate.
- Existing owner decisions preserve the intentional Cursor fallback and forbid
  fabricated placeholder surfaces.

No new owner decision is required.

## Specification-Derived Verification Plan

| Governing requirement | Fresh evidence after GO | Required result |
| --- | --- | --- |
| Project authorization and operation-time enforcement | Exact claim plus schema-v3 start for the one test target under the new PAUTH | `allowed=true`; authorization ID and target are exact. |
| Cursor fallback and cross-harness parity | Full `test_verified_finalization_validation_hardening.py` module | 22 tests pass; Claude/Codex helper behavior and all five Cursor fallback/absence cases remain intact. |
| Worktree hygiene and candidate binding | SHA-256, scoped status/numstat/diff, empty-index check | Hash remains `3CB6...708B`; exactly one 30/2 test diff; no staged or foreign path. |
| Separate lint/format gates | Ruff check and Ruff format check on the target | Both pass without changing the candidate. |
| Bridge/spec linkage | Candidate applicability and clause preflights, then live checks | Zero missing specifications and zero blocking gaps. |
| Atomic VERIFIED gate | Independent finalizer over the exact test plus versions 001–012 | One local commit is created; committed-path equality passes; no file-only VERIFIED and no push. |

## Acceptance Criteria

1. Version 010 independently grants GO against this exact recovery plan.
2. Prime Builder obtains a fresh exact claim and schema-v3 start packet before
   refreshing implementation evidence.
3. The candidate remains byte-identical and all focused/static checks pass.
4. Version 011 reports fresh commands, observed results, hashes, and the exact
   terminal cohort without claiming a commit.
5. Independent Loyal Opposition uses the governed atomic finalizer for version
   012 and commits only the declared cohort. Any PAUTH denial fails closed.

## Pre-Filing Preflight Subsection

Both mandatory preflights ran against this completed candidate through their
`--content-file` surfaces before filing.

- Applicability preflight: exit `0`; `preflight_passed: true`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; no missing parent or unclassified target paths;
  candidate packet hash
  `sha256:ce316ec7adb2f84229ebc118778cb1b209b9c6457a087895c5d560377607eee3`.
  Draft-only author-metadata warnings are expected; the governed revision
  helper inserts authoritative metadata before publication.
- Clause preflight: exit `0`; five clauses evaluated; three `must_apply`, two
  `may_apply`, zero must-apply evidence gaps, and zero blocking gaps.

The governed helper must re-run these gates after authoritative author metadata
is inserted. Any version race, claim loss, authorization denial, missing
specification, or blocking clause gap aborts filing.

## Risk And Rollback

The principal risk is laundering another work item's bytes or creating a file-
only terminal verdict. Exact hash binding, a one-path start packet, complete
predecessor inclusion, fresh independent review, and the narrow PAUTH constrain
that risk. This proposal makes no implementation change; rollback is a later
append-only bridge disposition. Before terminal commit, the frozen candidate
may be reverted only through separately authorized work. History rewrite is
forbidden.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
