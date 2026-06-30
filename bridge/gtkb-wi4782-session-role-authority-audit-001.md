NEW
author_identity: prime-builder/codex-auto-builder
author_harness_id: A
author_session_context_id: 019f18f9-7b2e-7961-8509-1327995b00db
author_model: gpt-5-codex
author_model_version: 2026-06-30
author_model_configuration: Codex Desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access; shell=powershell; resolved_role=prime-builder
author_metadata_source: Codex automation runtime environment

# Implementation Proposal - Phase 1 - Exhaustive deterministic audit (lint) of all surfaces for registry-as-authority-beyond-dispatcher and durable-role terminology; categorized file:line registry

bridge_kind: prime_proposal
Document: gtkb-wi4782-session-role-authority-audit
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4782

target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-wi4782-session-role-authority-audit.md", ".gtkb-state/role-authority-audit/wi4782-session-role-authority-audit.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a report-only audit slice for WI-4782 to enumerate registry-authority and durable-role terminology drift before any source/rule cleanup.

Work item description: Reusable deterministic scan over .claude/rules, CLAUDE.md, AGENTS.md, .cursor, .codex, .agent, .api-harness, config/agent-control, groundtruth-kb/templates, hooks, scripts, skills. Categorize V1 (registry leak into non-dispatcher gates), V2 (init marker non-propagation), V3 (durable-role terminology), V4 (enumerated-override backwards framing); emit file:line + CONTRADICTS/SUPPORTS. Doubles as the Phase 4 guard.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4782` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-wi4782-session-role-authority-audit.md`, `.gtkb-state/role-authority-audit/wi4782-session-role-authority-audit.json`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-SESSION-ROLE-RESOLUTION-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-20266540` - NO-GO: WI-4783 Session Role Gate Fallback Purge Blocker Response
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ENFORCEMENT-GAP` - Owner determination - cross-harness behavioral parity is a required, enforced invariant; current enforcement (registry-conformance) misses unregistered single-harness changes
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - Owner authorization: implement the cross-harness parity program (WI-4865)
- `DELIB-20266285` - Slice 6 batch-waiver of cross-harness parity harness-surface-difference hooks
- `DELIB-20266112` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4782`.

## Proposed Scope

- Run a deterministic, repository-root-contained audit for registry-as-authority-beyond-dispatcher language and durable-role terminology across startup/rule/config/harness surfaces.
- Classify each finding as current defect, false positive, retired/historical context, or follow-on implementation candidate without editing source/config/rules.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Report explicitly checks that non-dispatcher enforcement gates are not treating harness-registry role as authority. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Report maps findings to durable-dispatch versus transcript-interactive authority split and identifies stale terminology. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Proposal cites active Harness Parity Phase 2 PAUTH and keeps implementation to report/runtime evidence targets. |

## Acceptance Criteria

- A categorized report lists file:line evidence and recommended disposition for every credible match class.
- No source, test, config, rule, MemBase, or harness-state mutation occurs in this slice.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-wi4782-session-role-authority-audit.md`
- `.gtkb-state/role-authority-audit/wi4782-session-role-authority-audit.json`

## Recommended Commit Type

`feat`
