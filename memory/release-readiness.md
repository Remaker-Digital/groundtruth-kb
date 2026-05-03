# Release Readiness — v0.7.0-rc1 Path (S327 owner direction)

Last updated: 2026-05-02 (S327)

## Active Release Target: v0.7.0-rc1

**Owner directive 2026-05-02 (S327, end-of-session):** the next release opportunity is AFTER `GTKB-ISOLATION-017` closes. Goal: **complete clean-adopter productization**. Recorded as `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION`. Version choice `v0.7.0-rc1` (not `0.6.2` — too small a label for clean-adopter productization).

## ISOLATION-017 Status as of S327 close

| Slice | Description | Status |
|---|---|---|
| 1 | Doctor checks for isolation invariants | VERIFIED |
| 2 | Registry isolation | VERIFIED |
| 2.5 | Rationale/migration-note schema extension | VERIFIED |
| 3 | `gt project init` defaults + host-root binding | VERIFIED *(S327 commit `bdf154b3`)* |
| **4** | **`gt project upgrade` isolation + migration/rollback** | **NEXT** |
| 5 | Clean-adopter test suite + fixtures | After Slice 4 |
| 6 | Docs for application/product isolation + migration | Parallel after Slice 5 |
| 7 | Examples | Parallel after Slice 5 |
| 8 | Release-version gate + closeout | Final |

## Release-Hardening Blockers (address during Slice 8 closeout)

- **Dirty worktree** — RESOLVED 2026-05-02 S327 (commit `44ecb46f`); 5 commits landed; tree clean.
- **`ruff check .`** — red across full repo. Governance hardening verified ruff-clean only on touched files. Slice 8 scope: full-repo ruff resolution.
- **`pytest` full sweep** — timed out locally. Slice 8 scope: scope/parallelize slow lanes for CI feasibility.
- **Package version** — `groundtruth-kb/pyproject.toml` still produces `0.6.1`. Slice 8 scope: bump to `0.7.0-rc1`.
- **Release notes** — most recent at `release-notes-0.6.1.md`. Slice 8 scope: write `release-notes-0.7.0-rc1.md`.
- **Wheel/sdist + install smoke** — Slice 8 scope: verify `pip install groundtruth-kb==0.7.0rc1` produces a working `gt project init`.
- **Clean-adopter proof** — Slice 5's deliverable; Slice 8 verifies acceptance.
- **CI green** — Slice 8 scope: GitHub Actions full sweep + release-candidate-gate.yml workflow green.
- **Bridge terminal state** — Slice 8 scope: all ISOLATION-017 Slices VERIFIED; standing-Backlog/Primer/Disambiguation deferred status documented.

## Feature Freeze

Per S327 owner direction: NO new governance scope work until Slice 8 VERIFIED. The three governance programs landed in S327 (Backlog DB, Term Primer, Term Disambiguation) wait for the post-release window. Slice 1 deliverables are durable (committed at `5da729f8`) but Slices 2+ do not advance.

## ISOLATION-017-CLOSEOUT (S330)

Last updated: 2026-05-03 (S330)

