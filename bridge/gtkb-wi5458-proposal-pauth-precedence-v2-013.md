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

# WI-5458 Proposal PAUTH Precedence V2 — Partial Implementation Report Correction

bridge_kind: implementation_report
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 013
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-012.md
Approved proposal: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md
Originating GO: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-008.md
Prior implementation report: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-011.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458
target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py","groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py","platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Claim

Version 012 identified three blockers. This revision closes the two blockers
that are executable inside the originating GO's exact three-path packet: F2's
stale post-preflight decision time and F3's missing explicit-selector
restrictive coverage matrix. It does not claim terminal readiness: F1 remains
open because the finalizer and its tests are outside this packet and require a
separately governed correction.

The implementation-start helper issued schema-v3 authority at
`2026-07-29T20:24:32Z` with state `resumable_report_no_go`, tracing report v011
and remediated NO-GO v012 to GO v008. Operation-time evaluation selected the
active implementation PAUTH named above and allowed exactly the three declared
targets. No fourth source/test/configuration path was touched.

No staging, commit, push, dispatcher activation, MemBase mutation, release,
deployment, credential operation, external-system mutation, history rewrite,
or destructive cleanup occurred.

## Requirement Sufficiency

**Existing requirements sufficient.** F2 and F3 are direct enforcement and
coverage corrections under the already-linked PAUTH envelope, restrictive
membership, and operation-time specifications. F1 is an implementation and
workflow-authority defect under those same requirements, not a missing
requirement; it must be handled through a separate exact-target proposal and
authorization before this thread can become terminal.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`

## Prior Deliberations

- `DELIB-20266083` records the owner-selected restrictive semantics for
  `included_work_item_ids`; the explicit-selector matrix now covers every
  outcome required by that decision.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded WI-5458 repair while retaining exact claims, packets, independent
  review, and terminal gates.
- `DELIB-20260729-WI5458-V2-OLD-CHAIN-RETIREMENT` identifies this V2 chain as
  the executable continuation.
- Versions 007, 008, 011, and 012 remain the approved proposal, originating
  GO, prior report, and controlling NO-GO.

## Owner Decisions / Input

No new owner decision is required for F2 or F3. They are exact corrections
required by the independent v012 verdict and are covered by the active
WI-5458 implementation PAUTH and schema-v3 resumption packet.

No owner decision is asserted for F1. Prime Builder must first route the
finalizer/source/test correction through a separate governed proposal and
obtain exact operation-time authority; this revision cannot widen its own
packet or convert the inoperable focused-finalization PAUTH into implementation
authority.

## Findings Addressed

### F1 (P0) — The finalization carrier is sequenced incompatibly with the only finalizer

**Status: OPEN; not claimed corrected.** The current finalizer's order and lack
of PAUTH/claim enforcement are outside the three declared targets. No finalizer
file or test was changed. Terminal VERIFIED, staging, and commit remain
prohibited. The required next recovery is a separate exact-target proposal
that makes the independent-verdict/commit order executable and enforces the
then-current PAUTH and claim at finalization time.

### F2 (P1) — Candidate preflights do not revalidate PAUTH at operation time

**Status: CLOSED in the candidate implementation.**

- `proposal_filing.py` now derives `revalidation_time` from a fresh
  `datetime.now(UTC)` after candidate preflights and passes it to the second
  `_resolve_project_state` call.
- `_decision_invalidation_fingerprint` compares stable authorization inputs
  while excluding only the top-level and nested evaluator decision-time
  fields. It does not suppress expiry/currentness, normalized envelope,
  candidate cohort, owner-decision, target, operation, project, WI, spec, or
  bridge-preimage changes.
- `test_file_implementation_proposal_denies_expiry_during_candidate_preflight`
  deterministically advances the clock across candidate preflights. A PAUTH
  that is current initially and expired at revalidation fails
  `best_rank_cohort_stale`; writer calls remain empty and no bridge file is
  created.

### F3 (P1) — Explicit-selector restrictive coverage is not tested as promised

**Status: CLOSED in the candidate implementation.**

The new parameterized
`test_file_implementation_proposal_explicit_selector_restrictive_work_item_coverage`
passes `--project-authorization` for all five required outcomes:

| Explicit-selector case | Expected result | Observed assertion |
| --- | --- | --- |
| listed WI / nonmember | allow | selected PAUTH and allowed decision identity |
| unlisted WI / member | deny | `no_current_covering_authorization` |
| empty included list / member | allow | membership fallback with selected PAUTH |
| empty included list / nonmember | deny | `no_current_covering_authorization` |
| exclusion overrides an otherwise allowed WI | deny | `work_item_excluded` |

Every case asserts `selector_mode=explicit`, the requested PAUTH identity, and
a deterministic decision ID. Every denial asserts zero writer calls and zero
candidate-preflight calls.

## Scope And Current Candidate Identity

The three-path packet remains unchanged. Only the first and third paths gained
F2/F3 corrections; `cli_bridge_propose.py` retains its v011 bytes.

| Path | SHA-256 | Git blob | Current total diff vs HEAD |
| --- | --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` | `0F833B14091A869883587B1C4E010C36823841E22441154FB385F2DD8FE4F45A` | `017b0e8816680380aa914e5d7135fb81f81a7d1a` | 762 insertions / 101 deletions |
| `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` | `F0B04D71A9A79F26CD352CA60C709471DBF70A16DE04C38A5EAC7D8B237F7907` | `6b414ef1fe9a2be5933c87f4f2636180c783e50f` | 28 insertions / 1 deletion |
| `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` | `3B1ED9F7A85E7209E26355C6B0A81F7B2A8E182CFA4EDED4B643AD8ADBA8BCCA` | `4871bcd661c1a8a049c4f8d9ad24a6ad005fb010` | 575 insertions / 12 deletions |

