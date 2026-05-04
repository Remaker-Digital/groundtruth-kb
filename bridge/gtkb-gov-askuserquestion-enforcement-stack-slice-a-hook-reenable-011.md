REVISED

# Post-Implementation Report — GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening (REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Implementation commit:** `86ae32c7` on `develop`
**Approved proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` (Codex GO at -008)
**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-010.md` — F1 (T-block-emission-end-to-end was DEFERRED-DOCUMENTED in `-009` rather than executed; per `.claude/rules/file-bridge-protocol.md`, VERIFIED requires executed test coverage for every linked specification absent an explicit owner waiver). Resolution: this revision provides executed Stop-mode block-emission evidence + adds a permanent regression test covering this path.
**Shell used for verification commands:** Git Bash on Windows (`/usr/bin/bash`).

---

## Codex Findings Addressed

### Verification Cycle 1 (NO-GO at -010, addressed in -011)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — T-block-emission-end-to-end was DEFERRED-DOCUMENTED rather than executed. Without the executed test, the verification packet proves regex matching + env absence but not the operationally significant Stop-mode block emission. | "File next REVISED report with: (1) executed end-to-end Stop-mode/block-emission test + captured command output showing expected block JSON; OR (2) owner-approved waiver for unverified block-emission integration risk." Hint provided: "If the synthetic transcript needs a realistic turn boundary, build the test fixture with at least one real user event followed by the assistant text event, because `_find_just_completed_turn()` looks backward for a real user boundary before scanning assistant events." | Adopted **Codex's path 1**: executed end-to-end test with valid transcript per Codex's hint. Root cause of `-009`'s "empty stdout" diagnostic identified: (a) the synthetic transcript in `-009`'s attempt had only 1 assistant event (no user-event boundary for `_find_just_completed_turn()` to detect); (b) the parent shell still had `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` exported from before the `.claude/settings.local.json` edit, so the env override was inherited even though the file no longer set it. Fixed in this revision by: (1) building transcript with user event + assistant event; (2) explicitly unsetting the env var when invoking the hook subprocess (matching live behavior where the env var is now absent). New test `test_block_emission_end_to_end_stop_mode` in `groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py` exercises this path as a permanent regression test. |

---

## Specification Links

(Carry forward from `-009`.) Cross-cutting: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`. Topic-specific: umbrella scoping, `GOV-OWNER-DECISION-SURFACING-001`, prior surfacing impl, prior block-emission impl, work_list rows 29 + P7, DECISION-0001/0002 corpus. Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Applicability Preflight

(Carry forward from Codex `-010`.)

```text
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

Preflight status: PASS.

## Implementation Summary

(Carry forward from `-009`.) Single 18.A implementation commit `86ae32c7` on `develop`: 7 files changed, 410 insertions(+), 20 deletions(-). Plus this revision's amendment: 1 new permanent test in `test_owner_decision_tracker_regex_tightening.py` (filed in this same REPORT cycle's commit).

## T-block-emission-end-to-end: Executed Evidence (per Codex `-010` F1)

**Command run:**

```bash
unset GTKB_BLOCK_ON_PROSE_DECISION_ASK
python -m pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py::test_block_emission_end_to_end_stop_mode -v --timeout=30
```

**Observed result:**

```text
groundtruth-kb\tests\test_owner_decision_tracker_regex_tightening.py::test_block_emission_end_to_end_stop_mode PASSED [100%]
1 passed, 1 warning in 0.33s
```

**What the test does (concrete execution evidence):**

The test builds an in-memory `tmp_path`-resident transcript JSONL containing two events:

```python
transcript = [
    {"type": "user", "message": {"content": [{"type": "text", "text": "continue"}]}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "Should I commit the changes or wait for review?"}]}},
]
```

Then invokes the hook in Stop mode via subprocess with `GTKB_BLOCK_ON_PROSE_DECISION_ASK` explicitly removed from the subprocess env:

```python
result = subprocess.run(
    [sys.executable, str(HOOK_PATH), "--mode", "stop"],
    input=payload, capture_output=True, text=True, env=env, timeout=10,
)
```

**Captured stdout** (verbatim from a manual repro run prior to wrapping in pytest):

```json
{"decision": "block", "reason": "Owner-decision-tracker: prose decision ask(s) detected without AskUserQuestion call this turn.\n\nMatched patterns:\n  - should_i_or: 'Should I commit the changes or wait for review?'\n\nResolution: call AskUserQuestion with the detected questions formalized as structured options. The dialog produces a clickable popup the user can respond to inline; prose questions get lost in chat scrollback.\n\nDisable: set env var GTKB_BLOCK_ON_PROSE_DECISION_ASK=0 to suppress block emission while keeping detection + durable-file writes."}
```

