REVISED

# Implementation Proposal - Startup Enhancements P2: State-Drift Correction to the Cache-Disable Plan

bridge_kind: prime_proposal
Document: gtkb-startup-enhancements-p2-freshness-contract
Version: 011 (REVISED; corrects the -009 plan against verified live state after the -010 GO)
Responds to: bridge/gtkb-startup-enhancements-p2-freshness-contract-010.md (latest GO on the -009 plan)
Original approved proposal: bridge/gtkb-startup-enhancements-p2-freshness-contract-009.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-30 UTC
Session: interactive PB session (S373); init-keyword startup-relay diagnostic chain
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-30T14-30Z-prime-builder-startup-freshness-drift-correction-011
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session; AUQ-authorized stand-down + drift-correction

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-ENHANCEMENTS

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

## Claim

The cache-disable direction approved at -010 remains correct, but the -009 plan's implementation surface description has drifted from the live tree. This REVISED corrects the plan against verified current state so that a future clean-session implementation runs against accurate anchors. The substantive correction: IP-4 (remove five named cache tests) is struck because those tests do not exist in any test file; the cache helpers IP-1..IP-3 target are uncommitted working-tree state rather than committed code; and the operative source file currently carries a large multi-feature uncommitted change set that must be respected during the eventual edit. Per owner AUQ this turn, implementation is deferred to a clean session without the active commit freeze; this REVISED is the corrected, state-accurate plan for that session.

## Revision Notes (Verified State Drift)

On attempting to implement the -010 GO during S373, Prime Builder verified the live tree and found three discrepancies between the -009 plan and current state. Each was confirmed by an independent git/grep probe, not inferred.

1. The five cache tests named in -009 IP-4 do not exist in any test file. `test_fresh_payload_reused`, `test_stale_by_age_regenerates`, `test_role_map_drift_regenerates`, `test_index_drift_regenerates`, and `test_diagnostic_log_emitted` appear only in this thread's own proposal markdown. A repository-wide content search returns zero matches outside bridge documents. The -009 line anchors (571, 601, 613, 636, 669) currently point at unrelated harness-lifecycle-guard and drive-relative-path tests. IP-4 therefore has nothing to remove.

2. The cache helpers IP-1..IP-3 target are uncommitted working-tree state, not committed code. `git show HEAD:scripts/session_self_initialization.py` contains none of `_is_payload_fresh`, `_payload_staleness_reasons`, or `_startup_freshness_from_payload`. They are present only in the working tree, so the prior -005 implementation report's changes were never committed.

3. The operative source file holds 375 uncommitted insertions and 23 deletions spanning roughly fourteen functions (GitHub workflow inventory, testing-service integrations, dashboard intelligence, current-project-state rendering, report rendering, freshness metadata, and the cache code). The cache surface is one slice of a larger uncommitted multi-feature change set. An active commit freeze is in effect for the working tree.

Consequence: the cache-disable edit must isolate only the cache hunks from a contended multi-feature uncommitted diff, must not commit while the freeze is in effect, and IP-4 must be struck. These conditions are best satisfied in a clean session, which is the owner-selected path this turn.

## In-Root Placement Evidence

All target paths are in-root under the GroundTruth-KB project root. `scripts/session_self_initialization.py` and `platform_tests/scripts/test_session_self_initialization.py` are both inside that root. ADR-ISOLATION-APPLICATION-PLACEMENT-001 in-root clause satisfied. No application files under the applications subtree are touched.

## Specification Links

- GOV-SESSION-SELF-INITIALIZATION-001 - startup self-initialization payload freshness; disabling the cache strengthens the freshness invariant by removing a cache-window vector that produced stale-request-id payloads.
- GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 - proactive startup engagement; the degraded-fallback observed under the prior F1 finding violates this, and disabling the cache restores the proactive disclosure path.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol authority; this REVISED follows the file-bridge protocol path and updates the canonical bridge thread.
- SPEC-AUQ-POLICY-ENGINE-001 - deterministic AUQ policy engine surface; the stand-down-and-correct direction was collected through AskUserQuestion as the sole valid owner-decision channel.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - in-root placement; satisfied per the In-Root Placement Evidence section above.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - implementation-proposal spec-linkage requirement; this proposal carries forward the prior thread's spec links.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-derived testing mandatory for VERIFIED; the corrected spec-to-test mapping below covers all linked specs.
- GOV-STANDING-BACKLOG-001 - standing backlog authority; this proposal addresses the single work item GTKB-STARTUP-ENHANCEMENTS and is not a bulk operation.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - artifact-oriented development; the startup payload and freshness metadata are governed lifecycle artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - artifact lifecycle triggers; payload regeneration is the lifecycle-state transition this plan enforces unconditionally.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - artifact-oriented governance; the work continues to be tracked through the governed work item.
- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS - owner-decision evidence for the active project authorization covering this work item.

