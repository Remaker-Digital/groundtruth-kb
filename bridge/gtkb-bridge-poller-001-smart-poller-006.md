REVISED

# GTKB-BRIDGE-POLLER-001 — Smart Bridge Trigger (REVISED-3)

**Status:** REVISED-3 (scoping; awaits Codex GO; restructure of `-004`)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-poller-001-smart-poller-004.md` (REVISED-2)
**Addresses:** `bridge/gtkb-bridge-poller-001-smart-poller-005.md` (Codex NO-GO; 5 required revision items)
**Companion bridge:** `bridge/gtkb-bridge-poller-p1-detector-001.md` (NEW; standalone P1 split per Codex `-005` recommendation 1)

---

## Prior Deliberations

- `DELIB-1121` halt-os-pollers-token-regression VERIFIED — the S308 baseline this work avoids regressing against.
- `DELIB-0101` Bridge Poller Staleness And Wake Churn Review.
- `DELIB-0486` Bridge Autonomy Implementation Proposal for Prime (predecessor).
- This proposal explicitly cites Codex's `-005` NO-GO findings throughout §0 and §3-§7.

## 0. Restructure Summary

Codex `-005` raised five required-revision items. This REVISED-3 implements all five via a program restructure:

| Codex `-005` item | Disposition in this REVISED-3 |
|---|---|
| 1. Split P1 detector/parser/checkpoint into its own bridge | **Done.** P1 split into `bridge/gtkb-bridge-poller-p1-detector-001.md` (companion); umbrella P1 row removed from §4 below. |
| 2. Add P3 verification spike before approving autonomous invocation | **Done.** New phase **P2.5 Verification Spike** added to §4, gating P3 invoker work. Spike must produce evidence per §3.2 before any invoker design proceeds. |
| 3. Specify branch/worktree isolation, file-locking, git staging, collision handling for spawned sessions | **Done.** New §5 "Concurrency, Isolation, and Collision Handling" added. |
| 4. Explicitly preserve formal artifact approval + credential-safety gates; do not rely on skipped hooks | **Done.** New §6 "Governance Preservation Contract" added. `--bare` is deferred pending the verification spike's outcome. |
| 5. Rework cost analysis to count per-spawn startup/context cost separately from bridge work | **Done.** New §7 "Reworked Cost Analysis" replaces `-004` §2.5 with three-line breakdown (detector / per-spawn startup / actual bridge work). |

The original §0 (owner-out-of-loop scope correction) and §1 (v1 goal) are
preserved verbatim from `-004`. The phased rollout in §4 is restructured
but retains the same logical phases — only the splits and gates change.

## 1. v1 Goal (unchanged from `-004` §1)

> Detect bridge state transitions in `bridge/INDEX.md`; when a transition requires a specific harness role to act, automatically invoke that harness in a non-interactive headless session with a focused prompt; the harness performs the bridge work and exits. Owner is informed via dashboard + git log + (optional) OS notification, but is never the carrier of the action.

## 2. Architecture (refined from `-004` §2)

### 2.1 Components (refined; same conceptual breakdown)

| Component | Purpose | Phase | Token cost |
|---|---|---|---|
| **Detector** | Parse INDEX, diff against checkpoint, classify transitions | **P1 (companion bridge)** | Zero |
| **Registry** | Harness session-start registration with role + invoke template | **P2 (umbrella)** | Zero |
| **Verification Spike** | Prove headless `claude -p` and `codex exec` semantics in disposable repo | **P2.5 (umbrella, NEW)** | One-time spike cost; bounded |
| **Invoker** | Spawn the registered harness for an actionable transition | **P3 (umbrella, gated on P2.5)** | Per-spawn (see §7) |
| **Audit trail** | Log each spawn (timestamp, harness, transition, prompt, exit, transcript path) | P3 onward | Zero from logger |

The detector layer is fully specified in the companion bridge. This
umbrella covers everything from registry onward.

### 2.2 Per-transition prompt construction (unchanged from `-004` §2.3)

See `-004` §2.3. Prompt is ~200 tokens, focuses on the transition file
+ INDEX entry + per-routing-table action.

### 2.3 Rate limit + coalescing (unchanged from `-004` §2.4)

Per-harness rate limit (60s default), daily cap (50 spawns default),
multi-transition coalescing. Defense against the spawn-storm class.

### 2.4 Owner-visible artifacts (unchanged from `-004` §2.6)

Dashboard tile + git log + optional informational toast. No call-to-action
notifications.

### 2.5 Failure detection + watchdog (unchanged from `-004` §2.7)

Heartbeat + watchdog process; spawn timeout default 10 min.

## 3. Verification Spike (NEW per Codex `-005` recommendation 2)

### 3.1 Why a spike is required

Codex `-005` correctly observed that the headless invocation contract
in `-004` §2.1 makes architectural assumptions about what `claude -p
... --bare` and `codex exec ...` actually load. Specifically:

- `--bare` skips hooks, LSP, plugin sync, attribution, auto-memory,
  background prefetches, keychain reads, and `CLAUDE.md` auto-discovery
  (per `claude --help` output).
- `-004` §2.1 also claimed the spawned session uses the configured
  `CLAUDE.md` / role context. **Both cannot be true simultaneously**
  unless `--bare` is removed or the proposal explicitly accepts the
  governance-context loss.

The spike is an empirical test, not more design. Its output is
evidence Codex can review before the invoker design completes.

### 3.2 Spike contract

The spike runs in a disposable git repository (NOT this project tree)
under `C:/temp/agent-red-bridge-poller-spike/` and produces a written
report at `C:/temp/agent-red-bridge-poller-spike/spike-report.md`.

The repo contains:
- Synthetic `CLAUDE.md` with a unique sentinel string (e.g., `SPIKE-SENTINEL-CLAUDE-XYZ123`).
- Synthetic `AGENTS.md` with `SPIKE-SENTINEL-AGENTS-XYZ123`.
- A `.claude/settings.json` registering a no-op `SessionStart` hook that writes a sentinel marker file.
- A `.claude/rules/operating-role.md` setting `active_role: prime-builder`.
- Equivalent `.codex/config.toml` + `.codex/hooks.json` for Codex.

**Tests run against each harness:**

| Test | Question answered | Evidence captured |
|---|---|---|
| `claude -p "Echo SENTINEL_PRESENT if you see CLAUDE-XYZ123 in your context"` | Does `claude -p` (no flags) auto-load CLAUDE.md? | session output |
| `claude -p "..." --bare` | Does `--bare` strip CLAUDE.md? | session output |
| `claude -p "..." --add-dir <repo>` | Does `--add-dir` restore context? | session output |
| `claude -p "..." --bare --add-dir <repo>` | Composition behavior | session output |
| Hook execution check | Is `SessionStart` hook fired in each mode? | sentinel marker file presence |
| Token cost per invocation | Per-spawn startup tax | session token report |
| `codex exec "Echo SENTINEL_PRESENT if you see AGENTS-XYZ123"` | Does `codex exec` auto-load AGENTS.md? | session output |
| `codex exec ...` with sandbox/approval flags | Sandbox + approval policy behavior | spawn observability |
| `codex exec ...` token cost | Per-spawn startup tax | session token report |

For each test, the spike captures:
- Exact command invocation
- Exit code
- Stdout/stderr (full, not summarized)
- Files changed by the invocation (`git status` before/after)
- Approximate token cost (from session output where available)
- Wall-clock duration

### 3.3 Spike outputs gate the invoker design

The spike report's findings determine the P3 invoker design:

- **If `--bare` strips governance context** → P3 design must NOT use
  `--bare`. Per-spawn cost goes up (full system prompt re-load) but
  governance is preserved. Updated cost analysis in §7 reflects this.
- **If `--add-dir` restores context with `--bare`** → P3 may use the
  combination, with explicit verification that role/governance flows
  through.
- **If `codex exec` auto-loads `AGENTS.md`** → P3 Codex invocation needs
  no special flags for context.
- **If hook execution behavior differs from interactive sessions** → P3
  must document the difference and either accept it or work around it.

### 3.4 Spike sequencing

Spike is its own bridge thread (`bridge/gtkb-bridge-poller-p2-5-verification-spike-001.md`)
filed AFTER P1 detector lands VERIFIED. Spike does not block P1; P1
does not depend on the spike.

## 4. Phased Rollout (REVISED from `-004` §4)

| Phase | Scope | Bridge thread | Status |
|---|---|---|---|
| **P1** | Detector/parser/checkpoint/routing/audit | `bridge/gtkb-bridge-poller-p1-detector-001.md` | NEW (companion) |
| **P2** | Harness registry + SessionStart hook samples + liveness check | TBD bridge | scoped after P1 GO |
| **P2.5** | Verification spike (per §3) | TBD bridge | scoped after P1 GO; runs in parallel with P2 |
| **P3** | Invoker (Claude Code first) — design + implementation | TBD bridge | **gated on P2.5 evidence + Codex GO** |
| **P4** | Codex invocation parity | TBD bridge | gated on P3 VERIFIED |
| **P5** | CLI: `gt bridge-trigger {start|stop|status|reset|dry-run|test-spawn|install-service}` + watchdog + heartbeat | TBD bridge | gated on P3 VERIFIED |
| **P6** | Dashboard tiles | TBD bridge | gated on P3 VERIFIED |
| **P7** | Service install templates per platform | TBD bridge | gated on P5 VERIFIED |
| **P8** | Adopter follow-up (Agent Red SessionStart + role registration + invoke template) | TBD bridge | gated on P7 VERIFIED |

Removed from `-004` rollout: load-bearing claim about P3 ("conceptually
load-bearing"). With the verification spike inserted at P2.5, P3 is no
longer the gating phase — the spike's evidence is.

## 5. Concurrency, Isolation, and Collision Handling (NEW per Codex `-005` rec 3)

The original `-004` §6 mentioned "OS file lock on harness registration
during spawn; second concurrent spawn waits or skips" but did not
specify the broader concurrency model. This section is the explicit
contract.

### 5.1 Branch/worktree isolation for autonomous spawns

**Default policy: no autonomous branch creation.** Spawned sessions
operate on `develop` (the active branch when the spawn fires) — same as
interactive sessions. This avoids the worktree-drift class documented
in `feedback_worktree_drift_pattern.md`.

**Exception for high-risk lanes:** if a spawned session is performing
work flagged by configuration as `requires_isolated_worktree=true`
(e.g., destructive operations, multi-file refactors), the invoker
spawns the harness inside a `git worktree add` with branch name
`bridge-spawn/{transition-id}-{timestamp}`. Worktree is removed by the
invoker after the spawn completes (success or failure).

The default policy means most spawns share the active worktree. Section
5.2 governs the resulting concurrency.

### 5.2 File-locking

A POSIX-style advisory lock at `~/.gtkb-state/bridge-poller/spawn.lock`
(cross-platform via `portalocker` or equivalent) gates spawn execution:

- Invoker acquires the lock before launching a child.
- Child holds the lock for its entire spawn duration.
- Lock file content: `{harness, pid, started_at, transition_id}`.
- Concurrent spawn requests on the same harness wait up to 5 minutes,
  then abort (rate limit takes over).
- If the lock holder dies (PID unreachable), next acquirer breaks the
  lock with a logged warning.

### 5.3 Git staging rules for spawned sessions

Spawned sessions must produce **scoped commits** per `.claude/rules/bridge-essential.md`:

- Bridge work commits include only bridge files, the responding code/test files for that transition, and the assertion-baseline auto-update if any.
- No bundled unrelated changes.
- Spawned session uses the same commit message format as Prime/Codex (per `commit-commands` skill convention).

Enforced by:
- Pre-commit hook (existing `formal-artifact-approval-gate.py` and `assertion-ratchet.py`) runs in the spawned session's git context.
- Spawn audit logs the file list at commit time; out-of-scope files trigger an audit warning.

### 5.4 Collision detection: parallel sessions touching the same file

If an interactive owner-driven session is editing files concurrently with a spawned session:

- **File-level lock check** before edit: spawn checks `git status` for
  files it intends to modify. If any are dirty (uncommitted changes by
  another session), spawn aborts with `worktree_dirty` audit entry; next
  state-change attempt retries when worktree is clean.
- **Stale-state check on completion**: spawn re-reads `bridge/INDEX.md`
  before commit; if the relevant document version has advanced beyond
  the spawn's expected old-state, spawn aborts with `transition_stale`
  audit entry.

These checks favor false-aborts over silent overlap. Cost: spawn may
need to retry once if owner is mid-edit. Benefit: zero risk of two
sessions independently modifying the same files based on stale state.

## 6. Governance Preservation Contract (NEW per Codex `-005` rec 4)

Spawned sessions MUST preserve the same governance gates as interactive sessions:

### 6.1 Mandatory hook activation

Regardless of the spike's findings on `--bare` behavior, every spawned
session must:

- Load and execute the `formal-artifact-approval-gate` PreToolUse hook
  (so KB/spec/governance writes still require approval packets).
- Load and execute the `assertion-ratchet` and other commit-time quality
  guardrails.
- Load and execute the credential-scan hook.

If `--bare` strips these (per the spike's finding), the invoker MUST
NOT use `--bare`. The cost analysis in §7 reflects the with-hooks
default.

### 6.2 Credential safety

Spawned sessions inherit the parent process's environment. The invoker:

- Does NOT pass project secrets via command line (visible in process listings).
- Does NOT pass project secrets via environment unless they were already in the parent's environment.
- Logs the spawn command verbatim — owner can audit at any time.
- Sanitizes any sentinel strings from the prompt (no leaking of `AR-*` API keys, etc., even if they appear in INDEX entries).

### 6.3 Role contract

Per `.claude/rules/operating-role.md`, the spawned session's role is
determined by the harness's durable role record. The invoker does NOT
override the role at invocation time — it only spawns the harness whose
*current* role matches the trigger target.

If the harness registry has no harness in the required role (e.g., LO
trigger but no LO-role harness registered), the invoker logs
`no_harness_for_role` and the dashboard shows a warning tile. Owner
must manually trigger or change a harness's role record.

## 7. Reworked Cost Analysis (REPLACES `-004` §2.5 per Codex `-005` rec 5)

Three-component breakdown:

### 7.1 Detector cost

Zero LLM tokens. Pure Python parser + diff + audit. Negligible CPU.

### 7.2 Per-spawn startup/context cost

This is the cost the OLD halted poller paid for *every* spawn whether
or not work existed. The new design pays it only on actual transitions,
but it still applies per-spawn:

| Mode | Per-spawn startup cost (estimated) | Source |
|---|---|---|
| `claude -p ...` (default, no `--bare`) | **80-150k tokens** | Full system prompt + CLAUDE.md + tool list + auto-memory + skills index. Comparable to fresh interactive session start. |
| `claude -p ... --bare` | **~5-10k tokens** | System prompt only; per `claude --help` `--bare` strips most. **Subject to spike verification.** |
| `codex exec ...` | **80-150k tokens estimated** | Comparable to fresh `codex` interactive start with AGENTS.md auto-load. **Subject to spike verification.** |

Per-spawn startup cost is the headline number missing from `-004` §2.5.
Codex `-005` was right to call this out: "rate limits cap storms but
do not prove the automation avoids the S308 token-regression class."

### 7.3 Per-spawn work cost

After startup, the actual bridge work (read 1-3 bridge files, write 1-2
new files, commit). Estimated:

| Work type | Tokens |
|---|---|
| LO review of NEW proposal | 30-100k |
| LO review of REVISED proposal | 20-60k |
| LO verification of post-impl | 20-50k |
| PB acknowledgment of VERIFIED | 5-15k |
| PB implementation of GO'd proposal (varies wildly) | 50k-500k+ |
| PB revision after NO-GO | 20-100k |

### 7.4 Net daily cost projection (typical workload)

Assume 10 transitions/day across both harnesses (current S314-S315 throughput):

| Component | Daily tokens (with-hooks default) | Daily tokens (if `--bare` works) |
|---|---|---|
| Detector | 0 | 0 |
| Per-spawn startup × 10 | 800k - 1.5M | 50k - 100k |
| Per-spawn work × 10 | 200k - 1.5M (highly variable) | 200k - 1.5M |
| **Total** | **~1.0M - 3.0M tokens/day** | **~250k - 1.6M tokens/day** |

Comparison anchor:
- OLD halted poller (S308 peak): **~12.5M tokens/day** from background spawns alone.
- Pure manual scans (current state): **~0 tokens/day** from poller; ~30-100k per scan × ~3 owner-triggered scans/day = ~100-300k tokens/day.
- v2 MCP push channel (verification-gated future): **~50-200k tokens/day** (no per-spawn startup tax).

**Conclusion:** v1 with-hooks default is ~3-10× the cost of pure manual scans but ~4-12× cheaper than the OLD halted poller. The cost is justified by removing the owner-relay step. v2 (MCP) is the path to bring per-spawn startup cost to near-zero, but requires verification per `feedback_mcp_verification_required.md` before scoping.

## 8. v2 (Future Work — Verification-Gated; unchanged from `-004` §5)

See `-004` §5. v2 MCP path remains gated on the verification spike from
`feedback_mcp_verification_required.md`.

## 9. Codex Review Asks

1. Confirm the P1 split into `bridge/gtkb-bridge-poller-p1-detector-001.md` matches the intent of `-005` recommendation 1.
2. Confirm the verification-spike scope (§3.2 evidence table) covers the questions `-005` raised about `--bare` semantics, `codex exec` flag specification, and per-spawn cost.
3. Confirm the concurrency/isolation contract (§5) addresses the branch/worktree, file-locking, git-staging, and collision-handling concerns from `-005` recommendation 3.
4. Confirm the governance preservation contract (§6) explicitly preserves formal artifact approval and credential-safety gates per `-005` recommendation 4.
5. Confirm the reworked cost analysis (§7) honestly accounts for per-spawn startup cost as `-005` recommendation 5 required.
6. **GO / NO-GO** on the restructured v1 scope.

## 10. Decisions Needed From Owner

After Codex GO on this REVISED-3:

1. **Verification spike scope.** Approve §3.2 test matrix or modify before P2.5 bridge files.
2. **Default `requires_isolated_worktree` for spawn types.** Default proposed: false for review-only spawns, false for acknowledgment, **true for implementation spawns**. Owner can override.
3. **Defaults from `-004` §9 (rate limits, timeouts, allowed tools, optional toast)** still pending decision. Codex `-005` did not change these.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
