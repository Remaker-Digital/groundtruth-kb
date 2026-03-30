# Bridge Responsiveness Ledger

Purpose: maintain an additive record of bridge responsiveness failures, corrective actions, and recurring analysis so cadence can be judged from timestamps rather than memory.

## Operating Targets

- New bridge message acknowledgement: under 60 seconds from detection.
- Active claimed-thread status cadence: every 10 minutes or less until resolved.
- Delivery timing: meet the message `response_window`, or send a revised ETA before the window expires.

## Data Sources

- Prime bridge message/event timestamps from the bridge database via MCP.
- Poller heartbeat and activity from `.claude/hooks/.bridge-poller-codex.log`.
- Claimed/new thread state from `list_inbox(...)`.
- Owner-reported responsiveness failures when timestamp evidence supports them.

## Entry Format

Date | Scope | Observation | Evidence | Impact | Corrective action | Follow-up status

---

## Entries

### 2026-03-30 - Bootstrap-time ack breach on S234 Phase 7 advisory review

| Scope | Observation | Evidence | Impact | Corrective action | Follow-up status |
|------|-------------|----------|--------|-------------------|------------------|
| Protocol execution | A new Phase 7 advisory-review request from Prime arrived during local bootstrap and was not acknowledged within the under-60-second target. | Prime message `33a7b613-6d18-4634-b995-1a3b229bfef1` was created at `2026-03-30T18:42:26.442932+00:00`; pre-accept thread context showed `ack_breach=true` with `ack_due_at=2026-03-30T18:43:26.442932+00:00` and `ack_overdue_seconds=37`; Codex protocol acknowledgement `21a9309a-cdf8-4f13-90e8-ac8796c8bb79` was created at `2026-03-30T18:44:39.739195+00:00`. | The request sat unacknowledged for about 2 minutes 13 seconds, so the bridge had to escalate with an SLA breach even though Codex was already active in-session. | During startup, keep repeating bridge checks while bootstrap docs are loading; if a new Prime message appears, send the protocol acknowledgement immediately and defer the remaining local bootstrap reads until after acceptance. | Open |

### 2026-03-29 - Ack breach on S230 Phase 2 delta-review wake

| Scope | Observation | Evidence | Impact | Corrective action | Follow-up status |
|------|-------------|----------|--------|-------------------|------------------|
| Protocol execution | Codex missed the under-60-second acknowledgement target for the S230 Phase 2 IntentRouter delta-review request and only recovered after the wake already showed an `ack_breach`. | Prime message `7663e8d7-f71a-42ee-abcd-e5638eccbcf5` was created at `2026-03-29T08:31:25.542151+00:00`; the canonical wake snapshot `.claude/hooks/.codex-bridge-worker-last-context.json` showed `ack_breach=true` with `ack_overdue_seconds=527`; Codex protocol acceptance `e2f6f504-1ed5-4d59-9ded-ca4f8e90ef84` was created at `2026-03-29T08:42:01.625944+00:00`. | The bridge needed explicit wake recovery before work could be credibly taken, and the first response window was already missed by roughly 10 minutes 36 seconds. | On future wakes, read the canonical snapshot first, validate the thread immediately, and send protocol acceptance before any non-bridge startup reading beyond the mandatory snapshot check. | Open |
| Protocol execution | Codex again missed the under-60-second acknowledgement target on the S230 runtime-fixes re-review thread and only sent the protocol acknowledgement after the wake surfaced the breach. | Prime message `844e1a8d-05f3-4ff6-96ff-326222d5ecf4` was created at `2026-03-29T08:56:55.764000+00:00`; thread context showed `ack_due_at=2026-03-29T08:57:55.764000+00:00` and `ack_overdue_seconds=297` when claimed; Codex claimed the thread at `2026-03-29T09:02:52.993417+00:00`; Codex protocol acknowledgement `c2e92554-135c-4fa5-84c7-2303e6015a22` was created at `2026-03-29T09:02:58.053830+00:00`. | The acknowledgement window was missed by about 5 minutes 2 seconds, so bridge recovery again depended on a breach-triggered wake rather than normal near-real-time handling. | On any wake that includes `ack_breach`, claim and send protocol acknowledgement immediately after the mandatory startup/snapshot load, then move into artifact inspection and review. | Open |

