NEW

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice A of GTKB-GOV-AUQ-ENFORCEMENT-STACK (umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`, Codex GO at -004)
**Mechanism:** 2 (per umbrella sub-slice plan: Hook upgrade — logging → blocking)
**Risk tier:** Medium (regex pattern changes affect Stop-mode behavior; block emission re-enabled after env override removal)
**Authorization:** S331 AUQ #1 + #2 + #3 + umbrella -004 Codex GO + work_list row 29 owner directive (S328)

---

## Background

The umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (Codex GO at -004) decomposes the AUQ enforcement program into 6 sub-slices A through F. Sub-slice A is the highest-leverage starting point because it absorbs work_list row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`, owner-directed S328) and re-enables already-implemented block emission infrastructure that has been disabled via env override since S328.

Current state of `.claude/hooks/owner-decision-tracker.py`:

- **Detection:** `PROSE_DECISION_PATTERNS` (5 patterns) + `PROSE_FALSE_POSITIVE_GUARDS` (3 T14-class guards) currently active for Stop-mode prose-decision-ask detection.
- **Block emission:** Bounded-exception block JSON emission implemented per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED). Suppressed via `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` in `.claude/settings.local.json::env`.
- **Detection feedback loop:** Multiple S328 incidents documented where the regex matched factual status statements as false positives, prompting the env-override workaround.

S331 (this session) accumulated four prose-pattern matches in `memory/pending-owner-decisions.md` from agent prose during 18.B/18.C/umbrella drafting work. While some of those are arguably true positives (the agent reverted to prose decision-asks in places where AskUserQuestion was the correct channel), others are factual status statements where the regex over-triggered. This sub-slice tightens the regex to reduce the over-trigger surface AND re-enables block emission so future agent prose decision-asks fail fast at the harness boundary.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-001.md`; INDEX update at top of `bridge/INDEX.md` is the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this section enumerates all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section maps every spec clause to a concrete test command and expected result.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Canonical placement contract. Applicability to this sub-slice: this sub-slice modifies `.claude/hooks/owner-decision-tracker.py`, `.claude/settings.local.json`, and (test-only) files; it does NOT create files under `applications/`. T-out-of-applications-A in the test plan asserts no files under `applications/` are introduced by this sub-slice's commit.

Topic-specific governance for this work:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1 at GO -004) — defines this sub-slice's scope and dependencies.
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — Source rule for owner-decision surfacing infrastructure; this sub-slice extends with tightened detection + active block emission.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED 2026-04-27) — Original owner-decision surfacing implementation; this sub-slice modifies the hook this implementation produced.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED) — Bounded-exception block emission infrastructure; this sub-slice does NOT widen the bounded exception scope (still: prose-decision-ask without same-turn AUQ → one block per turn). It removes the env-override suppression and tightens the underlying regex.
- `memory/work_list.md` row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) — Owner-directed S328; this sub-slice absorbs and closes the row on VERIFIED.
- `.claude/rules/prime-builder-role.md` — Existing Prime rule; references AUQ. (Sub-slice B extends with explicit AUQ-only declaration; not modified by Sub-slice A.)
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; this proposal complies with Mandatory Specification Linkage Gate + Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; this proposal is the artifact submitted for review.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation; satisfied via Prior Deliberations section.
- `.claude/rules/project-root-boundary.md` — Project root boundary rule; this sub-slice operates entirely within `E:/GT-KB/`.
- `.claude/hooks/owner-decision-tracker.py` — Target of modification: `PROSE_DECISION_PATTERNS` tuple + `PROSE_FALSE_POSITIVE_GUARDS` tuple.
- `.claude/settings.local.json` — Target of modification: remove `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` env override.
- `memory/pending-owner-decisions.md` — Durable evidence file; existing entries preserved; new prose-detections after Sub-slice A VERIFIED will reflect tightened regex.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts, tests, reports, decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states.

The proposed tests in the Test Plan section derive from these linked specs as follows: regex tightening contract → T-regex-negative-fixtures + T-regex-positive-fixtures (factual status statements no longer match; genuine asks still match); T14 guard extension → T-guard-self-reference + T-guard-bridge-metadata (suppressors fire on detector-describing or bridge-metadata text); env-override removal → T-env-override-absent (env var no longer set in `.claude/settings.local.json`); block-emission round-trip → T-block-emission-end-to-end (synthetic prose-decision-ask without AUQ produces block JSON via Stop-mode hook invocation); platform smoke → T-platform-smoke (existing pytest suite passes).

## Prior Deliberations

Search performed against `groundtruth.db` deliberations table (per `.claude/rules/deliberation-protocol.md`):

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive (per `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED) | owner_conversation | owner_decision | Source rule for owner-decision surfacing |
| Implicit S321 owner directive (per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED) | owner_conversation | owner_decision | Bounded exception for block emission |
| S328 regex-tightening directive (work_list row 29) | owner_conversation | owner_decision | "tighten the regex to require an interrogative marker or 2nd-person object after `Awaiting`; add a guard that the detector does NOT match against text describing the detector itself" |
| S331 AUQ #1: "Block ISOLATION-018; enforcement first (Recommended)" | owner_conversation | owner_decision | Enforcement priority confirmed |
| S331 AUQ #2: "Full 6-mechanism stack (Recommended)" | owner_conversation | owner_decision | Umbrella scope confirmed |
| S331 AUQ #3: "Autonomous progression (Recommended)" | owner_conversation | owner_decision | Sub-slice A authorized to file under autonomous-progression contract |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice A is approved to file under standard bridge lifecycle |

