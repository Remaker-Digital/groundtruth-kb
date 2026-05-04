NEW

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.C: Docs Cluster Move

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice of GTKB-ISOLATION-018 (umbrella scoping `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` GO'd 2026-05-04)
**Cluster:** Agent Red documentation (`docs/` minus 3 platform-content exclusions, plus entire `docs-site/` Docusaurus site)
**Risk tier:** Medium (large file count but mostly bulk dir-rename; cross-references in 2 GitHub workflow files require in-place updates)
**Waiver basis:** `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE (per `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` VERIFIED). The waiver's SCOPE clause authorizes Agent Red root-file work during ISOLATION-018 execution.

---

## Background

This is the second concrete file-move sub-slice of the ISOLATION-018 program (after 18.B PDF cluster, VERIFIED at `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md`). The umbrella inventory at `bridge/gtkb-isolation-018-agent-red-file-migration-005.md:151-152` lists `docs/` (188 tracked files) and `docs-site/` (88 tracked files) for sub-slice 18.C.

This sub-slice is NOT a simple `git mv` of two directories because three subdirectories of `docs/` are GT-KB platform content, not Agent Red, and per `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` only Agent Red files migrate to `applications/Agent_Red/`. Per S331 owner directive (this proposal cycle, AskUserQuestion answers): the three platform subdirectories STAY at GT-KB root.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md`; INDEX update at top of `bridge/INDEX.md` is the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this section enumerates all governing specs (cross-cutting + topic-specific + advisory).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section maps every spec clause to a concrete test command and expected result.

Topic-specific governance for this work:

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner_decision, S330) — Source rule that authorizes the migration program; this sub-slice executes the rule's required end state for the docs cluster.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 (specified) — 5 binding rules including RULE 3 (Agent Red files MUST live in `applications/Agent_Red/`) and RULE 1 (no Agent Red files at GT-KB root). Compliance: this sub-slice moves Agent Red docs into compliance.
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 (specified) — Machine-checkable contract whose `exceptions[0]` clause cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER`. Compliance: this sub-slice's commits are covered by the waiver's SCOPE clause.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (owner_decision, S331) — **ACTIVE waiver** authorizing in-flight Agent Red root-file work. Compliance: this proposal cites the waiver per the CITATION OBLIGATION clause; commit is within waiver SCOPE.
- 2026-05-04 owner correction in `CLAUDE.md` — GT-KB platform content stays at GT-KB root, only Agent Red content moves. Compliance: this proposal explicitly excludes `docs/gtkb-dashboard/`, `docs/specification-scaffold/`, and `docs/assets/gtkb-dashboard/` per S331 owner AskUserQuestion confirmation in this session.
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (Codex GO 2026-05-04) — Umbrella scoping that defines this sub-slice. The umbrella's inventory at "Migrates to applications/Agent_Red/" lists docs/ (188) and docs-site/ (88). This proposal extends the umbrella with platform-content exclusions identified during live probing.
- `applications/Agent_Red/.gtkb-app-isolation.json` — Existing isolation registry; this proposal extends it with two new top-level entries (`docs`, `docs-site`).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Placement contract authorizing `applications/Agent_Red/` as the destination namespace.
- `DCL-APP-ROOT-MINIMIZATION-001` (proposed; pending sub-slice 6 of the application-isolation-contract program) — Minimization principle for `applications/Agent_Red/` root. The new `docs/` and `docs-site/` top-level entries will be added to the isolation registry's `top_level_artifacts[]` array as Bucket=A.
- `.claude/rules/project-root-boundary.md` — Project root boundary rule; auto-loaded at session start. This sub-slice operates entirely within `E:/GT-KB/`.
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; this proposal complies with Mandatory Specification Linkage Gate + Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; this proposal is the artifact submitted for review.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation; satisfied via Prior Deliberations section.
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-007.md` (Codex GO at -008; VERIFIED at -012) — Pattern precedent for sub-slice mechanics including in-place edits to files outside the cluster (script OUTPUT_PATH edits in 18.B; workflow path edits in 18.C).

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts. Compliance: this sub-slice produces a per-slice post-impl REPORT, an updated `.gtkb-app-isolation.json` registry entry, and updated workflow path strings.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts, tests, reports, decisions. Compliance: this proposal cites the umbrella, the waiver, the registry, the source rule, and the 18.B precedent; implementation preserves git history via `git mv` for tracked files.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states. Compliance: this sub-slice transitions tracked Agent Red docs from "active at GT-KB root (in violation, waiver-covered)" to "active at applications/Agent_Red/{docs,docs-site}/ (rule-compliant)".

