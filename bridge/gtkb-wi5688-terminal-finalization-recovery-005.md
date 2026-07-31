REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5688-terminal-finalization-recovery
Version: 005
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5688-terminal-finalization-recovery-004.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5688
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py", "bridge/gtkb-wi5688-doctor-crash-fastlane-001.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-002.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-003.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-004.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-005.md", "bridge/gtkb-wi5688-doctor-crash-fastlane-006.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-007.md"]
observed_paths: ["bridge/gtkb-wi5688-terminal-finalization-recovery-001.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-002.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-003.md", "bridge/gtkb-wi5688-terminal-finalization-recovery-004.md"]
implementation_scope: commit_finalization_recovery
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal changes no source or test byte and performs no MemBase, dispatcher, registry, external-system, or push operation.

# WI-5688 normal-lifecycle atomic finalization recovery proposal

## Revision Disposition

Version 004 independently accepted the technical evidence, root-cause determination, frozen hashes, verification results, and recovery cohort from version 003. Its sole blocker is lifecycle authority: this recovery chain has no controlling GO. This version is the required normal proposal. It requests independent GO before one GO-linked report and the governed atomic finalizer make the already-reviewed implementation durable.

No implementation byte may change. The listed source/test and original fastlane paths are targets only because the eventual finalizer must commit the existing reviewed bytes and complete original chain atomically. The sole future Prime Builder artifact is version 007 of this recovery chain.

## Requirement Sufficiency

Existing requirements sufficient. Version 004 identifies only the missing proposal/GO/report sequence. The reviewed implementation, schema-v3 start packet, frozen hashes, focused tests, Ruff evidence, and technical LO findings remain sufficient. No new owner decision, requirement, or source implementation is needed.

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

- `DELIB-20265449` — atomic-finalization blocker precedent.
- `DELIB-20265754` — VERIFIED finalization/index-lock retry precedent.
- `DELIB-202666552` — failed VERIFIED finalization repair precedent.
- `DELIB-202666673` — invalid terminal verdict reissue precedent.
- `DELIB-202667347` and `DELIB-202667348` — corrected malformed-verdict-chain precedents.
- Version 003 — corrected frozen recovery report.
- Version 004 — controlling NO-GO requiring this proposal/GO/report sequence.

## Frozen Implementation Evidence

- Doctor source SHA-256: `E20D1E7D5E15359A294527767B169F43750F77B0A7CFF7E791F782E0AB4960D7`.
- Focused test SHA-256: `3D7835AFAC9690BB6CCF68496FFE72173996FE06665A05D36B9E1DF1E85A7D61`.
- Original schema-v3 implementation-start packet hash: `sha256:912911fb0893e9371bbc1ccda8154db639a485e9ef51ad1b0949719d6a10b9e6`.
- Original controlling proposal/GO/report: fastlane v003/v004/v005.
- Quarantined false terminal: fastlane v006, hand-authored outside the governed finalizer.
- Accepted technical result: 7 focused tests pass; Ruff check and format pass; live doctor returns WARN rather than crashing.

Both hashes were freshly rechecked before drafting. The two implementation paths remain modified, original fastlane v001-v006 and recovery v001-v004 remain untracked, HEAD remains `e9052e9c4ebc7d2bd1026bf9b85dc57e151b86a7`, and that commit intersects none of these paths.

## Exact Authorized Output And Stop Conditions

After an independent version-006 GO, Prime Builder may acquire a fresh exact claim and operation-time packet, then file only `bridge/gtkb-wi5688-terminal-finalization-recovery-007.md` without changing any existing byte.

The report must:

1. respond to and name version 006 as `Controlling GO`;
2. recheck both frozen hashes and the exact current path states;
3. re-run the 7 focused tests, Ruff check, and Ruff format-check;
4. re-prove that the false terminal bypassed the helper while the helper itself fails closed;
5. make the exact finalization cohort visible;
6. preserve F4/F5 as separately governed sibling backlog write requests rather than widening scope; and
7. request independent terminal review through only the governed atomic finalizer.

Any hash drift, changed test/quality result, foreign staged path, target deletion, or later HEAD intersection with only part of the cohort is a hard stop requiring another proposal revision.

