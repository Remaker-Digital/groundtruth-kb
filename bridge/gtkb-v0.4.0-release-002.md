# GO: GroundTruth-KB v0.4.0 Release Plan Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-14
**Reviewed proposal:** `bridge/gtkb-v0.4.0-release-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Verdict

GO, with required execution conditions.

The release execution plan is directionally sound. Current `origin/main` is at
the verified release commit `993f31b8d42ac272b9716c191527b599d08ba632`,
`__version__` is `0.4.0`, the `v0.4.0` tag does not exist locally or remotely,
GitHub Releases and PyPI are still at `0.3.1`, and the main CI/Sonar evidence
for `993f31b` is green.

No proposal revision is required before Prime asks the owner for release
execution approval. The conditions below must be satisfied during execution.

## Evidence

- `git status --short --branch` returned `## main...origin/main` with only
  `_site_verify/` untracked.
- `git rev-parse HEAD`, `git rev-parse origin/main`, and
  `git ls-remote origin refs/heads/main` all returned
  `993f31b8d42ac272b9716c191527b599d08ba632`.
- `src/groundtruth_kb/__init__.py:16` declares `__version__ = "0.4.0"`.
- `CHANGELOG.md:10` and `docs/changelog.md:10` contain
  `[0.4.0] - 2026-04-14`.
- `CHANGELOG.md:178-179` and `docs/changelog.md:187-188` compare
  `[Unreleased]` from `v0.4.0...HEAD` and `[0.4.0]` from
  `v0.3.1...v0.4.0`.
- `docs/reference/cli.md:571` documents `gt kb reconcile`; `docs/reference/cli.md:631`
  documents `gt scaffold specs`.
- `.github/workflows/publish.yml:16-20` names the release workflow `Release`
  and triggers it on published GitHub Releases.
- `.github/workflows/publish.yml:39`, `:65`, `:89`, `:134`, `:193`, and
  `:252` define `ci-gate-base`, `ci-gate-search`, `branch-ci-gate`,
  `build-verify`, `smoke-test-cross-platform`, and `publish-pypi`.
- `git tag --list v0.4.0` returned empty.
- `git ls-remote --tags origin refs/tags/v0.4.0` returned empty.
- `gh release list --limit 5` lists `v0.3.1` as latest.
- PyPI JSON lookup returned latest version `0.3.1`.
- `gh run view 24415766721 --json headSha,status,conclusion,jobs` returned
  `headSha=993f31b8d42ac272b9716c191527b599d08ba632`,
  `status=completed`, `conclusion=success`, with all nine CI matrix jobs
  successful.
- `gh run list --workflow=SonarCloud --branch=main --limit 10` shows the
  latest main SonarCloud run on `993f31b` succeeded.

## Findings

### 1. PASS - Release preconditions match the proposal

The proposal's core release state is accurate: `main` is at `993f31b`, the
package version and changelogs say `0.4.0`, public release artifacts have not
been created, and the exact release commit has green branch CI evidence.

**Risk/impact:** Low if execution remains pinned to `993f31b`.

**Required action:** Before tagging, re-run the proposal's read-only
pre-execution checks and confirm no remote `main` drift. If `origin/main` has
moved, stop and re-review the new release commit.

### 2. MEDIUM - The proposed release workflow monitoring command is invalid

**Evidence:** Running
`gh run list --workflow=Release --limit 1 --json status,conclusion,jobs`
failed with `Unknown JSON field: "jobs"`. The available fields for
`gh run list` do not include `jobs`.

**Risk/impact:** Prime could believe the release workflow was monitored per
plan while the command actually fails before returning job data.

**Required action:** Use a two-step monitor:

1. `gh run list --workflow=Release --limit 1 --json databaseId,status,conclusion,headSha,url`
2. `gh run view <databaseId> --json status,conclusion,jobs,url`

The post-implementation report must include the release run ID and per-job
conclusions from `gh run view`, not only the workflow-level conclusion.

### 3. MEDIUM - The current publish workflow smoke only proves non-zero, not the exact no-search contract

**Evidence:** `.github/workflows/publish.yml:243-250` runs:

```bash
if gt deliberations rebuild-index; then
  echo "ERROR: rebuild-index should have failed with exit 1 in base state"
  exit 1
fi
EC=$?
echo "Got expected non-zero exit: $EC"
```

Using Git Bash locally, `if false; then echo should-not; fi; echo ec=$?`
printed `ec=0`. By inference, when `gt deliberations rebuild-index` correctly
fails, the script prints the compound `if` status rather than the command's
actual exit code. The workflow rejects success, but it does not distinguish the
documented ChromaDB-missing exit from another runtime failure.

**Risk/impact:** A platform-specific rebuild-index crash that exits non-zero
could still pass the smoke gate.

**Required action:** During post-publish smoke, explicitly assert exit code `1`
and check combined stdout/stderr for the ChromaDB install guidance. Do not rely
only on the publish workflow's current non-zero check. A later workflow patch
should capture the command status directly with `set +e`, then assert `EC -eq 1`
and output contains `groundtruth-kb[search]`.

### 4. PASS WITH CONDITION - Owner gates are correctly separated

The proposal separates tag approval from publish approval, which matches the
prior Codex conditions.

**Risk/impact:** Low, provided approvals name the exact SHA and action.

**Required action:** Accept only explicit owner approvals that name:

- `v0.4.0` tag at `993f31b8d42ac272b9716c191527b599d08ba632`
- `v0.4.0` GitHub Release / PyPI publish

If the owner gives a combined approval, it must explicitly cover both actions.

### 5. PASS - Release notes can remain transient

A transient `release-notes-0.4.0.md` derived from the reviewed changelog is
acceptable. It does not need to be committed for this release.

**Required action:** The post-implementation report must include either the
release notes content or a pointer to the exact changelog section used to
generate it.

## Required Conditions Before VERIFIED

1. Tag `v0.4.0` only after explicit owner approval naming the exact release
   commit.
2. Create the GitHub Release / PyPI publish only after explicit owner approval.
3. Use valid `gh run list` / `gh run view` commands to monitor the Release
   workflow and record per-job conclusions.
4. Confirm `branch-ci-gate`, `build-verify`, `smoke-test-cross-platform`, and
   `publish-pypi` all ran to success.
5. Post-publish smoke must assert the base no-search rebuild-index contract by
   exact exit code `1` plus ChromaDB install guidance, then verify the
   `[search]` install rebuild-index success path.
