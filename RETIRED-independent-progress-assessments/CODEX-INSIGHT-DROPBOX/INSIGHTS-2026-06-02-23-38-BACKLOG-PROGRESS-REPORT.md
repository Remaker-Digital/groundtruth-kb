# Backlog Progress Report - Loyal Opposition Advisory

Prepared: 2026-06-02T23:38:57Z
Prepared by: Codex Loyal Opposition
Automation: Backlog Progress Report
Evidence packet: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/backlog-progress-report-20260602T233857Z.json`

## Claim

MemBase now contains a first-class project hierarchy, but the backlog is not yet operationally clean enough to treat the project priority order as the complete execution queue. The strongest current signal is that most non-terminal work items are not attached to active first-class project memberships, many project descriptions are still backfill-derived, and active projects frequently retain only terminal member work. The priority order is therefore useful for project context, but Prime Builder should not execute from it without a reconciliation pass.

## Evidence

- Authority: `.claude/rules/operating-model.md:17`, `:59`, `:67`, and `:69` define project, work item, and backlog semantics; `:37` and `:83` define MemBase as the authoritative store.
- Schema: `groundtruth-kb/src/groundtruth_kb/db.py:298`, `:335`, `:358`, `:374`, `:706`, and `:711` define current work items, projects, memberships, dependencies, and current-state views.
- CLI contract: `groundtruth-kb/src/groundtruth_kb/cli.py:1122` and `:1156` identify `backlog list` as the unified MemBase work-item surface; `:1457` identifies the `projects list` surface.
- Project lifecycle contract: `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:97`, `:100`, `:368`, and `:475` define project listing/showing, membership gating, and project-scoped verified work-item logic.
- Live data source: SQLite queries against `E:\GT-KB\groundtruth.db` at 2026-06-02T23:38:57Z.

## Scope And Method

- Ordered projects include all current MemBase `current_projects` rows. Non-terminal projects are listed first by rank, then terminal projects by rank and id.
- Work items under each project are active `current_project_work_item_memberships`, ordered by membership order, then work-item implementation order, priority, and id.
- Work-item realness was checked across all current work items, not only project members: title, content length, source/spec/test/deliberation/bridge signals, and broken references.
- Unprojected non-terminal work items are discrepancies because they are real backlog work but are outside active first-class project membership.

## Summary Metrics

| Metric | Count |
|---|---:|
| Current projects | 170 |
| Non-terminal projects | 134 |
| Terminal projects | 36 |
| Current work items | 3030 |
| Non-terminal work items | 975 |
| Active project memberships | 580 |
| Non-terminal work items outside active project membership | 712 |
| Non-terminal work items without compatibility project_name | 809 |
| Non-terminal work items failing realness checks | 823 |
| Active project dependencies | 1 |

### Work Item Status Counts

| Resolution status | Count |
|---|---:|
| resolved | 1854 |
| open | 973 |
| retired | 76 |
| wont_fix | 61 |
| verified | 57 |
| not_a_defect | 7 |
| deferred | 1 |
| new | 1 |

### Non-Terminal Priority Counts

| Priority | Count |
|---|---:|
| low | 710 |
| P3 | 98 |
| P2 | 91 |
| P1 | 34 |
| (none) | 32 |
| high | 7 |
| P0 | 2 |
| medium | 1 |

## Dependency And Precedence Check

- `PROJECT-GTKB-ROLE-ENHANCEMENT` depends_on `PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION`; blocking status: `blocked`. Rationale: DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE sequencing constraint: do NOT begin role-enhancement substantive work until GTKB-ISOLATION-017 Phase 9 productization is VERIFIED. Owner reframe via DELIB-S381-ROLE-ENHANCEMENT-ISOLATION-DEPENDENCY-REFRAME.

Impact: the dependency record makes `PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION` precedent over substantive `PROJECT-GTKB-ROLE-ENHANCEMENT` work.

## Findings

### Finding P1-001: Project membership does not cover most active backlog work

Observation: 975 current work items are non-terminal, but 712 of them are not attached to an active first-class project membership. 809 non-terminal work items also have no compatibility `project_name`.

Deficiency Rationale: The operating model says backlog includes projects and work items; if most active work is not project-membered, project priority cannot function as the execution queue. This increases owner and agent triage cost and hides dependency relationships.

Proposed Solution/Enhancement: Treat backlog reconciliation as the next high-impact cleanup lane. First attach P0/P1/P2 non-terminal unprojected work items to existing projects where obvious; only create new projects when no existing project matches. Use `gt projects add-item` one item at a time or a reviewed dry-run packet for bulk remediation.

Option Rationale: This preserves MemBase as the backlog authority and avoids creating another backlog list. Reconciliation gives immediate priority clarity before lower-impact description polishing.

### Finding P1-002: Many project records are still weakly described or backfill-shaped

Observation: 144 current project records lack explicit purpose/target-outcome descriptions or rely mainly on generated/backfill notes.

Deficiency Rationale: Project records are meant to group related known work. When the description is just a migrated compatibility label, the project is hard to validate for accuracy and agents cannot confidently decide whether a work item belongs there.

Proposed Solution/Enhancement: Update purpose and target outcome for the highest-ranked active projects first, starting with ranked projects that have open members or active authorizations. Do not mutate formal artifacts in this advisory session; file a follow-on cleanup proposal or perform owner-approved project updates later.

Option Rationale: Top-rank projects affect immediate execution. Filling purpose/outcome first gives better routing with minimal schema or process change.

### Finding P2-001: Work-item realness is uneven

Observation: 823 non-terminal work items fail at least one realness check. 797 lack a source/evidence signal, and 37 have weak or missing content by this report's conservative content threshold.

Deficiency Rationale: A work item with insufficient content or no source trace may still be real, but it is not independently actionable. It cannot reliably map to specifications, deliberations, bridge history, tests, or acceptance criteria.

Proposed Solution/Enhancement: Backfill only the high-priority active gaps first. For new work items, enforce minimum content plus one durable source signal at creation: source spec, deliberation id, owner directive, bridge thread, test id, or failure evidence.

Option Rationale: Selective backfill avoids spending large effort on low-priority or terminal noise while preventing new low-evidence work from accumulating.

### Finding P2-002: Active projects retain terminal-only active memberships

Observation: 55 non-terminal project records have active member work items, but every active member is terminal.

Deficiency Rationale: This blurs progress reporting. A project can look active in the priority queue while its current member work is already resolved, verified, retired, or otherwise terminal.

Proposed Solution/Enhancement: Run the project completion/retirement scanner on these projects and repair missing implements links or authorizations before auto-retiring. Where the project is a parent umbrella, keep it active only if it has active child projects or a clear next outcome.

Option Rationale: This uses the existing project lifecycle model instead of inventing a separate completion convention.

## Ordered Project Backlog

Legend: `realness=gap` means the work item failed one or more title/content/source/reference checks in the JSON evidence packet. Terminal projects are retained in this section after non-terminal projects for completeness.

### `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-BRIDGE-MECHANICS` - Bridge mechanics

- Status/rank: `active` / `0`
- Parent: `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=6, open=0, terminal=6, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 0 | `WI-3264` | P0 | backlogged | resolved | gap | Cross-harness trigger Windows rename race + liveness diagnostics (P1 incident response) |
| 1 | `WI-3257` | P0 | resolved | resolved | gap | Bridge revision filing skill: /bridge revise verb + helper for REVISED versions |
| 1 | `WI-3265` | P1 | resolved | wont_fix | gap | Cross-harness trigger fires unreliably in codex exec sessions (dispatch-state refresh lag) |
| 2 | `WI-3258` | P0 | resolved | resolved | gap | Bridge implementation-report filing skill: /bridge impl-report verb + helper |
| 4 | `WI-3260` | P1 | resolved | resolved | gap | Bridge convenience verbs: /bridge show-thread <slug> and /bridge scan |
|  | `WI-3319` | P2 | resolved | resolved | ok | Lazy-import chromadb in db.py to remove PreToolUse hook import latency |

### `PROJECT-GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` - GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT

- Status/rank: `active` / `0`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=2, open=0, terminal=2, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 0 | `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` | P0 | resolved | resolved | gap | GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT |
|  | `WI-1515` |  | resolved | retired | ok | P0: Rotate all credentials exposed in .claude/settings.local.json |

### `PROJECT-ANTIGRAVITY-INTEGRATION` - Antigravity Integration

- Status/rank: `active` / `1`
- purpose: Add Google Antigravity (Antigravity IDE + Gemini CLI) as a third AI coding harness and consolidate harness registration and role assignment into a deterministic gt harness CLI over a DB-backed registry. Per DELIB-2079...
- Members: active=16, open=1, terminal=15, inactive=0, child_projects=4, active_auths=1, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3337` | P1 | completed | verified | gap | harnesses table schema and append-only versioning |
|  | `WI-3338` | P1 | completed | verified | gap | Generated hot-path harness-registry projection and generator |
|  | `WI-3339` | P1 | completed | verified | gap | Four-state harness lifecycle FSM and transition validators |
|  | `WI-3340` | P1 | completed | verified | gap | gt harness CLI command group |
|  | `WI-3341` | P1 | completed | verified | ok | Role portability and single-prime-builder invariant enforcement |
|  | `WI-3342` | P1 | resolved | resolved | ok | Phased reader migration from JSON to projection |
|  | `WI-3343` | P1 | resolved | resolved | ok | Extend ADR-SINGLE-HARNESS-OPERATING-MODE-001 for the harness registry architecture |
|  | `WI-3344` | P1 | completed | verified | gap | Data-driven cross-harness dispatch from invocation_surfaces |
|  | `WI-3345` | P1 | completed | verified | ok | Research spike: Antigravity IDE hook/skill config format and hook events |
|  | `WI-3346` | P1 | completed | verified | gap | .antigravity/ harness integration directory |
|  | `WI-3347` | P1 | completed | verified | gap | LO-role-scoped Antigravity capability adapters and registry entries |
|  | `WI-3348` | P1 | completed | verified | gap | Register the Antigravity harness (identity C) |
|  | `WI-3349` | P1 | resolved | resolved | ok | End-to-end Gemini CLI headless LO-review dispatch verification |
|  | `WI-3359` | P1 | closed | wont_fix | ok | Bridge notifier strands Codex-to-Claude dispatch when an interactive Claude session is open |
|  | `WI-3362` | P3 | completed | verified | ok | Backfill related_bridge_threads linkage for Antigravity WIs WI-3337..WI-3349 |
|  | `WI-3383` | P3 | backlogged | open | ok | Record harness, model, and settings provenance on each bridge document |

### `PROJECT-GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION` - Slice 2.3 (integration)

- Status/rank: `active` / `3`
- Parent: `PROJECT-GTKB-DASHBOARD-002`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 3 | `GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION` |  | backlogged | open | ok | GTKB-DASHBOARD-002 Slice 2.3 (integration) |

### `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE` - Project lifecycle

- Status/rank: `active` / `3`
- Parent: `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=3, open=1, terminal=2, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 3 | `WI-3259` | P1 | resolved | resolved | gap | Projects skill + gt projects CLI group (8 verbs: create/show/list/update/add-item/reorder/retire/link-bridge) |
|  | `WI-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001` | high | resolved | resolved | ok | Implement project-scoped authorization and automatic spec backlog intake |
|  | `WI-3481` | P2 | backlogged | open | ok | project_verified_completion_scanner prematurely auto-retires incrementally-materialized multi-slice projects |

### `PROJECT-GTKB-DASHBOARD-002-SLICE-2-2-METRICS` - Slice 2.2 (metrics)

- Status/rank: `active` / `4`
- Parent: `PROJECT-GTKB-DASHBOARD-002`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 4 | `GTKB-DASHBOARD-002-SLICE-2-2-METRICS` |  | backlogged | open | ok | GTKB-DASHBOARD-002 Slice 2.2 (metrics) |

### `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-VERIFICATION-MECHANICS` - Verification mechanics

- Status/rank: `active` / `5`
- Parent: `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 5 | `WI-3261` | P2 | backlogged | open | ok | Verification mechanics: /verify verdict-author skill + spec-to-test mapping helper |

### `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` - GTKB-GOV-PROPOSAL-STANDARDS

- Status/rank: `active` / `5`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=4, open=2, terminal=2, inactive=0, child_projects=4, active_auths=2, active_links=0
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 5 | `GTKB-GOV-PROPOSAL-STANDARDS` |  | resolved | resolved | gap | GTKB-GOV-PROPOSAL-STANDARDS Slice 1 |
| 1020 | `GTKB-GOV-PROPOSAL-STANDARDS-SLICE2` |  | backlogged | open | gap | Test-claim re-run verifier |
| 1021 | `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3` |  | resolved | verified | gap | Work-item-ID collision gate |
| 1022 | `GTKB-GOV-PROPOSAL-STANDARDS-SLICE4` |  | backlogged | open | gap | /gtkb-propose scaffolding skill |

### `PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION` - Phase 9 productization

- Status/rank: `active` / `5`
- Parent: `PROJECT-GTKB-ISOLATION`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1024 | `GTKB-ISOLATION-017` |  | backlogged | open | ok | Implement downstream adopter packaging and clean-adopter validation |

### `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DISCOVERABILITY` - Discoverability

- Status/rank: `active` / `6`
- Parent: `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=2, open=0, terminal=2, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 6 | `WI-3262` | P2 | resolved | resolved | ok | Discoverability: gt project doctor --json, gt backlog show <id>, ad-hoc-Python-smell triage |
|  | `WI-4220` | P2 | resolved | resolved | ok | Add subset filters to gt projects list and gt backlog list |

### `PROJECT-GTKB-GOV-DA-ENFORCEMENT` - GTKB-GOV-DA-ENFORCEMENT

