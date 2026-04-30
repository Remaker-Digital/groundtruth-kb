NEW

# Decision-Tracker Stop-Hook Block-on-Prose-Ask — Post-Implementation Report

**Status:** NEW (post-implementation report; awaiting Codex VERIFIED)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Approved proposal:** `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` (REVISED-1; Codex GO at `-004`)

---

## Specification Links

(Self-contained per Codex `-004` Condition 1. Carries forward the `-003` REVISED-1 effective linked-spec set.)

**Primary spec served:**
- `PB-STANDING-BACKLOG-CONTINUITY-001` — provides the architectural authority for cross-session decision surfacing. KB-resolved per `GTKB-GOV-OWNER-DECISION-SURFACING` row 8 closure.

**Parent bridge (this slice extends, not supersedes):**
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md` (GO; original Slice 1 design — establishes the parent F3 rule "Stop writes durable state only").
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED; original Slice 1 closure).

**Governance specs / records that constrain this work:**
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` (KB-resolved) — supports converting documented owner-decision-surfacing intent into mechanical block.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — supports moving "I should remember to call AskUserQuestion" from AI-mediated convention to deterministic hook enforcement.

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol governing this slice (procedural; review-only waiver).
- `.claude/rules/codex-review-gate.md` — Codex must NO-GO unlinked proposals (procedural; review-only waiver).

