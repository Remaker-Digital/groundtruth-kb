# GroundTruth-KB Fresh Session Startup

Generated: 2026-06-25T01:07:33Z
Dashboard: GroundTruth-KB Project Dashboard: [http://localhost:3000/d/gtkb/groundtruth-kb-dashboard](http://localhost:3000/d/gtkb/groundtruth-kb-dashboard)

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Loyal Opposition
- Interactive resolved role: Loyal Opposition
- Interactive role source: startup disclosure cache role mode lo; authoritative only when selected by the owner transcript/init-keyword path
- Durable registry role: Prime Builder
- Durable registry role authority: headless dispatch routing and interactive fallback only; non-overriding when a transcript-defined interactive role is present
- Role assignment: active AI harness assigned by owner through single role map entry for harness `E`
- Bridge: always available through TAFE/dispatcher state plus versioned bridge files and checked at session startup
- Bridge dispatch: cross-harness event-driven trigger registered as PostToolUse and Stop hooks (.claude/settings.json, .codex/hooks.json, .cursor/hooks.json); fires on tool-use and Stop rather than on a fixed interval; manual TAFE/dispatcher bridge scans available as fallback; retired smart poller and OS poller remain archived
- Bridge operation instructions: Bridge automation has two complementary axes. AXIS 1 (DISPATCHABLE WORK): the cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) is the canonical mechanism for self-contained work — reviews, verdicts, tests, work that a freshly-spawned counterpart harness can complete without further owner input. Registered as PostToolUse and Stop hooks. AXIS 2 (NON-DISPATCHABLE WORK): an owner-approved thread automation pattern may wake the interactive chat session to inspect TAFE/dispatcher bridge state and surface work that requires interactive owner input mid-stream — owner-AUQ-required decisions, multi-turn review with accumulating context, cross-thread coordination, AUQ-heavy implementation. Both axes are required; their roles do not overlap. Use the `gtkb-bridge` skill (`.claude/skills/bridge/SKILL.md`; Codex adapter `.codex/skills/bridge/SKILL.md`) for proposal/review/verification mechanics. Manual bridge scans remain available as fallback, but they must use TAFE/dispatcher bridge state and versioned bridge files. Do NOT create new bridge automations (Codex-app-side, Claude-side, or otherwise) without owner approval; any new automation must be classified by axis (dispatchable vs non-dispatchable) and inventoried in `config/agent-control/system-interface-map.toml`.
- Role mapping source: harness-state/harness-registry.json
- Harness self-identification: E
- Harness identity source: harness-state/harness-identities.json

- Strict GOV enforcement where mechanically available
- Formal artifact approval required for DA, GOV, SPEC, PB, ADR, and DCL mutations
- Standing backlog is the governed cross-session work authority
- Strategic self-improvement directive: Prime Builder and Loyal Opposition capture noticed fix-worthy issues and useful workflow enhancements as review/consideration backlog items in MemBase, not MEMORY.md; backlog capture is not implementation approval; implementation-approved backlog items require AskUserQuestion evidence; executing a consideration item means presenting insight/options and obtaining AskUserQuestion approval before implementation proposal work
- GT-KB adoption and release-readiness evidence remain release-gate visible
- Harness hook limitations require parity checks and explicit fallback disclosure

### Session-Context Review Independence

- Formal GO / NO-GO / VERIFIED must come from a different model session context than the artifact author/implementer.
- Blocker: reviewer session context equals artifact `author_session_context_id`; fail closed when metadata is missing or unreadable.
- Not the boundary: harness ID, vendor, or durable registry role (routing labels only).
- Full normative block: `config/agent-control/SESSION-STARTUP-INDEX.md § Session-context review independence (normative)`.

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
- GT-KB open MemBase work items: 16
- GT-KB dashboard-scoped bridge/contention entries, non-authoritative for queue state: 91
- GT-KB drift changed paths: 1
- GT-KB Testing/tool rollup: 0 failing, 2 manual, 15 ready/passing (queried repo: unknown)
- Active harness role slot: `prime-builder` (prime-builder, loyal-opposition, or shared)
- Harness topology: `multi_harness` (single_harness or multi_harness)
- GT-KB infrastructure posture: package 0.7.0rc1; dry-run upgrade plan available: True
- GT-KB dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: fail (harness=all, role=loyal-opposition, MISSING=27, PASS=123)

