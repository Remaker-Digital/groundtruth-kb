# Loyal Opposition Report: Dispatch Launchability and Scheduled Scan Precedence

Generated: 2026-06-11 06:58 America/Los_Angeles
Role: Loyal Opposition
Scope: WI-4404, WI-4413, WI-4388, WI-4408, WI-4410
Artifact type: advisory report, not an implementation proposal

## Claim

FAB-01 / WI-4413 should take precedence over standalone WI-4404 implementation. WI-4404 is still valid and P1, but it should be implemented only after, or inside the same governed proposal as, the launchability fix and launchability doctor check. A regular scheduled scanner that runs before active harness targets can launch will reliably rediscover work and amplify known dispatch failures instead of restoring useful bridge autonomy.

WI-4404 must also be framed as a new deduplicated wake substrate, not as permission to restore the retired OS poller or retired smart poller stacks.

## Evidence

- Live LO bridge scan on 2026-06-11 returned zero actionable `NEW` or `REVISED` entries. Current work therefore falls to backlog/advisory precedence rather than bridge artifact review.
- `groundtruth.db` read-only query for `work_items` shows WI-4404 as open, P1, stage `backlogged`, with owner directive: "We want the poller to run and regularly scan for changes. We only want it to dispatch work to a harness when there is new unclaimed work to dispatch. The current implementation is wrong." The same query shows WI-4413 as open, P1, stage `backlogged`, owner-directed from `bridge/gtkb-fable-investigation-advisory-001.md`.
- `bridge/gtkb-fable-investigation-advisory-001.md:114` defines FAB-01 as "Restore bridge dispatch launchability + add launchability doctor check" and maps it to HYG-001/HYG-004 plus WI-4388/WI-4408/WI-4410.
- `bridge/gtkb-fable-investigation-advisory-001.md:128` defines FAB-10 as dispatch telemetry, claim contract, and INDEX write perimeter.
- `bridge/gtkb-fable-investigation-advisory-001.md:148` states the sequencing constraint directly: "FAB-01 without FAB-10 leaves the next dispatch breakage invisible."
- `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md:95` through `:112` records HYG-001: every active dispatch target fails launch with WinError 2, including the forward-slash relative Python path and PATHEXT/gemini command failure.
- `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md:121` through `:133` recommends spawn-time normalization plus a doctor check that actually launches each active harness argv head with `--version`.
- `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md:255` and `:264` tie WI-4404 to the event-source gap and describe deduplicated scheduled polling as an option, not as a substitute for launchability.
- `.claude/rules/bridge-essential.md:95` through `:96` explicitly forbids re-enabling the retired OS poller or retired smart poller as a substitute for the cross-harness event-driven trigger.
- `AGENTS.md:189` through `:194` repeats the same operating constraint: do not restore the retired pollers; use the cross-harness trigger when healthy; otherwise use manual scans or monitoring only when separate harnesses or asynchronous monitoring require it.

## Risk / Impact

If WI-4404 lands first as a generic scheduled scanner, the system gains a more reliable way to repeatedly hit a launch-dead topology. That increases failure log churn, retry/circuit-breaker pressure, and owner-facing confusion without restoring actual Prime Builder / Loyal Opposition handoff.

If WI-4404 is interpreted as restoration of the old OS poller or smart poller, it conflicts with the current bridge operating rules and reopens the fixed-interval token-cost failure class that Slice 4 retired.

If FAB-01 lands without enough telemetry from FAB-10, the next dispatch break can again become invisible. The Fable advisory already calls out that dependency; the implementation proposal should carry it forward rather than treating launchability as isolated.

## Recommended Action

1. Treat WI-4413 / FAB-01 as the next implementation proposal for the dispatch cluster.
2. Include WI-4388, WI-4408, and WI-4410 in the FAB-01 proposal scope as overlap evidence, not separate competing starts.
3. Add an explicit "WI-4404 interaction" section to the FAB-01 proposal:
   - State that scheduled scanning remains P1 owner-directed work.
   - State that it must not restore the retired OS poller or smart poller.
   - State whether WI-4404 is deferred until after FAB-01/FAB-10 or implemented as a new deduplicated wake substrate inside a combined proposal.
4. Require launchability verification before any scheduled scanner is considered restored:
   - Normalize argv heads at spawn time or fix registry data, with the choice documented.
   - Add a doctor check that invokes each active dispatch target argv head with `--version`.
   - Prove at least one active Prime Builder and one active Loyal Opposition target can launch from the same subprocess path used by the dispatcher.
5. Carry FAB-10 telemetry and claim-contract requirements either into the same proposal or into an immediately following proposal before declaring dispatch autonomy healthy.

## Decision Needed From Owner

No immediate owner decision blocks this advisory. The owner already directed WI-4404 and chartered FAB-01..23. Prime Builder can proceed by filing the implementation proposal with the precedence above.

If Prime Builder wants to combine WI-4413 and WI-4404 into one implementation proposal, the proposal should ask one owner question only if it changes the mechanism choice beyond the existing directives.

## Completion / Monitoring Note

This report completes the LO advisory task of resolving dispatch-cluster precedence before implementation. It does not review any artifact created by this same session and does not mutate protected source, test, hook, or bridge protocol files.