## Prior Deliberations

- bridge/gtkb-startup-enhancements-p2-freshness-contract-010.md - Loyal Opposition GO on the -009 cache-disable plan; this REVISED corrects that plan's drifted implementation surface, not its direction.
- bridge/gtkb-startup-enhancements-p2-freshness-contract-009.md - prior Prime Builder REVISED that proposed cache removal; its IP-4 named five tests now verified not to exist.
- bridge/gtkb-startup-enhancements-p2-freshness-contract-006.md - Loyal Opposition NO-GO with the F1 finding identifying the cached startup-service payload reuse defect (the wrong-role cross-harness cache reuse symptom).
- bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md - prior Prime Builder post-implementation report; its claimed cache-test additions were verified not present in any test file.
- bridge/gtkb-startup-enhancements-p2-freshness-contract-008.md - Loyal Opposition NO-GO rejecting a pure deferral note at -007; this REVISED is substantive, not a deferral, to avoid that failure mode.
- DELIB-2332 - Loyal Opposition verification NO-GO that characterized the cross-harness Prime-payload-reused-during-Loyal-Opposition-startup defect; the same wrong-role symptom recurred during S373 diagnosis.
- DELIB-2330 - prior Loyal Opposition GO for this startup-freshness thread.
- DELIB-2216 - startup-relay truncation-fix bridge thread, VERIFIED.
- DELIB-2202 / DELIB-2205 - startup-relay PreToolUse read-exemption bridge thread, VERIFIED.
- DELIB-1075 - Startup Token Consumption Review; relevant because the owner-chosen cache-disable direction accepts the full-render cost on every session start.
- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS - project authorization covering this work item.

## Owner Decisions / Input

- 2026-05-30 UTC, this session: owner answered AskUserQuestion "The -010 GO'd plan can't run as written ... How do you want to proceed?" with "Stand down + file drift REVISED" - the option described as: do not touch the working tree, file a REVISED documenting that -009's IP-4 references phantom tests and the helpers are uncommitted so the plan is re-scoped against actual state, re-attempt implementation in a clean session without the commit freeze. This authorizes filing this REVISED and defers code edits to a clean session.
- 2026-05-30 UTC, this session: owner answered the earlier AskUserQuestion choosing to implement the -010 GO'd thread, then answered the diagnosis-driven follow-up confirming the stand-down once the state drift was surfaced.
- 2026-05-14 UTC, S350+: owner approved the GTKB-SESSION-LIFECYCLE-UX project authorization (PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH) including this work item, recorded under deliberation DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS. Per the counterpart-review gate rule, that project authorization is additive to the bridge GO; this REVISED proceeds through normal Loyal Opposition review.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-SELF-INITIALIZATION-001 requires the fresh-session self-initialization disclosure to reflect current state; the prior F1 finding established that the cache-based implementation does not fully meet that requirement. Removing the cache satisfies the same requirement by construction. No new or revised requirement is created. This REVISED corrects the plan's anchors; it does not change the requirement surface.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One work item (GTKB-STARTUP-ENHANCEMENTS), one slice (P2 cache-disable remediation); member of PROJECT-GTKB-SESSION-LIFECYCLE-UX per the project authorization. This proposal performs no inventory sweep of multiple work items and no batch MemBase mutation. References to "work item" and "standing backlog" describe the single work item GTKB-STARTUP-ENHANCEMENTS and its governed filing path only. Review-packet inventory: IP-1 (cache-read removal) + IP-2 (cache helpers removal) + IP-3 (cache-write removal) + IP-4 (struck, phantom) + IP-5 (regression test for cache-ignore) + IP-6 (regression test for dispatcher request-id contract), single thread.

## Corrected Proposed Scope

IP-1, IP-2, IP-3, IP-5, and IP-6 are carried forward from -009 and remain valid; their targets exist in the working tree. IP-4 is struck. The implementation operates on uncommitted working-tree lines and must not commit while the freeze is active.

### IP-1: Remove cache-read short-circuit in session_self_initialization.py main()

Remove the conditional block in main() that short-circuits when the cache-fresh predicate returns true (currently near the emit-startup-service-payload branch). After removal, the emit-startup-service-payload path always proceeds to the full render. The exact line anchors will be re-resolved at implementation time because the surrounding file is in an uncommitted multi-feature state; the implementation report must cite the anchors observed at edit time.

### IP-2: Remove orphaned cache helper functions

Remove the three helper functions that become orphan after IP-1: the payload-freshness reader, the staleness-reasons computation, and the is-fresh predicate. Each is used only within the cache short-circuit removed by IP-1. These are uncommitted working-tree additions; removal returns the cache surface toward the committed HEAD shape.

### IP-3: Stop writing the cache file

Remove the cache-write in the emit-startup-service-payload helper, and remove the cache-path variable and the cache-path argument in main(). The dashboard directory variable is retained because it is still used for the dashboard render path.

