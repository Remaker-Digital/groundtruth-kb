NEW

# Phase-1 Ollama Governance Implementation Child

bridge_kind: prime_proposal
Document: gtkb-ollama-integration-phase-1-governance-impl
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Project: PROJECT-GTKB-OLLAMA-INTEGRATION
Project Authorization: PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4324
work_item_ids: [WI-4324, WI-4325]
parent_bridge: gtkb-ollama-integration-phase-1
parent_status: GO@-004
responds_to: bridge/gtkb-ollama-integration-phase-1-006.md

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-pb-2026-06-05T19-08Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Prime Builder, workspace-write, approval-policy never

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-06-05-ADR-OLLAMA-HARNESS-ADOPTION-001.json", ".groundtruth/formal-artifact-approvals/2026-06-05-DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001.json", ".groundtruth/formal-artifact-approvals/2026-06-05-DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001.json", ".groundtruth/formal-artifact-approvals/2026-06-05-DCL-OLLAMA-TOOL-PARITY-GATE-001.json", ".groundtruth/formal-artifact-approvals/2026-06-05-GOV-HARNESS-ONBOARDING-CONTRACT-001.json", ".groundtruth/formal-artifact-approvals/2026-06-05-canonical-terminology-ollama-narrative.json", ".groundtruth/formal-artifact-approvals/2026-06-05-operating-model-ollama-narrative.json", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", "platform_tests/scripts/test_ollama_governance_artifacts.py"]

requires_verification: true
implementation_scope: governance_artifact_insertion

## Summary

This is Child 4 of 4 under the Phase-1 Ollama integration umbrella. It executes WI-4324 and WI-4325, the governance implementation work that the parent umbrella and the Loyal Opposition NO-GO at `bridge/gtkb-ollama-integration-phase-1-006.md` identify as missing.

The already VERIFIED children cover foundation, shim/routing, and verification/doctor behavior. This child covers only the remaining governance artifacts: five formal spec inserts, three canonical glossary entries, and one operating-model status update for Ollama as a registered, partial, no-active-role harness surface.