No prior deliberation rejects the regex-tightening direction or the block re-enable.

## Goal

Sub-slice A delivers three coupled outcomes within a single coherent scope:

1. **Tighten `PROSE_DECISION_PATTERNS`** to reduce false positives on factual status statements while preserving detection of genuine prose decision-asks.
2. **Extend `PROSE_FALSE_POSITIVE_GUARDS`** with two new guard patterns: (a) self-reference suppressor (text describing the detector itself); (b) bridge-metadata context suppressor (text near `Codex GO`/`Codex NO-GO`/`Codex VERIFIED` markers, which are factual bridge-state references rather than decision-asks).
3. **Re-enable block emission** by removing `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` from `.claude/settings.local.json::env`. After this sub-slice VERIFIED, agent prose decision-asks without same-turn AskUserQuestion calls will trigger the bounded-exception block emission, refusing turn-end and forcing the agent to formalize via AUQ.

work_list row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) is closed on Sub-slice A VERIFIED.

## Implementation Plan

### Step 1: Tighten `PROSE_DECISION_PATTERNS`

Current pattern definitions in `.claude/hooks/owner-decision-tracker.py:104-115`:

```python
PROSE_DECISION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("offering_or_choice", re.compile(r"\bwant me to\b[^.?!]*\bor\b[^.?!]*\?", re.IGNORECASE)),
    ("should_i_or", re.compile(r"\bshould I\b[^.?!]*\bor\b[^.?!]*\?", re.IGNORECASE)),
    ("awaiting_input", re.compile(r"\bawaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b", re.IGNORECASE)),
    ("standing_by_for", re.compile(r"\bstanding by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b", re.IGNORECASE)),
    ("your_decision_q", re.compile(r"\b(?:your|owner)\s+(?:decision|choice|input)\b[^.?!]{0,80}\?", re.IGNORECASE)),
)
```

Patterns 1, 2, 5 already require `?` (interrogative marker) and are conservative enough. Patterns 3 and 4 ("awaiting_input", "standing_by_for") match factual status statements; per S328 owner directive these need tightening.

Proposed replacement for patterns 3 and 4:

```python
# Tightened per S328 owner directive: split into interrogative-form and
# 1st-person-active-wait variants. Status-reports without an interrogative
# marker or 1st-person construct are excluded.
("awaiting_input_q", re.compile(
    r"\bawaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?",
    re.IGNORECASE,
)),
("awaiting_input_first_person", re.compile(
    r"\b(?:i am|i'm|we are|we're)\s+awaiting (?:your|owner)\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b",
    re.IGNORECASE,
)),
("standing_by_for_q", re.compile(
    r"\bstanding by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b[^.?!]*\?",
    re.IGNORECASE,
)),
("standing_by_for_first_person", re.compile(
    r"\b(?:i am|i'm|we are|we're)\s+standing by for\b[^.?!]*\b(?:direction|input|answer|decision|approval)\b",
    re.IGNORECASE,
)),
```

Effect on representative S331 false-positive samples:

| Sample text | Old match? | New match? |
|-------------|-----------:|-----------:|
| `"Awaiting your direction."` (factual status) | YES | NO (no `?`, no 1st-person) |
| `"Awaiting owner direction. No stale-entry act"` | YES | NO (no `?`, no 1st-person) |
| `"Awaiting your decision."` (factual status) | YES | NO (no `?`, no 1st-person) |
| `"Awaiting Codex re-review"` (no your/owner) | NO | NO (unchanged) |
| `"Awaiting your direction?"` (interrogative) | YES | YES (matched by `_q` variant) |
| `"I am awaiting your direction on the next slice"` (active wait) | YES | YES (matched by `_first_person` variant) |
| `"Standing by for owner approval?"` (interrogative) | YES | YES |
| `"I'm standing by for your decision"` (active wait) | YES | YES |

### Step 2: Extend `PROSE_FALSE_POSITIVE_GUARDS`

Current guards at `.claude/hooks/owner-decision-tracker.py:117-123`:

```python
PROSE_FALSE_POSITIVE_GUARDS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdecisions are (?:hard|complex|difficult|tricky)\b", re.IGNORECASE),
    re.compile(r"\bin general,?\s+decisions?\b", re.IGNORECASE),
    re.compile(r"\babstract(?:ly)?,?\s+(?:about\s+)?decisions?\b", re.IGNORECASE),
)
```

Add 2 new guards per S328 owner directive:

```python
PROSE_FALSE_POSITIVE_GUARDS: tuple[re.Pattern[str], ...] = (
    # Existing T14 guards (preserved):
    re.compile(r"\bdecisions are (?:hard|complex|difficult|tricky)\b", re.IGNORECASE),
    re.compile(r"\bin general,?\s+decisions?\b", re.IGNORECASE),
    re.compile(r"\babstract(?:ly)?,?\s+(?:about\s+)?decisions?\b", re.IGNORECASE),
    # NEW: self-reference suppressor (S328 directive). Suppresses match
    # when surrounding paragraph mentions detector internals.
    re.compile(
        r"\b(?:PROSE_DECISION_PATTERNS|owner-decision-tracker|decision-tracker|prose pattern|prose-pattern|regex tightening)\b",
        re.IGNORECASE,
    ),
    # NEW: bridge-metadata context suppressor. Bridge-state words
    # (Codex GO, Codex NO-GO, Codex VERIFIED, Codex review) signal
    # factual bridge-thread reporting, not a decision-ask.
    re.compile(
        r"\bCodex (?:GO|NO-GO|VERIFIED|review|`-\d+|F\d|umbrella)\b",
        re.IGNORECASE,
    ),
)
```

The guard logic in the hook applies these regexes against the matched text's surrounding paragraph. If any guard pattern matches the paragraph context, the prose-detection match is suppressed. The existing guard application loop at the hook's match-evaluation site is preserved as-is; only the guard tuple is extended.

### Step 3: Remove env-override suppression

Edit `.claude/settings.local.json` to remove the `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` env override. After removal:

```json
{
  "env": {
    // GTKB_BLOCK_ON_PROSE_DECISION_ASK removed; default '1' active
  },
  "permissions": { ... }
}
```

The hook's `_block_emission_enabled()` function defaults to enabled when the env var is unset. Block emission becomes active for genuine prose decision-asks without same-turn AskUserQuestion calls.

### Step 4: Add test fixtures

Create `groundtruth-kb/tests/fixtures/owner_decision_tracker/regex_negative_fixtures.txt` with the negative-fixture corpus (factual status statements that should NOT match):

```
Awaiting your direction.
Awaiting owner direction. No stale-entry act required.
Awaiting your decision.
Awaiting Codex re-review on -003.
Awaiting CI green on develop.
The PROSE_DECISION_PATTERNS regex catches awaiting your direction phrases when properly tuned.
Codex GO at -004 left awaiting your verdict on the next slice.
Sub-slice F's promotion gate is awaiting owner approval per the umbrella scope.
```

Create `groundtruth-kb/tests/fixtures/owner_decision_tracker/regex_positive_fixtures.txt` with the positive-fixture corpus (genuine decision-asks that SHOULD match):

```
Awaiting your direction?
I am awaiting your direction on which option to pick.
Standing by for owner approval?
I'm standing by for your decision on the deferred items.
Should I file -005 or wait for the umbrella?
Want me to clear pending or defer all of them?
Your decision on the next sub-slice priority?
```

Add `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` with tests:

- `test_negative_fixtures_no_match`: load negative-fixture file, assert `_collect_prose_matches()` returns empty for each line
- `test_positive_fixtures_match`: load positive-fixture file, assert `_collect_prose_matches()` returns ≥1 match per line
- `test_self_reference_guard_suppresses`: synthetic line "I'm awaiting your direction on the regex tightening" — the new guard suppresses despite first-person form
- `test_bridge_metadata_guard_suppresses`: synthetic line "Codex GO at -004 confirms we are awaiting your direction on next steps" — bridge-metadata guard suppresses
- `test_block_emission_enabled_when_env_unset`: assert `_block_emission_enabled()` returns True when `GTKB_BLOCK_ON_PROSE_DECISION_ASK` env var is absent

### Step 5: Commit on develop

Single commit on `develop` branch:

```
gtkb-gov-auq-enforcement-stack Slice A: hook re-enable + regex tightening