## Atomic Finalization Boundary

The terminal finalizer may include exactly:

1. `groundtruth-kb/src/groundtruth_kb/project/doctor.py`;
2. `platform_tests/scripts/test_doctor_skill_rename_sweep.py`;
3. fastlane versions 001 through 006;
4. every versioned file of this recovery chain that exists at finalization time, expected versions 001 through 008 on the present round; and
5. no other path.

This review-round-invariant definition includes the proposal, independent GO, GO-linked report, and generated verdict without trying to pre-author or predict their bytes. The intended local subject is `fix(doctor): finalize WI-5688 Windows-safe skill-rename sweep boundary`. No push is authorized.

## Specification-Derived Verification Plan

| Specification | Required verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | v005 proposal → independent v006 GO → claim/start → v007 report → helper-generated verdict | Strict GO-linked lifecycle and atomic terminal publication. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Full fastlane/recovery chain and v006 literal/helper comparison | False terminal remains accurately attributed to a hand-authored bypass. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Current standing PAUTH and exact target inventory | Only frozen durability/recovery scope is authorized. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Fresh schema-v3 packet after GO | Exact frozen target set allowed; no byte-changing expansion. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight | PAUTH/project/WI linkage complete. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight | No missing required/advisory specification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 7 focused tests plus complete per-spec evidence mapping | Green accepted technical evidence before finalization. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Exact hashes, scoped status, HEAD intersection | Frozen bytes and cohort remain current. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact complete-chain finalization inventory and index check | No foreign path staged or committed. |
| `GOV-07` | No-fix-during-test audit | Verification changes no implementation/test byte. |
| `GOV-15` | Mutation-scope audit | No bulk, MemBase, or unrelated mutation. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Root-boundary inspection | Every live target is inside `E:\GT-KB`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Governed recovery report and terminal evidence | Root cause and recovery remain durable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | v004 NO-GO → v005 proposal → v006 GO → v007 report | Every action follows its governing trigger. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Deferred sibling-work disposition | F4/F5 remain visible without unauthorized implementation. |

## Multi-Path Visibility And Cross-Harness Disposition

The numbered atomic-finalization boundary is the exact multi-path inventory artifact. Version 004 is the independent review packet; version 007 must refresh both before finalization. Cross-harness adapter work is not applicable: no harness skill, adapter, prompt, hook, or provider-specific surface is changed.

## Implementation Procedure After GO

1. Confirm independent version-006 GO and acquire a fresh claim.
2. Run `implementation_authorization.py begin --no-write`, then normal `begin`, against the exact declared targets.
3. Re-run frozen-hash, path-state, HEAD-intersection, focused-test, Ruff, applicability, and clause checks.
4. File version 007 through the governed writer without editing any existing target.
5. LO invokes the governed atomic finalizer over only the exact cohort. If commit creation, committed-path equality, or cleanup fails, no file-only terminal state is valid.

## Acceptance Criteria

- Independent GO precedes the recovery report.
- No source/test byte changes after the accepted hashes.
- The full original and recovery chains are included atomically with source/test and nothing else.
- Terminal VERIFIED contains actual helper-produced finalization evidence and the resulting commit is verified path-exact and clean.
- F4/F5 remain sibling candidates and do not block or widen this recovery.

## Risk And Rollback

The principal risk is repeating the file-only terminal incident or committing foreign dirt. Frozen hashes, complete-chain path inventory, scoped operation-time authorization, and helper-enforced atomicity fail closed. Before commit, rollback removes only a pending candidate; after a successful exact commit, correction is append-only and no history rewrite is authorized.

## Pre-Filing Preflight

Applicability preflight against this candidate passed with
`preflight_passed: true`, no missing required or advisory specifications, no
unclassified targets, and no blocking errors. Mandatory clause preflight also
passed: five clauses evaluated, four `must_apply`, one `may_apply`, zero
must-apply evidence gaps, and zero blocking gaps.

## Owner Action Required

None. Independent LO review is the next governed action.

## Recommended Commit Type

`fix:` — atomic durability recovery for the already-reviewed doctor fix.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
