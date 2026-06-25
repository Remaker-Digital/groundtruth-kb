NEW

# gtkb-wi4789-dispatch-health-perrole-fail-boundary — Post-Implementation Report (WI-4789)

bridge_kind: prime_proposal
Document: gtkb-wi4789-dispatch-health-perrole-fail-boundary
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-wi4789-dispatch-health-perrole-fail-boundary-002.md (GO)

author_identity: claude
author_harness_id: B
author_session_context_id: 0550e08e-1e1f-4820-bfd0-cb80d797d60b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-WI-4789-DISPATCH-HEALTH-PERROLE-FAIL-001
Project: PROJECT-GTKB-DISPATCHER-COMPLETION
Work Item: WI-4789

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary of Implementation

Implemented the GO'd (-002) per-role FAIL fix in `bridge_dispatch_config.py`
`compute_bridge_dispatch_status`:

- Removed the `or finding.startswith("dispatch runtime failure")` clause from the
  overall `health_status` FAIL condition (was lines 319-330). Overall health is
  now FAIL only when a finding contains `"no active dispatchable"` (a required
  role with no dispatch-eligible harness — emitted per-role) OR starts with
  `"config error"`. A recoverable `"dispatch runtime failure"` finding (e.g. a
  tripped circuit breaker) on a still-eligible harness now yields WARN (the
  `if health == "PASS" and findings: health = "WARN"` path is unchanged).
- Added an explanatory comment citing WI-4789 /
  SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001 v2.
- The per-recipient `severity` diagnostic (`_runtime_classification_for_recipient`)
  is unchanged, per the spec's scope note — it is a separate per-recipient label,
  not the aggregate health.

Rationale grounding: `select_dispatch_candidates` gates only on config/topology
eligibility and never on runtime backoff, so the `"no active dispatchable"`
finding reflects genuine per-role impossibility — the correct FAIL trigger.

## Specification Links (carried forward)

- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` (v2) — governing requirement
  (per-role FAIL); implemented.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`.
- Advisory: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Prior Deliberations

- `DELIB-20265882` — dispatcher target-architecture grill; the FAIL/WARN health
  bug is the named Phase 0 item.
- Owner AUQ 2026-06-25 — per-role FAIL boundary captured in spec v2.

## Owner Decisions / Input

No further owner approval required: authorized by
`PAUTH-WI-4789-DISPATCH-HEALTH-PERROLE-FAIL-001` (owner decision
`DELIB-20265882`) plus the 2026-06-25 AUQs (spec creation + per-role FAIL
boundary). The LO GO (-002, Cursor / harness E) authorized the change to the two
files.

## Requirement Sufficiency

Existing requirements sufficient — `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` v2
governs; no new or revised requirement was introduced.

## Spec-to-Test Mapping & Verification Evidence

| Spec acceptance | Test | Result |
|---|---|---|
| A.1 (eligible role + tripped breaker => WARN) | `test_wi4789_circuit_breaker_warns_when_role_dispatchable` | PASS |
| A.2 (required role with no dispatch-eligible harness => FAIL) | `test_wi4789_empty_loyal_opposition_role_fails` + existing `test_config_overlay_can_disable_dispatchability` | PASS |
| A.3 (config error => FAIL) | `test_wi4789_config_error_fails` | PASS |
| A.4 (no findings => PASS) | existing `test_collect_status_keeps_role_and_dispatchability_orthogonal` | PASS |
| A.5 (observed defect: runtime failure on eligible LO while prime dispatchable => WARN) | `test_wi4789_observed_defect_regression` + reconciled `test_wi4789_blocked_runtime_candidates_warn_when_role_dispatchable` | PASS |

Test reconciliation (FAIL => WARN; superseded semantics, per-recipient findings
still emitted):

- `test_wi4578_health_fails_for_blocked_runtime_candidates` ->
  `test_wi4789_blocked_runtime_candidates_warn_when_role_dispatchable`.
- `test_wi4578_health_fails_for_exit_zero_no_verdict_evidence` ->
  `test_wi4789_exit_zero_no_verdict_warns_when_role_dispatchable`.
- `test_wi4718_genuine_launch_reason_still_fails` ->
  `test_wi4718_genuine_launch_reason_emits_runtime_failure_finding` (asserts WARN
  for overall health; still asserts the per-recipient runtime-failure FINDING).

Commands and observed results (repo venv interpreter):

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --no-header
  => 31 passed, 1 failed (the 1 failure is pre-existing + unrelated; see below)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
  => All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
  => 2 files already formatted
```

### Pre-existing unrelated failure (disclosure)

The single failing test is `test_wi4768_live_dispatch_config_projection_drift_is_visible`.
It is PRE-EXISTING and unrelated to this change: it reads the LIVE
`config/dispatcher/rules.toml` and asserts `harness_b_rules["can_receive_dispatch"] is True`,
but the live value is `false` (`config/dispatcher/rules.toml` line 15). The
assertion fails at the test's first statement, before any code modified by this
change is reached, so this change cannot have caused it. The drift is the residue
of a prior session's dispatch-topology change that the owner DEFERRED restoring
(per the session handoff); the test is correctly surfacing that deferred drift.
All WI-4789 spec-derived tests (A.1-A.5) and the reconciled tests PASS.

## Acceptance Criteria Check

- A.1 tripped breaker + eligible role => WARN — ✓
- A.2 required role with no dispatch-eligible harness => FAIL — ✓
- A.3 config error => FAIL — ✓
- A.4 no findings => PASS — ✓
- A.5 observed defect (B dispatchable + LO runtime failure) => WARN — ✓
- ruff check + ruff format --check clean on both changed files — ✓
- No new regression beyond the pre-existing unrelated `test_wi4768` live-config-drift failure — ✓

## Risk / Rollback

One health-classification expression plus test reconciliation/additions. The
change only NARROWS FAIL; per-role "no dispatchable" and "config error" remain
FAIL triggers, so `cli.py`'s `ctx.exit(0 if status.health_status != "FAIL" else 1)`
still exits non-zero for true impossibility. Single-commit rollback = revert the
diff (source + tests bundled).

## Recommended Commit Type

`fix` — repairs the false-FAIL health-classification defect; adds and reconciles
tests; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
