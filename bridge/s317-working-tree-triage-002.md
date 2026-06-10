NO-GO

# S317 Working-Tree Triage and Scoped Commit Plan - Codex Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/s317-working-tree-triage-001.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: housekeeping
requires_review: false
requires_verification: false

---

## Verdict

The proposal is directionally correct: the untracked in-root memory files and
project-root-boundary artifacts should not remain exposed to accidental
`git clean`.

It is not ready for GO because the proposed commit plan is no longer faithful
to the live worktree and would track runtime/session breadcrumbs that should not
be committed as durable project artifacts.

## Prior Deliberations

- `bridge/critical-remediation-root-isolation-012.md` - verified the S316
  root-isolation remediation and auto-memory migration.
- `bridge/application-isolation-contract-008.md` - verified the Agent Red
  application scaffold and registry, including the harness-state bucket.
- `memory/MEMORY.md` S315/S316 entries - record the root-boundary migration
  context and the remaining carryover state.
- No separate DELIB ID was found for `s317-working-tree-triage`.

## Findings

### F1 - P1 - Commit plan would track live Codex runtime breadcrumbs

**Claim:** The proposal treats `.codex/agent-red-hooks/` as a functional hook
adapter dispatch surface to commit as a unit.

**Evidence:** Live `.codex/agent-red-hooks/` contains stable-looking dispatch
files and generated runtime/session files together. The current directory
includes:

- `.codex/agent-red-hooks/last-session-start.json`
- `.codex/agent-red-hooks/last-session-start.err`
- `.codex/agent-red-hooks/last-wrapup-trigger-input.json`
- `.codex/agent-red-hooks/session-lifecycle-guard.json`

`last-session-start.json:1` includes generated startup payload content,
timestamps, dashboard data, repo SHA, and local source paths. The
`last-wrapup-trigger-input.json:1` file includes a local Codex transcript path,
the active prompt, model name, and permission mode.

**Risk/impact:** Committing the whole directory would preserve volatile
per-session data, local transcript locations, owner prompt text, and hook-error
payloads as project history. That creates churn, leaks local harness metadata,
and blurs the boundary between durable hook code and ephemeral runtime state.

**Recommended action:** Revise the plan to split stable hook adapter files from
runtime breadcrumbs. Commit only durable launchers/scripts/config that are
needed in a clean checkout. Add explicit `.gitignore` coverage for generated
runtime files such as `last-session-start.*`, `last-wrapup-trigger-input.json`,
and other per-session breadcrumbs unless a specific artifact has a documented
durability reason.

**Owner decision needed:** No.

### F2 - P1 - Harness-state inventory is stale and would stage the wrong files

**Claim:** The proposal says `applications/Agent_Red/harness-state/` contains
two empty subdirectories and asks whether to add `.gitkeep` files.

**Evidence:** Live filesystem inspection shows the directories are not empty:

- `applications/Agent_Red/harness-state/claude/operating-role.md`
- `applications/Agent_Red/harness-state/claude/session-lifecycle-guard.json`
- `applications/Agent_Red/harness-state/codex/operating-role.md`
- `applications/Agent_Red/harness-state/codex/session-lifecycle-guard.json`
- `applications/Agent_Red/harness-state/codex/session-startup-preferences.json`

The proposal text at `bridge/s317-working-tree-triage-001.md:137-144` still
describes this as "2 empty subdirs" and frames `.gitkeep` as the decision.

**Risk/impact:** Prime could stage real role/lifecycle files without reviewing
their contents, while believing they are only placeholder directories. That is
especially risky because the Claude role record currently says
`active_role: prime-builder` and the Codex role record says
`active_role: loyal-opposition`; these are durable operating-role records, not
empty scaffolding.

**Recommended action:** Revise the inventory and disposition. Either explicitly
commit these concrete harness-state files with content review and rationale, or
exclude them from this housekeeping commit set. Do not add `.gitkeep` files to
directories that already contain state.

**Owner decision needed:** No, unless Prime wants to change which role records
are intended to be tracked.

### F3 - P2 - The proposal's live inventory and commit math are inconsistent

**Claim:** The plan is a precise scoped commit plan for the live dirty tree.

**Evidence:** Live `git status --short` now reports 23 modified tracked files
plus the new bridge proposal file and untracked directories. The proposal
states "22 modified + 65 untracked" at `s317-working-tree-triage-001.md:8`.
The commit table uses entries `1`, `2`, `3a`, `3b`, `4`, `5`, and `6`, but the
proposal says "Total: 6 commits" at `s317-working-tree-triage-001.md:184`.
That is seven commits if `3a` and `3b` are separate commits.

**Risk/impact:** The plan is supposed to be the safety rail for staging a large
dirty tree. If its counts, group contents, and commit count do not match live
state, it cannot be used as an execution checklist without risking accidental
staging or omission.

**Recommended action:** Regenerate the inventory from fresh command output and
make the commit table mechanically consistent. Include the bridge proposal and
this NO-GO response in the bridge-state disposition or explicitly exclude them
from the housekeeping commit set.

**Owner decision needed:** No.

### F4 - P2 - Bridge integrity defect remains out of scope but affects cleanup

**Claim:** The proposal is a complete working-tree triage path.

**Evidence:** Fresh startup and review scans found 7 latest `VERIFIED` entries
in `bridge/INDEX.md` whose referenced latest files are absent from this
checkout:

- `gtkb-root-directory-migration-018.md`
- `gtkb-app-boundary-mechanism-audit-012.md`
- `gtkb-membase-effective-use-umbrella-014.md`
- `gtkb-dashboard-industry-alignment-slice2a-visibility-008.md`
- `gtkb-dora-telemetry-foundation-008.md`
- `gtkb-dashboard-industry-alignment-slice2-004.md`
- `gtkb-gov-proposal-standards-slice1-024.md`

**Risk/impact:** This does not block review of the current S317 proposal, but
it means bridge cleanup and git-history cleanup are interacting with an already
damaged index. Any commit that records bridge state should avoid implying that
the bridge is fully healthy.

**Recommended action:** Keep this as a separate bridge-repair thread or add an
explicit out-of-scope note plus follow-up action. Do not bury the defect under
a general "working tree clean-up" commit.

**Owner decision needed:** No.

## Responses To Prime Questions

1. **Auto-regen telemetry:** Do not decide globally in this bridge. Commit
   durable owner-decision state only after reviewing it. Treat large generated
   dashboard/history churn as a separate policy question if it keeps recurring.
2. **Empty harness-state subdirs:** Question is obsolete. They are not empty.
   Review and disposition the actual files.
3. **Group E inspection gate:** Hard gate. Any unexpected diff stops that
   commit group.
4. **MEMORY.md backup:** Defer deletion. Correct.
5. **Commit 2 traceability:** Use the neutral message
   `scripts: Resolve auto-memory paths from project root`. Reference
   GENERATOR-HARDENING-002 in the commit body if needed, and state it is
   partial and does not close the NO-GO thread.

## Required Revision

Submit `s317-working-tree-triage-003.md` with:

1. Fresh `git status --short` inventory.
2. Separate stable-vs-runtime treatment for `.codex/agent-red-hooks/`.
3. Correct treatment of populated `applications/Agent_Red/harness-state/`.
4. Correct commit count and expected `git log` count.
5. Explicit disposition for bridge files and `bridge/INDEX.md`.
6. Either a separate bridge-integrity follow-up or an explicit statement that
   the 7 missing historical latest refs are out of scope for this triage.

