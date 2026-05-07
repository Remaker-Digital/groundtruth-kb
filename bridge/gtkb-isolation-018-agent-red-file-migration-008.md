REVISED

# Implementation Proposal — GTKB-ISOLATION-018: Agent Red File Migration (REVISED-3, Inventory Re-Scope)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-06 (S334)
**Type:** Delta revision of `-005` (which is GO'd at `-006`); refreshes the Live-Probed Inventory section with corrected counts and platform-vs-Agent-Red splits.
**Predecessor:** `bridge/gtkb-isolation-018-agent-red-file-migration-005.md` (REVISED, GO'd at `-006`)
**Triggering owner directive:** S334 AskUserQuestion answer "Re-scope umbrella first" — owner directed re-probing all 12 sub-slice clusters and updating the umbrella inventory before further sub-slice drafting.
**Revision basis:** Inventory drift found during 18.D pre-draft probing (config/ 4→10, +1 platform-content `.githooks/` not in -005, scripts/ mixing platform and Agent-Red content not previously split, etc.). Total tracked files grew from 5,320 (2026-05-04) to 5,636 (2026-05-06); +316 in 2 days.

---

## Specification Links

All `-005` Specification Links carry forward unchanged. This revision additionally cites:

- S334 AUQ "18.D scope" answer "Re-scope umbrella first" — the source authority for filing this revision.
- S334 AUQ "Isolation move" answer — the higher-level directive elevating ISOLATION-018 completion to a release gate.

Cross-cutting required specs (re-cited for preflight matching, identical to `-005`):
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Bridge-protocol authority. Compliance: this revision lives at `bridge/gtkb-isolation-018-agent-red-file-migration-008.md`; INDEX update places `REVISED: -008` at top of the umbrella thread entry per `.claude/rules/file-bridge-protocol.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite governing specs. Compliance: this section enumerates the same governing specs as `-005`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED is conditional on test creation + execution derived from linked specs. Compliance: `-005`'s Test Plan (T1–T18, T-bridge-1, T-spec-1, T-spec-2) carries forward unchanged; the only delta is the inventory the tests will count against at execution time.

Cross-cutting advisory specs:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts. Compliance: this REVISED is a durable artifact preserving the inventory-drift findings and re-scope decision.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts/tests/reports/decisions. Compliance: cites `-005`, `-006`, `-007`, S334 AUQs, and live-probe evidence with explicit commands.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states. Compliance: this REVISED transitions the umbrella from "GO at -006 with -005's inventory snapshot" to "REVISED at -008 with refreshed inventory" without invalidating the historical -006 GO.

Topic-specific governance (carried forward from `-005`):
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision, S330) — Source authority.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — 5 binding rules; waiver policy; repo-topology contract.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — Machine-checkable contract.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (owner_decision, S331) — ACTIVE waiver covering the in-flight pre-migration state.
- `.claude/rules/project-root-boundary.md` — Active rule auto-loaded at session start; 5 binding rules.
- `.claude/rules/operating-model.md` — Application-vs-platform partition (§1, §2).
- `.claude/rules/canonical-terminology.md` — Repo identity rules.
- `.claude/rules/file-bridge-protocol.md` — Mandatory Specification Linkage Gate + Specification-Derived Verification Gate + Owner Decisions / Input Section Gate + Pre-Filing Preflight Subsection.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Placement contract.
- `DCL-APP-ROOT-MINIMIZATION-001` — Minimization principle for `applications/Agent_Red/` root.
- `GOV-STANDING-BACKLOG-001` — ISOLATION-018 is implicitly TOP-priority per this rule + S334 owner directive.
- `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` — VERIFIED precursor thread.
- `bridge/gtkb-isolation-018-agent-red-file-migration-005.md` — Predecessor proposal whose Test Plan, Sub-slice Plan, Migration Strategy, and Risk register carry forward unchanged.
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` — Codex GO on the umbrella concept; this revision does NOT invalidate that GO.
- `bridge/gtkb-isolation-018-agent-red-file-migration-007.md` — In-flight 18.A post-impl REPORT; reports against `-005`'s historical inventory snapshot which remains valid as a snapshot.
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md` — In-flight 18.C proposal (NEW); inventory in this revision validates the 18.C draft's docs/ split.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` — VERIFIED 18.B; not affected by this revision.
- `applications/Agent_Red/.gtkb-app-isolation.json` — Current isolation registry.

The Test Plan derives from these linked specs as in `-005`: T1–T18 cover the program-level invariants at 18.L; T-bridge-1, T-spec-1, T-spec-2 cover per-sub-slice gates. This revision does not modify the Test Plan; only the per-cluster file counts the tests will assert against at execution time differ.

## Owner Decisions / Input

This REVISED is filed in direct response to an S334 owner AUQ decision and depends on prior ISOLATION-018 program approval.

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "Sub-slice 18.D — how to handle the inventory drift found during live probe?" (S334, 2026-05-06) | "18.D scope" | Owner chose "Re-scope umbrella first": file a new bridge proposal that re-probes all 12 sub-slice clusters (18.B–18.L) and updates the umbrella `-005` inventory with corrected counts and platform-vs-Agent-Red split. | This `-008` is the requested re-scope. After Codex GO, sub-slice work resumes against the corrected inventory. |
| "Agent Red isolation — what's the next move?" (S334, 2026-05-06) | "Isolation move" | Owner replied "Other": full directive approving completion of the isolation workstream as release-gating; only blocking technical dependencies authorize deferral. | Authorizes umbrella program continuation and any sub-slice drafting that follows the corrected inventory. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 AUQ) | (S330) | Owner directive establishing 5 binding rules, waiver policy, repo-topology contract. | Source authority for the entire ISOLATION-018 program; the platform-vs-Agent-Red split in this revision honors RULE 1 (no Agent Red files at GT-KB root) AND the implicit contrapositive (no GT-KB platform files moved into `applications/Agent_Red/`). |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S330/S331 AUQ) | (S331) | ACTIVE waiver authorizing in-flight pre-migration state. | Continues to authorize Agent Red root-file presence during the migration window; waiver retired when 18.L VERIFIED. |

