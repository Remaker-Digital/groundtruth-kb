REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder session; collaboration_mode=Default; approval_policy=never; cwd=E:/GT-KB

# Implementation Proposal - Bridge scan helpers omit NO-ACTION status parsing

bridge_kind: prime_proposal
Document: gtkb-wi5068-no-action-scan-helper-parser
Version: 002
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5068

target_paths: [".codex/skills/bridge/helpers/scan_bridge.py", ".claude/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Note

This version replaces Version 001. The only change is proposal hygiene: remove a literal obsolete aggregate-artifact mention and other incidental path-like prose so applicability target extraction is limited to the machine-readable target_paths declaration above.

## Summary

Repair the bridge scan-helper status parser so latest NO-ACTION numbered bridge files are recognized by Codex and Claude helper scans, preventing already-disposed advisory threads from remaining Prime Builder-actionable.

## Claim

Prime Builder proposes a narrow reliability fast-lane defect fix for WI-5068. The current Codex and Claude scan helper copies import a disposition matrix where NO-ACTION is a real latest-status disposition, but their status-recognition regexes omit that token. The managed template helper already recognizes NO-ACTION, and focused preflight coverage currently fails on this exact parser drift.

## Requirement Sufficiency

Existing requirements are sufficient. This proposal does not add a new public API, CLI command, dispatcher policy, or bridge lifecycle status. It aligns the harness helper parsers with the already-governed bridge status matrix and preserves the normal bridge GO, implementation-start, report, and VERIFIED gates.

Fast-lane eligibility under GOV-RELIABILITY-FAST-LANE-001:
- Origin is defect: current helper parsing contradicts the canonical status and disposition matrix.
- No new behavior beyond removing the defect: NO-ACTION is already a governed bridge status.
- No new or revised requirement is needed.
- The implementation is small and single-concern.

## In-Root Placement Evidence

All target paths are inside the GT-KB project root. No Agent Red or external project files are in scope.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - requires role-correct bridge status handling and prevents Prime Builder from treating latest LO or terminal dispositions as actionable implementation work.
- GOV-RELIABILITY-FAST-LANE-001 - authorizes small defect and reliability fixes under the standing reliability fast-lane project membership while preserving bridge review and verification.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - requires live project authorization, project, work item, and target-path metadata.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - requires concrete specification linkage in implementation proposals.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - requires spec-derived verification evidence before VERIFIED.
- ADR-CROSS-HARNESS-PARITY-001 - requires behavioral parity or an owner-approved typed waiver for harness-observable capabilities.
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 - requires this proposal's Cross-Harness Disposition section because skill-helper harness surfaces are targeted.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - keeps this platform bridge-helper work inside GT-KB and outside adopter application scope.

## Prior Deliberations

- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - standing owner decision for small reliability and defect fixes under PROJECT-GTKB-RELIABILITY-FIXES.
- No prior deliberation was found for this exact helper-regex drift.

## Owner Decisions / Input

- PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING - active project authorization covering WI-5068 by project membership.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - owner-approved fast-lane decision behind the standing authorization.
- No new owner decision is requested for this proposal.

## Proposed Scope

- Update the Codex and Claude bridge scan helper status recognizers to include NO-ACTION consistently with the imported disposition matrix.
- Keep the fix limited to parser/status recognition and focused regression coverage.
- Do not change bridge routing policy, dispatcher configuration, project authorization semantics, or status ownership.
- Preserve the managed template helper as the already-correct reference unless verification shows a parity gap.

## Cross-Harness Disposition

Applicable harness-observable surfaces:
- Codex: the Codex bridge scan helper must recognize NO-ACTION as a latest status and apply the same status-disposition matrix used by the runtime helper.
- Claude: the Claude bridge scan helper must recognize NO-ACTION as a latest status and apply the same status-disposition matrix used by the runtime helper.

Parity declaration:
- Behavioral parity is required and intended between Codex and Claude for this bridge scan-helper behavior: given the same numbered bridge thread whose latest file begins with NO-ACTION, both helpers must report latest_status=NO-ACTION, must not leave an older ADVISORY version visible as Prime Builder-actionable, and must classify the latest file according to the canonical role-disposition matrix.
- No owner-approved typed waiver is requested.

Non-applicable harnesses for this proposal:
- Ollama and OpenRouter dispatch through provider shim review flows rather than these local skill-helper scan files.
- Antigravity and Cursor do not have target_paths in this proposal. Any future equivalent helper surface discovered for those harnesses would require its own parity disposition or target-path expansion.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Run focused scan-helper tests proving a latest NO-ACTION status is parsed and role actionability no longer falls back to older ADVISORY files. |
| GOV-RELIABILITY-FAST-LANE-001 | Confirm the implementation is a small defect-only parser/status fix with no public API, dispatcher policy, or project authorization expansion. |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Re-run bridge applicability preflight for this proposal and confirm the live PAUTH, project, and WI metadata remain valid. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Re-run ADR and DCL clause preflight for this proposal and confirm no blocking linkage gaps. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Implementation report must include the failing-then-passing focused pytest evidence. |
| ADR-CROSS-HARNESS-PARITY-001 | Verify Codex and Claude helper copies carry equivalent NO-ACTION parser behavior. |
| DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 | Confirm the proposal retains this Cross-Harness Disposition section and implementation does not introduce unwaived harness asymmetry. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Confirm all modified paths remain in-root platform helper and test paths and no adopter application files are touched. |

## Acceptance Criteria

- A latest NO-ACTION file in a numbered bridge thread is parsed as latest_status=NO-ACTION.
- Prime Builder scans no longer surface older ADVISORY versions when a later NO-ACTION disposition exists.
- Loyal Opposition scans classify the latest NO-ACTION according to the canonical disposition matrix.
- Codex and Claude helper behavior remains equivalent for the status parser path.

## Risks / Rollback

Risk is low because the change is limited to status-recognition and regression coverage. The main risk is unintentionally widening actionability beyond the canonical disposition matrix; focused tests must guard against that.

Rollback is a revert of the source and test changes. Bridge files and MemBase records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

The implementation is limited to the three paths declared in target_paths.

## Recommended Commit Type

fix
