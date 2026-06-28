NEW

# gtkb-ar-readiness-phase-1-2-app-root-minimization-validator (Slice 1) - App-root minimization validator

bridge_kind: prime_proposal
Document: gtkb-ar-readiness-phase-1-2-app-root-minimization-validator
Version: 001
Author: Prime Builder / Codex Desktop
Date: 2026-06-28T17:11:23Z

author_identity: Prime Builder / Codex Desktop
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 via Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop, Windows PowerShell, danger-full-access workspace, network enabled

Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS-AGENT-RED-READINESS-PROGRAM-PHASE-1-ISOLATION-PARTITION-IN-PLACE
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: WI-4655

target_paths: ["groundtruth-kb/src/groundtruth_kb/isolation/app_root_minimization.py", "groundtruth-kb/src/groundtruth_kb/isolation/__init__.py", "groundtruth-kb/src/groundtruth_kb/isolation/registry_check.py", "groundtruth-kb/src/groundtruth_kb/isolation/doctor_verdicts.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/release_candidate_gate.py", "applications/Agent_Red/.gtkb-app-isolation.json", "platform_tests/scripts/test_ar_readiness_phase_1_2_app_root_minimization_validator.py", "platform_tests/scripts/test_release_candidate_gate.py"]

implementation_scope: source | test | release_gate | app_registry_metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4655, the Phase 1.2 Agent Red Readiness app-root minimization validator. The validator will consume `applications/Agent_Red/.gtkb-app-isolation.json`, compare the live top-level entries under `applications/Agent_Red/` against `top_level_artifacts[]`, enforce the DCL-aligned bucket requirements, and surface failures through both `gt project doctor` and the non-deploying release candidate gate.

This proposal is intentionally limited to the validator slice. It does not activate the work-subject write guard from WI-4656, does not perform partition-in-place data migration from WI-4657, and does not create or revise formal GOV/ADR/DCL/SPEC rows. It may update the registry's `validator_contract.implementation_status` from pending to implemented after the validator and release-gate wiring are in place.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs the append-only bridge filing and requires the latest bridge status to be live authority before protected implementation work begins.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the specifications that drive implementation and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires explicit project, work-item, and PAUTH linkage for this bridge proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires Loyal Opposition verification to be based on tests derived from the linked specifications rather than generic smoke evidence.
- `GOV-STANDING-BACKLOG-001` - establishes MemBase backlog authority; WI-4655 is the active P1 backlog item this proposal processes.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - requires Agent Red to remain a separate application project rather than being absorbed into GT-KB platform artifacts; the validator enforces the boundary from the GT-KB side.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires fresh canonical reads for state claims; the validator reads the live registry and filesystem state at execution time.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - requires Agent Red to live under `E:/GT-KB/applications/Agent_Red/`; the validator's scope is that application root.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - establishes the `applications/<name>/` placement contract that this validator checks for Agent Red.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - defines GT-KB applications as isolated execution contexts with application-scoped lifecycle artifacts.
- `DCL-APP-ROOT-MINIMIZATION-001` - defines the app-root minimization assertions that the validator must enforce: registry exists, `top_level_artifacts[]` entries carry `name`/`type`/`bucket`, bucket A has `purpose`, bucket B has `tool` plus `justification`, and buckets C/D are not allowed at the app root.

## Prior Deliberations

- `DELIB-20265219` - owner ratified the Agent Red Readiness program and its platform-side Phase 1 focus.
- `DELIB-20265220` - owner approved materializing Phase 1 slices and identified sub-slice 5 as the app-root validator work now represented by WI-4655.
- `DELIB-20265227` - owner resolved the Phase 1.1 governance foundation as both `ADR-APPLICATION-ISOLATION-CONTRACT-001` and `DCL-APP-ROOT-MINIMIZATION-001`; this slice implements the DCL enforcement surface.

## Owner Decisions / Input