Tightens PROSE_DECISION_PATTERNS by splitting awaiting_input and
standing_by_for into interrogative-form (_q) and 1st-person
(_first_person) variants. Status statements without ? or "I am" /
"I'm" / "we are" / "we're" no longer trigger.

Extends PROSE_FALSE_POSITIVE_GUARDS with self-reference suppressor
(detector-describing text) and bridge-metadata context suppressor
(Codex GO/NO-GO/VERIFIED/review markers).

Removes GTKB_BLOCK_ON_PROSE_DECISION_ASK=0 env override from
.claude/settings.local.json. Block emission becomes active for
genuine prose decision-asks without same-turn AskUserQuestion calls.

Test fixtures: regex_negative_fixtures.txt + regex_positive_fixtures.txt
plus test_owner_decision_tracker_regex_tightening.py covering both
fixture corpora plus the 2 new guard patterns.

Closes work_list.md row 29
(GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING).

Refs: bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md
(umbrella Codex GO);
bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-001.md
(this Sub-slice A proposal).
```

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-a" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains Specification Links + spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-out-of-applications-A** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (sub-slice A does not create `applications/` content) | `git diff <Sub-A-baseline>..<Sub-A-VERIFIED-commit> --name-only \| grep "^applications/"` | Empty (no files under `applications/` introduced) |
| **T-regex-negative-fixtures** | regex tightening contract (false-positive reduction) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_negative_fixtures_no_match -v` | PASS — every line in `regex_negative_fixtures.txt` returns empty `_collect_prose_matches()` result |
| **T-regex-positive-fixtures** | regex tightening contract (positive coverage preserved) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_positive_fixtures_match -v` | PASS — every line in `regex_positive_fixtures.txt` returns ≥1 match |
| **T-guard-self-reference** | T14 self-reference guard (per S328) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_self_reference_guard_suppresses -v` | PASS — synthetic detector-describing text suppresses despite matching positive form |
| **T-guard-bridge-metadata** | T14 bridge-metadata guard (per S328) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_bridge_metadata_guard_suppresses -v` | PASS — synthetic bridge-state-mentioning text suppresses |
| **T-env-override-absent** | env override removal | `python -c "import json; c=json.load(open('.claude/settings.local.json')); print('GTKB_BLOCK_ON_PROSE_DECISION_ASK' not in c.get('env', {}))"` | `True` (env var no longer present) |
| **T-block-emission-end-to-end** | block emission round-trip on prose-decision-ask without AUQ | Run hook in Stop mode with synthetic transcript containing prose decision-ask but no AUQ tool_use; capture stdout JSON | Stdout contains `{"decision": "block", "reason": "..."}` JSON; reason includes detected pattern name + excerpt |
| **T-platform-smoke** | GT-KB platform integrity | `python -m pytest groundtruth-kb/tests/ -x --tb=short -q -k "owner_decision or hook or decision_tracker" --timeout=60` | PASS (or pre-existing-known failures only) |
| **T-history-1** | tracked file history preserved (not applicable; this sub-slice does not move tracked files) | (skipped — no file moves) | N-A-skip |
| **T-row29-closure** | work_list row 29 dropped on VERIFIED | After VERIFIED, `grep -c "GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING" memory/work_list.md` | 0 (or row body replaced with closure note pointing at this sub-slice) |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `grep` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct (preflight pass) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct (Codex VERIFIED gate) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-A | Direct |
| Regex tightening contract (false-positive reduction) | T-regex-negative-fixtures | Direct |
| Regex tightening contract (positive coverage preserved) | T-regex-positive-fixtures | Direct |
| T14 guard extension (self-reference, per S328) | T-guard-self-reference | Direct |
| T14 guard extension (bridge metadata, per S328) | T-guard-bridge-metadata | Direct |
| Env override removal | T-env-override-absent | Direct |
| Block emission round-trip | T-block-emission-end-to-end | Direct |
| GT-KB platform integrity | T-platform-smoke | Direct |
| work_list row 29 closure | T-row29-closure | Direct |
| Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | (no new tests; satisfied by REPORT structure + lifecycle-state transition for work_list row 29) | Indirect |

Every required spec has direct or indirect test coverage.

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice A proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Regex changes reviewed for over-correction risk (positive fixtures cover representative genuine decision-asks; negative fixtures cover representative status statements)

VERIFIED when:

- [ ] All 12 tests T-bridge-1 through T-row29-closure PASS with command output captured in post-impl REPORT (T-history-1 skipped as N-A-skip; not applicable to non-mover sub-slice)
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Tightened regex passes negative + positive fixture suites (T-regex-negative-fixtures + T-regex-positive-fixtures)
- [ ] Both new T14 guards pass their tests (T-guard-self-reference + T-guard-bridge-metadata)
- [ ] Env override removed (T-env-override-absent returns True)
- [ ] Block emission verified end-to-end (T-block-emission-end-to-end)
- [ ] GT-KB platform smoke passes (T-platform-smoke)
- [ ] work_list row 29 closed (T-row29-closure)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Tightened regex over-corrects: genuine prose decision-asks fail to match | Medium | High | Positive-fixture suite (T-regex-positive-fixtures) covers representative true-positive forms; Codex review against fixture corpus during GO review |
| Tightened regex under-corrects: factual status statements still match | Medium | Medium | Negative-fixture suite (T-regex-negative-fixtures) covers S331-empirical false positives; can extend in follow-up if new false-positive shapes surface |
| Block emission fires on first turn after VERIFIED, blocking unrelated work | Low | Medium | Bounded-exception design (one block per turn) prevents loop; block JSON returns context allowing the agent to call AUQ on next turn |
| Self-reference guard over-suppresses: legitimate decision-asks mentioning detector terms get suppressed | Low | Low | Self-reference guard is paragraph-scoped; only suppresses when paragraph mentions detector internals AND a positive pattern matches |
| Bridge-metadata guard over-suppresses: agent uses "Codex GO" near a genuine ask | Low | Low | The bridge-metadata guard suppresses only when the bridge-state words appear NEAR the matched pattern; truly different phrasing patterns are unaffected |
| Test fixture file format diverges from hook's parsing | Low | Low | Fixtures are line-per-sample plain text; hook's `_collect_prose_matches()` operates on strings; test loader simply iterates lines |
| Pre-existing pytest failures (per 18.B precedent: scaffold-golden fixture mismatch) interfere | Medium | Low | T-platform-smoke uses focused `-k` filter; pre-existing failures documented as such per 18.B pattern |

Rollback: `git revert` of the single commit reverses regex changes, env-override removal, fixture additions, and test additions atomically. work_list row 29 reopens if revert is desired.

## Open Questions

(All scope decisions resolved via S331 owner AskUserQuestion answers and umbrella -004 GO; no open questions for this sub-slice.)

| ID | Question | Resolution |
|----|----------|------------|
| OQ-A-1 | Tighten patterns 3 + 4 only, or all 5 patterns? | Patterns 1, 2, 5 already require `?` (interrogative); only 3 + 4 need tightening per S328 directive |
| OQ-A-2 | Self-reference guard pattern scope? | Paragraph-scoped; mentions detector internals (`PROSE_DECISION_PATTERNS`, `owner-decision-tracker`, etc.) within ~100 chars of matched text |
| OQ-A-3 | Bridge-metadata guard pattern scope? | Paragraph-scoped; mentions `Codex GO|NO-GO|VERIFIED|review|`-NNN|FN|umbrella` within ~100 chars |

