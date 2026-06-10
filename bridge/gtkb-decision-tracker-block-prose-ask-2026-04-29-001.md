NEW

# GTKB Decision-Tracker Stop-Hook Block-on-Prose-Ask Extension

**Status:** NEW (implementation proposal extending existing `.claude/hooks/owner-decision-tracker.py`)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Owner directive (this session): "It is exceptionally difficult to find and respond to textual requests in the flow of the chat." Owner approved Part 2 of the two-part fix: extend the existing tracker to mechanically block Stop when prose-decision-asks happen without `AskUserQuestion` in the same turn.

bridge_kind: prime_proposal
work_item_ids: [GTKB-DECISION-TRACKER-BLOCK-PROSE-ASK]
spec_ids: [PB-STANDING-BACKLOG-CONTINUITY-001]
parent_bridge: bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md (VERIFIED) — original Slice 1 of GTKB-GOV-OWNER-DECISION-SURFACING (work_list row 8 DONE)
target_project: agent-red (live hook in `.claude/hooks/`); upstream-template mirroring deferred to a separate slice
implementation_scope: hook-extension + tests
requires_review: true
requires_verification: true

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate.

**Primary spec served:**
- `PB-STANDING-BACKLOG-CONTINUITY-001` — provides the architectural authority for cross-session decision surfacing. KB-resolved per work_list row 8 closure (`GTKB-GOV-OWNER-DECISION-SURFACING` DONE at S315).

**Parent bridge (this proposal extends, not supersedes):**
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md` (GO; original Slice 1 design) — original tracker design with F3 constraint "Stop-mode is silent; durable-file is the sole Stop-mode output".
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED) — original Slice 1 closure.

**Governance specs / records that constrain this work:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` (KB-resolved) — bridge protocol authority; this hook reads `bridge/INDEX.md` indirectly via the tracker's transcript-parse path. Read-only.
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` (KB-resolved) — supports converting documented owner-decision-surfacing intent into mechanical block (this proposal's exact purpose).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — supports moving "I should remember to call AskUserQuestion" from AI-mediated convention to deterministic hook enforcement.

**Adjacent hooks (this proposal does not modify):**
- `.claude/hooks/bridge-compliance-gate.py` — separate hook; PreToolUse gate on bridge files.
- `.claude/hooks/spec-classifier.py` — separate hook; UserPromptSubmit advisory.

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol governing this proposal.
- `.claude/rules/codex-review-gate.md` — Codex must NO-GO unlinked proposals.

---

## Specification-Derived Verification (Test Mapping)

Per file-bridge-protocol Mandatory Specification-Derived Verification Gate. Each test below derives from the proposed behavior:

| Behavior | Test | Run via |
|----------|------|---------|
| Prose-decision-ask + zero AskUserQuestion calls in same turn -> Stop-mode emits `decision: block` with explanatory reason | `test_stop_blocks_when_prose_ask_without_ask_user_question` (extends `tests/hooks/test_owner_decision_tracker.py`) | `pytest tests/hooks/test_owner_decision_tracker.py -v` |
| Prose-decision-ask + at least one AskUserQuestion call in same turn -> Stop-mode does NOT block | `test_stop_does_not_block_when_ask_user_question_called_in_same_turn` | `pytest` |
| Zero prose-decision-asks -> Stop-mode does NOT block (existing append-to-file path preserved) | `test_stop_does_not_block_when_no_prose_ask_detected` | `pytest` |
| AskUserQuestion called WITH prose-asks -> append-to-file path still records the prose-detected questions to durable file (parallel to AskUserQuestion entries) | `test_durable_file_records_both_prose_and_ask_user_question_entries_when_both_present` | `pytest` |
| Block-decision emission preserves existing graceful-degradation contract: hook never crashes the session even on malformed transcript | `test_stop_block_emission_handles_malformed_transcript_gracefully` | `pytest` |
| F3-constraint reconciliation: existing "writes nothing to stdout in Stop mode" was about NUDGE TEXT; the new `decision: block` JSON is a control-flow signal, not nudge text | Documented in §1 design rationale; no test (constraint reconciliation, not behavior) | n/a |
| Hook performance: Stop-mode runtime under 200ms even with prose-pattern matching across full turn transcript | `test_stop_runtime_under_200ms_for_typical_turn_transcript` | `pytest` |
| Existing tracker tests continue to pass (non-regression) | `pytest tests/hooks/test_owner_decision_tracker.py -v` | `pytest` |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full hook test suite.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `DELIB-OWNER-DECISION-SURFACE-001` (or equivalent harvested deliberation from S315) — owner directive originating the GTKB-GOV-OWNER-DECISION-SURFACING program; this proposal extends that program.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-001.md` through `-006.md` — full original thread (NEW -> NO-GO -> REVISED -> GO -> impl -> post-impl -> VERIFIED).
- This session's owner statement: "It is exceptionally difficult to find and respond to textual requests in the flow of the chat" + APPROVE response to my proposed Part 2 (mechanical block extension).
- No prior deliberation reverses this approach. The existing tracker explicitly anticipated future enhancements; this proposal lands one of them.

