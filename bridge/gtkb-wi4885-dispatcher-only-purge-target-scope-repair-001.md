NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-auto-builder-20260629-wi4885-scope-repair
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Prime Builder automation; WI-4885 target-scope repair
author_metadata_source: explicit Codex runtime metadata

# WI-4885 Dispatcher-Only Purge Target Scope Repair

bridge_kind: prime_proposal
Document: gtkb-wi4885-dispatcher-only-purge-target-scope-repair
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4885

target_paths: ["AGENTS.md", "CLAUDE.md", ".claude/settings.json", ".codex/hooks.json", ".claude/rules/*.md", "config/*.md", "config/**/*.md", "config/*.toml", "config/**/*.toml", "docs/gtkb-dashboard/**", "groundtruth-kb/docs/*.md", "groundtruth-kb/docs/**/*.md", "groundtruth-kb/src/*.py", "groundtruth-kb/src/**/*.py", "harness-state/bridge-substrate.json", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "scripts/*.py", "scripts/**/*.py", "platform_tests/*.py", "platform_tests/**/*.py"]

implementation_scope: source, configuration, operational-docs, tests, dispatcher-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The existing GO for `gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge` correctly approves the release-blocking dispatcher-only purge, but its target path list uses recursive globs such as `scripts/**/*.py`. The live implementation-start validator treats those as subdirectory-only patterns and therefore rejects direct script targets such as `scripts/gtkb_dispatcher_daemon.py` and a dispatcher-owned runtime module at `scripts/dispatcher_runtime.py`.

This proposal is a narrow scope/authorization repair. It does not change the owner's architecture decision, the implementation intent, or the release gate. It restates the same WI-4885 purge with explicit direct-file globs so a new implementation-start packet can legally cover the direct scripts, direct tests, and operational surfaces required to finish the purge.

Prime Builder must not continue direct `scripts/*.py` source mutation under the previous packet. After this proposal receives Loyal Opposition GO, Prime Builder should begin a new implementation-start packet and continue from the current worktree state, preserving unrelated user and harness changes.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/configuration mutations require live GO, role-correct proposal status, matching target paths, and implementation-start authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and inline JSON target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation report must carry forward the cited governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Loyal Opposition verification must map executed evidence back to this verification plan.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - automated bridge dispatch must be centralized under the dispatcher service.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status, topology, and health must be controlled through governed dispatcher surfaces.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon health is a release-readiness architecture surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - GT-KB platform/application isolation must remain intact while operational surfaces and tests are rewritten.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness must fail while stale automation paths remain canonical or reachable.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - automation must not create repeated user-visible process churn or recursive work bursts.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch envelopes must be daemon-owned, role-correct, and non-recursive.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - hook-surface changes must declare harness disposition instead of silently diverging.
- `ADR-CROSS-HARNESS-PARITY-001` - harness parity means equivalent governed behavior, not preserving an unsafe legacy hook path.

## Prior Deliberations

- `DELIB-20266276` - daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - release-health directive for dispatcher readiness.
- `bridge/gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge-001.md` and `bridge/gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge-002.md` - original WI-4885 purge proposal and GO; this thread repairs target-path encoding without broadening the approved architecture intent.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-004.md`, `bridge/gtkb-wi4896-startup-console-residual-006.md`, `bridge/gtkb-wi4896-daemon-loop-console-residual-004.md`, and `bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-005.md` - VERIFIED console-window suppression work proving hook/worker storms are release blockers.

## Owner Decisions / Input

- 2026-06-29 owner directive: the retired cross-harness trigger must be purged from all load-bearing artifacts involved in regular GT-KB operation. It is not a fallback option. Manual owner assignment is the only fallback. The dispatcher daemon is the only automated success path.
- 2026-06-29 owner directive: the release is blocked until the dispatcher is release-healthy and all harnesses are dispatchable and tested for Loyal Opposition and Prime Builder roles.

No further owner decision is required. This proposal corrects mechanical target-path coverage for an already selected architecture direction.

## Requirement Sufficiency

Existing requirements are sufficient.

`WI-4885`, `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, and the 2026-06-29 owner directive provide enough authority to remove the retired trigger family from load-bearing GT-KB operation and require dispatcher-only automation before release.

## Scope Correction

The original purge target list included broad recursive globs but omitted direct-file globs. The live validator currently rejects direct children for patterns like `scripts/**/*.py`. This proposal explicitly adds direct-file target classes:

- `scripts/*.py` and `scripts/**/*.py`
- `platform_tests/*.py` and `platform_tests/**/*.py`
- `groundtruth-kb/src/*.py` and `groundtruth-kb/src/**/*.py`
- direct config/documentation globs alongside recursive config/documentation globs

This makes the implementation-start packet align with the intended WI-4885 purge surface: dispatcher daemon entrypoint, extracted dispatcher runtime module, direct script stubs/deletions, root-level platform tests, mode-switch/doctor/status-driver source, and hook/config surfaces.

## Cross-Harness Disposition

This target-path repair preserves the same cross-harness disposition as the original GO: every harness must use dispatcher-only automation, and no harness-owned hook may launch bridge workers or use the retired trigger family as a fallback. Codex, Claude Code, Cursor, Antigravity, and provider harnesses all share the same fallback rule: manual owner assignment only.

