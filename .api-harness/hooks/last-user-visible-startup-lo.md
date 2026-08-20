# GroundTruth-KB Fresh Session Startup

Generated: 2026-08-18T19:34:04Z
Dashboard: GroundTruth-KB Project Dashboard: [http://localhost:3000/d/gtkb/groundtruth-kb-dashboard](http://localhost:3000/d/gtkb/groundtruth-kb-dashboard)

## Startup Disclosure

### Role And Governance Stance

- Role being assumed: Loyal Opposition
- Interactive resolved role: Loyal Opposition
- Interactive role source: startup disclosure cache role mode lo; authoritative only when selected by the owner transcript/init-keyword path
- Role assignment: active AI harness assigned by owner through single role map entry for harness `B`
- Bridge: always available through TAFE/dispatcher state plus versioned bridge files and checked at session startup
- Bridge dispatch: dispatcher daemon registered as PostToolUse and Stop hooks (.api-harness/settings.json, .api-harness/hooks.json, .cursor/hooks.json); fires on tool-use and Stop rather than on a fixed interval; manual TAFE/dispatcher bridge scans available as fallback; retired smart poller and OS poller remain archived
- Bridge operation instructions: Bridge automation has two complementary axes. AXIS 1 (DISPATCHABLE WORK): the dispatcher daemon (`scripts/dispatcher_runtime.py`) is the canonical mechanism for self-contained work â€” reviews, verdicts, tests, work that a freshly-spawned counterpart harness can complete without further owner input. Registered as PostToolUse and Stop hooks. AXIS 2 (NON-DISPATCHABLE WORK): an owner-approved thread automation pattern may wake the interactive chat session to inspect TAFE/dispatcher bridge state and surface work that requires interactive owner input mid-stream â€” owner-AUQ-required decisions, multi-turn review with accumulating context, cross-thread coordination, AUQ-heavy implementation. Both axes are required; their roles do not overlap. Use the `gtkb-bridge` skill (`.api-harness/skills/bridge/SKILL.md`; Codex adapter `.api-harness/skills/bridge/SKILL.md`) for proposal/review/verification mechanics. Manual bridge scans remain available as fallback, but they must use TAFE/dispatcher bridge state and versioned bridge files. Do NOT create new bridge automations (Codex-app-side, Claude-side, or otherwise) without owner approval; any new automation must be classified by axis (dispatchable vs non-dispatchable) and inventoried in `config/agent-control/gtkb-system-interface-map.toml`.
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
- Browser opening: use the harness-controlled browser for live dashboard inspection; startup open request: disabled; current mode: `harness_browser`. Startup hooks must not launch the operating system default browser unless explicitly configured with `dashboard_open_mode: system_default_browser`.
- KPI coverage: GT-KB backlog, MemBase work items, Deliberation Archive records, tests, specifications, drift, regression, contention, and tokens consumed at session start before user input.
- Dashboard scope: GroundTruth-KB project dashboard.
- Token measurement status: not_exposed_by_current_harness
- Tokens consumed before user input: unavailable

### Current Project State

- GT-KB release blockers: 0
- GT-KB active backlog items: 1
- GT-KB open MemBase work items: 6 (subject-scoped; 1024 across all subjects)
- GT-KB dashboard-scoped bridge/contention entries, non-authoritative for queue state: 312
- GT-KB drift changed paths: 46
- GT-KB Testing/tool rollup: 0 failing, 0 manual, 15 ready/passing (queried repo: unknown)
- Active harness role slot: `prime-builder` (prime-builder, loyal-opposition, or shared)
- Harness topology: `multi_harness` (single_harness or multi_harness)
- GT-KB infrastructure posture: package 0.7.0rc1; dry-run upgrade plan available: True
- GT-KB dev environment inventory: stale; generated 2026-05-08T19:04:30Z; redaction pass
- Harness parity: warn (phase-1 catalog parity; operational_readiness=not evaluated; run phase-2 readiness and hook discovery diff; harness=claude, role=loyal-opposition, EXTRA=1, PASS=53, UNSUPPORTED=4)

### Project State Rollup

- Source: MemBase tables: current_work_items + current_project_work_item_memberships grouped by `current_project_work_item_memberships.project_id`.
- Current work items: 5436; non-terminal: 1024; active projects: 86; ungrouped non-terminal: 118.
- Status counts: deferred=1, not_a_defect=9, open=1023, resolved=3597, retired=585, verified=67, wont_fix=154.
- Active project states:
  - `GTKB-BRIDGE-PROTOCOL-RELIABILITY`: 195 non-terminal (open=195); top: `WI-5686` - Preserve next-responder hook-marker semantics while retiring the status-first artifact-head envelope [open, P0].
  - `GET HEALTHY PHASE 3`: 126 non-terminal (open=126); top: `WI-5953` - Failed VERIFIED finalization leaves an orphaned terminal verdict when compensation cannot restore the bridge aggregate preimage, false-terminaling the thread [open, P0].
  - `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`: 55 non-terminal (open=55); top: `WI-5152` - Implement canonical modernization hard-invariant registry and gate projection [open, P0].
  - `GTKB Deterministic Housekeeping Hardening`: 43 non-terminal (open=43); top: `WI-5696` - Automatically admit new load-bearing artifacts and observe registered edits without notation [open, P0].
  - `GET HEALTHY PHASE 2`: 36 non-terminal (open=36); top: `WI-6220` - Qualify the clean neutral source with fresh-agent behavioral tests [open, P0].
  - `GT-KB Working Tree Stabilization`: 26 non-terminal (open=26); top: `WI-5317` - Recover and finalize orphaned WI-4978 compliance-audit source hunks [open, P0].
  - `GTKB Obsolete Reference Purge`: 26 non-terminal (open=26); top: `WI-6016` - Purge blocking-on-audit ceremony from live agent-facing surfaces so audit is best-effort, not a work gate [open, P0].
  - `Alibaba Cloud Studio Harness (DeepSeek V4 Pro via Anthropic endpoint)`: 24 non-terminal (open=24); top: `WI-5232` - Reissue WI-5216 PAUTH with registered forbidden-operation vocabulary [open, P0].
  - `GTKB-RELIABILITY-FIXES`: 22 non-terminal (open=22); top: `WI-5542` - Make Ollama D publisher-only recovery succeed without provider tool_choice enforcement [open, P0].
  - `GT-KB New Work Intake`: 21 non-terminal (open=21); top: `WI-5183` - Add an authority-correct CAS test-artifact update service [open, P0].
  - `DATABASE MIGRATION - Activation Bundle 2`: 20 non-terminal (open=20); top: `WI-5618` - Formalize Dispatcher Next authority, worker isolation, packet, routing, and migration architecture [open, P0].
  - `GT-KB Modernization: Harness Context Parity`: 18 non-terminal (open=18); top: `WI-5912` - Cursor hook adapter silently downgrades structured deny/ask to advisory context, failing four gates open [open, P0].
  - `Harness Test Corrections`: 18 non-terminal (open=18); top: `WI-5811` - Enforce bridge append-only and compliance gates for non-Claude harness file writes (first live violation evidence) [open, P0].
  - `Dispatcher Black-Box Worker Boundary Hardening`: 17 non-terminal (open=17); top: `WI-5271` - Deliver complete worker-safe action packets without raw bridge or predecessor-session dependency [open, P0].
  - `GT-KB Advisory Corrections 2026-07-29`: 15 non-terminal (open=15); top: `WI-5761` - Enforce project reactivation invariant: completed_at must be cleared by owner-evidenced reactivation [open, P1].
  - `GT-KB Modernization: Authority Foundations`: 14 non-terminal (open=14); top: `WI-5282` - Replace deliberation-dependent PAUTH approval with intrinsic exact-envelope approval [open, P0].
  - `GTKB-HARNESS-TRANSCRIPT-DEFECT-INVESTIGATION`: 14 non-terminal (open=14); top: `WI-6164` - Canonical glossary instructs the session-envelope remedy the owner has forbidden [open, P0].
  - `GT-KB Modernization: Governed Git Lifecycle and Workflow Drain Control`: 12 non-terminal (open=12); top: `WI-5158` - Implement governed project and work-item branch binding with wrong-branch fail closed [open, P0].
  - `GT-KB Timer and Throttle Governance`: 12 non-terminal (open=12); top: `WI-5868` - Externalize registry control-plane lock timing and publication wait policy [open, P0].
  - `GT-KB Bridge Protocol Legibility`: 11 non-terminal (open=11); top: `WI-6117` - Phase-distinct bridge vocabulary: resolver + context-free transition relation [open, P1].
  - `DATABASE MIGRATION`: 10 non-terminal (open=10); top: `WI-6246` - DATABASE MIGRATION program charter and portfolio graph [open, P0].
  - `GET HEALTHY PHASE 2`: 9 non-terminal (open=9); top: `WI-6232` - Goose projection: full native skill bodies, rules, hooks surface, correct manifest generator, registry capability block [open, P0].
  - `GT-KB OPS Dispatcher Modernization`: 9 non-terminal (open=9); top: `WI-5230` - Resolved WI-4978 VERIFIED commit omitted implementation hunks [open, P0].
  - `GT-KB Parallel Operation and Modernization Program`: 9 non-terminal (open=9); top: `WI-5735` - Bridge lifecycle resolver rejects Prime-authored ADVISORY entries, contradicting the role-agnostic advisory decision [open, P1].
  - `GT-KB Get Healthy Recovery Program`: 8 non-terminal (open=8); top: `WI-6184` - Qualify the Get Healthy baseline and produce the Release Re-planning Baseline [open, P0].
  - `Bridge Contention L3: Gate Races`: 7 non-terminal (open=7); top: `WI-6411` - Bridge work-intent claim leases block legitimate work: TTL expires mid-review and divergent session-id resolution makes a session collide with its own claim [open, P1].
  - `GTKB-MEMBASE-HYGIENE`: 7 non-terminal (open=7); top: `WI-5855` - Runtime residue is 138 GB / 1.85M files (.pytest-tmp 124.6 GB, .gtkb-state 11.3 GB); census cost makes gt project doctor take 29 minutes [open, P1].
  - `PROJECT-GTKB-SESSION-ENVELOPE`: 7 non-terminal (open=7); top: `WI-5935` - Session envelope must be single-session-context constrained (uniform across all harnesses); ::wrap must not cross session-contexts [open, P1].
  - `DATABASE MIGRATION - Activation Bundle 1`: 6 non-terminal (open=6); top: `WI-6247` - PostgreSQL authority architecture and formal seed [open, P0].
  - `Harness-Neutral Baseline and Projection Corrective Program`: 6 non-terminal (open=6); top: `WI-5964` - Implement DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001 Decision 4 storage repointing [open, P0].
  - `GT-KB Dispatcher Next Control Plane`: 5 non-terminal (open=5); top: `WI-AUTO-SPEC-INTAKE-528AB1` - Implement SPEC-INTAKE-528ab1: Counterpart harness identity is low-salience bookkeeping; counterpart role is the foregrounded identity [open, P2].
  - `GTKB Skill-Rename Reference Sweep`: 5 non-terminal (open=5); top: `WI-5665` - Sweep S4: fix ~25 broken and ~10 silent false-green skill-rename tests [open, P1].
  - `ADBR T0 - Inventory and structural sanitation`: 4 non-terminal (open=4); top: `WI-5959` - T0: enforce one canonical neutral source and eliminate competing source cues [open, P0].
  - `bridge-observability`: 4 non-terminal (open=4); top: `WI-5753` - Bridge queue-read CLI: false-empty schema divergence, unresolvable 20-item bound, no recency field, and shim cannot carry multi-line or JSON-array args [open, P1].
  - `GT-KB Harness Manual PB+LO Parity`: 4 non-terminal (open=4); top: `WI-5916` - Cursor manual PB+LO parity: materialize all skill adapters + Prime Builder rule + role switching [open, P0].
  - `GT-KB Modernization: Artifact Decontamination and Lifecycle`: 4 non-terminal (open=4); top: `WI-5172` - Implement canonical-carrier closure and non-authority evaluator [open, P0].
  - `GT-KB Timer and Throttle Governance`: 4 non-terminal (open=4); top: `WI-5875` - Externalize and tune the Ollama guard subprocess timeout [open, P1].
  - `implementation-authorization`: 4 non-terminal (open=4); top: `WI-5382` - Make implementation-start begin fail loudly or publish its named schema-v3 packet [open, P0].
  - `Advisory Proposal Envelope Scaffold`: 3 non-terminal (open=3); top: `WI-5263` - Teach Advisory Proposal semantics in generated role and startup scaffolds [open, P1].
  - `GT-KB Modernization: Runtime Context and Uniform Interfaces`: 3 non-terminal (open=3); top: `WI-5086` - Interactive Prime session mis-gated as Loyal Opposition when per-session role-marker write fails [open, P1].
  - `GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE`: 3 non-terminal (open=3); top: `WI-5568` - Session-stated role override not honored after context-refresh SessionStart re-derivation [open, P0].
  - `Harness Parity Phase 2`: 3 non-terminal (open=3); top: `WI-5246` - Classify active harness event-source capability gaps in Phase 2 parity [open, P2].
  - `Sole Projection Engine, CLI, and Target Qualification`: 3 non-terminal (open=3); top: `WI-5960` - Build and qualify the sole harness projection engine [open, P0].
  - `Backlog Triage and Hygiene`: 2 non-terminal (open=2); top: `WI-6413` - gt backlog update exposes --related-bridge-threads, inviting ephemeral bridge paths to be stored inside a source-of-truth record [open, P1].
  - `bridge-proposal-filing`: 2 non-terminal (open=2); top: `WI-5466` - Expose governed Prime NO-ACTION publication through gt bridge CLI [open, P0].
  - `GT-KB Git Object-Store Reclamation`: 2 non-terminal (open=2); top: `WI-6138` - develop is permanently unpushable: 58 commits carry 460MB groundtruth.db blobs, GitHub GH001 hard-rejects [open, P0].
  - `GT-KB Modernization: Registry-Derived Context Manifests`: 2 non-terminal (open=2); top: `WI-5141` - Decompose Context Manifests modernization packages [open, P1].
  - `GT-KB Working Tree Stabilization`: 2 non-terminal (open=2); top: `WI-6535` - Uncommitted shared-worktree code is an unversioned cross-session deploy that can retroactively change gate authority [open, P0].
  - `GTKB-BRIDGE`: 2 non-terminal (open=2); top: `WI-5756` - Harden LO/PB bridge scan + backlog CLIs for loop-cadence latency [open, P1].
  - `Harness Test`: 2 non-terminal (open=2); top: `WI-5808` - Stress-test the assigned Prime Builder through one full governed implementation cycle (harness capability probe) [open, P0].
  - `Neutral Source Readiness and Reference Closure`: 2 non-terminal (open=2); top: `WI-6314` - Amend existing harness baseline projection GOV, REQ, and conformance DCL [open, P0].
  - `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI`: 2 non-terminal (open=2); top: `WI-5295` - Make bridge WI lookup include governed secondary work-item links [open, P1].
  - `Reusable Direct-Cloud Harness Template`: 2 non-terminal (open=2); top: `WI-5726` - Add shared worker system-prompt composer to cloud_harness_base [open, P2].
  - `Work-Tree Hygiene`: 2 non-terminal (open=2); top: `WI-6510` - Eighty stray session scratch scripts accumulated at the repository root across five prior sessions, thirty-seven of them not ignored [open, P2].
  - `ADBR T1 - Neutral rules and behavioral contracts`: 1 non-terminal (open=1); top: `WI-6240` - T1: correct every harness-neutral rule and behavioral contract [open, P0].
  - `ADBR T2 - Neutral descriptors, schemas, and commands`: 1 non-terminal (open=1); top: `WI-6241` - T2: correct neutral descriptors, schemas, commands, and source manifests [open, P0].
  - `ADBR T3 - Startup and root guidance consumers`: 1 non-terminal (open=1); top: `WI-6242` - T3: correct startup and root guidance that consumes the neutral baseline [open, P0].
  - `ADBR T4 - Neutral skills, references, and helpers`: 1 non-terminal (open=1); top: `WI-6243` - T4: correct every neutral skill, reference, and helper [open, P0].
  - `ADBR T5 - Neutral hooks, plugins, and prompts`: 1 non-terminal (open=1); top: `WI-6244` - T5: correct neutral hooks, plugins, and embedded behavioral prompts [open, P0].
  - `ADBR T6 - Neutral templates and scaffolds`: 1 non-terminal (open=1); top: `WI-6245` - T6: correct templates and scaffolds to consume the clean neutral baseline [open, P0].
  - `Agent-Direction Baseline Content Remediation`: 1 non-terminal (open=1); top: `WI-6289` - Canonical agent direction contradicts enforced mechanism across four advisory-filing surfaces [open, P2].
  - `Backlog Triage and Hygiene`: 1 non-terminal (open=1); top: `WI-6571` - Work-item retirement triage has no safe criterion: heuristic bulk retirement produced four documented reversals while superseded_by/supersedes columns sit unpopulated [open, P1].
  - `Bridge Contention L2: Dispatch`: 1 non-terminal (open=1); top: `WI-6409` - Two Prime Builder sessions filed competing bridge threads for one work item with overlapping target_paths and no collision detection [open, P1].
  - `Bridge Protocol Reliability`: 1 non-terminal (open=1); top: `WI-6588` - Sibling incident-recovery items dispositioned inconsistently: WI-5898 marked canon-contrary, identical WI-5907 left unmarked [open, P2].
  - `canonical-artifact-hygiene`: 1 non-terminal (open=1); top: `WI-6434` - Session handoff-prompt service has no live spec while the glossary and SPEC-0807 still depend on it [open, P2].
  - `GET HEALTHY PHASE 3`: 1 non-terminal (open=1); top: `WI-6643` - scan_bridge classifies latest ADVISORY as Prime-actionable queue work [open, P1].
  - `GT-KB Git Object-Store Reclamation`: 1 non-terminal (open=1); top: `WI-5431` - Recurring .git object-store bloat from re-hashed tracked groundtruth.db (~5 GB/day regrowth; 441 GB outage precedent) [open, P1].
  - `GT-KB Goose Harness Adoption`: 1 non-terminal (open=1); top: `WI-5731` - Goose harness ships skill adapters with no hook or guard registration, leaving an ungated write path [open, P1].
  - `GT-KB Modernization: Envelope Protocol Architecture`: 1 non-terminal (open=1); top: `WI-6566` - Repair ::open activity-envelope context delivery: router path bypasses governed packet budget [open, P1].
  - `GT-KB Orphaned VERIFIED Evidence Preservation`: 1 non-terminal (open=1); top: `WI-6148` - Preserve orphaned VERIFIED verdict originals as tracked forensic evidence [open, P1].
  - `GT-KB Platform Modernization`: 1 non-terminal (open=1); top: `WI-5137` - Define and file the Platform Modernization umbrella proposal [open, P1].
  - `GT-KB Project Authorization Lifecycle Fusion`: 1 non-terminal (open=1); top: `WI-5781` - Fuse project creation and authorization into one atomic gt projects transaction (AT-03) [open, P0].
  - `GT-KB Registry Coverage-Model Refinement`: 1 non-terminal (open=1); top: `WI-5931` - KB-mutation completeness guard does not distinguish registry-projection runtime_state writes from MemBase canonical mutation [open, P3].
  - `GT-KB Runtime Orchestration Discovery`: 1 non-terminal (open=1); top: `WI-4851` - Author GT-KB factory<->agent-standard Rosetta-Stone mapping ADR (vocabulary alignment, Option A) [open, P3].
  - `GT-KB Skill Activation and Enforcement`: 1 non-terminal (open=1); top: `WI-5194` - Fix .jsonl prose-path truncation in proposal target preflight [open, P1].
  - `GTKB Dispatcher Reliability`: 1 non-terminal (open=1); top: `WI-6090` - Codex scan_bridge.py --role prime-builder processes leak: six accumulated over ~1 hour without exiting, contributing to control-plane lock contention [open, P2].
  - `GTKB-DASHBOARD-OBSERVABILITY`: 1 non-terminal (deferred=1); top: `GTKB-DASHBOARD-RETENTION` - Dashboard history retention policy (contingent) [deferred, order 1010].
  - `Ollama Direct-Cloud Harness (Anthropic-compatible, full hooks)`: 1 non-terminal (open=1); top: `WI-5075` - More complete hook support for the Ollama Kimi harness integration [open, P3].
  - `Project Authorization Model Correction`: 1 non-terminal (open=1); top: `WI-6619` - Purge program as authority-bearing language, retaining it only as planning vocabulary [open, P2].
  - `PROJECT-GTKB-DISPATCHER-NEXT`: 1 non-terminal (open=1); top: `WI-6284` - Absorb proposer-routing recommendations into Dispatcher Next authority and scheduler policy [open, P2].
  - `PROJECT-GTKB-GOOSE-RELIABILITY`: 1 non-terminal (open=1); top: `WI-6103` - Goose provider/model config: max_tokens truncation + tool-name misuse repair [open, P2].
  - `publication-linearizability`: 1 non-terminal (open=1); top: `WI-6401` - Bridge version number is baked into the document body at authoring time, so a concurrent publication invalidates completed work product (TOCTOU) [open, P1].
  - `publication-linearizability`: 1 non-terminal (open=1); top: `WI-6471` - Bridge verdict publication aborts on a concurrent file deletion in an UNRELATED thread (cross-thread TOCTOU) [open, P1].
  - `recurring-runtime-dirt`: 1 non-terminal (open=1); top: `WI-6638` - Protect GO'd uncommitted package sources from silent groundtruth-kb tree replacement [open, P0].
  - `session-startup-latency`: 1 non-terminal (open=1); top: `WI-5671` - WI-5650 Slice B: startup-relay fix - fail open on stale-but-valid cache + detached background refresh (replace 5s-capped synchronous self-heal) [open, P2].
  - `Work-Tree Hygiene`: 1 non-terminal (open=1); top: `WI-6418` - Destructive-operation guard matches command text not the operation, blocking cleanup and its own defect report [open, P1].

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
- Canonical state file: `.api-harness/session/work-subject.json` (legacy `.api-harness/hooks/.workstream-focus-state.json` migrated on next owner command).
- Counterpart harness detected; no role or subject conflicts.

### Top Priority Actions

1. **WI-5152**: Implement canonical modernization hard-invariant registry and gate projection (priority: P0)
2. **WI-5158**: Implement governed project and work-item branch binding with wrong-branch fail closed (priority: P0)
3. **WI-5159**: Implement project-to-develop and develop-to-stage promotion gates (priority: P0)