NEW

# GT-KB Bridge Implementation Report - gtkb-wi4718-dispatch-health-benign-cap-false-fail - 003

bridge_kind: implementation_report
Document: gtkb-wi4718-dispatch-health-benign-cap-false-fail
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-002.md
Approved proposal: bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md
Recommended commit type: fix:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: dispatch auto-session (bridge trigger, Prime Builder B)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4718-HEALTH-VERDICT
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4718

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

## Implementation Claim

The classifier defect in `_runtime_findings_for_recipient` has been corrected. A saturated dispatcher (all concurrency-cap slots busy, `last_result="launch_failed"`, `last_launch.reason="concurrency_cap_reached"`) no longer produces a `dispatch runtime failure` finding or escalates health to FAIL. Instead, saturation is reported as a `dispatch runtime warning: ... saturated (live_count=N/cap=N)` finding so the condition remains visible at WARN without generating false alarms.

Two files changed per the approved GO target_paths:

1. **`groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`**
   - Added `BENIGN_NONLAUNCH_LAUNCH_REASONS = frozenset({"concurrency_cap_reached"})` constant after `RUNTIME_FAILURE_LAUNCH_REASONS`.
   - Modified `_runtime_findings_for_recipient` to use a boolean intermediate `last_result_is_runtime_failure` that is overridden to `False` when `last_result == "launch_failed"` and `launch_reason in BENIGN_NONLAUNCH_LAUNCH_REASONS`.
   - Added a new `dispatch runtime warning: {recipient_key} saturated (live_count={live}/cap={cap}) with pending_count={pending_count}` branch so saturation stays visible as WARN when pending work exists.
   - All other failure detection paths (circuit-breaker, `failure_class`, `exit_failure_reason`, `_dispatch_not_ready`, fallback-skipped, `RUNTIME_FAILURE_LAUNCH_REASONS` genuine reasons) are untouched.

