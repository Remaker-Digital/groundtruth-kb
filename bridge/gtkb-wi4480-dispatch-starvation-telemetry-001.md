NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4480-dispatch-starvation-telemetry
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4480
target_paths: ["scripts/bridge_dispatch_starvation_telemetry.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4480 Slice A: Per-entry dispatch-starvation telemetry (zero-risk detector; no change to selection or the actionable-signature invariant)

## Summary

WI-4480 (P2, `bridge-dispatch`, origin=defect): the cross-harness trigger selects at most `max_items` (default 2) actionable entries per recipient per dispatch, **oldest-first** (`_selected_oldest_first` in `scripts/cross_harness_bridge_trigger.py:1468` → `list(reversed(items))[:max_items]`). When the oldest entries are stuck (dispatches that keep failing / never produce a verdict), they permanently occupy both cap-2 slots and newer actionable threads are never selected → **starvation**. Evidence (2026-06-12): WI-4472's REVISED@-003 sat un-dispatched ~90 min while the two oldest NEW entries (gtkb-fab-22, gtkb-fab-23) repeatedly won both slots.

Cycle-4 triage (this session) **confirmed WI-4480 is genuinely open, not already-fixed**: `_selected_oldest_first` is still pure oldest-first cap with no aging/fairness, and the circuit-breaker machinery operates per **recipient** (`failure_count` / `circuit_breaker_tripped` keyed by `loyal-opposition:A` etc.), which does NOT address per-**entry** starvation. No in-flight bridge thread covers the selection-fairness gap.

Per the owner's cycle-4 AskUserQuestion decision ("Detector-first (zero-risk) slice"), **this proposal is Slice A: a per-entry starvation DETECTOR with no change to selection behavior or the actionable-signature invariant.** It instruments the existing dispatch flow to record, per recipient, how many consecutive dispatches each actionable entry has gone *un-selected* while newer entries were selected, flags entries past a configurable threshold, and surfaces them via a report CLI. The actual selection-fairness behavior change (which necessarily alters dispatch selection and the byte-identical actionable-signature, a load-bearing swarm-coordination invariant per `.claude/rules/bridge-essential.md`) is deferred to a **Slice B** designed from this detector's evidence. Rationale: bridge dispatch is the top-priority coordination invariant; instrumenting starvation with data before altering critical selection logic is the responsible path, and it quantifies severity to size the real fix.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4480 is the backlog authority for this fix (P2 dispatch-reliability defect).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implementation proceeds under the active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1`, which includes WI-4480 and allows `source` + `test_addition`. Slice A stays strictly within that scope.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` is canonical bridge workflow state and the trigger dispatches bridge work from it; the detector OBSERVES dispatch selection without altering selection, the signature, or bridge authority.
- **`.claude/rules/bridge-essential.md`** (Operational Mode / Dual-Substrate: the byte-identical `_signature` actionable-signature scheme, regression-tested in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`) — Slice A preserves this invariant by construction: it reads the already-computed `filtered` + `selected` lists and writes only to a separate telemetry file; it does not touch `_selected_oldest_first`, `selected`, or `_signature(selected)`.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including a signature-invariant non-regression check.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root under `E:\GT-KB` (`scripts/`, `platform_tests/scripts/`); the telemetry artifact lives under the in-root `.gtkb-state/bridge-poller/` dispatch-state directory.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked detection mechanism with explicit test coverage and explicit lifecycle states (the genuinely-open defect, this detector slice, the deferred Slice-B behavior fix); the scope boundary is stated plainly.

## Requirement Sufficiency

Existing requirements sufficient. The starvation hazard is documented (WI-4480 + the 2026-06-12 WI-4472 incident), the cycle-4 code triage confirmed it is open, the bounded PAUTH authorizes the `source` + `test_addition` work, and the owner's cycle-4 AUQ selected the detector-first scope. No new or revised formal specification is required for Slice A. The deferred Slice-B selection-fairness change will declare its own scope (and will require the byte-identical-signature regression test to be deliberately updated under LO review).

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ admitting WI-4480 (and 8 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-STANDALONE-DEFECT-BATCH-1`.
- **Cycle-4 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Detector-first (zero-risk) slice" for WI-4480 over "actual selection-fairness fix now" and "defer", explicitly scoping this Slice A as a no-behavior-change detector and deferring the selection change to Slice B.
- **`bridge/gtkb-fab-10-dispatch-telemetry-claim-contract` (VERIFIED)** — prior dispatch-telemetry/claim-contract work. WI-4480 flagged a possible relation; cycle-4 code inspection confirms FAB-10 did NOT add selection fairness (`_selected_oldest_first` remains pure oldest-first), so this detector is distinct and non-duplicative. Cited to disambiguate and avoid re-litigating settled telemetry scope.
- **`.claude/rules/bridge-essential.md`** "Dual-Substrate Coexistence" / byte-identical `_signature` invariant — the load-bearing constraint this slice is designed to preserve.
- _Live semantic deliberation search was not run during authoring (the `gt deliberations search` ChromaDB path carries the WI-4453 first-embed hang risk that was only just resolved; per the session's standing caution I cited known threads instead)._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement Slice A.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4480 to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-STANDALONE-DEFECT-BATCH-1` (allowed: `source`, `test_addition`; forbids formal-artifact mutation).
- **Cycle-4 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Detector-first (zero-risk) slice"**, authorizing exactly this no-behavior-change detector scope and deferring the selection-fairness behavior change to Slice B. Slice A stays strictly within `source` + `test_addition` and changes no selection, signature, or dispatch behavior.

## Design (Slice A)

**New module `scripts/bridge_dispatch_starvation_telemetry.py`** (stdlib only):

1. **`update_starvation_telemetry(prev, recipient, actionable_keys, selected_keys, now_iso, threshold)` — pure function** (no I/O). `actionable_keys` = bridge document slugs of the dispatchable entries (`filtered`); `selected_keys` = slugs of the cap-selected entries (`selected`). Per recipient, maintains a per-entry record `{consecutive_non_selection: int, first_starved_at: iso}`:
   - increment `consecutive_non_selection` for each `actionable ∧ ¬selected` key (set `first_starved_at` on first starvation);
   - reset (drop the record) for any `selected` key;
   - prune records for keys no longer in `actionable_keys`.
   Returns `(new_telemetry, starved)` where `starved` = keys whose `consecutive_non_selection >= threshold` (with their counts + `first_starved_at`).
2. **`record_starvation(recipient, actionable_keys, selected_keys, *, project_root, now_iso, threshold)`** — loads `.gtkb-state/bridge-poller/starvation-telemetry.json` (schema-versioned), applies `update_starvation_telemetry`, writes it back atomically. **Fail-safe**: any load/parse/write error is swallowed and returns without raising (telemetry must never affect dispatch).
3. **`report_starved(project_root)` + `__main__` CLI** — prints currently-starved entries (count ≥ threshold) per recipient with wait counts and `first_starved_at`, for owner/swarm visibility and to size the Slice-B fix.
4. Default `threshold` from `GTKB_DISPATCH_STARVATION_THRESHOLD` env (default 5).

**Single fail-safe hook in `scripts/cross_harness_bridge_trigger.py`** — immediately after the existing `selected = _selected_oldest_first(filtered, target_max_items)` / `signature = _signature(selected)` (≈ lines 3028-3029), an additive, exception-swallowed observational call:

```
try:
    record_starvation(recipient, [<<slug(it)>> for it in filtered],
                      [<<slug(it)>> for it in selected],
                      project_root=<project_root>, now_iso=recipient_state["updated_at"])
except Exception:
    pass
```

Entry slugs use the entry's existing document-name accessor (the same identifier already rendered in the trigger's "Selected entries, oldest-first, capped at N: …" prompt line). The hook reads `filtered`/`selected` AFTER they are computed and signed; it does **not** mutate `filtered`, `selected`, `signature`, `recipient_state`'s signature-bearing fields, or any dispatch decision. No other selection site (signature/prompt/preview paths) is touched.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`) | Method |
|---|---|---|
| Un-selected actionable entry increments (WI-4480 starvation detection) | `test_non_selection_increments` | `update_starvation_telemetry` with actionable=[a,b,c], selected=[a,b] → c count=1; repeat → c count=2 |
| Selection resets the counter (no false starvation) | `test_selection_resets_counter` | after c starved twice, selected=[c] → c record dropped/zeroed |
| No-longer-actionable entries pruned | `test_pruned_when_not_actionable` | c starved, then actionable=[a,b] (c gone) → c pruned |
| Threshold flagging (GOV-STANDING-BACKLOG-001, WI-4480) | `test_starved_flag_at_threshold` | c un-selected `threshold` times → `starved` includes c with correct count |
| `first_starved_at` set once and preserved | `test_first_starved_at_preserved` | first starvation sets it; subsequent increments keep the original timestamp |
| Persistence round-trip | `test_persistence_round_trip` | `record_starvation` then reload → telemetry matches |
| Fail-safe: corrupt/missing telemetry never raises (dispatch unaffected) | `test_record_starvation_fail_safe` | corrupt JSON + unwritable dir → `record_starvation` returns without raising |
| **Signature invariant preserved (no behavior change to critical dispatch)** | `test_signature_invariant_unaffected` + run existing `platform_tests/scripts/test_cross_harness_bridge_trigger.py` | assert `_signature(_selected_oldest_first(items, n))` is byte-identical before/after the hook; the existing byte-identical-signature regression suite must still pass |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on all changed files; `python -m pytest platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`.

## Risk / Rollback

- **Risk: low (by construction).** Slice A adds one new stdlib module + one new test + a single fail-safe, exception-swallowed observational call in the trigger. It performs **no change to dispatch selection, the `_signature` actionable-signature, dispatch-state's signature-bearing fields, or any dispatch decision** — the owner's "no change to selection behavior or signatures" constraint is met by design. Telemetry writes go to a *separate* `.gtkb-state/bridge-poller/starvation-telemetry.json`. Any telemetry failure is swallowed and cannot break dispatch.
- **Invariant guard:** the existing byte-identical-signature regression suite (`test_cross_harness_bridge_trigger.py`) is run as part of verification and must still pass, proving the hook did not perturb selection/signature.
- **Deferred risk:** the actual selection-fairness behavior change (Slice B) DOES touch the signature invariant and is intentionally NOT in this slice; it will be designed from this detector's evidence under separate LO review.
- **Rollback:** delete the new module + test and revert the single trigger hook line. No migration, no schema change to dispatch-state, no KB mutation.

## Recommended Commit Type

`feat:` — net-new capability (a dispatch-starvation telemetry module + report CLI + a fail-safe observational hook), not a repair of existing behavior (the behavior fix is the deferred Slice B). Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`), net-new modules/capabilities are `feat:`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
