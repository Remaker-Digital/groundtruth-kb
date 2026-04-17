# GT-KB Adoption Gap Closure — Implementation Plan

**Status:** NEW
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295
**Scope:** Close the 5 remaining gaps blocking mass adoption per SPEC-GTKB-SCOPE
**Repository:** `groundtruth-kb` @ `31fe2c4` (main)
**Depends on:** `gtkb-mass-adoption-readiness-012` VERIFIED (MVP landed at `12fd083`)

---

## Context

The owner asked "Is GroundTruth-KB ready for mass adoption by developers?" twice this session. Both times the answer was No. The first time triggered the MVP implementation (bridge INDEX scaffolding, doctor accuracy, provider templates, bridge rule templates — VERIFIED at `-012`). The second assessment identified **5 remaining gaps** between current state and mass adoption readiness.

**Owner decisions on record (DELIB-GTKB-INIT-POSTURE, DELIB-GTKB-TOKEN-POSTURE):**
- `gt init` remains Layer 1 (core DB); `gt project init` is the scaffold entry point
- GT-KB does not manage auth tokens; provides step-by-step troubleshooting documentation only

**Owner scope definition (SPEC-GTKB-SCOPE):**
- All 12 first-class components must be addressed, not just the Python package

---

## The 5 Remaining Gaps

| # | Gap | Current state | What "ready" looks like |
|---|---|---|---|
| **G1** | No adopter documentation | 13 methodology docs for maintainers; no "Getting Started", no tutorials, no adopter journey | A developer who has never seen Agent Red can self-serve from docs alone |
| **G2** | Bridge automation is Windows-only | PS1 scheduled tasks work on owner's workstation; Mac/Linux developers cannot use the bridge without manual OS-specific setup | `gt bridge start` CLI command runs the bridge scheduler cross-platform; auth troubleshooting docs provided per owner decision |
| **G3** | GitHub CI is not templated | 9 CI workflows exist for Agent Red; `gt project init` does not generate CI workflows | `gt project init --profile dual-agent-webapp` generates working CI workflows from templates |
| **G4** | Zero-knowledge + multi-tenant patterns are spec-only | 4 ZK specs exist, 0 implemented; multi-tenant is Agent Red pattern, not scaffolded | `gt project init --profile zero-knowledge` and `--profile multi-tenant` generate working infrastructure patterns |
| **G5** | No second customer | Agent Red is the only project; "ready for mass adoption" is an untested claim | At least one project other than Agent Red successfully uses GT-KB end-to-end |

---

## Phased Implementation Plan

### Phase G1: Adopter Documentation

**Goal:** A developer can self-serve from documentation alone.

| WI | Deliverable | Scope | Est. |
|---|---|---|---|
| G1.1 | **Getting Started guide** | `docs/getting-started.md`. End-to-end: `pip install groundtruth-kb` → `gt project init my-project --profile dual-agent-webapp` → first spec → first test → first bridge exchange. Written for someone who has never seen Agent Red. No Agent Red references. | 2 days |
| G1.2 | **"Your First Specification" tutorial** | `docs/tutorials/first-spec.md`. Teaches GOV-01 spec-first workflow with a concrete example (e.g., building a simple API service). Creates a spec, creates a work item, links a test, runs assertions. | 1 day |
| G1.3 | **"Setting Up Dual-Agent Workflow" guide** | `docs/tutorials/dual-agent-setup.md`. How to configure Prime + LO with `gt project init --profile dual-agent`, start the bridge, do a proposal/review cycle, reach VERIFIED. Covers both Codex-based and Claude-only setups. References auth troubleshooting docs (per DELIB-GTKB-TOKEN-POSTURE: documentation only, no token management). | 1.5 days |
| G1.4 | **"Customizing Your Project" reference** | `docs/reference/customization.md`. Profile options, integration flags, template overrides, hook customization, provider configuration via `providers/schema.py`. | 1 day |
| G1.5 | **Auth troubleshooting guide** | `docs/troubleshooting/auth.md`. Step-by-step: "Bridge says AUTH FAILURE" → check provider auth → re-login instructions for Claude Desktop / set ANTHROPIC_API_KEY / Codex token refresh. Per DELIB-GTKB-TOKEN-POSTURE, GT-KB provides this documentation but does not manage tokens. | 0.5 days |

**Phase G1 exit:** `mkdocs serve` renders a coherent adopter documentation site with a clear journey from install to first VERIFIED bridge thread. No Agent Red references in any adopter-facing doc.

