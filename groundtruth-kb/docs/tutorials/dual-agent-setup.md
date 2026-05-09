# Dual-Agent Setup

Configure a Prime Builder and a Loyal Opposition agent with a shared file
bridge, activate the cross-harness event-driven trigger, and walk through a
complete proposal -> review -> VERIFIED cycle.

## Prerequisites

- `groundtruth-kb` installed (`pip install groundtruth-kb`)
- Claude Code (Prime Builder) and Codex (Loyal Opposition) available on your
  workstation

## Step 1: Scaffold a Dual-Agent Project

```bash
gt project init my-project --profile dual-agent --owner "Your Name"
cd my-project
```

The `dual-agent` profile generates:

- `groundtruth.toml` + `groundtruth.db`
- `CLAUDE.md` and `MEMORY.md` - session state templates
- `AGENTS.md` - Loyal Opposition operating contract
- `BRIDGE-INVENTORY.md` - bridge runtime inventory
- `bridge/INDEX.md` - the file bridge coordination file
- `.claude/hooks/`, `.claude/rules/`, `.claude/settings.json` - automation
  hooks, rules, and the cross-harness-trigger registration
- `.codex/hooks.json` - Codex-side hook registration for cross-harness
  parity
- `scripts/cross_harness_bridge_trigger.py` - the event-driven dispatch
  entrypoint
- `independent-progress-assessments/` - Codex report storage

`bridge-os-poller-setup-prompt.md` may also appear in the scaffold output as
a deprecated stub for two release cycles to give adopters time to migrate
references; do not follow its instructions.

## Step 2: Confirm Bridge Dispatch Automation

The file bridge uses `bridge/INDEX.md` as its authoritative queue. Bridge
dispatch is automated by the **cross-harness event-driven trigger**, which
fires on tool-use and Stop events rather than on a fixed interval. The
retired smart-poller and OS-scheduled-task implementations are no longer
used; see `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` and
`bridge-os-scheduler.md` (both DEPRECATED stubs) for retirement context.

The trigger entrypoint, hook registrations, and dispatch-state path are
scaffolded automatically. The relevant artifacts are:

- `scripts/cross_harness_bridge_trigger.py` - the trigger script that
  inspects `bridge/INDEX.md` and dispatches the appropriate counterpart
  harness when a recipient's actionable queue signature has changed.
- `.claude/settings.json` - registers the trigger as a `PostToolUse` and
  `Stop` hook on the Claude Code side.
- `.codex/hooks.json` - registers the trigger as a `PostToolUse` and `Stop`
  hook on the Codex side (forward-compatible per
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`).
- `.gtkb-state/bridge-poller/dispatch-state.json` - per-recipient
  dispatch-state record (read by the doctor's
  `_check_bridge_dispatch_liveness` check).

When a tool call modifies `bridge/INDEX.md` or the agent ends a turn, the
trigger evaluates whether the counterpart harness has actionable work and
dispatches it if so. Dispatch state is recorded in
`.gtkb-state/bridge-poller/dispatch-state.json` for both `prime-builder` and
`loyal-opposition` recipients.

Manual `bridge/INDEX.md` scans remain available as a fallback when the
trigger is unhealthy. The owner triggers a Prime bridge scan with a brief
prompt such as `Bridge` or `Bridge scan`; Codex bridge scans are similarly
owner-triggered in the Codex harness.

Check bridge dispatch health at any time:

```bash
gt project doctor
```

The doctor reports:

- `_check_cross_harness_trigger` - PASS/WARN/FAIL for trigger script
  presence, both hook registrations, and dispatch-state freshness.
- `_check_bridge_dispatch_liveness` - per-recipient dispatch-state liveness
  for `claude` and `codex`.

## Step 3: Run a Proposal/Review Cycle

### Prime Builder writes a proposal

Create `bridge/my-feature-001.md`:

```markdown
# My Feature - Implementation Proposal

**Status:** NEW
**WI:** WI-001

## Summary
Add a list_tasks() function to src/tasks.py that filters by status.

## Implementation plan
1. Add def list_tasks(status=None) to src/tasks.py
2. Add assertion to SPEC-002 for the list_tasks function

## Tests
- Unit test: list_tasks() returns [] when no tasks exist
- Unit test: list_tasks(status='open') returns only open tasks
```

Register it in `bridge/INDEX.md`:

```text
Document: my-feature
NEW: bridge/my-feature-001.md
```

### Loyal Opposition reviews

The cross-harness event-driven trigger fires when the INDEX update is
written, dispatching Codex with the actionable signature. Codex picks up
the NEW entry and writes a review at `bridge/my-feature-002.md` with a GO
or NO-GO verdict. The INDEX entry becomes:

```text
Document: my-feature
GO: bridge/my-feature-002.md
NEW: bridge/my-feature-001.md
```

### Prime Builder implements

On GO, implement the feature, run tests, and write a post-implementation
report at `bridge/my-feature-003.md`. Update INDEX.md:

```text
Document: my-feature
NEW: bridge/my-feature-003.md
GO: bridge/my-feature-002.md
NEW: bridge/my-feature-001.md
```

### Loyal Opposition verifies

Codex reviews the post-implementation report and writes VERIFIED (or
NO-GO) at `bridge/my-feature-004.md`:

```text
Document: my-feature
VERIFIED: bridge/my-feature-004.md
NEW: bridge/my-feature-003.md
GO: bridge/my-feature-002.md
NEW: bridge/my-feature-001.md
```

VERIFIED is terminal; Prime Builder takes no further action on this entry.

## Step 4: Auth Troubleshooting

If bridge automation reports `AUTH FAILURE`, see
[Auth Troubleshooting](../troubleshooting/auth.md) for provider-specific
re-auth steps.

## What's Next

- [Method: Dual-Agent](../method/06-dual-agent.md) - deeper explanation of the
  Prime Builder / Loyal Opposition model
- [Reference: CLI](../reference/cli.md) - full `gt project init` options
- Slice 3 closure (cross-harness-trigger hook registrations):
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`
- Slice 4 retirement (smart-poller retirement context):
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`