This proposal does not claim that approval packets already exist. It explicitly keeps both formal spec inserts and protected narrative edits packet-gated. If matching approval packets are not available during implementation, Prime Builder must stop before mutating `groundtruth.db` or protected narrative files and file a status update rather than bypass the gate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking): files a NEW versioned bridge proposal and relies on live `bridge/INDEX.md` as queue authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking): this section cites the governing specs for the proposal and implementation report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking): requires post-implementation spec-to-test mapping and executed evidence before VERIFIED.
- `GOV-ARTIFACT-APPROVAL-001` (blocking): formal spec inserts remain blocked until matching approval packets are present and validated.
- `DCL-CONCEPT-ON-CONTACT-001` (blocking): the new Ollama concepts are added to canonical terminology before parent closure is refiled.
- `GOV-HARNESS-ROLE-PORTABILITY-001` (blocking): narrative edits must preserve harness D as registered with no active role or dispatch target in Phase 1.
- `GOV-SESSION-ROLE-AUTHORITY-001` (blocking): the operating-model update must not create an alternate session-role authority for Ollama.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (blocking): cites the active project PAUTH containing WI-4324 and WI-4325 and the relevant mutation classes.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` (advisory): the PAUTH includes `membase_spec_insert` and `protected_narrative_file`, but does not bypass packet gates.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (blocking): the project PAUTH cites approved framing specs and this child carries the missing Phase-1 governance specs.
- `GOV-STANDING-BACKLOG-001` (blocking): WI-4324 and WI-4325 are canonical open backlog rows under `PROJECT-GTKB-OLLAMA-INTEGRATION`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking): all target paths remain under `E:\GT-KB`; no adopter application path is touched.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (advisory): implementation must verify live absence/presence from current files and MemBase, not cached reports.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory): the child preserves decisions, specs, approval packets, rule updates, and verification as durable artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory): work crosses into specifications, glossary, operating model, and backlog closure, so it is artifact-routed.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory): new/changed artifacts get explicit lifecycle evidence and parent closure remains blocked until VERIFIED.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (advisory): the inserted tool-parity DCL preserves the fail-closed local guard-adapter requirement from the parent revision.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---------|----------|-----------------|--------------|---------------------|
| CQ-SECRETS-001 | Yes | Keep packet paths and bridge text free of credential-shaped content. | Bridge helper credential scan plus staged secret scan before commit. | |
| CQ-PATHS-001 | Yes | Keep every target path under `E:\GT-KB` and avoid adopter application paths. | Bridge applicability preflight and targeted path assertions. | |
| CQ-COMPLEXITY-001 | Yes | Limit implementation code to focused packet validation and readback tests. | Ruff plus focused pytest on the new governance artifact test file. | |
| CQ-CONSTANTS-001 | Yes | Represent expected spec IDs and glossary headings as named test constants. | Ruff check on `platform_tests/scripts/test_ollama_governance_artifacts.py`. | |
| CQ-SECURITY-001 | Yes | Preserve formal and narrative approval packet gates for protected mutations. | Packet validation evidence plus narrative evidence check before commit. | |
| CQ-DOCS-001 | Yes | Update canonical terminology and operating-model text through approved packets. | Focused readback tests assert the exact required entries. | |
| CQ-TESTS-001 | Yes | Add focused tests for spec IDs, glossary entries, operating-model status, and packet references. | Focused pytest command recorded in the implementation report. | |
| CQ-LOGGING-001 | N/A | | | No runtime logging code is introduced by this governance child. |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, scoped Ruff, applicability preflight, and clause preflight before report filing. | Commands and observed outputs captured in the implementation report. | |

## Requirement Sufficiency

The existing requirements are sufficient for filing this child proposal. `DELIB-20260663` records the owner 12-AUQ decision pass for Ollama Phase 1, including Option A, static routing, harness D registered/no-role status, heavy governance, one Phase-1 PAUTH, and procedural plus machine-checkable GOV reach. The parent umbrella revision at `bridge/gtkb-ollama-integration-phase-1-003.md` then defines this exact Child 4 scope, and the GO at `-004` approves the ordered child sequence.

Implementation has a separate sufficiency constraint: mutating formal artifacts or protected narrative files requires exact matching approval packets. This proposal treats packet availability as an implementation-time gate, not as owner input needed for Loyal Opposition to review the plan.

## Prior Deliberations

- `DELIB-20260663` - owner decision record for the 12-AUQ Ollama Phase 1 scope.
- `DELIB-20260679` - parent umbrella GO context after the revised guard-adapter contract.
- `DELIB-20260680` - prior parent umbrella NO-GO requiring fail-closed guard-adapter proof.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - supports keeping harness D out of dispatch in Phase 1.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - supports registered plus empty role-set as an orthogonal state.
- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` - supports local external harness invocation while preserving root boundary.
- `bridge/gtkb-ollama-integration-phase-1-003.md` - operative parent revision defining Child 4.
- `bridge/gtkb-ollama-integration-phase-1-004.md` - Loyal Opposition GO for the parent umbrella.
- `bridge/gtkb-ollama-integration-phase-1-006.md` - Loyal Opposition NO-GO identifying this missing child as the parent closure blocker.

## Owner Decisions / Input

No new owner input is requested for this proposal review.

The following owner decisions from `DELIB-20260663` are directly authoritative: AUQ#1 selected Option A, AUQ#3 selected harness D as registered with no active role, AUQ#4 selected the Phase 1 MVP boundary, AUQ#6 selected full parity tools, AUQ#7 selected heavy governance, AUQ#8 selected one project PAUTH covering all Phase-1 WIs, AUQ#11 selected procedural plus machine-checkable GOV reach, and AUQ#12 selected a flat project shape.

This child does not ask Loyal Opposition to infer or waive owner approval for exact formal/narrative content. The implementation report must cite matching approval packets before claiming any protected mutation.

## Scope and Touchpoints

WI-4324 inserts five MemBase specs through packet-validated formal artifact writes:

