NEW

# Implementation Proposal - WI-5016 MemBase and Governance Duplicate-SoT Audit

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-membase-governance-audit
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
Work Item: WI-5016

target_paths: ["groundtruth.db", ".gtkb-state/sot-singleton-audit", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: audit | kb
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements `WI-5016`, the MemBase and governance-lane duplicate-SoT audit under the WI-5011 umbrella. The lane inspects MemBase-backed SoTs and governance registry/specification surfaces for persistent duplicate authoritative information. It produces a durable lane report and files or links one remediation work item per confirmed violation class.

Implementation MUST wait until `GOV-SOT-SINGLETON-001` is canonical and the WI-5014 audit engine/baseline is available. This proposal does not remediate findings inline.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge review before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/work metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant specs to be cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived implementation-report evidence.
- `GOV-STANDING-BACKLOG-001` - governs remediation WI creation/linkage.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the SoT registry the audit starting inventory.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - governs TOML/MemBase `sot_artifacts` projection parity so intentional projection is not misclassified as duplicate authority.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` - governs registry fields such as `depends_on` and `forbidden_substitutes` used by audit classification.
- `DCL-SOT-READ-HOOK-CONTRACT-001` - governs canonical-read enforcement and forbidden-substitute handling.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - governs fresh canonical reads and cache non-authority.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - provides the consolidation precedent for duplicate-authority handling.
- `ADR-0001` - establishes the MemBase / MEMORY.md / Deliberation Archive memory-tier model.
- `SPEC-2098` - governs Deliberation Archive behavior and scope.
- `GOV-ARTIFACT-APPROVAL-001` - governs formal artifact approval packets as evidence/preconditions rather than duplicate governance truth.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires audit findings and remediation links to be durable artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires concrete findings and future work to be captured.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs candidate, deferred, verified, complete, and remediation states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all work within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202665441` - owner selected registry-governed authoritative homes and derived-cache semantics.
- `DELIB-202665444` - owner selected registry-plus-closure audit coverage.
- `DELIB-202665455` - owner selected risk-first incremental remediation with one remediation WI per violation class.
- `DELIB-20260671` and `DELIB-20260672` - prior SoT registry and read-discipline decisions.
- `bridge/gtkb-sot-singleton-completeness-umbrella-002.md` - umbrella GO for child proposal routing.
- `bridge/gtkb-sot-singleton-coverage-audit-001.md` - whole-platform audit proposal that this lane depends on for engine/baseline.

## Owner Decisions / Input

Captured owner decisions for this lane:

- `DELIB-202665441`: authoritative homes are registry-governed; only regenerated, read-only, TTL-bound, provenance-stamped, non-authoritative derived caches are permitted.
- `DELIB-202665444`: coverage completeness is registry-plus-closure, not sampling.
- `DELIB-202665455`: confirmed violations get one remediation WI per violation class.

No new owner decision is required to file this proposal.

## Requirement Sufficiency

Requirements are sufficient to propose this audit lane. Implementation has two hard preconditions: `WI-5013` must record the singleton GOV, and `WI-5014` must provide the reusable audit classification mechanism/baseline.

## Audit Boundary

The lane covers MemBase and governance surfaces, including but not limited to:

- specifications, work items, tests, deliberations, projects, PAUTHs, assertion runs, and current projections in `groundtruth.db`;
- the `sot_artifacts` projection and parity with `config/registry/sot-artifacts.toml`;
- GOV/ADR/DCL/PB rows and formal-artifact approval packets as authority evidence;
- policy/config registries that claim authoritative governance state.

The output must classify every candidate as `registered_sot`, `permitted_derived_cache`, `non_sot_reference`, `registry_gap`, or `duplicate_sot_violation`, and either link existing remediation coverage or file one remediation WI per confirmed violation class.

## Out Of Scope

- No direct fix to a duplicate-SoT violation.
- No source-code implementation beyond running the WI-5014 audit mechanism.
- No edits to authoritative governance artifacts except remediation-WI creation/linkage in MemBase.

## Specification-Derived Verification / Spec-to-Test Plan

| Specification | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show latest thread status is `GO` before implementation start. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, work item, and target paths remain parseable. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-membase-governance-audit --json`; expected missing specs are empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands/results. |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Show registry-plus-closure inputs and cache/non-cache classifications. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-READ-HOOK-CONTRACT-001` | Show TOML/projection parity is intentional, registry metadata drives substitute classification, and forbidden substitutes are not read as authority. |
| `ADR-0001`, `SPEC-2098`, `GOV-ARTIFACT-APPROVAL-001` | Show MemBase, Deliberation Archive, MEMORY.md, and formal approval packets are classified according to their authoritative or evidentiary tier. |
| `GOV-STANDING-BACKLOG-001` | Show every confirmed violation class has one remediation WI or existing coverage link. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Show durable lane report, classifications, and lifecycle states. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Show all report and KB mutations remain under `E:\GT-KB`. |

Initial verification commands:

```text
python -m pytest groundtruth-kb/tests/test_sot_duplicate_audit.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-membase-governance-audit --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-sot-singleton-membase-governance-audit
gt backlog status --project PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS --with-verified-coverage --json
```

## Risk / Rollback

Primary risk is misclassifying historical/governance evidence as live duplicate authority. The lane must preserve negative evidence and distinguish authority from provenance. Rollback is normal report supersession plus remediation-WI correction/supersession if a false positive is filed.

## Recommended Commit Type

`docs`: this lane produces audit evidence and remediation-WI linkage, not platform code.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
