# Implementation Proposal — Worker-Context-Aware AUQ Enforcement (Slice 2 of 4)

bridge_kind: prime_proposal

## Summary

Make the owner-decision-tracker Stop hook context-aware. When the spawned-worker
env var `GTKB_BRIDGE_POLLER_RUN_ID` is present, the hook detects prose
decision-asks but:

1. Does NOT emit the `{"decision":"block"}` Stop signal (workers cannot
   recover from turn-end refusal; they would simply hang).
2. Writes a structured `requires_owner_decision` payload to the worker's
   dispatch-run output directory so the dispatching parent / next interactive
   session can surface it.
3. Still appends the detected ask to `memory/pending-owner-decisions.md` so
   the durable pending-decision list is not lost.

Owner-context behavior is unchanged: in interactive sessions, the existing
block-decision path remains the canonical AUQ enforcement signal.

Also amends the dispatch prompt in `_dispatch_prompt` to instruct workers
that interactive tools are unavailable and that owner decisions must be
reported via the bridge artifact rather than asked inline.

## Dependency on Slice 1

Implementation execution is gated on `gtkb-prime-worker-permission-profile-slice-1`
reaching `GO`. Codex may review this proposal in parallel; Prime will not
land code changes until Slice 1's `_harness_command` flags are in place,
because Slice 2's structural-context test fixtures will be easier to write
once `--allowed-tools` excludes AskUserQuestion (the worker's "I need a
decision" path is forced through prose, not AUQ).

Codex may NO-GO this proposal independently of Slice 1 if Slice 2's design
has defects; the dependency is on implementation order, not review order.

## Background

The current Stop hook at `.claude/hooks/owner-decision-tracker.py:910-960`
emits `{"decision":"block"}` when prose decision-asks are detected without
a same-turn AskUserQuestion call. In owner context this is correct: it
forces the agent to formalize the decision via AUQ before turn-end.

In worker context this is wrong: a worker that prose-asks (because it
genuinely needs owner input on a NO-GO clarification or scope question)
gets blocked, but no owner is present to answer. The worker subprocess
hangs until its harness timeout. The dispatch logs show `permission denied`
on attempted Edit calls as a downstream symptom (the worker tries to write
the post-impl report; the block prevents turn-end; the report never lands).

The env var `GTKB_BRIDGE_POLLER_RUN_ID` is already set on every spawned
child per `cross_harness_bridge_trigger.py:753`. Detection is one
`os.environ.get()` call away.

## Scope (Slice 2 of 4)

In scope:

1. Add worker-context detection to `_stop_handler`. Branch the block-emission
   decision on `GTKB_BRIDGE_POLLER_RUN_ID` presence.
2. In worker context, write `requires_owner_decision.json` to
   `.gtkb-state/cross-harness-trigger/dispatch-runs/<run-id>.owner-decision-requested.json`
   with fields: `run_id`, `detected_patterns` (list of `(name, snippet)`),
   `transcript_path`, `timestamp_utc`.
3. Update `_dispatch_prompt` in `cross_harness_bridge_trigger.py` to add
   one paragraph: "Interactive tools including AskUserQuestion are
   unavailable in this dispatched-worker context. If an owner decision is
   required, stop and report the required decision in the bridge artifact
   (post-implementation report or REVISED proposal) rather than asking
   inline."
4. Unit tests covering both branches.

Out of scope for Slice 2:

- Slice 3 lock granularity (separate thread).
- Slice 4 end-to-end regression (separate thread).
- Surfacing the `requires_owner_decision.json` in startup payload — that's
  a SessionStart concern, separately tracked.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\.claude\hooks\owner-decision-tracker.py` — Stop hook source (the `_stop_handler` branch + helper additions).
- `E:\GT-KB\scripts\cross_harness_bridge_trigger.py` — `_dispatch_prompt` text addition.
- `E:\GT-KB\platform_tests\hooks\test_owner_decision_tracker.py` (if present) or co-located test module — Slice 2 unit tests.
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py` — `_dispatch_prompt` text assertion test.
- `E:\GT-KB\.gtkb-state\cross-harness-trigger\dispatch-runs\<run-id>.owner-decision-requested.json` — worker-written context artifact (in-root).

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` — deterministic policy engine; this slice adds a context branch to the existing engine, no new classifier.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic-only enforcement; context detection is an env-var presence check.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from linked specs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — file bridge as canonical workflow state.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — canonical init keyword is the worker-context signal at SessionStart; the env var is its companion at Stop time.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — emitter authority; `GTKB_BRIDGE_POLLER_RUN_ID` is the durable worker-context marker.
- `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the Only Valid Owner-Decision Channel" — owner-context rule unchanged; worker-context exception narrowly scoped here.
- `.claude/rules/bridge-essential.md` § Bridge Dispatch Enablement Contract — workers act through the trigger; their context is the trigger's responsibility.
- `.claude/rules/file-bridge-protocol.md` — workers report findings through bridge artifacts.
- `.claude/rules/codex-review-gate.md` — review gate requirements.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement boundary; this proposal does not touch `applications/` paths or modify root-boundary behavior. Cited per path-match acknowledgement (the proposal references `.claude/rules/file-bridge-protocol.md`); no modification proposed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance discipline (advisory). The change adds a structured `requires_owner_decision.json` artifact for workers and preserves the durable pending-owner-decisions file.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development (advisory). Traceability preserved across worker dispatch run artifacts, the durable pending file, and the parent bridge thread.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle states (advisory). The proposal lifecycle is NEW → (GO/NO-GO) → VERIFIED per the file-bridge-protocol contract.

## Prior Deliberations

- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` REVISED-1 Codex GO at `-004` — established the Stop-mode block decision; this slice narrows it to owner context only.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` VERIFIED — Sub-slice A activated the tracker.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*` — the substrate that sets `GTKB_BRIDGE_POLLER_RUN_ID` on child env.
- Sibling thread `gtkb-prime-worker-permission-profile-slice-1-001.md` (NEW) — Slice 1 of this 4-slice fix.
- Sibling thread `gtkb-decision-tracker-cached-pending-block-exclusion-001.md` (NEW) — touches the same hook for a different false-positive class; merge conflict risk noted in Risks.

## Owner Decisions / Input

Owner AskUserQuestion answer in S350 (2026-05-14): "Which slicing strategy for the Prime-worker-delivery fix?" → **4-slice sequence (recommended)**. This authorizes Slice 2 as an independent proposal per the 4-slice plan.

Owner directive in S350 (2026-05-14): "Please draft Slices 2-4 in parallel." This authorizes filing Slices 2-4 before Slice 1 reaches GO, with implementation execution gated on Slice 1 GO per the Dependency section above.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-AUQ-POLICY-ENGINE-001` defines the engine; adding a context-aware branch is engine-internal. The AUQ-only rule at `.claude/rules/prime-builder-role.md` continues to apply to owner sessions; worker sessions are a new context that the rule did not previously address, but the workaround (stop-and-report via bridge artifact) is consistent with the rule's intent (no decision lost; no opaque hangs).

## target_paths

- `.claude/hooks/owner-decision-tracker.py` (`_stop_handler` branch + `requires_owner_decision.json` writer)
- `scripts/cross_harness_bridge_trigger.py` (`_dispatch_prompt` text addition)
- `platform_tests/hooks/test_owner_decision_tracker.py` if it exists, else co-located test file (worker-context branch tests)
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (`_dispatch_prompt` text assertion test)

## Implementation Plan

1. **Add `_is_worker_context()` helper** in `.claude/hooks/owner-decision-tracker.py`:
   ```python
   def _is_worker_context() -> bool:
       return bool(os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"))
   ```
2. **Modify `_stop_handler`** at line 910 onwards:
   - When prose-decision-ask is detected AND `_is_worker_context()` is True:
     - Write `requires_owner_decision.json` to the dispatch-runs subdir.
     - Append to `memory/pending-owner-decisions.md` as today.
     - Return `None` (no block decision). Worker turn ends; report is durable.
   - When prose-decision-ask is detected AND `_is_worker_context()` is False:
     - Existing behavior (return `{"decision":"block", "reason":...}`).
3. **Add `_write_requires_owner_decision()`** helper that resolves the dispatch-runs path from `GTKB_PROJECT_ROOT` (which the trigger also sets on the child env) and writes the JSON payload.
4. **Update `_dispatch_prompt`** in `scripts/cross_harness_bridge_trigger.py:330-377`:
   - Add one paragraph after `role_line`: "Interactive tools including AskUserQuestion are unavailable in this dispatched-worker context. If an owner decision is required, stop and report the required decision in the bridge artifact (post-implementation report or REVISED proposal) rather than asking inline. The owner-decision-tracker will capture detected prose asks to `.gtkb-state/cross-harness-trigger/dispatch-runs/<run-id>.owner-decision-requested.json` for the dispatching parent to surface."
5. **Unit tests**:
   - `test_stop_handler_worker_context_writes_requires_owner_decision_json`: env var set + prose ask → JSON file written, no block decision returned.
   - `test_stop_handler_worker_context_still_appends_durable_pending`: env var set + prose ask → `memory/pending-owner-decisions.md` mutation observed (existing durability invariant preserved).
   - `test_stop_handler_owner_context_unchanged_block_decision`: env var unset + prose ask → block decision returned (regression check).
   - `test_dispatch_prompt_contains_worker_context_interactive_tools_unavailable_paragraph`: `_dispatch_prompt(target, items, max_items)` returns text containing the worker-context paragraph.

## Spec-to-Test Mapping

- `SPEC-AUQ-POLICY-ENGINE-001` → all four tests (engine behavior across both context branches).
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` → all tests assert deterministic env-var + regex behavior, no LLM input.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` → `test_stop_handler_worker_context_writes_requires_owner_decision_json` validates the env-var marker drives context detection consistently.

## Risks

- **Merge conflict with sibling thread `gtkb-decision-tracker-cached-pending-block-exclusion-001`**: both touch `owner-decision-tracker.py`. *Mitigation:* sibling thread touches `_is_inside_structural_context` (top of file, structural pre-check); this thread touches `_stop_handler` (bottom of file, control flow). Distinct functions; mechanical merge should succeed. Codex review of one should land first; the second rebases.
- **Worker writes to dispatch-runs subdir but parent has cleaned up the run**: if the parent process exits before the worker stops, the dispatch-runs directory might not exist. *Mitigation:* writer uses `path.parent.mkdir(parents=True, exist_ok=True)` and writes atomically. If write fails, the durable pending-decisions file still captures the ask (no information loss).
- **Env-var leak into non-worker context**: if a developer manually sets `GTKB_BRIDGE_POLLER_RUN_ID` in their interactive shell, the owner-context block decision would be suppressed. *Mitigation:* documented as operator-only escape hatch; not a defect class. Tests assert the unset state matches owner context.

## Rollback

Remove `_is_worker_context()`, `_write_requires_owner_decision()`, and the
worker-context branch in `_stop_handler`. Revert `_dispatch_prompt` paragraph.
Hook reverts to its current owner-only behavior.

## Verification Procedure

1. Run `python -m pytest .claude/hooks/test_owner_decision_tracker.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`.
2. Manual smoke: set `GTKB_BRIDGE_POLLER_RUN_ID=test-run-1 python .claude/hooks/owner-decision-tracker.py --mode stop < fixture_transcript_with_prose_ask.jsonl`; assert `requires_owner_decision.json` exists and stdout has no block decision.
3. Regression smoke: same fixture without env var; assert block decision JSON on stdout.

## Acceptance Criteria

- Worker context detection via `GTKB_BRIDGE_POLLER_RUN_ID` is deterministic.
- Worker-context branch writes `requires_owner_decision.json` and returns no block.
- Owner-context branch returns block decision (regression intact).
- Dispatch prompt instructs workers to report owner decisions via bridge artifact.
- All preflights pass for this proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
