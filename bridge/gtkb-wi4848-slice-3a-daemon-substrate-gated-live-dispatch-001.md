NEW

# gtkb-wi4848-slice-3a-daemon-substrate-gated-live-dispatch — Arm the daemon's live-dispatch behind the substrate selector (held inert)

bridge_kind: prime_proposal
Document: gtkb-wi4848-slice-3a-daemon-substrate-gated-live-dispatch
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
Work Item: WI-4848

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

First slice of the go-live flip, per the owner's "build flip, hold the switch" decision (AUQ 2026-06-26). It gives the dispatcher daemon a **substrate-gated live-dispatch path**: when `harness-state/bridge-substrate.json` names the daemon as the active substrate, the daemon spawns workers for its (now-reconciled) decisions; for every other substrate value — including today's default `cross_harness_trigger` — it stays in shadow (records, never spawns). Because the selector defaults to `cross_harness_trigger` AND the governed `gt mode set-bridge-substrate` CLI does not yet accept the daemon substrate (that registration is slice 3b), the live path is **doubly inert** and cannot be reached in production by this slice. This is the "armed, switch held" state: the capability exists; the selector that would fire it is untouched.

## Why a substrate gate (not a flag)

The platform already owns atomic substrate cutover: `cross_harness_bridge_trigger.run_trigger` self-inerts the moment `bridge-substrate.json` names anything other than `cross_harness_trigger` (L3594-L3609, `_is_cross_harness_trigger_active_substrate`), and `single_harness_bridge_dispatcher` is a working non-trigger substrate with its own `_spawn_worker`. Gating the daemon's live-dispatch on the same selector means the off-state is the *default selector value*, not a flag someone must remember to leave unset — and "inert the trigger" + "rollback" become the existing governed `set-bridge-substrate` transaction, not bespoke wiring. This realizes `DELIB-20265888` (dispatch is triggered by the dispatcher service, not harness hooks).

## Design (for LO review)

In `scripts/gtkb_dispatcher_daemon.py`:

- `_active_substrate(project_root) -> str` — read `harness-state/bridge-substrate.json`'s `substrate` field (default `"cross_harness_trigger"` when absent/unreadable; fail-soft).
- `DAEMON_SUBSTRATE = "dispatcher_daemon"` constant.
- `run_tick(..., )`: after computing decisions, branch on `_active_substrate(project_root)`:
  - `== DAEMON_SUBSTRATE` → **live**: for each dispatch decision, spawn a worker by reusing the trigger's existing `_spawn_harness` launch (the same call the live trigger makes), with per-recipient signature dedup against the dispatch-state so an unchanged signature does not re-spawn (the `single_harness_bridge_dispatcher` discipline). Record the live result in `status.json` (`mode: "live"`).
  - otherwise → **shadow** (today's behavior; `mode: "shadow"`), unchanged.
- The WI-4790 monitoring/health wiring and the WI-4848 slice-2 `remaining_items` reconciliation are untouched and apply in both modes.

**Held-inert guarantees (both must be removed, by separate deliberate steps, to ever fire):**
1. `bridge-substrate.json` stays `cross_harness_trigger` (this slice does not write it).
2. `gt mode set-bridge-substrate` does not accept `dispatcher_daemon` yet (slice 3b registers it), so the selector cannot be moved to the daemon through the governed path.
3. Dispatch remains quiesced (`can_receive_dispatch=false`), so even a forced selector flip resolves zero targets.

## Out of scope (later slices)

- **3b:** register `dispatcher_daemon` in the `set-bridge-substrate` transaction enum (so the switch is governed) + the readiness/provider-backoff parity gates the live trigger applies.
- **3c:** doctor check (active substrate + daemon readiness) + the rollback runbook.
- **The switch (held):** `set-bridge-substrate dispatcher_daemon` + dispatch re-enable — the owner's deliberate one-command go.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — the daemon is the GT-KB-owned dispatcher; this arms its live-spawn behind the substrate selector per the retire-the-substrate pattern.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the dispatch service whose live-spawn path this adds (gated).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the active substrate is read fresh from `bridge-substrate.json` each tick.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4848-slice-3a-daemon-substrate-gated-live-dispatch-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4848 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision; "build flip, hold switch" AUQ (2026-06-26) selects this path.
- `DELIB-20265888` — harness/dispatch isolation (dispatch triggered by the dispatcher service + artifact deposit, not harness hooks) — the architecture this realizes.
- `DELIB-20266084` — WI-4787 daemon foundation. WI-4848 slices 1-2 VERIFIED (parity harness + decision reconciliation).

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Pragmatic: reconcile + flip" then "Build flip, hold the switch" — authorizes building the flip mechanism while leaving dispatch quiesced and the switch unthrown, under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. This slice is held inert by construction (the selector stays `cross_harness_trigger`; the governed CLI cannot select the daemon substrate until 3b). The deliberate go-live remains a separate owner step. No further owner decision required for this slice.

## Requirement Sufficiency

Existing requirements sufficient — the live-dispatch target is the trigger's existing, tested worker-spawn (`_spawn_harness`) under the existing substrate-selector contract. No new or revised requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (inert by default) | `test_daemon_default_substrate_stays_shadow` (new) | with no/`cross_harness_trigger` `bridge-substrate.json`, `run_tick` records shadow decisions and **spawns nothing** (`subprocess.Popen` patched to fail if called); `status.json` `mode == "shadow"`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (substrate-gated live) | `test_daemon_daemon_substrate_dispatches` (new) | with `bridge-substrate.json` `substrate=dispatcher_daemon` and a dispatchable synthetic state, `run_tick` enters live mode and invokes the spawn path (patched `_spawn_harness`/`Popen` asserted called); `status.json` `mode == "live"`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (shadow preserved) | existing daemon shadow/no-spawn tests | unchanged for the default substrate. |
| No-regression | full daemon test file; `ruff check` + `ruff format --check` | green. |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`; `ruff check`/`ruff format --check` on the changed files; confirm `harness-state/bridge-substrate.json` is unmodified (`substrate == cross_harness_trigger`).

## Risk / Rollback

- Risk: low *by construction*. The live branch is unreachable in production this slice (selector default + ungoverned daemon substrate + quiesce). The only reachable behavior is the unchanged shadow path. Changes confined to the in-root daemon under `E:\GT-KB`.
- Rollback: revert the substrate-gate + live branch; the daemon returns to unconditional shadow. `bridge-substrate.json` is not written by this slice, so there is nothing to revert there. Append-only KB untouched (`kb_mutation_in_scope: false`).
- The go-live flip (selector switch + dispatch re-enable) is NOT performed here and remains the owner's deliberate step after 3b/3c.
