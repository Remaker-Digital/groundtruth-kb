---
author_identity: claude
author_harness_id: B
author_session_context_id: 28d30cb5-bfc4-4a97-acca-57d36d002533
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m
---

# Handoff — 2026-06-12 — WI-4472 dispatch concurrency cap awaiting Codex GO

Interactive Prime Builder, harness B, claude-opus-4-8[1m]. Branch `develop`.
Owner standing directive: proceed autonomously through the priority fixes +
backlog-triage program until each is VERIFIED; AUQ only genuine owner decisions.

## CLOSED this program (verify live INDEX, but these are terminal)

- **WI-4459** dispatch retry-delay livelock — VERIFIED@-004, committed `16be9eb50`, MemBase resolved.
- **WI-4461** Codex skill-adapter strict-YAML — VERIFIED@-004, committed `3281b07dd`, MemBase resolved.
- **Stage 2 / WI-4456** router-corpus disposition TOOL — VERIFIED@-007, committed `324a6bc06`.
  WI-4456 deliberately stays `backlogged/open`: the tool is done, but the per-batch
  owner-AUQ `--apply` disposal of the 749-item `retire_candidate_unapproved_noise`
  cohort is separate pending work (NOT a tool defect).
- **Stage 3 / WI-4469** advisory-router approval-staged intake (stop-the-leak) —
  VERIFIED@-004, committed `ff51a5a4e`, MemBase resolved. Implemented by the /loop
  session 544b584c after a two-session collision; this session yielded (owner AUQ)
  and verified clean (21/21 tests, ruff clean). The router now STAGES advisories to
  `.gtkb-state/advisory-candidates/candidates.jsonl`; `scripts/hygiene/advisory_candidate_promote.py`
  promotes under per-batch owner AUQ. Stage 3 `--apply` promotions are also separate
  pending owner-gated work.

## THE ONE LIVE THREAD: WI-4472 (cross-harness dispatch concurrency cap)

- Bridge `gtkb-cross-harness-dispatch-concurrency-cap` is at **REVISED@-003**
  (preflight-clean), **NOT yet GO**. `-002` was a single-finding NO-GO (missing
  fast-lane citation); `-003` added it.
- **BLOCKED ON CODEX GO.** Bridge protocol forbids implementing without GO. Codex
  (harness A) is parked ("standing by") so it has not auto-reviewed the REVISED.
  The REVISED is Loyal-Opposition-actionable; the cross-harness trigger should
  dispatch Codex on Stop, or the owner lets Codex process the bridge once.
- **Owner decision (DECISION-1147, resolved via AUQ):** THIS interactive Claude
  session (harness B) implements WI-4472 **solo** once Codex GOs, AFTER the owner
  stopped the other Prime sessions (Gemini/antigravity harness C; /loop 544b584c).
  Single-owner to avoid the Stage-3-style live-dispatch-path collision.
- **Implementation plan (on GO):**
  1. Re-verify the field is still clear: `scripts/cross_harness_bridge_trigger.py` and
     `platform_tests/scripts/test_dispatch_concurrency_cap.py` quiescent (no concurrent edits).
  2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-cross-harness-dispatch-concurrency-cap`.
  3. Implement in `scripts/cross_harness_bridge_trigger.py` `_spawn_harness`: a pid
     sidecar file per live dispatched process, `_pid_alive(pid)`, `_count_live_dispatched_processes()`,
     and a fail-closed cap gate keyed to env `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`
     (default 8) — refuse to spawn when at/over cap, with durable audit to
     `.gtkb-state/bridge-poller/dispatch-failures.jsonl`. (Confirm exact contract
     against `-001`/`-003` before coding.)
  4. New `platform_tests/scripts/test_dispatch_concurrency_cap.py`.
  5. Verify: new tests + `ruff check` + `ruff format --check`. The pre-existing
     `test_cross_harness_bridge_trigger.py` has ~16 KNOWN-UNRELATED flaky failures —
     do a `git stash` baseline diff to prove no NEW regression; do NOT try to fix
     those 16 (out of scope).
  6. File post-impl report (`## Specification Links`, `## Bridge Protocol Compliance`
     naming `bridge/INDEX.md`, Recommended Commit Type `fix`) → Codex VERIFY.
  - target_paths come from the GO'd `-001`/`-003`; do not expand at impl time.

## OPEN backlog (consideration only — not implementation-approved)

- **WI-4471** (defect, `PROJECT-GTKB-RELIABILITY-FIXES`): work-intent claim gates only
  bridge-FILE Writes, not source-file implementation → two Prime sessions can implement
  the same GO'd thread in parallel and corrupt each other (this is what hit Stage 3).
  Candidate fix: extend the claim/lock to cover an in-flight impl-start packet's target_paths.

## Live-environment hazards (carry forward)

- MANY concurrent sessions run in this environment (the `gtkb-fab-*` Fable program,
  /loop, antigravity/Gemini). The owner has been stopping sessions to clear the field
  for WI-4472. Ignore the `gtkb-fab-*` GO/NO-GO threads — separate program, other sessions.
- Heavy concurrent git activity → use `git commit -- <paths>` (`--only`) for scoped,
  collision-proof commits; retry on transient `index.lock`.
- Bridge filing via the helper (`propose_bridge_codex_non_bypass` / `revise_bridge.py`)
  with env `GTKB_BRIDGE_POLLER_RUN_ID` + `GTKB_HARNESS_NAME=claude` + 6 author-metadata
  fields incl. `author_model_version`. `gt`/DB work via the venv
  `groundtruth-kb/.venv/Scripts/python.exe` with `PYTHONPATH=groundtruth-kb/src`;
  canonical DB = root `groundtruth.db`. Scratch under `.gtkb-state/scratch/` (gitignored).
