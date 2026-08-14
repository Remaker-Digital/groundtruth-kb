# Session Bootstrap - GroundTruth-KB

Purpose: one short startup file that makes session behavior deterministic after
restart.

> **2026-06-15 bridge cutover note:** After WI-4510 Phase-3, TAFE-backed bridge
> state and status-bearing numbered bridge files are canonical.
>
> **2026-07-01 activity envelope sharding (WI-4949):** Base startup loads only
> `global_baseline` surfaces per `config/agent-control/activity-envelope-sharding.toml`.
> Loyal Opposition runbooks, standing priorities, checklists, and templates listed under
> `classes.activity_only.deferred_surfaces` and `migration.wi4949.activity_map`
> load only after `::open <activity>`. Harness skill adapters are generated
> from the canonical baseline skill sources and require no separate startup load.

## What To Expect On Restart

These changes take effect automatically when the active AI harness starts in
this workspace and reads `AGENTS.md`:

- The assigned operating role must be loaded before role-specific permissions or
  restrictions are applied.
- Fresh-session startup discovers the harness's durable ID from
  `harness-state/harness-identities.json`, then discovers the assigned
  operating role from `harness-state/harness-registry.json` through
  `groundtruth_kb.harness_projection.read_roles` or the `roles` subcommand
  under `gt harness`.
- A persisted harness ID is workstation-unique and must not change after it is
  set except through an explicit owner-requested identity change operation.
- The explicit identity change operation is
  `python scripts/harness_identity.py set --harness-name <name> --harness-id <id> --owner-requested`.
- Prime Builder work follows Prime Builder governance; Loyal Opposition review
  follows Loyal Opposition governance.
- Prime Builder / Loyal Opposition coordination uses the file bridge in
  `bridge/`.
- Both Prime Builder and Loyal Opposition startup procedures load
  `{{HARNESS_RULES_DIR}}/canonical-terminology.md` so the live glossary is available
  before ordinary role work. **Antigravity Startup Optimization**: The Antigravity harness (ID C) is exempt from loading the full rules/logs payload at startup (exempt from Phase B steps 9-18a) to minimize startup resource consumption. It loads only the essential project metadata and baseline rules (`CLAUDE.md`, `AGENTS.md`, `canonical-terminology.md`, `file-bridge-protocol.md`, `MEMORY.md`), skipping non-essential runbooks and non-local background startup checks.
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
- The bridge dispatcher and TAFE-backed bridge state must be checked at startup
  in both Prime Builder and Loyal Opposition roles.
- TAFE-backed bridge state is the authoritative source for bridge queue state;
  startup reports, dashboard fields, cached scan counts,
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
  disabled. Use the dispatcher daemon when its registrations and
  dispatch state are healthy; otherwise use manual scans or activate monitoring
  only when Prime Builder and Loyal Opposition are running in separate harnesses
  or asynchronous monitoring is otherwise needed.
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

These changes now activate automatically when `harness-state/harness-registry.json`,
read through the canonical role reader, assigns the current harness ID to Loyal
Opposition mode:

- non-mutating review-mode hook behavior

Optional local environment overrides remain available:

- force read-only behavior:
  - `LOYAL_OPPOSITION_READONLY=1`
  - `CODEX_REVIEW_MODE=1`
- temporarily allow builder-style hook behavior during an explicitly approved implementation session:
  - `LOYAL_OPPOSITION_READONLY=0`
  - `CODEX_REVIEW_MODE=0`

## Recommended Review-Session Startup

**Phase A - Bridge dispatcher verification (first priority):**
1. Read TAFE-backed bridge state and run dispatcher status/health when topology,
   target eligibility, or dispatch health is in question.
2. Treat TAFE/dispatcher bridge state as authoritative; do not use
   cached startup reports or generated bridge scan values to
   determine current state.
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
   oldest to newest using `{{HARNESS_RULES_DIR}}/file-bridge-protocol.md`.
8. In Prime Builder mode, do not process latest `NEW`, `REVISED`, or
   `VERIFIED` entries as actionable queue work. Prime Builder bridge handling is
   limited to latest `GO` or `NO-GO` entries.
9. Report scan count: "File bridge scan: N entries processed."

**Phase B — Local bootstrap (after bridge obligations are clear):**
8. Start the assigned AI harness in this workspace:
   `E:\GT-KB`