- Status/rank: `active` / `6`
- scope: DA enforcement decomposed into five child work items: assertions, prior-deliberations hook, retroactive harvest, SPEC-DA promotion, and terminal project retirement.
- Members: active=5, open=0, terminal=5, inactive=1, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-4242` | P2 | resolved | resolved | ok | Add GOV-18 machine-verifiable assertions to the seven SPEC-DA specs |
| 2 | `WI-4243` | P2 | resolved | resolved | ok | Implement prior-deliberations citation pre-commit hook |
| 3 | `WI-4244` | P2 | resolved | resolved | ok | Re-execute retroactive DA harvest sweep against in-root MemBase |
| 4 | `WI-4245` | P2 | resolved | resolved | ok | Promote the seven SPEC-DA specs after assertions and harvest pass |
| 5 | `WI-4246` | P3 | resolved | resolved | ok | Retire PROJECT-GTKB-GOV-DA-ENFORCEMENT after child slices complete |

### `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` - GTKB-DETERMINISTIC-SERVICES-001

- Status/rank: `active` / `7`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=23, open=6, terminal=17, inactive=0, child_projects=5, active_auths=7, active_links=0
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 0 | `WI-3264` | P0 | backlogged | resolved | gap | Cross-harness trigger Windows rename race + liveness diagnostics (P1 incident response) |
| 1 | `WI-3257` | P0 | resolved | resolved | gap | Bridge revision filing skill: /bridge revise verb + helper for REVISED versions |
| 1 | `WI-3265` | P1 | resolved | wont_fix | gap | Cross-harness trigger fires unreliably in codex exec sessions (dispatch-state refresh lag) |
| 2 | `WI-3258` | P0 | resolved | resolved | gap | Bridge implementation-report filing skill: /bridge impl-report verb + helper |
| 3 | `WI-3259` | P1 | resolved | resolved | gap | Projects skill + gt projects CLI group (8 verbs: create/show/list/update/add-item/reorder/retire/link-bridge) |
| 4 | `WI-3260` | P1 | resolved | resolved | gap | Bridge convenience verbs: /bridge show-thread <slug> and /bridge scan |
| 5 | `WI-3261` | P2 | backlogged | open | ok | Verification mechanics: /verify verdict-author skill + spec-to-test mapping helper |
| 6 | `WI-3262` | P2 | resolved | resolved | ok | Discoverability: gt project doctor --json, gt backlog show <id>, ad-hoc-Python-smell triage |
| 7 | `WI-3263` | P1 | resolved | resolved | ok | Advance GTKB-ARTIFACT-RECORDER-CLI: file the scoping bridge proposal per its Next step field |
|  | `WI-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001` | high | resolved | resolved | ok | Implement project-scoped authorization and automatic spec backlog intake |
|  | `WI-3318` | P1 | resolved | resolved | ok | Implement `gt bridge propose --kind <type>` deterministic CLI for bridge-proposal scaffolding |
|  | `WI-3424` | P1 | backlogged | open | ok | Deterministic CLI: gt validate spec-coherence (detect cross-spec contradictions via surface-overlap, authority-hierar... |
|  | `WI-3319` | P2 | resolved | resolved | ok | Lazy-import chromadb in db.py to remove PreToolUse hook import latency |
|  | `WI-4220` | P2 | resolved | resolved | ok | Add subset filters to gt projects list and gt backlog list |
|  | `WI-4249` | P2 | backlogged | open | ok | Expand hygiene sweep patterns for wrap-scan recursion and runtime residue |
|  | `WI-4250` | P2 | backlogged | open | ok | Harden hygiene workflow command portability and UTF-8 output regression coverage |
|  | `WI-4259` | P2 | backlogged | open | ok | Wrap-scan scanner-owned artifact severity adjustment |
|  | `WI-3420` | P3 | resolved | resolved | ok | Deterministic CLI: gt hygiene sweep (enumerate config-drift instances against pattern set; JSON inventory + markdown... |
|  | `WI-3421` | P3 | resolved | resolved | ok | Skill: gtkb-hygiene-sweep (orchestrate gt hygiene sweep CLI; classify findings; guide remediation child-WI filing) |
|  | `WI-3429` | P3 | backlogged | open | ok | Add gt bridge revise CLI to automate REVISED filing boilerplate (deterministic-services slice) |
|  | `WI-3436` | P3 | resolved | resolved | ok | First-class `gt backlog update` CLI for post-creation WI field updates (esp. related_bridge_threads) |
|  | `WI-4216` | P3 | resolved | resolved | ok | Deterministic service: gt backlog reconcile plan --project <id> - current-row snapshot + proposed reconciliation rows... |
|  | `WI-4223` | P3 | resolved | resolved | ok | Bridge-VERIFIED auto-retire reconciler misses umbrella WIs whose related_bridge_threads cites only one child thread |

### `PROJECT-GTKB-GOV-OWNER-DECISION-SURFACING` - GTKB-GOV-OWNER-DECISION-SURFACING

- Status/rank: `active` / `8`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 8 | `GTKB-GOV-OWNER-DECISION-SURFACING` |  | resolved | verified | gap | GTKB-GOV-OWNER-DECISION-SURFACING |

### `PROJECT-GTKB-WRAPUP-ENHANCEMENTS` - GTKB-WRAPUP-ENHANCEMENTS

- Status/rank: `active` / `10`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 10 | `GTKB-WRAPUP-ENHANCEMENTS` |  | backlogged | open | gap | GTKB-WRAPUP-ENHANCEMENTS |

### `PROJECT-GTKB-ROLE-ENHANCEMENT` - GTKB-ROLE-ENHANCEMENT

- Status/rank: `active` / `11`
- scope: Parked pending PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION VERIFIED per DELIB-S381. Substantive 9-gap / 5-clause formalization per DELIB-S310-ROLE-DEFINITION-ASSESSMENT remains deferred per DELIB-S312-ROLE-CONTRACT-...
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 11 | `GTKB-ROLE-ENHANCEMENT` |  | backlogged | open | gap | GTKB-ROLE-ENHANCEMENT |

### `PROJECT-GTKB-COMMAND-SURFACE` - GTKB-COMMAND-SURFACE

- Status/rank: `active` / `12`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 12 | `GTKB-COMMAND-SURFACE` |  | backlogged | open | ok | GTKB-COMMAND-SURFACE |

### `PROJECT-GTKB-DB-BACKUP-001` - GTKB-DB-BACKUP-001

- Status/rank: `active` / `13`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 13 | `GTKB-DB-BACKUP-001` |  | resolved | resolved | ok | GTKB-DB-BACKUP-001 |

### `PROJECT-GTKB-BRIDGE-POLLER-001` - GTKB-BRIDGE-POLLER-001

- Status/rank: `active` / `14`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 14 | `GTKB-BRIDGE-POLLER-001` |  | backlogged | retired | ok | GTKB-BRIDGE-POLLER-001 |

### `PROJECT-GENERATOR-HARDENING-001` - GENERATOR-HARDENING-001

- Status/rank: `active` / `16`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 16 | `GENERATOR-HARDENING-001` |  | resolved | verified | ok | GENERATOR-HARDENING-001 |

### `PROJECT-GENERATOR-HARDENING-002` - GENERATOR-HARDENING-002

- Status/rank: `active` / `17`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 17 | `GENERATOR-HARDENING-002` |  | resolved | verified | ok | GENERATOR-HARDENING-002 |

### `PROJECT-GENERATOR-HARDENING-CROSS-REPO` - GENERATOR-HARDENING-CROSS-REPO

- Status/rank: `active` / `18`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 18 | `GENERATOR-HARDENING-CROSS-REPO` |  | resolved | verified | ok | GENERATOR-HARDENING-CROSS-REPO |

### `PROJECT-GTKB-COMMIT-TRIAGE-001` - GTKB-COMMIT-TRIAGE-001

- Status/rank: `active` / `20`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 20 | `GTKB-COMMIT-TRIAGE-001` | high | resolved | resolved | ok | Triage uncommitted file drift into bridge-thread-scoped commits |

### `PROJECT-GTKB-CANDIDATE-SPEC-INTAKE-FOLLOW-ONS` - GTKB-CANDIDATE-SPEC-INTAKE-FOLLOW-ONS

- Status/rank: `active` / `21`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 21 | `GTKB-CANDIDATE-SPEC-INTAKE-FOLLOW-ONS` |  | resolved | verified | gap | GTKB-CANDIDATE-SPEC-INTAKE-FOLLOW-ONS |

### `PROJECT-GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` - GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT

- Status/rank: `active` / `22`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 22 | `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` |  | backlogged | retired | gap | GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT |

### `PROJECT-GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR` - GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR

- Status/rank: `active` / `23`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 23 | `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR` |  | backlogged | retired | ok | GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR |

### `PROJECT-GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` - GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY

- Status/rank: `active` / `24`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 24 | `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` |  | resolved | resolved | ok | Migrate direct bridge INDEX writers to gtkb_bridge_writer.py |

### `PROJECT-GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC` - GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC

- Status/rank: `active` / `25`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 25 | `GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC` |  | backlogged | open | gap | GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC |

### `PROJECT-GTKB-ISOLATION-017-SLICE-2-5` - GTKB-ISOLATION-017-SLICE-2.5

- Status/rank: `active` / `26`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 26 | `GTKB-ISOLATION-017-SLICE-2.5` |  | backlogged | open | ok | GTKB-ISOLATION-017-SLICE-2.5 (registry rationale schema extension) |

### `PROJECT-GTKB-ISOLATION-017-SLICE-2-5-REGISTRY-RATIONALE-SCHEMA-EXTENSION` - (registry rationale schema extension)

- Status/rank: `active` / `26`
- Parent: `PROJECT-GTKB-ISOLATION-017-SLICE-2-5`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 26 | `GTKB-ISOLATION-017-SLICE-2.5` |  | backlogged | open | ok | GTKB-ISOLATION-017-SLICE-2.5 (registry rationale schema extension) |

### `PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` - GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH

- Status/rank: `active` / `27`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=7, open=1, terminal=6, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 27 | `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH` |  | resolved | resolved | gap | GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH |
|  | `WI-3282` | P1 | resolved | resolved | ok | Reconcile MemBase work_items.priority field to single canonical vocabulary |
|  | `WI-3285` | P1 | resolved | resolved | ok | Require explicit project assignment or loose=true at work_item creation; triage 13+ orphans |
|  | `WI-3490` | P1 | backlogged | open | ok | Slice 7-prime: Physical retirement of memory/work_list.md (migration-completion gate) |
|  | `WI-3284` | P2 | resolved | resolved | ok | Document and enforce the (resolution_status, stage) legal matrix in work_items |
|  | `WI-3292` | P2 | resolved | resolved | ok | Doctor check for stale-active projects; kept_open_reason field; session-wrap retirement prompt |
|  | `WI-3293` | P2 | resolved | resolved | ok | Reject work_item-id / project-name collisions at write; triage 23 existing collisions |

### `PROJECT-GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL` - GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL

- Status/rank: `active` / `28`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 28 | `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL` |  | resolved | resolved | gap | GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL |

### `PROJECT-GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING` - GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING

- Status/rank: `active` / `29`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 29 | `GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING` |  | resolved | verified | gap | GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING |

### `PROJECT-GTKB-STARTUP-REFRACTOR-001` - GTKB-STARTUP-REFRACTOR-001

- Status/rank: `active` / `30`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 30 | `GTKB-STARTUP-REFRACTOR-001` | P1 | backlogged | open | gap | GTKB-STARTUP-REFRACTOR-001 (Consolidate role startup and glossary loading) |

### `PROJECT-GTKB-STARTUP-REFRACTOR-001-CONSOLIDATE-ROLE-STARTUP-AND-GLOSSARY-LOADING` - (Consolidate role startup and glossary loading)

- Status/rank: `active` / `30`
- Parent: `PROJECT-GTKB-STARTUP-REFRACTOR-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 30 | `GTKB-STARTUP-REFRACTOR-001` | P1 | backlogged | open | gap | GTKB-STARTUP-REFRACTOR-001 (Consolidate role startup and glossary loading) |

### `PROJECT-GTKB-ISOLATION-017-SLICE-5-5` - GTKB-ISOLATION-017-SLICE-5.5

- Status/rank: `active` / `31`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 31 | `GTKB-ISOLATION-017-SLICE-5.5` |  | resolved | resolved | ok | GTKB-ISOLATION-017-SLICE-5.5 (overlay refresh + disposability + chroma-regen API) |

### `PROJECT-GTKB-ISOLATION-017-SLICE-5-5-OVERLAY-REFRESH-DISPOSABILITY-CHROMA-REGEN-API` - (overlay refresh + disposability + chroma-regen API)

- Status/rank: `active` / `31`
- Parent: `PROJECT-GTKB-ISOLATION-017-SLICE-5-5`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 31 | `GTKB-ISOLATION-017-SLICE-5.5` |  | resolved | resolved | ok | GTKB-ISOLATION-017-SLICE-5.5 (overlay refresh + disposability + chroma-regen API) |

### `PROJECT-GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL` - GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL

- Status/rank: `active` / `32`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 32 | `GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL` |  | backlogged | open | ok | GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL |

### `PROJECT-GTKB-ENV-INVENTORY-001` - GTKB-ENV-INVENTORY-001

- Status/rank: `active` / `33`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 33 | `GTKB-ENV-INVENTORY-001` |  | resolved | resolved | ok | GTKB-ENV-INVENTORY-001 (Harness and development environment inventory) |

### `PROJECT-GTKB-ENV-INVENTORY-001-HARNESS-AND-DEVELOPMENT-ENVIRONMENT-INVENTORY` - (Harness and development environment inventory)

- Status/rank: `active` / `33`
- Parent: `PROJECT-GTKB-ENV-INVENTORY-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 33 | `GTKB-ENV-INVENTORY-001` |  | resolved | resolved | ok | GTKB-ENV-INVENTORY-001 (Harness and development environment inventory) |

### `PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001` - GTKB-SYSTEMS-TERMINOLOGY-MAP-001

- Status/rank: `active` / `34`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 34 | `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` |  | resolved | resolved | gap | GTKB-SYSTEMS-TERMINOLOGY-MAP-001 (Canonical artifact/interface names and startup operating surface map) |

### `PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001-CANONICAL-ARTIFACT-INTERFACE-NAMES-AND-STARTUP-OPERATING-SURFACE-MAP` - (Canonical artifact/interface names and startup operating surface map)

- Status/rank: `active` / `34`
- Parent: `PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 34 | `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` |  | resolved | resolved | gap | GTKB-SYSTEMS-TERMINOLOGY-MAP-001 (Canonical artifact/interface names and startup operating surface map) |

### `PROJECT-AGENT-RED-RUFF-CLEANUP-001` - AGENT-RED-RUFF-CLEANUP-001

- Status/rank: `active` / `35`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 35 | `AGENT-RED-RUFF-CLEANUP-001` |  | resolved | resolved | ok | AGENT-RED-RUFF-CLEANUP-001 (Application-side ruff resolution; Agent Red product code) |

### `PROJECT-AGENT-RED-RUFF-CLEANUP-001-APPLICATION-SIDE-RUFF-RESOLUTION-AGENT-RED-PRODUCT-CODE` - (Application-side ruff resolution; Agent Red product code)

- Status/rank: `active` / `35`
- Parent: `PROJECT-AGENT-RED-RUFF-CLEANUP-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 35 | `AGENT-RED-RUFF-CLEANUP-001` |  | resolved | resolved | ok | AGENT-RED-RUFF-CLEANUP-001 (Application-side ruff resolution; Agent Red product code) |

### `PROJECT-GTKB-PIP-INSTALL-ADOPTER-UX-001` - GTKB-PIP-INSTALL-ADOPTER-UX-001

- Status/rank: `active` / `36`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 36 | `GTKB-PIP-INSTALL-ADOPTER-UX-001` |  | resolved | resolved | ok | GTKB-PIP-INSTALL-ADOPTER-UX-001 (Simplify `gt project init` UX for pip-installed wheels) |

### `PROJECT-GTKB-PIP-INSTALL-ADOPTER-UX-001-SIMPLIFY-GT-PROJECT-INIT-UX-FOR-PIP-INSTALLED-WHEELS` - (Simplify `gt project init` UX for pip-installed wheels)

- Status/rank: `active` / `36`
- Parent: `PROJECT-GTKB-PIP-INSTALL-ADOPTER-UX-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 36 | `GTKB-PIP-INSTALL-ADOPTER-UX-001` |  | resolved | resolved | ok | GTKB-PIP-INSTALL-ADOPTER-UX-001 (Simplify `gt project init` UX for pip-installed wheels) |

### `PROJECT-GTKB-CI-COVERAGE-FOR-PLATFORM-001` - GTKB-CI-COVERAGE-FOR-PLATFORM-001

- Status/rank: `active` / `37`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 37 | `GTKB-CI-COVERAGE-FOR-PLATFORM-001` |  | resolved | resolved | gap | GTKB-CI-COVERAGE-FOR-PLATFORM-001 (Add CI coverage for `groundtruth-kb/tests/`) |

### `PROJECT-GTKB-CI-COVERAGE-FOR-PLATFORM-001-ADD-CI-COVERAGE-FOR-GROUNDTRUTH-KB-TESTS` - (Add CI coverage for `groundtruth-kb/tests/`)

- Status/rank: `active` / `37`
- Parent: `PROJECT-GTKB-CI-COVERAGE-FOR-PLATFORM-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 37 | `GTKB-CI-COVERAGE-FOR-PLATFORM-001` |  | resolved | resolved | gap | GTKB-CI-COVERAGE-FOR-PLATFORM-001 (Add CI coverage for `groundtruth-kb/tests/`) |

### `PROJECT-GTKB-EVALUATION-MODULE-RESTORATION-001` - GTKB-EVALUATION-MODULE-RESTORATION-001

- Status/rank: `active` / `38`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 38 | `GTKB-EVALUATION-MODULE-RESTORATION-001` |  | resolved | resolved | gap | GTKB-EVALUATION-MODULE-RESTORATION-001 (Restore or refactor evaluation/ module references) |

### `PROJECT-GTKB-EVALUATION-MODULE-RESTORATION-001-RESTORE-OR-REFACTOR-EVALUATION-MODULE-REFERENCES` - (Restore or refactor evaluation/ module references)

- Status/rank: `active` / `38`
- Parent: `PROJECT-GTKB-EVALUATION-MODULE-RESTORATION-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 38 | `GTKB-EVALUATION-MODULE-RESTORATION-001` |  | resolved | resolved | gap | GTKB-EVALUATION-MODULE-RESTORATION-001 (Restore or refactor evaluation/ module references) |

### `PROJECT-GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` - GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001

- Status/rank: `active` / `39`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 39 | `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` |  | resolved | resolved | ok | GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001 (External resource identity registry and confusion audit) |

### `PROJECT-GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001-EXTERNAL-RESOURCE-IDENTITY-REGISTRY-AND-CONFUSION-AUDIT` - (External resource identity registry and confusion audit)

- Status/rank: `active` / `39`
- Parent: `PROJECT-GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 39 | `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` |  | resolved | resolved | ok | GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001 (External resource identity registry and confusion audit) |

### `PROJECT-GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001` - GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001

- Status/rank: `active` / `40`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 40 | `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001` |  | backlogged | open | gap | GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001 (Anchor-only in-source citation conventions + orphan-citation doctor invariant) |

### `PROJECT-GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001-ANCHOR-ONLY-IN-SOURCE-CITATION-CONVENTIONS-ORPHAN-CITATION-DOCTOR-INVARIANT` - (Anchor-only in-source citation conventions + orphan-citation doctor invariant)

- Status/rank: `active` / `40`
- Parent: `PROJECT-GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 40 | `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001` |  | backlogged | open | gap | GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001 (Anchor-only in-source citation conventions + orphan-citation doctor invariant) |

### `PROJECT-GTKB-OPS-CURRENT-STATE-MONITORING-001` - GTKB-OPS-CURRENT-STATE-MONITORING-001

- Status/rank: `active` / `41`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 41 | `GTKB-OPS-CURRENT-STATE-MONITORING-001` |  | resolved | resolved | ok | GTKB-OPS-CURRENT-STATE-MONITORING-001 (Deterministic `gt status` / dashboard / startup operating-state reporting) |

### `PROJECT-GTKB-OPS-CURRENT-STATE-MONITORING-001-DETERMINISTIC-GT-STATUS-DASHBOARD-STARTUP-OPERATING-STATE-REPORTING` - (Deterministic `gt status` / dashboard / startup operating-state reporting)

- Status/rank: `active` / `41`
- Parent: `PROJECT-GTKB-OPS-CURRENT-STATE-MONITORING-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 41 | `GTKB-OPS-CURRENT-STATE-MONITORING-001` |  | resolved | resolved | ok | GTKB-OPS-CURRENT-STATE-MONITORING-001 (Deterministic `gt status` / dashboard / startup operating-state reporting) |

### `PROJECT-GTKB-AUQ-POLICY-GATES-001` - GTKB-AUQ-POLICY-GATES-001

- Status/rank: `active` / `42`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 42 | `GTKB-AUQ-POLICY-GATES-001` |  | resolved | resolved | ok | GTKB-AUQ-POLICY-GATES-001 (Central deterministic AUQ policy gate with thin hook/CLI/dashboard adapters) |

### `PROJECT-GTKB-AUQ-POLICY-GATES-001-CENTRAL-DETERMINISTIC-AUQ-POLICY-GATE-WITH-THIN-HOOK-CLI-DASHBOARD-ADAPTERS` - (Central deterministic AUQ policy gate with thin hook/CLI/dashboard adapters)

- Status/rank: `active` / `42`
- Parent: `PROJECT-GTKB-AUQ-POLICY-GATES-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 42 | `GTKB-AUQ-POLICY-GATES-001` |  | resolved | resolved | ok | GTKB-AUQ-POLICY-GATES-001 (Central deterministic AUQ policy gate with thin hook/CLI/dashboard adapters) |

