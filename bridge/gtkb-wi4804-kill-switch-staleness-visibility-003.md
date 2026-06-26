NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 130bf9ae-15f0-4373-a7b5-9286568dbc97
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

# gtkb-wi4804-kill-switch-staleness-visibility — Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4804-kill-switch-staleness-visibility
Version: 003

Responds-To: bridge/gtkb-wi4804-kill-switch-staleness-visibility-002.md (GO)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4804
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26
Recommended commit type: fix

## Implementation Report

Implemented per the `-002` GO ("Implement per `-001`") within the authorized `target_paths`. Changes are staged in the working tree (uncommitted) for Loyal Opposition inspection; per the protocol the VERIFIED finalization helper creates the commit with the verified paths plus the verdict. Scope is the narrowed visibility half only (per DELIB-20266166); the dormancy auto-restart is tracked separately as WI-4852.

Verified paths (for the finalization helper `--include`):
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_doctor_kill_switch_staleness.py`

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
  - Constants `_KILL_SWITCH_ENV_VAR = "GTKB_NO_CROSS_HARNESS_TRIGGER"`, `_KILL_SWITCH_STALE_SECONDS = 7200` (2h), `_KILL_SWITCH_FIRST_SEEN_REL = .gtkb-state/ops/kill-switch-first-seen.json`.
  - Fail-soft bookkeeping helpers `_read_kill_switch_first_seen` / `_write_kill_switch_first_seen` (missing/corrupt/unwritable → degrade, never crash).
  - `_check_kill_switch_staleness(target)`: when the env var != "1", clears the first-seen record and returns `pass`. When set: reads/creates first-seen; `age >= threshold` → `warning` (names the timestamp + ~hours, says dispatch is disabled, tells the operator to clear it, and states it never auto-clears per SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001); `age < threshold` → `info` (recent deliberate stop). Never modifies the env var.
  - Registered: `checks.append(_check_kill_switch_staleness(target))` alongside the dispatch-health checks (`_check_bridge_dispatch_liveness` x2 + `_check_cross_harness_trigger`).
- `platform_tests/scripts/test_doctor_kill_switch_staleness.py` (new, dedicated, per the per-check doctor-test convention): 4 tests covering unset+clear, first-observation record, recent→info, and stale→warning (with the no-auto-clear assertion). First-seen timestamps are written directly to the tmp-target state file so the threshold branch is deterministic without a clock dependency.

No change to the cross-harness trigger, the kill-switch semantics, or any auto-clear behavior; the env var stays purely manual. Dormancy auto-restart is out of scope (WI-4852).

## Specification Links (carried forward from -001)

- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — visibility only; the check never auto-clears the manual env var.
- `ADR-DISPATCHER-ARCHITECTURE-001` — a silently-disabled dispatch lane is an observability gap this closes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the change stays in the in-root `groundtruth-kb` package + in-root test tree; first-seen bookkeeping under in-root `.gtkb-state/ops/` (CLAUSE-IN-ROOT satisfied).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — surfaces a stale operational state rather than letting it silently persist.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4804.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 (warn on stale; never auto-clear) | `test_warns_when_kill_switch_set_beyond_threshold` | PASS (warning + env var unchanged) |
| visibility threshold (no nag for a recent stop) | `test_info_when_kill_switch_set_recently` | PASS |
| clear bookkeeping on unset | `test_pass_and_clears_when_kill_switch_unset` | PASS |
| first observation records first-seen | `test_records_first_seen_on_first_observation` | PASS |
| No-regression | existing doctor checks unaffected; ruff | green |

## Verification Evidence (commands + observed results)

- `python -m pytest platform_tests/scripts/test_doctor_kill_switch_staleness.py -q --tb=short` → **4 passed**.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_doctor_kill_switch_staleness.py` → **All checks passed** (after an `--fix` import-ordering pass on the new test file).
- `python -m ruff format --check` (both files) → **already formatted**.
- doctor.py imports cleanly (the test imports `_check_kill_switch_staleness` + the constants from it, so the module loads and the registration is syntactically valid).

## Prior Deliberations

- `DELIB-20266140` — WI-4804 policy: visibility-not-auto-clear (honor SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001).
- `DELIB-20266166` — scope split: visibility now (this work); dormancy auto-restart → WI-4852 (WI-4790/WI-4848 daemon program).
- `DELIB-20266137` — owner authorization for this dispatcher-reliability drive.
- `bridge/gtkb-wi4804-kill-switch-staleness-visibility-002.md` (Cursor LO GO) — the verdict this report responds to.

## Owner Decisions / Input

- Authorized by `DELIB-20266140` + `DELIB-20266166` (owner AUQ this session); `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-FIXES-PHASES-DRIVE-2026-06-26` covers WI-4804. No further owner decision is required: the check is observe-and-warn (plus its own first-seen bookkeeping) and never auto-clears the kill-switch or changes dispatch behavior.

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). No new or revised requirement was needed.

## Risk / Rollback

- Risk: low. Observe-and-warn; the only mutation is the fail-soft first-seen bookkeeping file under in-root `.gtkb-state/ops/`. It never touches the env var, dispatch state, or dispatch behavior; WARN (not FAIL) keeps it non-blocking.
- Rollback: remove `_check_kill_switch_staleness`, its registration, the constants/helpers, and the test file. No schema change; append-only KB untouched.

## Recommended Commit Type

`fix:` — closes the silent-disabled-dispatch observability gap (a forgotten kill-switch had no surfaced signal). Non-blocking doctor WARN + fail-soft bookkeeping; no dispatch-behavior change and no kill-switch auto-clear.
