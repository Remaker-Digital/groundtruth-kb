NEW

# WI-5011 SoT Singleton Completeness Umbrella

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-completeness-umbrella
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-04T22:52:28Z

author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: 019f2ee1-6ef3-70b2-a55b-6aceae84fbab
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: approval_policy=never; role override from transcript init keyword ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-WI5011-UMBRELLA
Project: PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS
Work Item: WI-5011

target_paths: ["groundtruth.db", "config/registry/sot-artifacts.toml", ".groundtruth/formal-artifact-approvals", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests", "tests", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: governance | source | tests | audit
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This is the umbrella proposal for WI-5011, the platform-wide generalization of the dispatch field drift violation observed between `config/dispatcher/rules.toml` and `harness-state/harness-registry.json`. The architecture principle to formalize is owner-stated and deliberately strict: every Source-of-Truth is a singleton, meaning a single always-authoritative artifact. The only permitted duplication is a short-lived, regenerated, read-only, time-limited, provenance-stamped, non-authoritative cache that serves read performance within a bounded usage context.

The proposed work creates a fresh platform-wide project, `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS`, with seven scoped child work items. The project will first formalize the GOV principle, then perform a registry-plus-closure full-platform audit that proves inspection coverage, then install a doctor guard that prevents persistent duplicate SoT information from being reintroduced. Any discovered duplicate class is remediated through its own child work item and bridge GO, not by opportunistic in-line cleanup.

This proposal deliberately does not re-scope the dispatch self-optimization program. Per the owner-relayed Claude Code handoff, `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION`, WI-5012, and DELIB-202665450 already cover the dispatch selection-binding / SoT-consolidation slice and later cost-aware selection work. WI-5011 references that dispatch instance only as the motivating violation and as a risk-priority input.

## Unifying Architecture

The platform rule is:

- For each SoT-bearing datum, exactly one persistent artifact is authoritative.
- The authoritative home must be declared in the platform SoT registry or in a GOV-linked registry extension when a specialized registry is required.
- Persistent duplicates of the same information are violations even when they are currently in sync.
- Generated/cache artifacts are allowed only when machine-checkable metadata proves they are regenerated, read-only to humans, TTL-bound, provenance-stamped, and non-authoritative.
- Readers must either read the authoritative artifact or read an explicitly permitted derived cache for the usage context.
- Any artifact claiming authority outside the registry-plus-GOV chain is either a registry gap or a duplicate-SoT violation.

## Constituent Work Items

- `WI-5013` / `TEST-11283`: Formalize the SoT-singleton GOV and permitted derived-cache semantics.
- `WI-5014` / `TEST-11284`: Run the registry-plus-closure platform duplicate-SoT audit.
- `WI-5015` / `TEST-11285`: Add the duplicate-SoT drift-prevention doctor guard.
- `WI-5016` / `TEST-11286`: Audit MemBase and governance SoT duplicate classes.
- `WI-5017` / `TEST-11287`: Audit harness and control-surface SoT duplicate classes without duplicating WI-5012.
- `WI-5018` / `TEST-11288`: Audit bridge, runtime-state, and generated-cache SoT duplicate classes.
- `WI-5019` / `TEST-11289`: Audit narrative, docs, dashboard, and scaffold SoT duplicate classes.

## Sequencing

1. `WI-5013` GOV foundation: create the GOV-class artifact and formal approval packet, extending `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, and `GOV-PLATFORM-SOT-REGISTRY-001`.
2. `WI-5014` coverage engine/report: enumerate registered SoTs, discover unregistered SoT-like candidates, classify every candidate, and produce an audit evidence report showing whole-platform inspection coverage.
3. `WI-5015` prevention guard: turn the audit detection logic into a doctor check that fails persistent duplicate SoT reintroductions and verifies permitted-cache metadata.
4. `WI-5016` through `WI-5019` audit lanes: break the coverage work by subsystem/violation class so risk can be reviewed and remediated incrementally.
5. Violation remediation: file one additional remediation work item per confirmed violation class. No violation remediation is bundled into this umbrella unless a child proposal receives its own GO.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires this Prime Builder proposal to enter the bridge as `NEW` and wait for Loyal Opposition `GO` before protected implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires the proposal to cite the operative GOV/DCL requirements that govern the work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires explicit linkage to the project, work item, and bounded project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the implementation report and LO verification to use spec-derived tests rather than generic smoke checks.
- `GOV-STANDING-BACKLOG-001` - Governs backlog preservation and the creation of remediation work items discovered by the platform audit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confines this platform governance/source work to the GT-KB root and prevents any Agent Red or adopter fixture cleanup from being treated as directly integrated platform remediation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires decisions, requirements, reports, tests, and work items to remain traceable as an artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Governs candidate/active/deferred/verified lifecycle states used by the audit classification and remediation queue.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires concrete owner decisions, risks, and future work discovered by the audit to be preserved as durable artifacts rather than chat-only notes.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - Provides the motivating harness-state consolidation precedent and controls the dispatch/registry duplicate-risk class.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Establishes freshness and derived-artifact discipline that the singleton GOV extends with duplication prohibition and permitted-cache semantics.
- `GOV-PLATFORM-SOT-REGISTRY-001` - Establishes the platform SoT registry as the coverage starting point and declaration surface for authoritative homes.

## Prior Deliberations

- `DELIB-202665441` - AUQ-5011-01 owner decision: authoritative homes are registry-governed and permitted caches are regenerated, read-only, TTL-bound, provenance-stamped, and non-authoritative.
- `DELIB-202665444` - AUQ-5011-02 owner decision: coverage completeness must use registry-plus-closure scanning, not sampling.
- `DELIB-202665455` - AUQ-5011-03 owner decision: remediation sequencing is risk-first and incremental, with one violation class per child WI and bridge-gated remediation.
- `DELIB-202665450` - Related dispatch umbrella design from the Claude Code handoff. It is relevant only to avoid duplicating dispatch-specific selection/cost work.

## Owner Decisions / Input

The owner-grilling gate is complete:

- AUQ-5011-01 asked for the authoritative-home decision and cache semantics. Owner selected option `1`; recorded as `DELIB-202665441`.
- AUQ-5011-02 asked for the audit coverage-completeness method. Owner selected option `1`; recorded as `DELIB-202665444`.
- AUQ-5011-03 asked for remediation sequencing and risk policy. Owner selected option `1`; recorded as `DELIB-202665455`.

Those decisions authorize this umbrella's architecture and sequencing. They do not authorize direct protected implementation before bridge GO.

## Requirement Sufficiency

Existing requirements are sufficient for the umbrella proposal and first implementation slice. The operative requirements are WI-5011, the three owner AUQ deliberations above, `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, and `GOV-PLATFORM-SOT-REGISTRY-001`.

The implementation must still create or update formal GOV content through the formal-artifact approval path before recording the new GOV artifact. If implementation discovers a SoT-bearing artifact class not covered by the current registry model, it must record that as either a registry-extension requirement or a violation work item rather than silently expanding scope.

## Coverage-Completeness Method

The audit must produce an explicit inspection manifest, not just findings. The minimum closure set is:

- All entries in `config/registry/sot-artifacts.toml` and the generated/validated projection from `gt registry list` / `gt registry validate`.
- Every file or DB surface that declares "source of truth", "authority", "authoritative", "registry", "cache", "projection", "generated", "state", or "current" semantics.
- Every canonical writer/reader for harness registry, bridge state, MemBase project/backlog/spec/test rows, formal approval packets, startup-control config, doctor checks, generated dashboards, and scaffolded adopter fixtures.
- Every persistent artifact containing duplicate field-name clusters, schema-equivalent data, copied status/current-state data, copied role/identity metadata, or copied governance/spec assertions.
- Every generated or cache-like artifact that must be classified as permitted derived cache, forbidden persistent duplicate, or non-SoT.
- A negative-evidence section showing the commands/probes used and the artifact classes that were inspected with no violation found.

Each candidate must be classified as one of: registered SoT, permitted derived cache, non-SoT reference, registry gap, or duplicate-SoT violation. Each violation must produce exactly one remediation work item unless it is already covered by an existing work item such as WI-5012.

## Specification-Derived Verification Plan

Spec-to-test mapping for the implementation report must include command evidence and observed results. At minimum, Prime Builder will run the preflight gates and pytest surfaces below, then report exact pass/fail output:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run bridge compliance and verify this file enters as `NEW`; expected result is no compliance denial and no role-authority mismatch.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: verify `Project Authorization`, `Project`, `Work Item`, and `target_paths` are present and parseable; expected result is no project-linkage gap.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: run `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-sot-singleton-completeness-umbrella-001.md --json`; expected result is `preflight_passed: true` and no missing required specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-sot-singleton-completeness-umbrella-001.md`; expected result is zero blocking gaps.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: run `python -m pytest groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/adopter/test_doctor_detects_isolation_violations.py -q --tb=short`; expected observed result is pass or a documented pre-existing unrelated failure.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: verify the audit report preserves owner decisions, classifications, remediation work items, and lifecycle states as durable artifacts; expected observed result is that no finding is only preserved in chat or harness-local memory.
- `GOV-PLATFORM-SOT-REGISTRY-001`: run `gt registry validate --json`; expected result is no registry/projection divergence before implementation starts.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`: run the existing harness-state SoT consistency tests plus the new duplicate-SoT doctor tests in child implementation; expected result is that dispatcher/rules persistent duplication is either delegated to WI-5012 or flagged as an existing violation, not silently accepted.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: verify permitted caches carry regeneration/provenance/TTL/non-authority metadata and persistent copies without that metadata fail the new guard.
- `GOV-STANDING-BACKLOG-001`: verify every confirmed violation has a remediation WI and no duplicate remediation is filed for work already covered by WI-5012 or another existing item.

Initial regression command surface for this umbrella:

```text
python -m pytest groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/scripts/test_check_sot_registry_completeness.py platform_tests/scripts/test_check_harness_state_sot_consistency.py -q --tb=short
```

## Risk / Rollback

The main risk is over-broad authority churn: a singleton rule can tempt broad rewrites across governance, runtime state, generated projections, and documentation. This proposal prevents that by sequencing GOV first, audit second, guard third, and remediation last by dedicated child WI.

Rollback is by reverting the implementation commit(s) for each child slice and, for MemBase changes, using the project/work-item/history rows created by the governed CLI to identify the exact records introduced by this work. No destructive cleanup, credential lifecycle, production deployment, or dispatch self-optimization implementation is in scope.

## Bridge Filing

First-line role eligibility check: `gt harness identity` resolves Codex to durable harness ID `A`, and `gt harness roles` reports harness `A` with role `prime-builder`. Prime Builder is authorized to author `NEW` bridge proposals and is not authorized to author Loyal Opposition verdicts.

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-sot-singleton-completeness-umbrella`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat`: this umbrella introduces a platform governance capability, a coverage-complete audit program, and a prevention guard. Individual child remediations may use narrower commit types after their own bridge GO.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
