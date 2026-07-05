NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

# WI-4849 GO Claim Preempts Lingering LO Draft - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4849-go-claim-preempts-lingering-lo-draft
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-002.md
Approved proposal: bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4849-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4849
Recommended commit type: fix:

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

## Implementation Claim

Implemented the approved work-intent claim preemption repair. `scripts/bridge_work_intent_registry.acquire()` now computes the incoming claim kind before resolving holder conflicts, preserves the existing Prime-only role guard for all `go_implementation` claims, and permits replacement only when the incoming claim is `go_implementation` and the existing active holder is not already a `go_implementation` holder.

This closes the GO handoff defect where a lingering non-GO draft/review claim could block an eligible Prime session from acquiring the implementation claim after Loyal Opposition returned `GO`. Active peer `go_implementation` claims remain exclusive. Non-Prime GO attempts still fail the existing role-eligibility guard. `scripts/implementation_authorization.py` did not require code changes; WI-4996 begin-time collision/target-path protections remain intact.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-SPEC-RELEVANCE-CLOSURE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. This implementation stays within `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4849-BATCH-A2-20260705`.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorized continuing the high-priority reliability queue through governed bridge work.
- `bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-001.md` - approved proposal.
- `bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-002.md` - Loyal Opposition GO verdict.
- WI-4534 role-eligibility lineage - preserved by keeping `_resolve_go_implementation_eligibility()` ahead of the preemption write.
- WI-4996 begin-time overlap guard - preserved by leaving `scripts/implementation_authorization.py` unchanged and running its full test file.

## Specification-Derived Verification Plan

| Governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_go_impl_preempts_lingering_non_go_draft_claim` and `test_claim_go_implementation_preempts_lingering_draft_claim` build live versioned bridge files, transition latest status from `NEW` to `GO`, and prove the eligible Prime `go_implementation` claim replaces the lingering draft. |
| `DCL-SPEC-RELEVANCE-CLOSURE-001` | `test_go_impl_does_not_preempt_peer_go_implementation_claim` and `test_claim_go_implementation_refuses_peer_go_holder` prove the specific fix does not weaken peer implementation exclusivity. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | The new direct registry test starts with a Loyal Opposition draft claim and then uses a separate Prime dispatch session to acquire the GO implementation claim. |
| `GOV-SESSION-ROLE-AUTHORITY-001` carried by WI-4534 lineage | `test_lo_dispatch_cannot_upgrade_own_draft_after_go` proves a Loyal Opposition session cannot upgrade its own draft after the thread becomes `GO`; the role guard remains in front of the preemption write. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start authorization packet was issued successfully at `2026-07-05T22:14:50Z`, latest status `GO`, packet hash `sha256:55e0a55a209a3d55efb316ae514cd3ebf185da44b2332e2c79ddf97c4779f194`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full required pytest set plus both Ruff gates were executed and passed. |

## GO Advisory Disposition

- A1: Preserved WI-4996 begin-time guard; `scripts/implementation_authorization.py` was not modified and its full regression file passed.
- A2: Chosen behavior is explicit: non-Prime GO attempts hit the existing `WorkIntentRegistryError` role guard before any preemption write; peer GO implementation conflicts by Prime sessions still return `False`.
- A3: `_claim_values()` is now computed once inside the lock and reused for both the preemption predicate and the final insert.
- A4: Added an explicit regression proving an LO session cannot upgrade its own draft after the thread becomes `GO`.

## Commands Run

```text
python scripts\bridge_claim_cli.py claim gtkb-wi4849-go-claim-preempts-lingering-lo-draft --session-id 019f3170-d706-77d3-b3e1-be39d47f3eda --ttl-seconds 3600
python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4849-go-claim-preempts-lingering-lo-draft --session-id 019f3170-d706-77d3-b3e1-be39d47f3eda
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_work_intent_role_eligibility.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\bridge_work_intent_registry.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_work_intent_role_eligibility.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\bridge_work_intent_registry.py scripts\implementation_authorization.py platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_implementation_authorization.py platform_tests\scripts\test_work_intent_role_eligibility.py
```

## Observed Results

- Claim acquired successfully for session `019f3170-d706-77d3-b3e1-be39d47f3eda`; latest bridge status `GO`; implementation deadline `2026-07-05T22:44:36Z`.
- Implementation authorization begin succeeded; proposal file `bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-001.md`, GO file `bridge/gtkb-wi4849-go-claim-preempts-lingering-lo-draft-002.md`, requirement sufficiency `sufficient`.
- Pytest: `148 passed, 1 warning in 27.48s`. The warning is the existing `PytestConfigWarning: Unknown config option: asyncio_mode`.
- Ruff check: `All checks passed!`
- Ruff format check: `5 files already formatted`

## Files Changed

- `scripts/bridge_work_intent_registry.py` - adds the narrow lingering-draft preemption predicate and reorders incoming claim-kind calculation ahead of holder conflict handling.
- `platform_tests/scripts/test_bridge_claim_cli.py` - adds CLI coverage for draft preemption and peer GO holder refusal.
- `platform_tests/scripts/test_work_intent_role_eligibility.py` - adds direct registry coverage for LO draft preemption by Prime, peer GO exclusivity, and LO self-upgrade rejection.

Authorized target paths also included `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py`; they were intentionally left unchanged and verified.

## Risk And Rollback

Residual risk is low. The only newly allowed replacement is incoming `go_implementation` over an existing non-GO draft claim, and the existing Prime role guard still runs before the replacement write. Rollback is a normal revert of the three changed files; no schema, KB, bridge-history, or dispatcher-routing mutation was performed.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications, GO advisory conditions, and executed command evidence.
2. Return `VERIFIED` if satisfied, otherwise return `NO-GO` with concrete findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