Slice 8 disposition resolved per `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`: split into Slice 8 (release artifacts) + Slice 8.5 (CI-green capture). Authorizing bridge: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-005.md` (REVISED-2; Codex GO at `-006`).

### Blocker outcomes (Slice 8)

| Blocker | Outcome | Evidence |
|---|---|---|
| B1 — Version bump | DONE | `groundtruth-kb/src/groundtruth_kb/__init__.py` line 16 → `__version__ = "0.7.0rc1"`. Verified via `python -c "import groundtruth_kb; assert groundtruth_kb.__version__ == '0.7.0rc1'"`. |
| B2 — Ruff resolution | DONE (NARROWED) | `ruff check groundtruth-kb/` exits 0. Scope narrowed to `groundtruth-kb/` package per `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` (1,943 Agent Red product-code issues deferred to a separate Agent Red work item, not release-blocking for this rc). |
| B3 — Pytest feasibility | DONE (GREEN) | `python -m pytest groundtruth-kb/tests/ -q` runs to completion in ~620s; all tests PASS. 13 stale-baseline + behavioral failures fixed in this slice per `DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE`. Per-lane runtime breakdown documented in `release-notes-0.7.0-rc1.md`. |
| B4 — Release notes file | DONE | `groundtruth-kb/release-notes-0.7.0-rc1.md` (~170 LOC) authored mirroring `release-notes-0.6.1.md` structure. Cross-references Slice 8.5 follow-on. |
| B5 — Wheel/sdist install smoke | DONE | `scripts/_verify_slice8_closeout.py` `check_b5_wheel_smoke` runs full smoke: (a) `python -m build --wheel --sdist` from `groundtruth-kb/` produces `groundtruth_kb-0.7.0rc1-*.whl` + `groundtruth_kb-0.7.0rc1.tar.gz`; (b) `pip install` the wheel into a fresh tmp venv; (c) `gt --version` reports `0.7.0rc1`; (d) `gt project init SmokeApp --gt-kb-root <discovered_host_root> --dir <discovered_host_root>/applications/SmokeApp --profile local-only --no-include-ci --no-seed-example` succeeds; (e) scaffolded `groundtruth.toml` confirmed under target. The `--gt-kb-root` is discovered at runtime via `from groundtruth_kb.project.scaffold import _GT_KB_HOST_ROOT` per `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` — the original `-005` plan's `gt project init <tmp>/test-app --profile local-only` command shape did NOT work for installed wheels under Slice 4 isolation. Pip-install adopter UX simplification tracked at row 36 (`GTKB-PIP-INSTALL-ADOPTER-UX-001`); not blocking for this rc. |
| B6 — CI-green evidence | **DEFERRED to Slice 8.5** | Per `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE`. New bridge thread `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md` filed AFTER Slice 8 commit lands. Slice 8.5 captures GitHub Actions run URL + asserts final green status; gates `v0.7.0-rc1` tag authorization. |
| B7 — Bridge terminal state | DONE | All 8 ISOLATION-017 slice bridges VERIFIED: Slice 1 (doctor checks), Slice 2 (registry isolation), Slice 2.5 (rationale schema), Slice 3 (init defaults), Slice 4 (upgrade), Slice 5 (clean-adopter tests), Slice 6 (docs), Slice 7 (examples). This Slice 8 closes via the post-impl REPORT. Standing-Backlog DB / Term Primer / Term Disambiguation Slice 1s landed in S327; Slices 2-7 deferred per `Feature Freeze` block above (lifts at v0.7.0-rc1 tag). |

### Tag authorization gate

`git tag -a v0.7.0-rc1` does NOT authorize until BOTH:

1. Slice 8 (this thread) is VERIFIED + committed.
2. Slice 8.5 (`bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`) is VERIFIED.

Until both close, the rc has not been published; release-notes and announcement are author-ready but not authoritative.

### Owner sub-decisions archived (S330)

- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` — split into Slice 8 + Slice 8.5 per Codex F1 path 1.
- `DELIB-S330-ISOLATION-017-SLICE8-B2-RUFF-SCOPE-CHOICE` — narrowed B2 to `groundtruth-kb/` package only (1,943 Agent Red issues deferred).
- `DELIB-S330-ISOLATION-017-SLICE8-PYTEST-FIX-SCOPE-CHOICE` — added 13 pytest-baseline fixes to Slice 8 scope (within `-005` Risk 2 anticipated mitigation).

---

## Historical context: v0.6.x recovery

Original content below preserved as historical evidence for traceability.

Last updated: 2026-04-21 18:25 America/Los_Angeles

## Current State

Agent Red is in release-readiness recovery after a production-readiness inspection found P0/P1 blockers. The current repository head is `main@c372eef`, a release-evidence documentation commit. The latest full code candidate remains `main@e01e8ac` with green GitHub Actions evidence for Lint, Python Tests, Release Candidate Gate, SonarCloud, and Security Scan; `main@c372eef` also has green SonarCloud evidence and a fresh local non-deploying release-candidate gate pass.

