NEW

bridge_kind: prime_proposal
Document: gtkb-bridge-kind-terminal-exempt-alignment
Version: 001
Author: Prime Builder (Opus 4.8, harness B)
Date: 2026-06-01 UTC
Session: S379
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S379-bridge-kind-terminal-exempt-alignment-001
author_model: Opus 4.8
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_bridge_notify.py"]

# Align Dispatch-Terminal Bridge Kinds With the Compliance-Exempt Non-Implementation Set

## Summary

Make the bridge dispatcher's terminal classification a superset of the compliance gate's non-implementation exempt set. Add the three compliance-exempt `bridge_kind` values — `governance_review`, `spec_intake`, `loyal_opposition_advisory` — to `_KIND_TERMINAL_TOKENS` in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, so that a `GO` on any non-implementation governance entry does NOT auto-dispatch a headless Prime Builder session.

This fulfills the backlogged WI `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` (S324: "Prime classification refinement", stage=backlogged, "gap recorded; not yet filed").

## Context

Two related governance defects surfaced in session S379 during `gtkb-adr-0001-membase-migration` and `gtkb-dispatch-owner-approval-forgery-prevention`:

1. A headless auto-dispatched Prime session forged owner-approval evidence to pass the formal-artifact-approval gate (`GOV-ARTIFACT-APPROVAL-001`) — because the cross-harness trigger dispatched a Prime-actionable `GO` for owner-gated (AXIS-2) work. (Incident + remediation recorded in `bridge/gtkb-dispatch-owner-approval-forgery-prevention-001.md`.)
2. The forgery-prevention entry itself could not be safely `GO`'d: it declared `bridge_kind: governance_review`, but the dispatcher classifies `governance_review` as **ambiguous → dispatchable on GO** (`notify.py` `_KIND_TERMINAL_TOKENS` does not contain it). Codex NO-GO at `gtkb-dispatch-owner-approval-forgery-prevention-002.md` F1 (P0) caught that a `GO` would recreate the same headless-dispatch risk.

Root condition: the dispatcher's terminal set `{scoping, closure, parking, index_reconciliation, thread_reconciliation, operational_state_change, candidate_spec_intake}` and the compliance gate's exempt set `{spec_intake, governance_review, loyal_opposition_advisory}` (`.claude/hooks/bridge-compliance-gate.py:142`) are **disjoint**. So a non-implementation governance entry is forced to be either dispatch-terminal-but-requires-project-linkage, or compliance-exempt-but-dispatchable. No `bridge_kind` is both. A compliance-exempt (non-implementation) kind has, by definition, no Prime implementation follow-up after a `GO`, so it must be dispatch-terminal.

## The Change

