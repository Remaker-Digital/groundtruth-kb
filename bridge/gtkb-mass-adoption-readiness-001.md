# GT-KB Mass Adoption Readiness — Implementation Proposal

**Status:** NEW
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295
**Scope:** All 12 first-class GT-KB components per SPEC-GTKB-SCOPE
**Repository:** `groundtruth-kb` @ `2a324c6` (main)

---

## Context

The owner asked: "Is GroundTruth-KB ready for mass adoption by developers?"

**Answer: No.** A readiness assessment against all 12 first-class components (SPEC-GTKB-SCOPE) found:
- 3 components rated **Good** (Deliberation Archive, Specs scaffolding, Documentation)
- 7 components rated **Partial** (work for Agent Red but are not generalized/portable)
- 2 components rated **Weak** (Agent-Red-specific with no adoption path)

**The core blocker is portability.** A developer who runs `pip install groundtruth-kb` gets the KB, specs engine, and deliberation CLI. They do NOT get a functioning bridge, a Loyal Opposition, project scaffolding with Terraform, GitHub CI, or the agent cooperation infrastructure — and those are first-class components.

## Prior Deliberations

- **SPEC-GTKB-SCOPE** (VERIFIED, authority: stated) — the 12-component product scope boundary, recorded this session per owner directive
- **DELIB-0633** — GroundTruth-KB Strategic Assessment
- **DELIB-0469** — GroundTruth Bootstrap Gap-Closure Proposal
- **DELIB-0209** — Prime Review Packet - GroundTruth Strategy
- **DELIB-0208** — GroundTruth Competitive Decision Memo
- **DELIB-0474** — GroundTruth Execution Plan for Prime

## Objective

Make GroundTruth-KB adoptable by a developer who has never seen the Agent Red project, on any platform (Windows, macOS, Linux), with a single `gt init` command as the entry point.

**Exit state:** a developer runs `pip install groundtruth-kb && gt init my-project`, answers 3-5 setup questions, and gets a working project with all 12 components scaffolded and functional.

---

## Current State vs. Target State (per component)

| # | Component | Current | Target | Gap |
|---|---|---|---|---|
| 1 | Prime Builder | Agent-Red-specific skills/plugins/prompts in `.claude/` | `gt init` scaffolds a project-level `.claude/` with skills, plugins, prompt templates, and a `CLAUDE.md` tailored to the project profile | No generic skill/plugin scaffolding |
| 2 | Loyal Opposition | AGENTS.md + `.claude/rules/` manually configured for GPT-5.3/Codex on Windows | `gt init` generates `AGENTS.md` with configurable LO provider (Codex, Claude, or custom), platform-agnostic rules | Hardcoded to one provider + Windows |
| 3 | Bridge + protocol | File bridge works; PS1 automation is Windows-only; 15-min timeout; auth-token fragility | Cross-platform bridge automation (Python-based scheduler replacing PS1); `gt bridge start` CLI command; built-in auth-token management | PS1→Python migration; CLI entry point |
| 4 | Deliberation Archive | Functional (CLI, ChromaDB, harvest scripts) | Already close; add `gt init` integration so new projects get deliberation config out of the box | Minor: scaffold integration |
| 5 | MemBase-4-Claude | MEMORY.md + topic files pattern, undocumented | `gt init` scaffolds `memory/MEMORY.md` with section templates; adopter guide explaining the memory architecture | Documentation + scaffold |
| 6 | Dev environment CLI/SDK | pyproject.toml with extras; assumes Windows + Python 3.14 | Cross-platform dev setup guide; `gt doctor` validates environment (already exists, needs expansion); minimum Python version policy | Guide + doctor expansion |
| 7 | 3rd party integrations | ChromaDB optional; SonarCloud/CodeRabbit/Dependabot configured for Agent Red only | Integration configuration templates; `gt init --integrations` flag scaffolds `.github/dependabot.yml`, SonarCloud config, CodeRabbit config from templates | Template generation |
| 8 | GitHub configuration | 9 CI workflows, Agent-Red-specific | `gt scaffold github` generates CI workflows from a profile (minimal/standard/full); includes lint, test, coverage, docstring, security scan, accessibility | Workflow template engine |
| 9 | Documentation + guides | 13 methodology docs written for GT-KB maintainers | Adopter-facing "Getting Started" guide, "Your First Spec", "Setting Up Dual-Agent Workflow", "Customizing Your Project" | New adopter journey docs |
| 10 | Specs scaffolding | `gt scaffold specs` functional, tested | Already close; ensure `gt init` calls it during project setup | Minor: init integration |
| 11 | Test scaffolding | test_host + API gateway patterns exist for Agent Red | `gt scaffold tests` generates test infrastructure from project profile; test dashboard template; test_host Dockerfile template | New scaffold command + templates |
| 12 | Project scaffolding | `gt scaffold project` exists with profiles | Add Terraform templates for Azure; zero-knowledge architecture patterns; multi-tenant patterns as selectable profile options | Terraform + ZK + multi-tenant |

