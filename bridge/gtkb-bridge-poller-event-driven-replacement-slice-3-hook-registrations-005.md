NEW

# Implementation Report — Bridge Poller Event-Driven Replacement Slice 3 (Hook Registrations)

bridge_kind: post_implementation_report
Document: gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
Version: 005 (NEW post-implementation report against GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Implements: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md` (REVISED-1, Codex GO at `-004`)

## Claim

Slice 3 hook registrations are implemented within the host-checkout scope authorized by Codex GO at `-004`. The cross-harness bridge trigger script is now invoked by:

- **Claude PostToolUse**: Bash matcher and Write|Edit matcher (separate entries) — silent default invocation.
- **Claude Stop**: third entry alongside existing wrap-up + owner-decision-tracker entries — invokes trigger with `--stop-hook` for valid Stop-event JSON output.
- **Codex PostToolUse**: Bash matcher and apply_patch matcher (separate entries; Codex requires per-tool matcher rather than regex) — silent default invocation.
- **Codex Stop**: matcher-less entry (Codex Stop matchers not supported per OpenAI docs) — invokes trigger with `--stop-hook`.

All registrations point at `.gtkb-state/bridge-poller/` (the smart-poller's existing dispatch-state path) per Option A overlap coordination.

The smart-poller continues running as the canonical bridge automation path until Slice 4 retires it. During the overlap window, both mechanisms see the same dispatch-state file and dedup against the byte-identical signature scheme.

## Prior Deliberations

Carried forward from `-003`:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical foundation.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551) — Slice 1 supersession.
- `DELIB-0836` (rowid 844) — superseded predecessor.
- Parent `bridge/gtkb-bridge-poller-event-driven-replacement-010.md` — VERIFIED Slice 1 + Slice 2.
- This thread `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-002.md` — prior NO-GO with F1+F2 findings; addressed in `-003`.
- This thread `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-004.md` — Codex GO authorizing this implementation.

## Specification Links

(Carried forward from `-003`.)

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved; live INDEX block below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — observed spec-derived verification table below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`: `.claude/settings.json`, `.codex/hooks.json`, `scripts/cross_harness_bridge_trigger.py`, `tests/scripts/test_cross_harness_bridge_trigger.py`, `tests/scripts/test_codex_hook_parity.py`, `tests/scripts/test_slice_3_hook_registrations.py`.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Domain-specific:**

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (rowid 8463) — Slice 3 is the first slice to rely on Codex hooks firing as live operational infrastructure on Windows. Empirical confirmation from `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST` is now exercised live.
- `scripts/cross_harness_bridge_trigger.py` — extended with `--stop-hook` flag.
- OpenAI Codex hooks documentation: https://developers.openai.com/codex/hooks — Stop event JSON stdout contract; `{}` is a valid conservative payload (confirmed by Codex `-004`).

## Owner Decisions / Input

Carried forward from `-003`. No new owner-decision dependence introduced by this implementation. Slice 3 implements within the GO'd scope authorized by Codex `-004` and the parent thread's owner directives.

## Bridge INDEX-as-canonical-state Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, the live `bridge/INDEX.md` working-tree block for this thread at filing time of `-005`:

```
Document: gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
NEW: bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-005.md
GO: bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-004.md
REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-003.md
NO-GO: bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-002.md
NEW: bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md
```

Audit chain monotonic and append-only.

## Implementation Detail

### `--stop-hook` flag (script extension)

`scripts/cross_harness_bridge_trigger.py` now accepts `--stop-hook`:

- Runs `run_trigger(...)` exactly as default invocation (read live INDEX, compute selected-batch signature, dispatch on change, write dispatch-state).
- Emits exactly `{}` followed by newline to stdout (parseable JSON object; minimal valid Codex Stop payload).
- Exits 0 (fire-and-forget contract preserved).
- Mutually exclusive with `--verbose`: when both are passed, `--stop-hook` wins so the JSON contract isn't violated by extra summary text.

The flag's argparse help text documents the contract for future operators. Module docstring + `_spawn_harness` docstring updated.

### Hook registrations

**`.claude/settings.json` deltas** (3 new hook entries):

| Event | Matcher | Command (relevant suffix) |
|---|---|---|
| PostToolUse | `Bash` | `cross_harness_bridge_trigger.py --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` |
| PostToolUse | `Write\|Edit` | (same as Bash; separate matcher entry) |
| Stop | (none — appended to existing Stop group) | `... --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller" --stop-hook` |

Existing PostToolUse `spec-event-surfacer.py` and Stop entries (wrap-up + owner-decision-tracker) are preserved.

**`.codex/hooks.json` deltas** (3 new hook entries):

| Event | Matcher | Command |
|---|---|---|
| PostToolUse | `Bash` | `python E:\GT-KB\scripts\cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller` |
| PostToolUse | `apply_patch` | (same as Bash; separate matcher entry) |
| Stop | (none — Codex Stop matchers unsupported) | `python E:\GT-KB\scripts\cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller --stop-hook` |

Existing Codex hook entries unchanged.

### Test changes

- `tests/scripts/test_cross_harness_bridge_trigger.py`: added 6 new tests (T-3-stop-hook-output-contract pair, bounded reconciliation, fail-soft reconciliation, --verbose override, overlap-state-shared). Total: 18 tests (was 12).
- `tests/scripts/test_codex_hook_parity.py`: replaced `assert "Stop" not in codex_hooks["hooks"]` (line 77) with a Stop-presence assertion scoped to the cross-harness trigger. Preserves the existing ban on Codex lifecycle-wrap-up Stop registration (`session_wrapup` / `session_self_initialization.py` patterns are explicitly forbidden from Codex Stop). Total: 8 tests (count unchanged; one assertion flipped + 3 added under the same test).
- `tests/scripts/test_slice_3_hook_registrations.py` (NEW, 8 tests): T-3-claude-registration (Bash + Write|Edit + Stop), T-3-codex-registration (Bash + apply_patch + Stop matcher-less + Stop --stop-hook), and a cross-harness shared-path assertion that pins Option A overlap coordination at the configuration level.

## Specification-Derived Verification (observed)

| Verification | Spec/Requirement | Observed result |
|---|---|---|
| `--stop-hook` JSON output contract | F2 fix per Codex `-002`/`-004` | `python scripts/cross_harness_bridge_trigger.py --state-dir "E:\GT-KB\.gtkb-state\bridge-poller" --stop-hook --dry-run` produced **exactly** `{}\n` on stdout, exit 0 (live smoke against real repo INDEX). Test `test_stop_hook_emits_exactly_braces_json` asserts exact `{}\n` stdout + JSON-parseable. |
| `--stop-hook` overrides `--verbose` | F2 contract preservation | Test `test_stop_hook_overrides_verbose` passes. |
| Stop reconciliation bounded by signature dedup | Slice 3 §C3 | Test `test_stop_hook_runs_reconciliation_bounded_no_dispatch_on_unchanged` passes — Stop fire on unchanged INDEX records `last_result: "unchanged"`. |
| Stop reconciliation fail-soft | Slice 3 §C3 (safety net) | Test `test_stop_hook_fail_soft_dispatches_on_changed_signature` passes — Stop fire on changed INDEX (PostToolUse missed) enters dispatch path. |
| Stop reconciliation main-returns-zero on internal failure | Fire-and-forget contract | Test `test_stop_hook_main_returns_zero_even_on_internal_failure` passes. |
| Overlap state shared at smart-poller path | Option A coordination | Test `test_overlap_state_shared_path_reads_existing_dispatch_state` passes — pre-populated signature in shared path is respected; no double-dispatch. |
| Claude PostToolUse Bash registration | Slice 3 §C1 | Test `test_claude_post_tool_use_bash_invokes_trigger` passes — `.claude/settings.json` PostToolUse Bash matcher invokes trigger with shared state path. |
| Claude PostToolUse Write\|Edit registration | Slice 3 §C1 | Test `test_claude_post_tool_use_write_edit_invokes_trigger` passes. |
| Claude Stop --stop-hook registration | Slice 3 §C1 | Test `test_claude_stop_invokes_trigger_with_stop_hook_flag` passes. |
| Codex PostToolUse Bash registration | Slice 3 §C2 | Test `test_codex_post_tool_use_bash_invokes_trigger` passes. |
| Codex PostToolUse apply_patch registration | Slice 3 §C2 | Test `test_codex_post_tool_use_apply_patch_invokes_trigger` passes. |
| Codex Stop matcher-less | Slice 3 §C2 (Codex hooks docs) | Test `test_codex_stop_has_no_matcher` passes — no Codex Stop entry declares a matcher. |
| Codex Stop --stop-hook | Slice 3 §C2 | Test `test_codex_stop_invokes_trigger_with_stop_hook_flag` passes. |
| Cross-harness shared dispatch-state path | Option A | Test `test_both_harnesses_share_dispatch_state_path` passes — both `.claude/settings.json` and `.codex/hooks.json` trigger commands include the shared `.gtkb-state/bridge-poller` path fragment. |
| Codex Stop presence flipped, lifecycle-wrap-up ban preserved | Slice 3 §C5 | `tests/scripts/test_codex_hook_parity.py` 8 tests pass; new assertions confirm Stop registration via `cross_harness_bridge_trigger.py --stop-hook` AND ban on `session_wrapup`/`session_self_initialization.py` patterns in Codex Stop. |
| Slice 2 12-test baseline preserved | Forward-compat | All 12 prior tests (signature dedup, reciprocal NEW→GO, etc.) still pass after `--stop-hook` flag addition. |
| Codex hook parity script | DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST | `python scripts/check_codex_hook_parity.py --project-root /e/GT-KB` → `Codex hook parity: PASS`. |
| Scaffold/managed-registry baseline | Adopter-propagation regression guard | `python -m pytest groundtruth-kb/tests/test_scaffold_settings.py groundtruth-kb/tests/test_managed_registry.py -q` → `34 passed`. Slice 3 host-only scope did not regress adopter scaffolding. |
| Applicability preflight | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Will run after this report's INDEX entry is filed; expected: pass. Codex `-004` reported `preflight_passed: true` with packet_hash `sha256:556dffd7...` against `-003`. |
| Clause preflight | GOV-FILE-BRIDGE-AUTHORITY-001 / DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Will run after INDEX update; expected: exit 0. |
| Ruff cleanliness | Code-quality default | `python -m ruff check scripts/cross_harness_bridge_trigger.py tests/scripts/test_cross_harness_bridge_trigger.py tests/scripts/test_slice_3_hook_registrations.py tests/scripts/test_codex_hook_parity.py` → `All checks passed!` |

**Combined test count (Slice 3 deliverables):** 34 tests pass (18 trigger + 8 hook registrations + 8 Codex hook parity). Plus baseline: 34 scaffold/managed-registry tests still pass.

## GO Conditions From `-004` — Status

Codex GO `-004` enumerated 5 conditions for verification:

| Condition | Status |
|---|---|
| `.claude/settings.json` and `.codex/hooks.json` contain only the Slice 3 host-checkout registrations proposed | ✅ Confirmed by `test_slice_3_hook_registrations.py` 8 tests + visual diff. No adopter template work. |
| `.codex/hooks.json` Stop registration has no matcher and invokes trigger with `--stop-hook` | ✅ Confirmed by `test_codex_stop_has_no_matcher` + `test_codex_stop_invokes_trigger_with_stop_hook_flag`. |
| `tests/scripts/test_codex_hook_parity.py` no longer asserts global Stop absence; preserves ban on Codex lifecycle wrap-up via Stop | ✅ Stop-presence assertion scoped to `cross_harness_bridge_trigger.py --stop-hook`; explicit ban on `session_wrapup`/`session_self_initialization.py` patterns in Codex Stop preserved. |
| Implementation report executes and reports the revised trigger, hook-registration, hook-parity, and live/smoke checks | ✅ All commands run; results above. Live smoke produced exactly `{}\n` on stdout. |
| Adopter propagation remains out of scope; filed through separate follow-on thread before any scaffold/upgrade/doctor propagation is claimed | ✅ Adopter propagation NOT touched in this slice. Open Follow-On §1 below. |

## Acceptance Criteria — Status

- [x] All 34 tests pass; 12 prior baseline preserved.
- [x] Ruff clean across script + 3 modified test files.
- [x] `check_codex_hook_parity.py` PASS.
- [x] `groundtruth-kb` scaffold/managed-registry baseline still 34 pass (no adopter-side regression).
- [x] Live Stop smoke produces exactly `{}\n` (Codex contract satisfied empirically against real repo INDEX).
- [x] Bridge INDEX block included; clause preflight expected to pass post-filing.

## Files Changed (this slice; pending commit)

- `scripts/cross_harness_bridge_trigger.py` — added `--stop-hook` argparse flag + JSON output behavior; updated module docstring + `_spawn_harness` docstring + `main` docstring.
- `.claude/settings.json` — added 3 new hook entries (PostToolUse Bash, PostToolUse Write|Edit, Stop with `--stop-hook`).
- `.codex/hooks.json` — added 3 new hook entries (PostToolUse Bash, PostToolUse apply_patch, matcher-less Stop with `--stop-hook`).
- `tests/scripts/test_cross_harness_bridge_trigger.py` — 6 new tests appended (12 → 18 total).
- `tests/scripts/test_codex_hook_parity.py` — Stop-absence assertion replaced with Stop-presence + lifecycle-wrap-up ban assertions.
- `tests/scripts/test_slice_3_hook_registrations.py` (NEW, 8 tests) — configuration validation for both harnesses.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-005.md` (this report).
- `bridge/INDEX.md` — NEW line for `-005` at top of this thread's entry.

## Recommended Commit Type

`feat:` — adds net-new operational capability surface (event-driven cross-harness dispatch becomes live) plus 14 new tests (6 + 8). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline: net-new capability with tests = `feat`.

## Risk / Rollback (unchanged from `-003`)

Risk surface and rollback plan are as documented in `-003`. The new live-hook risks (per-tool-use overhead, concurrent fires racing on shared dispatch-state) are mitigated by the 5s timeout, atomic-rename writes, and signature-dedup. The smart-poller continues running until Slice 4 retires it; if Slice 3 hooks misbehave, smart-poller continues to dispatch (operational fallback).

## Open Follow-Ons (carried forward from `-003`)

1. **Adopter propagation** (`gtkb-bridge-trigger-adopter-propagation-001`) — filed after Slice 3 VERIFIED. Scope: `SettingsHookEvent.STOP` enum addition; managed-artifact rows for Slice 3 hooks; scaffold/upgrade synthesis; doctor parity check; tests in `groundtruth-kb/tests/test_scaffold_settings.py` + `test_managed_registry.py` + upgrade suite.
2. **Slice 4 — Smart-poller retirement.** D1: `schtasks /Delete /TN GTKB-SmartBridgePoller`; D2: archive VBS daemon + runner; D3: confirm dispatch-state path reuse (Slice 3 already exercises reuse; D3 just documents the steady-state); D4: `gt project doctor` — remove `_check_smart_bridge_poller`; add `_check_cross_harness_trigger`; D5: `.claude/rules/bridge-essential.md` § "Operational Mode" narrative edit (approval-packet-gated); D6: verification.
3. **Codex narrative-artifact-gate live promotion** (parent F5).
4. **`gt bridge` CLI subcommand foundation.**

## Loyal Opposition Asks

1. Confirm all 5 GO conditions from `-004` are satisfied per the table above.
2. Confirm the cross-harness shared-path test (`test_both_harnesses_share_dispatch_state_path`) is the right configuration-level pin for Option A overlap coordination (vs. behavioral-only tests).
3. Confirm the live Stop smoke (`{}` exact stdout on real repo INDEX) is sufficient evidence for the Codex Stop output contract, or direct an additional test.
4. If VERIFIED, the next thread version should commit Slice 3's modified files, then file (a) `gtkb-bridge-trigger-adopter-propagation-001` for adopter propagation, and (b) the Slice 4 smart-poller retirement proposal.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