**Est. total: 6 days**

### Phase G2: Cross-Platform Bridge Automation

**Goal:** `gt bridge start` runs the bridge scheduler on Windows, macOS, and Linux.

| WI | Deliverable | Scope | Est. |
|---|---|---|---|
| G2.1 | **Python bridge scheduler** | New module `src/groundtruth_kb/bridge/scheduler.py`. Replaces the PS1 scheduled-task dispatch pattern with a Python-based periodic scheduler. Uses stdlib `sched` module (no new dependency per owner's simplicity priority). Same 3-minute cadence, same `bridge/INDEX.md` scanning logic, same status-file JSON schema (`claude-scan-status.json`, `codex-scan-status.json`), same liveness-watcher dual-signal design. Runs as a foreground process (backgrounding is the adopter's responsibility via `nohup`, `screen`, `systemd`, `launchd`, or Windows Task Scheduler). | 3 days |
| G2.2 | **`gt bridge start` CLI command** | New CLI entry point in `cli.py`. `gt bridge start --agent prime` starts the scheduler for the named agent. `gt bridge status` reads the scan-status JSON files and reports freshness (same logic as `poller-freshness.py` hook). `gt bridge stop` writes a stop-sentinel that the scheduler checks each tick. | 1.5 days |
| G2.3 | **Bridge doctor integration** | Extend `gt project doctor` (from MVP `12fd083`) to check: bridge scheduler running (status file freshness), provider CLI auth (Claude/Codex), `bridge/INDEX.md` exists and is parseable. Report actionable next steps for each failure, pointing to `docs/troubleshooting/auth.md` for auth issues. | 1 day |
| G2.4 | **PS1 → Python migration path** | Document in `docs/migration/bridge-ps1-to-python.md` how existing Agent Red PS1 automation can coexist with or migrate to `gt bridge start`. PS1 scripts remain in-repo as reference but the docs recommend the Python scheduler for new projects. Agent Red's own migration is a separate, owner-approved change. | 0.5 days |
| G2.5 | **Cross-platform bridge tests** | Add tests for `scheduler.py` that run on all 3 platforms. Use `tmp_path` for status files, mock `subprocess` for agent dispatch. Add to CI matrix (Ubuntu + Windows + macOS). | 1.5 days |

**Phase G2 exit:** `pip install groundtruth-kb && gt project init my-project --profile dual-agent && gt bridge start --agent prime` works on Windows, macOS, and Linux. `gt project doctor` confirms bridge health.

**Est. total: 7.5 days**

### Phase G3: GitHub CI Template Generation

**Goal:** `gt project init` generates working CI workflows.

| WI | Deliverable | Scope | Est. |
|---|---|---|---|
| G3.1 | **CI workflow templates** | New directory `templates/github/workflows/`. Three profile tiers: `minimal` (lint + test), `standard` (+ coverage + docstring + mypy), `full` (+ security scan + accessibility + visual regression). Each workflow is a Jinja2 template parameterized by project name, Python version, and package name. Jinja2 added as a dependency (already widely used, well-known to developers). | 2 days |
| G3.2 | **`gt project init` CI integration** | Extend scaffold to generate `.github/workflows/` from the selected profile tier during `gt project init`. `--no-include-ci` flag (already exists) skips this step. Default behavior: generate CI matching the project profile. | 1 day |
| G3.3 | **Integration config templates** | Optional scaffolding for `.github/dependabot.yml`, `.coderabbitai.yaml`, `.sonarcloud.properties`. Generated when `gt project init --integrations` is passed. Each is a simple template with project-name substitution. | 1 day |
| G3.4 | **CI template tests** | Tests that verify generated workflows are valid YAML, reference the correct package name, and match the expected profile tier. | 1 day |

**Phase G3 exit:** `gt project init my-project --profile dual-agent-webapp` generates `.github/workflows/` with lint, test, coverage, docstring, and mypy CI steps. `gt project init my-project --profile dual-agent-webapp --integrations` additionally generates Dependabot and CodeRabbit config.

**Est. total: 5 days**

### Phase G4: Zero-Knowledge + Multi-Tenant Patterns

**Goal:** Advanced architectural patterns are scaffolded, not just specified.

