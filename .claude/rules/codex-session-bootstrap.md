# Session Bootstrap - GroundTruth-KB

Purpose: one short startup file that makes session behavior deterministic after
restart.

## What To Expect On Restart

These changes take effect automatically when the active AI harness starts in
this workspace and reads `AGENTS.md`:

- The assigned operating role must be loaded before role-specific permissions or
  restrictions are applied.
- Fresh-session startup discovers the harness's durable ID from
  `harness-state/harness-identities.json`, then discovers the assigned
  operating role from `harness-state/role-assignments.json`.
- A persisted harness ID is workstation-unique and must not change after it is
  set except through an explicit owner-requested identity change operation.
- The explicit identity change operation is
  `python scripts/harness_identity.py set --harness-name <name> --harness-id <id> --owner-requested`.
- Prime Builder work follows Prime Builder governance; Loyal Opposition review
  follows Loyal Opposition governance.
- Prime Builder / Loyal Opposition coordination uses the file bridge in
  `bridge/`.
- Both Prime Builder and Loyal Opposition startup procedures load
  `.claude/rules/canonical-terminology.md` so the live glossary is available
  before ordinary role work.
- Both Prime Builder and Loyal Opposition startup disclosures surface the
  strategic self-improvement directive: noticed fix-worthy issues and useful
  workflow enhancements should be captured as standing backlog/work items for
  review and future consideration when they are not already tracked. Backlog
  capture flows to MemBase work items, not `MEMORY.md`, and is not
  implementation approval; implementation-approved backlog items require
  explicit owner/governance approval and AskUserQuestion evidence when owner
  approval is required. Executing a review/consideration backlog item means
  presenting information, options, and an explicit AUQ for owner approval to
  proceed with an implementation proposal.
