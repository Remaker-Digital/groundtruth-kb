REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - Post-Stop Dispatch Reconciliation Hook Order (Slice 3 of 4)

bridge_kind: prime_proposal
Document: gtkb-prime-worker-post-stop-dispatch-retry-slice-3
Version: 003
Status: REVISED
Author: Prime Builder (Codex harness A)
Date: 2026-05-20 UTC
Responds to: `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-002.md`

target_paths: [".codex/hooks.json", ".claude/settings.json", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Revision Claim

This revision addresses the `-002` NO-GO by replacing the unworkable in-script sleep-and-retry design with a Stop hook order correction: the stopping harness clears its own active-session lock before `cross_harness_bridge_trigger.py --stop-hook` runs. The existing Stop reconciliation pass then observes the real inactive state and can dispatch previously suppressed signatures without waiting for an unrelated later trigger.

The revised implementation is configuration plus regression tests. It does not restore interval pollers, does not introduce per-thread locks, does not alter dispatch prompt construction, and does not mutate MemBase.

## Findings Addressed

### F1 - Stop-hook retry cannot observe the lock deletion it depends on

Response: Accepted. The original proposal depended on sleeping inside `cross_harness_bridge_trigger.py --stop-hook` while the same Stop hook's `active_session_heartbeat.py --mode session-stop` command had not yet run. This revision changes the design to the first acceptable shape named in the NO-GO: reorder the Stop hooks so `active_session_heartbeat.py --mode session-stop --role <harness>` runs before `cross_harness_bridge_trigger.py --stop-hook`.

Concrete revised hook order:

- `.codex/hooks.json`: in the `Stop` hook list, replace the pre-trigger `active_session_heartbeat.py --mode tool-use --role codex ...` refresh with `active_session_heartbeat.py --mode session-stop --role codex ...`, run it immediately before `cross_harness_bridge_trigger.py --stop-hook`, and remove the later duplicate `session-stop` command.
- `.claude/settings.json`: in the `Stop` hook list, keep owner-decision stop handling before bridge reconciliation, then run `active_session_heartbeat.py --mode session-stop --role claude ...` immediately before `cross_harness_bridge_trigger.py --stop-hook`, and remove the later duplicate `session-stop` command.

With this order, the trigger does not need to infer or ignore a stopping harness. It sees the same state directory that the heartbeat helper just updated, and `check_counterpart_active()` returns false for the stopping harness because the lock has already been removed.

### F2 - Proposal is not executable by the implementation-start authorization gate

Response: Accepted. This revision adds a top-level parser-supported metadata line:

```text
target_paths: [".codex/hooks.json", ".claude/settings.json", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]
```

The ambiguous prose-only `## target_paths` shape from `-001` is removed as the authorization source. The write set is concrete and bounded.

### F3 - Direct dispatch-governance specs are missing from the proposal links

Response: Accepted. This revision adds the direct dispatch-governance specs to `Specification Links` and maps them to regression checks in `Specification-Derived Verification`.

## Scope

In scope:

1. Stop hook ordering in `.codex/hooks.json` and `.claude/settings.json`.
2. Regression tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` that parse both hook registrations and prove session-stop precedes cross-harness Stop reconciliation.
3. A fixture-level regression test that models the stopped-harness lock lifecycle: active lock exists, `active_session_heartbeat.py --mode session-stop` clears it, then Stop reconciliation can evaluate dispatch without active-session suppression.

Out of scope:

- Per-bridge-thread locks.
- Interval pollers, scheduled-task pollers, or smart-poller restoration.
- Changes to prompt generation, role resolution, or dispatch-state schema.
- Slice 4 end-to-end worker-delivery integration coverage.

## In-Root Placement Evidence

All target paths are under `E:\GT-KB`:

- `E:\GT-KB\.codex\hooks.json`
- `E:\GT-KB\.claude\settings.json`
- `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py`

No `applications/` paths and no paths outside `E:\GT-KB` are written.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - file bridge authority; Stop reconciliation must preserve live `bridge/INDEX.md` dispatch semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites the direct governing specifications and the target paths are machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each dispatch-governance requirement to deterministic tests.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - Stop reconciliation must preserve canonical init-keyword prompt construction.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - retry/reconciliation dispatch must continue to resolve role labels and harness identities from durable records.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` - owner-out-of-loop dispatch must be event-driven and bounded, not interval-poller based.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - automatic dispatch is opt-out and must remain idempotent on unchanged signatures.
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` - spawned harness prompts defer to durable role records instead of hard-coded vendor assumptions.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` - do not restore disabled daemon/poller behavior; the fix must stay in the event-driven hook surface.
- `.claude/rules/bridge-essential.md` section `Active-Session Suppression` - this slice changes when the stopping lock is removed, not the suppression predicate.
- `.claude/rules/bridge-essential.md` section `Bridge Dispatch Enablement Contract` - Stop reconciliation remains part of opt-out event-driven bridge dispatch.
- `.claude/rules/file-bridge-protocol.md` - proposal/review/report lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed paths are root-contained GT-KB platform files.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory traceability and lifecycle context for the bridge artifact.

## Prior Deliberations

- `DELIB-1532` - verified active-session suppression implementation and the 120-second TTL model.
- `DELIB-1533` and `DELIB-1535` - prior review chain requiring suppressed signatures to remain retryable after counterpart exit.
- `DELIB-1499` - trigger-substrate changes must account for direct dispatch-governance specs.
- `DELIB-S337-OWNER-ACTIVE-SESSION-SUPPRESSION-DIRECTIVE-2026-05-09` - owner directive establishing active-session suppression TTL behavior.
- `bridge/gtkb-prime-worker-permission-profile-slice-1-004.md` - Slice 1 is latest `GO`, satisfying the stated dependency.
- `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-002.md` - current NO-GO addressed by this revision.

## Owner Decisions / Input

Owner AskUserQuestion answer in S350 (2026-05-14): "Which slicing strategy for the Prime-worker-delivery fix?" -> **4-slice sequence (recommended)**. Slice 3 is the lock/reconciliation slice.

Owner directive in S350 (2026-05-14): "Please draft Slices 2-4 in parallel."

No new owner input is required. This revision stays inside the owner-approved 4-slice worker-delivery sequence and selects a remediation shape explicitly offered by the Loyal Opposition NO-GO.

## Requirement Sufficiency

Existing requirements are sufficient. The suppression contract remains unchanged: a fresh active-session lock suppresses dispatch, and absent/stale locks permit dispatch. This slice fixes Stop hook ordering so the Stop reconciliation observes absent/stale state at the correct time.

## Implementation Plan

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
4. Keep existing `cross_harness_bridge_trigger.py --stop-hook` behavior and output contract unchanged unless tests reveal a narrowly necessary fixture affordance. Any such change must remain inside `platform_tests/scripts/test_cross_harness_bridge_trigger.py` and the existing script behavior surface; the authorized target list does not include production trigger code in this revision.

## Specification-Derived Verification

| Requirement | Test / check |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Existing dispatch tests plus Stop-hook order tests prove bridge event reconciliation remains event-driven and file-bridge based. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Existing changed-signature and unchanged-signature dispatch tests remain authoritative; new Stop-order test proves the event trigger is not replaced by a poller. |
| `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` | Hook-order tests prove the fix uses Stop event ordering rather than a background interval daemon. |
| `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` | Existing prompt/role-resolution tests remain unchanged; Stop reconciliation test asserts the trigger path is the same `--stop-hook` path and does not hard-code vendor role authority. |
| `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` | Target paths exclude scheduled-task/poller files; tests assert only Stop hook order changes. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` | Existing init-keyword/role-resolution tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` remain in the required test lane. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only` after implementation must show only the three approved root-contained target paths plus bridge report artifacts. |

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

- In both Codex and Claude Stop hook registrations, `active_session_heartbeat.py --mode session-stop` precedes `cross_harness_bridge_trigger.py --stop-hook`.
- There is no later duplicate session-stop heartbeat command after the Stop reconciliation in either hook registration.
- Regression tests parse both hook files and fail if the old ordering returns.
- Regression tests model a fresh lock cleared by `session-stop` before Stop reconciliation.
- Existing Stop-hook stdout contract remains exactly `{}`.
- Implementation-start authorization can parse the target paths from this proposal.

## Risk And Rollback

Risk: Clearing the active-session lock before later Stop housekeeping can make the harness appear inactive while remaining Stop hooks run. Impact is bounded because the reordered trigger is the immediate consumer of the cleared state, and the remaining hooks are non-interactive housekeeping.

Risk: Hook ordering differs subtly between Codex and Claude configuration formats. Mitigation is separate parser tests for each file.

Rollback: Restore the prior Stop hook order in `.codex/hooks.json` and `.claude/settings.json` and remove the added regression tests. The system returns to current behavior where suppressed signatures wait for a later trigger after Stop.
