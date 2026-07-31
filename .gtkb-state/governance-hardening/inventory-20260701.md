# Project Membership Reconciliation Inventory

Generated: `2026-07-01T06:39:57Z`

## Summary

- Total non-terminal work items: 186
- Source authority: fresh MemBase current-state views.
- Mode: read-only dry-run; no project, membership, work-item, bridge, or owner-decision mutation is performed.

| Classification | Count |
|---|---:|
| `already_active_project_member` | 48 |
| `dangling_or_terminal_project_membership` | 5 |
| `existing_project_candidate_exact` | 0 |
| `existing_project_candidate_weak` | 15 |
| `new_project_candidate_cluster` | 100 |
| `single_wi_project_candidate` | 0 |
| `obsolete_or_duplicate_candidate` | 11 |
| `dependency_blocked_candidate` | 0 |
| `needs_manual_triage` | 7 |

## already_active_project_member

| Work Item | Priority | Status | Candidate Projects | Reason |
|---|---|---|---|---|
| `WI-4944` | `P0` | `open` | PROJECT-GTKB-AD-HOC-RELEASE-20260701, PROJECT-GTKB-AD-HOC-RELEASE-20260701-DISPATCH-UNBLOCK | work item already has an active membership in a non-terminal project |
| `WI-4868` | `P1` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4909` | `P1` | `open` | PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-ADVERSARIAL-REVIEW | work item already has an active membership in a non-terminal project |
| `WI-4910` | `P1` | `open` | PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-SESSIONS | work item already has an active membership in a non-terminal project |
| `WI-4911` | `P1` | `open` | PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-FORMALIZATION-PREP | work item already has an active membership in a non-terminal project |
| `WI-4929` | `P1` | `open` | PROJECT-GTKB-MAY29-HYGIENE-STARTUP-RELAY | work item already has an active membership in a non-terminal project |
| `WI-4943` | `P1` | `open` | PROJECT-GTKB-AD-HOC-RELEASE-20260701, PROJECT-GTKB-AD-HOC-RELEASE-20260701-DISPATCHER-SUBSTRATE | work item already has an active membership in a non-terminal project |
| `WI-4945` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-UMBRELLA | work item already has an active membership in a non-terminal project |
| `WI-4946` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARDING-CONTRACT | work item already has an active membership in a non-terminal project |
| `WI-4947` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-COMPACT-CLI | work item already has an active membership in a non-terminal project |
| `WI-4948` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-ACTIVITY-LOADER | work item already has an active membership in a non-terminal project |
| `WI-4949` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARD-MIGRATION | work item already has an active membership in a non-terminal project |
| `WI-4950` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-HARNESS-PROJECTION | work item already has an active membership in a non-terminal project |
| `WI-4951` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-MEASUREMENT | work item already has an active membership in a non-terminal project |
| `WI-4952` | `P1` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-BLOCKER-REPAIRS | work item already has an active membership in a non-terminal project |
| `WI-3400` | `P2` | `open` | GTKB-V1-RELEASE-STRATEGY-001 | work item already has an active membership in a non-terminal project |
| `WI-3407` | `P2` | `open` | GTKB-V1-RELEASE-STRATEGY-001 | work item already has an active membership in a non-terminal project |
| `WI-3430` | `P2` | `open` | PROJECT-GTKB-ENV-SOT-TOPOLOGY | work item already has an active membership in a non-terminal project |
| `WI-3431` | `P2` | `open` | PROJECT-GTKB-ENV-SOT-TOPOLOGY | work item already has an active membership in a non-terminal project |
| `WI-3445` | `P2` | `open` | PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 | work item already has an active membership in a non-terminal project |
| `WI-4356` | `P2` | `open` | PROJECT-GTKB-RELIABILITY-FIXES | work item already has an active membership in a non-terminal project |
| `WI-4369` | `P2` | `open` | PROJECT-GTKB-PROTECTED-ARTIFACT-DRIFT-ROLLUP | work item already has an active membership in a non-terminal project |
| `WI-4784` | `P2` | `open` | PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE, PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4785` | `P2` | `open` | PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE, PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4791` | `P2` | `open` | PROJECT-HARNESS-PARITY-PHASE-2, PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1 | work item already has an active membership in a non-terminal project |
| `WI-4792` | `P2` | `open` | PROJECT-HARNESS-PARITY-PHASE-2, PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1 | work item already has an active membership in a non-terminal project |
| `WI-4823` | `P2` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4870` | `P2` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4306` | `P3` | `open` | PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS | work item already has an active membership in a non-terminal project |
| `WI-4554` | `P3` | `open` | PROJECT-OMNIGENT-ALIGNMENT | work item already has an active membership in a non-terminal project |
| `WI-4555` | `P3` | `open` | PROJECT-OMNIGENT-ALIGNMENT | work item already has an active membership in a non-terminal project |
| `WI-4749` | `P3` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4754` | `P3` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4800` | `P3` | `open` | PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE | work item already has an active membership in a non-terminal project |
| `WI-4824` | `P3` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4839` | `P3` | `open` | PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT | work item already has an active membership in a non-terminal project |
| `WI-4840` | `P3` | `open` | PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT | work item already has an active membership in a non-terminal project |
| `WI-4841` | `P3` | `open` | PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT | work item already has an active membership in a non-terminal project |
| `WI-4842` | `P3` | `open` | PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT | work item already has an active membership in a non-terminal project |
| `WI-4850` | `P3` | `open` | PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4853` | `P3` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4866` | `P3` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4876` | `P3` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `WI-4926` | `P3` | `open` | PROJECT-HARNESS-PARITY-PHASE-2 | work item already has an active membership in a non-terminal project |
| `GTKB-DASHBOARD-003` | `` | `open` | PROJECT-GTKB-DASHBOARD-OBSERVABILITY | work item already has an active membership in a non-terminal project |
| `GTKB-DORA-002` | `` | `open` | PROJECT-GTKB-DASHBOARD-OBSERVABILITY | work item already has an active membership in a non-terminal project |
| `GTKB-GOV-004` | `` | `open` | PROJECT-GTKB-GOVERNANCE-HARDENING | work item already has an active membership in a non-terminal project |
| `WI-4508` | `normal` | `open` | PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE | work item already has an active membership in a non-terminal project |

## dangling_or_terminal_project_membership

| Work Item | Priority | Status | Candidate Projects | Reason |
|---|---|---|---|---|
| `WI-4851` | `P3` | `open` | PROJECT-GTKB-AD-HOC-RELEASE-20260701, PROJECT-GTKB-AD-HOC-RELEASE-20260701-DISPATCH-UNBLOCK, PROJECT-GTKB-AD-HOC-RELEASE-20260701-DISPATCHER-SUBSTRATE, PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS, PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, PROJECT-GTKB-DASHBOARD-OBSERVABILITY, PROJECT-GTKB-ENV-SOT-TOPOLOGY, PROJECT-GTKB-GOVERNANCE-HARDENING, PROJECT-GTKB-MAY29-HYGIENE-STARTUP-RELAY, PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE, PROJECT-GTKB-PROTECTED-ARTIFACT-DRIFT-ROLLUP, PROJECT-GTKB-RELIABILITY-FIXES, PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-ADVERSARIAL-REVIEW, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-SESSIONS, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-FORMALIZATION-PREP, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-ACTIVITY-LOADER, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-BLOCKER-REPAIRS, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-COMPACT-CLI, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-HARNESS-PROJECTION, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-MEASUREMENT, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARD-MIGRATION, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARDING-CONTRACT, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-UMBRELLA, PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT, PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE, PROJECT-OMNIGENT-ALIGNMENT | membership exists but is inactive, missing, or points to a terminal project |
| `GTKB-DASHBOARD-RETENTION` | `` | `deferred` | PROJECT-GTKB-DASHBOARD-OBSERVABILITY | membership exists but is inactive, missing, or points to a terminal project |
| `GTKB-MASS-001` | `` | `open` | GTKB-V1-RELEASE-STRATEGY-001 | membership exists but is inactive, missing, or points to a terminal project |
| `WORKLIST-OWNER-DIRECTED-BACKLOG-ADDITION-2026-04-17-CLAUDE-DESIGN-GUI-EXPLORATION` | `` | `open` |  | membership exists but is inactive, missing, or points to a terminal project |
| `WORKLIST-ZERO-KNOWLEDGE-ARCHITECTURE-PHASE-4-LONGER-TERM` | `` | `open` |  | membership exists but is inactive, missing, or points to a terminal project |

## existing_project_candidate_exact

_No rows._

## existing_project_candidate_weak

| Work Item | Priority | Status | Candidate Projects | Reason |
|---|---|---|---|---|
| `WI-4535` | `P2` | `open` | PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 | title/id/component tokens weakly match an active project |
| `WI-4562` | `P2` | `open` | PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-SESSIONS | title/id/component tokens weakly match an active project |
| `WI-4827` | `P2` | `open` | PROJECT-GTKB-MAY29-HYGIENE-STARTUP-RELAY | title/id/component tokens weakly match an active project |
| `WI-4193` | `high` | `open` | PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE | title/id/component tokens weakly match an active project |
| `WI-4174` | `low` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-ACTIVITY-LOADER, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-BLOCKER-REPAIRS, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-COMPACT-CLI, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-HARNESS-PROJECTION, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-MEASUREMENT, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARD-MIGRATION, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARDING-CONTRACT, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-UMBRELLA | title/id/component tokens weakly match an active project |
| `WI-4176` | `low` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-ACTIVITY-LOADER, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-BLOCKER-REPAIRS, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-COMPACT-CLI, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-HARNESS-PROJECTION, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-MEASUREMENT, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARD-MIGRATION, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARDING-CONTRACT, PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-UMBRELLA | title/id/component tokens weakly match an active project |
| `WI-4177` | `low` | `open` | PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 | title/id/component tokens weakly match an active project |
| `WI-4178` | `low` | `open` | PROJECT-GTKB-GOVERNANCE-HARDENING | title/id/component tokens weakly match an active project |
| `WI-4188` | `low` | `open` | PROJECT-GTKB-MAY29-HYGIENE-STARTUP-RELAY | title/id/component tokens weakly match an active project |
| `WI-4198` | `low` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-SHARD-MIGRATION | title/id/component tokens weakly match an active project |
| `WI-4401` | `low` | `open` | PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY | title/id/component tokens weakly match an active project |
| `WI-4410` | `low` | `open` | PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1 | title/id/component tokens weakly match an active project |
| `WI-4436` | `low` | `open` | PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY | title/id/component tokens weakly match an active project |
| `WI-4446` | `low` | `open` | PROJECT-GTKB-MAY29-HYGIENE-STARTUP-RELAY | title/id/component tokens weakly match an active project |
| `WI-4465` | `low` | `open` | PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY, PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-ADVERSARIAL-REVIEW | title/id/component tokens weakly match an active project |

## new_project_candidate_cluster

| Work Item | Priority | Status | Candidate Projects | Reason |
|---|---|---|---|---|
| `WI-4455` | `P0` | `open` |  | unmatched compatibility cluster has 5 non-terminal work items |
| `WI-4545` | `P1` | `open` |  | unmatched compatibility cluster has 5 non-terminal work items |
| `WI-4702` | `P2` | `open` |  | unmatched compatibility cluster has 6 non-terminal work items |
| `WI-4705` | `P2` | `open` |  | unmatched compatibility cluster has 5 non-terminal work items |
| `WI-4712` | `P2` | `open` |  | unmatched compatibility cluster has 6 non-terminal work items |
| `WI-4725` | `P2` | `open` |  | unmatched compatibility cluster has 4 non-terminal work items |
| `WI-4764` | `P2` | `open` |  | unmatched compatibility cluster has 6 non-terminal work items |
| `WI-4802` | `P2` | `open` |  | unmatched compatibility cluster has 2 non-terminal work items |
| `WI-4837` | `P2` | `open` |  | unmatched compatibility cluster has 6 non-terminal work items |
| `WI-4849` | `P2` | `open` |  | unmatched compatibility cluster has 6 non-terminal work items |
| `WI-4539` | `P3` | `open` |  | unmatched compatibility cluster has 5 non-terminal work items |
| `WI-4721` | `P3` | `open` |  | unmatched compatibility cluster has 4 non-terminal work items |
| `WI-4722` | `P3` | `open` |  | unmatched compatibility cluster has 4 non-terminal work items |
| `WI-4726` | `P3` | `open` |  | unmatched compatibility cluster has 4 non-terminal work items |
| `WI-4748` | `P3` | `open` |  | unmatched compatibility cluster has 2 non-terminal work items |
| `WI-4867` | `P3` | `open` |  | unmatched compatibility cluster has 2 non-terminal work items |
| `WI-4274` | `high` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4308` | `high` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4409` | `high` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4165` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4166` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4167` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4168` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4169` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4170` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4171` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4172` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4173` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4175` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4179` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4180` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4181` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4182` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4183` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4184` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4185` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4186` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4187` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4189` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4190` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4191` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4192` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4194` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4195` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4196` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4197` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4199` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4200` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4201` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4202` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4203` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4204` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4205` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4206` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4207` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4208` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4209` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4210` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4211` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4212` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4219` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4221` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4224` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4226` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4239` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4240` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4247` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4252` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4260` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4261` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4262` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4263` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4265` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4275` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4276` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4277` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4284` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4285` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4287` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4288` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4290` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4309` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4310` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4311` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4312` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4313` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4314` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4359` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4397` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4400` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4406` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4407` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4408` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4411` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4439` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4444` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4445` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4447` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4448` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |
| `WI-4467` | `low` | `open` |  | unmatched compatibility cluster has 98 non-terminal work items |

## single_wi_project_candidate

_No rows._

## obsolete_or_duplicate_candidate

| Work Item | Priority | Status | Candidate Projects | Reason |
|---|---|---|---|---|
| `WI-4538` | `P2` | `open` |  | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4536` | `P3` | `open` |  | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4736` | `P3` | `open` | PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4822` | `P3` | `open` |  | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4825` | `P3` | `open` | PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4826` | `P3` | `open` |  | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4832` | `P3` | `open` |  | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4835` | `P3` | `open` |  | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4836` | `P3` | `open` |  | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4847` | `P3` | `open` | PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING, PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT, PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1 | work item carries obsolete, duplicate, superseded, or retirement signal |
| `WI-4222` | `low` | `open` | PROJECT-LO-ADVISORY-OWNER-GRILLING-GATE-001 | work item carries obsolete, duplicate, superseded, or retirement signal |

## dependency_blocked_candidate

_No rows._

## needs_manual_triage

| Work Item | Priority | Status | Candidate Projects | Reason |
|---|---|---|---|---|
| `WI-4563` | `P2` | `open` |  | no active membership, project candidate, duplicate signal, or cluster signal found |
| `WI-4650` | `P2` | `open` |  | no active membership, project candidate, duplicate signal, or cluster signal found |
| `WI-4808` | `P2` | `open` |  | no active membership, project candidate, duplicate signal, or cluster signal found |
| `WI-4669` | `P3` | `open` |  | no active membership, project candidate, duplicate signal, or cluster signal found |
| `WI-4719` | `P3` | `open` |  | no active membership, project candidate, duplicate signal, or cluster signal found |
| `WI-4890` | `P3` | `open` |  | no active membership, project candidate, duplicate signal, or cluster signal found |
| `WI-4405` | `` | `open` |  | no active membership, project candidate, duplicate signal, or cluster signal found |
