NEW

# WI-4849 GO Claim Preempts Lingering LO Draft

bridge_kind: prime_proposal
Document: gtkb-wi4849-go-claim-preempts-lingering-lo-draft
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4849-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4849

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

implementation_scope: source/test/governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4849 captures a post-GO handoff defect: after Loyal Opposition files `GO`, a peer LO draft/review work-intent claim can linger until its short TTL expires. Prime Builder then cannot acquire the required `go_implementation` claim for the same slug, so implementation-start is delayed even though the bridge is already approved and the LO claim no longer represents active implementation ownership.

This proposal changes the work-intent acquisition semantics, not the bridge review gate. A latest-`GO` bridge may be claimed by an eligible Prime Builder session as `go_implementation` even when a different session still holds a non-GO draft/review claim for that same slug. Active peer `go_implementation` claims remain exclusive, expired/lapsed cleanup remains unchanged, role eligibility remains fail-closed, and `implementation_authorization.py begin` continues to require the current session to hold the resulting implementation claim before protected mutation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - latest numbered bridge status determines whether a slug is in proposal/review or GO implementation state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the Batch A2 PAUTH permits this bounded source/test fix but does not replace LO review or implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass the live `GO`, work-intent claim, or target-path gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay within the named WI-4849 source/test envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governance surfaces that constrain the change.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map the claim semantics to focused tests and observed command output.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the claim behavior must be harness-neutral because LO and PB may run in different harnesses.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - WI-4849 can close only if tests prove the specific lingering LO draft/review claim case while preserving real peer-implementation exclusion.
- `GOV-STANDING-BACKLOG-001` - the open WI must reach terminal state only with durable bridge and test evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation and verification must read live bridge status and registry state rather than stale summaries.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the repair preserves the defect, decision, bridge proposal, test evidence, and eventual implementation report as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the work item is advanced through bridge artifacts and tests rather than informal session state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the transition from LO `GO` to Prime implementation claim is the lifecycle trigger being repaired.

## Prior Deliberations

- `INTAKE-5a61f299` - claim-gated implementation-start requires holding the GO-implementation claim before editing a GO'd thread's target paths.
- `INTAKE-e7d44d40` - GO-implementation claims are time-boxed with extension behavior; this proposal preserves that exclusivity and timer for real implementation claims.
- `INTAKE-3bf4889e` - LO-controlled dispatch hold context confirms cross-harness claim coordination is intentional, but a completed LO review should not delay Prime implementation after `GO`.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorized continuing Batch A2 high-priority reliability fixes through governed bridge disposition.
- `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json` - approval packet for that owner decision; it is scoped here by PAUTH and live bridge review.
- `WI-4849` backlog text - concrete defect statement observed on WI-4838: a lingering LO draft/review claim blocked Prime implementation-start after independent LO `GO`.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved continuing the high-priority queue through governed implementation/disposition work.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4849-BATCH-A2-20260705` - active Batch A2 authorization for WI-4849 source, tests, and governance evidence.

No additional owner decision is required. This proposal remains subject to Loyal Opposition `GO` and an implementation-start packet before any protected mutation.

## Requirement Sufficiency

Existing requirements sufficient.

The existing bridge/work-intent rules already require a latest `GO`, a Prime-eligible `go_implementation` claim, and a session-local implementation-start packet before protected mutation. WI-4849 identifies a defect in the handoff between LO review claims and Prime GO-implementation claims; no new formal requirement is needed to repair that bounded behavior.

## Proposed Implementation

1. Update `scripts/bridge_work_intent_registry.py` so `acquire()` computes the incoming claim kind from live bridge status before rejecting a different-session holder. If the incoming claim is `go_implementation`, the bridge is latest `GO`, the caller is Prime-eligible, and the existing holder is a non-GO draft/review claim, replace the lingering holder with the GO-implementation claim.
2. Preserve existing denials when the existing holder is an unexpired peer `go_implementation` claim, when the incoming caller is not Prime-eligible for GO implementation, when the latest bridge status is not `GO`, or when the slug/session is invalid.
3. Keep `scripts/implementation_authorization.py begin` coupled to the current session's work-intent claim. If implementation reveals a direct-begin diagnostic needs adjustment, keep it diagnostic-only; do not make `begin` silently mutate or bypass the claim requirement.
4. Add regression coverage for the WI-4849 handoff case and negative controls:
   - a peer draft claim created while a thread is `NEW` no longer blocks a Prime-eligible claim after a later `GO`;
   - an active peer `go_implementation` claim still blocks another Prime session;
   - a non-Prime session cannot use the preemption path to acquire a GO-implementation claim;
   - implementation-start succeeds only after the Prime session holds the resulting GO-implementation claim.

## Cross-Harness Disposition

This is shared bridge plumbing. The source lives under `scripts/` and is used by Claude, Codex, Antigravity, and headless dispatch paths through the same CLI/helpers. No harness-local behavior fork is proposed. Tests must exercise dispatch-style and interactive-style session identifiers where existing fixtures support them.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Claim kind is derived from the live latest bridge status, so only latest `GO` enables GO-implementation preemption. | Focused tests create a `NEW` thread, acquire a peer draft claim, add a later `GO`, then assert Prime claim returns `claim_kind == "go_implementation"`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The fix does not authorize protected mutation; it only allows the correct GO-implementation claim to be acquired. | `platform_tests/scripts/test_implementation_authorization.py` asserts `begin`/claim-block logic succeeds only after the Prime session owns the GO-implementation claim. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | LO and PB session contexts can differ without blocking the post-GO handoff, while non-Prime GO claim attempts fail closed. | `platform_tests/scripts/test_bridge_claim_cli.py` or `platform_tests/scripts/test_work_intent_role_eligibility.py` covers peer-session draft preemption and non-Prime denial. |
| `DCL-SPEC-RELEVANCE-CLOSURE-001` | The regression covers WI-4849's exact lingering LO draft/review shape and negative controls. | Tests assert peer draft is replaceable after GO, peer GO-implementation remains exclusive, and latest non-GO behavior remains unchanged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verification evidence is command-based and repeatable. | Implementation report includes exact pytest and ruff command output. |

Minimum verification commands after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short --basetemp .gtkb-state/pytest-tmp-wi4849
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_work_intent_role_eligibility.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_work_intent_role_eligibility.py
```

## Acceptance Criteria

- A Prime-eligible session can acquire a `go_implementation` claim after LO `GO` even if a different session still holds a non-GO draft/review claim on the slug.
- A different session cannot preempt an active peer `go_implementation` claim.
- A non-Prime session cannot acquire the `go_implementation` claim through the preemption path.
- `implementation_authorization.py begin` still requires the current session to hold the slug's GO-implementation claim and still writes only the normal packet when authorized.
- No bridge files, dispatcher state, KB rows, credentials, deployments, destructive cleanup, or bulk status mutations are changed by the implementation itself.

## Risk / Rollback

Risk is moderate because work-intent claims are concurrency control. The mitigation is a narrow preemption predicate: latest `GO`, incoming `go_implementation`, Prime eligibility, and existing non-GO claim only. Rollback is a single revert of the source/test diff; because this proposal does not mutate schema or durable bridge history, reverting restores the prior exclusive per-slug claim behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4849-go-claim-preempts-lingering-lo-draft`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the eventual diff repairs a concrete post-GO implementation-start handoff defect without adding a new user-facing feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
