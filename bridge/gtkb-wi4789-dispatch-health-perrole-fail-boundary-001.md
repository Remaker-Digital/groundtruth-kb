NEW

# gtkb-wi4789-dispatch-health-perrole-fail-boundary — Dispatch health FAIL only for per-role dispatch impossibility, not recoverable runtime failures

bridge_kind: prime_proposal
Document: gtkb-wi4789-dispatch-health-perrole-fail-boundary
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

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

## Summary

`compute_bridge_dispatch_status` in `bridge_dispatch_config.py` currently sets
overall `health_status = FAIL` whenever any health finding contains
`"dispatch runtime failure"` (lines 319-330). Candidate selection
(`select_dispatch_candidates`) gates only on config/topology eligibility (active
status, role membership, `can_receive_dispatch`, matching rules, quality floor)
and never on runtime backoff. Consequently a recoverable runtime failure on a
still-eligible recipient — for example a tripped circuit breaker with pending
work — forces FAIL even when one or more harnesses remain dispatchable. This is
the observed defect: `gt bridge dispatch status` reported FAIL while harness B
was dispatchable.

Per `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` v2 (per-role FAIL), overall
`health_status` MUST be FAIL only when dispatch is genuinely impossible: a
configuration error, or at least one required dispatch role with no
dispatch-eligible harness. Recoverable runtime failures yield WARN.

This proposal removes the `dispatch runtime failure` clause from the FAIL
condition so FAIL is driven only by the per-role "no active dispatchable harness
is eligible for role" / "no active harness holds role" findings and
`config error` findings. The per-recipient `severity` (lines 653-657) is a
separate diagnostic label and is intentionally unchanged. Three existing tests
that assert FAIL for runtime-failure-while-eligible are reconciled to WARN (they
encoded the now-superseded semantics), and regression tests for spec acceptance
A.1-A.5 are added.

## Specification Links

- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` (v2) — the governing requirement;
  defines per-role FAIL / WARN / PASS and the explicit constraint that a
  recoverable runtime failure must not by itself produce FAIL while the affected
  role retains a dispatch-eligible harness. This proposal implements it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is
  filed and versioned per the no-index bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: this
  proposal cites the governing spec and derives its tests from it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project /
  Work Item / Project Authorization metadata is present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the
  verification plan maps each spec acceptance clause to an executed test.
- `GOV-STANDING-BACKLOG-001` — WI-4789 is the governing backlog item
  (PROJECT-GTKB-DISPATCHER-COMPLETION, Phase 0).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — preserved: the change
  keeps the artifact graph intact (governing spec created, tests derived from
  it, with a post-implementation report and VERIFIED verdict to follow).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserved: the work is
  captured as durable artifacts (spec, PAUTH, bridge thread, tests) rather than
  as a transient change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — preserved: lifecycle states
  are respected (spec versioned v1 -> v2; WI-4789 transitions
  backlogged -> resolved on VERIFIED).

## Prior Deliberations

- `DELIB-20265882` — Dispatcher target-architecture grill resolutions (owner
  decision, 2026-06-24). Its "Health semantics" framing is the source of the
  FAIL/WARN definition and explicitly names the FAIL/WARN health bug as a
  Phase 0 acute fix. This proposal implements that Phase 0 item.
- No prior deliberation addressed the dispatch health-status computation
  specifically; `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` is the first formal
  definition of these semantics, so this proposal does not revisit a previously
  rejected approach. The scaffold-seeded INTAKE-* / TAFE / restore-poller
  candidates concern dispatch routing and scheduling, not health-status
  classification, and are not relied upon here.

## Owner Decisions / Input

This work is owner-authorized; the relevant durable decisions are:

- `DELIB-20265882` (owner decision, AUQ-backed — its content states "All 10
  branches resolved via AskUserQuestion") authorizes Phase 0 stabilization
  including the "FAIL/WARN health bug".
- AUQ 2026-06-25 (this session): owner approved creating
  `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` as written.
- AUQ 2026-06-25 (this session): owner selected the **per-role FAIL** boundary
  (a required role with no dispatch-eligible harness is FAIL; recoverable
  runtime failures are WARN), captured in spec v2 and
  `PAUTH-WI-4789-DISPATCH-HEALTH-PERROLE-FAIL-001`.

No further owner decision is required to implement.

## Requirement Sufficiency

Existing requirements sufficient — `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001`
v2 (governing) plus the cited bridge-governance specs fully constrain the
change. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

All tests live in `platform_tests/scripts/test_bridge_dispatch_config.py` and
run with:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --no-header
```

Spec-acceptance to test mapping (`SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` v2):

- A.1 (each required role has >=1 dispatch-eligible harness + a tripped breaker
  with pending work => WARN) => new test
  `test_wi4789_runtime_failure_warns_when_role_dispatchable`, plus the
  reconciled `test_wi4578_*` cases.
- A.2 (a required role has no dispatch-eligible harness => FAIL) => existing
  `test_config_overlay_can_disable_dispatchability` (asserts FAIL; unchanged by
  this fix) plus a new explicit `test_wi4789_empty_required_role_fails`.
- A.3 (config error => FAIL) => new test `test_wi4789_config_error_fails`
  exercising the `config.errors` path.
- A.4 (no findings => PASS) => existing
  `test_collect_status_keeps_role_and_dispatchability_orthogonal` (asserts PASS).
- A.5 (regression: runtime failure on a still-eligible loyal-opposition
  recipient while prime-builder remains dispatchable => WARN) => the reconciled
  `test_wi4578_health_fails_for_blocked_runtime_candidates` (now WARN) plus a
  new `test_wi4789_observed_defect_regression`.

Test reconciliation (FAIL => WARN; these encoded the superseded definition,
which `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` v2 supersedes — the
per-recipient "dispatch runtime failure" finding is still emitted; only the
overall `health_status` aggregation changes):

- `test_wi4578_health_fails_for_blocked_runtime_candidates` => assert WARN.
- `test_wi4578_health_fails_for_exit_zero_no_verdict_evidence` => assert WARN.
- `test_wi4718_genuine_launch_reason_still_fails` => assert WARN. (The companion
  `test_wi4718_absent_launch_reason_still_fails`, which asserts
  `_runtime_findings_for_recipient` emits the failure finding, is unchanged.)

Also run on the changed files:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
```

## Risk / Rollback

The risk surface is one health-classification expression in
`compute_bridge_dispatch_status` plus the affected test expectations. The change
narrows FAIL (fewer false FAILs) and cannot newly mask a genuine
dispatch-impossibility: per-role "no dispatchable harness" findings and
`config error` findings remain FAIL triggers, so the exit-code consumer in
`cli.py` (`ctx.exit(0 if status.health_status != "FAIL" else 1)`) still exits
non-zero for true impossibility. Single-commit rollback: revert the one commit;
the source and test changes are bundled together.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4789-dispatch-health-perrole-fail-boundary`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs broken health-classification behavior (false FAIL on
recoverable runtime failures); no new capability surface is added.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
