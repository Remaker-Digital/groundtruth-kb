WITHDRAWN
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d13f9026-d253-48b6-a61c-451dd5294846
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: prime_proposal
Document: gtkb-wi4804-killswitch-staleness-visibility
Version: 002
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4804
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26

## Withdrawal

This proposal (-001) is WITHDRAWN as a duplicate. A concurrent session (130bf9ae) had already filed an equivalent WI-4804 proposal under a near-identical slug - `bridge/gtkb-wi4804-kill-switch-staleness-visibility-001.md` (note the hyphenated "kill-switch" vs this thread's "killswitch") - which is now GO at `bridge/gtkb-wi4804-kill-switch-staleness-visibility-002.md` (Cursor LO, session cursor-e-20260626-lo-autoproc-3). Both implement the same DELIB-20266166-narrowed scope: a `_check_kill_switch_staleness` doctor check that records a first-seen timestamp for GTKB_NO_CROSS_HARNESS_TRIGGER, WARNs beyond a 2h threshold, clears on unset, and never auto-clears the env var (SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001).

This session filed this thread without seeing the peer's: `gt bridge threads --wi WI-4804` showed 0 threads at the pre-draft check, and the work-intent claim is per-slug, so the lexical slug difference ("killswitch" vs "kill-switch") evaded both the claim lock and the WI-ID collision hook (the peer's thread was filed and GO'd during this session's draft/preflight window). The peer's GO'd thread is the single canonical WI-4804 thread; this duplicate is withdrawn so only one proceeds to implementation. No carry-forward gap: the peer's GO'd -001 is functionally equivalent and slightly stronger (it pins the re-scoped dormancy half to WI-4852 and uses the trigger's exact `== "1"` predicate).

## Specification Links

(Carried from -001 for gate compliance; this version withdraws the thread rather than proposing implementation.)

- SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 - kill-switch manual/emergency-only; no auto-clear.
- ADR-DISPATCHER-ARCHITECTURE-001 - dispatch operability/observability.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - in-root platform placement (CLAUSE-IN-ROOT).
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - surface stale operational state.
- GOV-FILE-BRIDGE-AUTHORITY-001 - WITHDRAWN is a terminal status in the append-only versioned chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - satisfied (links carried).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - not applicable to a withdrawal (no implementation proceeds).
- GOV-STANDING-BACKLOG-001 - WI-4804 continues under the surviving GO'd thread.

## Owner Decisions / Input

- DELIB-20266166 + DELIB-20266140 (owner AUQ, 2026-06-26) authorize the WI-4804 visibility-half scope; the session AUQ "pick up WI-4804" directed this work. This withdrawal is governance hygiene - it removes a duplicate this session filed so the single canonical WI-4804 thread (the concurrent GO'd proposal) proceeds. No owner decision is required to withdraw a self-authored duplicate proposal.