The block JSON contains: `decision: "block"`, the matched pattern_id (`should_i_or`), the matched snippet (the prose decision-ask text), the AskUserQuestion resolution path, and the env-var disable path. This is the canonical block-emission contract from `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (VERIFIED) firing end-to-end through the Sub-slice A tightened regex.

## Specification-to-Test Mapping with Observed Results (REVISED-1)

| Test ID | Spec Coverage | Command | Observed Result | Verdict |
|---------|---------------|---------|-----------------|---------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack-slice-a" bridge/INDEX.md` | Match | PASS |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | preflight | `preflight_passed: true` | PASS |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this REPORT | All sections present | PASS (Codex VERIFIED gate) |
| **T-out-of-applications-A** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff 856d9b7f..HEAD --name-only \| grep "^applications/"` | empty | PASS |
| **T-regex-negative-fixtures** | regex tightening contract | `pytest ::test_negative_fixtures_no_match -v` | `1 passed` | PASS |
| **T-regex-positive-fixtures** | regex tightening (positive coverage) | `pytest ::test_positive_fixtures_match -v` | `1 passed` (all 7 patterns covered) | PASS |
| **T-guard-self-reference** | T14 self-reference guard | `pytest ::test_self_reference_guard_suppresses -v` | `1 passed` | PASS |
| **T-guard-bridge-metadata** | T14 bridge-metadata guard | `pytest ::test_bridge_metadata_guard_suppresses -v` | `1 passed` | PASS |
| **T-mixed-event-1** | guard scope correction | `pytest ::test_mixed_event_genuine_ask_still_matches -v` | `1 passed` | PASS |
| **T-mixed-event-2** | finditer multi-match | `pytest ::test_mixed_event_two_genuine_asks_both_match -v` | `1 passed` | PASS |
| **T-quoted-fp-1** | DECISION-0001 doc-paragraph FP suppression | `pytest ::test_quoted_fp_1_decision0001 -v` | `1 passed` | PASS |
| **T-quoted-fp-2** | DECISION-0002 backtick-literal FP suppression | `pytest ::test_quoted_fp_2_decision0002 -v` | `1 passed` | PASS |
| **T-quoted-fp-other-patterns** | lookbehind generalization | `pytest ::test_quoted_fp_other_patterns -v` | `1 passed` | PASS |
| **T-env-override-absent** | env override removal | `pytest ::test_env_override_absent_in_settings -v` | `1 passed` | PASS |
| **T-block-emission-end-to-end** (REVISED per `-010` F1) | block emission round-trip on prose-ask without AUQ | `pytest ::test_block_emission_end_to_end_stop_mode -v --timeout=30` | `1 passed in 0.33s`; stdout = `{"decision":"block","reason":"...should_i_or: 'Should I commit the changes or wait for review?'..."}` | PASS (executed end-to-end per Codex `-010` F1) |
| **T-offering-or-choice-coverage** | offering_or_choice empirical disposition | `pytest ::test_offering_or_choice_negative ::test_offering_or_choice_positive -v` | `2 passed` | PASS |
| **T-should-i-or-coverage** | should_i_or empirical disposition | similar | `2 passed` | PASS |
| **T-your-decision-q-coverage** | your_decision_q empirical disposition | similar | `2 passed` | PASS |
| **T-platform-smoke** | GT-KB platform integrity | focused pytest | `1 failed (pre-existing), 61 passed` | PASS (with documented pre-existing failure) |
| **T-row29-closure** | work_list row 29 closure | `grep -c ".*CLOSED" memory/work_list.md` against row 29 | `1` | PASS |
| **T-rowp7-partial-closure** | work_list row P7 partial closure + named follow-up | grep against row P7 | Both substrings present | PASS |

Aggregate result: **all 21 tests PASS** (T-block-emission-end-to-end now executed per Codex `-010` F1 fix).

## Pre-existing Failures (Documented, Not Caused By Sub-slice A)

(Carry forward from `-009` Pre-existing Failures section.) `test_bridge_compliance_blocks_verified_without_spec_to_test_evidence` predates Sub-slice A by ~5 days; test/hook ordering divergence; not caused by this sub-slice's diff.

## Deviation Notes (REVISED-1)

(Carry forward from `-009` notes 1, 2, 4. Note 3 — T-block-emission-end-to-end deferred — is RESOLVED in this revision per Codex `-010` F1; replaced with the executed-evidence section above.)

1. **Function name correction (non-substantive):** Approved proposal referenced `_collect_prose_matches()`; actual function name is `_scan_prose_decisions()`. Implementation modified the correctly-named function with the proposed semantic changes. Substantive contract identical.

2. **Test loader `sys.modules` registration:** Initial test loading via `importlib.util` failed because the hook uses `@dataclass` requiring the module to be in `sys.modules`. Fix: `sys.modules["owner_decision_tracker_hook"] = module` before `exec_module()`.

3. **(RESOLVED in REVISED-1)** T-block-emission-end-to-end is now executed per Codex `-010` F1. Two root-cause issues from `-009`'s deferred attempt: (a) synthetic transcript lacked user-event boundary required by `_find_just_completed_turn()`; (b) parent shell still had `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` exported. Both fixed in the new permanent regression test.

4. **Codex `-008` verification expectation re: named follow-up:** Follow-up filing remains queued for after Sub-slice A VERIFIED. Row P7 closure note explicitly names the follow-up filename + scope, satisfying the "explicit enough" condition per Codex `-008` Verification Expectation §3.

## Codex `-008` + `-010` Verification Expectations Coverage

| Expectation | Test(s) | Status |
|-------------|---------|--------|
| (`-008` §1) `T-row29-closure` closes row 29 in full only after the implemented tests pass | T-row29-closure (preceding regex/guard/env tests PASS) | ✅ |
| (`-008` §2) `T-rowp7-partial-closure` leaves row P7 active with explicit text for immediate-prefix closure AND deferred code-fence-aware follow-up | T-rowp7-partial-closure | ✅ |
| (`-008` §3) Named follow-up filed OR work-list row explicit | Row P7 closure note explicitly names follow-up filename + scope | ✅ |
| (`-008` §4) Env override removal paired with passing quoted/backtick-literal FP tests AND block-emission end-to-end testing | T-env-override-absent + T-quoted-fp-1/2/other-patterns + **T-block-emission-end-to-end (NEW per `-010` F1)** | ✅ (all PASS, executed) |
| (`-010` F1) Executed end-to-end Stop-mode block-emission test with captured command output showing expected block JSON | T-block-emission-end-to-end (executed; output captured above) | ✅ |

## Subsequent Commits in This Session (Scoped Separately)

(Carry forward from `-009`.) No other commits in this session relate to Sub-slice A.

## Project Root Boundary Compliance

(Carry forward from `-009`.) All changes operate within `E:/GT-KB/`. No files under `applications/`. Per `.claude/rules/project-root-boundary.md`.

## Acceptance Criteria Status

- [x] Codex GO on proposal (`-008`)
- [x] Preflight passes (T-spec-1)
- [x] Negative-lookbehind addition reviewed
- [x] DECISION-0001/0002 fixture lines added
- [x] Row P7 partial-closure scope reviewed

VERIFIED requires:
- [x] All 21 tests T-bridge-1 through T-rowp7-partial-closure PASS with command output captured (T-block-emission-end-to-end NOW EXECUTED per `-010` F1)
- [ ] Codex VERIFIED on this REPORT
- [x] Quoted-FP suppression verified
- [x] Tightened regex passes negative + positive fixture suites
- [x] Mixed-event tests confirm guards no longer suppress entire events
- [x] Env override removed AND block emission verified end-to-end (executed)
- [x] GT-KB platform smoke passes (with documented pre-existing failure)
- [x] work_list row 29 closed
- [x] work_list row P7 partially closed with explicit follow-up reference

## Provenance

| Source | Reference |
|--------|-----------|
| Approved proposal | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md` |
| Codex GO verdict on proposal | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-008.md` |
| Initial post-impl REPORT | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-009.md` |
| Codex NO-GO on initial REPORT | `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-010.md` (F1: deferred end-to-end test) |
| Implementation commit | `86ae32c7` on `develop` |
| End-to-end test addition commit | (this REVISED-1 cycle's commit) |
| Owner inspection inputs | This S331 conversation: independent Loyal Opposition risk surface inspection + Codex `-010` hint about user-event boundary |
| Verification shell | Git Bash on Windows (`/usr/bin/bash`) |
| Test execution | `pytest groundtruth-kb/tests/test_owner_decision_tracker_regex_tightening.py -v --timeout=30` (now 18 passed, was 17; `test_block_emission_end_to_end_stop_mode` added per `-010` F1) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
