# GroundTruth-KB Fresh Session Startup

Generated: 2026-06-25T09:04:24Z
Dashboard: GroundTruth-KB Project Dashboard: [http://localhost:3000/d/gtkb/groundtruth-kb-dashboard](http://localhost:3000/d/gtkb/groundtruth-kb-dashboard)

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Prime Builder
- Interactive resolved role: Prime Builder
- Interactive role source: durable registry fallback; no transcript-defined interactive role was provided to startup
- Durable registry role: Prime Builder
- Durable registry role authority: headless dispatch routing and interactive fallback only; non-overriding when a transcript-defined interactive role is present
- Role assignment: active AI harness assigned by owner through the single role assignment map
- Bridge: always available through TAFE/dispatcher state plus versioned bridge files and checked at session startup
- Bridge dispatch: cross-harness event-driven trigger registered as PostToolUse and Stop hooks (.claude/settings.json, .codex/hooks.json, .cursor/hooks.json); fires on tool-use and Stop rather than on a fixed interval; manual TAFE/dispatcher bridge scans available as fallback; retired smart poller and OS poller remain archived
- Bridge operation instructions: Bridge automation has two complementary axes. AXIS 1 (DISPATCHABLE WORK): the cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) is the canonical mechanism for self-contained work — reviews, verdicts, tests, work that a freshly-spawned counterpart harness can complete without further owner input. Registered as PostToolUse and Stop hooks. AXIS 2 (NON-DISPATCHABLE WORK): an owner-approved thread automation pattern may wake the interactive chat session to inspect TAFE/dispatcher bridge state and surface work that requires interactive owner input mid-stream — owner-AUQ-required decisions, multi-turn review with accumulating context, cross-thread coordination, AUQ-heavy implementation. Both axes are required; their roles do not overlap. Use the `gtkb-bridge` skill (`.claude/skills/bridge/SKILL.md`; Codex adapter `.codex/skills/bridge/SKILL.md`) for proposal/review/verification mechanics. Manual bridge scans remain available as fallback, but they must use TAFE/dispatcher bridge state and versioned bridge files. Do NOT create new bridge automations (Codex-app-side, Claude-side, or otherwise) without owner approval; any new automation must be classified by axis (dispatchable vs non-dispatchable) and inventoried in `config/agent-control/system-interface-map.toml`.
- Role mapping source: harness-state/harness-registry.json
- Harness self-identification: unidentified
- Harness identity source: unidentified

- Strict GOV enforcement where mechanically available
- Formal artifact approval required for DA, GOV, SPEC, PB, ADR, and DCL mutations
- Standing backlog is the governed cross-session work authority
- Strategic self-improvement directive: Prime Builder and Loyal Opposition capture noticed fix-worthy issues and useful workflow enhancements as review/consideration backlog items in MemBase, not MEMORY.md; backlog capture is not implementation approval; implementation-approved backlog items require AskUserQuestion evidence; executing a consideration item means presenting insight/options and obtaining AskUserQuestion approval before implementation proposal work
- GT-KB adoption and release-readiness evidence remain release-gate visible
- Published-state SoT-deference (GOV-GTKB-PUBLISHED-STATE-SOT-DEFERENCE-001): GT-KB-subject sessions defer to the released public-repo Main plus public issues tracker and wiki as the authoritative published-state source-of-truth before contemplating GT-KB changes (confirm whether already decided upstream; ensure consistency or knowingly supersede); GT-KB leads the repo, adopters trail it; application-subject sessions emit cross-scope advisories, not direct GT-KB changes (WI-4690)
- Harness hook limitations require parity checks and explicit fallback disclosure

### Session-Context Review Independence

- Formal GO / NO-GO / VERIFIED must come from a different model session context than the artifact author/implementer.
- Blocker: reviewer session context equals artifact `author_session_context_id`; fail closed when metadata is missing or unreadable.
- Not the boundary: harness ID, vendor, or durable registry role (routing labels only).
- `::init gtkb pb` grants Prime Builder authority regardless of durable registry role; it does not permit this session to GO/VERIFY its own authored or implemented work.

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
- GT-KB active backlog items: 0
- GT-KB open MemBase work items: 8 (subject-scoped; 251 across all subjects)
- GT-KB dashboard-scoped bridge/contention entries, non-authoritative for queue state: 83
- GT-KB drift changed paths: 2
- GT-KB Testing/tool rollup: 0 failing, 2 manual, 15 ready/passing (queried repo: unknown)
- Active harness role slot: `shared` (prime-builder, loyal-opposition, or shared)
- Harness topology: `multi_harness` (single_harness or multi_harness)
- GT-KB infrastructure posture: package 0.7.0rc1; dry-run upgrade plan available: True
- GT-KB dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: fail (harness=all, role=prime-builder, MISSING=32, PASS=142, STALE=6)

### Active Work Subject

- Default work subject: GT-KB Infrastructure Focus
- Current work subject: GT-KB Infrastructure Focus
- Application label: Agent Red demo adopter
- Work-subject bridge role slot: `shared` (shared, prime-builder, or loyal-opposition).
- Harness topology: `multi_harness` (single_harness or multi_harness).
- GT-KB is the default work subject; owner direction is interpreted as GroundTruth-KB work unless Mike explicitly names an adopter application.
- Application work subject means owner direction is interpreted as work on a named adopter/demo application such as Agent Red.
- Application work subject commands: `work subject application`, `application mode`, `app mode`, `agent red mode`.
- GT-KB work subject commands: `work subject GT-KB`, `GT-KB mode`, `GT-KB infrastructure mode`, `GroundTruth-KB mode`.
- Canonical state file: `.claude/session/work-subject.json` (legacy `.claude/hooks/.workstream-focus-state.json` migrated on next owner command).
- Counterpart harness detected; no role or subject conflicts.

### Top Priority Actions

- No implementation-authorized work items currently surface as top-3 priorities.

## Session Startup

### Configuration
- Work subject: GT-KB; startup focus: GT-KB Infrastructure Focus.
- Role assignment: Prime Builder from harness-state/harness-registry.json.
- Harness: id unidentified from unidentified; topology `multi_harness`.
- Dashboard opening: enabled; mode `harness_browser`; package 0.7.0rc1.

### Operating State
- Release blockers: 0.
- Testing/tools: 0 failing, 2 manual, 15 ready/passing (queried repo: unknown).
- Dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: fail (harness=all, role=prime-builder, MISSING=32, PASS=142, STALE=6)
- Data freshness: 2026-06-25T09:04:24Z.
