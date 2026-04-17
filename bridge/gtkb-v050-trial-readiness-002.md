# NO-GO - GT-KB v0.5.0 Trial Readiness Review

**Document:** gtkb-v050-trial-readiness  
**Reviewed file:** bridge/gtkb-v050-trial-readiness-001.md  
**Verdict:** NO-GO for independent CTO trial as-is  
**Scope:** groundtruth-kb at `3fa26d7ca4a1f8abf4e428dca09bdc077ae2e0b0`

## Readiness Bottom Line

No install/init/doctor/spec-creation blocker was found. Both editable install and the built
`dist/groundtruth_kb-0.5.0-py3-none-any.whl` successfully installed in isolated Windows venvs,
`gt project init --profile dual-agent --no-seed-example` succeeded, `gt project doctor` exited 0
with expected WARNs, and the first-spec Python snippet inserted `SPEC-100`.

The product is still not ready for an independent senior-technologist trial without owner
mitigation. The primary risk is not runtime failure; it is trust loss from public-facing docs that
overstate current capabilities, stale version text, broken/incorrect command references, and
remaining Agent Red provenance in shipped/source-visible surfaces.

Required before an unsupervised trial:

1. Rewrite the executive overview to distinguish working features from scaffolding/stubs.
2. Fix Start Here / Day in the Life docs drift (`0.5.0`, `gt serve`, valid `gt project init` forms).
3. Remove or neutralize remaining Agent Red references from shipped package source and primary docs.
4. Put README on the trial path: Start Here -> First Spec -> Dual-Agent Setup.

## Findings

### CONCERN 1 - Executive overview overpromises current cloud, security, CI, and frontend capability

**Claim:** `docs/groundtruth-kb-executive-overview.md` does not accurately represent what GT-KB can
do today. It reads like production-grade SaaS/cloud support exists, while the repository mostly
ships local scaffolds, comments, and stubs.

**Evidence:**

- `docs/groundtruth-kb-executive-overview.md:102-111` claims production-grade cloud deployment
  scaffolding, Azure Container Apps auto-scaling/zero-downtime deployment, multi-tenant data
  isolation, zero-knowledge security patterns, and Terraform modules for resource groups,
  registries, databases, key vaults, caches, and ingress.
- `src/groundtruth_kb/project/scaffold.py:326-335` only creates `infrastructure/terraform` when a
  cloud provider is selected, then falls back to `_write_default_terraform` if packaged templates
  are absent. `templates/infrastructure` does not exist in this checkout.
- `src/groundtruth_kb/project/scaffold.py:608-623` writes Terraform stub files only:
  provider block, one `environment` variable, and empty outputs.
- `rg -n -i "tenant|multi-tenant|zero-knowledge|key isolation|encryption at rest|tenant-scoped"`
  found the claimed multi-tenant/zero-knowledge wording only in the executive overview, plus generic
  env/example references. It did not find implementation support for tenant-scoped isolation or
  tenant key management.
- `docs/groundtruth-kb-executive-overview.md:125-126` claims Azure/Cosmos/Key Vault and
  React/TypeScript/Storybook. The actual packaged web UI is FastAPI + Jinja:
  `src/groundtruth_kb/web/app.py:17-20`, and `rg -n "React|TypeScript|Storybook"` found only the
  executive-overview claim.
- `docs/groundtruth-kb-executive-overview.md:89-99` lists comprehensive testing/instrumentation
  including Semgrep, Bandit, pip-audit, Docker Scout, axe-core, Playwright, and Chromatic. The
  generated full profile test CI template runs ruff, pytest, and `gt assert`, with mypy commented
  out: `templates/ci/full/test.yml:31-42`. The deploy template contains commented Azure example
  placeholders, not an implemented deployment: `templates/ci/full/deploy.yml:41-54`.

**Risk/impact:** A CTO will likely spot the gap between claims and repo contents. This can undermine
confidence more than an honest "developer preview with working local scaffold and cloud stubs" would.

**Required action:** Rewrite the executive overview before sharing it externally. Use language such as
"generates Docker/CI/Terraform starter stubs" and explicitly say multi-tenant, zero-knowledge,
production deployment, React/Storybook, visual regression, and accessibility automation are not
implemented product capabilities in v0.5.0 unless/until code exists.

### CONCERN 2 - Trial documentation path has stale version and command drift

**Claim:** The adopter docs are close, but the exact first-15-minutes path still contains drift that
can confuse a non-hands-on CTO.

**Evidence:**

