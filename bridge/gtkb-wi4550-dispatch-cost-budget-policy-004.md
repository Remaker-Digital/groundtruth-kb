NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-28T21-30-01Z-prime-builder-A-8c66e6
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex bridge auto-dispatch session, approval_policy=never

bridge_kind: implementation_report
Document: gtkb-wi4550-dispatch-cost-budget-policy
Version: 004 (NEW; implementation complete)
Responds to approved verdict: bridge/gtkb-wi4550-dispatch-cost-budget-policy-003.md
Approved proposal: bridge/gtkb-wi4550-dispatch-cost-budget-policy-002.md
Project Authorization: PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-OMNIGENT-ALIGNMENT
Work Item: WI-4550
Recommended commit type: feat

target_paths: ["config/dispatcher/rules.toml", "scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatch_cost_budget.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source | config | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# WI-4550 Dispatch Cost Budget Policy - Implementation Report

## Implementation Claim

WI-4550 Slice 1 is implemented within the approved config/source/test target paths.

The dispatcher now has a declarative, disabled-by-default dispatch budget model in `config/dispatcher/rules.toml`, parser/reporting support in `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, and a pre-spawn budget gate in `scripts/cross_harness_bridge_trigger.py`.

The launch-path budget gate:

- Allows current behavior when `[budget].enabled = false`.
- Fails closed for enabled priced harness rows with unknown model cost data.
- Fails open for explicitly unpriced harness rows when `unpriced_model_policy = "fail_open"`.
- Suppresses dispatch before implementation authorization and before `subprocess.Popen` when the projected per-session or per-user-daily budget would exceed the hard cap.
- Records durable suppression evidence in `dispatch-failures.jsonl`.
- Records accepted estimated dispatch spend in `dispatch-budget-ledger.jsonl`.
- Surfaces budget config and budget-cap holds in dispatch status/reporting without turning budget cap holds into generic process-saturation failures.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-AUTOMATION-VALUE-VS-COST-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-OMNIGENT-ADVISORY-20260614` - identified cost/token budget enforcement as the top Omnigent-alignment risk.
- `DELIB-20263229` - owner decision for patterns-only Omnigent emulation without a runtime dependency.
- `DELIB-20265586` - owner-approved project authorization snapshot covering WI-4550.
- `INTAKE-2ce995f2` - bounded parallel cross-harness auto-dispatch substrate that needs budget boundaries.
- `DELIB-TAFE-PHASE-1-DISPATCH-TRACK-PAUTH-20260613` - dispatch-track implementation authorization context.
- `bridge/gtkb-wi4550-dispatch-cost-budget-policy-002.md` - approved revised proposal.
- `bridge/gtkb-wi4550-dispatch-cost-budget-policy-003.md` - Loyal Opposition GO verdict.

## Owner Decisions / Input

No new owner decision was requested or obtained in this auto-dispatched worker.

Implementation used existing owner/project authorization from `PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23` and stayed within the approved target paths. This worker did not perform deployment, credential lifecycle work, force-push/history mutation, or formal KB mutation.

## Implementation Authorization

Implementation-start packet:

```json
{
  "bridge_id": "gtkb-wi4550-dispatch-cost-budget-policy",
  "created_at": "2026-06-28T21:35:05Z",
  "expires_at": "2026-06-28T23:35:05Z",
  "latest_status": "GO",
  "packet_hash": "sha256:66ecd08bd8a94cbb0414047e03a0998f9e0d8a5e684e2ac5e0f9643247b26392",
  "target_path_globs": [
    "config/dispatcher/rules.toml",
    "scripts/cross_harness_bridge_trigger.py",
    "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py",
    "platform_tests/scripts/test_dispatch_cost_budget.py",
    "platform_tests/scripts/test_bridge_dispatch_config.py"
  ]
}
```

## Files Changed

- `config/dispatcher/rules.toml`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatch_cost_budget.py`

Scoped diff stat for tracked target paths:

```text
config/dispatcher/rules.toml                       |  38 +++++
groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py | 159 ++++++++++++++++++-
platform_tests/scripts/test_bridge_dispatch_config.py       |  57 +++++++
scripts/cross_harness_bridge_trigger.py            | 176 +++++++++++++++++++++
4 files changed, 429 insertions(+), 1 deletion(-)
```

`platform_tests/scripts/test_dispatch_cost_budget.py` is a new target-path test file.

## Spec-To-Test Mapping

| Specification / governing surface | Verification evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4550-dispatch-cost-budget-policy --session-id 2026-06-28T21-30-01Z-prime-builder-A-8c66e6` | PASS; packet minted for only approved target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4550-dispatch-cost-budget-policy --json` | PASS; `missing_required_specs: []`, `preflight_passed: true`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4550-dispatch-cost-budget-policy` | PASS; 0 blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, lint, and format commands listed below. | PASS. |
| `GOV-STANDING-BACKLOG-001` | Bridge thread and implementation packet carry `Work Item: WI-4550` under `PROJECT-OMNIGENT-ALIGNMENT`. | PASS. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | `platform_tests/scripts/test_dispatch_cost_budget.py` covers default behavior, hard session cap, daily cap, fail-closed unknown priced model, and fail-open unpriced model. | PASS. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | This report preserves implementation, evidence, and verification mapping in the bridge audit chain. | PASS. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi4550-dispatch-cost-budget-policy --session-id 2026-06-28T21-30-01Z-prime-builder-A-8c66e6
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4550-dispatch-cost-budget-policy --session-id 2026-06-28T21-30-01Z-prime-builder-A-8c66e6
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_cost_budget.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short --basetemp .gtkb-state/tmp/pytest-wi4550-8c66e6d
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_dispatch_cost_budget.py platform_tests/scripts/test_bridge_dispatch_config.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_dispatch_cost_budget.py platform_tests/scripts/test_bridge_dispatch_config.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4550-dispatch-cost-budget-policy --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4550-dispatch-cost-budget-policy
```

## Observed Results

- Implementation authorization: PASS; packet hash `sha256:66ecd08bd8a94cbb0414047e03a0998f9e0d8a5e684e2ac5e0f9643247b26392`.
- Focused pytest: PASS; `44 passed, 1 warning in 1.60s`. The warning is a pre-existing pytest cache path creation warning under `.pytest_cache`, not a test failure.
- Ruff lint: PASS; `All checks passed!`.
- Ruff format: PASS; `4 files already formatted`.
- Applicability preflight: PASS; `preflight_passed: true`, `missing_required_specs: []`. Advisory omissions reported by the proposal preflight are carried forward in this report's `Specification Links`.
- Clause preflight: PASS; 0 blocking gaps.

## Acceptance Criteria Status

- [x] Default budget config preserves current dispatch behavior unless enabled.
- [x] Budget fields parse and surface in dispatch config/status JSON/text.
- [x] Invalid budget config disables the budget gate and emits a visible warning.
- [x] Unknown priced model cost data fails closed before worker spawn.
- [x] Explicitly unpriced model rows fail open when configured to do so.
- [x] Per-session hard cap suppresses before `subprocess.Popen`.
- [x] Per-user-daily cap reads `dispatch-budget-ledger.jsonl` and suppresses before `subprocess.Popen`.
- [x] Budget suppressions are recorded in `dispatch-failures.jsonl`.

## Residual Risk / Follow-Up

This slice uses static `estimated_usd_per_dispatch` values, not provider-reported token usage. That is intentional for Slice 1 and keeps the launch gate deterministic. A later slice can replace static estimates with provider/runtime metering without changing the dispatch pre-spawn gate contract.

Initial pytest attempts using the default Windows temp directory and `E:\tmp` failed with `WinError 5` before test execution. Verification was rerun successfully with `TEMP`, `TMP`, and pytest `--basetemp` under `.gtkb-state/tmp`.

## WI-4897 Selected Entry Handling

The same auto-dispatch selected `gtkb-wi4897-release-gate-parity-hard-gate-alignment` at latest `NO-GO`, but that entry became stale during this session. A separate Prime Builder session filed `bridge/gtkb-wi4897-release-gate-parity-hard-gate-alignment-007.md`, and Loyal Opposition filed terminal `VERIFIED` at `bridge/gtkb-wi4897-release-gate-parity-hard-gate-alignment-008.md`. This worker therefore did not act on WI-4897.

## Risk And Rollback

Risk is moderate and localized to dispatch-launch policy. The budget gate is disabled by default in `config/dispatcher/rules.toml`, so current dispatch behavior is preserved until an operator enables it. Rollback is a single commit revert of the five target files listed above.
