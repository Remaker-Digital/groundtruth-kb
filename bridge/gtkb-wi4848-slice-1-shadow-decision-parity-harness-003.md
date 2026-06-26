NEW

# gtkb-wi4848-slice-1-shadow-decision-parity-harness — Implementation Report (parity harness built; live sample = 0 under quiesce)

bridge_kind: implementation_report
Document: gtkb-wi4848-slice-1-shadow-decision-parity-harness
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4848-slice-1-shadow-decision-parity-harness-002.md (GO)

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4848

Recommended commit type: feat

---

## Summary

Implemented WI-4848 slice 1 per the `-002` GO: a read-only shadow-decision parity harness (`scripts/ops/dispatch_parity.py`) that computes the daemon's shadow dispatch decision and the trigger's canonical dispatch selection for a given bridge state and reports per-role field-for-field parity (recipient, selected docs, signature). It spawns nothing, writes no dispatch state, and re-enables no dispatchability — running it leaves the quiesced posture unchanged. The harness faithfully replicates the trigger's `remaining_items` shrink (so it can detect the multi-target divergence class Cursor flagged) and isolates that one variable by resolving both sides against the same state dir.

## Honest Finding — live parity sample is currently zero

The real-state smoke (`python scripts/ops/dispatch_parity.py`) returned:

```
{ "overall_match": true, "per_role": {}, "roles_compared": [] }
```

`overall_match: true` here is **vacuous**: dispatch is quiesced (every harness `can_receive_dispatch=false` from the storm mitigation), so `_resolve_dispatch_targets` yields no targets on either side → zero decisions → trivial match. **The harness works; the current posture simply provides no substantive live sample.** This is the key input for the go-live decision: gathering real parity evidence requires running the harness against a state with actionable, dispatchable targets (a brief controlled un-quiesce), OR accepting the structural argument (daemon reuses trigger helpers) plus this harness as a permanent regression guard. That trade-off is exactly what WI-4848 slice 2 (the owner-gated flip) must weigh.

## Files Changed (scoped)

- `scripts/ops/dispatch_parity.py` — new read-only parity harness (pure `compare_decisions` core + `trigger_canonical_decisions` / `daemon_shadow_decisions` + `compute_parity` + CLI).
- `platform_tests/scripts/test_dispatch_parity.py` — new, 4 tests.

Both files are in-root under `E:\GT-KB`; no existing file changed; `kb_mutation_in_scope: false`.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — the cutover must be gated on shadow-decision parity evidence; this builds that evidence source.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the dispatch service whose shadow/live decision-equivalence is measured.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — parity is computed from the fresh live bridge state.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this report is filed as the next numbered bridge file (`bridge/gtkb-wi4848-slice-1-shadow-decision-parity-harness-003.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied.
- `GOV-STANDING-BACKLOG-001` — WI-4848 is the governing backlog item.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| ADR-DISPATCHER-ARCHITECTURE-001 (parity logic) | `test_parity_single_target_matches` | PASS — identical decisions -> `overall_match` True, no divergences. |
| ADR-DISPATCHER-ARCHITECTURE-001 (multi-role) | `test_parity_multi_role` | PASS — prime+LO compared per role. |
| ADR-DISPATCHER-ARCHITECTURE-001 (detects divergence) | `test_parity_reports_divergence` | PASS — the multi-target `remaining_items` divergence (index 1) is reported `match: False`. |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (read-only/inert) | `test_parity_is_read_only` | PASS — `compute_parity` on a synthetic project spawns no subprocess (`Popen` patched to raise). |
| No-regression | `ruff check` + `ruff format --check` | PASS. |

## Commands Executed + Results

- `python -m pytest platform_tests/scripts/test_dispatch_parity.py -q --tb=short` → 4 passed.
- `python -m ruff check scripts/ops/dispatch_parity.py platform_tests/scripts/test_dispatch_parity.py` → All checks passed.
- `python -m ruff format --check ...` → 2 files already formatted (after `ruff format`).
- `python scripts/ops/dispatch_parity.py` → `{"overall_match": true, "per_role": {}, "roles_compared": []}` (zero live sample under quiesce; see Honest Finding).

## Prior Deliberations

- `DELIB-20266138` — owner minimum-viable activation decision (WI-4848 in path).
- `DELIB-20266084` — WI-4787 daemon foundation (the shadow decision path measured).
- GO at `-002` (Cursor, harness E, session `cursor-e-20260626-lo-autoproc-5`) — flagged the `remaining_items` vs `items` divergence the harness detects.

## Owner Decisions / Input

- Owner AUQ (2026-06-26): "Minimum-viable activation, autonomous" (`DELIB-20266138`); implemented under `PAUTH-MINVIABLE-ACTIVATION-DRIVE-2026-06-26`. This slice is inert (no spawn, no dispatch re-enable). The go-live flip (WI-4848 slice 2) is the owner-gated decision and will be brought as an AUQ with this finding (zero live sample under quiesce) made explicit. No owner decision required for this slice.

## Requirement Sufficiency

Existing requirements sufficient (carried forward from the GO'd proposal). No new or revised requirement.

## Risk / Rollback

- Risk: very low. New read-only module + test, both in-root under `E:\GT-KB`. No existing file changed; trigger/daemon imported read-only and never driven to spawn; dispatch remains quiesced.
- Rollback: delete the two new files. Append-only KB untouched (`kb_mutation_in_scope: false`).
- Next: bring the owner the WI-4848 slice-2 go-live decision, with the zero-live-sample finding explicit (controlled un-quiesce to gather real parity evidence vs. accept structural + regression-guard argument). The `remaining_items` divergence + the state-dir difference are documented reconciliation items for the flip slice.
