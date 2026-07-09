NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: a6d97151-27d2-41c8-8e3b-1d88f3960cf8
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via ::init gtkb pb

# WI-5070 Governed Dispatcher Budget Model Setter — Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5070-dispatch-budget-model-setter
Version: 005
Responds to: bridge/gtkb-wi5070-dispatch-budget-model-setter-004.md
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI5070-DISPATCH-MODEL-SETTER-20260707
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-5070
work_item_ids: [WI-5070, WI-5047]

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "config/dispatcher/rules.toml", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

Implements the GO'd proposal `-003` (GO at `-004`): a governed dispatcher budget-model
transaction plus CLI verb, then use of that verb to complete the WI-5047 stale harness-D
budget-model label correction — all through the governed dispatcher control surface, never
by direct TOML editing (`DCL-DISPATCHER-CONFIG-CLI-ONLY-001`).

## Specification Links

Carried forward from `-003`/`-004`:

- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` — the model change flows through
  `gt bridge dispatch config set-model`, not a direct file edit.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — the new verb reuses the existing audited
  transaction path; output is inspectable JSON with dry-run/defer semantics.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatcher metadata is now truthful for D.
- `ADR-CROSS-HARNESS-PARITY-001` — the budget/status model label agrees with the
  owner-selected Kimi route.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under the active WI-5070
  PAUTH after GO + implementation-start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report requires an independent LO VERIFIED before
  terminal closure.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — linkage + spec-derived test evidence
  below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — GT-KB platform work; all files under
  `E:/GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-STANDING-BACKLOG-001` — the NO-GO blocker
  is promoted into implemented, tested, audited work.

## Prior Deliberations

- `DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` — owner decision selecting the Kimi route
  and requiring a governed follow-on path (the authority for the harness-D label value).
- `DELIB-20260702-OLLAMA-DEEPSEEK-V4-PRO-CLOUD` — the prior route, superseded for this path.
- `DELIB-202665814`, `DELIB-202665815` — LO confirmation of the WI-5047 budget-model-setter
  blocker and subsequent hold.

## Owner Decisions / Input

No new owner decision was required. Owner authority is carried by
`DELIB-20260706-OLLAMA-KIMI-K2-7-CODE-CLOUD` and the active WI-5070 PAUTH, which permits
source, test, cli-extension, and config mutations while forbidding credential,
provider-account, role, reviewer-precedence, dispatch-eligibility, and unrelated
harness-setting changes. The implementation stayed inside that bounded scope.

## What Was Implemented

### 1. `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py`

- `set_model(project_root, harness_id, *, model, dry_run, defer_to_next_session)` (new).
  Updates only `budget.harnesses.<id>.model` through the existing `_apply_transaction`
  audited path (same clone → mutate → render → hash → audit flow as `set_caps`).
  Preserves sibling budget fields (`pricing`, `estimated_usd_per_dispatch`).
- `_require_budget_harness(raw, harness_id)` (new). Fails closed for a missing `[budget]`
  table or a missing budget harness row.
- `_validate_model(value)` (new). Fails closed for an empty/whitespace model value.

### 2. `groundtruth-kb/src/groundtruth_kb/cli.py`

- `bridge_dispatch_config_set_model_cmd` (new) — `gt bridge dispatch config set-model
  <HARNESS_ID> --model <MODEL> [--dry-run] [--defer-to-next-session] [--json]`, mirroring
  the existing `set-caps` verb and reusing `_run_dispatch_transaction`.

### 3. `config/dispatcher/rules.toml`

- Harness D budget model corrected `deepseek-v4-pro-cloud` → `kimi-k2-7-code-cloud` **via
  the new governed CLI command** (WI-5047 follow-on), not a direct edit. The applied diff
  is exactly one line; no reformat collateral.

### 4/5. Tests

- `platform_tests/scripts/test_bridge_dispatch_transactions.py` — 5 transaction tests.
- `platform_tests/scripts/test_bridge_dispatch_config.py` — 2 CLI tests (apply + dry-run).

## Requirement Sufficiency

Existing requirements sufficient. The owner decision, WI-5070 PAUTH, and linked dispatcher
specs fully constrained the work. No new GOV/ADR/DCL/SPEC record required.

## Pre-File Code-Quality Gates

```
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_bridge_dispatch_config.py
python -m ruff format --check <same 4 python files>
```

Results: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`. (config/dispatcher/rules.toml is TOML, out of ruff scope.)

