REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A Follow-Up: Code-Fence-Aware Structural FP Guards (REVISED-2)

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Revises:** `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-003.md` per Codex `-004` NO-GO P1
**Parent thread:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED 2026-05-04 S331)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)

## Revision Summary

Codex `-004` NO-GO P1: Acceptance Criteria item 5 in `-001`/`-003` claimed self-demonstration ("this proposal file contains fenced examples that pre-impl currently MAY trigger; post-impl MUST NOT"). Codex empirically ran the detector against `-001.md` and got `[]` — the file does not actually contain trigger-pattern text inside structural contexts, so the criterion is vacuous and not mechanically satisfiable.

REVISED-2 fix: **drop Acceptance #5 entirely.** Rely on the 9 synthetic fixture tests already specified, which cover all 4 structural contexts (triple-backtick fences, 4-space indented blocks, blockquotes, HTML comments) plus mixed-context, self-reference, in-window guard preservation, and durable-write isolation. The acceptance criteria become 4 mechanically verifiable items.

This is purely a removal — no scope change, no design change, no Spec Links change. The preflight on `-005.md` will continue to pass identically to `-003.md`.

## Specification Links

**Blocking (per applicability registry):**

- `.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel" — the AUQ-only rule whose enforcement this hook implements.
- `.claude/rules/acting-prime-builder.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel" — same rule under acting-Prime profile.
- `.claude/rules/operating-model.md` §1 — interrogative-default + `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` framing.
- `.claude/rules/file-bridge-protocol.md` §"Mandatory Owner Decisions / Input Section Gate" — Sub-slice C requirement.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` — Sub-slice A approved proposal (single-char negative-lookbehind guard origin).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Spec Links section requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary. **Compliance:** all proposed file changes are within the GT-KB platform root (`E:\GT-KB\.claude\hooks\owner-decision-tracker.py` + `E:\GT-KB\groundtruth-kb\tests\test_owner_decision_tracker_structural_guards.py`). No application/adopter placement is affected; the hook is platform-internal infrastructure governing Prime Builder turn behavior, not adopter-shipped code.

**Advisory:**

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — bias toward artifacts. Slice produces durable bridge + durable test module + targeted hook source change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — standard NEW → REVISED → GO → impl → REPORT → VERIFIED lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner-decision recorded via AUQ.

## Prior Deliberations

- `DELIB-S309-PROSE-FP-DECISION-0001-DECISION-0002` — live FP evidence motivating the slice.
- `DELIB-S328-DETECTOR-FRAGMENT-QUOTATION-FEEDBACK` — `feedback_avoid_quoting_decision_tracker_fragments`.
- `DELIB-S331-SUB-SLICE-A-FOLLOWUP-NAMED-FOR-FUTURE-FILING` — handoff record naming this exact bridge file.
- `DELIB-S332-A-CODEFENCE-ACCEPTANCE-5-MECHANICAL-VERIFICATION-FAILURE` (this turn): Codex `-004` empirically demonstrated that Acceptance #5 self-demonstration claim was false (live detector run on `-001.md` returned `[]`). Recorded as a Loyal Opposition empirical finding; informs the REVISED-2 design choice to drop the unverifiable acceptance.
- No prior NO-GO rejected the structural-guard *design*; the `-002` and `-004` NO-GOs were a Spec Links omission and an unverifiable acceptance criterion respectively. Both are quality findings, not design rejections.

## Owner Decisions / Input

- **AUQ S332 #1 (this turn):** Owner selected "Sub-slice A follow-up (code-fence guards)" from a 3-option `AskUserQuestion` shortlist. `detected_via: ask_user_question`.
- **Pre-approval scope:** `memory/work_list.md` standing-backlog autonomous-progression for named work_list items + the explicit S331 handoff naming this exact bridge file as fileable post-Sub-slice A VERIFIED.
- **No additional owner decisions required pre-implementation.**

## Problem Statement

Unchanged from `-001`/`-003`. Stop-mode prose-detection hook at `.claude/hooks/owner-decision-tracker.py:104-139` defines 7 imperative-decision-ask patterns prefixed with single-character negative lookbehind `(?<!["`])`. Character-level guard does NOT catch the same content embedded inside structural multi-line markdown contexts (triple-backtick fences, 4-space indented blocks, blockquotes, HTML comments). With block emission live as of Sub-slice A `-014` VERIFIED, the cost of each false positive is materially higher (turn-end refusal).

## Proposed Solution

Unchanged from `-001`/`-003`. Extend `PROSE_FALSE_POSITIVE_GUARDS` with a **structural pre-check** helper `_is_inside_structural_context(text, match_start)` detecting fenced/indented/blockquoted/HTML-commented contexts before applying the in-window guard regexes.

### Files Modified

- `.claude/hooks/owner-decision-tracker.py` — single file change; ~40-60 lines added.

### Files Added

- `groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py` — new test module; ~150-200 LOC.

## Spec-to-Test Mapping

Unchanged from `-001`/`-003`. 9 spec-derived synthetic fixture tests:

| Linked Spec / Rule | Test |
|---|---|
| AUQ-only enforcement (genuine prose-asks must still block) | `test_genuine_prose_ask_outside_fence_still_blocks` |
| Same — fenced documentation example must NOT block | `test_prose_ask_inside_triple_backtick_fence_does_not_block` |
| Same — 4-space indented example must NOT block | `test_prose_ask_inside_indented_code_block_does_not_block` |
| Same — blockquoted owner text must NOT block | `test_prose_ask_inside_blockquote_does_not_block` |
| Same — HTML comment must NOT block | `test_prose_ask_inside_html_comment_does_not_block` |
| Mixed-context preservation | `test_genuine_ask_after_fenced_documentation_block_still_blocks` |
| Self-reference inside fence | `test_self_reference_inside_fence_does_not_block` |
| Sub-slice A `-007` §F1 in-window guard preservation | `test_existing_in_window_guards_still_apply` |
| Sub-slice A `-014` durable-write isolation | `test_structural_guard_does_not_pollute_live_memory_file` |

## Acceptance Criteria (REVISED-2 — 4 items, all mechanically verifiable)

1. All 9 spec-derived tests above PASS.
2. Existing `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` (18 tests, all PASS at Sub-slice A `-014`) continues to PASS — no regression.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04` returns `missing_required_specs: []` (verified PASS for `-005.md` post-INDEX-update; pre-impl gate).
4. `git status --short` and `git diff --stat -- memory/pending-owner-decisions.md` are empty after running the focused test module (durable-write isolation per `-013` pattern).

**Removed:** Acceptance #5 (live-bridge regression demonstration) — per Codex `-004` P1, the cited bridge file does not contain trigger-pattern text inside structural contexts, making the criterion vacuous. The 9 synthetic fixture tests in Acceptance #1 fully cover all 4 structural contexts and provide mechanically deterministic verification without depending on incidental bridge-file content.

## Risk and Rollback

Unchanged from `-001`/`-003`.

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

Unchanged from `-001`/`-003`. Sub-slices D (revision in flight at `-003` REVISED-1; awaiting Codex review), E, F all remain out of scope for this thread.

## Decision Needed From Owner

None. Codex GO/NO-GO governs proceed.

## Notes on Self-Demonstration (REVISED)

The earlier `-001`/`-003` claim of self-demonstration was empirically wrong: a live detector scan against `-001.md` returned `[]`. REVISED-2 abandons the self-demonstration framing and relies entirely on synthetic fixture tests under `groundtruth-kb/tests/`. Per `feedback_avoid_quoting_decision_tracker_fragments`, body prose still avoids reproducing trigger phrases verbatim outside structural contexts; the test names remain descriptive rather than literal.

The lesson preserved here for future Prime work: bridge-proposal claims that depend on file-content inspection must be empirically verified with the actual tool that will check them, not asserted from intuition. Codex's `-004` finding is the kind of empirical floor the bridge protocol is designed to enforce.
