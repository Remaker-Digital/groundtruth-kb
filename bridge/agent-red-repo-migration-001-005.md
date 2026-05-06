NEW

# Post-Impl REPORT - AGENT-RED-REPO-MIGRATION-001 Read-Only Migration Inventory

Reported by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: `bridge/agent-red-repo-migration-001-003.md` REVISED-1; Loyal Opposition GO at `bridge/agent-red-repo-migration-001-004.md`
Requested bridge disposition: `VERIFIED` for read-only inventory only

## Claim

The read-only Agent Red migration inventory is complete. No external repository writes were performed, no branch settings or secrets were changed, no tags were created, and no Agent Red source files were copied into GT-KB.

Key findings:

- Canonical Agent Red: `https://github.com/mike-remakerdigital/agent-red` (`private`, default branch `main`).
- De facto Agent Red: `https://github.com/Remaker-Digital/agent-red-customer-engagement` (`private`, default branch `main`).
- Both repositories currently have identical `develop` heads: `84b2f8b065037582d230bc8552acb6810421e219`.
- The accepted transient Slice 8.5 / Slice 8.6 de facto CI evidence remains one commit behind current `develop`, at `98b7eab19812ed995d1e606d1d9854a7da803dab`; the only commit from `98b7eab1` to `84b2f8b0` changes `bridge/INDEX.md` and adds `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-005.md`.
- Canonical `develop` has equivalent workflow files, but canonical CI is not fully green: Lint, Release Candidate Gate, and Python Tests passed on `push`; SonarCloud passed only on later `workflow_dispatch`; Security Scan remains failed in Docker Scout credential/authentication steps.
- Canonical `main` is graph-ancestor of de facto `main`; de facto `main` is 136 commits ahead and canonical `main` is 0 commits ahead. A fast-forward appears graph-viable, but it is an external mutation and remains out of scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed in `bridge/` and registered in `bridge/INDEX.md`.
- `.claude/rules/file-bridge-protocol.md` - bridge status semantics and post-implementation review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward bridge, owner-decision, root-boundary, release, and artifact lifecycle authorities.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps inventory acceptance criteria to command evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red is separate from GT-KB; this report records external metadata only.
- `.claude/rules/project-root-boundary.md` - GT-KB artifacts produced by this work remain under `E:\GT-KB`.
- `.claude/rules/canonical-terminology.md` - canonical project-resource alias handling and GT-KB / Agent Red terminology.
- `.claude/rules/project-resource-aliases.toml` - canonical external resource identity for Agent Red.
- `memory/project_external_resource_registry.md` - human-readable resource registry companion.
- `memory/feedback_groundtruth_kb_canonical_project_urls.md` - canonical URL discipline.
- `GOV-ARTIFACT-APPROVAL-001` - any later mutation or waiver artifact requiring owner approval must use the formal approval path.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - owner-approved transient exception and migration prerequisite.
- `bridge/agent-red-repo-migration-001-003.md` - approved read-only inventory proposal.
- `bridge/agent-red-repo-migration-001-004.md` - Loyal Opposition GO.
- Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Owner Decisions / Input

This report relies on `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`.

- Scope: Slice 8.6 and Slice 8.5 may cite de facto Agent Red CI evidence from `Remaker-Digital/agent-red-customer-engagement` while canonical migration is pending.
- Expiry: the exception expires only after the migration thread reaches `VERIFIED`, equivalent canonical CI evidence is captured on `mike-remakerdigital/agent-red`, and Slice 8.5 reaches `VERIFIED` on canonical evidence.
- Residual risk: de facto CI may diverge from canonical post-migration CI; repository identity confusion remains possible; migration complexity may delay rc1.
- Citation obligation: Slice 8.6 / Slice 8.5 artifacts using de facto CI evidence must cite the DELIB by full ID.

This report does not request or perform owner-gated external mutations.

## Read-Only Command Log

Commands used:

```text
git remote -v
git ls-remote --heads https://github.com/mike-remakerdigital/agent-red.git
git ls-remote --heads https://github.com/Remaker-Digital/agent-red-customer-engagement.git
gh repo view mike-remakerdigital/agent-red --json nameWithOwner,isPrivate,defaultBranchRef,url
gh repo view Remaker-Digital/agent-red-customer-engagement --json nameWithOwner,isPrivate,defaultBranchRef,url
git fetch --no-tags <canonical-url> +refs/heads/develop:refs/tmp/agent-red-migration-inventory/canonical/develop +refs/heads/main:refs/tmp/agent-red-migration-inventory/canonical/main
git fetch --no-tags <de-facto-url> +refs/heads/develop:refs/tmp/agent-red-migration-inventory/defacto/develop +refs/heads/main:refs/tmp/agent-red-migration-inventory/defacto/main
git merge-base <canonical-ref> <de-facto-ref>
git rev-list --left-right --count <canonical-ref>...<de-facto-ref>
git diff --name-status --find-renames <canonical-ref>...<de-facto-ref>
git ls-tree -r --name-only <ref> -- .github/workflows .github/dependabot.yml
gh run list --repo <repo> --branch develop --limit 10 --json databaseId,workflowName,headBranch,event,headSha,conclusion,status,url,createdAt
gh run view <run-id> --repo mike-remakerdigital/agent-red --json databaseId,workflowName,headBranch,event,headSha,conclusion,status,url,jobs
git update-ref -d refs/tmp/agent-red-migration-inventory/canonical/develop
git update-ref -d refs/tmp/agent-red-migration-inventory/canonical/main
git update-ref -d refs/tmp/agent-red-migration-inventory/defacto/develop
git update-ref -d refs/tmp/agent-red-migration-inventory/defacto/main
git for-each-ref refs/tmp/agent-red-migration-inventory
```

Temporary local analysis refs were removed. `git for-each-ref refs/tmp/agent-red-migration-inventory` returned no refs.

## Repository Identity

| Resource | URL | Privacy | Default branch | Relevant head |
|---|---|---|---|---|
| Canonical Agent Red | https://github.com/mike-remakerdigital/agent-red | private | `main` | `develop@84b2f8b065037582d230bc8552acb6810421e219` |
| De facto Agent Red | https://github.com/Remaker-Digital/agent-red-customer-engagement | private | `main` | `develop@84b2f8b065037582d230bc8552acb6810421e219` |

Local GT-KB remotes:

```text
agent-red https://github.com/mike-remakerdigital/agent-red.git (fetch/push)
origin    https://github.com/Remaker-Digital/groundtruth-kb.git (fetch/push)
```

No GT-KB local remote is configured for the de facto Agent Red repository; it was queried by URL only.

## Commit-Graph Shape

| Comparison | Common ancestor | Ahead/behind result | Interpretation |
|---|---|---|---|
| canonical `develop` vs de facto `develop` | `84b2f8b065037582d230bc8552acb6810421e219` | `0 0` | Heads are identical; file diff is empty. |
| canonical `main` vs de facto `main` | `6f857e8932bef552eb2a26889ba959f42802f53e` | `0 136` | De facto `main` is 136 commits ahead; canonical `main` is an ancestor. Graph-wise fast-forward appears possible, but external mutation is out of scope. |
| Slice accepted CI SHA vs current `develop` | `98b7eab1...` to `84b2f8b0...` | `0 1` | Current `develop` adds only the Slice 8.6 post-implementation bridge report and index update after accepted CI evidence. |

For canonical `main` to de facto `main`, `git diff --name-status --find-renames` reported 1,317 changed paths. `git diff --dirstat=files,0` showed the largest category is `bridge/` at 77.3%, followed by scripts, tests, independent progress assessments, workflow files, docs, and GT-KB governance surfaces.

