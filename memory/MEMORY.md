# GroundTruth-KB Platform Memory - Index

> MEMORY.md is the operational-notepad **INDEX**, not a content store or backlog
> authority. Canonical knowledge lives in the native authority behind the `gt`
> CLI (PostgreSQL, sole record source under GOV-SOT-SINGLETON-001); per-session
> detail lives in git history (referenced commits) and interactive session logs.
> The backlog authority is the native work-item domain via `gt backlog list`.
>
> Slice 8 of `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` (WI-4346/WI-4347) reduced
> this file from a ~109 KB session-state log to this index; the retired session
> ephemera remain recoverable in git history.

## Session Bootstrap
- Location: `E:\GT-KB`; key files: `CLAUDE.md`, `.harness-baseline-configuration/AGENTS.md`, this index.
- Role: assigned only to the immutable native context by the exact supplied init marker and `gt session bind`; a harness, model or registry never assigns a role.
- Current state: `gt status` (fresh native reads; certifies no context); task requirements: `gt context work-item <WI-ID>`.
- Bridge: `gt bridge queue --role <pb|lo>` for the actionable queue, `gt bridge show <thread>` for messages, `gt bridge deliver` to file a response; bridge payloads are ephemeral and never git-tracked.
- Backlog: `gt backlog list`; formal records: `gt specs show <ID>`; deliberations are read-only history: `gt deliberations list|show`.

## Quick Reference
- **Active branch:** `develop` (verify live with `git status`; dirty shared worktree)
- **Virtual env:** `E:\GT-KB\groundtruth-kb\.venv`
- **Test runner:** `python -m pytest platform_tests/`
- **CI / CD:** `npx playwright test`
- **Live web UI:** `localhost:8090`
- **CLI prefix:** `gt` / `python -m groundtruth_kb`
- **JSON-array CLI args** (`--related-bridge-threads`, `--depends-on-work-items`): invoke via `python -m groundtruth_kb.cli`; the `gt` shim mangles them intermittently (WI-6176 / WI-7616).
- **Registry:** `config/registry/sot-artifacts.toml` (`gt registry validate` / `gt registry sync`)
- **Harness configuration:** derived from `.harness-baseline-configuration` by `gt harness project <harness>`; never edit a projected directory; `gt harness diagnostic <ID>` reads the installation record.

## Protected Files (DO NOT MODIFY)
- `.claude/settings.json`
- `.codex/hooks.json`

Do not record known-ephemeral information in this document, such as session notes, handoff notes, or other similar types of information. This document should be an entry point into the GT-KB memory document set structure: keep this document very concise and use it to clarify where to find further details or elaboration on given subjects.

### Index Retention
- Keep this operational index at or below 12,000 UTF-8 bytes and every physical line at or below 240 characters.
- Fresh authority routes: backlog `gt backlog list`; bridge `gt bridge queue` / `gt bridge show`; status `gt status`; deliberations `gt deliberations list`.
- After every edit run `python -m pytest platform_tests/scripts/test_slice8_memory_reconciliation.py platform_tests/scripts/test_memory_md_ceiling.py -q --tb=short`.
