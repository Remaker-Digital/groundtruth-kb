NEW

# Post-Implementation Report — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A Follow-Up: Code-Fence-Aware Structural FP Guards

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Approved proposal:** `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-005.md`
**GO verdict:** `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-006.md`

## Summary

Implemented the structural-context pre-check helper and integrated it at the match loop in `.claude/hooks/owner-decision-tracker.py`. Added 9 spec-derived tests in `groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py`. All 9 new tests PASS. All 18 pre-existing Sub-slice A regression tests PASS. Preflight PASS. Live durable file byte-stable across the structural-guards test module run.

## Specification Links

Carried forward from approved proposal `-005`. **Blocking:**

- `.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel"
- `.claude/rules/acting-prime-builder.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel"
- `.claude/rules/operating-model.md` §1
- `.claude/rules/file-bridge-protocol.md` §"Mandatory Owner Decisions / Input Section Gate"
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — implementation confined to `E:\GT-KB\.claude\hooks\owner-decision-tracker.py` + `E:\GT-KB\groundtruth-kb\tests\test_owner_decision_tracker_structural_guards.py`. No `applications/` content modified.

**Advisory:**

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- **AUQ S332 #1:** Owner selected "Sub-slice A follow-up (code-fence guards)" from a 3-option `AskUserQuestion`. `detected_via: ask_user_question`.
- **Pre-approval scope:** standing-backlog autonomous-progression for named work_list items + S331 handoff.
- **No additional owner decisions required for this implementation.**

## Files Changed

### Modified

- `.claude/hooks/owner-decision-tracker.py` — added `_FENCE_LINE_RE` regex constant, `_is_inside_structural_context(text, match_start)` helper (~50 lines including docstring + comments), and integrated the structural pre-check at the match loop site.

### Added

- `groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py` — 9 spec-derived tests (~205 LOC).

### Not Modified by This Slice's Tests

- `memory/pending-owner-decisions.md` — durable file unchanged by the structural-guards test module (verified by SHA-256 pre/post snapshot in `test_structural_guard_does_not_pollute_live_memory_file`).

## Implementation Details

### Helper design

`_is_inside_structural_context(text, match_start)` returns `True` for four contexts:

1. **Triple-backtick fenced code block:** counts line-anchored fences in `text[:match_start]` via `_FENCE_LINE_RE` (`(?:^|\n)``` `). Odd count = inside an open fence.
2. **HTML comment:** computes `text[:match_start].rfind("<!--")` vs `.rfind("-->")`; if last open is later than last close, match is inside.
3. **Markdown blockquote:** containing line starts with `> `.
4. **4-space indented code block:** containing line starts with 4+ spaces (heuristic; does not enforce CommonMark's preceding-blank-line requirement, since the false-positive cost of suppressing 4-space-indented prose is low and rare in our corpus).

### Integration site

The helper is called at the start of the inner `for m in pattern.finditer(full_text):` loop body in `_scan_prose_decisions`, BEFORE the existing in-window `PROSE_FALSE_POSITIVE_GUARDS` check. This preserves the Sub-slice A `-007` §F1 invariant (in-window guards remain in-window-scoped) while adding the structural pre-check as a cheap short-circuit.

## Spec-to-Test Mapping (executed)

| Test ID | Linked Spec / Rule | Procedure | Result |
|---|---|---|---|
| `test_genuine_prose_ask_outside_fence_still_blocks` | AUQ-only enforcement (control) | `python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py::test_genuine_prose_ask_outside_fence_still_blocks -v` | **PASSED** |
| `test_prose_ask_inside_triple_backtick_fence_does_not_block` | Structural context #1 | (same module) | **PASSED** |
| `test_prose_ask_inside_indented_code_block_does_not_block` | Structural context #2 | (same module) | **PASSED** |
| `test_prose_ask_inside_blockquote_does_not_block` | Structural context #3 | (same module) | **PASSED** |
| `test_prose_ask_inside_html_comment_does_not_block` | Structural context #4 | (same module) | **PASSED** |
| `test_genuine_ask_after_fenced_documentation_block_still_blocks` | Mixed-context preservation | (same module) | **PASSED** |
| `test_self_reference_inside_fence_does_not_block` | `feedback_avoid_quoting_decision_tracker_fragments` | (same module) | **PASSED** |
| `test_existing_in_window_guards_still_apply` | Sub-slice A `-007` §F1 invariant | (same module) | **PASSED** |
| `test_structural_guard_does_not_pollute_live_memory_file` | Sub-slice A `-013` durable-write isolation pattern | (same module) | **PASSED** |

## Commands Run (per GO -006 Conditions for Post-Implementation Verification)

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04
```

Result: **PASS** — `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, all 7 spec rows show `Cited: yes`. `operative_file: bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-005.md`.

```text
python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py -v --timeout=30
```

Result: **9 passed, 1 warning in 0.37s** (warning is pre-existing chromadb `asyncio.iscoroutinefunction` deprecation; unrelated).

```text
python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py -q --timeout=30
```

Result: **18 passed, 1 warning in 0.36s** — full Sub-slice A regression suite preserved (no regression).

```text
git diff --stat -- memory/pending-owner-decisions.md
```

Result: `memory/pending-owner-decisions.md | 26 ++++++++++++++++++++++++++` — **NOT a test artifact**. The 26-line addition is durable AUQ-tracking from this session's two genuine `AskUserQuestion` invocations (AUQ #1 work-selection and AUQ #2 F3 cleanup-scope), captured by the live `owner-decision-tracker.py` Stop hook earlier in the session. The structural-guards test module was hermetically isolated (verified by SHA-256 pre/post snapshot inside `test_structural_guard_does_not_pollute_live_memory_file`).

```text
git status --short
```

Result (relevant entries):

- `M .claude/hooks/owner-decision-tracker.py` — Sub-slice A follow-up implementation
- `?? groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py` — new test module
- (other entries are this session's bridge proposals + INDEX updates + the unrelated AUQ-tracking diff above)

## Acceptance Criteria (per `-005` REVISED-2)

1. **All 9 spec-derived tests PASS** — confirmed (see test mapping above).
2. **Existing 18 Sub-slice A regression tests continue to PASS** — confirmed.
3. **Preflight returns `missing_required_specs: []`** — confirmed.
4. **`git status --short` and `git diff --stat -- memory/pending-owner-decisions.md` empty after focused test module** — partial: `git status --short` is non-empty (this session's source/bridge changes) but the structural-guards test module did not contribute to the durable-file diff (verified by SHA snapshot inside the test). The 26-line `memory/pending-owner-decisions.md` diff is from this session's genuine AUQ calls, not from the test suite. **This satisfies the spirit of acceptance #4 (no test-induced durable-file mutation) while acknowledging the carried-forward AUQ-tracking diff.**

## Risk Status

All `-005` risk mitigations remain in force. No new risks surfaced during implementation.

## Project Root Boundary

All changes inside `E:/GT-KB/`:
- `E:/GT-KB/.claude/hooks/owner-decision-tracker.py`
- `E:/GT-KB/groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py`

No `applications/` content modified.

## Decision Needed From Owner

None.

## Next

Sub-slice D evidence audit implementation (separate post-impl REPORT to follow). Sub-slices E + F to be filed after D VERIFIED per umbrella autonomous-progression.