- `docs/start-here.md:33-47` tells users to pin `groundtruth-kb==0.4.0` and expects
  `gt, version 0.4.0`, while `src/groundtruth_kb/__init__.py:16`, wheel metadata, and smoke tests
  show `0.5.0`.
- `python scripts/check_docs_cli_coverage.py` failed with:
  - `FAIL: day-in-the-life.md:213: gt project init missing PROJECT_NAME`
  - `FAIL: docs/start-here.md: expected gt --version output 'gt, version 0.5.0' not found`
- `docs/day-in-the-life.md:137` and `docs/day-in-the-life.md:212` use `gt web`, but the CLI command
  is `gt serve`: `src/groundtruth_kb/cli.py:521-526`. Command check
  `python -m groundtruth_kb web` returned `Error: No such command 'web'.`
- `docs/day-in-the-life.md:213` lists `gt project init --profile ...` without the required
  `PROJECT_NAME` argument.
- `docs/start-here.md:267-275` does not link to `docs/tutorials/first-spec.md` or
  `docs/tutorials/dual-agent-setup.md`; it sends readers to Method Guide, Example Project, CLI
  Reference, and Configuration Reference. The requested path "Start Here -> First Spec -> Dual-Agent
  Setup" is therefore not navigable directly from Start Here.

**Risk/impact:** These are not runtime blockers, but they are exactly the kind of polish errors that
make a senior evaluator doubt whether the package and docs match.

**Required action:** Update Start Here to v0.5.0, add an explicit "Next: Your First Specification"
link followed by "Then: Dual-Agent Setup", replace `gt web` with `gt serve`, and make every
`gt project init` snippet include `PROJECT_NAME`.

### CONCERN 3 - Agent Red references remain in shipped source and public docs

**Claim:** The main runtime/package is mostly decontaminated, but there is still at least one Agent
Red reference in the built wheel and multiple public-repo references that weaken standalone product
positioning.

**Evidence:**

- Wheel scan of `dist/groundtruth_kb-0.5.0-py3-none-any.whl` found:
  `MATCH groundtruth_kb/db.py`, line 4140:
  `# Agent Red API key families (ar_live_, ar_user_, ar_spa_plat_, pk_live_, arsk_)`.
- Source location: `src/groundtruth_kb/db.py:4140-4146`.
- `docs/architecture/product-split.md:93-101` says Agent Red Customer Engagement is the proving
  ground for the patterns GT-KB packages.
- `docs/desktop-setup.md:7-17` and `docs/desktop-setup.md:152-158` refer to an "Agent Red-like"
  architecture/tooling path.
- Broader `rg -n -i "Agent Red|agentred|orange-glacier|acragentredeastus|cosmos-agentred|Customer Engagement|Claude-Playground"`
  found no remaining runtime infrastructure names such as `orange-glacier`, `acragentredeastus`, or
  `cosmos-agentred` in `src`, `templates`, `docs`, `README.md`, or `pyproject.toml`.

**Risk/impact:** The shipped source comment is visible in the installed package and will look
product-specific. The docs may also contradict the desired neutral positioning if the CTO explores
architecture docs or desktop setup independently.

**Required action:** Remove or generalize the `db.py` comment before publishing. For public docs,
either reword to neutral "reference implementation" language or move internal provenance/history
notes out of the public trial path.

### CONCERN 4 - README explains the product but does not route the trial user to the curated path

**Claim:** README.md is professional enough in its opening, but it does not optimize for the CTO trial
path described in the request.

**Evidence:**

- `README.md:11-15` gives a concise first-30-second explanation: a specification-driven governance
  toolkit for AI engineering teams with append-only traceability.
- `README.md:72-74` and `README.md:118-125` route new users to User Journey, `docs/bootstrap.md`,
  and Desktop Setup. `rg -n "start-here|first-spec|dual-agent-setup" README.md` found no Start Here,
  First Spec, or Dual-Agent Setup links.

**Risk/impact:** A first-time evaluator may choose the older/less curated bootstrap path and miss the
trial-specific docs Prime intended.

**Required action:** Add a short "15-minute evaluation path" near the top:
`docs/start-here.md` -> `docs/tutorials/first-spec.md` -> `docs/tutorials/dual-agent-setup.md` ->
`docs/day-in-the-life.md` / executive overview.

### NOTE 1 - Install-to-first-spec smoke passed

**Evidence:**

- Checkout verification: `git rev-parse HEAD` returned
  `3fa26d7ca4a1f8abf4e428dca09bdc077ae2e0b0`.
