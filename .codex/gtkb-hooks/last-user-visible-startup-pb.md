# GroundTruth-KB Fresh Session Startup

Generated: 2026-05-31T21:17:56Z
Dashboard: GroundTruth-KB Project Dashboard: [http://localhost:3000/d/gtkb/groundtruth-kb-dashboard](http://localhost:3000/d/gtkb/groundtruth-kb-dashboard)

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Prime Builder
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
- Harness parity: warn (harness=codex, role=prime-builder, EXTRA=2, PASS=26)

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

## Session Startup

### Configuration
- Work subject: GT-KB; startup focus: GT-KB Infrastructure Focus.
- Role assignment: Prime Builder from harness-state/role-assignments.json.
- Harness: id A from harness-state/harness-identities.json; topology `multi_harness`.
- Dashboard opening: enabled; mode `harness_browser`; package 0.7.0rc1.

### Operating State
- Release blockers: 0.
- Testing/tools: 0 failing, 6 manual, 13 ready/passing (queried repo: unknown).
- Dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: warn (harness=codex, role=prime-builder, EXTRA=2, PASS=26)
- Data freshness: 2026-05-31T21:17:56Z.

### Work State
- File bridge: generated-time latest NEW/REVISED=2; latest GO/NO-GO for Prime=96; latest ADVISORY=5. Live `bridge/INDEX.md` remains authoritative after generation.
- MemBase project rollup: 50 active group(s), 277 non-terminal item(s); top: `WI-3185` - Test coverage gap: Testable Element Dimension Taxonomy [open, P3].
- Standing backlog top priorities: GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL: GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL; GTKB-GOV-010: Maintain unified backlog harvest/reconciliation audit as release-gate input; WI-3172: Resolve deploy pipeline Phase 0 environment validation failure.
- Drift changed paths: 0.
- Action center first signal: Review GT-KB scaffold upgrade plan - 23 mutating dry-run action(s) are available..

### Recommended Session Focus

Reply with A, B, C, D, or an exact label from the full focus list. Each recommendation is generated from current startup evidence.

A. **Continue Last Session**
   Evidence: Live bridge metrics show 96 latest GO/NO-GO responses for Prime continuation.
   Expected work: Continue from the last session using the dashboard action center and any latest GO/NO-GO bridge responses, including responses produced by a prior Loyal Opposition session.

B. **Top Priority Actions**
   Evidence: Prime-actionable bridge responses should be considered alongside standing priorities.
   Expected work: Focus this session on the established top priority actions.

C. **Repair Testing/Tool Integrations**
   Evidence: Testing/tool state reports 0 failing and 14 unknown integration(s); first signal: GitHub Actions.
   Expected work: Focus this session on restoring testing service/tool integration health.

D. **Full Focus List**
   Choose any label below; the active role will expand it using the stored prompt details.
   - Optimize Startup Token Consumption
   - Top Priority Actions
   - Resolve Release Blockers
   - Repair Testing/Tool Integrations
   - Remediate Known Risks
   - Clear Stage/Test Release Path
   - Clean For Internal Review
   - Pick From Standing Backlog
   - Commit and push to GitHub
   - Merge to main, build and push to the staging environment
   - Execute end-to-end tests in the staging environment
   - Push staged-and-tested build to production, then smoke test
   - Continue Last Session

Or provide a prompt for something else.