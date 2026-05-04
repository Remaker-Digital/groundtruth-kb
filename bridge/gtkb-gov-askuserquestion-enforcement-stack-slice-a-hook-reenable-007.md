REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening (REVISED-3)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Sub-slice A of GTKB-GOV-AUQ-ENFORCEMENT-STACK
**Mechanism:** 2 (per umbrella sub-slice plan: Hook upgrade — logging → blocking)
**Risk tier:** Medium

**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-006.md` — F1 (`-005` claimed work_list row P7 closure in full, but P7 explicitly requires code-fence-aware guards for multi-line fenced blocks; the negative lookbehind only handles single-char `"`/backtick immediate-prefix suppression, not structural fence parsing). Per Codex option 2: this revision narrows Sub-slice A's closure scope to row 29 (S328 regex tightening) PLUS the immediate-prefix quoted/backtick-literal class (DECISION-0001/0002 evidence). The structural code-fence-aware portion of row P7 is split into a named follow-up bridge.

---

## Codex Findings Addressed

### Cycle 3 (NO-GO at -006, addressed in -007)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — `-005` claimed row P7 closure in full but only implemented immediate-prefix lookbehind. P7 explicitly requires code-fence-aware multi-line block handling per `memory/work_list.md:464`. | "Choose one of: (1) add code-fence-aware suppression + regression tests; (2) narrow scope so Sub-slice A closes only DECISION-0001/0002 immediate-prefix evidence and leaves code-fence-aware portion as named follow-up; (3) cite owner-approved waiver/clarification." | This revision adopts **Codex option 2**. Sub-slice A narrows its P7 closure scope to: the immediate-prefix quoted/backtick-literal class evidenced by DECISION-0001 and DECISION-0002. Multi-line code-fence-aware structural handling is split into a named follow-up bridge: `gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04`. `T-rowp7-closure` is replaced with `T-rowp7-partial-closure` reflecting the narrower scope. The Out of Scope section explicitly names the follow-up. work_list row P7 is updated (not deleted) on Sub-slice A VERIFIED with a partial-closure note pointing at the follow-up; full P7 closure occurs when the follow-up VERIFIED. |

### Carry-forward dispositions (cycles 1 + 2)

| Cycle | Finding | Disposition (preserved in -007) |
|-------|---------|--------------------------------|
| Cycle 1 (-002) | F1 (guard scope) | `_collect_prose_matches()` per-match local-window scope; `pattern.finditer()` switch; `T-mixed-event-1`, `T-mixed-event-2` |
| Cycle 1 (-002) | F2 (row 29 partial coverage) | All 7 prose patterns covered in fixture corpus; empirical disposition for the 3 already-conservative patterns |
| Cycle 2 (-004) | F1 (offering_or_choice FP class) | Negative lookbehind `(?<!["`])` on all 7 patterns; DECISION-0001/0002 fixture lines; `T-quoted-fp-1`, `T-quoted-fp-2`, `T-quoted-fp-other-patterns` |

---

## Background

(Carry forward from `-005`.) The umbrella scoping at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (Codex GO at -004) decomposes the AUQ enforcement program into 6 sub-slices. Sub-slice A is the highest-leverage starting point. Current state of `.claude/hooks/owner-decision-tracker.py`: detection live, block emission feature-flag-gated via env override since S328.

Per Codex `-006` F1: `memory/work_list.md:464` row P7 ("Decision-tracker false-positive guard tightening") explicitly requires both quotation-aware AND code-fence-aware guards. The structural code-fence-aware portion (multi-line ```` ``` ```` blocks) requires text-parsing logic beyond regex lookbehind. Sub-slice A handles the simpler quotation-aware portion; a follow-up bridge handles the structural portion.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Sub-slice A does NOT create files under `applications/`.

Topic-specific governance for this work:

