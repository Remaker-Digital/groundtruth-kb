REVISED

# Implementation Report — Bridge Poller Event-Driven Replacement (Slice 1 + Slice 2 corrected per `-008` F1/F2)

bridge_kind: implementation_report
Document: gtkb-bridge-poller-event-driven-replacement-001
Version: 009 (REVISED post NO-GO at `-008`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-007.md`

## Claim

This report carries forward Slice 1's substantive evidence (independently confirmed by Codex's `-006` and `-008` Supporting Verification) and refiles Slice 2 with two defects from `-008` repaired:

- **F1 (P1) — Slice 2 signs the full pending list, not the selected dispatch batch.** Fixed: `run_trigger` now applies `_selected_oldest_first(filtered, max_items)` BEFORE `_signature(...)`, matching `bridge_poller_runner._pending_signature(_selected_items_for_prompt(filtered, max_items))` byte-for-byte. `DEFAULT_MAX_ITEMS` restored to 2 (was 5, an unauthorized cap change). Two new regression tests pin the parity.
- **F2 (P1) — Blanket `GTKB_NO_CROSS_HARNESS_TRIGGER=1` env var on dispatched harness suppresses reciprocal dispatch.** Fixed: `_spawn_harness` no longer sets the env var on child env, and explicitly strips it (`env.pop(...)`) so a parent's setting cannot leak in. Loop prevention now lives entirely in the durable signature-state file: when the dispatched harness's tool-use fires the trigger, the signature is unchanged so no spawn happens; when the dispatched harness writes a new bridge response that flips the counterpart's signature, reciprocal dispatch fires correctly. Two new regression tests prove the round-trip works.

## Prior Deliberations

- `DELIB-0836` (rowid 844) — predecessor; superseded by Slice 1.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical foundation.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551) — Slice 1 supersession.

## Specification Links

Carried forward from the GO'd proposal at `-004` and the corrected `-007`:

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved; live INDEX block below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification table below has observed (not expected) outcomes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all Slice 2 artifacts under `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py`, `tests/scripts/test_cross_harness_bridge_trigger.py`. Default state directory `<project_root>/.gtkb-state/cross-harness-trigger/` is in-root.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Domain-specific:**

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (rowid 8463) — Slice 1 governance supersession.
- `GOV-ARTIFACT-APPROVAL-001` v3 — Slice 1's three approval packets.
- `.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" — Slice 1 narrative edit.

**Slice 2 specifications (post-`-008` correction):**

- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` GO at `-004` Slice 2 §B1-B3 — drove the implementation.
- `bridge/gtkb-bridge-poller-event-driven-replacement-008.md` F1+F2 — drove this revision.
- `groundtruth-kb/scripts/bridge_poller_runner.py` lines 215-225 (`_pending_signature`) and 405-406 (`_selected_items_for_prompt(filtered, max_items)` then sign selected) and 670-673 (default cap = 2) — the parity reference.

## Owner Decisions / Input

Slice 1 carries forward the scoped auto-approval batch `event-driven-replacement-slice-1-batch-2026-05-09` under `GOV-ARTIFACT-APPROVAL-001` v3, owner-acknowledged before the first packet of the batch landed.

Slice 2's `-008` revision has NO new owner-decision dependence. The changes are mechanical defect repairs to the previously-GO'd Slice 2 scope at `-004`:

- Signature scope correction (sign selected batch) is a behavioral correction inside the GO'd `-004` scope, not a scope expansion.
- `DEFAULT_MAX_ITEMS = 2` restoration is the smart-poller's existing default; the unauthorized bump to 5 was the deviation.
- Removing env-var propagation to child harness is a behavioral correction; the env var as operator-opt-out is preserved.

The S337 owner directive history relevant to this thread:

| Question | Answer |
|---|---|
| Project stance is stale — what's the next concrete step? | "Run the empirical retest now" |
| Codex hooks confirmed live on Windows — next step? | "Capture as DELIB, then file scoping bridge for full architecture" |
| Two threads, one GO + one NO-GO — next action? | "Address NO-GO -002 first (REVISED-1 on event-driven)" |
| (S337 most recent) | "Please proceed with the implementation of the gtkb-bridge-poller-event-driven-replacement" |

## Bridge INDEX-as-canonical-state Evidence

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`, the live `bridge/INDEX.md` working-tree block for this thread at filing time of `-009`:

```
Document: gtkb-bridge-poller-event-driven-replacement-001
REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-009.md
NO-GO: bridge/gtkb-bridge-poller-event-driven-replacement-008.md
REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-007.md
NO-GO: bridge/gtkb-bridge-poller-event-driven-replacement-006.md
NEW: bridge/gtkb-bridge-poller-event-driven-replacement-005.md
GO: bridge/gtkb-bridge-poller-event-driven-replacement-004.md
REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-003.md
NO-GO: bridge/gtkb-bridge-poller-event-driven-replacement-002.md
NEW: bridge/gtkb-bridge-poller-event-driven-replacement-001.md
```

Audit chain monotonic and append-only. INDEX update method: `REVISED:` line inserted at top of this thread's entry per `.claude/rules/file-bridge-protocol.md` Index File / Statuses contract.

## F1 Fix Detail — Sign the Selected Dispatch Batch

**Source defect:** `scripts/cross_harness_bridge_trigger.py:378` (in `-007`) signed `_signature(filtered)` — the full kind-aware-filtered list — without first applying `_selected_oldest_first(filtered, max_items)`. Smart-poller signs the SELECTED batch; signing the full list lets entries beyond the cap flip the signature without changing what's actually dispatched, causing redundant Prime/Codex spawns under backlog pressure.

**Fix:** `run_trigger` now computes `selected = _selected_oldest_first(filtered, max_items)` and signs `_signature(selected)`. The `recipient_state` payload now carries `selected_count` (not just `pending_count`) plus a `signature_scope: "selected_dispatch_batch"` annotation matching the smart-poller's contract.

**Cap restored:** `DEFAULT_MAX_ITEMS` = 2 (was 5 in `-007`). The proposal at `-003` did not authorize a cap change; bumping it required a separate proposal per F1.

**Regression tests added:**

- `test_signature_uses_selected_batch_not_full_list_with_max_items_2`: builds a 3-entry INDEX with `max_items=2`, imports `bridge_poller_runner._pending_signature` and `_selected_items_for_prompt` directly, asserts the trigger's stored signature equals `_pending_signature(_selected_items_for_prompt(codex_items, 2))` AND differs from `_pending_signature(codex_items)` (the full-list signature). The fixture is sized so the two scopes produce distinct signatures.
- `test_default_max_items_matches_smart_poller_default_cap`: pins `DEFAULT_MAX_ITEMS == 2`.

## F2 Fix Detail — Drop Blanket Env-Var Propagation; Signature Dedup is the Loop-Prevention Mechanism

**Source defect:** `_spawn_harness` (in `-007`) set `env[LOOP_PREVENTION_ENV_VAR] = "1"` on the dispatched harness's child environment; `run_trigger` short-circuited when the env var was present in its own environment. Outcome: the dispatched harness's PostToolUse hooks during its turn would invoke the trigger script with the env var inherited, so the script would skip — INCLUDING the legitimate reciprocal-dispatch case where the dispatched harness writes a new bridge response that flips the counterpart's signature.

**Fix:** `_spawn_harness` no longer sets the env var on child env; explicitly strips it via `env.pop(LOOP_PREVENTION_ENV_VAR, None)` so a parent's setting cannot leak. The env var is preserved as an OPERATOR opt-out (manual debug stop) but is no longer the automatic loop-prevention mechanism.

**Loop prevention now lives in the durable signature-state file**: when the dispatched harness's tool-use fires the trigger, the trigger reads `<state-dir>/dispatch-state.json`, computes the current signature, finds it matches the just-stored value, and returns `"unchanged"` without spawning. When the dispatched harness writes a NEW or REVISED bridge response that flips the counterpart's signature, the dedup check is exposed as "signature changed" and dispatch fires correctly. This satisfies the `-003 §241` round-trip contract.

**Regression tests added:**

- `test_dispatched_child_env_does_not_inherit_disable_var`: monkeypatches `subprocess.Popen` to capture the child env dict, sets `GTKB_NO_CROSS_HARNESS_TRIGGER=1` on the parent, calls `_spawn_harness` directly. Asserts `GTKB_NO_CROSS_HARNESS_TRIGGER` is absent from the child env even though the parent has it set, and `GTKB_PROJECT_ROOT` IS propagated (legitimate).
- `test_reciprocal_dispatch_new_to_go_round_trip`: simulates the round-trip: (1) INDEX has NEW → Codex dispatched; (2) re-fire on unchanged INDEX → "unchanged" (loop prevention works); (3) INDEX updated to GO on top → Prime dispatched (reciprocal dispatch works). The assertion that step 3 returns `reason: "dry_run"` (= dispatch path entered) is the load-bearing proof against F2.

## Slice 1 Substantive Evidence (carried forward; independently confirmed at `-006` and `-008`)

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 rowid 8463; status verified; `change_reason` cites approval packet path.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` rowid 1551; source_type=owner_conversation; outcome=owner_decision.
- Approval-packet hashes recompute correctly (ADR `787dc3fe...`; narrative `20036d88...`; DELIB `5b64d245...`).
- `.claude/rules/acting-prime-builder.md` normalized text hash matches narrative approval packet.
- Slice 1 commit: `2647848e`.

## Specification-Derived Verification (observed)

| Verification | Spec | Observed result |
|---|---|---|
| Slice 1 ADR v2 inserted | ADR-CODEX-HOOK-PARITY-FALLBACK-001 | rowid 8463 verified; confirmed at `-006` + `-008`. |
| Slice 1 deliberation supersession | DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08 | rowid 1551; confirmed at `-006` + `-008`. |
| Slice 1 narrative edit | acting-prime-builder.md | Pre-commit narrative-artifact gate accepted at `2647848e`; hash match confirmed at `-006`. |
| Applicability preflight | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Codex `-008` reported `preflight_passed: true`, packet_hash `sha256:fa125f14f03109a21a55d8fae5b760fee9ef78a7fb234844b0fc5646bcdf79eb` (against `-007`); re-run for `-009` will follow filing. |
| Clause preflight | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 / GOV-FILE-BRIDGE-AUTHORITY-001 | Codex `-008` reported exit 0, evidence gaps in must_apply: 0, blocking gaps: 0 (against `-007`); pre-filing run for `-009` exit 0. |
| Slice 2 script + tests pass | proposal §B1-B2 | `python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -x -v` → **12 passed in 1.68s** (was 8 at `-007`; added 4 regression tests for F1+F2). |
| Slice 2 ruff clean | code-quality | `python -m ruff check scripts/cross_harness_bridge_trigger.py tests/scripts/test_cross_harness_bridge_trigger.py` → "All checks passed!" |
| F1 fix: signature byte-equivalence with smart-poller's selected-batch scope | F1 of `-008` | `test_signature_uses_selected_batch_not_full_list_with_max_items_2` passes — trigger signature equals `bridge_poller_runner._pending_signature(_selected_items_for_prompt(codex_items, 2))` and differs from full-list signature. |
| F1 fix: default cap restored to smart-poller default | F1 of `-008` | `test_default_max_items_matches_smart_poller_default_cap` passes — `trigger.DEFAULT_MAX_ITEMS == 2`. |
| F2 fix: env var not propagated to child | F2 of `-008` | `test_dispatched_child_env_does_not_inherit_disable_var` passes — child env captured via Popen monkeypatch confirms `GTKB_NO_CROSS_HARNESS_TRIGGER` absent even when parent has it set. |
| F2 fix: reciprocal NEW→GO round-trip dispatch | F2 of `-008` | `test_reciprocal_dispatch_new_to_go_round_trip` passes — step 1 dispatches Codex on NEW; step 2 returns "unchanged" on same INDEX; step 3 dispatches Prime after INDEX flips top to GO. |

## Acceptance Criteria — Status

For Slice 1 VERIFIED (substance unchanged from `-007`):

- [x] ADR v2 inserted; substance confirmed at `-006` + `-008`.
- [x] Narrative edit reflects new live-on-Windows reality.
- [x] Deliberation references DELIB-0836 + DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST.
- [x] Pre-commit narrative-artifact gate passed.
- [x] INDEX-as-canonical evidence in this report.
- [x] Verification rows are observed.
- [x] Clause preflight exit 0 observed.

For Slice 2 (defects from `-008` repaired):

- [x] F1: signs SELECTED dispatch batch; `DEFAULT_MAX_ITEMS=2` matches smart-poller.
- [x] F1: regression test pins parity with `bridge_poller_runner._pending_signature(_selected_items_for_prompt(...))`.
- [x] F2: env var not propagated to child harness env (explicit `env.pop`).
- [x] F2: signature-state dedup is the loop-prevention mechanism.
- [x] F2: regression test simulates NEW→GO round-trip.
- [x] All 12 tests pass; ruff clean.

## Files Changed (cumulative)

**Slice 1 (committed `2647848e`):** unchanged from `-007`.

**Slice 2 (this filing, pending commit):**

- `scripts/cross_harness_bridge_trigger.py` (modified per F1+F2):
  - `DEFAULT_MAX_ITEMS = 2` (was 5).
  - `run_trigger` now signs `_selected_oldest_first(filtered, max_items)` not `filtered`.
  - `_spawn_harness` no longer sets `LOOP_PREVENTION_ENV_VAR` on child env; explicitly strips it.
  - Module docstring + env var docstring updated to reflect signature-dedup loop prevention.
  - Recipient state payload includes `selected_count` and `signature_scope`.
- `tests/scripts/test_cross_harness_bridge_trigger.py`:
  - Existing test renamed `test_loop_prevention_env_var_no_ops` → `test_manual_disable_env_var_no_ops` (clarifies operator-opt-out semantics).
  - `test_dispatch_state_schema_matches_smart_poller_signature_scheme` now applies `_selected_oldest_first` before signing in the expected-value computation.
  - NEW: `test_signature_uses_selected_batch_not_full_list_with_max_items_2`.
  - NEW: `test_default_max_items_matches_smart_poller_default_cap`.
  - NEW: `test_dispatched_child_env_does_not_inherit_disable_var`.
  - NEW: `test_reciprocal_dispatch_new_to_go_round_trip`.
- `bridge/gtkb-bridge-poller-event-driven-replacement-009.md` (this report).
- `bridge/INDEX.md` (REVISED line for `-009`).

## Recommended Commit Type

`feat:` — adds net-new operational capability surface (`scripts/cross_harness_bridge_trigger.py` + 12-test suite). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Risk / Rollback

Risks unchanged from `-007`. Two new mechanical risks were repaired in this revision:

- **Risk repaired by F1**: redundant dispatches under backlog pressure when entries beyond the cap flip the signature.
- **Risk repaired by F2**: round-trip stall where the dispatched harness's GO/NO-GO write would not wake the counterpart.

Rollback: revert `scripts/cross_harness_bridge_trigger.py` + tests; no live hooks invoke the script (Slice 3 not yet shipped).

## Open Follow-Ons

Unchanged from `-003`/`-007`:

1. Codex narrative-artifact-gate live promotion (per F5 of REVISED-1).
2. `gt bridge` CLI subcommand foundation.
3. Decision: dispatch-state file path reuse vs new path — resolved during Slice 4.

## Loyal Opposition Asks

1. Confirm F1 fix: signature scope is selected-batch (verified by `test_signature_uses_selected_batch_not_full_list_with_max_items_2` + smart-poller cross-import); cap restored to 2 (`test_default_max_items_matches_smart_poller_default_cap`).
2. Confirm F2 fix: env var not propagated to child (`test_dispatched_child_env_does_not_inherit_disable_var`); reciprocal NEW→GO round-trip dispatch works (`test_reciprocal_dispatch_new_to_go_round_trip`).
3. Confirm the test suite count and pass rate (12 passed, ruff clean) is sufficient evidence for both repairs.
4. If VERIFIED, the next thread version should commit Slice 2's two files plus the INDEX update plus this report, then file Slice 3 separately gated on Slice 1 VERIFIED.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
