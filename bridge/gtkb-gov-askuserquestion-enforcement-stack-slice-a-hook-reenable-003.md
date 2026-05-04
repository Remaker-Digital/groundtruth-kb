REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening (REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice A of GTKB-GOV-AUQ-ENFORCEMENT-STACK (umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`, Codex GO at -004)
**Mechanism:** 2 (per umbrella sub-slice plan: Hook upgrade — logging → blocking)
**Risk tier:** Medium

**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-002.md` — F1 (proposed guard-scope semantics conflicted with the actual hook implementation: current `_collect_prose_matches()` at `.claude/hooks/owner-decision-tracker.py:642-643` applies guards to `full_text` and skips ALL detection for the event if any guard matches; the `-001` proposal described guards as "paragraph-scoped" without specifying the required code change), F2 (row 29 mentions both `prose:awaiting_input` and `prose:offering_or_choice` as too liberal; `-001` only addressed the awaiting/standing_by patterns and lacked fixture coverage proving `offering_or_choice` behavior is acceptable).

---

## Codex Findings Addressed

### Cycle 1 (NO-GO at -002, addressed in -003)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — Proposed guard semantics conflicted with hook implementation. Current code: `if any(g.search(full_text) for g in PROSE_FALSE_POSITIVE_GUARDS): continue` (line 642-643) — guards apply to FULL assistant event and skip ALL detection if any guard matches. Adding broad guard terms (`Codex GO`, `regex tightening`, etc.) at full-event scope would create systematic false negatives: a long assistant message mentioning bridge state ANYWHERE could suppress unrelated genuine prose decision-asks elsewhere in the same event. | "Revise the proposal to either: (1) change `_collect_prose_matches()` so guards are applied only to the matched snippet's paragraph or bounded local window, then add regression tests proving unrelated asks in the same assistant event still match; or (2) explicitly accept full-event guard semantics and narrow the new guard patterns enough to make that safe." | This revision adopts **path 1**: `_collect_prose_matches()` is modified to apply guards per-match against a bounded local window (default ±200 chars around the match), not against `full_text`. The hook switches from `pattern.search()` (first match only) to `pattern.finditer()` (all matches), and applies guards per-match. New tests added covering same-event mixed guard + genuine-ask cases (T-mixed-event-1 and T-mixed-event-2). |
| **F2** — Row 29 cites both `prose:awaiting_input` AND `prose:offering_or_choice` as too liberal. `-001` only addressed `awaiting_input`/`standing_by_for` and lacked fixture coverage proving `offering_or_choice` is acceptable. Closing all of row 29 on Sub-slice A VERIFIED would be misleading. | "Revise to: include `offering_or_choice` tightening + fixture coverage; OR split into a named follow-up; OR cite evidence that the cited `offering_or_choice` text was superseded/misclassified plus targeted test proving current pattern is acceptable." | This revision adopts **path 3**: `offering_or_choice` and `your_decision_q` (the two patterns that were already conservative — both already require `?`) are added to BOTH the negative and positive fixture corpora. Targeted tests verify their behavior is acceptable. The revision documents in §"Empirical disposition of `offering_or_choice` and `your_decision_q`" below that no documented false-positive shape exists for these patterns; the row 29 grouping was likely intuitive (all 5 prose patterns share the file) rather than evidence-based for these 2. Sub-slice A closes all of row 29 with this evidence. |

---

## Background

(Carry forward from `-001` background — current state of `.claude/hooks/owner-decision-tracker.py`, current env override, S331 prose accumulation.)

The umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (Codex GO at -004) decomposes the AUQ enforcement program into 6 sub-slices A through F. Sub-slice A is the highest-leverage starting point because it absorbs work_list row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`, owner-directed S328) and re-enables already-implemented block emission infrastructure that has been disabled via env override since S328.

Current state of `.claude/hooks/owner-decision-tracker.py`:

- **Detection:** `PROSE_DECISION_PATTERNS` (5 patterns) + `PROSE_FALSE_POSITIVE_GUARDS` (3 T14-class guards) currently active for Stop-mode prose-decision-ask detection.
- **Guard application:** `_collect_prose_matches()` at line 642-643 applies guards to `full_text` (full assistant event) and skips ALL detection if any guard matches. Per Codex `-002` F1, this is broader than the proposal's "paragraph-scoped" intent and requires explicit code change.
- **Block emission:** Bounded-exception block JSON emission implemented per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED). Suppressed via `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` in `.claude/settings.local.json::env`.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-003.md`; INDEX update at top of `bridge/INDEX.md` is the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this section enumerates all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section maps every spec clause to a concrete test command and expected result.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Canonical placement contract. Applicability: this sub-slice modifies `.claude/hooks/owner-decision-tracker.py`, `.claude/settings.local.json`, and (test-only) files; it does NOT create files under `applications/`. T-out-of-applications-A asserts no files under `applications/` are introduced.

Topic-specific governance for this work:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1 at GO -004) — defines this sub-slice's scope and dependencies.
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — Source rule for owner-decision surfacing infrastructure.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED 2026-04-27) — Original owner-decision surfacing implementation.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED) — Bounded-exception block emission infrastructure.
- `memory/work_list.md` row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) — Owner-directed S328; this sub-slice absorbs and closes the row on VERIFIED with full coverage of all 5 prose patterns.
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; this proposal complies with Mandatory Specification Linkage Gate + Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; this proposal is the artifact submitted for review.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation; satisfied via Prior Deliberations section.
- `.claude/rules/project-root-boundary.md` — Project root boundary rule; this sub-slice operates entirely within `E:/GT-KB/`.
- `.claude/hooks/owner-decision-tracker.py` — Target of modification: `PROSE_DECISION_PATTERNS` tuple, `PROSE_FALSE_POSITIVE_GUARDS` tuple, AND `_collect_prose_matches()` function (per Codex `-002` F1).
- `.claude/settings.local.json` — Target of modification: remove `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` env override.
- `memory/pending-owner-decisions.md` — Durable evidence file; existing entries preserved.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts, tests, reports, decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states.

