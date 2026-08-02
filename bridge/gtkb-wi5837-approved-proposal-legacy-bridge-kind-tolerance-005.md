REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=default; thread_source=automation
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5837-approved-proposal-legacy-bridge-kind-tolerance
Version: 005
Responds to: bridge/gtkb-wi5837-approved-proposal-legacy-bridge-kind-tolerance-004.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5837

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight_legacy_proposal_kind.py"]
implementation_scope: approved_proposal_resolver_legacy_bridge_kind_tolerance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none; this proposal performs no KB mutation.

# WI-5837 Revised Implementation Proposal — Legacy Proposal-Kind Resolution

## Revision Claim

Version 004 correctly rejects version 003's claim that an unclaimed GO can be closed as stale. No implementation report exists, so this revision does not fabricate one. Fresh inspection on 2026-08-01 shows that `scripts/bridge_applicability_preflight.py` is tracked and byte-identical to HEAD (Git blob `c9de9bcab3f7d2d165d5379b94f6a4620a9b4927`, SHA-256 `5F16BADECCB1B5D49438C62C5DFD3AA1FF5E6AE092F1C424A454F035D9C0C4D9`) and still admits only the explicit `prime_proposal` and `implementation_proposal` markers. The dedicated legacy regression target does not exist. Therefore versions 002–004 contain approval and disposition evidence, but not implementation evidence.

The current latest status is NO-GO, so the former version 002 GO is historical rather than a current implementation-start state. This REVISED entry restores the exact bounded proposal to independent review. No protected target may be changed unless a new independent GO becomes current, this Prime Builder session acquires the exact work-intent claim, and a fresh schema-v3 implementation-start packet passes currentness, project authority, role, target, overlap, and clause gates.

## Findings Response

1. **No implementation report exists — accepted.** Current source bytes still implement the strict marker-only resolver, and the proposed new test module is absent. This entry is a proposal, not a report.
2. **No active claim is not an implementation result — accepted.** Claim absence is recorded only as current concurrency state. It is not completion evidence and does not extinguish approved work.
3. **NO-ACTION is not closure — accepted.** Version 003 remains append-only historical evidence of an invalid attempted disposition. WI-5837 remains open.

## Problem and Bounded Design

`_approved_proposal_for_report()` currently rejects a pre-convention proposal whose `bridge_kind` is absent even when a later independent GO names that exact earlier version. The protected-commit chain checker resolves the proposal structurally while still requiring the Prime implementation artifact to be labeled as an implementation report. On a legacy chain, those two gates can therefore leave no authorable report that both resolves its approved proposal and reaches finalization evaluation.

The implementation is confined to the two declared targets:

1. Add a legacy predicate beside `_approved_proposal_for_report()`. It may accept a candidate only when all of these are true: the marker is absent rather than conflicting; a later GO names the exact candidate as operative; declared target paths are non-empty; the candidate is Prime-authored NEW or REVISED; and report-only `Approved proposal:` / `Controlling GO:` markers are absent.
2. Preserve explicit-marker precedence. The legacy predicate runs only when strict marker resolution finds no candidate. A declared non-proposal marker is never tolerated. Existing same-thread, must-precede, matching-GO, and highest-version rules remain fail-closed.
3. Replace the generic unresolved-proposal sentence with a deterministic diagnostic naming each examined earlier version and its rejection reason.
4. Record the resolved proposal path and recognition mode (`explicit_marker` or `legacy_structural`) in the operation-time project-authorization evidence and rendered packet. If the current packet-hash schema already has durable consumers at implementation time, advance the schema instead of silently changing existing hash material.
5. Add the dedicated test module. Do not modify the protected-commit checker; exercise its chain resolution read-only to prove cross-gate agreement.

This proposal does not tolerate missing GO evidence, mismatched markers, report-shaped artifacts, unrelated versions, out-of-root paths, or finalization without the normal claim/start/verification gates.

## Current Authority and Coordination