---

## 1. Implementation Design

### 1.1 Existing Behavior (preserved)

The existing `owner-decision-tracker.py` Stop mode:
- Parses the just-completed turn's JSONL transcript for `AskUserQuestion` tool_use entries.
- Matches prose anti-patterns (5 patterns at lines 81-92: `offering_or_choice`, `should_i_or`, `awaiting_input`, `standing_by_for`, `your_decision_q`).
- Applies false-positive guards (lines 95-100) to avoid over-detection on abstract decision discussion.
- Appends unresolved entries to `memory/pending-owner-decisions.md` `## Pending` section.
- Moves same-turn-answered entries directly to `## Resolved`.
- Returns 0 (graceful degradation; never blocks).

### 1.2 New Behavior (added)

After existing parse + match + classification:
- If at least one prose-decision-ask was detected in this turn AND zero AskUserQuestion tool_use entries exist in the same turn:
  - Emit `{"decision": "block", "reason": "<message>"}` to stdout.
  - Reason text: lists the detected patterns (id + matching text excerpt) and instructs the agent to call AskUserQuestion to formalize the decision request.
- Otherwise: continue with existing behavior (silent stdout; durable-file is the sole output).

The block decision is a Claude Code hook control-flow signal that prevents the agent from ending the turn. The agent (Claude) receives the reason text as additionalContext and continues the turn — at which point it can call AskUserQuestion to satisfy the requirement.

### 1.3 F3-Constraint Reconciliation (preserves prior design)

The original Slice 1's Codex `-004` GO §F3 said "Stop-mode is silent; durable-file is the sole Stop-mode output". That constraint was specifically about NUDGE TEXT being injected back into the agent's context for behavioral nudging. The new `decision: block` JSON is fundamentally different:
- It is a control-flow signal (prevents stop), not a nudge or advisory message.
- It only fires under a specific hard condition (prose-ask without AskUserQuestion); the typical turn produces no stdout at all.
- It is bounded in frequency: at most once per turn, only when the explicit failure mode occurs.

This proposal does NOT revise the F3 constraint; it adds a new output channel that is type-distinct from the channel F3 banned. The bridge review may direct otherwise.

### 1.4 Hook Output JSON Schema (block case)

```json
{
  "decision": "block",
  "reason": "Owner-decision-tracker: prose decision ask(s) detected without AskUserQuestion call this turn.\n\nMatched patterns:\n  - awaiting_input at offset 12345: 'awaiting your direction'\n  - offering_or_choice at offset 14567: 'want me to revise or pause?'\n\nResolution: call AskUserQuestion with the detected questions formalized as structured options. The dialog produces a clickable popup the user can respond to inline; prose questions get lost in chat scrollback.\n\nThis hook fires per DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 + owner directive (this session). To bypass: file a bridge proposal."
}
```

The reason text is verbose by design; agents receive it as additionalContext, and the verbosity surfaces both the failure detection AND the resolution path.

### 1.5 Mode Routing

The existing hook uses `--mode` argument: `stop` and `user-prompt-submit`. The new block-decision logic only applies in `stop` mode. The `user-prompt-submit` mode is unchanged.

---

## 2. Files Touched

**Modified:**
- `.claude/hooks/owner-decision-tracker.py` — add block-decision emission per §1.2 (estimated +30 LOC).
- `tests/hooks/test_owner_decision_tracker.py` — add 5 new tests per Specification-Derived Verification table (estimated +120 LOC).

**Not touched (deferred to separate slice):**
- `groundtruth-kb/templates/hooks/owner-decision-tracker.py` (upstream template mirror) — adopters consume the modified hook via `gt project upgrade` after this slice VERIFIED + a separate upstream-template-sync slice. Out of this slice's scope to keep the change tight.
- `groundtruth-kb/templates/managed-artifacts.toml` — no new registration entries (the existing entry at the registry already registers this hook; only the hook script body changes).

**Other:**
- `scripts/release_candidate_gate.py` — already runs the hook tests; no wiring change needed.
- `memory/work_list.md` — on VERIFIED, add a closure row (or extend existing GTKB-GOV-OWNER-DECISION-SURFACING row 8 with this enhancement).

---

## 3. Verification Plan

### 3.1 Tests (per §Specification-Derived Verification)

```bash
pytest tests/hooks/test_owner_decision_tracker.py -v
python scripts/release_candidate_gate.py --skip-frontend
```

