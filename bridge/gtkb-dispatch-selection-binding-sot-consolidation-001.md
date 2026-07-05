NEW

# Implementation Proposal - WI-5012 Dispatch Selection-Binding and SoT Consolidation

bridge_kind: prime_proposal
Document: gtkb-dispatch-selection-binding-sot-consolidation
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-05T07:03:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012
Project: PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION
Work Item: WI-5012

target_paths: ["config/dispatcher/rules.toml", "harness-state/harness-registry.json", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_rules.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/tafe_dispatch_runtime.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/lane_scoring.py", "groundtruth-kb/src/groundtruth_kb/dispatcher/rules_loader.py", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/harness_ops.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py", "groundtruth-kb/tests/test_harness_projection.py", "groundtruth-kb/tests/test_harness_ops.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: source | config | kb | test | report
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements `WI-5012`, the first buildable slice of `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION`. It resolves the dispatch instance of the SoT-singleton duplicate field class and binds live dispatch selection to one canonical attribute home.

The conservative implementation path is **P-B** for this slice: keep `groundtruth_kb.dispatcher.lane_scoring` as the shadow/evidence model for the downstream scoring WIs, and wire the live dispatcher/runtime/config surfaces to consume projection-backed harness attributes from the harness registry/MemBase instead of duplicated `rules.toml` copies. If implementation proves P-A (activating lane_scoring as the production selector) is required, Prime Builder must pause and file a revision rather than silently expanding scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge review, live GO, work-intent claim, and implementation-start packet before protected implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant governing specs to be cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-derived verification evidence before VERIFIED.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - establishes harness registry/MemBase as the durable harness-state authority and forbids competing persistent copies.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - requires canonical harness-state reader/projection entrypoints.
- `REQ-HARNESS-REGISTRY-001` - governs harness registry fields, roles, dispatch metadata, and projection behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires fresh canonical reads and forbids stale substitutes as authority.
- `GOV-SOT-SINGLETON-001` - formalizes the SoT-singleton principle and permitted derived-cache semantics.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the SoT registry the inventory starting point.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatcher control/read surfaces.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - forbids ad hoc dispatcher config mutation outside governed CLI/control paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - constrains dispatcher architecture and runtime/control boundaries.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs centralized dispatch service operation.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - constrains dispatch envelope and rule semantics.
- `GOV-STANDING-BACKLOG-001` - keeps WI-5012 and follow-on dispatch calibration work visible in MemBase.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires durable artifact linkage for evidence and decisions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires concrete findings, risks, and future work to be preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs candidate, verified, resolved, superseded, and remediation states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all work under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202665442` - owner selected harness registry/MemBase as the single authoritative home for the five duplicated dispatch fields; `rules.toml` becomes policy-only and references through `harness_projection`.
- `DELIB-202665446` - owner selected Claude/B as headless-eligible and first-class selectable for headless LO work.
- `DELIB-202665447` - owner selected the per-lane threshold-filter plus objective model with median and tail floors.
- `DELIB-202665449` - owner selected weekly capability-adjust as GO-required proposal generation, never auto-apply.
- `DELIB-202665441`, `DELIB-202665444`, `DELIB-202665455` - SoT-singleton umbrella decisions: registry-governed homes, registry-plus-closure coverage, and one remediation WI per violation class.
- `bridge/gtkb-sot-singleton-harness-control-audit-005.md` - WI-5017 links the known duplicate dispatch field class to WI-5012.
- `bridge/gtkb-sot-singleton-bridge-runtime-cache-audit-004.md` - WI-5018 VERIFIED bridge/runtime/cache audit; no competing runtime-cache remediation.
- `bridge/gtkb-sot-singleton-coverage-audit-008.md` - WI-5014 VERIFIED duplicate-SoT audit engine/baseline.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-19-08-dispatch-attribute-calibration-advisory.md` - source advisory for the dispatch-selection self-optimization project.

## Owner Decisions / Input

The following AskUserQuestion-backed deliberations authorize the proposal scope:

- `DELIB-202665442`: five dispatch fields have one authoritative home: harness registry/MemBase; `rules.toml` becomes policy-only; derived caches must be regenerated, read-only, time-limited, and never hand-edited.
- `DELIB-202665446`: Claude/B is headless-eligible and must remain selectable.
- `DELIB-202665447`: dispatch selection uses threshold-filter then per-lane objective; floors include median and tail bounds.
- `DELIB-202665449`: weekly capability-adjust emits GO-required proposals and never auto-applies.

Project authorization `PAUTH-PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION-WI5012` was created from this owner-decision evidence and explicitly preserves bridge-GO gating.

## Requirement Sufficiency

Existing requirements sufficient. The owner decisions and governing specs above are enough to propose the first WI-5012 implementation slice. Any implementation discovery that requires activating `lane_scoring` as the production selector, changing the downstream WI ordering, or altering weekly capability-adjust semantics must return to the bridge as a revision before implementation proceeds.

## Implementation Plan

1. Document the true live selection path in the implementation report, including the current dispatcher/runtime ordering and where `lane_scoring.py` is shadow-only.
2. Convert `config/dispatcher/rules.toml` to policy-only for the five duplicated fields by removing persistent per-harness copies of `can_fire_events`, `can_receive_dispatch`, `dispatch_availability`, `dispatch_cost`, and `dispatch_quality`.
3. Update dispatcher config/runtime/read surfaces so dispatchability, event capability, quality, cost, and availability are read from the canonical harness registry/MemBase projection through existing harness projection entrypoints.
4. Preserve `rules.toml` policy fields such as `selection_order`, rules, budget, and future per-lane floor/objective policy.
5. Keep Claude/B selectable for headless LO dispatch and add/adjust tests that prove it is not precedence-excluded.
6. Add or update doctor/test coverage so reintroducing persistent duplicate copies of the five fields fails deterministically after WI-5012.
7. Run the duplicate-SoT audit and dispatcher tests; file a post-implementation report with exact outputs and Architecture Alignment Ledger.

## Out Of Scope

- No weekly capability-adjust implementation or scheduled automation.
- No automatic application of recalibrated attribute values.
- No full production activation of the downstream lane-scoring model unless this proposal is revised and GO'd again.
- No remediation of unrelated SoT audit findings outside the five-field dispatch duplicate class.
- No credential lifecycle, production deployment, or destructive cleanup.

## Spec-Derived Verification Plan

| Specification | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show latest bridge status `GO`, a Prime Builder work-intent claim, and implementation-start packet before mutation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Show PAUTH, project, work item, and target paths parse in the implementation packet. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-selection-binding-sot-consolidation --json`; expect no missing specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands and observed results. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, `REQ-HARNESS-REGISTRY-001`, `GOV-SOT-SINGLETON-001` | Prove the five dispatch fields have one persistent authoritative home in harness registry/MemBase and no persistent duplicate copy in `rules.toml`. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-PLATFORM-SOT-REGISTRY-001` | Run `gt registry audit-duplicates --json --no-write`; expect no `duplicate-dispatch-harness-fields` violation after implementation. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001` | Run focused dispatcher config/runtime tests proving live selection consumes projected attributes and preserves policy-only rule semantics. |
| `GOV-STANDING-BACKLOG-001` | Show WI-5012 remains the single remediation lane for this duplicate class and that no competing remediation WI was created. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | File implementation report and evidence with disposition for the duplicate class. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Show all changed paths are under `E:\GT-KB`. |

Initial verification command set:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_bridge_dispatch_lo_quality_floor.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/groundtruth_kb/test_dispatch_lane_scoring_projection.py groundtruth-kb/tests/test_harness_projection.py groundtruth-kb/tests/test_harness_ops.py platform_tests/scripts/test_check_sot_duplicate_guard.py groundtruth-kb/tests/test_sot_duplicate_audit.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-selection-binding-sot-consolidation --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-selection-binding-sot-consolidation
gt registry audit-duplicates --json --no-write
gt bridge dispatch config --json
gt bridge dispatch status --json
gt project doctor --json
```

If `gt project doctor --json` still reports unrelated pre-existing failures, the implementation report must quote the WI-5012-relevant checks separately and list unrelated failures as residual risk rather than claiming a global doctor pass.

## Architecture Alignment Ledger

- OPS consolidation: this slice reduces owner burden by making the dispatch attribute home explicit and machine-enforced rather than maintained through parallel files.
- Dispatcher daemon architecture: keeps dispatcher behavior behind the governed dispatch control/runtime surfaces and avoids ad hoc edits to runtime state.
- Lifecycle-first / scoring-last precedence: resolves the lifecycle and SoT conflict before activating richer scoring; full lane-scoring production activation remains downstream.
- Portfolio reconciliation: implements the exact remediation linked by WI-5017 and does not duplicate WI-5011 audit lanes or later calibration WIs.

## Risk / Rollback

Primary risk is changing dispatch selection behavior while removing duplicated config fields. Mitigation is to keep the first slice conservative: preserve the existing policy order and runtime semantics, move only the authoritative field reads to harness projection, and prove Claude/B remains selectable. Rollback is a single commit revert after LO verification if selection behavior regresses.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-dispatch-selection-binding-sot-consolidation`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `fix:`

`fix:` is recommended because this slice repairs a confirmed duplicate-SoT defect and dispatch selection/source-of-truth inconsistency rather than adding a new standalone feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
