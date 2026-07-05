NEW

# Implementation Proposal - WI-5014 Registry-Plus-Closure SoT Duplicate Audit

bridge_kind: prime_proposal
Document: gtkb-sot-singleton-coverage-audit
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-04T23:47:06Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f2ee1-6ef3-70b2-a55b-6aceae84fbab
author_model: GPT-5 via Codex Desktop
author_model_version: current Codex Desktop runtime
author_model_configuration: interactive Prime Builder session; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS-UMBRELLA
Project: PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS
Work Item: WI-5014

target_paths: ["groundtruth.db", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/src/groundtruth_kb/project/sot_audit.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_sot_duplicate_audit.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX", ".gtkb-state/sot-singleton-audit"]

implementation_scope: source | audit | kb
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements `WI-5014`, the registry-plus-closure duplicate-SoT audit required by the WI-5011 umbrella. The work will build and run a deterministic audit that starts from the platform SoT registry, expands to whole-repository SoT-like candidates, classifies every candidate, and files or links one remediation work item per confirmed duplicate-SoT violation class.

This proposal is intentionally not the GOV foundation. `WI-5013` already has GO on `gtkb-sot-singleton-gov-foundation`, but the GOV text still needs exact-content owner approval and MemBase insertion. Implementation of this audit MUST NOT begin until `GOV-SOT-SINGLETON-001` exists in MemBase or the implementation-start packet cites an equivalent verified GOV-foundation result from `WI-5013`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this proposal to enter the bridge as `NEW` and wait for Loyal Opposition `GO` before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all operative governing specs to be linked in this proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to map linked specifications to executed verification evidence.
- `GOV-STANDING-BACKLOG-001` - governs creation and preservation of remediation work items discovered by the audit.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - defines fresh canonical-read and permitted cache discipline that this audit must preserve.
- `GOV-PLATFORM-SOT-REGISTRY-001` - defines the platform SoT registry as the audit starting inventory and authoritative-home declaration surface.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` - provides the harness-state precedent and motivating duplicate-risk class.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires audit findings, classifications, reports, tests, and work items to remain traceable artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires concrete findings and future remediation work to be preserved in governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs candidate/active/deferred/verified states for audit classifications and remediation work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps platform audit work inside the GT-KB root and prevents unqualified Agent Red remediation.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` - governs registry record fields such as `depends_on` and `forbidden_substitutes`.
- `DCL-SOT-READ-HOOK-CONTRACT-001` - governs the hook/doctor read-discipline enforcement surface that the audit must not weaken.

## Prior Deliberations

- `DELIB-202665441` - owner selected registry-governed authoritative homes and derived-cache semantics.
- `DELIB-202665444` - owner selected registry-plus-closure coverage, not sampling, as the audit method.
- `DELIB-202665455` - owner selected risk-first incremental remediation, one violation class per child/remediation WI.
- `DELIB-20260671` and `DELIB-20260672` - prior SoT registry/freshness expansion decisions used by the existing registry and read-discipline implementation.
- `bridge/gtkb-sot-singleton-completeness-umbrella-002.md` - umbrella GO authorizing child proposal filing while preserving child GO gates.
- `bridge/gtkb-sot-singleton-gov-foundation-002.md` - WI-5013 GO requiring canonical GOV foundation before audit work begins.

## Owner Decisions / Input

Owner decisions already captured for this audit:

- `DELIB-202665441`: authoritative homes are registry-governed and derived caches are regenerated, read-only, TTL-bound, provenance-stamped, and non-authoritative.
- `DELIB-202665444`: coverage completeness must use registry-plus-closure scanning.
- `DELIB-202665455`: remediation sequencing is risk-first and incremental.

No new owner decision is required to file this proposal. A separate exact-content owner approval remains required for the `WI-5013` GOV candidate before this audit may begin implementation.

## Requirement Sufficiency

Requirements are sufficient to propose the audit, but implementation has a hard precondition:

- `GOV-SOT-SINGLETON-001` must be recorded in MemBase by `WI-5013`; or
- the implementation-start packet must show equivalent verified GOV-foundation evidence accepted by Loyal Opposition.

Without that precondition, this proposal may receive GO for sequencing but Prime Builder must stop before source, audit, or KB mutation.

## Proposed Audit Architecture

The implementation will add a reusable read-only audit engine, likely under `groundtruth_kb.project.sot_audit`, using `groundtruth_kb.project.sot_registry` as the canonical registry parser and projection reader. The engine must not introduce an alternate registry parser or second authority.

Minimum audit phases:

1. Registry inventory: load every `SoTArtifact` from `config/registry/sot-artifacts.toml` and validate TOML/projection parity with `gt registry validate --json`.
2. Registry closure checks: validate `depends_on`, `forbidden_substitutes`, missing parents, dangling references, and obvious cycles or unresolved authority chains.
3. Whole-repository candidate probes: search for SoT-like authority claims, current-state readers, duplicate field clusters, persistent generated/cache outputs, and registry substitutes.
4. Candidate classification: classify every candidate as `registered_sot`, `permitted_derived_cache`, `non_sot_reference`, `registry_gap`, or `duplicate_sot_violation`.
5. Evidence manifest: write a deterministic audit report with commands, inspected classes, negative evidence, and classification rationale.
6. Remediation filing: for each confirmed violation class, either link an existing covering WI (for example WI-5012 for the dispatcher instance) or create exactly one remediation WI with a linked test.

## Out Of Scope

- No GOV formalization; that is `WI-5013`.
- No doctor/release guard implementation; that is `WI-5015`.
- No direct remediation of duplicate-SoT violations.
- No dispatch selection-binding, cost objective, or self-optimization work; that remains in `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION` / `WI-5012`.
- No credential lifecycle, production deployment, destructive cleanup, or out-of-root dependency.

## Specification-Derived Verification Plan

| Specification | Verification evidence required in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show latest child thread status is `GO` before implementation start and include implementation-start packet evidence. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, work item, and JSON `target_paths` remain parseable. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-sot-singleton-coverage-audit --json`; expected missing required/advisory specs are empty. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this table into the implementation report with executed commands and observed results. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Verify the audit does not read generated caches as authority and classifies cache candidates by declared freshness metadata. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Run `gt registry validate --json`; expected `in_sync: true` before and after audit work. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | Verify the dispatcher/harness duplicate instance is classified as an existing covered violation delegated to WI-5012 rather than silently accepted. |
| `GOV-STANDING-BACKLOG-001` | Verify each confirmed violation has exactly one new or existing covering remediation WI and linked test. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify audit findings, classifications, remediation WIs, and reports are durable artifacts and not chat-only notes. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all mutated files remain under `E:\GT-KB` and adopter remediation is not performed inline. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-READ-HOOK-CONTRACT-001` | Verify registry fields and read-discipline hooks are not weakened by audit implementation. |

Initial regression command surface:

```text
python -m pytest groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py groundtruth-kb/tests/test_sot_duplicate_audit.py platform_tests/scripts/test_check_sot_registry_completeness.py -q --tb=short
```

## Risk / Rollback

Primary risk is false-positive audit scope: a platform-wide closure scan can mistake explanatory prose, generated views, or historical bridge/audit trails for duplicate authority. The implementation must classify candidates explicitly and preserve negative evidence.

Second risk is sequencing drift. This proposal can be reviewed now, but implementation must wait for `WI-5013` to make the singleton GOV canonical.

Rollback is a normal source/test/report revert for the audit engine plus governed retraction or supersession of any remediation WIs filed from false-positive findings. Bridge files remain append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-sot-singleton-coverage-audit`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat`: this work introduces a reusable coverage-complete duplicate-SoT audit capability and durable audit report surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
