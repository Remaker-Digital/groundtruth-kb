NEW

# Implementation Report — Owner-Decision Tracker: Pattern Bounds + Same-Turn AUQ Auto-Resolution

bridge_kind: implementation_report
Document: gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001
Version: 007 (post-implementation report)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Implements: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md` per GO at `-006`.

## Summary

Implementation of the owner-decision-tracker pattern-bounds + same-turn-AUQ auto-resolution slice per GO at `-006` REVISED-2. Hook code changes (snippet extraction tightening + correlation helpers + Stop-mode auto-resolution); DecisionEntry extended with `resolved_via` field; 8 new tests added (all passing alongside 31 existing tests for 39/39 pass); 2 new DCLs inserted into MemBase with formal-artifact-approval packets.

## Specification Links

(Carried forward from `-005` proposal + `-006` GO.)

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section satisfies linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Test Plan mapping below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 — 2 formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-{QUESTION-EXTRACTION-BOUNDS,SAME-TURN-AUQ-RESOLUTION}-001.json`.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

**Specs preserved unchanged:** `SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`. The new correlation rule is purely deterministic — no LLM classification.

**New specs created by this slice:**

- `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` v1 (NEW; design_constraint; status=specified). MemBase rowid created.
- `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` v1 (NEW; design_constraint; status=specified). MemBase rowid created.

## Owner Decisions / Input

- AUQ "Approve as drafted (Recommended)" 2026-05-09 — owner authorized DCL-1 (`QUESTION-EXTRACTION-BOUNDS`) per IP-IIa.
- AUQ "Approve as drafted (Recommended)" 2026-05-09 — owner authorized DCL-2 (`SAME-TURN-AUQ-RESOLUTION`) per IP-IIb.
- AUQ "File both REVISED-2 -005s now (Recommended)" 2026-05-09 (prior) — authorized REVISED-2 filing addressing 2 findings of `-004`.
- AUQ "Continue with decision-tracker next (Recommended)" 2026-05-09 (prior) — authorized this implementation cycle.

## Implementation Evidence

### IP-1: Snippet extraction tightening (`_extract_question_snippet`)

- **File:** `.claude/hooks/owner-decision-tracker.py`.
- **New helper:** `_extract_question_snippet(full_text, match)` — captures `match.group(0)`; extends forward to nearest `[.?!]` within 60-char window when match doesn't end at terminator; caps at 120 chars with `...` truncation.
- **Callsite update:** `_scan_prose_decisions` line ~885 changed from `snippet = full_text[max(0, m.start() - 20):m.end() + 20].strip()` to `snippet = _extract_question_snippet(full_text, m)`.
- **Authority:** `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` v1.

### IP-2: Same-turn AUQ auto-resolution

- **New helpers:** `_normalize_question_text`, `_tokenize_with_stoplist`, `_discriminating_jaccard`, `_substring_containment_min_length`, `_option_label_overlap`, `_correlate_prose_to_auq`.
- **Boilerplate stoplist constant** `_CORRELATION_STOPLIST` — 47 tokens including `want`, `me`, `to`, `or`, `wait`, `should`, `now`, `approve`, `defer`, etc. Conservative; biases toward false-negatives (better to keep prose pending than silently auto-resolve unrelated decisions).
- **`_stop_handler` modification:** during prose-scan loop, accumulate AUQ question/options pairs from Scan A; for each prose match, compute two-signal correlation against each AUQ; on first match, mark `resolved_via="same_turn_auq_formalization"` and append to `## Resolved`; otherwise append to `## Pending` (existing behavior preserved).
- **Counterexample resilience verified:** Codex F1 boilerplate-only counterexample (`Want me to commit now or wait?` vs `Want me to deploy now or wait?`) correctly stays pending — after stoplist removal, J_d = 0/2 = 0.0 → Signal A fails.
- **Authority:** `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` v1.

### IP-IIa + IP-IIb: DCL approval packets + MemBase inserts

Both DCLs inserted via `KnowledgeDB.insert_spec(...)` with `GTKB_FORMAL_APPROVAL_PACKET` env var pointing at the per-DCL approval packet:

| DCL | Packet path | sha256 (full_content) | MemBase result |
|---|---|---|---|
| `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` | `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.json` | `064da0e92d64a320e3697761e6f6b32d16cdae582e8b8dfb4699c03ec887c528` | v1 specified — KB-SPEC-EVENT confirmed |
| `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` | `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.json` | `aedb5466bcc458302db21568d3c3a7ec048db0bc8337ee80b788c98e49205860` | v1 specified — KB-SPEC-EVENT confirmed |

Both packets schema-validated against `.claude/hooks/formal-artifact-approval-gate.py`'s `REQUIRED_PACKET_FIELDS`, `VALID_ARTIFACT_TYPES`, and `VALID_APPROVAL_MODES` per IP-IIa/IP-IIb F2 fix. Each DCL has 4-5 list-of-dict assertions matching the existing DCL pattern (e.g., `DCL-CROSS-HARNESS-ENFORCEMENT-001`).

### IP-3: Tests (8 new)

All in `tests/hooks/test_owner_decision_tracker.py`, alongside existing 31 tests. Test count: 39 total, all passing.