- tracked generated production manifest with plaintext credentials,
- fail-open standalone admin behavior when deployed without an admin password,
- static fallback signing secrets reaching production if env vars are absent,
- commercial integration state durability and secure per-tenant restore have
  local implementation and non-deploying release-gate evidence.

## Completed Recovery Work

- Removed `scripts/deploy/production-gateway-generated.yaml` from the working tree.
- Ignored future generated production gateway YAML.
- Updated `scripts/deploy/restore-production-gateway.ps1` to write `_production-gateway-generated.local.yaml`.
- Added production startup guard in `src/app/lifecycle.py` requiring deployed environments to provide required admin, signing, public URL, and CORS settings.
- Hardened `src/app/standalone_auth.py` so staging/production do not allow passwordless admin access.
- Added `tests/security/test_production_config_guard.py`.
- Added `scripts/release_candidate_gate.py`.
- Added `.github/workflows/release-candidate-gate.yml`.
- Changed `.github/workflows/python-tests.yml` so full Python shards run on `develop` pushes.
- Changed `.github/workflows/security-scan.yml` so Semgrep scans outside `src/` and Docker Scout logs into ACR before building.
- Changed `.github/workflows/security-scan.yml` so Docker Scout uses scan-only ACR credentials and separate Docker Hub authentication secrets.
- Reduced the production Docker image vulnerability surface by removing the curl healthcheck dependency, upgrading Debian packages during build, and switching the healthcheck to Python stdlib.
- Added `pyOpenSSL>=26.0.0` to resolve dependency audit CVEs.
- Added Bandit config for the Cosmos-query B608 heuristic and verified Bandit medium/high gate passes.
- Added `.claude/skills/release-candidate-gate/SKILL.md` to make the non-deploying release gate an explicit local operator skill.
- Made `.claude` governance hooks, rules, and skills visible to git instead of leaving them hidden by the blanket `.claude/*` ignore.
- Added `GTKB-GOV-001`, `GTKB-GOV-002`, and `GTKB-GOV-003` to the top of `memory/work_list.md` for pending Tier A apply completion, release-gate skill upstreaming, and governance-adoption doctor work.
- Enabled the upstream GT-KB managed skills `gtkb-decision-capture`, `gtkb-bridge-propose`, and `gtkb-spec-intake` with their helper scripts.
- Added `.claude/rules/acting-prime-builder.md` so GT-KB Prime Builder skill labels map explicitly to Codex while the owner-directed acting-Prime exception is active.

## Regression Coverage

Observable regression coverage now includes:

- `tests/security/test_production_config_guard.py` for deployed startup config fail-closed behavior.
- `tests/scripts/test_release_candidate_gate.py` for release-gate manifest containment and Python-version checks.
- `scripts/release_candidate_gate.py` for local and CI release-candidate checks.
- `.github/workflows/release-candidate-gate.yml` for Python 3.12 security/config checks plus Windows frontend builds and widget tests.
- `.github/workflows/python-tests.yml` on `develop` pushes for full shard/coverage signal.
- `tests/scripts/test_groundtruth_governance_adoption.py` for GroundTruth adopter config, KnowledgeDB gate plugin config, governance hook/rule/skill presence, gitignore visibility, release workflow lanes, and work-queue ordering.
- The governance adoption test now also requires the three upstream GT-KB managed skills and the local acting-Prime role mapping rule.
- `python scripts\release_candidate_gate.py --skip-frontend` passed locally under Python 3.14 with Ruff E/F, import cycles, Bandit, pip-audit, and 147 targeted tests.
- `python scripts\release_candidate_gate.py` passed locally under Python 3.14 with secret manifest containment, Ruff E/F, import cycles, Bandit, pip-audit, Codex hook parity, and 186 targeted tests.
- `tests/test_host/test_build_contract.py::TestConfigurationDriftAcrossLayers::test_production_dockerfile_avoids_curl_healthcheck_dependency` verifies the production Dockerfile does not depend on curl for healthchecks.

## 2026-04-20 Risk Register Remediation Pass