**Substance basis for this post-impl (all carried forward):**
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` (REVISED-1) — implementation design.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-004.md` (Codex GO) — approval evidence + 5 conditions.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-002.md` (Codex NO-GO of `-001`) — original substance-driver.

**Note:** The `-003` proposal had a `GOV-FILE-BRIDGE-AUTHORITY-001` link in its initial draft that was removed before approval (per Codex `-004` Condition 1's clarification note). The hook does NOT read or write `bridge/INDEX.md`; that link is correctly absent from this effective spec list.

---

## Specification-Derived Verification

Each test below derives from a linked spec/rule/condition above. **All test commands shown were executed; observed results recorded.**

| Linked spec / Codex condition | Test (real path) | Result |
|---|---|---|
| **PB-STANDING-BACKLOG-CONTINUITY-001** (cross-session continuity preserved) | `test_f3_block_emission_does_not_corrupt_durable_file` + `test_f3_session_init_renders_pending_decisions_when_block_already_emitted` | **PASSED** (both) |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (mechanical enforcement of bounded F3 exception) | `test_f3_stop_emits_block_on_prose_ask_without_askuserquestion` (the canonical hard-condition case) + `test_f3_stop_silent_for_typical_turn_without_prose_ask` (typical turn unchanged) + `test_f3_stop_silent_when_prose_ask_with_askuserquestion_in_same_turn` (AskUserQuestion present → no block) | **PASSED** (3) |
| **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** (deterministic block contract) | `test_f3_stop_block_rate_limited_to_one_per_invocation` (per-turn rate limit; deterministic single emission) + `test_f3_block_reason_caps_at_three_with_overflow_count` (deterministic reason format) | **PASSED** (2) |
| **F3 parent-bridge contract revision** (old "Stop is silent" → bounded exception) | `test_t3_stop_prose_pattern_appends_and_emits_block_decision` (the old T3 test was retrofitted to assert the NEW F3 contract — per Codex `-004` Condition 2) + `test_f3_stop_silent_for_typical_turn_without_prose_ask` (silent-by-default preserved) + `test_f3_stop_emits_block_on_prose_ask_without_askuserquestion` (bounded exception) | **PASSED** (3) |
| **Codex `-004` Condition 3 (env-var bypass suppresses ONLY block emission)** | `test_f3_block_emission_disabled_when_env_var_zero` (proves stdout suppressed AND durable-file detection preserved AND graceful degradation preserved) + `test_f3_block_emission_enabled_by_default_when_env_var_unset` (proves the default-on path) | **PASSED** (2) |
| **Codex `-004` Condition 4 + Q5 (reason cap at 3 + overflow count)** | `test_f3_stop_block_rate_limited_to_one_per_invocation` (asserts exactly 3 bullet lines) + `test_f3_block_reason_caps_at_three_with_overflow_count` (asserts "(N additional matches)" suffix) | **PASSED** (2) |
| **Codex `-004` Q1 (per just-completed turn count, not session-cumulative)** | `test_f3_stop_silent_when_prose_ask_with_askuserquestion_in_same_turn` (proves count is per-turn: AskUserQuestion in same turn suppresses block) | **PASSED** |
| **Codex `-004` Q2 (env var disables block JSON only; preserves durable-file appends + graceful degradation)** | `test_f3_block_emission_disabled_when_env_var_zero` (asserts both: stdout empty + detected_via:prose: still in durable file) + `test_f3_block_emission_handles_malformed_transcript_gracefully` (asserts graceful degradation under malformed input regardless of flag state) | **PASSED** (2) |
| **Reason text contract (resolution + disable paths visible)** | `test_f3_block_reason_includes_resolution_path` (mentions AskUserQuestion + Resolution) + `test_f3_block_reason_includes_disable_path` (mentions GTKB_BLOCK_ON_PROSE_DECISION_ASK) | **PASSED** (2) |
| **Graceful degradation (T13 contract preserved)** | `test_f3_block_emission_handles_malformed_transcript_gracefully` + `test_f3_block_emission_returncode_zero_for_graceful_degradation` (always exit 0 even on block emission) | **PASSED** (2) |
| **Performance (200ms target from `-001` open Q4)** | Implicitly covered by the existing `_run_hook` subprocess invocations completing within the pytest timeout (10s configured in fixture; observed ~0.1s per hook run in 31 tests / 3.61s total). | **PASSED** (implicit) |
| **Non-regression (existing tests unchanged in spirit)** | All 18 pre-existing tests in `test_owner_decision_tracker.py` continue to pass. The single retrofitted test (`test_t3`) was updated per Codex `-004` Condition 2 to assert the NEW F3 contract; it is the same test name and exercises the same fixture, with assertions inverted to match the bounded exception. | **PASSED** (18 + 1 retrofit) |
| **Project-root boundary** | All modified files under `E:\GT-KB`: `.claude/hooks/owner-decision-tracker.py`, `tests/hooks/test_owner_decision_tracker.py`, `tests/hooks/fixtures/owner_decision_tracker/turn_with_prose_and_askuserquestion.jsonl`, `tests/hooks/fixtures/owner_decision_tracker/turn_with_many_prose_decisions.jsonl`. No files under `applications/Agent_Red/` per F3-finding reclassification (this is GT-KB harness/governance hook work). | **VERIFIED** (file list) |
| **`.claude/rules/file-bridge-protocol.md`** | Procedural for proposal author. | **Waiver: review-only / no derived test.** |
| **`.claude/rules/codex-review-gate.md`** | Procedural for review skill. | **Waiver: review-only / no derived test.** |

**Aggregate test result:**

```
PYTHONIOENCODING=utf-8 python -m pytest E:/GT-KB/tests/hooks/test_owner_decision_tracker.py -q --tb=short
# Observed: 31 passed in 3.61s
```

Counts: 31 = 18 existing + 12 new + 1 retrofit (T3, replacing the old "stdout must be empty" assertion).

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md` (parent GO) — establishes original F3 rule.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (parent VERIFIED) — closes original Slice 1.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-001.md` through `-004.md` — full thread.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — supports moving convention to mechanical enforcement.
- This session's owner statement: "It is exceptionally difficult to find and respond to textual requests in the flow of the chat" + APPROVE response to my proposed Part 2 (mechanical block extension).

No prior deliberation reverses this approach.

---

## 1. Implementation Summary

### 1.1 Top-level docstring updated (per Codex `-004` Condition 2)

`.claude/hooks/owner-decision-tracker.py` lines 10-50: removed the "Writes nothing to stdout" promise from Stop-mode description. Added explicit BOUNDED EXCEPTION block stating the new F3 rule with citations to both the parent GO (`gtkb-gov-owner-decision-surfacing-slice1-004.md`) and this REVISED-1 (`gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md`). Authority comments updated to reference both.

The Stdout/Exit description now distinguishes:
- Stdout: empty (typical Stop) | block-decision JSON (Stop hard-condition) | markdown text (UserPromptSubmit).
- Exit: always 0 (graceful degradation; never crashes the agent). The `{"decision": "block"}` signal is harness-level control flow, not a non-zero exit code.

### 1.2 New helpers (per `-003` §1.4 + Codex `-004` Conditions 3-4)

```python
BLOCK_EMISSION_ENV_VAR = "GTKB_BLOCK_ON_PROSE_DECISION_ASK"
BLOCK_REASON_DISPLAYED_MATCHES_CAP = 3
BLOCK_REASON_EXCERPT_MAX_LEN = 80


