---
name: Branching strategy
description: main=production mirror, develop=active development. Established S267.
type: project
---

Branching strategy established in S267 (2026-04-07):
- `main` = production mirror. Currently v1.98.89. Only updated via merge at deployment time.
- `develop` = continuous development. All work lands here.
- Old branch `codex/groundtruth-control-surface` was deleted after migration.

**Why:** The old feature branch had become the de facto mainline (68 commits ahead of main, including the production build). GitHub appeared stale because main hadn't been updated. Owner requested main reflect production.

**How to apply:** All sessions start on `develop`. Merge to `main` only as part of production deployment. Hotfixes branch from `main`, merge to both.
