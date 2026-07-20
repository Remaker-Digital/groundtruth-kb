# INSIGHTS: Permission Reconciliation and Harmonization Advisory

Status: ADVISORY / discovery packet. Non-authoritative until formalized through ADR/DCL/GOV/spec and bridge GO.

Date: 2026-07-03

Owner directive: create umbrella project `PREMISSION RECONCILIATION AND HARMONIZATION` with one seed work item to produce an implementation approach and work-item list proposal.

Created artifacts:
- Project: `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION`
- Seed work item: `WI-5005`
- Owner decision: `DELIB-20260703-GTKB-PREMISSION-RECONCILIATION-DIRECTIVE`
- Deferred requirement intake: `INTAKE-77d4f633`

## Executive Claim

The owner diagnosis is correct: WI-4997 is not only a dispatcher reliability issue. It is an early symptom of a broader mutation-permission architecture gap. GT-KB has strong adversarial diligence around implementation proposals and verification, but ordinary operational state changes can still be made through local commands, scripts, generated files, or autonomous session behavior without a common activity-window authority, risk class, permission scope, and durable reasoning trail.

The immediate dispatcher-quiesce control appears to have been locally remediated, but it should be treated as the first narrow instance of a larger pattern: all meaningful GT-KB and application mutations need a declared authority, bounded execution window, independent review path, audit evidence, and post-action verification proportional to risk.

## Key Evidence

- The bridge protocol already requires implementation proposals touching source, tests, scripts, hooks, configuration, deployment, repository state, or KB mutation to include concrete `target_paths`, requirement sufficiency, and verification mapping before GO. Evidence: `.claude/rules/file-bridge-protocol.md` lines 43-74.
- Formal bridge review independence is session-context based, not just harness based. Evidence: `.claude/rules/file-bridge-protocol.md` lines 282-299.
- Bridge `DEFERRED` already models non-actionability with owner evidence, reason, and clear/resume condition. Evidence: `.claude/rules/file-bridge-protocol.md` lines 341-357.
- Activity envelopes already distinguish `ops`, `deliberation`, `build`, `test`, `spec`, and `project`, but those envelopes currently describe routing/preload behavior, not a full mutation-permission model. Evidence: `groundtruth-kb/src/groundtruth_kb/session/envelope.py` lines 21-40 and 321-339.
- Dispatcher quiesce now has a time-bound operator primitive with reason, actor, expiration, and dispatched-worker clear protection. Evidence: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` lines 177-312.
- Dispatcher runtime suppresses live spawns when operator quiesce is active. Evidence: `scripts/gtkb_dispatcher_daemon.py` lines 794-830.
- Tests cover operator quiesce preventing runtime/daemon spawns and surfacing in dispatch status/health. Evidence: `platform_tests/scripts/test_dispatcher_runtime.py` lines 432-464, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` lines 441-469, and `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py` lines 197-214.
- The older bridge-substrate switch still directly applies an audited state change to `harness-state/bridge-substrate.json`; it validates artifacts and writes an audit record, but it is not a general adversarial-diligence permission object. Evidence: `groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py` lines 61-143 and `groundtruth-kb/src/groundtruth_kb/cli.py` lines 8196-8235.
- WI-4997 records the original failure mode: config-level quiesce was reverted by an autonomous process, with no reliable interactive/config-level mechanism to pause dispatch. The item is now resolved, but the broader permission model remains open. Evidence: `gt backlog show WI-4997 --json`.

## Finding 1: Narrow Quiesce Exists, General Mutation Authority Does Not

Severity: P1

### Observation

The code now includes `operator_quiesce` for dispatcher spawn suppression, with TTL, actor, reason, clear behavior, status reporting, and tests. That is useful and should be preserved.

### Deficiency Rationale

The owner concern is wider than dispatcher spawn control. The current quiesce primitive does not by itself govern Git pushes, deployments, worktree cleanup, credential/security changes, application user record mutations, canonical artifact changes, or remediation/performance-review actions. Those mutations still need a common authority model.

### Proposed Solution/Enhancement

Define a generalized mutation-permission model with:
- activity window ID and typed activity envelope;
- risk class and mutation class;
- allowed actors, harnesses, commands, paths, targets, and environments;
- TTL/execution window and single-use/reuse semantics;
- owner/proxy authorization source;
- PB/LO review requirements;
- rollback/cancel semantics;
- expected evidence and after-action review.

Treat dispatcher quiesce as one concrete operational permission type inside that model, not as the whole model.

### Option Rationale

Generalizing from the quiesce primitive avoids duplicating one-off controls for every risky operation. It also matches the already-selected LAN authority service direction: service-owned live coordination state with durable authored artifacts remaining Git/file-governed.

## Finding 2: Adversarial Diligence Needs a Single-Harness Compensating Path

Severity: P1

### Observation

The bridge protocol requires session-context independence for formal GO/VERIFIED decisions. The owner also wants adversarial diligence even when only one harness is available.

### Deficiency Rationale

When one harness is the only functional actor, full independence is impossible in the strict sense. Treating same-harness self-review as equivalent to LO review would weaken the core differentiation. Blocking all emergency work would also be unsafe when the dispatcher or environment is down.

### Proposed Solution/Enhancement

Define a "single-harness exception packet" that is not a normal GO path:
- requires explicit cause, scope, TTL, and owner/proxy authorization when reachable;
- records why normal adversarial diligence was unavailable;
- permits only bounded recovery or time-critical action;
- requires after-action Loyal Opposition review as soon as another session/harness is available;
- marks any permanent repair/enhancement as proposal work, not silently implemented policy.

### Option Rationale

