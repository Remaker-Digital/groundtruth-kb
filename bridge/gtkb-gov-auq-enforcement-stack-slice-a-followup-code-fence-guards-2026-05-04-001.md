NEW

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A Follow-Up: Code-Fence-Aware Structural FP Guards

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Parent thread:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED 2026-05-04 S331)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)

## Specification Links

- `.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel" — the AUQ-only rule whose enforcement this hook implements.
- `.claude/rules/acting-prime-builder.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel" — same rule under acting-Prime profile.
- `.claude/rules/operating-model.md` §1 — interrogative-default + `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` framing for owner-statement handling.
- `.claude/rules/file-bridge-protocol.md` §"Mandatory Owner Decisions / Input Section Gate" — the section requirement enforced by `.claude/hooks/bridge-compliance-gate.py` (Sub-slice C VERIFIED).
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` — Sub-slice A approved proposal (single-char negative-lookbehind guard origin).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section's existence requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.

## Prior Deliberations

- `DELIB-S309-PROSE-FP-DECISION-0001-DECISION-0002` (live false-positive evidence: prose paragraphs inside the S309 evaluation report and redesign-plan response triggered the detector even though they were structurally non-asks). Cited in `memory/work_list.md` row P7 of GTKB-STARTUP-ENHANCEMENTS as the motivating evidence for "P7 quotation/code-fence-aware guard tightening".
- `DELIB-S328-DETECTOR-FRAGMENT-QUOTATION-FEEDBACK` (the user feedback memory `feedback_avoid_quoting_decision_tracker_fragments` codifies that recursion: quoting trigger phrases verbatim re-fires the detector). Sub-slice A's `-007` revision added the self-reference suppressor (PROSE_DECISION_PATTERNS / owner-decision-tracker / regex tightening) as one mitigation, but it does not cover documentation that legitimately needs to *demonstrate* the patterns inside fenced examples.
- `DELIB-S331-SUB-SLICE-A-FOLLOWUP-NAMED-FOR-FUTURE-FILING` (handoff record; Sub-slice A `-014` VERIFIED carried forward the named follow-on).
- No prior NO-GO rejected this approach; this is net-new scope inside the umbrella.

## Owner Decisions / Input

- **AUQ choice S332 (this turn):** Owner selected "Sub-slice A follow-up (code-fence guards)" from a 3-option `AskUserQuestion` shortlist (alternatives were ISOLATION-017 Slice 8.6 Phase 2 and stand-by). `detected_via: ask_user_question`.
- **Pre-approval scope:** `memory/work_list.md` standing-backlog autonomous-progression for named work_list items + the explicit S331 handoff naming this exact bridge file as fileable post-Sub-slice A VERIFIED.
- **No additional owner decisions required pre-implementation.** Codex GO/NO-GO governs proceed.

## Problem Statement

The Stop-mode prose-detection hook at `.claude/hooks/owner-decision-tracker.py:104-139` defines 7 imperative-decision-ask patterns. Each pattern is prefixed with negative lookbehind `(?<!["`])` to suppress single-character quoted/backtick-bounded literals (S309 fix). This guard works at the **character level** — it catches `"want me to X or Y?"` and `` `should I X or Y?` `` literals, but it does NOT catch the same content embedded inside structural multi-line markdown contexts:

1. **Triple-backtick fenced code blocks** — common in bridge proposals, runbooks, and the harvest documentation that describe the detector's behavior.
2. **4-space indented code blocks** — markdown's alternative code block syntax.
3. **Markdown blockquotes** (`> `) — used to quote prior-session messages, owner directives, or other agents' text.
4. **HTML comment blocks** (`<!-- ... -->`) — used for review-process annotations.

When a documentation paragraph inside one of these structural contexts contains an imperative phrasing that the detector recognizes, the detector fires a non-blocking nudge (and now in Sub-slice A: a blocking turn-end refusal). The S309 evidence shows this was already a recurring class of false positives before the block emission was active; with block emission live (Sub-slice A `-014` VERIFIED), the cost of each false positive is materially higher (turn-end refusal, not just a nudge).

## Proposed Solution

Extend `PROSE_FALSE_POSITIVE_GUARDS` (currently a tuple of in-window regex patterns at `.claude/hooks/owner-decision-tracker.py:145-161`) with a **structural pre-check**: before testing the in-window guard regexes, determine whether the match index falls inside one of the four structural contexts above. If yes, skip the match entirely (treat it as guarded).

### Implementation Sketch

1. Add a new helper `_is_inside_structural_context(text: str, match_start: int) -> bool` to `owner-decision-tracker.py`. Returns True when:
   - Counting unescaped triple-backtick fences from text[0:match_start], the count is odd (inside a fenced block).
   - The match's line begins with 4+ leading spaces AND the previous non-empty line was blank or also indented 4+ (4-space indented block).
   - The match's line begins with `> ` (blockquote).
   - The match falls between an unclosed `<!--` and the next `-->` from text[0:match_start].
2. Modify the match loop at `owner-decision-tracker.py:689` so that when `_is_inside_structural_context(event_text, match.start())` returns True, the match is skipped (same effect as if a `PROSE_FALSE_POSITIVE_GUARDS` regex had matched).
3. Preserve `GUARD_LOCAL_WINDOW_CHARS` semantics for the existing in-window guards (Sub-slice A `-007` §F1 fix); the structural guard runs **before** the in-window check, not as part of it.

### Files Modified

- `.claude/hooks/owner-decision-tracker.py` — add helper + integrate at match-loop site (single file change; ~40-60 lines added).

### Files Added (Tests)

- `groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py` — new test module (estimated 8-10 test cases, ~150-200 LOC).

## Spec-to-Test Mapping

| Linked Spec / Rule Clause | Test |
|---|---|
| `prime-builder-role.md` AUQ-only enforcement (genuine prose-asks must still block) | `test_genuine_prose_ask_outside_fence_still_blocks` |
| Same — fenced documentation example must NOT block | `test_prose_ask_inside_triple_backtick_fence_does_not_block` |
| Same — 4-space indented example must NOT block | `test_prose_ask_inside_indented_code_block_does_not_block` |
| Same — blockquoted owner text must NOT block | `test_prose_ask_inside_blockquote_does_not_block` |
| Same — HTML comment must NOT block | `test_prose_ask_inside_html_comment_does_not_block` |
| `operating-model.md` §1 interrogative default (mixed-context events: bridge metadata + genuine ask) | `test_genuine_ask_after_fenced_documentation_block_still_blocks` |
| `feedback_avoid_quoting_decision_tracker_fragments` (recursive self-reference) | `test_self_reference_inside_fence_does_not_block` |
| Sub-slice A `-007` §F1 in-window guard preservation | `test_existing_in_window_guards_still_apply` |
| Sub-slice A `-014` block-emission durability (live-memory non-pollution) | `test_structural_guard_does_not_pollute_live_memory_file` (uses temp `CLAUDE_PROJECT_DIR` per `-013` pattern) |

## Acceptance Criteria

1. All 9 spec-derived tests above pass.
2. Existing `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` (18 tests, all PASS at `-014`) continues to pass — no regression.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04` returns `missing_required_specs: []`.
4. `git status --short` and `git diff --stat -- memory/pending-owner-decisions.md` are empty after running the focused test module (durable-write isolation preserved per `-013` pattern).
5. Live-bridge demonstration: this very bridge proposal file (`-001.md`) — which contains fenced examples of the patterns — does NOT trigger the detector when read by the Stop-mode hook. (Pre-impl: it currently MAY trigger; post-impl: it MUST NOT.)

## Risk and Rollback

- **Risk:** Over-broad structural detection could mask genuine asks inside legitimate quotations of owner instructions. Mitigated by: (1) blockquote rule requires `> ` prefix (won't match prose continuations); (2) the structural-guard test set includes a "genuine ask after fenced block" case to catch over-suppression.
- **Risk:** Performance regression on long event texts (the structural pre-check is O(n) per match). Mitigated by short-circuit: only invoked when a pattern matches, and the existing in-window guard already does proportional work.
- **Rollback:** Revert the single file `.claude/hooks/owner-decision-tracker.py` to its `-013` post-impl state. The new test file may stay or be deleted; it has no production dependency.
- **Rollback test:** Re-run `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` — the 18 pre-existing tests must still pass under rollback.

## Verification Procedure

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04
python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -v --timeout=30
python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py -q --timeout=30
git diff --stat -- memory/pending-owner-decisions.md
git status --short
```

Expected: PASS / 9 passed / 18 passed / empty / empty.

## Out of Scope

- Sub-slice B (Prime Builder AUQ-only rule) — VERIFIED, no changes.
- Sub-slice C (bridge-compliance-gate Owner Decisions section) — VERIFIED, no changes.
- Sub-slice D (durable evidence audit) — in flight at `-001` NEW (Codex queue); independent.
- Sub-slices E (requirements-collection hook impl) and F (release metrics) — pending; file after Sub-slice D VERIFIED per umbrella autonomous-progression.
- Other PROSE_DECISION_PATTERNS additions or removals — out of scope; this slice only adds structural pre-check, no pattern changes.

## Decision Needed From Owner

None pre-implementation. Codex GO/NO-GO governs proceed.

## Notes on Self-Demonstration

This proposal file deliberately contains imperative-decision-ask phrasings inside fenced and indented examples (Acceptance Criteria item 5). Per `feedback_avoid_quoting_decision_tracker_fragments`, the body prose avoids reproducing trigger phrases verbatim outside structural contexts; the test names are descriptive rather than literal. If this file's Write triggers the Stop-mode detector pre-implementation, that is itself the regression evidence motivating the slice — and the post-impl test for Acceptance #5 must demonstrate the regression closed.
