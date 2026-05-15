# Implementation Proposal — Cross-Harness Trigger Diagnose Tool Bugfix

bridge_kind: prime_implementation_proposal

## Summary

Fix two defects in `scripts/cross_harness_bridge_trigger.py --diagnose`:

1. **Default state-dir mismatch.** `--diagnose` defaults to `<project_root>/.gtkb-state/cross-harness-trigger/` per `DEFAULT_STATE_SUBDIR`, but the live hook registrations in `.claude/settings.json` and `.codex/hooks.json` pass `--state-dir <project_root>/.gtkb-state/bridge-poller/` (the smart-poller-substrate path preserved by Slice 4 retirement comments). A maintainer running `python scripts/cross_harness_bridge_trigger.py --diagnose` with no flag sees stale state from a different path while live dispatch operates on the production path.
2. **Recipient-key drift in diagnose iteration.** `_emit_diagnose_summary` iterates `for name in ("codex", "prime")` (per the code at line 1155 region) — legacy keys retired by IP-3c migration in the same script. Live `dispatch-state.json` uses `"prime-builder"` and `"loyal-opposition"` keys after the first dispatch cycle. The diagnose per-recipient liveness section reports `(no state recorded)` for both even when the live state has recent entries.

Both bugs are diagnostic-surface only (no impact on dispatch correctness), but they make liveness reporting actively misleading.

## Background

Discovered in S350 (2026-05-14) while doing a baseline check during a Prime-worker-delivery review cycle. The diagnose output showed `DEGRADED: one or more recipients in an unrecognized state` and `Last update: 2026-05-12T15:39:42+00:00` despite live workers having dispatched and delivered bridge verdicts within the same session.

Direct inspection of `.gtkb-state/bridge-poller/dispatch-state.json` confirms the live path has recent state with `last_dispatched_signature` populated under the new keys.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py` — `_emit_diagnose_summary` recipient iteration + `main` state-dir resolution.
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger_diagnose.py` — regression tests.
- `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-state.json` and `E:\GT-KB\.gtkb-state\cross-harness-trigger\dispatch-state.json` — both candidate state files inspected by the upgraded resolution (in-root).

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge as canonical workflow state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — diagnose output is an operational artifact whose accuracy matters for governance hygiene (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved between diagnose output and live state (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — bug lifecycle: NEW → (GO/NO-GO) → VERIFIED (advisory).
- `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract — doctor check `_check_bridge_dispatch_liveness` consumes equivalent state; the diagnose tool should agree.
- `.claude/rules/file-bridge-protocol.md` — protocol invariants.
- `.claude/rules/codex-review-gate.md` — review gate.

## Prior Deliberations

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*` — Slice 4 retirement preserved the smart-poller state path; the diagnose default lagged.
- `bridge/gtkb-canonical-init-keyword-syntax-001-007.md` Codex GO at `-008` — IP-3c established the durable-role-label migration from `("prime", "codex")` to `("prime-builder", "loyal-opposition")`. The diagnose tool was not updated as part of that migration scope (likely overlooked because diagnose is read-only and the cosmetic gap wasn't blocking).
- No prior deliberation on diagnose-tool ergonomics surfaced.

## Owner Decisions / Input

Owner directive in S350 (2026-05-14): "Please continue" — interpreted as authorization to file noticed fix-worthy issues per the strategic self-improvement directive in `CLAUDE.md` ("Prime Builder ... capture noticed fix-worthy issues ... as review/consideration backlog items"). This is a clear-path protocol-hygiene fix (no scope ambiguity), so per `feedback_fix_problems_without_auq`, filing directly without additional AUQ.

## Requirement Sufficiency

Existing requirements sufficient. The diagnose tool's purpose is documented in its own docstring and in `.claude/rules/bridge-essential.md`; this proposal narrows defects within that purpose.

## target_paths

- `scripts/cross_harness_bridge_trigger.py` (`_emit_diagnose_summary` recipient iteration + default state-dir resolution in `main`)
- `platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py` (regression tests for both fixes)

## Implementation Plan

1. **State-dir resolution upgrade.** In `main`, when `args.state_dir is None` AND `args.diagnose is True`, probe both candidate paths and use the one whose `dispatch-state.json` is newer (by mtime). If neither exists, fall through to current default. Comment-document the choice.
2. **Recipient-key iteration upgrade.** In `_emit_diagnose_summary`, change `for name in ("codex", "prime")` to `for name in ("loyal-opposition", "prime-builder")`, matching the durable role labels used by `scripts/single_harness_bridge_dispatcher.py:610` (the single-harness dispatcher already iterates over durable role labels, per `bridge/gtkb-single-harness-bridge-dispatcher-001` Codex GO at `-014` IP-3c migration). Add a legacy fallback: if neither new key has state but legacy `"codex"` / `"prime"` keys do, report under both with a "(legacy key)" annotation so historical state remains visible during the transition window. Until this is fixed, automation cannot safely use diagnose output as a control signal — confirmed by owner directive in S350 (2026-05-14).
3. **Regression tests:**
   - `test_diagnose_default_state_dir_prefers_bridge_poller_when_newer`: stage both directories with files; assert diagnose reads the newer one.
   - `test_diagnose_default_state_dir_falls_through_when_neither_exists`: stage neither; assert diagnose uses the original default (no surprise behavior).
   - `test_diagnose_reads_durable_role_label_keys`: stage `dispatch-state.json` with `loyal-opposition` and `prime-builder` keys; assert diagnose reports both with their respective last_result values.
   - `test_diagnose_falls_back_to_legacy_keys_with_annotation`: stage `dispatch-state.json` with only legacy `codex` and `prime` keys; assert diagnose reports both with `(legacy key)` annotation.

## Spec-to-Test Mapping

- `GOV-FILE-BRIDGE-AUTHORITY-001` → all 4 tests (diagnose accurately reports on the live bridge dispatch state, the canonical workflow surface).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → spec-to-test mapping is one test per assertion class.

## Risks

- **Multiple state dirs with overlapping data could confuse maintainers**: if both `.gtkb-state/cross-harness-trigger/` and `.gtkb-state/bridge-poller/` have fresh data, the diagnose tool picking the newer one is ambiguous. *Mitigation:* the production hooks pass `--state-dir` explicitly to `.gtkb-state/bridge-poller/`; maintainers running without `--state-dir` get the newer-of-two heuristic; explicit `--state-dir` always overrides. A follow-on cleanup proposal can retire the unused directory once observability lands.
- **Legacy-key fallback complicates output**: dual key reporting is mildly more cluttered. *Mitigation:* the annotation `(legacy key)` is explicit; readers see exactly which keys are in play; cleanup happens on next migration pass.

## Rollback

Revert `_emit_diagnose_summary` recipient iteration and `main` state-dir resolution. Remove the 4 new tests.

## Verification Procedure

1. Run `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py -q --tb=short` — all existing + 4 new tests pass.
2. Run `python scripts/cross_harness_bridge_trigger.py --diagnose` against the live project. Output should show `Last update` matching the live `.gtkb-state/bridge-poller/dispatch-state.json`'s `updated_at`, and per-recipient sections for `loyal-opposition` and `prime-builder` with their actual `last_result` values.
3. Run preflights: applicability + clause must both pass.

## Acceptance Criteria

- Diagnose without `--state-dir` uses the newer of the two candidate state dirs.
- Diagnose reads durable-role-label keys with legacy-key fallback.
- 4 new regression tests pass.
- All preflights pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
