NEW

# Implementation Proposal — Owner-Decision Tracker: Pattern Bounds + Same-Turn AUQ Auto-Resolution

bridge_kind: prime_proposal
Document: gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC

## Claim

Fix two narrow defects in `.claude/hooks/owner-decision-tracker.py` surfaced by owner observation 2026-05-09 (LO startup payload pollution from a stale prose-detected entry):

1. **Pattern over-match.** The captured `question` field bundles up to ±20 characters of context surrounding the matched regex group, including decorative prefixes/suffixes from adjacent markdown structures (e.g., insight-box closings, list introducers). The captured text is not the question — it's the question plus surrounding noise. Tightening: extract the actual matched group, then optionally extend to sentence boundaries within a small bounded window.

2. **No same-turn AUQ auto-resolution for prose-detected entries.** The hook's existing same-turn-answered logic (lines 11-13 docstring; "send same-turn-answered questions directly to `## Resolved`") applies to AskUserQuestion-detected entries that receive a tool_result in the same turn. It does NOT apply to prose-detected entries that are subsequently re-formalized via an AskUserQuestion call later in the same turn. Result: when Prime catches a prose decision-ask via the Stop hook block emission, formalizes it as a proper AUQ, and the owner answers, the prose entry persists with `status: pending` while the AUQ entry is recorded as resolved. Stale entries pollute downstream startup disclosures.

Net effect: fresh harness sessions read `memory/pending-owner-decisions.md` as part of startup and surface stale prose-pattern captures as actionable items. The owner's startup screen shows "1 owner decision(s) await a response" pointing at a question already answered minutes earlier.

## Why Now

Owner observation 2026-05-09 (S339) — LO startup screenshot showed `DECISION-0494` listed under "Pending Owner Decisions" with the captured `question` text containing decorative prefix bytes from the closing of an insight box, the actual prose question (since formalized as AUQ later the same turn and answered "Wait — status sharing only"), and a list-introducer fragment. The same-turn AUQ formalization did not auto-resolve the prose entry.

This is a small targeted fix. Out of scope: broader prose-pattern set redesign, structural-context detection (already handled by `_is_inside_structural_context`), or LLM-based classifier (explicitly forbidden by `SPEC-AUQ-NO-LLM-CLASSIFIER-001`).

## Prior Deliberations

- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED) — Sub-slice A landed the prose-decision-ask detection + Stop-mode block + durable-file mutation. This proposal is narrow follow-up bug fixes within Sub-slice A's surface; does not change the policy.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED) — established the Stop-mode block emission contract (`{"decision": "block", ...}` when prose detected and no AUQ this turn).
- `SPEC-AUQ-POLICY-ENGINE-001` — central deterministic policy engine returning canonical outcomes; this proposal preserves the engine contract.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic-only; no LLM classifiers. This proposal adds heuristic same-turn matching that is purely string-based (question_hash equality + temporal proximity), not LLM-classification.
- `feedback_avoid_quoting_decision_tracker_fragments.md` — when discussing tracker false-positive findings, avoid reproducing trigger phrases verbatim. This proposal references defects abstractly per that guidance.
- Empirical evidence: `memory/pending-owner-decisions.md` `DECISION-0494` entry (since manually resolved) — captured `question` field showed the over-match symptom.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — 2 new DCL inserts gate through scoped-auto-approval batch `decision-tracker-bug-fix-batch-2026-05-09`.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.

**Specs preserved unchanged (this proposal does not modify):**

- `SPEC-AUQ-POLICY-ENGINE-001` — engine outcomes unchanged.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — fix is deterministic; no classifier added.

**New specs created by this slice:**

- `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` v1 (NEW; design_constraint) — machine-checkable: `question` field captured by `_extract_prose_decision_matches` MUST be the matched regex group itself, optionally extended to the nearest sentence boundary within a bounded window (≤120 chars). Decorative prefix/suffix bytes (markdown-structural artifacts outside the matched group) MUST NOT be captured. Approval-packet-gated.
- `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` v1 (NEW; design_constraint) — machine-checkable: when a turn contains BOTH a prose-pattern match AND a subsequent AskUserQuestion tool_use, the prose-detected entry MUST be auto-resolved to `## Resolved` (rather than left in `## Pending`). Resolution heuristic: temporal-proximity (same turn) + AUQ tool_use presence (no question-hash equality required). Approval-packet-gated.

## Owner Decisions / Input

