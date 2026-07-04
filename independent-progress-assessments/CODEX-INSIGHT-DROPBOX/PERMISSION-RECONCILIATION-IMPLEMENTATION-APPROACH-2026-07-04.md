# Permission Reconciliation Implementation Approach

Status: Prime Builder implementation output for `WI-5005`; awaits bridge verification.
Date: 2026-07-04
Bridge thread: `gtkb-wi5005-permission-reconciliation-approach`
Project: `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION`
Work item: `WI-5005`
Owner decisions: `DELIB-20260703-GTKB-PREMISSION-RECONCILIATION-DIRECTIVE`, `DELIB-20260703-GTKB-MUTATION-PERMISSION-GENERAL-PRIMITIVE-FIRST`

## Claim

GT-KB should implement a general mutation-permission control plane first, then treat dispatcher quiesce as the first concrete adapter and hardening case. A dispatcher-only quiesce fix has already reduced the immediate failure mode, but it does not cover the broader owner concern: GT-KB still lacks a common authority model for operational mutations, configuration changes, canonical artifact writes, git/deploy actions, cleanup, and emergency recovery.

This report defines the approach and a normalized downstream work-item sequence. It does not create those downstream MemBase work items and does not mutate source, tests, configuration, deployment state, or canonical specifications.

## Current Evidence