The proposed tests in the Test Plan section derive from these linked specs as follows: regex tightening contract → T-regex-negative-fixtures + T-regex-positive-fixtures (factual status statements still skip; genuine asks still match across all 5 patterns); guard-scope correction → T-mixed-event-1 + T-mixed-event-2 (guards suppress ONLY the matched snippet's local window; unrelated asks in the same event still match); T14 guard extensions → T-guard-self-reference + T-guard-bridge-metadata; env-override removal → T-env-override-absent; block-emission round-trip → T-block-emission-end-to-end; platform smoke → T-platform-smoke; row 29 full closure → T-row29-closure (all 5 patterns covered).

## Prior Deliberations

(Carry forward from `-001` Prior Deliberations table.)

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive (per `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED) | owner_conversation | owner_decision | Source rule for owner-decision surfacing |
| Implicit S321 owner directive (per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED) | owner_conversation | owner_decision | Bounded exception for block emission |
| S328 regex-tightening directive (work_list row 29) | owner_conversation | owner_decision | Tighten regex; add T14-class guards |
| S331 AUQ #1: "Block ISOLATION-018; enforcement first" | owner_conversation | owner_decision | Enforcement priority |
| S331 AUQ #2: "Full 6-mechanism stack" | owner_conversation | owner_decision | Umbrella scope |
| S331 AUQ #3: "Autonomous progression" | owner_conversation | owner_decision | Sub-slice filing autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice A approved to file under standard lifecycle |
| Codex Sub-slice A -002 NO-GO | bridge_thread | no_go | F1 (guard-scope conflict) + F2 (row 29 partial coverage) addressed in this revision |

## Goal

Sub-slice A delivers four coupled outcomes within a single coherent scope (revised from 3 in `-001` per Codex `-002` F1):

1. **Tighten `PROSE_DECISION_PATTERNS`** to reduce false positives on factual status statements (split `awaiting_input` and `standing_by_for` into `_q` and `_first_person` variants per `-001`).
2. **Modify `_collect_prose_matches()`** to apply guards per-match against a bounded local window (±200 chars), not against `full_text`. Switch from `pattern.search()` to `pattern.finditer()` for full-event coverage. **(NEW per Codex `-002` F1.)**
3. **Extend `PROSE_FALSE_POSITIVE_GUARDS`** with self-reference and bridge-metadata suppressors (per `-001`).
4. **Re-enable block emission** by removing env override (per `-001`).

work_list row 29 is closed on Sub-slice A VERIFIED with **full coverage of all 5 prose patterns** (per Codex `-002` F2).

## Empirical Disposition of `offering_or_choice` and `your_decision_q` (per Codex `-002` F2)

The S328 work_list row 29 directive groups all 5 prose patterns as "too liberal", but provides only 1 explicit example (the "Awaiting Codex re-review" / "Awaiting your direction" contrast for `awaiting_input`). Patterns 1, 2, and 5 (`offering_or_choice`, `should_i_or`, `your_decision_q`) already require an interrogative marker (`?`):

```python
("offering_or_choice", re.compile(r"\bwant me to\b[^.?!]*\bor\b[^.?!]*\?", re.IGNORECASE)),
("should_i_or", re.compile(r"\bshould I\b[^.?!]*\bor\b[^.?!]*\?", re.IGNORECASE)),
("your_decision_q", re.compile(r"\b(?:your|owner)\s+(?:decision|choice|input)\b[^.?!]{0,80}\?", re.IGNORECASE)),
```

These are inherently more conservative because:
- `offering_or_choice` requires the literal lead-in "want me to", binary "or" connector, AND interrogative `?`
- `should_i_or` requires "should I", "or", AND `?`
- `your_decision_q` requires "your"/"owner" + decision-class word + `?` within 80 chars

No documented false-positive shape exists for these 3 patterns. The S331 prose-decision-ask false positives accumulated this session were all `awaiting_input` matches.

This revision treats the row-29 grouping as intuitive (all 5 prose patterns share the same hook file and were authored together) rather than evidence-based for the 3 already-conservative patterns. To verify this empirical disposition, the test corpus includes coverage for ALL 5 patterns:

- Negative fixtures for `offering_or_choice`: factual status statements containing "want me to" or "or" without the binary-question form
- Positive fixtures for `offering_or_choice`: genuine binary-choice asks
- Same coverage for `should_i_or` and `your_decision_q`

If the tests pass, the empirical disposition is confirmed and row 29 is closed in full. If a false-positive shape surfaces during testing, that pattern is added to the tightening scope before VERIFIED.

## Implementation Plan

### Step 1: Tighten `PROSE_DECISION_PATTERNS` (carry forward from `-001`)

Replace patterns 3 and 4 (`awaiting_input`, `standing_by_for`) with split variants:

```python
PROSE_DECISION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("offering_or_choice", re.compile(r"\bwant me to\b[^.?!]*\bor\b[^.?!]*\?", re.IGNORECASE)),
    ("should_i_or", re.compile(r"\bshould I\b[^.?!]*\bor\b[^.?!]*\?", re.IGNORECASE)),
    # NEW: split awaiting_input into _q (interrogative) + _first_person (active wait)
    ("awaiting_input_q", re.compile(
        r"\bawaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?",
        re.IGNORECASE,
    )),
    ("awaiting_input_first_person", re.compile(
        r"\b(?:i am|i'm|we are|we're)\s+awaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b",
        re.IGNORECASE,
    )),
    # NEW: split standing_by_for into _q + _first_person
    ("standing_by_for_q", re.compile(
        r"\bstanding by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?",
        re.IGNORECASE,
    )),
    ("standing_by_for_first_person", re.compile(
        r"\b(?:i am|i'm|we are|we're)\s+standing by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b",
        re.IGNORECASE,
    )),
    ("your_decision_q", re.compile(r"\b(?:your|owner)\s+(?:decision|choice|input)\b[^.?!]{0,80}\?", re.IGNORECASE)),
)
```

### Step 2: Modify `_collect_prose_matches()` for matched-snippet-scoped guards (NEW per Codex `-002` F1)

Current implementation at `.claude/hooks/owner-decision-tracker.py:625-649`:

```python
def _collect_prose_matches(turn_events) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    for ev in turn_events:
        # ... extract full_text ...
        # GUARDS APPLIED TO FULL EVENT (current; per F1 too broad)
        if any(g.search(full_text) for g in PROSE_FALSE_POSITIVE_GUARDS):
            continue
        for name, pattern in PROSE_DECISION_PATTERNS:
            m = pattern.search(full_text)  # FIRST match only
            if m:
                snippet = full_text[max(0, m.start() - 20):m.end() + 20].strip()
                matches.append((name, snippet))
    return matches
```

Proposed replacement:

```python
# New constant: guard window size (chars) around each match
GUARD_LOCAL_WINDOW_CHARS = 200

def _collect_prose_matches(turn_events) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    for ev in turn_events:
        # ... extract full_text ...
        for name, pattern in PROSE_DECISION_PATTERNS:
            for m in pattern.finditer(full_text):  # ALL matches (was: search/first only)
                # Per-match guard scope: bounded local window around the match
                window_start = max(0, m.start() - GUARD_LOCAL_WINDOW_CHARS)
                window_end = min(len(full_text), m.end() + GUARD_LOCAL_WINDOW_CHARS)
                window = full_text[window_start:window_end]
                # Guards now apply to LOCAL WINDOW only, not full_text
                if any(g.search(window) for g in PROSE_FALSE_POSITIVE_GUARDS):
                    continue  # this match suppressed; other matches still evaluated
                snippet = full_text[max(0, m.start() - 20):m.end() + 20].strip()
                matches.append((name, snippet))
    return matches
```

Key behavioral changes:
- `pattern.search()` → `pattern.finditer()`: detects multiple matches per pattern per event
- Guards no longer skip the entire event; they only suppress the individual match whose local window contains a guard pattern
- Existing T14 guards (`decisions are hard`, `in general decisions`, `abstract decisions`) become more permissive: they now suppress only nearby matches, not all detection. This is a slight semantic relaxation but matches the original T14 intent (suppress ABSTRACT discussion of decisions, not all detection in a verbose event).

### Step 3: Extend `PROSE_FALSE_POSITIVE_GUARDS` (carry forward from `-001`)

Add 2 new guard patterns:

```python
PROSE_FALSE_POSITIVE_GUARDS: tuple[re.Pattern[str], ...] = (
    # Existing T14 guards (preserved):
    re.compile(r"\bdecisions are (?:hard|complex|difficult|tricky)\b", re.IGNORECASE),
    re.compile(r"\bin general,?\s+decisions?\b", re.IGNORECASE),
    re.compile(r"\babstract(?:ly)?,?\s+(?:about\s+)?decisions?\b", re.IGNORECASE),
    # NEW: self-reference suppressor (S328 directive). Applied per-match
    # via _collect_prose_matches() local-window logic (Step 2).
    re.compile(
        r"\b(?:PROSE_DECISION_PATTERNS|owner-decision-tracker|decision-tracker|prose pattern|prose-pattern|regex tightening)\b",
        re.IGNORECASE,
    ),
    # NEW: bridge-metadata context suppressor. Applied per-match via local-window logic.
    re.compile(
        r"\bCodex (?:GO|NO-GO|VERIFIED|review|`-\d+|F\d|umbrella)\b",
        re.IGNORECASE,
    ),
)
```

### Step 4: Remove env-override suppression (carry forward from `-001`)

Edit `.claude/settings.local.json` to remove the `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` env override.

### Step 5: Add test fixtures and tests (extended per Codex `-002` F1 + F2)

Create `groundtruth-kb/tests/fixtures/owner_decision_tracker/regex_negative_fixtures.txt`:

```
Awaiting your direction.
Awaiting owner direction. No stale-entry act required.
Awaiting your decision.
Awaiting Codex re-review on -003.
Awaiting CI green on develop.
The PROSE_DECISION_PATTERNS regex catches awaiting your direction phrases when properly tuned.
Codex GO at -004 left awaiting your verdict on the next slice.
Sub-slice F's promotion gate is awaiting owner approval per the umbrella scope.
The choice between A or B depends on context.
Either go or stop, the choice is structural.
This decision was hard, choosing between A or B felt risky.
Status: Codex GO at -004; want me to file Sub-slice B or wait for owner direction is unclear from the index alone.
```

(Last line is a synthesized factual status containing the trigger words but NOT in genuine ask form: it lacks the literal "Want me to X or Y?" interrogative form.)

Create `groundtruth-kb/tests/fixtures/owner_decision_tracker/regex_positive_fixtures.txt`:

```
Awaiting your direction?
I am awaiting your direction on which option to pick.
Standing by for owner approval?
I'm standing by for your decision on the deferred items.
Should I file -005 or wait for the umbrella?
Want me to clear pending or defer all of them?
Want me to file Sub-slice B or pause until owner directs?
Should I commit and push now or wait for review?
Your decision on the next sub-slice priority?
What is your choice between Path A or Path B for the deferred items?
```

Add `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` with tests:

- `test_negative_fixtures_no_match`: load negative-fixture file, assert `_collect_prose_matches()` returns empty for each line
- `test_positive_fixtures_match`: load positive-fixture file, assert `_collect_prose_matches()` returns ≥1 match per line; assert at least one positive fixture matches each of the 7 prose patterns (after split: 7 patterns total)
- `test_self_reference_guard_suppresses`: synthetic event "I am awaiting your direction on the regex tightening" — guard suppresses despite first-person form
- `test_bridge_metadata_guard_suppresses`: synthetic event "Codex GO at -004 confirms we are awaiting your direction on next steps" — guard suppresses
- **`test_mixed_event_genuine_ask_still_matches` (NEW per Codex `-002` F1):** synthetic event with TWO paragraphs: paragraph 1 = "The umbrella -004 Codex GO confirmed scope. PROSE_DECISION_PATTERNS regex tightening was approved." (guard region); paragraph 2 (separated by 500+ chars) = "I am awaiting your direction on Sub-slice B priority." (genuine ask, far from guard region). Assert `_collect_prose_matches()` returns the genuine ask match (proves guards no longer suppress entire event).
- **`test_mixed_event_two_genuine_asks_both_match` (NEW per Codex `-002` F1):** synthetic event with two genuine asks separated by neutral text. Assert both matches detected (proves `finditer()` switch).
- `test_block_emission_enabled_when_env_unset`: assert `_block_emission_enabled()` returns True when env var is absent
- `test_offering_or_choice_negative`: factual statements containing "want me to" or "or" without `?` — assert no match (verifies pattern is acceptably conservative)
- `test_offering_or_choice_positive`: genuine binary-choice asks — assert match
- `test_should_i_or_negative`: factual statements containing "should I" without `?` — assert no match
- `test_should_i_or_positive`: genuine "Should I X or Y?" asks — assert match
- `test_your_decision_q_negative`: factual statements containing "your decision" without `?` — assert no match
- `test_your_decision_q_positive`: genuine "your decision?" asks — assert match

### Step 6: Commit on develop

(Carry forward from `-001` Step 5; commit message updated to reflect F1 + F2 fixes.)

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-a" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains Specification Links + spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-out-of-applications-A** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff <Sub-A-baseline>..<Sub-A-VERIFIED-commit> --name-only \| grep "^applications/"` | Empty (no files under `applications/` introduced) |
| **T-regex-negative-fixtures** | regex tightening contract (false-positive reduction; covers all 7 split patterns) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_negative_fixtures_no_match -v` | PASS — every line in `regex_negative_fixtures.txt` returns empty match list |
| **T-regex-positive-fixtures** | regex tightening contract (positive coverage preserved across all 7 split patterns) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_positive_fixtures_match -v` | PASS — every positive line matches; ≥1 positive line maps to each of the 7 patterns |
| **T-guard-self-reference** | T14 self-reference guard (per S328) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_self_reference_guard_suppresses -v` | PASS — synthetic detector-describing text suppresses match |
| **T-guard-bridge-metadata** | T14 bridge-metadata guard (per S328) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_bridge_metadata_guard_suppresses -v` | PASS — synthetic bridge-state-mentioning text suppresses |
| **T-mixed-event-1** (NEW per Codex `-002` F1) | guard scope correction: guards apply per-match, not whole-event | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_mixed_event_genuine_ask_still_matches -v` | PASS — genuine ask in same event but far from guard region still matches |
| **T-mixed-event-2** (NEW per Codex `-002` F1) | finditer switch: multiple genuine asks per event detected | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_mixed_event_two_genuine_asks_both_match -v` | PASS — both asks detected as separate matches |
| **T-env-override-absent** | env override removal | `python -c "import json; c=json.load(open('.claude/settings.local.json')); print('GTKB_BLOCK_ON_PROSE_DECISION_ASK' not in c.get('env', {}))"` | `True` |
| **T-block-emission-end-to-end** | block emission round-trip | Run hook in Stop mode with synthetic transcript containing prose decision-ask but no AUQ tool_use; capture stdout JSON | Stdout contains `{"decision": "block", "reason": "..."}` JSON |
| **T-offering-or-choice-coverage** (NEW per Codex `-002` F2) | offering_or_choice empirical disposition | 2 pytest tests: `test_offering_or_choice_negative` + `test_offering_or_choice_positive` | Both PASS |
| **T-should-i-or-coverage** (NEW per Codex `-002` F2) | should_i_or empirical disposition | 2 pytest tests: `test_should_i_or_negative` + `test_should_i_or_positive` | Both PASS |
| **T-your-decision-q-coverage** (NEW per Codex `-002` F2) | your_decision_q empirical disposition | 2 pytest tests: `test_your_decision_q_negative` + `test_your_decision_q_positive` | Both PASS |
| **T-platform-smoke** | GT-KB platform integrity | `python -m pytest groundtruth-kb/tests/ -x --tb=short -q -k "owner_decision or hook or decision_tracker" --timeout=60` | PASS (or pre-existing-known failures only) |
| **T-row29-closure** | work_list row 29 dropped on VERIFIED with FULL coverage of all 5 (now 7 split) prose patterns | After VERIFIED, `grep -c "GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING" memory/work_list.md` | 0 (or row body replaced with closure note citing coverage of all 5 prose-pattern families) |

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-A | Direct |
| Regex tightening contract — 7 split patterns | T-regex-negative-fixtures, T-regex-positive-fixtures | Direct |
| Guard scope correction (per Codex `-002` F1) | T-mixed-event-1, T-mixed-event-2 | Direct |
| T14 guard extensions (per S328) | T-guard-self-reference, T-guard-bridge-metadata | Direct |
| `offering_or_choice` empirical disposition (per Codex `-002` F2) | T-offering-or-choice-coverage | Direct |
| `should_i_or` empirical disposition (per Codex `-002` F2) | T-should-i-or-coverage | Direct |
| `your_decision_q` empirical disposition (per Codex `-002` F2) | T-your-decision-q-coverage | Direct |
| Env override removal | T-env-override-absent | Direct |
| Block emission round-trip | T-block-emission-end-to-end | Direct |
| GT-KB platform integrity | T-platform-smoke | Direct |
| work_list row 29 full closure | T-row29-closure | Direct |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice A REVISED-1 proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Regex changes reviewed for over-correction risk
- [ ] Guard-scope correction reviewed (per-match local-window semantics)
- [ ] Empirical disposition for `offering_or_choice` / `should_i_or` / `your_decision_q` reviewed and accepted

VERIFIED when:

- [ ] All 17 tests T-bridge-1 through T-row29-closure PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Tightened regex passes negative + positive fixture suites covering all 7 split patterns
- [ ] Both new T14 guards pass per-match local-window tests (T-guard-self-reference + T-guard-bridge-metadata)
- [ ] Mixed-event tests confirm guards no longer suppress entire events (T-mixed-event-1, T-mixed-event-2)
- [ ] Empirical disposition coverage tests pass (T-offering-or-choice-coverage, T-should-i-or-coverage, T-your-decision-q-coverage)
- [ ] Env override removed (T-env-override-absent)
- [ ] Block emission verified end-to-end (T-block-emission-end-to-end)
- [ ] GT-KB platform smoke passes (T-platform-smoke)
- [ ] work_list row 29 closed with full-coverage citation (T-row29-closure)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Guard-scope correction over-permits: small assistant events with guard text adjacent to genuine ask still suppress | Medium | Medium | `GUARD_LOCAL_WINDOW_CHARS = 200` is tuneable; if guard region overlaps genuine asks within ~200 chars, the guard still suppresses (designed behavior). T-mixed-event-1 separates regions by 500+ chars to verify clear separation works |
| `finditer()` switch produces duplicate matches per event when same pattern matches multiple sentences | Low | Low | Each match is its own (pattern_name, snippet) tuple; duplicates with different snippets are distinct decisions; deduplication occurs in the durable-file write path via `question_hash` |
| Tightened regex over-corrects: genuine prose asks fail to match | Medium | High | Positive-fixture suite covers 7 split patterns; Codex review against fixture corpus during GO review |
| Self-reference guard fires on legitimate use of detector terms in genuine asks | Low | Low | Per-match local-window scope makes this very narrow: only suppresses if guard term is within ±200 chars of the matched ask AND the ask itself doesn't span outside that window |
| Bridge-metadata guard fires when reporting bridge state alongside genuine ask | Low | Low | Per-match scope; if bridge-state mention is ≥200 chars from the ask, no suppression |
| Block emission causes loop (ask blocked → AUQ called → next turn blocks again) | Low | High | Bounded-exception design preserves one-block-per-turn invariant per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` |
| Pre-existing pytest failures interfere | Medium | Low | T-platform-smoke uses focused `-k` filter; pre-existing failures documented |

Rollback: `git revert` of the single commit reverses regex changes, env-override removal, fixture additions, test additions, and `_collect_prose_matches()` modifications atomically.

## Open Questions

(All scope decisions resolved.)

| ID | Question | Resolution |
|----|----------|------------|
| OQ-A-1 | Tighten which patterns? | Patterns 3 + 4 split into _q + _first_person variants (4 new patterns; 7 total after split). Patterns 1, 2, 5 verified acceptable via empirical disposition tests (per Codex `-002` F2). |
| OQ-A-2 | Guard scope? | Per-match local window (±200 chars) per Codex `-002` F1. Implemented via `_collect_prose_matches()` modification (Step 2). |
| OQ-A-3 | row 29 closure? | Full closure on Sub-slice A VERIFIED with empirical disposition coverage for all 5 prose-pattern families (now 7 with split). |
| OQ-A-4 (NEW) | `GUARD_LOCAL_WINDOW_CHARS` value? | 200 (default; tuneable via constant). Codex review against synthetic fixtures during GO. |

## Owner Decisions / Input

This sub-slice's authorization derives from a chain of owner AskUserQuestion answers in S331 and the umbrella-level approval cascade:

1. **Enforcement priority** — owner: "Block ISOLATION-018; enforcement first"
2. **Umbrella scope** — owner: "Full 6-mechanism stack"
3. **Sub-slice autonomy** — owner: "Autonomous progression" (authorizes filing this sub-slice and revisions under standard lifecycle)

Plus prior owner directive (S328, work_list row 29) defining the regex-tightening + T14-guard-extension scope.

No additional owner input pending at sub-slice level.

## Out of Scope

- Widening the bounded-exception block-emission scope (still: one block per turn per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md`)
- Modifying the bridge-compliance-gate hook (Sub-slice C)
- Modifying Prime Builder rules (Sub-slice B)
- Audit pass over `memory/pending-owner-decisions.md` historical entries (Sub-slice D)
- Implementing the requirements-collection hook (Sub-slice E)
- Adding release-metric doctor checks (Sub-slice F)
- Resolution of pre-existing scaffold-golden fixture mismatch (separate fixture-refresh slice)
- Session-tracker cwd anchoring fix (separate hook-hygiene slice)

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- Targets `.claude/hooks/owner-decision-tracker.py`, `.claude/settings.local.json`, `groundtruth-kb/tests/` (test fixtures + new test file), and `bridge/`.
- No live-dependency paths outside `E:/GT-KB/`.
- Does NOT depend on Agent Red as a live GT-KB artifact.
- Does NOT create new content under `applications/`.
- Per `.claude/rules/project-root-boundary.md`.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1) |
| Umbrella Codex GO | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` |
| Sub-slice A Codex NO-GO | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-002.md` (F1 + F2 findings addressed in this revision) |
| Source DELIB (S328 regex-tightening directive) | work_list row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) |
| Existing surfacing impl | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED 2026-04-27 |
| Existing block emission impl | `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED |
| Owner scope confirmations | This S331 conversation: 3 AskUserQuestion answers (priority, scope, autonomy) |
| Empirical false-positive corpus | This S331 conversation: 4 prose-pattern matches accumulated in `memory/pending-owner-decisions.md` |
| Live probes | `head` of `.claude/hooks/owner-decision-tracker.py` lines 100-149 (PROSE_DECISION_PATTERNS + GUARDS), 620-649 (`_collect_prose_matches()`) (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