2. **`platform_tests/scripts/test_bridge_dispatch_config.py`**
   - Added 6 new WI-4718 tests (imports for `BENIGN_NONLAUNCH_LAUNCH_REASONS` and `_runtime_findings_for_recipient` added):
     - `test_wi4718_saturation_emits_warn_not_fail` — integration test; confirms no `dispatch runtime failure` finding and `health_status != "FAIL"` for a `loyal-opposition:D` saturation row.
     - `test_wi4718_saturation_with_live_count_cap_in_finding` — unit test; confirms the WARN finding text includes `live_count=4/cap=4`.
     - `test_wi4718_no_findings_when_no_pending_work` — unit test; confirms zero findings when `pending_count=0, selected_count=0`.
     - `test_wi4718_genuine_launch_reason_still_fails` — integration test; `reason="spawn_rate_limited"` still produces `dispatch runtime failure`.
     - `test_wi4718_absent_launch_reason_still_fails` — unit test; `last_launch={}` (no reason key) still emits `dispatch runtime failure` (fail-closed).
     - `test_wi4718_benign_constant_contains_expected_reasons` — constant test; confirms `"concurrency_cap_reached" in BENIGN_NONLAUNCH_LAUNCH_REASONS` and it is a `frozenset`.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` — governing principle: a chronic false-FAIL health signal is recurring cost (false alarm + signal masking) with no informational value; the fix restores the verdict's value/cost ratio.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the health verdict is a state claim about canonical dispatch state; reporting FAIL for a saturated-but-healthy dispatcher is an inaccurate state claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs this bridge filing and the numbered-file chain (blocking, paths-match `bridge/**`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report carries forward all proposal spec links (blocking).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item metadata present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in the verification section below (blocking).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed files are under `E:\GT-KB` (`groundtruth-kb/src/...`, `platform_tests/...`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — WI-4718 + this report preserve the defect and decision as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability across WI, proposal, tests, and report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — WI-4718 candidate -> implementation -> verified lifecycle.

## Owner Decisions / Input

No new owner decision is required by this implementation report. The implementation stays within the GO'd scope from the approved proposal. Carry-forward owner evidence:

- Owner AUQ (2026-06-21) authorized filing this classifier fix as a new proposal (`DELIB-20265509`).
- PAUTH `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4718-HEALTH-VERDICT` covers `source + test_addition` mutations under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.

## Prior Deliberations

- `bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md` — approved implementation proposal carried forward.
- `bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-002.md` — Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20265509` — owner decision (AUQ 2026-06-21) authorizing this proposal.
- `DELIB-20265484` — Loyal Opposition GO for sibling WI-4662; confirmed the sibling scope leaves the health verdict unchanged, which is exactly the gap this fix closes.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — saturation is not a failure | `test_wi4718_saturation_emits_warn_not_fail`: recipient row `last_result="launch_failed"`, `last_launch.reason="concurrency_cap_reached"`, `pending_count=3` → no `dispatch runtime failure` finding; health status NOT FAIL. PASSED. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` — saturation is visible as WARN | `test_wi4718_saturation_with_live_count_cap_in_finding`: same row with `live_count=4/cap=4` → WARN finding present with `live_count=4/cap=4` text. PASSED. |
| Fail-closed: no pending work → no findings | `test_wi4718_no_findings_when_no_pending_work`: `pending_count=0, selected_count=0` → zero findings. PASSED. |
| Fail-closed: genuine launch reason still fails | `test_wi4718_genuine_launch_reason_still_fails`: `reason="spawn_rate_limited"` → `dispatch runtime failure` finding present; health FAIL. PASSED. |
| Fail-closed: absent reason still fails | `test_wi4718_absent_launch_reason_still_fails`: `last_launch={}` (no reason) → `dispatch runtime failure` present. PASSED. |
| Benign constant correctness | `test_wi4718_benign_constant_contains_expected_reasons`: `"concurrency_cap_reached" in BENIGN_NONLAUNCH_LAUNCH_REASONS` and `frozenset`. PASSED. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — non-regression | `test_wi4578_health_fails_for_blocked_runtime_candidates`, `test_wi4578_health_fails_for_exit_zero_no_verdict_evidence`, `test_wi4578_manual_scan_excludes_acknowledged_archived_nonterminal` — all continued PASSED. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
```

## Observed Results

**pytest (19 tests):**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
collected 19 items

platform_tests\scripts\test_bridge_dispatch_config.py ................... [100%]

========================= 19 passed, 1 warning in 22.85s ======================
```

**ruff check:**
```text
All checks passed!
LINT_CLEAN
```

**ruff format --check:**
```text
2 files already formatted
FORMAT_CLEAN
```

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Recommended Commit Type

- Recommended commit type: `fix:`
- Rationale: Repairs a classifier bug that produced false FAIL health verdicts for a saturated-but-healthy dispatcher. No new capability is added; the `BENIGN_NONLAUNCH_LAUNCH_REASONS` constant and the WARN emission are part of the correctness fix, not new features.

## Acceptance Criteria Status

- [x] `last_result="launch_failed"` + `last_launch.reason="concurrency_cap_reached"` + pending work emits NO `dispatch runtime failure` finding; `_compute_health_status` does not return FAIL for that row alone. (`test_wi4718_saturation_emits_warn_not_fail` PASSED)
- [x] The same row emits a `dispatch runtime warning: ... saturated (live_count=.../cap=...)` finding (saturation stays visible). (`test_wi4718_saturation_with_live_count_cap_in_finding` PASSED)
- [x] `last_result="launch_failed"` with a genuine failure reason (e.g. `spawn_rate_limited`) or an absent reason still emits a `dispatch runtime failure` finding — no regression. (`test_wi4718_genuine_launch_reason_still_fails`, `test_wi4718_absent_launch_reason_still_fails` PASSED; `test_wi4578_*` PASSED)
- [x] All other classifier paths (circuit breaker, failure_class, exit_failure_reason, fallback-skipped, unchanged) are unchanged.
- [x] New unit tests pass; `ruff check` + `ruff format --check` clean on changed files.

## Applicability Preflight

Run against proposal (`-001.md`; operative content for this thread):

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4718-dispatch-health-benign-cap-false-fail
```

Result:
```text
## Applicability Preflight

- packet_hash: `sha256:30e2b508eb37901e60e7a9898be4894231fd820529df4d884dedaf359e281f4f`
- bridge_document_name: `gtkb-wi4718-dispatch-health-benign-cap-false-fail`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4718-dispatch-health-benign-cap-false-fail
```

Result:
```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4718-dispatch-health-benign-cap-false-fail`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit: 0 (pass)
```

## Risk And Rollback

- **Residual risk**: The `concurrency_cap_reached` benign set is a single explicit token. Any future non-launch reason that should be treated as benign requires a separate proposal to extend `BENIGN_NONLAUNCH_LAUNCH_REASONS`. This is intentional narrow scope.
- **Chronic saturation**: If the dispatcher is chronically saturated, the WARN finding will appear continuously on the health surface. This is the correct behavior — it signals a throughput concern without masking genuine failures.
- **Rollback**: Revert `bridge_dispatch_config.py` to the pre-WI-4718 state. The test additions are additive and safe to leave in place. No schema changes, no MemBase mutations, no KB mutations.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and the executed test evidence above.
2. Return VERIFIED if the report and implementation satisfy the approved proposal; return NO-GO with findings otherwise.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
