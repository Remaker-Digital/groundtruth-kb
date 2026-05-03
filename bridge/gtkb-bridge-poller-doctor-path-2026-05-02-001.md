NEW

# Implementation Proposal — Smart-Poller Doctor-Path Fix

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Subject: Redirect `_check_bridge_poller` to read smart-poller state from its current output path; fix schema fields; add BOM-tolerant decode; reconcile rule-text drift in `.claude/rules/bridge-essential.md`.

## Context

Owner directive 2026-05-02: "The smart-poller must be restored to full function." Live state probe (this session, 2026-05-02 06:05 UTC) shows the smart poller is running healthily — `wscript.exe` + `pythonw.exe bridge_poller_runner.py --interval 15`, single-instance lock at `.gtkb-state/bridge-poller/bridge-poller-runner.lock`, audit log writing every ~15s (4,030 iterations × 15s ≈ 16.8h uptime since `2026-05-01T13:15:11Z` run-id), `dispatch-state.json` updated 2026-05-02T06:05:19+00:00.

Doctor output for the live system reports two contradictory results in the same run:

- **PASS:** `smart-poller active (task 'GTKB-SmartBridgePoller', VBS daemon → runner verified, PS1 helper → runner verified, audit event 8s old)` — the activation-chain check sees the live smart poller.
- **FAIL:** `claude bridge status file unreadable: Unexpected UTF-8 BOM` and the same for codex — the per-agent freshness check is reading retired/legacy state files written by the now-removed OS pollers (S308 halt, 2026-04-25). Those legacy files have a BOM; the smart-poller does not write to those paths at all.

The two checks are not both wrong about the system; they are right about *different* surfaces. The activation check is current. The per-agent check has stale path constants.

## Specification Links

1. **`.claude/rules/bridge-essential.md` §"Poller Enablement Contract"** — condition 3 ("`gt platform doctor` or an equivalent verification command reports the smart poller infrastructure healthy"). The doctor's per-agent freshness check is the mechanical predicate for this condition; today it FAILs against a healthy poller because of stale paths.
2. **`.claude/rules/bridge-essential.md` §"Operational Mode"** — current text says "Until the smart poller is available and functioning, bridge scans remain manual in both directions." Live state contradicts this. Reconciliation is in scope.
3. **Umbrella bridge** `bridge/gtkb-bridge-poller-001-smart-poller-007.md` GO — the smart-poller program. This proposal is a follow-on cleanup, not a new sub-track. Cited as the program parent; no new umbrella scope is added.
4. **Activation bridge** `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md` GO — the thread that activated the smart poller end-to-end. Doctor's `_BRIDGE_STATUS_PATHS` constants at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1127–1130` were never migrated as part of this activation; the proposal closes that gap.
5. **`GOV-19` Outside-in testing** — tests exercise `_check_bridge_poller` against fixtures that mirror the live `dispatch-state.json` schema, not the function's internals.
6. **`GOV-20` Architecture decisions** — the change is small enough to skip ADR/DCL, but ships an IPR + CVR pair to record (a) the path/schema redirection rationale and (b) post-impl proof of doctor-PASS against the live poller.
7. **Probed source-of-truth schemas** (live, this session):
   - `.gtkb-state/bridge-poller/dispatch-state.json` schema_version 1: top-level `recipients.{prime,codex}` with fields `updated_at` (ISO8601 with timezone), `last_result` ∈ {`unchanged`, `no_pending`, dispatch-result-string}, `pending_count`, `raw_pending_count`, `filtered_terminal_count`, `signature`.
   - `.gtkb-state/bridge-poller/notifications/pending-bridge-action-{prime,codex}.json` schema_version 3: `recipient`, `written_at`, `poller_run_id`, `pending_actions` (list with `document_name`, `top_status`, `top_file`, `index_line_number`, `dispatchable`, `classification`).
8. **Prior Deliberations search:** running `python -m groundtruth_kb deliberations search --query "smart poller doctor health check"` returned no rows in this environment. Active prior context is the umbrella thread `-007` and activation `-004` cited above.

## Scope

### In-scope

