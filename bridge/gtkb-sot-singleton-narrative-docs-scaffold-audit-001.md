NEW

# Implementation Proposal - WI-5019 Narrative, Docs, Dashboard, and Scaffold Duplicate-SoT Audit

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-narrative-docs-scaffold-audit
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
Work Item: WI-5019

target_paths: ["groundtruth.db", ".gtkb-state/sot-singleton-audit", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: audit | kb
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements `WI-5019`, the narrative, documentation, dashboard, and scaffold duplicate-SoT audit lane. The lane distinguishes explanatory prose from authoritative state, identifies stale duplicate claims, and validates any generated/cache-like surfaces against singleton/cache semantics.

Implementation MUST wait for `WI-5013` and `WI-5014`. This lane audits, reports, and files/links remediation WIs; it does not directly rewrite docs, dashboards, or scaffolds.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge review before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/work metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant specs to be cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived implementation-report evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - governs permitted cache freshness and non-authority.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the SoT registry the audit starting inventory.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - provides duplicate-authority precedent for role/control prose drift.
- `GOV-STANDING-BACKLOG-001` - governs remediation WI creation/linkage.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires durable audit and remediation artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires concrete findings and future work to be preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs finding/remediation lifecycle states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all work within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202665441` - owner selected registry-governed authoritative homes and derived-cache semantics.
- `DELIB-202665444` - owner selected registry-plus-closure audit coverage.
- `DELIB-202665455` - owner selected risk-first incremental remediation with one remediation WI per violation class.
- `bridge/gtkb-sot-singleton-completeness-umbrella-002.md` - umbrella GO for child proposal routing.
- `bridge/gtkb-sot-singleton-coverage-audit-001.md` - whole-platform audit proposal that this lane depends on for engine/baseline.

## Owner Decisions / Input

Captured owner decisions for this lane:

- `DELIB-202665441`: authoritative homes are registry-governed; only regenerated, read-only, TTL-bound, provenance-stamped, non-authoritative derived caches are permitted.
- `DELIB-202665444`: coverage completeness is registry-plus-closure, not sampling.
- `DELIB-202665455`: confirmed violations get one remediation WI per violation class.

No new owner decision is required to file this proposal.

## Requirement Sufficiency

Requirements are sufficient to propose this lane. Implementation waits for the singleton GOV and WI-5014 audit baseline.

## Audit Boundary

The lane covers narrative and generated user-facing surfaces, including but not limited to:

- `.claude/rules`, `AGENTS.md`, active docs under `groundtruth-kb/docs`, dashboard JSON/reporting surfaces, scaffold/template registries, generated docs, and startup/dashboard summaries;
- narrative claims that specify current authoritative state rather than merely explaining how to find it;
- generated views that may be permitted caches only if regenerated, read-only, TTL-bound, provenance-stamped, and non-authoritative;
- stale duplicate claims that owner/harness workflows might treat as authority.

Every candidate must be classified as `registered_sot`, `permitted_derived_cache`, `non_sot_reference`, `registry_gap`, or `duplicate_sot_violation`.

## Out Of Scope

- No direct narrative cleanup or documentation rewrite.
- No dashboard/scaffold implementation change.
- No source-code implementation beyond running the WI-5014 audit mechanism.

## Specification-Derived Verification / Spec-to-Test Plan

| Specification | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show latest thread status is `GO` before implementation start. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, work item, and target paths remain parseable. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-narrative-docs-scaffold-audit --json`; expected missing specs are empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands/results. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Show each generated/cache candidate has or lacks the required cache metadata and non-authority posture. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Show registry-driven candidate discovery and registry-gap classification. |
| `GOV-STANDING-BACKLOG-001` | Show every confirmed violation class has one remediation WI or existing coverage link. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Show durable lane report, classifications, and lifecycle states. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Show all report and KB mutations remain under `E:\GT-KB`. |

Initial verification commands:

```text
python -m pytest groundtruth-kb/tests/test_sot_duplicate_audit.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-narrative-docs-scaffold-audit --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-sot-singleton-narrative-docs-scaffold-audit
rg -n "Source of Truth|source of truth|authoritative|canonical" AGENTS.md .claude/rules groundtruth-kb/docs config
```

## Risk / Rollback

Primary risk is over-reading explanatory docs as authority. The lane must distinguish normative current-state claims from ordinary references. Rollback is report supersession plus remediation-WI correction/supersession if a false positive is filed.

## Recommended Commit Type

`docs`: this lane produces audit evidence and remediation-WI linkage, not platform code.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
