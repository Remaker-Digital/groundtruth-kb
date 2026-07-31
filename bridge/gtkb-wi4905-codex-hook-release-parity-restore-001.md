NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop Prime Builder interactive session; hooks contained; approval_policy=never; cwd=E:\GT-KB

# Implementation Proposal - Expand no-window process-spawn audit to every harness launcher, verifier, benchmark runner, and recurring worker

bridge_kind: prime_proposal
Document: gtkb-wi4905-codex-hook-release-parity-restore
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4905

target_paths: [".codex/hooks.json", ".codex/config.toml", ".codex/gtkb-hooks", "platform_tests/scripts/test_codex_hook_runtime_containment.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/scripts/test_hook_registration_parity.py", "platform_tests/scripts/test_fab09_safety_gate_registration.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Restore release-safe Codex hook parity after WI-4905 runtime containment by re-enabling the Codex hook mirror through hardened no-window wrappers, while continuing to exclude retired cross-harness/single-harness dispatch triggers.

Work item description: WI-4896 resolved dispatcher-owned background console flashes, but Phase 2 needs full coverage. Extend the static/runtime no-window spawn audit to all Python and PowerShell launch surfaces for harness adapters, readiness verifiers, benchmark runners, recurring evaluators, dispatcher helpers, and provider wrappers, including scripts such as verify_antigravity_dispatch.py that are outside the current release-runtime allowlist.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4905` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.codex/hooks.json`, `.codex/config.toml`, `.codex/gtkb-hooks`, `platform_tests/scripts/test_codex_hook_runtime_containment.py`, `platform_tests/scripts/test_codex_hook_parity.py`, `platform_tests/scripts/test_cross_harness_protocol_parity.py`, `platform_tests/scripts/test_hook_registration_parity.py`, `platform_tests/scripts/test_fab09_safety_gate_registration.py`, `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266423` - Separation Check
- `DELIB-20266413` - Separation Check
- `DELIB-20266353` - GO - gtkb-wi4896-startup-console-residual - Boot-time and Minute-cadence Windows console/focus-steal fix
- `DELIB-20266349` - Separation Check
- `DELIB-20266107` - Owner decision: reconcile dispatch can_receive_dispatch drift to Honest-ON (WI-4821)

## Owner Decisions / Input

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4905`.

## Cross-Harness Disposition

- Codex (A): behavioral parity will be restored for the unwaived Codex hook mirror by registering safe no-window equivalents for Claude hook capabilities. This is not a waiver.
- Claude Code (B): no behavioral change in this slice; Claude remains the comparison source for the hook capabilities already registered in `.claude/settings.json` and `.claude/hooks/`.
- Antigravity (C): no waiver or retirement applies; this slice does not mutate Antigravity surfaces, and later dispatcher-permutation work remains required for Antigravity dispatchability.
- Ollama (D) and OpenRouter (F): no hook-surface mutation in this slice; these dispatch recipients remain governed through the dispatcher daemon path and `.env.local` credential loading.
- Cursor (E): no waiver or retirement applies; this slice does not mutate Cursor surfaces, and later dispatcher-permutation work remains required for Cursor dispatchability.
- Retired cross-harness trigger paths: not a fallback and not parity-equivalent; this proposal explicitly hard-excludes `cross_harness_bridge_trigger.py`, `single_harness_bridge_automation.py`, and `bridge-dispatch-trigger.cmd` from all Codex hook registrations.

## Proposed Scope

- Re-enable `.codex/hooks.json` with Codex equivalents for every unwaived Claude hook capability reported by `scripts/parity_discovery_diff.py`.
- Route hook commands through `pythonw.exe` plus the hardened `run_cmd_no_window.py` / `run_py_no_window.py` wrappers so no registered hook can spawn a visible Windows console or inherit unbounded stdin.
- Do not register `cross_harness_bridge_trigger.py`, `single_harness_bridge_automation.py`, `bridge-dispatch-trigger.cmd`, or any other retired dispatch trigger path; bridge dispatch remains daemon-only.
- Add or update focused tests proving discovery-diff symmetry, implementation-start-gate registration, no-window command forms, and runtime no-orphan behavior for the restored hook registry.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4905-codex-hook-release-parity-restore` must validate all target paths before protected edits. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `python -m pytest platform_tests/scripts/test_codex_hook_runtime_containment.py -q --tb=short` plus a post-probe process scan must find no hook orphans. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `python scripts/parity_discovery_diff.py --json` must return `overall_status` `SYMMETRY` and no findings. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `gt project doctor --json` must omit `Cross-harness parity discovery-diff` and `Dispatcher config CLI-only guard` failures. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `gt project doctor --json` must omit the cross-harness disposition/parity failures for `.codex/hooks.json`. |
| `ADR-CROSS-HARNESS-PARITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- `gt project doctor --json` no longer reports `Cross-harness parity discovery-diff` or `Dispatcher config CLI-only guard` failures from `.codex/hooks.json`.
- `python scripts/parity_discovery_diff.py --json` exits cleanly with `overall_status` `SYMMETRY`.
- No registered Codex hook command references retired dispatch triggers or foreground launchers.
- Focused hook runtime containment tests pass and a post-probe process scan finds no live Codex hook wrapper/handler processes.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.codex/hooks.json`
- `.codex/config.toml`
- `.codex/gtkb-hooks`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`
- `platform_tests/scripts/test_codex_hook_parity.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `platform_tests/scripts/test_hook_registration_parity.py`
- `platform_tests/scripts/test_fab09_safety_gate_registration.py`
- `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`

## Recommended Commit Type

`feat`
