REVISED

# Implementation Proposal — Owner-Decision Tracker: Pattern Bounds + Same-Turn AUQ Auto-Resolution — REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md` (NEW; NO-GO at `-002`).

## Revision Notes (REVISED-1)

This revision addresses all 5 Loyal Opposition findings from `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-002.md`. All `-001` scope carries forward unchanged except where the items below are revised.

### F1 (P1) — Deterministic correlation rule for same-turn auto-resolution

**Codex evidence:** `-001` IP-2 said "same-turn-AUQ-presence signal is sufficient evidence" with "no question-hash equality required". Codex flagged that a turn with two unrelated owner decisions (prose about A + AUQ about B) would silently lose A.

**Resolution:** Replace the loose "any AUQ in the same turn" rule with a **deterministic correlation rule**. A prose-detected entry is auto-resolved ONLY when it can be deterministically correlated to a same-turn AUQ. Acceptable correlation signals (any one is sufficient):

1. **Normalized-substring overlap**: after lower-casing both texts and collapsing whitespace, the prose snippet appears as a substring of an AUQ question text, OR vice versa.
2. **Jaccard similarity over word tokens** (≥ 0.5 on the word-set Jaccard index): the prose snippet and an AUQ question share most of their meaningful tokens. Threshold rationale: 0.5 is the "majority overlap" threshold; lower would risk false positives, higher would miss legitimate paraphrase.
3. **Question-text identity** after normalization (the strictest signal; satisfies criteria 1 and 2 trivially).

If correlation is absent → prose entry stays in `## Pending`. The Stop-mode block contract is preserved exactly as `-001` (block fires when prose detected AND zero AUQ tool_use this turn).

This is purely string-based, deterministic, no LLM. Per `SPEC-AUQ-NO-LLM-CLASSIFIER-001` compliance.

### F2 (P1) — Approval-packet-and-acknowledgement plan as implementation work

**Codex evidence:** `-001` asserted DCLs are approval-packet-gated and flow through batch `decision-tracker-bug-fix-batch-2026-05-09`, but no packets exist; the formal-artifact-approval-gate hook requires `auto_approval_scope` and `auto_approval_activated_by='owner'`.

**Resolution:** Owner chose option (a) per AUQ "Address all 5 findings" 2026-05-09 — include the exact approval-packet/acknowledgement sequence as implementation work. Two new IP steps:

- **IP-IIa (NEW):** Before inserting `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` v1, present the full DCL content to the owner via AUQ and write the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-NN-DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.json` with `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request=<verbatim AUQ answer>`, `changed_by="claude-prime-builder"`, `change_reason="Slice IP-IIa: per bridge -003 REVISED-1 ..."`.
- **IP-IIb (NEW):** Same pattern for `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` v1.

The 2 packets are filed individually (not via auto-approval batch) to keep audit trail explicit. Each AUQ presents the full proposed DCL content (id, title, description, assertions); owner answer is captured verbatim in the packet's `explicit_change_request` field.

### F3 (P2) — `DecisionEntry` model extended for `resolved_via`

**Codex evidence:** IP-2 + tests assert `resolved_via: "same_turn_auq_formalization"` is written to durable file, but `DecisionEntry` dataclass, `render()` method, and `_set_entry_field()` parser don't support the field. Round-trip would fail.

**Resolution:** Extend the model. Three changes in `.claude/hooks/owner-decision-tracker.py`:

- Add `resolved_via: str | None = None` to `DecisionEntry` dataclass (line 305-324 area).
- Update `render()` to emit `resolved_via: <value>` after `resolved_at` when set (line 347-353 area).
- Add parse mapping in `_set_entry_field()` for `"resolved_via"` (line 524-537 area).

Plus a round-trip test: write a synthetic entry with `resolved_via="same_turn_auq_formalization"`, render it, parse it back, assert field preservation.

### F4 (P3) — Test layout aligned with existing hook test convention

**Codex evidence:** Existing tests live at `tests/hooks/test_owner_decision_tracker.py` with fixtures under `tests/hooks/fixtures/owner_decision_tracker/`. `-001` proposed `tests/scripts/test_owner_decision_tracker.py` (different location).

**Resolution:** All new tests added to existing `tests/hooks/test_owner_decision_tracker.py`. Reuse existing fixture infrastructure under `tests/hooks/fixtures/owner_decision_tracker/`; add new fixtures only if needed for the snippet-extraction or correlation-rule scenarios.

### F5 (P3) — Advisory spec added

**Resolution:** Added `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to the Cross-cutting (advisory) Specification Links. Re-run preflight after this REVISED-1 lands at `-003`; expected `missing_advisory_specs: []`.

