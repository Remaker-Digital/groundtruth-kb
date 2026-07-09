NEW

# Implementation Proposal - WI-5017 Harness and Control-Surface Duplicate-SoT Audit

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-harness-control-audit
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-05T00:00:16Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f2ee1-6ef3-70b2-a55b-6aceae84fbab
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: interactive Prime Builder session; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA
Project: PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS
Work Item: WI-5017

target_paths: ["groundtruth.db", ".gtkb-state/sot-singleton-audit", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: audit | kb
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements `WI-5017`, the harness and control-surface duplicate-SoT audit lane. The lane inspects harness-state and agent-control authority surfaces, while explicitly avoiding duplicate implementation scope with `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION` / `WI-5012`.

Implementation MUST wait for `WI-5013` and `WI-5014`. This lane audits, reports, and files/links remediation WIs; it does not directly repair the dispatch-specific duplicated fields or any other violation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge review before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/work metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant specs to be cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived implementation-report evidence.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - governs harness-state authority and the motivating duplicate field class.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - governs canonical harness-state readers and projections.
- `REQ-HARNESS-REGISTRY-001` - governs durable harness registry fields and role/dispatch metadata.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - governs role portability across harnesses rather than vendor-specific role claims.
- `GOV-SESSION-ROLE-AUTHORITY-001` - governs durable versus interactive session role authority.
- `DCL-SESSION-ROLE-RESOLUTION-001` - governs role resolution behavior and prevents prose/marker substitutes from becoming authority.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatcher control/read surfaces in this lane.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - governs dispatcher configuration mutation/read discipline.
- `ADR-DISPATCHER-ARCHITECTURE-001` - governs dispatcher architecture boundaries relevant to control-surface classification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs centralized dispatcher service authority.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - constrains dispatch envelope/rule semantics, with any conflict deferred to the newer singleton-GOV decision.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the SoT registry the audit starting inventory.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - governs fresh canonical reads and cache non-authority.
- `GOV-STANDING-BACKLOG-001` - governs remediation WI creation/linkage.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires durable audit and remediation artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires concrete findings and future work to be preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs finding/remediation lifecycle states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all work within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202665441` - owner selected registry-governed authoritative homes and derived-cache semantics.
- `DELIB-202665444` - owner selected registry-plus-closure audit coverage.
- `DELIB-202665455` - owner selected risk-first incremental remediation with one remediation WI per violation class.
- `DELIB-202665442` - owner selected harness registry/MemBase as authoritative home for the five duplicated dispatch fields while `rules.toml` becomes policy-only.
- `DELIB-202665450` - dispatch self-optimization umbrella and `WI-5012` scope boundary.
- `DELIB-20260670`, `DELIB-20260671`, and `DELIB-20260672` - prior SoT substitution survey, registry decision, and read-discipline hook decision.
- `bridge/gtkb-sot-singleton-completeness-umbrella-002.md` - umbrella GO for child proposal routing.
- `bridge/gtkb-sot-singleton-coverage-audit-001.md` - whole-platform audit proposal that this lane depends on for engine/baseline.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-19-08-dispatch-attribute-calibration-advisory.md` - advisory that scoped the dispatch-specific instance separately.

## Owner Decisions / Input

Captured owner decisions for this lane:

- `DELIB-202665441`: authoritative homes are registry-governed; only regenerated, read-only, TTL-bound, provenance-stamped, non-authoritative derived caches are permitted.
- `DELIB-202665444`: coverage completeness is registry-plus-closure, not sampling.
- `DELIB-202665455`: confirmed violations get one remediation WI per violation class.

No new owner decision is required to file this proposal.

## Requirement Sufficiency

Requirements are sufficient to propose this lane. Implementation waits for the singleton GOV and the WI-5014 audit baseline.

## Audit Boundary

The lane covers harness and control surfaces, including but not limited to:

- `harness-state/harness-identities.json`, `harness-state/harness-registry.json`, and bridge substrate state;
- `config/agent-control/harness-capability-registry.toml`, startup control maps, activity registries, system interface maps, and policy registries;
- role/dispatch projection readers and generated or cached startup/control summaries;
- the known dispatcher/rules.toml versus harness-registry duplicate field cluster, treated as delegated to `WI-5012` unless additional uncovered violation classes appear.

Every candidate must be classified as `registered_sot`, `permitted_derived_cache`, `non_sot_reference`, `registry_gap`, or `duplicate_sot_violation`.

## Out Of Scope

- No dispatch-selection implementation or field migration; that remains in `WI-5012`.
- No direct edit to harness registries or dispatcher configuration under this lane.
- No source-code implementation beyond running the WI-5014 audit mechanism.

## Specification-Derived Verification / Spec-to-Test Plan

| Specification | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show latest thread status is `GO` before implementation start. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, work item, and target paths remain parseable. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-harness-control-audit --json`; expected missing specs are empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands/results. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | Show harness/control duplicate candidates and delegated `WI-5012` classification for the known dispatch field cluster. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, `REQ-HARNESS-REGISTRY-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001` | Show role/identity/capability candidates are classified against canonical harness readers and durable registry authority rather than prose or generated summaries. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001` | Show dispatcher-control candidates are audited without remediating the known field overlap, and that overlap remains delegated to `WI-5012`. |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Show registry-driven candidate discovery and cache classification. |
| `GOV-STANDING-BACKLOG-001` | Show every confirmed violation class has one remediation WI or existing coverage link. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Show durable lane report, classifications, and lifecycle states. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Show all report and KB mutations remain under `E:\GT-KB`. |

Initial verification commands:

```text
python -m pytest groundtruth-kb/tests/test_sot_duplicate_audit.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-harness-control-audit --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-sot-singleton-harness-control-audit
gt backlog show WI-5012 --json
```

## Risk / Rollback

Primary risk is accidentally broadening or duplicating `WI-5012`. This lane must classify the known dispatch field issue as delegated, not remediate it. Rollback is report supersession plus remediation-WI correction/supersession if a false positive is filed.

## Recommended Commit Type

`docs`: this lane produces audit evidence and remediation-WI linkage, not platform code.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