Claim: Production GO remains blocked. The risk-register remediation target is not
to claim release readiness prematurely; it is to close, explicitly defer, or
supersede every blocker with governed evidence.

Historical evidence from that pass:

- Local branch was `main` at `869f867a` after the SonarCloud trigger, dependency, and organization-key fixes.
- The last green code candidate at that point was `main@869f867a`.
- Remote branch divergence: `origin/main...origin/develop` reports 23 commits
  unique to `main` and 0 commits unique to `develop`; `develop` no longer has
  unreconciled release-candidate commits ahead of `main`, but the branch-policy
  decision for future release provenance still needs owner/project disposition.
- Generated manifest containment: `scripts/deploy/production-gateway-generated.yaml`
  does not exist in the working tree, remains tracked, and is staged as a
  pending deletion in local git status.
- Generated local restore output is ignored by
  `.gitignore` via `scripts/deploy/_production-gateway-generated*.yaml`.
- Correct GitHub project confirmed by owner:
  `Remaker-Digital/agent-red-customer-engagement`.
- Local `.env.local` now identifies `AGENT_RED_GITHUB_REPO` as
  `Remaker-Digital/agent-red-customer-engagement` and
  `GROUND_TRUTH_GITHUB_REPO` as `Remaker-Digital/groundtruth-kb`.
- The local git remote and dashboard GitHub Actions links must remain aligned
  to `Remaker-Digital/agent-red-customer-engagement`.
- Correct-project repository secrets visible through
  `gh secret list --repo Remaker-Digital/agent-red-customer-engagement` include
  `SONAR_TOKEN`, last updated 2026-04-10T03:57:11Z, plus scan-only
  `ACR_SCOUT_USERNAME` and `ACR_SCOUT_PASSWORD`, last updated 2026-04-21.
  Docker Hub credentials for the Docker Scout GitHub Action are not currently
  configured.
- Correct-project workflow inventory now includes active `SonarCloud` and
  `Security Scan` workflows in
  `Remaker-Digital/agent-red-customer-engagement`.
- GitHub Actions evidence for the current candidate `main@869f867a` is green
  for Release Candidate Gate, Python Tests, Lint, and SonarCloud. Release
  Candidate Gate included the Python 3.12 release gate and Windows
  frontend/widget gate. The runs were created 2026-04-21T13:59:04Z and
  completed by 2026-04-21T14:07:58Z.
- Security Scan on `main@869f867a` failed in the Docker Scout job before image
  scanning because `ACR_USERNAME` was not configured as a repository secret.
  Semgrep SAST, Bandit, and pip-audit jobs passed in the same run. The
  workflow has since been changed to use scan-only `ACR_SCOUT_USERNAME` and
  `ACR_SCOUT_PASSWORD` secrets for Docker Scout ACR login.
- Docker Scout is connected to `acragentredeastus.azurecr.io` through the
  Docker Scout Azure Container Registry integration using an Azure-created
  read-only registry token.
- Security Scan on `main@e3a4000b` advanced past scan-only secret validation,
  ACR login, and local image build, then failed in `docker/scout-action@v1`
  with `no credential found for "https://index.docker.io/v1/"`. The workflow
  now requires separate Docker Scout Hub credentials before running Scout:
  `DOCKER_SCOUT_HUB_USER` and `DOCKER_SCOUT_HUB_PAT`.
- SonarCloud release evidence is now cleared for the exact candidate:
  `.github/workflows/sonarcloud.yml` runs on `main` and manual dispatch,
  filters the known native dependency from CI install, validates
  `SONAR_TOKEN`, and uses the discoverable Sonar organization key
  `mike-remakerdigital`.
- Prior SonarCloud and Security Scan failures harvested from any
  non-authoritative repository are no longer release evidence for Agent Red.
