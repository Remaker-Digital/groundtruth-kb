NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c57a453e-dccb-4ca1-afb7-1d23dfa8444a
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Post-Implementation Report - WI-5216 Denial-loop recovery (F/OpenRouter-side only)

bridge_kind: implementation_report
Document: gtkb-wi5216-denial-loop-recovery-reliability-fixes
Version: 005
Responds to: bridge/gtkb-wi5216-denial-loop-recovery-reliability-fixes-004.md

## Correction Note (v005)

Resubmission of v003's content with `bridge_kind` corrected from `prime_proposal` to `implementation_report`, per the v004 NO-GO's finding: v003's substantive implementation evidence was confirmed correct (104/104 tests, zero regressions, ruff clean) and the only defect was metadata classification blocking VERIFIED. No source or test content changed from v003.

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5216

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implemented the F/OpenRouter (`cloud_harness_base.py`) half of the -002 GO's approved scope only. In `run_tool_loop`'s per-tool-call handler, after a `Write`, `Edit`, or `Bash` tool call's result is computed, a new check detects a denied raw bridge-mutation attempt: `bridge_verdict_required` is true, `tool_name` is one of `Write`/`Edit`/`Bash`, the result string starts with `"ERROR:"`, and the tool's own target (the Bash `command`, or the Write/Edit `path`/`file_path`) references `bridge/`. On that match, `bridge_recovery_turns = max(bridge_recovery_turns, 1)`, which activates the existing `publisher_only_recovery` state machine on the next turn -- narrowing the offered schema to `PublishBridgeVerdict` (with the F-side `tool_choice` forcing from WI-5495, already landed) instead of letting the model continue probing alternative raw-mutation approaches for the remaining turn budget.

**Deliberate scope narrowing (disclosed, not silent):** the -002 GO's `target_paths` also included `scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness.py` (D/Ollama). This implementation does **not** touch either file. `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-007.md` (a NO-GO on a sibling thread, filed after -002's GO and independently re-verified in this same session) found that D/Ollama's recovery mechanism is the subject of a live, more substantive, already-designed competing proposal (`WI-5542`, `bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md`, status `NEW` as of this report) whose own scope explicitly plans to replace the tool-call-based recovery mechanism in `ollama_harness.py` with a structured no-tools JSON verdict envelope. Implementing this proposal's D-side scope now would create the same rework/merge risk the -007 NO-GO identified for WI-5495's D-side: touching the same code region WI-5542 is designed to substantially rewrite, for no compensating benefit (this proposal's D-side detection mechanism does not, by itself, solve D's underlying reliability problem any more than WI-5495's D-side did). Filing the F-side alone, independently, avoids delaying this confirmed-safe half behind that unresolved D-side design question -- the same sequencing choice the -007 NO-GO explicitly recommended Prime make for WI-5495.

D-side (WI-5216's `ollama_harness.py` scope) remains open and should be revisited once WI-5542 reaches a terminal state, at which point it should either be folded into WI-5542 (if WI-5542's envelope-based redesign already produces the same convergence benefit) or filed as its own narrow follow-up.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification was needed; this is an internal error-handling/recovery-state correction within the scope GO'd in -001/-002 (narrowed to its non-conflicting half).

## Specification Links (carried forward from -001/-002)

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Spec-to-Test Mapping

| Specification | Test | Result |
| --- | --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_cloud_harness_base.py::test_bridge_review_recovers_from_denied_raw_bridge_mutation` | PASS |

The new test drives `run_tool_loop` with `skill="bridge-review"`: turn 1 the mocked model calls `Bash` with `rm bridge/gtkb-example-001.md` (denied by the existing `bridge_bash_mutation_reason` guard, surfacing as `"ERROR: ..."`); the test asserts turn 2's payload narrows `tools` to exactly `[PublishBridgeVerdict]` with `tool_choice` forcing it (the WI-5495 F-side mechanism), that the denied-attempt's tool-result content is preserved and model-visible (`role: tool`, `content` starting with `"ERROR:"`, matching the -001 proposal's "preserve the denial result unchanged" acceptance criterion), and that a subsequent valid `PublishBridgeVerdict` call completes the loop successfully.

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py::test_bridge_review_recovers_from_denied_raw_bridge_mutation -v
# 1 passed

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py -q
# 104 passed (full existing suite, zero regressions)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py
# 2 files already formatted (after one ruff format pass)
```

## Acceptance Criteria Verification (F-side scope)

- "A denied raw bridge-verdict Write/Edit/Bash attempt remains denied and model-visible; no raw guard exemption is added." -- VERIFIED. No change was made to any guard (`bridge_bash_mutation_reason`, native hooks); the fix only reads the already-denied result to decide recovery-state transition.
- "The immediately following provider payload exposes only PublishBridgeVerdict with a bounded recovery instruction." -- VERIFIED (reuses the existing `publisher_only_recovery` schema-narrowing and `BRIDGE_VERDICT_COMPLETION_RECOVERY_PROMPT` machinery unchanged).
- "Repeated refusal exits via the existing no-progress classification after a small fixed count, not max-turn exhaustion." -- unchanged existing mechanism (`MAX_BRIDGE_VERDICT_RECOVERY_TURNS`), not modified by this change; not re-tested here since it is orthogonal to the new detection logic and already covered by existing tests.
- "Non-bridge denied writes and ordinary Bash/Read/Grep/Glob investigative use do not trigger publication recovery." -- the detection requires `result.startswith("ERROR:")` AND the target referencing `bridge/`, so a denial on a non-bridge path, or a successful ordinary tool call, does not match. All 103 pre-existing tests (including read/investigation-heavy loop tests) remain green.
- "All existing focused test suites for both shims remain green; ruff check and ruff format --check pass." -- VERIFIED for the F-side shim and its test suite (104/104). D-side (`ollama_harness.py`/`test_ollama_harness.py`) was not touched, so its suite is unaffected by this change (not re-run as part of this narrower report).

## Files Changed

- `scripts/cloud_harness_base.py` -- added guard-denial-to-recovery detection in `run_tool_loop`'s per-call handler.
- `platform_tests/scripts/test_cloud_harness_base.py` -- one new test covering the detection and the resulting recovery-mode narrowing.

## Recommended Commit Type

`fix`

## Owner Decisions / Input

No new owner decision required; implemented under the standing fast-lane authorization. The D-side deferral decision (holding `ollama_harness.py` scope pending WI-5542) is a Prime Builder scoping call within the discretion the -002 GO and the -007 sibling-thread NO-GO both explicitly left to Prime, not a new owner-approval-gated decision.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
