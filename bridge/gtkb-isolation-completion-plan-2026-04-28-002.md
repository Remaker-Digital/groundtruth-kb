# Bridge Proposal — GT-KB Isolation Completion Plan: Owner Decisions Addendum (2026-04-28)

**Status:** NEW (version 002 — addendum recording owner decisions on `-001` Section 9)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-isolation-completion-plan-2026-04-28`
**Builds on:** `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md` (NEW; the comprehensive scoping)

This addendum records the owner's explicit answers to the 7 decisions in `-001` Section 9, plus one operational clarification about the bridge poller. It does NOT supersede `-001`; it amends it with resolutions. Codex review should treat the combined `-001 + -002` as the proposed final state.

---

## 1. Owner Decisions Received

| # | Decision | Owner answer |
|---|---|---|
| 1 | Section 1.3 mixed/stale category defaults | **Confirmed** — proceed with the proposed defaults for all 12 categories (delete stale, per-file split mixed, etc.) |
| 2 | Dashboard service: manual vs. always-on | **Always-on** (Option β) — `gt platform configure-host` registers a Windows scheduled task that runs `gt serve` at boot/login; persistent. |
| 3 | "Platform does not auto-install cloud SDKs" stance | **Confirmed** — platform install identifies missing cloud tooling and points to install instructions; does not auto-perform `az login`, `gh auth login`, etc. |
| 4 | Application discovery: Strategy β + γ (user-config file + interactive fallback) | **Confirmed** — primary discovery via `~/.config/groundtruth-kb/config.toml` (Unix) / `%APPDATA%\groundtruth-kb\config.toml` (Windows); fallback to interactive prompt if file missing. |
| 5 | KB record migration approach | **Tag-in-place** — existing Agent Red KB records are tagged `application_id = "Agent_Red"` in-place via schema migration. No DB rebuild. |
| 6 | Phase ordering | **Confirmed: Phase 1 → 2 → 3 → 4 → 5 → 6.** Sequential; each phase must reach VERIFIED before the next begins. |
| 7 | Phase 2 (file moves) — this session or next? | **Next session.** Current session ends with proposal filed and (pending Codex) VERIFIED. Phase 1 closes any cleanup that doesn't require restructuring. Phase 2 is its own dedicated session(s). |

These resolutions are now binding. Subsequent phase proposals must cite this addendum when implementing Section 9 items.

## 2. Smart-Poller Operational Clarification

Owner addendum to the bridge poller question (`-001` Section 4.2.4):

> "The previous poller implementation was disabled at my direction. The new smart poller should not be disabled if it is available and functioning."

This distinguishes two distinct poller concepts that `-001` did not explicitly separate:

### 2.1 The OLD bridge poller (retired)

- **Identity:** Windows scheduled tasks `AgentRedFileBridgeIndexScan-Claude`, `AgentRedFileBridgeIndexScan-Codex`, `AgentRedBridgeLivenessAlert`, `AgentRedPollerLivenessWatcher`, plus the `Agent Red Bridge Monitor` foreground watchdog and the in-session `CronCreate` poller.
- **Status:** Disabled / retired 2026-04-25 (S308) per owner directive. Drove ~10× token-cost regression (12.5M tokens/day from background spawns).
- **Future state:** **STAYS DISABLED.** Per `bridge-essential.md` §"Re-Enabling Pollers", reactivation requires explicit owner approval and a written cost/benefit analysis demonstrating the regression has been mitigated. This proposal does NOT request re-enabling the OLD poller.

### 2.2 The NEW smart poller (in active development)

- **Identity:** `GTKB-BRIDGE-POLLER-001` umbrella per `memory/work_list.md` row 14. Architecture per `bridge/gtkb-bridge-poller-001-smart-poller-007.md` (REVISED-3 GO). Sub-threads:
  - **P1 detector** — `bridge/gtkb-bridge-poller-p1-detector-004.md` (REVISED-1 GO)
  - **P2 registry** — `bridge/gtkb-bridge-poller-p2-registry-006.md` (REVISED-2 GO; static-record-only)
  - **P2.5 verification spike** — `bridge/gtkb-bridge-poller-p2-5-verification-spike-004.md` (REVISED-1 GO; ~2.1M-token one-time owner-approval-gated spike)
  - **P3 invoker** — design hard-gated on P2.5 spike report
- **Architecture:** owner-out-of-loop; headless CLI spawn (`claude -p ... --bare` / `codex exec`); concurrency / isolation / governance / cost-analysis contracts defined in umbrella `-006`.
- **Status:** Implementation queued upstream in `groundtruth-kb` per the original work-item plan. With this proposal's restructure, that implementation now lands inside the GT-KB platform at `E:\GT-KB\` directly (not "upstream in groundtruth-kb" since GT-KB IS the platform).
- **Future state per owner directive:** **ENABLE WHEN AVAILABLE AND FUNCTIONING.** Specifically:
  - When `gt platform configure-host` runs (Section 4.2.4 of `-001`), it registers and **starts** the smart poller if the smart-poller code is present and verification has passed.
  - If the smart-poller code is not yet present (pre-Phase-3 of this plan), `gt platform configure-host` does NOT register the OLD poller's scheduled tasks; it leaves the bridge in manual-scan mode (current behavior).
  - The smart poller's enablement is conditional on:
    1. The relevant work_list row 14 sub-threads have shipped and are VERIFIED.
    2. `gt platform doctor` reports the smart-poller infrastructure as healthy.
    3. The host OS supports the spawn mechanism (Windows-supported headless invocation).
  - The smart poller is **opt-out, not opt-in**, when those conditions are met.

### 2.3 Implementation impact on phase ordering

The smart poller's enablement affects Phase 4 (`-001` Section 7.4) and Phase 5 (Section 7.5):

- **Phase 4** (`gt platform init` + `gt platform configure-host`): registers smart-poller scheduled task / service IF smart-poller code is present in the framework at install time. Otherwise registers nothing for the poller (manual-scan mode persists).
- **Phase 5** (application install): the application install does NOT enable the smart poller; that's a platform concern. The application install simply works correctly under either manual-scan or smart-poller mode.

The smart-poller code itself is GTKB-BRIDGE-POLLER-001 work, separate from this proposal. This proposal commits to the *enablement contract* (always-on when available); the *production* of the smart poller is its own multi-bridge work program.

## 3. Confirmed Items, No Change Needed

The following from `-001` are already aligned with owner's intent and do not need amendment:

- Section 0 framing (canonical platform-spec document, machine-verifiable manifest, owner-verified-before-execution gate).
- Section 1 inventory (proceeds with stale deletions per owner confirmation #1).
- Section 2 target layout (the canonical platform model).
- Section 3 install behavior (per Decision #3 confirmation).
- Section 4 setup, with two clarifications now incorporated:
  - Section 4.2.3: dashboard becomes always-on per Decision #2 — `gt platform configure-host` registers a Windows scheduled task / boot service for `gt serve`.
  - Section 4.2.4: smart-poller enablement contract per §2.2 above.
- Section 5 application install (per Decision #4 confirmation).
- Section 6 Agent Red setup (per Decision #5 confirmation: tag-in-place migration; no DB rebuild).
- Section 7 phase ordering (per Decision #6 confirmation).
- Section 11 reversibility.

## 4. Codex Re-Review Request (Updated)

Please re-verify `-001` with the resolutions in this `-002` addendum:

1. **Section 1 inventory completeness** — sample 10 random files in `E:\GT-KB\` and confirm each is correctly classified per `-001` Section 1. (Carry-forward from `-001` Section 10 item 1.)
2. **Section 2 layout** — does the target structure satisfy the owner's "GT-KB IS the platform; applications are slots" model? Does the smart-poller-conditional dashboard always-on add anything that breaks this model?
3. **Sections 3-6 install descriptions** — internal consistency under the owner's clarifications:
   - Always-on dashboard (Decision #2): does Section 4.2.3 reflect this in a way that doesn't conflict with Decision #3 ("don't auto-install cloud SDKs")? The dashboard is GT-KB infrastructure, so it auto-starts; cloud SDKs are external dependencies, so they don't auto-install. Verify this distinction is clean.
   - Tag-in-place migration (Decision #5): does Section 6.3.1 correctly describe the tag-in-place mechanism (no DB rebuild)?
   - Smart poller (this addendum §2): does the conditional-enablement model fit cleanly into Phase 4?
4. **Phase ordering** (Decision #6 confirmation): flag any dependency violations now that Phases 4-5 must conditionally include smart-poller enablement.
5. **Phase 2 = next session** (Decision #7 confirmation): confirm this is the right pacing; flag any work in current-session scope that should be deferred to Phase 2 or pulled forward to Phase 1.
6. **Resolved Section 9 decisions** in this addendum (`-002` §1) — verify each is actionable and testable.

A NO-GO with specific findings remains more valuable than a fast GO. The owner has explicitly paid the cost of detailed up-front planning to avoid loss-of-coherence; that cost should not be wasted on a rubber-stamp review.

## 5. Reversibility (No Change)

This addendum does not directly mutate any artifact. It records owner decisions for the proposal contract. Subsequent phase proposals execute the contract.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
