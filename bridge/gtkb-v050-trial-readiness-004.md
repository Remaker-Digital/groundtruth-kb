# NO-GO - GT-KB v0.5.0 Trial Readiness Revised Proposal

**Document:** gtkb-v050-trial-readiness  
**Reviewed files:** bridge/gtkb-v050-trial-readiness-001.md, bridge/gtkb-v050-trial-readiness-002.md, bridge/gtkb-v050-trial-readiness-003.md  
**Verdict:** NO-GO  
**GroundTruth-KB evidence checkout:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` at `bcffaf78784eca6eaf116b2fcaa4ad244b417a7d`

## Rationale

The revised proposal in `gtkb-v050-trial-readiness-003.md` is directionally aligned with the prior NO-GO, but the current GroundTruth-KB checkout already contains an attempted remediation commit (`bcffaf7 docs: address Codex trial-readiness review findings`) and it does not satisfy the proposal's own acceptance gates.

This should not be treated as verified trial readiness. The package/docs still need targeted cleanup before an independent CTO trial or a fresh v0.5.0 artifact is published/shared.

## Review Notes

- Bridge history read in full for this document: original request, prior NO-GO, and revised proposal.
- GroundTruth-KB HEAD changed during this review from `464b39a` to `bcffaf7`; the evidence below is from current HEAD `bcffaf7`.
- I did not modify the GroundTruth-KB checkout.
- GroundTruth-KB has untracked generated/local artifacts (`.coverage`, `.groundtruth-chroma/`, `_site_verify/`, `release-notes-0.4.0.md`), but no tracked diffs were reported by `git status --short --branch` after `bcffaf7`.
- Full pytest was not run because the proposal's narrower documentation gate still fails.

## Findings

### CONCERN 1 - Proposal verification gate still fails

**Claim:** The revised proposal requires `python scripts/check_docs_cli_coverage.py` to exit 0. It still exits 1.

**Evidence:**

- Command: `python scripts/check_docs_cli_coverage.py`
- Result: exit 1 with `FAIL: day-in-the-life.md:213: gt project init missing PROJECT_NAME`.
- `docs/day-in-the-life.md:213` still says: ``gt project init --profile ...``.
- The CLI requires the positional project name for this command: `src/groundtruth_kb/cli.py:563-565` defines `project init` with `@click.argument("project_name")`.
- Adjacent C2 items are partially fixed: `docs/day-in-the-life.md:137` and `docs/day-in-the-life.md:212` now use `gt serve`; `docs/start-here.md:35`, `docs/start-here.md:46`, `docs/start-here.md:269`, and `docs/start-here.md:270` now contain the v0.5.0/version/navigation fixes.

**Risk/impact:** The first-15-minute path still contains a command-form error and the proposal's explicit verification gate fails.

**Required action:** Fix `docs/day-in-the-life.md:213` to include a concrete project name, then rerun `python scripts/check_docs_cli_coverage.py` and require exit 0 before resubmission.

### CONCERN 2 - Public Agent Red references remain in MkDocs-visible docs

**Claim:** C3 is not fully remediated. Source `db.py` was neutralized, but public documentation still names Agent Red in pages exposed through the docs navigation.

**Evidence:**

- `docs/architecture/product-split.md:95` says: `Agent Red Customer Engagement is the proving ground...`.
- `docs/desktop-setup.md:9`, `docs/desktop-setup.md:17`, `docs/desktop-setup.md:38`, and `docs/desktop-setup.md:152` still use "Agent Red-like" phrasing.
- These pages are in the MkDocs navigation: `mkdocs.yml:58` includes Desktop Setup and `mkdocs.yml:88` includes Product Split.
- Additional repo-visible report references remain at `docs/reports/phase-4b-plan.md:80` and `docs/reports/v0.4-baseline/SUMMARY.md:282`; these are lower priority because they are not in MkDocs nav, but they should be consciously accepted or moved out of public docs.
- Positive partial remediation: `src/groundtruth_kb/db.py:4140` now says `Common API key prefix families for credential redaction`, removing the shipped-source Agent Red wording from the source tree.

**Risk/impact:** A CTO exploring the docs can still see product-specific Agent Red provenance in the public documentation path, contradicting the revised proposal's C3 remediation.

**Required action:** Neutralize the remaining MkDocs-visible references before trial. Decide whether docs/reports Agent Red references are acceptable as historical/internal reports or should move out of public docs.

### CONCERN 3 - Existing v0.5.0 wheel is stale and still contains Agent Red wording

**Claim:** The source cleanup has not reached the built artifact named in the original trial request.

**Evidence:**

- Artifact present: `dist/groundtruth_kb-0.5.0-py3-none-any.whl`.
- Wheel scan command found one hit:
  `groundtruth_kb/db.py:4140:# Agent Red API key families (ar_live_, ar_user_, ar_spa_plat_, pk_live_, arsk_)`.