| WI | Deliverable | Scope | Est. |
|---|---|---|---|
| G4.1 | **Terraform module templates** | Expand the existing Terraform stubs (from `scaffold.py:479-494`) into working Azure modules: resource group, container registry, Cosmos DB, Key Vault, Redis, Container Apps. Based on Agent Red's `terraform/` directory. Parameterized by project name, region, SKU tier. `gt project init --cloud-provider azure` generates a `terraform/` directory that can be `terraform plan`'d without edits. | 3 days |
| G4.2 | **Zero-knowledge architecture scaffold** | Implement the 4 existing ZK specs (BL-ZK-001). `gt project init --profile zero-knowledge` generates: tenant data isolation patterns, encrypted-at-rest configuration, zero-knowledge key management stubs, privacy-preserving API patterns. Implementation follows the 5-phase plan in MEMORY.md. | 5 days |
| G4.3 | **Multi-tenant architecture scaffold** | `gt project init --profile multi-tenant` generates: tenant isolation middleware, per-tenant configuration, shared-infrastructure-with-tenant-scoped-access patterns, tenant provisioning scripts. Based on Agent Red's `src/multi_tenant/` patterns. | 3 days |
| G4.4 | **Infrastructure tests** | Tests that verify: generated Terraform is syntactically valid (`terraform validate`), generated Docker configs build, generated multi-tenant patterns pass isolation assertions. | 2 days |

**Phase G4 exit:** `gt project init my-project --profile zero-knowledge --cloud-provider azure` generates a complete, `terraform plan`-able infrastructure with ZK data-handling patterns.

**Est. total: 13 days**

### Phase G5: Second Customer Validation

**Goal:** Prove GT-KB works for a project that isn't Agent Red.

| WI | Deliverable | Scope | Est. |
|---|---|---|---|
| G5.1 | **Internal dogfood project** | Use GT-KB to bootstrap a new internal project (could be a simple SaaS app, a documentation site, or a tool). Exercise the full adopter journey: `pip install` → `gt project init` → specs → tests → bridge → deliberations → deployment. Document friction, bugs, and gaps encountered. | 5 days |
| G5.2 | **Friction report** | Write up every point where the adopter journey was unclear, broken, or required Agent Red knowledge. File work items for each gap. This becomes the input for a post-G5 polish round. | 1 day |
| G5.3 | **Polish round** | Fix the top-5 friction items from G5.2. These are likely doc clarifications, scaffold edge cases, or doctor checks that need tuning. | 3 days |

**Phase G5 exit:** A second project exists that uses GT-KB end-to-end, and the friction items from that adoption are documented and the worst ones fixed.

**Est. total: 9 days**

---

## Dependency Graph

```
G1 (adopter docs) — no dependencies, can start immediately
│
G2 (cross-platform bridge) — no dependencies, can start in parallel with G1
│
G3 (GitHub CI templates) — depends on G1.1 (Getting Started should reference generated CI)
│
G4 (ZK + multi-tenant) — depends on G3.1 (Terraform scaffolding uses the same template engine)
│
G5 (second customer) — depends on G1 + G2 + G3 (needs the adopter path to exist)
    └── G4 is NOT a dependency of G5 (advanced patterns are optional for the second customer)
```

**Critical path:** G1 + G2 (parallel, ~7.5 days) → G3 (5 days) → G5 (9 days) = **~21.5 days to "ready for mass adoption" without advanced patterns.**

G4 (13 days) runs in parallel with G3+G5 and is not on the critical path unless the second customer specifically needs ZK or multi-tenant.

---

## Estimated Total

| Phase | WIs | Est. days | Parallel? |
|---|---|---|---|
| G1 Adopter documentation | 5 | 6 | Yes (with G2) |
| G2 Cross-platform bridge | 5 | 7.5 | Yes (with G1) |
| G3 GitHub CI templates | 4 | 5 | After G1.1 |
| G4 ZK + multi-tenant | 4 | 13 | Parallel with G3+G5 |
| G5 Second customer | 3 | 9 | After G1+G2+G3 |
| **Total** | **21** | **40.5 days** | |
| **Critical path** | | **~21.5 days** | |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Cross-platform bridge scheduler is harder than estimated (platform-specific process management, signal handling) | Medium | G2.1 uses stdlib `sched` with no daemon mode — adopter handles backgrounding. Keeps implementation simple. |
| Jinja2 dependency rejected | Low | Alternative: Python string.Template (stdlib, limited). Jinja2 is already a near-universal Python dependency. |
| Terraform templates drift from Agent Red's actual infra | Medium | G4.1 is parameterized FROM Agent Red's working terraform; divergence tracked via assertions. |
| Second customer finds fundamental architecture issues | High | G5 is deliberately last. If it reveals deep problems, those feed back into G1-G4 as a follow-up cycle, not a blocker. |
| ZK implementation is more complex than 5-day estimate | High | ZK has 31 WIs across 5 phases per MEMORY.md. The 5-day estimate is for SCAFFOLDING the patterns, not implementing the full ZK system. Owner should decide how deep the scaffold goes. |
| Adopter docs reference Agent Red patterns | Medium | G1 exit criterion explicitly requires zero Agent Red references. Review each doc with `grep -i "agent.red\|remaker"` before declaring done. |

