REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-cross-harness-trigger-active-session-target-naming
Project Authorization: PAUTH-WI-3485-ACTIVE-SESSION-SUPPRESSION-NAMING
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3485
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py", "platform_tests/scripts/test_bridge_dispatch_per_document_lease.py"]

# Implementation Proposal: Active-Session Suppression Target Naming Cleanup

## Summary

Complete WI-3485 by renaming the stale `counterpart` active-session suppression language in `scripts/cross_harness_bridge_trigger.py` and its targeted tests to target/receiver semantics. The current behavior checks whether the harness about to receive a dispatched bridge event already has its own active-session lock. The code and diagnostics still call that condition `counterpart_active_session_present`, which caused an incorrect mechanism explanation during owner discussion.

This proposal is naming and compatibility cleanup only. It preserves dispatch behavior, per-document lease substitution, heartbeat lock names, TTL behavior, and all active-session suppression decisions.

## Prior Deliberations

- Backlog row `WI-3485` records the naming defect: active-session suppression checks the receiver/target harness's own lock, not the counterpart's lock.
- Prior archived bridge context thread `gtkb-cross-harness-trigger-active-session-suppression-001` established the active-session suppression behavior being preserved; the specific historical file is cited as archival context, not as a live INDEX thread.
- Prior archived bridge context thread `gtkb-canonical-init-keyword-syntax-001` is adjacent context for active-session marker and init-keyword behavior; the specific historical file is cited as archival context, not as a live INDEX thread.
- `DELIB-2813` records the current owner directive to continue until the listed items are completed and supports the narrow PAUTH cited above.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1890` — seed=search; bridge_thread; Bridge thread: gtkb-cross-harness-trigger-active-session-suppression-001 (8 vers
- DA: `DELIB-1516` — seed=search; bridge_thread; Loyal Opposition Review - Claude Code Bridge-Status Thread Automation REVISED-1
- DA: `DELIB-2417` — seed=search; bridge_thread; Loyal Opposition Verification - Cross-Harness Trigger Dispatch-State Lag
- DA: `DELIB-1549` — seed=search; bridge_thread; Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-P
- DA: `DELIB-1512` — seed=search; bridge_thread; Loyal Opposition Review - Canonical Init-Keyword Syntax REVISED-3


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-1890` — seed=search; bridge_thread; Bridge thread: gtkb-cross-harness-trigger-active-session-suppression-001 (8 vers
- DA: `DELIB-1516` — seed=search; bridge_thread; Loyal Opposition Review - Claude Code Bridge-Status Thread Automation REVISED-1
- DA: `DELIB-2417` — seed=search; bridge_thread; Loyal Opposition Verification - Cross-Harness Trigger Dispatch-State Lag
- DA: `DELIB-1549` — seed=search; bridge_thread; Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-P
- DA: `DELIB-1512` — seed=search; bridge_thread; Loyal Opposition Review - Canonical Init-Keyword Syntax REVISED-3

## Owner Decisions / Input

No new owner decision is required. The active PAUTH authorizes source, test, and governance-evidence changes for WI-3485 while preserving normal bridge GO, implementation-start packet, post-implementation report, and Loyal Opposition verification gates.

## Specification Links

- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`

## Requirement Sufficiency

Existing requirements are sufficient. The implementation is constrained to renaming misleading active-session suppression semantics while preserving the already-governed dispatch and active-session behavior. No new specification is required before implementation.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep proposal and code changes credential-free; no environment values or secrets are introduced. | Bridge helper credential scan and targeted pytest. | |
| CQ-PATHS-001 | Yes | Keep all edits inside the listed in-root target paths. | Applicability preflight and git diff review. | |
| CQ-COMPLEXITY-001 | Yes | Rename semantics narrowly without redesigning dispatch or lease logic. | Focused tests around suppression and dispatch diagnostics. | |
| CQ-CONSTANTS-001 | Yes | Preserve lock filename templates, TTL constants, and legacy result-string compatibility. | Targeted suppression and diagnose tests. | |
| CQ-SECURITY-001 | Yes | Preserve active-session lock safety behavior and no double-spawn suppression. | Existing suppression and per-document lease tests. | |
| CQ-DOCS-001 | Yes | Update only in-code comments, docstrings, and diagnostics needed to avoid the misnomer. | Targeted diagnose output tests. | |
| CQ-TESTS-001 | Yes | Add or update tests for target naming and legacy-value compatibility. | `python -m pytest platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Keep JSON/diagnostic classification stable while clarifying target/receiver wording. | Diagnose and dispatch-state tests. | |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check, and ruff format before the implementation report. | Commands recorded in the post-implementation report. | |

## Scope

In scope:

- Rename `check_counterpart_active` and related local variables/comments/docstrings to target/receiver terminology where safe.
- Prefer new result/diagnostic naming such as `target_active_session_present` for newly written state when the target harness is already active.
- Preserve read/classification compatibility for legacy `counterpart_active_session_present` state values.
- Update targeted tests to assert target/receiver semantics and legacy-value compatibility.

Out of scope:

- Lock filename changes, including `active-{role}-session.lock` templates.
- Dispatch resolver changes, lease substitution changes, heartbeat TTL changes, or target eligibility changes.
- Retired poller restoration or alternate queue/runtime work.

## Acceptance Criteria

- Active-session suppression diagnostics describe the receiver/target harness's own active-session lock, not a counterpart harness lock.
- New code names and newly written result values use target/receiver semantics where safe.
- Legacy `counterpart_active_session_present` values remain readable and classified equivalently.
- Per-document lease behavior and active-session suppression decisions are unchanged.
- Targeted tests pass and include a compatibility assertion for the legacy state string.
- `WI-3485` is resolved only after Loyal Opposition verifies the implementation report.

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` and file bridge rules: run bridge preflights after filing and include the packet in the implementation report.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: verify the Codex-safe bridge proposal and implementation-report path remains helper-mediated.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`: run active-session/diagnose tests that cover init-session active markers and assertion semantics.
- Code behavior: run `python -m pytest platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py -q --tb=short`.
- Lint: run `python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py`.
- Formatting: run `python -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger_diagnose.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py`.

## Pre-Filing Preflight

Manual catch-22 check performed before filing: this proposal cites bridge authority, project linkage, source-of-truth freshness, artifact-oriented governance, init-keyword, and verified-testing specs triggered by the target paths and implementation proposal content.

The bridge artifact is filed under `bridge/`, and the live queue state is the `bridge/INDEX.md` entry for `gtkb-cross-harness-trigger-active-session-target-naming`; this revision inserts the `REVISED: bridge/gtkb-cross-harness-trigger-active-session-target-naming-002.md` line at the top of that document entry without deleting or rewriting prior versions.

After filing, Prime Builder will run applicability, clause, and citation-freshness preflights and will revise if any blocking gap is reported.

## Risk And Rollback

Risk is low but real: renaming a persisted result string could strand diagnostics if compatibility is missed. Mitigation is to preserve read compatibility for the legacy value and add a regression assertion. Rollback restores the prior names in the changed source/test files; bridge audit files remain append-only.
