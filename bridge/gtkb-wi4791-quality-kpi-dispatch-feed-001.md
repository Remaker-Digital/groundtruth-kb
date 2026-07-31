NEW

# WI-4791 - Quality KPI Dispatch Feed

bridge_kind: prime_proposal
Document: gtkb-wi4791-quality-kpi-dispatch-feed
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T01:17:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-WI4791-BATCH-C-20260705
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4791

target_paths: ["scripts/benchmarks/harness_quality_scoring.py", "scripts/benchmarks/harness_quality_runner.py", "scripts/benchmarks/harness_quality_reporting.py", "scripts/benchmarks/harness_quality_telemetry.py", "scripts/benchmarks/fixture_corpus.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/harness_ops.py", "config/dispatcher/rules.toml", "platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py", "platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py", "platform_tests/scripts/test_api_harness_stewardship_monitor.py", "platform_tests/scripts/test_bridge_dispatch_priority.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4791 extends the existing harness-quality benchmark and dispatch-lane foundations into a governed quality input for dispatcher/TAFE selection. The current code already has isolated seeded-flaw fixtures, synthetic benchmark evidence records, deterministic quality scoring, compact dispatch-lane projections, and a Loyal Opposition quality floor that consumes `dispatch_quality` from harness registry records while ignoring deprecated `config/dispatcher/rules.toml` quality seeds. What is still missing is the Batch C bridge-governed implementation that turns benchmark consensus evidence into relative per-harness quality scores inside GT-KB and feeds those scores into the live dispatcher quality input path.

The implementation should add a deterministic, compact quality-KPI producer that aggregates multi-harness benchmark evidence across seeded-flaw fixtures and real GT-KB work references, calibrates scores against WI-4580 fixture answer keys and WI-4583 hybrid scoring outputs, and emits per-harness/per-role/per-activity quality components suitable for `lane_scoring` projections and dispatcher candidate records. The selector must keep failing closed when quality evidence is absent, stale, malformed, or below a configured per-activity floor. Deprecated static quality fields in `rules.toml` must remain non-authoritative; they may be retained only as legacy warnings or fallback metadata that cannot override governed MemBase/registry quality evidence.

This proposal does not authorize silent production ranking changes outside the normal bridge lifecycle. It authorizes the bounded source/test/CLI/config/governance-evidence implementation under the active PAUTH after Loyal Opposition `GO`, with explicit regression evidence showing that benchmark-derived quality is traceable, compact, and does not leak raw benchmark transcripts into dispatcher projections.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires this proposal, Loyal Opposition review, latest `GO`, implementation-start authorization, implementation report, and verification before WI-4791 can be treated as terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the owner-approved WI-4791 Batch C scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization satisfies owner approval only; it does not bypass bridge `GO`, target paths, report, or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this proposal to the active project authorization, project, and work item.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge, dispatcher, TAFE, and harness-quality specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map the quality-KPI and fail-closed dispatch requirements to concrete tests.
- `SPEC-1529` - cross-harness benchmark outputs must remain comparable, evidence-backed, and suitable for harness quality analysis.
- `ADR-CROSS-HARNESS-PARITY-001` - quality scoring must preserve cross-harness comparability and avoid harness-specific hidden advantages.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher selection must consume centralized, governed quality inputs rather than ad hoc static seeds.
- `ADR-DISPATCHER-ARCHITECTURE-001` - quality scoring and candidate selection must remain inside the dispatcher architecture and not recreate retired poller behavior.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - any operational quality input or status surface must remain inspectable through dispatcher/control-plane surfaces.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - dispatcher/TAFE state remains the authority for live routing state, while compact benchmark evidence feeds quality inputs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - benchmark and dispatcher work must honor GT-KB root/application boundaries and must not treat adopter application files as directly integrated GT-KB artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-4791 remains the MemBase backlog authority and must be resolved only with bridge/report/verification evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - quality KPI evolution must remain artifact-backed instead of an untracked ranking tweak.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, PAUTH, bridge proposal, implementation report, tests, and backlog disposition must remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4791 moves from backlog candidate to bridge proposal, implementation report, verification, and terminal backlog resolution through explicit lifecycle states.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch C continuation and the active PAUTH covering WI-4791.
- `DELIB-20265882` - owner grill/AUQ source for the Phase 4 quality-KPI backlog item and its requirement to calibrate real-work consensus through seeded-flaw fixtures.
- WI-4580, WI-4581, and WI-4583 - resolved prerequisite work providing isolated seeded-flaw fixtures, cross-role benchmark dispatch records, and deterministic/adjudicated scoring primitives.
- WI-4586 - relevant design constraint that benchmark-informed dispatch enforcement must remain gated and advisory-first unless explicitly approved through later governance.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and active authorization `PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-WI4791-BATCH-C-20260705`. No fresh owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. The backlog row defines the quality-KPI behavior, the prerequisite WIs define the fixture/runner/scoring inputs, and the active PAUTH explicitly allows source, test, CLI, config, and governance-evidence mutations while forbidding credential lifecycle, deployment, destructive cleanup, and broad bulk status mutation. Implementation must remain bridge-gated and must not silently change production ranking outside the approved target paths and verification plan.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Benchmark evidence is calibrated against seeded-flaw fixtures | Add or update benchmark scoring tests so seeded-defect recall, false positives, citation coverage, verdict outcome, and adjudication availability produce deterministic quality components by harness/role/activity. |
| Quality scores are relative and computed inside the dispatcher path | Extend `groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py` tests so compact lane projections derive quality components from governed benchmark evidence/snapshots rather than raw static config fields. |
| Dispatcher/TAFE consumes governed quality input | Extend `platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py` or adjacent dispatch-config tests so candidate selection uses the computed `dispatch_quality` input, ignores deprecated `rules.toml` quality seeds, and remains deterministic under ties. |
| Per-activity quality-required floors fail closed | Add tests for at least Loyal Opposition review activity and one Prime Builder/build activity showing below-floor, missing, stale, and malformed quality evidence prevents selection or surfaces a health finding rather than routing blindly. |
| Projections remain compact and governance-safe | Preserve or extend `projection_is_compact` coverage so raw benchmark transcripts, fixture payloads, and adjudication text are omitted from dispatcher projection snapshots while evidence refs remain countable/traceable. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` bridge lifecycle | Implementation must run only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4791-quality-kpi-dispatch-feed`; report must cite target-path authorization evidence. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py platform_tests/scripts/test_api_harness_stewardship_monitor.py -q --tb=short
python -m pytest platform_tests/scripts/test_bridge_dispatch_priority.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4791-quality-kpi-dispatch-feed --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4791-quality-kpi-dispatch-feed
```

## Risk / Rollback

Risk is concentrated in making benchmark evidence look more authoritative than it is, leaking raw benchmark content into live dispatcher state, or allowing legacy config values to override governed quality evidence. Keep the implementation compact, append-only where evidence is stored, fail closed on insufficient evidence, and roll back as one commit if dispatcher eligibility or projection compactness regresses.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-wi4791-quality-kpi-dispatch-feed`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - the expected implementation adds a governed quality-KPI feed for dispatcher/TAFE quality inputs.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
