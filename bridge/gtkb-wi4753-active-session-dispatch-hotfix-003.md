REVISED

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Bridge Hotfix (REVISED) - WI-4753 Active-Session Dispatch Suppression - Independent Review Re-Request

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4753
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_dispatch_per_document_lease.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

Document: gtkb-wi4753-active-session-dispatch-hotfix

## Revision Note - Independent Review Required (the reason for this REVISED)

The prior `-002` GO is a **same-session self-review** and is not a valid approval:
both the `-001` proposal and the `-002` GO carry the identical
`author_session_context_id: codex-wi4753-hotfix-20260622`. Per
`.claude/rules/file-bridge-protocol.md` (Review Independence Boundary) and
`.claude/rules/codex-review-gate.md` (Review Independence Gate), a review whose
session context equals the artifact author's session context is self-review and
must not stand as `GO`. Owner decision (AUQ, 2026-06-22): obtain a genuinely
independent Loyal Opposition review before implementation.

This REVISED carries the `-001` content forward unchanged in substance (the hotfix
design is sound) and is authored from a different session (`5b6095bb-...`, Claude
Prime Builder, harness B) so that any LO session other than the original
`codex-wi4753-hotfix-20260622` is an independent reviewer. Loyal Opposition: please
issue an independent `GO`/`NO-GO` on this thread. The full incident detail, problem
evidence, and design rationale remain in `-001`
(`bridge/gtkb-wi4753-active-session-dispatch-hotfix-001.md`); read the full thread
before verdict.

## Summary

Restore a target-active-session pre-spawn suppression check in
`scripts/cross_harness_bridge_trigger.py` so a hook-fired trigger does not spawn a
headless worker when the selected target harness already has a fresh foreground
active-session lock. Live incident: a Windows Console Window Host process storm from
repeated headless dispatch attempts while active Codex/Claude sessions are present.
`check_target_active(target, state_dir)` already exists but is no longer called on the
live dispatch path before spawning; this restores it as a pre-spawn guard ahead of
per-document lease filtering. Per-document lease behavior remains governing when no
target foreground session is active.

## Scope

In scope: restore the target-active-session pre-spawn suppression branch in
`scripts/cross_harness_bridge_trigger.py`; update the three focused tests so the
behavior is explicit (fresh target active-session lock suppresses spawning;
per-document leases still govern when no target active-session lock is present).
Out of scope: replacing the per-document lease registry; hook registration; retired
poller behavior; dispatch prompt content; project-authorization logic; MemBase
schemas; dispatch concurrency; reviewer routing.

## In-Root Placement Evidence (ADR-ISOLATION-APPLICATION-PLACEMENT-001 / CLAUSE-IN-ROOT)

All target paths are in-root under `E:\GT-KB` (`scripts/...`, `platform_tests/...`).
No out-of-root path is created, read as a live dependency, or required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge dispatch governed by status-bearing files + implementation authorization.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - live dispatch state must not create false/stale worker state while the target is visibly active.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - repeated headless spawning outweighs value while a foreground target session is present.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` - event-driven dispatch stays enabled; this adds a pre-spawn guard, not interval polling.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - auto-trigger-on-actionable-change preserved; spawn suppressed only when the target is already active.
- `SPEC-INTAKE-57a736` - per-document leases remain the same-document contention mechanism absent a fresh target active-session lock.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing links cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization/project/work item metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification mapped below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4753 is a single reliability work item, not a bulk backlog operation.

## Prior Deliberations

- `-001`/`-002` of this thread: original proposal + the self-reviewed GO this REVISED corrects.
- `DELIB-2512`/`DELIB-2513` - per-document lease substitution (this hotfix limits the restored active-session guard to an incident backpressure role, preserving leases).
- `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-006.md` - verified the per-document lease implementation.
- `bridge/gtkb-bridge-auto-dispatch-storm-004.md` - earlier spawn backpressure/rate-guard work; current incident shows active foreground target sessions still not suppressing hook-fired spawns.

## Owner Decisions / Input

- Owner approved the hotfix work in-session 2026-06-22 (`approve bridge hotfix`).
- Owner AUQ 2026-06-22 (this session): on discovering the `-002` self-review, the owner chose **"Independent review, then I implement"** - obtain an independent LO GO before Prime Builder implements. This REVISED executes that decision.

## Requirement Sufficiency

Existing requirements sufficient. Bridge-dispatch reliability + automation value/cost
requirements already require preventing runaway/low-value headless dispatch; the
per-document lease decision remains governing for document-level contention. This
hotfix adds an incident backpressure guard for the separate case where the target
harness itself is already active in the foreground. No new requirement.

## Specification-Derived Verification Plan

| Spec or behavior | Verification |
|---|---|
| `GOV-AUTOMATION-VALUE-VS-COST-001` active foreground target avoids duplicate headless cost | Focused test: a fresh target active-session lock returns the suppression token and does not dry-run/spawn. |
| `SPEC-INTAKE-57a736` per-document lease behavior valid without a foreground active lock | Existing lease tests still pass after updating the active-lock expectation. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` actionable signatures stay retryable | Suppression records `last_suppressed_signature`; no `last_dispatched_signature` written for active-session suppression. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest over the trigger suppression + per-document lease test modules; ruff check + ruff format --check on changed files. |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

## Acceptance Criteria

1. `run_trigger` checks the selected target's active-session lock before spawning a headless worker.
2. A fresh target active-session lock suppresses dispatch and records a suppressed signature for retry.
3. Per-document lease tests still prove same-document lease refusal and cross-document non-suppression when no target foreground session is active.
4. Focused pytest, ruff check, and ruff format check pass for the changed files.

## Recommended Commit Type

`fix:` - incident backpressure repair to bridge dispatch; no new capability surface.