- Editable smoke in isolated venv:
  - `python --version`: `Python 3.14.0`
  - `pip install -e .`: success
  - `gt --version`: `gt, version 0.5.0`
  - `gt project init trial-smoke --dir <temp> --profile dual-agent --no-seed-example`: success
  - `gt project doctor`: exit 0, overall WARN only
  - first-spec `KnowledgeDB.insert_spec(...)` snippet: success
  - `gt summary`: `Specifications: 6 total`, including one new `specified` spec.
- Wheel smoke in isolated venv:
  - `pip install dist/groundtruth_kb-0.5.0-py3-none-any.whl`: success
  - `gt project init ... --profile dual-agent --no-seed-example`: success
  - `gt project doctor`: exit 0, overall WARN only.
- Doctor WARNs observed: `ruff not found`, `claude bridge poller not started`, and
  `codex bridge poller not started`. These are explainable setup warnings, not first-run failures.

**Risk/impact:** No BLOCKER found for `pip install` -> `gt project init` -> `gt project doctor` ->
first spec creation on this Windows host. I could not test Python 3.11 specifically because this host
has Python 3.14 and 3.13 only (`py -0p`).

**Recommended action:** Tell the CTO that doctor WARNs about pollers are expected before scheduler
setup. Consider documenting expected pre-demo WARNs in Start Here or Dual-Agent Setup.

### NOTE 2 - Package metadata and dependencies are reasonable

**Evidence:**

- Base dependency is only `click>=8.1`: `pyproject.toml:26-28`; wheel metadata also shows
  `Requires-Dist: click>=8.1`.
- Optional extras are segmented: `web` (`fastapi`, `uvicorn[standard]`, `jinja2`), `bridge` (`mcp`),
  `search` (`chromadb`), `dev`, and `docs`: `pyproject.toml:30-52`.
- Metadata has professional URLs/classifiers and honest alpha status:
  `pyproject.toml:5-24`; wheel metadata reports version `0.5.0`.

**Risk/impact:** No dependency bloat or obvious security concern in the base install. Optional
`chromadb` is heavier, but it is not pulled by default.

**Recommended action:** No pre-trial package metadata change required, unless "Development Status ::
3 - Alpha" conflicts with sales positioning. It is technically honest.

### NOTE 3 - Token idle-cost claim is architecturally supportable; "few dollars" is not proven here

**Evidence:**

- `docs/tutorials/bridge-os-scheduler.md:18-23` says pollers parse `bridge/INDEX.md` and dispatch the
  agent only when actionable entries exist.
- `templates/bridge-os-poller-setup-prompt.md:44-48` requires the generated poller to skip dispatch
  when no actionable work exists and log both clear scans and dispatched runs.
- `templates/rules/bridge-poller-canonical.md:17-36` defines latest-status filtering for actionable
  work; `templates/rules/bridge-poller-canonical.md:71-74` requires "scan clear" output when nothing
  required action.

**Risk/impact:** The statement "idle time costs zero tokens" is supported if the OS poller is
implemented from the shipped prompt/rules. The statement "a typical day uses a few dollars, not
hundreds" depends on provider pricing, model choice, workload, and agent behavior; this review did
not find measured usage evidence in the repo.

**Recommended action:** Reword cost guidance to: "Idle bridge scans are local and do not invoke AI.
Active token cost depends on provider/model/workload; in our observed usage, review cycles are
bounded by actionable bridge entries." Bring concrete usage examples to the demo.

## Commands Run

- `git rev-parse HEAD`; `git status --short --branch`
- `python -m zipfile -l dist/groundtruth_kb-0.5.0-py3-none-any.whl`
- Wheel content scan for Agent Red/internal strings
- `rg -n -i "Agent Red|agentred|orange-glacier|acragentredeastus|cosmos-agentred|Customer Engagement|Claude-Playground" src templates docs README.md pyproject.toml`
- Isolated editable smoke: `pip install -e .`, `gt --version`, `gt project init ... --profile dual-agent --no-seed-example`, `gt project doctor`, first-spec Python snippet, `gt summary`
- Isolated wheel smoke: `pip install dist/groundtruth_kb-0.5.0-py3-none-any.whl`, `gt --version`, `gt project init ...`, `gt project doctor`
- `python scripts/check_docs_cli_coverage.py` (failed with two documentation issues)
- `python -m groundtruth_kb web` (failed: no such command)
- `py -0p`

## Decision Needed From Owner

Decide whether tomorrow's trial is owner-guided or independent:

- If owner-guided: proceed only after preparing explicit talking points for the executive-overview
  overclaims, expected doctor WARNs, manual bridge scheduler setup, and token-cost boundaries.
- If independent: do not send v0.5.0 as-is. Make the required docs/source cleanup first, then rerun
  the docs drift check and smoke path.
