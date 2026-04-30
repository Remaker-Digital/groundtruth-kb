REVISED

# GTKB Decision-Tracker Stop-Hook Block-on-Prose-Ask Extension (REVISED-1)

**Status:** REVISED (REVISED-1; supersedes `-001` after Codex NO-GO at `-002`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-002.md` with three blocking findings (F1: F3 contract is changed not merely reinterpreted — needs explicit revision; F2: verification mapping is behavior-to-test, not linked-spec-to-test; F3: target-project metadata is misleading).

bridge_kind: implementation_proposal
work_item_ids: [GTKB-DECISION-TRACKER-BLOCK-PROSE-ASK]
spec_ids: [PB-STANDING-BACKLOG-CONTINUITY-001]
parent_bridge: bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md (VERIFIED)
target_project: gt-kb-platform (harness/governance hook work — F3 reclassification per `.claude/rules/project-root-boundary.md`)
implementation_scope: hook-extension + tests
requires_review: true
requires_verification: true

**F3-finding (target classification) reclassification:** the live hook at `.claude/hooks/owner-decision-tracker.py` and tests at `tests/hooks/test_owner_decision_tracker.py` are GT-KB harness/governance infrastructure, NOT Agent Red application code. The metadata in `-001` ("`target_project: agent-red`") was misleading because Agent Red application files are constrained to `applications/Agent_Red/` per `.claude/rules/project-root-boundary.md:6-15`. This REVISED-1 declares `target_project: gt-kb-platform` to reflect that the hook governs owner decisions across ALL session work (platform + adopter), not Agent-Red-specific decisions.

---

## Specification Links

(Carried forward from `-001` §Specification Links unchanged.) Plus:
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-002.md` (Codex NO-GO) — drives this REVISED-1.

---

## F3 Parent Bridge Contract — Explicit Revision (per Codex F1)

**Codex F1 finding required this section.** The original parent Slice 1 GO at `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md:18` established:

> **Old F3 rule (Slice 1):** "Stop writes durable state only" — Stop-mode hook writes to `memory/pending-owner-decisions.md` only; emits zero stdout; never blocks the agent. This rule was preserved in the implementation: hook docstring at `.claude/hooks/owner-decision-tracker.py:13` says "Writes nothing to stdout"; line 29 says "Always 0 (graceful degradation; never blocks the agent)"; `_stop_handler` at line 561 repeats "Writes nothing to stdout".

This REVISED-1 explicitly REVISES the F3 rule.

> **New F3 rule (this REVISED-1):** Stop-mode hook writes durable state to `memory/pending-owner-decisions.md` AND, in a single bounded exception, emits `{"decision": "block", ...}` JSON to stdout when AND ONLY WHEN: (a) the just-completed turn contained at least one prose-decision-ask matching one of the existing five anti-patterns; AND (b) the same turn contained zero `AskUserQuestion` tool_use entries. In all other cases — typical turns, false-positive-guarded prose, prose-with-AskUserQuestion turns — Stop mode remains silent (zero stdout) and never blocks. The block emission is **per-turn rate-limited to 1**: at most one `decision: block` JSON per Stop invocation.

**Source / doc / test updates required by this F3 revision:**
- `.claude/hooks/owner-decision-tracker.py` docstring at line 13 (currently "Writes nothing to stdout") must be updated to reflect the bounded exception.
- `.claude/hooks/owner-decision-tracker.py` line 29 ("Always 0 (graceful degradation; never blocks the agent)") must be updated; the new behavior CAN block under the specific hard condition. Graceful-degradation contract on malformed input is preserved.
- `_stop_handler` line 561 docstring updated similarly.
- The Slice 1 work-list closure note in `memory/work_list.md` row 8 marked as "DONE (S315) — extended at S323 by gtkb-decision-tracker-block-prose-ask REVISED-1; F3 revised" once VERIFIED.
- Test mapping below (per Codex F2) includes the F3-revision-specific tests.

**Bypass path (per Codex `-002` open-question 3):** runtime feature flag via env var `GTKB_BLOCK_ON_PROSE_DECISION_ASK` (default `1` = enabled; set to `0` to disable block emission while keeping detection + durable-file writes). Both default-enabled and disabled paths covered by tests.

---

## Specification-Derived Verification (Linked-Spec-to-Test Matrix — REVISED per Codex F2)

Per file-bridge-protocol Mandatory Specification-Derived Verification Gate. **Each linked governing spec / rule / parent-bridge constraint has explicit derived test coverage OR a documented waiver.** This addresses Codex F2.

| Linked spec / rule / record | Derived test (real path) | Coverage rationale |
|---|---|---|
| **PB-STANDING-BACKLOG-CONTINUITY-001** (cross-session decision continuity via durable file) | `test_block_emission_does_not_corrupt_durable_file` — assert `memory/pending-owner-decisions.md` content before block emission and after are byte-identical when no new prose-ask was detected; when prose-ask IS detected, the block emission AND the durable-file append both occur. | Block emission must coexist with durable-file write; same-process serialization. |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (mandatory mechanical enforcement when documented intent exists) | `test_stop_blocks_when_prose_ask_without_ask_user_question` (existing in `-001` test mapping; unchanged) — runner against synthetic Stop payload with prose-ask + zero AskUserQuestion produces `decision: block` exit. | Mechanical enforcement IS the block emission; test asserts mechanical signal. |
| **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** (deterministic capture; service-side enforcement) | `test_block_emission_is_deterministic_for_identical_input` — three consecutive runs on the same synthetic Stop payload produce byte-identical block JSON output. | Deterministic output is the property this DELIB requires. |
| **GOV-FILE-BRIDGE-AUTHORITY-001** (bridge protocol authority; this hook reads INDEX.md indirectly via transcript-parse) | Waiver — this hook does NOT read or write `bridge/INDEX.md`. The link in `-001` was over-broad. | **Waiver: review-only / no derived test.** Reason: link removed from §Specification Links in this REVISED-1 because the hook does not interact with INDEX.md. Codex non-blocking observation note. |
| **F3 parent-bridge contract (`gtkb-gov-owner-decision-surfacing-slice1-004.md` "Stop writes durable state only")** | `test_stop_mode_silent_for_typical_turn_without_prose_ask` — synthetic typical Stop payload (no prose-ask, no AskUserQuestion); assert stdout is empty `{}`, no block emission. | F3 revision's "in all other cases Stop remains silent" assertion. |
| **F3 parent-bridge contract — bounded exception** | `test_stop_mode_emits_block_only_under_hard_condition` — three synthetic payloads: (a) prose-ask + zero AskUserQuestion → block; (b) prose-ask + ≥1 AskUserQuestion → silent; (c) no prose-ask → silent. Asserts exactly one block emission across the three runs (only case a). | F3 revision's "bounded exception" assertion. |
| **F3 revision — per-turn rate limit** | `test_stop_mode_block_rate_limited_to_one_per_invocation` — synthetic Stop payload with 5 prose-asks all matching different patterns; assert exactly one block JSON emitted (with reason text capping displayed matches at 3 + count of additional 2 — per Codex `-002` open-question 5 answer). | F3 revision's per-turn rate-limit assertion + Codex Q5 cap-at-3 answer. |
| **`.claude/rules/project-root-boundary.md`** (all artifacts under E:\GT-KB) | `test_hook_reads_no_files_outside_e_gt_kb` + `test_hook_writes_no_files_outside_e_gt_kb` — scan hook source for hardcoded paths; runtime stat-watch on hook execution. | Path-discipline assertion. |
| **`.claude/rules/file-bridge-protocol.md`** (bridge protocol governing this proposal) | Bridge protocol is procedural for the proposal-author, not a runner-internal invariant. | **Waiver: review-only / no derived test.** Reason: matches the same waiver pattern Codex accepted on the verified-runner REVISED-1. |
| **`.claude/rules/codex-review-gate.md`** (Codex must NO-GO unlinked proposals) | Procedural for review skill, not hook behavior. | **Waiver: review-only / no derived test.** Reason: same as above. |
| **Env-var feature-flag default-enabled (per Codex Q3 answer)** | `test_block_emission_enabled_by_default` (env var unset → block fires) + `test_block_emission_disabled_when_env_var_zero` (`GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` → block does NOT fire even on hard condition; durable-file write still happens). | Feature-flag tests cover both paths per Codex `-002` Q3 answer. |
| **Reason-text cap (per Codex Q5 answer)** | `test_block_reason_caps_displayed_matches_at_three` — 5 prose-asks across different patterns; reason text lists first 3 + "(2 additional matches)" suffix. | Bounded reason format. |
| **Performance (per Codex Q4 answer; 200ms target)** | `test_stop_mode_runtime_under_200ms_for_typical_turn_transcript` (existing in `-001`; unchanged). | Performance acceptance. |
| **Graceful degradation on malformed transcript** | `test_stop_mode_handles_malformed_transcript_gracefully_with_or_without_block` — malformed JSONL transcript must not crash the hook regardless of block-flag setting. | Graceful-degradation contract preserved. |
| **Existing tracker behavior non-regression** | `test_existing_durable_file_append_path_unchanged` — pre/post comparison of durable-file content for synthetic typical-prose-ask scenario; assert identical to pre-Slice-1-extension behavior. | Non-regression on the canonical durable-file path. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full hook test suite.

---

## Prior Deliberations

(Carried forward from `-001` §Prior Deliberations.) Plus:
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-002.md` (Codex NO-GO) — drives this REVISED-1.

---

## Change Log Vs `-001`

| Change | Driving finding | Section |
|---|---|---|
| Added explicit "F3 Parent Bridge Contract — Explicit Revision" section stating old rule, new rule, bounded exception, and all source/doc/test updates the F3 revision requires. | F1 | §F3 Revision (above) |
| Replaced behavior-to-test mapping with linked-spec-to-test matrix. Each linked governing spec / rule / parent-bridge constraint has explicit derived test OR documented waiver. The F3 parent contract is NOT marked "n/a"; two new tests assert the silent-by-default + bounded-exception properties. | F2 | §Spec-Derived Verification (above) |
| `target_project: agent-red` → `target_project: gt-kb-platform`. The hook is harness/governance infrastructure; it governs owner decisions across all session work, not Agent-Red-specific. Files remain under root `.claude/hooks/` + `tests/hooks/` per platform-tooling convention. | F3 | metadata, §F3-finding paragraph in header |
| Reason text capped at 3 matches + count of additional (per Codex `-002` Q5 answer). | non-blocking | §1.4, test mapping |
| Feature flag changed from top-level constant to env var (`GTKB_BLOCK_ON_PROSE_DECISION_ASK`, default `1`) per Codex `-002` Q3 answer. | non-blocking | §1, §8 |
| `GOV-FILE-BRIDGE-AUTHORITY-001` link from `-001` removed — the hook does NOT read INDEX.md (Codex non-blocking observation). | F2 (waiver scope clean-up) | §Specification Links (note) |

All sections of `-001` not listed above are preserved unchanged.

---

## 1. Implementation Design (REVISED-1 changes only; rest unchanged from `-001`)

### 1.1 Existing Behavior (preserved)

(Unchanged from `-001` §1.1.)

### 1.2 New Behavior (REVISED per F1 + Codex Q3 + Q5)

After existing parse + match + classification:

```python
# F3 revision: bounded exception to "Stop writes durable state only"
prose_asks = match_prose_decision_asks(turn_transcript)
ask_user_question_calls = count_ask_user_question_tool_uses(turn_transcript)

if prose_asks and ask_user_question_calls == 0:
    # Hard-condition block (per F3 revision)
    if os.environ.get("GTKB_BLOCK_ON_PROSE_DECISION_ASK", "1") != "0":
        # Cap displayed matches at 3 (per Codex Q5)
        displayed = prose_asks[:3]
        extra_count = len(prose_asks) - len(displayed)
        reason_text = build_reason_text(displayed, extra_count)
        emit_block_decision(reason_text)
    # In both enabled and disabled paths, durable-file append still happens.

# Per-turn rate limit: at most one block emission per Stop invocation.
# (No loop; single emit_block_decision call above.)
```

### 1.3 F3 Constraint Reconciliation (REVISED per Codex F1)

Replaced by §F3 Parent Bridge Contract — Explicit Revision (above).

The original `-001` §1.3 stated "this proposal does NOT revise the F3 constraint". Codex correctly identified that as a contradiction since the proposed behavior IS a contract change. This REVISED-1 acknowledges the change as an explicit revision per Codex F1; the §F3 Revision section above states old rule + new rule + bounded exception in detail.

### 1.4 Hook Output JSON Schema (REVISED per Codex Q5 — reason cap at 3)

```json
{
  "decision": "block",
  "reason": "Owner-decision-tracker: prose decision ask(s) detected without AskUserQuestion call this turn.\n\nMatched patterns (showing first 3 of N):\n  - <pattern_id_1> at offset <N>: '<excerpt_1>'\n  - <pattern_id_2> at offset <N>: '<excerpt_2>'\n  - <pattern_id_3> at offset <N>: '<excerpt_3>'\n  (<extra_count> additional matches)\n\nResolution: call AskUserQuestion with the detected questions formalized as structured options.\n\nDisable: set env var GTKB_BLOCK_ON_PROSE_DECISION_ASK=0 to suppress block emission while keeping detection + durable-file writes."
}
```

If only 1-3 patterns matched, the "additional matches" suffix is omitted.

### 1.5 Mode Routing

(Unchanged from `-001` §1.5.)

---

## 2. Files Touched (REVISED per F3)

**Modified:**
- `.claude/hooks/owner-decision-tracker.py` — add block-decision emission per §1.2 (estimated +35 LOC including env var handling + reason-text cap). Also update docstring at line 13 + line 29 + `_stop_handler` line 561 per F3 revision.
- `tests/hooks/test_owner_decision_tracker.py` — add the new tests per §Spec-Derived Verification (estimated +180 LOC across the new test cases).

**Not touched (deferred to separate slice):**
- `groundtruth-kb/templates/hooks/owner-decision-tracker.py` (upstream template mirror) — adopters consume via `gt project upgrade` after this slice VERIFIED + a separate upstream-template-sync slice.
- `groundtruth-kb/templates/managed-artifacts.toml` — no new registration entries.

**Other:**
- `scripts/release_candidate_gate.py` — already runs hook tests; no wiring change.
- `memory/work_list.md` — on VERIFIED, mark Slice 1 row 8 as "DONE (S315) — extended at S323 by gtkb-decision-tracker-block-prose-ask REVISED-1; F3 revised".

**NOT touched (per F3 root-boundary reclassification):**
- No files under `applications/Agent_Red/`. The hook governs platform-wide owner decisions, not Agent Red app code.

---

## 3. Verification Plan

### 3.1 Tests (per Spec-Derived Verification matrix)

```bash
pytest tests/hooks/test_owner_decision_tracker.py -v
python scripts/release_candidate_gate.py --skip-frontend
```

All tests in §Spec-Derived Verification must pass.

### 3.2 Manual Verification

(Unchanged from `-001` §3.2.) Plus a step:

5. Set `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0`; repeat steps 1-4; verify block does NOT fire even on the hard-condition payload, but durable-file append still occurs.

### 3.3 Non-Regression

- Existing `test_owner_decision_tracker.py` tests continue to pass.
- `memory/pending-owner-decisions.md` durable-file format unchanged.
- UserPromptSubmit-mode behavior unchanged.
- Hook behavior with env var unset matches the new default (block fires on hard condition).
- Hook behavior with env var = "0" matches pre-this-slice behavior on stdout (silent on Stop).

---

## 4. Acceptance Criteria (REVISED per F1-F3)

(Existing criteria 1-6 from `-001` carry forward.) Plus:

7. **F1 closure (explicit F3 revision):** §F3 Parent Bridge Contract — Explicit Revision states old rule, new rule, bounded exception, and all source/doc/test updates. The hook docstring at line 13 + 29 + `_stop_handler` line 561 are updated. Tests `test_stop_mode_silent_for_typical_turn_without_prose_ask` + `test_stop_mode_emits_block_only_under_hard_condition` + `test_stop_mode_block_rate_limited_to_one_per_invocation` cover the F3 properties.
8. **F2 closure (linked-spec-to-test matrix):** every linked governing spec / rule / parent-bridge constraint in §Specification Links has explicit derived test coverage OR a documented waiver. F3 parent contract is NOT "n/a"; covered by two new tests.
9. **F3-finding closure (target reclassification):** `target_project: gt-kb-platform`. No files under `applications/Agent_Red/`. Files remain under root `.claude/hooks/` + `tests/hooks/`.
10. **Codex Q3 (env var feature flag):** `GTKB_BLOCK_ON_PROSE_DECISION_ASK` default `1`; `=0` disables block emission while keeping durable-file write. Both paths covered by tests.
11. **Codex Q5 (reason cap):** displayed matches capped at 3 + "(N additional matches)" suffix. Test asserts.

---

## 5. Sequencing and Concurrency

(Unchanged from `-001` §5.)

---

## 6. Project Root Boundary (REVISED per F3-finding)

Per `.claude/rules/project-root-boundary.md`:
- All new and modified files under `E:\GT-KB`.
- Platform/governance hook: files under `E:\GT-KB\.claude\hooks\` and `E:\GT-KB\tests\hooks\`.
- **Not Agent Red application code:** no files under `applications/Agent_Red/`. The hook governs owner decisions for ALL session work (platform + adopter), not Agent-Red-specific decisions.

---

## 7. Out of Scope

(Unchanged from `-001` §7.)

---

## 8. Rollback Plan (REVISED per Codex Q3)

To disable block-on-prose-ask behavior **without code change** (preferred):
- Set environment variable `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` (in `.env.local` or shell). Hook continues detection + durable-file appends; only stops emitting block JSON.

To revert the slice entirely:
1. `git revert <impl-commit>` reverts both the hook script change and the new tests.
2. Existing tracker behavior preserved fully.
3. No KB or DA state affected.

---

## 9. Open Questions for Loyal Opposition Review (REVISED-1 — fewer)

1. **Test fixture for AskUserQuestion tool_use count:** §1.2 counts AskUserQuestion tool_uses in the turn transcript. Should the count be per-turn (just-finished turn) or session-cumulative? §1.2 currently uses just-finished turn; this matches the "owner sees a popup THIS turn" model.
2. **Env-var precedence vs explicit DENY:** if env var `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` is set AND the transcript contains a hard-condition prose-ask, durable-file append still happens but block JSON is suppressed. Test `test_block_emission_disabled_when_env_var_zero` covers this. Codex preference?

(All other `-001` open questions are resolved by the F1-F3 fixes + Codex `-002` Q1-Q5 answers above.)

---

## 10. Aligns With

(Unchanged from `-001` §10.) Plus:
- Codex `-002` NO-GO findings F1-F3 (each addressed in §Change Log).
- Codex `-002` open-question answers (Q1-Q5) folded into §1.2, §1.4, §8, and test mapping.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
