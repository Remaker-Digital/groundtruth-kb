NEW

# gtkb-wi4820-dispatch-eligibility-projection-regen — Implementation Report (regen-on-write)

bridge_kind: implementation_report
Document: gtkb-wi4820-dispatch-eligibility-projection-regen
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4820-dispatch-eligibility-projection-regen-002.md (GO)

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4820

Recommended commit type: fix

---

## Summary

Implemented the WI-4820 control-plane write-through per the GO at -002, adopting all five GO review notes. After an applied dispatcher-config transaction, `bridge_dispatch_transactions._apply_transaction` now regenerates the static `harness-state/harness-registry.json` projection (the source the cross-harness trigger reads via `_record_can_receive_dispatch`), so `set_eligibility` / `set_weights` / `set_caps` / `set_rule` / `add_harness` / `remove_harness` are no longer false-greens: enabling a harness through the CLI now reaches the trigger immediately and `status` matches the trigger's view.

## GO Review Notes — Disposition

1. **Centralize regen in `_apply_transaction`** — DONE. The regen hook lives in the single shared `_apply_transaction` applied-path, covering all six mutators, not three wrappers.
2. **Skip regen on dry_run / defer_to_next_session** — DONE. The hook sits after the dry_run and deferred early-returns, so it runs only when status == "applied" and mutated is True. Guarded by `test_dry_run_does_not_regenerate_projection`.
3. **Drop cli.py** — DONE. No cli.py change; the regen outcome surfaces through the existing `result.message` rendering. cli.py was authorized in target_paths but intentionally left untouched (narrower diff).
4. **Soft-fail logging** — DONE. `_regenerate_harness_projection` catches all exceptions and returns a WARNING string appended to `result.message`; the rules.toml write is preserved, so the transaction is never half-applied.
5. **Focused unit test** — DONE. The three new tests are module-level unit tests (no full trigger spawn); they read the projection via the trigger's exact `can_receive_dispatch` field, resolved through `harness_registry_path` (honoring the scripts/ conftest registry override).

## Files Changed (scoped)

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py` — regen-on-write in the `_apply_transaction` applied branch + new `_regenerate_harness_projection(root)` soft-fail helper (+41 lines).
- `platform_tests/scripts/test_bridge_dispatch_transactions.py` — new module-level regression tests (3).

cli.py: authorized but unchanged (GO note #3). `config/dispatcher/rules.toml` is NOT part of this change; its working-tree modification is the unrelated dispatch quiesce plus this session's reverted controlled-test toggle.

## Specification Links (carried forward)

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is filed as the next numbered bridge file (`bridge/gtkb-wi4820-dispatch-eligibility-projection-regen-003.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fresh canonical read) | `test_set_eligibility_regenerates_projection` | PASS — after `set_eligibility(D, True)` the static projection D `can_receive_dispatch` flips false->true (the trigger's source). |
| DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (projection consistency) | `test_set_eligibility_disable_flips_projection_back` + agreement assertion in `test_set_eligibility_regenerates_projection` | PASS — disable flips true->false; rules.toml and projection agree (no residual drift). |
| ADR-DISPATCHER-ARCHITECTURE-001 (trigger honors eligibility) | `test_set_eligibility_regenerates_projection` (projection field == the trigger's `_record_can_receive_dispatch` source) | PASS. |
| GO review note #2 (regen only on applied path) | `test_dry_run_does_not_regenerate_projection` | PASS — dry_run leaves the projection untouched and emits no regen message. |

## Commands Executed + Results

- `python -m pytest platform_tests/scripts/test_bridge_dispatch_transactions.py -q --tb=short` -> 3 passed.
- `python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short` -> 36 passed, 1 failed (pre-existing; see below).
- `python -m ruff check` (both changed .py) -> All checks passed.
- `python -m ruff format --check` (both changed .py) -> 2 files already formatted.

### Pre-existing failure (NOT caused by this change)

`test_bridge_dispatch_config.py::test_wi4768_live_dispatch_config_projection_drift_is_visible` FAILS asserting the live `config/dispatcher/rules.toml` harness B `can_receive_dispatch is True`. The committed (HEAD) rules.toml has B=true; the working tree has B=false from the operative dispatch quiesce (present at session start per `git status`). The test reads rules.toml DATA; the WI-4820 change is CODE in `bridge_dispatch_transactions.py` and never modifies B. The failure is a function of the working-tree quiesce, not this code, and reproduces with the code change reverted. It clears when dispatch is un-quiesced (B restored to true). Out of scope for WI-4820.

## Prior Deliberations

- `DELIB-20266134` — owner decision to fix WI-4820 (control plane) first.
- `DELIB-20266107` — one-time Honest-ON reconcile this systematizes into an automatic write-through.
- `DELIB-20265899` — ADR-DISPATCHER-ARCHITECTURE-001 authorization.
- Bridge GO at -002 (Cursor harness E, session `cursor-e-20260626-lo-review`) — the five implementation notes adopted here.

## Owner Decisions / Input

- Owner AUQ this session: "Fix WI-4820 (control plane) first" (`DELIB-20266134`). Owner relayed the Cursor-LO GO and directed implementation.
- Topology: Claude(B)=Prime Builder, Cursor(E)=Loyal Opposition. This report awaits Cursor-LO VERIFIED; the VERIFIED verdict is the commit-finalization step (Prime does not self-commit).

## Requirement Sufficiency

Existing requirements sufficient (carried forward from the GO'd proposal). No new or revised requirement.

## Risk / Rollback

- Risk: low. The regen reuses the established `generate_harness_projection` path and fails soft. The 36 passing tests (including every CLI-transaction test that exercises `_apply_transaction`) confirm no regression to the transaction surface.
- Rollback: revert `bridge_dispatch_transactions.py` and remove the new test; append-only KB untouched (`kb_mutation_in_scope: false`).
- Recommended commit type: `fix` (repairs broken control-plane behavior; no new capability surface).
