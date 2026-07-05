GO

# Loyal Opposition Review — WI-5023 Storm Watchdog Governed CLI Parity (Slice 1)

bridge_kind: lo_verdict
Document: gtkb-dispatcher-complex-watchdog-cli-parity
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-05 UTC
Reviewer: Loyal Opposition
Responds-To: bridge/gtkb-dispatcher-complex-watchdog-cli-parity-001.md
Verdict: GO

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T07-29-05Z-loyal-opposition-B-a2d09b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched Loyal Opposition worker; ::init gtkb lo; resolved role loyal-opposition

Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5023

## Verdict

GO. The Slice-1 implementation proposal for WI-5023 (storm watchdog governed CLI parity) is approved to proceed within the declared `target_paths`.

The proposal is structurally complete, its premise is independently verified true, both mandatory preflights are clean, all cited specifications exist in MemBase, and the design is a faithful mirror of the already-shipped dispatcher supervisor control surface while preserving runtime fault isolation. This GO authorizes only Slice 1 (watchdog control API + `gt` CLI group + doctor check + governed installer + tests); it does not authorize the Slice 2 `complex` group, the Slice 3 `health` rollup, or the Slice 4 doctor delegation.

## Separation Check

The proposal (`-001`) was authored by Prime Builder (Claude, harness B) interactive session `f128ea1d-e645-49bf-93a5-72661ec0d0c7`. This verdict is authored from an independent Loyal Opposition session (Claude, harness B, auto-dispatched worker session `2026-07-05T07-29-05Z-loyal-opposition-B-a2d09b`). Reviewer and author session contexts differ, satisfying the session-context review-independence gate. Per `.claude/rules/file-bridge-protocol.md` § Review Independence Boundary, a shared harness ID (both B) is NOT the review boundary — session context is — so this cross-session, same-harness review is valid.

## Applicability Preflight

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-complex-watchdog-cli-parity --json
```

Observed (exit 0):

- packet_hash: `sha256:d579cc964f5d49bf9c1628cc045b77442c8803f7c4d01045f5714c90320dc80e`
- operative_file: `bridge/gtkb-dispatcher-complex-watchdog-cli-parity-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

The applicability preflight is clean; this GO is not conditioned on any missing cross-cutting spec.

## Clause Applicability

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatcher-complex-watchdog-cli-parity
```

Observed (exit 0):

- Operative file: `bridge/gtkb-dispatcher-complex-watchdog-cli-parity-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

The clause preflight is clean; no blocking clause gap.

## Prior Deliberations

The proposal's Prior Deliberations were independently confirmed to exist in the Deliberation Archive:

- `INTAKE-6554ff58` — the requirement candidate captured for this project. Confirmed present.
- `DELIB-202665470` — the dispatch resume decision whose investigation surfaced the watchdog CLI gap. Confirmed present.
- `DELIB-20266276` — the ADR-DISPATCHER-ARCHITECTURE-001 daemon-resilience lineage that established the watchdog as a separate resilience task. Confirmed present.

A `gt deliberations search` for the dispatcher watchdog CLI-parity topic returned no additional prior deliberation revisiting this design.

## Premise Verification (Positive Confirmations)

Independently inspected by this reviewer:

- **All cited specifications exist in MemBase.** `SPEC-INTAKE-5e9375` (requirement, specified), `ADR-DISPATCHER-COMPLEX-CLI-001` (architecture_decision, specified), `ADR-DISPATCHER-ARCHITECTURE-001` (architecture_decision, specified), `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` (design_constraint, specified), `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (requirement, specified), plus the mandatory-gate DCLs and `GOV-FILE-BRIDGE-AUTHORITY-001` (verified). The anchor ADR the slice implements exists as a formally-inserted artifact.
- **CLI-gap premise is TRUE.** `groundtruth-kb/src/groundtruth_kb/cli.py` line 1196 defines `@bridge_dispatch_daemon_group.group("supervisor")` with `status/install/enable/disable/uninstall` commands (WI-4937) backed by `DispatcherSupervisorError`. A content scan of `cli.py` for `watchdog`/`supervisor` returns supervisor matches only — there is NO existing `daemon watchdog` command group. The storm watchdog is therefore the only complex member without governed `gt` CLI parity, as claimed.
- **Supervisor parallel exists.** `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py` defines `collect_supervisor_status` (line 73), `install_supervisor` (196), `enable_supervisor` (223), `disable_supervisor` (233), `uninstall_supervisor` (243) — the exact API shape the proposal mirrors for the new `dispatcher_watchdog.py`.
- **Deliverables correctly absent.** `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py` and `scripts/install_storm_watchdog_task.ps1` do not yet exist (they are Slice-1 deliverables); `scripts/install_dispatcher_daemon_task.ps1` exists as the installer parallel.
- **Storm watchdog is a real task.** `GTKB-HarnessStormWatchdog` is referenced in `scripts/gtkb_dispatcher_daemon.py`, `scripts/install_dispatcher_daemon_task.ps1`, and prior VERIFIED WI threads (WI-4780 kill-switch strip, storm-watchdog liveness-aware reaping, noncodex process-family detection).
- **Project/WI linkage valid.** `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI` is active with WI-5023 (Slice 1) .. WI-5026 (Slice 4) plus the intake WI; WI-5023 is a member of that project.
- **In-root placement.** All `target_paths` are under `groundtruth-kb/src/`, `scripts/`, and `platform_tests/` — platform placement within the project root, satisfying `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Owner Authorization Note (advisory; not a GO blocker)

