REVISED

# Implementation Proposal — Owner-Decision Tracker: Pattern Bounds + Same-Turn AUQ Auto-Resolution — REVISED-2

bridge_kind: prime_proposal
Document: gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001
Version: 005 (REVISED-2 post NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md` (REVISED-1; NO-GO at `-004`).

## Revision Notes (REVISED-2)

This revision addresses both findings F1 (P1) and F2 (P1) from `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-004.md`. All `-003` scope carries forward unchanged except where the items below are revised.

### F1 (P1) — Stricter correlation rule (Jaccard alone is insufficient)

**Codex evidence:** the Jaccard ≥0.5 rule from `-003` resolves unrelated decisions because boilerplate-heavy phrasings dominate the token overlap. Concrete counter-examples Codex provided:

- `Want me to commit now or wait?` vs `Want me to deploy now or wait?` → Jaccard 6/8 = 0.75; same shape, different decisions.
- `Should I approve the DCL or defer?` vs `Should I approve the deployment or defer?` → Jaccard 6/8 = 0.75; same shape, different decisions.

**Resolution:** Replace the Jaccard-alone rule with a **two-signal-required** rule. Auto-resolution requires BOTH:

1. **Token overlap on discriminating tokens.** Tokenize both texts (lower-case, whitespace + punctuation split). Subtract the boilerplate stoplist below. Compute the discriminating-token Jaccard `J_d = |A_d ∩ B_d| / |A_d ∪ B_d|`. Require `J_d ≥ 0.5` AND at least one **shared discriminating token** is a noun-or-verb (heuristically detected as a non-stoplist token of length ≥ 4 characters that's not pure-numeric).
2. **AND** at least one of:
    - (a) **Normalized substring containment with minimum substantive length:** lower-cased, whitespace-collapsed, punctuation-stripped — one is a substring of the other AND the shared substring length is ≥ 20 characters (the smaller text's length floor).
    - (b) **Option-label overlap:** at least one of the AUQ's option labels appears verbatim (lower-cased) in the prose snippet OR vice versa.
    - (c) **Post-normalization text identity:** the prose snippet text equals an AUQ question text after normalization (subsumes (a) trivially).

**Boilerplate stoplist:** `{"want", "me", "to", "or", "wait", "should", "i", "now", "approve", "the", "defer", "do", "you", "should", "we", "is", "this", "are", "go", "stop", "yes", "no", "any", "of", "in", "on", "at", "for", "with", "and", "but", "as", "be", "have", "has", "had", "did", "does", "can", "could", "will", "would", "shall", "must", "may", "might"}`. (Conservative; biases toward false-negatives. Better to leave a prose entry pending than to silently resolve an unrelated decision.)

If both signals fire → auto-resolve with `resolved_via: "same_turn_auq_formalization"`. If only one fires (or neither) → keep prose entry pending. Stop-mode block contract preserved unchanged.

This is purely deterministic string-based; per `SPEC-AUQ-NO-LLM-CLASSIFIER-001` compliance.

**Counter-example resilience:**

- `Want me to commit now or wait?` vs `Want me to deploy now or wait?`:
    - Tokens: `{want, me, to, commit, now, or, wait}` vs `{want, me, to, deploy, now, or, wait}`.
    - After stoplist removal: `{commit}` vs `{deploy}`. `J_d = 0/2 = 0.0`. **Below 0.5 → no auto-resolve.** Correct.
- `Should I approve the DCL or defer?` vs `Should I approve the deployment or defer?`:
    - After stoplist removal: `{approve, dcl}` vs `{approve, deployment}`. `J_d = 1/3 ≈ 0.33`. **Below 0.5 → no auto-resolve.** Correct.
- Genuine same-decision case: `Should I commit the slice 4 work?` (prose) vs `Should I commit the Slice 4 work now?` (AUQ):
    - After stoplist removal: `{commit, slice, work, 4}` vs `{commit, slice, work, 4}`. `J_d = 4/4 = 1.0`. ✓ Plus normalized substring containment: `"commit the slice 4 work"` is in both. ✓ Both signals fire → auto-resolve. Correct.

### F2 (P1) — Approval-packet recipe corrected to match formal-artifact-approval-gate.py schema

**Codex evidence:** IP-IIa/IP-IIb in `-003` cited `narrative-artifact-approval.toml` schema with `artifact_type="spec"`. The active `.claude/hooks/formal-artifact-approval-gate.py` requires:

- `VALID_ARTIFACT_TYPES = {"deliberation", "governance", "requirement", "protected_behavior", "architecture_decision", "design_constraint"}` — `"spec"` is NOT in the set. DCLs use `"design_constraint"`.
- `VALID_APPROVAL_MODES = {"approve", "acknowledge", "edit-and-approve", "auto"}` — `approval_mode` is required.
- `REQUIRED_PACKET_FIELDS = {"artifact_type", "artifact_id", "action", "source_ref", "full_content", "full_content_sha256", "approval_mode", "presented_to_user", "transcript_captured", "explicit_change_request", "changed_by", "change_reason"}`.
- For manual approval/acknowledgement, `approved_by` (when `approval_mode="approve"`) or `acknowledged_by` (when `approval_mode="acknowledge"`) is also required.

**Resolution:** Rewrite IP-IIa and IP-IIb with the correct packet schema. Each DCL packet has these exact fields:

```json
{
    "artifact_type": "design_constraint",
    "artifact_id": "DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001",
    "action": "create",
    "source_ref": "bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md",
    "full_content": "<TITLE>\n\n<DESCRIPTION>\n\n<assertions JSON>",
    "full_content_sha256": "<sha256 of full_content>",
    "approval_mode": "approve",
    "approved_by": "owner",
    "presented_to_user": true,
    "transcript_captured": true,
    "explicit_change_request": "<verbatim AUQ answer text>",
    "changed_by": "claude-prime-builder",
    "change_reason": "Slice IP-IIa: approve DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 v1 per bridge -005 REVISED-2."
}
```

Same shape for IP-IIb (`DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001`).

**Pre-insertion validation step (NEW per F2 of `-004`):** before running `db.insert_spec(...)`, dry-run-validate the packet against the gate's schema:

```python
import json
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("gate", ".claude/hooks/formal-artifact-approval-gate.py")
gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
packet = json.loads(Path(packet_path).read_text(encoding="utf-8"))
# Validate required fields:
missing = gate.REQUIRED_PACKET_FIELDS - set(packet.keys())
assert not missing, f"missing required fields: {missing}"
# Validate enum values:
assert packet["artifact_type"] in gate.VALID_ARTIFACT_TYPES
assert packet["approval_mode"] in gate.VALID_APPROVAL_MODES
if packet["approval_mode"] == "approve":
    assert packet.get("approved_by") == "owner"
elif packet["approval_mode"] == "acknowledge":
    assert packet.get("acknowledged_by") == "owner"
```

Run this validation BEFORE attempting the MemBase insert. Surface validation errors clearly so the implementation phase can correct packet shape without hitting the gate's hard-block path.

## Claim

(Carried forward from `-003`/`-001`, unchanged.) Fix two narrow defects in `.claude/hooks/owner-decision-tracker.py`: pattern over-match (defect 1) and missing same-turn AUQ auto-resolution for prose entries (defect 2). REVISED-2 tightens the correlation rule per F1 of `-004` and corrects the packet recipe per F2 of `-004`.

## Why Now

(Carried forward from `-003`, unchanged. Owner observation 2026-05-09 surfaced the LO startup payload pollution from a stale prose-detected entry; both defects identified; both addressable.)

## Prior Deliberations

- All records cited in `-003` and `-001` carry forward unchanged.
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-004.md` — Codex NO-GO on REVISED-1; F1 (P1) Jaccard rule too permissive, F2 (P1) packet recipe wrong schema. Both addressed in this REVISED-2.
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-002.md` — Codex NO-GO on `-001`; 5 findings F1-F5 all addressed in `-003`; reaffirmed unchanged here.
- `feedback_avoid_quoting_decision_tracker_fragments.md` — when discussing tracker false-positive findings, avoid reproducing trigger phrases verbatim.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan section below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — 2 new DCL inserts gate via per-DCL approval packet workflow per IP-IIa/IP-IIb (corrected per F2 of `-004`).

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decisions, requirements, specifications flow through this slice.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented framing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — supersession/retirement triggers.

**Specs preserved unchanged:** `SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`. Per F1 of `-004` fix, the new correlation rule is purely deterministic — no LLM classification.

**New specs created by this slice (descriptions tightened per F1 of `-004`):**

- `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` v1 (NEW; design_constraint) — same as `-001`/`-003`. Approval packet flow per IP-IIa.
- `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` v1 (NEW; design_constraint) — DESCRIPTION TIGHTENED PER F1 of `-004`: "When a turn contains BOTH a prose-pattern match AND an AskUserQuestion tool_use, the prose-detected entry MUST be auto-resolved ONLY when BOTH (a) discriminating-token Jaccard ≥ 0.5 (after boilerplate-stoplist removal; with at least one shared discriminating token of length ≥ 4 chars) AND (b) at least one of: normalized-substring containment ≥ 20 chars OR option-label overlap OR post-normalization text identity. Single-signal correlation is insufficient. Stop-mode block contract preserved." Approval packet flow per IP-IIb.

## Owner Decisions / Input

- AUQ "Combine — clear -0494 now AND file the bridge proposal" 2026-05-09 → manual clear of DECISION-0494 landed in commit `d5fde427`; this proposal addresses the underlying defects.
- AUQ "Address all 5 findings" 2026-05-09 → authorized REVISED-1 `-003` addressing 5 findings of `-002`.
- AUQ "File both REVISED-2 -005s now (Recommended)" 2026-05-09 → authorized this REVISED-2 addressing 2 findings of `-004`.
- 2 owner-AUQ acknowledgements required during implementation, one per DCL approval packet (IP-IIa, IP-IIb). Each AUQ presents the full DCL content (id, title, description, assertions); answer captured verbatim in packet's `explicit_change_request` field.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this REVISED-2 lands at `-005`. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. Clause preflight expected exit 0.

## Implementation Plan

### IP-1 — Tighten snippet extraction (Defect 1)

(Unchanged from `-001`/`-003`.)

### IP-2 — Same-turn AUQ auto-resolution for prose entries (REVISED per F1 of `-004`)

In `.claude/hooks/owner-decision-tracker.py::_stop_handler`, for each prose-detected match in the turn:

1. Extract the prose snippet via the IP-1 helper.
2. For each AUQ tool_use in the turn, extract the AUQ's `question` text from `tool_input["questions"][i]["question"]` AND the option labels from `tool_input["questions"][i]["options"][j]["label"]`.
3. Compute correlation per the two-signal-required rule (Specification Links section above):
    - **Signal A — discriminating-token Jaccard** with boilerplate stoplist; require `J_d ≥ 0.5` AND at least one shared discriminating token of length ≥ 4 chars (non-numeric).
    - **Signal B — at least one of:**
        - **B1 (substring):** normalized substring containment ≥ 20 chars.
        - **B2 (option-label overlap):** at least one AUQ option label appears in prose snippet (or vice versa).
        - **B3 (text identity):** post-normalization equality.
4. Auto-resolve ONLY if Signal A AND at least one of B1/B2/B3 fire. Append entry to `## Resolved` with `resolved_via: "same_turn_auq_formalization"`, `resolved_at: <turn end timestamp>`, `notes: "Prose pattern detected; same turn contained correlated AskUserQuestion (signals: A=<true>, B=<b_subsignal>); auto-resolved per DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001."`
5. Otherwise → append to `## Pending` (existing behavior).

The Stop-mode block contract preserved unchanged. The new auto-resolution applies only when AUQ tool_use IS present AND the two-signal correlation succeeds.

Helper functions to add:

- `_normalize_question_text(text: str) -> str` — lower-case, whitespace-collapse, strip punctuation.
- `_tokenize_with_stoplist(text: str, stoplist: frozenset[str]) -> set[str]` — token set after stoplist removal.
- `_discriminating_jaccard(prose_tokens: set[str], auq_tokens: set[str]) -> tuple[float, bool]` — returns `(J_d, has_min_length_token)`.
- `_substring_containment_min_length(a: str, b: str, min_chars: int = 20) -> bool`.
- `_option_label_overlap(prose: str, auq_options: list[str]) -> bool`.
- `_correlate_prose_to_auq(prose_snippet: str, auq_question: str, auq_options: list[str]) -> tuple[bool, str | None]` — orchestrator returning `(correlated, b_signal_name | None)`.

### IP-IIa (REVISED per F2 of `-004`) — Approval packet for `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001`

Before MemBase insert:

1. Present full DCL content (id, title, description, assertions) to owner via AUQ.
2. AUQ answer captured verbatim.
3. Write packet at `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.json` with the schema-correct fields:

```json
{
    "artifact_type": "design_constraint",
    "artifact_id": "DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001",
    "action": "create",
    "source_ref": "bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md",
    "full_content": "<TITLE>\n\n<DESCRIPTION>\n\n<JSON-encoded assertions>",
    "full_content_sha256": "<sha256 of full_content>",
    "approval_mode": "approve",
    "approved_by": "owner",
    "presented_to_user": true,
    "transcript_captured": true,
    "explicit_change_request": "<verbatim AUQ answer>",
    "changed_by": "claude-prime-builder",
    "change_reason": "Slice IP-IIa: approve DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 v1 per bridge -005 REVISED-2."
}
```

4. Pre-insertion validation: dry-run-validate packet against `.claude/hooks/formal-artifact-approval-gate.py` schema (REQUIRED_PACKET_FIELDS, VALID_ARTIFACT_TYPES, VALID_APPROVAL_MODES, approved_by/acknowledged_by check). See F2 of `-004` Resolution above.
5. Run `db.insert_spec(...)` with `GTKB_FORMAL_APPROVAL_PACKET=<packet path>` env var so the gate validates at insert time.

### IP-IIb (REVISED per F2 of `-004`) — Approval packet for `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001`

Same recipe as IP-IIa, separate packet at `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.json` with `artifact_id: "DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001"` and `change_reason` adjusted accordingly. Owner AUQ asks separately so answers are independent records.

### IP-3 — Tests (REVISED per F1 of `-004`)

All tests added to existing `tests/hooks/test_owner_decision_tracker.py` (per `-003` IP-3 / F4 of `-002` fix). Reuse fixtures under `tests/hooks/fixtures/owner_decision_tracker/`.

- `test_question_snippet_extracts_match_group_only` — IP-1 (carried forward from `-003`).
- `test_question_snippet_extends_to_sentence_boundary` — IP-1.
- `test_question_snippet_capped_at_120_chars` — IP-1.
- `test_correlated_two_signal_resolves_prose_entry_substring_path` — IP-2; correlation triggers via Signal A (discriminating Jaccard) + Signal B1 (substring); assert `## Resolved`.
- `test_correlated_two_signal_resolves_prose_entry_option_label_path` — IP-2; Signal A + Signal B2 (option-label overlap); assert `## Resolved`.
- `test_correlated_two_signal_resolves_prose_entry_identity_path` — IP-2; Signal A + Signal B3 (post-normalization identity); assert `## Resolved`.
- **NEW per F1 of `-004`:** `test_uncorrelated_boilerplate_overlap_keeps_prose_pending` — Codex's counter-example: `Want me to commit now or wait?` (prose) vs `Want me to deploy now or wait?` (AUQ); after stoplist removal, J_d = 0; assert prose entry stays in `## Pending`.
- **NEW per F1 of `-004`:** `test_uncorrelated_signal_a_only_keeps_prose_pending` — Signal A fires (J_d ≥ 0.5 with discriminating tokens) but no B signal fires; assert prose entry pending.
- **NEW per F1 of `-004`:** `test_uncorrelated_signal_b_only_keeps_prose_pending` — Signal B fires (e.g., normalized substring) but Signal A fails (J_d < 0.5); assert prose entry pending.
- `test_block_contract_preserved_no_auq_in_turn` — IP-2; prose match + zero AUQ → block; entry in `## Pending`.
- `test_auq_only_no_prose_unchanged` — baseline.
- `test_resolved_via_field_round_trip` — F3 of `-002` carried forward.

### IP-4 — Dry-run on existing pending-owner-decisions.md entries

(Unchanged from `-001`/`-003`.)

### IP-5 — DecisionEntry model extension for `resolved_via`

(Unchanged from `-003`. F3 of `-002` fix.)

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-DT-snippet-match-group-only | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | (Unchanged from `-003`.) |
| T-DT-snippet-sentence-extension | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | (Unchanged.) |
| T-DT-snippet-length-cap | DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001 | (Unchanged.) |
| T-DT-correlated-two-signal-substring | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 (F1 of `-004` tightened) | Synthetic: Signal A (J_d ≥ 0.5 with discriminating noun/verb) + Signal B1 (≥20-char substring); assert resolution. |
| T-DT-correlated-two-signal-option-label | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 | Signal A + Signal B2 (option-label overlap); assert resolution. |
| T-DT-correlated-two-signal-identity | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 | Signal A + Signal B3 (text identity); assert resolution. |
| T-DT-uncorrelated-boilerplate-counterexample | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 (F1 of `-004` fix) | Codex counter-example: prose=`Want me to commit now or wait?`, AUQ=`Want me to deploy now or wait?`; J_d after stoplist = 0; assert prose entry stays pending. |
| T-DT-uncorrelated-signal-a-only | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 | Signal A fires alone (no B signal); assert prose entry pending. |
| T-DT-uncorrelated-signal-b-only | DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001 | Signal B fires alone (Signal A fails); assert prose entry pending. |
| T-DT-block-contract-preserved | Sub-slice A -014 contract preservation | (Unchanged from `-003`.) |
| T-DT-auq-only-unchanged | Sub-slice A baseline | (Unchanged.) |
| T-DT-resolved-via-round-trip | F3 of `-002` fix; DecisionEntry model extension | (Unchanged from `-003`.) |
| T-DT-packet-schema-validation | F2 of `-004` fix | Pre-insertion dry-run-validate packet shape against formal-artifact-approval-gate.py REQUIRED_PACKET_FIELDS / VALID_ARTIFACT_TYPES / VALID_APPROVAL_MODES; assert no missing fields, valid enums, approved_by="owner" present. |

## Acceptance Criteria

- [ ] Codex confirms F1 of `-004` closed: two-signal-required correlation rule (Signal A discriminating-token Jaccard ≥0.5 + Signal B substring/option-label/identity); boilerplate counter-example correctly leaves prose entry pending.
- [ ] Codex confirms F2 of `-004` closed: packet recipe uses `artifact_type="design_constraint"`, `approval_mode="approve"`, `approved_by="owner"`; pre-insertion dry-run validation step added; cite `.claude/hooks/formal-artifact-approval-gate.py` as schema source.
- [ ] All `-003`/`-001` carry-forward acceptance criteria continue to hold (snippet extraction; Stop-mode block contract; DecisionEntry model extension; tests under tests/hooks/; preflight clean).

## Risk / Rollback

(Carried forward from `-003`.)

- **F1 of `-004` risk:** the two-signal-required rule is conservative; in rare cases a paraphrased question might fail correlation (e.g., prose "Should I commit?" vs AUQ "Ready to land changes?"). Mitigation: false-negative case keeps prose entry pending — the AUQ answer is still recorded separately; the duplicate prose pending eventually gets manual resolution but doesn't lose information. The owner-decision tracker is fail-closed state preservation; this rule biases toward safe defaults per Codex's recommendation.
- **F2 of `-004` risk:** dry-run validation could mask real gate-side schema changes (if the gate adds new required fields, the dry-run uses an old schema snapshot). Mitigation: dry-run helper imports the gate's schema constants directly via `importlib.util.spec_from_file_location`, so schema changes flow through automatically.
- All other risk/rollback from `-003` carry forward unchanged.

## Files Expected To Change

- `.claude/hooks/owner-decision-tracker.py` — IP-1 + IP-2 + IP-5 changes (snippet helper, two-signal correlation helpers, DecisionEntry extension).
- `tests/hooks/test_owner_decision_tracker.py` — 12 test cases per IP-3.
- `tests/hooks/fixtures/owner_decision_tracker/` — new fixtures only if needed for correlation scenarios.
- `groundtruth.db` — 2 new DCL inserts (after IP-IIa + IP-IIb owner AUQs).
- `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.json` (IP-IIa; schema-correct).
- `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.json` (IP-IIb; schema-correct).
- `memory/pending-owner-decisions.md` — IP-4 dry-run sweep results (manual moves of stale prose entries to `## Resolved`).
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md` (this REVISED-2).
- `bridge/INDEX.md` (REVISED entry prepended).

## Open Follow-Ons

(None. This is a contained bug-fix slice.)

## Recommended Commit Type

`fix:` — unchanged. Repairs broken behavior without adding new capability surface.

## Loyal Opposition Asks

1. Confirm F1 of `-004` closed: two-signal-required correlation; boilerplate counter-example test verifies the false-positive class is closed.
2. Confirm F2 of `-004` closed: packet recipe matches `formal-artifact-approval-gate.py` schema; pre-insertion dry-run validation step is sufficient.
3. Confirm `-003` carry-forward asks (IP-1, Stop-mode block contract, DecisionEntry extension, tests/hooks/ layout, preflight clean) continue to hold.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
