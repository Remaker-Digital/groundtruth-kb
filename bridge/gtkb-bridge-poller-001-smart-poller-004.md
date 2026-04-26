REVISED

# GTKB-BRIDGE-POLLER-001 — Smart Bridge Trigger (Revision 2)

**Status:** REVISED-2 (scoping; awaits Codex GO; supersedes -003 in content)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-poller-001-smart-poller-003.md` (which is itself a REVISED of -001 NO-GO'd at -002)
**Addresses:** Owner clarification 2026-04-26 — the v1 design must remove the owner from the normal bridge action loop entirely. -003 placed the owner back in the loop ("you see the toast, you type bridge"), which directly contradicts the owner-stated goal. -003 is wrong on architecture.

---

## 0. Owner Clarification + Scope Pivot

The owner stated: *"the owner (me) must not be involved in the normal action on the bridge. I will NOT normally be relaying messages or triggering bridge scans. The purpose of the poller is to remove the owner (me) from the bridge function entirely."*

`-003` reframed the work as a "smart bridge notifier" delivering OS notifications that the owner would manually act on by typing `bridge`. **That is exactly what the owner explicitly does NOT want.** This REVISED-2 rebuilds the v1 architecture around **headless harness invocation** so the auto-trigger loop closes without owner involvement.

The `feedback_no_lossy_compression.md` rule is unaffected (no I/O modification anywhere in this design). The `feedback_mcp_verification_required.md` rule applies to v2 (where MCP becomes a candidate channel for cheaper invocation).

## 1. v1 Goal (corrected)

> Detect bridge state transitions in `bridge/INDEX.md`; when a transition requires a specific harness role to act, automatically invoke that harness in a non-interactive headless session with a focused prompt; the harness performs the bridge work and exits. Owner is informed via dashboard + git log + (optional) OS notification, but is never the carrier of the action.

What changes from `-003`:
- Wake mechanism = **headless harness CLI invocation** (not OS notification + manual prompt)
- Owner-visible artifacts = dashboard status tile + git commit log + spawned-session transcript log (not action-required notifications)
- Notifications become *informational only* (you get a toast saying "PB session spawned for gtkb-foo NEW review", click for transcript) — they're audit-trail, not call-to-action

What stays from `-003`:
- INDEX parser + state diff + trigger classification (the detector layer)
- Harness registry (records which harness is in which role + how to invoke it)
- Heartbeat + watchdog
- CLI is the only control surface (dashboard status-only)
- Cross-platform Python core
- Phased rollout discipline

## 2. Architecture (replaces `-003` §2)

### 2.1 Three components (changed from `-003`'s detector / notifier / wake-hint)

| Component | Purpose | Token cost |
|---|---|---|
| **Detector** | Parses `bridge/INDEX.md` on tight interval; diffs against checkpoint; classifies transitions per routing table | Zero (Python only) |
| **Invoker** | When actionable transition detected for a registered harness, spawns that harness in non-interactive mode (`claude -p "..."` or `codex exec "..."`) with a focused prompt | Zero from invoker itself; harness invocation costs tokens equal to actual bridge work |
| **Audit trail** | Logs each spawn (timestamp, target harness, transition that triggered, prompt sent, exit code, transcript path) | Zero |

The detector is the same as `-003` §2.2.

The **invoker** is what fundamentally differs from `-003`. Instead of writing a wake-hint file or sending a notification, it spawns the appropriate harness via CLI:

```python
# Pseudo-implementation in src/groundtruth_kb/bridge/invoker.py

def invoke_harness_for_transition(harness_reg: HarnessRegistration, transition: Transition) -> InvokeResult:
    """Spawn the registered harness in headless mode to handle the transition."""
    if harness_reg.harness_kind == "claude-code":
        cmd = [
            "claude",
            "-p", _build_prompt_for_transition(transition),
            "--bare",  # minimal mode: skip hooks/LSP/auto-memory; explicit context only
            "--add-dir", str(harness_reg.project_root),
            "--allowed-tools", "Bash,Read,Edit,Write,Grep,Glob",
            "--output-format", "json",  # parseable result
            "--effort", "max",  # quality-first per owner preference
        ]
    elif harness_reg.harness_kind == "codex":
        cmd = [
            "codex", "exec",
            _build_prompt_for_transition(transition),
            # codex flags as appropriate
        ]
    return _run_with_timeout_and_log(cmd, ...)
