# Dual-Agent Setup

<!-- © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. -->

Configure a Prime Builder and a Loyal Opposition agent with a shared file
bridge, start the OS-scheduler pollers, and walk through a complete
proposal → review → VERIFIED cycle.

## Prerequisites

- `groundtruth-kb` installed (`pip install groundtruth-kb`)
- Claude Code (Prime Builder) and Codex (Loyal Opposition) available on your
  workstation

---

## Step 1: Scaffold a Dual-Agent Project

```bash
gt project init my-project --profile dual-agent --owner "Your Name"
cd my-project
```

The `dual-agent` profile generates:

- `groundtruth.toml` + `groundtruth.db`
- `CLAUDE.md` and `MEMORY.md` — session state templates
- `AGENTS.md` — Loyal Opposition operating contract
- `BRIDGE-INVENTORY.md` — bridge runtime inventory
- `bridge-os-poller-setup-prompt.md` — prompt for configuring OS pollers
- `bridge/INDEX.md` — the file bridge coordination file
- `.claude/hooks/` and `.claude/rules/` — automation hooks and rules
- `independent-progress-assessments/` — Codex report storage

---

## Step 2: Start the OS-Scheduler Bridge

The file bridge uses OS-native scheduling to run Prime Builder and Loyal
Opposition on a recurring interval. See
[Bridge OS Scheduler](bridge-os-scheduler.md) for platform-specific setup
(macOS/Linux cron, Windows Task Scheduler).

The bridge poller script is generated at scaffold time from the
`bridge-os-poller-setup-prompt.md` file in your project root. Use that
prompt with Claude Code to configure the OS-scheduler pollers:

```bash
# Open bridge-os-poller-setup-prompt.md, fill in the placeholders,
# then paste it into Claude Code to set up the pollers automatically.
```

Once running, each poller:

1. Reads `bridge/INDEX.md` every 3 minutes
2. Dispatches the agent only when actionable work exists
3. Writes a status file under
   `independent-progress-assessments/bridge-automation/logs/`

Check bridge health at any time:

```bash
gt project doctor
```

---

## Step 3: Run a Proposal/Review Cycle

### Prime Builder writes a proposal

Create `bridge/my-feature-001.md`:

```markdown
# My Feature — Implementation Proposal

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

```
Document: my-feature
NEW: bridge/my-feature-001.md
```

### Loyal Opposition reviews

Codex will pick up the NEW entry within 3 minutes and write a review at
`bridge/my-feature-002.md` with a GO or NO-GO verdict. The INDEX entry
becomes:

```
Document: my-feature
GO: bridge/my-feature-002.md
NEW: bridge/my-feature-001.md
```

### Prime Builder implements

On GO, implement the feature, run tests, and write a post-implementation
report at `bridge/my-feature-003.md`. Update INDEX.md:

```
Document: my-feature
NEW: bridge/my-feature-003.md
GO: bridge/my-feature-002.md
NEW: bridge/my-feature-001.md
```

### Loyal Opposition verifies

Codex reviews the post-implementation report and writes VERIFIED
(or NO-GO) at `bridge/my-feature-004.md`:

```
Document: my-feature
VERIFIED: bridge/my-feature-004.md
NEW: bridge/my-feature-003.md
GO: bridge/my-feature-002.md
NEW: bridge/my-feature-001.md
```

VERIFIED is terminal — Prime Builder takes no further action on this entry.

---

## Step 4: Auth Troubleshooting

If the bridge poller reports `AUTH FAILURE`, see
[Auth Troubleshooting](../troubleshooting/auth.md) for provider-specific
re-auth steps.

---

## What's Next

- [Bridge OS Scheduler](bridge-os-scheduler.md) — platform-specific
  cron and Task Scheduler setup
- [Method: Dual-Agent](../method/06-dual-agent.md) — deeper explanation
  of the Prime Builder / Loyal Opposition model
- [Reference: CLI](../reference/cli.md) — full `gt project init` options