The proposed tests in the Test Plan section derive from these linked specs as follows: GOV RULE 3 → T-rule-1 + T-inv-1 (Agent Red docs at applications/Agent_Red/); GOV RULE 1 → T-rule-2 (no migrated docs files at root); platform-exclusion contract → T-platform-stay (3 platform subdirs remain at docs/); workflow CI integrity → T-wf-1 + T-wf-2 (in-place workflow edits resolve correctly); registry update → T-reg-1; no-import-break → T-import-1; bridge protocol → T-bridge-1; preflight → T-spec-1; spec-derived testing → T-spec-2; waiver citation → T-waiver-1; git-mv history → T-history-1; platform smoke → T-platform-smoke-1; manifest co-location → T-pkg-1 (docs-site package.json resolves at new location).

## Prior Deliberations

Search performed against `groundtruth.db` deliberations table (per `.claude/rules/deliberation-protocol.md`):

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source rule authorizing this work |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` | owner_conversation | owner_decision | ACTIVE waiver covering in-flight Agent Red root-file work |
| Bridge thread DELIBs at `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (umbrella GO), `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` (waiver VERIFIED), `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED) | bridge_thread | go / verified | Programmatic predecessors and pattern precedent |
| S331 AskUserQuestion answers (this session) | owner_conversation | owner_decision | Three scope confirmations: (a) platform exclusions for gtkb-dashboard, specification-scaffold, assets/gtkb-dashboard; (b) in-place workflow edits in 18.C; (c) atomic dir-rename for docs-site/ |

No prior deliberation rejects moving Agent Red docs into `applications/Agent_Red/docs/` or the entire `docs-site/` into `applications/Agent_Red/docs-site/`.

## Goal

Move all Agent Red documentation files from `E:/GT-KB/docs/` and `E:/GT-KB/docs-site/` to `E:/GT-KB/applications/Agent_Red/docs/` and `E:/GT-KB/applications/Agent_Red/docs-site/` respectively, preserving GT-KB platform content (`docs/gtkb-dashboard/`, `docs/specification-scaffold/`, `docs/assets/gtkb-dashboard/`) at GT-KB root. Update GitHub workflow path references (deploy-docs.yml, docs-quality.yml) in-place to point at the new docs-site location. Update `applications/Agent_Red/.gtkb-app-isolation.json` registry with two new Bucket-A entries.

## Live-Probed Inventory (2026-05-04)

### Stays at GT-KB root (platform content; per S331 owner AskUserQuestion confirmation)

| Path | Tracked | Why platform |
|------|--------:|--------------|
| `docs/gtkb-dashboard/` | 12 | Referenced by `scripts/gtkb_dashboard/refresh_dashboard_db.py:409`, `scripts/gtkb_overlay.py:55-57`, `.codex/gtkb-hooks/session_start_dispatch.py:53`, `groundtruth-kb/tests/test_scaffold_isolation.py:290` |
| `docs/specification-scaffold/` | 4 | README explicitly states: "specification templates and boilerplate specifications used to bootstrap new projects built on the groundtruth-kb knowledge database" |
| `docs/assets/gtkb-dashboard/` | 6 | 6 PNG screenshots of GT-KB dashboard UI |

Platform total at root: **22 tracked files** (4 ignored files in docs/ all live inside docs/gtkb-dashboard/ which stays).

### Migrates to `applications/Agent_Red/docs/`

| Path | Tracked files | Notes |
|------|--------------:|-------|
| `docs/admin-guide/` | 21 | git mv subdir |
| `docs/architecture/` | 12 | git mv subdir |
| `docs/archive/` | 2 | git mv subdir |
| `docs/billing/` | 3 | git mv subdir |
| `docs/design/` | 1 | git mv subdir |
| `docs/getting-started/` | 3 | git mv subdir |
| `docs/integrations/` | 1 | git mv subdir |
| `docs/legal/` | 1 | git mv subdir |
| `docs/marketing/` | 2 | git mv subdir |
| `docs/operations/` | 31 | git mv subdir |
| `docs/plans/` | 2 | git mv subdir |
| `docs/proposals/` | 6 | git mv subdir |
| `docs/reports/` | 1 | git mv subdir |
| `docs/research/` | 6 | git mv subdir |
| `docs/shopify/` | 12 | git mv subdir |
| `docs/specs/` | 1 | git mv subdir (SPEC-1879 phone identity channel; Agent Red spec) |
| `docs/tests/` | 3 | git mv subdir |
| `docs/vision/` | 2 | git mv subdir |
| `docs/workflows/` | 4 | git mv subdir |
| `docs/assets/prechat-form-phone-mockup.html` | 1 | git mv individual file (gtkb-dashboard/ subdir at docs/assets/gtkb-dashboard/ stays) |
| `docs/assets/prechat-form-phone-optin.png` | 1 | git mv individual file |
| `docs/<top-level Agent Red files>` | ~50 | Top-level .md/.docx/.html files (AGENT-RED-*, COMMERCIAL-*, COMPREHENSIVE-*, etc.); count finalized at execution via `git ls-files docs/ -- ':!docs/gtkb-dashboard/' ':!docs/specification-scaffold/' ':!docs/assets/'` minus the 21 subdirs above |

**docs/ Agent Red migration total: 166 tracked files** (188 tracked total - 22 platform).

### Migrates to `applications/Agent_Red/docs-site/`

Single atomic dir-rename per S331 owner AskUserQuestion confirmation:

| Path | Tracked | Untracked-ignored | Notes |
|------|--------:|------------------:|-------|
| `docs-site/` (entire dir) | 88 | 42,498 | Docusaurus site for Agent Red product (`title: 'Agent Red Customer Experience'`, `url: 'https://agentredcx.com'` per `docs-site/docusaurus.config.js`). Ignored content is mostly `node_modules/`, `build/`, `.docusaurus/` — Docusaurus rebuildables that move atomically with the dir-rename and don't need re-installation at the new path. |

### In-place edits to files OUTSIDE the cluster (per 18.B precedent for OUTPUT_PATH script edits)

Per S331 owner AskUserQuestion confirmation (in-place edits in 18.C, not deferred to 18.G):

- `.github/workflows/deploy-docs.yml` — 3 path references to `docs-site/` (lines 12, 39, 52) updated to `applications/Agent_Red/docs-site/`. Workflow file itself stays in `.github/workflows/` (its migration is 18.G scope; only its internal path strings change now).
- `.github/workflows/docs-quality.yml` — 5 path references to `docs-site/` (lines 20, 25, 47, 66, 67) updated similarly.

These workflow files are GT-KB CI infrastructure. Their internal path strings reference the Docusaurus build location; updating those strings keeps the docs CI green during the transition window.

## Migration Strategy

### Step 1: Create destination directories + registry update

```
mkdir -p applications/Agent_Red/docs
```

(`applications/Agent_Red/docs-site/` will be created by the atomic dir-rename in Step 4; no `mkdir` needed.)

Update `applications/Agent_Red/.gtkb-app-isolation.json` to add 2 entries in `top_level_artifacts[]`:

```json
{
  "name": "docs",
  "type": "DIR",
  "bucket": "A",
  "purpose": "Agent Red documentation (admin guides, architecture, plans, proposals, marketing, etc.; migrated from GT-KB root in S331 sub-slice 18.C; covered by DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER v1 SCOPE clause). Platform docs (gtkb-dashboard, specification-scaffold, assets/gtkb-dashboard) explicitly excluded per S331 owner directive."
},
{
  "name": "docs-site",
  "type": "DIR",
  "bucket": "A",
  "purpose": "Agent Red Docusaurus site (agentredcx.com source); migrated from GT-KB root in S331 sub-slice 18.C as atomic dir-rename per owner directive; covered by DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER v1 SCOPE clause."
}
```

Update `last_updated` to `2026-05-04` (already set by 18.B; idempotent confirmation).

### Step 2: Move 21 Agent Red subdirectories of docs/ via per-subdir git mv

```
git mv docs/admin-guide applications/Agent_Red/docs/
git mv docs/architecture applications/Agent_Red/docs/
git mv docs/archive applications/Agent_Red/docs/
git mv docs/billing applications/Agent_Red/docs/
git mv docs/design applications/Agent_Red/docs/
git mv docs/getting-started applications/Agent_Red/docs/
git mv docs/integrations applications/Agent_Red/docs/
git mv docs/legal applications/Agent_Red/docs/
git mv docs/marketing applications/Agent_Red/docs/
git mv docs/operations applications/Agent_Red/docs/
git mv docs/plans applications/Agent_Red/docs/
git mv docs/proposals applications/Agent_Red/docs/
git mv docs/reports applications/Agent_Red/docs/
git mv docs/research applications/Agent_Red/docs/
git mv docs/shopify applications/Agent_Red/docs/
git mv docs/specs applications/Agent_Red/docs/
git mv docs/tests applications/Agent_Red/docs/
git mv docs/vision applications/Agent_Red/docs/
git mv docs/workflows applications/Agent_Red/docs/
```

Each `git mv` of a subdirectory renames all tracked files within it as a bulk operation; git records each as a rename for `--follow` history preservation.

### Step 3: Move docs/ top-level Agent Red files

Enumerated dynamically at execution via `git ls-files docs/ -- ':(top)docs/[!a-z]*' ':(top)docs/[a-z][^/]*\.[a-z]*'` (matches files at docs/ top level only, not subdirectory contents). Concrete list reproduced from live probe:

```
git mv docs/AGENT-RED-QUALITY-EVALUATION-UPDATE-2026-03-09.md applications/Agent_Red/docs/
git mv docs/AGENT-RED-QUALITY-EVALUATION.md applications/Agent_Red/docs/
git mv docs/AGNTCY-BASELINE-VERIFICATION-REPORT.md applications/Agent_Red/docs/
git mv docs/Agent-Red-Executive-Summary.docx applications/Agent_Red/docs/
git mv docs/Agent-Red-Full-Assessment-2026-03-05.docx applications/Agent_Red/docs/
git mv docs/COMMERCIAL-SAAS-PROPOSAL.md applications/Agent_Red/docs/
git mv docs/COMPREHENSIVE-TEST-PLAN.md applications/Agent_Red/docs/
git mv docs/GITHUB-HYGIENE-CHECKLIST.md applications/Agent_Red/docs/
git mv docs/INTEGRATION-TESTING-SETUP.md applications/Agent_Red/docs/
git mv docs/MASTER-TEST-PLAN-1.0.md applications/Agent_Red/docs/
git mv docs/Master-Plan-Review-01-30-2026.md applications/Agent_Red/docs/
git mv docs/PRODUCT-FEATURES-RAG.md applications/Agent_Red/docs/
git mv docs/PROJECT-PLAN.md applications/Agent_Red/docs/
git mv docs/PROTECTED-BEHAVIORS.md applications/Agent_Red/docs/
git mv docs/RAG-CONFIGURATION-MANAGEMENT-ENHANCEMENTS-PROPOSAL.md applications/Agent_Red/docs/
git mv docs/SESSION-INIT-LINT-REMEDIATION.md applications/Agent_Red/docs/
git mv docs/STRATEGIC-ASSESSMENT-2026-02-07.md applications/Agent_Red/docs/
git mv docs/admin-guide.html applications/Agent_Red/docs/
git mv docs/changelog.html applications/Agent_Red/docs/
```

Plus any other top-level `.md`/`.docx`/`.html` files enumerated by `git ls-files` at execution. Final list re-confirmed via `git ls-files docs/ | awk -F/ 'NF==2'` to catch any drift between proposal time and execution.

### Step 4: Move docs/assets/ Agent Red files (selective, leaving gtkb-dashboard/ subdir)

```
mkdir -p applications/Agent_Red/docs/assets
git mv docs/assets/prechat-form-phone-mockup.html applications/Agent_Red/docs/assets/
git mv docs/assets/prechat-form-phone-optin.png applications/Agent_Red/docs/assets/
```

`docs/assets/gtkb-dashboard/` (with its 6 platform PNGs) remains in place at `docs/assets/gtkb-dashboard/`.

### Step 5: Move docs-site/ via atomic dir-rename

```
git mv docs-site applications/Agent_Red/
```

This single command renames all 88 tracked files in git's index AND moves the entire directory tree on the filesystem (including the 42,498 untracked-ignored files: `node_modules/`, `build/`, `.docusaurus/`, etc.). New location: `applications/Agent_Red/docs-site/`.

### Step 6: Update GitHub workflow path references in-place

Edit `.github/workflows/deploy-docs.yml`:
- Line ~12: `'docs-site/**'` → `'applications/Agent_Red/docs-site/**'`
- Line ~39: `cache-dependency-path: docs-site/package-lock.json` → `cache-dependency-path: applications/Agent_Red/docs-site/package-lock.json`
- Line ~52: `path: docs-site/build` → `path: applications/Agent_Red/docs-site/build`

Edit `.github/workflows/docs-quality.yml`:
- Line ~20: `'docs-site/**'` → `'applications/Agent_Red/docs-site/**'`
- Line ~25: `'docs-site/**'` → `'applications/Agent_Red/docs-site/**'`
- Line ~47: `cache-dependency-path: docs-site/package-lock.json` → `cache-dependency-path: applications/Agent_Red/docs-site/package-lock.json`
- Line ~66: `--config=docs-site/.vale.ini sync` → `--config=applications/Agent_Red/docs-site/.vale.ini sync`
- Line ~67: `--config=docs-site/.vale.ini docs-site/docs` → `--config=applications/Agent_Red/docs-site/.vale.ini applications/Agent_Red/docs-site/docs`

Workflow files themselves stay in `.github/workflows/` (their migration is 18.G scope; only path strings change now). Total edits: 8 path-string substitutions across 2 files.

### Step 7: Commit on develop

Single commit on `develop` branch with message:

```
gtkb-isolation-018 Slice 18.C: docs cluster move to applications/Agent_Red/{docs,docs-site}/