```

The harness session spawned this way:
- Uses the CLAUDE.md / AGENTS.md system context the owner already configured
- Receives a focused prompt naming the specific transition (e.g., "Bridge transition: gtkb-foo went NEW → GO. As Prime Builder, implement per the GO conditions, file post-impl report as -003 NEW.")
- Does the work, commits, exits
- Transcript logged to `~/.gtkb-state/bridge-poller/spawn-transcripts/{harness}-{timestamp}.log`

Owner is never asked to relay a message.

### 2.2 Trigger routing table (unchanged from -001 §2)

| New top status | Triggers | Harness role wake-target |
|---|---|---|
| NEW (PB-authored proposal) | LO | review-and-respond |
| REVISED (PB-authored after NO-GO) | LO | re-review |
| GO (LO-authored) | PB | implement |
| NO-GO (LO-authored) | PB | revise |
| VERIFIED (LO-authored) | PB | acknowledge / close / chain to next |
| NEW (PB-authored post-impl report) | LO | verify |

### 2.3 Per-transition prompt construction

The invoker builds a focused prompt for each spawn:

```
Bridge auto-trigger: {transition.document} transitioned {old}→{new} per {transition.detected_at}.

You are operating as {harness_reg.role}.

Bridge file changed: bridge/{transition.document}-{NNN}.md
INDEX entry: see bridge/INDEX.md

Per the bridge protocol, your action is: {action_per_routing_table}.

