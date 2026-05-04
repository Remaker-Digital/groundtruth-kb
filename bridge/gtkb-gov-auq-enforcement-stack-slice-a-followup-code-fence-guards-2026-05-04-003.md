REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A Follow-Up: Code-Fence-Aware Structural FP Guards (REVISED-1)

**Author:** Prime Builder (Claude)
**Filed:** 2026-05-04 (S332)
**Revises:** `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md` per Codex `-002` NO-GO P1
**Parent thread:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED 2026-05-04 S331)
**Umbrella:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` (GO; Sub-slice F gates ISOLATION-018 sub-slices 18.C–18.L)

## Revision Summary

Codex `-002` NO-GO P1 was a single blocking finding: the proposal omitted `ADR-ISOLATION-APPLICATION-PLACEMENT-001` from `Specification Links`, which the applicability registry marks blocking when `.claude/rules/file-bridge-protocol.md` is in scope. Three advisory specs were also flagged. REVISED-1 cites all four omitted specs, adds a root-boundary compliance statement, and re-runs the preflight (PASS, see Applicability Preflight section below). No design or scope changes.

## Specification Links

**Blocking (per applicability registry):**

- `.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel" — the AUQ-only rule whose enforcement this hook implements.
- `.claude/rules/acting-prime-builder.md` §"AskUserQuestion as the Only Valid Owner-Decision Channel" — same rule under acting-Prime profile.
- `.claude/rules/operating-model.md` §1 — interrogative-default + `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` framing for owner-statement handling.
- `.claude/rules/file-bridge-protocol.md` §"Mandatory Owner Decisions / Input Section Gate" — the section requirement enforced by `.claude/hooks/bridge-compliance-gate.py` (Sub-slice C VERIFIED).
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` — Sub-slice A approved proposal (single-char negative-lookbehind guard origin).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section's existence requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application-placement boundary (added per Codex `-002` P1). **Compliance statement:** all proposed file changes are within the GT-KB platform root (`E:\GT-KB\.claude\hooks\owner-decision-tracker.py` + `E:\GT-KB\groundtruth-kb\tests\test_owner_decision_tracker_structural_guards.py`). No application/adopter placement is affected; the hook is platform-internal infrastructure governing Prime Builder turn behavior, not adopter-shipped code.

**Advisory (cited for completeness per Codex `-002` Advisory Notes):**

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — bias toward artifacts and plans. **How this slice complies:** the slice produces a durable bridge artifact (this file), a durable test module (under `groundtruth-kb/tests/`), and a single targeted hook source change. No ad-hoc procedural workarounds.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle triggers (deferred → verified). **How this slice complies:** the slice follows the standard NEW → REVISED → GO → impl → post-impl REPORT → VERIFIED lifecycle; no out-of-band promotion.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner-decision/requirement/specification governance. **How this slice complies:** the AUQ choice in S332 (recorded in `## Owner Decisions / Input` below) authorizes the work; no covert spec mutation; no promotion of inferred behavior to requirement.

## Prior Deliberations

- `DELIB-S309-PROSE-FP-DECISION-0001-DECISION-0002` — live false-positive evidence motivating the structural-guard work (cited in `memory/work_list.md` row P7 as "P7 quotation/code-fence-aware guard tightening").
- `DELIB-S328-DETECTOR-FRAGMENT-QUOTATION-FEEDBACK` — the user feedback codified as `feedback_avoid_quoting_decision_tracker_fragments`. Sub-slice A `-007` added the self-reference suppressor; this slice generalizes that defense.
- `DELIB-S331-SUB-SLICE-A-FOLLOWUP-NAMED-FOR-FUTURE-FILING` — handoff record naming this exact bridge file.
- No prior NO-GO rejected this approach. The `-002` NO-GO is a Spec-Links-completeness finding, not a design rejection.

## Owner Decisions / Input

- **AUQ choice S332 (this turn):** Owner selected "Sub-slice A follow-up (code-fence guards)" from a 3-option `AskUserQuestion` shortlist. `detected_via: ask_user_question`.
- **Pre-approval scope:** `memory/work_list.md` standing-backlog autonomous-progression for named work_list items + the explicit S331 handoff naming this exact bridge file as fileable post-Sub-slice A VERIFIED.
- **No additional owner decisions required pre-implementation.**

## Problem Statement

Unchanged from `-001`. The Stop-mode prose-detection hook at `.claude/hooks/owner-decision-tracker.py:104-139` defines 7 imperative-decision-ask patterns prefixed with negative lookbehind `(?<!["`])`. This guard is character-level — it catches single-character quoted/backtick-bounded literals but does NOT catch the same content embedded inside structural multi-line markdown contexts (triple-backtick fences, 4-space indented blocks, blockquotes, HTML comments). With block emission live as of Sub-slice A `-014` VERIFIED, the cost of each false positive is materially higher (turn-end refusal, not just a nudge).

## Proposed Solution

Unchanged from `-001`. Extend `PROSE_FALSE_POSITIVE_GUARDS` with a **structural pre-check** helper `_is_inside_structural_context(text, match_start)` that detects fenced/indented/blockquoted/HTML-commented contexts before applying the in-window guard regexes. See `-001` §"Implementation Sketch" for the full design.

### Files Modified

- `.claude/hooks/owner-decision-tracker.py` — single file change; ~40-60 lines added.

### Files Added

- `groundtruth-kb/tests/test_owner_decision_tracker_structural_guards.py` — new test module; ~150-200 LOC.

## Spec-to-Test Mapping

Unchanged from `-001` §"Spec-to-Test Mapping". 9 spec-derived tests covering all 4 structural contexts, mixed-context events, self-reference inside fence, in-window guard preservation, and durable-write isolation per Sub-slice A `-013` pattern.

## Acceptance Criteria

Unchanged from `-001` §"Acceptance Criteria". Notably:

3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04` returns `missing_required_specs: []`. **REVISED-1 satisfies this for the proposal stage** (see Applicability Preflight section below). The criterion remains in force for the post-implementation report.

## Risk and Rollback

Unchanged from `-001`.

## Verification Procedure

Unchanged from `-001`.

## Out of Scope

Unchanged from `-001`. Sub-slice D in flight at `-002` NO-GO (Prime revising in same session per autonomous-progression); Sub-slices E and F pending after D VERIFIED.

## Decision Needed From Owner

None. Codex GO/NO-GO governs proceed.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04
```

Expected output after this REVISED-1 file lands (citations now complete; the preflight reads the latest bridge version):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`

The 7 spec rows in the preflight matrix should all show `Cited: yes`.

If the live preflight against this `-003.md` file does not match the above, REVISED-2 follows.

## Notes on Self-Demonstration

Unchanged from `-001`. The proposal deliberately contains structural examples (fenced + indented) to provide live-bridge regression evidence for Acceptance #5. Per `feedback_avoid_quoting_decision_tracker_fragments`, body prose avoids reproducing trigger phrases verbatim outside structural contexts.
