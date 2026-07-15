NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f664e-c30a-7a21-aac0-877b56e5e9fe
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; Prime Builder; collaboration_mode=Default

# Implementation Proposal - Implement SPEC-INTAKE-8161dc: Advisory Bridge Authority And Initiation Semantics

bridge_kind: prime_proposal
Document: gtkb-advisory-proposal-envelope-scaffold-implementation
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-ENVELOPE-SCAFFOLD-COMBINED-20260715
Project: PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-ENVELOPE-SCAFFOLD
Work Item: WI-AUTO-SPEC-INTAKE-8161DC

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "config/agent-control/activity-disposition-profiles.toml", "config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement the advisory proposal envelope scaffold requirement from SPEC-INTAKE-8161dc by teaching generated role/startup, deliberation, and build prompt/envelope surfaces that Advisory Proposals are governed bridge artifacts, ADVISORY is non-dispatchable and not implementation approval, workers access/progress advisories through governed bridge intake/disposition, and dropbox files are non-canonical session evidence only.

Work item description: _No work item description supplied._

## Claim

Prime Builder proposes a bounded implementation slice for `WI-AUTO-SPEC-INTAKE-8161DC` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`, `config/agent-control/activity-disposition-profiles.toml`, `config/agent-control/SESSION-STARTUP-INDEX.md`, `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`, `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`, `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`.

## Specification Links

- `SPEC-INTAKE-8161dc` - auto-linked governing or work-item specification.
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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266027` - Verdict
- `DELIB-20266057` - Loyal Opposition Review - WI-22C078 Attested Role Eligibility Test Guard
- `DELIB-2372` - Loyal Opposition Verification - Core Spec Intake Default Slice 1
- `DELIB-202665827` - Verdict Summary
- `DELIB-20261578` - Loyal Opposition Review - Core Spec Intake Default REVISED-2

## Owner Decisions / Input

- `DELIB-20260715-ADVISORY-PROPOSAL-ENVELOPE-SCAFFOLD-COMBINED-PROPOSAL` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-ADVISORY-PROPOSAL-INTAKE-WORKFLOW-ENVELOPE-SCAFFOLD-COMBINED-20260715` - active project authorization covering `WI-AUTO-SPEC-INTAKE-8161DC`.

## Proposed Scope

- Implement WI-5263 role/startup scaffold wording for Advisory Proposal bridge authority, access, non-approval semantics, and dropbox non-authority.
- Implement WI-5264 deliberation/build activity envelope profile wording for Advisory Proposal progression and Loyal Opposition future-work initiation semantics.
- Implement WI-5265 executable assertion coverage tying TEST-11408, TEST-11418, TEST-11419, and TEST-11420 to the generated prompt/envelope surfaces.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-8161dc` | Run the new advisory proposal envelope scaffold assertion test plus targeted prompt/envelope checks; TEST-11408, TEST-11418, TEST-11419, and TEST-11420 must map to executable coverage. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability preflight and verify bridge proposal/review state is read from TAFE plus numbered bridge files, not retired aggregates. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live applicability preflights must report no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must execute spec-derived tests and map every linked spec to observed passing evidence before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance and live preflight must accept Project Authorization, Project, Work Item, and target_paths metadata. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run implementation_authorization begin after GO to prove the PAUTH is active, current, tied to the project, and does not bypass target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start must fail before GO and pass only after GO with approved target paths; implementation report must preserve this evidence. |

## Acceptance Criteria

- Generated role/startup prompt surfaces contain the Advisory Proposal semantics required by SPEC-INTAKE-8161dc.
- Deliberation and build activity envelope prompt packages contain the same required Advisory Proposal semantics and progression guidance.
- Executable assertion coverage fails if any required surface omits bridge authority, access path, non-dispatchable/non-approval semantics, Loyal Opposition future-work initiation, or dropbox non-authority wording.
- Protected edits do not start until Loyal Opposition GO and implementation-start authorization succeeds.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `config/agent-control/activity-disposition-profiles.toml`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py`

## Recommended Commit Type

`feat`
