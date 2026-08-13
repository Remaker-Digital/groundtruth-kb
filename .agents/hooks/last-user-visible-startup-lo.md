# GroundTruth-KB Fresh Session Startup

Generated: 2026-08-13T13:46:19Z
Dashboard: GroundTruth-KB Project Dashboard: [http://localhost:3000/d/gtkb/groundtruth-kb-dashboard](http://localhost:3000/d/gtkb/groundtruth-kb-dashboard)

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Loyal Opposition
- Interactive resolved role: Loyal Opposition
- Interactive role source: startup disclosure cache role mode lo; authoritative only when selected by the owner transcript/init-keyword path
- Role assignment: active AI harness assigned by owner through single role map entry for harness `B`
- Bridge: always available through TAFE/dispatcher state plus versioned bridge files and checked at session startup
- Bridge dispatch: dispatcher daemon registered as PostToolUse and Stop hooks (.claude/settings.json, .codex/hooks.json, .cursor/hooks.json); fires on tool-use and Stop rather than on a fixed interval; manual TAFE/dispatcher bridge scans available as fallback; retired smart poller and OS poller remain archived
- Bridge operation instructions: Bridge automation has two complementary axes. AXIS 1 (DISPATCHABLE WORK): the dispatcher daemon (`scripts/dispatcher_runtime.py`) is the canonical mechanism for self-contained work â€” reviews, verdicts, tests, work that a freshly-spawned counterpart harness can complete without further owner input. Registered as PostToolUse and Stop hooks. AXIS 2 (NON-DISPATCHABLE WORK): an owner-approved thread automation pattern may wake the interactive chat session to inspect TAFE/dispatcher bridge state and surface work that requires interactive owner input mid-stream â€” owner-AUQ-required decisions, multi-turn review with accumulating context, cross-thread coordination, AUQ-heavy implementation. Both axes are required; their roles do not overlap. Use the `gtkb-bridge` skill (`.claude/skills/bridge/SKILL.md`; Codex adapter `.codex/skills/bridge/SKILL.md`) for proposal/review/verification mechanics. Manual bridge scans remain available as fallback, but they must use TAFE/dispatcher bridge state and versioned bridge files. Do NOT create new bridge automations (Codex-app-side, Claude-side, or otherwise) without owner approval; any new automation must be classified by axis (dispatchable vs non-dispatchable) and inventoried in `config/agent-control/gtkb-system-interface-map.toml`.
- Role mapping source: harness-state/harness-registry.json
- Harness self-identification: B
- Harness identity source: harness-state/harness-identities.json

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
- Full normative block: `config/agent-control/gtkb-session-startup-index.md Â§ Session-context review independence (normative)`.

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
- GT-KB active backlog items: 1
- GT-KB open MemBase work items: 13 (subject-scoped; 907 across all subjects)
- GT-KB dashboard-scoped bridge/contention entries, non-authoritative for queue state: 346
- GT-KB drift changed paths: 4
- GT-KB Testing/tool rollup: 0 failing, 0 manual, 17 ready/passing (queried repo: unknown)
- Active harness role slot: `prime-builder` (prime-builder, loyal-opposition, or shared)
- Harness topology: `multi_harness` (single_harness or multi_harness)
- GT-KB infrastructure posture: package 0.7.0rc1; dry-run upgrade plan available: True
- GT-KB dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: warn (phase-1 catalog parity; operational_readiness=not evaluated; run phase-2 readiness and hook discovery diff; harness=claude, role=loyal-opposition, EXTRA=1, PASS=53, UNSUPPORTED=3)

### Project State Rollup

- Source: MemBase tables: current_work_items + current_project_work_item_memberships grouped by `current_project_work_item_memberships.project_id`.
- Current work items: 5002; non-terminal: 907; active projects: 59; ungrouped non-terminal: 139.
- Status counts: deferred=1, not_a_defect=8, open=906, resolved=3514, retired=446, verified=67, wont_fix=60.
- Active project states:
  - `GTKB-BRIDGE-PROTOCOL-RELIABILITY`: 174 non-terminal (open=174); top: `WI-5686` - ENVELOPE_RESPONDER_BY_STATUS is inverted: dispatchable bridge artifacts carry the author role in the artifact-head ::init line instead of the responder role [open, P0].
  - `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`: 67 non-terminal (open=67); top: `WI-5152` - Implement canonical modernization hard-invariant registry and gate projection [open, P0].
  - `GTKB Deterministic Housekeeping Hardening`: 50 non-terminal (open=50); top: `WI-5696` - Automatically admit new load-bearing artifacts and observe registered edits without notation [open, P0].
  - `GT-KB Working Tree Stabilization`: 44 non-terminal (open=44); top: `WI-5314` - Do not create worker session envelopes for non-spawn dispatcher decisions [open, P0].
  - `Alibaba Cloud Studio Harness (DeepSeek V4 Pro via Anthropic endpoint)`: 39 non-terminal (open=39); top: `WI-5232` - Reissue WI-5216 PAUTH with registered forbidden-operation vocabulary [open, P0].
  - `Dispatcher Black-Box Worker Boundary Hardening`: 33 non-terminal (open=33); top: `WI-5269` - Dispatcher ordinary ops build activity-envelope authority validators [open, P0].
  - `GTKB-RELIABILITY-FIXES`: 32 non-terminal (open=32); top: `WI-5542` - Make Ollama D publisher-only recovery succeed without provider tool_choice enforcement [open, P0].
  - `GT-KB Advisory Corrections 2026-07-29`: 27 non-terminal (open=27); top: `WI-5803` - Project-only authority rule leaves 89 of 111 projects with no controlling authorization (569 of 593 active PAUTHs non-controlling) [open, P0].
  - `Harness Test Corrections`: 27 non-terminal (open=27); top: `WI-5811` - Enforce bridge append-only and compliance gates for non-Claude harness file writes (first live violation evidence) [open, P0].
  - `GT-KB Dispatcher Next Control Plane`: 24 non-terminal (open=24); top: `WI-5617` - Prove the Dispatcher Next durable execution and A2A foundation [open, P0].
  - `GT-KB Modernization: Harness Context Parity`: 21 non-terminal (open=21); top: `WI-5334` - Restore a dispatchable low-cost harness floor required by frozen parity acceptance [open, P0].
  - `GTKB-HARNESS-TRANSCRIPT-DEFECT-INVESTIGATION`: 19 non-terminal (open=19); top: `WI-6164` - Canonical glossary instructs the session-envelope remedy the owner has forbidden [open, P0].
  - `GTKB Obsolete Reference Purge`: 18 non-terminal (open=18); top: `WI-5582` - Remove residual retired-advisory-carrier authority from canonical governance and routing surfaces [open, P1].
  - `GT-KB Timer and Throttle Governance`: 17 non-terminal (open=17); top: `WI-5868` - Externalize registry control-plane lock timing and publication wait policy [open, P0].
  - `GT-KB Modernization: Authority Foundations`: 15 non-terminal (open=15); top: `WI-5178` - Enforce PAUTH allowed-mutation and forbidden-operation bounds at implementation start [open, P0].
  - `GT-KB Modernization: Governed Git Lifecycle and Workflow Drain Control`: 13 non-terminal (open=13); top: `WI-5157` - Prepare two-tier Git lifecycle formal packet and conflicting-authority disposition [open, P0].
  - `GT-KB OPS Dispatcher Modernization`: 13 non-terminal (open=13); top: `WI-5230` - Resolved WI-4978 VERIFIED commit omitted implementation hunks [open, P0].
  - `GT-KB Parallel Operation and Modernization Program`: 10 non-terminal (open=10); top: `WI-5735` - Bridge lifecycle resolver rejects Prime-authored ADVISORY entries, contradicting the role-agnostic advisory decision [open, P1].
  - `PROJECT-GTKB-SESSION-ENVELOPE`: 10 non-terminal (open=10); top: `WI-6073` - Build a governed batch-finalization path clearing accumulated terminal VERIFIED verdicts in one authorized transaction [open, P0].
  - `GT-KB Bridge Protocol Legibility`: 9 non-terminal (open=9); top: `WI-6117` - Phase-distinct bridge vocabulary: resolver + context-free transition relation [open, P1].
  - `GT-KB Get Healthy Recovery Program`: 7 non-terminal (open=7); top: `WI-6184` - Qualify the Get Healthy baseline and produce the Release Re-planning Baseline [open, P0].
  - `GTKB Skill-Rename Reference Sweep`: 7 non-terminal (open=7); top: `WI-5665` - Sweep S4: fix ~25 broken and ~10 silent false-green skill-rename tests [open, P1].
  - `GT-KB Modernization: Artifact Decontamination and Lifecycle`: 6 non-terminal (open=6); top: `WI-5172` - Implement canonical-carrier closure and non-authority evaluator [open, P0].
  - `GT-KB Modernization: Envelope Protocol Architecture`: 6 non-terminal (open=6); top: `WI-5376` - Envelope Protocol Slice D: worker hook injection and harness fallback disposition [open, P0].
  - `PROJECT-GTKB-HARNESS-NEUTRAL-BASELINE`: 6 non-terminal (open=6); top: `WI-5959` - Reconcile three divergent generations of agent-control artifacts [open, P0].
  - `GT-KB Harness Manual PB+LO Parity`: 5 non-terminal (open=5); top: `WI-5916` - Cursor manual PB+LO parity: materialize all skill adapters + Prime Builder rule + role switching [open, P0].
  - `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI`: 5 non-terminal (open=5); top: `WI-5284` - Populate canonical dispatch metrics snapshots from live dispatcher telemetry [open, P1].
  - `GT-KB Timer and Throttle Governance`: 4 non-terminal (open=4); top: `WI-5875` - Externalize and tune the Ollama guard subprocess timeout [open, P1].
  - `GTKB-MEMBASE-HYGIENE`: 4 non-terminal (open=4); top: `WI-5855` - Runtime residue is 138 GB / 1.85M files (.pytest-tmp 124.6 GB, .gtkb-state 11.3 GB); census cost makes gt project doctor take 29 minutes [open, P1].
  - `implementation-authorization`: 4 non-terminal (open=4); top: `WI-5382` - Make implementation-start begin fail loudly or publish its named schema-v3 packet [open, P0].
  - `Advisory Proposal Envelope Scaffold`: 3 non-terminal (open=3); top: `WI-5263` - Teach Advisory Proposal semantics in generated role and startup scaffolds [open, P1].
  - `bridge-proposal-filing`: 3 non-terminal (open=3); top: `WI-5466` - Expose governed Prime NO-ACTION publication through gt bridge CLI [open, P0].
  - `GT-KB Modernization: Registry-Derived Context Manifests`: 3 non-terminal (open=3); top: `WI-5170` - Implement registry-derived session and activity context manifests [open, P0].
  - `GT-KB Modernization: Runtime Context and Uniform Interfaces`: 3 non-terminal (open=3); top: `WI-5086` - Interactive Prime session mis-gated as Loyal Opposition when per-session role-marker write fails [open, P1].
  - `GT-KB Registry Coverage-Model Refinement`: 3 non-terminal (open=3); top: `WI-5925` - Recursive-container coverage for high-churn test trees; restore registry membership_complete [open, P1].
  - `GTKB Dispatcher Reliability`: 3 non-terminal (open=3); top: `WI-6090` - Codex scan_bridge.py --role prime-builder processes leak: six accumulated over ~1 hour without exiting, contributing to control-plane lock contention [open, P2].
  - `GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE`: 3 non-terminal (open=3); top: `WI-5568` - Session-stated role override not honored after context-refresh SessionStart re-derivation [open, P0].
  - `Harness Parity Phase 2`: 3 non-terminal (open=3); top: `WI-5246` - Classify active harness event-source capability gaps in Phase 2 parity [open, P2].
  - `PROJECT-GTKB-GOOSE-RELIABILITY`: 3 non-terminal (open=3); top: `WI-6104` - Goose shell tool long-command discipline: stream-drain false timeouts, no backgrounding, 300s default [open, P1].
  - `Bridge Protocol Reliability`: 2 non-terminal (open=2); top: `WI-5898` - Repair WI-5741 invalid PB-authored terminal bridge chain without erasing evidence [open, P0].
  - `GT-KB Orphaned VERIFIED Evidence Preservation`: 2 non-terminal (open=2); top: `WI-6160` - Allow VERIFIED finalization to explicitly suppress unrelated project auto-retirement [open, P0].
  - `GT-KB Skill Activation and Enforcement`: 2 non-terminal (open=2); top: `WI-5194` - Fix .jsonl prose-path truncation in proposal target preflight [open, P1].
  - `GTKB-BRIDGE`: 2 non-terminal (open=2); top: `WI-5756` - Harden LO/PB bridge scan + backlog CLIs for loop-cadence latency [open, P1].
  - `Reusable Direct-Cloud Harness Template`: 2 non-terminal (open=2); top: `WI-5726` - Add shared worker system-prompt composer to cloud_harness_base [open, P2].
  - `bridge-observability`: 1 non-terminal (open=1); top: `WI-5753` - Bridge queue-read CLI: false-empty schema divergence, unresolvable 20-item bound, no recency field, and shim cannot carry multi-line or JSON-array args [open, P1].
  - `DISPATCHER-COMPLEX-CLI`: 1 non-terminal (open=1); top: `WI-5896` - Execute the live dispatch_events migration with snapshot, bounded quiescence, and recovery proof [open, P1].
  - `GT-KB Git Object-Store Reclamation`: 1 non-terminal (open=1); top: `WI-6138` - develop is permanently unpushable: 58 commits carry 460MB groundtruth.db blobs, GitHub GH001 hard-rejects [open, P0].
  - `GT-KB Git Object-Store Reclamation`: 1 non-terminal (open=1); top: `WI-5431` - Recurring .git object-store bloat from re-hashed tracked groundtruth.db (~5 GB/day regrowth; 441 GB outage precedent) [open, P1].
  - `GT-KB Goose Harness Adoption`: 1 non-terminal (open=1); top: `WI-5731` - Goose harness ships skill adapters with no hook or guard registration, leaving an ungated write path [open, P1].
  - `GT-KB Housekeeping Hardening`: 1 non-terminal (open=1); top: `WI-6186` - Purge TAFE dispatcher config from worker-facing gt bridge state-report and gt harness roles output [open, P3].
  - `GT-KB OPS Dispatcher Modernization`: 1 non-terminal (open=1); top: `WI-5239` - Fresh-recipient document reroute control for dispatcher recovery [open, P2].
  - `GT-KB Platform Modernization`: 1 non-terminal (open=1); top: `WI-5137` - Define and file the Platform Modernization umbrella proposal [open, P1].
  - `GT-KB Project Authorization Lifecycle Fusion`: 1 non-terminal (open=1); top: `WI-5781` - Fuse project creation and authorization into one atomic gt projects transaction (AT-03) [open, P0].
  - `GT-KB Runtime Orchestration Discovery`: 1 non-terminal (open=1); top: `WI-4851` - Author GT-KB factory<->agent-standard Rosetta-Stone mapping ADR (vocabulary alignment, Option A) [open, P3].
  - `GTKB-DASHBOARD-OBSERVABILITY`: 1 non-terminal (deferred=1); top: `GTKB-DASHBOARD-RETENTION` - Dashboard history retention policy (contingent) [deferred, order 1010].
  - `Harness Test`: 1 non-terminal (open=1); top: `WI-5808` - Stress-test the assigned Prime Builder through one full governed implementation cycle (harness capability probe) [open, P0].
  - `Ollama Direct-Cloud Harness (Anthropic-compatible, full hooks)`: 1 non-terminal (open=1); top: `WI-5075` - More complete hook support for the Ollama Kimi harness integration [open, P3].
  - `PROJECT-GTKB-AGENT-DIRECTION-BASELINE-REMEDIATION`: 1 non-terminal (open=1); top: `WI-6040` - T0: mechanism repair and discovery for the Agent-Direction Baseline Remediation program [open, P1].
  - `session-startup-latency`: 1 non-terminal (open=1); top: `WI-5671` - WI-5650 Slice B: startup-relay fix - fail open on stale-but-valid cache + detached background refresh (replace 5s-capped synchronous self-heal) [open, P2].

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

1. **WI-5152**: Implement canonical modernization hard-invariant registry and gate projection (priority: P0)
2. **WI-5154**: Add lifecycle-aware current formal-artifact scanning to hygiene inventory (priority: P0)
3. **WI-5157**: Prepare two-tier Git lifecycle formal packet and conflicting-authority disposition (priority: P0)