---

## Phased Implementation Plan

### Phase 1: Cross-Platform Foundation (P1)

**Goal:** Remove Windows-only dependencies and establish the cross-platform `gt init` entry point.

| WI | Scope | Est. effort |
|---|---|---|
| P1.1 | **Bridge automation: PS1 → Python migration.** Replace the 9 PowerShell scheduled-task scripts with a Python-based bridge scheduler (`groundtruth_kb.bridge.scheduler`) that works on Windows, macOS, and Linux. Uses `sched` or `apscheduler` for periodic dispatch. Retains the same 3-minute cadence, status-file JSON schema, and liveness-watcher dual-signal design. The PS1 scripts remain in-repo as legacy/reference but are no longer the primary path. | 3-4 days |
| P1.2 | **`gt bridge start` CLI command.** New CLI entry point that starts the bridge scheduler as a foreground or background process. Replaces the manual Windows Task Scheduler setup. `gt bridge start --agent prime --background` daemonizes on Unix, runs as a background job on Windows. | 1-2 days |
| P1.3 | **`gt init` command.** New top-level CLI command that scaffolds a complete project. Prompts for: project name, profile (minimal/standard/full), agent provider (Codex/Claude/custom), integrations (GitHub CI, ChromaDB, SonarCloud). Calls existing `scaffold_project()` + new generators for components 1-2, 5, 7-8. | 3-4 days |
| P1.4 | **Auth-token management.** Built-in token persistence + refresh for the bridge scheduler. Replaces the fragile `.local/claude-oauth-token.txt` → PS1 injection path. `gt bridge auth refresh` CLI command. | 1-2 days |
| P1.5 | **Cross-platform CI.** Ensure all GT-KB CI workflows run on `ubuntu-latest` (already true) AND that the test suite passes on macOS and Windows runners (add matrix). | 1 day |

**Phase 1 exit:** `pip install groundtruth-kb && gt init my-project && gt bridge start --agent prime` works on all three platforms.

### Phase 2: Agent Configuration Templates (P2)

**Goal:** Make Prime Builder and Loyal Opposition setup reproducible and configurable.

| WI | Scope | Est. effort |
|---|---|---|
| P2.1 | **Prime Builder template set.** `gt init` generates `.claude/CLAUDE.md` (project rules), `.claude/hooks/` (assertion-check, credential-scan, poller-freshness — all from templates), `.claude/settings.json` (hook registrations). Templates are parameterized by project profile. | 2-3 days |
| P2.2 | **Loyal Opposition template set.** `gt init` generates `AGENTS.md` with configurable LO provider. Generates `.claude/rules/` rule files (loyal-opposition.md, bridge-essential.md, deliberation-protocol.md, file-bridge-protocol.md, report-depth.md). Provider-specific sections are conditionally included. | 2-3 days |
| P2.3 | **MemBase template.** `gt init` scaffolds `memory/MEMORY.md` with standard sections (Current Status, Feedback Index, Strategic Thesis, Plan-of-Record, Standing Operating Decisions, Recent Sessions, Quick Reference, Memory Files). Includes a "How to use MEMORY.md" header comment block. | 1 day |
| P2.4 | **Bridge protocol templates.** `gt init` scaffolds `bridge/INDEX.md` + bridge protocol documentation. Pre-populates the INDEX header with the file-bridge-protocol rules. | 0.5 days |

**Phase 2 exit:** `gt init` produces a project where both Prime and LO agents can start working immediately, with bridge protocol ready, memory structure in place, and hooks wired.

### Phase 3: GitHub + Integration Scaffolding (P3)

**Goal:** Generate CI/CD and integration configuration from templates.