### 2026-03-27 - Bridge cadence failure after protocol hardening

| Scope | Observation | Evidence | Impact | Corrective action | Follow-up status |
|------|-------------|----------|--------|-------------------|------------------|
| Protocol execution | Codex failed to maintain active-thread updates within 10 minutes on a claimed advisory-review thread. | Bridge thread `e2ba6777-7589-45b8-ba21-08fd6e9c4e55` was claimed at `2026-03-27T19:41:01.396257+00:00`; the next protocol-compliant status update sent by Codex was `3bdc01bb-4f31-471a-9172-548846d1f369` at `2026-03-27T20:59:52.712114+00:00`. | This created a silent gap of about 79 minutes on active work, violating the stated cadence and forcing owner intervention. | Treat every claimed bridge thread as a timed obligation; send a bridge `status_update` on each open claimed thread every 10 minutes or less until resolution. | Open |
| Protocol execution | Codex missed the required near-real-time acknowledgement window for a new GO/NO-GO request. | New message `802fd527-0fb7-4cab-ba50-de1c7d137515` was created at `2026-03-27T20:55:20.888752+00:00`; Codex acknowledgement `9bd71fba-7f13-4dab-abb7-5aaaa998e1df` was accepted at `2026-03-27T20:58:22.966061+00:00`. | This missed the `<60s` acknowledgement target and confirms that bridge detection alone is not sufficient if active monitoring is not maintained. | Include new-message acknowledgement latency in each periodic responsiveness review and treat any over-60-second acknowledgement as a defect, not a soft warning. | Open |
| Session-gap responsiveness | Codex left a new advisory-review message unclaimed for about 1 hour 47 minutes before the next active session sweep. | New message `9d37b820-ebe1-4342-9056-edee17892dcb` was created at `2026-03-27T22:03:45.134489+00:00`; Codex claimed it at `2026-03-27T23:50:48.829222+00:00`. | This is another concrete miss against the intended near-real-time servicing model and shows that session gaps still dominate worst-case responsiveness. | Track message-age-at-first-claim separately from in-session ack speed, and do not describe these gaps as mere “offline” periods without recording the elapsed time explicitly. | Open |
| Protocol execution | Codex again missed the 10-minute active-thread cadence on the Phase 3 advisory-review thread despite prompt acceptance/claim. | Bridge thread `0698f90e-ff37-4db1-9f64-888b67bb362a` was claimed at `2026-03-28T02:22:31.019840+00:00`; the next Codex-originated status update in that thread was `bd0a7e8d-3602-47a0-90f9-2658627169e6` at `2026-03-28T02:34:09.408228+00:00` (followed by another Codex status update `dc0b5093-e612-4d2b-9833-4b01609fdb71` at `2026-03-28T02:34:30.161145+00:00`). | This created a silent gap of about 11 minutes 38 seconds on active claimed work. The lapse is smaller than the earlier 79-minute failure but still violates the stated cadence after the rule was already documented and hardened. | Treat `claimed_at` as the active-thread timer start unless a later Codex status/completion message resets it, and force a status update before the 10-minute mark even during initial document review. | Open |
| Diagnosis | The current failure mode is no longer primarily transport or protocol-definition weakness; it is execution-discipline drift after those fixes were already in place. | The poller heartbeat remained current in `.claude/hooks/.bridge-poller-state-codex.json` (`updated_at: 2026-03-27T20:57:32.942564+00:00`) and the codex poller log shows active bridge intake through event `515` at `2026-03-27 19:41:01`; protocol requirements are already defined in `.claude/rules/prime-bridge-collaboration-protocol.md`. | Prior fixes can appear successful while real responsiveness still regresses in practice. | Periodic analysis must distinguish between mechanism failures, protocol-definition failures, and operator-execution failures. | Open |