Workflow-file changes on `main` include added `accessibility.yml`, `chromatic.yml`, `release-candidate-gate.yml`, `visual-regression.yml`, and modified `deploy-docs.yml`, `docs-quality.yml`, `lint.yml`, `python-tests.yml`, `security-scan.yml`, and `sonarcloud.yml`.

## Workflow And Release Evidence Shape

Both `develop` heads contain identical workflow inventory:

```text
.github/dependabot.yml
.github/workflows/accessibility.yml
.github/workflows/build-agent-containers.yml
.github/workflows/build-api-gateway.yml
.github/workflows/build-slim-gateway.yml
.github/workflows/build-test-host.yml
.github/workflows/chromatic.yml
.github/workflows/deploy-docs.yml
.github/workflows/docs-quality.yml
.github/workflows/lint.yml
.github/workflows/python-tests.yml
.github/workflows/release-candidate-gate.yml
.github/workflows/security-scan.yml
.github/workflows/sonarcloud.yml
.github/workflows/visual-regression.yml
```

Required Slice 8.5 / Slice 8.6 workflow files are present on canonical and de facto `develop`: Lint, Release Candidate Gate, SonarCloud, Security Scan, and Python Tests.

Current canonical `develop@84b2f8b0` run evidence:

| Workflow | Event | Run | Conclusion | Notes |
|---|---|---|---|---|
| Lint | `push` | https://github.com/mike-remakerdigital/agent-red/actions/runs/25297741987 | success | Canonical push evidence exists. |
| Release Candidate Gate | `push` | https://github.com/mike-remakerdigital/agent-red/actions/runs/25297741988 | success | Canonical push evidence exists. |
| Python Tests | `push` | https://github.com/mike-remakerdigital/agent-red/actions/runs/25297741985 | success | Canonical push evidence exists. |
| SonarCloud | `push` | https://github.com/mike-remakerdigital/agent-red/actions/runs/25297741982 | failure | Fails at `Validate SonarCloud token`; later `workflow_dispatch` run `25298460502` succeeded. |
| Security Scan | `push` | https://github.com/mike-remakerdigital/agent-red/actions/runs/25297741991 | failure | Docker Scout failed at `Validate Docker Scout ACR secrets`. |
| Security Scan | `workflow_dispatch` | https://github.com/mike-remakerdigital/agent-red/actions/runs/25299124205 | failure | Docker Scout advanced past ACR validation, then failed at Docker Hub login. |

Accepted de facto evidence remains the transient exception chain from `Remaker-Digital/agent-red-customer-engagement` at `98b7eab19812ed995d1e606d1d9854a7da803dab`: Lint `25296718957`, Release Candidate Gate `25296719002`, SonarCloud `25296718961`, Security Scan `25296718958`, and Python Tests `25296718963`, all `success`.

Conclusion: Slice 8.5 can proceed under the transient exception before canonical migration completes, and the Slice 8.5 report has done so. Canonical CI acceptance is still incomplete because canonical Security Scan is red and canonical push SonarCloud was red.

## Branch Inventory

Branch counts:

- Canonical: 19 heads.
- De facto: 18 heads.

Branches only on canonical:

```text
claude/investigate-credit-usage-ecQjY
codex/claude-design-backlog
dependabot/github_actions/actions/checkout-6
dependabot/npm_and_yarn/admin/eslint-10.2.0
dependabot/npm_and_yarn/admin/mantine/core-9.0.1
dependabot/npm_and_yarn/widget/storybook-10.3.5
dependabot/npm_and_yarn/widget/vite-8.0.8
dependabot/pip/azure-identity-gte-1.25.3
dependabot/pip/mutmut-gte-3.5.0
dependabot/pip/qrcode-gte-8.2
gh-pages
```

Branches only on de facto:

```text
codex/gtkb-current-main-integration
dependabot/github_actions/actions/setup-node-6
dependabot/npm_and_yarn/admin/multi-0193e73c84
dependabot/npm_and_yarn/admin/typescript-eslint/parser-8.59.0
dependabot/npm_and_yarn/widget/preact/preset-vite-2.10.5
dependabot/npm_and_yarn/widget/storybook/preact-vite-10.3.5
dependabot/pip/azure-storage-blob-gte-12.28.0
dependabot/pip/pypdf-gte-6.10.2
dependabot/pip/pytest-timeout-gte-2.4.0
e1-apply
```

## Conflict And Risk Inventory

Facts:

- `develop` migration shape is already aligned at the git object level: same head and empty diff.
- Canonical `develop` still lacks fully green canonical CI evidence.
- Canonical `main` can likely fast-forward to de facto `main` from a graph perspective, but that is a repository mutation and requires a separate plan.
- Branch inventory has asymmetric Dependabot and working branches; branch cleanup or preservation requires owner/project disposition.
- Canonical workflow failures appear configuration/secret related, not workflow-file drift: SonarCloud token validation and Docker Scout ACR/Docker Hub authentication.

Risks:

- Treating equal `develop` heads as release authorization would skip canonical CI evidence; do not do that.
- Fast-forwarding `main` without owner approval would mutate the canonical repository and possibly alter release/default-branch behavior.
- Secret/configuration remediation is outside Codex credential lifecycle scope; Codex may validate or use configured values only when the task requires it and Mike authorizes that use.
- Dependabot branch asymmetry may create duplicate or stale dependency-update work if both repositories remain active.

## Follow-On Approval Plan

Facts and recommendations are separated below.

Facts:

- No code migration is needed to make canonical `develop` equal de facto `develop`; it is already equal.
- Canonical CI evidence is the immediate remaining release-evidence gap.
- Canonical `main` is behind de facto `main` by 136 commits.

Recommended follow-on proposals:

1. File a canonical CI evidence proposal for `mike-remakerdigital/agent-red` `develop@84b2f8b0`, focused on resolving or formally disposing SonarCloud and Security Scan configuration gaps.
2. File a separate owner-approved mutation plan for any `main` fast-forward or PR-based reconciliation.
3. File a branch-retention cleanup plan for asymmetric Dependabot and work branches after canonical CI is green.
4. Keep `v0.7.0-rc1` blocked until canonical CI evidence is captured and the Slice 8.5 thread reaches the required terminal state under the governing release plan.

Owner or repository-admin approvals required before mutation:

- Any push, force-push, merge, PR creation, tag creation, or branch deletion.
- Any GitHub repository settings, branch protection, environment, workflow secret, or deployment configuration change.
- Any release tag, PyPI publish, or production deployment.

## Specification-Derived Verification

| Test ID | Spec coverage | Procedure | Result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` updated so this file is latest `NEW` | PASS |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id agent-red-repo-migration-001` | PASS - `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect report for DELIB scope, expiry, residual risk, citation obligation, and authorization limits | PASS |
| T-boundary-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, project root boundary | Inspect changed paths | PASS - GT-KB bridge/backlog artifacts only; no Agent Red source copied into GT-KB |
| T-readonly-1 | External mutation separation | Review command log for external writes | PASS - no push, tag, branch-protection, settings, secrets, or deployment operation present |
| T-inventory-1 | Acceptance criteria | Review inventory tables for repo heads, commit graph, workflow shape, conflict/risk categories, and follow-on approvals | PASS |

## Authorization Block

This report does not authorize any external mutation and does not authorize `v0.7.0-rc1`.

`v0.7.0-rc1 remains unauthorized` pending canonical migration, canonical CI evidence, and required bridge terminal states.

## Applicability Preflight

```text
packet_hash: sha256:deaa6e8f91f3d5223fcdc20ff7151776939c91cd5a4345c6f213a5d24ad6abba
bridge_document_name: agent-red-repo-migration-001
operative_file: bridge/agent-red-repo-migration-001-005.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```