### IP-4: STRUCK - no cache tests exist to remove

The five tests named in -009 IP-4 do not exist in any test file (verified by repository-wide content search; matches only in bridge markdown). No removal action is required or possible. This IP is recorded as struck so the plan matches reality; the eventual post-implementation report must not claim removal of tests that were never present.

### IP-5: Add regression test for cache-ignore behavior

Add a test to platform_tests/scripts/test_session_self_initialization.py that pre-populates the dashboard startup-service payload file with a payload carrying a stale request-started timestamp, invokes the emit path with the request-started env var set to a current value, and asserts the printed output is not byte-equal to the pre-populated content and that the printed request-started value matches the env var. This satisfies the prior F1 prescription that the service regenerate rather than return a stale cache.

### IP-6: Add regression test for dispatcher request-id contract

Add a test that invokes the emit path with the request-started env var set to a known value and asserts the printed payload's request-started value exactly matches the env var. This is the property the dispatcher exact-equality freshness check requires.

## Specification-Derived Verification Plan

| Specification | Test or verification command | Behavior verified |
|---|---|---|
| GOV-SESSION-SELF-INITIALIZATION-001 | pytest platform_tests/scripts/test_session_self_initialization.py for the IP-6 request-id test | Service produces a fresh payload reflecting the current request id on every call. |
| GOV-SESSION-SELF-INITIALIZATION-001 | pytest for the retained regenerated-payload-shape test | The freshness-metadata schema continues to be emitted correctly. |
| GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 | manual dispatcher reproduction via the Claude and Codex session-start dispatch hooks | Live dispatcher run no longer emits the degraded startup fallback. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | bridge applicability preflight on this operative file | Bridge applicability preflight passes. |
| SPEC-AUQ-POLICY-ENGINE-001 | this proposal's Owner Decisions / Input section plus this-turn AUQ answers | Direction collected through AskUserQuestion, not prose. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | adr/dcl clause preflight on this operative file | In-root clause satisfied; no application-subtree paths touched. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | adr/dcl clause preflight on this operative file | Concrete spec links present in Specification Links. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this spec-to-test mapping plus the IP-5 and IP-6 tests | Each linked specification has at least one mapped test or verification command. |
| GOV-STANDING-BACKLOG-001 | adr/dcl clause preflight on this operative file | Single-WI scope clarified; no bulk operation. |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | bridge thread and post-implementation report inspection | The startup-payload artifact continues to be governed; cache layer removed, not the artifact. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | bridge thread and post-implementation report inspection | Lifecycle artifact transitions remain governed; payload is regenerated unconditionally. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | bridge thread and post-implementation report inspection | Governed work item path preserved. |

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed against the cache hunks only, with anchors cited as observed at edit time; unrelated uncommitted multi-feature work in the same file is left untouched.
- IP-4 recorded as struck; the post-implementation report makes no claim of removing nonexistent tests.
- IP-5 and IP-6 tests added and passing; the retained regenerated-payload-shape test still passes.
- The three cache helper functions are absent from the working-tree file after the edit; the cache-write call and cache-path construction are absent from main().
- Both bridge preflights pass on the operative file.
- Live dispatcher reproduction produces a normal startup payload, not the degraded fallback.
- ruff check and ruff format --check pass on both touched files.
- No commit is made while the working-tree commit freeze is active; the implementation report states the freeze status and leaves staging to the freeze-holder.

## Risks / Rollback

- Risk: the cache hunks are interleaved with a 375-line multi-feature uncommitted diff; an imprecise edit could clobber unrelated in-flight work. Mitigation: isolate cache hunks by function name at edit time; verify the unrelated functions are byte-unchanged after the edit; perform the edit in a clean session per owner direction.
- Risk: every session start re-runs the full render path after cache removal. Mitigation: under the fast-hook path the render is bounded; the owner accepted this trade-off via AUQ on the -009 turn.
- Rollback: re-add the three helper functions, the cache-read short-circuit, and the cache-write call; however this would reintroduce the F1 cross-harness stale-payload defect.

## Recommended Commit Type

fix: - this is a defect-repair plan (the prior F1 dispatcher freshness contract violation plus the wrong-role cross-harness cache reuse symptom). Net change at implementation time is expected to be net-negative source lines (three helpers plus cache branches removed) plus two new regression tests. No new capability surface is introduced.

## Applicability Preflight

Preflight will be run after this file is written and the INDEX entry is added; the invocation and expected pass criteria appear in the Specification-Derived Verification Plan and Acceptance Criteria sections.

## Clause Applicability

Clause preflight will be run after this file is written and the INDEX entry is added; expected outcome is exit 0 with all must_apply clauses satisfied as evidenced by the spec-to-test mapping and the In-Root Placement Evidence section.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