- Local non-deploying release candidate gate passed after the wrapped-blocker
  parser fix: `python scripts/release_candidate_gate.py --skip-frontend`
  completed Ruff E/F, import-cycle detection, Bandit, pip-audit, Codex hook
  parity, and 183 targeted tests.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest is
  owner-managed outside Codex scope. Codex must not ask Mike to rotate keys; when
  credentials change, Mike will update `env.local`, and Codex may consume,
  validate, or upload those values only when the task requires it and Mike has
  authorized that use.
- Owner must decide whether git history requires secret purging: still
  owner-gated. Do not close without an explicit owner decision.
- GitHub SonarCloud must pass with valid `SONAR_TOKEN` and project
  configuration: cleared for `main@869f867a`.
- GitHub Security Scan must pass with valid Docker Scout credentials: was still
  blocked in this pass. `ACR_SCOUT_USERNAME` and `ACR_SCOUT_PASSWORD` were configured, but
  `docker/scout-action@v1` also required Docker Hub authentication through
  `DOCKER_SCOUT_HUB_USER` and `DOCKER_SCOUT_HUB_PAT`. This blocker was later
  cleared in the 2026-04-21 Docker Scout clearance pass below.
- `main` and `develop` release provenance: operational divergence is cleared
  for the current candidate (`develop` is 0 commits ahead of `main`), but the
  release-branch policy still needs owner/project disposition.
- Full Python 3.12 CI on the current candidate commit: cleared for
  `main@869f867a` by green Release Candidate Gate and Python Tests runs.
- Commercial durability launch scope must be decided for
  Shopify/Stripe/action-executor in-memory paths: still owner/product-scope
  gated.

Recommended next actions:

- Prime Builder: do not request credential rotation. Treat credential lifecycle
  as owner-managed outside Codex scope; when Mike updates `env.local`, consume,
  validate, or upload the updated values only when the task requires it and Mike
  has authorized that use.
- Owner: decide whether repository history must be purged for the exposed
  manifest.
- Prime Builder: keep local remote, dashboard GitHub Actions evidence, and
  generated startup reports aligned to
  `Remaker-Digital/agent-red-customer-engagement`.
- Repo admin: configure valid `DOCKER_SCOUT_HUB_USER` and
  `DOCKER_SCOUT_HUB_PAT` repository secrets for Docker Scout Hub
  authentication, then rerun Security Scan on the exact candidate. Completed
  in the 2026-04-21 Docker Scout clearance pass below.
- Owner/project: decide the release-branch policy now that `develop` has no
  commits ahead of `main` and `main` is 23 commits ahead of `develop`.

## 2026-04-21 Docker Scout Clearance Pass

Claim: The GitHub Security Scan release blocker is cleared for the latest full code candidate.

Current evidence:

- Latest full code candidate: `main@e01e8ac154675ca29a80a4cdfd0a9056dd00307c`.
- GitHub Actions on `main@e01e8ac` are green for Lint, Python Tests, Release Candidate Gate, SonarCloud, and Security Scan.
- Security Scan run `24731909565` completed successfully on `main@e01e8ac` after Docker Scout ACR and Docker Hub credentials were configured.
- Docker Scout ACR credentials are present as repository secrets `ACR_SCOUT_USERNAME` and `ACR_SCOUT_PASSWORD`.
- Docker Hub credentials are present as repository secrets `DOCKER_SCOUT_HUB_USER` and `DOCKER_SCOUT_HUB_PAT`.
- Security Scan run `24731386383` previously proved Docker Scout authentication was working but failed on high CVEs in Debian packages pulled into the production image.
- Commit `e01e8ac` removed the curl healthcheck dependency, upgraded Debian packages during image build, and switched the production healthcheck to Python stdlib.
- Local targeted regression passed: `python -m pytest tests\test_host\test_build_contract.py::TestConfigurationDriftAcrossLayers::test_production_dockerfile_avoids_curl_healthcheck_dependency tests\multi_tenant\test_s175_scaling_680.py::TestUvicornWorkers::test_dockerfile_has_four_workers tests\multi_tenant\test_s175_scaling_680.py::TestLifecycleIntegration::test_dockerfile_has_tini_entrypoint -q --tb=short`.
- Local governance regression passed: `python -m pytest tests\scripts\test_groundtruth_governance_adoption.py -q --tb=short`.
- Standing backlog harvest regression passed: `python -m pytest tests\scripts\test_standing_backlog_harvest.py -q --tb=short`.
- Standing backlog source audit now reports only owner/project-gated release blockers after the Security Scan blocker is removed from this record.

