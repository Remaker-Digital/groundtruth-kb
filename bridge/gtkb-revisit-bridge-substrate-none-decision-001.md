NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Revisit bridge-substrate=none decision: B is now active PB; original 'Claude-offline' premise has shifted

bridge_kind: prime_proposal
Document: gtkb-revisit-bridge-substrate-none-decision
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4326

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The WI-4326 premise has been overtaken by intervening work and is now stale on both of its operative claims; the residual gap is the absence of a regression-lock that ties the *configured* bridge substrate to the cross-harness trigger's *active-substrate predicate*, so the original drift (substrate left at `none` while Claude/B is the active Prime Builder) cannot silently recur. Specifically:

1. **Substrate premise stale.** WI-4326 was authored when `harness-state/bridge-substrate.json` recorded `substrate: "none"` (set by commit `c9e1efa7` "configure Claude-offline bridge mode"). The live file now records `{"substrate": "cross_harness_trigger", "applied_at": "2026-06-15T16:32:34Z", "applied_by": "B"}` — the decision the WI asks to "revisit" has already been flipped to the active path via the WI-4510/WI-4574 TAFE-cutover consolidation (git timeline: `c9e1efa7` set `none` -> `f2b249e3` / `760de974` consolidation moved it to `cross_harness_trigger`).
2. **Codex-hook premise stale.** WI-4326 claims "PostToolUse + Stop trigger registrations are absent" in `.codex/hooks.json`. Inspection shows `.codex/hooks.json` already contains `cross_harness_bridge_trigger` references (and `.claude/settings.json` likewise), so the symmetric-registration gap the WI describes no longer exists.

The remaining, genuine engineering gap is that `scripts/cross_harness_bridge_trigger.py::_is_cross_harness_trigger_active_substrate` *fail-opens* (returns `True`) when `harness-state/bridge-substrate.json` is missing/invalid, and there is no regression test asserting the inert-vs-active behavior across the full substrate value set. The existing `test_substrate_inert_path_when_disagrees_with_durable_selection` covers only the `none` -> inert direction. This proposal adds a focused regression-lock so the active-substrate predicate's contract (the very mechanism whose misconfiguration motivated WI-4326) is pinned, and adds an inline contract docstring note documenting the fail-open rationale.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge `VERIFIED`/dispatch authority) and the substrate-transaction contract `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` already establish that the configured substrate governs whether the cross-harness trigger dispatches; this proposal only adds regression coverage and an inline docstring that lock the *already-specified* active-substrate predicate behavior. No new or revised requirement/specification is introduced. (The WI's alternative framing — formally re-affirming or reversing the substrate-mode policy as a governance decision — is an owner decision, not an implementation requirement, and is surfaced in `## Owner Decisions / Input` rather than encoded as a new spec.)

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py`, `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`.

## Bridge File Chain Evidence

This proposal is filed as the next numbered, append-only versioned bridge file in its thread (`bridge/gtkb-revisit-bridge-substrate-none-decision-001.md`), with the canonical `NEW` status token on the first non-blank line. No prior bridge version is deleted or rewritten; subsequent REVISED/GO/report/VERIFIED entries will be added as further numbered files (`-002.md`, `-003.md`, ...) per the numbered-file-chain-is-canonical authority of `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governing authority for bridge dispatch; the configured substrate gates whether the cross-harness trigger dispatches, so locking the active-substrate predicate preserves the bridge's dispatch authority against silent misconfiguration.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the regression-lock preserves the durable behavior contract of the substrate configuration as a tested artifact rather than tribal knowledge that drifted (the WI-4326 drift).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each test from a cited spec clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - WI-4326 is consideration-only (no implementation approval for a policy reversal); any decision to re-affirm vs. reverse the substrate mode is an owner decision routed through AskUserQuestion, and this proposal does not encode a policy change without that channel.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform trigger script and platform tests; no application-placement boundary is crossed and no adopter/application surface is touched.
- `GOV-STANDING-BACKLOG-001` - WI-4326 is a standing-backlog work item (origin=hygiene, P3) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the WI's secondary claim concerns Codex-side hook registration parity; this proposal records the current parity state (registrations present) as evidence and the regression-lock indirectly protects the substrate that hook parity depends on.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the substrate configuration state remains artifact-backed (`harness-state/bridge-substrate.json`) and its consumption is now test-pinned rather than inferred.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the regression coverage with the substrate-configuration lifecycle state that gates trigger activeness.

## Prior Deliberations

- `DELIB-20260665` - Bridge substrate=none premise-shift surfacing (B is active PB again; June 1 'Claude-offline' premise no longer holds) - the origin deliberation for WI-4326; this proposal records that the premise has since been resolved by the substrate flip to `cross_harness_trigger`.
- `DELIB-20263793` - Loyal Opposition Verification, Bridge-Mode Config Transactions Slice 1 REVISED-1 - established the `gt mode set-bridge-substrate` transaction component and the validation contract this proposal's regression-lock pins.
- `DELIB-20260798` - Verification: Active-Status Capability Gate Lifecycle and Substrate Alignment - prior work aligning active-harness status with substrate selection; directly relevant to the "B is active PB" half of the WI-4326 premise.
- `DELIB-20261375` - Verification: Active-Status Capability Gate Lifecycle and Substrate Alignment (sibling verification record) - same alignment context.
- `DELIB-20265457` - Owner decision (2026-06-21 AUQ) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch; WI-4326 is in scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the project-scoped non-fast-lane batch authorization that covers WI-4326 implementation through active project membership in PROJECT-GTKB-RELIABILITY-FIXES; this proposal's scope (1 source docstring note + 1 test-file regression-lock; no public-surface change, no new/revised spec) falls within the authorized envelope.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items in this batch; WI-4326 is P3 (origin=hygiene), authored after the higher-priority pipeline/P1/P2 items per the batch direction.

