NEW

# CA9165 implementation report: per-role concurrency cap for cross-harness auto-dispatch (Slice 1)

bridge_kind: implementation_report
Document: gtkb-perrole-concurrency-cap-dispatch
Version: 003 (NEW - post-implementation report)
Responds to: bridge/gtkb-perrole-concurrency-cap-dispatch-002.md
Recommended commit type: feat:

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-CA9165

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implemented the GO'd (version 002) Slice-1 per-role concurrency cap from SPEC-INTAKE-ca9165: a deterministic per-role cap that bounds how many live dispatched headless workers a single role (prime-builder / loyal-opposition) may hold, so one role cannot monopolize the global pool and starve the other role's dispatch lane. The cap is evaluated AFTER the existing global cap (WI-4472), which keeps precedence. No binary same-role active-session suppression is reintroduced.

## Changes Implemented (additive, source + test only)

1. `scripts/cross_harness_bridge_trigger.py`:
   - Constants `MAX_LIVE_DISPATCHED_PER_ROLE_ENV_VAR = "GTKB_MAX_LIVE_DISPATCHED_PER_ROLE"` and `DEFAULT_MAX_LIVE_DISPATCHED_PER_ROLE = 3` (default sits inside the global default of 8).
   - `_max_live_dispatched_per_role()` — fail-safe env reader mirroring `_max_live_dispatched_processes()` exactly (blank/invalid/<=0 -> default).
   - `_count_live_dispatched_processes_for_role(runs_dir, role_label)` — reuses the liveness + stale-sidecar-prune semantics of `_count_live_dispatched_processes`, counting only `.pid` sidecars whose `dispatch_id` contains the `-<role_label>-` token produced by `_new_dispatch_id` (the two role labels are non-overlapping, so the match is unambiguous; a transient miscount can only UNDER-count, never over-suppress).
   - In `_spawn_harness`, immediately AFTER the global-cap gate and before `_is_spawn_rate_limited`, a new per-role gate: when `per_role_live >= per_role_cap`, record a dispatch-failure meta with `reason="per_role_concurrency_cap_reached"` (plus `role`, `per_role_live`, `per_role_cap`) and return without spawning, issuing no authorization packet and acquiring no claim (same fail-closed shape as the global cap).
2. `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`: new focused test module (11 tests).

`check_target_active` / binary same-role active-session suppression is NOT reintroduced into the live dispatch path; the suppression model (per-document lease + work-intent claim) is unchanged. No KB mutation; no DCL supersession (`DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` is already retired).

## Specification Links (carried forward from the GO'd -001 proposal)

- `SPEC-INTAKE-ca9165` — the governing requirement: bounded parallel cross-harness auto-dispatch with a per-role concurrency cap superseding binary same-role active-session suppression.
- `SPEC-INTAKE-9cb2ee` — claim-gated implementation-start (Prime-side per-item dedup that makes same-role parallelism collision-safe).
- `SPEC-INTAKE-57a736` — per-document lease (LO-side per-document suppression providing same-role parallelism on different documents).
- `GOV-AUTOMATION-VALUE-VS-COST-001` — the per-role cap is the cheap deterministic gate in front of the expensive same-role spawn (the S308 lesson the spec cites).
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-STANDING-BACKLOG-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `ADR-SINGLE-HARNESS-OPERATING-MODE-001`.

## Spec-to-Test Mapping

| Specification / GO condition | Test | Result |
| --- | --- | --- |
| ca9165: per-role cap bounds concurrent same-role workers | `test_per_role_cap_suppresses_at_limit` | PASS (reason `per_role_concurrency_cap_reached`; no Popen; durable failure row) |
| GO cond. 3: same-role parallelism allowed below the cap (no binary suppression) | `test_per_role_below_cap_allows_same_role_spawn` | PASS (spawn proceeds) |
| per-role count is role-scoped, not global | `test_per_role_count_is_role_scoped` | PASS (LO=2, Prime=1, global=3) |
| GO cond. 1: global cap retains precedence (reason stays `concurrency_cap_reached`) | `test_global_cap_keeps_precedence_over_per_role` | PASS |
| fail-safe config reader | `test_per_role_cap_default_when_unset` / `_env_override` / `_invalid_or_nonpositive_falls_back` | PASS |
| counter zero for missing runs dir | `test_per_role_count_zero_for_missing_runs_dir` | PASS |

## Verification Commands + Results

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py platform_tests/scripts/test_dispatch_concurrency_cap.py -q --tb=short`: **26 passed** (11 new + 15 global-cap regression).
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q` (run with `CLAUDE_CODE_SESSION_ID` and `GTKB_NO_CROSS_HARNESS_TRIGGER` unset): **91 passed**.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`: **All checks passed!**
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check ...`: **2 files already formatted**.

GO condition 2 (no `check_target_active` reintroduction) is satisfied by construction: the change is purely additive at the spawn gate; `is_lease_held`, `_filter_prime_selected_by_work_intent`, and the `run_trigger` lease branch are untouched, and the `test_per_role_below_cap_allows_same_role_spawn` test demonstrates same-role spawn still proceeds below the cap.

## Preflight Results

### Applicability Preflight (run against this report draft via `--content-file`)

- `preflight_passed: true`; `missing_required_specs: []`.
- `missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]` — advisory-only, none block; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` does not resolve as a live MemBase spec (verify-before-cite).
- Draft packet_hash: `sha256:ec2141c98c5b12cc243118057ae2512e64a2d4a05c7e43591fd16c14b2f23106` (Loyal Opposition recomputes against the filed `-003` file).

### ADR/DCL Clause Preflight

- Clauses evaluated: 5; must_apply: 1; Evidence gaps in must_apply clauses: 0; **Blocking gaps (gate-failing): 0**; exit 0 (pass).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`: must_apply, evidence found: yes (spec-to-test table above).

## Prior Deliberations

- `DELIB-20265459` — owner re-open decision (AUQ 2026-06-21): the live backlog row identifies this as the reason CA9165 (`WI-AUTO-SPEC-INTAKE-CA9165`) is active again. This report cites it per the version-002 GO condition 4.
- `DELIB-20263189` — owner AUQ authorization (2026-06-13) for the 3 P1 dispatch specs; the direct authorization basis under the cited PAUTH.
- `bridge/gtkb-bounded-parallel-cross-harness-dispatch-003.md` — the WITHDRAWN prior thread on this topic, which flagged the per-role cap as the one genuinely-unimplemented element ca9165 named; this Slice-1 implements exactly that, with a new slug.
- `bridge/gtkb-perrole-concurrency-cap-dispatch-002.md` — the Loyal Opposition GO verdict this report responds to.

## Risk And Rollback

- Risk: per-role cap set too low throttles legitimate same-role throughput. Mitigation: default 3 (inside the global 8), env-overridable; the cap only suppresses ADDITIONAL same-role spawns once a role already holds N live workers.
- Risk: per-role count miscount after a crash leaves a stale `.pid`. Mitigation: reuses the exact liveness+prune logic of the global counter; a transient miscount can only under-count, never over-suppress, and the global cap is the hard backstop.
- Rollback: single-commit revert of `scripts/cross_harness_bridge_trigger.py`; the new test file is additive. No state-file schema change (reuses the runs-dir `.pid`/`.exit_code` sidecars), no MemBase mutation, no new runtime dependency.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
