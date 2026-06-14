NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T21-01-51Z-prime-builder-B-a34377
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m; headless bridge auto-dispatch (GTKB_BRIDGE_POLLER_RUN_ID set)

Project Authorization: PAUTH-PROJECT-GT-KB-INFRASTRUCTURE-WI-4564-STARTUP-SERVICE-TIMEOUT-ALIGNMENT-INNER-COST-A-C
Project: PROJECT-GT-KB-INFRASTRUCTURE
Work Item: WI-4564
target_paths: ["scripts/session_start_dispatch_core.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/scripts/test_session_self_initialization.py"]
bridge_kind: implementation_report

# Implementation Report — WI-4564: Startup-service timeout alignment + inner-cost reduction (A+C)

- **Bridge thread:** `gtkb-wi4564-startup-service-timeout-and-fanout`
- **Version:** 005
- **Status:** NEW (post-implementation report awaiting VERIFIED)
- **Bridge kind:** implementation_report
- **Work Item:** WI-4564
- **Project:** PROJECT-GT-KB-INFRASTRUCTURE
- **Author:** prime-builder / claude (Opus 4.8 [1m]), harness B, headless auto-dispatch `2026-06-14T21-01-51Z-prime-builder-B-a34377`
- **Implements:** `bridge/gtkb-wi4564-startup-service-timeout-and-fanout-003.md` (REVISED), GO at `-004`
- **Implementation-start packet:** `sha256:40157ec5591ba79029a98c82c6f7d2d73801950007e5a1f54963343be809bf89` (derived from live GO@-004; PAUTH active)

## Implementation Summary

The GO'd A+C scope is delivered across the four authorized `target_paths`. A material part of the GO'd scope was **already satisfied on entry** (one piece committed concurrently during this dispatch window, one pre-existing); this report records the actual delivered state honestly rather than re-deriving from the proposal's "current state" description, which had drifted from the working tree.

| GO'd scope item | Delivered state | Where |
|---|---|---|
| **Part A** — env-configurable, budget-aligned inner timeout (`GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS`, default raised 50.0→150.0, resolved via `_startup_service_timeout_seconds()` and used at the subprocess call site) | **Committed at HEAD `9f8e81ab3`** (committed by a concurrent sweep session during this dispatch window). Verified present in the working tree and exercised by new tests authored this session. | `scripts/session_start_dispatch_core.py:52-53,101-109,698` |
| **Part C1** — in-process backlog read (no child `python -m groundtruth_kb backlog list --json` interpreter) | **Pre-existing / committed.** `_backlog_items_from_membase` already calls `db.get_open_work_items()` in-process. Locked in by a new regression test this session. | `scripts/session_self_initialization.py:1223-1265` |
| **Part C2** — compute git `branch`/`HEAD`/`short-sha`/`last_commit` once and reuse | **Implemented this session.** `_git_metadata(cwd)` is a memoized helper (pre-existing); the one remaining un-deduped recompute on `project_root` — `_repo_state` — now reads from that cache, removing four duplicate git subprocesses per payload build. Behavior-preserving. | `scripts/session_self_initialization.py:3032-3050` |
| **Tests** — Part A resolver + Part C backlog/git-dedup | **Implemented this session.** New file for the dispatch-core resolver (9 tests); two new tests appended to the self-init suite. | both `platform_tests/scripts/test_*` |

### Part C2 detail (the substantive code change this session)

`_repo_state(project_root)` previously issued four fresh `git` subprocesses (`branch --show-current`, `rev-parse HEAD`, `rev-parse --short HEAD`, `log -1 …`) on `project_root`. Those exact values are already computed and cached by `_git_metadata(project_root)`, which `_git_drift` populates earlier in the same payload build. `_repo_state` now reads from `_git_metadata(project_root)`; the git commands are byte-identical, so the emitted payload values are unchanged while the cold-tree git invocation count drops by four. `_git_checkout_info` (arbitrary cross-checkout path, scope-guarded) is intentionally left unchanged — it is semantically distinct from the main-repo recompute and out of the proposal's stated dedup target.

## Specification Links

Carried forward from the GO'd proposal (-003):

- **GOV-RELIABILITY-FAST-LANE-001** — reliability defect-fix framing for the timeout bound correction (Part A).
- **GOV-SESSION-SELF-INITIALIZATION-001** — the startup self-initialization disclosure contract is preserved (degraded mode remains fallback, not norm).
- **DCL-SESSION-STARTUP-TOKEN-BUDGET-001** — Part C reduces per-startup subprocess cost (in-process backlog read; git-call dedup).
- **PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001** — the fix increases the probability the full (non-degraded) governance/role disclosure is delivered.
- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001** — fewer degraded events improve the freshness of the disclosed startup state without weakening live-read discipline.

Cross-cutting bridge-governance specs (always applicable):

- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file-bridge protocol; `bridge/INDEX.md` remains canonical; append-only audit trail preserved.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — all relevant governing specs cited.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the spec-to-test mapping below derives executed tests from the linked specifications.

Artifact-oriented governance specs (advisory): **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**, **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001**, **GOV-STANDING-BACKLOG-001**.

## Spec-to-Test Mapping (executed)