Blocker disposition:

- GitHub Security Scan must pass with valid Docker Scout credentials: cleared for `main@e01e8ac` by run `24731909565`.
- Credential lifecycle for values exposed in the deleted generated manifest is owner-managed outside Codex scope. Codex must not ask Mike to rotate keys; when credentials change, Mike will update `env.local`, and Codex may consume, validate, or upload those values only when the task requires it and Mike has authorized that use.
- Owner must decide whether git history requires secret purging: still owner-gated. Do not close without an explicit owner decision.
- `main` and `develop` release provenance: operational divergence is cleared for the current candidate, but the release-branch policy still needs owner/project disposition.
- Commercial integration state for Shopify, Stripe, and action-executor paths
  must be durably persisted per tenancy and recoverable from a durable, secure
  tenant backup.

## 2026-04-21 GTKB-GOV-006 Evidence Freshness Pass

Claim: The release-readiness blocker list is current as of `main@c372eef`; production GO remains blocked only by owner/project decisions.

Current evidence:

- Current repository head: `main@c372eef04f854b6216afc16ca88eae9485b34ccc`.
- Commit `c372eef` modifies only `memory/release-readiness.md` relative to its parent and records green Security Scan evidence.
- GitHub Actions on `main@c372eef` show SonarCloud run `24732405946` completed successfully.
- GitHub Actions on `main@e01e8ac` show Lint run `24731899661`, Python Tests run `24731899611`, Release Candidate Gate run `24731899768`, SonarCloud run `24731899451`, and Security Scan run `24731909565` completed successfully.
- Branch divergence from `git rev-list --left-right --count origin/main...origin/develop` is `29 0`: `origin/main` is 29 commits ahead of `origin/develop`; `origin/develop` has no commits ahead of `origin/main`.
- Standing backlog source audit reports four remaining release blockers, matching the list below.
- Local non-deploying release-candidate gate passed on the checked-out tree: `python scripts/release_candidate_gate.py --skip-frontend`. The gate completed secret manifest containment, Ruff E/F, import-cycle detection, Bandit, pip-audit, Codex hook parity, and 185 targeted tests.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest remains owner-managed outside Codex scope. Codex must not ask Mike to rotate keys.
- Secret-history purge remains owner-gated. Do not close without an explicit owner decision.
- Release-branch provenance policy remains owner/project-gated. Operational divergence is known and bounded (`develop` is 0 commits ahead of `main`), but the durable policy decision is still open.
- Commercial durability launch scope remains owner/product-scope gated for Shopify/Stripe/action-executor in-memory paths.

## 2026-04-21 Option 3 Release Blocker Verification Pass

Claim: The selected release-blocker focus did not uncover a current technical gate failure; production GO remains blocked by the four governed owner/project disposition items below.

Current evidence:

- Checked-out branch: `main`.
- Current repository head: `main@c372eef04f854b6216afc16ca88eae9485b34ccc`.
- Branch divergence from `git rev-list --left-right --count origin/main...origin/develop` remains `29 0`: `origin/main` is 29 commits ahead of `origin/develop`; `origin/develop` has no commits ahead of `origin/main`.
- Local non-deploying release-candidate gate passed on the checked-out tree: `python scripts/release_candidate_gate.py`. The gate completed secret manifest containment, Ruff E/F, import-cycle detection, Bandit medium/high scan, pip-audit, Codex hook parity, and 185 targeted tests.
- Standing backlog source audit passed and reports exactly four release blockers, matching the remaining blocker list below: `python scripts/audit_standing_backlog_sources.py`.
- GitHub Actions evidence from `gh run list --repo Remaker-Digital/agent-red-customer-engagement --branch main --limit 10` shows the latest `main` runs still green for SonarCloud on `main@c372eef`, plus Security Scan, Lint, Release Candidate Gate, Python Tests, and SonarCloud on the latest full code candidate `main@e01e8ac`.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest remains owner-managed outside Codex scope. Codex must not ask Mike to rotate keys.
- Secret-history purge remains owner-gated. Do not close without an explicit owner decision.
- Release-branch provenance policy remains owner/project-gated. Operational divergence is known and bounded (`develop` is 0 commits ahead of `main`), but the durable policy decision is still open.
- Commercial durability launch scope remains owner/product-scope gated for Shopify/Stripe/action-executor in-memory paths.