## Isolation Impact

The implementation is limited to GT-KB platform/runtime surfaces under `E:\GT-KB`. It does not move Agent Red or any adopter application files, does not introduce application source into platform directories, and does not use archived outside-root material as authority. Any platform test updates must preserve the platform/application boundary while retiring the old dispatcher trigger assumptions.

## Implementation Plan

1. Start a new implementation-start packet against this corrected thread after Loyal Opposition GO.
2. Validate that `scripts/*.py`, `platform_tests/*.py`, and other direct target paths are authorized by the new packet before additional source mutation.
3. Finish the dispatcher-only purge already begun in the worktree: keep dispatcher daemon operation on `dispatcher_daemon`, move still-needed pure helpers into dispatcher-owned modules, remove hook/legacy substrate references from load-bearing surfaces, and update tests to assert dispatcher-only behavior.
4. Preserve historical bridge/evidence files and non-authoritative runtime residue as out of scope.
5. File a post-implementation report that explains the pre-GO target-path mismatch, lists all touched files, and carries forward spec-derived verification evidence.

## Load-Bearing Purge Boundary

In scope: startup instructions, role overlays, governance rules, canonical terminology, dispatcher config/state, hook configs, doctor/dashboard health surfaces, CLI docs, scaffolds/templates, dispatcher daemon code, dispatcher probes, mode-switch substrate code, regular tests, and any script imported by those surfaces.

Out of scope: historical bridge files, immutable evidence records, dispatch-run logs, `.gtkb-state` runtime residue, `.claude/worktrees`, and scratch files that are not read by startup, dispatcher, doctor, dashboard, CLI, hooks, tests, or release gates.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/implementation_authorization.py validate --target scripts/dispatcher_runtime.py` and representative direct target validations after new packet creation | Direct scripts and direct tests are covered by the corrected implementation-start packet. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch health --json`; `gt bridge dispatch status --json` | Dispatcher daemon is the only automated success path; health does not depend on old trigger checks. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch config --json` plus review of hook configs | Dispatcher topology is exposed through governed dispatcher state; hook configs do not launch bridge workers. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Focused daemon tests after refactor | Daemon owns dispatch launch/reap behavior without importing old trigger modules. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Review touched paths and run focused platform tests | GT-KB platform/application isolation remains intact; no adopter application file becomes part of the platform runtime. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Static no-window/no-hook storm scan plus focused spawn tests | No regular GT-KB operation can recursively spawn console-backed workers from hooks. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Load-bearing reference scan for forbidden trigger-family terms, excluding bridge/evidence/runtime archives | No operational surface presents the old trigger as active, fallback, healthy, registered, or re-enableable. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Dispatcher selection/envelope tests for PB and LO roles | Dispatch envelopes remain role-correct and daemon-owned after old trigger deletion/refactor. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Hook-surface tests and static hook scan | All harness hook surfaces share the same no-bridge-worker-launch rule. |

Focused verification commands:

```text
python scripts/implementation_authorization.py validate --target scripts/dispatcher_runtime.py
python -m py_compile scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py scripts/ops/dispatch_parity.py scripts/verify_antigravity_dispatch.py scripts/verify_cursor_dispatch.py scripts/session_self_initialization.py scripts/session_start_dispatch_core.py scripts/harness_parity_phase2.py scripts/check_codex_hook_parity.py scripts/auto_finalize_sweep.py scripts/implementation_start_gate.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/operating_state.py
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_slice_3_hook_registrations.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py platform_tests/test_no_active_smart_poller_wording.py -q --tb=short
rg -n "cross_harness_bridge_trigger|single_harness_bridge_automation|cross_harness_trigger|cross-harness event-driven trigger|bridge-dispatch-trigger" AGENTS.md CLAUDE.md .claude/rules config docs groundtruth-kb/docs groundtruth-kb/src scripts platform_tests -g "!.claude/worktrees/**" -g "!.gtkb-state/**"
python -m ruff check scripts groundtruth-kb/src platform_tests
python -m ruff format --check scripts groundtruth-kb/src platform_tests
gt bridge dispatch health --json
```

## Pre-Filing Preflight Subsection

The Codex bridge helper must run the pending bridge compliance gate before writing this file, including:

- `python scripts/bridge_applicability_preflight.py --content-file <helper scratch file>`
- `python scripts/adr_dcl_clause_preflight.py --content-file <helper scratch file>`

Both must pass before the proposal file is created. A failing helper audit means this proposal must not be filed.

## Risk / Rollback

Risk: the current worktree already contains partial direct-script purge work begun under the original GO before the validator mismatch was discovered. Mitigation: do not continue direct source mutation until this corrected thread receives GO and a new implementation-start packet validates representative direct targets.

Risk: broad terminology cleanup may accidentally erase historical context needed for audits. Mitigation: keep historical bridge/evidence artifacts intact and limit edits to operational surfaces.

Rollback: revert the implementation commit after the corrected implementation is committed if needed. Do not restore hook-based trigger automation as a fallback; rollback may only return to manual assignment plus disabled trigger containment until a corrected dispatcher implementation is ready.

## Recommended Commit Type

fix:

The expected implementation removes a release-blocking obsolete automation path and makes dispatcher-only operation enforceable under matching target-path authorization.