| Specification | Derived test | Result |
|---|---|---|
| GOV-RELIABILITY-FAST-LANE-001; PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001 | `test_session_start_dispatch_core.py::test_timeout_env_name_and_default_constant`, `…falls_back_to_default_when_unset`, `…reads_env_when_set`, `…reads_fractional_env`, `…invalid_value_falls_back`, `…blank_value_falls_back`, `…non_positive_falls_back[0/-5/-0.1]` (9 cases) — assert the resolver reads `GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS` and falls back to the 150.0 default when unset/invalid/non-positive. | PASS (9) |
| DCL-SESSION-STARTUP-TOKEN-BUDGET-001; GOV-SESSION-SELF-INITIALIZATION-001 | `test_session_self_initialization.py::test_backlog_fetch_is_in_process_no_child_interpreter` — asserts backlog items come from `db.get_open_work_items()` with no child `-m groundtruth_kb` interpreter, and the item shape is preserved. | PASS |
| DCL-SESSION-STARTUP-TOKEN-BUDGET-001 | `test_session_self_initialization.py::test_repo_state_reuses_git_metadata_cache` — asserts `_repo_state` adds zero new git subprocesses after `_git_metadata` populates the cache, and the returned shape is preserved. | PASS |
| GOV-SESSION-SELF-INITIALIZATION-001 (regression) | Existing emit-path tests `test_emit_startup_service_payload_returns_full_codex_session_start_contract`, `test_direct_script_execution_emits_startup_payload`, `test_emit_request_started_matches_env_var`, `test_emit_ignores_pre_populated_stale_payload_file` — valid non-degraded payload from the full emit path (isolated tmp dashboard dirs). | PASS |
| Code quality | `ruff check` AND `ruff format --check` on all four changed `.py` files (separate gates). | PASS / PASS |

## Verification Evidence (commands executed)

```text
python -m pytest platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_session_self_initialization.py -q
  => 79 passed in 64.86s

python -m ruff check scripts/session_start_dispatch_core.py scripts/session_self_initialization.py platform_tests/scripts/test_session_start_dispatch_core.py platform_tests/scripts/test_session_self_initialization.py
  => All checks passed!

python -m ruff format --check <same four files>
  => 4 files already formatted
```

Note on the manual full-emit invocation: a raw `python scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook` run is **correctly refused** by `GTKB-IMPLEMENTATION-START-GATE` because the emit path writes `docs/gtkb-dashboard/**` artifacts that are outside this proposal's `target_paths`. The non-degraded-payload regression is therefore covered by the suite's isolated-tmp-dir emit tests (listed above), not by mutating out-of-scope dashboard files.

## Files Changed

- `scripts/session_start_dispatch_core.py` — Part A (committed at HEAD `9f8e81ab3` by a concurrent session; +14/-2: env constant, 50→150 default, `_startup_service_timeout_seconds()` resolver, call-site rewire).
- `scripts/session_self_initialization.py` — Part C2 (`_repo_state` routed through `_git_metadata` cache; +12/-4). Uncommitted.
- `platform_tests/scripts/test_session_start_dispatch_core.py` — NEW (87 lines, 9 Part A tests). Uncommitted.
- `platform_tests/scripts/test_session_self_initialization.py` — +130 lines (2 Part C tests + raw loader). Uncommitted.

Per dispatched-worker discipline, the uncommitted changes are left for verification; no commit was made this session.

## Recommended Commit Type

`fix:` — corrects a reliability defect (premature inner-timeout cutoff) with an accompanying efficiency reduction (git-call dedup); no new capability surface. Matches the diff stat (two scripts + two test files; corrective net behavior).

## Owner Decisions / Input

This work depends on owner approval; the authorizing decision is durably recorded and unchanged from the GO'd proposal:

- **Durable owner decision:** `DELIB-20263378` (`source_type=owner_conversation`, "Owner decision: startup-service timeout fix scope (WI-4564, A+C)") — owner approved the A+C scope (env-configurable budget-aligned inner timeout + inner-cost reduction; Part B sync-exclusions already implemented, out of scope).
- **Bounded project authorization:** `PAUTH-PROJECT-GT-KB-INFRASTRUCTURE-WI-4564-STARTUP-SERVICE-TIMEOUT-ALIGNMENT-INNER-COST-A-C` — active; cites `DELIB-20263378`; includes `WI-4564`; allows mutation classes `source` and `test_addition`; forbids `deployment` and `sync_configuration_change`. All changes are within the authorized source/test scope.

No new owner decision is required: GO@-004 recorded "Owner Action Required: None," and the implementation stayed within the GO'd `target_paths`.

## Prior Deliberations

- `DELIB-20263378` — owner decision establishing the A+C scope (governing decision).
- Carried forward from -003: the cache-freshness cluster (`WI-3447`, `WI-3486`, `WI-3456`) is related-but-distinct (not superseded); prior measurement thread `gtkb-startup-payload-budget-report` (VERIFIED) established the cost baseline this fix targets.
- _No additional prior deliberations: the timeout-bound + git-dedup topic returned no further matches beyond the cluster above (novel corrective topic)._

## Preflight Evidence (-005)

Run after filing this version and updating `bridge/INDEX.md` so the preflights resolve the operative `-005` file. Actual results:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4564-startup-service-timeout-and-fanout`
  - `preflight_passed: true`; `operative_file: bridge/gtkb-wi4564-startup-service-timeout-and-fanout-005.md`; `missing_required_specs: []`; `missing_advisory_specs: []`; `packet_hash: sha256:3ff481346ee4fc2c21a5ed46de6c3a85115448c5ea9d64ce681e2c29bee93314`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4564-startup-service-timeout-and-fanout`
  - must_apply: 3, may_apply: 2, not_applicable: 0; Evidence gaps in must_apply clauses: 0; **Blocking gaps (gate-failing): 0**; exit 0.
- `python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-wi4564-startup-service-timeout-and-fanout`
  - No stale cross-thread citations detected.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