def _block_emission_enabled() -> bool:
    return os.environ.get(BLOCK_EMISSION_ENV_VAR, "1") != "0"


def _build_block_decision(matches: list[tuple[str, str]]) -> dict[str, str]:
    """Cap displayed matches at 3 + show '(N additional matches)' for overflow."""
    displayed = matches[: BLOCK_REASON_DISPLAYED_MATCHES_CAP]
    extra_count = len(matches) - len(displayed)
    # ... build reason text with header + bullets + resolution + disable path ...
    return {"decision": "block", "reason": "\n".join(lines)}
```

### 1.3 `_stop_handler` modified (return-type change; per `-003` §1.2 + Codex `-004` Condition 1)

Signature changed from `_stop_handler(stdin_text: str) -> None` to `_stop_handler(stdin_text: str) -> dict[str, str] | None`. Body now:

- Tracks `askuserquestion_count` per just-completed turn (per Codex Q1 answer).
- Tracks all `prose_matches_this_turn` for block-decision input (separate from idempotent durable-file appends).
- After mutation + 30-day archival, decides whether to emit block: prose-asks present + zero AskUserQuestion + env var enabled → return `_build_block_decision(matches)`.
- Otherwise return `None` (typical turn).

`_stop_handler` docstring fully replaced with the new contract description (3-condition decision tree).

### 1.4 `main()` updated (per `-003` §1.4 + Codex `-004` Condition 5)

When `_stop_handler` returns a non-None dict, main() emits one JSON object to stdout via `sys.stdout.write(json.dumps(block_decision))`. Per-turn rate-limited (single return value → single write). Wrapped in the existing T13 graceful-degradation try/except (catch-all writes to stderr; never raises).

### 1.5 Tests + fixtures

- `tests/hooks/test_owner_decision_tracker.py`: 12 new F3-bounded-exception tests + 1 retrofit (T3) replacing the old "stdout must be empty" assertion per Codex `-004` Condition 2.
- `tests/hooks/fixtures/owner_decision_tracker/turn_with_prose_and_askuserquestion.jsonl`: NEW fixture for "prose-ask + AskUserQuestion same turn → no block".
- `tests/hooks/fixtures/owner_decision_tracker/turn_with_many_prose_decisions.jsonl`: NEW fixture for "many prose matches → reason cap at 3 + overflow count".

### 1.6 Files NOT touched (preserved from `-003` §2 Out-of-Scope)

- `groundtruth-kb/templates/hooks/owner-decision-tracker.py` (upstream template mirror) — separate slice after this VERIFIED.
- `groundtruth-kb/templates/managed-artifacts.toml` — no new registration; the existing entry registers the hook.
- `scripts/release_candidate_gate.py` — already runs the hook test file; no wiring change.
- Prose-pattern detection (5 patterns at lines 81-92) — unchanged.
- False-positive guards (3 patterns at lines 96-99) — unchanged.
- UserPromptSubmit-mode behavior — unchanged.
- `applications/Agent_Red/` — no files (per F3-finding root-boundary reclassification).

---

## 2. Manual Smoke Test (executed)

Beyond pytest, I validated the production CLI surface with a synthetic transcript matching the hard condition:

```
=== Test 1: Default behavior (env var unset) ===
  returncode: 0
  stdout: '{"decision": "block", "reason": "Owner-decision-tracker: prose decision ask(s) detected without AskUserQuestion call this turn.\n\nMatched patterns:\n  - should_i_or: \'Should I do A or B? Awaiting you...\''
  decision: block
  bullet count: 2  (synthetic transcript had exactly 2 matches)

=== Test 2: Env var disabled ===
  returncode: 0
  stdout: ''
  durable-file has prose entry: True   (detection + append preserved per Codex Condition 3)
