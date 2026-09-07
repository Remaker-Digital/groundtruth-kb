# GroundTruth-KB Platform Memory - Index

> MEMORY.md is the operational-notepad **INDEX**, not a content store or backlog
> authority. Canonical knowledge lives in MemBase (`groundtruth.db`); design
> reasoning lives in the Deliberation Archive (`gt deliberations`); per-session
> detail lives in git history (referenced commits) and `bridge/*-NNN.md`. The
> backlog authority is the MemBase `work_items` table via `gt backlog list`.
>
> Slice 8 of `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` (WI-4346/WI-4347) reduced
> this file from a ~109 KB session-state log to this index; the retired session
> ephemera remain recoverable in git history.

## Session Bootstrap
- Location: `E:\GT-KB`; key files: `CLAUDE.md`, this index.
- Role: resolved from `harness-state/harness-registry.json` (`gt harness roles`).
- Bridge: `gt bridge dispatch status` + status-bearing `bridge/*-NNN.md`.
- `bridge/` is gitignored ephemeral runtime state (WI-6530); bridge files are not git-tracked, so per-thread history comes from the numbered chain on disk, not `git log`.
- Backlog: `gt backlog list`. Recent-session detail: git history + `bridge/`.

## Quick Reference
- **Active branch:** `develop` (verify live with `git status`; dirty shared worktree)
- **Virtual env:** `E:\GT-KB\groundtruth-kb\.venv`
- **Test runner:** `python -m pytest platform_tests/`
- **CI / CD:** `npx playwright test`
- **Live web UI:** `localhost:8090`
- **CLI prefix:** `gt` / `python -m groundtruth_kb`
- **JSON-array CLI args** (`--related-bridge-threads`, `--depends-on-work-items`): invoke via `python -m groundtruth_kb.cli`; the `gt` shim mangles them intermittently (WI-6176 / WI-7616).
- **Registry:** `config/registry/sot-artifacts.toml` (`gt registry validate` / `gt registry sync`)

## Protected Files (DO NOT MODIFY)
- `.claude/settings.json`
- `.codex/hooks.json`

Do not record known0ephemeral information in this document, such as session notes, handoff notes, or other similar types of information. This document should be an entry point into the GT-KB memory document set structure: keep this document very concise and use it to clarify where tofind further details or elaboration on given subjects.

### Index Retention
- Keep this operational index at or below 12,000 UTF-8 bytes and every physical line at or below 240 characters.
- Fresh authority routes: backlog `gt backlog list`; bridge `gt bridge state-report`; deliberations `gt deliberations search`.
- After every edit run `python -m pytest platform_tests/scripts/test_slice8_memory_reconciliation.py platform_tests/scripts/test_memory_md_ceiling.py -q --tb=short`.
