NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-pb-20260629-dispatcher-purge-proposal
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Prime Builder session; dispatcher purge proposal
author_metadata_source: explicit Codex runtime metadata

# WI-4885 Dispatcher-Only Cross-Harness Trigger Purge

bridge_kind: prime_proposal
Document: gtkb-wi4885-dispatcher-only-cross-harness-trigger-purge
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4885

target_paths: ["AGENTS.md", "CLAUDE.md", ".claude/settings.json", ".codex/hooks.json", ".claude/rules/*.md", "config/**/*.md", "config/**/*.toml", "docs/gtkb-dashboard/**", "groundtruth-kb/docs/**/*.md", "groundtruth-kb/src/**/*.py", "harness-state/bridge-substrate.json", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "scripts/**/*.py", "platform_tests/**/*.py"]

implementation_scope: source, configuration, operational-docs, tests, dispatcher-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The owner's 2026-06-29 release directive changes the dispatcher architecture boundary: `scripts/cross_harness_bridge_trigger.py` is no longer an acceptable active automation path, fallback path, substrate, readiness reference, or operationally canonical mechanism. The only acceptable automated success path is the dispatcher daemon. The only acceptable fallback is user-initiated manual assignment of work to each harness.

Emergency containment already disabled Codex hook automation and made `scripts/cross_harness_bridge_trigger.py` and `scripts/single_harness_bridge_automation.py` exit immediately, but that is only containment. It leaves the old trigger embedded in load-bearing rules, startup docs, doctor checks, dispatcher modules, mode-switch substrate state, readiness probes, dashboard health surfaces, and tests. This proposal authorizes the release-blocking cleanup that removes those active references and replaces them with dispatcher-only operation.

Historical bridge files, archived evidence, and non-authoritative scratch/log output are explicitly out of scope for rewrite. They may continue to mention the old trigger as history. Operational surfaces that influence startup, health, dispatch, governance, docs, generated dashboard state, or tests must not preserve it as a live option.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/configuration mutations require live GO, role-correct proposal status, and implementation-start authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and inline JSON target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation must preserve cited governing specifications and carry them into the report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Loyal Opposition verification must map evidence back to this verification plan.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - automated bridge dispatch must be centralized under the dispatcher service.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status, topology, and health must be controlled through governed dispatcher surfaces.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon health is a release-readiness architecture surface.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness must fail while stale automation paths remain canonical or reachable.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - automation must not create repeated user-visible process churn or recursive work bursts.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch envelopes must be daemon-owned, role-correct, and non-recursive.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - hook-surface changes must declare harness disposition instead of silently diverging.
- `ADR-CROSS-HARNESS-PARITY-001` - harness parity means equivalent governed behavior, not preserving an unsafe legacy hook path.
- `GOV-STANDING-BACKLOG-001` - any residual parity/dispatchability blocker found during purge must become tracked release-blocking work, not scratch state.

## Prior Deliberations

- `DELIB-20266276` - daemon-resilience program scope-lock and full-topology release-readiness authority.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - release-health directive for dispatcher readiness.
- `bridge/gtkb-wi4885-dispatch-topology-activation-repair-001.md` and `bridge/gtkb-wi4885-dispatch-topology-activation-repair-002.md` - current WI-4885 GO for topology readiness repair; this proposal supersedes the old trigger fallback assumption rather than relying on that target envelope.
- `bridge/gtkb-wi4893-daemon-hook-storm-hardening-004.md` - VERIFIED containment for hook storm risk.
- `bridge/gtkb-wi4896-dispatcher-console-window-suppression-004.md`, `bridge/gtkb-wi4896-startup-console-residual-006.md`, `bridge/gtkb-wi4896-daemon-loop-console-residual-004.md`, and `bridge/gtkb-wi4896-codex-desktop-antigravity-console-residual-005.md` - VERIFIED console-window suppression work that proved window storms are release blockers.
- `bridge/gtkb-no-index-dispatcher-trigger-cleanout-007.md` - prior no-index cleanout context; this proposal is stricter because the old trigger is no longer a fallback.

## Owner Decisions / Input

- 2026-06-29 owner directive: "The cross-harness trigger must be completely purged (and all references to it) from all load-bearing artifacts which are involved in the regular operation of GT-KB. It is not a fallback option. The only fallback is user-initiated manual assignment of work to each harness. The only success path is full implementation of the dispatcher."
- 2026-06-29 owner directive: the release is blocked until the dispatcher is release-healthy and all harnesses are dispatchable and tested for Loyal Opposition and Prime Builder roles.

No further owner decision is required for this proposal. The owner has directly selected the architecture direction and fallback rule.

## Requirement Sufficiency

Existing requirements are sufficient.

