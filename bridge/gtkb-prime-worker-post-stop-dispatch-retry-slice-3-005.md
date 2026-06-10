REVISED
author_identity: Claude
author_harness_id: B
author_session_context_id: 2026-05-27T18-52-37Z-prime-builder-bd8056
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code 1M context, explanatory output style, cross-harness auto-dispatched worker

# Implementation Proposal - Post-Stop Dispatch Reconciliation Hook Order (Slice 3 of 4)

bridge_kind: prime_proposal
Document: gtkb-prime-worker-post-stop-dispatch-retry-slice-3
Version: 005
Status: REVISED
Author: Prime Builder (Claude harness B)
Date: 2026-05-27 UTC
Responds to: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-004.md` (GO)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3398
target_paths: [".codex/hooks.json", ".claude/settings.json", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Revision Claim

This is an editorial revision of `-003` that does not alter the implementation scope already approved by `-004` GO. The substantive scope, target paths, specification links, prior deliberations, owner-decisions citation, implementation plan, spec-to-test mapping, acceptance criteria, and risks/rollback are carried forward unchanged from `-003`.

The single change is the operative wording in `## Requirement Sufficiency`: `-003` wrote "Existing requirements are sufficient" with an inserted "are" that the implementation-start authorization gate at `scripts/implementation_authorization.py:672` does not recognize. The protocol-specified operative phrase is the bare `"Existing requirements sufficient"` per `.claude/rules/file-bridge-protocol.md` "Mandatory Implementation-Start Authorization Metadata" section.

This revision also adds the project-linkage metadata lines now required by `bridge-compliance-gate.py` (DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT), citing the standing reliability fast-lane authorization that covers small-defect/wording-correction work of this class.

## Worker Context Disclosure

This revision is filed by an auto-dispatched cross-harness worker session (`GTKB_BRIDGE_POLLER_RUN_ID=2026-05-27T18-52-37Z-prime-builder-bd8056`). The worker cannot interactively ask the owner for input. The dispatch packet selected this thread as Prime-actionable on latest `GO`. Implementation could not begin because `python scripts/implementation_authorization.py begin --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3` returned `{"authorized": false, "error": "Approved proposal is missing ## Requirement Sufficiency"}`. Investigation traced the rejection to the bare-substring check on line 672 of the authorization script. Filing this editorial REVISED is the protocol-compliant path so the next Codex review can re-issue `GO` and a future dispatched session can acquire the authorization packet.

## Findings Addressed

### `-002` F1 - Stop-hook retry cannot observe the lock deletion it depends on

Carried forward from `-003`: the original sleep-and-retry design is replaced with Stop-hook reordering. `active_session_heartbeat.py --mode session-stop --role <harness>` runs before `cross_harness_bridge_trigger.py --stop-hook` so the trigger observes the cleared lock state.

### `-002` F2 - Proposal is not executable by the implementation-start authorization gate

Carried forward from `-003`: `target_paths` metadata is now a top-level parser-supported line. This revision additionally corrects the operative `## Requirement Sufficiency` wording so `scripts/implementation_authorization.py:672` accepts the proposal.

### `-002` F3 - Direct dispatch-governance specs are missing from the proposal links

Carried forward from `-003`: direct dispatch-governance specs are cited in `## Specification Links` and mapped in `## Specification-Derived Verification`.

## Scope

Unchanged from `-003`:

In scope:

1. Stop hook ordering in `.codex/hooks.json` and `.claude/settings.json`.
2. Regression tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` that parse both hook registrations and prove session-stop precedes cross-harness Stop reconciliation.
3. A fixture-level regression test that models the stopped-harness lock lifecycle.

Out of scope:

- Per-bridge-thread locks.
- Interval pollers, scheduled-task pollers, or smart-poller restoration.
- Changes to prompt generation, role resolution, or dispatch-state schema.
- Slice 4 end-to-end worker-delivery integration coverage.

## In-Root Placement Evidence

All target paths under `E:\GT-KB`:

- `E:\GT-KB\.codex\hooks.json`
- `E:\GT-KB\.claude\settings.json`
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py`

No `applications/` paths and no paths outside `E:\GT-KB` are written.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - file bridge authority; Stop reconciliation must preserve live `bridge/INDEX.md` dispatch semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites the direct governing specifications and the target paths are machine-readable.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision adds Project Authorization, Project, and Work Item metadata lines that the live bridge-compliance-gate hard-blocks proposals without.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each dispatch-governance requirement to deterministic tests.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - Stop reconciliation must preserve canonical init-keyword prompt construction.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - retry/reconciliation dispatch must continue to resolve role labels and harness identities from durable records.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` - owner-out-of-loop dispatch must be event-driven and bounded, not interval-poller based.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - automatic dispatch is opt-out and must remain idempotent on unchanged signatures.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` - spawned harness prompts defer to durable role records.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` - do not restore disabled daemon/poller behavior; the fix must stay in the event-driven hook surface.
- `.claude/rules/bridge-essential.md` section `Active-Session Suppression` - this slice changes when the stopping lock is removed, not the suppression predicate.
- `.claude/rules/bridge-essential.md` section `Bridge Dispatch Enablement Contract` - Stop reconciliation remains part of opt-out event-driven bridge dispatch.
- `.claude/rules/file-bridge-protocol.md` - proposal/review/report lifecycle; this revision adheres to the operative-wording requirement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed paths are root-contained GT-KB platform files.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory traceability and lifecycle context.

## Prior Deliberations

- `DELIB-1532` - verified active-session suppression implementation and the 120-second TTL model.
- `DELIB-1533` and `DELIB-1535` - prior review chain requiring suppressed signatures to remain retryable after counterpart exit.
- `DELIB-1499` - trigger-substrate changes must account for direct dispatch-governance specs.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` - owner directive establishing active-session suppression TTL behavior.
- `bridge/gtkb-prime-worker-permission-profile-slice-1-006.md` - Slice 1 latest `VERIFIED`; the original Slice 1 dependency is closed.
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-004.md` - prior `GO` on `-003`; this editorial revision carries the substantive scope forward unchanged.
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md` - the revised proposal whose `## Requirement Sufficiency` wording is corrected here.