Files modified:
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — replace `_BRIDGE_STATUS_PATHS` (lines 1127–1130) with a single `_BRIDGE_DISPATCH_STATE_PATH` constant pointing at `.gtkb-state/bridge-poller/dispatch-state.json`. Modify `_check_bridge_poller(target, agent)` (lines 1156–1266) to (a) read the single dispatch-state file, (b) map `agent` argument values "claude"→"prime" and "codex"→"codex" (one-line dict lookup), (c) read `recipients[role].updated_at` instead of top-level `updatedAtUtc`, (d) derive `state_display` from `last_result` and `pending_count`, (e) decode with `utf-8-sig` for forward-compatibility against future BOM introduction (the smart poller does not BOM today; defensive only), (f) preserve all three age thresholds and result statuses unchanged. Touch is confined to the bridge smart-poller liveness block (lines 1125–1266).
- `.claude/rules/bridge-essential.md` — update §"Operational Mode" text to acknowledge that the smart poller is now active and that automated dispatch is occurring; preserve the existing §"Poller Enablement Contract" wording; add a one-line pointer that the doctor health check is the canonical predicate.
- Existing test under `groundtruth-kb/tests/` covering `_check_bridge_poller` — probed during implementation; will be updated to use the new path/schema. (Probe pending — list to be reported in post-impl. If no test exists today, a new test file is added under `groundtruth-kb/tests/test_doctor_bridge_poller.py`.)

Files created (new):
- `groundtruth-kb/tests/test_doctor_bridge_poller.py` (only if no existing test covers `_check_bridge_poller` — probe will resolve at implementation start).

Documents (per GOV-20):
- `IPR-BRIDGE-POLLER-DOCTOR-PATH-001` — pre-implementation review citing the schema migration rationale and the rule-text reconciliation.
- `CVR-BRIDGE-POLLER-DOCTOR-PATH-001` — post-impl proof: doctor reports per-agent PASS against the live poller; bridge-essential.md text reflects current state; tests pass.

### Out-of-scope (deferred to other threads)

- Row 22 GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT (Prime auto-spawn false positives for plan-level/umbrella GOs).
- Row 23 GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR (broader simplification, trigger-conditional).
- The umbrella's P3 invoker design and P7-P8 Agent-Red adopter follow-up tracks.
- Any of the other doctor-flagged failures (DA harvest 0/6 coverage, missing hooks, `canonical-terminology.toml`, `scanner-safe-writer.py`, product-scope writability, `work_list.md` heuristic flags, deprecated `workstream-focus.py`). These are separate items; this thread is doctor-path-only.
- Adding new dispatch-stalled checks or per-agent notification checks (feature additions). This thread fixes the existing check; it does not add new checks.

## Implementation Plan

1. Probe `_BRIDGE_STATUS_PATHS` callers across `groundtruth-kb/` (grep) — should be zero callers outside `_check_bridge_poller` itself; reported in post-impl.
2. Probe existing tests for `_check_bridge_poller` — exact test files reported in post-impl.
3. Replace constants:
   ```python
   _BRIDGE_DISPATCH_STATE_PATH = Path(".gtkb-state/bridge-poller/dispatch-state.json")
   _BRIDGE_AGENT_TO_RECIPIENT = {"claude": "prime", "codex": "codex"}
   ```
4. Rewrite `_check_bridge_poller` body to read the single state file once, navigate `recipients[role]`, parse `updated_at`, compute `age_secs`, return per-agent `ToolCheck` with the same fresh/warn/alarm thresholds. Use `path.read_bytes().decode("utf-8-sig")` to be BOM-tolerant.
5. Update message strings to reference `last_result` (e.g., "state: unchanged, pending: 21").
6. Update tests (or add new test file) covering: missing state file, BOM-prefixed valid JSON, missing `recipients` key, missing `recipients[role]`, missing `updated_at`, fresh/warn/alarm time bands, and the agent-name mapping.
7. Reconcile `.claude/rules/bridge-essential.md` §"Operational Mode" — minimal text edit acknowledging the smart-poller is active and the doctor predicate is canonical.
8. File IPR-BRIDGE-POLLER-DOCTOR-PATH-001 (pre-implementation) and CVR-BRIDGE-POLLER-DOCTOR-PATH-001 (post-implementation) per GOV-20 advisory pilot.
9. Run `python -m groundtruth_kb project doctor` to confirm the per-agent checks now report PASS against the live poller; capture the output in the post-impl report.

## Test Plan (spec-to-test mapping)