| WI | Scope | Est. effort |
|---|---|---|
| P3.1 | **`gt scaffold github` command.** Generates `.github/workflows/` from profile. Profiles: `minimal` (lint + test), `standard` (+ coverage + docstring + mypy), `full` (+ security scan + accessibility + Chromatic + OpenAPI compat). Each workflow is a Jinja2 or string-template file in `templates/github/`. | 2-3 days |
| P3.2 | **Integration config scaffolding.** `gt init --integrations` generates: `.github/dependabot.yml` (pip, npm, Actions, Docker), `.sonarcloud.properties`, `.coderabbitai.yaml`, `.chromatic.yml`. Each is optional and profile-driven. | 1-2 days |
| P3.3 | **`gt doctor` expansion.** Extend the existing `run_doctor()` to check: Python version ≥ 3.10, git installed, `gt` CLI version, ChromaDB availability (optional), bridge scheduler running, Claude/Codex auth status, GitHub CLI auth (`gh auth status`). Report actionable fixes for each failure. | 1-2 days |

**Phase 3 exit:** `gt scaffold github --profile standard` generates a working CI pipeline. `gt doctor` validates the full development environment.

### Phase 4: Advanced Patterns (P4)

**Goal:** Implement the architectural patterns listed in SPEC-GTKB-SCOPE items 11-12.

| WI | Scope | Est. effort |
|---|---|---|
| P4.1 | **Test scaffolding.** `gt scaffold tests` generates: `tests/` directory structure, `conftest.py` with standard fixtures, `test_host/Dockerfile` template, API gateway mock template, test dashboard configuration. Profile-driven (unit-only / integration / full). | 2-3 days |
| P4.2 | **Terraform project scaffolding.** `gt scaffold infra --provider azure` generates: `terraform/` directory with modules for resource group, container registry, Cosmos DB, Key Vault, Redis, Container Apps. Based on the Agent Red Azure infrastructure pattern. Parameterized by project name and region. | 3-4 days |
| P4.3 | **Zero-knowledge architecture patterns.** Implement the 4 existing specs (BL-ZK-001, 31 WIs, 5 phases per MEMORY.md). `gt scaffold project --profile zero-knowledge` generates the ZK-specific infrastructure and data-handling patterns. | 5-7 days |
| P4.4 | **Multi-tenant architecture patterns.** `gt scaffold project --profile multi-tenant` generates tenant isolation patterns, per-tenant configuration, shared infrastructure with tenant-scoped access control. Based on Agent Red's tenant model. | 3-5 days |

**Phase 4 exit:** Advanced users can scaffold production-grade infrastructure with architectural patterns from the CLI.

### Phase 5: Adopter Documentation (P5)

**Goal:** Documentation written for the adopter, not the maintainer.

| WI | Scope | Est. effort |
|---|---|---|
| P5.1 | **"Getting Started" guide.** End-to-end walkthrough: install GT-KB → `gt init` → first spec → first test → first bridge exchange → first deployment. Written for a developer who has never seen Agent Red. | 2-3 days |
| P5.2 | **"Your First Specification" tutorial.** Teaches the spec-first workflow (GOV-01) with a concrete example project. | 1 day |
| P5.3 | **"Setting Up Dual-Agent Workflow" guide.** How to configure Prime + LO, start the bridge, do your first proposal/review cycle. Covers both Codex and Claude-only setups. | 1-2 days |
| P5.4 | **"Customizing Your Project" reference.** Profile options, integration flags, template overrides, hook customization. | 1-2 days |
| P5.5 | **API reference regeneration.** Ensure `mkdocs` / `pdoc` API docs cover all 12 components, not just the Python package public API. | 1 day |

**Phase 5 exit:** A developer can self-serve from documentation alone, without needing Agent Red as a reference implementation.

---

## Dependency Graph

```
P1 (cross-platform foundation)
├── P1.1 PS1→Python bridge scheduler
├── P1.2 gt bridge start CLI
├── P1.3 gt init (depends on P1.1, P1.2 for bridge scaffolding)
├── P1.4 Auth-token management
└── P1.5 Cross-platform CI

P2 (agent templates) — depends on P1.3 (gt init exists)
├── P2.1 Prime Builder templates
├── P2.2 Loyal Opposition templates
├── P2.3 MemBase template
└── P2.4 Bridge protocol templates

P3 (GitHub + integrations) — depends on P1.3
├── P3.1 gt scaffold github
├── P3.2 Integration config
└── P3.3 gt doctor expansion

P4 (advanced patterns) — depends on P1.3, P3.1
├── P4.1 Test scaffolding
├── P4.2 Terraform scaffolding
├── P4.3 Zero-knowledge patterns
└── P4.4 Multi-tenant patterns

P5 (documentation) — depends on P1-P4 (documents what exists)
├── P5.1-P5.5 all depend on implemented features
```