| Mitigation deployment | A real local wake path now exists for bridge work even when the interactive desktop thread is idle. | At `2026-03-27T17:16:37-07:00`, `scripts/install_codex_exec_shim.ps1` installed a user-space shim in `C:\Users\micha\AppData\Local\OpenAI\Codex\bin`, after which `Get-Command codex` resolved to that path and `codex -V` succeeded. At `2026-03-27T17:16:54-07:00`, scheduled task `\AgentRedCodexBridgeWake` was created with a 3-minute repetition interval and `Last Result: 0`; `.claude/hooks/.codex-bridge-wake.log` recorded successful idle polls. | This removes the specific `WindowsApps` execution blocker and establishes an automated bridge-to-`codex exec` trigger path for future responsiveness data. | Measure whether worst-case first-claim and claimed-thread silence intervals improve after this deployment; if not, tighten cadence logic rather than reverting to manual sweeps. | Open |
| Conversational exchange state | Codex falsely presented `0045b5f2` as newly picked-up work even though the bridge database already showed the thread as claimed, completed, and answered. | Local bridge DB query against `C:\Users\micha\.claude\prime-bridge\bridge.db` showed `0045b5f2-d18c-4b8c-95ac-ec3336cd3804` with `status='done'` and `claimed_by='codex'`, plus later codex messages `d2292a50-98ba-4750-aaac-36e66d2cb3d4` and `bc30c93f-f7b2-42fc-97ca-ea4ab9c1f5c6` already recorded the in-progress update and final `GO` outcome. Despite that, I initially acted as if the message still needed pickup. | This creates a misleading conversational state: the user receives a fresh “I’m claiming and reviewing” narrative for work that has already been completed, which undermines trust in both liveness and factual state tracking. | Before responding to any bridge message reference, first resolve the full canonical message id and current row state from the bridge DB; if the item is already `claimed` or `done`, summarize the recorded outcome instead of narrating a new pickup. | Open |

| Mitigation deployment | Bridge detection now triggers automatic investigation, and each wake run now carries canonical thread context instead of bare message IDs. | On `2026-03-27 20:00:55 -07:00`, `bridge_poller.py` was updated so read-only codex inbox detection launches `scripts/codex_bridge_wake.py` immediately for newly detected peer messages; `scripts/codex_bridge_wake.py` was updated to build `.claude/hooks/.codex-bridge-wake-last-context.json` using `prime_bridge_runtime.describe_thread_context(...)`; `prime_bridge_runtime.py` now resolves short IDs and correlation threads directly. Verification: `python -m py_compile prime_bridge_runtime.py bridge_poller.py scripts/codex_bridge_wake.py` succeeded, `describe_thread_context('a06b8dd8', recipient='codex')` resolved the canonical thread, and the generated context identified prior Codex review state plus report paths under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`. | This directly addresses both current failure modes: messages should no longer sit as passive poller detections, and wake-triggered runs now know whether a message is new, correlated, or already reviewed before they narrate action. | Watch the next real inbound bridge messages for three metrics: time from detection to wake launch, whether `.codex-bridge-wake-last-context.json` names the canonical report path, and whether any resend is described as a resend rather than a fresh pickup. | Open |
| Bridge intake defect | A real Prime message was missed by the standard bridge intake path because it arrived with `status='pending'` instead of `status='new'`. | Direct DB query showed Prime message `8b313b05-a58a-45b6-b369-11a92748ed50` (`Phase 3 Proposal v4 -- Analytics Proof Fixed (Last Blocker)`) created at `2026-03-28T03:40:18.594492Z` with `status='pending'`; at the same time `prime_bridge_runtime.list_inbox(agent='codex', status='new')` returned `count=0`, and the codex poller could not see the message through its `status='new'` inbox scan. | This is a concrete mechanism failure: even with the hardened wake path, a message outside the expected status set is invisible to the automated intake pipeline and requires manual DB inspection. | Extend bridge intake so Codex can detect and service `pending` recipient messages, or normalize inbound message status to `new` at insert time so the poller and `list_inbox(...)` see them. | Open |

---

## Standing Review Questions

Use these in periodic analysis:

1. What was the longest acknowledgement latency for a new message since the last review?
2. What was the longest silence interval on a claimed thread since the last review?
3. Did any thread miss its declared `response_window` without a prior status update?
4. Was the bridge daemon healthy during the lapse, or was this a tool outage?
5. Did the corrective action change actual timing behavior, or only documentation/protocol text?

## Current Working Rule

When any bridge thread is `claimed` by `codex`, it remains active operational work even if no user message is pending. The next check must look at:

- count of `new` messages
- count of `claimed` messages
- age of each claimed thread since last Codex-originated status/completion message

If any claimed thread approaches 10 minutes without an outbound status/completion update, Codex should send a status update before continuing silent work.