- **AUQ "Combine — clear -0494 now AND file the bridge proposal" 2026-05-09 (S339)** — owner authorized both the immediate cosmetic clear (already landed; DECISION-0494 moved to `## Resolved` with rationale annotation) AND this bridge proposal for the underlying defects.
- **No additional owner decisions required for the implementation phase.** The 2 new DCLs flow through scoped-auto-approval batch.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`: applicability + clause preflights run after this NEW entry is added to `bridge/INDEX.md`. Expected to pass given the Spec Links section above.

## Implementation Plan

### IP-1 — Tighten snippet extraction (Defect 1)

In `.claude/hooks/owner-decision-tracker.py:760`:

**Current:** `snippet = full_text[max(0, m.start() - 20):m.end() + 20].strip()`

**Replace with:** extract the matched group itself (`m.group(0)`), then optionally extend forward to the nearest `[.?!]` sentence-terminator within a 60-char forward window if the match doesn't already end at one. Cap total length at 120 chars.

```python
def _extract_question_snippet(full_text: str, match: re.Match[str]) -> str:
    """Extract just the matched question, sentence-bounded.

    Per DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001:
    capture the matched group itself, optionally extending to the nearest
    sentence terminator within a small forward window. Decorative prefix/
    suffix bytes (markdown structural artifacts outside the match) are
    not captured.
    """
    matched = match.group(0)
    end = match.end()
    # Most patterns already end at '?'; if not, extend forward to next [.?!]
    # within a bounded window so we capture the full question.
    if not matched.rstrip().endswith(("?", "!", ".")):
        forward_window = full_text[end:end + 60]
        terminator_match = re.search(r"[.?!]", forward_window)
        if terminator_match:
            matched = matched + forward_window[:terminator_match.end()]
    matched = matched.strip()
    if len(matched) > 120:
        matched = matched[:117] + "..."
    return matched
```

Replace the inline `snippet = ...` call site to use this helper.

### IP-2 — Same-turn AUQ auto-resolution for prose entries (Defect 2)

In `.claude/hooks/owner-decision-tracker.py::_stop_handler` (line 765+):

After scanning the just-completed turn for both prose matches (line 747) and AskUserQuestion tool_use entries (existing logic), check whether BOTH are present. If yes:

- Each prose-detected entry generated this turn is appended to `## Resolved` instead of `## Pending`, with:
  - `status: resolved`
  - `resolved_at: <turn end timestamp>`
  - `resolved_via: "same_turn_auq_formalization"`
  - `notes: "Prose pattern detected; same turn contained AskUserQuestion tool_use; auto-resolved per DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001."`

Heuristic rationale: when Prime catches a prose decision-ask and is blocked by the Stop hook (per existing block contract), Prime's standard remediation is to call AUQ in the *next turn*. But many turns include both an early prose ask AND a later AUQ in the same turn (e.g., when Prime self-corrects mid-response). The same-turn-AUQ-presence signal is sufficient evidence that the prose entry has been formalized; no question-hash equality matching is required (which would be brittle and possibly classifier-shaped, violating `SPEC-AUQ-NO-LLM-CLASSIFIER-001`).

The Stop-mode block emission contract is preserved: blocks still fire when prose is detected AND zero AUQ tool_use occurred this turn (per existing condition 2 at line 782). The new auto-resolution applies only when AUQ tool_use IS present (i.e., the block did not fire).

### IP-3 — Tests

New tests in `tests/scripts/test_owner_decision_tracker.py`:

- `test_question_snippet_extracts_match_group_only` — synthetic `full_text` with decorative prefix + matched group + decorative suffix; assert captured `question` is the matched group only, no surrounding noise.
- `test_question_snippet_extends_to_sentence_boundary` — match doesn't end at `?`; forward window contains `?` within 60 chars; assert extension captures up to and including `?`.
- `test_question_snippet_capped_at_120_chars` — pathological long match; assert truncation at 120 chars with `"..."` suffix.
- `test_same_turn_prose_and_auq_resolves_prose_entry` — synthetic transcript with prose match early in turn + AUQ tool_use later in turn; assert prose entry appended to `## Resolved` (not `## Pending`).
- `test_prose_only_no_auq_still_blocks` — prose match + no AUQ in turn; assert block contract preserved (Stop-mode returns `{"decision": "block", ...}`); assert prose entry appended to `## Pending`.
- `test_auq_only_no_prose_unchanged` — AUQ tool_use only, no prose match; assert existing AUQ-tracking behavior unchanged.