---

## Open Decisions for Codex

1. **G1 + G2 parallel start.** Both phases have no dependencies. Should implementation start with G1 (docs, lower risk, validates the adopter mental model) or G2 (bridge, higher technical value, unblocks real cross-platform usage)? **Recommendation:** start both in parallel — G1 by Prime Opus (writing), G2 by headless Sonnet (coding). Same dual-track pattern that worked for 4B.8 + 4B.9.

2. **Template engine.** G3 proposes Jinja2. The prior mass-adoption-readiness review cycle did not reach a final answer on this. **Recommendation:** Jinja2. GitHub workflow templates have conditional sections (e.g., security scan only in `full` profile) that string.Template can't handle cleanly.

3. **G4 scope depth.** The ZK scaffold could range from "generate directory structure + placeholder files" (2 days) to "generate working encryption + key management + privacy patterns" (10+ days). **Recommendation:** generate the structure + documented patterns that a developer fills in, not working crypto code. GT-KB is a scaffolding tool, not a crypto library.

4. **G5 candidate project.** What should the second customer project be? Options: (a) a new internal Remaker Digital project, (b) the GT-KB project itself (dogfood — use GT-KB to manage GT-KB), (c) an open-source example project published alongside GT-KB. **Recommendation:** (c) — an example project in the GT-KB repo under `examples/` that demonstrates the full adopter journey and doubles as a living integration test.

5. **Phase ordering strictness.** Should G3 wait for G1.1 to be VERIFIED, or can G3 start as soon as G1.1 is drafted (even if still in review)? **Recommendation:** start G3 when G1.1 draft exists, don't wait for VERIFIED. The Getting Started guide and CI templates inform each other.

---

## Success Criteria

GroundTruth-KB is ready for mass adoption when ALL of the following are true:

1. **Adopter self-service:** a developer on any platform runs `pip install groundtruth-kb`, follows the Getting Started guide, and has a working project with bridge, specs, and tests within 1 hour — without reading Agent Red source code or asking the maintainer
2. **Cross-platform bridge:** `gt bridge start --agent prime` runs on Windows, macOS, and Linux
3. **CI out of the box:** `gt project init` generates working GitHub CI workflows
4. **Doctor validates everything:** `gt project doctor` checks all 12 components and reports actionable fixes
5. **Second customer exists:** at least one project other than Agent Red uses GT-KB end-to-end and the friction report has been actioned
6. **Zero Agent Red references** in any adopter-facing documentation or generated template
7. **All existing quality gates pass:** 858+ tests, ≥70% coverage, ≥85% docstrings, mypy --strict clean, ruff clean

---

## Relationship to Prior Work

| Prior | Relationship |
|---|---|
| Phase 4B (4B.1-4B.9) | Prerequisite. Package quality is now sufficient for external adoption (858 tests, 70% coverage, 85% docstrings, mypy clean). |
| `gtkb-mass-adoption-readiness-012` VERIFIED | MVP. Landed provider templates, bridge INDEX scaffolding, doctor accuracy, bridge rule templates. This plan builds on that MVP. |
| SPEC-GTKB-SCOPE | Scope authority. All 12 components are addressed across G1-G5. |
| DELIB-GTKB-INIT-POSTURE | Command surface: `gt project init` is the entry point, not `gt init`. |
| DELIB-GTKB-TOKEN-POSTURE | Token scope: documentation only, no token management in GT-KB. G1.5 and G2.3 implement this as docs + doctor checks. |
| DELIB-0474, DELIB-0633 | Strategic context: staged execution, external validation before claims, alpha/developer-preview posture. G5 directly addresses DELIB-0633's "not yet proven across projects" finding. |
