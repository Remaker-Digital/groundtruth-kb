author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T13-14-30Z-loyal-opposition-B-6eef3a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; loyal-opposition; explanatory output style

# Loyal Opposition Addendum — WI-4978 Re-Offer at v027 (defers to the 12:05Z mechanical-break advisory)

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001
WIs: WI-4978, WI-5038, WI-5041, WI-5042
Bridge thread: gtkb-wi4978-helper-compliance-audit-chokepoint (at version 027 as of this addendum)
Date: 2026-07-06T13:14Z UTC

---

## This is an addendum, not a new advisory

The canonical WI-4978 treadmill analysis remains
`INSIGHTS-2026-07-06-12-05-wi4978-treadmill-mechanical-break.md` (Claude-B,
~1h ago, at v024). Its claim, evidence, severity (P1), and owner-gated
recommendation are unchanged and current. Do not re-read the prior four
re-offer records to reconstruct context — the 12:05Z advisory is the single
current synthesis. This addendum adds only the new re-offer datum and one
escalation point.

## New datum: the loop advanced v024 → v027 *after* the mechanical-break advisory

The 12:05Z advisory concluded: "No further bridge verdicts should be filed on
this thread until that break is applied." In the ~70 minutes since, the thread
advanced **three more versions** (v025 impl-report / v026 NO-GO / v027 REVISED),
driven by the multi-harness LO pool re-arming Codex-A. This is direct empirical
confirmation of `record-and-stop-doesnt-hold-loop-across-multi-lo-pool`: a
dropbox record-and-stop is non-mechanical, so it stops *the recording session*
from re-arming the loop but cannot park the thread against the rest of the pool.
The single-advisory approach provably does not self-arrest this treadmill.

## What I did this dispatch (record-and-stop, no verdict)

I was auto-dispatched as Loyal Opposition on `REVISED`
`bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-027.md` (Codex-A, filed
~6 min before my dispatch). I filed **no bridge verdict**. Every verdict on this
thread is loop-fuel or dishonest: VERIFIED is impossible (linked parity test
genuinely red, no owner waiver, `.codex` mirror unwritable under the Deny-ACE),
NO-GO is Prime-actionable and re-arms Codex-A, GO is nonsensical. Not filing
holds the LO actionable signature stable so *this* session does not re-wake the
loop.

## Freshness confirmation (cheap checks only; skipped the expensive re-run)

- Live state: `gt bridge show ... --json --compact` → latest `-027`, status
  `REVISED`, version_count 27 (not superseded).
- Blocker unchanged: `-027` itself re-ran
  `test_codex_skill_adapter_parity_check` at ~13:08Z (6 min before dispatch) →
  still red, "would update 34 file(s)". I did **not** re-run the pytest — per
  the churn-avoidance rule, the premise is freshly confirmed and the git tree
  has not moved toward green.
- No waiver: `gt deliberations search "WI-4978 parity verification waiver owner
  codex ACL"` → only unrelated waivers (WI-4589, WI-4681); no WI-4978 waiver,
  no active `.codex` ACL-repair authorization.
- Root-cause WIs still open: `gt backlog show` → **WI-5038** (P2, open),
  **WI-5041** (P2, open — its description documents this exact treadmill),
  **WI-5042** (P2, open). Capture-by-default is already satisfied; no new WI to
  file.

## Escalation

The mechanical break is now **overdue**, not merely recommended. Owner-gated,
unchanged from the 12:05Z advisory:

1. **Park the thread now** — owner-directed `DEFERRED` (clear/resume =
   "WI-5038 parity-scan pollution purged AND `.codex` writability resolved per
   WI-5042/WI-5002") or owner-directed `WITHDRAWN` of the verification retry.
   This is the only action that stops *every* LO harness in the pool.
2. **Prioritize WI-5041** (per-thread re-offer backoff) — the general cure.
3. **Prioritize WI-5038** (exclude pyc/draft-/temp- scratch from the parity set)
   and **WI-5042 / revisit WI-5002** (`.codex` writability routing).

## Churn cap (reaffirmed)

Further identical re-offers on an unchanged blocker record-and-stop with **no
new dropbox artifact** unless thread state materially changes (finalization, a
recorded waiver, a different blocker, or a version that carries new reviewable
content). This addendum exists only because the post-advisory version advance
(v024→v027) is itself the new escalation datum. No MemBase mutation, no bridge
verdict, no new WI filed this dispatch.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
