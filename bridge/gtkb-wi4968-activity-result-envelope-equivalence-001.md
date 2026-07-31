NEW

# WI-4968 - Activity Result Envelope Equivalence

bridge_kind: prime_proposal
Document: gtkb-wi4968-activity-result-envelope-equivalence
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T01:48:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4968-BATCH-C-20260705
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4968

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py", "groundtruth-kb/src/groundtruth_kb/tafe_dispatch_policy.py", "scripts/benchmarks/benchmark_dispatch_envelope.py", "scripts/benchmarks/harness_quality_telemetry.py", "scripts/benchmarks/activity_envelope_load.py", "scripts/benchmarks/harness_observed_scorecard.py", "platform_tests/scripts/test_dispatcher_envelope_runtime.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_harness_quality_runner.py", "platform_tests/scripts/test_harness_quality_telemetry.py", "platform_tests/scripts/test_benchmark_activity_envelope_load.py", "platform_tests/scripts/test_dispatcher_runtime_worker_delivery.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4968 implements Phase 3 gap 06: use WI-4950 as the baseline and prove, with transcript/result evidence, that each harness either exposes equivalent activity/result/session-envelope behavior or carries a specific typed waiver. This proposal is about evidence and equivalence, not reopening verified envelope-sharding work except through explicit supersession links.

The implementation should define compact comparison records for activity envelopes, result envelopes, and session envelopes across harnesses, connect them to benchmark/telemetry inputs, and expose a deterministic report or helper that distinguishes equivalent, missing, stale, malformed, and waived cases. Existing dispatcher/session envelope tests should be extended to keep the runtime and benchmark representations aligned.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - bridge/PAUTH lifecycle applies.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - proposal, spec, and verification linkage are mandatory.
- `ADR-CROSS-HARNESS-PARITY-001` - envelope equivalence is a cross-harness parity requirement.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` and `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - envelope evidence must preserve the governed dispatch/result schema.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve artifact traceability and root boundaries.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation.
- `DELIB-202665197` and `bridge/harness-equivalence-phase-3-umbrella-002.md` - Phase 3 child-gap authority.
- WI-4950 - baseline for activity/result/session envelope sharding.
- `TEST-11268` - manual test linkage for WI-4968 under `ADR-CROSS-HARNESS-PARITY-001`.

## Owner Decisions / Input

Owner approval is already recorded by the active PAUTH. No fresh owner decision is required.

## Requirement Sufficiency

Existing requirements are sufficient: use WI-4950 as baseline, compare harness evidence, and record typed waivers for non-equivalent surfaces.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Activity/result/session envelope equivalence is measured | Add tests for equivalent, missing, stale, malformed, and waived envelope records across fixture harnesses. |
| Runtime and benchmark schemas stay aligned | Extend dispatcher/session-envelope and benchmark telemetry tests to share stable fields and compact IDs. |
| Verified sharding work is not reopened silently | Add assertions that any supersession of WI-4950 evidence is explicit and referenced. |
| Bridge lifecycle is preserved | Run proposal/report preflights and cite implementation-start evidence. |

Minimum expected verification commands:

```text
python -m pytest platform_tests/scripts/test_dispatcher_envelope_runtime.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_dispatcher_runtime_worker_delivery.py -q --tb=short
python -m pytest platform_tests/scripts/test_harness_quality_runner.py platform_tests/scripts/test_harness_quality_telemetry.py platform_tests/scripts/test_benchmark_activity_envelope_load.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4968-activity-result-envelope-equivalence --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4968-activity-result-envelope-equivalence
```

## Risk / Rollback

Risk is mixing runtime dispatch envelopes with benchmark-only evidence or overwriting verified sharding decisions. Keep evidence compact and additive; rollback if envelope runtime tests regress.

## Bridge Filing

This proposal is filed as the first numbered bridge file for `gtkb-wi4968-activity-result-envelope-equivalence`.

## Recommended Commit Type

feat - add harness envelope equivalence evidence.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