Moves Agent Red documentation (166 tracked files in docs/) +
entire Docusaurus site (88 tracked + 42,498 ignored in docs-site/)
to applications/Agent_Red/. Excludes 3 platform-content
subdirectories from migration per S331 owner directive:
docs/gtkb-dashboard/ (12 files), docs/specification-scaffold/
(4 files), docs/assets/gtkb-dashboard/ (6 files). Updates 8 path
references in .github/workflows/{deploy-docs,docs-quality}.yml
in-place to point at the new docs-site location. Updates
applications/Agent_Red/.gtkb-app-isolation.json registry with 2
new Bucket-A entries (docs, docs-site).

Authorized by DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER v1 SCOPE
clause (in-flight Agent Red root-file work covered until ISOLATION-018
VERIFIED).

Refs: bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md
(Codex GO target);
bridge/gtkb-isolation-018-agent-red-file-migration-006.md (umbrella GO);
bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md (18.B VERIFIED, pattern precedent).
```

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-isolation-018-slice-c-docs-cluster" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-c-docs-cluster` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains Specification Links + spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-rule-1** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 | `find applications/Agent_Red/docs -type f \| wc -l` and `find applications/Agent_Red/docs-site -type f \| wc -l` | docs: 166 tracked + 0 untracked = 166. docs-site: 88 tracked + ~42,498 untracked-ignored ≈ 42,586 total |
| **T-rule-2** | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 1 | `git ls-files docs/ \| grep -vE "^docs/(gtkb-dashboard\|specification-scaffold\|assets/gtkb-dashboard)/"` and `git ls-files docs-site/` | First command returns only the 22 platform files; second returns empty (entire docs-site/ moved) |
| **T-platform-stay** | 2026-05-04 owner correction (platform stays at root) | `git ls-files docs/gtkb-dashboard/ \| wc -l`, `git ls-files docs/specification-scaffold/ \| wc -l`, `git ls-files docs/assets/gtkb-dashboard/ \| wc -l` | 12, 4, 6 respectively (unchanged) |
| **T-inv-1** | umbrella inventory match | `git ls-files applications/Agent_Red/docs/ \| wc -l` and `git ls-files applications/Agent_Red/docs-site/ \| wc -l` | 166 and 88 respectively |
| **T-reg-1** | `applications/Agent_Red/.gtkb-app-isolation.json` registry update | `python -c "import json; r=json.load(open('applications/Agent_Red/.gtkb-app-isolation.json')); names=[a['name'] for a in r['top_level_artifacts']]; print('docs' in names and 'docs-site' in names)"` | `True` |
| **T-wf-1** | workflow path updates (deploy-docs.yml) | `grep -c "applications/Agent_Red/docs-site" .github/workflows/deploy-docs.yml` and `grep -c "^[^#]*['\\\"]docs-site/" .github/workflows/deploy-docs.yml` | First: ≥3 (new path refs added). Second: 0 (no remaining bare docs-site/ refs in non-comment lines). |
| **T-wf-2** | workflow path updates (docs-quality.yml) | Same pattern as T-wf-1 against docs-quality.yml | First: ≥5. Second: 0. |
| **T-import-1** | no external import breakage | `grep -rn "docs-site/" --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --include="*.toml" --include="*.yml" --include="*.yaml" \| grep -vE "^(bridge/\|memory/\|independent-progress-assessments/\|applications/Agent_Red/docs-site/\|docs-site/node_modules/\|\.codex/\|\.claude/\|harness-state/\|\.github/workflows/(deploy-docs\|docs-quality)\.yml)"` | (empty) — no unhandled cross-references to the old `docs-site/` path |
| **T-pkg-1** | docs-site/package.json resolves at new location | `cd applications/Agent_Red/docs-site && cat package.json \| python -c "import json,sys,os; d=json.load(sys.stdin); print('name=' + d.get('name','?'))"` | Returns the package name from the manifest (no JSON parse errors; manifest survived the move) |
| **T-history-1** | tracked files preserve history via `git mv` | `git log --follow --oneline applications/Agent_Red/docs/AGENT-RED-QUALITY-EVALUATION.md \| wc -l` and `git log --follow --oneline applications/Agent_Red/docs-site/docusaurus.config.js \| wc -l` | Both >= 1 (history preserved across rename) |
| **T-waiver-1** | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` CITATION OBLIGATION | `git log -1 --pretty=%B` (most recent commit on develop) | Contains "DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER" |
| **T-platform-smoke-1** | GT-KB platform integrity preserved (gtkb-dashboard scripts continue resolving docs/gtkb-dashboard/ paths) | `python scripts/gtkb_overlay.py --help 2>&1 \| head -3` (smoke; verifies the script imports/resolves without breaking on docs/gtkb-dashboard/ path references) | Returns help text without ImportError or path resolution failure |
| **T-platform-smoke-2** | GT-KB platform tests | `python -m pytest groundtruth-kb/tests/ -x --tb=short -q -k "isolation or registry or scaffold" --timeout=60` | Pass (or pre-existing-known failures only; the scaffold-golden fixture mismatch from 18.B is documented as pre-existing) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `find`, `grep`, `ls`, `cat` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct (preflight pass) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct (Codex VERIFIED gate) |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 1 | T-rule-2 | Direct |
| `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` RULE 3 | T-rule-1, T-inv-1 | Direct |
| 2026-05-04 owner correction (platform stays at root) | T-platform-stay | Direct |
| `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` waiver-coverage | T-waiver-1 | Direct (commit cites waiver) |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` CITATION OBLIGATION | T-waiver-1 | Direct |
| `applications/Agent_Red/.gtkb-app-isolation.json` registry | T-reg-1 | Direct |
| Workflow CI integrity | T-wf-1, T-wf-2 | Direct (in-place workflow edits) |
| no-import-break invariant | T-import-1 | Direct |
| docs-site manifest co-location | T-pkg-1 | Direct |
| `git mv` history preservation | T-history-1 | Direct |
| GT-KB platform integrity | T-platform-smoke-1, T-platform-smoke-2 | Direct |
| Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | (no new tests; satisfied by registry update + REPORT structure + lifecycle-state transition) | Indirect |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Inventory and migration strategy reviewed; no missing files; no incorrect destinations; platform exclusions confirmed
- [ ] Workflow update strategy confirmed (in-place 18.C edits per S331 owner directive)

