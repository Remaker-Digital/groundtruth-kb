# Implementation Proposal — Owner-Decision-Tracker: Cached Pending Block Exclusion

bridge_kind: prime_implementation_proposal

## Summary

Extend `_is_inside_structural_context` in `.claude/hooks/owner-decision-tracker.py` to treat matches inside a `### Pending Owner Decisions` markdown section as structural context (skip the match). This eliminates the recursive-fire pattern where the cached SessionStart payload's `### Pending Owner Decisions` block, when re-rendered as user-visible startup content, contains verbatim DECISION-NNNN body text that lexically matches the `offering_or_choice` and similar patterns — producing turn-end blocks that have nothing to do with the agent's actual prose.

## Background

The owner reports this as a recurring issue in S350 (2026-05-14). Concrete recurrence: my prior turn this session rendered the cached startup disclosure verbatim (per the SessionStart contract — "Do not summarize, paraphrase, shorten, reorder, or omit"). The `### Pending Owner Decisions` block contained the text of DECISION-0572 ("want me to proceed with the full 2-file..."), which matches the `offering_or_choice` pattern at line 108-111. The Stop hook emitted a block decision, even though I made no new prose decision-ask.

This is a salience-case (per `.claude/rules/canonical-terminology.md`): the cached-pending-block context is a real exception that was not on the structural-pre-check candidate list. The structural pre-check at line 183-199 already covers fenced code, indented code, blockquotes, and HTML comments — adding section-scope exclusion follows the same pattern.

## Specification Links

- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic pattern matching only; no LLM classifiers. Section-scope structural exclusion is deterministic.
- `SPEC-AUQ-POLICY-ENGINE-001` — central deterministic policy engine returning canonical outcomes; structural pre-check is the engine's existing exception surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from linked specs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the Only Valid Owner-Decision Channel" — the rule the tracker enforces; this proposal narrows enforcement, not the rule.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants.
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review gate.

## Prior Deliberations

- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` REVISED-1 Codex GO at `-004` — established the Stop-mode block decision (the substrate this proposal narrows).
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` VERIFIED — Sub-slice A activated the tracker; established `PROSE_DECISION_PATTERNS` + `PROSE_FALSE_POSITIVE_GUARDS` contract.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-005.md` Codex GO at `-006` — Sub-slice A follow-up that added the structural pre-check for fenced code / indented code / blockquotes / HTML comments. This proposal extends that pre-check with a 5th context.
- Memory `feedback_avoid_quoting_decision_tracker_fragments` (S328) — the operational workaround Prime Builder has been applying when this fires; this proposal converts the workaround into a deterministic exclusion.

## Owner Decisions / Input

Owner statement in S350 (2026-05-14): "FYI - this is a recurring issue" (provided as a screenshot acknowledgement that the recursive-fire pattern keeps recurring), followed by "Please continue."

This proposal interprets "Please continue" as authorization to file the captured follow-on candidate I described in the Slice 1 closing note, as a separate bridge thread (not folded into Slice 2). The decision class is operational hook-tightening; the rule narrowed is `PROSE_DECISION_PATTERNS` enforcement scope, not the AUQ-only contract itself, and no owner-visible behavior change is introduced. If Codex review judges this proposal should have been an explicit AUQ-gated decision rather than executed-as-directed, NO-GO and Prime files a REVISED with an AUQ-evidence section.

## Requirement Sufficiency

Existing requirements sufficient. The AUQ-only enforcement contract at `.claude/rules/prime-builder-role.md` and the tracker's behavior contract at `SPEC-AUQ-POLICY-ENGINE-001` are unchanged; this proposal narrows a deterministic false-positive surface within the existing contract. Cached SessionStart payloads are the rendering surface, not new behavior.

## target_paths

- `.claude/hooks/owner-decision-tracker.py` (extend `_is_inside_structural_context`)
- `.claude/hooks/owner-decision-tracker.py` (add test fixtures in adjacent test module if not already present)
- `platform_tests/hooks/test_owner_decision_tracker.py` if it exists, otherwise add the test alongside existing tracker tests

## Implementation Plan

1. **Extend `_is_inside_structural_context`** in `.claude/hooks/owner-decision-tracker.py:183-199` with a 5th context: section-heading scope. Specifically:
   - Scan `text[:match_start]` for the last line matching `^#{2,3}\s+Pending Owner Decisions\s*$` (case-insensitive).
   - If found, scan the remaining `text[last_heading_end:match_start]` for a subsequent line matching `^#{1,3}\s+` (any heading of equal or higher level that would close the section).
   - If a `Pending Owner Decisions` heading is present AND no closing heading appears before the match position, the match is inside the cached pending block — return True.