## Claim

(Carried forward from `-001`, unchanged.) Fix two narrow defects in `.claude/hooks/owner-decision-tracker.py`: pattern over-match (defect 1) and missing same-turn AUQ auto-resolution for prose entries (defect 2). REVISED-1 tightens the correlation rule per F1, adds explicit packet-and-acknowledgement plan per F2, extends the model per F3, aligns test layout per F4, fixes preflight advisory miss per F5.

## Why Now

(Carried forward from `-001`, unchanged.)

## Prior Deliberations

(Carried forward from `-001` plus this round's NO-GO.)

- All records cited in `-001` carry forward.
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-002.md` — Codex NO-GO; 5 findings F1-F5, all addressed in this revision.

## Specification Links

**Cross-cutting (blocking):** (unchanged from `-001`)

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** (F5 fix — DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 added)

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Specs preserved unchanged:** `SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`. Per F1 fix, the new correlation rule is purely deterministic string-based — no LLM classification.

**New specs created by this slice (descriptions tightened per F1):**

- `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` v1 (NEW; design_constraint) — same as `-001`. Approval packet flow per IP-IIa.
- `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` v1 (NEW; design_constraint) — DESCRIPTION TIGHTENED PER F1: "When a turn contains BOTH a prose-pattern match AND an AskUserQuestion tool_use, the prose-detected entry MUST be auto-resolved ONLY when the prose snippet can be deterministically correlated to a same-turn AUQ question via (a) normalized-substring containment, OR (b) Jaccard token-set similarity ≥ 0.5, OR (c) post-normalization text identity. Bare same-turn AUQ presence without correlation MUST NOT auto-resolve the prose entry; the entry stays in `## Pending`. Stop-mode block contract preserved unchanged from current behavior." Approval packet flow per IP-IIb.

## Owner Decisions / Input

(Updated per F2 fix.)

- AUQ "Combine — clear -0494 now AND file the bridge proposal" 2026-05-09 → manual clear of DECISION-0494 landed in commit d5fde427; this proposal addresses the underlying defects.
- AUQ "Address all 5 findings" 2026-05-09 (S339) — owner authorized REVISED-1 with all 5 NO-GO findings addressed (this thread).
- **NEW per F2:** 2 owner-AUQ acknowledgements required during implementation, one per DCL approval packet (IP-IIa, IP-IIb). Each AUQ presents the full DCL content; answer is captured verbatim in the packet's `explicit_change_request` field. NOT covered by a scoped-auto-approval batch this round.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED-1 lands at `-003`. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` (F5 fix). Clause preflight expected exit 0.

## Implementation Plan

### IP-1 — Tighten snippet extraction (Defect 1)

(Unchanged from `-001`.)

### IP-2 — Same-turn AUQ auto-resolution for prose entries (Defect 2; REVISED per F1)

In `.claude/hooks/owner-decision-tracker.py::_stop_handler`:

After scanning the just-completed turn for both prose matches and AskUserQuestion tool_use entries, for each prose match:

1. Extract the prose snippet via the IP-1 helper.
2. For each AUQ tool_use in the turn, extract the AUQ's `question` text from `tool_input["questions"][i]["question"]`.
3. Compute deterministic correlation between the prose snippet and each AUQ question:
    - **(a) Normalized-substring containment:** lower-case both, collapse whitespace, strip punctuation; check if either is a substring of the other. Match → correlated.
    - **(b) Jaccard token-set similarity:** lower-case both, tokenize on whitespace + punctuation, compute `|A ∩ B| / |A ∪ B|`. ≥ 0.5 → correlated.
    - **(c) Post-normalization text identity:** trivially satisfies (a) and (b); kept here for explicitness.
4. If ANY AUQ question correlates with the prose snippet → append the prose entry to `## Resolved` with `resolved_via: "same_turn_auq_formalization"`, `resolved_at: <turn end timestamp>`, `notes: "Prose pattern detected; same turn contained correlated AskUserQuestion tool_use; auto-resolved per DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 (correlation: <signal>)."` where `<signal>` is `"normalized_substring"` / `"jaccard_overlap"` / `"text_identity"`.
5. If NO AUQ question correlates → append the prose entry to `## Pending` (existing behavior).

The Stop-mode block contract (per existing condition 2 at line 782): block fires when prose detected AND zero AUQ tool_use this turn. Preserved unchanged. The new auto-resolution applies only when AUQ tool_use IS present AND correlated.

Helper functions to add:

- `_normalize_question_text(text: str) -> str` — lower-case, collapse whitespace, strip punctuation. Reusable.
- `_jaccard_token_similarity(a: str, b: str) -> float` — token-set Jaccard.
- `_correlate_prose_to_auq(prose_snippet: str, auq_questions: list[str]) -> tuple[bool, str | None]` — returns `(correlated, signal_name)`.

### IP-IIa (NEW per F2) — Approval-packet plan for `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001`

Before MemBase insert:

1. Present full DCL content (id, title, description, assertions) to owner via AUQ.
2. AUQ answer captured verbatim.
3. Write packet at `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.json` with all required fields per `narrative-artifact-approval.toml` schema (artifact_type="spec", artifact_id, action="create", target_path="groundtruth.db (specifications table)", source_ref="bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md", full_content, full_content_sha256, presented_to_user=true, transcript_captured=true, explicit_change_request=<verbatim AUQ answer>, changed_by="claude-prime-builder", change_reason).
4. Run `db.insert_spec(...)` with `GTKB_FORMAL_APPROVAL_PACKET=<packet path>` env var so the formal-artifact-approval-gate hook validates.

### IP-IIb (NEW per F2) — Approval-packet plan for `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001`

Same pattern as IP-IIa, separate packet at `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.json`. Owner AUQ asks separately so the answers are independent records.

### IP-3 — Tests (REVISED per F1 + F4)

All new tests added to `tests/hooks/test_owner_decision_tracker.py` (per F4). Reuse fixture infrastructure under `tests/hooks/fixtures/owner_decision_tracker/`.

- `test_question_snippet_extracts_match_group_only` — IP-1 (unchanged from `-001`).
- `test_question_snippet_extends_to_sentence_boundary` — IP-1.
- `test_question_snippet_capped_at_120_chars` — IP-1.
- `test_correlated_auq_resolves_prose_entry_normalized_substring` — IP-2 + F1 fix; prose snippet appears as substring of AUQ question; assert `## Resolved` with `resolved_via: "same_turn_auq_formalization"`, signal `"normalized_substring"`.
- `test_correlated_auq_resolves_prose_entry_jaccard_overlap` — IP-2 + F1; prose and AUQ share ≥50% tokens but neither contains the other; assert resolution with signal `"jaccard_overlap"`.
- `test_uncorrelated_auq_keeps_prose_pending` — IP-2 + F1; turn has prose match (about decision A) + AUQ (about decision B); correlation fails; assert prose entry in `## Pending` (NOT auto-resolved).
- `test_block_contract_preserved_no_auq_in_turn` — IP-2; prose match + zero AUQ → Stop-mode returns `{"decision": "block", ...}`; entry in `## Pending`.
- `test_auq_only_no_prose_unchanged` — baseline; AUQ tool_use only, no prose match; existing AUQ-tracking behavior.
- `test_resolved_via_field_round_trip` — F3 fix; write entry with `resolved_via="same_turn_auq_formalization"`, render to file, parse back, assert field value preserved.

### IP-4 — Dry-run on existing pending-owner-decisions.md entries

(Unchanged from `-001`.)

### IP-5 — DecisionEntry model extension for `resolved_via` (NEW per F3)

Three edits in `.claude/hooks/owner-decision-tracker.py`:

- `DecisionEntry` dataclass (line 305-324): add `resolved_via: str | None = None` after `resolved_at`.
- `render()` method (line 347-353): emit `resolved_via: <value>` after `resolved_at` when `self.resolved_via is not None`.
- `_set_entry_field()` parser (line 524-537): add parse mapping `"resolved_via": lambda entry, value: setattr(entry, "resolved_via", value)`.

Round-trip test per IP-3 (`test_resolved_via_field_round_trip`).

## Spec-Derived Test Plan

(Updated per F1 + F3 + F4.)

| Test | Spec/Requirement | Method |
|---|---|---|
| T-DT-snippet-match-group-only | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | (Unchanged from `-001`.) |
| T-DT-snippet-sentence-extension | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | (Unchanged.) |
| T-DT-snippet-length-cap | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | (Unchanged.) |
| T-DT-correlated-substring-resolves | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 (F1 tightened) | Synthetic: prose snippet appears as substring of AUQ question; assert resolution with `resolved_via: "same_turn_auq_formalization"`, correlation signal `"normalized_substring"`. |
| T-DT-correlated-jaccard-resolves | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 (F1 tightened) | Synthetic: prose and AUQ share ≥50% tokens, neither is substring of other; assert resolution with signal `"jaccard_overlap"`. |
| T-DT-uncorrelated-keeps-pending | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 (F1 tightened) | Synthetic: prose about decision A + AUQ about decision B; assert prose entry in `## Pending`. |
| T-DT-block-contract-preserved | Sub-slice A -014 contract preservation | (Unchanged.) |
| T-DT-auq-only-unchanged | Sub-slice A baseline | (Unchanged.) |
| T-DT-resolved-via-round-trip | F3 fix; DecisionEntry model extension | Write entry with `resolved_via="same_turn_auq_formalization"`; render; parse; assert field preserved. |

## Acceptance Criteria

- [ ] Codex confirms F1 closed: deterministic correlation rule (normalized-substring OR Jaccard ≥0.5 OR text identity); no LLM; uncorrelated case keeps prose entry pending.
- [ ] Codex confirms F2 closed: explicit packet-and-acknowledgement plan in IP-IIa + IP-IIb; no asserted-but-absent batch state.
- [ ] Codex confirms F3 closed: `resolved_via` field added to `DecisionEntry`, `render()`, `_set_entry_field()`; round-trip test passes.
- [ ] Codex confirms F4 closed: tests in `tests/hooks/test_owner_decision_tracker.py`; fixture reuse where applicable.
- [ ] Codex confirms F5 closed: preflight reports `missing_advisory_specs: []`.
- [ ] Codex confirms IP-1's snippet-extraction is unchanged from `-001` and remains correct.
- [ ] Codex confirms Stop-mode block contract preserved.

## Risk / Rollback

(Carried forward from `-001` plus F1 mitigation.)

- **F1 risk:** correlation rule could in rare cases miss a paraphrased question (e.g., prose "Should I commit?" vs AUQ "Ready to land changes?"). Mitigation: Jaccard ≥0.5 captures most semantic overlap; the false-negative case leaves the prose entry pending, which is the safe default (the AUQ entry separately records the answer; the duplicate prose pending will eventually need manual resolution but doesn't lose information).
- **Rollback:** revert `.claude/hooks/owner-decision-tracker.py` changes; revert tests; spec rollback per `-001`.

## Files Expected To Change

- `.claude/hooks/owner-decision-tracker.py` — IP-1 + IP-2 + IP-5 changes (snippet helper, correlation helpers, DecisionEntry extension).
- `tests/hooks/test_owner_decision_tracker.py` — 9 new test cases per IP-3 (F4 fix moves them here).
- `tests/hooks/fixtures/owner_decision_tracker/` — new fixtures only if needed for correlation scenarios.
- `groundtruth.db` — 2 new DCL inserts (after IP-IIa + IP-IIb owner AUQs).
- `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.json` (IP-IIa).
- `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.json` (IP-IIb).
- `memory/pending-owner-decisions.md` — IP-4 dry-run sweep results (manual moves of stale prose entries to `## Resolved`).
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md` (this REVISED-1).
- `bridge/INDEX.md` (REVISED entry prepended).

## Recommended Commit Type

`fix:` — unchanged from `-001`. Repairs broken behavior without adding new capability surface.

## Loyal Opposition Asks

1. Confirm F1 closed: deterministic correlation rule (normalized-substring OR Jaccard ≥0.5 OR text identity); no LLM classification.
2. Confirm F2 closed: explicit IP-IIa + IP-IIb owner-AUQ acknowledgement steps before DCL inserts; per-DCL packet (not auto-approval batch).
3. Confirm F3 closed: `DecisionEntry` extended with `resolved_via`; render + parse + round-trip test land together.
4. Confirm F4 closed: tests under `tests/hooks/test_owner_decision_tracker.py`.
5. Confirm F5 closed: preflight clean.
6. Confirm IP-1 + Stop-mode block contract continue to hold.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
