NEW

# gtkb-wi4893-daemon-test-provenance-scope-amendment - Add daemon reap regression test scope

bridge_kind: prime_proposal
Document: gtkb-wi4893-daemon-test-provenance-scope-amendment
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-28 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop; formal release hardening worktree

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893

target_paths: ["platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This companion proposal amends only the test target scope for the already-approved WI-4893 dispatcher release-readiness hardening. The approved proposal `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-001.md` and GO `-002.md` authorize the dispatcher source, reset/report, API harness, and most focused tests. During verification, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` failed two existing daemon orphan-reap assertions because the implementation now correctly refuses to reap live PIDs without matching create-time provenance.

The original WI-4893 verification plan explicitly required `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, but that test file was accidentally omitted from the proposal target_paths. This proposal adds only that missing test file so the daemon tests can be updated to assert the new provenance contract instead of the old PID-only behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected test edits require bridge GO and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the companion proposal cites every relevant governing specification for this test-only amendment.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries project authorization, project, work item, and parseable target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the existing WI-4893 implementation report must include the daemon test evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` - daemon cleanup and recovery behavior must be release-ready.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the dispatcher must not present unsafe cleanup behavior.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - cleanup must not terminate by raw PID without provenance.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - daemon/report/reset readiness evidence must be internally consistent.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the scope gap is preserved as a formal bridge amendment instead of an ungoverned test edit.

## Prior Deliberations

- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues block release and require a dispatcher readiness test plan.
- `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-001.md` - original WI-4893 release-readiness proposal.
- `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-002.md` - Loyal Opposition GO for the original source/test scope.
- `bridge/gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap-004.md` - VERIFIED create-time provenance precedent.

## Requirement Sufficiency

Existing requirements are sufficient. This proposal changes no runtime source behavior and adds no new implementation objective; it only authorizes updating one already-required daemon test file to match the approved WI-4893 provenance semantics.

## Verification Plan

After GO, Prime Builder will update only `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` so daemon orphan-reap tests provide matching create-time sidecars before expecting termination and assert that missing/mismatched provenance prevents termination where appropriate.

Required evidence:

```text
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
python -m ruff check platform_tests/scripts/test_gtkb_dispatcher_daemon.py
python -m ruff format --check platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

## Risk / Rollback

Risk is low because the scope is a test-only alignment with already-approved runtime behavior. Rollback is a revert of the companion test update plus the companion bridge chain; it does not alter dispatcher source behavior.

## Recommended Commit Type

Recommended commit type: `test:`
