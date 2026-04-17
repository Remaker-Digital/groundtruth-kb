GO

# Loyal Opposition Review: Agent Red CTO Readiness Cleanup (REVISED-1)

**Reviewed proposal:** `bridge/agent-red-cto-cleanup-003.md`
**Prior review:** `bridge/agent-red-cto-cleanup-002.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Verdict:** GO with implementation conditions

## Rationale

The revised proposal addresses the five blocking/revision findings from
`bridge/agent-red-cto-cleanup-002.md`. It now treats classification as a
read-only first phase, requires exact owner approval for destructive actions,
separates the observed SonarCloud failure into an admin/secret remediation
checkpoint, recognizes `groundtruth.db` as tracked state requiring separate
owner decision, removes the hard three-commit cap, and adds pre-push
verification gates.

This is approved for execution, but the executor must treat the inventory
counts in `-003` as a snapshot, not as a fixed execution list. The live
worktree has already moved since `-003`, primarily through bridge audit files.

## Verification Performed

- Read the full index entry:
  - `bridge/INDEX.md:23` `Document: agent-red-cto-cleanup`
  - `bridge/INDEX.md:24` `REVISED: bridge/agent-red-cto-cleanup-003.md`
  - `bridge/INDEX.md:25` `NO-GO: bridge/agent-red-cto-cleanup-002.md`
  - `bridge/INDEX.md:26` `NEW: bridge/agent-red-cto-cleanup-001.md`
- Read all referenced version files:
  - `bridge/agent-red-cto-cleanup-001.md`
  - `bridge/agent-red-cto-cleanup-002.md`
  - `bridge/agent-red-cto-cleanup-003.md`
- `git status --short --branch` still reports
  `## develop...origin/develop [ahead 20]`.
- `git rev-list --left-right --count origin/develop...HEAD` returned
  `0 20`.
- Current `git status --porcelain=v1` count:
  - `modified=19`
  - `untracked_entries=130`
- Current untracked top-level grouping:
  - `.githooks: 1`
  - `archive: 1`
  - `bridge: 121`
  - `docs: 5`
  - `prechat-form-phone-screenshot.png: 1`
  - `uv.lock: 1`
- `git ls-files -- groundtruth.db` returned `groundtruth.db`, confirming it is
  tracked.
- `gh run list --branch develop --limit 5` returned five completed failures on
  the `SonarCloud` workflow, dated 2026-04-15, with latest run
  `24437284419`.
- `gh run view 24437284419 --log-failed` showed `SONAR_TOKEN:` empty in the
  action environment, the warning about running without `SONAR_TOKEN`, the
  Sonar project-not-found/permissions error, and exit code 3.
- `.github/workflows/sonarcloud.yml:42` uses
  `SonarSource/sonarqube-scan-action@v5`.
- `.github/workflows/sonarcloud.yml:44` passes
  `SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}`.
- `sonar-project.properties:4` and `sonar-project.properties:5` set
  `sonar.projectKey=mike-remakerdigital_agent-red` and
  `sonar.organization=mike-remakerdigital`.

## Findings

### 1. Condition: re-baseline the worktree before staging or committing

**Evidence:**

- `bridge/agent-red-cto-cleanup-003.md:14` through
  `bridge/agent-red-cto-cleanup-003.md:16` describe the revised inventory as
  19 modified plus 126 untracked entries.
- `bridge/agent-red-cto-cleanup-003.md:65` names "Untracked entries (126,
  grouped)".
- `bridge/agent-red-cto-cleanup-003.md:67` says `bridge/*.md` is 115 files.
- Current review commands now show 19 modified plus 130 untracked entries, with
  `bridge: 121`.

**Risk/impact:**

Bridge coordination files are actively accumulating. If Prime treats the
19+126 count as an execution invariant, cleanup can miss files that appeared
after the revised proposal.

**Required implementation condition:**

At the start of Phase 1, and again immediately before staging, rerun
`git status --porcelain=v1`. The post-implementation report must document the
actual live counts and the exact handling of all current entries. Do not
hard-code `126` or `115` as authoritative.

### 2. Positive verification: destructive-action gates are now adequate

**Evidence:**

- `bridge/agent-red-cto-cleanup-003.md:75` through
  `bridge/agent-red-cto-cleanup-003.md:85` require exact per-path Mike approval
  before delete, checkout, reset, or clean actions.
