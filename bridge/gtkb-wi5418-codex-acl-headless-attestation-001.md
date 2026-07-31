NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined PB role; no direct harness contact

# Implementation Proposal - Make Codex .codex ACL attestation compatible with the active sandbox identity model

bridge_kind: prime_proposal
Document: gtkb-wi5418-codex-acl-headless-attestation
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5418

target_paths: ["scripts/repair_codex_dotdir_acl.ps1", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_codex_dotdir_acl_repair.py", "platform_tests/scripts/test_repair_codex_dotdir_acl.py", "platform_tests/scripts/test_verify_codex_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair Codex ACL attestation so the required no-window subprocess path works under both Windows PowerShell and PowerShell 7, reports real ACL defects instead of module-load noise, and preserves exact least-privilege Deny-only remediation before WI-5310 proof renewal.

Work item description: The read-only Codex dispatcher verifier currently exits 1 with codex_dotdir_acl_ok=false: 218 checked entries all report errors, the current interactive identity has no explicit allow, CodexSandboxUsers cannot be resolved, risky_deny_count is zero, and needs_repair=true. Because the opt-in repair path only removes recognized risky Deny ACEs, it cannot repair this state. Diagnose the supported current Codex sandbox identity and inherited ACL contract; make Check mode non-mutating, bounded, and actionable; pass healthy least-privilege ACLs without requiring a nonexistent legacy group; continue to fail closed on actual unreadable paths or risky denies; preserve private-desktop/no-window dispatch and never disable A or the bridge as remediation. Evidence: scripts/verify_codex_dispatch.py --json at 2026-07-17T02:20Z and WI-5310 bridge version 008 F1.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5418` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/repair_codex_dotdir_acl.ps1`, `scripts/verify_codex_dispatch.py`, `platform_tests/scripts/test_codex_dotdir_acl_repair.py`, `platform_tests/scripts/test_repair_codex_dotdir_acl.py`, `platform_tests/scripts/test_verify_codex_dispatch.py`.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ISOLATION-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202665686` - Loyal Opposition Review Verdict — NO-GO
- `DELIB-202665687` - Loyal Opposition Review Verdict — NO-GO
- `DELIB-202665764` - Verdict
- `DELIB-202666255` - Loyal Opposition Proposal Review - WI-5250 Codex A Dispatch Readiness
- `DELIB-202665690` - Loyal Opposition Review: gtkb-wi4978-helper-compliance-audit-chokepoint-021

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5418`.

## Proposed Scope

- Make ACL read, write, and local sandbox-identity resolution independent of PowerShell module auto-loading when Windows PowerShell is launched with CREATE_NO_WINDOW, while preserving PowerShell 7 behavior.
- Keep Check mode strictly read-only and collapse launcher-capability failure into a bounded actionable diagnostic rather than one false error per descendant.
- Keep Apply mode opt-in and idempotent: remove only explicit non-inherited Deny ACEs carrying risky write, modify, delete, permission, or ownership rights; preserve unrelated rules, owner/group, and inheritance.
- Prove the verifier launcher remains no-window and that real risky Deny ACEs are visible under the same subprocess flags used in production.
- Sequence this shared verifier/test repair before any WI-5310 revision or proof renewal; do not change harness eligibility, dispatcher/TAFE routing, leases, model allowances, or live workers.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Integration tests exercise the exact production no-window launcher against supported Windows PowerShell and PowerShell 7 ACL/identity paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The repair remains behind project PAUTH, independent GO, matching claim, implementation-start, report, and independent verification gates. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests prove the native Windows fallback stays hidden and functionally equivalent across available PowerShell hosts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Verifier tests prove readiness reflects real ACL state and cannot certify A while risky Deny or unreadable-path defects remain. |
| `GOV-HARNESS-ISOLATION-001` | Review confirms no direct harness contact or cross-harness state mutation is introduced. |

## Acceptance Criteria

- The production no-window Windows PowerShell path reads the .codex ACL without Microsoft.PowerShell.Security or LocalAccounts auto-load failures, or fails once with an explicit capability diagnostic before descendant scanning.
- The same no-window probe under PowerShell 7 remains compatible and reports the same risky-Deny classification.
- Check mode makes no ACL mutation and reports actual risky Deny entries; Apply removes only those entries and a post-Check is clean while required current-user and Codex sandbox access remains.
- verify_codex_dispatch no longer reports hundreds of synthetic unreadable entries caused by its own launcher and remains fail closed on genuine ACL defects.
- Focused ACL and Codex verifier tests pass; no console window, dispatcher-state, TAFE, eligibility, lease, or live-worker mutation occurs.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/repair_codex_dotdir_acl.ps1`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_codex_dotdir_acl_repair.py`
- `platform_tests/scripts/test_repair_codex_dotdir_acl.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

## Recommended Commit Type

`feat`