## Owner Decisions / Input

This sub-slice's authorization derives from a chain of owner AskUserQuestion answers in S331 (this session):

1. **Enforcement priority** (umbrella OQ-A) — owner selected: "Block ISOLATION-018; enforcement first (Recommended)"
2. **Umbrella scope** (umbrella OQ-B) — owner selected: "Full 6-mechanism stack (Recommended)"
3. **Sub-slice autonomy** (umbrella OQ-C) — owner selected: "Autonomous progression (Recommended)" — explicitly authorizes filing of this Sub-slice A bridge under standard lifecycle without per-sub-slice owner approval

Plus the prior owner directive in work_list row 29 (S328) that defines the regex-tightening + T14-guard-extension scope.

No additional owner input pending at sub-slice level.

## Out of Scope

- Widening the bounded-exception block-emission scope (still: one block per turn on prose-decision-ask without same-turn AUQ; per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED contract).
- Modifying the bridge-compliance-gate hook (Sub-slice C).
- Modifying Prime Builder rules (Sub-slice B).
- Audit pass over `memory/pending-owner-decisions.md` historical entries (Sub-slice D).
- Implementing the requirements-collection hook (Sub-slice E).
- Adding release-metric doctor checks (Sub-slice F).
- Resolution of pre-existing scaffold-golden fixture mismatch (separate fixture-refresh slice).
- Session-tracker cwd anchoring fix (separate hook-hygiene slice).

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- All changes target files within `E:/GT-KB/.claude/hooks/owner-decision-tracker.py`, `E:/GT-KB/.claude/settings.local.json`, `E:/GT-KB/groundtruth-kb/tests/` (test fixtures + new test file), and `E:/GT-KB/bridge/` (this sub-slice's bridge files).
- No live-dependency paths outside `E:/GT-KB/`.
- Does NOT depend on Agent Red as a live GT-KB artifact.
- Does NOT create new content under `applications/`.
- Per `.claude/rules/project-root-boundary.md`.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1) |
| Umbrella Codex GO | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` |
| Source DELIB (S328 regex-tightening directive) | work_list row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) |
| Existing surfacing impl | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED 2026-04-27 |
| Existing block emission impl | `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED |
| Owner scope confirmations | This S331 conversation: 3 AskUserQuestion answers (priority, scope, autonomy) |
| Empirical false-positive corpus | This S331 conversation: 4 prose-pattern matches accumulated in `memory/pending-owner-decisions.md` (DECISION-0410 through DECISION-0419) |
| Live probes | `grep -nE "PROSE_DECISION_PATTERNS"`, `head` of `.claude/hooks/owner-decision-tracker.py` (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