2. **No change to** `PROSE_DECISION_PATTERNS` or `PROSE_FALSE_POSITIVE_GUARDS`. The fix is structural-context exclusion only.
3. **Add unit tests** asserting:
   - `test_structural_context_pending_owner_decisions_block_h3`: an `offering_or_choice` match inside a `### Pending Owner Decisions` block returns `is_inside_structural_context = True`.
   - `test_structural_context_pending_owner_decisions_block_h2`: same for `## Pending Owner Decisions` (h2 variant).
   - `test_structural_context_pending_owner_decisions_closes_at_next_heading`: a match AFTER a sibling-level heading that closes the pending block returns `is_inside_structural_context = False` (the structural protection ends at the next heading).
   - `test_structural_context_genuine_ask_unaffected`: a normal prose decision-ask outside any pending block still matches (regression check).

## Spec-to-Test Mapping

- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` → all four tests assert deterministic regex/structural behavior (no LLM input).
- `SPEC-AUQ-POLICY-ENGINE-001` → `test_structural_context_genuine_ask_unaffected` ensures the policy engine's positive-detection path remains intact.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → spec-to-test mapping is one test per assertion class.

## Risks

- **False-negative cascade**: if a genuine prose decision-ask appears in the same response as a cached pending block AND falls inside the pending block's section scope, it would be missed. *Mitigation:* genuine asks should not be in the cached pending block (the block is a list of pre-existing decisions; new asks go in fresh prose). The `closes_at_next_heading` test verifies that scope correctly terminates so subsequent prose is still scanned.
- **Section regex too narrow**: matches only the exact heading text `Pending Owner Decisions`. *Mitigation:* this is the only known recurring false-positive source. If new cached-block context surfaces in future startup payload revisions, a follow-up proposal adds them.
- **Multi-block startup payloads**: if a future startup payload renders the pending block with different heading wording, the fix becomes stale. *Mitigation:* the SessionStart contract requires verbatim rendering of the cached payload (per the explicit "Do not summarize, paraphrase, shorten, reorder, or omit" instruction), so heading wording is stable until the cache generator is rev'd. Cache-generator changes already require their own bridge thread review.

## Rollback

Remove the section-scope branch from `_is_inside_structural_context` and remove the associated tests. The hook reverts to its pre-fix behavior (fenced/indented/blockquote/HTML-comment structural pre-check only).

## Verification Procedure

1. Run `python -m pytest .claude/hooks/test_owner_decision_tracker.py -q --tb=short` (or the canonical path for tracker tests) — all existing tests must continue to pass; the four new tests must pass.
2. Manual smoke: in a fresh session, render the cached startup payload's `### Pending Owner Decisions` block; the Stop hook must NOT emit a block decision based on text inside that block.
3. Negative manual smoke: in the same response, append a genuine prose decision-ask outside the pending block; the Stop hook MUST emit a block decision (this verifies the fix is scoped to the pending block, not a blanket pattern weakening).

## Acceptance Criteria

- `_is_inside_structural_context` returns True for matches inside `### Pending Owner Decisions` and `## Pending Owner Decisions` sections.
- Structural scope terminates at the next heading of equal-or-higher level.
- Existing `PROSE_DECISION_PATTERNS` and `PROSE_FALSE_POSITIVE_GUARDS` are unchanged.
- All preflights (applicability, clause) pass for this proposal.
- Existing tracker test suite continues to pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