## Spec-to-Test Mapping (executed)

| Specification / Decision | Test / Evidence | Executed | Result |
|---|---|---|---|
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` | `test_wi5070_set_model_cli_updates_budget_model` (change flows through the CLI verb); live D correction performed via `gt`/`python -m groundtruth_kb` CLI | yes | PASS |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `test_set_model_dry_run_does_not_write`, `test_wi5070_set_model_cli_dry_run_does_not_write` (auditable output, dry-run leaves config untouched) | yes | PASS |
| `ADR-CROSS-HARNESS-PARITY-001` | `test_set_model_updates_budget_model_and_preserves_siblings` + live `gt bridge state-report` showing `D | ollama | kimi-k2-7-code-cloud` | yes | PASS |
| fail-closed safety (`GOV-FILE-BRIDGE-AUTHORITY-001`) | `test_set_model_missing_budget_harness_fails_closed`, `test_set_model_empty_model_fails_closed`, `test_set_model_invalid_harness_id_fails_closed` | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | implementation began only after GO `-004` + `implementation_authorization.py begin` packet | yes | PASS |

## Commands Executed & Results

```
python -m pytest platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
# => 70 passed (7 new: 5 transaction + 2 CLI)

# live WI-5047 follow-on (governed CLI, not direct edit):
python -m groundtruth_kb bridge dispatch config set-model D --model kimi-k2-7-code-cloud --json
# => transaction=set-model, status=applied, mutated=true; git diff = 1 line

gt bridge state-report   # => D | ollama | kimi-k2-7-code-cloud

# regression sweep of the 3 files referencing the old model (all isolated fixtures):
python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py -q
# => 194 passed, 1 skipped
```

## Acceptance Criteria Check

- Transaction updates only the requested budget harness model + preserves siblings — PASS.
- CLI command supports dry-run, deferred transaction, and JSON output — PASS.
- Invalid harness ids, missing budget harness rows, empty model values fail closed — PASS.
- Dispatcher evidence reports harness D budget model as `kimi-k2-7-code-cloud` — PASS
  (live `gt bridge state-report`).

## Scope Discipline

`git status` shows exactly the five authorized `target_paths` modified. The
`config/dispatcher/rules.toml` change is a single line applied by the governed transaction;
no reformat collateral. The three other test files that mention the old model string use
isolated tmp_path fixtures and are unaffected (194 passed, 1 skipped).

## WI-5047 Disposition

The WI-5047 remaining defect was the stale dispatcher budget/status label for harness D.
This report performs that correction through the new governed verb, so WI-5047 can move to
closure on this report's VERIFIED (its route-side evidence already pointed at Kimi). No
separate direct-TOML action is required or was taken.

## Risk And Rollback

Risk: an over-broad mutation touching sibling budget fields or other harnesses. Mitigation:
`set_model` mutates only the single `model` field of the named budget harness and is
covered by the sibling-preservation test. Rollback: re-run the governed verb with the prior
value (`set-model D --model deepseek-v4-pro-cloud`) and revert the bounded source/test
changes; bridge, PAUTH, deliberation, and audit records remain append-only.

## Recommended Commit Type

Recommended commit type: feat — adds a net-new governed dispatcher control transaction and
CLI verb (`set-model`), a new capability surface on the dispatcher control CLI, plus the
config correction it enables.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