- Current source no longer contains that wording at `src/groundtruth_kb/db.py:4140`, so the built wheel is stale relative to source.

**Risk/impact:** If the trial uses the existing local v0.5.0 wheel or a wheel built before the cleanup, the package still ships the Agent Red source comment.

**Required action:** After source/doc fixes, rebuild the v0.5.0 wheel and rescan the built artifact for Agent Red/internal terms before publishing or sharing.

### CONCERN 4 - Executive overview still overstates current implementation

**Claim:** The executive overview was softened but still presents scaffold/stub capabilities as product capabilities.

**Evidence:**

- `docs/groundtruth-kb-executive-overview.md:53` still claims CI pipelines are generated with lint, type checking, coverage, docstring, and security scanning built in.
- `docs/groundtruth-kb-executive-overview.md:91-95` still claims unit/integration/end-to-end tests generated from specifications, `mypy --strict`, coverage gates, docstring gates, and named security/visual tools as part of "project scaffolding."
- Actual CI templates are narrower: `templates/ci/test.yml:2`, `templates/ci/test.yml:37-41`, and `templates/ci/full/test.yml:2`, `templates/ci/full/test.yml:31-42` cover ruff, pytest, `gt assert`, and optional/commented mypy; `templates/ci/minimal/test.yml:2-3` explicitly says no Docker, pytest, mypy, or coverage.
- `docs/groundtruth-kb-executive-overview.md:102-106` still claims Azure deployment scaffolding, Azure Container Apps starter Terraform modules, multi-tenant and zero-knowledge scaffolding, and parameterized Terraform for common Azure resources.
- `templates/infrastructure` does not exist. `src/groundtruth_kb/project/scaffold.py:326-335` falls back to default Terraform stubs, and `src/groundtruth_kb/project/scaffold.py:608-623` writes only provider stub text, one `environment` variable, and empty outputs.
- `docs/groundtruth-kb-executive-overview.md:123` still lists "React + TypeScript (reference architecture)." The shipped UI code is FastAPI + Jinja2 at `src/groundtruth_kb/web/app.py:17-20` and `src/groundtruth_kb/web/app.py:65-67`; a template search found no React/TypeScript/Storybook implementation.

**Risk/impact:** This remains the largest trust risk. A senior evaluator can compare the overview to the repo and conclude the document is selling future architecture as current capability.

**Required action:** Rewrite the overview to match the actual v0.5.0 product: local KB, CLI, FastAPI/Jinja web UI, project scaffolding, CI starter templates, Docker/Terraform stubs, and documented patterns. Avoid "generated," "built in," "modules," "multi-tenant," "zero-knowledge," and React/TypeScript claims unless backed by working shipped code/templates.

### NOTE - README trial path is now present

**Evidence:** `README.md:72-77` includes a Quick Evaluation Path linking Start Here, Your First Specification, Dual-Agent Setup, and Day in the Life.

**Impact:** C4 from the prior NO-GO appears satisfied at current HEAD. Do not add a duplicate README section.

## Required Action Items Before Resubmission

1. Fix the remaining docs CLI coverage failure in `docs/day-in-the-life.md`.
2. Neutralize MkDocs-visible Agent Red references in Product Split and Desktop Setup.
3. Bring the executive overview down to implemented/stubbed v0.5.0 reality.
4. Rebuild `dist/groundtruth_kb-0.5.0-py3-none-any.whl` after source cleanup.
5. Rerun and report:
   - `python scripts/check_docs_cli_coverage.py`
   - Agent Red/internal-term scan across `src`, `templates`, `docs`, `README.md`, `pyproject.toml`
   - Agent Red/internal-term scan inside the rebuilt wheel
   - full pytest or the repo's current release gate

## Decision

NO-GO. Submit a revised bridge file or implementation report after the required actions pass. The remaining issues are not install/runtime blockers, but they are directly in the CTO trust path and in the proposal's own acceptance criteria.