**Critical path:** P1.1 → P1.3 → P2 → P5. Everything else is parallelizable.

---

## Estimated Total Effort

| Phase | WIs | Estimated days |
|---|---|---|
| P1 Cross-platform foundation | 5 | 9-13 |
| P2 Agent templates | 4 | 5.5-7.5 |
| P3 GitHub + integrations | 3 | 4-7 |
| P4 Advanced patterns | 4 | 13-19 |
| P5 Adopter documentation | 5 | 6-9 |
| **Total** | **21 WIs** | **37.5-55.5 days** |

This is a multi-month effort. Phases 1-2 are the minimum viable adoption path (~15-20 days). Phases 3-5 bring it to production-grade mass adoption.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| PS1→Python bridge migration breaks Agent Red's working bridge | High | Run both in parallel during migration; PS1 remains as fallback; feature-flag the Python scheduler |
| `gt init` scope creep — trying to scaffold too much upfront | Medium | Start with "minimal" profile that scaffolds only components 3-5, 10; expand profiles incrementally |
| Zero-knowledge / multi-tenant patterns are underspecified (only 4 specs exist) | Medium | Implement P4.3/P4.4 only after P1-P3 stabilize; treat as post-MVP |
| Cross-platform testing reveals Unix-specific assumptions in bridge code | Medium | P1.5 adds macOS/Linux CI matrix early; fix platform bugs as discovered |
| Agent provider lock-in (Codex assumes GPT-5.3, Prime assumes Opus 4.6) | Medium | P2.1/P2.2 parameterize the provider; abstract model-specific prompts behind template variables |
| Documentation written by the builder is still builder-focused | Medium | P5 should be reviewed by someone who has NOT used GT-KB before (user testing) |

---

## Open Decisions for Codex

1. **Phase ordering.** P1 → P2 → P3 → P4 → P5 is the proposed sequence. Should P5 (documentation) be interleaved earlier (e.g., write the Getting Started guide during P1 to validate the `gt init` UX)?

2. **Bridge scheduler technology.** Python `sched` module (stdlib, simple) vs `apscheduler` (3rd party, more features like persistent job store) vs `asyncio` periodic task. Recommendation: stdlib `sched` for MVP; migrate to `apscheduler` if persistent scheduling is needed.

3. **Template engine.** String formatting (simple, no dependency) vs Jinja2 (powerful, well-known, adds a dependency). Recommendation: Jinja2, because GitHub workflow templates have complex conditional sections.

4. **Minimum Python version.** Currently tested on 3.14 only. Mass adoption requires 3.10+ support (covers the last 4 major versions). Should the CI matrix test 3.10, 3.11, 3.12, 3.13, 3.14?

5. **MVP scope.** Should the first release targeting adoption include all 5 phases, or should P1+P2 ship as a "developer preview" with P3-P5 following?

---

## Success Criteria

GroundTruth-KB is ready for mass adoption when:

1. A developer on any platform (Windows, macOS, Linux) can run `pip install groundtruth-kb && gt init my-project` and get a working project with all 12 components scaffolded
2. `gt doctor` validates the full environment and reports actionable fixes
3. `gt bridge start` runs the bridge scheduler cross-platform without manual Task Scheduler / crontab setup
4. Adopter documentation exists that does NOT reference Agent Red
5. At least one project other than Agent Red successfully uses GT-KB end-to-end (the "second customer" test)

---

## Relationship to Phase 4B

Phase 4B (quality hardening) addressed the Python package's internal quality: mypy, coverage, docstrings. This proposal addresses the PRODUCT's external adoptability. Phase 4B is a prerequisite (the package must be internally sound before it can be externally adopted) but is not sufficient — a well-tested, well-documented Python package that can only run on one Windows workstation with manually-configured PS1 scripts is not an adoptable product.

Phase 4C (structured logging) and 4D (broad-exception review) from the existing phase-4b-plan.md should be re-scoped to cover all 12 components per SPEC-GTKB-SCOPE, not just `src/groundtruth_kb/`.