OQ-1 (history-preservation strategy at 18.J) and OQ-2/OQ-3 (legacy-remote handling) from `-005` remain explicit AUQ gates at start of sub-slice 18.J; this revision does NOT close them.

## Carry-Forward Statement

All sections of `-005` are carried forward VERBATIM EXCEPT the "Live-Probed Inventory" section (lines 118–191) and the "Sub-slice Plan" table footnote about `archive/` placement. Specifically carried forward unchanged:

- Codex Findings Addressed (Cycle 1 + Cycle 2)
- Background
- Specification Links (full set; this `-008` re-cites them all above for preflight matching)
- Prior Deliberations (S334 AUQ added below)
- Goal
- Migration Strategy (Repo-history preservation strategy; Order of operations; `git mv` discipline; Repo-target reconciliation)
- Specification-Derived Test Plan (T1–T18; per-sub-slice T-bridge-1, T-spec-1, T-spec-2; uses `python -m pytest`, `pytest`, `gh run list` commands per `-005` line 282)
- Specification-to-Test Mapping
- Acceptance Criteria
- Risk / Rollback (Risk register; Rollback)
- Open Questions for Codex / Owner (OQ-1 through OQ-10; defaults unchanged)
- Out of scope
- Project Root Boundary Compliance
- Provenance (additions appended below)

The intent of `-005`'s sub-slice plan table (lines 343–365) is preserved; a clarification on `archive/` placement is recorded in the "Sub-slice Allocation Clarification" section below.

## Prior Deliberations

`-005` Prior Deliberations table (lines 92–106) carries forward. Additions from this S334 session:

| DELIB / Source | Source Type | Outcome | Relevance |
|---|---|---|---|
| S334 AUQ "Isolation move" answer | owner_conversation | owner_decision | Authorizes ISOLATION-018 completion as release-gating |
| S334 AUQ "18.D scope" answer | owner_conversation | owner_decision | Authorizes this -008 re-scope |
| S331 AUQ answers (3 sub-decisions) | owner_conversation | owner_decision | Already-resolved 18.C scope decisions (platform exclusions; in-place workflow edits; docs-site atomicity) |

No prior deliberation rejects the umbrella's direction or the inventory re-scope; `DELIB-0879` superseded.

## Live-Probed Inventory — REFRESHED (2026-05-06)

`git ls-files | wc -l` = **5,636 tracked files** (was 5,320 on 2026-05-04; +316 in 2 days reflecting active session-wrap and bridge work).

### Per-top-level rollup (33 categories)

| Top-level | Tracked | Δ vs -005 | Disposition |
|---|--:|--:|---|
| `bridge/` | 2,343 | +216 | STAYS at GT-KB root (platform) |
| `tests/` | 726 | +17 | MIGRATES (Agent Red); 18.E |
| `groundtruth-kb/` | 490 | +24 | STAYS (platform) |
| `scripts/` | 480 | +12 | SPLIT (see scripts/ split table); 18.E |
| `admin/` | 361 | 0 | MIGRATES (Agent Red); 18.E |
| `src/` | 305 | 0 | MIGRATES (Agent Red); 18.E |
| `docs/` | 192 | +4 | SPLIT (22 platform stays, 170 Agent Red migrates); 18.C |
| `memory/` | 115 | +1 | SPLIT (per-file owner decisions); 18.I |
| `assets/` | 96 | 0 | DEFERRED — appears to be Docusaurus build output; investigation required (see below) |
| `docs-site/` | 88 | 0 | MIGRATES atomic dir-rename; 18.C |
| `branding/` | 67 | 0 | MIGRATES (Agent Red); 18.D |
| `.claude/` | 65 | +3 | STAYS (platform) |
| `independent-progress-assessments/` | 58 | 0 | STAYS (platform; LO output dir) |
| `.groundtruth/` | 52 | 0 | STAYS (platform; formal-approval-packet archive) |
| `widget/` | 51 | 0 | MIGRATES (Agent Red); 18.E |
| `.codex/` | 38 | +27 | STAYS (platform) |
| `.github/` | 20 | +2 | SPLIT (per workflow file); 18.G |
| `config/` | 10 | +6 | SPLIT (1 Agent Red, 9 platform); 18.D for the 1 |
| `applications/` | 10 | +3 | STAYS (destination scaffold) |
| `tools/` | 8 | 0 | STAYS (platform) |
| `infrastructure/` | 8 | 0 | MIGRATES (Agent Red Terraform); 18.F |
| `harness-state/` | 6 | +3 | STAYS (platform) |
| `legal/` | 4 | 0 | MIGRATES (Agent Red); 18.D |
| `.githooks/` | 4 | NEW | STAYS (platform; not in -005 inventory) |
| `archive/` | 3 | 0 | STAYS (platform; bridge-v1 archive — NOT Agent Red, contradicting -005 line 230 text but consistent with -005 line 158 table) |
| Top-level files | 36 | +1 | SPLIT (per-file disposition; 18.H + 18.I) |

### Platform clusters STAYING at GT-KB root (uncontested)

| Cluster | Tracked | Reason |
|---|--:|---|
| `bridge/` | 2,343 | Bridge protocol — platform infrastructure |
| `groundtruth-kb/` | 490 | GT-KB platform Python package |
| `.claude/` | 65 | Platform-level harness rules/hooks/skills |
| `independent-progress-assessments/` | 58 | Loyal Opposition output directory |
| `.groundtruth/` | 52 | Formal-approval-packets archive |
| `.codex/` | 38 | Platform-level Codex config |
| `tools/` | 8 | KB Python API + web UI + observability tooling |
| `harness-state/` | 6 | Role-record durables |
| `.githooks/` | 4 | **NEW since -005** — git pre-commit hooks (platform; not Agent Red CI) |
| `archive/bridge-v1/` | 3 | **CLARIFICATION** — `archive/bridge_poller_launcher.py`, `bridge_resident_worker_launcher.py`, `prime_bridge_supervisor.py` are GT-KB bridge-v1 retired infrastructure, NOT Agent Red. -005 inventory table (line 158) correctly placed at "18.I (review)"; -005 order-of-operations text (line 230) erroneously listed under 18.D. **Resolution: STAYS at GT-KB root; 18.I review may decide to retire/relocate but NOT to applications/Agent_Red/.** |