### `PROJECT-GTKB-ENV-INVENTORY-DRIFT-CONTROL-001` - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001

- Status/rank: `active` / `43`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=2, open=1, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 43 | `GTKB-ENV-INVENTORY-DRIFT-CONTROL-001` |  | resolved | resolved | ok | GTKB-ENV-INVENTORY-DRIFT-CONTROL-001 (Inventory baseline drift control for protected artifacts) |
|  | `WI-3452` | P2 | backlogged | open | ok | Harden inventory drift gate against non-version toolchain field drift (broken-tool environments) |

### `PROJECT-GTKB-ENV-INVENTORY-DRIFT-CONTROL-001-INVENTORY-BASELINE-DRIFT-CONTROL-FOR-PROTECTED-ARTIFACTS` - (Inventory baseline drift control for protected artifacts)

- Status/rank: `active` / `43`
- Parent: `PROJECT-GTKB-ENV-INVENTORY-DRIFT-CONTROL-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 43 | `GTKB-ENV-INVENTORY-DRIFT-CONTROL-001` |  | resolved | resolved | ok | GTKB-ENV-INVENTORY-DRIFT-CONTROL-001 (Inventory baseline drift control for protected artifacts) |

### `PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` - GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001

- Status/rank: `active` / `44`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 44 | `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` |  | backlogged | open | gap | GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001 (Apply ADR/DCL logic as clause-level review tests) |

### `PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001-APPLY-ADR-DCL-LOGIC-AS-CLAUSE-LEVEL-REVIEW-TESTS` - (Apply ADR/DCL logic as clause-level review tests)

- Status/rank: `active` / `44`
- Parent: `PROJECT-GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 44 | `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` |  | backlogged | open | gap | GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001 (Apply ADR/DCL logic as clause-level review tests) |

### `PROJECT-GTKB-ISOLATION-PHASE-7-SLICE-2` - Phase 7 Slice 2

- Status/rank: `active` / `1000`
- Parent: `PROJECT-GTKB-ISOLATION`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1000 | `GTKB-ISOLATION-015` |  | backlogged | open | ok | Complete full Phase 7 work-subject/root enforcement (Slice 1 VERIFIED; Slice 2 remaining) |

### `PROJECT-GTKB-DASHBOARD-002` - GTKB-DASHBOARD-002

- Status/rank: `active` / `1006`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=3, open=2, terminal=1, inactive=0, child_projects=3, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 3 | `GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION` |  | backlogged | open | ok | GTKB-DASHBOARD-002 Slice 2.3 (integration) |
| 4 | `GTKB-DASHBOARD-002-SLICE-2-2-METRICS` |  | backlogged | open | ok | GTKB-DASHBOARD-002 Slice 2.2 (metrics) |
| 1006 | `GTKB-DASHBOARD-002` |  | resolved | retired | ok | Dashboard industry-alignment Slice 2 (scoped into 2.1 / 2.2 / 2.3) |

### `PROJECT-GTKB-DASHBOARD-002-SLICE-2` - Slice 2

- Status/rank: `active` / `1006`
- Parent: `PROJECT-GTKB-DASHBOARD-002`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1006 | `GTKB-DASHBOARD-002` |  | resolved | retired | ok | Dashboard industry-alignment Slice 2 (scoped into 2.1 / 2.2 / 2.3) |

### `PROJECT-GTKB-DASHBOARD-SLICE-3` - Slice 3

- Status/rank: `active` / `1007`
- Parent: `PROJECT-GTKB-DASHBOARD`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1007 | `GTKB-DASHBOARD-003` |  | backlogged | open | ok | Dashboard industry-alignment Slice 3 (SLO, flow metrics, PR health, incident/MTTR, remote exposure, WCAG) |

### `PROJECT-GTKB-DORA-001` - GTKB-DORA-001

- Status/rank: `active` / `1008`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1008 | `GTKB-DORA-001` |  | resolved | verified | ok | DORA telemetry foundation (deployable_change + rollback/hotfix linkage + incidents table) |

### `PROJECT-GTKB-DORA` - GTKB-DORA

- Status/rank: `active` / `1009`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1009 | `GTKB-DORA-002` |  | backlogged | open | ok | DORA four-keys panels (consumer of GTKB-DORA-001) |

### `PROJECT-GTKB-DORA-FOUR-KEYS-PANELS` - Four-keys panels

- Status/rank: `active` / `1009`
- Parent: `PROJECT-GTKB-DORA`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1009 | `GTKB-DORA-002` |  | backlogged | open | ok | DORA four-keys panels (consumer of GTKB-DORA-001) |

### `PROJECT-GTKB-DASHBOARD` - GTKB-DASHBOARD

- Status/rank: `active` / `1010`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=2, open=2, terminal=0, inactive=0, child_projects=2, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1007 | `GTKB-DASHBOARD-003` |  | backlogged | open | ok | Dashboard industry-alignment Slice 3 (SLO, flow metrics, PR health, incident/MTTR, remote exposure, WCAG) |
| 1010 | `GTKB-DASHBOARD-RETENTION` |  | backlogged | deferred | ok | Dashboard history retention policy (contingent) |

### `PROJECT-GTKB-DASHBOARD-RETENTION-POLICY` - Retention policy

- Status/rank: `active` / `1010`
- Parent: `PROJECT-GTKB-DASHBOARD`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1010 | `GTKB-DASHBOARD-RETENTION` |  | backlogged | deferred | ok | Dashboard history retention policy (contingent) |

### `PROJECT-GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` - GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1

- Status/rank: `active` / `1017`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1017 | `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE1` |  | resolved | retired | gap | Backlog schema linter + bridge→backlog citation gate (upstream-routed) |

### `PROJECT-GTKB-GOV-BACKLOG-DISCIPLINE-SLICE2` - GTKB-GOV-BACKLOG-DISCIPLINE-SLICE2

- Status/rank: `active` / `1018`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1018 | `GTKB-GOV-BACKLOG-DISCIPLINE-SLICE2` |  | resolved | retired | gap | Backlog state automation + ordering-freshness enforcement (upstream-routed) |

### `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-2` - Slice 2

- Status/rank: `active` / `1020`
- Parent: `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1020 | `GTKB-GOV-PROPOSAL-STANDARDS-SLICE2` |  | backlogged | open | gap | Test-claim re-run verifier |

### `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-3` - Slice 3

- Status/rank: `active` / `1021`
- Parent: `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1021 | `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3` |  | resolved | verified | gap | Work-item-ID collision gate |

### `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-4` - Slice 4