### Project State Rollup

- Source: MemBase tables: current_work_items + current_project_work_item_memberships grouped by `current_project_work_item_memberships.project_id`.
- Current work items: 3583; non-terminal: 294; active projects: 48; ungrouped non-terminal: 137.
- Status counts: deferred=1, not_a_defect=7, open=293, resolved=3045, retired=112, verified=64, wont_fix=61.
- Active project states:
  - `GTKB-DISPATCHER-COMPLETION`: 11 non-terminal (open=11); top: `WI-4786` - Phase 1 - Umbrella ADR for dispatcher architecture (persistent daemon + computed-quality + full black box); amend TAFE R-series, SPEC-CENTRALIZED-DISPATCH-SERVICE-001, DCL-DISPATCH-ENVELOPE-RULES-001 in place; resolve INDEX-vs-dispatcher transition [open, P1].
  - `GTKB-RELIABILITY-FIXES`: 11 non-terminal (open=11); top: `WI-4806` - Add worker-lifetime timeout to run_with_status.py so dispatched workers cannot hang forever (fast-lane; part of WI-4670 Phase 0) [open, P1].
  - `LO Advisory Routing`: 11 non-terminal (open=11); top: `WI-3306` - Route LO advisory: INSIGHTS-2026-05-07-06-39-GTKB-DOCUMENTATION-QUALITY-REVIEW.md [open, P3].
  - `May29 Hygiene`: 11 non-terminal (open=11); top: `WI-4763` - Prevent concurrent commits from bundling freshly staged LO verdicts [open, P1].
  - `AGENT-RED-TEST-COVERAGE-GAPS`: 8 non-terminal (open=8); top: `WI-3212` - Test coverage gap: Phone Identity Channel: SMS OTP via Azure Communication Services [open, P3].
  - `GTKB Obsolete Reference Purge`: 8 non-terminal (open=8); top: `WI-4794` - Methodology: obsolete-reference-purge ADR + DCL [open, P2].
  - `Activity-Envelope Disposition and Autonomous Dispatch`: 6 non-terminal (open=6); top: `WI-4683` - Reconcile the activity-vocabulary drift to one canonical closed set (re-admit ops) [open, P1].
  - `GTKB-ADOPTER-EXPERIENCE`: 6 non-terminal (open=6); top: `GTKB-GOV-001` - Complete Agent Red Tier A managed-skill adoption apply [open, order 1029].
  - `GTKB-SOURCE-OF-TRUTH-FRESHNESS`: 6 non-terminal (open=6); top: `WI-3501` - Formalize the source-of-truth-freshness principle as governance (DA decision + GOV + DCL) [open, P2].
  - `Harness State SoT Consolidation`: 6 non-terminal (open=6); top: `WI-4328` - Define canonical reader entrypoint in groundtruth_kb.harness_projection (or equivalent) [open, P2].
  - `Omnigent Alignment`: 6 non-terminal (open=6); top: `WI-4550` - Omnigent#1: Cost/token-iteration budget policy for dispatched bridge workers [open, P1].
  - `GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE`: 5 non-terminal (open=5); top: `WI-4781` - Phase 0 - Amend GOV-SESSION-ROLE-AUTHORITY-001 to carry the canonical registry-role-is-dispatcher-only principle as single source; split DCL-SESSION-ROLE-RESOLUTION-001 (self-role-choice MAY use hint; enforcement-gate MUST NOT) [open, P1].
  - `Harness Testing and Quality Benchmarking 1`: 5 non-terminal (open=5); top: `WI-4580` - Build isolated GT-KB benchmark fixture corpus with seeded flaws [open, P1].
  - `GTKB-APPROVAL-PACKET-ERGONOMICS`: 4 non-terminal (open=4); top: `WI-3378` - Build a first-class gap-state formal-artifact MemBase capture lane [open, P2].
  - `GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE`: 4 non-terminal (open=4); top: `WI-4255` - Windows governance preflight evidence model [open, P2].
  - `Agent Red Readiness Program`: 3 non-terminal (open=3); top: `WI-4655` - Phase 1.2 - App-root minimization validator (sub-slice 5) [open, P1].
  - `Backlog Triage and Hygiene`: 3 non-terminal (open=3); top: `WI-4665` - intake-pipeline auto-confirm path leaves SPEC description field NULL [open, P2].
  - `GT-KB v1.0 Release Strategy`: 3 non-terminal (open=3); top: `WI-3400` - Capture Antigravity 2026-05-27 V1-RELEASE-STRATEGY-REVIEW advisory disposition (peer-solution-advisory-loop) [open, P2].
  - `GTKB-BRIDGE-PROTOCOL-RELIABILITY`: 3 non-terminal (open=3); top: `WI-4671` - implementation_authorization Requirement-Sufficiency gate false-positives on forward-looking 'needed for a later <scope>' sentences, starving headless Prime dispatch [open, P1].
  - `GTKB-BRIDGE-SIGNAL-QUALITY`: 3 non-terminal (open=3); top: `WI-4253` - Bridge signal quality inactive substrate diagnostics [open, P2].
  - `Activity-Envelope Disposition and Autonomous Dispatch`: 2 non-terminal (open=2); top: `WI-4730` - Follow-on AUQ: define the unique disposition-profile details of each of the six Activity Envelope types [open, P1].
  - `GTKB-DASHBOARD-OBSERVABILITY`: 2 non-terminal (open=2); top: `GTKB-DASHBOARD-003` - Dashboard industry-alignment Slice 3 (SLO, flow metrics, PR health, incident/MTTR, remote exposure, WCAG) [open, order 1007].
  - `GTKB-GOVERNANCE-HARDENING`: 2 non-terminal (open=2); top: `GTKB-GOV-004` - Reconcile legacy MemBase work items into a high-quality unified backlog [open, order 1032].
  - `GTKB-IMPLEMENTATION-START-GATE-HARDENING-001`: 2 non-terminal (open=2); top: `WI-3350` - implementation_authorization project-auth validator should accept a parent-project PAUTH for a sub-project proposal [open, P2].
  - `PROJECT-GTKB-ENV-SOT-TOPOLOGY`: 2 non-terminal (open=2); top: `WI-3430` - Migrate Agent Red from 3-file SoT layout to single SoT + CLI-generated per-sub-app views [open, P2].
  - `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`: 2 non-terminal (open=2); top: `WI-4566` - TAFE Phase B residual cutover-evidence cleanup [open, P1].
  - `Agent Disposition and Protocol Enforcement`: 1 non-terminal (open=1); top: `WI-4591` - Normalize bridge disposition workflow for ADVISORY NO-GO NEW REVISED GO and VERIFIED states [open, P2].
  - `AGENT-RED-CLAUDE-DESIGN-GUI-EXPLORATION`: 1 non-terminal (open=1); top: `WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION` - Explore Claude Design GUI workflow for Agent Red GUI work [open, order 1037].
  - `AGENT-RED-DEPLOY-PIPELINE`: 1 non-terminal (open=1); top: `WI-3172` - Resolve deploy pipeline Phase 0 environment validation failure [open].
  - `AGENT-RED-SPEC-HYGIENE`: 1 non-terminal (open=1); top: `WI-3183` - KB integrity -- SPA cluster test-ID investigation closure: 10 SPA specs have no current test linkage [open, P2].
  - `Backlog add command`: 1 non-terminal (open=1); top: `WI-3269` - GTKB-GT-BACKLOG-ADD-CLI - add `gt backlog add` subcommand for owner-directed backlog additions [open, P3].
  - `Envelope Open and Close action refinement`: 1 non-terminal (open=1); top: `WI-4482` - Explicit-hint layer umbrella spec: activity-envelope rename + init-keyword v3 glossary fix + interception DCL [open, P2].
  - `GT-KB Clarification Tooling`: 1 non-terminal (open=1); top: `WI-AUTO-SPEC-INTAKE-1262C1` - Implement SPEC-INTAKE-1262c1: grill-me-for-clarification owner clarification interview skill [open].
  - `GT-KB Infrastructure`: 1 non-terminal (open=1); top: `WI-4248` - Diagnose Codex Windows parallel shell launch flake [open, P2].
  - `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001`: 1 non-terminal (open=1); top: `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` - GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001 (Apply ADR/DCL logic as clause-level review tests) [open, order 44].
  - `GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL`: 1 non-terminal (open=1); top: `GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL` - GTKB-AI-ASSISTED-DELIVERY-MATURITY-MODEL [open, order 32].
  - `GTKB-DASHBOARD`: 1 non-terminal (deferred=1); top: `GTKB-DASHBOARD-RETENTION` - Dashboard history retention policy (contingent) [deferred, order 1010].
  - `GTKB-DETERMINISTIC-SERVICES-001`: 1 non-terminal (open=1); top: `WI-4567` - Deterministic service: end-to-end bridge implementation-proposal filing (DELIB + PAUTH + claim + write + preflight) [open, P3].
  - `GTKB-GOV-PROPOSAL-STANDARDS`: 1 non-terminal (open=1); top: `WI-4537` - gtkb_propose_scaffold defaults are stale vs current bridge gates (bridge_kind + pytest -p flag) [open, P3].
  - `GTKB-ISOLATION`: 1 non-terminal (open=1); top: `GTKB-ISOLATION-018` - Execute Agent Red child-directory cutover [open, order 1025].
  - `GTKB-ISOLATION-017-SLICE-2.5`: 1 non-terminal (open=1); top: `GTKB-ISOLATION-017-SLICE-2.5` - GTKB-ISOLATION-017-SLICE-2.5 (registry rationale schema extension) [open, order 26].
  - `GTKB-MASS-001`: 1 non-terminal (open=1); top: `GTKB-MASS-001` - Execute GT-KB mass-adoption readiness plan [open, order 1027].
  - `GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH`: 1 non-terminal (open=1); top: `WI-3512` - Decouple harness_ops role-retention from active status (honor ADR-ROLE-STATUS-ORTHOGONALITY-001 section 9) [open, P2].
  - `LO Advisory Owner-Grilling Gate`: 1 non-terminal (open=1); top: `WI-3445` - Slice 2: Update CODEX-REVIEW contracts + 3 LO-advisory-emitting skills [open, P2].
  - `May29 Hygiene`: 1 non-terminal (open=1); top: `WI-4674` - Enforce verification verdict structure and commit-type checks [open, P2].
  - `PROJECT-GTKB-SKILL-MODERNIZATION`: 1 non-terminal (open=1); top: `WI-3459` - Slice 3b: kb-work-item skill rewrite + Codex/Antigravity adapter regen + registry parity (clean-tree follow-on) [open, P2].
  - `Protected-Artifact Drift Rollup`: 1 non-terminal (open=1); top: `WI-4369` - Protected-artifact drift rollup: govern 23-path accumulated drift via per-cluster AUQs [open, P2].
  - `ZERO-KNOWLEDGE-ARCHITECTURE`: 1 non-terminal (open=1); top: `WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` - Zero-knowledge architecture Phase 4 [open, order 1041].

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