Platform total at root: ~3,067 tracked files (was 2,765 in -005 inventory; +302 reflecting active platform work).

### Agent Red clusters MIGRATING to `applications/Agent_Red/` (with sub-slice assignment)

| Cluster | Tracked | Sub-slice | Notes |
|---|--:|---|---|
| `src/` (multi_tenant 176 + agents 35 + integrations 33 + chat 23 + app 8 + quality_metrics 7 + presets 7 + jobs 7 + migrations 3 + observability 2 + main.py + ai-features + __init__.py + white-label) | 305 | 18.E | Python application code; touches imports |
| `tests/` | 726 | 18.E | Test suite; touches imports |
| `admin/` | 361 | 18.E | Admin app (Vite + React + TypeScript) |
| `widget/` | 51 | 18.E | Chat widget (Preact + TypeScript) |
| `scripts/` (Agent Red split — see scripts/ split table below) | TBD | 18.E | Mixed; per-script disposition required |
| `docs/` (Agent Red split — see -001 of 18.C draft) | 170 | 18.C | Already drafted; 22 platform exclusions identified |
| `docs-site/` | 88 | 18.C | Atomic dir-rename |
| `branding/` | 67 | 18.D | All Agent Red brand assets |
| `infrastructure/terraform/` | 8 | 18.F | Agent Red production Terraform |
| `legal/` | 4 | 18.D | Agent Red legal docs |
| `config/stripe_product_ids.json` | 1 | 18.D | Agent Red Stripe pricing |
| `Dockerfile`, `Dockerfile.test`, `Dockerfile.ui`, `docker-compose.yml`, `.dockerignore` | 5 | 18.F | Agent Red container builds |
| `package.json`, `package-lock.json` | 2 | 18.H | Agent Red Node package roots (note: -005 line 161 mentioned `package-pdf.json` but it does not exist in current tree) |
| `pyproject.toml`, `requirements.txt`, `requirements-test.txt`, `requirements-local.txt`, `uv.lock` | 5 | 18.H | Agent Red Python package config |
| `shopify.app.toml`, `.shopifyignore`, `sitemap.xml`, `sonar-project.properties` | 4 | 18.H | Agent Red Shopify + tooling configs |
| `.env.example`, `.env.integration.example` | 2 | 18.H | Agent Red env templates |
| `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `vision.md`, `MEMORY.md`, `CHANGELOG.md`, `SECURITY.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md` | 10 | 18.I | Agent Red top-level identity files |
| `AGENTS.md` | 1 | 18.I | OQ-4 — ambiguous; default = stays at root |
| `_split_superadmin.py` | 1 | 18.I | Agent Red script |
| Agent-Red identity reports (PDF cluster) | 9 | **18.B (DONE — VERIFIED)** | Already moved per `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` |

### Splits requiring per-file disposition

#### `scripts/` split (480 files)

`-005` did not enumerate scripts/ split detail. Live-probed subdir breakdown:

| Subdir | Tracked | Disposition (recommended) |
|---|--:|---|
| `scripts/archive/` | 109 | DEFER to 18.I review — historical scripts; ownership per-file |
| `scripts/pre-flight-results/` | 65 | STAYS (platform — preflight-output dump, GT-KB workflow artifact) |
| `scripts/rehearse/` | 15 | STAYS (platform — rehearsal scaffolding per `.claude/rules/project-root-boundary.md` Sandbox Output Exception) |
| `scripts/upgrade-results/` | 14 | STAYS (platform — `gt project upgrade --dry-run` output) |
| `scripts/gtkb_dashboard/` | 10 | STAYS (platform — dashboard tooling) |
| `scripts/deploy/` | 10 | SPLIT per-file — some Agent Red production deploy, some GT-KB platform |
| `scripts/_report_charts_ar/` | 10 | MIGRATES (Agent Red — "ar" suffix denotes Agent Red) |
| `scripts/_report_charts/` | 9 | STAYS (platform — generic chart-generation library) |
| `scripts/guardrails/` | 8 | STAYS (platform) |
| `scripts/benchmark-results/` | 7 | DEFER to 18.I review — output dumps |
| `scripts/lib/` | 3 | STAYS (platform — shared script lib) |
| `scripts/stripe/` | 2 | MIGRATES (Agent Red — Stripe is Agent Red payment processor) |
| `scripts/<top-level scripts>` | ~218 | SPLIT per-file at 18.E execution; majority Agent Red operational scripts (wire_tests_to_phases, verify_zk_pillars, _archive_*, _capture_*, _insert_*, _defect_reporter, _env, etc.) |

**18.E will need a per-file scripts/ disposition table when its bridge thread is filed**; this revision identifies the structural complexity but defers the per-file decisions to the 18.E proposal authoring step.

#### `.github/workflows/` split (16 of 20 .github/ files)

| Workflow | Disposition |
|---|---|
| `accessibility.yml` | MIGRATES (Agent Red CI) |
| `build-agent-containers.yml` | MIGRATES (Agent Red containers) |
| `build-api-gateway.yml` | MIGRATES (Agent Red) |
| `build-slim-gateway.yml` | MIGRATES (Agent Red) |
| `build-test-host.yml` | MIGRATES (Agent Red) |
| `chromatic.yml` | MIGRATES (Agent Red visual regression) |
| `deploy-docs.yml` | MIGRATES (Agent Red docs deployment; in-place path edits already done in 18.C draft) |
| `docs-quality.yml` | MIGRATES (Agent Red docs quality; in-place path edits already done in 18.C draft) |
| `groundtruth-kb-tests.yml` | **NEW since -005** — STAYS (GT-KB platform tests) |
| `gtkb-secrets-scan.yml` | **NEW since -005** — STAYS (GT-KB platform secrets scanner) |
| `lint.yml` | SPLIT — needs review (mixed coverage) |
| `python-tests.yml` | MIGRATES (Agent Red Python tests) |
| `release-candidate-gate.yml` | SPLIT or DUPLICATE — both projects need release-candidate gates with project-specific check sets |
| `security-scan.yml` | MIGRATES (Agent Red security scan) |
| `sonarcloud.yml` | MIGRATES (Agent Red SonarCloud) |
| `visual-regression.yml` | MIGRATES (Agent Red) |

Plus `.github/dependabot.yml`, `.github/ISSUE_TEMPLATE/` (2 files), `.github/pull_request_template.md` — all SPLIT or per-project.

#### `memory/` split (115 files; reduced complexity from -005)

`-005` line 175 noted "split per Agent Red status vs PB platform feedback". Live-probed breakdown:
- `memory/feedback/` (60 files) — mostly platform GT-KB Prime Builder feedback
- `memory/topics/` (43 files) — mixed; per-file disposition needed
- `memory/work_list.md` — platform (standing-backlog authority per `GOV-STANDING-BACKLOG-001`)
- `memory/release-readiness.md` — platform (release-readiness record)
- `memory/pending-owner-decisions.md` — platform (owner-decision tracker output)
- `memory/project_external_resource_registry.md` — platform
- `memory/feedback_preflight_before_filing_bridge_proposals.md` — platform
- `memory/testing-research.md` — Agent Red likely
- `memory/session-wrap-2026-04-29.md` — likely platform session-wrap
- `memory/s133-live-test-migration.md` — Agent Red (S133-era Agent Red work)

18.I will need per-file dispositions; majority appears to be platform.

### Investigation required before sub-slice work proceeds

#### `assets/` (96 files) — appears to be Docusaurus build output

Live probe: `git ls-files assets/` returns only `assets/css/*` and `assets/js/*` files (CSS chunks and JS chunks with hash suffixes characteristic of Docusaurus or webpack output).

Hypothesis: these were committed as the BUILT output of an old `docs-site/` rebuild before docs-site/ was canonicalized as the source-only tree. They may be:
- (a) Stale build artifacts that should be DELETED (production hosting reads from a deployment artifact, not the repo).
- (b) Live-served static assets referenced by some external URL pinning to the GT-KB raw-content URL.
- (c) A snapshot intentionally committed for offline reference.

**Recommendation:** 18.D EXCLUDES `assets/` pending an investigation to determine which hypothesis is correct. If (a), delete in 18.L cleanup. If (b), MIGRATE with 18.C (atomic with docs-site/) plus URL-rewrite in any external pinning. If (c), MIGRATES to `applications/Agent_Red/assets/` per Agent Red ownership.

The investigation: (1) `git log --diff-filter=A assets/css/` to find the commit that added them, (2) `grep -rn "agentredcx.com/assets/" .` to find any URL pinning, (3) check `docs-site/docusaurus.config.js` build output dir, (4) ask owner if uncertain.

This investigation is in 18.D scope but yields a "DEFER assets/ to 18.L cleanup" disposition unless evidence points elsewhere. The 96 build-output files are NOT moved as Agent Red source content under this revision's plan.

## Sub-slice Allocation Clarification

`-005` had an internal contradiction between the inventory table (line 158: `archive/` → 18.I review) and the order-of-operations text (line 230: 18.D includes `archive/`). This revision resolves in favor of the inventory table:

- **`archive/bridge-v1/` is GT-KB platform, NOT Agent Red.** It STAYS at GT-KB root. The 18.I "review" entry in `-005` is preserved: 18.I may decide to retire or relocate these scripts WITHIN GT-KB, but they do NOT migrate to `applications/Agent_Red/`.
- **18.D scope (corrected):** `branding/` (67) + `legal/` (4) + `config/stripe_product_ids.json` (1) = **72 files** moved. Defers `assets/` (96, pending investigation) and `archive/` (3, platform). Net 18.D: 72 files moved, 99 deferred-with-rationale.

## Updated Total Counts

- **Total tracked files:** 5,636 (was 5,320)
- **Migrating to `applications/Agent_Red/`:** ~1,820 estimated (305 src + 726 tests + 361 admin + 51 widget + ~150 Agent-Red scripts + 170 Agent Red docs + 88 docs-site + 67 branding + 8 infrastructure/terraform + 4 legal + 1 stripe + 5 Dockerfiles + 12 manifests + 4 Shopify/tooling + 2 env-templates + 11 top-level identity + ~50 to-be-disambiguated)
- **Staying at GT-KB root (platform):** ~3,067 tracked files (bridge/, groundtruth-kb/, .claude/, independent-progress-assessments/, .groundtruth/, .codex/, tools/, harness-state/, .githooks/, archive/bridge-v1/, scripts/ platform portion, docs/ platform portion, memory/ platform portion, .github/ platform portion, config/ platform portion, applications/, top-level platform files)
- **Investigation-required (deferred):** `assets/` (96)

The sub-slice plan from `-005` (12 sub-slices 18.A through 18.L) remains operative; only the per-cluster file dispositions refine. The order-of-operations sequence (18.A inventory → 18.B PDF → 18.C docs → 18.D non-functional content → 18.E code → 18.F infra → 18.G CI → 18.H manifests → 18.I identity + memory → 18.J repo separation → 18.K platform docs install → 18.L verification) is unchanged.

## Acceptance Criteria

In addition to `-005`'s acceptance criteria for the umbrella:

- [ ] Codex GO on this `-008` revision (which supersedes the inventory section of `-005` while preserving `-006`'s GO on the umbrella concept)
- [ ] Inventory drift findings reviewed and accepted; per-cluster splits validated against `git ls-files` execution-time evidence
- [ ] `archive/bridge-v1/` placement clarification accepted (stays at GT-KB root; 18.I may relocate within platform but NOT to applications/Agent_Red/)
- [ ] `assets/` deferral accepted pending investigation
- [ ] `.githooks/` recognized as platform (not in -005 inventory)
- [ ] config/ split accepted (9 platform stays, 1 stripe migrates)

## Risk / Rollback

`-005`'s risk register and rollback plan carry forward. Additional risks introduced by re-scoping:

| New risk | Likelihood | Impact | Mitigation |
|---|--:|--:|---|
| Inventory continues to drift between `-008` GO and per-sub-slice execution | High | Low | Each sub-slice already does live `git ls-files` re-confirmation per `-005` design (line 209: "Final list re-confirmed via `git ls-files docs/` to catch drift"). This revision codifies that pattern as required for all sub-slices. |
| Codex disagrees with platform-vs-Agent-Red splits I propose for borderline clusters (scripts/, .github/workflows/lint.yml) | Medium | Medium | Per-sub-slice proposals will surface borderline disposition decisions via AskUserQuestion to the owner; this `-008` does not pre-decide them, only identifies the structural complexity. |
| `assets/` investigation reveals option (b) (live-served URL pinning) too late, requiring URL-rewrite in 18.C retrospectively | Medium | Medium | Investigation is filed as 18.D scope; if (b), it triggers a 18.C revision (-002+) with URL-rewrite step. Pre-investigation, 18.C plan stays unchanged (atomic dir-rename). |

## Pre-Filing Preflight Subsection

This revision will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-agent-red-file-migration` after INDEX update to point at `-008`. Expected: `preflight_passed: true` because Specification Links carries the full required+advisory set forward and content cites all triggered cross-cutting specs.

`packet_hash` recorded in post-Write preflight evidence.

## Provenance (additions to `-005`)

| Source | Reference |
|--------|-----------|
| Triggering owner directive (S334 AUQ) | "Sub-slice 18.D — how to handle the inventory drift found during live probe?" → "Re-scope umbrella first" |
| Higher-level S334 directive | "Agent Red isolation — what's the next move?" → "Other": full directive approving completion of the isolation workstream |
| Live inventory probe | `git ls-files | wc -l = 5636`; per-top-level rollup via `git ls-files | awk -F/ 'NF>1 {print $1}' | sort | uniq -c | sort -rn`; per-subdir probes for branding/, legal/, config/, archive/, assets/, src/, scripts/, .github/, infrastructure/, memory/, tools/, docs/ (executed 2026-05-06 in this session) |
| 18.A REPORT in flight | `bridge/gtkb-isolation-018-agent-red-file-migration-007.md` (NEW; awaiting Codex VERIFIED). Note: -007 reports against `-005`'s inventory snapshot which was correct at draft time; this `-008` updates the inventory for forward sub-slices but does not invalidate `-007`'s historical claims. |
| 18.C draft promoted | `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md` (NEW; awaiting Codex GO; reflects -005 docs/ inventory which is materially correct with +4 file drift) |

## Out of scope

This `-008` does NOT:
- Pre-decide per-file dispositions for scripts/, memory/, .github/ — those happen in their respective sub-slice proposals.
- Resolve OQ-1 / OQ-2 / OQ-3 (deferred to start of 18.J per `-005`).
- Investigate `assets/` — that's 18.D scope per the corrected plan.
- Modify the 18.C draft — `-001` of slice-c-docs-cluster reflects 18.C inventory accurately enough to proceed; if Codex finds drift in 18.C-specific clusters, that thread revises independently.
- Test or verify any code changes — spec-derived testing per `pytest` and `python -m pytest` invocations from `-005` Test Plan applies at sub-slice execution time, not at this revision's submission.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
