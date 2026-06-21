NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Owner-decision-tracker: auto-resolve cross-turn prose-ask once a later AskUserQuestion answers it

bridge_kind: prime_proposal
Document: gtkb-owner-decision-tracker-auto-resolve-cross-turn
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4289

target_paths: [".claude/hooks/owner-decision-tracker.py", "platform_tests/hooks/test_owner_decision_tracker.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The owner-decision tracker's Stop handler (`.claude/hooks/owner-decision-tracker.py`, `_stop_handler`) auto-resolves a prose decision-ask only when a correlated `AskUserQuestion` (AUQ) occurs in the **same turn**. When a prose decision-ask is recorded as pending in turn N and a covering AUQ is answered in turn N+1 (cross-turn), the prior pending prose entry is NOT auto-resolved: Scan A processes the new AUQ and creates a fresh resolved entry, but it never revisits the pre-existing `## Pending` prose entries from earlier turns. The orphaned prose entry lingers in `## Pending` (observed S403 with DECISION-0983 / DECISION-0987) and requires a manual `resolve DECISION-NNNN` / `clear pending` shortcut. This proposal closes the cross-turn half of the gap by reusing the existing fail-closed two-signal correlator to resolve already-pending prose entries against the current turn's answered AUQ.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` already establishes the two-signal-required (Signal A discriminating-token Jaccard plus one of B1/B2/B3) correlation contract and the fail-closed bias (never silently auto-resolve an unrelated decision). This fix extends the *application point* of that existing correlation contract from same-turn prose matches to already-pending prose entries, using the identical `_correlate_prose_to_auq` predicate; it introduces no new correlation semantics, no new public surface, and no new/revised specification. The owner-direct-plain-text-answer resolution path (the harder half, with false-resolution risk) is explicitly deferred per the WI and is NOT in scope.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks/owner-decision-tracker.py`, `platform_tests/hooks/test_owner_decision_tracker.py`.

## Specification Links

- `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` - the governing correlation contract; this fix reuses its two-signal-required `_correlate_prose_to_auq` predicate and fail-closed bias verbatim, extending its application from same-turn prose to already-pending cross-turn prose entries. No correlation semantics change.
- `SPEC-AUQ-POLICY-ENGINE-001` - AUQ is the sole valid owner-decision channel; this fix improves the tracker's fidelity by clearing pending prose-ask noise once the owner has in fact answered via AUQ, reinforcing the AUQ-only policy rather than weakening it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the change is filed and reviewed through the bridge protocol; the hook itself is bridge-protocol support tooling whose correctness preserves the GO/VERIFIED audit discipline for owner decisions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the durable owner-decision ledger (`memory/pending-owner-decisions.md`) is the artifact being kept consistent: resolved decisions move out of `## Pending` into `## Resolved` so the artifact reflects true lifecycle state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each test from a cited spec clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to a GT-KB platform hook (`.claude/hooks/...`) and platform tests (`platform_tests/...`); no application/adopter surface is touched and no placement boundary is crossed.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the owner-decision tracker is a Claude-side Stop hook; this fix is behavior-internal to that hook and does not alter the hook-parity registration surface, so no Codex-side parity work is implied.
- `GOV-STANDING-BACKLOG-001` - WI-4289 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the resolved-decision state transition remains artifact-backed (driven by an answered AUQ tool_result in the transcript), not inferred from chat heuristics alone.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the pending-to-resolved lifecycle trigger of the owner-decision ledger with the verification-equivalent event (the owner answering the covering AUQ).

## Prior Deliberations

- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch; WI-4289 is in scope.
- _No prior deliberations on the cross-turn auto-resolve mechanism specifically: the same-turn correlation work (DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001) is the nearest precedent and is cited under Specification Links; no DA record rejects or supersedes a cross-turn extension of it._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the active project authorization envelope that covers source/test/hook changes for PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane work; WI-4289 (origin=improvement, P3, single-concern, no new public surface, bounded to one hook + its test) falls within this envelope through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items; this WI is one of them. No additional per-item owner decision is required to author or (post-GO) implement this bounded defect-class fix.

## Proposed Scope

1. In `.claude/hooks/owner-decision-tracker.py` `_stop_handler`, capture the answer text alongside each answered AUQ collected in the existing Scan A loop. Today `auq_questions_this_turn` accumulates `(question_text, options)`; extend the answered branch (the branch that already sets `entry.answer = _extract_answer_text(tr)`) to also record `(question_text, options, answer)` for answered AUQ in a new local list (e.g. `answered_auq_this_turn`). This is additive and does not change the existing same-turn correlation list used by Scan B.

2. Add a new "Scan A2 - cross-turn pending-prose resolution" step that runs after Scan A and before/independent of Scan B, iterating a snapshot of `sections["pending"]` and, for each pending entry that is a prose-detected ask (`detected_via` starts with `prose:`), testing it against each answered AUQ from this turn via the existing `_correlate_prose_to_auq(pending.question, auq_question, auq_options)`. On the first correlated match, move that entry from `sections["pending"]` to `sections["resolved"]`, set `status="resolved"`, `resolved_at`/`resolved_in_session`, `resolved_via="cross_turn_auq_formalization"`, populate `answer` from the matched AUQ's answer text, and append a notes line citing `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` (cross-turn application). Set `mutated = True`.

3. Constraints preserving the existing contract:
   - Reuse `_correlate_prose_to_auq` unchanged - the two-signal-required, fail-closed predicate is the safety boundary; no new/looser matching is introduced.
   - Only `prose:`-detected pending entries are eligible (AUQ-origin pending entries are resolved by their own tool_result, not by correlation).
   - Iterate over a copied snapshot of the pending list while mutating the underlying sections to avoid in-place mutation hazards; preserve original list ordering for unaffected entries.
   - Idempotence: a pending entry already resolved in a prior run is no longer in `sections["pending"]`, so re-running on the same transcript does not double-resolve; the existing `_question_hash` idempotence for Scan A is unaffected.
   - The new path only moves entries to `## Resolved`; it never deletes, never emits a block decision, and never alters the F3 block-emission condition (which is keyed to fresh prose matches in the current turn, not to pre-existing pending entries).

4. Add regression tests in `platform_tests/hooks/test_owner_decision_tracker.py` plus the minimal JSONL fixture(s) under `platform_tests/hooks/fixtures/owner_decision_tracker/` needed to exercise the cross-turn path through the subprocess CLI surface (outside-in, matching the existing fixture-driven test architecture). See the verification plan.

This is the cross-turn defect-removal path. The WI's harder half (resolving a prose-ask when the owner answers in plain text rather than via AUQ) carries false-resolution risk and is explicitly deferred to a separate decision per the WI; it is out of scope here.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` (correlated AUQ resolves a prose ask) applied cross-turn | `test_cross_turn_pending_prose_resolves_on_later_correlated_auq` | Run 1 (fixture: prose ask, no AUQ) leaves a `prose:`-detected entry in `## Pending`. Run 2 on the same project dir (fixture: a correlated answered AUQ, no prose) moves that entry to `## Resolved` with `resolved_via: cross_turn_auq_formalization` and a populated `answer`, and removes it from `## Pending`. |
| `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` (fail-closed: never auto-resolve an unrelated decision) | `test_cross_turn_uncorrelated_auq_leaves_prose_pending` | A pending `prose:` entry about topic X is NOT resolved when a later turn answers an AUQ about an unrelated topic Y (two-signal correlation rejects boilerplate-only overlap); the entry remains in `## Pending`. |
| `SPEC-AUQ-POLICY-ENGINE-001` / `DCL-...-SAME-TURN-...-001` (same-turn behavior unchanged; no regression) | `test_same_turn_correlation_still_resolves_after_cross_turn_change` | The existing same-turn correlated fixture (`turn_prose_auq_correlated_substring.jsonl`) still yields `resolved_via: same_turn_auq_formalization` in `## Resolved` and nothing in `## Pending` (Scan A2 does not disturb the same-turn Scan B path). |
| T13 graceful-degradation contract (hook never raises) | `test_cross_turn_resolution_never_raises_on_empty_and_malformed` | The hook exits 0 for the cross-turn fixtures and for a no-pending / no-AUQ turn (Scan A2 is a no-op when either the pending-prose set or the answered-AUQ set is empty). |

Execution commands:
- `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short`
- `python -m ruff check .claude/hooks/owner-decision-tracker.py platform_tests/hooks/test_owner_decision_tracker.py`
- `python -m ruff format --check .claude/hooks/owner-decision-tracker.py platform_tests/hooks/test_owner_decision_tracker.py`

## Acceptance Criteria

1. A prose decision-ask recorded as pending in an earlier turn is moved to `## Resolved` with `resolved_via: cross_turn_auq_formalization` and a populated `answer` when a later turn answers a correlated AUQ (correlation judged by the existing two-signal `_correlate_prose_to_auq`).
2. A pending prose entry is NOT resolved by a later, uncorrelated AUQ (fail-closed contract preserved); it stays in `## Pending`.
3. Existing same-turn AUQ resolution behavior is unchanged (no regression in the same-turn correlated / uncorrelated tests), and the F3 block-emission condition is unchanged.
4. The hook never raises (exit 0) across the new fixtures and the empty/no-op cases.
5. The four derived tests pass; `ruff check` and `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: false cross-turn resolution of an unrelated pending prose entry. Mitigation: the new path reuses the existing two-signal-required, fail-closed `_correlate_prose_to_auq` unchanged, which already rejects the boilerplate-only counterexample (commit-vs-deploy); only `prose:`-origin pending entries are eligible.
- Risk: in-place mutation hazard while iterating `sections["pending"]`. Mitigation: iterate a copied snapshot and rebuild/preserve the pending list; covered by the cross-turn resolution test verifying both removal from Pending and presence in Resolved.
- Risk: double-resolution on re-run. Mitigation: a resolved entry leaves `sections["pending"]`, so subsequent runs find nothing to resolve; existing `_question_hash` idempotence for Scan A is untouched.
- Risk: disturbing the same-turn correlation path. Mitigation: Scan A2 is additive and only reads the answered-AUQ list; the regression test `test_same_turn_correlation_still_resolves_after_cross_turn_change` guards the same-turn path.
- Rollback: revert the additive answered-AUQ capture and the Scan A2 block in `_stop_handler` plus the new tests/fixtures. The change is a localized, guarded addition with no migration and no schema change; fully reversible.

## Files Expected To Change

- `.claude/hooks/owner-decision-tracker.py`
- `platform_tests/hooks/test_owner_decision_tracker.py`
- (new fixture file(s) under `platform_tests/hooks/fixtures/owner_decision_tracker/` for the cross-turn test; co-located test data, not a separate source surface)

## Recommended Commit Type

`fix`
