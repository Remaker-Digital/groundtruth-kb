NEW

# WI-4870 - Auto-Retire Stranded GO PAUTH

bridge_kind: prime_proposal
Document: gtkb-wi4870-auto-retire-stranded-go-pauth
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T02:01:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4870

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_auto_retire_on_resolve.py", "platform_tests/scripts/test_auto_retire_on_verified.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_project_verified_completion_scanner.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4870 captures a live-pipeline reliability defect: automatic project retirement can strand an open latest-`GO` bridge thread whose covering PAUTH belonged to the retired project. When a headless Prime Builder later tries to start implementation, `scripts/implementation_authorization.py begin` fails because the project authorization is not attached to an active project. The result is a dead-end GO thread that looks PB-actionable to the dispatcher but cannot create an implementation-start packet.

The implementation should prevent or explicitly reconcile that state. Candidate approaches are: defer auto-retirement when the project has active non-terminal GO implementation threads, tolerate a retired-project PAUTH only when there is an active successor membership and explicit reconciliation evidence, or route stranded GO threads into a governed holding/re-home path. The narrow expected fix should be conservative: fail visibly rather than silently implementing under stale project authority, and add regression tests that reproduce the retired-project/GO-thread begin failure.

This proposal does not authorize broad project re-homing, bulk status mutation, or direct implementation of any already in-flight GO. It only authorizes the source/test changes needed to keep future auto-retirement from creating unimplementable bridge states.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires bridge `GO`, implementation-start authorization, implementation report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the broad Phase 2 PAUTH includes WI-4870 and bounds this proposal.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge lifecycle or project-authorization checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - header binds proposal to project authorization and WI.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing project/bridge requirements before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map auto-retire and implementation-start behavior to tests.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - headless workers must encounter deterministic governed enforcement rather than a hidden dead end.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher PB routing must not be handed bridge work that cannot create a valid implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - project lifecycle repair must remain GT-KB-rooted and not depend on adopter application state.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve traceability across WI, PAUTH, bridge, tests, report, and final disposition.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner approved the broad Phase 2 PAUTH including WI-4870.
- WI-4870 backlog row - records the observed WI-4537 re-home failure where `implementation_authorization.py begin` failed with a retired/unattached PAUTH.
- Existing auto-retirement tests for WI-4807/WI-4741 - relevant regression surfaces for project retirement on resolve and VERIFIED.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` and active authorization `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`. No fresh owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. The backlog row names the failure, the implementation-start error, the candidate fix classes, and the live-pipeline impact. Implementation must select the least risky fix and explain why it preserves project lifecycle governance.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Auto-retirement does not strand active GO work | Add project lifecycle tests where a project has terminal member rows plus an open latest-`GO` bridge thread and assert auto-retire defers or records a visible exclusion. |
| Implementation-start cannot silently use stale PAUTH authority | Extend `test_implementation_authorization.py` with retired-project/active-successor or unreconciled-retired cases, expecting deterministic allow/deny behavior. |
| Backlog resolve/VERIFIED paths preserve retirement safety | Extend `test_auto_retire_on_resolve.py` and `test_auto_retire_on_verified.py` so update/finalization paths share the same non-terminal GO guard. |
| Re-home/holding behavior is explicit if implemented | Add tests for any successor-project or holding-project metadata, including project authorization and bridge-thread evidence requirements. |
| Bridge lifecycle is preserved | Implementation must run only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4870-auto-retire-stranded-go-pauth`. |

Minimum expected verification commands:

```text
python -m pytest platform_tests/scripts/test_auto_retire_on_resolve.py platform_tests/scripts/test_auto_retire_on_verified.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4870-auto-retire-stranded-go-pauth --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4870-auto-retire-stranded-go-pauth
```

## Risk / Rollback

Risk is blocking legitimate project completion too aggressively or weakening implementation-start PAUTH checks. Keep behavior fail-closed, require explicit reconciliation evidence for any tolerated retired-project PAUTH, and roll back as one commit if project retirement or authorization tests regress.

## Bridge Filing

This proposal is filed as the first numbered bridge file for `gtkb-wi4870-auto-retire-stranded-go-pauth`; no prior version is deleted or rewritten.

## Recommended Commit Type

fix - prevent automatic project retirement from stranding implementable GO threads.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
