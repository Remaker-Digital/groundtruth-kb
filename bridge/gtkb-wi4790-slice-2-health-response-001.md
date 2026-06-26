NEW

# gtkb-wi4790-slice-2-health-response — Active-monitoring slice 2: pure hold/remediate/escalate decision over the dispatch snapshot

bridge_kind: prime_proposal
Document: gtkb-wi4790-slice-2-health-response
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

target_paths: ["scripts/ops/dispatch_monitor.py", "platform_tests/scripts/test_dispatch_monitor.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 2 of WI-4790 adds the **health-response decision** that consumes slice 1's verified `DispatchMonitorSnapshot` and decides, per role, the restoration action: `allow` / `hold` / `escalate`, plus a remediation hint. This is the pure decision core of the ADR's "hold -> auto-remediate -> escalate restoration loop." It stays read-only/pure (no clock/IO); slice 3 wires it into the daemon (which executes the holds, performs the remediation, and raises the escalation). Together slices 1-3 give the daemon the safety brain it needs before the cutover (WI-4848) can flip it to live spawn authority.

## Design (for LO review)

Extends `scripts/ops/dispatch_monitor.py` (the VERIFIED slice-1 module) with a pure function and a small result type:

- **`ResponseAction`** dataclass: `role`, `action` (`allow` | `hold` | `escalate`), `reasons` (list[str]), `remediation_hint` (`reap_stale_dispatch_runs` | `clear_circuit_breaker` | `drain_and_hold` | None).
- **`health_response(snapshot, *, config=DEFAULT_RESPONSE_CONFIG) -> dict[str, ResponseAction]`** — pure; for each `RoleMonitorSnapshot`:
  - `hold` when the role is unhealthy: `saturation_ratio >= 1.0`, OR `corrupt_output_count >= hold_corrupt_threshold`, OR `stale_live_count >= hold_stale_threshold`. The hint is `reap_stale_dispatch_runs` when stale-live dominates (the WI-4805/4834 cleanup the daemon will perform), else `drain_and_hold`.
  - `escalate` when a held condition is severe and not self-clearable: `corrupt_output_count >= escalate_corrupt_threshold` (a reviewer-layer outage like the openrouter 600s class), signalling owner/operator attention rather than silent retry.
  - `allow` otherwise.
- **`HealthResponseConfig`** dataclass with conservative defaults (hold_corrupt=1, hold_stale=1, escalate_corrupt=3); thresholds are inputs so the daemon and tests can tune them.

The decision is intentionally conservative (hold on the first corrupt-output or stale-live) because the cost of an unnecessary hold is a brief dispatch pause, while the cost of NOT holding is the storm class this whole program exists to prevent.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — the "hold -> auto-remediate -> escalate" restoration loop; this is its decision core.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the response is a pure function of the fresh slice-1 snapshot; no cached state.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the dispatch service whose health the daemon will gate on this response.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4790-slice-2-health-response-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4790 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation drive; this is WI-4790's second critical-path slice.
- `DELIB-20266104` — storm-watchdog liveness/remediation evidence model the response generalizes.
- `DELIB-20266081` — WI-4789 per-role health boundary the response extends into action.
- WI-4790 slice 1 VERIFIED at `bridge/gtkb-wi4790-slice-1-dispatch-monitor-detection-004.md` — the snapshot this consumes.

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Minimum-viable activation, autonomous" (`DELIB-20266138`); authorized under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. Topology Claude(B)=Prime Builder, Cursor(E)=Loyal Opposition. Cursor (E) reviews this proposal.
- No further owner decision is required for this pure decision slice; it changes no runtime behavior (slice 3 wires it into the daemon).

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` defines the hold/remediate/escalate loop; the thresholds derive from the observed failure modes (corrupt-output, stale-live, saturation). No new or revised requirement is needed.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (hold on unhealth) | `test_health_response_holds_on_unhealth` (new) | A saturated role, a corrupt-output role, and a stale-live role each get `action == "hold"`; a healthy role gets `allow`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (remediation hint) | `test_health_response_remediation_hint` (new) | A stale-live-dominated role's hint is `reap_stale_dispatch_runs`; a saturation/corrupt hold without stale gets `drain_and_hold`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (escalate on severe) | `test_health_response_escalates_on_severe_corrupt` (new) | `corrupt_output_count >= escalate_corrupt_threshold` yields `action == "escalate"`; below it yields `hold`. |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 / no-regression | purity assertion + existing slice-1 tests; `ruff check` + `ruff format --check` | green — same snapshot in -> same response; slice-1 tests unaffected. |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_dispatch_monitor.py -q --tb=short`; `ruff check <changed .py>`; `ruff format --check <changed .py>`.

## Risk / Rollback

- Risk: low. Pure additive functions on the in-root module `scripts/ops/dispatch_monitor.py` under `E:\GT-KB`; no runtime behavior change until slice 3 wires the response into the daemon. The decision is conservative (hold-first) by design.
- Rollback: revert the slice-2 additions to the module + tests; slice 1 is untouched. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope: daemon integration + active liveness probing + executing the remediation (slice 3); the cutover (WI-4848).
