NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f0cf7-9439-7cc3-8b58-cdad991c5890
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop Prime Builder interactive session

# GT-KB Bridge Implementation Proposal - gtkb-wi4887-dispatch-chaos-fault-injection-harness - 001

bridge_kind: prime_proposal
Document: gtkb-wi4887-dispatch-chaos-fault-injection-harness
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4887
Recommended commit type: test:

target_paths: ["scripts/ops/dispatch_load_harness.py", "scripts/ops/dispatch_chaos_harness.py", "platform_tests/scripts/test_dispatch_chaos_harness.py"]

implementation_scope: source_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Implement WI-4887 by adding a deterministic STUB-only chaos and fault-injection harness for daemon-resilience recovery tests.

The harness will model the failure modes selected by `DELIB-20266276` without killing real processes, starting the live daemon, invoking real harnesses, or spending provider calls:

- daemon death
- worker hang
- worker crash
- spawn storm
- corrupt daemon state
- harness saturation
- provider outage

The implementation will produce machine-readable JSON reports that show the detected failure, selected recovery action, recovery-cycle expectation, final state, degraded components, owner-alert requirement, and audit events. The tests will become the standing deterministic resilience regression suite for the Phase 5 slice.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, Work Item, and inline JSON `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the governing daemon-resilience ADR and DCLs that define the failure modes and recovery expectations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map each recovery behavior to tests derived from linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected script/test implementation requires live bridge `GO`, a work-intent claim, and an implementation-start packet.
- `GOV-STANDING-BACKLOG-001` - WI-4887 is the MemBase-backed backlog item selected under `PROJECT-GTKB-DISPATCHER-RELIABILITY`.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the resilience addendum selects STUB load/chaos verification, full auto-recovery, degraded continuity, and fleet-saturation caps.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - recovery and reroute decisions must stay centralized in the dispatcher service and audit trail.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - each selected failure mode requires bounded automatic recovery behavior and deterministic STUB verification.
- `DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001` - component failures must circuit-break or disable only the failing component while healthy components remain eligible when safe.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` - daemon-death and corrupt-state recovery must not create duplicate daemon owners.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - daemon-death recovery must model the dedicated supervisor ensure-alive path rather than dispatching work directly.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - the harness must not move dispatch control, target selection, or suspension authority into real harness sessions.

## Requirement Sufficiency

Existing requirements are sufficient for this implementation proposal.

WI-4887 is explicitly scoped by `DELIB-20266276` and covered by the active daemon-resilience project authorization. The Phase 0 ADR/DCL records define the required failure modes, recovery behavior, degradation policy, single-instance boundary, and STUB-chaos verification posture.

Implementation should remain conditional on two upstream bridge outcomes:

- If the WI-4884 Phase 0 formalization thread is rejected or materially changes the daemon-resilience DCL text, this proposal must be revised before implementation starts.
- If the WI-4886 load harness proposal is rejected or lands with materially different target paths or scheduler vocabulary, this proposal must be revised before implementation starts.

No new owner input is requested.

## Target Paths

The implementation is limited to:

- `scripts/ops/dispatch_load_harness.py`
- `scripts/ops/dispatch_chaos_harness.py`
- `platform_tests/scripts/test_dispatch_chaos_harness.py`

No configuration, harness registry, live daemon state, scheduled-task state, bridge runtime state, formal artifact, MemBase, credential, deployment, or generated adapter files are in scope.

## Implementation Plan