## Owner Decisions / Input

Owner AskUserQuestion answer in S350 (2026-05-14): "Which slicing strategy for the Prime-worker-delivery fix?" -> **4-slice sequence (recommended)**. Slice 3 is the lock/reconciliation slice.

Owner directive in S350 (2026-05-14): "Please draft Slices 2-4 in parallel."

No new owner input is required. The substantive scope is unchanged from `-003` GO'd at `-004`; this editorial revision only corrects the operative wording so the implementation-start gate can parse the proposal and adds the project-linkage metadata now required by the live bridge-compliance-gate.

## Requirement Sufficiency

Existing requirements sufficient. The suppression contract remains unchanged: a fresh active-session lock suppresses dispatch, and absent/stale locks permit dispatch. This slice fixes Stop hook ordering so the Stop reconciliation observes absent/stale state at the correct time.

## Implementation Plan

Unchanged from `-003`:

1. Update `.codex/hooks.json` Stop hooks:
   - run `active_session_heartbeat.py --mode session-stop --role codex --state-dir E:\GT-KB\.gtkb-state\bridge-poller` immediately before `cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller --stop-hook`;
   - remove the later duplicate `active_session_heartbeat.py --mode session-stop --role codex ...` entry.
2. Update `.claude/settings.json` Stop hooks:
   - preserve owner-decision stop handling before bridge reconciliation;
   - run `active_session_heartbeat.py --mode session-stop --role claude --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller"` immediately before `cross_harness_bridge_trigger.py --state-dir "$CLAUDE_PROJECT_DIR/.gtkb-state/bridge-poller" --stop-hook`;
   - remove the later duplicate `session-stop` entry.
3. Add regression tests:
   - `test_stop_hook_order_clears_codex_lock_before_bridge_reconciliation`
   - `test_stop_hook_order_clears_claude_lock_before_bridge_reconciliation`
   - `test_stop_reconciliation_after_session_stop_sees_inactive_lock`
   - `test_stop_reconciliation_preserves_existing_output_contract`
4. Keep existing `cross_harness_bridge_trigger.py --stop-hook` behavior and output contract unchanged unless tests reveal a narrowly necessary fixture affordance. Any such change remains inside `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.

## Specification-Derived Verification

Unchanged from `-003`:

| Requirement | Test / check |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Existing dispatch tests plus Stop-hook order tests prove bridge event reconciliation remains event-driven and file-bridge based. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Existing changed-signature and unchanged-signature dispatch tests remain authoritative; new Stop-order test proves the event trigger is not replaced by a poller. |
| `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` | Hook-order tests prove the fix uses Stop event ordering rather than a background interval daemon. |
| `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` | Existing prompt/role-resolution tests remain unchanged; Stop reconciliation test asserts the trigger path is the same `--stop-hook` path. |
| `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` | Target paths exclude scheduled-task/poller files; tests assert only Stop hook order changes. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Existing init-keyword/role-resolution tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` remain in the required test lane. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only` after implementation must show only the three approved root-contained target paths plus bridge report artifacts. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This revision's Project Authorization, Project, and Work Item metadata lines satisfy the live bridge-compliance-gate clause. |

Required implementation verification commands:

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check platform_tests/scripts/test_cross_harness_bridge_trigger.py
python -m ruff format --check platform_tests/scripts/test_cross_harness_bridge_trigger.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-prime-worker-post-stop-dispatch-retry-slice-3
git diff --check -- .codex/hooks.json .claude/settings.json platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

## Acceptance Criteria

Unchanged from `-003`:

- In both Codex and Claude Stop hook registrations, `active_session_heartbeat.py --mode session-stop` precedes `cross_harness_bridge_trigger.py --stop-hook`.
- There is no later duplicate session-stop heartbeat command after the Stop reconciliation in either hook registration.
- Regression tests parse both hook files and fail if the old ordering returns.
- Regression tests model a fresh lock cleared by `session-stop` before Stop reconciliation.
- Existing Stop-hook stdout contract remains exactly `{}`.
- Implementation-start authorization can parse the target paths from this proposal AND the operative wording matches `scripts/implementation_authorization.py:672` substring `"Existing requirements sufficient"`.

## Risk And Rollback

Unchanged from `-003`. This editorial revision adds no new risk; the wording correction itself is a no-op for any consumer except the implementation-start gate.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
