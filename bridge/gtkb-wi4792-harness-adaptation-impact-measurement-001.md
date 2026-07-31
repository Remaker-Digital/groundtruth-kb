NEW

# WI-4792 - Harness Adaptation Impact Measurement

bridge_kind: prime_proposal
Document: gtkb-wi4792-harness-adaptation-impact-measurement
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T01:31:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-WI4792-BATCH-C-20260705
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4792

target_paths: ["scripts/benchmarks/harness_quality_manifest.py", "scripts/benchmarks/benchmark_dispatch_envelope.py", "scripts/benchmarks/harness_quality_runner.py", "scripts/benchmarks/harness_quality_scoring.py", "scripts/benchmarks/harness_quality_telemetry.py", "scripts/benchmarks/harness_quality_reporting.py", "scripts/benchmarks/harness_adaptation_impact.py", "scripts/cursor_harness.py", "scripts/verify_cursor_dispatch.py", "platform_tests/scripts/test_harness_quality_runner.py", "platform_tests/scripts/test_harness_quality_scoring.py", "platform_tests/scripts/test_harness_quality_telemetry.py", "platform_tests/scripts/test_harness_quality_reporting.py", "platform_tests/scripts/test_harness_adaptation_impact.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/scripts/test_verify_cursor_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4792 adds controlled measurement for harness-specific adaptations: prompt wording, skill-route language, shim behavior, or similar harness-local changes must be versioned and measured against seeded-flaw fixtures so quality changes can be attributed to the adaptation rather than to live-work noise. The immediate first consumer is Cursor/E, whose prerequisite WI-4778 readiness work is resolved but whose current registry projection is still not dispatch-receivable. Therefore this proposal keeps WI-4792 evidence fixture-based and non-mutating; it does not require or authorize a live Cursor dispatch attempt.

The implementation should introduce a compact adaptation-version identity, likely derived from explicit adaptation metadata plus stable fingerprints of the relevant prompt/skill/shim inputs. Benchmark evidence records should be able to carry a baseline adaptation version and a candidate adaptation version, then produce before/after quality deltas using the seeded-flaw fixture corpus and existing deterministic/adjudicated scoring primitives. Cursor/E should be the first measured target by covering the `scripts/cursor_harness.py` bridge-review/verification skill-route behavior and readiness evidence without changing durable role assignments, enabling dispatch, or touching credentials.

This proposal is sequenced after WI-4791 in the project plan, but it can be reviewed independently because it does not depend on production dispatch enforcement. Its output is an advisory, traceable KPI-delta artifact that can later feed WI-4791 quality inputs only after the bridge-approved quality feed exists and receives its own implementation/verification evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires this proposal, Loyal Opposition review, latest `GO`, implementation-start authorization, implementation report, and verification before WI-4792 can be treated as terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the owner-approved WI-4792 Batch C scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization satisfies owner approval only; it does not bypass bridge `GO`, target paths, report, or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this proposal to the active project authorization, project, and work item.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge, benchmark, dispatch-envelope, and harness-portability specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map adaptation-versioning and before/after KPI-delta requirements to concrete tests.
- `SPEC-1529` - benchmark outputs must remain comparable, calibrated, and suitable for cross-harness quality analysis.
- `ADR-CROSS-HARNESS-PARITY-001` - adaptation measurements must compare harnesses fairly and avoid hidden per-harness scoring advantages.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - before/after benchmark records should preserve dispatch-envelope identity and avoid durable role mutation.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - adaptation metadata added to benchmark envelopes or evidence must remain schema-validated and compact.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - Cursor/E measurement must preserve portable harness behavior instead of depending on a workstation-only manual state.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - Cursor readiness evidence remains relevant because Cursor/E is the first consumer of the adaptation-measurement path.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - benchmark and harness-shim work must honor GT-KB root/application boundaries and must not treat adopter application files as directly integrated GT-KB artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-4792 remains the MemBase backlog authority and must be resolved only with bridge/report/verification evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - adaptation changes and quality deltas must be preserved as durable evidence rather than informal impressions.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, PAUTH, bridge proposal, implementation report, tests, and terminal backlog disposition must remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4792 moves from backlog candidate to bridge proposal, implementation report, verification, and terminal backlog resolution through explicit lifecycle states.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation and the active PAUTH covering WI-4792.
- `DELIB-20265882` - owner grill/AUQ source for the Phase 5 requirement to measure harness adaptations through seeded-fixture A/B evidence.
- WI-4778 - resolved Cursor dispatch-readiness prerequisite and first-consumer context for Cursor/E-specific adaptation measurement.
- WI-4791 - upstream quality-KPI feed work; WI-4792 should produce advisory delta evidence that can later feed the quality path only after WI-4791 is implemented and verified.
- WI-4580, WI-4581, and WI-4583 - resolved benchmark fixture, cross-role runner, and scoring prerequisites reused by this proposal.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and active authorization `PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-WI4792-BATCH-C-20260705`. No fresh owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. The backlog row defines the adaptation-versioning and seeded-fixture A/B goal, the PAUTH explicitly authorizes WI-4792 source/test/CLI/config/governance-evidence work, and WI-4778 supplies Cursor/E as the first consumer. The implementation must not change durable role assignments, enable live dispatch, mutate credentials, or treat advisory deltas as production ranking changes.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Adaptations have stable, explicit identities | Add `platform_tests/scripts/test_harness_adaptation_impact.py` coverage for deterministic adaptation IDs/fingerprints from explicit metadata and prompt/skill/shim inputs, with stable ordering and no raw prompt leakage in compact outputs. |
| Before/after evidence isolates adaptation impact | Extend benchmark runner/scoring tests so paired baseline/candidate records over the same fixture corpus compute deterministic quality deltas and reject mismatched fixture sets, modes, harness IDs, or run tiers. |
| Cursor/E is the first measured consumer without live dispatch | Extend Cursor harness/readiness tests to expose or consume adaptation-version metadata for bridge-review/verification skill-route behavior while keeping readiness fixture-based and not requiring `can_receive_dispatch=true`. |
| Telemetry and reports preserve compact advisory deltas | Extend telemetry/reporting tests so adaptation IDs, baseline/candidate labels, score deltas, token/cost deltas, and advisory-only mutation boundaries are present without persisting live TAFE, bridge, backlog, or harness-state mutations. |
| Dispatch-envelope schema remains valid | Update envelope/manifest tests so any adaptation fields are schema-governed and cannot silently change durable role assignments or live dispatcher eligibility. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` bridge lifecycle | Implementation must run only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4792-harness-adaptation-impact-measurement`; report must cite target-path authorization evidence. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_harness_quality_runner.py platform_tests/scripts/test_harness_quality_scoring.py platform_tests/scripts/test_harness_quality_telemetry.py platform_tests/scripts/test_harness_quality_reporting.py platform_tests/scripts/test_harness_adaptation_impact.py -q --tb=short
python -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4792-harness-adaptation-impact-measurement --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4792-harness-adaptation-impact-measurement
```

## Risk / Rollback

Risk is concentrated in confusing advisory adaptation deltas with production dispatch eligibility, accidentally requiring live Cursor dispatch, or storing raw prompt/skill text in compact evidence. Keep the implementation fixture-based, compact, and advisory-only; fail closed on unpaired or mismatched evidence; and roll back as one commit if benchmark schema validation, Cursor readiness tests, or mutation-boundary guarantees regress.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-wi4792-harness-adaptation-impact-measurement`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - the expected implementation adds governed harness-adaptation KPI delta measurement.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