`WI-4885`, `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, and the 2026-06-29 owner directive provide enough authority to remove the old trigger from load-bearing GT-KB operation and require dispatcher-only automation before release.

## Cross-Harness Disposition

This proposal changes hook-surface parity by making the safe behavior identical across harnesses: no harness-owned hook may launch bridge workers or use the retired trigger family as a fallback.

- Codex (harness A): `.codex/hooks.json` must not register bridge dispatch automation. Any remaining Codex hooks must be non-dispatch governance hooks or startup/session hooks that cannot spawn bridge workers.
- Claude Code (harness B): `.claude/settings.json` must not register bridge dispatch automation. Any remaining Claude hooks must be non-dispatch governance hooks or startup/session hooks that cannot spawn bridge workers.
- Cursor (harness E): Cursor must not receive a separate trigger fallback. Dispatchability must be proven through the central dispatcher and readiness probes, or work must be manually assigned by the owner.
- Antigravity (harness C): Antigravity must not receive a separate trigger fallback. Dispatchability must be proven through the central dispatcher and readiness probes, or work must be manually assigned by the owner.
- Other registered/future harnesses: parity is dispatcher-only automation plus manual owner assignment fallback. No typed waiver is requested or accepted for the retired trigger.

## Implementation Plan

1. Enumerate load-bearing references to the retired trigger family with bounded scans that exclude historical bridge chains, evidence archives, `.gtkb-state`, transient logs, and `.claude/worktrees`.
2. Remove active hook registration and operational documentation references from AGENTS, CLAUDE, rule files, startup overlays, dashboard inputs, doctor registry, and scaffold/templates so the trigger is not presented as canonical, healthy, fallback, or re-enableable.
3. Refactor dispatcher daemon and readiness/probe code so no daemon or probe imports `scripts/cross_harness_bridge_trigger.py`; move any still-needed pure helpers into dispatcher-owned modules whose names and entrypoints cannot be mistaken for hook automation.
4. Retire `scripts/cross_harness_bridge_trigger.py` and `scripts/single_harness_bridge_automation.py` from regular operation. Prefer deletion if imports are removed; otherwise leave only non-load-bearing historical compatibility stubs that are not registered, imported, advertised, or callable by GT-KB operation.
5. Remove `cross_harness_trigger` as a substrate option from mode-switch, doctor, bridge-substrate, dashboard, and tests. Dispatcher daemon is the only automated substrate; manual owner assignment is the only fallback.
6. Add anti-regression tests and scans that fail if load-bearing operational surfaces reintroduce the old trigger family, its hook registrations, or the single-harness automation fallback as a live path.

## Load-Bearing Purge Boundary

In scope: startup instructions, role overlays, governance rules, canonical terminology, dispatcher config/state, hook configs, doctor/dashboard health surfaces, CLI docs, scaffolds/templates, dispatcher daemon code, dispatcher probes, mode-switch substrate code, regular tests, and any script imported by those surfaces.

Out of scope: historical bridge files, immutable evidence records, dispatch-run logs, `.gtkb-state` runtime residue, `.claude/worktrees`, and scratch files that are not read by startup, dispatcher, doctor, dashboard, CLI, hooks, tests, or release gates. If a scratch file is confusing and safe to delete, delete it under ordinary hygiene rules rather than adding warnings to it.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch health --json`; `gt bridge dispatch status --json` | Dispatcher daemon is the only automated success path; health does not depend on old trigger checks. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch config --json` plus review of hook configs | Dispatcher topology is exposed through governed dispatcher state; hook configs do not launch bridge workers. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Focused daemon tests after refactor | Daemon owns dispatch launch/reap behavior without importing old trigger modules. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Static no-window/no-hook storm scan plus focused spawn tests | No regular GT-KB operation can recursively spawn console-backed workers from hooks. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Load-bearing reference scan for forbidden trigger-family terms, excluding bridge/evidence/runtime archives | No operational surface presents the old trigger as active, fallback, healthy, registered, or re-enableable. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | Dispatcher selection/envelope tests for PB and LO roles | Dispatch envelopes remain role-correct and daemon-owned after old trigger deletion/refactor. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Hook-surface tests and static hook scan | All harness hook surfaces share the same no-bridge-worker-launch rule. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward with exact command outputs and residual-reference inventory | Loyal Opposition has direct evidence for every requirement. |

Focused verification commands:

```text
rg -n "cross_harness_bridge_trigger|single_harness_bridge_automation|cross_harness_trigger|cross-harness event-driven trigger|bridge-dispatch-trigger" AGENTS.md CLAUDE.md .claude/rules config docs groundtruth-kb/docs groundtruth-kb/src scripts platform_tests -g "!.claude/worktrees/**" -g "!.gtkb-state/**"
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py platform_tests/scripts/test_slice_3_hook_registrations.py platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py platform_tests/test_no_active_smart_poller_wording.py -q --tb=short
python -m ruff check scripts groundtruth-kb/src platform_tests
python -m ruff format --check scripts groundtruth-kb/src platform_tests
gt bridge dispatch health --json
```

If implementation discovers additional load-bearing files with forbidden references, those files are in scope under the `target_paths` globs and must be included in the report's residual-reference inventory.

## Risk / Rollback

Risk: the daemon currently imports implementation helpers from the old trigger module. Mitigation: extract only pure, needed logic into dispatcher-owned modules and prove daemon import/startup without the old module.

Risk: broad terminology cleanup may accidentally erase historical context needed for audits. Mitigation: keep historical bridge/evidence artifacts intact and limit edits to operational surfaces.

Risk: deletion of old scripts may break stale tests. Mitigation: update stale tests to assert dispatcher-only behavior and forbidden-reference scans rather than preserving old implementation details.

Rollback: revert the implementation commit and restore emergency containment if needed. Do not restore hook-based trigger automation as a fallback; rollback may only return to manual assignment plus disabled trigger stubs until a corrected dispatcher implementation is ready.

## Bridge Filing

This proposal creates a new WI-4885 release-blocking bridge thread because the existing WI-4885 GO does not authorize a full purge of the former trigger across operational docs, rules, source, doctor/dashboard, and tests. Prime Builder must wait for a Loyal Opposition GO and a matching implementation-start packet before mutating protected target paths.

## Recommended Commit Type

fix:

The expected implementation removes a release-blocking obsolete automation path and makes dispatcher-only operation enforceable.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