This preserves the meaning of adversarial diligence without making the system brittle in recovery conditions. It also prevents the exception from becoming the normal autonomous path.

## Finding 3: Not All "Operations" Should Pay the Same Friction Cost

Severity: P2

### Observation

The owner list includes destructive mutation, deployment, credential/security changes, health checks, diagnostics, remediation, and performance reviews.

### Deficiency Rationale

Health checks and status reports can be read-only. Diagnostics may be read-only until they write reports or alter state. Performance tests can be harmless in a toy environment and dangerous in production. A blanket full-GO requirement for every operation would likely stall useful observability and create pressure to bypass the control.

### Proposed Solution/Enhancement

Use a tiered mutation taxonomy:
- `read_only`: no state mutation, report-only evidence, pre-authorized for routine scheduling.
- `bounded_maintenance`: cleanup or repair inside declared paths/targets with rollback/cancel and evidence.
- `configuration_mutation`: changes to GT-KB/app config, dispatcher state, harness routing, canonical artifacts.
- `environment_mutation`: deployment, production user/security/credential changes, data migrations.
- `emergency_break_glass`: time-critical or dispatcher-unavailable action with strict after-action review.

### Option Rationale

The taxonomy lets routine automation continue while giving serious mutations the adversarial diligence they deserve.

## Finding 4: The Reasoning Trail Must Be a First-Class Artifact

Severity: P1

### Observation

WI-4997's core pain was not only that quiesce was reverted. It was that the system could not explain why the reversion happened.

### Deficiency Rationale

Without a durable causality trail, the owner cannot distinguish a legitimate automation, a stale worker, a role confusion defect, an ungoverned direct mutation, or an intentional override. That prevents reliable post-action review.

### Proposed Solution/Enhancement

Require every material mutation to emit a structured action record:
- intent;
- actor/device/session/harness;
- authority source;
- packet/window ID and version/hash;
- target paths/resources/environments;
- before/after diff or state projection;
- result;
- evidence;
- rollback/cancel status;
- reviewer/after-action verdict.

Generated bridge/status files may remain compatibility views, but the authoritative live mutation trail should be transactional and queryable.

### Option Rationale

This directly addresses the "reverted within minutes and no reasoning trail" failure, and it aligns with service-owned coordination state from the runtime-orchestration discovery track.

## Recommended Implementation-Approach Scope for WI-5005

The future Prime Builder implementation proposal should not jump straight to code. It should propose the downstream work-item list and explicitly cover:

1. Mutation inventory: enumerate all mutation surfaces in GT-KB and Agent Red/application workflows, including CLI commands, scripts, hooks, daemon paths, dashboard/API actions, bridge writers, git operations, deploy operations, and canonical artifact writers.
2. Risk taxonomy: define mutation classes, risk classes, and environment classes.
3. Activity-window model: define permission packet schema, TTL, single-use/reuse semantics, allowed side effects, branch constraints, target worker/harness policy, and expected evidence.
4. Quiesce/freeze controls: reconcile operator quiesce, bridge-substrate switching, dispatch pause/freeze, and queue/lease behavior under one durable control model.
5. Exception paths: specify single-harness/dispatcher-unavailable recovery and time-critical break-glass handling.
6. Enforcement points: identify CLI guards, service/API guards, worker lease checks, dashboard restrictions, hook checks, and fail-closed behavior.
7. Audit and after-action review: define durable action records, review requirements, and dashboard/reporting projections.
8. Migration path: preserve current operator quiesce behavior while moving toward service-owned live coordination.
9. Test strategy: include unit tests for packet validation, CLI guard tests, dispatcher/worker lease tests, service transaction tests, and end-to-end adversarial diligence flow tests.
10. Work-item proposal: produce the complete ordered downstream WI list, but do not create those WIs until the proposal receives GO.

## Candidate Work Items After Proposal GO

These are advisory candidates only; they should not be created until the WI-5005 proposal receives GO.

- Inventory all mutation surfaces and classify by mutation/risk/environment.
- Specify mutation permission packet schema and lifecycle.
- Implement durable for-cause dispatch quiesce under the broader permission model.
- Gate bridge-substrate and dispatcher-state mutation behind permission packets.
- Gate Git push, cleanup, deploy, and canonical artifact mutation through activity-window authority.
- Add emergency/single-harness exception packet and after-action review workflow.
- Add structured mutation action log and dashboard/API projections.
- Add CLI/client enforcement and local-maintenance/offline recovery mode.
- Add regression tests for autonomous re-enable prevention and unauthorized mutation denial.
- Update ADR/DCL/GOV/spec surfaces after the design is approved.

## Open Decisions for Grill-Me-for-Clarification

The first dependency decision is whether to model the new system as:

- a general mutation-permission/control-plane primitive, with dispatcher quiesce as the first implementation case;
- a dispatcher-specific quiesce fix first, with broader mutation permissions later;
- or a broad global freeze/mutation lock first, then refine per activity class.

Secondary decisions depend on that answer:
- which actions require owner approval versus proxy/runbook approval;
- whether read-only diagnostics need packets;
- how much authority an automation can hold for recurring maintenance;
- whether service-owned state is mandatory for this release or a staged migration;
- how break-glass authorization is represented when the dispatcher is unavailable;
- what operations, if any, remain permissible outside an activity window.

## Recommendation

Proceed with `WI-5005` as the only current implementation-bearing work item under `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION`.

The implementation proposal should recommend a general mutation-permission primitive and use dispatcher quiesce as the first hardening case. This is the least-regret option because it addresses the root architectural gap while still letting the already-present operator-quiesce work remain useful.

Skills applied: grill-me-for-clarification, projects, loyal-opposition-report, proposal-review, gtkb-decision-capture, gtkb-spec-intake
