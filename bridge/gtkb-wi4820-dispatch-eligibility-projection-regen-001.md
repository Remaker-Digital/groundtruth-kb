NEW

# gtkb-wi4820-dispatch-eligibility-projection-regen — Fix the dispatch-eligibility false-green: regenerate the harness-registry projection on set-eligibility

bridge_kind: prime_proposal
Document: gtkb-wi4820-dispatch-eligibility-projection-regen
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4820

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4820 is a dispatch-eligibility control-plane false-green. `gt bridge dispatch config set-eligibility <id> --can-receive-dispatch` reports success and `gt bridge dispatch status` then shows the harness `dispatchable=True` and selected — but the cross-harness trigger dispatches nothing (`no_active_target_for_role`), because the trigger reads `can_receive_dispatch` from the static `harness-registry.json` projection, which the eligibility transaction never regenerates.

Root cause (code-confirmed this session): `bridge_dispatch_transactions.set_eligibility()` writes the `config/dispatcher/rules.toml` overlay and records the transaction, but does NOT regenerate the projection. `harness_projection.generate_harness_projection()` already loads and applies the rules.toml overlay via `build_projection(..., dispatch_config=...)`, so the only missing wire is "regenerate after write." Until some unrelated regen runs (e.g. `gt mode set-role`), the trigger keeps reading a stale projection. This is the systemic recurrence of the one-time Honest-ON reconcile owner-decided in DELIB-20266107.

## Problem detail (for LO review)

- The trigger's dispatchability gate is `scripts/cross_harness_bridge_trigger.py:3047` -> `_record_can_receive_dispatch(h_info)` (line 2912), reading the projection loaded by `load_harness_projection` (the static `harness-state/harness-registry.json`).
- `gt bridge dispatch status` (`bridge_dispatch_config.py` ~line 285) loads the projection and applies the rules.toml overlay live at read time (`apply_dispatch_config_to_record`), so it shows the post-write value. The trigger reads the static file, which is stale. The two diverge exactly when the projection has not been regenerated since the last `set-eligibility`.
- `bridge_dispatch_config.py` (~line 717) already emits a "dispatch config drift warning" when rules.toml and the projection disagree — confirming the drift is known but not auto-reconciled.
- `gt harness` exposes no eligibility setter, so there is no alternate authoritative write path either.

Live reproduction this session: `set-eligibility E --can-receive-dispatch` -> status `dispatchable=True, loyal-opposition: E`; one trigger cycle -> result `loyal-opposition launched=false, reason=no_active_target_for_role`; `harness-registry.json` still has E `can_receive_dispatch: false`.

## Proposed change

1. In `bridge_dispatch_transactions.set_eligibility()` (and the sibling projected-field mutators `set_weights` and `set_caps`, which also flow through `apply_dispatch_config_to_record`), after the rules.toml write and transaction record succeed, regenerate the harness-registry projection by opening the KnowledgeDB and calling `harness_projection.generate_harness_projection(db, project_root)` — the same regen path `gt mode set-role` already uses. This makes the write a write-through so the static projection the trigger reads reflects the CLI change.
2. Keep `gt bridge dispatch status`/`health` reading the live-merged value (already correct); after the fix it matches the regenerated projection, eliminating the false-green.
3. No schema migration and no change to the trigger's read path. The fix is confined to the eligibility transaction's post-write regen, consistent with the existing `_dispatch_metadata` / overlay design.