## 2026-04-21 Resolve Release Blockers Freshness Pass

Claim: The requested release-blocker resolution pass found no remaining local
technical gate failure. The remaining blockers are now limited to the governed
owner/project disposition items below.

Current evidence:

- Checked-out branch: `main`.
- Current repository head: `main@c372eef04f854b6216afc16ca88eae9485b34ccc`.
- Branch divergence from `git rev-list --left-right --count origin/main...origin/develop` remains `29 0`: `origin/main` is 29 commits ahead of `origin/develop`; `origin/develop` has no commits ahead of `origin/main`.
- GitHub Actions evidence from `gh run list --repo Remaker-Digital/agent-red-customer-engagement --branch main --limit 15` remains green for SonarCloud on `main@c372eef`, plus Security Scan, Lint, Release Candidate Gate, Python Tests, and SonarCloud on latest full code candidate `main@e01e8ac`.
- Local release gate passed: `python scripts/release_candidate_gate.py`. The gate completed secret manifest containment, Ruff E/F, import-cycle detection, Bandit medium/high scan, pip-audit, Codex hook parity, and 186 targeted tests.
- Standing backlog source audit passed: `python scripts/audit_standing_backlog_sources.py`. It reports four release blockers, matching the remaining blocker list below.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest remains owner-managed outside Codex scope. Codex must not ask Mike to rotate keys.
- Secret-history purge remains owner-gated. Do not close without an explicit owner decision.
- Release-branch provenance policy remains owner/project-gated. Operational divergence is known and bounded (`develop` is 0 commits ahead of `main`), but the durable policy decision is still open.
- Commercial durability launch scope remains owner/product-scope gated for Shopify/Stripe/action-executor in-memory paths.

## Remaining Release Blockers

None as of the 2026-04-21 commercial durability implementation pass.

## 2026-04-21 Owner Credential Lifecycle Disposition

Claim: The credential lifecycle blocker is closed by owner disposition.

Evidence:

- Owner replied `Close` to the credential lifecycle disposition question.
- The standing directive remains unchanged: credential lifecycle is
  owner-managed outside Codex scope, and Codex must not ask Mike to rotate keys.

Blocker disposition:

- Credential lifecycle for values exposed in the deleted generated manifest:
  closed by owner disposition.
- Active release blocker list now contains three remaining owner/project
  disposition items: secret-history purge, release-branch provenance policy, and
  commercial durability launch scope.

## 2026-04-21 Owner Secret-History Purge Disposition

Claim: The secret-history purge blocker is closed by owner disposition.

Evidence:

- Owner replied `Close` to the secret-history purge disposition question.

Blocker disposition:

- Git history purge for the exposed generated manifest: closed by owner
  disposition.
- Active release blocker list now contains two remaining owner/project
  disposition items: release-branch provenance policy and commercial durability
  launch scope.

## 2026-04-21 Owner Release-Branch Provenance Disposition

Claim: The release-branch provenance blocker is closed by owner disposition.

Evidence:

- Owner replied `Close` to the release-branch provenance policy disposition
  question.
- Current recorded branch evidence remains `origin/main...origin/develop` at
  `29 0`: `origin/develop` has no commits ahead of `origin/main`.

Blocker disposition:

- Release-branch provenance policy for `main`/`develop`: closed by owner
  disposition.
- Active release blocker list now contains one remaining owner/product-scope
  disposition item: commercial durability launch scope.

## 2026-04-21 Owner Commercial Durability Scope Decision