9. Review-mode hooks should auto-activate from `harness-state/harness-identities.json`
   plus canonical role state in `harness-state/harness-registry.json`.
   Only set an environment flag if you need to force or override the detected mode.
10. Confirm **global baseline** startup surfaces loaded (see
    `config/agent-control/activity-envelope-sharding.toml` § `classes.global_baseline`
    and `config/agent-control/SESSION-STARTUP-INDEX.md`):
   - `AGENTS.md`
   - `harness-state/harness-identities.json`
   - `harness-state/harness-registry.json`
   - `{{HARNESS_RULES_DIR}}/operating-role.md` guidance
   - `{{HARNESS_RULES_DIR}}/canonical-terminology.md` (core primer subset only)
   - `{{HARNESS_RULES_DIR}}/file-bridge-protocol.md`
   - `config/agent-control/SESSION-STARTUP-INDEX.md` + role overlay
11. **Do not** load activity-only Loyal Opposition surfaces at base startup. Open the matching
    activity envelope first (`::open build|test|project|deliberation|spec|ops`) and
    then load deferred surfaces from `migration.wi4949.activity_map` in
    `activity-envelope-sharding.toml`. Typical mappings:
    - `::open build` or `::open test` → `review-operating-contract.md`,
      `loyal-opposition-runbook.md`
    - `::open test` → also `review-checklists.md`, `template-code-review.md`
    - `::open project` → `standing-priorities.md`, `groundtruth-kb-vision.md`
    - `::open deliberation` → `way-of-working.md`
12. For substantial LO review work inside an opened activity envelope, use:
   - `{{HARNESS_RULES_DIR}}/review-checklists.md`
   - `{{HARNESS_RULES_DIR}}/template-code-review.md`
   - `{{HARNESS_RULES_DIR}}/template-decision-memo.md`
13. In Loyal Opposition mode, include the standard project-state startup
    report after bridge verification:
    - direct `git status --short --branch`
    - TAFE/dispatcher latest-status counts and latest `NEW`/`REVISED`
      actionability
    - Prime-actionable latest `GO`/`NO-GO` bridge responses for owner context
    - MemBase `current_work_items` status counts
    - every active MemBase `project_name` group with non-terminal count, status
      mix, and top current item
    - release blockers or release-target constraints when present

## Quick Restart Prompt

Use these as separate messages at the start of a new Prime Builder session if
needed. For a Loyal Opposition session, use `::init gtkb lo` for message 1.

Message 1:

```text
::init gtkb pb
```

Message 2:

```text
::open project
```

Message 3:

```text
Resolve this harness's persistent ID from
`harness-state/harness-identities.json`, then start in the GroundTruth-KB role
recorded for that harness ID in `harness-state/harness-registry.json`, read
through `groundtruth_kb.harness_projection.read_roles` or the `roles`
subcommand under `gt harness`.
Load AGENTS.md, the harness identity map, the role assignment map,
{{HARNESS_RULES_DIR}}/canonical-terminology.md (core primer subset),
{{HARNESS_RULES_DIR}}/file-bridge-protocol.md,
config/agent-control/SESSION-STARTUP-INDEX.md, and the active role overlay.
Defer activity-only Loyal Opposition surfaces (standing priorities, review contract,
loyal-opposition runbook, way-of-working, checklists) until `::open <activity>`
per config/agent-control/activity-envelope-sharding.toml migration.wi4949.
Surface the standing strategic self-improvement directive from
standing-priorities after opening the project activity envelope,
including that future-work candidates flow to MemBase rather than MEMORY.md,
that consideration backlog items are distinct from implementation-approved
backlog items, and that executing a consideration item requires owner
presentation plus AskUserQuestion approval before implementation proposal work.
Apply only the
permissions and restrictions for the assigned operating role. Use
TAFE-backed bridge state and dispatcher status/health for bridge work. Prime
Builder acts only on latest `GO` or `NO-GO` entries; Loyal Opposition processes
latest `NEW` or `REVISED` entries.
```

## Read-Only Review Mode Behavior

When Loyal Opposition review mode is active, the local hook behavior should:

- skip scheduler mutation
- skip assertion-run pruning
- read session handoff without consuming it

## Boundary

- The `{{HARNESS_CONFIG_DIR}}` skills and hook changes are local-only because `{{HARNESS_CONFIG_DIR}}` is git-ignored in this repo.
- The tracked baseline for intended setup lives in `config/agent-control/`.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