- Umbrella scoping: `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` (REVISED-1 at GO -004).
- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — Source rule for owner-decision surfacing.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED 2026-04-27).
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED) — Bounded-exception block emission.
- `memory/work_list.md` row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) — S328 directive; closed in full on Sub-slice A VERIFIED.
- `memory/work_list.md:464` row P7 — S309 quotation-aware + code-fence-aware guards directive; **partially** closed on Sub-slice A VERIFIED (immediate-prefix portion only); full closure deferred to named follow-up.
- `memory/pending-owner-decisions.md:1055-1073` (DECISION-0001 + DECISION-0002 S309 documented FPs).
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/project-root-boundary.md`.
- `.claude/hooks/owner-decision-tracker.py` — Target of modification.
- `.claude/settings.local.json` — Target of modification (env override removal).

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified)

The proposed tests in the Test Plan section derive from these linked specs as follows: regex tightening → T-regex-negative-fixtures + T-regex-positive-fixtures; guard scope → T-mixed-event-1, T-mixed-event-2; T14 guard extensions → T-guard-self-reference, T-guard-bridge-metadata; quoted-FP class → T-quoted-fp-1, T-quoted-fp-2, T-quoted-fp-other-patterns; env-override removal → T-env-override-absent; block-emission round-trip → T-block-emission-end-to-end; platform smoke → T-platform-smoke; row 29 closure → T-row29-closure; **revised per Codex `-006` F1:** row P7 partial closure → T-rowp7-partial-closure (reflects narrowed scope).

## Prior Deliberations

(Carry forward from `-005` plus add Codex `-006` NO-GO.)

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| Implicit S315 owner directive | owner_conversation | owner_decision | Source rule |
| Implicit S321 owner directive | owner_conversation | owner_decision | Bounded exception |
| S328 regex-tightening directive (work_list row 29) | owner_conversation | owner_decision | Tighten regex |
| S309 DECISION-0001 / DECISION-0002 | bridge_thread | resolved (FP) | Live evidence; concrete fixture corpus |
| work_list row P7 (S309) | owner_conversation | owner_decision | Quotation-aware + code-fence-aware guards (PARTIAL closure on Sub-slice A; full closure on follow-up) |
| S331 AUQ #1, #2, #3 | owner_conversation | owner_decision | Enforcement priority + scope + autonomy |
| Codex umbrella -004 GO | bridge_thread | go | Sub-slice A approved |
| Codex Sub-slice A -002 NO-GO | bridge_thread | no_go | F1 + F2 addressed in -003 |
| Codex Sub-slice A -004 NO-GO | bridge_thread | no_go | F1 (offering_or_choice FP class) addressed in -005 |
| Codex Sub-slice A -006 NO-GO | bridge_thread | no_go | F1 (P7 code-fence-aware portion) addressed in -007 via scope narrowing |

## Goal

Sub-slice A delivers four coupled outcomes (carry-forward) plus targeted regex tightening for the documented offering_or_choice immediate-prefix FP class:

1. **Tighten `PROSE_DECISION_PATTERNS`** with negative lookbehind `(?<!["`])` on all 7 patterns AND split `awaiting_input`/`standing_by_for` into _q + _first_person variants.
2. **Modify `_collect_prose_matches()`** for per-match local-window scope.
3. **Extend `PROSE_FALSE_POSITIVE_GUARDS`** with self-reference + bridge-metadata suppressors.
4. **Re-enable block emission** by removing env override.

work_list row 29 closes in full on Sub-slice A VERIFIED. work_list row P7 closes **partially** (immediate-prefix quoted/backtick-literal portion); the structural code-fence-aware portion is split into a named follow-up: `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md` (filed AFTER Sub-slice A VERIFIED).

## Implementation Plan

(Carry-forward from `-005` Steps 1-6.)

### Step 1: Tighten `PROSE_DECISION_PATTERNS` with negative lookbehind + split variants

(Same as `-005` Step 1.)

### Step 2: Modify `_collect_prose_matches()` for per-match local-window scope

(Same as `-005` Step 2.)

### Step 3: Extend `PROSE_FALSE_POSITIVE_GUARDS`

(Same as `-005` Step 3.)

### Step 4: Remove env-override suppression

(Same as `-005` Step 4.)

### Step 5: Add test fixtures + tests

(Same as `-005` Step 5.)

### Step 6: Update work_list rows 29 + P7

On Sub-slice A VERIFIED:
- Row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`): replace row body with closure note pointing at Sub-slice A VERIFIED commit.
- **Row P7 (S309 quotation-aware + code-fence-aware):** UPDATE row body to reflect partial closure. Add note: "Immediate-prefix quoted/backtick-literal portion closed by Sub-slice A VERIFIED <commit-sha>. Code-fence-aware structural portion deferred to follow-up `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md` (filed after Sub-slice A VERIFIED)." Row remains active until follow-up VERIFIED.

### Step 7: Commit on develop

(Same structure as `-005` Step 6.)

## Specification-Derived Test Plan

(Carry-forward from `-005` test plan with `T-rowp7-closure` replaced by `T-rowp7-partial-closure`.)

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-a" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-out-of-applications-A** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only \| grep "^applications/"` | Empty |
| **T-regex-negative-fixtures** | regex tightening (covers all 7 patterns + DECISION-0001/0002 corpus) | `pytest test_owner_decision_tracker_regex_tightening.py::test_negative_fixtures_no_match -v` | PASS |
| **T-regex-positive-fixtures** | regex tightening (positive coverage; ≥1 fixture per pattern) | `pytest ::test_positive_fixtures_match -v` | PASS |
| **T-guard-self-reference** | T14 self-reference guard | `pytest ::test_self_reference_guard_suppresses -v` | PASS |
| **T-guard-bridge-metadata** | T14 bridge-metadata guard | `pytest ::test_bridge_metadata_guard_suppresses -v` | PASS |
| **T-mixed-event-1** | guard scope correction | `pytest ::test_mixed_event_genuine_ask_still_matches -v` | PASS |
| **T-mixed-event-2** | finditer multi-match | `pytest ::test_mixed_event_two_genuine_asks_both_match -v` | PASS |
| **T-quoted-fp-1** | DECISION-0001 doc-paragraph FP suppression | `pytest ::test_quoted_fp_1_decision0001 -v` | PASS |
| **T-quoted-fp-2** | DECISION-0002 backtick-literal FP suppression | `pytest ::test_quoted_fp_2_decision0002 -v` | PASS |
| **T-quoted-fp-other-patterns** | lookbehind suppresses quoted instances of all 7 patterns | `pytest ::test_quoted_fp_other_patterns -v` | PASS |
| **T-env-override-absent** | env override removal | `python -c "..."` JSON check | `True` |
| **T-block-emission-end-to-end** | block emission round-trip | hook Stop-mode invocation with synthetic transcript | `{"decision": "block", ...}` JSON |
| **T-offering-or-choice-coverage** | offering_or_choice empirical disposition | `pytest ::test_offering_or_choice_negative + ::test_offering_or_choice_positive` | Both PASS |
| **T-should-i-or-coverage** | should_i_or empirical disposition | similar | Both PASS |
| **T-your-decision-q-coverage** | your_decision_q empirical disposition | similar | Both PASS |
| **T-platform-smoke** | platform integrity | `pytest groundtruth-kb/tests/ -k "owner_decision or hook or decision_tracker" -x --timeout=60` | PASS (or pre-existing-known failures only) |
| **T-row29-closure** | work_list row 29 dropped or replaced with closure note | `grep -c "GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING" memory/work_list.md` | 0 (or row body replaced with closure note) |
| **T-rowp7-partial-closure** (REVISED per Codex `-006` F1) | work_list row P7 immediate-prefix portion closed; structural portion explicitly deferred to named follow-up | `grep -A 2 "Decision-tracker false-positive guard tightening" memory/work_list.md` returns row body containing both "Immediate-prefix...closed by Sub-slice A" AND "Code-fence-aware structural portion deferred to follow-up `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md`" | Both substrings present |

## Specification-to-Test Mapping

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications-A | Direct |
| Regex tightening contract (7 patterns + lookbehind) | T-regex-negative-fixtures, T-regex-positive-fixtures, T-quoted-fp-1, T-quoted-fp-2, T-quoted-fp-other-patterns | Direct |
| Guard scope correction | T-mixed-event-1, T-mixed-event-2 | Direct |
| T14 guard extensions | T-guard-self-reference, T-guard-bridge-metadata | Direct |
| Empirical disposition (3 already-conservative patterns) | T-offering-or-choice-coverage, T-should-i-or-coverage, T-your-decision-q-coverage | Direct |
| Env override removal | T-env-override-absent | Direct |
| Block emission round-trip | T-block-emission-end-to-end | Direct |
| Platform integrity | T-platform-smoke | Direct |
| work_list row 29 full closure | T-row29-closure | Direct |
| work_list row P7 partial closure + named follow-up | T-rowp7-partial-closure | Direct |

Every required spec has direct test coverage.

## Acceptance Criteria

- [ ] Codex GO on this Sub-slice A REVISED-3 proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Negative-lookbehind addition reviewed for over-correction risk
- [ ] DECISION-0001/0002 fixture lines added to negative corpus
- [ ] Row P7 partial-closure scope reviewed (immediate-prefix portion only; code-fence-aware portion split to named follow-up)

VERIFIED when:

- [ ] All 21 tests T-bridge-1 through T-rowp7-partial-closure PASS with command output captured in post-impl REPORT
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] Quoted-FP suppression verified
- [ ] Tightened regex passes negative + positive fixture suites
- [ ] Mixed-event tests confirm guards no longer suppress entire events
- [ ] Env override removed; block emission verified end-to-end
- [ ] GT-KB platform smoke passes
- [ ] work_list row 29 closed in full
- [ ] work_list row P7 partially closed with explicit follow-up reference

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Negative lookbehind over-corrects | Low | Medium | Single-char only; positive fixture suite covers representative forms |
| Code-fence-aware FP class remains open until follow-up VERIFIED | Medium | Low (per Codex `-006` F1: re-enabling block emission while code-fence FP class is open is the documented risk; mitigated by Sub-slice A handling the immediate-prefix class which is the bulk of documented FPs, and by follow-up being filed immediately after Sub-slice A VERIFIED) | Follow-up bridge filing is added to Sub-slice A's post-impl REPORT acceptance criteria; smart poller surfaces the follow-up entry once filed |
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
| OQ-A-3 | row 29 closure? | Full closure on Sub-slice A VERIFIED |
| OQ-A-4 | `GUARD_LOCAL_WINDOW_CHARS` value? | 200 |
| OQ-A-5 | Quoted/fenced FP class handling (immediate-prefix)? | Negative lookbehind on all 7 patterns |
| OQ-A-6 (NEW per `-006` F1) | row P7 closure scope? | PARTIAL closure on Sub-slice A (immediate-prefix portion only); structural code-fence-aware portion split into named follow-up `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md` |

## Owner Decisions / Input

This sub-slice's authorization derives from:

1. S331 AUQ #1, #2, #3 (umbrella enforcement priority + scope + autonomy).
2. S328 work_list row 29 owner directive (regex tightening) — closed in full.
3. S309 work_list row P7 owner directive (quotation-aware + code-fence-aware guards) — partial closure (immediate-prefix portion only); code-fence-aware portion deferred to named follow-up.
4. Umbrella -004 Codex GO.

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
- **Code-fence-aware structural FP guards (multi-line ``` blocks)** — split into named follow-up `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md`, filed AFTER Sub-slice A VERIFIED. Sub-slice A handles ONLY the immediate-prefix quoted/backtick-literal portion (DECISION-0001/0002 evidence) per Codex `-006` F1 option 2.

## Project Root Boundary Compliance

(Carry-forward.) Operates entirely within `E:/GT-KB/`. No files under `applications/` introduced.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella scoping | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md` |
| Umbrella Codex GO | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md` |
| Sub-slice A Codex NO-GO `-002` | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-002.md` |
| Sub-slice A Codex NO-GO `-004` | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-004.md` |
| Sub-slice A Codex NO-GO `-006` | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-006.md` (F1: P7 code-fence portion not implemented) |
| Source DELIB (S328 regex-tightening) | work_list row 29 |
| Source DELIB (S309 quotation-aware tightening) | work_list row P7 |
| Documented FP corpus | `memory/pending-owner-decisions.md:1055-1073` |
| Existing surfacing impl | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` |
| Existing block emission impl | `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` |
| Owner scope confirmations | This S331 conversation: 3 AskUserQuestion answers |
| Live probes | `grep` of `memory/pending-owner-decisions.md`, `memory/work_list.md` (executed 2026-05-04 in this session) |
| Named follow-up bridge (deferred portion of row P7) | `bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-001.md` (to be filed after Sub-slice A VERIFIED) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
