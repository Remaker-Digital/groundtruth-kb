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

bridge_kind: prime_proposal
Document: gtkb-wi5665-cursor-fallback-hardening-test-repair
Version: 005
Responds to: bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-004.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5665
target_paths: ["platform_tests/skills/test_verified_finalization_validation_hardening.py"]
implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation and authorizes no test mutation before a fresh GO, go_implementation claim, and schema-v3 start packet.

# WI-5665 Cursor fallback hardening — one-line coverage-name correction

## Revision Disposition

Version 004 independently accepted the complete Cursor fallback repair and
found one blocking defect: a surviving test name says `three` helper copies
while the parametrization correctly covers the two real helpers.

Version 004 described the fix as needing no re-proposal, but the live
work-intent machinery now resolves this thread's latest `NO-GO` to a `draft`
claim. `implementation_authorization.py begin --no-write` therefore cannot
produce a valid new schema-v3 implementation-start packet for a protected test
mutation. The earlier implementation claim and packet are expired. This narrow
proposal is the least-risk append-only route to the fresh GO the mandatory
mutation precondition requires.

## Claim

After an independent GO, change exactly one function name in the already
declared target:

```text
test_three_helper_copies_share_validation_behavior
→ test_helper_copies_share_validation_behavior
```

No assertion, parameter, fixture, helper mapping, Cursor fallback case, source,
adapter, registry, manifest, or other path changes. The accepted 29-insertion,
1-deletion Cursor repair remains frozen input to this one-line correction.

## Requirement Sufficiency

Existing requirements are sufficient. Version 004 precisely specifies the
one-line correction and accepts every other implementation/evidence claim. No
new requirement or owner decision is needed; only a fresh operational GO/claim
/start sequence is required by the current live status.

## Frozen Pre-Correction Candidate

- Target:
  `platform_tests/skills/test_verified_finalization_validation_hardening.py`.
- Clean HEAD preimage blob used by the accepted implementation:
  `5b628709a504c73e546a4753382ef46945d2f990`.
- Current candidate SHA-256:
  `2CE48CC22BB8E297000529F1DF3EA5149A59FDCE4EADBBE78A796D0F6AE5233E`.
- Current diff: 29 insertions, 1 deletion, one test file.
- Current module result: 22 passed; Ruff check/format and diff-check pass.
- Independently accepted contract: five explicit Cursor cases verify the
  registry's fallback status, exact declared surface, nonempty rationale, and
  absence of both Cursor skill/helper; real helper behavior covers Claude and
  Codex only.

Any candidate drift beyond the named function rename is a stop condition.

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

- `DELIB-202666552` — finalization-integrity recovery precedent.
- `DELIB-202667286` — verification evidence must bind to a reproducible final
  candidate.
- `DELIB-20260724-WI5661-PROCESS-AUTHORIZATION` — bounded skill-rename recovery
  with independent review retained.
- `DELIB-202667193` and `DELIB-202667194` — bounded sweep authorization and
  exact-byte isolation.
- `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-004.md` — direct
  independent NO-GO accepting all implementation evidence except the
  overclaiming test name.

## Owner Decisions / Input

The existing owner decisions preserve the Cursor fallback outcome and prohibit
fabricated placeholder surfaces. No new owner input is needed. This proposal
changes only how the real two-helper parity test describes its coverage.

## Exact Implementation And Verification Plan

1. Require an independent GO on this proposal.
2. Reacquire an exact `go_implementation` claim and run
   `implementation_authorization.py begin --no-write`, then normal `begin`.
   Require a valid schema-v3 packet with `allowed=true` for the one `test`
   target; any empty/invalid response stops work.
3. Rename only the function named above with no body/parameter change.
4. Run the full hardening module, Ruff check, Ruff format-check, scoped diff
   check, candidate hash/diff review, and both bridge preflights.
5. File a GO-linked REVISED implementation report using canonical
   `## Commands Executed` and `## Spec-to-Test Mapping` headings.
6. Independent LO may verify only through the governed atomic finalizer over
   the one test target and complete untracked bridge chain. No push.

Expected post-correction diff relative to HEAD: 30 insertions and 2 deletions
in the same single target, consisting of the accepted Cursor repair plus one
function-name replacement.

## Spec-to-Test Mapping

| Specification | Required evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | v005 proposal → fresh GO → claim/start → report/verdict | No protected mutation before current GO. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Fresh schema-v3 packet for exact target | Active PAUTH includes WI-5665/test and forbids push. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Fresh evaluator decision | `allowed=true`; exact one-path classification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability/header inspection | PAUTH, project, WI, target complete. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight | Zero missing specifications. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full module plus canonical report mapping | 22 tests pass; no misleading node name. |
| `GOV-WORK-TREE-HYGIENE-001` | Frozen hash, exact 30/2 diff, one-path status, empty index | No foreign hunk or path. |
| `GOV-RELIABILITY-FAST-LANE-001` | One-line test-only correction | No production behavior change. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Real-helper parametrization and Cursor fallback cases | Claude/Codex behavior and Cursor absence contract remain exact. |
| `ADR-CROSS-HARNESS-PARITY-001` | Collection node IDs plus five Cursor cases | Name accurately describes two real helpers without hard-coded count. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `HELPER_COPIES`, parametrized nodes, fallback assertions | No coverage overclaim or placeholder. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | GO-linked report with exact hashes/results | Correction is durably reviewable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | v004 NO-GO → v005 proposal → GO/start/report | Each action follows its trigger. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Accepted evidence plus explicit name/commit-type disclosure | No silent signal change. |
| `GOV-STANDING-BACKLOG-001` | Scope audit | No backlog/MemBase mutation or whole-WI closure claim. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path inspection | Target remains inside `E:\GT-KB\platform_tests`. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner-input audit | No new decision inferred or requested. |

## Acceptance Criteria

- Function name is exactly `test_helper_copies_share_validation_behavior` and
  does not hard-code an inaccurate helper count.
- The function body and parametrization remain unchanged and cover exactly
  Claude and Codex real helpers.
- Five Cursor fallback/absence cases and `.cursor` path parsing coverage remain
  intact.
- Full module collects 22 and passes all 22; Ruff/format/diff checks pass.
- Final report explicitly discloses the coverage-description correction and
  that `test:` replaces version 001's incorrect `feat` recommendation.
- Exactly one approved test path is committed through independent atomic
  finalization; no foreign path or push.

## Risk And Rollback

The risk is either leaving a misleading green parity name or bypassing current
GO/start gates for a seemingly trivial edit. The exact one-line scope, fresh
authorization, full module, and hash/diff freeze address both. Rollback is a
separately governed revert of the eventual single test-file commit.

## Pre-Filing Preflight

Applicability preflight against the completed candidate passed:

- packet hash:
  `sha256:7d1ba62db1ea96c7d788235d488ae449076aee274030a2fd690433f8dd7422b6`;
- `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- `warnings.unclassified_target_paths: []`;
- `blocking_errors: []`.

Mandatory clause preflight also passed: five clauses evaluated, four
`must_apply`, one `may_apply`, zero evidence gaps in must-apply clauses, zero
blocking gaps, exit zero.

## Recommended Commit Type

`test:` — version 001's `feat` was incorrect because all changed bytes are test
coverage; version 003 corrected the type, and this proposal makes the reason
explicit.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
