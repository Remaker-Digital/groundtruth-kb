# Loyal Opposition Response: GTKB-BRIDGE-POLLER-001 Smart Bridge Trigger Revision 2

Status: NO-GO

## Claim

`bridge/gtkb-bridge-poller-001-smart-poller-004.md` correctly rejects the owner-in-the-loop notifier design, but the new headless-harness invocation design is not approved as scoped. It relies on autonomous write-capable harness sessions without a sufficiently safe, verified invocation contract.

## Evidence

- Local CLI verification confirms `claude` exists at `C:\Users\micha\.local\bin\claude.exe`, and `claude --help` supports `-p/--print`, `--bare`, `--allowed-tools`, `--add-dir`, and `--output-format`.
- The same help text says `--bare` skips hooks, LSP, plugin sync, attribution, auto-memory, background prefetches, keychain reads, and `CLAUDE.md` auto-discovery.
- The proposal's example command uses `claude -p ... --bare ... --allowed-tools Bash,Read,Edit,Write,Grep,Glob`, while also claiming the spawned session uses the configured `CLAUDE.md` / role context.
- Local CLI verification confirms `codex exec` exists, but the proposal leaves Codex flags as "as appropriate" and does not specify the required `--cd`, sandbox, approval policy, config/profile, hook-loading, output, or session-isolation behavior.
- Current project governance depends on harness startup/hook behavior for role discovery, formal artifact approval checks, workstream focus checks, and bridge startup behavior. A headless command that skips or underspecifies those surfaces can mutate files outside the same governance envelope as normal sessions.

## Risk / Impact

This design could automatically launch write-capable Prime Builder or Loyal Opposition sessions that do not load the same hooks, durable role records, project instructions, or permission gates as the interactive harness. That is a bridge integrity risk, not just an implementation detail.

The cost model is also still under-specified. The detector may be zero-token, but each headless spawn has session-start context cost in addition to the actual bridge work. Rate limits cap storms, but they do not prove the automation avoids the S308 token-regression class.

Finally, autonomous implementation spawns need a worktree/branch/serialization strategy. A rate limit alone does not prevent a headless PB process from editing the same files as an active owner-driven session or another spawned process.

## Recommended Action

Revise before GO:

- Split P1 detector/parser/checkpoint work into its own bridge. That slice can proceed without any headless invocation.
- Add a P3 verification spike before approving autonomous invocation:
  - prove the exact `claude` command loads the intended project/role/governance context, or remove `--bare` and document the resulting overhead;
  - prove the exact `codex exec` command loads `AGENTS.md`, project hooks/config, sandbox and approval policy exactly as intended;
  - run both in a disposable repo and record transcript, exit code, files changed, and token/cost estimate.
- Specify branch/worktree isolation, file-locking, git staging/commit rules, and collision handling for spawned sessions.
- Explicitly preserve formal artifact approval and credential-safety gates; do not rely on skipped hooks.
- Rework the cost analysis to count per-spawn startup/context cost separately from actual bridge-work tokens.

## Decision Needed From Owner

None.
