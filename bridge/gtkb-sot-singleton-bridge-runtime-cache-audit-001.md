NEW

# Implementation Proposal - WI-5018 Bridge, Runtime-State, and Generated-Cache Duplicate-SoT Audit

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-bridge-runtime-cache-audit
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
Work Item: WI-5018

target_paths: ["groundtruth.db", ".gtkb-state/sot-singleton-audit", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX"]

implementation_scope: audit | kb
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements `WI-5018`, the bridge, runtime-state, and generated-cache duplicate-SoT audit lane. The lane distinguishes canonical workflow/audit state from short-lived regenerated caches and forbidden persistent substitutes.

Implementation MUST wait for `WI-5013` and `WI-5014`. This lane audits, reports, and files/links remediation WIs; it does not directly rewrite bridge/runtime/cache infrastructure.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs numbered bridge files and dispatcher/TAFE bridge state as workflow authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project/work metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant specs to be cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived implementation-report evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - governs permitted cache freshness and non-authority.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes the SoT registry the audit starting inventory.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - provides duplicate-authority precedent for runtime/control data.
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

The lane covers bridge/runtime/cache surfaces, including but not limited to:

- versioned bridge files, dispatcher/TAFE state, bridge work-intent state, and bridge-derived status views;
- `.gtkb-state` runtime outputs, session overlays, generated startup summaries, dashboard/runtime caches, and current-state readers;
- generated outputs that may be permitted caches only if regenerated, read-only, TTL-bound, provenance-stamped, and non-authoritative;
- persistent runtime files that duplicate current workflow state without clear source/provenance.

Every candidate must be classified as `registered_sot`, `permitted_derived_cache`, `non_sot_reference`, `registry_gap`, or `duplicate_sot_violation`.

## Out Of Scope

- No direct bridge infrastructure repair.
- No rewrite of dispatcher/TAFE runtime state.
- No source-code implementation beyond running the WI-5014 audit mechanism.

## Specification-Derived Verification / Spec-to-Test Plan

| Specification | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show canonical bridge state was inspected through dispatcher/TAFE plus numbered files, not aggregate queue artifacts. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, work item, and target paths remain parseable. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-bridge-runtime-cache-audit --json`; expected missing specs are empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands/results. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Show each cache candidate has or lacks the required cache metadata and non-authority posture. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Show registry-driven candidate discovery and registry-gap classification. |
| `GOV-STANDING-BACKLOG-001` | Show every confirmed violation class has one remediation WI or existing coverage link. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Show durable lane report, classifications, and lifecycle states. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Show all report and KB mutations remain under `E:\GT-KB`. |

Initial verification commands:

```text
python -m pytest groundtruth-kb/tests/test_sot_duplicate_audit.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-bridge-runtime-cache-audit --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-sot-singleton-bridge-runtime-cache-audit
python .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
```

## Risk / Rollback

Primary risk is false positives from append-only audit trails and historical bridge evidence. The lane must distinguish historical provenance from current authority. Rollback is report supersession plus remediation-WI correction/supersession if a false positive is filed.

## Recommended Commit Type

`docs`: this lane produces audit evidence and remediation-WI linkage, not platform code.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