No project authorization (`PAUTH-*`) currently exists for `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI`, and the proposal carries no `Project Authorization:` header line. This is NOT a GO blocker: `scripts/implementation_authorization.py` treats project authorization as optional (the packet is built with `project_authorization = None` when no `Project Authorization:` line is cited — line 1320 adds it only `if project_authorization is not None`). The proposal's owner-approval evidence is its `## Owner Decisions / Input` AUQ record ("Approve — land it all") plus the durably-inserted `ADR-DISPATCHER-COMPLEX-CLI-001` (formal ADR insertion itself requires owner approval) and the active project/WIs.

Advisory: because this is Slice 1 of a 4-slice program, the owner may wish to mint a `PAUTH` covering `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI` so slices 2–4 inherit a durable bounded authorization and the "land it all" approval has a persistent record. This is a suggestion for owner consideration, not a condition of this GO.

## GO Conditions

1. Keep implementation strictly within the declared `target_paths` under the project root.
2. Preserve runtime fault isolation per `ADR-DISPATCHER-ARCHITECTURE-001`: the watchdog control surface must not merge the watchdog with the supervisor or daemon, must not touch the daemon lock, and must not modify the supervisor/daemon task. The proposal's `test_dispatcher_watchdog_control.py` fault-isolation assertion must exercise this.
3. Mirror the VERIFIED supervisor installer posture (pythonw launcher, hidden window) and the WI-4896 console-residual fix; the new doctor check must assert `uses-pythonw` for `GTKB-HarnessStormWatchdog`, structurally identical to the supervisor check.
4. Before any protected edit, create the implementation-start authorization packet from this GO: `python scripts/implementation_authorization.py begin --bridge-id gtkb-dispatcher-complex-watchdog-cli-parity`.
5. The implementation report must carry forward the spec-to-test mapping with executed commands and observed results, and MUST run BOTH `ruff check` and `ruff format --check` on every changed Python file (separate gates) before filing, per `.claude/rules/file-bridge-protocol.md`.

## Spec-Derived Verification Expectations (carried into the implementation report)

| Specification / clause | Required implementation-report evidence |
|---|---|
| `ADR-DISPATCHER-COMPLEX-CLI-001` decision 2 (watchdog CLI parity) | `test_bridge_dispatch_daemon_watchdog.py` asserts the `gt bridge dispatch daemon watchdog {status,install,enable,disable,uninstall}` verbs exist and dispatch to the control API. |
| Watchdog-control API | `test_dispatcher_watchdog_control.py` unit tests for install/enable/disable/uninstall/status against a nonce-suffixed task. |
| Doctor watchdog check | Doctor test asserts the `GTKB-HarnessStormWatchdog` check reports registered/enabled/hidden/uses-pythonw. |
| Fault isolation (`ADR-DISPATCHER-ARCHITECTURE-001`) | Assertion that the watchdog control path does not touch the supervisor/daemon task or the daemon lock. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report includes the executed pytest command + results and both ruff gates. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Latest thread status `GO` before implementation start; project/WI/target_paths remain parseable. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changes remain under the project root at platform placement. |

## Owner Action Required

None. This verdict is filed from a headless auto-dispatched worker that cannot solicit owner input. The owner-authorization note above is advisory; no owner decision blocks Slice-1 implementation.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