VERIFIED when:

- [ ] All 16 tests T-bridge-1 through T-platform-smoke-2 PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] No regression in GT-KB platform tests (T-platform-smoke-2 — pre-existing failures only)
- [ ] `applications/Agent_Red/docs/` exists with 166 tracked files; `applications/Agent_Red/docs-site/` exists with 88 tracked + node_modules/build/.docusaurus moved (T-rule-1 + T-inv-1)
- [ ] 22 platform-content files remain at `docs/gtkb-dashboard/` (12), `docs/specification-scaffold/` (4), `docs/assets/gtkb-dashboard/` (6) (T-platform-stay)
- [ ] No tracked Agent Red docs files at root (T-rule-2)
- [ ] Workflow files reference new paths only (T-wf-1, T-wf-2)
- [ ] Registry updated; isolation contract satisfied at the entry-level (T-reg-1)
- [ ] Stray harness state under migrated app directory absent (lesson from 18.B Codex `-010` F1 timing artifact: re-run T-rule-1 inventory after any in-session `cd` operations)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Hidden code reference to old `docs/` or `docs-site/` paths breaks at runtime | Medium | Medium | T-import-1 explicitly checks; the platform exclusion design preserves all GT-KB script-to-docs references (gtkb-dashboard refs unchanged); workflow refs explicitly handled in Step 6 |
| Atomic `git mv docs-site applications/Agent_Red/` slow or fails on Windows due to 42K-file count | Medium | Medium | git's directory rename is atomic at the index level even if the filesystem rename takes time; if filesystem rename fails partway, `git mv` errors and we can retry; rollback via `git revert` or `git mv` reversal |
| Workflow path updates miss a reference, breaking docs CI | Low | Medium | T-wf-1/T-wf-2 verify both path-pattern presence AND absence of bare old refs; manual re-grep in REPORT |
| docs/ subdir count drifts between proposal and execution (e.g., new subdirs added by parallel work) | Low | Low | Step 3 re-enumerates via live `git ls-files` at execution; subdir list re-confirmed against prior probe |
| Session-tracker hook re-creates `.claude/session/` under new applications/Agent_Red/{docs,docs-site}/ during in-session verification | Medium | Low (per 18.B `-010` precedent) | Avoid `cd` into the new directories during verification; use absolute paths; if it happens, owner-approved cleanup pattern from 18.B applies (split rm + rmdir) |
| `git mv` rename detection fails for some subdir due to internal file moves | Low | Low | `git mv` of a directory uses git's index rename which preserves history at the per-file level; T-history-1 verifies rename detection on at least 2 sample files |
| Registry JSON merge conflict if INDEX.md or registry was edited by parallel work mid-slice | Low | Low | Re-check `git status` before commit; rebase if needed |
| Platform smoke regression from script paths breaking | Low | High | T-platform-smoke-1 (gtkb_overlay.py smoke) and T-platform-smoke-2 (pytest subset) explicitly check; platform exclusions design preserves script-to-platform-doc refs |