- `ADR-OLLAMA-HARNESS-ADOPTION-001`: architecture decision for the Python shim and static routing, with rejected alternatives and the fail-closed guard adapter consequence from parent `-003`.
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001`: schema constraint for `.ollama/routing.toml`.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001`: author/model metadata injection before governed Ollama writes.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: canonical full-parity tool subset with fail-closed GT-KB guard-adapter dispatch for mutating tools.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`: procedural and machine-checkable harness onboarding floor.

The exact spec text should be derived from the original full drafts in `bridge/gtkb-ollama-integration-phase-1-001.md` plus the guard-adapter deltas in `bridge/gtkb-ollama-integration-phase-1-003.md`.

WI-4325 updates the protected narrative artifacts only with matching narrative approval packets:

- `.claude/rules/canonical-terminology.md` adds `ollama`, `routing.toml`, and `task-to-model routing` entries with source citations to `DELIB-20260663` and the verified child bridge chain.
- `.claude/rules/operating-model.md` section 3 records Ollama as a registered, partial Phase-1 harness surface with no active role, no dispatch routing, and no role promotion until a later approved bridge.

## Implementation Plan

1. Re-read live `bridge/INDEX.md`, the full parent thread, and WI-4324/WI-4325.
2. Confirm no existing `Document: gtkb-ollama-integration-phase-1-governance-impl` entry has been inserted by another session.
3. Prepare five formal approval packets and two narrative approval packets with exact post-edit content and `approved_by: owner`.
4. Validate formal packets before inserting specs and validate narrative packets before protected writes.
5. Insert the five specs into `groundtruth.db` through the canonical `KnowledgeDB`/`gt` path, never by direct SQL.
6. Apply protected narrative edits through the protected-write helper or another hook-covered path that verifies the approval packet against the final content.
7. Add focused regression coverage in `platform_tests/scripts/test_ollama_governance_artifacts.py` for the five spec IDs, glossary entries, operating-model status text, and packet-gated evidence references.
8. Run targeted tests, scoped Ruff checks, bridge applicability preflight, and ADR/DCL clause preflight.
9. File a post-implementation report for this child. After Loyal Opposition VERIFIED, refile the parent umbrella closure as `REVISED`.

## Specification-Derived Verification Plan

- WI-4324 formal specs: `gt` or KnowledgeDB readback shows all five spec IDs with expected type/status and verifying assertions.
- Formal packet gate: implementation report cites five packet paths and packet validation results before spec insertion.
- WI-4325 glossary entries: focused test asserts `### ollama`, `### routing.toml`, and `### task-to-model routing` exist with source citations.
- Operating model status: focused test asserts Ollama is described as registered/no-active-role and not a dispatch target.
- Tool-parity DCL: focused test or spec readback asserts `DCL-OLLAMA-TOOL-PARITY-GATE-001` contains fail-closed guard adapter language.
- Project authorization: `gt projects authorizations PROJECT-GTKB-OLLAMA-INTEGRATION --json` shows active PAUTH includes WI-4324/WI-4325 and allowed mutation classes.
- Parent closure blocker: live bridge scan shows governance child latest VERIFIED before parent closure is refiled.
- Cross-cutting gates: `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` pass for the child implementation report.

## Pre-Filing Preflight Subsection

Commands run against this proposal before live INDEX filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-governance-impl --content-file bridge/gtkb-ollama-integration-phase-1-governance-impl-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-governance-impl --content-file bridge/gtkb-ollama-integration-phase-1-governance-impl-001.md
```

Expected result: applicability preflight passes with `missing_required_specs: []`; ADR/DCL clause preflight exits 0 with no blocking gaps.

## Risk and Rollback

Risk: the exact formal and narrative approval packets may not exist yet. The proposal treats that as an implementation-time hard stop rather than a workaround opportunity.

Risk: the parent umbrella contains draft language from both `-001` and `-003`. The implementation must carry the later `-003` guard-adapter delta into the final formal spec text.

Risk: updating operating-model status too early could imply role promotion. The narrative edit must explicitly say registered/no-active-role until a later approved role-promotion bridge.

Rollback:

- If this proposal is NO-GO, no source, database, or protected narrative mutation is required; file a revised proposal.
- If implementation starts and a packet is invalid, stop before mutation and report the packet gap.
- If an inserted spec or narrative edit is later found wrong, use the normal append-only formal/narrative correction path with new approval evidence.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