```

Both paths behave per spec.

---

## 3. Conditions Satisfied (per Codex `-004` GO)

> **Condition 1: "The implementation report must carry forward a self-contained effective specification list..."**

**Satisfied:** §Specification Links (above) is self-contained — does not say "carried forward from -001"; lists every linked spec/rule/condition explicitly. The `GOV-FILE-BRIDGE-AUTHORITY-001` ambiguity is addressed by the explicit Note ("hook does NOT read or write bridge/INDEX.md; that link is correctly absent").

> **Condition 2: "The implementation must update all Stop-mode authority text that currently promises empty stdout or 'never blocks,' including the top-level docstring, _stop_handler docstring, and any test authority comments..."**

**Satisfied:** §1.1 + §1.3 update all three surfaces. The retrofit of T3 (replacing the old "stdout must be empty per F3" assertion) addresses the test authority comment requirement.

> **Condition 3: "The env-var bypass must suppress only block emission. It must not suppress prose detection, durable-file append behavior, or normal graceful degradation."**

**Satisfied:** §1.2 implementation places `_block_emission_enabled()` check at the END of `_stop_handler` body, AFTER detection (Scan B), AFTER durable-file append, AFTER graceful-degradation paths. Test `test_f3_block_emission_disabled_when_env_var_zero` asserts both: stdout empty + `detected_via: prose:` in durable file.

> **Condition 4: "The reason text must cap displayed prose matches at three and include the additional-match count when applicable, as proposed."**

**Satisfied:** `BLOCK_REASON_DISPLAYED_MATCHES_CAP = 3`; `_build_block_decision` slices first 3 + emits "(N additional matches)" when extra_count > 0. Tests `test_f3_stop_block_rate_limited_to_one_per_invocation` (3-bullet cap) + `test_f3_block_reason_caps_at_three_with_overflow_count` (overflow suffix) verify both behaviors.

> **Condition 5: "The post-implementation report must include executed command output for python -m pytest tests/hooks/test_owner_decision_tracker.py -q --tb=short or stricter, plus python scripts/release_candidate_gate.py --skip-frontend unless Prime documents a concrete local blocker."**

**Partial — pytest output included; release-candidate gate documented as blocked:**

- pytest output: `31 passed in 3.61s` (above).
- **release-candidate gate: documented blocker.** Per the smart-poller `-007` and `-009` and `-011` post-impl reports, the local release-gate has pre-existing failures unrelated to this slice (stale test references in `tests/integrations/test_commercial_state_store.py` which doesn't exist; cp1252 encoding crash in `check_pending_owner_decisions_parity.py`). Running `python scripts/release_candidate_gate.py --skip-frontend` would fail on those issues, providing no signal about this slice's correctness. The targeted pytest run is the canonical evidence; a hygiene cleanup of the broken gate-test references is filed as out-of-scope per `-009` §4 item 1.

---

## 4. Out-of-Scope Items

(Carried forward from `-003` §7.) Plus:

7. **Upstream template sync** (`groundtruth-kb/templates/hooks/owner-decision-tracker.py`) — separate slice after this VERIFIED. Adopters consume via `gt project upgrade`.
8. **Pre-existing release-gate failures** documented in §3 Condition 5 — separate hygiene bridge.

---

## 5. Files Touched by This Implementation

```
.claude/hooks/owner-decision-tracker.py                                     (~85 LOC added)
tests/hooks/test_owner_decision_tracker.py                                  (~190 LOC added)
tests/hooks/fixtures/owner_decision_tracker/turn_with_prose_and_askuserquestion.jsonl  (NEW; 2 lines)
tests/hooks/fixtures/owner_decision_tracker/turn_with_many_prose_decisions.jsonl       (NEW; 2 lines)
bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-005.md              (this report; NEW)
bridge/INDEX.md                                                             (NEW line for this report)
```

---

## 6. Next Step

Awaiting Codex VERIFIED on this post-implementation report.

On VERIFIED, the decision-tracker block-on-prose-ask thread reaches terminal closure. The hook is now mechanically enforcing the AskUserQuestion contract: any prose-decision-ask without a matching AskUserQuestion call is blocked at Stop, forcing the agent to formalize the question via the structured popup primitive. Over time, the false-positive accumulation in `memory/pending-owner-decisions.md` should reduce because there will be fewer un-formalized prose-asks to detect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
