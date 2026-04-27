GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-001 Smart Bridge Trigger REVISED-3

Reviewed: 2026-04-27
Subject: `bridge/gtkb-bridge-poller-001-smart-poller-006.md`
Scope: umbrella scoping revision for smart bridge trigger program after Codex `-005` NO-GO
Verdict: GO

## Prior Deliberations

Relevant deliberations found:

- `DELIB-1121` records the halt of the OS pollers and the token-regression baseline.
- `DELIB-1104` records the prior bridge-poller thread state.
- `DELIB-0101` and `DELIB-0486` are relevant predecessor discussions.

The immediate operative prior review is `bridge/gtkb-bridge-poller-001-smart-poller-005.md`.

## Claim

GO on the umbrella restructure. REVISED-3 resolves the five `-005` scoping blockers at the program level: P1 is split out, autonomous invocation is gated behind an empirical spike, governance preservation is explicit, concurrency handling is specified enough for later detailed bridges, and the cost model now counts per-spawn startup/context cost separately from bridge work.

This GO does not approve the companion P1 detector proposal. That proposal is reviewed separately in the `gtkb-bridge-poller-p1-detector` bridge thread.

## Evidence

- `bridge/gtkb-bridge-poller-001-smart-poller-006.md` section 0 maps each Codex `-005` required revision item to a specific revised section.
- Section 3 adds a verification spike with exact evidence requirements: command invocation, exit code, stdout/stderr, files changed, token cost, and wall-clock duration for Claude and Codex headless modes.
- Section 3.3 correctly gates P3 invoker design on spike evidence, including the specific `--bare` governance-context risk identified in `-005`.
- Section 5 adds branch/worktree isolation, spawn locking, staging rules, dirty-worktree checks, and stale-transition checks.
- Section 6 explicitly requires formal-artifact approval, assertion/quality guardrails, credential scanning, and durable-role-record role selection to survive spawned sessions.
- Section 7 now separates detector cost, per-spawn startup/context cost, and per-spawn work cost. It explicitly acknowledges that with-hooks v1 is more expensive than manual scans but cheaper than the halted S308 poller peak.

## Risk / Impact

The largest risks remain in future phases, not in this umbrella scope:

- Whether `claude -p` / `codex exec` can preserve the same governance envelope as interactive sessions is still unknown. REVISED-3 correctly moves that to a required spike before invoker approval.
- Shared-worktree spawning remains risky. REVISED-3 narrows the risk with locks and dirty/stale checks, and leaves implementation-spawn isolation as an explicit owner/default decision before P3.
- The companion P1 detector needs revision before it can be the foundation for this umbrella.

## Implementation Constraints

- Do not implement P3 invoker behavior until a P2.5 verification-spike bridge is reviewed and GO'd with concrete local command evidence.
- Treat spawned implementation work as isolated-worktree by default unless Mike explicitly approves shared-worktree implementation spawns.
- Keep P1 detector/parser approval independent; a GO on this umbrella does not override a NO-GO in the companion detector thread.

## Decision Needed From Owner

Not for this GO. The proposal correctly queues owner decisions for later phases, after the spike/P1 evidence exists.

