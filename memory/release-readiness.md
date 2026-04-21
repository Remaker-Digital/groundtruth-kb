# Release Readiness Recovery

Last updated: 2026-04-21 00:23 America/Los_Angeles

## Current State

Agent Red is in release-readiness recovery after a production-readiness inspection found P0/P1 blockers:

- tracked generated production manifest with plaintext credentials,
- fail-open standalone admin behavior when deployed without an admin password,
- static fallback signing secrets reaching production if env vars are absent,
- red GitHub security/SonarCloud gates,
- incomplete exact-candidate CI evidence for the active release branch,
- in-memory production-facing commercial state requiring a launch-scope decision.

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

## 2026-04-20 Risk Register Remediation Pass

Claim: Production GO remains blocked. The risk-register remediation target is not
to claim release readiness prematurely; it is to close, explicitly defer, or
supersede every blocker with governed evidence.

Current evidence:

- Local branch: `main` at `f06e28e5` after the session-wrap artifact commit.
- Last green code candidate: `main@760efa43`.
- Remote branch divergence: `origin/main...origin/develop` reports 15 commits
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
  `SONAR_TOKEN`, last updated 2026-04-10T03:57:11Z.
- Correct-project workflow inventory currently lists `Docs Quality` and
  `Python Tests`; `gh workflow list` / `gh run list` found no active workflows
  named `SonarCloud` or `Security Scan` in
  `Remaker-Digital/agent-red-customer-engagement`.
- GitHub Actions evidence for the last code candidate `main@760efa43` is green
  for Release Candidate Gate, Python Tests, Lint, and Accessibility. The runs
  were created 2026-04-21T07:00:46Z and completed by 2026-04-21T07:09:46Z.
- No GitHub Actions run was visible yet for wrap-only HEAD `f06e28e5` during
  wrap-up verification. Treat `760efa43` as the last green code candidate, or
  rerun required gates on `f06e28e5` before treating repository HEAD as the
  exact production candidate.
- Prior SonarCloud and Security Scan failures harvested from any non-authoritative
  repository are no longer release evidence for Agent Red.
- Local non-deploying release candidate gate passed after the GT-KB dependency
  alignment fix: `python scripts/release_candidate_gate.py --skip-frontend`
  completed Ruff E/F, import-cycle detection, Bandit, pip-audit, Codex hook
  parity, and 183 targeted tests.

Blocker disposition:

- Production credentials exposed in the deleted generated manifest must be
  rotated: still owner/secret-provider gated. Do not close without credential
  rotation evidence.
- Owner must decide whether git history requires secret purging: still
  owner-gated. Do not close without an explicit owner decision.
- GitHub SonarCloud must pass with valid `SONAR_TOKEN` and project
  configuration: still blocked. `SONAR_TOKEN` exists in the correct project,
  but no active correct-project SonarCloud workflow/run evidence exists.
- GitHub Security Scan must pass with valid `ACR_USERNAME` and `ACR_PASSWORD`:
  still blocked. No active correct-project Security Scan workflow/run evidence
  exists.
- `main` and `develop` release provenance: operational divergence is cleared
  for the current candidate (`develop` is 0 commits ahead of `main`), but the
  release-branch policy still needs owner/project disposition.
- Full Python 3.12 CI on the last code candidate commit: cleared for
  `main@760efa43` by green Release Candidate Gate and Python Tests runs. If
  deploying repository HEAD, rerun or obtain required CI evidence for
  `f06e28e5`.
- Commercial durability launch scope must be decided for
  Shopify/Stripe/action-executor in-memory paths: still owner/product-scope
  gated.

Recommended next actions:

- Owner: rotate any production credentials that were exposed in the deleted
  generated manifest and provide rotation evidence suitable for release
  readiness.
- Owner: decide whether repository history must be purged for the exposed
  manifest.
- Prime Builder: keep local remote, dashboard GitHub Actions evidence, and
  generated startup reports aligned to
  `Remaker-Digital/agent-red-customer-engagement`.
- Prime Builder or repo admin: add or restore SonarCloud and Security Scan
  workflows on the correct project, then run them on the exact candidate.
- Owner/project: decide the release-branch policy now that `develop` has no
  commits ahead of `main` and `main` is 15 commits ahead of `develop`.

## Remaining Release Blockers

- Production credentials exposed in the deleted generated manifest must be rotated.
- Owner must decide whether git history requires secret purging.
- GitHub SonarCloud must pass with valid `SONAR_TOKEN` and project configuration.
- GitHub Security Scan must pass with valid `ACR_USERNAME` and `ACR_PASSWORD`.
- If deploying repository HEAD rather than the last green code candidate,
  required CI evidence must be obtained for `f06e28e5`.
- Owner/project must decide the release-branch provenance policy for
  `main`/`develop`.
- Commercial durability launch scope must be decided for Shopify/Stripe/action-executor in-memory paths.

## Governance Notes

- Relevant prior deliberations searched and cited in the 2026-04-19 insight report: `DELIB-0560`, `DELIB-0565`, `DELIB-0602`, `DELIB-0603`.
- Current KnowledgeDB records: `DOC-release-readiness-recovery` v2 and `DOC-groundtruth-governance-adoption-2026-04-19` v1.
- Current Deliberation Archive record: `DELIB-0829` v1 for the owner governance-adoption directive and implementation evidence.
- Current role-governance decision: `DELIB-0830` v1 records the owner directive that Loyal Opposition/Codex assumes the acting Prime Builder role while canonical Prime Builder is unavailable.
- Current role-portability principle: any capable AI harness may assume Prime Builder or Loyal Opposition when assigned by the owner; the assigned harness must enable that role's skills, plugins, hooks, directives, and responsibilities to the extent possible, and when the bridge is available the counterpart is always Loyal Opposition.
- Current GT-KB installation principle: when GT-KB is installed, the project must be fully configured for Prime Builder; if multiple capable harnesses are installed, configuration should be prepared for all of them so the owner can assign Prime Builder and the non-Prime bridge participant assumes Loyal Opposition.
- Owner approval to continue and modify all necessary files was received in-session.
- This topic should be updated again after GitHub CI, credential rotation, and branch reconciliation are complete.
- The release-candidate gate now treats governance adoption as part of production readiness, not a separate manual checklist.