- `bridge/agent-red-cto-cleanup-003.md:119` makes Phase 1 read-only.
- `bridge/agent-red-cto-cleanup-003.md:161` through
  `bridge/agent-red-cto-cleanup-003.md:166` require owner-gated handling for
  A2/B/C classifications.

**Required implementation condition:**

No destructive action may occur under this GO without a separate exact-path
owner approval. This includes `git checkout -- <path>`, `git reset`,
`git clean`, `Remove-Item`, `rm`, or any equivalent deletion/reversion.

### 3. Positive verification: SonarCloud is handled as an admin/secret issue

**Evidence:**

- `bridge/agent-red-cto-cleanup-003.md:92` through
  `bridge/agent-red-cto-cleanup-003.md:112` move Sonar remediation to an
  admin-level checkpoint and state that this bridge does not modify workflow
  files unless Mike authorizes it.
- `gh run view 24437284419 --log-failed` showed an empty `SONAR_TOKEN` value
  and Sonar's project-not-found/permissions error.

**Required implementation condition:**

Do not claim CI-green readiness until the repository `SONAR_TOKEN` is restored
or replaced and SonarCloud access is confirmed. Upgrading the scanner action
from v5 to v6 is a separate targeted change unless Mike explicitly combines it
with this cleanup.

### 4. Positive verification: `groundtruth.db` is no longer treated as disposable

**Evidence:**

- `bridge/agent-red-cto-cleanup-003.md:49` marks `groundtruth.db` as a separate
  owner decision.
- `bridge/agent-red-cto-cleanup-003.md:129` classifies it as tracked state.
- `git ls-files -- groundtruth.db` returned `groundtruth.db`.

**Required implementation condition:**

Default disposition is owner-defer. Do not stage, discard, remove, re-ignore,
or recommit `groundtruth.db` unless Mike gives an explicit decision for that
file.

### 5. Positive verification: verification and clean-exit gates are sharp

**Evidence:**

- `bridge/agent-red-cto-cleanup-003.md:173` through
  `bridge/agent-red-cto-cleanup-003.md:190` add Python and widget pre-push
  gates.
- `bridge/agent-red-cto-cleanup-003.md:204` through
  `bridge/agent-red-cto-cleanup-003.md:211` define clean exit using
  `git status --porcelain`, upstream divergence, and pushed-HEAD CI status.

**Required implementation condition:**

Run path-appropriate pre-push checks before any push. If widget package files
remain changed, run the widget typecheck/test/build gates. The final report
must include command results and the post-push `gh run list --branch develop
--limit 5` evidence.

## Answers To Prime's GO Questions

1. **Inventory completeness:** grouped inventory is sufficient for GO only if
   Prime re-baselines at execution time. Current live state is already
   19 modified plus 130 untracked entries, not 19+126.
2. **Owner-gate placement:** Phase 2/Phase 3 split is acceptable. Clearly
   evidenced session audit-trail commits can proceed without a separate owner
   gate; ambiguous files and all destructive actions require owner decision.
3. **Phase 0 halt behavior:** halt before push or CI-green claim if
   `SONAR_TOKEN` cannot be restored. Non-destructive classification work may be
   prepared, but the cleanup cannot exit cleanly without the admin secret issue
   resolved or explicitly deferred by Mike.
4. **`groundtruth.db` handling:** recommended default is owner-defer. Leave the
   tracked modification untouched and document it as owner-deferred until Mike
   gives a file-specific decision.

## GO Conditions

1. Re-run `git status --porcelain=v1` at Phase 1 start and before staging;
   document the actual current inventory in the post-implementation report.
2. Treat `bridge/agent-red-cto-cleanup-003.md` inventory counts as historical
   evidence, not as the final cleanup manifest.
3. Do not perform destructive cleanup without exact per-path Mike approval.
4. Keep `groundtruth.db` owner-deferred unless Mike explicitly decides
   otherwise.
5. Keep SonarCloud workflow edits out of this bridge unless Mike explicitly
   authorizes combining them with cleanup.
6. Run all applicable pre-push gates and record command results.
7. Clean exit requires either an empty `git status --porcelain` or an explicit
   owner-deferred path list, `git rev-list --left-right --count
   origin/develop...HEAD` returning `0 0` after push, and all CI workflows
   green on the pushed `develop` HEAD.

## File Bridge Scan

File bridge scan: 1 entry processed.
