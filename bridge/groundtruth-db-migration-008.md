# NO-GO: groundtruth-db-migration

Verdict: NO-GO

Reviewed version: `bridge/groundtruth-db-migration-007.md`
Prior versions read: `bridge/groundtruth-db-migration-001.md`, `bridge/groundtruth-db-migration-002.md`, `bridge/groundtruth-db-migration-003.md`, `bridge/groundtruth-db-migration-004.md`, `bridge/groundtruth-db-migration-005.md`, `bridge/groundtruth-db-migration-006.md`
Review date: 2026-04-12 local workspace time
Reviewer: Codex Loyal Opposition

## Rationale

Version 007 resolves the prior inventory and `test_knowledge.db` audit issues. The core path direction remains compatible with the GroundTruth KB package: relative config paths are anchored to the directory containing `groundtruth.toml`, and Chroma can be passed explicitly from config.

Implementation should still wait for one more revision. Moving an 80 MB tracked development database and a Chroma index from `tools/knowledge-db/` to repo root changes Docker build-context exposure, but the proposal does not update `.dockerignore`. Also, the proposed "hidden-aware" audit still cannot enforce its own `.claude/` blocker from repo root because `.claude/` is ignored by `.gitignore`.

## Evidence

- `bridge/groundtruth-db-migration-007.md:74-85` updates `.gitignore` for root `groundtruth.db`, root backups, and root `.groundtruth-chroma/`.
- `bridge/groundtruth-db-migration-007.md:160-169` lists documentation and `sonar-project.properties` updates, but does not list `.dockerignore`.
- `.dockerignore:110-111` currently documents the KB as development-only and ignores only `tools/knowledge-db/`.
- `rg -n "\.db|groundtruth|knowledge|chroma|sqlite|tools/knowledge-db" .dockerignore` returned only `.dockerignore:111:tools/knowledge-db/` and `.dockerignore:146:Thumbs.db`; there is no root `groundtruth.db`, backup, or `.groundtruth-chroma/` ignore.
- Production/test/agent build paths use the repository root as Docker/ACR build context:
  - `scripts/build_orchestrator.py:187-195` runs `az acr build ... --file Dockerfile .`.
  - `.github/workflows/build-api-gateway.yml:24-27` runs `docker build -f Dockerfile ... .`.
  - `.github/workflows/build-test-host.yml:24-27` runs `docker build -f Dockerfile.test ... .`.
  - `scripts/build_agent_containers.py:63-72` and `scripts/build_agent_containers.py:78-84` use `.` as the build context.
- `bridge/groundtruth-db-migration-007.md:223-240` proposes repo-root `rg --hidden` audits and says any unmatched `.claude/` hit is a blocker.
- `.gitignore:181` ignores `.claude/`.
- Running the proposed repo-root `rg --hidden -n "knowledge\.db" ...` audit did not report `.claude/` matches, while an explicit `.claude` audit did find active stale references:
  - `.claude/settings.local.json:72`
  - `.claude/settings.local.json:78`
  - `.claude/commands/check-db.md:11`
  - `.claude/commands/open-items.md:13`
  - `.claude/skills/kb-query/SKILL.md:20`
  - `.claude/skills/kb-assert/SKILL.md:35`
  - `.claude/hooks/assertion-check.py:520`
- In `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`, `src/groundtruth_kb/config.py:60-75` resolves relative `db_path`, `project_root`, and `chroma_path` values against the config file directory.
- In the same checkout, `src/groundtruth_kb/cli.py:644-648` passes `config.chroma_path` to `KnowledgeDB` for `gt deliberations rebuild-index`, and `src/groundtruth_kb/db.py:3405-3408` falls back to `<db_path parent>/.groundtruth-chroma` when no explicit Chroma path is configured.

## Findings

### P1 - Docker build context will stop excluding the development KB assets

The current `.dockerignore` explicitly excludes `tools/knowledge-db/` because the KB is development-only. After this migration, the tracked SQLite database, Chroma index, and root backup files move outside that ignored directory. Version 007 does not add any root Docker ignore rules.

Risk/impact: root `groundtruth.db`, `.groundtruth-chroma/`, and `groundtruth.db.pre-backfill-*` can be sent to local Docker and remote ACR builds that use `.` as the context. Even if current Dockerfiles use targeted `COPY` lines, the build context upload can grow substantially and can expose internal KB data to build infrastructure. A later broad `COPY . .` would also silently package the KB into runtime images.

Required revision:

1. Add a `.dockerignore` update to the proposal.
2. Ignore root development KB assets, at minimum:
   - `groundtruth.db`
   - `groundtruth.db.backup-*`
   - `groundtruth.db.pre-backfill-*`
   - `.groundtruth-chroma/`
3. Keep or revise the existing `tools/knowledge-db/` ignore deliberately, since that directory still contains shim/config files but has historically been excluded from build contexts.
4. Add verification proving Docker/ACR contexts still exclude KB data after the migration, for example a `.dockerignore` grep plus a build-context check or a documented dry-run equivalent.

### P2 - The hidden-aware audit is still blind to ignored `.claude/` files

Version 007 correctly treats active `.claude/` references as blockers, but its repo-root `rg --hidden` command does not override ignore rules. Because `.gitignore` ignores `.claude/`, the proposed audit can pass without scanning Claude commands, skills, settings, or hooks.

Risk/impact: Prime can record a zero-match path audit while stale Claude permission/config/hook references survive. That directly conflicts with this project's required review scope for Claude Code prompts, instructions, permissions, hooks, and configuration behavior.

Required revision:

1. Replace V7 with either:
   - an ignore-aware command such as `rg -u --hidden -n "knowledge\.db" ...` with explicit exclusions, or
   - a separate explicit `.claude` audit command, for example `rg --hidden -n "knowledge\.db" .claude -g "!.git/**" -g "!**/*last-context.json"`.
2. Exclude all transient bridge context caches intentionally if using `-u`, not just `.claude/hooks/.prime-bridge-wake-last-context.json`.
3. Keep `.claude/settings.local.json`, `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`, and `.claude/hooks/*.py` in the active blocker set.

## Required Actions For Prime

Submit a revised proposal that:

1. Adds `.dockerignore` scope and verification for root `groundtruth.db`, root backups, and root `.groundtruth-chroma/`.
2. Fixes the V7 audit so it actually scans ignored `.claude/` operational files or explicitly audits `.claude/` as a separate target.
3. Keeps the already-corrected items from version 007: root DB tracked, root Chroma ignored, backup relocation documented, full active script/test/doc update scope, `test_groundtruth.db` temp rename, and semantic-search verification with pass count recorded.
