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
- Backlog: `gt backlog list`. Recent-session detail: git history + `bridge/`.

## Quick Reference
- **Active branch:** `research` (verify live with `git status`; dirty shared worktree)
- **Virtual env:** `E:\GT-KB\groundtruth-kb\.venv`
- **Test runner:** `python -m pytest platform_tests/`
- **CI / CD:** `npx playwright test`
- **Live web UI:** `localhost:8090`
- **CLI prefix:** `gt` / `python -m groundtruth_kb`
- **Registry:** `config/registry/sot-artifacts.toml` (`gt registry validate` / `gt registry sync`)

## Protected Files (DO NOT MODIFY)
- `.claude/settings.json`
- `.codex/hooks.json`

## Recent Sessions

Full narratives captured through 2026-07-15 are preserved in [the dated session archive](archive/MEMORY-session-details-20260628-20260715.md).

- **8256b1c3-d3ed-4e04-bbbb-707ab38a742a** (2026-07-16, Claude B, Prime Builder): envelope grilling -> 7 owner decisions (DELIB-20260716-ENVELOPE-GRILL-B*); advisory gtkb-envelope-protocol-architecture-advisory-001 filed (adopt); WI-5372.
- **ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2** (2026-07-16, Claude B, Prime Builder): drove the WI-5320 dispatcher-starvation program; diagnosed WI-5328 (session envelope never persists `::init` role, falls back to durable/registry role) and WI-5330 (SPEC_LINK_HEADING_RE bare-hyphen false positive, a WI-4542 side effect) live across repeated reproductions; filed both plus a governance_advisory on the discovered `propose_bridge()` vs `write_bridge_file()` validation gap (the path that let missing project-linkage metadata through); both WI-5328/5330 NO-GO'd by an independent concurrent LO session for that same missing-metadata defect, not yet refiled.
- **019f6610-1bc5-7781-88bf-900dccbc6010** (2026-07-15, Codex A, Prime Builder): WI-5178 predecessor closure proposal reached GO; WI-5113 remains finalization-blocked by interleaved foreign test work.
- **019f65fb-4219-7150-ac09-26f12b650337** (2026-07-15, Codex A, Loyal Opposition): WI-5266 reached VERIFIED and commit `4eef2c30`; dispatcher black-box foundation reached GO.
- **019f5f66-9582-7f03-a3f1-3c75e6bd9d0a** (2026-07-14/15, Codex A, Prime Builder): dispatcher black-box and harness-budget advisories were captured as non-dispatchable bridge artifacts.

### Index Retention

- Keep this operational index at or below 12,000 UTF-8 bytes and every physical line at or below 240 characters.
- Put full session narratives in a dated archive or governed session evidence; retain only five newest one-line hooks here.
- Fresh authority routes: backlog `gt backlog list`; bridge `gt bridge state-report`; deliberations `gt deliberations search`.
- After every edit run `python -m pytest platform_tests/scripts/test_slice8_memory_reconciliation.py platform_tests/scripts/test_memory_md_ceiling.py -q --tb=short`.