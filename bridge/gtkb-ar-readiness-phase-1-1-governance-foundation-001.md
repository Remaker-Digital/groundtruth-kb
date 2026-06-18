NEW

# GT-KB Implementation Proposal - Agent Red Readiness Phase 1.1 Governance Foundation

bridge_kind: prime_proposal
Document: gtkb-ar-readiness-phase-1-1-governance-foundation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: automation-agent-red-2026-06-18-phase-1-1
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation Prime Builder session

Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS-AGENT-RED-READINESS-PROGRAM-PHASE-1-ISOLATION-PARTITION-IN-PLACE
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: WI-4654

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/*.json", ".gtkb-state/formal-artifact-content/agent-red-readiness-phase-1-1/*.md", "platform_tests/scripts/test_ar_readiness_phase_1_1_governance_foundation.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements Agent Red Readiness Phase 1.1 for WI-4654. It creates the deferred governance foundation for Agent Red application isolation by recording two formal specs through the governed `gt spec record` path:

1. `ADR-APPLICATION-ISOLATION-CONTRACT-001` - GT-KB applications are isolated execution contexts, not merely folders under `applications/`.
2. `DCL-APP-ROOT-MINIMIZATION-001` - each top-level entry under an application root must be represented in that application's `.gtkb-app-isolation.json` registry with bucket, purpose/tool, and justification metadata.

The implementation scope is narrow: two in-root content drafts, two formal-artifact approval packets, two MemBase spec records, and one focused platform test. It does not change app-root source files, production deployment behavior, runtime write guards, release gates, or the later partition-in-place migration.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this NEW proposal awaits LO review before implementation mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specification surfaces and maps them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header includes Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must carry forward spec-derived tests and command evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4654 is the live MemBase work authority under the Agent Red Readiness project.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active PAUTH covers WI-4654 but does not replace bridge GO or implementation-start evidence.
- `GOV-ARTIFACT-APPROVAL-001` - formal ADR/DCL insertion requires per-artifact approval-packet evidence.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder must preserve owner-visible formal-artifact approval evidence.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - the ADR and DCL become canonical only through the formal-artifact approval path.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the implementation must use approval packets under `.groundtruth/formal-artifact-approvals/` rather than direct DB writes.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` - the formal artifacts are based on owner decisions `DELIB-20265219` and `DELIB-20265220`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the ADR/DCL must reflect the current Agent Red Readiness state and Phase 0 census evidence.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - Agent Red is the reference adopter and conformance target.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - Agent Red lives under `applications/Agent_Red/`; the DCL constrains that in-root application boundary.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the new ADR refines placement into execution-context isolation while preserving the in-root placement rule.
- `.claude/rules/project-root-boundary.md` - all target paths are inside `E:/GT-KB`; no live dependency or output is outside the root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the slice preserves owner decisions as formal artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the slice turns repeated isolation intent into durable governance records.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Phase 0 found the promised formal-artifact slice incomplete, triggering this artifact lifecycle work.

## Prior Deliberations

- `DELIB-20265219` - owner ratified the Agent Red Readiness Program after Phase 0 found isolation enforcement incomplete and found the ADR/DCL absent from MemBase.
- `DELIB-20265220` - owner approved Phase 1 scoping, materialized WI-4653 through WI-4657, and accepted the D-P1a block-list policy direction. WI-4654 is the approved Phase 1.1 slice.
- `DELIB-20261916` - the prior isolation closeout was VERIFIED, but later census evidence showed sub-slices 5 and 6 were not actually complete.
- `bridge/application-isolation-contract-005.md` - prior proposal split formal artifact writes into a later sub-slice and required approval packets before formal writes.
- `bridge/application-isolation-contract-006.md` - LO GO approved only sub-slice 1 and did not approve formal artifact writes.
- `bridge/application-isolation-contract-008.md` - LO VERIFIED sub-slice 1 and left formal-artifact and app-root minimization work as follow-up.
- `DELIB-1402` - downstream partition context: Agent Red specs may apply to GT-KB. This slice creates vocabulary used by WI-4657 but does not perform the partition.

## Owner Decisions / Input

No new owner input is required. `DELIB-20265219`, `DELIB-20265220`, and the active project authorization already approve this Phase 1 scope. The implementation still must generate per-artifact approval packets before formal ADR/DCL insertion, because the PAUTH explicitly forbids formal GOV/ADR/DCL/SPEC insertion without that packet evidence.

## Requirement Sufficiency

Existing requirements sufficient. The owner-approved Phase 1 scoping in `DELIB-20265220`, the active PAUTH, the prior `application-isolation-contract` bridge chain, and the governing specs listed above constrain this slice.

## Proposed Formal Artifact Content

`ADR-APPLICATION-ISOLATION-CONTRACT-001` will be recorded as type `architecture_decision`, status `specified`, title `Application Isolation Contract`. It must include `## Decision`, `## Rationale`, `## Consequences`, and `## Rejected Alternatives`. The decision text will state that application placement under `applications/<name>/` is necessary but insufficient; sessions, local harness configuration, application-root tooling exceptions, runtime configuration, deployable source, and application lifecycle evidence must be scoped to the application root when they govern the application rather than the GT-KB platform.

`DCL-APP-ROOT-MINIMIZATION-001` will be recorded as type `design_constraint`, status `specified`, title `Application Root Minimization`. It must include `## Constraint`, `## Application Scope Vocabulary`, `## D-P1a Block List Policy`, and `## Assertions`. Minimum assertions are:

- `DCL-APP-ROOT-MINIMIZATION-001.A1` - `applications/Agent_Red/.gtkb-app-isolation.json` exists.
- `DCL-APP-ROOT-MINIMIZATION-001.A2` - the registry has `top_level_artifacts` entries and every entry has non-empty `path`, `kind`, and `bucket`.
- `DCL-APP-ROOT-MINIMIZATION-001.A3` - every bucket B entry has non-empty `tool` and `justification`.
- `DCL-APP-ROOT-MINIMIZATION-001.A4` - the DCL content includes the D-P1a bridge-allowed block-list policy for downstream write-guard work.

## Proposed Implementation Steps

1. Confirm no current MemBase specs already exist for `ADR-APPLICATION-ISOLATION-CONTRACT-001` or `DCL-APP-ROOT-MINIMIZATION-001`.
2. Create content draft files under `.gtkb-state/formal-artifact-content/agent-red-readiness-phase-1-1/` for the ADR and DCL.
3. Run `gt spec record --dry-run --json` for each draft with `--owner-presented`, `--auq-id DELIB-20265220`, and concise `--auq-answer` text describing the approved Phase 1.1 slice.
4. Run live `gt spec record` for each artifact after dry-run success. This writes approval packets under `.groundtruth/formal-artifact-approvals/` and inserts the new MemBase records.
5. Add `platform_tests/scripts/test_ar_readiness_phase_1_1_governance_foundation.py` to verify both specs exist, required ADR/DCL sections exist, DCL assertions are present, approval packets validate, and no app-root source/config files changed in this slice.
6. Run focused verification commands and file a post-implementation report for LO verification.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use the bridge helper credential scan and avoid credential literals in proposal, content drafts, tests, and reports. | Helper credential scan plus focused git diff review. | |
| CQ-PATHS-001 | Yes | Keep all outputs under `E:/GT-KB` and restrict implementation writes to declared target paths. | Applicability preflight and post-implementation git diff path review. | |
| CQ-COMPLEXITY-001 | Yes | Limit the slice to two formal records, two content drafts, two approval packets, and one focused platform test. | Focused diff review plus pytest command for the new test. | |
| CQ-CONSTANTS-001 | Yes | Use explicit spec IDs, assertion IDs, and named test constants instead of opaque literals in test code. | Ruff check on the new test file. | |
| CQ-SECURITY-001 | Yes | Make no runtime security behavior changes; use governed `gt spec record` for MemBase writes. | Helper credential scan and git diff path review. | |
| CQ-DOCS-001 | Yes | Preserve ADR/DCL native content drafts and approval packet evidence for later reviewers. | Platform test checks required content sections and packet presence. | |
| CQ-TESTS-001 | Yes | Add a focused platform test for the new ADR/DCL records, DCL assertions, packets, and no app-root file changes. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ar_readiness_phase_1_1_governance_foundation.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | No runtime logging, service telemetry, or observability code changes are in scope. | Git diff path review confirms no runtime logging files changed. | No logging surface is modified by this governance-only slice. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, ruff check, ruff format check, and `gt assert --spec DCL-APP-ROOT-MINIMIZATION-001` after implementation. | Post-implementation report cites commands and observed results. | |

## Spec-Derived Verification Plan

- Bridge/proposal specs: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ar-readiness-phase-1-1-governance-foundation` and require `missing_required_specs: []`.
- Clause gate: run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ar-readiness-phase-1-1-governance-foundation` and require zero blocking gaps.
- Project authorization: after GO, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-ar-readiness-phase-1-1-governance-foundation` before implementation writes.
- Formal artifact gate: run `gt spec record --dry-run --json` for both content files before live insert; the platform test validates approval packets with `groundtruth_kb.governance.approval_packet.validate_packet`.
- Freshness and Agent Red conformance: the platform test verifies recorded ADR/DCL text references the live Agent Red app-root registry path `applications/Agent_Red/.gtkb-app-isolation.json`.
- Focused implementation gates: run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_ar_readiness_phase_1_1_governance_foundation.py -q --tb=short`, `groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_ar_readiness_phase_1_1_governance_foundation.py`, `groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_ar_readiness_phase_1_1_governance_foundation.py`, and `gt assert --spec DCL-APP-ROOT-MINIMIZATION-001`.

## Risk / Rollback

Risk is medium because the slice mutates MemBase and creates formal-artifact approval packets. Blast radius is bounded to two new specification rows, two approval packet files, two in-root content draft files, and one additive platform test. No app source, platform source, hooks, config, deployment, or write-guard behavior changes are in scope.

Rollback is append-only for MemBase: if wording is wrong, file a corrective bridge and use `gt spec update` with a new approval packet rather than editing database history. Git rollback can remove the additive test and content draft files. Approval packets remain audit evidence once used.

## Bridge Filing

This proposal is filed under `bridge/` as `bridge/gtkb-ar-readiness-phase-1-1-governance-foundation-001.md`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the implementation creates two new canonical governance artifacts and a new verification test. Although the work is governance-focused, it adds durable platform capability by making the Agent Red isolation contract testable and formally referencable.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
