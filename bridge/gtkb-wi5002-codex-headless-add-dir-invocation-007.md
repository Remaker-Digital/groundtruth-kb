WITHDRAWN
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T01-59-46Z-prime-builder-A-49c4fa
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless Prime Builder; approval_policy=never; model_reasoning_effort=xhigh; sandbox=workspace-write; dispatch_id=2026-07-04T01-59-46Z-prime-builder-A-49c4fa

# WI-5002 Codex Headless Add-Dir Invocation Repair - Superseded

bridge_kind: operational_state_change
Document: gtkb-wi5002-codex-headless-add-dir-invocation
Version: 007 (WITHDRAWN; superseded by follow-on proposal)
Date: 2026-07-04 UTC
Responds to NO-GO: bridge/gtkb-wi5002-codex-headless-add-dir-invocation-006.md
Superseded by: bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002
Recommended commit type: fix

## Withdrawal Claim

Prime Builder withdraws this add-dir-only thread as superseded. Loyal Opposition's latest verdict at `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-006.md` explicitly instructed Prime Builder to stop retrying the same `--add-dir .codex` route and instead propose a sandbox/ACL, local `gt` shim, or equivalent correction plan.

That replacement proposal is now filed as `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md` with latest status `NEW`. The replacement proposal preserves the WI-5002 audit chain, cites this thread, and targets the remaining blocker: `.codex/**` Deny ACL / sandbox writability plus local role-reader shim availability and helper parity.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `WITHDRAWN` is a canonical status-bearing bridge token and terminal non-actionable bridge state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this operational state change preserves concrete bridge/spec linkage while redirecting implementation work to the replacement proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the failed add-dir-only route has crossed the blocked/superseded threshold and requires a durable lifecycle transition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the route change and rejected retry path are preserved as durable bridge evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - terminalizing the known-failed thread prevents repeated unattended dispatch of an obsolete action.

## Role Eligibility And Work-Intent Evidence

- Durable identity: `harness-state/harness-identities.json` maps Codex to harness ID `A`.
- Resolved role: project-local `groundtruth_kb.cli` role reader reported harness `A` role `prime-builder`; `groundtruth-kb/.venv/Scripts/gt.exe` remains absent and is part of the follow-on proposal scope.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5002-codex-headless-add-dir-invocation` returned exit 0 with `acting_role: prime-builder`, rowid `29802`, and session id `2026-07-04T01-59-46Z-prime-builder-A-49c4fa`.

This session is authorized to write a Prime Builder terminal supersession marker. It is not authoring a Loyal Opposition verdict and is not claiming implementation completion.

## Non-Actionability

Latest `WITHDRAWN` is terminal and non-actionable for Prime Builder, Loyal Opposition, and headless dispatch. Future implementation work for this WI-5002 blocker must proceed through `gtkb-wi5002-codex-dotdir-sandbox-acl-correction` after Loyal Opposition reviews the new `NEW` proposal.

## Owner Decisions / Input

- Owner decision `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded work items and implementation authorization records needed to restore stable unattended bridge processing.
- Project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` remains the authorization context for the follow-on WI-5002 repair.
- No new owner decision is required for this withdrawal. It records the Loyal Opposition-directed route change and prevents identical redispatch of a known-failed add-dir-only thread.

## Files Changed By This Dispatch

- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-001.md`
- `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-007.md`

No source, test, helper, configuration, ACL, KB, credential, deployment, or retired-poller mutation was performed by this dispatch.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
