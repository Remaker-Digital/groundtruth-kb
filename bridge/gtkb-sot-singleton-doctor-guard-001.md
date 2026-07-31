NEW

# Implementation Proposal - WI-5015 Duplicate-SoT Doctor Guard

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-doctor-guard
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-04T23:54:31Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f2ee1-6ef3-70b2-a55b-6aceae84fbab
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: interactive Prime Builder session; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA
Project: PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS
Work Item: WI-5015

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/sot_audit.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_sot_duplicate_audit.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", ".gtkb-state/sot-singleton-audit", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: source | guard | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal implements `WI-5015`, the mechanical doctor guard that prevents re-introduction of persistent duplicate Source-of-Truth information after the WI-5011 audit baseline exists. The guard is the drift-prevention layer: it should fail or warn deterministically when an artifact copies authoritative SoT data outside a permitted derived-cache contract.

This proposal deliberately sequences after `WI-5013` and `WI-5014`. The singleton GOV defines what counts as an illegal duplicate and what metadata a permitted derived cache must carry. The coverage audit provides the initial complete classification baseline and any accepted allowlist/delegation evidence. Implementation of this guard MUST NOT begin until both conditions are present.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this implementation proposal to enter the file bridge and wait for Loyal Opposition `GO`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and parseable target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires every relevant governing specification to be cited before approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to carry forward spec-derived tests and observed results.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - governs freshness, canonical reads, and cache non-authority.
- `GOV-PLATFORM-SOT-REGISTRY-001` - governs the SoT registry and registry-backed discovery that the doctor guard must use.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - provides the harness-state duplicate precedent and forbids competing harness authority copies.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` - governs registry fields used by guard logic, including `depends_on` and `forbidden_substitutes`.
- `DCL-SOT-READ-HOOK-CONTRACT-001` - governs existing SoT read-discipline enforcement that the new guard must complement rather than weaken.
- `GOV-STANDING-BACKLOG-001` - governs preservation of any guard-discovered remediation work item instead of silent inline fixes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the guard baseline, violations, reports, and tests to be durable traceable artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires concrete findings and future work to be captured as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs candidate, active, deferred, verified, and complete states for guard findings.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps implementation and verification inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202665441` - owner selected registry-governed authoritative homes and strict derived-cache semantics.
- `DELIB-202665444` - owner selected registry-plus-closure whole-system audit coverage.
- `DELIB-202665455` - owner selected risk-first incremental remediation, one violation class per child/remediation WI.
- `bridge/gtkb-sot-singleton-completeness-umbrella-002.md` - umbrella GO authorizing child proposal routing.
- `bridge/gtkb-sot-singleton-gov-foundation-002.md` - WI-5013 GO with exact-content owner-approval precondition.
- `bridge/gtkb-sot-singleton-coverage-audit-001.md` - WI-5014 proposal defining the audit baseline this guard must consume after GO/implementation.

## Owner Decisions / Input

Owner decisions already captured for this guard:

- `DELIB-202665441`: the only permitted duplicate-like artifact is a regenerated, read-only, TTL-bound, provenance-stamped, non-authoritative derived cache.
- `DELIB-202665444`: coverage completeness must be established by registry-plus-closure scanning, not by sampling.
- `DELIB-202665455`: confirmed violations are remediated incrementally with one remediation work item per violation class.

No new owner decision is required to file this proposal. Exact-content owner approval remains separately required for `WI-5013` before this guard can be implemented.

## Requirement Sufficiency

Requirements are sufficient to propose the guard, but implementation has hard preconditions:

- `GOV-SOT-SINGLETON-001` must be recorded in MemBase by `WI-5013`; and
- the WI-5014 audit must have produced or identified a verified baseline of `registered_sot`, `permitted_derived_cache`, `non_sot_reference`, `registry_gap`, and `duplicate_sot_violation` classifications.

Without those preconditions, this proposal may be reviewed for architecture and sequencing, but Prime Builder must stop before source or test mutation.

## Proposed Guard Architecture

The implementation will add a deterministic guard to the existing `gt project doctor` family. The guard should reuse the WI-5014 audit engine instead of adding a second scanner. Its job is to compare the current repository state to the verified audit baseline and fail on new persistent duplicate-SoT information unless the candidate is classified as a permitted derived cache with machine-checkable metadata.

Expected shape:

1. Reuse `groundtruth_kb.project.sot_audit` to load registry records and duplicate/candidate classifications.
2. Add a doctor check in `groundtruth_kb.project.doctor`, next to `_check_sot_registry_completeness`, `_check_sot_read_discipline`, and `_check_harness_state_sot_consistency`.
3. Treat new or unclassified duplicate candidates as guard failures after the audit baseline is verified.
4. Treat known delegated violations as non-green until their remediation WI is terminal, unless the audit baseline explicitly marks them as existing covered violations.
5. Keep allowed derived-cache handling strict: regenerated, read-only, TTL-bound, provenance-stamped, non-authoritative, and not hand-edited.
6. Report actionable artifact paths and the governing SoT IDs so each violation can become exactly one remediation WI.

## Out Of Scope

- No formal GOV insertion; that is `WI-5013`.
- No full platform audit implementation; that is `WI-5014`.
- No remediation of violation classes; remediation gets separate WIs and bridge proposals.
- No change to dispatcher/harness selection behavior; dispatch-specific remediation remains under `WI-5012`.
- No production deployment, credential work, or out-of-root dependency.

## Spec-Derived Verification Plan

| Specification | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show latest thread status is `GO` before implementation start and include implementation-start packet evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, work item, and JSON `target_paths` remain parseable. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-doctor-guard --json`; expected missing required/advisory specs are empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands and observed results. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Test that hand-edited or stale cache-shaped duplicates fail while machine-checkable permitted caches do not become authority. |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Test that the guard uses registry records and forbidden-substitute metadata rather than hard-coded second authority lists. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | Test the dispatcher/harness duplicate field cluster is detected or remains delegated to existing remediation coverage, not silently green. |
| `DCL-SOT-READ-HOOK-CONTRACT-001` | Test the new guard coexists with `_check_sot_read_discipline` and does not weaken hook registration checks. |
| `GOV-STANDING-BACKLOG-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify any newly discovered violation is reported with enough evidence to file exactly one remediation WI. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all mutated files and generated reports remain under `E:\GT-KB`. |

Initial regression command surface:

```text
python -m pytest groundtruth-kb/tests/test_sot_duplicate_audit.py platform_tests/scripts/test_check_sot_duplicate_guard.py platform_tests/scripts/test_check_sot_registry_completeness.py platform_tests/scripts/test_check_sot_read_discipline.py -q --tb=short
gt project doctor --json
```

## Risk / Rollback

Primary risk is false failure after the first complete audit: a strict guard can block unrelated work if the baseline is ambiguous. The implementation must use explicit baseline classification and actionable messages.

Second risk is hidden duplication in generated or historical artifacts. The guard must distinguish archived evidence and read-only generated caches from live persistent duplicate authority.

Rollback is a normal source/test revert for the doctor guard plus supersession of the guard baseline if the WI-5014 audit classification is corrected. Bridge files remain append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered file for `gtkb-sot-singleton-doctor-guard`. Dispatcher/TAFE state plus the numbered file chain are the live workflow state.

## Recommended Commit Type

`feat`: this work introduces a new doctor guard for duplicate-SoT drift prevention.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