Rollback: `git revert` of the single commit reverses all moves and workflow edits atomically. Untracked-ignored content (node_modules etc.) at the new docs-site/ location would need manual cleanup if revert is desired (or simply leave them; they're rebuildable).

## Open Questions

(All scope decisions resolved via S331 owner AskUserQuestion answers in this session; no open questions for this proposal.)

| ID | Question | Resolution |
|----|----------|------------|
| OQ-A | Platform exclusions: which docs/ subdirs stay at root? | All 3 confirmed: gtkb-dashboard, specification-scaffold, assets/gtkb-dashboard |
| OQ-B | Workflow refs handling? | In-place 18.C edits |
| OQ-C | docs-site/ move strategy? | Atomic dir-rename |

## Out of Scope

- Migration of `.github/workflows/` files themselves (18.G scope; only their path-string contents are touched in 18.C as in-place edits, mirroring 18.B's OUTPUT_PATH script-edits pattern).
- Migration of `scripts/` (18.E scope).
- Migration of `branding/`, `assets/` (18.D scope; note: `docs/assets/` is in 18.C scope but root-level `assets/` is a separate sub-slice).
- Migration of `package.json`, `package-lock.json`, root `pyproject.toml`, etc. (18.H scope).
- Cleanup of historical archive scripts in `scripts/archive/` that reference `docs/index.html` (these are archived one-time scripts; their string references are not active dependencies).
- Resolution of pre-existing `test_tp14_local_only_matches_golden_fixture` failure (documented in 18.B post-impl REPORT as pre-existing; separate fixture-refresh slice).
- Session-tracker cwd anchoring fix (filed as 18.B post-impl REPORT backlog item; separate hook-hygiene slice).

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- Moves files from `E:/GT-KB/<root>` → `E:/GT-KB/applications/Agent_Red/{docs,docs-site}/` (within-root operation).
- Cites `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 ACTIVE as the authorization for in-flight Agent Red root-file work during the migration window.
- Per `.claude/rules/project-root-boundary.md`.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping (Codex GO) | `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (2026-05-04) |
| Source DELIB | `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` |
| Authorizing GOV | `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1 |
| Authorizing DCL | `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1 |
| Active waiver | `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (S331) |
| Existing isolation registry | `applications/Agent_Red/.gtkb-app-isolation.json` |
| Pattern precedent | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED, OUTPUT_PATH in-place edit precedent) |
| Owner scope confirmations | This S331 conversation: 3 AskUserQuestion answers (platform exclusions, workflow edits, docs-site atomicity) |
| 2026-05-04 owner correction | `CLAUDE.md` "Agent Red Separate-Project Boundary" + S327 platform-vs-application terminology |
| Live probes | `git ls-files`, `git check-ignore`, `find`, `grep -rn`, `head` (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