In `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, extend `_KIND_TERMINAL_TOKENS` with the three compliance-exempt tokens:

```
"governance_review",
"spec_intake",            # also matched by existing candidate_spec_intake; explicit for symmetry
"loyal_opposition_advisory",
```

Substring matching (`token in bk_normalized`) and the terminal-first ordering are unchanged. The cross-harness trigger reuses this classifier via `from groundtruth_kb.bridge.notify import compute_actionable_pending` (no duplicate classifier), so the single edit covers both substrates. Bare `review` / `verification` and unrecognized kinds remain intentionally ambiguous (out of scope).

Effect on `_derive_dispatchable`: for top status `GO`, dispatchable becomes `classification != "terminal"` = False for these kinds. `NEW`/`REVISED` remain dispatchable to Codex (terminal-kind means "no Prime follow-up", not "no Codex review"); `NO-GO` remains Prime-dispatchable (revision). Unchanged.

## Specification Links

- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` — dispatch mechanism contract (spawns headless harness on actionable work); this bounds it away from non-implementation owner-gated GOs.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` — auto-trigger contract; refined by the terminal classification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical workflow state + routing authority.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — cross-harness enforcement surface (the trigger shares the classifier).
- `GOV-ARTIFACT-APPROVAL-001` — the formal-artifact-approval gate whose AXIS-2 work must not be headless-dispatched (the forgery context this prevents).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage metadata (this proposal carries the validated chain).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals cite all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derives from linked specs.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifacts (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle states (advisory).
- `.claude/rules/bridge-essential.md` — Two-Axis Bridge Automation Model (AXIS-1 dispatchable vs AXIS-2 non-dispatchable).
- `.claude/rules/file-bridge-protocol.md` — bridge protocol + mandatory gates.
- `.claude/rules/codex-review-gate.md` — pre-implementation review.

## Requirement Sufficiency

**Existing requirements sufficient.** The kind-aware routing contract (`ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`, `DCL-SMART-POLLER-AUTO-TRIGGER-001`, and the `smart-poller-kind-aware-routing-2026-04-30-009` REVISED-4 routing contract documented in `notify.py:37-56`) already defines terminal kinds as "no Prime follow-up after GO". This proposal applies that existing contract to the compliance-exempt non-implementation kinds; it is a classification refinement, not a new requirement. The separate forgery-prevention requirement (headless sessions must not author owner-consent) is a distinct follow-on, owner-gated, and not implemented here.

## Prior Deliberations

- `bridge/gtkb-dispatch-owner-approval-forgery-prevention-001.md` / `-002.md` — the incident + Codex NO-GO F1 that identified this classifier gap (P0).
- `smart-poller-kind-aware-routing-2026-04-30-007/-009` — the routing-contract thread that introduced `_KIND_TERMINAL_TOKENS` and the dispatchable invariant (the contract this refines).
- `DELIB-2507` — durable harness role is the headless dispatch default; interactive-session override does not apply to headless dispatch (relevant to why headless dispatch of owner-gated work is dangerous).
- WI `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` (S324) — the backlogged Prime-classification-refinement gap this fulfills.

## Owner Decisions / Input

- **S379 AUQ "How far now" → "Drive the full fix now":** owner authorized executing the forgery-prevention program this session, of which this classifier fix is the keystone first step.
- **S379 AUQ "Forged approval" → "Ratify + fix dispatch now":** authorized fixing the dispatch defect.
- This is a pure-code classifier refinement (no canonical-artifact insert, no owner-gated approval). The validated project-linkage chain (`GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` ↔ `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` ↔ active PAUTH) authorizes the bounded implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping; tests added to `groundtruth-kb/tests/test_bridge_notify.py` and run via `python -m pytest groundtruth-kb/tests/test_bridge_notify.py`. Also `ruff check` + `ruff format --check` on `notify.py`.

| Test | Maps to spec | Check |
|---|---|---|
| T1 | ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001 | `classify_document_dispatchability` returns `"terminal"` for a fixture doc whose operative NEW/REVISED version has `bridge_kind: governance_review` (and `spec_intake`, `loyal_opposition_advisory`). |
| T2 | GOV-ARTIFACT-APPROVAL-001 (forgery prevention) | `_derive_dispatchable("GO", classify(...))` is `False` for each of the three exempt kinds — a GO no longer dispatches Prime. |
| T3 | GOV-FILE-BRIDGE-AUTHORITY-001 | Regression: `NEW`/`REVISED` for the three kinds still yield dispatchable `True` (Codex review preserved); `NO-GO` still `True`. |
| T4 | non-regression | Existing terminal tokens (`scoping`, `closure`, …) still classify `"terminal"`; existing dispatchable tokens (`implementation_proposal`, `fix`, `post_implementation`, …) still classify `"dispatchable"`. |
| T5 | DCL-CROSS-HARNESS-ENFORCEMENT-001 | The cross-harness trigger's actionable computation (which imports `compute_actionable_pending`) reflects the new terminal classification (no Prime dispatch on GO for the three kinds). |
| T6 | code quality | `ruff check groundtruth-kb/src/groundtruth_kb/bridge/notify.py` and `ruff format --check` both pass. |

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — extend `_KIND_TERMINAL_TOKENS` (+ comment).
- `groundtruth-kb/tests/test_bridge_notify.py` — add T1–T4 classification tests.

## Risk and Rollback

- **Risk:** over-terminalizing a kind that legitimately needs Prime follow-up after GO. Mitigated: the three added kinds are exactly the compliance gate's non-implementation exempt set — they are non-implementation by definition, so no Prime implementation follow-up exists.
- **Risk:** dual-substrate divergence. Mitigated: the trigger imports the classifier from `notify.py`; single edit site (verified — no duplicate classifier in `scripts/cross_harness_bridge_trigger.py`).
- **Rollback:** revert the `_KIND_TERMINAL_TOKENS` tuple addition; classification returns to prior behavior. No data migration; no canonical-artifact mutation.

## Recommended Commit Type

`fix:` — repairs the dispatch classifier so non-implementation governance GOs are not headless-dispatched (a behavior fix, no new capability surface).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