Claim: Commercial durability is in launch scope and remains release-blocking
until implemented and verified.

Evidence:

- Owner stated that integration state for each tenancy must be durable.
- Owner stated that it must be possible to fully restore the configuration of a
  tenancy from a durable, secure backup.

Blocker disposition:

- The commercial durability launch-scope question is resolved: Shopify,
  Stripe, and action-executor commercial integration state durability is in
  scope.
- The active release blocker is now implementation and verification of durable
  per-tenant state plus secure restore, not an owner-decision question.

## 2026-04-21 Commercial Durability Implementation Pass

Claim: The commercial durability release blocker is cleared by local
implementation and non-deploying release-gate evidence.

Evidence:

- Added Cosmos schema containers for durable commercial runtime state and
  encrypted commercial-state backups: `commercial_state` and
  `commercial_state_backups`.
- Added `src/integrations/commercial_state_store.py` with Cosmos-backed
  staging/production persistence, explicit local/test in-memory storage, and
  encrypted tenant backup/restore operations.
- Rewired the integration framework admin API sync state, event logs, and HITL
  configuration through the commercial state store.
- Rewired `ActionExecutor` pending actions, HITL overrides, and audit entries
  through the commercial state store so pending approval state survives executor
  recreation.
- Rewired Stripe usage counters, Stripe pack balances, Shopify subscription
  state, and Stripe webhook reset/pack-credit flows through the commercial state
  store.
- Added release-gate regression coverage for commercial state backup/restore,
  integration schema, action executor persistence, admin integration framework
  state, Stripe consumption, Shopify billing, and Stripe webhooks.
- Local focused regression passed: `python -m pytest
  tests/integrations/test_action_executor.py
  tests/integrations/test_admin_integration_framework_api.py
  tests/integrations/test_usage_consumption.py
  tests/integrations/test_shopify_billing.py
  tests/unit/test_shopify_billing.py tests/unit/test_stripe_webhooks.py
  tests/integrations/test_commercial_state_store.py
  tests/integrations/test_cosmos_schema_extensions.py
  tests/scripts/test_standing_backlog_harvest.py -q --tb=short`.
- Local non-deploying release gate passed with frontend skipped: `python
  scripts/release_candidate_gate.py --skip-frontend`. The gate completed secret
  manifest containment, Ruff E/F, import-cycle detection, Bandit medium/high,
  pip-audit, Codex hook parity, and 362 targeted tests.

Blocker disposition:

- Commercial integration state durability and secure tenant restore: cleared by
  implementation and local release-gate evidence.
- Active release blocker list is empty as of this pass.

## Governance Notes

- Relevant prior deliberations searched and cited in the 2026-04-19 insight report: `DELIB-0560`, `DELIB-0565`, `DELIB-0602`, `DELIB-0603`.
- Current KnowledgeDB records: `DOC-release-readiness-recovery` v2 and `DOC-groundtruth-governance-adoption-2026-04-19` v1.
- Current Deliberation Archive record: `DELIB-0829` v1 for the owner governance-adoption directive and implementation evidence.
- Current role-governance decision: `DELIB-0830` v1 records the owner directive that Loyal Opposition/Codex assumes the acting Prime Builder role while canonical Prime Builder is unavailable.
- Current role-portability principle: any capable AI harness may assume Prime Builder or Loyal Opposition when assigned by the owner; the assigned harness must enable that role's skills, plugins, hooks, directives, and responsibilities to the extent possible, and when the bridge is available the counterpart is always Loyal Opposition.
- Current GT-KB installation principle: when GT-KB is installed, the project must be fully configured for Prime Builder; if multiple capable harnesses are installed, configuration should be prepared for all of them so the owner can assign Prime Builder and the non-Prime bridge participant assumes Loyal Opposition.
- Owner approval to continue and modify all necessary files was received in-session.
- This topic should be updated again after GitHub CI, owner-managed credential-state changes, and branch reconciliation are complete.
- The release-candidate gate now treats governance adoption as part of production readiness, not a separate manual checklist.
