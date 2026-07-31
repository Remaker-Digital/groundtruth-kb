# Loyal Opposition Advisory — WI-4978 Verification Treadmill RE-OFFER (record-and-stop addendum)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T01-25-59Z-loyal-opposition-B-166fa0
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; loyal-opposition; explanatory output style

- **Harness / role:** Claude, harness B, Loyal Opposition (headless bridge auto-dispatch)
- **Dispatch id:** 2026-07-06T01-25-59Z-loyal-opposition-B-166fa0
- **Date (UTC):** 2026-07-06T01:25Z (per dispatch id)
- **Bridge thread:** `gtkb-wi4978-helper-compliance-audit-chokepoint` (latest `bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-005.md`, status REVISED, 5 versions)
- **Authoritative companion advisory (full analysis):** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-06-00-30.md`
- **WIs:** WI-4978 (subject); WI-5038 (root-cause parity-scan-pollution defect, tracked); WI-4837 (precedent pattern)

## This is an addendum, not a new analysis

I was auto-dispatched onto the `-005` REVISED entry as reviewing Loyal Opposition — the **same** entry a prior LO-B session (`2026-07-06T00-20-56Z-loyal-opposition-B-9cfafb`, ~00:30 UTC) already dispositioned via record-and-stop. Per that precedent and the WI-4837 pattern, I am **again recording-and-stopping: I am NOT filing a `-006` GO/NO-GO verdict.** The full thread state, live verification evidence, the 29-path parity decomposition, the owner decision options, and the WI-5038 capture live in the companion advisory above and are not repeated here.

## What is new this cycle: the predicted re-offer occurred

The 00:30 companion advisory's finding [P2] warned that owner-gated verification threads get re-offered because the dispatcher has no backoff for the NO-GO ↔ REVISED verification treadmill. My 01:25 re-dispatch onto the unchanged `-005` **is that gap materializing** — a wasted LO worker cycle on an already-adjudicated, owner-gated blocker. Concrete corroborating evidence (2nd instance within ~1h) that the systemic gap is live and costing worker cycles.

## State confirmed unchanged since the 00:30 disposition (read-only)

- Latest bridge file is still `-005` (REVISED); no `-006` exists → no peer verdict, no finalization.
- `git log --oneline` shows no WI-4978 finalization commit; the thread is still stuck.
- `WI-5038` (the root-cause parity-scan-pollution tooling defect) is confirmed tracked via `gt backlog show WI-5038` (open, P2, `origin=defect`, `component=cross-harness-parity`). **Not re-filed** (no duplicate capture).

I deliberately did **not** re-run the expensive parity test / `icacls .codex` this cycle: two verifications within the prior ~2h (Prime at 23:35 while filing `-005`; LO at 00:30) already confirmed the blocker live, and nothing changed since. Re-proving a stable owner-gated blocker on every re-offer is itself the waste the systemic gap produces; restraint is the correct response.

## Why no verdict, again (record-and-stop rationale)

- `-006 NO-GO` = redundant (the `-004` NO-GO + 00:30 advisory already gave this blocker its honest verdict) AND loop-fuel (NO-GO is Prime-actionable → wakes headless Prime → re-transports the same owner-gated blocker → wakes LO → …).
- `-006 GO` / `VERIFIED` = false: the linked, no-waiver cross-harness-parity test (`test_codex_skill_adapter_parity_check`) is red and no owner-waiver DELIB exists.
- `DEFERRED` = owner/Prime-only; a headless LO cannot file it.
- Leaving the thread at `-005` REVISED (LO-actionable, Prime-non-actionable) with no new file = no actionable-signature change = the quietest stable rest state a headless LO can produce.

## Recommendation (owner / dispatcher-modernization owner)

1. **Clear WI-4978** via any one option in the 00:30 companion advisory — recommended: grant a scoped cross-harness-parity waiver for WI-4978's `.codex/.../impl_report_bridge.py` mirror plus a follow-on WI to regenerate `.codex` adapters (once the ACL is cleared) and purge the transient pollution. The core fix is already verified correct in `-004`; the blocker is pollution/environment, not a WI-4978 code defect.
2. **Break the treadmill now:** a durable-Prime session files `DEFERRED` on this thread (clear/resume = "owner waiver granted OR `.codex` ACL cleared + adapters regenerated"), optionally pausing dispatchability for the thread while it waits.
3. **Dispatcher backoff:** extend circuit-breaker/backoff to owner-gated verification threads (per-thread suppression after N consecutive re-transports with no new content). Now evidenced by WI-4837 and WI-4978 (≥2 re-offers). Deliberately **not** filed blind from this scoped headless dispatch — flagged for dedup against `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION` (WI-4977 / WI-4990 / WI-4992) and WI-5038, consistent with the 00:30 advisory.

## Churn cap (guidance for future re-dispatches)

To avoid dropbox churn, further identical re-dispatches onto the unchanged `-005` should **record-and-stop without spawning yet another advisory** — this addendum plus the 00:30 companion already stand as the durable record that this thread is in an owner-gated re-offer loop. A new advisory is warranted only if the thread state materially changes (new version, finalization, or a materially different blocker).

## Methodology (read-only)

- Read: the five WI-4978 bridge files (`-001`..`-005`); the 00:30 companion advisory; `gt backlog show WI-5038`.
- `git log --oneline -8` (no WI-4978 finalization); Glob of the bridge slug (only `-005` exists).
- No source, test, KB, or bridge files were mutated. **No bridge verdict was filed** (intentional; see rationale above).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
