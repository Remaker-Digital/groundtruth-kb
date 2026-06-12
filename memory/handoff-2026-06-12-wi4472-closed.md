---
author_identity: claude
author_harness_id: B
author_session_context_id: 625a52ea-e8ba-489a-8d61-97a8edab0b08
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
---

# Handoff — 2026-06-12 — WI-4472 CLOSED (dispatch concurrency cap) + dispatch-reliability backlog

Interactive Prime Builder, harness B, claude-opus-4-8[1m]. Branch `develop`.
Supersedes `handoff-2026-06-12-wi4472-awaiting-go.md` (stale).
Owner standing directive: proceed autonomously through priority fixes + backlog-triage
until each is VERIFIED; AUQ only genuine owner decisions.

## WI-4472 — CLOSED (verify live INDEX, but terminal)

- **VERIFIED** at `bridge/gtkb-cross-harness-dispatch-concurrency-cap-010.md` (Codex, harness A — independent verification). Full chain `-001..-010`.
- **Committed** `17c7672e4` on `develop` (9 files, path-scoped; the unrelated FAB-01 edit to `test_cross_harness_bridge_trigger.py` was deliberately excluded). All pre-commit gates passed (secrets / inventory-drift / ruff-format).
- **MemBase resolved** (GOV-15 owner-approved via AskUserQuestion): `resolution_status=resolved`, `stage=resolved`, status_detail "VERIFIED@-010; committed 17c7672e4".
- Implementation: `scripts/cross_harness_bridge_trigger.py` `_spawn_harness` hard global concurrency cap (env `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`, default 8) + pid-sidecar live-process accounting (`_pid_alive`, `_count_live_dispatched_processes`), fail-closed with `dispatch-failures.jsonl` audit. New `platform_tests/scripts/test_dispatch_concurrency_cap.py` (15 tests).
- **Provenance (for the record):** DECISION-1147 designated THIS session to implement solo, but in the multi-session storm Antigravity (harness C) raced ahead: authored `-003` (proposal), `-004` (self-GO), `-005` (impl). Owner AUQ "Accept + Codex verify" then "File accurate report" → I filed accurate report `-007`. Codex NO-GO'd `-007` at `-008` (the pre-existing B007). Antigravity fixed it at `-009` (`legacy_recipient`→`_legacy_recipient`). Codex VERIFIED `-009` at `-010`. The bridge protocol converged despite messy provenance — the independent-review guarantee held.

## New backlog captured this session (candidates — NOT implementation-approved)

- **WI-4478** (hygiene/P3) — pre-existing ruff B007. **RESOLVED**: the `-009` `_legacy_recipient` rename fixed it (committed in `17c7672e4`); Codex `-010` confirms "B007 no longer present."
- **WI-4479** (defect/P1) — headless Codex dispatch crashes on startup (exit `0xFFFFFFFF`; `[features].codex_hooks` deprecation). AXIS-1 auto-dispatch to Codex non-functional → every Codex action this session needed manual owner hand-off. Likely overlaps FAB-01 dispatch-substrate-revival.
- **WI-4480** (defect/P2) — cap-2 oldest-first dispatch selection starves newer threads (WI-4472's REVISED sat ~90 min behind stuck `gtkb-fab-22/23`).
- **WI-4481** (defect/P1) — `bridge/INDEX.md` Document blocks lost/duplicated under concurrent non-atomic writes; recurring manual owner repair (3 events this session). Bridge-integrity. Candidate fix: atomic INDEX writes behind a lock with read-modify-merge.

WI-4479/4480/4481 are the dispatch + bridge-integrity reliability cluster the multi-session storm exposed. WI-4479 is the upstream cause (broken dispatch → retries → INDEX contention + starvation).

## Open consideration item (carried forward, NOT approved)

- **WI-4471** (defect) — work-intent claim gates only bridge-FILE writes, not source implementation → two Prime sessions can co-implement one GO'd thread (the Stage-3 collision class; recurred here as Antigravity vs. this session). Candidate fix: extend the claim/lock to cover an in-flight impl-start packet's `target_paths`.

## Live-environment hazards (carry forward)

- MANY concurrent sessions (FAB Fable program `gtkb-fab-*`, `/loop`, Antigravity/Gemini harness C, ollama/openrouter LO harnesses). Ignore `gtkb-fab-*` threads unless the owner scopes them.
- **AXIS-1 auto-dispatch is effectively DOWN (WI-4479)** — Codex bridge actions require manual owner-directed runs (owner pastes `::init gtkb lo` + a focused single-thread task prompt; verify-prompt template is in this session's transcript).
- **`bridge/INDEX.md` corrupts under concurrency (WI-4481)** — always re-verify the live INDEX before trusting any block; repair duplicates/losses as bridge-integrity top priority (targeted fail-safe Edit).
- Heavy concurrent git → use `git add -- <paths>` then `git commit -o -- <paths> -m ...` for scoped commits; retry on `index.lock`.
- Bridge impl-report filing: `.claude/skills/bridge/helpers/impl_report_bridge.py file <slug> --content-file <draft>` (writes via `gtkb_bridge_writer`, bypasses the Write-tool compliance hook). Requires latest thread status GO; env `PYTHONPATH=groundtruth-kb/src` + `GTKB_HARNESS_NAME=claude`; include the full 6-field author block in the content (author_identity / harness_id / session_context_id / model / model_version / model_configuration).
- `gt`/DB via `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb ...` with `PYTHONPATH=groundtruth-kb/src` + `GTKB_HARNESS_NAME=claude` (changed_by resolution). Canonical DB = root `groundtruth.db`.
- `gt backlog resolve <WI>` requires `--owner-approved` for **defect/regression** WIs (GOV-15) — collect via AskUserQuestion first. Hygiene/new WIs resolve without it.
- Work-intent claim: `python scripts/bridge_claim_cli.py claim <slug>` (TTL 10 min; session-id resolves to `CLAUDE_CODE_SESSION_ID`).

## Next session

WI-4472 is done. The natural follow-on is the reliability cluster — WI-4479 (P1, upstream cause) → WI-4481 (P1) → WI-4480 (P2) → WI-4471 — but all need owner prioritization and the standard propose → GO → implement → VERIFIED path, and they overlap the FAB dispatch-substrate-revival program, so check for dedup/linkage first.
