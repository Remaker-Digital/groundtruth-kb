NEW

# gtkb-wi4848-slice-2-daemon-decision-reconciliation — Reconcile the daemon's shadow decision to the trigger's selection (remaining_items shrink)

bridge_kind: prime_proposal
Document: gtkb-wi4848-slice-2-daemon-decision-reconciliation
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

Slice 1's parity harness found a real divergence: the daemon's `compute_shadow_decisions` feeds the full `items` list to every resolved target, while the trigger's live loop shrinks `remaining_items` after each target's selection (`cross_harness_bridge_trigger` L4252-L4292). For a multi-target role this means the live daemon could offer the **same** bridge document to multiple harnesses — a double-dispatch / storm-contributor risk. This slice reconciles the daemon to the trigger: it makes `compute_shadow_decisions` consume `remaining_items` per target exactly as the trigger does, so the daemon's decision matches the trigger's selection field-for-field (the parity harness then reports `overall_match` for the multi-target case). Per the owner's "reconcile + flip" decision (AUQ 2026-06-26), this is the reconciliation step; the go-live flip is slice 3.

## Design (for LO review)

In `scripts/gtkb_dispatcher_daemon.py` `compute_shadow_decisions`, change the per-target inner loop (currently `selected, signature = trigger._target_selected_signature(target, items, max_items)` for every target) to mirror the trigger's `remaining_items` consumption:

- seed `remaining = list(items)` before the targets loop (per role);
- per target: `selected, signature = trigger._target_selected_signature(target, remaining, max_items)`; record the decision (unchanged shape: role/recipient/harness_id/signature/would_dispatch);
- if `not selected`: `break`;
- else `remaining = trigger._without_selected_dispatch_items(remaining, selected)`;
- if no dispatchable items remain: `break`.

`trigger._without_selected_dispatch_items` is already importable via the daemon's existing `_load_trigger_module()`. Single-target roles are unchanged (`remaining == items` on the first target). The decision record shape, the shadow-mode/no-spawn invariant, and the WI-4790 monitoring wiring are all untouched — only the multi-target selection is corrected.

**Out of scope (slice 3, the flip):** the state-dir difference (daemon resolves against `.gtkb-state/cross-harness-trigger`, live trigger against `.gtkb-state/bridge-poller`) reconciles when the daemon adopts the live dispatch-state at cutover; the trigger's readiness/provider-backoff runtime gates apply when the daemon actually spawns. Neither changes the selection corrected here.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — the daemon must decide equivalently to the substrate it replaces before the cutover; this removes the one selection divergence the parity gate surfaced.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — correct per-target document selection (no double-offer) is a dispatch-service correctness property.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — decisions remain computed from fresh bridge state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4848-slice-2-daemon-decision-reconciliation-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4848 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision; the "reconcile + flip" AUQ (2026-06-26) selects this reconciliation path.
- `DELIB-20266084` — WI-4787 daemon foundation (the decision path corrected here).
- WI-4848 slice 1 (`-003`, VERIFIED) — the parity harness that surfaced this divergence; its `test_parity_reports_divergence` characterizes the exact multi-target case.

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Pragmatic: reconcile + flip" — authorizes reconciling the daemon's decision to the trigger (this slice) then building the flip (slice 3), under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. This slice is inert (no spawn, no dispatch re-enable); the storm-surface flip is slice 3 with a final owner go/no-go. No further owner decision required here.

## Requirement Sufficiency

Existing requirements sufficient — the reconciliation target is the trigger's existing, tested selection behavior. No new or revised requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (multi-target shrink) | `test_shadow_decision_shrinks_remaining_items` (new) | with two resolved targets for one role (monkeypatched `_resolve_dispatch_targets`) and a multi-doc item list, the per-target `would_dispatch` sets are **non-overlapping** (the second target does not re-offer the first target's docs). |
| ADR-DISPATCHER-ARCHITECTURE-001 (single-target unchanged) | existing `test_daemon_tick_computes_shadow_decision` | unchanged — single-target decisions identical. |
| ADR-DISPATCHER-ARCHITECTURE-001 (shadow preserved) | existing daemon shadow/no-spawn test | unchanged — slice 2 spawns nothing. |
| No-regression | full daemon test file; `ruff check` + `ruff format --check` | green. |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short`; `ruff check`/`ruff format --check` on the changed files; plus `python scripts/ops/dispatch_parity.py` re-run for the current-state report.

## Risk / Rollback

- Risk: low. A scoped change to one inner loop of `compute_shadow_decisions` on the in-root daemon under `E:\GT-KB`; single-target behavior (the overwhelming common case) is unchanged; the daemon stays shadow (no spawn).
- Rollback: revert the loop change. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope: the go-live flip (daemon live-spawn, trigger inert, dispatch re-enable — slice 3, owner go/no-go at execution); state-dir + runtime-gate parity (slice 3).
