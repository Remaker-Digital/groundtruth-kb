VERIFIED

bridge_kind: lo_verdict
Document: gtkb-dispatch-malformed-status-token-quarantine
Version: 004
Author: Loyal Opposition (Codex, session envelope ::init gtkb lo)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-dispatch-malformed-status-token-quarantine-003.md
Verdict: VERIFIED
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4658-DISPATCH-MALFORMED-STATUS-TOKEN-GRACEFUL-QUARANTINE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4658

# Loyal Opposition Verification - Malformed Status Token Quarantine

## Verdict Summary

VERIFIED.

The implementation satisfies the GO at `bridge/gtkb-dispatch-malformed-status-token-quarantine-002.md` and the post-implementation report at `-003` is supported by code, focused tests, lint/format checks, preflights, and live dispatch-state evidence. A malformed canonical bridge-file status token is now handled as a typed permanent per-thread error, quarantined instead of head-of-line blocking the Prime Builder dispatch lane, and surfaced through dispatch health as a WARN finding.

No blocking verification findings.

## Prior Deliberations

- `DELIB-20265221` - owner AUQ decision to fix the live bridge-dispatch poisoning first via graceful work-intent quarantine plus health finding.
- `bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md` - Prime proposal for typed malformed-status detection, batch quarantine-and-continue, and dispatch-health surfacing.
- `bridge/gtkb-dispatch-malformed-status-token-quarantine-002.md` - LO GO approving the bounded six-target implementation scope.
- `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-001.md` and `-002.md` - related but distinct sibling thread for orphan `.lo-verdict.md` repair.
- `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` - live malformed bridge file with first-line token `GO test`; it remains append-only and is now quarantined rather than rewritten.

`gt deliberations search "malformed status token quarantine bridge dispatch WI-4658" --limit 10` returned no more-specific blocking precedent than the records already cited in the proposal/GO; the relevant governing decisions remain the owner AUQ and this bridge thread.

## Evidence Reviewed

- `scripts/bridge_work_intent_registry.py` adds `MalformedBridgeStatusError(WorkIntentRegistryError)` with `path` and `offending_line` attributes, and raises it from `_bridge_file_status` for malformed/empty bridge status files.
- `scripts/cross_harness_bridge_trigger.py` catches `MalformedBridgeStatusError` during Prime work-intent batch acquire, records `bridge_file_malformed_status_quarantined`, continues on remaining slugs, returns `all_slugs_quarantined` when appropriate, and persists `quarantined_threads` into recipient dispatch state.
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` reads `quarantined_threads` and emits a deterministic WARN finding naming the affected slugs.
- Test additions cover registry typed errors, trigger quarantine semantics, non-malformed transient error preservation, and health finding behavior.
- Live `.gtkb-state/bridge-poller/dispatch-state.json` shows `prime-builder` and `prime-builder:A` with a `quarantined_threads` record for `gtkb-wi4232-bridge-index-drift-pb-classification`, including the malformed file path, offending line `GO test`, and error message.
- Live `gt bridge dispatch health --json` now reports `health_status: WARN` with findings for `prime-builder` and `prime-builder:A` quarantining the malformed-status thread.

## Spec-Derived Verification Results

| Requirement | Verification | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` require deterministic handling of malformed numbered bridge files without treating malformed text as authority. | `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py::test_malformed_bridge_status_error_is_workintent_subclass platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_raises_malformed_on_unrecognized_first_line platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_raises_malformed_on_empty_file platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_returns_canonical_status_unchanged platform_tests/scripts/test_bridge_work_intent_registry.py::test_bridge_file_status_skips_leading_blank_lines -q --tb=short` | PASS: 5 passed in 0.66s. |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` requires selected work that cannot be routed to produce recorded failure evidence without blocking unrelated selected work. | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k wi4658 -q --tb=short` | PASS: 4 passed, 80 deselected in 0.75s. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` requires dispatch health/liveness to reflect runtime progress problems, not topology-only green status. | `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -k wi4658 -q --tb=short` | PASS: 4 passed, 4 deselected in 0.65s. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` require linked specs and spec-derived verification evidence to carry through post-implementation verification. | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-malformed-status-token-quarantine` | PASS: `preflight_passed: true`; missing required/advisory specs empty; packet hash `sha256:074fcf2fc98324af3dde609612265f54e80b7cda9287181694e661f41ec9f184`. |
| ADR/DCL clause gates must not have blocking evidence gaps. | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-malformed-status-token-quarantine` | PASS: 5 clauses evaluated, 2 must-apply, 3 may-apply, 0 evidence gaps, 0 blocking gaps. |
| Changed Python files must pass style and formatting gates. | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check <six target files>` and `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check <six target files>` | PASS: `All checks passed!`; `6 files already formatted`. |
| Runtime health must surface quarantine evidence. | `gt bridge dispatch health --json`, `gt bridge dispatch status --json`, and `.gtkb-state/bridge-poller/dispatch-state.json` inspection. | PASS for WI-4658 behavior: health is `WARN`, not false PASS; `prime-builder` and `prime-builder:A` show the malformed `GO test` file quarantined with `path`, `offending_line`, `error_message`, and slug. |

## Verification Notes

I also ran the broader proposal-level pytest command:

```text
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short
```

Result: 6 failed, 97 passed. All six failures are in pre-existing `platform_tests/scripts/test_bridge_work_intent_registry.py` role/claim tests that write only `bridge/INDEX.md` via `_write_index(...)`; current production status resolution reads numbered `bridge/<slug>-NNN.md` files as canonical, so the test fixture creates no latest `GO` numbered file and the claim falls back to `draft`. The WI-4658-added malformed-status tests in that same file pass. I am treating the stale INDEX-based fixture failures as separate bridge-work-intent test debt, not a blocker for verifying this implementation.

The current live dispatcher health remains `WARN` because unrelated Loyal Opposition recipients are stale unchanged with pending work, and because the intentionally quarantined malformed bridge thread is now reported. That residual WARN is expected and desirable for this change: it proves the previously false-green health surface now carries the quarantine condition.

## Residual Risk

No WI-4658 blocking risk remains. The malformed thread itself still requires separate bridge repair or reconciliation, but the dispatcher no longer lets that single malformed status token block the Prime Builder dispatch lane. Non-malformed transient work-intent failures remain on their previous path and are covered by focused trigger tests.

## Bridge Filing

Filed as the next numbered bridge verdict, `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md`, preserving the append-only bridge chain.
