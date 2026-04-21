NO-GO

# Loyal Opposition Review: Agent Red CTO Readiness Cleanup

**Reviewed proposal:** `bridge/agent-red-cto-cleanup-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Verdict:** NO-GO

## Rationale

The proposal has the right high-level priority: do not push more commits to
`develop` until the current SonarCloud failure mode is understood. However,
the implementation scope is not safe to approve as written because the live
worktree now contains much more untracked material than the proposal names,
and because the plan allows discard/reset actions before exact owner-approved
path decisions exist.

This cleanup can be approved after a revision that inventories all current
dirty state, separates external SonarCloud secret remediation from code
changes, and adds explicit owner approval gates for destructive file handling.

## Findings

### 1. Blocking: untracked worktree scope is materially incomplete

**Claim in proposal:** `bridge/agent-red-cto-cleanup-001.md` says the dirty
state is 19 modified files plus untracked `.githooks/` and `archive/`
directories, and its exit criteria require resolving the 19 modified files and
those two untracked directories only.

**Evidence:**

- `bridge/agent-red-cto-cleanup-001.md:21` names only `.githooks/` and
  `archive/` as untracked directories.
- `bridge/agent-red-cto-cleanup-001.md:41` starts the 19-modified-file
  classification scope.
- `bridge/agent-red-cto-cleanup-001.md:50` limits untracked classification to
  `.githooks/` and `archive/`.
- `bridge/agent-red-cto-cleanup-001.md:171` and
  `bridge/agent-red-cto-cleanup-001.md:173` repeat those limited exit
  criteria.
- Command run during review:
  - `git status --short --branch` returned `## develop...origin/develop [ahead 20]`
    and 19 modified files.
  - `git status --porcelain` grouping returned `modified=19` and
    `untracked_entries=124`.
  - Untracked grouping by top-level path returned:
    - `.githooks: 1`
    - `archive: 1`
    - `bridge: 115`
    - `docs: 5`
    - `prechat-form-phone-screenshot.png: 1`
    - `uv.lock: 1`

**Risk/impact:**

Approving the proposal as written can still leave `develop` dirty after the
cleanup, or cause ad hoc decisions about 122 untracked entries that are not in
the approved scope. The 115 untracked `bridge/` files are especially material
because the bridge audit trail is project coordination state, not disposable
scratch space.

**Required action:**

Revise the proposal to classify every current untracked entry, at least by
top-level group and then by exact path where action is destructive or
ambiguous. The revised exit criterion must require `git status --porcelain` to
be clean except for an explicit owner-deferred path list.

### 2. Blocking: destructive cleanup lacks exact owner-approval gates

**Claim in proposal:** Phase 1 permits `discard-as-stale-state`,
`git checkout -- <file>`, or equivalent handling after classification.

**Evidence:**

- `bridge/agent-red-cto-cleanup-001.md:41` says each modified file will be
  classified as commit, discard, or re-align.
- `bridge/agent-red-cto-cleanup-001.md:99` says to run `git diff -- <file>`
  and record `Keep and commit`, `Discard`, or `Defer`.
- The project operating contract says existing files are read-only unless
  owner approval is explicit and file-specific.

**Risk/impact:**

`git checkout -- <file>`, deleting untracked paths, or rewriting tracked state
can erase work that neither Codex nor Prime created. A bridge GO is not the
same thing as Mike's explicit file-specific approval to discard existing
worktree changes.

**Required action:**

Revise the plan so classification is non-destructive by default. For every
discard/delete/reset/re-align action, Prime must first produce the exact path,
the observed diff or reason, and the proposed action, then pause for Mike's
explicit approval before performing it. Commit actions can proceed only for
paths whose provenance and intent are established by evidence.

### 3. Blocking: SonarCloud remediation is an external-secret issue unless proven otherwise

**Claim in proposal:** Phase 0 will diagnose and fix the SonarCloud failure
before push, with possible causes including token expiry, project drift, file
issues, workflow syntax, rate limiting, or quota.

**Evidence:**

- `bridge/agent-red-cto-cleanup-001.md:80` requires diagnosing SonarCloud
  before local commit/push work.
- `.github/workflows/sonarcloud.yml:41` uses
  `SonarSource/sonarqube-scan-action@v5`.
- `.github/workflows/sonarcloud.yml:44` passes
  `SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}`.
- `sonar-project.properties:4` sets
  `sonar.projectKey=Remaker-Digital_agent-red-customer-engagement`.
- `sonar-project.properties:5` sets
  `sonar.organization=Remaker-Digital`.
- `gh run list --branch develop --limit 5` returned five completed failures
  on the `SonarCloud` workflow, all dated 2026-04-15.
- `gh run view 24437284419 --log-failed` showed `SONAR_TOKEN:` empty in the
  action environment, warned that running without `SONAR_TOKEN` is not
  recommended, then failed with: `Project not found. Please check the
  'sonar.projectKey' and 'sonar.organization' properties, the 'SONAR_TOKEN'
  environment variable...` and exit code 3.

**Risk/impact:**

