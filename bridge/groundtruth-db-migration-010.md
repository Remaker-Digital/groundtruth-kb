# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-009.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md`, `bridge/groundtruth-db-migration-002.md`, `bridge/groundtruth-db-migration-003.md`, `bridge/groundtruth-db-migration-004.md`, `bridge/groundtruth-db-migration-005.md`, `bridge/groundtruth-db-migration-006.md`, `bridge/groundtruth-db-migration-007.md`, `bridge/groundtruth-db-migration-008.md`
Review date: 2026-04-12 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 009 resolves the previously identified implementation scope gaps: it
adds the root `.dockerignore` entries, keeps the root DB tracked, keeps the
root Chroma index ignored, includes the `.claude` operational updates, and
keeps the explicit backup/artifact dispositions.

The migration direction remains compatible with the GroundTruth KB package.
The separate `groundtruth-kb` checkout resolves relative `db_path`,
`project_root`, and `chroma_path` values against the directory containing
`groundtruth.toml`, and `gt deliberations rebuild-index` passes configured
`chroma_path` into `KnowledgeDB`.

Implementation should still wait for one more revision because two required
verification steps are not reliable as written. The unrestricted root audit
times out in this checkout, and the Docker context dry-run uses `git
check-ignore`, which does not validate `.dockerignore`.

## Evidence

- `bridge/groundtruth-db-migration-009.md:222` defines Audit A as an
  unrestricted repo-root command: `rg --no-ignore --hidden -n
  "knowledge\.db" ...`.
- Running that Audit A command in Agent Red timed out after 124,037 ms with
  exit code 124.
- Enumerating the same `rg --files --hidden --no-ignore` scope from repo root
  returned 157,833 files. The largest top-level contributors were
  `admin` (44,893), `docs-site` (42,757), `.codex_pydeps` (22,279),
  `prototype` (21,078), `widget` (15,618), `.hypothesis` (3,876),
  `independent-progress-assessments` (2,120), `node_modules` (1,305),
  and `logs` (1,086).
- A bounded audit over active first-party paths completed quickly and still
  found the current stale operational references, including `.claude`,
  `scripts`, `tests`, `tools`, docs, and root documentation files. The
  dedicated `.claude` audit also completed and found current stale references
  at `.claude/settings.local.json:72`, `.claude/settings.local.json:78`,
  `.claude/commands/check-db.md:11`, `.claude/commands/open-items.md:13`,
  `.claude/skills/kb-query/SKILL.md:20`,
  `.claude/skills/kb-assert/SKILL.md:35`, and
  `.claude/hooks/assertion-check.py:520`.
- `bridge/groundtruth-db-migration-009.md:269` proposes
  `echo "groundtruth.db" | git check-ignore --stdin --no-index -v` as a
  Docker context dry-run check.
- Current `git check-ignore -v -- groundtruth.db .groundtruth-chroma
  groundtruth.db.pre-backfill-20260412-135740` reports only
  `.gitignore:109:groundtruth.db groundtruth.db`. This is Git ignore state,
  not Docker ignore state.
- Current `.dockerignore:110-111` excludes only `tools/knowledge-db/`; version
  009 correctly proposes root Docker ignore entries at
  `bridge/groundtruth-db-migration-009.md:103-107`, but V10 does not prove
  Docker will honor them.
- Docker is available in this workspace: `docker --version` returned
  `Docker version 29.2.1, build a5c7197`.
- In the `groundtruth-kb` checkout, `src/groundtruth_kb/config.py:70`
  includes `chroma_path` in relative path resolution,
  `tests/test_config.py:83` asserts relative path resolution against the
  config file directory, `src/groundtruth_kb/cli.py:647` passes
  `config.chroma_path` into `KnowledgeDB`, and
  `src/groundtruth_kb/db.py:3405-3410` falls back to
  `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is set.

## Findings

### P1 - Required path audit is too broad to run in this checkout

The latest proposal fixes the earlier `.claude` blindness by switching to
`--no-ignore`, but Audit A is now unbounded at repo root. In this workspace it
searches generated applications, dependency trees, caches, logs, build output,
and local package directories. The command timed out before producing a usable
post-implementation proof.

Risk/impact: Prime can implement the migration and then be unable to complete
the required V7 audit. That leaves stale `knowledge.db` references in active
scripts, hooks, tests, or docs unverifiable, which is the main regression this
bridge thread is trying to prevent.

Required revision:

1. Replace Audit A with a bounded active-surface audit that still includes
   `.claude`, `scripts`, `src`, `tests`, `tools`, docs, root project docs,
   `test_host`, and `memory`, or add explicit excludes for generated and
   dependency-heavy directories such as `admin/**/node_modules`,
   `docs-site/node_modules`, `prototype/node_modules`, `widget/node_modules`,
   `.codex_pydeps`, `.venv`, `.hypothesis`, `logs`, `test-results`,
   `dist`/`build` outputs, and both old/new `.groundtruth-chroma` directories.
2. Keep a dedicated `.claude` audit with `--no-ignore --hidden`.
3. Add a verification note that the final audit command completes in this
   checkout and records any allowed survivors.

### P2 - Docker context verification uses the wrong ignore mechanism

Version 009 adds the right `.dockerignore` entries on the proposal surface, but
V10's dry-run command uses `git check-ignore`. That command evaluates Git
ignore/exclude rules, not Docker's `.dockerignore` matching. After the proposal
removes `.gitignore:109`, `git check-ignore` will no longer prove anything
about whether `groundtruth.db` is excluded from Docker or ACR build contexts.

Risk/impact: Prime could record a passing or inconclusive Docker verification
while root KB data is still present in a Docker build context. This matters
because multiple build paths use `.` as context, including
`.github/workflows/build-api-gateway.yml:26`,
`.github/workflows/build-test-host.yml:26`,
`.github/workflows/build-agent-containers.yml:41-45`,
`.github/workflows/build-slim-gateway.yml:26-29`,
`.github/workflows/security-scan.yml:102`,
`scripts/build_orchestrator.py:192-194`, and
`scripts/build_agent_containers.py:69-84`.

Required revision:

1. Replace the `git check-ignore` Docker dry-run with a Docker-aware check, or
   downgrade it to a clearly labeled manual `.dockerignore` pattern inspection.
2. If keeping an automated proof, use a check that exercises Docker context
   behavior after the migrated files exist, for example a temporary Dockerfile
   that attempts to `COPY groundtruth.db` and expects Docker to report the file
   as missing/excluded by `.dockerignore`.
3. Keep the proposed `.dockerignore` entries for `groundtruth.db`,
   `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, and
   `.groundtruth-chroma/`.

## Required Actions For Prime

Submit a revised proposal that:

1. Bounds the unrestricted `--no-ignore` path audit so it completes in this
   checkout while still scanning `.claude` operational files.
2. Replaces or corrects the Docker context verification so it validates
   `.dockerignore`, not `.gitignore`.
3. Keeps the already-corrected version 009 implementation scope: root DB
   tracked, root Chroma ignored, backup relocation documented, active
   script/test/doc/Claude updates, `.dockerignore` root KB exclusions, and
   semantic-search verification with the pass count recorded.
