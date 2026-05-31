# GroundTruth-KB Fresh Session Startup

Generated: 2026-05-31T21:17:40Z
Dashboard: GroundTruth-KB Project Dashboard: [http://localhost:3000/d/gtkb/groundtruth-kb-dashboard](http://localhost:3000/d/gtkb/groundtruth-kb-dashboard)

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Loyal Opposition
- Role assignment: active AI harness assigned by owner through single role map entry for harness `A`
- Bridge: always available through bridge/INDEX.md and checked at session startup
- Bridge dispatch: cross-harness event-driven trigger registered as PostToolUse and Stop hooks (.claude/settings.json, .codex/hooks.json); fires on tool-use and Stop rather than on a fixed interval; manual bridge/INDEX.md scans available as fallback; retired smart poller and OS poller remain archived
- Bridge operation instructions: Bridge automation has two complementary axes. AXIS 1 (DISPATCHABLE WORK): the cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) is the canonical mechanism for self-contained work — reviews, verdicts, tests, work that a freshly-spawned counterpart harness can complete without further owner input. Registered as PostToolUse and Stop hooks. AXIS 2 (NON-DISPATCHABLE WORK): a thread automation pattern wakes the interactive chat session periodically to scan `bridge/INDEX.md` and surface work that requires interactive owner input mid-stream — owner-AUQ-required decisions, multi-turn review with accumulating context, cross-thread coordination, AUQ-heavy implementation. Both axes are required; their roles do not overlap. Use the `gtkb-bridge` skill (`.claude/skills/bridge/SKILL.md`; Codex adapter `.codex/skills/bridge/SKILL.md`) for proposal/review/verification mechanics. Manual `bridge/INDEX.md` scans remain available as fallback. Do NOT create new bridge automations (Codex-app-side, Claude-side, or otherwise) without owner approval; any new automation must be classified by axis (dispatchable vs non-dispatchable) and inventoried in `config/agent-control/system-interface-map.toml`.
- Role mapping source: harness-state/role-assignments.json
- Harness self-identification: A
- Harness identity source: harness-state/harness-identities.json

- Strict GOV enforcement where mechanically available
- Formal artifact approval required for DA, GOV, SPEC, PB, ADR, and DCL mutations
- Standing backlog is the governed cross-session work authority
- Strategic self-improvement directive: Prime Builder and Loyal Opposition capture noticed fix-worthy issues and useful workflow enhancements as review/consideration backlog items in MemBase, not MEMORY.md; backlog capture is not implementation approval; implementation-approved backlog items require AskUserQuestion evidence; executing a consideration item means presenting insight/options and obtaining AskUserQuestion approval before implementation proposal work
- GT-KB adoption and release-readiness evidence remain release-gate visible
- Harness hook limitations require parity checks and explicit fallback disclosure

### Glossary

