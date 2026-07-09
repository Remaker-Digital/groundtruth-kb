NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f0ec0-6e20-7302-a463-748e680a1f7b
author_model: GPT-5 Codex
author_model_version: 2026-06-28 desktop runtime
author_model_configuration: Codex automation Prime Builder

# WI-4881 Headless Cursor LO Dispatch Verdict Verification

bridge_kind: prime_proposal
Document: gtkb-wi4881-headless-cursor-lo-dispatch-verdicts
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4881

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source and test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4881 asks GT-KB to verify that the dispatcher daemon's own headless Cursor-E Loyal Opposition path produces real bridge verdict output, rather than depending on the separate interactive Cursor auto-process that carried the PHASE-Y loop's LO half.

This proposal is a narrow verification-and-regression slice for that risk. It does not flip dispatcher topology, activate retired harnesses, change dispatcher routing configuration, run production deployment, or modify dirty dispatcher source files. It validates the clean Cursor harness surface that the daemon dispatches through and adds focused regression coverage so headless LO route execution cannot silently degrade into a no-op.

## Bridge Filing

This proposal will be filed as the next append-only numbered bridge file at `bridge/gtkb-wi4881-headless-cursor-lo-dispatch-verdicts-001.md`. No prior versioned bridge files are rewritten, deleted, or treated as mutable queue authority.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` governs this implementation proposal, the required Loyal Opposition `GO`, implementation-start authorization, post-implementation report, and verification verdict.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` requires concrete governing specification links and specification-derived verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` requires the Project Authorization, Project, Work Item, and parseable `target_paths` metadata in this proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires the implementation report to map executed verification evidence back to the linked specifications.
- `GOV-STANDING-BACKLOG-001` makes MemBase work item `WI-4881` the current backlog authority for this dispatcher-reliability risk.
- `ADR-DISPATCHER-ARCHITECTURE-001` governs dispatcher-daemon architecture and the expectation that daemon-spawned harnesses perform real PB/LO workflow work.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` requires dispatcher service behavior to be observable and reliable enough for autonomous bridge work.
- `DCL-DISPATCH-ENVELOPE-RULES-001` governs dispatch envelope evidence and prevents treating a zero-output harness invocation as successful bridge work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` requires all test fixtures and harness path handling to remain inside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` require this discovered dispatcher-risk branch to be preserved as governed proposal, test, and verification evidence rather than scratch context.

## Prior Deliberations

- `DELIB-20266203` defines the autonomous dispatcher-daemon PB/LO loop goal and the zero-owner-touch acceptance path.
- `DELIB-20266272` records the PHASE-Y full daemon go-live authorization and the synthetic live-loop acceptance context.
- `DELIB-20266209` records the Cursor headless LO skill-route blocker and the bounded fix that preceded this WI.
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` records the harden-first/go-live-later sequencing and the owner expectation that headless Cursor LO eventually carry the LO half.
- `WI-4881` records the post-PHASE-Y observation that the apparent LO success came from an interactive Cursor auto-process, while the daemon-spawned Cursor worker exited too quickly with no output.

## Owner Decisions / Input

Existing owner decisions are sufficient for this proposal. `DELIB-20266276` authorized the daemon-resilience program including `WI-4881`; `DELIB-20266203`, `DELIB-20266272`, and `DELIB-20266209` supply the relevant loop, go-live, and Cursor headless-route decisions.

No new owner decision is requested. This proposal explicitly excludes production deployment, credential lifecycle action, dispatcher topology flips, activating retired harness C, direct dispatcher-rule edits, and force-pushing or history rewriting.

## Requirement Sufficiency

Existing requirements are sufficient. The owner has already defined the desired autonomous loop behavior and identified the risk: daemon-spawned headless Cursor LO must produce substantive verdict output, not merely exit successfully while an interactive process does the real review work.

No new or revised requirement is needed before implementation. If Loyal Opposition finds that only a real live daemon-dispatch smoke can satisfy WI-4881, it should return `NO-GO` with the required smoke boundaries; this proposal currently keeps the implementation deterministic and narrowly scoped.

## Implementation Plan

1. Extend `platform_tests/scripts/test_cursor_harness.py` with regression coverage for the headless LO invocation path:
   - bridge-review and verification route keys resolve to the intended skill contracts;
   - the built Cursor Agent command includes the prompt-mode invocation, trust flag, `--workspace E:\GT-KB`, and `--output-format ...` with the skill-injected prompt;
   - a fake Cursor Agent process that emits a minimal status-bearing verdict body is treated as successful output and not collapsed to an empty/no-op result;
   - a zero-output successful process is detected as insufficient for the WI-4881 acceptance path, either by existing behavior plus explicit test expectation or by a small harness guard if the current code silently accepts it.
2. If needed, minimally update `scripts/cursor_harness.py` so `main()` fails closed when a headless bridge-review or verification invocation exits 0 but produces no stdout. The guard must be scoped to Loyal Opposition bridge skills only, preserving normal non-bridge command behavior.
3. Run a read-only local smoke of `scripts/cursor_harness.py --skill bridge-review` when a Cursor Agent binary is available. If unavailable, record that the deterministic fake-agent regression is the executed evidence and that a real-provider smoke remains a follow-on release-readiness check.
4. File a post-implementation report with the exact commands, observed results, and whether a real Cursor Agent smoke was available in this environment.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `implementation_authorization.py begin` and target validation must authorize only `scripts/cursor_harness.py` and `platform_tests/scripts/test_cursor_harness.py`. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Cursor harness tests must prove the daemon-dispatched command path produces non-empty bridge-review/verification output through the same shim entry point the dispatcher uses. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | A zero-output bridge-review/verification worker must not be accepted as a successful LO verdict path. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Test fixtures and fake-agent paths must remain under the pytest temporary directory or `E:\GT-KB`; no outside project dependency is introduced. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must include focused pytest, Ruff lint, Ruff format, and any available live Cursor smoke evidence. |

Required local verification commands:

```text
python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short
python -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py
python -m ruff format --check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4881-headless-cursor-lo-dispatch-verdicts
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4881-headless-cursor-lo-dispatch-verdicts
```

Optional live smoke when Cursor Agent is available:

```text
python scripts/cursor_harness.py --skill bridge-review --output-format text --timeout 300 --prompt "<bounded synthetic review prompt>"
```

## Acceptance Criteria

- Headless Cursor LO bridge-review and verification route keys still resolve to real skill contracts.
- The Cursor harness test suite proves a daemon-equivalent headless invocation can return non-empty verdict-like output.
- A zero-output successful Cursor Agent process cannot be mistaken for a successful bridge verdict path for bridge-review or verification routes.
- The implementation report clearly distinguishes deterministic fake-agent evidence from any real Cursor Agent smoke evidence available in this environment.
- No dispatcher topology, dispatcher configuration, production deployment, credential lifecycle, or dirty dispatcher source file is changed.

## Risk / Rollback

The primary risk is over-tightening `cursor_harness.py` and blocking a legitimate Cursor Agent invocation that emits structured output somewhere other than stdout. The implementation should keep any fail-closed zero-output guard scoped to Loyal Opposition bridge skills and should preserve stderr passthrough for diagnostics.

Rollback is a single revert of the test and any minimal `cursor_harness.py` guard. No dispatcher state, routing configuration, MemBase records, or production surfaces are modified by this slice.

## Recommended Commit Type

Recommended commit type: `test:` if only regression coverage is needed; `fix:` if `scripts/cursor_harness.py` must gain a zero-output fail-closed guard.
