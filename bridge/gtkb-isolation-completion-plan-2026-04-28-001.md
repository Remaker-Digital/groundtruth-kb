# Bridge Proposal — GT-KB Isolation Completion Plan (2026-04-28)

**Status:** NEW (version 001 — comprehensive scoping for owner verification)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-isolation-completion-plan-2026-04-28`
**Scope:** This is the canonical implementation proposal for completing the GT-KB platform vs. Agent Red application separation. Owner directive 2026-04-28: produce a plan detailed enough to verify before any further execution.

**Important:** This proposal does NOT execute work. It is a contract. Once owner-verified, subsequent bridges (Phase 1 implementation, Phase 2 implementation, etc.) execute slices of it.

---

## Section 0 — Why This Proposal Exists

### 0.1 The owner's stated concern

> "We have been trying to complete this GT-KB isolation project for several days. I continue to discover issues with the execution of the plan. I do not know why we are experiencing a loss of control and coherence between sessions. This work has undermined the value of GT-KB."

### 0.2 Honest assessment of why coherence has been lost

Five concrete root causes, ranked by impact:

1. **No canonical "what GT-KB is" document.** CLAUDE.md, MEMORY.md, AGENTS.md, work_list.md, CLAUDE-ARCHITECTURE.md, and dozens of bridge prose files all describe the project in terms that mix "Agent Red is the project" with "GT-KB is the project." Each new session reads a subset of these and reconstructs a slightly different mental model. A platform with applications cannot be coherent if its own self-description is ambiguous.

2. **The "Agent Red is primary" framing was baked into governance early.** When CLAUDE.md was written, Agent Red was the immediate priority. GT-KB was described as "implementation infrastructure" (e.g., AR-DASH-001 made the dashboard about Agent Red). That was true at the time. It is not true now. But the framing persists in dozens of files until it is mechanically corrected.

3. **The bridge protocol scopes well to incremental code changes, poorly to architectural decisions.** Bridge proposals enforce single-purpose discipline (which is good for code) but make it difficult to file an architecture-defining document (which is what's needed here). Architectural decisions have been made in conversational dialogue across sessions and then partially captured in scattered DELIB records. There is no single source of truth for "what the platform model IS."

4. **Infrastructure breakage masked the structural problem.** The `groundtruth_kb` Python API has been broken since S315 (the editable package was uninstalled to satisfy the project-root-boundary directive, but the source was at `E:\Claude-Playground\` outside the boundary). Sessions worked around symptoms (assertion-check fails → mark blocked; harvest fails → defer) without confronting the structural cause: the framework had no in-boundary home.

5. **Sessions inherit work_list rows that reference "upstream in groundtruth-kb"** for ~3 work items (DB-BACKUP-001, BRIDGE-POLLER-001, ARTIFACT-RECORDER-CLI). Those references pointed to the now-archived external checkout. Each session accepted them as actionable; none surfaced that the "upstream" had no path.

### 0.3 What this proposal does to prevent recurrence

Three structural fixes embedded in the deliverable:

- **Single canonical platform-spec document.** Section 2 of this proposal IS the platform specification. Once owner-verified, CLAUDE.md and MEMORY.md collapse to thin pointers at this document.
- **Machine-verifiable manifest.** Section 1's inventory is structured. After implementation, a tool (`gt platform doctor` or similar) can audit the actual disk state against the manifest and report drift in seconds.
- **Owner-verified-before-execution gate.** The proposal must reach VERIFIED status before any of its phases execute. If subsequent sessions try to execute the plan from memory, the bridge protocol will reject the implementation without a citation back to this document.

### 0.4 What this proposal is NOT

- Not a Python package design proposal for `groundtruth-kb` itself (the framework code is the framework's own concern).
- Not a roadmap for Agent Red's commercial features.
- Not an immediate execution plan — it's the contract that subsequent execution slices reference.
- Not a partial fix — the goal is one document covering all 6 questions the owner asked, plus the meta-question about coherence.

---

## Section 1 — Current State Inventory

### 1.1 GT-KB Platform Artifacts (currently on this workstation)

The following exist on this workstation and are GT-KB platform-level (regardless of where they currently live). After restructure, all of these belong at `E:\GT-KB\` directly or under platform-specific subdirectories within it.

#### 1.1.1 Framework source code (currently at `E:\GT-KB\groundtruth-kb\`, must move to `E:\GT-KB\`)

| Current path | Target path | Type | Notes |
|---|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/` | `src/groundtruth_kb/` | dir | Python package — 50+ modules including `cli.py`, `bootstrap.py`, `db.py`, `dashboard.py`, `bridge/`, `governance/`, `project/`, `web/`, etc. |
| `groundtruth-kb/pyproject.toml` | `pyproject.toml` | file | Framework build config — defines `gt` console script, package metadata, dependencies, optional `[web]`, `[bridge]`, `[search]`, `[dev]`, `[docs]` extras |
| `groundtruth-kb/Makefile` | `Makefile` | file | Framework dev commands |
| `groundtruth-kb/.editorconfig` | `.editorconfig` | file | Editor config |
| `groundtruth-kb/.pre-commit-config.yaml` | `.pre-commit-config.yaml` | file | Pre-commit hooks |
| `groundtruth-kb/.github/` | `.github/` | dir | GitHub Actions CI workflows + issue templates (will need careful merge with existing `.github/`) |
| `groundtruth-kb/tests/` | `tests/` | dir | 60+ framework tests (replaces current root-level tests/ which is Agent Red's) |
| `groundtruth-kb/docs/` | `docs/` | dir | Framework documentation (mkdocs) — replaces current root-level docs/ |
| `groundtruth-kb/templates/` | `templates/` | dir | Project scaffold templates: `templates/hooks/`, `templates/rules/`, `templates/skills/`, `templates/ci/`, `templates/project/`, `managed-artifacts.toml` |
| `groundtruth-kb/scripts/` | `scripts/framework/` | dir | Framework utility scripts: `audit_docstrings.py`, `audit_types.py`, `check_doc_links.py`, `collect_evidence_metrics.py`, etc. |
| `groundtruth-kb/examples/` | `examples/` | dir | Reference applications: `task-tracker/` (the canonical example app) |
| `groundtruth-kb/evidence/` | `evidence/` | dir | Framework evidence artifacts |
| `groundtruth-kb/mkdocs.yml` | `mkdocs.yml` | file | Documentation site config |
| `groundtruth-kb/sonar-project.properties` | `sonar-project.properties` | file | SonarCloud config |
| `groundtruth-kb/CHANGELOG.md` | `CHANGELOG.md` | file | Framework changelog (replaces current root CHANGELOG.md which is Agent Red's) |
| `groundtruth-kb/CODE_OF_CONDUCT.md` | `CODE_OF_CONDUCT.md` | file | OSS metadata |
| `groundtruth-kb/CONTRIBUTING.md` | `CONTRIBUTING.md` | file | OSS metadata (replaces current root CONTRIBUTING.md which is Agent Red's) |
| `groundtruth-kb/LICENSE` | `LICENSE` | file | OSS license |
| `groundtruth-kb/README.md` | `README.md` | file | Framework README (replaces current root README.md which describes Agent Red) |
| `groundtruth-kb/SECURITY.md` | `SECURITY.md` | file | OSS metadata |
| `groundtruth-kb/release-notes-*.md` | `release-notes/` | dir | Release notes for v0.6.0, v0.6.1 |

#### 1.1.2 Platform infrastructure already at the GT-KB root (stays where it is)

| Path | Type | Description |
|---|---|---|
| `.claude/hooks/` | dir | All platform hooks: `assertion-check.py`, `credential-scan.py`, `destructive-gate.py`, `formal-artifact-approval-gate.py`, `owner-decision-tracker.py`, `scheduler.py`, `spec-classifier.py`, `workstream-focus.py`, `_delib_common.py` |
| `.claude/skills/` | dir | All platform skills: 30+ skills including `bridge-propose/`, `decision-capture/`, `kb-*`, `release-candidate-gate/`, `proposal-review/`, etc. |
| `.claude/rules/` | dir | All platform rules: `acting-prime-builder.md`, `bridge-essential.md`, `codex-review-gate.md`, `deliberation-protocol.md`, `file-bridge-protocol.md`, `loyal-opposition.md`, `operating-role.md`, `prime-builder-role.md`, `project-root-boundary.md`, `report-depth-prime-builder-context.md` |
| `.claude/agents/` | dir | Platform agent definitions |
| `.claude/commands/` | dir | Platform custom commands |
| `.claude/plans/` | dir | Planning templates |
| `.claude/settings.json`, `settings.local.json`, `launch.json` | files | Platform settings |
| `.claude/SCHEDULE.md` | file | Deliberation schedule |
| `.codex/config.toml`, `hooks.json` | files | Codex configuration |
| `.codex/gtkb-hooks/` | dir | Codex hook dispatchers (recently renamed from `agent-red-hooks/` by Codex) |
| `.github/` | dir | CI workflows |
| `.githooks/` | dir | Git hook scripts |
| `.groundtruth/` | dir | Formal artifact approvals + session archives + wrap-scan results |
| `.groundtruth-chroma/` | dir | ChromaDB vector store for embeddings (~79 MB) |
| `bridge/` | dir | Bridge protocol working directory + INDEX.md + historical thread files |
| `bridge/INDEX.md` | file | Bridge protocol authoritative state |
| `groundtruth.db` | file | Platform KB database (~893 MB; 8374 spec versions, 24512 tests, 1431 deliberations) |
| `groundtruth.toml` | file | Platform configuration |
| `harness-state/` | dir | S317 harness bootstrap (claude/codex operating-role.md, session-lifecycle-guard.json) — recently created by Codex |
| `memory/MEMORY.md` | file | Platform session memory (currently mixed with Agent Red content; needs split per Section 5.4) |
| `memory/work_list.md` | file | Platform work list (currently mixed; needs split) |
| `memory/pending-owner-decisions.md` | file | Hook-managed owner-decision archive |
| `memory/feedback/` | dir | Platform feedback memories (some Agent-Red-specific need filtering) |
| `memory/topics/` | dir | Topic archives |
| `memory/gtkb-dashboard.sqlite` | file | Dashboard state DB |
| `memory/gtkb-dashboard-history.json` | file | Dashboard history (gitignored per S317 telemetry-churn-policy) |
| `memory/release-readiness.md` | file | Release readiness checklist |
| `tools/knowledge-db/` | dir | KB explorer web app (Flask + SQLite UI) — `app.py`, `assertions.py`, `db.py`, `seed.py`, `templates/`, `static/` |
| `tools/grafana/` | dir | Grafana observability configuration |
| `tools/sqlite-cli/` | dir | SQLite CLI utility |
| `infrastructure/terraform/` | dir | Terraform IaC for platform deployment (Azure) |
| `config/agent-control/` | dir | Service control configuration |
| `docs-site/` | dir | Docusaurus site (publishes framework docs) |
| `CLAUDE.md` | file | Platform session operating procedures (currently Agent-Red-framed; needs reframing) |
| `CLAUDE-ARCHITECTURE.md` | file | Platform architecture reference (needs reframing) |
| `CLAUDE-REFERENCE.md` | file | Platform reference docs |
| `CLAUDE_ARCHIVE.md` | file | Archived platform procedures |
| `MEMBASE-4-CLAUDE.md` | file | Platform memory base specification |
| `vision.md` | file | Platform vision statement |
| `AGENTS.md` | file | Bridge agent assignment (currently mostly Agent Red — needs reframe) |
| `.gitignore` | file | Mostly platform-level (telemetry-churn additions, etc.); has Agent-Red sections that need split |
| `.mcp.json` | file | MCP bridge configuration |
| `.prime-bridge-mcp-health.json` | file | Bridge health state |

#### 1.1.3 Inventory totals

- Framework source files (vendored, awaiting move): **333**
- Platform infrastructure already at root: **~120**
- Bridge thread files (mixed platform-protocol vs. Agent Red work): **~600+** (the protocol is platform; specific threads mostly Agent Red)
- Documentation (framework docs, ~80 files): **~80**
- Templates (framework scaffold templates, ~70 files): **~70**

### 1.2 Agent Red Application Artifacts (currently on this workstation)

The following exist on this workstation and are Agent Red application-level. After restructure, all of these belong under `E:\GT-KB\applications\Agent_Red\`.

#### 1.2.1 Application source code currently at the platform root

| Current path | Target path | Type | Notes |
|---|---|---|---|
| `src/` | `applications/Agent_Red/src/` | dir | Agent Red FastAPI application: `agents/`, `app/`, `chat/`, `integrations/`, `jobs/`, `migrations/`, `multi_tenant/`, `observability/`, `presets/`, `quality_metrics/`, `transport/`, `ui_intelligence/`, etc. |
| `admin/` | `applications/Agent_Red/admin/` | dir | Agent Red admin SPA (React/Vite) |
| `widget/` | `applications/Agent_Red/widget/` | dir | Agent Red customer widget (React/TypeScript) |
| `agents/` | `applications/Agent_Red/agents/` | dir | Agent definitions |
| `shopify/` | `applications/Agent_Red/shopify/` | dir | Shopify deployment target |
| `standalone/` | `applications/Agent_Red/standalone/` | dir | Standalone deployment target |
| `branding/` | `applications/Agent_Red/branding/` | dir | Agent Red brand assets (logo, colors, fonts) |
| `legal/` | `applications/Agent_Red/legal/` | dir | Agent Red legal/contract documents |

#### 1.2.2 Application tests currently mixed with platform tests

The current `tests/` directory at root has both Agent Red tests (~95%) and platform-test infrastructure (~5%). After restructure:

| Current | Target | Notes |
|---|---|---|
| `tests/conftest.py` (31 KB) | `applications/Agent_Red/tests/conftest.py` | Agent Red pytest fixtures |
| `tests/accessibility/`, `agents/`, `chat/`, `contract/`, `e2e*`, `integration*`, `migrations/`, `multi_tenant/`, `observability/`, `quality*`, `security/`, `transport/`, `unit/`, `visual/`, `widget/` | `applications/Agent_Red/tests/<same>/` | Agent Red test suites |
| `tests/evaluation/`, `flows/`, `fuzzing/`, `helpers/`, `integrations/`, `live_api/`, `ops/`, `perf/`, `performance/`, `persistent_memory/`, `property/`, `provider_visual/`, `regression/` | `applications/Agent_Red/tests/<same>/` | Agent Red test strategies |
| `tests/test_*.py` at root (Agent Red app tests) | `applications/Agent_Red/tests/<same>` | E.g., `test_conftest_*.py`, `test_cross_module.py`, `test_deployment_pipeline.py` |
| `tests/hooks/` | `tests/hooks/` (stays at platform root, was platform-level all along) | Framework hook tests |
| `tests/scripts/` | `tests/scripts/` (stays at platform root) | Test utility scripts |

#### 1.2.3 Application scripts currently mixed with platform scripts

The current `scripts/` directory has both Agent Red deploy/ops scripts and platform utility scripts. After restructure:

| Current | Target | Class |
|---|---|---|
| `scripts/deploy_pipeline.py` | `applications/Agent_Red/scripts/deploy_pipeline.py` | Application |
| `scripts/deploy.py`, `deploy_dashboard.py`, `seed_tenant.py`, `upgrade_verification.py`, `test_pipeline.py` | `applications/Agent_Red/scripts/<same>` | Application |
| `scripts/create_shopify_pages.py`, `create_shopify_products.py`, `repair_widget_hash.py`, `update_shopify_navigation.py` | `applications/Agent_Red/scripts/<same>` | Application (Shopify integration) |
| `scripts/seed_platform_admin.py`, `test_admin_ui_validation.py` | `applications/Agent_Red/scripts/<same>` | Application |
| `scripts/build.py`, `build_orchestrator.py`, `build_agent_containers.py` | TBD — partly platform, partly Agent Red | Mixed |
| `scripts/audit_standing_backlog_sources.py` | `scripts/framework/<same>` | Platform |
| `scripts/check_codex_hook_parity.py` | `scripts/framework/<same>` | Platform |
| `scripts/archive_claude_design_handoff.py`, `backfill_lo_reports.py` | `scripts/framework/<same>` | Platform |
| `scripts/harvest_session_deliberations.py` | `scripts/framework/<same>` | Platform |
| `scripts/release_candidate_gate.py` | `scripts/framework/<same>` | Platform |
| `scripts/rehearse/`, `rehearsal/` | `scripts/framework/rehearsal/` | Platform (isolation rehearsal) |
| `scripts/session_self_initialization.py`, `workstream_focus.py` | `scripts/framework/<same>` | Platform |
| `scripts/gtkb_dashboard/` | merge into `tools/grafana/` or `scripts/framework/dashboard/` | Platform |

#### 1.2.4 Application docs currently at platform root

| Current | Target |
|---|---|
| `docs/AGENT-RED-QUALITY-EVALUATION.md` | `applications/Agent_Red/docs/<same>` |
| `docs/COMPREHENSIVE-TEST-PLAN.md` | `applications/Agent_Red/docs/<same>` |
| `docs/MASTER-TEST-PLAN-1.0.md` | `applications/Agent_Red/docs/<same>` |
| `docs/PROJECT-PLAN.md` | `applications/Agent_Red/docs/<same>` |
| `docs/STRATEGIC-ASSESSMENT-2026-02-07.md` | `applications/Agent_Red/docs/<same>` |
| `docs/admin-guide/` | `applications/Agent_Red/docs/admin-guide/` |
| `docs/archive/` | `applications/Agent_Red/docs/archive/` |
| `docs/assets/` | `applications/Agent_Red/docs/assets/` |
| `docs/architecture/` | per-file split (some platform, some Agent Red) |

#### 1.2.5 Application bridge threads (~24 explicit + ~580 implicit)

| Current | Target |
|---|---|
| `bridge/agent-red-*.md` (~24 explicit Agent-Red-named threads) | `applications/Agent_Red/bridge/<same>` |
| Other Agent-Red-content threads (DORA, ISOLATION, GH-*, deploy_pipeline-related, etc.) | `applications/Agent_Red/bridge/<same>` per content audit |
| `bridge/INDEX.md` | stays at platform root (the protocol itself) |
| Historical platform-protocol-development threads | stay at platform root |

#### 1.2.6 Application configuration / build artifacts

| Current | Target | Notes |
|---|---|---|
| `pyproject.toml` (root) | `applications/Agent_Red/pyproject.toml` | Currently Agent Red's pytest/tooling config; framework's pyproject.toml takes the root |
| `package.json` / `package-lock.json` (root) | `applications/Agent_Red/package.json` | Currently Agent Red's npm config |
| `shopify.app.toml` | `applications/Agent_Red/shopify.app.toml` | Shopify CLI config |
| `.shopify/`, `.shopifyignore` | `applications/Agent_Red/.shopify/`, `.shopifyignore` | Shopify CLI state |
| `_split_superadmin.py`, `generate-pdf-report.py` | `applications/Agent_Red/scripts/<same>` | Application utilities |
| `AgentRed-Technical-Evaluation-Report.docx`, `OrbaTech-Technical-Evaluation-Report.docx` | `applications/Agent_Red/docs/evaluations/<same>` | Application evaluations |
| `CHANGELOG.md` (root) | `applications/Agent_Red/CHANGELOG.md` | Currently Agent Red's; framework's takes root |
| `CONTRIBUTING.md` (root) | `applications/Agent_Red/CONTRIBUTING.md` | Currently Agent Red's; framework's takes root |
| `README.md` (root) | per-section split: GT-KB framework gets a fresh README; Agent Red's content moves to `applications/Agent_Red/README.md` |
| `PDF-Generation-Instructions.md` | `applications/Agent_Red/docs/<same>` |
| `PRODUCTION-READINESS-ASSESSMENT.md` | `applications/Agent_Red/docs/<same>` |

#### 1.2.7 Application data records inside the platform's KB

These records physically live in `groundtruth.db` (the platform KB) but logically belong to Agent Red:

- All `SPEC-*` records that describe Agent Red commercial features (commercial-readiness specs, integration specs, multi-tenant specs, ACS/SMS specs, agent-extensibility specs, customer-competitiveness specs, etc.) — most of the 8374 spec versions
- All Agent-Red-related work items
- All Agent-Red-related test definitions
- Most Agent-Red-related deliberations
- Some Agent-Red-related procedures
- Cross-cutting lessons documents (`DOC-cross-cutting-lessons`, `DOC-owner-preferences`, etc.)

These records do **not** physically move (the DB is platform-shared per owner clarification). They are "owned by Agent Red" via the application-registration metadata (Section 5.4 below).

#### 1.2.8 Application memory entries inside platform's MEMORY.md

`memory/MEMORY.md` currently contains both platform-level operational state (the "this is GT-KB" header, governance pointers) and Agent Red-specific session state ("Agent Red is hibernating," "v1.98.92 is in production," "ACS toll-free verification in progress," etc.). Per owner clarification, application-specific entries are inserted by the install script when an application is installed; they don't leave the platform file.

After restructure, MEMORY.md keeps both — but the **structure** distinguishes platform sections from per-application sections. Section 5.4 below specifies the layout.

### 1.3 Mixed / requires-decision / stale categories

The following 12 categories need explicit owner decisions before the restructure can be deterministic. Defaults proposed; owner override accepted.

| Category | Default proposal |
|---|---|
| `bridge/` historical threads (the ~580+ files) | Move to `applications/Agent_Red/bridge/` if content is Agent-Red-specific; stay at root if content is platform-protocol-development. Audit per-file (manual or scripted). |
| `docs/architecture/` | Per-file split: framework architecture docs to root `docs/`; Agent Red architecture docs to `applications/Agent_Red/docs/architecture/`. |
| `archive/` | Drop entirely (stale per inventory) unless owner override; if kept, all under `applications/Agent_Red/archive/`. |
| `assets/` | Per-file split: dashboard assets to platform; brand assets to Agent Red. |
| `infrastructure/terraform/` | Stays at platform root (the IaC is platform infra; Agent Red's deployment is one tenant of it). |
| `package.json` (root) | Agent Red's; moves. The framework doesn't currently have an npm-level component except docs-site. |
| `.vscode/` | Per-file split: editor config that's framework-level stays; Agent-Red-specific settings move. |
| Stale dirs (~25): `.codex_pydeps/`, `.hypothesis/`, `.nojekyll`, `.playwright-mcp`, `.tmp.driveupload/`, `agent-red.wiki/`, `C:Users...` (junk path artifact), `drafts/`, `evaluation/`, `extensions/`, `img/`, `independent-progress-assessments/` (mostly stale Codex archives), `logs/`, `output/`, `pacts/`, `prototype/`, `test-results/`, `test_host/`, `tmp/`, `website/`, `wiki/`, `.tmp.driveupload`, `.wiki/` | Delete during restructure unless owner override. |
| `404.html`, `index.html`, `docs.html`, `CNAME`, `.nojekyll` | Old GitHub Pages artifacts; delete unless owner override. |
| `independent-progress-assessments/` | Mostly Codex archive content; the active subset (CODEX-* documents Codex is currently editing) moves to `applications/Agent_Red/codex-bootstrap/` per the framework template; the archived insights/logs subset gets reviewed and either kept or deleted per owner direction. |
| `MEMBASE-4-CLAUDE.md` | Stays at platform root (it's the GT-KB MemBase specification). |
| `vision.md` | Stays at platform root (platform vision statement). |

---

## Section 2 — Target State Architecture

### 2.1 The platform model (canonical definition)

**`E:\GT-KB\` IS the GroundTruth-KB platform.** There is no nesting; the directory at that path *is* GT-KB. When a user `pip install groundtruth-kb`s for the first time on a machine, the installer either creates `<somewhere>/GT-KB/` or the user manually creates that directory and runs `gt platform init` inside it. The directory's contents define the platform.

**`E:\GT-KB\applications\<app-name>\` is the applications slot.** Each subdirectory of `applications/` is one application, installed by `pip install <app-name>` followed by registration with the platform.

**Data records share the platform's databases, ownership is logical.** Application-specific specs/tests/work-items/deliberations live in `E:\GT-KB\groundtruth.db`. They are inserted by the application's install script. They are owned by the application via metadata. When the application is uninstalled, those records are removed (or marked as `application_uninstalled`) by the uninstall script.

**Application-specific session state lives under the application directory.** Each application has its own `applications/<app>/MEMORY.md`, `applications/<app>/bridge/`, etc. The platform's `memory/MEMORY.md` references applications by name.

### 2.2 GT-KB platform layout (target)

```
E:\GT-KB\
├── pyproject.toml              # Framework's; defines `gt` console script
├── Makefile                    # Framework dev commands
├── README.md                   # Framework README
├── LICENSE
├── CHANGELOG.md                # Framework changelog
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
├── mkdocs.yml                  # Framework docs build config
├── sonar-project.properties
├── groundtruth.toml            # Platform configuration
├── groundtruth.db              # Platform KB database
├── MEMORY.md                   # Platform memory (with per-app sections)
├── CLAUDE.md                   # Platform AI assistant rules (collapsed pointer)
├── AGENTS.md                   # Bridge agent assignment
├── vision.md                   # Platform vision
├── MEMBASE-4-CLAUDE.md         # MemBase spec
├── .editorconfig
├── .pre-commit-config.yaml
├── .gitignore
├── .mcp.json
│
├── src/
│   └── groundtruth_kb/         # Framework Python package
│       ├── cli.py
│       ├── bootstrap.py
│       ├── db.py
│       ├── dashboard.py
│       ├── governance/
│       ├── project/
│       ├── bridge/
│       ├── web/
│       ├── reporting/
│       ├── providers/
│       └── ...
│
├── tests/
│   ├── framework/              # Framework unit/integration tests
│   ├── hooks/                  # Hook tests (already here)
│   └── scripts/                # Script tests (already here)
│
├── docs/                        # Framework documentation (mkdocs source)
│   ├── index.md
│   ├── start-here.md
│   ├── desktop-setup.md
│   ├── method/                  # Method docs
│   ├── reference/               # Reference docs
│   ├── tutorials/               # Tutorials
│   ├── architecture/            # Framework architecture
│   └── ...
│
├── docs-site/                   # Built documentation site
│
├── templates/                   # Project scaffold templates
│   ├── hooks/                   # Hooks scaffolded into new projects
│   ├── rules/                   # Rules scaffolded into new projects
│   ├── skills/                  # Skills scaffolded into new projects
│   ├── ci/                      # CI workflow templates
│   ├── project/                 # Project skeleton (CLAUDE.md, MEMORY.md, etc.)
│   ├── application/             # NEW: application scaffold (for `gt application init`)
│   └── managed-artifacts.toml
│
├── examples/                    # Reference applications
│   └── task-tracker/            # Canonical small example
│
├── evidence/                    # Framework evidence artifacts
│
├── release-notes/
│
├── scripts/
│   └── framework/               # Framework utility scripts
│       ├── audit_docstrings.py
│       ├── audit_types.py
│       ├── harvest_session_deliberations.py
│       ├── release_candidate_gate.py
│       ├── session_self_initialization.py
│       ├── workstream_focus.py
│       ├── rehearsal/
│       └── ...
│
├── tools/
│   ├── knowledge-db/            # KB explorer web app
│   ├── grafana/                 # Grafana observability
│   └── sqlite-cli/              # SQLite CLI utility
│
├── infrastructure/
│   └── terraform/               # Platform IaC
│
├── config/
│   └── agent-control/           # Service control configuration
│
├── memory/
│   ├── feedback/                # Platform feedback memories
│   ├── topics/                  # Topic archives
│   ├── pending-owner-decisions.md
│   ├── work_list.md             # Platform work list
│   ├── release-readiness.md
│   └── gtkb-dashboard.sqlite
│
├── bridge/                      # Bridge protocol working dir
│   ├── INDEX.md                 # Authoritative bridge state
│   ├── (platform-protocol-development threads)
│   └── (framework-improvement threads)
│
├── harness-state/               # Harness operating-role and lifecycle state
│   ├── claude/
│   └── codex/
│
├── .claude/                     # Claude Code harness config
│   ├── hooks/
│   ├── skills/
│   ├── rules/
│   ├── agents/
│   ├── commands/
│   ├── plans/
│   ├── settings.json
│   └── SCHEDULE.md
│
├── .codex/                      # Codex harness config
│   ├── config.toml
│   ├── hooks.json
│   └── gtkb-hooks/
│
├── .github/                     # GitHub Actions
│
├── .githooks/                   # Git hooks
│
├── .groundtruth/                # Formal artifact approvals + session archives
│
├── .groundtruth-chroma/         # ChromaDB vector store
│
└── applications/                # Application slot directory
    └── Agent_Red/               # Agent Red application (Section 2.3)
```

### 2.3 Agent Red application layout (target)

```
E:\GT-KB\applications\Agent_Red\
├── pyproject.toml              # Agent Red package config
├── package.json                # Agent Red npm config
├── README.md                   # Agent Red README
├── CHANGELOG.md                # Agent Red changelog
├── CONTRIBUTING.md             # Agent Red contribution guide
├── application.toml            # Application registration manifest (NEW; consumed by GT-KB platform)
├── shopify.app.toml            # Shopify CLI config
├── .shopifyignore
│
├── src/                        # Agent Red FastAPI application
│   ├── agents/
│   ├── app/
│   ├── chat/
│   ├── integrations/
│   ├── jobs/
│   ├── migrations/
│   ├── multi_tenant/
│   ├── observability/
│   ├── presets/
│   ├── quality_metrics/
│   ├── transport/
│   └── ui_intelligence/
│
├── admin/                      # Admin SPA (React/Vite)
├── widget/                     # Customer widget
├── agents/                     # Agent definitions
├── shopify/                    # Shopify deployment target
├── standalone/                 # Standalone deployment target
├── branding/                   # Brand assets
├── legal/                      # Legal documents
│
├── tests/                      # Agent Red tests (everything except platform-test infra)
│   ├── conftest.py
│   ├── accessibility/
│   ├── agents/
│   ├── chat/
│   ├── e2e/
│   ├── integration/
│   ├── multi_tenant/
│   ├── observability/
│   ├── quality_*/
│   ├── security/
│   ├── transport/
│   └── ...
│
├── scripts/                    # Agent Red scripts
│   ├── deploy_pipeline.py
│   ├── deploy.py
│   ├── deploy_dashboard.py
│   ├── seed_tenant.py
│   ├── upgrade_verification.py
│   ├── test_pipeline.py
│   ├── create_shopify_pages.py
│   ├── _split_superadmin.py
│   └── ...
│
├── docs/                       # Agent Red documentation
│   ├── admin-guide/
│   ├── architecture/
│   ├── archive/
│   ├── assets/
│   ├── evaluations/
│   ├── COMPREHENSIVE-TEST-PLAN.md
│   ├── MASTER-TEST-PLAN-1.0.md
│   ├── PROJECT-PLAN.md
│   └── ...
│
├── memory/
│   └── MEMORY.md               # Agent Red session memory (deploy_versions, hibernation state, etc.)
│
├── bridge/                     # Agent Red's bridge threads
│   └── (Agent Red-specific bridge work threads)
│
├── codex-bootstrap/            # Per-app Codex bootstrap (per templates/project/codex-bootstrap/ pattern)
│   ├── CODEX-SESSION-BOOTSTRAP.md
│   ├── CODEX-REVIEW-OPERATING-CONTRACT.md
│   ├── CODEX-WAY-OF-WORKING.md
│   └── LOYAL-OPPOSITION-LOG.md
│
├── harness-state/              # Per-app harness state (already here from S317)
│   ├── claude/
│   └── codex/
│
├── .claude/                    # Per-app Claude Code config (subset; mostly inherits from platform)
├── .codex/                     # Per-app Codex config
├── .vscode/                    # Per-app editor config
└── .gtkb-app-isolation.json    # Already here from S316 sub-slice 1; declares isolation contract
```

### 2.4 The platform-application boundary

**Resources owned by the platform, consumed by all applications:**
- The Python package `groundtruth_kb`
- The CLI `gt`
- The KB database `groundtruth.db`
- The bridge protocol (the protocol itself, not specific threads)
- All hooks, skills, rules in `.claude/` and `.codex/`
- The dashboard, dashboard service, KB explorer
- The deliberation archive (a section of the KB DB)
- The MemBase memory subsystem
- All scaffold templates
- Host configuration scripts
- Quality guardrails (Test deletion, Assertion ratchet, Architectural guards, Credential scan, TSX commit gate)

**Resources owned by an application:**
- The application's source code, tests, frontends, brand
- The application's deploy scripts and deployment targets
- The application's documentation
- The application's bridge threads (the .md files about the application's work)
- The application's session memory file
- The application's per-app harness state (operating-role, lifecycle-guard)
- The application's `application.toml` manifest (declares it to the platform)
- The application's data records inside platform databases (logically owned, physically platform-stored)

**Resources shared with both ownership stamps:**
- KB records: physically in `groundtruth.db`; metadata column declares owning application
- MEMORY.md: physically at platform root; structured with `# Application: <name>` sections
- Bridge INDEX.md: physically at platform root; entries' bridge files may be in platform root or per-app `applications/<app>/bridge/`

---

## Section 3 — `pip install groundtruth-kb` (Target Behavior)

### 3.1 What the install does today (per framework audit)

- Creates `gt` console script in user's Python `Scripts/` (Windows) or `bin/` (Unix)
- Installs Python dependencies: `click>=8.1` plus optional extras
- Bundles framework templates inside the wheel (`groundtruth_kb/templates/`)
- **Does not** create any system directories
- **Does not** modify the host OS

This is correct as far as it goes — the package install is just-the-package. The platform-creation is a separate step.

### 3.2 What the user experience must be after install (per owner directive)

> "When a user installs GroundTruth-KB, the directory that is created must be called 'GT-KB' and it must contain every part of GroundTruth, including the scripts which configure the host OS."

This implies a **two-step install**:

1. `pip install groundtruth-kb` — installs the Python package + `gt` CLI.
2. `gt platform init [--target <path>]` — creates the GT-KB directory at `<path>/GT-KB/` (default: current directory) and populates it with everything at the layout defined in Section 2.2.

**Existing closest command:** `gt project init` and `gt bootstrap-desktop` already do something like step 2, but they target a "project" model (single self-contained KB), not a "platform with applications slot" model. The new `gt platform init` would extend that with:

- Always creates a directory literally named `GT-KB` (not parameterized name, per owner directive).
- Lays down the full Section 2.2 structure including empty `applications/` slot.
- Installs platform-level `application.toml` registry at `applications/registry.toml` (or similar).
- Runs `gt platform configure-host` (Section 4) to set up host OS.

### 3.3 Step-by-step: `pip install groundtruth-kb` outcome

After `pip install groundtruth-kb`:

| Artifact | Location (typical) | Notes |
|---|---|---|
| `groundtruth_kb` Python package | `<python>/site-packages/groundtruth_kb/` | The package code |
| `gt` console script | `<python>/Scripts/gt.exe` (Win) or `<python>/bin/gt` (Unix) | CLI entry point |
| `groundtruth_kb-<version>.dist-info/` | `<python>/site-packages/` | PEP 376 install metadata |
| Bundled templates | `<python>/site-packages/groundtruth_kb/templates/` | Scaffold templates inside the wheel |

No directory called `GT-KB` is created at this stage. The user must explicitly run `gt platform init` next.

### 3.4 Step-by-step: `gt platform init [--target <path>]` outcome

This command **does not exist yet** — it's a new design proposed by this plan. Behavior:

1. Resolve target: `<path>/GT-KB/` (creates the directory, errors if it already exists unless `--force`).
2. Lay down the platform layout from Section 2.2 by extracting the bundled templates and scaffold:
   - All framework source code (the package itself comes from the installed package; the platform directory holds editable framework if installing-from-source, or just symlinks/references for installed-from-PyPI).
   - All scaffold templates and starter governance files (CLAUDE.md, MEMORY.md, AGENTS.md, etc.).
   - Empty `applications/` slot.
   - `groundtruth.toml` configuration with `project_root = "<absolute-path-to-GT-KB>"`.
   - Initialized empty `groundtruth.db` (or seeded with platform governance specs).
   - Empty `bridge/INDEX.md` with the protocol header comments.
   - The `harness-state/` directory with placeholder operating-role files.
   - The `.claude/`, `.codex/`, `.github/`, `.githooks/` directories with default contents.
   - The `tools/`, `infrastructure/`, `config/`, `memory/`, `docs/`, `docs-site/`, `evidence/`, `release-notes/`, `scripts/framework/` directories.
   - The `.groundtruth/` and `.groundtruth-chroma/` directories.
3. Run `git init` (optional, on by default; `--no-git` to skip).
4. Run `gt platform configure-host` to perform host OS configuration (Section 4).
5. Run `gt platform doctor` to verify all checks pass.
6. Print location and quickstart pointer.

### 3.5 Gap analysis: today vs. target

| Capability | Today | Target |
|---|---|---|
| `pip install groundtruth-kb` installs `gt` CLI | ✅ Already works | ✅ Same |
| Bundles templates inside wheel | ✅ Already works | ✅ Same |
| `gt platform init` exists | ❌ Does not exist | ✅ New command needed |
| Lays down full platform structure | Partial via `gt project init` | Full per Section 2.2 |
| Creates `applications/` slot | ❌ Not in current scaffold | ✅ Required |
| Configures host OS | ❌ Not done | ✅ Required (Section 4) |
| Initializes `harness-state/`, `.codex/gtkb-hooks/` etc. | ❌ Not in scaffold | ✅ Required |
| Creates `applications/registry.toml` | ❌ Concept doesn't exist | ✅ New concept needed |

**Implementation effort:** Moderate. The framework already has scaffold infrastructure (`scaffold.py`, `bootstrap.py`, templates). Extending it with a `platform init` command that produces the Section 2.2 layout is mostly a templating task plus the `applications/` registry concept.

---

## Section 4 — GT-KB Host Setup

### 4.1 The "GT-KB user" concept

Owner phrasing: "the identification of the GT-KB user, the configuration of the host OS, installation and configuration of all service accounts/CLI/SDK, python, etc."

**Proposed model:**

The "GT-KB user" is the human or service identity that owns the GT-KB installation on a particular host. They are:

- The owner of the directory `<somewhere>/GT-KB/` (file system permissions).
- The identity under which `gt platform configure-host` runs (Windows scheduled tasks, services).
- The identity under which the harness AIs (Claude Code, Codex) execute, so the bridge protocol works.
- The identity recorded in `groundtruth.toml` `[platform]` section.
- The identity that holds credentials for downstream services (Azure SDK, GitHub CLI, ACR, etc.).

**Identification step:** `gt platform configure-host` should:

1. Ask: "Who is this GT-KB installation for? (default: $USER)" — captures display name + email.
2. Write to `groundtruth.toml [platform] owner_name = "..."`, `owner_email = "..."`.
3. Verify the running user has write access to the GT-KB directory.

### 4.2 Host OS configuration steps

Per the owner clarification: "the bridge poller setup, the destructive-gate hook, the formal-artifact-approval-gate, the SessionStart/Stop hooks in `.claude/hooks/` — the dashboard is GT-KB infrastructure, as is membase, the deliberation archive, the hooks/skills/plugins, all utilities."

`gt platform configure-host` must perform the following on the host OS (Windows-specific where relevant; other OSes are out-of-scope today since the project is Windows-developed):

#### 4.2.1 Path & shim

- Verify `gt` is on PATH (it should be from pip install).
- If not, add `<python>/Scripts` to PATH (Windows User PATH).

#### 4.2.2 Hook registration

The hooks live as Python files in `.claude/hooks/` and `.codex/gtkb-hooks/`, but they need entries in `.claude/settings.json` and `.codex/hooks.json`. Today these are provisioned by `gt project init` via the templates. `gt platform configure-host` performs this for the platform install.

#### 4.2.3 Dashboard service

The dashboard runs on `localhost:8090` via `gt serve`. Two options for "service" semantics:

- **Option α (Manual):** User runs `gt serve` when they want it. No OS-level service. Lowest friction.
- **Option β (Always-on):** Register a Windows scheduled task that runs at boot/login, runs `gt serve` in the background. Persistent.

Recommended default: **α** (manual) for individual developer installs; **β** (scheduled task) when running on a shared host or as a monitoring station. `--service` flag toggles.

#### 4.2.4 Bridge poller

The bridge poller scans `bridge/INDEX.md` periodically for new entries. Currently halted (per `bridge-essential.md` §"Bridge Polling: Halted" — owner directive 2026-04-25). After the platform stabilizes, the poller may be re-enabled per the cost/benefit analysis required by that rule. Until then, `gt platform configure-host` registers the *infrastructure* (a disabled scheduled task, ready to be enabled) but does not start it.

#### 4.2.5 Git hooks

`.githooks/` directory is registered with git via `git config core.hooksPath .githooks`. `gt platform configure-host` runs that.

#### 4.2.6 Pre-commit

Run `pre-commit install` to register the pre-commit hooks defined in `.pre-commit-config.yaml`.

#### 4.2.7 Session lifecycle scripts

Per S317 harness-state migration, the platform install lays down `harness-state/{claude,codex}/operating-role.md` and `session-lifecycle-guard.json`. These are read by `scripts/framework/session_self_initialization.py` at session start and `scripts/framework/workstream_focus.py` at workstream changes.

### 4.3 Service accounts / CLI / SDK / Python

The platform requires the following on the host. `gt platform configure-host` checks each (using the existing `gt project doctor` mechanism, extended) and reports gaps:

| Tool | Required for | Auto-install? |
|---|---|---|
| Python 3.11+ | The framework | No (manual) |
| pip | Package management | Comes with Python |
| git 2.0+ | Git operations | No (manual) |
| pre-commit | Pre-commit hooks | Yes via pip |
| pytest | Test running | Yes via pip |
| ruff | Linting | Yes via pip |

For applications that consume cloud services (e.g., Agent Red uses Azure):

| Tool | Required for | Auto-install? |
|---|---|---|
| `az` Azure CLI | Application deploy | No (manual; documentation pointer) |
| Azure subscription credentials | Application deploy | No (`az login` is interactive) |
| `node`/`npm` | Frontend builds | No (manual) |
| Docker Desktop | Container builds | No (manual) |
| GitHub CLI `gh` | PR/issue ops | No (manual) |

**Critical clarification:** the platform does not auto-install cloud SDKs or service-account credentials. It identifies what's missing and points the user to install instructions. Service accounts and credentials are the responsibility of the application install (Section 6).

### 4.4 Database / state initialization

After `gt platform init`:

- `groundtruth.db` is created via `KnowledgeDB(db_path).create_schema()` (or equivalent).
- Platform governance specs are seeded (`load_governance_seeds(db)` from `bootstrap.py:16`): GOV-01 through GOV-05 + the additional governance specs the framework defines.
- ChromaDB vector store at `.groundtruth-chroma/` is initialized.
- Bridge `INDEX.md` is created with header comments.
- Empty `MEMORY.md` is created with the platform structure (no application sections yet).

### 4.5 Gap analysis

Today:
- `gt project init` does most of the file-creation work — but at "project" granularity, not "platform" granularity.
- `gt project doctor` does host checking but does not configure the host.
- No `gt platform configure-host` exists.

To close: implement `gt platform init` and `gt platform configure-host` per above. Estimated complexity: ~500-1000 lines of Python on top of existing scaffold infrastructure.

---

## Section 5 — `pip install agent-red` (Target Behavior)

### 5.1 The discovery problem

Owner phrasing: "When a user pip installs Agent Red, they will locate their GT-KB directory and Agent Red will be installed automatically into the applications subdirectory."

This requires **the agent-red package to know about the GT-KB directory**. Three discovery strategies, in order of robustness:

- **Strategy α — Environment variable:** `GTKB_HOME=<path>` env var declares the platform location. Agent Red's post-install script reads it. Simplest.
- **Strategy β — Configuration file:** A user-level config file (e.g., `~/.config/groundtruth-kb/config.toml` on Unix or `%APPDATA%\groundtruth-kb\config.toml` on Windows) records the active GT-KB platform path. Set by `gt platform init` and read by all applications. Most robust.
- **Strategy γ — Interactive prompt:** Application install asks the user "Where is your GT-KB platform? [/some/default]". Highest friction.

**Proposed default: combine β + γ.** `gt platform init` writes to the user-config file; if Agent Red doesn't find it, it falls back to interactive prompt.

### 5.2 What `pip install agent-red` does (target behavior)

Two-step similar to platform install:

1. `pip install agent-red` installs the Python package + Agent Red's CLI (`agent-red` or `gt-app agent-red`).
2. `agent-red install --to <gt-kb-path>` performs application registration (see 5.3).

### 5.3 What the application-install script does

`agent-red install --to <gt-kb-path>` (the new step) performs:

1. **Verify target:** confirms `<gt-kb-path>/groundtruth.toml` exists and is a valid GT-KB platform.
2. **Verify version compatibility:** read framework version from `groundtruth.toml`, compare with Agent Red's required range.
3. **Locate target slot:** create `<gt-kb-path>/applications/Agent_Red/` if not already present.
4. **Lay down application files:** copy/link the application's source, tests, scripts, frontends, etc., into `applications/Agent_Red/` per the Section 2.3 layout.
5. **Write `application.toml`:** create `applications/Agent_Red/application.toml` declaring application metadata (name, version, owner, required services, etc.).
6. **Run platform-side configuration scripts:** call `gt application register Agent_Red`, which the platform handles by:
   - Adding an entry to `applications/registry.toml`.
   - Inserting Agent Red's specs/tests/work-items/deliberations into `groundtruth.db` (Agent Red ships its own KB seed file for this).
   - Inserting Agent-Red-specific sections into `MEMORY.md` if relevant.
   - Registering Agent Red's per-app harness-state under `applications/Agent_Red/harness-state/{claude,codex}/`.
   - Registering any application-level hooks, skills, or rules into the platform registry (with namespacing so `Agent_Red`'s hooks don't collide with another app's).
   - Updating the dashboard config to add Agent Red KPIs.
7. **Run application post-install:** any application-specific setup (Section 6).
8. **Run platform doctor for the application:** `gt application doctor Agent_Red` — verifies the install registered correctly.

### 5.4 What gets created when Agent Red is installed (per artifact)

| Artifact | Created at | Owner | Source |
|---|---|---|---|
| Agent Red source code | `applications/Agent_Red/src/` | Agent Red | Bundled in Agent Red package |
| Agent Red tests | `applications/Agent_Red/tests/` | Agent Red | Bundled |
| Agent Red scripts | `applications/Agent_Red/scripts/` | Agent Red | Bundled |
| Agent Red frontends | `applications/Agent_Red/{admin,widget,agents,shopify,standalone}/` | Agent Red | Bundled |
| Agent Red branding | `applications/Agent_Red/branding/` | Agent Red | Bundled |
| Agent Red docs | `applications/Agent_Red/docs/` | Agent Red | Bundled |
| Agent Red `application.toml` | `applications/Agent_Red/application.toml` | Agent Red | Generated at install |
| Agent Red `pyproject.toml` | `applications/Agent_Red/pyproject.toml` | Agent Red | Bundled |
| Agent Red `package.json` | `applications/Agent_Red/package.json` | Agent Red | Bundled |
| Agent Red `MEMORY.md` | `applications/Agent_Red/memory/MEMORY.md` | Agent Red | Generated at install |
| Agent Red `bridge/` | `applications/Agent_Red/bridge/` (empty initially) | Agent Red | Generated at install |
| Agent Red codex-bootstrap | `applications/Agent_Red/codex-bootstrap/` | Agent Red | Generated from template |
| Agent Red harness-state | `applications/Agent_Red/harness-state/{claude,codex}/` | Agent Red | Generated at install |
| Agent Red `.claude/`, `.codex/`, `.vscode/` per-app | `applications/Agent_Red/.{claude,codex,vscode}/` | Agent Red | Generated from template |
| Agent Red `.gtkb-app-isolation.json` | `applications/Agent_Red/.gtkb-app-isolation.json` | Agent Red | Generated at install |
| Agent Red KB records | inserted into `groundtruth.db` | Logically Agent Red, physically platform | From Agent Red's seed file |
| Agent Red MEMORY.md sections | inserted into platform `MEMORY.md` | Logically Agent Red, physically platform | From Agent Red's seed |
| Agent Red entry in `applications/registry.toml` | `applications/registry.toml` | Platform | Created by registration |

### 5.5 Gap analysis: today vs. target

| Capability | Today | Target |
|---|---|---|
| Agent Red is a pip-installable package | Partial (it has pyproject.toml at root, but it's tangled with the platform) | ✅ After restructure (Section 7) |
| `agent-red install --to <path>` exists | ❌ No | ✅ New command needed |
| `gt application register <name>` exists | ❌ No | ✅ New command needed |
| `applications/registry.toml` exists | ❌ Concept doesn't exist | ✅ Required |
| Application has a `application.toml` manifest | ❌ Concept doesn't exist (closest analog: `.gtkb-app-isolation.json` from S316) | ✅ Required |
| Application can declare KB seed records | ❌ No mechanism | ✅ Required |
| Platform can scope KB queries by application | Partial (has `application_id` columns in some tables, not consistently) | ✅ Required |
| Per-app harness-state | ✅ Exists from S317 | ✅ Same |

**Implementation effort:** Significant. The application-registration model is the largest conceptual gap. ~1500-3000 lines of Python including the registry, the install script, the KB-record-tagging migration, and tests.

---

## Section 6 — Agent Red Setup

### 6.1 The Agent Red user / service accounts

Agent Red consumes external services. Its install must guide setup of:

| Service | Purpose | Setup mechanism |
|---|---|---|
| Azure subscription | Container Apps deployment | `az login` (interactive) |
| Azure Container Registry | Container images | Same Azure auth |
| Cosmos DB | Multi-tenant data store | Same Azure auth |
| Azure Key Vault | Secrets | Same Azure auth |
| Azure Communication Services | SMS / email | Same Azure auth |
| Stripe | Payments | API key (manual entry) |
| Shopify | Storefront | Shopify CLI auth (interactive) |
| Titan (SMTP) | Email | Credentials in env / vault |
| GitHub | CI/CD, releases | `gh auth login` (interactive) |

Agent Red's install script:
1. Checks each prerequisite via `agent-red doctor`.
2. For each missing prereq, prints concrete setup instructions.
3. Does not auto-perform any interactive auth — the user runs `az login`, `gh auth login`, etc.

### 6.2 Host OS configuration changes (Agent Red specific)

Most platform-level OS configuration is done by `gt platform configure-host` (Section 4.2). Agent Red adds:

- (None mandatory at install time.) Deployment-related Windows scheduled tasks (e.g., the previously-retired ACS toll-free SMS verification monitor) are application-level and registered only when the user runs them.

### 6.3 Database imports

Owner clarification: "all of those references must be inserted into their parent artifacts."

Concretely, when `gt application register Agent_Red` runs:

#### 6.3.1 KB record import

Agent Red ships an `agent_red.kb_seed` module with all the spec/test/work-item/deliberation records that "belong" to Agent Red. The registration script inserts them into `groundtruth.db` with `application_id = "Agent_Red"` metadata. Idempotent (re-runs skip already-present records).

This includes:

- All Agent Red commercial-readiness specs (SPEC-1828–1834 etc.)
- All Agent Red feature specs (Customer Competitiveness, Agent Extensibility, Quality Measurement, Canonical Identity, SPA Control Plane, A/B Testing, Integration Framework, MCP Agents, Pipeline Observatory, Backlog-018, Zero-Knowledge Architecture, etc.)
- Their associated tests, work items, deliberations, and procedures
- Cross-cutting documents (DOC-cross-cutting-lessons, DOC-owner-preferences) that have Agent-Red-specific sections

#### 6.3.2 MEMORY.md import

Agent Red's seed includes a `MEMORY.md` template fragment that gets appended to the platform `MEMORY.md` under a `# Application: Agent_Red` section header. Includes:

- Current production version, hibernation state, ACS verification status
- Active deployment targets (staging, production)
- Active Azure resources
- Branch state
- Application-specific recent sessions

The platform's `MEMORY.md` structure becomes:

```
# GT-KB Platform Memory

## Current Status
(platform-level items only)

## Recent Sessions
(platform-level items only)

# Application: Agent_Red

## Current Status
(Agent-Red-specific items)

## Recent Sessions
(Agent-Red-specific items)
```

#### 6.3.3 work_list.md import

Same pattern: Agent Red's work items get appended to a per-application section in the platform `work_list.md`.

#### 6.3.4 Bridge thread inheritance

If installing Agent Red on a fresh GT-KB, no bridge threads come pre-populated (clean slate). If migrating from the current `E:\GT-KB\` (which is what we're doing in Phase 2 of this plan), bridge threads are physically moved per the Section 1.2 inventory.

### 6.4 CLI / SDK configuration

After `agent-red install --to <gt-kb-path>` completes:

- `agent-red` CLI is on PATH.
- `agent-red doctor` passes (or reports specific missing prerequisites).
- `gt application list` includes Agent_Red.
- `gt summary` shows total spec/test/WI counts including Agent Red's contributions.
- `gt summary --application Agent_Red` shows Agent-Red-only counts.

Per-service configuration (Azure, Stripe, Shopify, etc.) requires user-driven `az login`, etc. The application's documentation lists each step.

### 6.5 Verification

`agent-red doctor` checks:

- Required directories present in `applications/Agent_Red/`.
- KB records seeded (`SELECT count(*) FROM specifications WHERE application_id = 'Agent_Red'` returns >0).
- `application.toml` valid.
- Platform `groundtruth.db` has Agent Red's records with correct metadata.
- All required services credentials configured.
- All deployment targets reachable.

---

## Section 7 — Implementation Phases

This section sequences the work. Each phase is a separate bridge proposal that must reach VERIFIED before the next phase begins.

### Phase 1 — Stabilize current state (no restructure yet)

1. Wait for Codex's in-flight framing-correction edits to commit.
2. Audit + delete stale dirs (per Section 1.3 "Stale dirs" list, owner-confirmed).
3. Resolve all open Codex framing edits.
4. Run `gt platform doctor` (extended to detect the current pre-restructure state) and document gaps.

**Estimated size:** 1-3 commits. **Estimated session:** 1.

### Phase 2 — Restructure (the file moves)

1. Move framework files from `groundtruth-kb/` subdirectory to GT-KB root (with conflict resolution against current root files).
2. Move Agent Red files from GT-KB root to `applications/Agent_Red/`.
3. Update all import paths and configuration references.
4. Update `pyproject.toml` to be the framework's; Agent Red's moves under applications/.
5. Update `.gitignore`, CI workflows, hooks, and tests for the new layout.
6. Run full test suite; fix breakage.
7. Run `gt platform doctor` against the new layout.

**Estimated size:** ~200-500 file moves, ~50-200 import updates, ~5-10 commits. **Estimated session:** 1-3 (this is the largest phase).

### Phase 3 — Application registration design + implementation

1. Design `application.toml` schema.
2. Design `applications/registry.toml` schema.
3. Implement `gt application register <name>` and `gt application unregister <name>`.
4. Implement `gt application list` and `gt application doctor <name>`.
5. Migrate KB schema to add `application_id` column where missing.
6. Tag existing KB records with `application_id = 'Agent_Red'` for Agent Red's records.
7. Implement KB-seed-file import mechanism for application-shipped seeds.
8. Implement MEMORY.md insertion mechanism for application-shipped sections.

**Estimated size:** ~3000 LOC across framework code + tests. **Estimated session:** 2-4.

### Phase 4 — Platform install design + implementation

1. Implement `gt platform init` command.
2. Implement `gt platform configure-host` command.
3. Implement user-level config file (`~/.config/groundtruth-kb/config.toml`).
4. Document the platform install flow.
5. Test fresh install on a clean Windows machine (or VM).

**Estimated size:** ~1500 LOC across framework code + tests. **Estimated session:** 2-3.

### Phase 5 — Application install design + implementation

1. Design Agent Red's `agent-red` package structure.
2. Implement `agent-red install --to <path>` command.
3. Implement `agent-red doctor`.
4. Bundle Agent Red's KB seed file.
5. Bundle Agent Red's MEMORY.md fragment.
6. Test fresh install on a clean GT-KB platform.

**Estimated size:** ~1500 LOC + Agent Red package restructuring. **Estimated session:** 2-3.

### Phase 6 — Cross-platform install testing + documentation

1. Test platform install + Agent Red install end-to-end on Windows.
2. (Optional) Test on Unix.
3. Update framework docs to document the platform/application model.
4. Publish framework v0.7.0 (or appropriate version) to PyPI.
5. Publish Agent Red as `agent-red` to PyPI.

**Estimated size:** ~1 session.

**Total estimated effort:** 8-15 sessions across all phases. The current session would deliver Phase 1 + this proposal as a VERIFIED contract for subsequent phases.

---

## Section 8 — Coherence Prevention Going Forward

### 8.1 What changes after this proposal is VERIFIED

1. **CLAUDE.md collapses to ~50 lines** that point at this proposal as the canonical platform spec, plus the bridge protocol pointers and copyright.
2. **MEMORY.md restructures** with explicit `# Platform` and `# Application: <name>` sections.
3. **Each session starts** by reading: AGENTS.md → role file → `bridge/INDEX.md` → this proposal → only-then the application-specific MEMORY.md sections.
4. **Bridge proposals must cite** this document when proposing platform-level changes. Application-level changes cite the application's own architecture docs.
5. **The work_list mechanically distinguishes** platform work from per-application work (column or section header).

### 8.2 What machine checks enforce coherence

After Phase 4 lands, `gt platform doctor` checks:

- Section 2.2 layout matches actual disk state.
- All applications registered in `applications/registry.toml` have valid `application.toml` files.
- KB records all have valid `application_id` values.
- MEMORY.md sections match registered applications.
- No "orphan" files at the platform root that should be in `applications/`.

These checks make incoherence detectable in seconds, not days.

### 8.3 What this proposal does not solve

- AI attention decay on long sessions (a model behavior, not a structural one).
- Concurrent edit coordination between Prime Builder and Loyal Opposition harnesses (the bridge protocol partially addresses this; full solution is async-merge tooling).
- Owner-time scarcity (no proposal can solve "the owner only has 2 hours per day").

These are real, but out of scope for this proposal.

---

## Section 9 — Owner Decisions Required

Before any phase executes, the owner must explicitly answer:

1. **Section 1.3 mixed/stale categories** — confirm the defaults or override per category.
2. **Section 4.2.3 dashboard service** — Option α (manual) vs. β (always-on)?
3. **Section 4.3 service accounts** — confirm "platform doesn't auto-install cloud SDKs" stance.
4. **Section 5.1 application discovery** — confirm Strategy β + γ combination.
5. **Section 5.4 KB record migration** — confirm: existing Agent Red records get tagged `application_id = "Agent_Red"` in-place; no DB rebuild.
6. **Section 7 phase ordering** — confirm Phase 1 → 2 → 3 → 4 → 5 → 6, or override.
7. **Phase 2 work begins this session or next?** Owner stated "must complete this session" earlier; I am asking to revise that to "Phase 1 completes this session; Phase 2 begins next session" given the scale.

---

## Section 10 — Codex Verification Request

Please verify the following before GO:

1. **Section 1 inventory completeness** — sample 10 random files in `E:\GT-KB\` and confirm each is correctly classified.
2. **Section 2 layout** — does the proposed target structure satisfy the owner's "GT-KB IS the platform; applications are slots" model?
3. **Section 3-6 install descriptions** — are they internally consistent? Do steps in Section 5 (Agent Red install) correctly depend on prerequisites in Section 4 (platform install)?
4. **Section 7 phase ordering** — flag any dependency violations.
5. **Section 8 coherence prevention** — does this address the loss-of-control concern, or is it mostly aspirational?
6. **Gaps** — what important architectural questions does this proposal NOT address?
7. **Risk** — is the estimated effort (8-15 sessions) plausible?

A NO-GO with specific findings is more valuable than a fast GO. The owner explicitly said "I do not believe that we can complete the GT-KB isolation project unless I can verify that this information meets my expectations."

---

## Section 11 — Reversibility

This proposal does not directly mutate any artifact. It is a contract.

Each subsequent phase (Phase 1, 2, 3, etc.) lands as its own bridge proposal with its own reversibility analysis. Phase 2 (the file moves) is the largest reversibility risk; its own proposal will define rollback procedures and checkpoints.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