- `WI-5005` is the active P1 seed item for a bridge-ready implementation approach and normalized downstream work-item list. The live MemBase record requires coverage for durable quiesce, activity-window authority, adversarial diligence, emergency handling, audit evidence, rollback/cancel semantics, branch/dispatch constraints, relationship to `WI-4997`, and downstream sequencing.
- `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION` is active and intentionally scoped as a discovery/proposal shell until this implementation approach exists.
- The active PAUTH for this slice allows only `bridge` and `metadata` mutation classes for `WI-5005`; it does not authorize source/config/test mutation.
- The approved bridge thread is latest `GO` at `bridge/gtkb-wi5005-permission-reconciliation-approach-002.md`.
- `WI-4997` is now resolved by `gtkb-wi4997-time-bound-dispatch-quiesce`, but its original failure mode remains the canonical first case: a dispatched/autonomous process re-enabled dispatch after an operator quiesce.
- Existing dispatcher quiesce state is file-backed at `.gtkb-state/bridge-poller/operator-quiesce.json` and exposed through `operator_quiesce_status`, `set_operator_quiesce`, and `clear_operator_quiesce` in `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py:177`, `:238`, and `:281`.
- Dispatcher runtime and daemon paths suppress spawns when operator quiesce is active. Evidence includes `scripts/gtkb_dispatcher_daemon.py:795`, `:1232`, `:1484`, and `:1492`.
- Existing tests cover runtime/daemon spawn suppression and dispatch status/report visibility: `platform_tests/scripts/test_dispatcher_runtime.py:436`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py:441`, and `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py:197`.
- Activity envelopes already classify session topics as `ops`, `deliberation`, `build`, `test`, `spec`, and `project`, but this currently supports routing/preload context rather than mutation permission. Evidence: `groundtruth-kb/src/groundtruth_kb/session/envelope.py:23` through `:58`.
- Bridge-substrate switching already validates, writes audit records, and atomically updates `harness-state/bridge-substrate.json`; it is still a specialized state mutation rather than a general permission packet. Evidence: `groundtruth-kb/src/groundtruth_kb/mode_switch/bridge_substrate.py:61` through `:143` and `groundtruth-kb/src/groundtruth_kb/cli.py:8214` through `:8256`.

## Approach

### 1. Define The Primitive Before Expanding Enforcement

Create a first-class mutation-permission packet model before adding more one-off command guards. The packet should describe:

- packet id, version, hash, issuer, and creation time;
- authority source, such as owner decision, PAUTH, bridge `GO`, emergency runbook, or service policy;
- activity window id and activity envelope;
- mutation class, risk class, environment class, and target resource class;
- allowed actors, harnesses, commands, paths, repositories, environments, and services;
- TTL, activation time, expiry, single-use or reusable semantics, and renewal rules;
- expected evidence, before/after state projection, rollback/cancel path, and after-action review requirement;
- branch, worktree, dispatch, and concurrency constraints;
- explicit forbidden operations.

The packet should be validated by deterministic services, not reconstructed manually inside agent prompts.

### 2. Keep Dispatcher Quiesce As The First Adapter

Preserve the existing operator-quiesce behavior as a concrete permission type:

- `dispatch.quiesce.set` requires cause, actor, TTL, authority source, and target substrate/scope.
- `dispatch.quiesce.clear` requires either expiry, original-authority clearance, or a higher-authority cancellation packet.
- dispatched workers and daemon maintenance loops must not clear or override active operator quiesce.
- status and health reports must surface active quiesce distinctly from dispatcher failure.

The existing WI-4997 implementation is useful, but future work should route quiesce set/clear through the general permission packet so it composes with other mutation classes and audit trails.

### 3. Use A Tiered Mutation Taxonomy

Not every operation should pay the same friction cost.

| Class | Examples | Default authority |
| --- | --- | --- |
| `read_only` | status, report, inventory, health checks | standing policy; no mutation packet unless exporting formal evidence |
| `metadata` | bridge reports, insight reports, project membership notes | bridge `GO` or PAUTH-scoped packet |
| `bounded_maintenance` | generated-cache cleanup, local repair, format-only cleanup | packet with target paths, rollback/cancel, and evidence |
| `configuration_mutation` | dispatcher state, harness routing, hooks, CI, bridge substrate | bridge `GO` plus activity-window packet |
| `canonical_artifact_mutation` | GOV/ADR/DCL/SPEC/procedure/status promotion | formal approval evidence plus bridge `GO` where implementation is involved |
| `repository_state_mutation` | commits, pushes, tags, branch operations | verified include-set and commit/push authority |
| `environment_mutation` | deploys, production user/security/data changes | owner or delegated runbook authority, environment evidence, rollback |
| `emergency_break_glass` | dispatcher-unavailable repair, single-harness recovery | explicit cause, minimal scope, TTL, after-action LO review |

### 4. Preserve Adversarial Diligence Without Blocking Recovery

Normal implementation remains bridge-governed: Prime proposes, Loyal Opposition reviews, Prime implements, and Loyal Opposition verifies. Emergency and single-harness cases should not pretend to be ordinary `GO` reviews.

The compensating path should require:

- explicit cause and failure condition;
- reason normal adversarial diligence was unavailable;
- minimal mutation scope and TTL;
- owner/proxy authority when reachable;
- automatic after-action Loyal Opposition review once an independent context is available;
- mandatory conversion of permanent policy or product changes into a normal bridge proposal.

This protects the meaning of `GO` and `VERIFIED` while still allowing bounded recovery when the dispatcher or counterpart harness is unavailable.

### 5. Make The Action Record Queryable

Every material mutation should emit a structured action record, separate from compatibility markdown views:

- requested intent and authority source;
- packet id/hash and activity window;
- actor, harness, session, process, and command;
- target paths/resources/environments;
- before/after projection or diff reference;
- result, errors, rollback/cancel status, and evidence paths;
- required verifier and after-action status.

Bridge files, insight reports, and dashboards can project this record, but the durable mutation trail should be transactional and queryable from MemBase or a governed service-owned state store.

### 6. Enforce At The Lowest Practical Control Point

The enforcement plan should layer checks rather than rely on prompt obedience:

- CLI guard: validate packet and target scope before mutating commands run.
- Service/API guard: validate packet inside any dashboard, daemon, or future LAN authority service endpoint.
- Worker guard: dispatched workers receive a bounded activity window and cannot exceed its paths, commands, or TTL.
- Hook guard: keep local hooks as a last-mile backstop for file writes and bridge compliance.
- Status guard: report active permissions, blocked attempts, and expired/cancelled windows.
- Test guard: regression tests must cover denial, expiry, cancellation, stale packet rejection, and autonomous re-enable prevention.

## Downstream Work-Item Proposal

The following items are proposed, not inserted into MemBase by this implementation slice. Create them only after this report receives Loyal Opposition verification or an owner/Prime follow-on authorization explicitly allows creation.

| Order | Proposed title | Component | Priority | Depends on | Deliverable |
| --- | --- | --- | --- | --- | --- |
| 1 | Inventory GT-KB and adopter mutation surfaces | governance | P1 | `WI-5005` | Report listing CLI, scripts, hooks, daemons, dashboard/API paths, bridge writers, git/deploy operations, canonical writers, application mutation paths, and current authority gaps. |
| 2 | Specify mutation permission packet schema and lifecycle | governance | P1 | item 1 | Draft GOV/DCL/SPEC set defining packet fields, activity windows, risk classes, allowed operations, expiry, renewal, cancellation, evidence, and failure modes. |
| 3 | Implement permission packet validation service | source | P1 | item 2 | Deterministic validator/API for packet creation, hash verification, scope matching, expiry checks, and denial reasons. |
| 4 | Adapt dispatcher quiesce to permission packets | dispatcher | P1 | items 2-3, `WI-4997` | Preserve current quiesce behavior while routing set/clear authority through the general packet model. |
| 5 | Gate bridge-substrate and dispatcher-state mutations | dispatcher | P1 | items 2-4 | Require packet authority for substrate switches, daemon dispatch enable/disable, target eligibility mutation, and queue/lease control changes. |
| 6 | Add activity-window enforcement to dispatched workers | dispatcher | P1 | items 3-5 | Pass bounded window metadata into workers; reject out-of-scope target paths, commands, and expired windows before mutation. |
| 7 | Gate canonical artifact and MemBase mutations | governance | P1 | items 2-3 | Require formal approval evidence plus packet authority for GOV/ADR/DCL/SPEC/procedure/status/work-item mutation paths. |
| 8 | Gate repository-state, cleanup, deploy, and environment mutations | operations | P1 | items 2-3 | Add command guards and runbook integration for commit/push/tag, destructive cleanup, deployment, credential/security, production data, and application-user changes. |
| 9 | Define emergency and single-harness exception packets | governance | P1 | item 2 | Specify break-glass cause, owner/proxy authority, minimal scope, TTL, forbidden operations, and after-action LO review requirements. |
| 10 | Implement structured mutation action log and projections | observability | P2 | items 3-9 | Add queryable action records plus CLI/dashboard/report projections for active windows, denials, expiries, after-action status, and rollback evidence. |
| 11 | Add regression and adversarial-diligence test suite | tests | P1 | items 3-10 | Unit/CLI/daemon/service tests for allowed mutation, unauthorized denial, expiry, cancellation, autonomous re-enable prevention, worker-scope enforcement, and break-glass after-action review. |
| 12 | Migrate existing specialized controls into the common model | governance | P2 | items 4-11 | Convert bridge writer, substrate switching, quiesce, project authorization, formal approval, and release/deploy gates to consistent packet/action-log semantics where appropriate. |

## Sequencing

1. Verify this report through the bridge as the `WI-5005` implementation output.
2. Create downstream work items from the table above in a single governed backlog/project mutation slice, preserving order and dependencies.
3. Bridge and implement item 1 before any source enforcement work; the inventory defines the target surface.
4. Bridge and approve item 2 before code work; the packet schema is the authority contract.
5. Implement validation service and dispatcher-quiesce adapter as the first executable slices.
6. Add enforcement slices from narrower/highest-risk surfaces outward: dispatcher state, dispatched workers, canonical artifacts, repository/environment operations.
7. Add observability/action-log projection once at least one real adapter emits records, then backfill projections for specialized controls.

## Rollback And Cancel Semantics

- Permission packet creation is additive; rollback is supersession or cancellation, not deletion.
- Active windows need explicit cancellation records with actor, authority, reason, and timestamp.
- Mutating commands must report whether a rollback is possible, unavailable, or completed.
- Emergency packets expire by default and require after-action review before permanent follow-on work.
- Existing bridge files and verified audit records remain append-only.

## Verification Plan For Downstream Slices

Future implementation proposals should map each linked requirement to executable tests. Minimum expected coverage:

- schema validation accepts complete packets and rejects missing authority, expired TTL, target mismatch, and forbidden operation attempts;
- dispatcher quiesce cannot be cleared by dispatched-worker context while active;
- substrate/dispatcher mutation commands deny stale or absent packet authority;
- worker activity window denies out-of-scope paths and commands before mutation;
- emergency packet flow records cause, TTL, scope, and after-action review requirement;
- action log records include packet hash, actor/session/harness, before/after projection, result, and rollback/cancel status.

## Residual Risks

- Current quiesce remains file-backed under the project root until a future slice moves authority to a stronger service or guarded state path.
- The project name intentionally preserves the owner's `PREMISSION` spelling; future human-facing summaries should not silently "correct" it when citing the project id/name.
- Broad enforcement can create workflow friction if read-only diagnostics or routine status checks require packets. The taxonomy above keeps read-only work outside the high-friction path.
- Single-harness exception design must avoid laundering self-review into normal `GO` or `VERIFIED`; it should be explicitly marked as compensating evidence only.

