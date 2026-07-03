NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# AUQ Headless Hook Launch Hygiene Exact Target Amendment

bridge_kind: prime_proposal
Document: gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment
Version: 001
Date: 2026-07-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE-WI-4959
Project: PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE
Work Item: WI-4959

target_paths: [".codex/gtkb-hooks/bridge-compliance-audit.cmd", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd", ".codex/gtkb-hooks/bridge-compliance-gate.cmd", ".codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd", ".codex/gtkb-hooks/codex-mcp-worker-guard.cmd", ".codex/gtkb-hooks/credential-scan.cmd", ".codex/gtkb-hooks/destructive-gate.cmd", ".codex/gtkb-hooks/directive-enforcement.cmd", ".codex/gtkb-hooks/formal-artifact-approval.cmd", ".codex/gtkb-hooks/implementation-start-gate.cmd", ".codex/gtkb-hooks/lo-file-safety-gate.cmd", ".codex/gtkb-hooks/session-start.cmd", ".codex/gtkb-hooks/session-stop.cmd", ".codex/gtkb-hooks/wi-id-collision-gate.cmd", ".codex/gtkb-hooks/workstream-focus.cmd", "platform_tests/scripts/test_codex_hook_runtime_containment.py"]

implementation_scope: scope-amendment-only
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Summary

Prime Builder paused WI-4959 implementation because the approved `target_paths` entry `.codex/gtkb-hooks` is treated as an exact path by the implementation-start target preflight, not as recursive directory authority. This amendment requests Loyal Opposition approval for the exact Codex `.cmd` hook adapters that the original GO intended to authorize.

## Claim

Approve exact target-path coverage for the Codex hook batch adapters that currently invoke bare console-attached `python`, plus the existing focused runtime-containment test. This does not add new product scope; it narrows the original `.codex/gtkb-hooks` directory intent into machine-checkable exact paths so Prime Builder can implement WI-4959 without bypassing the target gate.

## Requirement Sufficiency

Existing requirements sufficient.

The owner requirement, PAUTH, WI-4959, original proposal, and GO already authorize AUQ-adjacent headless hook-launch hygiene. This amendment only resolves a target-path precision defect discovered by the implementation-start target preflight.

## In-Root Placement Evidence

All requested target paths are under `E:/GT-KB`. No Agent Red application source, production deployment, credential lifecycle path, dispatcher topology configuration, OPS lifecycle state, or lane-scoring source is in scope.

## OPS Consolidation Integration

This amendment keeps the WI-4959 slice aligned with the OPS consolidation by preserving lifecycle-first/scoring-last boundaries: it only enables hook-launch hygiene, not OPS lifecycle/protocol or lane-scoring behavior. It also respects the dispatcher daemon architecture by avoiding dispatcher topology changes and by treating owner-decision/AUQ ergonomics as support for governed artifact flow, not a new dispatch control plane.

## Architecture Alignment Ledger

| Alignment surface | Evidence |
| --- | --- |
| OPS consolidation | Amendment is subordinate to Wave 1 WI-4959 and does not alter WI-4957 lifecycle/protocol or WI-4958 lane-scoring scope. |
| Dispatcher daemon architecture | Target list is limited to Codex hook adapters; no daemon rules, ranking, topology, runtime state, or worker selection code is changed. |
| Lifecycle-first/scoring-last precedence | This unblocks owner-facing AUQ/headless friction without implementing scoring semantics or treating launch hygiene as lifecycle policy. |
| Portfolio reconciliation | Canonical project remains `PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE` under `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`; duplicate project-family records retired by WI-4960 are not reused. |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires status-bearing bridge append-only authority, role-correct `NEW` proposal filing by Prime Builder, and live GO/claim discipline before protected mutations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target-path metadata on implementation-targeting bridge proposals.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires all relevant governing specifications to be cited before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - keeps the eventual WI-4959 implementation report tied to the changed adapters and focused tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confines the amendment and future changes to GT-KB platform paths, not Agent Red source.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - governs no-console Windows launch expectations for dispatch-related wake/helper paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - preserves daemon-owned dispatch semantics and forbids harness-side topology/control-plane drift.
- `ADR-CROSS-HARNESS-PARITY-001` - requires harness-surface changes to preserve cross-harness behavioral parity.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires an explicit cross-harness disposition for harness-surface target paths.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - governs Codex hook parity and fallback behavior for hook-surface changes.
- `SPEC-AUQ-POLICY-ENGINE-001` - keeps AUQ policy decisions centralized; this amendment changes launcher mechanics only, not AUQ policy logic.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - treats the target-path conflict as a governed artifact update instead of an unrecorded implementation shortcut.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves traceability from defect observation to WI, proposal, GO, amendment, implementation report, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - records this amendment as an active bridge artifact rather than silently changing scope after GO.

## Prior Deliberations

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - owner observed two short-lived console windows after each AUQ and directed headless behavior.
- `DELIB-20260702-DISPATCH-OPS-WAVE1-FILE-ALL-PRIORITIZE-AUQ-HEADLESS` - owner prioritized AUQ/headless hygiene in Wave 1.
- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner selected governed project, WI, and bridge proposal creation.
- `DELIB-20260702-DISPATCH-OPS-FOUNDATION-FIRST-IMPLEMENTATION-WAVE` - Wave 1 includes OPS foundation, lane-scoring foundation, AUQ/headless hygiene, and portfolio control.
- `DELIB-20266297` - prior owner directive and authorization for WI-4896 console-window suppression.

## Owner Decisions / Input

- `DELIB-20260702-AUQ-ADJACENT-CONSOLE-WINDOWS-HEADLESS-REQUIREMENT` - owner reported the AUQ-adjacent two-console-window symptom and requested headless behavior.
- `DELIB-20260702-DISPATCH-OPS-CREATE-ACTUAL-PROJECT-WIS-BRIDGE-PROPOSALS` - owner approved actual governed project/work-item/bridge proposal creation for this Wave 1 program.
- `PAUTH-PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE-WI-4959` - active authorization for bounded bridge, source, tests, and harness-config changes for WI-4959.

## Pre-Implementation Target Gate Evidence

Prime Builder acquired the WI-4959 work-intent claim and implementation-start packet, then ran the exact target preflight before mutation:

```text
python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-auq-headless-hook-launch-hygiene --candidate-paths .codex/gtkb-hooks/session-start.cmd .codex/gtkb-hooks/session-stop.cmd .codex/gtkb-hooks/workstream-focus.cmd platform_tests/scripts/test_codex_hook_runtime_containment.py --json
```

Observed result: `verdict: out_of_scope_drift`; `.codex/gtkb-hooks/session-start.cmd`, `.codex/gtkb-hooks/session-stop.cmd`, and `.codex/gtkb-hooks/workstream-focus.cmd` were reported out of scope while `platform_tests/scripts/test_codex_hook_runtime_containment.py` was in scope. The approved proposal target list contained `.codex/gtkb-hooks`, which the gate treats as exact rather than recursive.

Static scan also found these Codex `.cmd` adapters invoking bare `python`:

- `.codex/gtkb-hooks/bridge-compliance-audit.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate.cmd`
- `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd`
- `.codex/gtkb-hooks/codex-mcp-worker-guard.cmd`
- `.codex/gtkb-hooks/credential-scan.cmd`
- `.codex/gtkb-hooks/destructive-gate.cmd`
- `.codex/gtkb-hooks/directive-enforcement.cmd`
- `.codex/gtkb-hooks/formal-artifact-approval.cmd`
- `.codex/gtkb-hooks/implementation-start-gate.cmd`
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`
- `.codex/gtkb-hooks/session-start.cmd`
- `.codex/gtkb-hooks/session-stop.cmd`
- `.codex/gtkb-hooks/wi-id-collision-gate.cmd`
- `.codex/gtkb-hooks/workstream-focus.cmd`

## Proposed Scope

- Treat the exact `.cmd` files listed in `target_paths` as the approved Codex implementation targets for WI-4959.
- Permit only launcher hygiene changes in those files: replace bare `python` with a hidden/no-window Python launcher pattern that preserves stdout/stderr behavior for hook diagnostics.
- Add a focused static regression in `platform_tests/scripts/test_codex_hook_runtime_containment.py` that fails when Codex hook `.cmd` adapters invoke bare `python` again.
- Continue to use the original WI-4959 GO for the unchanged verification obligations: focused tests, ruff on changed Python, Windows smoke or justified equivalent, and explicit cross-harness disposition in the implementation report.

## Cross-Harness Disposition

- Codex harness A: exact target amendment applies to Codex `.cmd` adapters under `.codex/gtkb-hooks`.
- Claude Code harness B: no additional `.claude/hooks` target is requested here; the original WI-4959 implementation report must still document the Claude parity disposition.
- Cursor harness E: no additional `.cursor` target is requested here; the original WI-4959 implementation report must still document the Cursor parity disposition.
- Provider harnesses D/F: no provider-specific hook files are requested here.
- Retired Antigravity harness C: no active hook-surface target is requested here.

## Out Of Scope

- Dispatcher topology, rules, ranking, daemon, worker lifecycle, or claim semantics.
- OPS lifecycle/protocol implementation for WI-4957.
- Lane-scoring registry/projection implementation for WI-4958.
- Project/backlog/spec metadata mutation.
- Credential lifecycle changes, production deployment, and Agent Red application source.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | LO verifies this amendment is Prime-authored `NEW`, append-only, and limited to exact target-path approval before implementation proceeds. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance and LO verify PAUTH, project, WI, and target paths are present and active. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Future WI-4959 implementation verifies the listed adapters use no-window launch mechanics instead of bare console-attached `python`. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Review confirms the amendment touches hook-launch adapter paths only and excludes dispatcher daemon topology/routing changes. |
| `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | This amendment includes a cross-harness disposition, and the final WI-4959 implementation report carries the original parity audit/disposition forward. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Final WI-4959 implementation report maps each changed adapter to focused tests and Windows smoke/equivalent evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target preflight and review confirm all exact paths stay in GT-KB platform surfaces. |

## Acceptance Criteria

- LO approves exact target paths for the listed Codex `.cmd` adapters and the focused runtime-containment test.
- Prime Builder re-runs `impl_start_target_paths_preflight.py` against the exact adapter list before any protected mutation.
- If the exact target preflight still fails after this amendment receives GO, Prime Builder pauses again rather than mutating protected hook files.
- The final WI-4959 implementation report enumerates every changed adapter and maps each to regression evidence.

## Risks / Rollback

Risk is low. The amendment expands no behavior beyond the original GO; it only converts a directory-level target into exact file targets accepted by the implementation-start gate.

Rollback is procedural: if LO does not approve, Prime Builder leaves WI-4959 source/config/test files unchanged and either revises scope or waits for a different governed path. Bridge files remain append-only audit history.

## Pre-Filing Self-Check

- Role eligibility: harness `codex` durable ID `A`; resolved role includes `prime-builder`; Prime Builder may author `NEW` bridge proposals.
- Live thread state: `gtkb-auq-headless-hook-launch-hygiene` latest status is `GO`; no protected hook/source/test mutation was performed after the exact target preflight reported out-of-scope drift.
- Work intent: the WI-4959 implementation claim is held by session `019f23f0-b16e-7481-8a18-9622ab564d50`; the amendment thread will acquire its own bridge write claim through the governed helper.

## Files Expected To Change After Amendment GO

- `.codex/gtkb-hooks/bridge-compliance-audit.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate.cmd`
- `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd`
- `.codex/gtkb-hooks/codex-mcp-worker-guard.cmd`
- `.codex/gtkb-hooks/credential-scan.cmd`
- `.codex/gtkb-hooks/destructive-gate.cmd`
- `.codex/gtkb-hooks/directive-enforcement.cmd`
- `.codex/gtkb-hooks/formal-artifact-approval.cmd`
- `.codex/gtkb-hooks/implementation-start-gate.cmd`
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`
- `.codex/gtkb-hooks/session-start.cmd`
- `.codex/gtkb-hooks/session-stop.cmd`
- `.codex/gtkb-hooks/wi-id-collision-gate.cmd`
- `.codex/gtkb-hooks/workstream-focus.cmd`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`

## Recommended Commit Type

`fix`