| # | Test | Spec / behavior covered | Surface exercised |
|---|---|---|---|
| T1 | `test_check_bridge_poller_returns_pass_when_fresh` | `bridge-essential.md` §"Poller Enablement Contract" condition 3 | `_check_bridge_poller("claude")` returns `status="pass"` against fixture with `recipients.prime.updated_at` set to now |
| T2 | `test_check_bridge_poller_returns_warning_when_4_to_10_min_old` | `_BRIDGE_FRESH_SECS` boundary | fixture with `updated_at` 5 minutes ago → `status="warning"` |
| T3 | `test_check_bridge_poller_returns_fail_when_over_10_min_old` | `_BRIDGE_WARN_SECS` boundary | fixture with `updated_at` 15 minutes ago → `status="fail"` |
| T4 | `test_check_bridge_poller_returns_warning_when_state_file_absent` | not-started semantics | empty target dir → `status="warning"`, message references `_BRIDGE_SCHEDULER_DOC` |
| T5 | `test_check_bridge_poller_handles_utf8_bom_gracefully` | defensive forward-compat per `bridge-essential.md` lessons | fixture with `﻿` prefix parses cleanly |
| T6 | `test_check_bridge_poller_returns_fail_when_recipients_key_missing` | schema-validation behavior | fixture missing `recipients` → `status="fail"` |
| T7 | `test_check_bridge_poller_returns_fail_when_role_missing` | schema-validation behavior | fixture with `recipients` but no `prime` key → `status="fail"` |
| T8 | `test_check_bridge_poller_maps_agent_to_recipient` | name-mapping correctness | calling with `agent="claude"` reads `recipients["prime"]`; `agent="codex"` reads `recipients["codex"]` |
| T9 | `test_check_bridge_poller_message_includes_pending_count` | observability — surface live `pending_count` | fixture with `pending_count=21` produces message containing "pending: 21" |

Existing scaffold/upgrade tests remain unchanged; the constant rename (if any callers exist outside doctor.py) will be reported in post-impl with adjusted call sites in the same commit.

## Verification Commands

The post-implementation report will include exact commands and observed output:

- `python -m groundtruth_kb project doctor 2>&1 | grep -E "bridge poller|smart-poller"` — confirm per-agent PASS against the live poller.
- `uv run pytest groundtruth-kb/tests/test_doctor_bridge_poller.py -v` (or the existing test file path if probe identifies one).
- `uv run pytest groundtruth-kb/tests/test_doctor_*.py -v` — regression sweep across all doctor tests.
- `uv run ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_bridge_poller.py`.

## Risk and Rollback

- **Risk: schema drift between proposal time and implementation.** `dispatch-state.json` `schema_version: 1` and `pending-bridge-action-*.json` `schema_version: 3` are stable today; if the smart-poller bumps schema_version between proposal and impl, the implementation must read the bumped fields. Mitigation: implementation re-probes the live schema as the first step; reports any drift in post-impl.
- **Risk: legacy paths still referenced elsewhere.** Doctor's constants may be the only callers, but other tooling (e.g., dashboard, scripts) might read the legacy paths too. Mitigation: implementation greps for `claude-scan-status` / `codex-scan-status` repo-wide; reports findings; either updates them in the same commit or files them as separate items.
- **Rollback:** revert the implementation commit; `_BRIDGE_STATUS_PATHS` and the original schema reads return. Doctor's per-agent check resumes its current FAIL behavior; smart poller is unaffected. No DB schema changes; no bridge-protocol-level dependencies.

## Acceptance Criteria

A post-implementation report shall be filed when ALL of the following hold:
- Doctor reports per-agent `bridge poller: OK` for both `claude` and `codex` against the live smart-poller.
- T1–T9 pass under `uv run pytest`.
- Existing doctor tests still pass.
- Ruff clean on modified and new files.
- IPR-BRIDGE-POLLER-DOCTOR-PATH-001 and CVR-BRIDGE-POLLER-DOCTOR-PATH-001 inserted via the formal-artifact-approval gate.
- `.claude/rules/bridge-essential.md` §"Operational Mode" reconciled to current state with no other text changes.

## Open Items (probed during implementation; reported in post-impl)

- Exact existing test file(s) covering `_check_bridge_poller` (probe is one grep call; deferred to keep this proposal terse).
- Any non-doctor callers of `_BRIDGE_STATUS_PATHS` legacy paths (probe is one grep; deferred).
- Whether the smart-poller's `dispatch-state.json` schema_version 1 has a bump in flight (probe at implementation start).

## Deliberation Capture

Per `.claude/rules/deliberation-protocol.md`: this proposal is the substantive design record for the doctor-path fix. The IPR/CVR pair captures the schema migration. No pre-implementation owner decisions are required; the design follows directly from the live smart-poller's existing schema.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