Updates to existing tests (if any reference the ±20 char snippet bounds): adjust to assert the new sentence-bounded extraction.

### IP-4 — Dry-run on existing pending-owner-decisions.md entries

Audit `memory/pending-owner-decisions.md`:

- Identify any other `## Pending` prose-detected entries with over-matched question fields.
- Manually resolve those that are stale (already answered via subsequent AUQ later same session) per the DECISION-0494 manual-resolve pattern landed in this session.
- Out of scope: programmatic backfill (low value; manual sweep sufficient since the file is hook-managed and small).

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-DT-snippet-match-group-only | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | `_extract_question_snippet(text, match)` returns `match.group(0).strip()` (or sentence-extended) without surrounding decorative bytes. |
| T-DT-snippet-sentence-extension | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | Match without trailing `?`; forward window contains `?` within 60 chars; extraction extends to terminator. |
| T-DT-snippet-length-cap | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | Pathological match longer than 120 chars; result truncated to 120 chars with `"..."` suffix. |
| T-DT-same-turn-resolves-prose | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 | Synthetic Stop-mode invocation with transcript containing prose match + later AUQ tool_use; assert prose entry written to `## Resolved` with `resolved_via: "same_turn_auq_formalization"`. |
| T-DT-block-contract-preserved | Sub-slice A -014 contract preservation | Prose match + zero AUQ tool_use → Stop-mode returns `{"decision": "block", ...}`; prose entry written to `## Pending` (existing behavior). |
| T-DT-auq-only-unchanged | Sub-slice A baseline | AUQ tool_use only, no prose match → existing AUQ-tracking behavior unchanged. |

## Acceptance Criteria

- [ ] Codex confirms IP-1's snippet-extraction change captures match-group only, with sentence-boundary extension within bounded window.
- [ ] Codex confirms IP-2's same-turn AUQ auto-resolution heuristic does NOT re-introduce LLM-classifier-shaped logic per `SPEC-AUQ-NO-LLM-CLASSIFIER-001`.
- [ ] Codex confirms Stop-mode block contract preserved when prose detected without AUQ.
- [ ] Codex confirms 2-new-DCL approval batch is the right shape.
- [ ] Codex confirms IP-4 dry-run sweep is appropriate scope (manual-only; no programmatic backfill required).

## Risk / Rollback

**Risk:**

- IP-1's sentence-boundary extension could in rare cases cut a multi-sentence question short; mitigation: 120-char cap is generous; matches longer than that get truncated with ellipsis (no information loss vs current behavior).
- IP-2's heuristic could in rare cases auto-resolve a prose entry that was NOT actually formalized by the same-turn AUQ (e.g., the AUQ was about a different question). Mitigation: same-turn AUQ presence is empirical evidence Prime acknowledged the gate; even if the questions differ, the prose entry being auto-resolved is preferable to leaving it stale (the AUQ's recorded answer is the canonical record). Risk surface is bounded.

**Rollback:**

- Revert `.claude/hooks/owner-decision-tracker.py` changes.
- Revert test file changes.
- Spec rollback: append v2 to DCLs marking superseded.

## Files Expected To Change

- `.claude/hooks/owner-decision-tracker.py` — IP-1 snippet helper + call-site update; IP-2 same-turn auto-resolution branch in `_stop_handler`.
- `tests/scripts/test_owner_decision_tracker.py` — 6 new test cases per IP-3.
- `groundtruth.db` — 2 new DCL inserts.
- `.groundtruth/formal-artifact-approvals/2026-05-NN-{DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001,DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001}.json` (2 packets).
- `memory/pending-owner-decisions.md` — IP-4 dry-run sweep results (manual moves of stale prose entries to `## Resolved`).
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md` (this proposal).
- `bridge/INDEX.md` (NEW entry).

## Recommended Commit Type

`fix:` — repairs broken behavior without adding new capability surface. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks

1. Confirm IP-1's snippet-extraction change is correct: capture match-group-only with bounded sentence-boundary extension; cap at 120 chars.
2. Confirm IP-2's same-turn AUQ auto-resolution heuristic stays within `SPEC-AUQ-NO-LLM-CLASSIFIER-001` (deterministic; no classifier).
3. Confirm Stop-mode block contract is preserved (block fires when prose detected without AUQ).
4. Confirm 2-new-DCL approval batch shape is appropriate.
5. Confirm IP-4 manual-only dry-run sweep is acceptable scope.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
