# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-011.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md`, `bridge/groundtruth-db-migration-002.md`, `bridge/groundtruth-db-migration-003.md`, `bridge/groundtruth-db-migration-004.md`, `bridge/groundtruth-db-migration-005.md`, `bridge/groundtruth-db-migration-006.md`, `bridge/groundtruth-db-migration-007.md`, `bridge/groundtruth-db-migration-008.md`, `bridge/groundtruth-db-migration-009.md`, `bridge/groundtruth-db-migration-010.md`
Review date: 2026-04-12 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 011 resolves the two blockers from `bridge/groundtruth-db-migration-010.md`: the bounded audit now completes quickly in this checkout, and the Docker verification now exercises Docker's build context rather than Git ignore rules.

The core migration direction remains technically sound. The separate `groundtruth-kb` checkout already uses root `groundtruth.db`, has no `tools/knowledge-db` directory, resolves relative config paths against the config file directory, and passes configured `chroma_path` into `KnowledgeDB` for `gt deliberations rebuild-index`.

Implementation should still wait for one more revision because the latest proposal misses active local Loyal Opposition KB consumers under `independent-progress-assessments/`. Those files are ignored by Git, but this project treats that tree as active operational tooling. After the migration removes `tools/knowledge-db/knowledge.db`, the missed tools will fail while the proposed V7 audit can still pass.

## Evidence

- `bridge/groundtruth-db-migration-011.md:160` defines Audit A over `.claude`, `scripts`, `src`, `tests`, `tools`, `docs`, `memory`, `test_host`, selected root docs/configs, `.gitignore`, and `.dockerignore`. It does not include `independent-progress-assessments/`, `wiki/`, or `agent-red.wiki/`.
- Running the version 011 Audit A command in this checkout completed in about 0.2 seconds and returned current stale references in the proposed target set. That verifies the timeout fix, but also confirms the audit is bounded to the listed paths.
- `AGENTS.md:51-60` requires session bootstrap and review material from `independent-progress-assessments/`; `AGENTS.md:70` makes that tree the report output location.
- `CLAUDE.md:200` lists `independent-progress-assessments/` as permitted Loyal Opposition reports/runbooks/logs, and `CLAUDE.md:216` says Loyal Opposition wrap-up defaults to that tree.
- `independent-progress-assessments/PROJECT-PROGRESS-DASHBOARD-RUNBOOK.md:3` says the dashboard pipeline reads the Knowledge DB, and `independent-progress-assessments/PROJECT-PROGRESS-DASHBOARD-RUNBOOK.md:8` instructs running `python independent-progress-assessments\tools\project_progress_snapshot.py`.
- `independent-progress-assessments/tools/project_progress_snapshot.py:28` still sets `KB_PATH = ROOT / "tools" / "knowledge-db" / "knowledge.db"`, and `independent-progress-assessments/tools/project_progress_snapshot.py:1632` exits with `Knowledge DB not found` if that path is absent.
- `independent-progress-assessments/export_specifications_csv.py:24` still sets `DEFAULT_DB_PATH = PROJECT_ROOT / "tools" / "knowledge-db" / "knowledge.db"`, `independent-progress-assessments/export_specifications_csv.py:101` raises `FileNotFoundError` when the DB is absent, and `independent-progress-assessments/export_specifications_csv.py:145` still documents `Path to knowledge.db`.
- `git check-ignore -v -- independent-progress-assessments/tools/project_progress_snapshot.py independent-progress-assessments/export_specifications_csv.py` reports `.gitignore:194:independent-progress-assessments/` for both paths. They are ignored, but they are present and operationally referenced.
- A targeted ignored-area audit found stale docs in locally present wiki copies, including `wiki/Specifications.md:4`, `wiki/Developer-Onboarding.md:104`, `agent-red.wiki/Specifications.md:4`, and `agent-red.wiki/Developer-Onboarding.md:104`.
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `Test-Path groundtruth.db` returned `True`, `Test-Path tools/knowledge-db` returned `False`, `src/groundtruth_kb/config.py:61-72` anchors relative `db_path`, `project_root`, and `chroma_path` to the config file directory, `tests/test_config.py:83-92` asserts this behavior, `src/groundtruth_kb/cli.py:645-647` passes `config.chroma_path` into `KnowledgeDB`, and `src/groundtruth_kb/db.py:3405-3410` falls back to `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is set.

## Findings

### P1 - Active Loyal Opposition KB tools are outside the migration and audit scope

The proposal lists active script, test, Claude tooling, and documentation updates, but it omits the active `independent-progress-assessments/` tools that read the Knowledge DB. The project instructions and dashboard runbook treat this tree as active operational surface, not merely historical archive. After `tools/knowledge-db/knowledge.db` is moved, both `project_progress_snapshot.py` and `export_specifications_csv.py` will default to a nonexistent path and raise hard errors.

Risk/impact: Prime can implement the migration, pass the proposed V7 audit, and still break local Loyal Opposition dashboard/export workflows. That violates the migration objective of removing nested-path fragility from active KB consumers.

Required revision:

1. Add `independent-progress-assessments/tools/project_progress_snapshot.py` and `independent-progress-assessments/export_specifications_csv.py` to the implementation scope, updating defaults and user-facing help text to root `groundtruth.db`.
2. Add a bounded audit target for active `independent-progress-assessments/` tooling/runbooks, while excluding generated logs, exported CSV snapshots, dashboard artifacts, and historical `CODEX-INSIGHT-DROPBOX/` reports.
3. Add post-implementation verification for at least:
   - `python independent-progress-assessments/tools/project_progress_snapshot.py --history-limit 1`
   - `python independent-progress-assessments/export_specifications_csv.py --latest-only --output <temporary output path>`
4. If Prime believes `independent-progress-assessments/` must remain out of implementation scope because it is Codex-owned or ignored, state that explicitly and request the owner decision before proceeding.

### P2 - Published wiki copies are omitted or need an explicit exclusion decision

The repository has locally present `wiki/` and `agent-red.wiki/` directories with stale KB path documentation. `CLAUDE.md:200` classifies wiki material as external-facing published docs, but version 011 only updates `docs/`, root docs, and selected specification scaffold files.

Risk/impact: user-facing or published documentation can continue directing operators to the retired `tools/knowledge-db/knowledge.db` path after the migration.

Required revision:

1. Either include `wiki/` and `agent-red.wiki/` KB path docs in the documentation update scope, or explicitly classify them as generated/ignored mirrors that are intentionally not updated by this migration.
2. If they are excluded, add a follow-up action for the source-of-truth publication path so stale external wiki docs do not linger indefinitely.

## Required Actions For Prime

Submit a revised proposal that:

1. Covers active ignored/local KB consumers under `independent-progress-assessments/`, especially the dashboard snapshot and specification CSV export tools.
2. Extends the bounded path audit so it cannot pass while those active local tools still point at `tools/knowledge-db/knowledge.db`.
3. Makes an explicit update-or-exclude decision for `wiki/` and `agent-red.wiki/` path documentation.
4. Keeps the corrected version 011 scope: root DB tracked, root Chroma ignored, backup relocation documented, active `.claude`/script/test/doc updates, bounded audit, Docker-aware `.dockerignore` verification, and semantic-search verification with pass count recorded.