No new owner decision is required before filing. The active Phase 1 PAUTH covers WI-4655 and cites `DELIB-20265219`; the work item itself cites `DELIB-20265219` and `DELIB-20265220`. A per-slice bridge GO and implementation-start packet are still required before protected source, test, script, or registry mutations.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4655 states the required acceptance outcome: "Validator runs in doctor + release gate; fails unmatched app-root entries." Phase 1.1 has already resolved the prerequisite ADR/DCL work, and MemBase current rows show `ADR-APPLICATION-ISOLATION-CONTRACT-001` and `DCL-APP-ROOT-MINIMIZATION-001` as specified.

## Proposed Implementation

1. Add a focused app-root minimization validator under `groundtruth_kb.isolation` that:
   - loads `.gtkb-app-isolation.json` from a supplied application root,
   - validates schema shape for `application`, `top_level_artifacts[]`, and `validator_contract`,
   - compares real top-level filesystem entries against registry entries by `name` plus `type`,
   - fails unmatched filesystem entries and duplicate/missing registry entries,
   - enforces bucket A `purpose`, bucket B `tool` plus `justification`, and rejects bucket C/D at app root,
   - returns structured findings without mutating files.
2. Wire the validator into `gt project doctor` as a required isolation check for `applications/Agent_Red/`, with pass/fail JSON and text output that names the offending entries.
3. Wire the validator into `scripts/release_candidate_gate.py` so the non-deploying release gate fails on unmatched app-root entries even when heavier Python/frontend gates are skipped.
4. Update `applications/Agent_Red/.gtkb-app-isolation.json` metadata only to mark `validator_contract.implementation_status` as implemented by this slice, after the validator and release-gate wiring pass.
5. Add focused platform tests covering clean live state, synthetic unmatched file/registry failures, bucket field failures, doctor integration, and release-gate failure propagation.

## Explicit Non-Goals

- No work-subject write-guard activation. That belongs to WI-4656.
- No data partition-in-place or bulk MemBase path rewrite. That belongs to WI-4657.
- No formal artifact insertion or revision. Any future GOV/ADR/DCL/SPEC mutation would require a formal-artifact approval packet outside this slice.
- No writes outside `E:/GT-KB`.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `DCL-APP-ROOT-MINIMIZATION-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ar_readiness_phase_1_2_app_root_minimization_validator.py -q --tb=short` proves each DCL assertion maps to validator behavior. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-APPLICATION-ISOLATION-CONTRACT-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | The same focused pytest confirms the validator remains scoped to `applications/Agent_Red/` and reports application-root findings without moving application artifacts into GT-KB platform authority. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Focused tests create temporary registry/filesystem fixtures and assert the validator reads live state at execution time rather than cached bridge or startup summaries. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest plus release-gate tests cover clean, unmatched-entry, malformed-registry, and bucket-contract failure cases. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001` | Bridge applicability preflight and clause preflight must pass for this proposal, and implementation-start must bind the GO bridge to WI-4655 before protected edits. |

Expected post-implementation commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ar_readiness_phase_1_2_app_root_minimization_validator.py platform_tests/scripts/test_release_candidate_gate.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ar_readiness_phase_1_1_governance_foundation.py platform_tests/scripts/test_ar_isolation_status_reconciliation.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/isolation groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/release_candidate_gate.py platform_tests/scripts/test_ar_readiness_phase_1_2_app_root_minimization_validator.py platform_tests/scripts/test_release_candidate_gate.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/isolation groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/release_candidate_gate.py platform_tests/scripts/test_ar_readiness_phase_1_2_app_root_minimization_validator.py platform_tests/scripts/test_release_candidate_gate.py
groundtruth-kb/.venv/Scripts/gt.exe project doctor --dir . --json
groundtruth-kb/.venv/Scripts/python.exe scripts/release_candidate_gate.py --skip-python --skip-frontend --skip-dev-inventory --skip-dev-inventory-drift
```

## Risk / Rollback

Risk is moderate because the slice adds required doctor and release-gate failure surfaces. False positives could block local readiness or release-candidate checks, so tests must cover synthetic and live-tree clean cases. Rollback is a single commit revert restoring the previous doctor/release-gate behavior and the registry metadata `implementation_status`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-ar-readiness-phase-1-2-app-root-minimization-validator`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat - this adds a new enforced validator and release-gate surface for an existing governance contract.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