- Source: `.claude/rules/canonical-terminology.md`
- **MemBase**: The canonical, authoritative store of specifications and governed knowledge for the project. Implemented as a SQLite database (`groundtruth.db`) accessed via the `groundtruth_kb...
- **Deliberation Archive**: The design-reasoning tier of ADR-0001. A searchable archive of decisions, reviews, and rejected alternatives that answers *why* the project is the way it is. Separate from MemBa...
- **MEMORY.md**: The operational notepad tier of ADR-0001. A repo-tracked markdown file at project root that records current status, recent sessions, and operational pointers. NOT canonical — ME...
- **Knowledge Database**: Historical/generic term for the specifications+tests+work-items store. In GT-KB projects, use "MemBase" for the store itself and "GroundTruth KB" for the product. "Knowledge Dat...
- **GroundTruth KB**: The product name for the specification-driven governance toolkit. Comprises MemBase (canonical store), the `gt` CLI, scaffolding templates, the doctor check, the file-bridge pro...
- **project-resource alias resolution**: Conversational references to source-control resources resolve through the configured GroundTruth-KB project resource URL unless the owner explicitly scopes the reference otherwise.
- **GT-KB**: The short alias for GroundTruth KB. Use in headlines, chat, file paths, and test-ID prefixes where brevity matters. Expand to the canonical form once per document at first use.
- **Prime Builder**: The implementing agent in the dual-agent protocol. Proposes changes, writes code, runs tests, and keeps the system internally consistent. Receives GO / NO-GO verdicts from Loyal...
- ... 68 additional canonical term(s) omitted from startup summary.

### Live Project Dashboard

- Dashboard: GroundTruth-KB Project Dashboard: [http://localhost:3000/d/gtkb/groundtruth-kb-dashboard](http://localhost:3000/d/gtkb/groundtruth-kb-dashboard)
- Dashboard reachability: Grafana health endpoint: unavailable; target: http://localhost:3000/api/health
- Dashboard reachability: GT-KB dashboard URL: unavailable; target: http://localhost:3000/d/gtkb/groundtruth-kb-dashboard
- Dashboard recovery hint: Grafana is optional for startup; start or restart the local Grafana service and re-open the dashboard link when reachability is unavailable.
- Browser opening: use the harness-controlled browser for live dashboard inspection; startup open request: enabled; current mode: `harness_browser`. Startup hooks must not launch the operating system default browser unless explicitly configured with `dashboard_open_mode: system_default_browser`.
- KPI coverage: GT-KB backlog, MemBase work items, Deliberation Archive records, tests, specifications, drift, regression, contention, and tokens consumed at session start before user input.
- Dashboard scope: GroundTruth-KB project dashboard.
- Token measurement status: not_exposed_by_current_harness
- Tokens consumed before user input: unavailable

### Current Project State

- GT-KB release blockers: 0
- GT-KB active backlog items: 31
- GT-KB open MemBase work items: 26
- GT-KB dashboard-scoped bridge/contention entries, non-authoritative for queue state: 4
- GT-KB drift changed paths: 0
- GT-KB Testing/tool rollup: 0 failing, 6 manual, 13 ready/passing (queried repo: unknown)
- Bridge role slot: `shared` (prime-builder, loyal-opposition, or shared)
- Harness topology: `multi_harness` (single_harness or multi_harness)
- GT-KB infrastructure posture: package 0.7.0rc1; dry-run upgrade plan available: True
- GT-KB dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: warn (harness=codex, role=loyal-opposition, EXTRA=2, PASS=22)

### Project State Rollup

- Source: MemBase table: current_work_items grouped by `project_name`.
- Current work items: 2276; non-terminal: 277; active projects: 50; ungrouped non-terminal: 107.
- Status counts: deferred=1, in_progress=1, new=1, not_a_defect=7, open=274, resolved=1808, retired=68, verified=56, wont_fix=60.
- Active project states:
  - `AGENT-RED-TEST-COVERAGE-GAPS`: 38 non-terminal (open=38); top: `WI-3185` - Test coverage gap: Testable Element Dimension Taxonomy [open, P3].
  - `PROJECT-GTKB-RELIABILITY-FIXES`: 28 non-terminal (open=28); top: `WI-3388` - Enforce implementation-report structural compliance + preserve draft mtime in impl_report_bridge.py file_report helper [open, P1].
  - `GTKB-RELIABILITY-FIXES`: 16 non-terminal (open=16); top: `WI-3360` - Repair cross-harness bridge trigger: ModuleNotFoundError import defect and stale active-session lock cleanup [open, P2].
  - `GTKB-V1-RELEASE-STRATEGY-001`: 8 non-terminal (open=8); top: `WI-3404` - Define v1.0 acceptance criteria (sole anti-perpetual-rc1 checkpoint per §9.2) [open, P0].
  - `AGENT-RED-SPEC-HYGIENE`: 7 non-terminal (open=7); top: `WI-3183` - KB integrity -- SPA cluster test-ID investigation closure: 10 SPA specs have no current test linkage [open, P2].
  - `GTKB-DETERMINISTIC-SERVICES-001`: 6 non-terminal (open=6); top: `WI-3265` - Cross-harness trigger fires unreliably in codex exec sessions (dispatch-state refresh lag) [open, P1, order 1].
  - `GTKB-GOVERNANCE-ADOPTION`: 5 non-terminal (open=5); top: `GTKB-GOV-001` - Complete Agent Red Tier A managed-skill adoption apply [open, order 1029].
  - `PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES`: 5 non-terminal (open=5); top: `WI-3373` - Bridge scheduler Slice 2: per-document lease registry [open, P2].
  - `GTKB-GOV-PROPOSAL-STANDARDS`: 4 non-terminal (in_progress=1, open=3); top: `GTKB-GOV-PROPOSAL-STANDARDS` - GTKB-GOV-PROPOSAL-STANDARDS Slice 1 [in_progress, order 5].
  - `GTKB-ISOLATION`: 4 non-terminal (open=4); top: `GTKB-ISOLATION-015` - Complete full Phase 7 work-subject/root enforcement (Slice 1 VERIFIED; Slice 2 remaining) [open, order 1000].
  - `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`: 3 non-terminal (open=3); top: `WI-3353` - Bridge governance hooks resolve project root from session cwd, mis-targeting MemBase and bridge/INDEX.md in .claude/worktrees/* sessions [open, P1].
  - `PROJECT-GTKB-SKILL-MODERNIZATION`: 3 non-terminal (open=3); top: `WI-3391` - Skill modernization umbrella: thin-wrapper migration for kb-* skills + send-review deprecation + skill-health checker (S363 LO advisory response) [open, P2].
  - `GTKB-BACKLOG-CAPTURE-001`: 2 non-terminal (open=2); top: `WI-3271` - Backlog approval-state taxonomy and AUQ implementation gate [open, P1].
  - `GTKB-DASHBOARD`: 2 non-terminal (deferred=1, open=1); top: `GTKB-DASHBOARD-003` - Dashboard industry-alignment Slice 3 (SLO, flow metrics, PR health, incident/MTTR, remote exposure, WCAG) [open, order 1007].
  - `GTKB-DASHBOARD-002`: 2 non-terminal (open=2); top: `GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION` - GTKB-DASHBOARD-002 Slice 2.3 (integration) [open, order 3].
  - `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`: 2 non-terminal (open=2); top: `WI-3424` - Deterministic CLI: gt validate spec-coherence (detect cross-spec contradictions via surface-overlap, authority-hierarchy, and status-drift checks across current_specifications) [open, P1].
  - `PROJECT-GTKB-ENV-SOT-TOPOLOGY`: 2 non-terminal (open=2); top: `WI-3430` - Migrate Agent Red from 3-file SoT layout to single SoT + CLI-generated per-sub-app views [open, P2].
  - `AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION`: 1 non-terminal (open=1); top: `WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION` - Explore Claude Design GUI workflow for Agent Red GUI work [open, order 1037].
  - `AGENT-RED-DEPLOY-PIPELINE`: 1 non-terminal (open=1); top: `WI-3172` - Resolve deploy pipeline Phase 0 environment validation failure [open].
  - `AGENT-RED-RELEASE-READINESS`: 1 non-terminal (open=1); top: `WI-3248` - Agent Red deployability and maintainability preservation gate [open, P0].
  - `Antigravity Integration`: 1 non-terminal (open=1); top: `WI-3349` - End-to-end Gemini CLI headless LO-review dispatch verification [open, P1].
  - `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`: 1 non-terminal (open=1); top: `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` - GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001 (Apply ADR/DCL logic as clause-level review tests) [open, order 44].
  - `GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL`: 1 non-terminal (open=1); top: `GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL` - GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL [open, order 32].
  - `GTKB-ARTIFACT-RECORDER-CLI`: 1 non-terminal (open=1); top: `GTKB-ARTIFACT-RECORDER-CLI` - GTKB-ARTIFACT-RECORDER-CLI [open, order 15].
  - `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL`: 1 non-terminal (open=1); top: `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL` - GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL [open, order 28].
  - `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`: 1 non-terminal (open=1); top: `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY` - Migrate direct bridge INDEX writers to gtkb_bridge_writer.py [open, order 24].
  - `GTKB-COMMAND-SURFACE`: 1 non-terminal (open=1); top: `GTKB-COMMAND-SURFACE` - GTKB-COMMAND-SURFACE [open, order 12].
  - `GTKB-CORE-001`: 1 non-terminal (open=1); top: `GTKB-CORE-001` - Make core application specification intake default GT-KB behavior [open, order 1028].
  - `GTKB-DORA`: 1 non-terminal (open=1); top: `GTKB-DORA-002` - DORA four-keys panels (consumer of GTKB-DORA-001) [open, order 1009].
  - `GTKB-GOV-004`: 1 non-terminal (open=1); top: `GTKB-GOV-004` - Reconcile legacy MemBase work items into a high-quality unified backlog [open, order 1032].
  - `GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH`: 1 non-terminal (open=1); top: `WI-3490` - Slice 7-prime: Physical retirement of memory/work_list.md (migration-completion gate) [open, P1].
  - `GTKB-GOV-DA-ENFORCEMENT`: 1 non-terminal (open=1); top: `GTKB-GOV-DA-ENFORCEMENT` - GTKB-GOV-DA-ENFORCEMENT [open, order 6].
  - `GTKB-GOVERNANCE-CORRECTION-S358`: 1 non-terminal (open=1); top: `WI-3462` - Phase-2 implements-link backfill for v4 project auto-completion [open, P2].
  - `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001`: 1 non-terminal (open=1); top: `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001` - GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001 (Anchor-only in-source citation conventions + orphan-citation doctor invariant) [open, order 40].
  - `GTKB-ISOLATION-017-SLICE-2.5`: 1 non-terminal (open=1); top: `GTKB-ISOLATION-017-SLICE-2.5` - GTKB-ISOLATION-017-SLICE-2.5 (registry rationale schema extension) [open, order 26].
  - `GTKB-LO-REPORT-BACKFILL`: 1 non-terminal (new=1); top: `WI-3162` - Backfill existing LO reports and bridge history [new, P2].
  - `GTKB-MASS-001`: 1 non-terminal (open=1); top: `GTKB-MASS-001` - Execute GT-KB mass-adoption readiness plan [open, order 1027].
  - `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY`: 1 non-terminal (open=1); top: `GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY` - GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY [open, order 19].
  - `GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC`: 1 non-terminal (open=1); top: `GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC` - GTKB-REHEARSE-DRIVER-WAVE-BANNER-COSMETIC [open, order 25].
  - `GTKB-REQUIREMENTS-QUALITY-AUDIT`: 1 non-terminal (open=1); top: `WI-3247` - Critical quality and consistency audit of early-project requirements [open, P1].
  - `GTKB-ROLE-ENHANCEMENT`: 1 non-terminal (open=1); top: `GTKB-ROLE-ENHANCEMENT` - GTKB-ROLE-ENHANCEMENT [open, order 11].
  - `GTKB-STARTUP-ENHANCEMENTS`: 1 non-terminal (open=1); top: `GTKB-STARTUP-ENHANCEMENTS` - GTKB-STARTUP-ENHANCEMENTS [open, P1, order 9].
  - `GTKB-STARTUP-REFRACTOR-001`: 1 non-terminal (open=1); top: `GTKB-STARTUP-REFRACTOR-001` - GTKB-STARTUP-REFRACTOR-001 (Consolidate role startup and glossary loading) [open, P1, order 30].
  - `GTKB-WRAPUP-ENHANCEMENTS`: 1 non-terminal (open=1); top: `GTKB-WRAPUP-ENHANCEMENTS` - GTKB-WRAPUP-ENHANCEMENTS [open, order 10].
  - `POR-SPEC-HYGIENE`: 1 non-terminal (open=1); top: `WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE` - Complete POR Steps 16.D-16.E spec hygiene remediation [open, order 1040].
  - `PROJECT-ANTIGRAVITY-INTEGRATION`: 1 non-terminal (open=1); top: `WI-3383` - Record harness, model, and settings provenance on each bridge document [open, P3].
  - `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION`: 1 non-terminal (open=1); top: `WI-3438` - Slice 3: Execute CLAUDE.md split + 18.I files migration to applications/Agent_Red/ [open, P1].
  - `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY`: 1 non-terminal (open=1); top: `WI-3434` - Amend project-root-boundary.md with bounded external-harness-executable resolution exception + doctor check [open, P1].
  - `PROJECT-GTKB-PUSH-GATE`: 1 non-terminal (open=1); top: `WI-3416` - PROJECT-GTKB-PUSH-GATE master: comprehensive deterministic CI gate Slice 0-11 design + implementation [open, P1].
  - `ZERO-KNOWLEDGE-ARCHITECTURE`: 1 non-terminal (open=1); top: `WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` - Zero-knowledge architecture Phase 4 [open, order 1041].

### Active Work Subject

- Default work subject: GT-KB Infrastructure Focus
- Current work subject: GT-KB Infrastructure Focus
- Application label: Agent Red demo adopter
- Bridge role slot: `shared` (shared, prime-builder, or loyal-opposition).
- Harness topology: `multi_harness` (single_harness or multi_harness).
- GT-KB is the default work subject; owner direction is interpreted as GroundTruth-KB work unless Mike explicitly names an adopter application.
- Application work subject means owner direction is interpreted as work on a named adopter/demo application such as Agent Red.
- Application work subject commands: `work subject application`, `application mode`, `app mode`, `agent red mode`.
- GT-KB work subject commands: `work subject GT-KB`, `GT-KB mode`, `GT-KB infrastructure mode`, `GroundTruth-KB mode`.
- Canonical state file: `.claude/session/work-subject.json` (legacy `.claude/hooks/.workstream-focus-state.json` migrated on next owner command).

### Pending Owner Decisions

3 owner decision(s) await a response. Address one by quoting its DECISION-NNNN ID, type `resolve DECISION-NNNN: <answer>` to record an answer, `defer all` to acknowledge without resolving, or `clear pending` to dismiss intentionally.

- **DECISION-0860** (asked 2026-05-31T07:32:41.916810Z)
> Want me to triage that broader 55-entry queue (most are other-stream GOs awaiting implementation), or hold here until...
- **DECISION-0861** (asked 2026-05-31T07:52:24.177485Z)
> want me to triage that queue, push this commit, or stop here?
- **DECISION-0870** (asked 2026-05-31T17:48:18.550796Z)
> Want me to (a) continue the diagnostic of the cache/sidecar mismatch I started, (b) propose unifying the startup/fres...

### Wrap-Up Trigger Commands

- Wrap-up trigger: use one of the documented commands as a standalone message.
- Accepted wrap-up commands: `wrap up`, `wrap up this session`, `session wrap-up`, `run session wrap-up`, `close this session`, `end this session`, `new session`, `fresh session`, `start a new session`, `start a fresh session`, `begin a new session`, `begin a fresh session`, `open a new session`, `prepare a new session`, `initialize a new session`, `start fresh`, `begin fresh`.
- Optional leading or trailing `please` and final punctuation are accepted.