Note on the WI's consideration-only flag: WI-4326's description states it is "consideration-only — no implementation approval" for a *policy reversal* (flip substrate back to `none`, or formally re-affirm). This proposal does NOT reverse or re-affirm the substrate-mode policy; it accepts the already-applied `cross_harness_trigger` state as current and adds regression coverage only. Should Loyal Opposition or the owner prefer that the substrate-mode policy itself be formally re-decided, that is a separate owner AUQ and is explicitly out of this implementation's scope.

## Proposed Scope

Minimal, defect-class hygiene fix. The WI premise is already resolved by intervening work; the implementation locks the resolution against regression and documents the residual fail-open behavior.

1. **`scripts/cross_harness_bridge_trigger.py`** - augment the docstring of `_is_cross_harness_trigger_active_substrate` (currently lines ~3092-3109) to explicitly document the fail-open contract: when `harness-state/bridge-substrate.json` is missing or invalid the predicate returns `True` (trigger active) for backward compatibility, and when it records a non-`cross_harness_trigger` value (`none` or `single_harness_dispatcher`) the predicate returns `False` (trigger inert, recorded as `substrate_mismatch_inert`). This is a comment/docstring-only change to the source; no behavioral logic change. (The WI-4326 drift was precisely the un-pinned `none`-while-B-active state; documenting + testing the predicate is the bounded fix, not altering dispatch behavior.)

2. **`platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`** - add a focused regression-lock test (or small parametrized set) asserting `_is_cross_harness_trigger_active_substrate` returns the correct value for the full substrate domain:
   - `cross_harness_trigger` -> `True` (active);
   - `none` -> `False` (inert);
   - `single_harness_dispatcher` -> `False` (inert);
   - missing file -> `True` (fail-open);
   - invalid/non-dict JSON -> `True` (fail-open).
   This complements the existing `test_substrate_inert_path_when_disagrees_with_durable_selection` (which only exercises the `none` -> inert end-to-end path) by pinning the predicate contract directly.

Explicitly OUT of scope (would require new requirement/owner AUQ, not this fast-batch fix):
- Flipping the substrate back to `none` or formally re-affirming the substrate-mode policy (owner decision).
- Any change to the dispatch-failure audit schema or the `substrate_mismatch_inert` reason string.
- Adding new Codex-side hook registrations (already present per inspection; no parity gap remains).

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (configured substrate gates dispatch) | `test_active_substrate_predicate_true_for_cross_harness_trigger` | `_is_cross_harness_trigger_active_substrate` returns `True` when `bridge-substrate.json` records `cross_harness_trigger` (the live configured state). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (non-matching substrate -> inert) | `test_active_substrate_predicate_false_for_none_and_single_harness` | The predicate returns `False` for `none` and for `single_harness_dispatcher`, locking the inert directions that the WI-4326 drift (`none`-while-B-active) exercised. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (fail-open contract is durable) | `test_active_substrate_predicate_fail_open_when_missing_or_invalid` | The predicate returns `True` (fail-open) when `bridge-substrate.json` is absent or contains invalid/non-dict JSON, matching the documented backward-compatibility contract. |

Execution commands:
- `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py -q --tb=short`
- `python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`
- `python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`

## Acceptance Criteria

1. The new regression-lock test(s) assert the correct active-substrate-predicate result for all five substrate-domain cases (`cross_harness_trigger` -> True; `none` -> False; `single_harness_dispatcher` -> False; missing file -> True; invalid JSON -> True).
2. `_is_cross_harness_trigger_active_substrate` carries an explicit docstring documenting the fail-open and mismatch-inert contract; no behavioral logic of the predicate or the trigger changes.
3. The three derived tests pass and the existing `test_substrate_inert_path_when_disagrees_with_durable_selection` continues to pass (no regression).
4. `ruff check` and `ruff format --check` are clean on both changed files.
5. The proposal records, as evidence for WI-4326 closure, that (a) the live substrate is `cross_harness_trigger` (premise resolved) and (b) `.codex/hooks.json` already registers `cross_harness_bridge_trigger` (parity premise resolved).

## Risks / Rollback

- Risk: a test author could pin behavior that does not match the live predicate (e.g., asserting `single_harness_dispatcher` -> True). Mitigation: the assertions are derived directly from the source logic at lines ~3104-3106 (`if substrate and substrate != "cross_harness_trigger": return False`) and the existing inert test; the verification commands run the suite before filing the report.
- Risk: over-reach — accidentally changing predicate behavior while editing its docstring. Mitigation: scope is docstring/comment-only on the source; the regression-lock would fail loudly if behavior shifted.
- Risk: the seeded DELIB IDs in `## Prior Deliberations` may not all resolve in MemBase. Mitigation: Loyal Opposition can confirm during review; the load-bearing owner-decision (`DELIB-20265457`) and PAUTH are the authorization evidence and are independently citable.
- Rollback: revert the docstring edit in `cross_harness_bridge_trigger.py` and remove the added test(s); the change is additive (one docstring + new tests), carries no migration, and is fully reversible.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py`

## Recommended Commit Type

`fix`