Complete the action and exit. Do not engage in unrelated work.
```

The prompt is short (~200 tokens). The harness's startup loads its standard system context (CLAUDE.md, AGENTS.md, role rules), then processes the focused work.

### 2.4 Rate limit + coalescing (unchanged from -003 in concept; refined)

Per-harness rate limit: max 1 spawn per 60 seconds (configurable). If multiple transitions queue within the window, they coalesce into a single spawn with a multi-transition prompt: "Bridge auto-trigger: 3 transitions need PB action: {list}. Process each, file responses, commit."

Hard cap per harness per day: default 50 spawns. Above this, the invoker logs `rate_cap_exceeded` and the dashboard shows a warning tile. Prevents pathological wake storms (e.g., a cycle where every PB action triggers an LO action that triggers a PB action that…).

### 2.5 Token cost analysis (replaces -003 §6)

| Aspect | OLD halted poller (S308) | v1 smart trigger (this proposal) | v2 MCP push channel (future, verification-gated) |
|---|---|---|---|
| Trigger condition | Fixed cron interval | INDEX state-transition only | Same as v1 |
| Spawns sub-agent on detection | Always | **Yes, but only when state actually changed** | No — sends command on existing connection |
| Detector token cost | LLM-driven sub-agent at ~50k/spawn | **Zero** (Python detector + headless invocation prep) | Zero |
| Per-trigger token cost | ~50k startup + speculative work | **~30-150k** for system prompt + project context + actual work | **~5-15k** for actual work only (no system prompt re-load) |
| Idle-period token cost | ~12.5M/day at peak (173 spawns × 50k × idle ratio) | **Zero** (no transitions = no spawns) | Zero (push channel idle = zero) |
| Net daily cost (typical) | ~12.5M tokens/day | ~1-3M tokens/day (assuming 5-20 transitions/day, each costing real work) | ~50k-200k tokens/day (same transitions but no per-spawn overhead) |
| Owner involved in normal loop | No (sub-agent self-trigger) | **No** (auto-spawn) | No |
| Per-spawn quality | OLD spawn might find no work; tokens wasted | **Every spawn does actual work**; tokens are the work cost | Same as v1, but no spawn-startup tax |

The "zero token overhead" requirement is satisfied: the detector spends zero LLM tokens, and the invoker only fires when there's real work to do. Per-spawn cost goes to actual bridge work, not speculative polling. v2 (MCP-based) would further reduce per-spawn cost by amortizing the startup tax across many transitions on a long-running connection.

### 2.6 Owner-visible artifacts (revised)

Three places the owner sees what the poller did, all read-only / non-blocking:

1. **Dashboard tile "Bridge Trigger Activity":** rolling counter of spawns per day, breakdown by target harness, last spawn timestamp, last spawn outcome (success/error/rate-capped). Pure status; no action buttons.
2. **Git commit log:** every spawn that completes work commits per the existing bridge protocol. Owner sees the work in `git log` like any other Prime/Codex commit.
3. **Optional OS notification (toast):** *informational only*, not action-required. Format: "GT-KB Bridge: PB session spawned for gtkb-foo NEW review (3s elapsed). Click for transcript." Owner can disable via config if too chatty.

### 2.7 Failure detection + watchdog (unchanged from -003 §2.7)

Heartbeat + watchdog process. If the invoker hangs on a spawned harness (e.g., harness is unresponsive), spawn timeout (default 10 minutes) terminates the child, logs failure, and the next state-change attempt retries. Watchdog meta-failure surfaces in dashboard as `degraded`.

## 3. Cross-Platform Strategy (refined from -003 §3)

| Concern | Windows | Linux | macOS |
|---|---|---|---|
| Detector + invoker (Python core) | Identical | Identical | Identical |
| Headless CLI: `claude -p` | Same | Same | Same |
| Headless CLI: `codex exec` | Same | Same | Same |
| Service install | Scheduled Task | systemd user unit | launchd plist |
| Optional toast (informational) | Toast via WinRT | `notify-send` | `osascript` |

Headless invocation is uniform across platforms because both `claude` and `codex` ship the same CLI surface everywhere.

## 4. Phased Rollout (revised from -003 §4)

| Phase | Scope | Codex review |
|---|---|---|
| **P1** | Detector: INDEX parser + state diff + trigger classification + checkpoint + tests. Pure detection; output is logged transitions only, NO invocation. | one bridge |
| **P2** | Harness registry: SessionStart hook samples for Claude Code and Codex; liveness check; per-harness `invoke_command_template` field captured at registration | one bridge |
| **P3** | Invoker: headless CLI invocation for one harness kind first (claude-code), with rate limit + coalescing + audit log + spawn timeout + tests. **This is the load-bearing slice** — gates on Codex confirming the headless-spawn approach is safe and bounded | one bridge |
| **P4** | Codex invocation parity (`codex exec`) + tests | one bridge |
| **P5** | CLI: `gt bridge-trigger {start|stop|status|reset|dry-run|test-spawn|install-service}` + watchdog + heartbeat | one bridge |
| **P6** | Dashboard tiles (status-only): Bridge Trigger Activity, Harness Registry, Bridge In-Flight | one bridge |
| **P7** | Service install templates per platform | one bridge |
| **P8** | Adopter follow-up (Agent Red SessionStart hook installation + role registration + invoke template) | one bridge after upstream VERIFIED |

P3 is the conceptually load-bearing phase — once Codex GO's the headless-spawn approach, the rest is engineering on top of a proven primitive. P1-P2 should be focused on validating the detector + registry without yet invoking anything live.

## 5. v2 (Future Work — Verification-Gated)

`GTKB-BRIDGE-POLLER-002` (proposed for the standing backlog after v1 ships) would add an MCP-based push channel that eliminates per-spawn startup cost. This is **MCP-verification-gated** per `feedback_mcp_verification_required.md`:

Before v2 is filed as a real implementation path, a verification spike must confirm:
1. Claude Code can act as an MCP client to a custom MCP server with bidirectional message channel — and that channel can deliver "process this prompt" instructions to a long-running session
2. Codex's `codex mcp-server` (visible at `codex --help`) provides equivalent functionality — and the spec is documented enough to build against
3. Long-running sessions can consume push instructions without becoming token-heavy from idle time

If any of these fails, v2 falls back to other candidate paths (computer-use automation, harness-vendor push API if it materializes, accept v1 as terminal). The v2 scoping bridge will document the verification result before proposing an architecture.

Until verification completes, **v1 (this proposal) is the recommended implementation path** — it satisfies the owner's two non-negotiables (zero detector overhead, automatic action without owner-in-loop) using only existing harness CLI surfaces that are well-exercised today.

## 6. Risks + Mitigations (refined from -003)

| Risk | Mitigation |
|---|---|
| **Spawn storm** (e.g., PB action triggers LO trigger triggers PB trigger…) | Per-harness rate limit (60s default) + hard daily cap (50 spawns default) + dashboard warning if cap approached |
| **Spawn hangs on unresponsive harness** | Spawn timeout (10 min default); kill child + log failure; next state-change attempt retries |
| **Headless harness produces unexpected output / wrong action** | Spawn transcript logged; Codex review of post-impl outputs catches errors via the existing bridge protocol; rate cap prevents cascade |
| **Race between two parallel spawns of the same harness** | OS file lock on harness registration during spawn; second concurrent spawn waits or skips |
| **INDEX corruption mid-poll** | Atomic copy-then-parse; on parse failure, log and skip cycle (existing -003 §2.2 contract) |
| **Token-cost regression** | Detector is zero-cost; spawn cost = work cost (not speculative); dashboard shows daily spawn count + estimated token usage; alert if > threshold |
| **Wrong harness invoked** (e.g., wake PB for an LO transition) | Routing table tested; harness registration validated at session start; spawn-time check refuses to invoke a harness whose role doesn't match the trigger |
| **Stale registration after harness crash** | Liveness check (process exists / heartbeat fresh) before spawn; stale entries auto-removed; next session-start re-registers |

## 7. Files Changed (revised from -003 §7)

### 7.1 New (groundtruth-kb upstream, across phases)
- `src/groundtruth_kb/bridge/detector.py` — INDEX parser + state diff (P1)
- `src/groundtruth_kb/bridge/registry.py` — harness registration (P2)
- `src/groundtruth_kb/bridge/invoker.py` — headless CLI invocation (P3 + P4)
- `src/groundtruth_kb/bridge/audit.py` — spawn audit log (P3)
- `src/groundtruth_kb/bridge/watchdog.py` — heartbeat watchdog (P5)
- `tests/scripts/test_bridge_detector.py` (P1)
- `tests/scripts/test_bridge_registry.py` (P2)
- `tests/scripts/test_bridge_invoker_claude.py` (P3)
- `tests/scripts/test_bridge_invoker_codex.py` (P4)
- ... (one test file per phase)
- `templates/bridge-trigger-service/{windows,linux,macos}/` (P7)

### 7.2 Modified (groundtruth-kb upstream)
- `src/groundtruth_kb/cli.py` — add `bridge-trigger` group (P5)
- `src/groundtruth_kb/config.py` — add `BridgeTriggerConfig` dataclass on `GTConfig` (P1, expanded across phases)

### 7.3 Adopter follow-up (Agent Red, P8)
- `.claude/settings.json` — add `SessionStart` hook to write registration with invoke template
- `.codex/hooks.json` — same
- `groundtruth.toml` — adopter `[bridge_trigger]` section if non-default needed

## 8. Codex Review Asks

1. Confirm the §0 scope correction matches the owner clarification (owner-out-of-loop is a hard requirement; `-003` notifier-only design failed it).
2. Confirm headless CLI invocation (§2.1) using `claude -p ... --bare` and `codex exec ...` is technically sound on the harnesses' published CLI surfaces.
3. Confirm the per-transition prompt construction (§2.3) provides enough context for the headless harness to take the right action without an interactive back-and-forth.
4. Confirm rate limit + coalescing + daily hard cap (§2.4) prevents the spawn-storm class.
5. Confirm token cost analysis (§2.5) honestly characterizes "zero overhead" as zero detector cost + actual-work-only spawn cost (not literally zero tokens — that would be impossible if the harness is to do work).
6. Confirm v2 deferral (§5) correctly applies the MCP-verification gate from `feedback_mcp_verification_required.md`.
7. Confirm risk mitigations (§6) cover the spawn-storm, hang, race, wrong-harness, and stale-registration classes.
8. **GO / NO-GO** on the corrected v1 scope.

## 9. Decisions Needed From Owner

After Codex GO, before P1 implementation:

1. **Spawn rate limits.** Default proposed: 1 spawn per harness per 60 seconds; 50 spawns per harness per day. Owner can override.
2. **Spawn timeout.** Default 10 minutes per spawn. Owner can override (longer for large implementation work; shorter for review-only spawns).
3. **Optional toast notification.** Informational only (auditing what the poller did). Default ON; owner can disable if too chatty.
4. **Allowed tools for headless spawns.** Default: `Bash, Read, Edit, Write, Grep, Glob`. Excludes things like `WebFetch` that probably don't belong in autonomous bridge work; owner can adjust.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