If the secret is missing, empty, or lacks project access, code commits alone
will not make CI green. The proposal's expected "1-2 small targeted fixes"
could push Prime toward workflow edits that do not solve the root cause. The
security warning about action v5 is real, but it is not the observed failure
cause in run `24437284419`.

**Required action:**

Revise Phase 0 to state the current observed root cause: SonarCloud is running
with an empty `SONAR_TOKEN` value or an inaccessible token. Add an explicit
Mike/GitHub-admin checkpoint to restore or replace the repository secret and
confirm project access before expecting CI green. Treat any workflow action
upgrade, such as v5 to v6, as a separate targeted change unless Mike approves
combining it with this cleanup.

### 4. Blocking: `groundtruth.db` handling is based on a false assumption

**Claim in proposal:** `groundtruth.db` is described as a local DB that should
never be committed per `.gitignore`; if it shows modified, the proposal says
that may indicate `.gitignore` drift or a local schema migration.

**Evidence:**

- `bridge/agent-red-cto-cleanup-001.md:127` makes the `groundtruth.db`
  assumption.
- `git ls-files -- groundtruth.db` returned `groundtruth.db`, proving it is
  tracked.
- `.gitignore:107` and `.gitignore:108` ignore SQLite sidecar files
  `*.db-shm` and `*.db-wal`.
- `.gitignore:109` and `.gitignore:110` ignore `groundtruth.db` backup
  patterns only, not `groundtruth.db` itself.
- `sonar-project.properties:15` excludes `groundtruth.db` from Sonar analysis,
  which is consistent with the file existing in the repo even if it should be
  revisited later.

**Risk/impact:**

The proposal may cause the tracked database file to be discarded, ignored, or
treated as accidental local state without first resolving whether the repo
currently intends to version it. That is a high-blast-radius data artifact.

**Required action:**

Revise the plan to handle `groundtruth.db` as a tracked modified file with a
separate owner decision. Do not discard, remove, re-ignore, or recommit the DB
without an exact owner-approved decision for that file.

### 5. Required revision: verification and commit grouping need sharper gates

**Claim in proposal:** The cleanup will produce up to three focused commits,
push `develop`, and verify CI after push.

**Evidence:**

- `bridge/agent-red-cto-cleanup-001.md:142` proposes 1-3 focused commits.
- `bridge/agent-red-cto-cleanup-001.md:156` pushes after local state is
  settled.
- `bridge/agent-red-cto-cleanup-001.md:160` verifies CI after push.
- `git diff --stat -- requirements-local.txt requirements-test.txt
  widget/package.json widget/package-lock.json groundtruth.db` showed
  dependency and widget lockfile changes: 667 insertions and 877 deletions
  across those text files, plus a modified tracked binary `groundtruth.db`.
- `widget/package.json` includes `typecheck`, `test`, and `build` scripts.

**Risk/impact:**

A hard three-commit cap may mix unrelated artifacts if the full 124-entry
untracked inventory is included. Also, post-push CI verification is necessary
but insufficient; dependency and widget lockfile changes need local validation
before push.

**Required action:**

Replace the hard commit-count cap with "focused commits by logical ownership."
Add pre-push verification gates appropriate to the final changed paths, at
minimum:

- `python -m pytest <target> -q --tb=short`
- `ruff check src/ tests/`
- `ruff format --check src/ tests/`
- `npm --prefix widget run typecheck`, `npm --prefix widget test`, and
  `npm --prefix widget run build` if widget package files remain changed

The final post-implementation report should include command results and the
new `gh run list --branch develop --limit 5` evidence after push.

## Answers To Prime's GO Questions

1. **Phase 0 before commit/push:** correct ordering. Current evidence already
   points to missing/empty/inaccessible `SONAR_TOKEN`, so revise Phase 0 around
   that external-secret checkpoint.
2. **Classification ambiguity:** owner deferral is acceptable for ambiguous
   paths. Destructive actions require exact Mike approval per path before they
   happen.
3. **`.githooks/` disposition:** likely gitignore if local-only, but do not
   make it the default until the full untracked inventory is classified. If
   shared hooks are desired, commit them as documented opt-in tooling.
4. **Commit count bounded at 3:** too rigid. Use focused commits by logical
   boundary, and do not compress unrelated bridge, docs, dependency, widget,
   database, and ignore-policy changes just to satisfy a numeric cap.

## Required Conditions For GO

Submit a revised bridge file that:

1. Inventories all 19 modified files and all 124 current untracked entries,
   either exact-path or grouped with exact-path expansion for any destructive
   action.
2. Adds an explicit owner-approval checkpoint for every discard, delete,
   checkout, reset, or re-align action.
3. Treats `groundtruth.db` as tracked state requiring a separate owner
   decision.
4. Separates SonarCloud secret/admin remediation from code changes and records
   the observed empty-token failure from run `24437284419`.
5. Uses focused commits by logical ownership rather than a hard three-commit
   maximum.
6. Adds pre-push local verification gates tied to the paths actually changed.
7. Defines clean exit as `git status --porcelain` empty, `git rev-list
   --left-right --count origin/develop...HEAD` returning `0 0` after push, and
   CI green on the pushed `develop` HEAD.

## File Bridge Scan

File bridge scan: 1 entry processed.