- Status/rank: `active` / `1022`
- Parent: `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1022 | `GTKB-GOV-PROPOSAL-STANDARDS-SLICE4` |  | backlogged | open | gap | /gtkb-propose scaffolding skill |

### `PROJECT-GTKB-ISOLATION` - GTKB-ISOLATION

- Status/rank: `active` / `1025`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=6, open=4, terminal=2, inactive=0, child_projects=4, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1000 | `GTKB-ISOLATION-015` |  | backlogged | open | ok | Complete full Phase 7 work-subject/root enforcement (Slice 1 VERIFIED; Slice 2 remaining) |
| 1024 | `GTKB-ISOLATION-017` |  | backlogged | open | ok | Implement downstream adopter packaging and clean-adopter validation |
| 1025 | `GTKB-ISOLATION-018` |  | backlogged | open | ok | Execute Agent Red child-directory cutover |
| 1026 | `GTKB-ISOLATION-019` |  | backlogged | open | ok | Close the isolation program with final verification and backlog cleanup |
|  | `WI-3286` | P2 | resolved | resolved | ok | Re-home or retire AGENT-RED-* projects/work_items in GT-KB MemBase per project-root boundary |
|  | `WI-3289` | P2 | resolved | resolved | ok | Consolidate to single canonical groundtruth.db; classify or remove duplicates |

### `PROJECT-GTKB-ISOLATION-AGENT-RED-CUTOVER` - Agent Red cutover

- Status/rank: `active` / `1025`
- Parent: `PROJECT-GTKB-ISOLATION`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1025 | `GTKB-ISOLATION-018` |  | backlogged | open | ok | Execute Agent Red child-directory cutover |

### `PROJECT-GTKB-ISOLATION-PROGRAM-CLOSEOUT` - Program closeout

- Status/rank: `active` / `1026`
- Parent: `PROJECT-GTKB-ISOLATION`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1026 | `GTKB-ISOLATION-019` |  | backlogged | open | ok | Close the isolation program with final verification and backlog cleanup |

### `PROJECT-GTKB-MASS-001` - GTKB-MASS-001

- Status/rank: `active` / `1027`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1027 | `GTKB-MASS-001` |  | backlogged | open | ok | Execute GT-KB mass-adoption readiness plan |

### `PROJECT-GTKB-CORE-001` - GTKB-CORE-001

- Status/rank: `active` / `1028`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1028 | `GTKB-CORE-001` |  | backlogged | open | gap | Make core application specification intake default GT-KB behavior |

### `PROJECT-GTKB-GOVERNANCE-ADOPTION-TIER-A` - Tier A

- Status/rank: `active` / `1029`
- Parent: `PROJECT-GTKB-GOVERNANCE-ADOPTION`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1029 | `GTKB-GOV-001` |  | backlogged | open | gap | Complete Agent Red Tier A managed-skill adoption apply |

### `PROJECT-GTKB-GOVERNANCE-ADOPTION` - GTKB-GOVERNANCE-ADOPTION

- Status/rank: `active` / `1030`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=8, open=5, terminal=3, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1029 | `GTKB-GOV-001` |  | backlogged | open | gap | Complete Agent Red Tier A managed-skill adoption apply |
| 1030 | `GTKB-GOV-002` |  | backlogged | open | gap | Promote Agent Red release-candidate gate into the GT-KB managed skill/doctor model |
| 1031 | `GTKB-GOV-003` |  | backlogged | open | gap | Add an Agent Red governance-adoption doctor check |
| 1033 | `GTKB-GOV-008` |  | backlogged | open | gap | Repair bridge dispatcher deferral enforcement |
| 1034 | `GTKB-GOV-009` |  | resolved | verified | gap | Await GT-KB Azure CI/CD gates verification |
| 1035 | `GTKB-GOV-010` |  | backlogged | open | gap | Maintain unified backlog harvest/reconciliation audit as release-gate input |
|  | `WI-3287` | P2 | resolved | resolved | ok | Detect gt CLI silent-drift on PATH; document python -m groundtruth_kb as canonical fallback |
|  | `WI-3290` | P2 | resolved | resolved | ok | GT-KB CLI shall emit UTF-8 regardless of host shell codepage; doctor check verifies non-ASCII emit |

### `PROJECT-GTKB-GOV-004` - GTKB-GOV-004

- Status/rank: `active` / `1032`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1032 | `GTKB-GOV-004` |  | backlogged | open | gap | Reconcile legacy MemBase work items into a high-quality unified backlog |

### `PROJECT-FORWARD-WORK` - Forward-work

- Status/rank: `active` / `1036`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1036 | `WORKLIST-FORWARD-WORK-ORDERING-REFERENCE-GO-D-2026-04-17` |  | resolved | retired | ok | ordering reference (GO'd 2026-04-17) |

### `PROJECT-AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION` - AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION

- Status/rank: `active` / `1037`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1037 | `WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION` |  | backlogged | open | ok | Explore Claude Design GUI workflow for Agent Red GUI work |

### `PROJECT-CTO` - CTO

- Status/rank: `active` / `1038`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1038 | `WORKLIST-CTO-READINESS-AGENT-RED-FULL-CLEANUP` |  | resolved | retired | ok | readiness (Agent Red full cleanup) |

### `PROJECT-GT-KB` - GT-KB

- Status/rank: `active` / `1039`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1039 | `GT-KB` |  | resolved | retired | ok | Operational Skills Tier A (Phase A scope GO'd 2026-04-17) |

### `PROJECT-GT-KB-TIER-A` - Tier A

- Status/rank: `active` / `1039`
- Parent: `PROJECT-GT-KB`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1039 | `GT-KB` |  | resolved | retired | ok | Operational Skills Tier A (Phase A scope GO'd 2026-04-17) |

### `PROJECT-POR-SPEC-HYGIENE` - POR-SPEC-HYGIENE

- Status/rank: `active` / `1040`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1040 | `WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE` |  | backlogged | open | ok | Complete POR Steps 16.D-16.E spec hygiene remediation |

### `PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE` - ZERO-KNOWLEDGE-ARCHITECTURE

- Status/rank: `active` / `1041`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1041 | `WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` |  | backlogged | open | ok | Zero-knowledge architecture Phase 4 |

### `PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4` - Phase 4

- Status/rank: `active` / `1041`
- Parent: `PROJECT-ZERO-KNOWLEDGE-ARCHITECTURE`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1041 | `WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` |  | backlogged | open | ok | Zero-knowledge architecture Phase 4 |

### `PROJECT-MINOR` - Minor

- Status/rank: `active` / `1042`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1042 | `WORKLIST-MINOR-GT-KB-FIXES-INVESTIGATED-2026-04-17-BOTH-RESOLVED-NON-ISSUES` |  | resolved | not_a_defect | ok | GT-KB fixes (investigated 2026-04-17 — both resolved/non-issues) |

### `GTKB-V1-RELEASE-STRATEGY-001` - GT-KB v1.0 Release Strategy

- Status/rank: `active` / `None`
- purpose: Organize all v1.0 implementation prerequisite and slice work under one governed scope, per DELIB-2234 (Hybrid Variant + Release-Gate + 3-tier + In-tree-then-separate spec corpus + Promotion governance + Quality-driven...
- target: v1.0 release declared when Agent Red successfully ports onto a clean install of the release-layer scaffold and acceptance criteria (§10.3) are met.
- scope: In-scope: §10.1 enforcement gate, §10.2 spec-corpus distillation, §10.3 acceptance criteria, §10.4 Docker validator, §10.5 rule-corpus cleanse, framing-restoration revision, Antigravity advisory disposition, envelope-...
- notes: Created at S363 ::wrap to provide cross-session continuity for 8 open tasks. Authoritative DELIBs: DELIB-2234 (strategy), DELIB-2238 (envelope convention). Work items added immediately after project creation.
- Members: active=8, open=8, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3404` | P0 | backlogged | open | ok | Define v1.0 acceptance criteria (sole anti-perpetual-rc1 checkpoint per §9.2) |
|  | `WI-3401` | P1 | backlogged | open | ok | Scope §10.1 mechanical-enforcement gate bridge proposal (Hybrid Variant prereq) |
|  | `WI-3402` | P1 | backlogged | open | ok | Scope §10.2 spec-corpus distillation bridge proposal (in-tree specs/ initially) |
|  | `WI-3403` | P1 | backlogged | open | ok | Scope Docker isolation-validator test (release-gate validator, promoted from Antigravity Finding 1) |
|  | `WI-3400` | P2 | backlogged | open | ok | Capture Antigravity 2026-05-27 V1-RELEASE-STRATEGY-REVIEW advisory disposition (peer-solution-advisory-loop) |
|  | `WI-3405` | P2 | backlogged | open | ok | Revise gtkb-agent-red-reference-adopter-framing-restoration to -003 REVISED (ADR-ISOLATION-APPLICATION-PLACEMENT-001... |
|  | `WI-3406` | P2 | backlogged | open | ok | Scope envelope-convention specs + reconsidered wrap-procedure (deferred to later session) |
|  | `WI-3407` | P2 | backlogged | open | ok | Create decision-capture composite DELIB workflow skill (per owner agreement) |

### `PROJECT-AGENT-RED-DEPLOY-PIPELINE` - AGENT-RED-DEPLOY-PIPELINE

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=30, open=1, terminal=29, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3172` |  | backlogged | open | gap | Resolve deploy pipeline Phase 0 environment validation failure |
|  | `WI-3173` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3174` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3175` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3176` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3177` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3219` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3220` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3225` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3226` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3227` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3228` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3229` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3230` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3231` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3232` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3233` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3234` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3235` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3236` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3237` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3238` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3239` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3240` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3241` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3242` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3243` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3244` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3245` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |
|  | `WI-3246` |  | resolved | retired | gap | Deploy pipeline failure: Phase 0 (Validate Environment) |

### `PROJECT-AGENT-RED-RELEASE-READINESS` - AGENT-RED-RELEASE-READINESS

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3248` | P0 | backlogged | open | ok | Agent Red deployability and maintainability preservation gate |

### `PROJECT-AGENT-RED-SPEC-HYGIENE` - AGENT-RED-SPEC-HYGIENE

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=7, open=7, terminal=0, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3183` | P2 | backlogged | open | gap | KB integrity -- SPA cluster test-ID investigation closure: 10 SPA specs have no current test linkage |
|  | `WI-3184` | P2 | backlogged | open | gap | control-plane placeholder-test remediation: revert 10 specs from verified to implemented — no KB test linkage after S... |
|  | `WI-3178` | P3 | backlogged | open | gap | Verified-but-untested spec hygiene: SPEC-1076 alert acknowledge endpoint needs real test coverage |
|  | `WI-3179` | P3 | backlogged | open | ok | Verified-but-untested spec hygiene: SPEC-1078 MFA status endpoint needs real test coverage |
|  | `WI-3180` | P3 | backlogged | open | ok | Verified-but-untested spec hygiene: SPEC-0661 pricing overage thresholds need real test coverage |
|  | `WI-3181` | P3 | backlogged | open | ok | Verified-but-untested spec hygiene: SPEC-0811 pipeline budget P50/timeout needs real test coverage |
|  | `WI-3182` | P3 | backlogged | open | ok | Verified-but-untested spec hygiene: SPEC-1138 widget views definition needs real behavioral test |

### `PROJECT-AGENT-RED-TEST-COVERAGE-GAPS` - AGENT-RED-TEST-COVERAGE-GAPS

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=38, open=38, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3185` | P3 | backlogged | open | gap | Test coverage gap: Testable Element Dimension Taxonomy |
|  | `WI-3186` | P3 | backlogged | open | gap | Test coverage gap: Campaigns Agent -- Marketing Campaign Information MCP Server |
|  | `WI-3187` | P3 | backlogged | open | gap | Test coverage gap: Bot Agent -- External AI Agent Conversation MCP Server |
|  | `WI-3188` | P3 | backlogged | open | gap | Test coverage gap: Sales Agent -- In-line Purchase Completion MCP Server |
|  | `WI-3189` | P3 | backlogged | open | gap | Test coverage gap: Gateway Agent -- Human Escalation Connection MCP Server |
|  | `WI-3190` | P3 | backlogged | open | gap | Test coverage gap: Schedule Agent -- Follow-up Activities and Event Notifications MCP Server |
|  | `WI-3191` | P3 | backlogged | open | gap | Test coverage gap: 3rd-Party MCP Server Integrations -- External Service Connectors |
|  | `WI-3192` | P3 | backlogged | open | gap | Test coverage gap: Documentation: First-login magic link flow in setup guide |
|  | `WI-3193` | P3 | backlogged | open | gap | Test coverage gap: Documentation: Intent categories diagram legible in light and dark mode |
|  | `WI-3194` | P3 | backlogged | open | gap | Test coverage gap: Documentation: Knowledge retrieval technical detail in How It Works |
|  | `WI-3195` | P3 | backlogged | open | gap | Test coverage gap: Docs site landing page logo must use black text variant in light mode |
|  | `WI-3196` | P3 | backlogged | open | gap | Test coverage gap: Changelog must include entries for all production-deployed versions |
|  | `WI-3197` | P3 | backlogged | open | gap | Test coverage gap: Integration Framework - Admin UI Setup & Dashboard |
|  | `WI-3198` | P3 | backlogged | open | gap | Test coverage gap: Integration Framework - Cosmos DB Schema Extensions |
|  | `WI-3199` | P3 | backlogged | open | gap | Test coverage gap: Zendesk Integration - Full Helpdesk Adapter |
|  | `WI-3200` | P3 | backlogged | open | gap | Test coverage gap: Slack Integration - Channel Adapter for AI Bot |
|  | `WI-3201` | P3 | backlogged | open | gap | Test coverage gap: Google Docs Integration - Knowledge Source Adapter |
|  | `WI-3202` | P3 | backlogged | open | gap | Test coverage gap: Integration Framework - Internal Event Bus |
|  | `WI-3203` | P3 | backlogged | open | gap | Test coverage gap: Container Failure Resilience |
|  | `WI-3204` | P3 | backlogged | open | gap | Test coverage gap: Multi-Replica Agent Routing |
|  | `WI-3205` | P3 | backlogged | open | gap | Test coverage gap: Natural Language Escalation to Peer Agents |
|  | `WI-3206` | P3 | backlogged | open | gap | Test coverage gap: Agent Marketplace Discovery and Installation |
|  | `WI-3207` | P3 | backlogged | open | gap | Test coverage gap: Conversation-Level Agent Activation |
|  | `WI-3208` | P3 | backlogged | open | gap | Test coverage gap: Structured Answer Blocks |
|  | `WI-3209` | P3 | backlogged | open | gap | Test coverage gap: Transcript Continuity |
|  | `WI-3210` | P3 | backlogged | open | gap | Test coverage gap: Conversation Preview with Message Insights |
|  | `WI-3211` | P3 | backlogged | open | gap | Test coverage gap: Community Feedback Harvesting Loop |
|  | `WI-3212` | P3 | backlogged | open | gap | Test coverage gap: Phone Identity Channel: SMS OTP via Azure Communication Services |
|  | `WI-3213` | P3 | backlogged | open | gap | Test coverage gap: WhatsApp Escalation Channel: Deep-Link to Merchant WhatsApp |
|  | `WI-3214` | P3 | backlogged | open | gap | Test coverage gap: Tenant Display Name — human-readable tenant identifier for SPA |
|  | `WI-3215` | P3 | backlogged | open | gap | Test coverage gap: Superadmin Contact Requirement — hard provisioning gate |
|  | `WI-3216` | P3 | backlogged | open | gap | Test coverage gap: Deliberation archive: structured storage and semantic search for reasoning artifacts |
|  | `WI-3217` | P3 | backlogged | open | gap | Test coverage gap: Pipeline lifecycle metrics: data model and collection |
|  | `WI-3218` | P3 | backlogged | open | gap | Test coverage gap: Pipeline lifecycle metrics: computed metrics and aggregation |
|  | `WI-3221` | P3 | backlogged | open | gap | Test coverage gap: SPEC-1585 needs deterministic test evidence |
|  | `WI-3222` | P3 | backlogged | open | gap | Test coverage gap: SPEC-1586 needs deterministic test evidence |
|  | `WI-3223` | P3 | backlogged | open | gap | Test coverage gap: SPEC-1587 needs deterministic test evidence |
|  | `WI-3224` | P3 | backlogged | open | gap | Test coverage gap: Deployment modal pre-fill (SPEC-1841 superseded-meaning) |

### `PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-ONBOARDING` - Antigravity Onboarding

- Status/rank: `active` / `None`
- Parent: `PROJECT-ANTIGRAVITY-INTEGRATION`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=5, open=0, terminal=5, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3345` | P1 | completed | verified | ok | Research spike: Antigravity IDE hook/skill config format and hook events |
|  | `WI-3346` | P1 | completed | verified | gap | .antigravity/ harness integration directory |
|  | `WI-3347` | P1 | completed | verified | gap | LO-role-scoped Antigravity capability adapters and registry entries |
|  | `WI-3348` | P1 | completed | verified | gap | Register the Antigravity harness (identity C) |
|  | `WI-3349` | P1 | resolved | resolved | ok | End-to-end Gemini CLI headless LO-review dispatch verification |

### `PROJECT-ANTIGRAVITY-INTEGRATION-HARNESS-REGISTRY-REFACTOR` - Harness Registry Refactor

- Status/rank: `active` / `None`
- Parent: `PROJECT-ANTIGRAVITY-INTEGRATION`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=8, open=0, terminal=8, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3337` | P1 | completed | verified | gap | harnesses table schema and append-only versioning |
|  | `WI-3338` | P1 | completed | verified | gap | Generated hot-path harness-registry projection and generator |
|  | `WI-3339` | P1 | completed | verified | gap | Four-state harness lifecycle FSM and transition validators |
|  | `WI-3340` | P1 | completed | verified | gap | gt harness CLI command group |
|  | `WI-3341` | P1 | completed | verified | ok | Role portability and single-prime-builder invariant enforcement |
|  | `WI-3342` | P1 | resolved | resolved | ok | Phased reader migration from JSON to projection |
|  | `WI-3343` | P1 | resolved | resolved | ok | Extend ADR-SINGLE-HARNESS-OPERATING-MODE-001 for the harness registry architecture |
|  | `WI-3344` | P1 | completed | verified | gap | Data-driven cross-harness dispatch from invocation_surfaces |

### `PROJECT-ANTIGRAVITY-ONBOARDING` - Antigravity Onboarding

- Status/rank: `active` / `None`
- Parent: `PROJECT-ANTIGRAVITY-INTEGRATION`
- purpose: Antigravity harness onboarding: .antigravity/ integration dir, LO-role-scoped capability adapters, harness record C, Gemini CLI data-driven dispatch verification.
- Members: active=5, open=0, terminal=5, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-3345` | P1 | completed | verified | ok | Research spike: Antigravity IDE hook/skill config format and hook events |
| 2 | `WI-3346` | P1 | completed | verified | gap | .antigravity/ harness integration directory |
| 3 | `WI-3347` | P1 | completed | verified | gap | LO-role-scoped Antigravity capability adapters and registry entries |
| 4 | `WI-3348` | P1 | completed | verified | gap | Register the Antigravity harness (identity C) |
| 5 | `WI-3349` | P1 | resolved | resolved | ok | End-to-end Gemini CLI headless LO-review dispatch verification |

### `PROJECT-GT-KB-CLARIFICATION-TOOLING` - GT-KB Clarification Tooling

- Status/rank: `active` / `None`
- Description: (missing purpose, target outcome, scope note, and notes)
- Members: active=2, open=1, terminal=1, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-AUTO-SPEC-INTAKE-1262C1` |  | backlogged | open | ok | Implement SPEC-INTAKE-1262c1: grill-me-for-clarification owner clarification interview skill |
| 2 | `WI-3321` | medium | resolved | resolved | ok | Implement grill-me-for-clarification owner clarification interview skill |

### `PROJECT-GT-KB-INFRASTRUCTURE` - GT-KB Infrastructure

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-4248` | P2 | backlogged | open | ok | Diagnose Codex Windows parallel shell launch flake |

### `PROJECT-GTKB-ADOPTER-EXPERIENCE` - GTKB-ADOPTER-EXPERIENCE

- Status/rank: `active` / `None`
- purpose: GT-KB adopter packaging, core-spec intake, governance-adoption doctor surfaces.
- target: Downstream adopters can consume GT-KB cleanly and verify adoption health via doctor.
- Members: active=8, open=8, terminal=0, inactive=0, child_projects=0, active_auths=2, active_links=7

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `GTKB-CORE-001` |  | backlogged | open | gap | Make core application specification intake default GT-KB behavior |
|  | `GTKB-GOV-001` |  | backlogged | open | gap | Complete Agent Red Tier A managed-skill adoption apply |
|  | `GTKB-GOV-002` |  | backlogged | open | gap | Promote Agent Red release-candidate gate into the GT-KB managed skill/doctor model |
|  | `GTKB-GOV-003` |  | backlogged | open | gap | Add an Agent Red governance-adoption doctor check |
|  | `GTKB-GOV-008` |  | backlogged | open | gap | Repair bridge dispatcher deferral enforcement |
|  | `GTKB-GOV-010` |  | backlogged | open | gap | Maintain unified backlog harvest/reconciliation audit as release-gate input |
|  | `WI-3248` | P0 | backlogged | open | ok | Agent Red deployability and maintainability preservation gate |
|  | `WI-3352` | P3 | backlogged | open | ok | Canonical end-to-end GT-KB lifecycle reference for new-agent orientation |

### `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` - GTKB-APPROVAL-PACKET-ERGONOMICS

- Status/rank: `active` / `None`
- purpose: Reduce per-mutation approval-packet handling friction across the formal-artifact-approval workflow.
- target: Approval-packet generation, validation, and gate behavior reduce friction in routine sessions without weakening governance.
- Members: active=5, open=4, terminal=1, inactive=0, child_projects=0, active_auths=1, active_links=4

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3279` | P1 | created | open | ok | gt generate-approval-packet CLI: deterministic packet generation + LF normalization helper |
|  | `WI-3277` | P2 | created | open | ok | Owner-decision-tracker baseline restoration: investigate + repair 21 pre-existing failures |
|  | `WI-3281` | P2 | created | open | ok | bridge-skill helper: protected-file Write that lets the gate hook fire |
|  | `WI-3378` | P2 | backlogged | open | ok | Build a first-class gap-state formal-artifact MemBase capture lane |
|  | `WI-3310` |  | resolved | resolved | gap | Implementation gate friction hygiene (null-sink redirect allowlist + state-aware chain walk + sqlite PRAGMA-dropped s... |

### `PROJECT-GTKB-BACKLOG-CAPTURE-001-APPROVAL-STATE-TAXONOMY` - Approval state taxonomy

- Status/rank: `active` / `None`
- Parent: `PROJECT-GTKB-BACKLOG-CAPTURE-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3271` | P1 | backlogged | open | ok | Backlog approval-state taxonomy and AUQ implementation gate |

### `PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-ADD-COMMAND` - Backlog add command

- Status/rank: `active` / `None`
- Parent: `PROJECT-GTKB-BACKLOG-CAPTURE-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=2, open=2, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3270` | P2 | backlogged | open | ok | Add governed backlog item creation command |
|  | `WI-3269` | P3 | created | open | ok | GTKB-GT-BACKLOG-ADD-CLI - add `gt backlog add` subcommand for owner-directed backlog additions |

### `PROJECT-GTKB-BRIDGE-CONTENTION-L1-INDEX-WRITES` - Bridge Contention L1: INDEX Writes

- Status/rank: `active` / `None`
- Parent: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- purpose: Consolidated view of bridge INDEX lost-update and serialization work.
- scope: Consolidated bridge-contention project view; not a second backlog authority.
- Members: active=2, open=0, terminal=2, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-3513` | P1 | resolved | resolved | ok | Serialize agent-tool INDEX.md edits: close lost-update gap after bridge-scheduler slices 3/4 |
| 2 | `WI-3280` | P3 | resolved | resolved | ok | Cross-harness event-driven trigger: INDEX edit race coordination + quiesce window |

### `PROJECT-GTKB-BRIDGE-CONTENTION-L2-DISPATCH` - Bridge Contention L2: Dispatch

- Status/rank: `active` / `None`
- Parent: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- purpose: Consolidated view of bridge dispatch suppression, lease, and role/status work.
- scope: Consolidated bridge-contention project view; not a second backlog authority.
- Members: active=4, open=0, terminal=4, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-3265` | P1 | resolved | wont_fix | gap | Cross-harness trigger fires unreliably in codex exec sessions (dispatch-state refresh lag) |
| 2 | `WI-3485` | P3 | resolved | resolved | ok | cross_harness_bridge_trigger active-session suppression 'counterpart' naming misnomer: checks receiver/target's OWN l... |
| 3 | `WI-4213` | P2 | resolved | resolved | ok | Formalize active-status capability gate: 'active' requires bridge-event reception (PB-role-without-event-surface is i... |
| 4 | `WI-AUTO-SPEC-INTAKE-57A736` |  | resolved | resolved | ok | Implement SPEC-INTAKE-57a736: Bridge dispatch suppression scoped per bridge document (per-document lease) |

### `PROJECT-GTKB-BRIDGE-CONTENTION-L3-GATE-RACES` - Bridge Contention L3: Gate Races

- Status/rank: `active` / `None`
- Parent: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- purpose: Consolidated view of bridge gate race and harness boundary friction.
- scope: Consolidated bridge-contention project view; not a second backlog authority.
- Members: active=3, open=3, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-3320` | P3 | created | open | ok | Fix flaky bridge-compliance-audit test (shared audit-file race) |
| 2 | `WI-3334` | P2 | backlogged | open | ok | bridge-compliance-gate fires an ask on every bridge/INDEX.md edit when a pending proposal lists INDEX.md in target_paths |
| 3 | `WI-3322` | P2 | created | open | ok | spec-intake auto-WI IDs (WI-AUTO-*) are rejected by the bridge-compliance-gate Work Item metadata regex |

### `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` - GTKB-BRIDGE-PROTOCOL-RELIABILITY

- Status/rank: `active` / `None`
- purpose: Bridge poller / trigger / index reliability + freshness work.
- target: Bridge dispatch substrate operates reliably; INDEX edit races avoided; citation freshness enforced.
- Members: active=22, open=6, terminal=16, inactive=0, child_projects=4, active_auths=6, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3256` | P2 | resolved | resolved | ok | Reconsider mechanism for gtkb-claude-code-bridge-status-thread-automation (Codex NO-GO@004; 4 NO-GOs across 4 differe... |
|  | `GTKB-BRIDGE-POLLER-001` |  | backlogged | retired | ok | GTKB-BRIDGE-POLLER-001 |
|  | `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` |  | backlogged | retired | gap | GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT |
|  | `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR` |  | backlogged | retired | ok | GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR |
|  | `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` |  | resolved | resolved | ok | Migrate direct bridge INDEX writers to gtkb_bridge_writer.py |
|  | `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL` |  | resolved | resolved | gap | GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL |
|  | `WI-3353` | P1 | backlogged | open | ok | Bridge governance hooks resolve project root from session cwd, mis-targeting MemBase and bridge/INDEX.md in .claude/w... |
|  | `WI-3380` | P1 | backlogged | open | gap | Add a deterministic preflight comparing produced files against GO-derived target_path_globs |
|  | `WI-3513` | P1 | resolved | resolved | ok | Serialize agent-tool INDEX.md edits: close lost-update gap after bridge-scheduler slices 3/4 |
|  | `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` | P1 | resolved | resolved | ok | Implement SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001: Bridge and operating-mode switching transactions |
|  | `GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` | P2 | created | open | ok | Align implementation-start gate verification-plan heading recognition with bridge clause-preflight |
|  | `WI-3267` | P2 | resolved | resolved | ok | GTKB-BRIDGE-PROPOSAL-CITATION-FRESHNESS-PREFLIGHT - warn on stale cross-thread state references |
|  | `WI-3414` | P2 | resolved | resolved | gap | Integrate bridge work-intent registry into Prime-side write paths (hook + helper + trigger) |
|  | `WI-3439` | P2 | backlogged | open | ok | Add ## Requirement Sufficiency presence check to bridge-compliance-gate at proposal Write-time |
|  | `WI-3448` | P2 | backlogged | open | ok | bridge-compliance-gate CLAUSE-PROJECT-METADATA-PRESENT never fires on real proposals (first_line keys off NEW/REVISED... |
|  | `WI-4215` | P2 | resolved | resolved | ok | impl-auth begin gate requires ## section headings but no upstream gate enforces it (post-GO dead-end) |
|  | `WI-4217` | P2 | resolved | resolved | ok | inventory-drift gate strands commits on legitimate toolchain version upgrades + collector non-determinism |
|  | `WI-4218` | P2 | resolved | resolved | ok | Inventory-drift gate non-reconcilable: writer vs checker disagree on gh version-probe evidence |
|  | `WI-3280` | P3 | resolved | resolved | ok | Cross-harness event-driven trigger: INDEX edit race coordination + quiesce window |
|  | `WI-3384` | P3 | backlogged | open | gap | CLAUSE-IN-ROOT failure detector false-positives on disclosure mentions of out-of-root paths |
|  | `WI-3485` | P3 | resolved | resolved | ok | cross_harness_bridge_trigger active-session suppression 'counterpart' naming misnomer: checks receiver/target's OWN l... |
|  | `WI-AUTO-SPEC-INTAKE-57A736` |  | resolved | resolved | ok | Implement SPEC-INTAKE-57a736: Bridge dispatch suppression scoped per bridge document (per-document lease) |

### `PROJECT-GTKB-BRIDGE-RECONCILIATION` - Bridge Reconciliation Detection and Correction

- Status/rank: `active` / `None`
- Parent: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- purpose: Detect and correct drift between bridge history, bridge INDEX state, and MemBase backlog/work-item terminal state without broad automatic mutations.
- target: Reusable checks surface bridge/backlog deviations early, correction packets are prepared one mutation class at a time, and verified bridge work is reflected accurately in backlog/project state.
- scope: Includes read-only detection, JSON/markdown reporting, governed correction packet generation, skill/runbook integration, and hygiene-sweep/session-wrap surfacing. Excludes automatic bulk status mutation and any bypass...
- Members: active=6, open=6, terminal=0, inactive=0, child_projects=0, active_auths=2, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 0 | `WI-4241` | P1 | backlogged | open | ok | Implementation-start gate consumes durable owner Requirement Sufficiency clarification |
| 1 | `WI-4234` | P2 | backlogged | open | ok | Reusable sanity gate for bridge/backlog terminal-state reconciliation |
| 2 | `WI-4235` | P1 | backlogged | open | ok | Detect bridge INDEX/file-chain deviations and prepare repair packets |
| 3 | `WI-4236` | P1 | backlogged | open | ok | Generate governed bridge reconciliation correction packets by triage class |
| 4 | `WI-4237` | P2 | backlogged | open | ok | Create bridge reconciliation operator skill and runbook |
| 5 | `WI-4238` | P2 | backlogged | open | ok | Integrate bridge reconciliation checks into hygiene sweep or session-wrap scan |

### `PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY` - GTKB-BRIDGE-SIGNAL-QUALITY

- Status/rank: `active` / `None`
- purpose: Improve bridge operational signal quality across dispatch diagnostics and Codex bridge governance hook adapters.
- target: Intentional inactive bridge substrate is reported as state rather than failure-log spam, and Codex bridge hooks reliably distinguish benign bridge path references from governed bridge content writes.
- scope: Backlog capture only. Implementation still requires bridge proposal review, GO, implementation report, and Loyal Opposition verification.
- notes: Approved by Mike on 2026-06-02 after grilling decisions captured in DELIB-20260602-BRIDGE-SIGNAL-PROJECT-STRICTNESS and DELIB-20260602-BRIDGE-SIGNAL-SUBSTRATE-STATE-ONLY. Project backlog-capture approval captured in D...
- Members: active=2, open=2, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-4253` | P2 | backlogged | open | ok | Bridge signal quality inactive substrate diagnostics |
| 2 | `WI-4254` | P2 | backlogged | open | ok | Codex bridge Bash adapters classify writes versus references |

### `PROJECT-GTKB-DASHBOARD-OBSERVABILITY` - GTKB-DASHBOARD-OBSERVABILITY

- Status/rank: `active` / `None`
- purpose: Dashboard, DORA metrics, observability surfaces.
- target: Owner has live visibility into platform/application state via Grafana dashboards + DORA panels.
- Members: active=4, open=4, terminal=0, inactive=0, child_projects=0, active_auths=1, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION` |  | backlogged | open | ok | GTKB-DASHBOARD-002 Slice 2.3 (integration) |
|  | `GTKB-DASHBOARD-002-SLICE-2-2-METRICS` |  | backlogged | open | ok | GTKB-DASHBOARD-002 Slice 2.2 (metrics) |
|  | `GTKB-DASHBOARD-003` |  | backlogged | open | ok | Dashboard industry-alignment Slice 3 (SLO, flow metrics, PR health, incident/MTTR, remote exposure, WCAG) |
|  | `GTKB-DORA-002` |  | backlogged | open | ok | DORA four-keys panels (consumer of GTKB-DORA-001) |

### `PROJECT-GTKB-ENV-SOT-TOPOLOGY` - PROJECT-GTKB-ENV-SOT-TOPOLOGY

- Status/rank: `active` / `None`
- purpose: Capture and maintain the env source-of-truth topology principle (separate platform + per-application SoTs; CLI-enforced alignment) as governed ADR/DCL/GOV artifacts.
- scope: Spec authoring per S365 owner directive; gt env CLI implementation + Agent Red migration are follow-on.
- Members: active=3, open=3, terminal=0, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3427` | P1 | backlogged | open | ok | Capture env-SoT topology principle as ADR + DCL + revised GOV per S365 AUQs |
|  | `WI-3430` | P2 | backlogged | open | ok | Migrate Agent Red from 3-file SoT layout to single SoT + CLI-generated per-sub-app views |
|  | `WI-3431` | P2 | backlogged | open | ok | Separate platform-level values from Agent Red application-level values in root .env.local |

### `PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT` - Envelope Open and Close action refinement

- Status/rank: `active` / `None`
- purpose: Refine the GT-KB session envelope open (startup disclosure) and close (wrap-up) behaviors plus work envelope dispositions per owner directive S366 2026-05-29
- scope: Touches session_self_initialization.py startup-disclosure composition, wrap-up procedures, and work envelope handling. First concrete WI removes the 'Work State' and 'Recommended Session Focus' sections from the start...
- Members: active=2, open=2, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3467` | P3 | backlogged | open | ok | Remove 'Work State' and 'Recommended Session Focus' sections from session envelope opening disclosure |
|  | `WI-3468` | P3 | backlogged | open | ok | Deliberation: owner grilling on potential GT-KB session envelope open/close + work envelope disposition enhancements |

### `PROJECT-GTKB-GOVERNANCE-HARDENING` - GTKB-GOVERNANCE-HARDENING

- Status/rank: `active` / `None`
- purpose: Hook/gate hardening: file-safety enforcement, commit hygiene, codex-feedback lints, legacy WI reconcile.
- target: PreToolUse gates close known drift gaps (LO file-safety, auto-push, commit-scope bundling) and codex-feedback patterns become pre-filing lints.
- Members: active=7, open=5, terminal=2, inactive=0, child_projects=0, active_auths=1, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `GTKB-GOV-DA-ENFORCEMENT` |  | resolved | retired | ok | GTKB-GOV-DA-ENFORCEMENT |
|  | `GTKB-GOV-CODE-QUALITY-BASELINE` |  | resolved | resolved | gap | GTKB-GOV-CODE-QUALITY-BASELINE |
|  | `GTKB-GOV-004` |  | backlogged | open | gap | Reconcile legacy MemBase work items into a high-quality unified backlog |
|  | `WI-3308` | P1 | created | open | gap | Governance hardening: enforce LO file-safety rule via PreToolUse Write/Edit hook |
|  | `GTKB-AUTO-PUSH-INVESTIGATION-001` | P2 | backlogged | open | ok | Investigate background auto-push of local commits to origin/develop |
|  | `GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001` | P2 | backlogged | open | ok | Pre-commit predicate to detect cross-scope bundling via mismatched approval packets |
|  | `WI-3268` | P2 | created | open | gap | GTKB-CODEX-FEEDBACK-PATTERN-LINTS - pre-filing lint catching recurrent NO-GO mechanical patterns |

### `PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001` - GTKB-IMPLEMENTATION-START-GATE-HARDENING-001

- Status/rank: `active` / `None`
- purpose: Harden the .claude/hooks/implementation-start-gate.py PreToolUse:Bash hook against false positives on read-only commands and other classification gaps.
- scope: First slice: axis-based classification per memory/feedback_security_parser_executing_wrapper_distinction.md + unit tests for read-only exempt + opaque-wrapper blocked. Future slices may follow.
- Members: active=2, open=1, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3291` | P1 | resolved | resolved | ok | Implementation-start-gate hook shall correctly classify read-only commands as exempt |
|  | `WI-3350` | P2 | backlogged | open | gap | implementation_authorization project-auth validator should accept a parent-project PAUTH for a sub-project proposal |

### `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` - GT-KB Interactive Session Role Override

- Status/rank: `active` / `None`
- purpose: Implement the durable-vs-session role authority split per ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 across both Claude and Codex SessionStart dispatchers and shared workstream-focus / attribution / doctor surfaces.
- target: Owner-typed init keyword ::init gtkb (pb\|lo) overrides durable role for interactive session disclosure, AXIS 2 surface, focus menu, attribution, and AUQ routing; durable role remains headless dispatch authority.
- scope: Bounded to 10 implementation slices per bridge/gtkb-interactive-session-role-override-scoping-003.md. Out of scope: Codex AXIS 2 app-thread (follow-on).
- Members: active=7, open=3, terminal=4, inactive=3, child_projects=0, active_auths=2, active_links=8

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3474` | P2 | backlogged | open | ok | Slice 4 - AXIS 2 Claude-native surface role-awareness + shared session-role resolver |
|  | `WI-3475` | P3 | resolved | resolved | ok | Slice 5 - Workstream-focus role awareness (focus-menu shape follows resolved session role) |
|  | `WI-3476` | P3 | resolved | resolved | ok | Slice 6 - MemBase attribution reflects resolved session role |
|  | `WI-3477` | P3 | resolved | resolved | ok | Slice 7 - Doctor checks for session-role marker validity |
|  | `WI-3478` | P3 | resolved | resolved | gap | Slice 8 - Codex hook parity check enforces the new resolution-table contract |
|  | `WI-3479` | P3 | backlogged | open | gap | Slice 9 - Rule and CLAUDE/AGENTS updates for the durable-vs-session split |
|  | `WI-3480` | P3 | backlogged | open | gap | Slice 10 - Regression and integration tests across both harnesses |

### `PROJECT-GTKB-ISOLATION-CLOSEOUT` - GTKB-ISOLATION-CLOSEOUT

- Status/rank: `active` / `None`
- purpose: Final closeout of the GT-KB isolation program (Phase 7 + adopter packaging + program backstop).
- target: GTKB-ISOLATION-015, -017, -019 reach VERIFIED; isolation program retired.
- Members: active=3, open=3, terminal=0, inactive=0, child_projects=0, active_auths=1, active_links=3

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `GTKB-ISOLATION-015` |  | backlogged | open | ok | Complete full Phase 7 work-subject/root enforcement (Slice 1 VERIFIED; Slice 2 remaining) |
|  | `GTKB-ISOLATION-017` |  | backlogged | open | ok | Implement downstream adopter packaging and clean-adopter validation |
|  | `GTKB-ISOLATION-019` |  | backlogged | open | ok | Close the isolation program with final verification and backlog cleanup |

### `PROJECT-GTKB-LO-ADVISORY-INTAKE` - GTKB-LO-ADVISORY-INTAKE

- Status/rank: `active` / `None`
- purpose: Route accumulated Loyal-Opposition advisory drops (INSIGHTS-*.md) into governed Prime-side dispositions per peer-solution-advisory-loop rules.
- target: All current LO advisories either filed as DELIB records (reject/defer/monitor) or converted into bridge proposals (adopt/adapt).
- Members: active=12, open=8, terminal=4, inactive=0, child_projects=0, active_auths=1, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3297` | high | resolved | resolved | ok | Route LO advisory: INSIGHTS-2026-05-09-22-26-GTKB-MCP-STABLE-HARNESS-SURFACE-ADVISORY.md |
|  | `WI-3303` | high | resolved | resolved | ok | Route LO advisory: INSIGHTS-2026-05-11-08-44-LO-HYGIENE-ASSESSMENT-SKILL-ADVISORY.md |
|  | `WI-3298` | medium | resolved | resolved | ok | Route LO advisory: INSIGHTS-2026-05-09-22-35-BRIDGE-ADVISORY-REPORT-MESSAGE-TYPE.md |
|  | `WI-3300` | P2 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md |
|  | `WI-3296` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-09-14-20-ROLE-SESSION-LIFECYCLE-REVIEW.md |
|  | `WI-3299` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md |
|  | `WI-3301` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-11-06-51-GOOGLE-OPAL-REVIEW.md |
|  | `WI-3302` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW.md |
|  | `WI-3304` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-11-11-00-GITHUB-AI-HARNESS-ECOSYSTEM-ADVISORY.md |
|  | `WI-3305` | P3 | resolved | resolved | gap | Route bridge ADVISORY: gtkb-owner-role-switch-codex-loyal-opposition |
|  | `WI-3306` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md |
|  | `WI-3307` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-07-16-12-CANONICAL-TERMINOLOGY-SYSTEM-AND-BOUNDED-CONTEXT-ADVISORY.md |

### `PROJECT-GTKB-LO-ADVISORY-ROUTING` - LO Advisory Routing

- Status/rank: `active` / `None`
- purpose: Bundle standalone WIs that route Loyal Opposition advisories through the peer-solution-advisory-loop protocol per .claude/rules/peer-solution-advisory-loop.md
- scope: Each WI represents one LO-filed advisory awaiting Prime disposition (adopt/adapt/reject/defer/monitor per the 5-state vocabulary). Disposition produces either a NEW bridge proposal (adopt/adapt) or a Deliberation Arch...
- Members: active=25, open=23, terminal=2, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3433` | high | created | open | gap | Route LO advisory: INSIGHTS-2026-05-28-14-52-GTKB-DASHBOARD-OPERATIONS-COCKPIT-ADVISORY.md |
|  | `WI-3440` | high | created | open | gap | Route LO advisory: INSIGHTS-2026-05-29-06-50-delib-2500-review.md |
|  | `WI-3331` | P1 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-15-15-07-owner-decision-tracker-startup-relay-false-positive.md |
|  | `WI-3390` | P1 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-27-06-50-GTKB-SKILLS-GUIDANCE-COMPLIANCE-ADVISORY.md |
|  | `WI-3399` | P1 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md |
|  | `WI-3300` | P2 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md |
|  | `WI-3296` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-09-14-20-ROLE-SESSION-LIFECYCLE-REVIEW.md |
|  | `WI-3299` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md |
|  | `WI-3301` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-11-06-51-GOOGLE-OPAL-REVIEW.md |
|  | `WI-3302` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW.md |
|  | `WI-3304` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-11-11-00-GITHUB-AI-HARNESS-ECOSYSTEM-ADVISORY.md |
|  | `WI-3305` | P3 | resolved | resolved | gap | Route bridge ADVISORY: gtkb-owner-role-switch-codex-loyal-opposition |
|  | `WI-3306` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md |
|  | `WI-3307` | P3 | created | open | ok | Route LO advisory: INSIGHTS-2026-05-07-16-12-CANONICAL-TERMINOLOGY-SYSTEM-AND-BOUNDED-CONTEXT-ADVISORY.md |
|  | `WI-3330` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md |
|  | `WI-3389` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-27-06-49.md |
|  | `WI-3393` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md |
|  | `WI-3408` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-27-13-40.md |
|  | `WI-3412` | P3 | created | open | gap | Route LO advisory: INSIGHTS-2026-05-28-00-10.md |
|  | `WI-3437` | low | created | open | gap | Route LO advisory: INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md |
|  | `WI-3441` | low | created | open | gap | Route LO advisory: INSIGHTS-2026-05-29-07-12-delib-2500-envelope-convention-advisory.md |
|  | `WI-3457` | low | resolved | resolved | gap | Route bridge ADVISORY: gtkb-lo-hourly-quality-scout-advisory |
|  | `WI-3461` | low | created | open | gap | Route LO advisory: INSIGHTS-2026-05-29-23-15-GTKB-QUALITY-SCOUT-ADVISORY.md |
|  | `WI-3472` | low | created | open | gap | Route LO advisory: INSIGHTS-2026-05-30-01-05.md |
|  | `WI-3505` | low | created | open | gap | Route bridge ADVISORY: antigravity-inspection-results-053026-options-for-implementation |

### `PROJECT-GTKB-LO-REPORT-BACKFILL` - GTKB-LO-REPORT-BACKFILL

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3162` | P2 | backlogged | new | gap | Backfill existing LO reports and bridge history |

### `PROJECT-GTKB-MAY29-HYGIENE` - May29 Hygiene

- Status/rank: `active` / `None`
- purpose: Bundle near-term standalone hygiene WIs identified during S366 session for thorough hygiene execution today or tomorrow
- scope: Houses session-discovered hygiene defects + improvements small enough for near-term execution. Excludes multi-slice infrastructure work and items already covered by other active projects.
- Members: active=10, open=10, terminal=0, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3379` | P1 | backlogged | open | ok | Restore the implementation-start-gate.py PreToolUse registration in .claude/settings.json |
|  | `WI-3276` | P2 | created | open | ok | audit_standing_backlog_sources.py: WITHDRAWN not in actionable-status exclusion |
|  | `WI-3355` | P2 | backlogged | open | gap | insert_work_item project_name backfill doubles an already-PROJECT-prefixed id, mis-filing work-item project membershi... |
|  | `WI-3382` | P2 | backlogged | open | gap | Standardize a counterpart-reproducible in-root pytest temp surface across harnesses |
|  | `WI-3278` | P3 | created | open | gap | memory/work_list.md GTKB-GOV-010: correct stale tests/scripts path -> platform_tests/scripts |
|  | `WI-3317` | P3 | created | open | gap | Fix MUTATING_COMMAND_RE format-spec false-positive in implementation-start-gate |
|  | `WI-3327` | P3 | created | open | ok | Investigate startup-disclosure open-work-items metric (reported 3 vs actual 139 open) |
|  | `WI-3465` | P3 | backlogged | open | gap | Reconcile work_list.md vs MemBase work_items counts in session-startup metrics |
|  | `WI-3466` | P3 | backlogged | open | ok | Fix vestigial Agent Red scope filter naming on GT-KB MemBase work-item count |
|  | `WI-3469` | P3 | backlogged | open | ok | Reclaim .pytest-tmp/ from ACL contamination by parallel-session python processes; introduce unique-per-session basete... |

### `PROJECT-GTKB-RELIABILITY-FIXES` - GTKB-RELIABILITY-FIXES

- Status/rank: `active` / `None`
- purpose: Standing home for small, incidentally-discovered defect and reliability fixes that do not descend from a planned workstream.
- scope: Fast-lane eligibility governed by GOV-RELIABILITY-FAST-LANE-001.
- Members: active=84, open=68, terminal=16, inactive=0, child_projects=0, active_auths=12, active_links=3
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3323` | high | resolved | resolved | ok | Fix init-keyword startup-disclosure relay truncation: bounded pointer contract + harness-scoped cache |
|  | `WI-3333` | high | resolved | resolved | ok | Fix implementation_authorization.py parser false-positives blocking authorization of GO'd bridge proposals |
|  | `WI-3332` | P1 | resolved | resolved | ok | Suppress already-known startup relay matches in owner-decision tracker |
|  | `WI-3359` | P1 | closed | wont_fix | ok | Bridge notifier strands Codex-to-Claude dispatch when an interactive Claude session is open |
|  | `WI-3388` | P1 | backlogged | open | gap | Enforce implementation-report structural compliance + preserve draft mtime in impl_report_bridge.py file_report helper |
|  | `WI-3425` | P1 | backlogged | open | ok | Supersede DCL-SESSION-STARTUP-TOKEN-BUDGET-001 + DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001 (cache-presuming DCLs... |
|  | `WI-3426` | P1 | backlogged | open | ok | Amend GOV-08 (Knowledge Database is the single source of truth) to add bridge/INDEX.md to permitted markdown allowlis... |
|  | `WI-3427` | P1 | backlogged | open | ok | Capture env-SoT topology principle as ADR + DCL + revised GOV per S365 AUQs |
|  | `WI-3435` | P1 | backlogged | open | gap | Rebuild WI-3420 hygiene-sweep CLI test module after parallel-session destruction |
|  | `WI-3443` | P1 | backlogged | open | ok | D3+D4 fix: project-completion scanner/lifecycle should not count incidental Work Item citations; GOV-PROJECT-VERIFIED... |
|  | `WI-3449` | P1 | backlogged | open | ok | Durable fix: classify toolchain.*.version volatile in inventory drift gate + regen (2026-05-29) |
|  | `WI-4225` | P1 | backlogged | open | ok | Registry and scaffold fixture drift blocks pristine GT-KB test suite |
|  | `WI-3387` | medium | resolved | resolved | ok | Remediate Codex hook-strictness P1+P2 (apply_patch) findings |
|  | `WI-3322` | P2 | created | open | ok | spec-intake auto-WI IDs (WI-AUTO-*) are rejected by the bridge-compliance-gate Work Item metadata regex |
|  | `WI-3334` | P2 | backlogged | open | ok | bridge-compliance-gate fires an ask on every bridge/INDEX.md edit when a pending proposal lists INDEX.md in target_paths |
|  | `WI-3335` | P2 | backlogged | open | ok | spec-intake auto-WI IDs (WI-AUTO-*) are not recognized by the project-VERIFIED-completion scanner Work Item regex |
|  | `WI-3336` | P2 | backlogged | open | ok | bridge-compliance-gate section-boundary scanners treat heading lines inside fenced code blocks as section boundaries,... |
|  | `WI-3351` | P2 | backlogged | open | ok | bridge-compliance-gate SPEC_TEST_HEADING_RE lacks re.MULTILINE, hard-blocking every Claude-authored VERIFIED bridge v... |
|  | `WI-3355` | P2 | backlogged | open | gap | insert_work_item project_name backfill doubles an already-PROJECT-prefixed id, mis-filing work-item project membershi... |
|  | `WI-3356` | P2 | backlogged | open | ok | implementation-start-gate MUTATING_COMMAND_RE misclassifies read-only commands containing comparison operators as she... |
|  | `WI-3357` | P2 | backlogged | open | ok | implementation-start gate finalization exemption misclassifies quoted control markers as command chaining |
|  | `WI-3360` | P2 | resolved | resolved | ok | Repair cross-harness bridge trigger: ModuleNotFoundError import defect and stale active-session lock cleanup |
|  | `WI-3363` | P2 | backlogged | open | ok | bridge-stop-drain.py fires when it should defer: owner-decision recency window and no wrap-up-command deference |
|  | `WI-3364` | P2 | backlogged | open | ok | bridge/INDEX.md grows unbounded: add automatic deterministic archival trim to the bridge-write helpers |
|  | `WI-3369` | P2 | resolved | resolved | ok | Harness-registry mirror writer smoke-tested against the real groundtruth.db, inverting the harnesses registry table |
|  | `WI-3371` | P2 | resolved | resolved | ok | Orphaned platform_tests/test_host/test_build_contract.py aborts pytest platform_tests/ collection |
|  | `WI-3372` | P2 | backlogged | open | ok | Bridge-compliance check: require groundtruth.db in target_paths when a proposal declares KB mutation |
|  | `WI-3386` | P2 | backlogged | open | ok | Worker packet authorization envelope Slice 2: auto packet creation on dispatch |
|  | `WI-3391` | P2 | backlogged | open | gap | Skill modernization umbrella: thin-wrapper migration for kb-* skills + send-review deprecation + skill-health checker... |
|  | `WI-3396` | P2 | backlogged | open | ok | Canonicalize work_items.priority field values to P0/P1/P2/P3 schema (data hygiene migration) |
|  | `WI-3397` | P2 | resolved | resolved | ok | Back-fill project_work_item_memberships for 58 orphan open WIs lacking project membership rows |
|  | `WI-3398` | P2 | backlogged | open | ok | Worker-context bridge-protocol blocker recording (slice-2 cross-thread gate + slice-3 impl-auth wording) |
|  | `WI-3409` | P2 | backlogged | open | ok | Work-subject-aware testing/tool integration probe (query GT-KB repo for GT-KB session, Agent Red repo for application... |
|  | `WI-3413` | P2 | backlogged | open | ok | Dashboard launcher idempotence and PID tracking defects |
|  | `WI-3414` | P2 | resolved | resolved | gap | Integrate bridge work-intent registry into Prime-side write paths (hook + helper + trigger) |
|  | `WI-3417` | P2 | backlogged | open | ok | Repair SonarCloud project-key + source paths in sonar-project.properties (relink Agent-Red config to GT-KB layout) |
|  | `WI-3418` | P2 | backlogged | retired | ok | Repair RC Gate membase-seed step: resilient handling when CI seed fixture is absent (Path B) |
|  | `WI-3422` | P2 | resolved | resolved | ok | Add CI/security/release content triggers to spec-applicability.toml |
|  | `WI-3432` | P2 | resolved | resolved | ok | Harden run_spec_derived_tests.py: resolver-aware token extraction + implemented-vs-governing spec distinction |
|  | `WI-3442` | P2 | backlogged | open | ok | AXIS-2 classifier: exclude scoping-terminal threads with successor in flight |
|  | `WI-3447` | P2 | backlogged | open | ok | PB startup-disclosure cache fails freshness contract validation |
|  | `WI-3450` | P2 | backlogged | open | ok | Orphan-WI membership discovery Slice 2: per-orphan AUQ backfill assigning orphan open WIs to projects |
|  | `WI-3454` | P2 | backlogged | open | ok | Auth-gate Requirement Sufficiency parser escapes pre-impl review surfaces |
|  | `WI-3462` | P2 | backlogged | open | ok | Phase-2 implements-link backfill for v4 project auto-completion |
|  | `WI-3464` | P2 | backlogged | open | ok | Orphan-WI backfill Slice 2b: per-WI retire/exclude service (deterministic per-WI lifecycle surface) |
|  | `WI-3471` | P2 | backlogged | open | gap | Phase-3: resolve current ambiguous projects' implements-links via one-at-a-time owner AUQs |
|  | `WI-3488` | P2 | backlogged | open | ok | bridge/INDEX.md has 9 parse errors incl. stale role sentinel claiming Codex-as-Prime/prime_only (2026-05-20) |
|  | `WI-3491` | P2 | backlogged | open | ok | bridge/INDEX.md de-index gap: ~39 WITHDRAWN supersession notices + ~2 superseded threads not reflected in INDEX lates... |
|  | `WI-3492` | P2 | backlogged | open | ok | Add gt bridge propose deterministic CLI for proposal authoring (DELIB-S312) |
|  | `WI-3497` | P2 | backlogged | open | ok | Pre-commit hook auto-stages files outside the verified staged set (commit-scope contamination) |
|  | `WI-3498` | P2 | backlogged | open | gap | S373/S378 ruff cleanup: pre-run ruff format/check before commit-ready and clear current groundtruth-kb drift |
|  | `WI-3499` | P2 | backlogged | open | ok | impl-auth begin target_paths parser: exact-heading match misses annotated headings + slurps ### subsections |
|  | `WI-3500` | P2 | backlogged | open | ok | Startup rollup 'ungrouped non-terminal' counts the legacy work_items.project_name field, not the canonical membership... |
|  | `WI-3508` | P2 | backlogged | open | gap | CLAUSE-IN-ROOT failure_pattern false-matches in-root scratch paths (Unix temp token matched as bare substring); tight... |
|  | `WI-4251` | P2 | backlogged | open | ok | Allow read-only wrap and hygiene capture under implementation-start gate |
|  | `WI-3320` | P3 | created | open | ok | Fix flaky bridge-compliance-audit test (shared audit-file race) |
|  | `WI-3325` | P3 | created | open | ok | Fix adr_dcl_clause_preflight.py crash on relative --content-file path |
|  | `WI-3328` | P3 | created | open | ok | Session wrap-up does not clear the implementation-start packet (current.json) at VERIFIED |
|  | `WI-3329` | P3 | created | open | ok | complete_project_authorization() auto-retires the project when the sole authorization completes, with no keep-open op... |
|  | `WI-3354` | P3 | backlogged | open | gap | Audit and consolidate the eight independent project-root resolver definitions across the GT-KB codebase |
|  | `WI-3358` | P3 | backlogged | open | gap | implementation-start gate misclassifies mutating-command keywords and protected-path tokens inside quoted command arg... |
|  | `WI-3361` | P3 | backlogged | open | ok | Fix stale assertion regex in test_non_go_bridge_entry_cannot_create_authorization |
|  | `WI-3381` | P3 | backlogged | open | gap | GOV-REQUIREMENTS-COLLECTION-HOOK-001 tags retain abandoned-design remnants |
|  | `WI-3392` | P3 | backlogged | open | ok | Commit regenerated dev-environment inventory artifacts (2026-05-27 hygiene) |
|  | `WI-3394` | P3 | backlogged | open | gap | Investigate and repair local git repo broken-blob (tree aec44289 -> missing blob 01448913) |
|  | `WI-3410` | P3 | backlogged | open | ok | Impl-auth gate's literal substring matcher rejects valid Requirement Sufficiency phrasings (bias-case defect) |
|  | `WI-3411` | P3 | backlogged | open | ok | backlog add CLI auto-creates doubled-prefix project_work_item_memberships row (PROJECT-PROJECT-X instead of PROJECT-X) |
|  | `WI-3415` | P3 | backlogged | open | ok | Deterministic-service CLI: gt bridge verify-embedded-evidence for inline-appendix byte-faithfulness + root-boundary r... |
|  | `WI-3419` | P3 | backlogged | open | ok | Hygiene sweep: enumerate and remediate Agent-Red-inherited config drift across GT-KB repo (S363 Phase 2 class observa... |
|  | `WI-3423` | P3 | resolved | resolved | ok | Run ruff check --fix + ruff format on platform_tests/ to resolve 66 lint violations (S363 Phase 2 CI gate) |
|  | `WI-3428` | P3 | backlogged | open | gap | Commit regenerated dev-environment inventory artifacts (2026-05-28 hygiene) |
|  | `WI-3456` | P3 | backlogged | open | gap | Flaky: Claude SessionStart dispatcher tests degrade on startup-service freshness-contract validation under timing pre... |
|  | `WI-3460` | P3 | backlogged | open | gap | Pre-existing failures in platform_tests/hooks/test_workstream_focus.py: stale relay-cache fixtures + counterpart-stat... |
|  | `WI-3463` | P3 | backlogged | open | ok | Bridge gate detectors require magic content phrases, surfacing failures late |
|  | `WI-3473` | P3 | resolved | resolved | gap | Catch ruff format --check before VERIFIED (pre-file gate, not just ruff check) |
|  | `WI-3482` | P3 | backlogged | open | gap | Lint/doctor check: flag bridge proposals targeting .git/hooks when core.hooksPath differs |
|  | `WI-3486` | P3 | backlogged | open | ok | Startup relay cache 30-min TTL has no in-window self-heal when inner freshness contract fails |
|  | `WI-3487` | P3 | backlogged | open | ok | system-interface-map human companion docs/gtkb-systems-and-tools.md is missing (was VERIFIED-added 2026-05-06) |
|  | `WI-3489` | P3 | backlogged | open | ok | Dashboard SQLite not generated; gt status dashboard=UNKNOWN, dashboard reachability degraded at startup |
|  | `WI-3493` | P3 | backlogged | open | ok | Bash hook destructive-command detection: false positive on g-i-t r-m substring in scope text |
|  | `WI-3494` | P3 | backlogged | open | ok | Add --auto-create-pauth flag to gt backlog add for projects lacking PAUTH coverage |
|  | `WI-3495` | P3 | backlogged | open | ok | Auto-inject bridge proposal author/model audit metadata block (6 lines) in scaffold step |
|  | `WI-3496` | P3 | backlogged | open | ok | bridge-compliance-gate regex: accept markdown-bold variant or emit pattern in error message |
|  | `WI-3507` | P3 | resolved | resolved | ok | impl-start gate verification-heading tokens diverge from clause-preflight evidence acceptance |

### `PROJECT-GTKB-REQUIREMENTS-QUALITY-AUDIT` - GTKB-REQUIREMENTS-QUALITY-AUDIT

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3247` | P1 | backlogged | open | ok | Critical quality and consistency audit of early-project requirements |

### `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH

- Status/rank: `active` / `None`
- purpose: Implement role/status orthogonality with single-ACTIVE-per-role dispatch (DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH). Umbrella for slices 1-7.
- target: Resolver, doctor, and narrative honor (role, status==active) dispatch filtering; multiple same-role harnesses coexist with exactly one active per role.
- scope: Slice 1 ADR/DCL (VERIFIED); Slice 2 resolver+attribution; Slice 3 GOV updates; Slice 4 narrative; Slice 5 packet generators; Slice 6 doctor; Slice 7 registry reconciliation.
- Members: active=5, open=2, terminal=3, inactive=0, child_projects=0, active_auths=4, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3509` | P1 | resolved | resolved | ok | Slice 2: status-aware dispatch resolver + active-PB attribution (role/status orthogonality) |
|  | `WI-3511` | P1 | resolved | resolved | ok | Slice-2 landing: suspend antigravity (C) to restore single-active-PB dispatch |
|  | `WI-3512` | P2 | backlogged | open | ok | Decouple harness_ops role-retention from active status (honor ADR-ROLE-STATUS-ORTHOGONALITY-001 section 9) |
|  | `WI-4213` | P2 | resolved | resolved | ok | Formalize active-status capability gate: 'active' requires bridge-event reception (PB-role-without-event-surface is i... |
|  | `WI-4214` | P2 | backlogged | open | ok | Retire orphaned role-assignments.json legacy mirror (multi-slice) |

### `PROJECT-GTKB-RULE-FILE-CURRENCY-AUDIT-001` - GTKB-RULE-FILE-CURRENCY-AUDIT-001

- Status/rank: `active` / `None`
- purpose: Audit and remediate stale path/CLI references in CLAUDE.md, AGENTS.md, and `.claude/rules/`; add doctor check for ongoing drift.
- scope: Scope is documentation currency: paths, CLI invocations, DB locations, configuration locations. Out of scope: governance content review.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3288` | P2 | resolved | resolved | ok | Audit and remediate stale path/CLI references in CLAUDE.md, AGENTS.md, and .claude/rules/ |

### `PROJECT-GTKB-SKILL-MODERNIZATION` - PROJECT-GTKB-SKILL-MODERNIZATION

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=4, open=4, terminal=0, inactive=0, child_projects=0, active_auths=2, active_links=0
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3391` | P2 | backlogged | open | gap | Skill modernization umbrella: thin-wrapper migration for kb-* skills + send-review deprecation + skill-health checker... |
|  | `WI-3451` | P2 | backlogged | open | ok | Skill modernization Slice 0: skill-health static checker (scripts/check_skill_health.py) |
|  | `WI-3455` | P2 | backlogged | open | ok | Skill modernization Slice 3: migrate kb-work-item to a gt CLI thin wrapper (GOV-12/13 WI+test+phase verb) |
|  | `WI-3459` | P2 | backlogged | open | gap | Slice 3b: kb-work-item skill rewrite + Codex/Antigravity adapter regen + registry parity (clean-tree follow-on) |

### `PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS` - GTKB-SOURCE-OF-TRUTH-FRESHNESS

- Status/rank: `active` / `None`
- purpose: Operationalize the owner principle that all information about the state of a source-of-truth must be a fresh read of the source, not a cached copy, snapshot, or summary.
- target: Reporting/state surfaces read canonical source-of-truth (tables/views) freshly; cached/snapshot surfaces are inventoried and either justified with a declared TTL or converted to fresh-read.
- scope: Reconsider only if latency or overload become problems (owner: not at this time).
- Members: active=12, open=10, terminal=2, inactive=0, child_projects=0, active_auths=0, active_links=1

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-4227` | P1 | resolved | resolved | ok | Bidirectional bridge history and backlog terminal-state reconciliation audit |
|  | `WI-4228` | P1 | backlogged | open | ok | Correction packet: stale backlog status for VERIFIED bridge metadata, P1/P2 first |
|  | `WI-4229` | P1 | backlogged | open | ok | Correction packet: VERIFIED bridge threads whose associated backlog items remain non-terminal |
|  | `WI-3501` | P2 | backlogged | open | ok | Formalize the source-of-truth-freshness principle as governance (DA decision + GOV + DCL) |
|  | `WI-3502` | P2 | backlogged | open | gap | Audit all cached/snapshot surfaces against the fresh-read source-of-truth principle |
|  | `WI-3503` | P2 | backlogged | open | ok | Referential-integrity gap: active work-item memberships pointing at retired projects (strict vs loose orphan count; r... |
|  | `WI-4230` | P2 | backlogged | open | ok | Correction packet: missing or incorrect related_bridge_threads linkage |
|  | `WI-4231` | P2 | backlogged | open | ok | Evidence review packet: terminal backlog rows without cited completion evidence |
|  | `WI-4232` | P2 | backlogged | open | ok | Bridge INDEX drift triage for VERIFIED on-disk history absent from live INDEX |
|  | `WI-4233` | P2 | backlogged | open | ok | Bridge history triage for VERIFIED threads without exact backlog match |
|  | `WI-4234` | P2 | backlogged | open | ok | Reusable sanity gate for bridge/backlog terminal-state reconciliation |
|  | `WI-3506` | P3 | resolved | resolved | ok | Rule-vs-MemBase drift: phantom GOV-CHAT-DERIVED-SPEC-APPROVAL-001 cited in 3 narrative rule files |

### `PROJECT-GTKB-SPEC-TEST-QUALITY` - GTKB-SPEC-TEST-QUALITY

- Status/rank: `active` / `None`
- purpose: Spec hygiene + test/assertion quality + clause enforcement quality.
- target: All open specs have spec-derived tests; assertion quality meets GOV-18; audit scripts handle full status taxonomy.
- Members: active=4, open=4, terminal=0, inactive=0, child_projects=0, active_auths=1, active_links=4

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` |  | backlogged | open | gap | GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001 (Apply ADR/DCL logic as clause-level review tests) |
|  | `WI-3247` | P1 | backlogged | open | ok | Critical quality and consistency audit of early-project requirements |
|  | `WI-3276` | P2 | created | open | ok | audit_standing_backlog_sources.py: WITHDRAWN not in actionable-status exclusion |
|  | `WI-3278` | P3 | created | open | gap | memory/work_list.md GTKB-GOV-010: correct stale tests/scripts path -> platform_tests/scripts |

### `PROJECT-GTKB-V1-RELEASE-STRATEGY-001` - GTKB-V1-RELEASE-STRATEGY-001

- Status/rank: `active` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=9, open=9, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3404` | P0 | backlogged | open | ok | Define v1.0 acceptance criteria (sole anti-perpetual-rc1 checkpoint per §9.2) |
|  | `WI-3401` | P1 | backlogged | open | ok | Scope §10.1 mechanical-enforcement gate bridge proposal (Hybrid Variant prereq) |
|  | `WI-3402` | P1 | backlogged | open | ok | Scope §10.2 spec-corpus distillation bridge proposal (in-tree specs/ initially) |
|  | `WI-3403` | P1 | backlogged | open | ok | Scope Docker isolation-validator test (release-gate validator, promoted from Antigravity Finding 1) |
|  | `WI-3400` | P2 | backlogged | open | ok | Capture Antigravity 2026-05-27 V1-RELEASE-STRATEGY-REVIEW advisory disposition (peer-solution-advisory-loop) |
|  | `WI-3405` | P2 | backlogged | open | ok | Revise gtkb-agent-red-reference-adopter-framing-restoration to -003 REVISED (ADR-ISOLATION-APPLICATION-PLACEMENT-001... |
|  | `WI-3406` | P2 | backlogged | open | ok | Scope envelope-convention specs + reconsidered wrap-procedure (deferred to later session) |
|  | `WI-3407` | P2 | backlogged | open | ok | Create decision-capture composite DELIB workflow skill (per owner agreement) |
|  | `WI-3395` | P3 | backlogged | open | gap | ChromaDB semantic-history backfill design for v1.0 identifier-reset cut (Finding 3 from V1 Release Strategy LO review) |

### `PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE` - GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE

- Status/rank: `active` / `None`
- purpose: Provide Windows-native governance preflight surfaces so Codex and Git can run hook-equivalent commit and push checks without Bash/WSL-only manual equivalents.
- target: Agents can call canonical gt preflight commands, Windows Git hooks can delegate to native wrappers, push-readiness can be diagnosed read-only, and failures produce durable evidence for owner-reviewed bypass rather tha...
- scope: Backlog capture only. Credential changes remain owner-only. Implementation still requires bridge proposal review, GO, implementation report, and Loyal Opposition verification.
- notes: Approved by Mike on 2026-06-02. Decisions: DELIB-20260602-WINDOWS-PREFLIGHT-INTERFACE-BOTH, DELIB-20260602-WINDOWS-PREFLIGHT-PUSH-DIAGNOSTICS, DELIB-20260602-WINDOWS-PREFLIGHT-EVIDENCE-BYPASS, DELIB-20260602-WINDOWS-P...
- Members: active=4, open=4, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-4255` | P2 | backlogged | open | ok | Windows governance preflight evidence model |
| 2 | `WI-4256` | P2 | backlogged | open | ok | Windows commit governance preflight command and wrapper |
| 3 | `WI-4257` | P2 | backlogged | open | ok | Windows push governance preflight command and wrapper |
| 4 | `WI-4258` | P2 | backlogged | open | ok | Read-only push readiness diagnostic |

### `PROJECT-HARNESS-REGISTRY-REFACTOR` - Harness Registry Refactor

- Status/rank: `active` / `None`
- Parent: `PROJECT-ANTIGRAVITY-INTEGRATION`
- purpose: Harnesses table, generated hot-path projection, gt harness CLI, 4-state lifecycle FSM, phased reader migration, ADR-SINGLE-HARNESS-OPERATING-MODE-001 new version, and data-driven dispatch.
- Members: active=8, open=0, terminal=8, inactive=0, child_projects=0, active_auths=1, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-3337` | P1 | completed | verified | gap | harnesses table schema and append-only versioning |
| 2 | `WI-3338` | P1 | completed | verified | gap | Generated hot-path harness-registry projection and generator |
| 3 | `WI-3339` | P1 | completed | verified | gap | Four-state harness lifecycle FSM and transition validators |
| 4 | `WI-3340` | P1 | completed | verified | gap | gt harness CLI command group |
| 5 | `WI-3341` | P1 | completed | verified | ok | Role portability and single-prime-builder invariant enforcement |
| 6 | `WI-3342` | P1 | resolved | resolved | ok | Phased reader migration from JSON to projection |
| 7 | `WI-3343` | P1 | resolved | resolved | ok | Extend ADR-SINGLE-HARNESS-OPERATING-MODE-001 for the harness registry architecture |
| 8 | `WI-3344` | P1 | completed | verified | gap | Data-driven cross-harness dispatch from invocation_surfaces |

### `PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001` - LO Advisory Owner-Grilling Gate

- Status/rank: `active` / `None`
- purpose: Implement GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001 and DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 across 3 slices: rule+template, skills+checklists, lint.
- target: Owner-grilling gate is mechanically enforced on adopt/adapt LO advisories; warning phase initially, blocking phase via separate owner approval.
- scope: Touches .claude/rules/peer-solution-advisory-loop.md; CODEX-REVIEW-OPERATING-CONTRACT.md; CODEX-REVIEW-CHECKLISTS.md; .codex/skills/codex-report/SKILL.md; .codex/skills/lo-opportunity-radar/SKILL.md; .codex/skills/loy...
- Members: active=3, open=3, terminal=0, inactive=0, child_projects=0, active_auths=1, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3444` | P2 | backlogged | open | ok | Slice 1: Amend peer-solution-advisory-loop.md with Owner-Grilling Gate subsection + advisory template skeleton |
|  | `WI-3445` | P2 | backlogged | open | ok | Slice 2: Update CODEX-REVIEW contracts + 3 LO-advisory-emitting skills |
|  | `WI-3446` | P2 | backlogged | open | ok | Slice 3: Create scripts/advisory_grilling_gate_lint.py + Stop-mode hook + tests |

### `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001` - GTKB-BRIDGE-WORK-FRONT-DRAIN-001

- Status/rank: `retired` / `1`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=8, open=0, terminal=8, inactive=0, child_projects=2, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-3249` | P0 | resolved | resolved | ok | Implement gtkb-loyal-opposition-startup-symmetry GO@008 |
| 2 | `WI-3250` | P0 | resolved | resolved | ok | Implement gtkb-canonical-init-keyword-syntax GO@008 |
| 3 | `WI-3251` | P1 | resolved | resolved | gap | File proposal for bridge advisory_report message type (response to LO advisory) |
| 4 | `WI-3252` | P0 | resolved | resolved | gap | Revise gtkb-scaffold-upgrade-tier-a (Codex NO-GO@002, F1-F5) |
| 5 | `WI-3253` | P1 | resolved | resolved | gap | Revise gtkb-role-session-lifecycle-simplification (Codex NO-GO@002) |
| 6 | `WI-3254` | P1 | resolved | resolved | ok | Revise gtkb-session-start-formalization (Codex NO-GO@002, depends on WI-3250) |
| 7 | `WI-3255` | P1 | resolved | resolved | ok | Revise gtkb-single-harness-bridge-dispatcher-001 (Codex NO-GO@002) |
| 8 | `WI-3256` | P2 | resolved | resolved | ok | Reconsider mechanism for gtkb-claude-code-bridge-status-thread-automation (Codex NO-GO@004; 4 NO-GOs across 4 differe... |

### `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001-WAVE-1-DRAINABLE` - Wave 1 - Drainable

- Status/rank: `retired` / `1`
- Parent: `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=4, open=0, terminal=4, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `WI-3249` | P0 | resolved | resolved | ok | Implement gtkb-loyal-opposition-startup-symmetry GO@008 |
| 2 | `WI-3250` | P0 | resolved | resolved | ok | Implement gtkb-canonical-init-keyword-syntax GO@008 |
| 3 | `WI-3251` | P1 | resolved | resolved | gap | File proposal for bridge advisory_report message type (response to LO advisory) |
| 4 | `WI-3252` | P0 | resolved | resolved | gap | Revise gtkb-scaffold-upgrade-tier-a (Codex NO-GO@002, F1-F5) |

### `PROJECT-GTKB-DORA-001B` - GTKB-DORA-001b

- Status/rank: `retired` / `1`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=1, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `GTKB-DORA-001b` |  | resolved | verified | ok | GTKB-DORA-001b Track 1 |

### `PROJECT-GTKB-DORA-001B-TRACK-1` - Track 1

- Status/rank: `retired` / `1`
- Parent: `PROJECT-GTKB-DORA-001B`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 1 | `GTKB-DORA-001b` |  | resolved | verified | ok | GTKB-DORA-001b Track 1 |

### `PROJECT-GTKB-ISOLATION-016` - GTKB-ISOLATION-016

- Status/rank: `retired` / `2`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 2 | `GTKB-ISOLATION-016` |  | resolved | verified | gap | GTKB-ISOLATION-016 |

### `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001-WAVE-2-CARRY-OVER-NO-GO-TRIAGE` - Wave 2 - Carry-over NO-GO triage

- Status/rank: `retired` / `5`
- Parent: `PROJECT-GTKB-BRIDGE-WORK-FRONT-DRAIN-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=4, open=0, terminal=4, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 5 | `WI-3253` | P1 | resolved | resolved | gap | Revise gtkb-role-session-lifecycle-simplification (Codex NO-GO@002) |
| 6 | `WI-3254` | P1 | resolved | resolved | ok | Revise gtkb-session-start-formalization (Codex NO-GO@002, depends on WI-3250) |
| 7 | `WI-3255` | P1 | resolved | resolved | ok | Revise gtkb-single-harness-bridge-dispatcher-001 (Codex NO-GO@002) |
| 8 | `WI-3256` | P2 | resolved | resolved | ok | Reconsider mechanism for gtkb-claude-code-bridge-status-thread-automation (Codex NO-GO@004; 4 NO-GOs across 4 differe... |

### `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICE-1` - Slice 1

- Status/rank: `retired` / `5`
- Parent: `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 5 | `GTKB-GOV-PROPOSAL-STANDARDS` |  | resolved | resolved | gap | GTKB-GOV-PROPOSAL-STANDARDS Slice 1 |

### `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-ARTIFACT-RECORDING` - Artifact recording

- Status/rank: `retired` / `7`
- Parent: `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
- scope: Backfilled from current_work_items.subproject_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 7 | `WI-3263` | P1 | resolved | resolved | ok | Advance GTKB-ARTIFACT-RECORDER-CLI: file the scoping bridge proposal per its Next step field |

### `PROJECT-GTKB-GOV-CODE-QUALITY-BASELINE` - GTKB-GOV-CODE-QUALITY-BASELINE

- Status/rank: `retired` / `7`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 7 | `GTKB-GOV-CODE-QUALITY-BASELINE` |  | resolved | resolved | gap | GTKB-GOV-CODE-QUALITY-BASELINE |

### `PROJECT-GTKB-STARTUP-ENHANCEMENTS` - GTKB-STARTUP-ENHANCEMENTS

- Status/rank: `retired` / `9`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=3, open=1, terminal=2, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 9 | `GTKB-STARTUP-ENHANCEMENTS` | P1 | resolved | resolved | ok | GTKB-STARTUP-ENHANCEMENTS |
|  | `WI-3283` | P2 | resolved | resolved | ok | Startup-disclosure backlog counts shall use a single documented filter rule |
|  | `WI-3326` | P3 | created | open | ok | Resolve phantom spec citations in SessionStart hook payload (ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001, DCL-SESSION... |

### `PROJECT-GTKB-ARTIFACT-RECORDER-CLI` - GTKB-ARTIFACT-RECORDER-CLI

- Status/rank: `retired` / `15`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=4
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 15 | `GTKB-ARTIFACT-RECORDER-CLI` |  | resolved | resolved | ok | GTKB-ARTIFACT-RECORDER-CLI |

### `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` - GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY

- Status/rank: `retired` / `19`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=1
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
| 19 | `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` |  | resolved | retired | gap | GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY |

### `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` - GTKB Governance Chain Mechanical Enforcement

- Status/rank: `retired` / `None`
- purpose: Mechanical enforcement of the spec -> project -> work item -> bridge chain per owner directive 2026-05-14 (S350+).
- target: All 5 newly-inserted GOV/DCL specs have backing hook/script enforcement; the chain rejects work-item bridge dispatch lacking project authorization, project authorization lacking spec linkage, and spec amendment lackin...
- scope: In-scope: GT-KB platform governance hooks/scripts/CLI. Out-of-scope: adopter application work; agent-side or harness-side enforcement.
- Members: active=6, open=6, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3312` | P1 | created | open | gap | Add spec-linkage requirement to gt projects authorize |
|  | `WI-3313` | P1 | created | open | gap | Add amendment-approval gate to project_authorizations linked_specs mutations |
|  | `WI-3314` | P1 | created | open | gap | Add Project Authorization/Project/Work Item metadata requirement to bridge-compliance-gate |
|  | `WI-3315` | P1 | created | open | gap | Add WI-project membership check to bridge-compliance-gate |
|  | `WI-3316` | P2 | created | open | gap | Build VERIFIED -> COMPLETED AUQ trigger and project retirement flow |
|  | `WI-3317` | P3 | created | open | gap | Fix MUTATING_COMMAND_RE format-spec false-positive in implementation-start-gate |

### `PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION` - Commit-scope bundling detection

- Status/rank: `retired` / `None`
- Description: (missing purpose, target outcome, scope note, and notes)
- Members: active=0, open=0, terminal=0, inactive=1, child_projects=0, active_auths=0, active_links=1
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`
- Work items: none with active current membership.

### `PROJECT-GTKB-BACKLOG-CAPTURE-001` - GTKB-BACKLOG-CAPTURE-001

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=2, child_projects=2, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES` - Bridge Scheduler Lanes and Leases

- Status/rank: `retired` / `None`
- purpose: Replace the fixed DEFAULT_MAX_ITEMS=2 bridge dispatch cap with a lease-based worker scheduler (per-document leases, serialized bridge/INDEX.md writer, per-role concurrency, work-lane classification, aging/priority).
- target: Bridge work dispatched as parallel as correctness allows: artificial single-harness-lock serialization removed; necessary serialization (per-document leases, INDEX writer, governance lane) preserved.
- scope: Implements Slices 2-6 of the GO'd gtkb-bridge-scheduler-lanes-leases-slice-1-scoping plan. Each slice proceeds through the bridge protocol.
- Members: active=5, open=0, terminal=5, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3373` | P2 | resolved | resolved | ok | Bridge scheduler Slice 2: per-document lease registry |
|  | `WI-3374` | P2 | resolved | resolved | ok | Bridge scheduler Slice 3: serialized bridge/INDEX.md writer |
|  | `WI-3375` | P2 | resolved | resolved | ok | Bridge scheduler Slice 4: per-role dispatch concurrency limits |
|  | `WI-3376` | P3 | resolved | resolved | ok | Bridge scheduler Slice 5: work-lane classification |
|  | `WI-3377` | P3 | resolved | resolved | ok | Bridge scheduler Slice 6: aging and priority weighting |

### `PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS` - GTKB-BRIDGE-TOOLING-ENHANCEMENTS

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=3, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` - GTKB CLAUDE.md Scope Correction

- Status/rank: `retired` / `None`
- purpose: Implement the owner-approved CLAUDE.md scope clarification (Approach C split per Slice 1 GO; 18.I scope expansion + F1-F5 corrections per Slice 2 REVISED GO). Splits root CLAUDE.md into platform CLAUDE.md and applicat...
- target: Root CLAUDE.md is platform-scoped (<=300 lines per GOV-01); applications/Agent_Red/CLAUDE.md is application-scope authority; protected-artifact registry covers app-side narrative authority; doctor profile passes; all...
- scope: Implementation of Slice 2 governance design at bridge/gtkb-claude-md-scope-clarification-slice-2-003.md (Codex GO at -004). Does NOT include CLAUDE-REFERENCE.md content scope review (Slice 4), CLAUDE-ARCHITECTURE.md i...
- notes: Authorized via owner AUQ chain S364 2026-05-28: Approach C, 18.I scope expansion, F1 reframe to governance review, F4 registry expansion.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3438` | P1 | resolved | resolved | ok | Slice 3: Execute CLAUDE.md split + 18.I files migration to applications/Agent_Red/ |

### `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` - PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY

- Status/rank: `retired` / `None`
- purpose: Amend project-root-boundary.md with a bounded, doctor-enforced exception for external harness executable resolution (codex/claude/gemini), unblocking cross-harness dispatch including headless Gemini (WI-3349).
- scope: Protected-rule amendment + doctor check + .env.local-configured external-tool location shape. Consumer WI-3349 resumes after this lands.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3434` | P1 | resolved | resolved | ok | Amend project-root-boundary.md with bounded external-harness-executable resolution exception + doctor check |

### `PROJECT-GTKB-GOVERNANCE-CORRECTION-S358` - GTKB-GOVERNANCE-CORRECTION-S358

- Status/rank: `retired` / `None`
- Description: (missing purpose, target outcome, scope note, and notes)
- Members: active=0, open=0, terminal=0, inactive=6, child_projects=0, active_auths=0, active_links=6
- Project description check: `description relies on notes/links but lacks explicit purpose and outcome`
- Work items: none with active current membership.

### `PROJECT-GTKB-LO-OPPORTUNITY-RADAR` - Loyal Opposition opportunity-radar

- Status/rank: `retired` / `None`
- purpose: Deliver the Loyal Opposition opportunity-radar capability specified by SPEC-LO-OPPORTUNITY-RADAR-001.
- scope: First authorized slice is the lo-opportunity-radar skill; deferred scanner/CLI/hooks (advisory Findings 2-4) would be future slices under separate authorization.
- Members: active=1, open=0, terminal=1, inactive=0, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose or target_outcome counterpart`

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3324` | medium | resolved | resolved | ok | Route LO advisory: INSIGHTS-2026-05-15-10-58-lo-opportunity-radar.md |

### `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE` - GTKB-MEMBASE-EFFECTIVE-USE

- Status/rank: `retired` / `None`
- purpose: MemBase usage patterns, provenance anchors, MCP current-version surfaces.
- target: MemBase is the canonical, queryable, provenance-bearing source-of-truth for governed knowledge.
- Members: active=0, open=0, terminal=0, inactive=3, child_projects=0, active_auths=0, active_links=3
- Work items: none with active current membership.

### `PROJECT-GTKB-METHODOLOGY-AI-MATURITY` - GTKB-METHODOLOGY-AI-MATURITY

- Status/rank: `retired` / `None`
- purpose: AI-assisted delivery methodology + artifact-recorder umbrella + MASS.
- target: GT-KB exposes a documented maturity model for AI-assisted delivery practice.
- Members: active=0, open=0, terminal=0, inactive=2, child_projects=0, active_auths=0, active_links=2
- Work items: none with active current membership.

### `PROJECT-GTKB-PUSH-GATE` - PROJECT-GTKB-PUSH-GATE

- Status/rank: `retired` / `None`
- purpose: Comprehensive deterministic CI gate that mechanically blocks pushes to GitHub when any artifact fails any tracked check (lint, type, hardcoded-externals AST, tests, architecture assertions, security, governance integr...
- target: Push gate active on develop + main branches; any defect class blocks until fixed; gate logic lives in repo with bridge-protocol governance for changes.
- scope: Spans Slice 0 (governance scoping) through Slice 11 (branch protection enable). Includes new scripts/push_gate.py CLI, content-addressed cache substrate, hardcoded-externals AST checker, integration with existing gt a...
- notes: Authorized 2026-05-28 by owner direction in S365 chat: 'This is a very important enhancement of GT-KB. Please proceed in order.' Owner resolved three design tensions: (1) no amnesty - all errors must be found and fixe...
- Members: active=1, open=1, terminal=0, inactive=0, child_projects=0, active_auths=0, active_links=0

| Order | Work item | Priority | Stage | Status | Realness | Title |
|---:|---|---|---|---|---|---|
|  | `WI-3416` | P1 | backlogged | open | gap | PROJECT-GTKB-PUSH-GATE master: comprehensive deterministic CI gate Slice 0-11 design + implementation |

### `PROJECT-GTKB-SECURITY-PRIVACY` - GTKB-SECURITY-PRIVACY

- Status/rank: `retired` / `None`
- purpose: Zero-knowledge architecture + POR spec hygiene for security/privacy concerns.
- target: Security/privacy concerns have governance coverage; ZK architecture proposed; POR spec hygiene complete.
- Members: active=0, open=0, terminal=0, inactive=2, child_projects=0, active_auths=0, active_links=2
- Work items: none with active current membership.

### `PROJECT-GTKB-SESSION-LIFECYCLE-UX` - GTKB-SESSION-LIFECYCLE-UX

- Status/rank: `retired` / `None`
- purpose: Startup, wrap-up, role-presentation per-session owner-facing surface.
- target: Each session start/end loop reduces owner cognitive load via consistent, governed surfaces.
- Members: active=0, open=0, terminal=0, inactive=4, child_projects=0, active_auths=0, active_links=4
- Work items: none with active current membership.

### `PROJECT-PROJECT-ANTIGRAVITY-INTEGRATION` - PROJECT-ANTIGRAVITY-INTEGRATION

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=1, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` - PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=3, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES` - PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=5, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` - PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=1, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-DETERMINISTIC-SERVICES-001` - PROJECT-GTKB-DETERMINISTIC-SERVICES-001

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=2, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-ENV-SOT-TOPOLOGY` - PROJECT-GTKB-ENV-SOT-TOPOLOGY

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=2, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` - PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=1, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-PUSH-GATE` - PROJECT-GTKB-PUSH-GATE

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=1, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-RELIABILITY-FIXES` - PROJECT-GTKB-RELIABILITY-FIXES

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=32, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

### `PROJECT-PROJECT-GTKB-SKILL-MODERNIZATION` - PROJECT-GTKB-SKILL-MODERNIZATION

- Status/rank: `retired` / `None`
- scope: Backfilled from current_work_items.project_name compatibility field.
- Members: active=0, open=0, terminal=0, inactive=1, child_projects=0, active_auths=0, active_links=0
- Project description check: `missing purpose/target_outcome and no durable descriptive note`
- Work items: none with active current membership.

## Unprojected Non-Terminal Work Items

This section lists the first 100 of 712 non-terminal work items that are not attached to active first-class project memberships. The full list is in the JSON evidence packet.

| Priority | Work item | Stage | Status | Compatibility project | Title |
|---|---|---|---|---|---|
| high | `WI-4150` | created | open |  | Route LO advisory: INSIGHTS-2026-04-11-00-07-S279-LIFECYCLE-METRICS-PROPOSAL-REVIEW.md |
| high | `WI-4151` | created | open |  | Route LO advisory: INSIGHTS-2026-04-11-00-54-S279-POST-IMPLEMENTATION-REVIEW.md |
| high | `WI-4152` | created | open |  | Route LO advisory: INSIGHTS-2026-04-11-01-36-S279-STREAM-B-REPAIR-REVIEW.md |
| high | `WI-4153` | created | open |  | Route LO advisory: INSIGHTS-2026-04-11-01-39-S279-9739-REPAIR-ADDENDUM.md |
| high | `WI-4193` | created | open |  | Route LO advisory: INSIGHTS-2026-04-22-13-09-BRIDGE-SCAN-ROLE-AUTHORITY-GOV-FAILURE.md |
| medium | `WI-3603` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-14-43.md |
| P2 | `WI-3510` | backlogged | open |  | Reconcile divergent included_work_item_ids semantics between Write-time bridge-compliance gate and impl-start authori... |
| low | `WI-3514` | created | open |  | Route LO advisory: INSIGHTS-2026-03-17-15-26.md |
| low | `WI-3515` | created | open |  | Route LO advisory: INSIGHTS-2026-03-17-15-38.md |
| low | `WI-3516` | created | open |  | Route LO advisory: INSIGHTS-2026-03-17-16-47.md |
| low | `WI-3517` | created | open |  | Route LO advisory: INSIGHTS-2026-03-17-18-09.md |
| low | `WI-3518` | created | open |  | Route LO advisory: INSIGHTS-2026-03-17-21-11.md |
| low | `WI-3519` | created | open |  | Route LO advisory: INSIGHTS-2026-03-24-15-11.md |
| low | `WI-3520` | created | open |  | Route LO advisory: INSIGHTS-2026-03-24-16-29.md |
| low | `WI-3521` | created | open |  | Route LO advisory: INSIGHTS-2026-03-24-17-12.md |
| low | `WI-3522` | created | open |  | Route LO advisory: INSIGHTS-2026-03-24-19-29.md |
| low | `WI-3523` | created | open |  | Route LO advisory: INSIGHTS-2026-03-24-22-19.md |
| low | `WI-3524` | created | open |  | Route LO advisory: INSIGHTS-2026-03-24-23-38.md |
| low | `WI-3525` | created | open |  | Route LO advisory: INSIGHTS-2026-03-25-00-27.md |
| low | `WI-3526` | created | open |  | Route LO advisory: INSIGHTS-2026-03-25-01-24.md |
| low | `WI-3527` | created | open |  | Route LO advisory: INSIGHTS-2026-03-25-01-38.md |
| low | `WI-3528` | created | open |  | Route LO advisory: INSIGHTS-2026-03-25-07-24.md |
| low | `WI-3529` | created | open |  | Route LO advisory: INSIGHTS-2026-03-25-18-12.md |
| low | `WI-3530` | created | open |  | Route LO advisory: INSIGHTS-2026-03-25-20-27.md |
| low | `WI-3531` | created | open |  | Route LO advisory: INSIGHTS-2026-03-25-21-07.md |
| low | `WI-3532` | created | open |  | Route LO advisory: INSIGHTS-2026-03-26-06-53.md |
| low | `WI-3533` | created | open |  | Route LO advisory: INSIGHTS-2026-03-26-07-20.md |
| low | `WI-3534` | created | open |  | Route LO advisory: INSIGHTS-2026-03-26-07-48.md |
| low | `WI-3535` | created | open |  | Route LO advisory: INSIGHTS-2026-03-26-08-38.md |
| low | `WI-3536` | created | open |  | Route LO advisory: INSIGHTS-2026-03-26-09-03.md |
| low | `WI-3537` | created | open |  | Route LO advisory: INSIGHTS-2026-03-26-10-31.md |
| low | `WI-3538` | created | open |  | Route LO advisory: INSIGHTS-2026-03-26-18-15.md |
| low | `WI-3539` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-01-00.md |
| low | `WI-3540` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-02-14.md |
| low | `WI-3541` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-02-51.md |
| low | `WI-3542` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-07-52.md |
| low | `WI-3543` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-08-31.md |
| low | `WI-3544` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-09-37.md |
| low | `WI-3545` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-09-48.md |
| low | `WI-3546` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-09-52.md |
| low | `WI-3547` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-10-52.md |
| low | `WI-3548` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-11-16.md |
| low | `WI-3549` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-11-29.md |
| low | `WI-3550` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-14-10.md |
| low | `WI-3551` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-14-53.md |
| low | `WI-3552` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-16-52.md |
| low | `WI-3553` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-17-14.md |
| low | `WI-3554` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-17-31-PHASE2-REREVIEW.md |
| low | `WI-3555` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-17-31.md |
| low | `WI-3556` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-17-35.md |
| low | `WI-3557` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-18-10-PHASE2-FINAL-REREVIEW.md |
| low | `WI-3558` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-19-34-PHASE3-ADVISORY.md |
| low | `WI-3559` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-19-37.md |
| low | `WI-3560` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-19-54-PHASE3-V2-ADVISORY.md |
| low | `WI-3561` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-20-00-BRIDGE-MECHANISM-HARDENING.md |
| low | `WI-3562` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-20-30-PHASE3-V3-ADVISORY.md |
| low | `WI-3563` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-21-25-PHASE3-V4-ADVISORY.md |
| low | `WI-3564` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-22-10-PHASE3-V5-ADVISORY.md |
| low | `WI-3565` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-22-11-PHASE3-V5-ADVISORY.md |
| low | `WI-3566` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-22-14-PHASE3-V6-ADVISORY.md |
| low | `WI-3567` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-22-52-PHASE3-COMPLETION-ADVISORY.md |
| low | `WI-3568` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-22-52-PHASE3-COMPLETION-REVIEW.md |
| low | `WI-3569` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-23-01-PHASE3-COMPLETION-REREVIEW.md |
| low | `WI-3570` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-23-02-PHASE3-REREVIEW.md |
| low | `WI-3571` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-23-20-PHASE3-REREVIEW-2.md |
| low | `WI-3572` | created | open |  | Route LO advisory: INSIGHTS-2026-03-27-23-21-PHASE3-REREVIEW-2.md |
| low | `WI-3573` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-00-21-SLIM-DIAGNOSTIC.md |
| low | `WI-3574` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-00-36-RG-STREAM-BYPASS-REVIEW.md |
| low | `WI-3575` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-00-50-SLIM-DOC-EVALUATION.md |
| low | `WI-3576` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-00-SLIM-UPGRADE-COMPARISON.md |
| low | `WI-3577` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-10-PER-INTERFACE-TRANSPORT-POLICY.md |
| low | `WI-3578` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-20-PHASE3-RG-PLACEMENT-RECOMMENDATION.md |
| low | `WI-3579` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-33-PHASE3-CLOSURE-CHECK.md |
| low | `WI-3580` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-40-PHASE3-COMPLETION-FINAL.md |
| low | `WI-3581` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-46-PHASE4-PLAN-REVIEW.md |
| low | `WI-3582` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-48-PHASE4-REVISED-PLAN-REVIEW.md |
| low | `WI-3583` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-01-55-PHASE4-PLAN-ADVISORY.md |
| low | `WI-3584` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-05-PHASE4-PLAN-REREVIEW.md |
| low | `WI-3585` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-07-PHASE4-COMPLETION-CLOSURE-CHECK.md |
| low | `WI-3586` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-20-PHASE4-COMPLETION-REVIEW.md |
| low | `WI-3587` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-28-PHASE4-REREVIEW-CLOSURE.md |
| low | `WI-3588` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-30-PHASE4-COMPLETION-REREVIEW.md |
| low | `WI-3589` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-32-PHASE5-PLAN-REVIEW.md |
| low | `WI-3590` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-35-PHASE5-PLAN-ADVISORY.md |
| low | `WI-3591` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-38-PHASE5-PLAN-REREVIEW.md |
| low | `WI-3592` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-39-PHASE5-PLAN-VERIFICATION.md |
| low | `WI-3593` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-44-PHASE5-COMPLETION-REVIEW.md |
| low | `WI-3594` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-46-PHASE5-COMPLETION-REVIEW.md |
| low | `WI-3595` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-50-PHASE5-REREVIEW-2.md |
| low | `WI-3596` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-02-51-PHASE5-COMPLETION-REREVIEW.md |
| low | `WI-3597` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-07-25-SLIM-DIAGNOSTIC.md |
| low | `WI-3598` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-08-07-LIVE-STOREFRONT-CHAT-VERIFICATION.md |
| low | `WI-3599` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-08-09-READINESS-GATE-LIVE-CHAT.md |
| low | `WI-3600` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-08-41-UI-REPAIR-ACCEPTANCE-CRITERIA.md |
| low | `WI-3601` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-08-43-S227-UI-PLAN-ADVISORY.md |
| low | `WI-3602` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-08-44-S227-PLAN-ADVISORY-REVIEW.md |
| low | `WI-3604` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-15-08-S228-ADVISORY-REVIEW.md |
| low | `WI-3605` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-15-22-S227-POST-IMPLEMENTATION-VERIFICATION.md |
| low | `WI-3606` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-15-42-S227-REVERIFICATION.md |
| low | `WI-3607` | created | open |  | Route LO advisory: INSIGHTS-2026-03-28-16-07-S227-TIER34-CONTINUATION-VERIFICATION.md |

## Correction Approach

1. Respect the active dependency: clear or explicitly park `PROJECT-GTKB-ISOLATION-PHASE-9-PRODUCTIZATION` before substantive `PROJECT-GTKB-ROLE-ENHANCEMENT` work.
2. Reconcile project membership for non-terminal P0/P1/P2 work items before broad low-priority advisory cleanup.
3. Update purpose and target outcome on high-ranked active projects whose descriptions are still backfill-shaped.
4. Backfill evidence links only where the work item is active and likely to be executed; terminal and low-priority gaps should be handled by retirement or batched hygiene, not manual archaeology.
5. Run project completion/retirement checks for active projects whose active member work is already entirely terminal.

## Open Decisions Required From Owner

None for this advisory report. Follow-on correction work can be proposed without a new owner decision; actual bulk MemBase mutation should still use the governed bridge/dry-run path.

## Verification

- Generated by read-only SQLite extraction from `groundtruth.db`; no MemBase rows were mutated.
- JSON evidence packet written at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/backlog-progress-report-20260602T233857Z.json`.
- Report intentionally does not review or verify itself; this session only created the advisory artifact.
