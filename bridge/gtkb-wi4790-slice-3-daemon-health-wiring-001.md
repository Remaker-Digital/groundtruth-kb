NEW

# gtkb-wi4790-slice-3-daemon-health-wiring — Active-monitoring slice 3: wire detection + response into the daemon tick + health status

bridge_kind: prime_proposal
Document: gtkb-wi4790-slice-3-daemon-health-wiring
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4790

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 3 completes WI-4790 by wiring the VERIFIED detection (slice 1 `compute_snapshot`) and response (slice 2 `health_response`) into the dispatcher daemon's tick, so the daemon **actively monitors** each cycle and **exposes its health**. This is the capability the ADR requires before the cutover (WI-4848) can flip the daemon to live spawn authority: the daemon must know its own health and the per-role hold/escalate posture. The daemon remains in shadow mode (no spawning) in this slice — slice 3 adds the monitoring/health output to the tick; the live spawn-gating-on-health happens at cutover.

## Design (for LO review)

Extends `scripts/gtkb_dispatcher_daemon.py`:

- **`_load_dispatch_monitor()`** — importlib loader for `scripts/ops/dispatch_monitor.py`, mirroring the existing `_load_trigger_module()` pattern (no package dependency on `scripts/ops`).
- **`run_tick`** — after computing the shadow decisions (unchanged), additionally:
  - `outcomes = dispatch_monitor.gather_outcomes(project_root)` (read-only),
  - `snapshot = dispatch_monitor.compute_snapshot(outcomes, caps={}, now=time.time())`,
  - `response = dispatch_monitor.health_response(snapshot)`,
  - include `monitoring` (`snapshot.to_json_dict()`) and `health` (per-role `{action, reasons, remediation_hint}`) in the tick result and in `status.json`.
  - The whole monitoring block is wrapped fail-soft: a monitoring error never breaks the tick (the daemon still computes decisions + heartbeat); it records a `monitoring_error` field instead.
- The daemon stays **shadow** (no spawn). Caps default for now (`caps={}` -> `DEFAULT_PER_ROLE_CAP`); reading real per-role caps from the dispatch config is a noted refinement, not required for the health surface.

Net effect: the daemon's `status.json` now carries a live, per-role health posture (`allow`/`hold`/`escalate` + reasons) derived from fresh dispatch evidence each tick — the observable health the cutover will gate spawning on.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — the daemon owns liveness/quality/health; this wires active monitoring into the daemon so health is daemon-owned and observable.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the dispatch service whose health the daemon now computes each tick.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the tick recomputes the snapshot from fresh dispatch evidence; no cached health.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4790-slice-3-daemon-health-wiring-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4790 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation drive; WI-4790's final slice.
- `DELIB-20266084` — WI-4787 daemon foundation (`run_tick` / shadow mode) this extends.
- WI-4790 slice 1 VERIFIED (`-004`) + slice 2 VERIFIED (`-004`) — the detector + response this wires in.

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Minimum-viable activation, autonomous" (`DELIB-20266138`); authorized under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. Topology Claude(B)=Prime Builder, Cursor(E)=Loyal Opposition. Cursor (E) reviews this proposal.
- Owner AUQ (2026-06-26): "Stay min-viable" — confirmed the activation set (WI-4790 -> WI-4788 -> WI-4848) and that the GO'd sibling WI-4793 stays with a fleet PB session; this slice continues the approved path.
- No further owner decision is required; the daemon stays shadow (no spawn). The cutover that uses this health to gate spawning is the separate owner-gated WI-4848.

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` requires the daemon to own health; this is the wiring. No new or revised requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (daemon owns health) | `test_run_tick_includes_health_monitoring` (new, in `test_gtkb_dispatcher_daemon.py`) | `run_tick(tmp)` result and the written `status.json` include `monitoring` (a snapshot dict with `per_role`) and `health` (a per-role dict); on a fresh root both are present and well-typed. |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fail-soft, no tick break) | `test_run_tick_monitoring_failsoft` (new) | When the monitor loader/compute raises (monkeypatched), `run_tick` still returns decisions + writes heartbeat and records a `monitoring_error` rather than raising. |
| ADR-DISPATCHER-ARCHITECTURE-001 (shadow preserved) | existing daemon shadow test | unchanged — slice 3 spawns nothing. |
| No-regression | existing daemon tests; `ruff check` + `ruff format --check` | green. |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`; `ruff check <changed .py>`; `ruff format --check <changed .py>`.

## Risk / Rollback

- Risk: low. Additive to `run_tick` on the in-root daemon `scripts/gtkb_dispatcher_daemon.py` under `E:\GT-KB`; the monitoring block is fail-soft, the daemon stays shadow (no spawn), and the only behavior change is a richer `status.json`.
- Rollback: revert the `run_tick` additions + the loader; the daemon returns to decision-only shadow ticks. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope: spawn-gating on health (the cutover, WI-4848); reading real per-role caps from the dispatch config (refinement); the WI-4788 gate activation.
