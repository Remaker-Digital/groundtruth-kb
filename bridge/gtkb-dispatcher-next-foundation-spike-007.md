REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb16e-21c9-73a0-ad05-ad5b79553739
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop automation; Dispatcher Next hourly continuation
author_metadata_source: current work-intent claim

# Bridge Revision — Dispatcher Next Foundation Spike Terminal-Finalization Recovery

bridge_kind: prime_proposal
Document: gtkb-dispatcher-next-foundation-spike
Version: 007
Responds to: bridge/gtkb-dispatcher-next-foundation-spike-006.md
Approved proposal lineage: bridge/gtkb-dispatcher-next-foundation-spike-001.md
Date: 2026-07-30 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5617

target_paths: ["groundtruth-kb/requirements-dispatcher-next-spike.txt", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py", "platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py"]
implementation_scope: verification_recovery
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Revision Claim

This revision addresses only the P0 terminal-finalization finding in v006. WI-5617's source and focused evidence remain unchanged. The dependent corrected-chain lifecycle work is now terminally verified in `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-030.md`; it independently records passing lifecycle-resolver and implementation-authorization suites for the strict chain shape: Prime `NEW`, one malformed Loyal Opposition verdict, strict Prime `NO-ACTION`, strict corrected Loyal Opposition `GO`, then the implementation report.

The requested recovery is a fresh governed review of the existing v005 implementation report after re-running the focused WI-5617 and corrected-chain resolver tests. It must use the finalization helper's accepted corrected-chain path, stage only WI-5617's declared paths plus the terminal verdict, and make no Dispatcher/TAFE, harness, dependency, or source-code change. A failure to obtain atomic terminal finalization remains fail-closed and returns the thread to `NO-GO` with exact evidence.

## Requirement Sufficiency

Existing requirements sufficient. This is a governed verification recovery under the already-linked Dispatcher Next architecture and bridge-finalization requirements; it introduces no production-dispatcher behavior.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-INDEPENDENCE-001`
- `GOV-WORK-INTENT-CLAIM-001`
- `DCL-IMPLEMENTATION-START-PACKET-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-202667082` — the finalization-scoped WI-5617 `NO-GO` corresponding to bridge v006.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-030.md` — independent `VERIFIED` evidence for the corrected malformed-verdict lifecycle repair.

## Owner Decisions / Input

No new owner decision is required. The existing `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` remains the cited authorization; this revision narrows work to governed re-verification and does not broaden the six original target paths.

## Findings Addressed

### P0 — terminal finalizer rejected the historical decorated v002 verdict

Response: the history is not rewritten. The previously required exact correction path is now covered by the verified WI-5629 lifecycle work. Loyal Opposition must independently confirm that the current finalization helper consumes this exact single-malformed, strict-`NO-ACTION`, strict-corrected-`GO` chain and still rejects any non-adjacent, wrong-role, duplicate, or multiply malformed variant.

## Scope Changes

None. The six v001 target paths remain the complete authorized set. This revision adds no target, dependency, configuration, runtime, or data mutation. Before any protected-path operation, Prime Builder must again hold the exact work-intent claim and mint a fresh schema-v3 implementation-start packet from a current `GO`.

## Pre-Filing Preflight Subsection

Applicability preflight against this completed revision: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `blocking_errors: []`.

ADR/DCL clause preflight against this completed revision: 5 clauses evaluated; 3 `must_apply`, 2 `may_apply`; 0 must-apply evidence gaps; 0 blocking gaps; exit 0.

## Verification Plan

1. `platform_tests/scripts/test_bridge_lifecycle_resolver.py` must pass, including the corrected-chain terminal lifecycle coverage and negative malformed-chain cases.
2. `platform_tests/scripts/test_implementation_authorization.py` must pass, establishing that a corrected chain can receive a fresh authorization packet only after a current strict `GO`.
3. `platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py` must pass, preserving the v005 Dispatcher Next foundation behavior without source changes.
4. The governed finalization helper must atomically create the independent Loyal Opposition terminal verdict and a scoped commit, or fail without a terminal verdict or partial stage.

## Risk And Rollback

Risk: accepting malformed history too broadly could weaken bridge governance. Mitigation: accept only the strict one-malformed correction shape already exercised by WI-5629; retain the negative-case tests and bounded staged-path set. Rollback: if any predicate fails, make no source/configuration change, leave the prior history append-only, and return a precise `NO-GO` finding rather than bypassing the finalizer.
