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

- **019f765b-9cc2-7ae3-bfa1-fc2e2b6fca41** (2026-07-18/19, Codex A, PB): WI-5427 stale carrier WITHDRAWN v007; WI-5429 remains GO v006. No protected edit; reacquire its lapsed claim and regenerate the start packet before implementation.
- **6834c55b-a1b4-44de-98d1-8f49d316296c** (2026-07-18, Claude B, session-stated Prime Builder via `::init gtkb pb`): investigated LO GO/NO-GO verdict-write gate defect (implementation_start_gate.py/controlled_artifact_paths.py shadow lo-file-safety-gate.py's own new-verdict allow-list; surfaced during WI-5343 review); standing-backlog check found WI-5540 already captured it (separate LO session, hours earlier) -- filed proposal against WI-5540 rather than duplicating: bridge/gtkb-wi5540-lo-verdict-write-gate-shadow-repair-001 (NEW, both mandatory preflights clean); two adjacent follow-ons (missing GO/NO-GO verdict CLI; heredoc-source false-positive colliding with in-flight WI-5497) documented in-proposal, deliberately not split into new WIs; DA harvest blocked on GOV-ARTIFACT-APPROVAL-001 (no formal-approval packet for this session's content).
- **20dd407b-d159-4c05-9700-63511dadff11** (2026-07-18, Claude B, Prime Builder): WI-5412 stale-index review follow-up -> WI-5511 filed (restores dead WI-4837 git-add clearance, shadowed by WI-5138); WI-5501 corroborated; WI-5512 filed+escalated P1 (`gt session wrap` deletes role marker mid-session, breaks write authority; cross-ref WI-5328/5504/5505, same `::init`-persistence defect family); DELIB-202666775/776 captured.
- **0a04261d-f108-40de-bc61-475cc29c8162** (2026-07-18, Claude B, Prime Builder): WI-5370 sprawl reconciliation -- closed 4 missing-targets threads (wi5336/5335/5347/5348) WITHDRAWN on the target-superseded-by-live-thread pattern; classified the remaining 9 as correctly blocked on gtkb-wi5370-batched-archive-preserve-service (GO v002, unimplemented); attempted implementation and hit a GO author-provenance gap (missing `author_session_context_id`), NO-ACTION'd v003; found and backlogged two live governance defects -- `::init` role-persistence silent no-op (WI-5504: regex/fullmatch has no line-anchor, and the production hook runs under bare `pythonw` with a 5s timeout) and implementation-start-gate over-broad matching (WI-5505); independently reconfirmed WI-5370 resolution_status-resolved-while-open drift a 3rd time via wi5347's own NO-GO.
- **b4694d28-2640-45d9-8f63-bdb571b8fff8** (2026-07-17, Claude B, Prime Builder): verified wi5350 vs WI-5407 duplicate-bridge report; AUQ: withdraw citing WI-5407, owner reviews main-checkout sweep first; WI-5472/5473 filed.

### Index Retention

- Keep this operational index at or below 12,000 UTF-8 bytes and every physical line at or below 240 characters.
- Put full session narratives in a dated archive or governed session evidence; retain only five newest one-line hooks here.
- Fresh authority routes: backlog `gt backlog list`; bridge `gt bridge state-report`; deliberations `gt deliberations search`.
- After every edit run `python -m pytest platform_tests/scripts/test_slice8_memory_reconciliation.py platform_tests/scripts/test_memory_md_ceiling.py -q --tb=short`.