Placement rationale: the projection is a write-through cache of "MemBase harnesses (+) rules.toml overlay"; `set-eligibility` updates the overlay (backing store) without refreshing the cache. The generator already knows the merge; the fix refreshes the cache on write.

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — governing principle: state claims (here, the trigger's dispatchability decision) must derive from a fresh canonical read; the stale projection violates this.
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture-of-record; eligibility is a control-plane input the trigger/daemon consume; this fix keeps the projection authoritative for the dispatch substrate.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` — the harness-state projection reader contract; this fix keeps the generated projection consistent with the eligibility source.
- `GOV-RELIABILITY-FAST-LANE-001` — authority: WI-4820 is a small reliability defect fix in PROJECT-GTKB-RELIABILITY-FIXES under the standing PAUTH.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed via the no-index bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project / Work Item / Project Authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4820 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266134` — this session's owner decision to fix WI-4820 (control plane) first; topology B=PB / E=LO; the regen-on-write approach.
- `DELIB-20266107` — owner decision to reconcile can_receive_dispatch drift to Honest-ON, a one-time manual reconcile; this proposal systematizes that into an automatic write-through so the drift cannot recur.
- `DELIB-20265899` — owner authorization of ADR-DISPATCHER-ARCHITECTURE-001, the architecture this control-plane fix serves.
- `DELIB-20266132` / `DELIB-20266133` — dispatcher work re-scope / re-home context (storm-containment; dispatcher-reliability project).

## Owner Decisions / Input

- Owner AUQ this session (2026-06-25): asked to enable the dispatcher if it would function correctly, else fix it (standing directive). After live evidence showed it would not (reviewer-layer 600s timeouts plus this WI-4820 false-green), owner chose **"Fix WI-4820 (control plane) first"** over operating the interactive bridge or an ad-hoc reconcile. Recorded as `DELIB-20266134`.
- Owner directive (2026-06-25): topology Claude(B)=Prime Builder, Cursor(E)=Loyal Opposition; Codex(A) and Antigravity(C) unavailable today. Cursor (E) reviews this proposal as Loyal Opposition.
- No further owner decision is required to implement this bounded reliability fix; it changes no runtime dispatch behavior on its own (it makes the existing CLI honest). Re-enabling dispatch remains a separate owner-gated step.

## Requirement Sufficiency

Existing requirements sufficient — `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `ADR-DISPATCHER-ARCHITECTURE-001` + `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` fully constrain the fix (the projection must reflect the eligibility source the trigger reads). No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fresh canonical read) | `test_set_eligibility_regenerates_projection` (new, in `platform_tests/scripts/test_bridge_dispatch_transactions.py`) | After `set_eligibility(harness, can_receive_dispatch=True)`, the static `harness-registry.json` projection record for that harness has `can_receive_dispatch == True` — the trigger's source reflects the CLI write. |
| DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (projection consistency) | same test, second assertion | `set_eligibility(..., can_receive_dispatch=False)` flips the projection record back to `False`; the `bridge_dispatch_config` drift check reports no drift afterward. |
| ADR-DISPATCHER-ARCHITECTURE-001 (trigger honors eligibility) | `test_trigger_target_resolution_reflects_set_eligibility` (new) | After enabling a harness via `set_eligibility`, the trigger's active-target resolver reading the regenerated projection includes that harness for its role. |
| No-regression | existing `test_bridge_dispatch_transactions.py` + dispatcher-config tests; `ruff check` and `ruff format --check` on changed files | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_bridge_dispatch_transactions.py -q --tb=short`; `ruff check <changed .py>`; `ruff format --check <changed .py>`.

## Risk / Rollback

- Risk: low. The change adds a regen call after an already-successful write; the regen path is the same one `gt mode set-role` exercises. If the DB is unavailable at transaction time, the regen fails soft (log and leave the rules.toml write in place) rather than raising — so `set-eligibility` never half-fails. The graceful-degradation behavior is part of this proposal.
- Rollback: revert the transaction-module change; prior behavior (write rules.toml only) returns. No data migration, no schema change, append-only KB untouched (`kb_mutation_in_scope: false`).
- Out of scope: the reviewer-layer 600s timeouts (separate blocker), the daemon shadow->live cutover, and the Cursor watchdog blind-spot coverage (storm-watchdog Cursor harness drift). This proposal only makes the eligibility CLI honest.