All 5 new tests + existing tests pass.

### 3.2 Manual Verification

After implementation, demonstrate the block:
1. Write a Stop-event payload that simulates a turn ending with prose-decision-ask in the agent's output AND zero AskUserQuestion tool_use entries.
2. Pipe to `python .claude/hooks/owner-decision-tracker.py --mode stop`.
3. Verify stdout contains `{"decision": "block", ...}` with the expected reason text.
4. Repeat with AskUserQuestion present in the synthetic turn -- verify stdout is empty `{}` (not blocked).

### 3.3 Non-Regression

- Existing `test_owner_decision_tracker.py` continues to pass.
- `memory/pending-owner-decisions.md` durable-file format unchanged.
- UserPromptSubmit-mode behavior unchanged.

---

## 4. Acceptance Criteria

1. Functional: all tests in §Specification-Derived Verification pass.
2. F3 reconciliation: documented in §1.3; the new `decision: block` JSON is type-distinct from the nudge-text channel F3 banned.
3. Performance: hook runtime under 200ms for typical turn transcripts (large transcripts may exceed; out of scope for tightening).
4. Graceful degradation: hook never crashes the session even on malformed transcripts (existing contract preserved).
5. Mechanical enforcement: a synthetic turn with prose-ask + no AskUserQuestion produces `decision: block` exit; agent's next turn has the reason in context.
6. Bypass path: nothing in the hook implementation is irreversible — restoration to pre-block behavior is a single `git revert` of the implementation commit.

---

## 5. Sequencing and Concurrency

Internal: single coherent slice (one hook script + tests).

External:
- Independent of all currently-in-flight bridges. No file-collisions with `gtkb-membase-effective-use-recovery-slice-a-event-surfacer`, `gtkb-spec-lifecycle-schema`, `gtkb-active-workspace-declaration-architecture`, or others.
- Adopter-side upstream-template sync deferred to a separate slice (out of scope here).

Concurrency: hook is read-only against transcript JSONL; only durable-file writes use atomic-rename (pre-existing pattern).

---

## 6. Project Root Boundary

Per `.claude/rules/project-root-boundary.md`:
- All artifacts under `E:\GT-KB`.
- Live hook in `E:\GT-KB\.claude\hooks\`.
- Tests in `E:\GT-KB\tests\hooks\`.
- No external paths.

---

## 7. Out of Scope

- Upstream template sync (`groundtruth-kb/templates/hooks/owner-decision-tracker.py`) — separate slice after this VERIFIED.
- Modifying prose-pattern detection (5 patterns at lines 81-92 are unchanged).
- Modifying false-positive guards (3 patterns at lines 96-99 unchanged).
- Modifying UserPromptSubmit mode behavior (unchanged).
- Cross-harness Codex-side equivalent (separate slice; Codex has its own hook system).
- Changing the durable-file format.
- Deleting any prior pending entries during the migration (append-only behavior preserved).

---

## 8. Rollback Plan

To disable the block-on-prose-ask behavior:
1. `git revert <impl-commit>` reverts both the hook script change and the new tests.
2. Existing tracker behavior (prose + AskUserQuestion detection + durable-file append) preserved fully.
3. No KB or DA state affected (hook is observability + control-flow only; no KB writes).

To partially disable while keeping detection:
- Edit the hook script to set a feature flag `EMIT_BLOCK_ON_UNFORMALIZED_PROSE_ASK = False` (also added by this slice as a top-level constant for runtime toggling). Changes the block emission to silent append-only.

---

## 9. Open Questions for Loyal Opposition Review

1. F3 reconciliation per §1.3: is the type-distinction between control-flow JSON and nudge text sufficient justification, or should this proposal explicitly REVISE the F3 constraint (with corresponding work_list row 8 update)?
2. Reason text verbosity per §1.4: the reason includes pattern excerpts + resolution instructions. Codex preference for shorter or more diagnostic-only?
3. Should the feature flag in §8's partial-disable path be a top-level constant (added by this slice) or an env var (e.g., `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0`)? Env var allows runtime toggling without code changes.
4. Performance cap: §4.3 sets 200ms. Codex preference for tighter (100ms) or looser?
5. Block-on-multi-pattern-asks: if 5 prose patterns match in one turn, the reason text lists all 5. Should it cap at the first 3 to keep the additionalContext concise?

---

## 10. Aligns With

- Owner directive (this session): mechanical popup decision dialog when user input requested.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (move convention to mechanical enforcement).
- DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 (mandatory mechanical enforcement when documented intent exists).
- PB-STANDING-BACKLOG-CONTINUITY-001 (cross-session decision continuity via durable-file).
- AskUserQuestion tool (Claude Code primitive that produces inline popup dialog).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
