REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening (REVISED-2)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice A of GTKB-GOV-AUQ-ENFORCEMENT-STACK (umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`, Codex GO at -004)
**Mechanism:** 2 (per umbrella sub-slice plan: Hook upgrade — logging → blocking)
**Risk tier:** Medium

**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-004.md` — F1 (`-003`'s claim that no documented FP shape exists for `offering_or_choice` was contradicted by live S309 evidence: `memory/pending-owner-decisions.md:1055-1073` records DECISION-0001 and DECISION-0002 as `prose:offering_or_choice` quoted/backtick-literal false positives, plus `memory/work_list.md:464` row P7 explicitly preserves this as "Decision-tracker false-positive guard tightening" with quotation-aware + code-fence-aware guards as the documented fix path). Codex's local simulation confirmed `-003`'s proposed regex + guards still match these documented fragments.

---

## Codex Findings Addressed

### Cycle 2 (NO-GO at -004, addressed in -005)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — `offering_or_choice` disposition contradicts live FP evidence. DECISION-0001 (`memory/pending-owner-decisions.md:1055-1063`) and DECISION-0002 (`:1065-1073`) are documented `prose:offering_or_choice` quoted/backtick-literal FPs from S309. work_list row P7 preserves this as a separate tightening item. `-003`'s proposed self-reference + bridge-metadata guards do not match the literal text `("want me to X or Y?")` because the guard patterns (`PROSE_DECISION_PATTERNS`, `owner-decision-tracker`, etc.) do not appear adjacent to the matched fragment. | "Add quotation-aware / code-fence-aware guard behavior and regression fixtures for DECISION-0001 and DECISION-0002; OR tighten `offering_or_choice` itself so quoted or detector-describing examples do not fire while genuine owner-facing binary asks still fire; OR split `offering_or_choice` false-positive closure into a named follow-up." | This revision adopts **Codex's option 2 (regex tightening)** by adding a single-character negative lookbehind `(?<!["` + chr(96) + `])` to all 7 prose patterns. The lookbehind suppresses matches when the trigger word is immediately preceded by `"` (double-quote) or a backtick. This handles the documented FP class uniformly across all 7 patterns at the regex layer (before the per-match local-window guard step from `-003`). DECISION-0001 and DECISION-0002 fragments are added to `regex_negative_fixtures.txt`; new tests T-quoted-fp-1 (DECISION-0001 doc-paragraph FP) and T-quoted-fp-2 (DECISION-0002 backtick-literal FP) verify suppression. work_list row 29 closes in full on Sub-slice A VERIFIED with this evidence; work_list row P7 (quotation-aware tightening) is also closed by the lookbehind addition. |

### Cycle 1 (NO-GO at -002, addressed in -003 — carry-forward)

| Finding | Disposition (preserved in -005) |
|---------|--------------------------------|
| F1 (guard scope) | `_collect_prose_matches()` modified for per-match local-window scope; `pattern.search()` → `pattern.finditer()`; new tests T-mixed-event-1, T-mixed-event-2. |
| F2 (row 29 partial coverage) | All 5 prose-pattern families covered in fixture corpus; empirical disposition for the 3 already-conservative patterns. **Updated in -005:** the "no documented FP shape exists" claim is replaced with "negative lookbehind handles documented quoted FPs" (per `-004` F1). |

---

## Background

(Carry forward from `-003`.) The umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (Codex GO at -004) decomposes the AUQ enforcement program into 6 sub-slices. Sub-slice A is the highest-leverage starting point. Current state of `.claude/hooks/owner-decision-tracker.py`: detection live, block emission feature-flag-gated via env override since S328.

S331 (this session) accumulated additional prose-pattern matches in `memory/pending-owner-decisions.md`. Combined with the S309 DECISION-0001/0002 documented FPs and the S328 regex-tightening directive, this sub-slice tightens the regex AND re-enables block emission.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-005.md`; INDEX update at top of `bridge/INDEX.md` is the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Canonical placement contract. Applicability: this sub-slice modifies `.claude/hooks/owner-decision-tracker.py`, `.claude/settings.local.json`, and (test-only) files; it does NOT create files under `applications/`.

Topic-specific governance for this work:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1 at GO -004).
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — Source rule for owner-decision surfacing infrastructure.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED 2026-04-27).
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED) — Bounded-exception block emission.
- `memory/work_list.md` row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) — Owner-directed S328; absorbed by Sub-slice A.
- `memory/work_list.md:464` row P7 ("Decision-tracker false-positive guard tightening") — quotation-aware + code-fence-aware guards; absorbed by Sub-slice A via negative-lookbehind addition (per Codex `-004` F1).
- `memory/pending-owner-decisions.md:1055-1073` (DECISION-0001 + DECISION-0002 S309 documented FPs) — concrete fixture corpus per Codex `-004` F1.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/project-root-boundary.md` — bridge protocol + rules.
- `.claude/hooks/owner-decision-tracker.py` — Target of modification: `PROSE_DECISION_PATTERNS` tuple (negative lookbehind added to all 7 patterns), `PROSE_FALSE_POSITIVE_GUARDS` tuple (2 new guards), `_collect_prose_matches()` function (per-match local-window scope per `-003` Step 2).
- `.claude/settings.local.json` — Target of modification: remove `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` env override.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

The proposed tests in the Test Plan section derive from these linked specs as follows: regex tightening → T-regex-negative-fixtures + T-regex-positive-fixtures (factual status statements + quoted/fenced literals skip; genuine asks still match across all 7 patterns); guard scope correction → T-mixed-event-1 + T-mixed-event-2 (carry-forward); T14 guard extensions → T-guard-self-reference + T-guard-bridge-metadata (carry-forward); **NEW per Codex `-004` F1:** quoted-FP coverage → T-quoted-fp-1 + T-quoted-fp-2 (DECISION-0001 + DECISION-0002 fixture lines suppress); env-override removal → T-env-override-absent; block-emission round-trip → T-block-emission-end-to-end; platform smoke → T-platform-smoke; row 29 + row P7 closure → T-row29-closure + T-rowp7-closure.

## Prior Deliberations

(Carry forward from `-003`, plus add Codex `-004` NO-GO + S309 DECISION-0001/0002 evidence.)

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive (per `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED) | owner_conversation | owner_decision | Source rule |
| Implicit S321 owner directive (per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED) | owner_conversation | owner_decision | Bounded exception |
| S328 regex-tightening directive (work_list row 29) | owner_conversation | owner_decision | Tighten regex; add T14-class guards |
| S309 DECISION-0001 / DECISION-0002 (`memory/pending-owner-decisions.md:1055-1073`) | bridge_thread | resolved (FP) | Live evidence per Codex `-004` F1; concrete fixture corpus |
| work_list row P7 (`memory/work_list.md:464`) | owner_conversation | owner_decision | Quotation-aware + code-fence-aware guards |
| S331 AUQ #1, #2, #3 | owner_conversation | owner_decision | Enforcement priority + scope + autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice A approved |
| Codex Sub-slice A -002 NO-GO | bridge_thread | no_go | F1 + F2 addressed in -003 |
| Codex Sub-slice A -004 NO-GO | bridge_thread | no_go | F1 (offering_or_choice FP class) addressed in -005 |

## Goal

Sub-slice A delivers four coupled outcomes (carry-forward from `-003`) plus one targeted regex tightening for the documented offering_or_choice FP class:

1. **Tighten `PROSE_DECISION_PATTERNS`** with negative lookbehind `(?<!["` + chr(96) + `])` on all 7 patterns (NEW per `-004` F1) AND split `awaiting_input`/`standing_by_for` into _q + _first_person variants (carry-forward from `-001`/`-003`).
2. **Modify `_collect_prose_matches()`** for per-match local-window scope (carry-forward from `-003`).
3. **Extend `PROSE_FALSE_POSITIVE_GUARDS`** with self-reference + bridge-metadata suppressors (carry-forward from `-001`/`-003`).
4. **Re-enable block emission** by removing env override (carry-forward).

work_list row 29 (S328 regex tightening) AND row P7 (S309 quotation-aware tightening) both close on Sub-slice A VERIFIED with the negative-lookbehind addition and concrete DECISION-0001/0002 fixture coverage.

## Implementation Plan

### Step 1: Tighten `PROSE_DECISION_PATTERNS` with negative lookbehind + split variants

Replace the current pattern definitions with:

```python
PROSE_DECISION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # All patterns prefixed with negative lookbehind (?<!["`])
    # to suppress quoted/backtick-bounded literals (DECISION-0001/0002 class).
    ("offering_or_choice", re.compile(
        r'(?<!["`])\bwant me to\b[^.?!]*\bor\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    ("should_i_or", re.compile(
        r'(?<!["`])\bshould I\b[^.?!]*\bor\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    # NEW: split awaiting_input into _q (interrogative) + _first_person (active wait), with lookbehind
    ("awaiting_input_q", re.compile(
        r'(?<!["`])\bawaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    ("awaiting_input_first_person", re.compile(
        r'(?<!["`])\b(?:i am|i\'m|we are|we\'re)\s+awaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b',
        re.IGNORECASE,
    )),
    # NEW: split standing_by_for similarly, with lookbehind
    ("standing_by_for_q", re.compile(
        r'(?<!["`])\bstanding by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?',
        re.IGNORECASE,
    )),
    ("standing_by_for_first_person", re.compile(
        r'(?<!["`])\b(?:i am|i\'m|we are|we\'re)\s+standing by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b',
        re.IGNORECASE,
    )),
    ("your_decision_q", re.compile(
        r'(?<!["`])\b(?:your|owner)\s+(?:decision|choice|input)\b[^.?!]{0,80}\?',
        re.IGNORECASE,
    )),
)
```

Effect on documented FP corpus from `memory/pending-owner-decisions.md`:

| Sample | Old match? | New match? | Reason |
|--------|-----------:|-----------:|--------|
| `ose anti-patterns ("want me to X or Y?") and logs them.` (DECISION-0001) | YES | NO | Lookbehind blocks: `"` precedes "want" |
| ``The detector saw `"want me to X or Y?"` as a literal string.`` (DECISION-0002) | YES | NO | Lookbehind blocks: `"` precedes "want" inside backtick fence |
| `Want me to push or wait?` (genuine, sentence-start) | YES | YES | Lookbehind passes: start-of-string before "Want" |
| `Mike asked, want me to push or wait?` | YES | YES | Lookbehind passes: comma+space before "want" |
| `("Want me to start?")` (parenthesized quote) | YES | NO | Lookbehind blocks: `"` precedes "Want" |
| `Awaiting your direction.` (status report) | YES | NO | New _q/_first_person split; no `?` and no 1st-person |
| `Awaiting your direction?` (interrogative) | YES | YES | Matched by `_q` variant |
| `I am awaiting your direction.` (1st-person active wait) | YES | YES | Matched by `_first_person` variant |
| `("Awaiting your direction?")` (quoted ask example) | YES | NO | Lookbehind blocks: `"` precedes "Awaiting" |

### Step 2: Modify `_collect_prose_matches()` for matched-snippet-scoped guards (carry-forward from `-003`)

Same as `-003` Step 2: switch `pattern.search()` to `pattern.finditer()`; add `GUARD_LOCAL_WINDOW_CHARS = 200` constant; apply guards per-match against bounded local window instead of `full_text`.

### Step 3: Extend `PROSE_FALSE_POSITIVE_GUARDS` (carry-forward from `-003`)

Same 2 new guards: self-reference suppressor + bridge-metadata context suppressor.

### Step 4: Remove env-override suppression (carry-forward)

Edit `.claude/settings.local.json` to remove `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0`.

### Step 5: Add test fixtures + tests (extended per Codex `-004` F1)

Add the following negative fixture lines to `groundtruth-kb/tests/fixtures/owner_decision_tracker/regex_negative_fixtures.txt` (carry-forward from `-003` plus 2 new fixture lines):

```
# (existing -003 negative fixture lines preserved)

# Quoted/backtick-bounded FP class (DECISION-0001 + DECISION-0002 from memory/pending-owner-decisions.md:1055-1073, S309)
ose anti-patterns ("want me to X or Y?") and logs them.
The detector saw `"want me to X or Y?"` as a literal string.
prose anti-patterns ("should I X or Y?") and logs them.
The detector saw `"awaiting your direction?"` as a literal example.
```

Add the following tests to `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` (carry-forward from `-003` plus 2 new tests):

- (existing `-003` tests preserved)
- **`test_quoted_fp_1_decision0001` (NEW per `-004` F1):** assert `_collect_prose_matches()` returns empty for DECISION-0001 fixture line `ose anti-patterns ("want me to X or Y?") and logs them.`
- **`test_quoted_fp_2_decision0002` (NEW per `-004` F1):** assert `_collect_prose_matches()` returns empty for DECISION-0002 fixture line ``The detector saw `"want me to X or Y?"` as a literal string.``
- **`test_quoted_fp_other_patterns` (NEW per `-004` F1):** assert lookbehind suppresses quoted instances of all 7 patterns; positive control: same patterns at sentence-start still match

### Step 6: Commit on develop

(Same structure as `-003`, with commit message updated to reference `-004` F1 fix.)

## Specification-Derived Test Plan

(Carry-forward from `-003` test plan with 3 new tests added per `-004` F1.)

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-a" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-out-of-applications-A** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only \| grep "^applications/"` | Empty |
| **T-regex-negative-fixtures** | regex tightening (covers all 7 patterns + DECISION-0001/0002 quoted-FP corpus) | `pytest test_owner_decision_tracker_regex_tightening.py::test_negative_fixtures_no_match -v` | PASS |
| **T-regex-positive-fixtures** | regex tightening (positive coverage; ≥1 fixture per pattern) | `pytest ::test_positive_fixtures_match -v` | PASS |
| **T-guard-self-reference** | T14 self-reference guard | `pytest ::test_self_reference_guard_suppresses -v` | PASS |
| **T-guard-bridge-metadata** | T14 bridge-metadata guard | `pytest ::test_bridge_metadata_guard_suppresses -v` | PASS |
| **T-mixed-event-1** | guard scope correction (carry-forward from `-003`) | `pytest ::test_mixed_event_genuine_ask_still_matches -v` | PASS |
| **T-mixed-event-2** | finditer multi-match (carry-forward from `-003`) | `pytest ::test_mixed_event_two_genuine_asks_both_match -v` | PASS |
| **T-quoted-fp-1** (NEW per `-004` F1) | DECISION-0001 doc-paragraph FP suppression | `pytest ::test_quoted_fp_1_decision0001 -v` | PASS |
| **T-quoted-fp-2** (NEW per `-004` F1) | DECISION-0002 backtick-literal FP suppression | `pytest ::test_quoted_fp_2_decision0002 -v` | PASS |
| **T-quoted-fp-other-patterns** (NEW per `-004` F1) | lookbehind suppresses quoted instances of all 7 patterns | `pytest ::test_quoted_fp_other_patterns -v` | PASS |
| **T-env-override-absent** | env override removal | `python -c "..."` JSON check | `True` |
| **T-block-emission-end-to-end** | block emission round-trip | hook Stop-mode invocation with synthetic transcript | `{"decision": "block", ...}` JSON |
| **T-offering-or-choice-coverage** | offering_or_choice empirical disposition (carry-forward from `-003`, now strengthened by lookbehind) | `pytest ::test_offering_or_choice_negative + ::test_offering_or_choice_positive` | Both PASS |
| **T-should-i-or-coverage** | should_i_or empirical disposition | similar | Both PASS |
| **T-your-decision-q-coverage** | your_decision_q empirical disposition | similar | Both PASS |
| **T-platform-smoke** | platform integrity | `pytest groundtruth-kb/tests/ -k "owner_decision or hook or decision_tracker" -x --timeout=60` | PASS (or pre-existing-known failures only) |
| **T-row29-closure** | work_list row 29 dropped on VERIFIED | `grep -c "GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING" memory/work_list.md` | 0 (or row body replaced with closure note citing this Sub-slice) |
| **T-rowp7-closure** (NEW per `-004` F1) | work_list row P7 (quotation-aware tightening) dropped on VERIFIED | `grep -c "Decision-tracker false-positive guard tightening" memory/work_list.md` | 0 (or replaced with closure note) |

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-A | Direct |
| Regex tightening contract (7 patterns + lookbehind) | T-regex-negative-fixtures, T-regex-positive-fixtures, T-quoted-fp-1, T-quoted-fp-2, T-quoted-fp-other-patterns | Direct |
| Guard scope correction (per `-002` F1) | T-mixed-event-1, T-mixed-event-2 | Direct |
| T14 guard extensions (per S328) | T-guard-self-reference, T-guard-bridge-metadata | Direct |
| Empirical disposition (per `-002` F2) | T-offering-or-choice-coverage, T-should-i-or-coverage, T-your-decision-q-coverage | Direct |
| Env override removal | T-env-override-absent | Direct |
| Block emission round-trip | T-block-emission-end-to-end | Direct |
| Platform integrity | T-platform-smoke | Direct |
| work_list row 29 + row P7 closure | T-row29-closure, T-rowp7-closure | Direct |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice A REVISED-2 proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Negative-lookbehind addition reviewed for over-correction risk (e.g., apostrophes after "Mike's" do not break adjacent matches)
- [ ] DECISION-0001/0002 fixture lines added to negative corpus

VERIFIED when:

- [ ] All 20 tests T-bridge-1 through T-rowp7-closure PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Quoted-FP suppression verified (T-quoted-fp-1, T-quoted-fp-2, T-quoted-fp-other-patterns)
- [ ] Tightened regex passes negative + positive fixture suites
- [ ] Mixed-event tests confirm guards no longer suppress entire events
- [ ] Env override removed; block emission verified end-to-end
- [ ] GT-KB platform smoke passes
- [ ] work_list row 29 + row P7 closed (T-row29-closure, T-rowp7-closure)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Negative lookbehind over-corrects: legitimate sentence-internal asks preceded by `"` or backtick fail to match | Low | Medium | Lookbehind is single-char; only suppresses immediate `"` or backtick prefix. Sentence-start asks (most common form) and asks after whitespace are unaffected. Positive fixture suite covers representative forms |
| Apostrophe in "I'm" / "we're" inside the lookbehind character class | Low | Medium | Character class is `["` + backtick `]` only; apostrophe (`'`) NOT included. Patterns like "I'm awaiting your direction" are not affected because the lookbehind sits BEFORE "I" in `I'm` (or before "we" in "we're"), and the prefix is whitespace/start, not quote |
| Backtick lookbehind blocks legitimate technical mentions in genuine asks | Low | Low | Edge case: `\`code\` should I update or wait?` — preceding char of "should" is space, lookbehind passes. Match. Correct |
| (carry-forward) guard-scope correction over-permits | Medium | Medium | T-mixed-event-1/2 verify clear separation works |
| (carry-forward) tightened regex over-corrects | Medium | High | Positive-fixture suite + Codex review |
| (carry-forward) block emission causes loop | Low | High | Bounded-exception design preserves one-block-per-turn invariant |
| Pre-existing pytest failures interfere | Medium | Low | T-platform-smoke uses focused `-k` filter |

Rollback: `git revert` of the single commit reverses all changes atomically.

## Open Questions

(All scope decisions resolved.)

| ID | Question | Resolution |
|----|----------|------------|
| OQ-A-1 | Tighten which patterns? | All 7 (split + lookbehind) |
| OQ-A-2 | Guard scope? | Per-match local window (per `-002` F1) |
| OQ-A-3 | row 29 closure? | Full closure on Sub-slice A VERIFIED with empirical disposition + lookbehind coverage |
| OQ-A-4 | `GUARD_LOCAL_WINDOW_CHARS` value? | 200 |
| OQ-A-5 (NEW per `-004` F1) | Quoted/fenced FP class handling? | Codex option 2 (regex tightening): negative lookbehind `(?<!["` + backtick + `])` on all 7 patterns. Closes work_list row P7 alongside row 29. |

## Owner Decisions / Input

This sub-slice's authorization derives from:

1. S331 AUQ #1, #2, #3 (umbrella enforcement priority + scope + autonomy).
2. S328 work_list row 29 owner directive (regex tightening).
3. S309 work_list row P7 owner directive (quotation-aware + code-fence-aware guards) — absorbed by this revision via negative-lookbehind addition.
4. Umbrella -004 Codex GO (enforcement umbrella approved).

No additional owner input pending at sub-slice level.

## Out of Scope

- Widening the bounded-exception block-emission scope.
- Modifying the bridge-compliance-gate hook (Sub-slice C).
- Modifying Prime Builder rules (Sub-slice B).
- Audit pass over `memory/pending-owner-decisions.md` historical entries (Sub-slice D).
- Implementing the requirements-collection hook (Sub-slice E).
- Adding release-metric doctor checks (Sub-slice F).
- Resolution of pre-existing scaffold-golden fixture mismatch.
- Session-tracker cwd anchoring fix.
- Code-fence-aware structural detection (multi-line ``` blocks). The negative lookbehind handles single-char-prefixed quoted/backtick literals which covers DECISION-0001/0002. Full structural code-fence parsing is over-engineering for the documented FP class; deferred unless future evidence requires it.

## Project Root Boundary Compliance

(Carry-forward from `-003`.) Operates entirely within `E:/GT-KB/`. No files under `applications/` introduced.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` |
| Umbrella Codex GO | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` |
| Sub-slice A Codex NO-GO `-002` | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-002.md` |
| Sub-slice A Codex NO-GO `-004` | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-004.md` (F1: offering_or_choice FP class) |
| Source DELIB (S328 regex-tightening) | work_list row 29 |
| Source DELIB (S309 quotation-aware tightening) | work_list row P7 (`memory/work_list.md:464`) |
| Documented FP corpus | `memory/pending-owner-decisions.md:1055-1073` (DECISION-0001 + DECISION-0002, S309 resolutions) |
| Existing surfacing impl | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED |
| Existing block emission impl | `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED |
| Owner scope confirmations | This S331 conversation: 3 AskUserQuestion answers |
| Live probes | `grep` of `memory/pending-owner-decisions.md` for DECISION-0001/0002 (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
