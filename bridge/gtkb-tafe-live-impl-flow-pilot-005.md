NEW

bridge_kind: implementation_report
Document: gtkb-tafe-live-impl-flow-pilot
Version: 005
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T06-50-36Z-prime-builder-B-28c410
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code headless bridge auto-dispatch session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC
Responds to: bridge/gtkb-tafe-live-impl-flow-pilot-004.md (Loyal Opposition GO)

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-2-REFORMATION-IMPL-FLOW-PILOT
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4495
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py", "groundtruth-kb/tests/test_tafe_live_pilot.py"]
implementation_scope: source, test
Recommended commit type: feat:

# WI-4495 (re-cast) — Implementation Report: TAFE Live Implementation-Flow Pilot (module core; CLI deferred)

## Scope of This Report (honest partial delivery)

This report covers the **module + module-level test suite** half of the GO'd
proposal (`-003` REVISED, GO at `-004`). That is the substantive, independently
verifiable deliverable: the live, enforcing, parity-checking pilot module
(`tafe_live_pilot.py`) and its 23-test suite (`test_tafe_live_pilot.py`).

The proposal's third target path —
`groundtruth-kb/src/groundtruth_kb/cli.py` (`gt flow pilot <slug> [--stdout]`) —
**remains deferred**, exactly as the test suite's own `NOTE (partial-delivery
scope)` records (`test_tafe_live_pilot.py:29-37`). The original deferral reason
(`cli.py` contention with the then-pending `gtkb-tafe-slice-c-ingestion-consolidated`
thread) has changed but **not cleared**: `gtkb-tafe-slice-c-ingestion-consolidated`
is now terminal `VERIFIED`, but the live `cli.py` claimant role passed to the
pending `NEW` thread `gtkb-wi4521-backlog-update-source-spec-id` — see
§ Deferred Work below for the exact live contention.

The proposal's **Spec-Derived Verification Plan** (`-003` lines 308-322) tests
the module suite (`test_tafe_live_pilot.py`) and the consumed renderer suite
(`test_tafe_index_preview.py`); it does **not** include a CLI test target. The
verification gate for this report is therefore fully satisfiable on the module
deliverable, with the CLI tracked as an explicit follow-on.

## What This Session Changed

The module and its test suite were authored across sessions (the `-003` proposal
author, harness B session `896e79f0`, created both as untracked files). This
dispatched session (`2026-06-14T06-50-36Z-prime-builder-B-28c410`) completed the
deliverable by fixing a real defect and bringing the suite to green:

| File | Change | Detail |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py` | **Defect fix** - flow-event idempotence | `run_live_pilot` built a deterministic event id `FLOWEVENT-PILOT-{slug}-v{version}` but inserted unconditionally, so a same-version rerun raised `sqlite3.IntegrityError: UNIQUE constraint failed: flow_events.id`. Wrapped the insert in a `service.get_flow_event(event_id)` get-or-create guard, mirroring the existing flow-instance and stage-instance get-or-create patterns in the same module. |
| `groundtruth-kb/tests/test_tafe_live_pilot.py` | Lint hygiene | Removed an unused `ThreadStatus` import (ruff `F401`, autofixed). |

The defect was caught by the suite's own `test_run_live_pilot_is_idempotent_on_rerun`,
which failed pre-fix (`1 failed, 22 passed`) and passes post-fix (`23 passed`).
No behavior outside the idempotence path changed; the parity, enforcement,
never-self-review, and AST-no-canonical-write semantics are untouched.

## Deferred Work (CLI - `cli.py`)

The `gt flow pilot <slug> [--stdout]` command (`-003` Implementation Plan item 2)
is **not** delivered in this report. Rationale, with live evidence:

1. **`cli.py` is targeted by a concurrent unreviewed thread.** The pending `NEW`
   thread `gtkb-wi4521-backlog-update-source-spec-id` declares
   `target_paths` including `groundtruth-kb/src/groundtruth_kb/cli.py`
   (its `backlog_update` region ~`cli.py:2817`). Editing `cli.py` from this
   non-interactive dispatched session would re-introduce the exact
   concurrent-same-file contention the `-003` author deferred to avoid (the
   regions differ - `flow pilot` ~`cli.py:1314` vs `backlog_update` ~`cli.py:2817`
   - so a future textual merge is clean, but a dispatched worker cannot
   coordinate the edit ordering or the two threads' post-impl/commit sequencing).
2. **The `flow pilot` slot is governance-ready.** The current `cli.py:1314`
   `flow_pilot_cmd` is a Phase-0 no-op placeholder in the `flow` "command
   skeleton" group ("pilot activation requires later governed eligibility and
   approval"). This GO + the cited PAUTH +
   `DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613` **are** that governed
   eligibility - so the CLI is authorized; only the file-contention sequencing
   blocks it now.

**Clear-condition for the CLI follow-on:** once `gtkb-wi4521-backlog-update-source-spec-id`
reaches a terminal state (`VERIFIED`/`WITHDRAWN`) and no other live thread claims
`cli.py`, an interactive (coordinating) Prime Builder session completes the
deferred CLI command + its CLI tests + the CLI AST refusal-token guard under this
same GO, then files the next report version. The module deliverable in this report
does not depend on that follow-on.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - the live, enforcing, parallel-run
  half over the generic TAFE runtime; `bridge/INDEX.md` stays canonical. (Carried
  forward from `-003`.)
- `SPEC-TAFE-R1` (Controlled Artifact Routing) - ordered, role-gated stage
  sequence; the pilot drives + enforces it.
- `SPEC-TAFE-R7` (Interface Principle) - MemBase canonical; TAFE state mutated
  only through the public service API; `index_text` read-only injected.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the module writes nothing to `bridge/INDEX.md`
  (AST structural guard) and divergence resolves in the canonical index's favor.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each linked spec maps to
  executed evidence (table below).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH/project/WI/target
  metadata is in the header.
- `GOV-STANDING-BACKLOG-001` - WI-4495 (re-cast, terminal `resolved`) is the
  backlog authority of record; not reopened by this slice.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets are in-root under
  `E:\GT-KB`.

## Spec-to-Test Mapping

| Specification | Tests (in `test_tafe_live_pilot.py`) | Result |
|---|---|---|
| `SPEC-TAFE-R1` (ordered, role-gated routing) | `test_legal_transition_*`, `test_illegal_transition_*`, `test_enforcement_legal_drive_parity_match`, `test_enforcement_never_self_review_blocks_and_diverges`, `test_enforcement_role_violation_blocks`, `test_enforcement_full_sequence_to_complete`, `test_expected_stage_for_thread`, `test_bridge_status_to_stage_table_shape` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no canonical write; divergence favors canonical) | `test_pilot_module_has_no_canonical_write_surface` (AST guard: no `open`, no file-write attrs, no `subprocess`, no `bridge/INDEX.md` literal), `test_run_live_pilot_self_review_divergence` (records `canonical_wins=True`) | PASS |
| `SPEC-TAFE-R7` (public-API-only; read-only index) | `test_parse_index_thread_status_*`, `test_run_live_pilot_parity_match_records_verdict` (service-API flow/stage/event), `test_run_live_pilot_missing_thread_raises` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the whole suite; plus the idempotence regression `test_run_live_pilot_is_idempotent_on_rerun` exercising this session's fix | PASS |

## Verification Evidence (exact commands + observed results)

```text
$ groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_live_pilot.py -q --tb=short
23 passed in 2.39s

$ groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_index_preview.py -q --tb=short
12 passed in 2.07s    # consumed renderer (render_tafe_bridge_index_preview) remains green under the new caller

$ groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py groundtruth-kb/tests/test_tafe_live_pilot.py
All checks passed!

$ groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py groundtruth-kb/tests/test_tafe_live_pilot.py
2 files already formatted
```

Pre-fix baseline (for the record): `test_run_live_pilot_is_idempotent_on_rerun`
failed with `sqlite3.IntegrityError: UNIQUE constraint failed: flow_events.id`
(`1 failed, 22 passed`); post-fix `23 passed`.

**`bridge/INDEX.md` no-write note:** the proposal's `git status --short bridge/INDEX.md`
check is the proof that the *pilot* never writes the canonical index. The module
makes no such write (proven structurally by the passing AST guard, and no
`gt flow pilot` run was executed - the CLI is deferred). `bridge/INDEX.md` does
carry an unrelated working-tree modification that pre-existed this session (the
five other pending `NEW`/`REVISED` thread entries, present in the session-start
`git status` snapshot) plus this report's own append line; neither originates in
the pilot module.

## Owner Decisions / Input

This thread depends on owner approval already on record (no new AskUserQuestion
required to build or verify the module deliverable):

- `DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613` - owner pre-approval of this
  exact design (parallel/shadow drive + enforce + semantic parity via the
  WI-4507 renderer; `bridge/INDEX.md` canonical; no cutover).
- `DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613` - owner authorization for
  the implementation-flow pilot scope; the cited PAUTH's owner decision.
- WI-4495 lifecycle is owner-fixed terminal `resolved` (owner AUQ 2026-06-13,
  "Promote, keep WI-4495 resolved"); this slice performs no lifecycle change.

The deferred CLI follow-on requires **no new owner decision** - it is authorized
under this same GO/PAUTH; it is gated only by the live `cli.py` file contention
described in § Deferred Work, which an interactive session resolves by
sequencing, not by owner input.

## Recommended Commit Type

`feat:` - completes the live implementation-flow pilot **module** (new
`tafe_live_pilot.py` + new test suite) as a net-new capability surface; no
authority change, no cutover, no live dispatch substrate. (This dispatched worker
does not commit; the recommendation is for the eventual commit per the
Conventional Commits discipline.)

## Risk / Rollback

Low risk. The change is one get-or-create guard plus a lint autofix, both inside
already-untracked new files. Rollback is a single-commit revert of the new module
+ test. No KB mutation, no schema change, no `cli.py` edit, no `bridge/INDEX.md`
write by the module.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