- WI-5837 is open and is an active member of `PROJECT-GTKB-HARNESS-TEST-CORRECTIONS`.
- The project's list-free PAUTH is active, unexpired, and allows source, test, and test-addition mutations. The PAUTH does not replace the exact proposal, independent GO, fresh claim, schema-v3 start packet, target-path enforcement, implementation report, or independent VERIFIED gates.
- The source target is a shared governance surface. Preparation and review may proceed in parallel, but implementation must rerun exact target overlap/currentness checks and fail closed if another active claim owns the same bytes.
- The existing zero-byte `.git/index.lock` is foreign and out of scope. This work requires no Git mutation and must not remove, replace, or reinterpret that lock.
- TAFE/dispatcher activation or mutation is forbidden and out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; defines append-only bridge authority and supplies WI-5837 / TEST-11788.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — blocking; governs operation-time project authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking; requires complete proposal specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; requires verification derived from cited specifications.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; both targets, the numbered bridge artifact under `E:/GT-KB/bridge/`, and every live dependency are in-root under `E:/GT-KB`.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory; the repair restores agreement between two mechanical gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; recognition provenance must remain visible in durable packet evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; traceability binds proposal, GO, report, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; version 004 triggers this substantive revision rather than closure.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory; deterministic resolution replaces manual legacy-chain workarounds.

## Prior Deliberations

- `DELIB-202667731` — owner-approved list-free Harness Test Corrections whole-project PAUTH; it is the current project authority cited above.
- `DELIB-202667730` — Harness Test Corrections synthesis that carries this defect family.
- `DELIB-202667723` — relevant historical finalization evidence decision; it does not waive current GO/claim/start gates.
- Version 004 also searched `DELIB-20263237`, `DELIB-202667478`, and `DELIB-202667519` and found no owner disposition closing WI-5837 without implementation. This revision preserves that conclusion.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202667731` supplies active bounded project authority, while the exact implementation remains disabled until a fresh independent GO, claim, and schema-v3 start packet exist.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-FILE-BRIDGE-AUTHORITY-001`, WI-5837, and its spec-derived `TEST-11788` already define the legacy-resolution success and explicit-diagnostic obligations. No new formal requirement is invented by this revision.

## Specification-Derived Verification Plan

| Requirement | Test | Required observed behavior |
|---|---|---|
| `TEST-11788` / `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_legacy_first_version_resolves_as_approved_proposal` | A markerless Prime proposal with exact later GO and non-empty targets resolves and reaches finalization-phase PAUTH evaluation. |
| `TEST-11788` diagnostic obligation | `test_unresolved_diagnostic_names_each_examined_version` | Failure names every examined version and deterministic rejection reason. |
| Cross-gate agreement | `test_cross_gate_agreement_on_legacy_chain` | The same legacy fixture clears file-time proposal resolution and the protected-commit checker's structural proposal chain. |
| Fail-closed recognition | negative tests for missing GO, conflicting marker, missing targets, report-only headers, and non-proposal status | Each missing conjunct rejects the candidate; no marker mismatch is silently promoted. |
| Explicit-marker precedence | `test_marker_path_takes_precedence_over_legacy` | A qualifying explicit proposal wins over any markerless candidate. |
| Legacy revision ordering | `test_highest_legacy_version_wins` | The highest qualifying legacy NEW/REVISED candidate is selected. |
| Durable evidence | `test_packet_records_recognition_provenance` | Packet JSON, hash material, and markdown identify recognition mode and resolved path consistently. |
| Non-regression | existing `platform_tests/scripts/test_bridge_applicability_preflight.py` suite | Current explicit-marker, PAUTH-phase, linkage, and failure behavior remains green. |

## Acceptance Criteria

1. The declared source and new test target are the only modified protected paths.
2. The focused legacy test module and existing applicability-preflight suite pass with concise tracebacks.
3. Ruff lint and format checks pass for both changed Python files.
4. A real pre-convention chain resolves its exact GO-approved proposal and records `legacy_structural`; explicit-marker chains record `explicit_marker` without behavioral drift.
5. Every negative discriminator remains fail-closed and the unresolved diagnostic names the rejected version.
6. Cross-gate agreement is demonstrated without modifying `scripts/check_protected_commit_authorization.py`.
7. No bridge file, MemBase formal record, dispatcher/TAFE state, Git index, or foreign lock is mutated by implementation.
8. No hard-coded timer, retry, throttle, fan-out, or concurrency value is added; any new bound must come from the centralized configuration surface.

## Risk and Rollback

The material risk is false promotion of a legacy report. Conjunctive structural proof, explicit-marker precedence, per-signal negative tests, and visible recognition provenance bound that risk. Hash-material drift is fail-closed: advance the packet schema if current consumers make an in-place change incompatible. Rollback is the exact source hunk removal plus deletion of the new test module; no data migration or external action is involved.

## DISARM — Implementation

This file requests review only. It does not authorize protected-file mutation, implementation start, commit, deployment, release, TAFE/dispatcher activation, or finalization. Implementation starts only after a new independent GO is canonical and the implementing PB obtains the exact claim and fresh schema-v3 start packet.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