| New test | Asserts |
|---|---|
| `test_question_snippet_extracts_match_group_only` | Snippet captures only the matched group, not surrounding 20-char window. |
| `test_question_snippet_extends_to_sentence_boundary` | Forward-extension to terminator within window; no extension when no terminator. |
| `test_question_snippet_capped_at_120_chars` | Cap with `...` truncation. |
| `test_correlated_two_signal_resolves_prose_entry_substring_path` | Correlated prose match auto-resolves; lands in `## Resolved` with `resolved_via: same_turn_auq_formalization`. |
| `test_uncorrelated_boilerplate_overlap_keeps_prose_pending` | Codex F1 counterexample (commit-vs-deploy) correctly stays pending. |
| `test_uncorrelated_pure_helpers_counterexample` | Direct-helper-call assertions for two-signal-required logic. |
| `test_correlation_positive_via_option_label_overlap` | Signal A + Signal B2 (option-label overlap) auto-resolves. |
| `test_decision_entry_resolved_via_round_trips` | `resolved_via` field renders in DecisionEntry markdown output. |

Two new fixtures: `turn_prose_auq_correlated_substring.jsonl`, `turn_prose_auq_uncorrelated_boilerplate.jsonl`.

### IP-5: DecisionEntry extension

- **`resolved_via: str = ""`** field added to dataclass.
- **`render()`:** appends `resolved_via: <value>` line when non-empty.
- **`_set_entry_field`:** added `"resolved_via": "resolved_via"` mapping for parse-side round-trip.

## Spec-Derived Test Plan & Results

| Test | Spec/Requirement | Method | Result |
|---|---|---|---|
| T-DT-snippet-match-group-only | `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.A1` | `test_question_snippet_extracts_match_group_only` | **PASS** |
| T-DT-snippet-sentence-extension | `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.A4` | `test_question_snippet_extends_to_sentence_boundary` | **PASS** |
| T-DT-snippet-length-cap | `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.A3` | `test_question_snippet_capped_at_120_chars` | **PASS** |
| T-DT-correlated-two-signal-substring | `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.A2` | `test_correlated_two_signal_resolves_prose_entry_substring_path` | **PASS** |
| T-DT-uncorrelated-boilerplate-counterexample | `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.A3` | `test_uncorrelated_boilerplate_overlap_keeps_prose_pending` | **PASS** |
| T-DT-uncorrelated-pure-helpers | `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.A4` | `test_uncorrelated_pure_helpers_counterexample` | **PASS** |
| T-DT-correlated-option-label | `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.A1` | `test_correlation_positive_via_option_label_overlap` | **PASS** |
| T-DT-resolved-via-round-trip | `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.A2` | `test_decision_entry_resolved_via_round_trips` | **PASS** |
| T-DT-block-contract-preserved | Sub-slice A -014 contract preservation | `test_f3_block_emission_does_not_corrupt_durable_file` (existing) | **PASS** |
| (carried-forward) | All other Sub-slice A invariants | 31 existing tests | **31 PASS** |

**Test command:** `python -m pytest tests/hooks/test_owner_decision_tracker.py`
**Test result:** `============================= 39 passed in 5.10s ==============================`

## Files Changed

| Path | Change | Authorization |
|---|---|---|
| `.claude/hooks/owner-decision-tracker.py` | UPDATE: add `_extract_question_snippet`, correlation helpers, stoplist, `resolved_via` field, modified `_stop_handler` | bridge GO -006 |
| `tests/hooks/test_owner_decision_tracker.py` | UPDATE: 8 new tests appended | spec-derived test plan |
| `tests/hooks/fixtures/owner_decision_tracker/turn_prose_auq_correlated_substring.jsonl` | CREATE: positive correlation fixture | IP-3 |
| `tests/hooks/fixtures/owner_decision_tracker/turn_prose_auq_uncorrelated_boilerplate.jsonl` | CREATE: Codex F1 counterexample fixture | IP-3 |
| `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001.json` | CREATE: DCL-1 packet | owner AUQ 2026-05-09 |
| `.groundtruth/formal-artifact-approvals/2026-05-09-DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001.json` | CREATE: DCL-2 packet | owner AUQ 2026-05-09 |
| MemBase: `DCL-OWNER-DECISION-TRACKER-QUESTION-EXTRACTION-BOUNDS-001` | INSERT v1 | DCL-1 packet |
| MemBase: `DCL-OWNER-DECISION-TRACKER-SAME-TURN-AUQ-RESOLUTION-001` | INSERT v1 | DCL-2 packet |
| `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-007.md` | CREATE: this post-impl report | bridge protocol |
| `bridge/INDEX.md` | UPDATE: NEW entry prepended | bridge protocol |

## Recommended Commit Type

`feat:` — net-new capability surface (snippet-extraction tightening; same-turn AUQ auto-resolution with two-signal-required correlation; new DCLs governing the contracts). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline.

## Loyal Opposition Asks (for VERIFIED review)

1. Confirm IP-1 snippet extraction matches the proposal verbatim (match-group-only + 60-char forward-extension + 120-char cap).
2. Confirm IP-2 two-signal-required correlation matches the proposal (Signal A discriminating-Jaccard ≥ 0.5 with ≥ 4-char shared token; Signal B at least one of substring/option-label/identity).
3. Confirm Codex F1 boilerplate counterexample (commit-vs-deploy) correctly stays pending under the new logic (test_uncorrelated_boilerplate_overlap_keeps_prose_pending).
4. Confirm IP-IIa/IP-IIb approval packets are schema-correct and DCL inserts succeeded with KB-SPEC-EVENT confirmation.
5. Confirm Stop-mode block contract is preserved unchanged (existing test_f3_* tests still pass).
6. Confirm `resolved_via` field round-trips correctly (DecisionEntry render + parse).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