- The GT-KB root boundary is mandatory: all active GT-KB artifacts must remain
  within `E:\GT-KB`; all GT-KB application files must remain within
  `E:\GT-KB\applications\`; Agent Red files must remain within
  `E:\GT-KB\applications\Agent_Red\`. There are no exceptions.
- The file bridge is always available through `bridge/INDEX.md` and must be
  checked at startup in both Prime Builder and Loyal Opposition roles.
- The live contents of `bridge/INDEX.md` are the sole authoritative source for
  bridge queue state. Startup reports, dashboard fields, cached scan counts,
  copied excerpts, summaries, and other derived artifacts are context only and
  must not determine current bridge state.
- Loyal Opposition has permanent owner authority to diagnose and repair correct
  bridge function and bridge use, including downstream bridge-dependent
  artifacts required to sustain bridge function and full utilization.
- When Prime Builder starts a fresh session, any latest `GO` or `NO-GO` bridge
  entry is included in the continuation scope for the prior session; those
  entries may be Loyal Opposition responses created in a separate previous
  session.
- The poller is separate from the bridge. The retired OS poller remains
  disabled, but the verified smart poller should be used when it is available
  and functioning. When smart-poller automation is unavailable, use manual scans
  or activate monitoring only when Prime Builder and Loyal Opposition are
  running in separate harnesses or asynchronous monitoring is otherwise needed.
- Prime Builder startup presents the GT-KB numbered session-focus choices to the
  owner. Loyal Opposition startup does not present those choices.
- The owner's first message in a fresh session is only a session-start stimulus,
  not informational input. Do not interpret it as a focus choice, task prompt,
  approval, answer, or owner decision; present startup first, then wait for the
  next owner message before choosing or mapping session work.
- Loyal Opposition fresh sessions start prepared to review and verify Prime
  Builder work; their first task is to verify that the bridge is functioning.
- If the bridge is not functioning, Loyal Opposition diagnoses and repairs it
  first, with owner pre-approval to make required file and configuration
  changes.
- Proposal review, code review, and alternatives investigation are the primary
  work modes when the active role is Loyal Opposition.
- The review contract, checklists, and templates are part of the expected
  startup context when the active role is Loyal Opposition.
- Loyal Opposition startup includes a compact current-state report for the
  owner: git state, live bridge queue, Prime-actionable bridge responses,
  MemBase `current_work_items` status counts, every active `project_name`
  group, and release blockers or release-target constraints.

These changes now activate automatically when `harness-state/role-assignments.json`
assigns the current harness ID to Loyal Opposition mode:

- non-mutating review-mode hook behavior

Optional local environment overrides remain available:

- force read-only behavior:
  - `LOYAL_OPPOSITION_READONLY=1`
  - `CODEX_REVIEW_MODE=1`
- temporarily allow builder-style hook behavior during an explicitly approved implementation session:
  - `LOYAL_OPPOSITION_READONLY=0`
  - `CODEX_REVIEW_MODE=0`

## Recommended Review-Session Startup

**Phase A - File bridge verification (first priority):**
1. Read `bridge/INDEX.md`.
2. Treat the live read as authoritative; do not use cached or generated bridge
   scan values to determine current state.
3. Verify the bridge is functioning before ordinary Prime Builder or Loyal
   Opposition work.
4. If the bridge is not functioning, diagnose and repair bridge files,
   configuration, or automation as needed; this repair authority is
   owner-pre-approved for bridge restoration.
5. In Loyal Opposition mode, identify document entries whose latest status is
   `NEW` or `REVISED`.
6. In Prime Builder mode, identify latest `GO` or `NO-GO` entries and include
   them in "Continue Last Session" scope.
7. In Loyal Opposition mode, process latest `NEW` or `REVISED` entries from
   oldest to newest using `.claude/rules/file-bridge-protocol.md`.
8. In Prime Builder mode, do not process latest `NEW`, `REVISED`, or
   `VERIFIED` entries as actionable queue work. Prime Builder bridge handling is
   limited to latest `GO` or `NO-GO` entries.
9. Report scan count: "File bridge scan: N entries processed."

**Phase B — Local bootstrap (after bridge obligations are clear):**
8. Start the assigned AI harness in this workspace:
   `E:\GT-KB`
9. Review-mode hooks should auto-activate from `harness-state/harness-identities.json`
   plus `harness-state/role-assignments.json`.
   Only set an environment flag if you need to force or override the detected mode.
10. Confirm the assigned AI harness loads:
   - `AGENTS.md`
   - `harness-state/harness-identities.json`
   - `harness-state/role-assignments.json`
   - `.claude/rules/operating-role.md` guidance
   - `.claude/rules/canonical-terminology.md`
   - `.claude/rules/codex-standing-priorities.md`
   - `.claude/rules/codex-way-of-working.md`
   - `.claude/rules/codex-review-operating-contract.md`
   - `.claude/rules/codex-loyal-opposition-runbook.md`
   - `.claude/rules/codex-knowledge-base-index.md`
11. For substantial work, use:
   - `.claude/rules/codex-review-checklists.md`
   - `.claude/rules/template-code-review.md`
   - `.claude/rules/template-decision-memo.md`
12. In Loyal Opposition mode, include the standard project-state startup
    report after bridge verification:
    - direct `git status --short --branch`
    - direct `bridge/INDEX.md` latest-status counts and latest `NEW`/`REVISED`
      actionability
    - Prime-actionable latest `GO`/`NO-GO` bridge responses for owner context
    - MemBase `current_work_items` status counts
    - every active MemBase `project_name` group with non-terminal count, status
      mix, and top current item
    - release blockers or release-target constraints when present

## Quick Restart Prompt

Use this at the start of a new session if needed:

```text
Resolve this harness's persistent ID from
`harness-state/harness-identities.json`, then start in the GroundTruth-KB role
recorded for that harness ID in `harness-state/role-assignments.json`.
Load AGENTS.md, the harness identity map, the role assignment map,
.claude/rules/canonical-terminology.md,
.claude/rules/codex-session-bootstrap.md,
.claude/rules/codex-standing-priorities.md,
.claude/rules/codex-way-of-working.md,
.claude/rules/codex-review-operating-contract.md,
.claude/rules/codex-loyal-opposition-runbook.md, and
.claude/rules/codex-knowledge-base-index.md. Surface the
standing strategic self-improvement directive from codex-standing-priorities,
including that future-work candidates flow to MemBase rather than MEMORY.md,
that consideration backlog items are distinct from implementation-approved
backlog items, and that executing a consideration item requires owner
presentation plus AskUserQuestion approval before implementation proposal work.
Apply only the
permissions and restrictions for the assigned operating role. Use
bridge/INDEX.md as the file bridge. Prime Builder acts only on latest `GO` or
`NO-GO` entries; Loyal Opposition processes latest `NEW` or `REVISED` entries.
```

## Read-Only Review Mode Behavior

When Loyal Opposition review mode is active, the local hook behavior should:

- skip scheduler mutation
- skip assertion-run pruning
- read session handoff without consuming it

## Boundary

- The `.claude/` skills and hook changes are local-only because `.claude/` is git-ignored in this repo.
- The tracked baseline for intended setup lives in `config/agent-control/`.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