1. Build on the WI-4886 STUB worker/load model once that thread is approved and implemented.
2. Add `scripts/ops/dispatch_chaos_harness.py` with a pure in-memory scenario runner and a small CLI.
3. Define an explicit failure-mode catalog for daemon death, worker hang, worker crash, spawn storm, corrupt state, harness saturation, and provider outage.
4. Model recovery outcomes as deterministic state transitions: supervisor restart, reap and redispatch, storm suppression, checkpoint or safe-empty reset, cap backoff, provider circuit-break, healthy-fleet reroute, blocked state, and owner-visible alert.
5. Keep all time expectations cycle-based rather than wall-clock sleeps: supervisor interval, daemon lifecycle sweep, watchdog/recovery cycle, lifetime-cap expiry, and failure-threshold reached.
6. Emit JSON suitable for future dispatcher health/status integration without writing live dispatcher state.
7. Add focused tests in `platform_tests/scripts/test_dispatch_chaos_harness.py`.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not read, print, embed, or require credentials; provider outage is modeled as a symbolic STUB state. | Bridge helper credential scan, focused test review, and no credential/environment access in target diff. | |
| CQ-PATHS-001 | Yes | Limit implementation to the three declared target paths. | Implementation-start target validation, `git diff --name-only`, and bridge applicability preflight. | |
| CQ-COMPLEXITY-001 | Yes | Represent failure modes, recovery actions, and final states as small enums/dataclasses with table-driven scenarios. | Ruff check plus focused test review of scenario table coverage. | |
| CQ-CONSTANTS-001 | Yes | Name cycle labels, failure-mode tokens, recovery-action tokens, and default caps as constants or enums. | Ruff check and tests asserting the expected scenario/report tokens. | |
| CQ-SECURITY-001 | Yes | Do not spawn subprocesses, kill processes, touch live daemon state, mutate dispatcher config, or invoke real harness/provider paths. | `test_chaos_harness_does_not_spawn_or_kill_real_processes` plus target diff review for subprocess/live-state calls. | |
| CQ-DOCS-001 | Yes | Provide concise module/CLI help describing STUB-only behavior, scenario names, and JSON report fields. | CLI `--help` assertion or direct parser/help test. | |
| CQ-TESTS-001 | Yes | Add deterministic tests for every required failure mode, degraded continuity, single-instance preservation, isolation, and JSON report shape. | `python -m pytest platform_tests/scripts/test_dispatch_chaos_harness.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | The harness emits structured JSON reports rather than runtime logs. | Target diff review confirms no new logging behavior. | No runtime logging surface is added. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge applicability preflight, and ADR/DCL clause preflight before reporting implementation. | Command output included in the post-implementation report. | |

## Out Of Scope

- Real daemon process kill, restart, or scheduled-task mutation.
- Real harness invocation or real provider calls.
- Live dispatcher state mutation.
- Topology changes or Antigravity activation.
- Phase 6 sustained live fleet run and real-harness smoke acceptance.
- MemBase or formal artifact mutation.
- Owner alert delivery implementation beyond deterministic report fields.

## Owner Decisions / Input

No new owner input is requested.

Relevant existing decisions:

- `DELIB-20266276` - daemon-resilience program scope lock, including failure modes, STUB load/chaos posture, degraded continuity, fleet-saturation target, and either-PB routing.
- `DELIB-20266354` - owner approval of the Phase 0 formal-artifact bodies that define the ADR/DCL basis for this slice.

## Prior Deliberations

- `DELIB-20265888` - selected harness/dispatch isolation architecture.
- `DELIB-20266084` - dispatcher daemon foundation and daemon-death detection lessons.
- `DELIB-20266276` - selected daemon-resilience program scope, failure modes, and STUB load/chaos strategy.
- `DELIB-20266354` - approved Phase 0 ADR/DCL content now recorded in MemBase.
- `bridge/gtkb-wi4884-daemon-resilience-formalization-011.md` - latest WI-4884 implementation report awaiting Loyal Opposition verification.
- `bridge/gtkb-wi4886-mock-worker-load-scale-harness-001.md` - Phase 4 STUB load/scale proposal that this Phase 5 proposal should build on after approval.

## Spec-Derived Verification Plan

- `ADR-DISPATCHER-ARCHITECTURE-001`: `test_chaos_matrix_covers_resilience_addendum_failure_modes` proves the harness includes daemon death, worker hang, worker crash, spawn storm, corrupt state, saturation, and provider outage as deterministic STUB scenarios.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001`: `test_each_failure_mode_has_bounded_recovery_action` proves each selected failure mode maps to a recovery action and cycle expectation without owner action.
- `DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001`: `test_provider_outage_circuit_breaks_one_component_and_keeps_healthy_fleet` proves a failing component is isolated while healthy alternatives remain eligible when safe.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001`: `test_daemon_death_recovery_preserves_single_owner` proves daemon restart modeling never permits two owners of queue/recovery state.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`: `test_daemon_death_uses_supervisor_restart_not_dispatch_directly` proves daemon-death recovery models the ensure-alive supervisor path rather than a dispatch worker path.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`: `test_chaos_harness_does_not_spawn_or_kill_real_processes` proves the harness does not call real harness, subprocess, task, or process-kill surfaces.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: `test_recovery_report_contains_centralized_audit_events` proves recovery decisions and reroutes are represented as centralized dispatcher audit events.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the post-implementation report must include exact focused pytest, Ruff, format-check, bridge applicability, and ADR/DCL preflight outputs.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: before implementation, Prime Builder must acquire a work-intent claim and create an implementation-start packet from the live latest `GO`; protected target validation must pass for all target paths.

## Verification Commands

```powershell
python -m pytest platform_tests/scripts/test_dispatch_chaos_harness.py -q --tb=short
python -m ruff check scripts/ops/dispatch_load_harness.py scripts/ops/dispatch_chaos_harness.py platform_tests/scripts/test_dispatch_chaos_harness.py
python -m ruff format --check scripts/ops/dispatch_load_harness.py scripts/ops/dispatch_chaos_harness.py platform_tests/scripts/test_dispatch_chaos_harness.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4887-dispatch-chaos-fault-injection-harness
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4887-dispatch-chaos-fault-injection-harness
```

## Acceptance Criteria

- The harness covers all seven daemon-resilience failure modes selected by `DELIB-20266276`.
- Every failure mode produces a deterministic recovery action, cycle expectation, final state, and audit event.
- Worker hang and crash scenarios are reaped and redispatched when safe.
- Spawn storm and harness saturation scenarios never exceed per-harness one-worker caps.
- Corrupt state scenarios recover to a checkpoint or safe-empty state with audit evidence.
- Provider outage scenarios circuit-break only the failing component and surface degraded state.
- Daemon-death scenarios model supervisor restart while preserving single daemon ownership.
- Tests prove no real harness/provider subprocess, process kill, scheduled task, or live daemon mutation occurs.
- The implementation stays within the three target paths.

## Risk And Rollback

Risk is moderate because the slice creates the vocabulary and fixtures that later Phase 6 acceptance may rely on. The main risk is modeling recovery too abstractly to catch useful daemon defects. Mitigation: align failure-mode names, recovery actions, cap behavior, degraded-state fields, and audit vocabulary with the Phase 0 ADR/DCL text and the WI-4886 load-harness concepts.

Rollback is deletion of the new chaos harness and focused test file plus reversal of any WI-4886 load-harness extension made by this slice before VERIFIED. After VERIFIED, replacement should go through a follow-up bridge thread so Phase 6 references remain auditable.