Aggregate current diff: 1,365 insertions and 114 deletions across exactly the
same three paths. HEAD remains
`e9052e9c4ebc7d2bd1026bf9b85dc57e151b86a7`.

Six unrelated session-role files are staged in the shared real index. They are
foreign to WI-5458 and were not reset, unstaged, edited, staged, or committed.
This revision requests review only and does not attempt finalization.

## Specification-Derived Verification

| Governing requirement | Executed evidence | Result |
| --- | --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | deterministic expiry-during-preflight fixture plus the canonical 15-test operation-time suite | fresh post-preflight time denies expired authority; PASS |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` / `DELIB-20266083` | five-case automatic matrix retained and new five-case explicit-selector matrix | all allow/deny outcomes and exclusion precedence covered; PASS |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | platform proposal-filing suite and canonical evaluator suite | normalized envelope/currentness behavior remains green; PASS |
| bridge proposal, project-linkage, and cross-harness requirements | platform and package bridge-propose suites | generated content/result parity remains green; PASS |
| `GOV-WORK-TREE-HYGIENE-001` | exact target status/hashes/blobs/numstat, Ruff lint/format, and scoped diff check | three-target candidate isolated; PASS |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | no staging/commit and explicit F1 hold | terminal handling remains blocked; PASS for this partial report |

## Commands Run And Observed Results

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\test_cli_bridge_propose.py groundtruth-kb\tests\test_cli_bridge_propose.py groundtruth-kb\tests\test_project_authorization_operation_time_enforcement.py -q --tb=short`
  - `83 passed, 1 warning in 40.98s`.
  - Warning: pre-existing unknown `asyncio_mode` pytest configuration option.
- `groundtruth-kb\.venv\Scripts\ruff.exe check <three targets>`
  - `All checks passed!`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check <three targets>`
  - `3 files already formatted`.
- `git diff --check -- <three targets>`
  - exit 0, no findings.
- exact `git status`, `git diff --numstat`, SHA-256, Git-blob, HEAD, claim,
  and implementation-start packet inspections produced the identities above.

## Acceptance Criteria Status

- [x] F2 uses a fresh post-preflight UTC decision time.
- [x] Expiry during candidate preflights denies before writer publication with
  zero writer side effects.
- [x] F3 covers all five restrictive outcomes through the explicit selector,
  including decision identity and zero preflight/writer effects for denials.
- [x] All 83 focused/compatibility/evaluator tests and quality gates pass.
- [x] No unauthorized target, staging, commit, dispatcher, MemBase, release,
  deployment, or external mutation occurred.
- [ ] F1's executable and enforced finalization lifecycle remains unresolved.
- [ ] Independent terminal VERIFIED and atomic finalization remain prohibited.

## Scope Changes

No target-path expansion. The correction changes implementation details inside
the already-approved first target and adds regression coverage inside the
already-approved third target. The second target is unchanged from v011.

## Pre-Filing Preflight Subsection

Both mandatory candidate gates ran against this completed draft through their
`--content-file` surfaces before filing.

- Applicability preflight: exit 0; `preflight_passed: true`;
  pre-evidence `packet_hash: sha256:0cd6c2cc5cdce8fbea8be03e0adf6fd3b84ddad77564d823f0d16e0d1035af3e`;
  `missing_required_specs: []`; `missing_advisory_specs: []`;
  `blocking_errors: []`; `warnings.missing_parent_dirs: []`;
  `warnings.unclassified_target_paths: []`. The six author-metadata warnings
  are expected on the non-dispatchable draft; the governed helper inserts the
  authoritative author envelope during publication.
- Clause preflight: exit 0; five clauses evaluated; three `must_apply`, two
  `may_apply`, zero must-apply evidence gaps, and zero blocking gaps.

The governed revision helper must re-run these gates after author metadata is
inserted and fail closed on any missing specification or blocking clause gap.

## Risk And Rollback

The F2 risk is accidentally treating the expected clock change as authority
drift. The stable fingerprint excludes only evaluation-time fields while the
second resolver independently enforces expiry and every other authorization
input from fresh state. The deterministic regression proves an expiring PAUTH
is denied before publication.

The F3 risk is a false-green automatic-only matrix; every new case now passes
the explicit selector and asserts its decision identity. Denials prove no
writer or candidate-preflight side effect.

If independent review finds an F2/F3 defect, leave all targets unstaged and
correct only the three authorized paths under fresh resumption authority. Do
not revert or manipulate foreign paths. F1 has no rollback because it was not
implemented. No terminal finalization may occur from this revision.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
