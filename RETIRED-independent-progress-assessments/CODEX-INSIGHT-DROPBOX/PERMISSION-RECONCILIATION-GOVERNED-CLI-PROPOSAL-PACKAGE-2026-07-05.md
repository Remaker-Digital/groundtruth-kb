# Permission Reconciliation Governed CLI Proposal Package

Status: Candidate implementation proposal package; non-governing until converted into normal bridge proposals and reviewed.
Date: 2026-07-05
Project: `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION`
Seed work item: `WI-5005`
Extends: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/PERMISSION-RECONCILIATION-IMPLEMENTATION-APPROACH-2026-07-04.md`

## Claim

GT-KB should implement mutation permission around a worker-facing `skills + gt CLI` contract backed by service/API/TAFE authority. The immediate next implementation slice should inventory all mutating `gt` commands and specify the governed command manifest, central risk-policy snapshot, audit-event, and recovery/import packet schemas before enforcement code is written.

This package converts the WI-5005 clarification interview into an implementation program. It does not create downstream MemBase work items, does not mutate source/config/test code, and does not govern implementation until a follow-on bridge proposal receives normal review.

## Current Model

`NEW` is the actual current path for injecting new work into the adversarial diligence workflow. Later `GO` and `NO-GO` states continue already admitted work; they do not originate new work. Advisory entries may inject information, but do not autonomously drive work.

Direct filesystem access is still a physical enforcement gap. Any harness with filesystem access can mutate GT-KB if the harness allows it. GT-KB therefore cannot honestly claim perfect local access control. The practical goal is best-effort enforcement everywhere, especially at GT-KB-controlled surfaces, plus detection, audit, freeze, and remediation for out-of-band mutation.

The worker-facing public contract is:

> Worker-facing skills plus CLI, authority-backed service/API.

Workers use skills and `gt` because those are the low-token, uniform, intuitive surfaces. Authority lives underneath in dispatcher/service/TAFE/MemBase/policy mechanisms.

## Key Decisions Captured

Primary decision records include:

- `DELIB-202665405`, `DELIB-202665408`, `DELIB-202665409`: worker-facing surfaces, `NEW` origination, and direct filesystem enforcement reality.
- `DELIB-202665412`, `DELIB-202665414`, `DELIB-202665415`: all governed CLI mutations support adversarial diligence, but governed CLI is compliance-by-default rather than a perfect security boundary.
- `DELIB-202665417`, `DELIB-202665418`: governed CLI commands require manifest plus shared guardrails; per-invocation adversarial diligence would make the workflow consume itself.
- `DELIB-202665419`, `DELIB-202665421`: unregistered mutating `gt` commands fail closed after inventory-complete plus owner cutoff.
- `DELIB-202665423`, `DELIB-202665425`, `DELIB-202665427`: high-risk CLI invocations require separate authority; risk is policy-derived from command-declared facts; manifest and risk-policy changes require owner/proxy authority plus adversarial review.
- `DELIB-202665428`, `DELIB-202665429`, `DELIB-202665432`, `DELIB-202665433`, `DELIB-202665434`, `DELIB-202665435`, `DELIB-202665436`: central policy registry with snapshot-first access, low-risk stale-policy grace, and initial four-hour grace.
- `DELIB-202665438`, `DELIB-202665439`, `DELIB-202665440`, `DELIB-202665443`, `DELIB-202665445`: full invocation decision audit, append-only local audit log with service ingestion, pre-mutation audit required, and append-only repair supplements.
- `DELIB-202665448`, `DELIB-202665452`, `DELIB-202665453`, `DELIB-202665454`, `DELIB-202665457`, `DELIB-202665458`, `DELIB-202665459`: ingestion lag thresholds, scoped degradation, reconciliation recovery, incident freeze, and verified closure.
- `DELIB-202665460`, `DELIB-202665461`, `DELIB-202665462`, `DELIB-202665463`, `DELIB-202665464`, `DELIB-202665465`, `DELIB-202665466`, `DELIB-202665467`: service-owned/local-compatible design, import/verify/freeze migration, post-service cache/outbox semantics, and outage recovery boundaries.
- `DELIB-202665468`, `DELIB-202665469`, `DELIB-202665471`, `DELIB-202665472`, `DELIB-202665473`, `DELIB-202665474`, `DELIB-202665475`, `DELIB-202665476`: recovery/import packet contents, explicit import, review routing, service-only disposition, and visibility.
- `DELIB-202665477`, `DELIB-202665478`, `DELIB-202665479`, `DELIB-202665480`: first slice, completion bar, verification evidence, and decision to generate this proposal package.

## Architecture Position

### 1. Governed CLI Boundary

All governed CLI mutations count as supporting adversarial diligence, but only if the command meets the governed-command bar:

- registered command manifest entry;
- shared validation and audit helpers;
- stable operation ID;
- mutation class;
- risk defaults;
- required authority inputs;
- target-scope declaration;
- denial behavior;
- audit schema;
- regression/schema tests.

After migration, unregistered mutating `gt` commands fail closed. The migration window ends only after inventory completion, candidate registration review, resolution or waiver of high-risk gaps, and owner/proxy cutoff approval.

### 2. Risk And Authority

Commands declare operation facts; policy derives risk. A command may raise risk, but cannot lower policy-derived risk.

High-risk invocations require separate authority even when the command itself is governed. The authority must be bound to target, environment, action, command or packet version/window, and expected evidence.

Manifest and risk-policy changes are owner-authorized plus adversarially reviewed because they change mutation eligibility.

### 3. Policy Snapshots

Risk policy is centrally governed but snapshot-first on the hot path.

`gt` uses signed or versioned local policy snapshots for normal risk derivation. It refreshes on TTL, checkpoint, or invalidation events. Protected/high-risk mutations fail closed if the snapshot is stale, invalid, or unreachable.

Low-risk governed CLI mutations may use the last valid snapshot within a four-hour grace window. That grace applies to all low-risk governed mutations. Protected and high-risk classes have zero stale-policy grace.

### 4. Audit

Every governed mutating `gt` command emits a full invocation decision record:

- operation ID;
- command/version;
- actor, harness, and session;
- declared facts;
- derived risk;
- authority source;
- policy snapshot ID/hash;
- target resources;
- before/after summary where available;
- result;
- denial or warning reason;
- evidence pointers.

The command must write a pre-mutation intent/decision audit event before mutation. If that write fails, the mutation fails closed. The result event is written after mutation. If mutation succeeds but result-event write fails, the command enters structured deficiency/recovery handling, not automatic rollback unless rollback was declared safe and available.

Audit records are written first to an append-only local JSONL log. The service ingests those records into queryable projections.

### 5. Audit Ingestion Lag

Ingestion lag thresholds are risk-tiered:

- low-risk governed CLI audit records: 4 hours;
- protected, canonical, or configuration audit records: 1 hour;
- high-risk or authority-bearing audit records: 15 minutes.

These are alert/escalation thresholds, not rollback triggers.

When a threshold is exceeded, GT-KB alerts and applies scoped degradation: affected device/session/audit stream is marked degraded; new protected/high-risk mutations from that stream are suppressed; low-risk mutations continue only if local audit and policy grace remain valid.

Recovery from degradation requires catch-up plus reconciliation. Clean reconciliation restores low/protected eligibility automatically; high-risk still requires normal separate authority. Failed reconciliation creates an incident packet plus scoped freeze.

### 6. Incident Freeze And Closure

Failed audit reconciliation freezes conservatively across:

- affected device/session/audit stream;
- implicated target resources;
- implicated operation class.

Closure requires a verified incident closure packet containing append-only reconciliation evidence, continuity proof or gap accounting, deficiency supplements, target impact assessment, policy-validity check, and owner/LO disposition when ambiguity or elevated risk remains.

### 7. LAN Authority Service Alignment

The design is service-owned but local-compatible.

Before the LAN authority service exists, local mode may generate/read service-shaped manifest, policy snapshot, and audit-log files using the same schemas the service will later own.

When the LAN service takes over, it imports and verifies local-compatible files. Conflicts freeze affected scope plus related targets. Import conflicts include schema/version/hash validation failures, ambiguous device/session identity, audit continuity gaps, material local/service policy disagreement, unverifiable authority records, and target/resource state disagreement.

After service takeover:

- local manifest/policy files become service-generated cache/snapshot artifacts;
- local audit files remain append-only outboxes;
- local mode cannot independently change manifest or policy authority except through explicit recovery/import workflows.

### 8. Outage Recovery And Import

During LAN service outage after service authority exists, local recovery mode may:

- continue low-risk governed CLI operations within valid policy snapshot/audit grace;
- create recovery/import packets with outage evidence.

It may not change manifest or policy authority locally.

Recovery/import packets include outage start/end evidence, last valid policy snapshot ID/hash, commands run, audit event IDs, target resources, derived risks, authority used, deficiencies, and requested import/reconciliation action.

`gt` maintains a recovery/import packet draft automatically during outage mode. Import/reconciliation is explicit after reconnection.

Launch authority is policy-routed:

- clean low-risk packets may be launched by a scoped registered worker/device;
- protected, high-risk, authority-bearing, deficient, or ambiguous packets require owner/proxy launch or LO/owner disposition.

The service may auto-accept clean low-risk records only. Non-auto-accepted records route through policy review:

- protected/canonical/configuration -> LO review;
- high-risk/authority-bearing -> owner/proxy review;
- conflicts/deficiencies -> incident path.

Recovery/import review surfaces as service review items. A normal `NEW` bridge proposal is required when disposition creates new implementation, remediation, policy change, canonical mutation, or target-resource repair.

## First Implementation Slice

Title: Governed CLI Inventory And Manifest Specification

Scope:

- inventory all mutating `gt` commands;
- classify commands by mutation class and target resource class;
- identify currently unclassified or ambiguous mutating commands;
- draft the command manifest schema;
- draft the risk-policy snapshot schema and defaults;
- draft the full invocation audit event schema;
- draft the recovery/import packet schema;
- define migration cutoff mechanics;
- define static inventory and schema-test verification.

Out of scope for slice 1:

- enforcing command manifest at runtime;
- implementing local audit emission;
- implementing policy snapshot refresh/invalidation;
- implementing service ingestion;
- modifying existing mutating commands beyond discovery scaffolding required for inventory;
- creating downstream MemBase work items unless separately authorized.

Completion bar:

- mutating CLI inventory exists and is reproducible;
- manifest schema exists and includes every required field;
- policy snapshot schema includes risk derivation defaults, stale-policy grace, and ingestion-lag thresholds;
- audit event schema supports full invocation decision records;
- recovery/import packet schema supports outage evidence plus local mutation ledger;
- migration plan defines warning phase, cutoff criteria, owner/proxy cutoff approval, and fail-closed behavior;
- test plan maps every schema and inventory claim to deterministic checks.

Verification evidence:

- deterministic inventory check enumerates mutating `gt` commands;
- inventory check flags unclassified mutations;
- schema tests validate example command manifest, policy snapshot, audit event, and recovery/import packet records;
- cutoff logic is represented in a tested or statically verified policy fixture;
- no executable enforcement prototype is required in this slice unless separately scoped.

## Proposed Downstream Work Items

These are proposed work items, not yet inserted into MemBase.

| Order | Proposed title | Component | Priority | Depends on | Deliverable |
| --- | --- | --- | --- | --- | --- |
| 1 | Governed CLI inventory and manifest specification | governance/cli | P1 | `WI-5005` | Inventory, schemas, policy defaults, migration plan, and static verification checks. |
| 2 | Governed CLI manifest registry and migration warning mode | cli/governance | P1 | item 1 | Manifest registry loader, unregistered mutating command detection, warning/audit phase, cutoff readiness report. |
| 3 | Shared governed CLI validation and audit helpers | cli/source | P1 | item 1 | Shared helpers for command fact declaration, risk derivation, authority validation, pre/post audit events, and denial diagnostics. |
| 4 | Local append-only audit log foundation | cli/observability | P1 | items 1,3 | Local JSONL audit outbox with pre-mutation fail-closed behavior and result-event deficiency handling. |
| 5 | Policy snapshot generation and validation | governance/cli | P1 | items 1,3 | Signed or versioned policy snapshots, TTL/grace validation, invalidation hooks, stale-snapshot denial behavior. |
| 6 | Governed CLI enforcement migration slice | cli/source | P1 | items 2-5 | Apply manifest plus shared guardrails to selected high-value mutating `gt` commands; keep unregistered commands in migration warning until cutoff. |
| 7 | Audit ingestion and projection service, local-compatible mode | service/observability | P1 | item 4 | Ingest local audit outbox into queryable service/projection state; expose dashboard/API/`gt` status views. |
| 8 | Audit lag degradation and incident-freeze workflow | service/ops | P1 | item 7 | Risk-tiered ingestion lag thresholds, scoped degradation, reconciliation, incident packets, verified closure packets. |
| 9 | Recovery/import packet workflow for LAN service outage | service/ops | P1 | items 5,7 | Automatic outage draft packets, explicit launch, policy-routed import/review, clean low-risk auto-accept. |
| 10 | LAN authority service import-and-verify takeover path | service/migration | P1 | items 7-9 | Import local-compatible manifest/policy/audit files, verify, freeze conflicts, require verified import closure packets. |
| 11 | Command manifest cutoff and fail-closed activation | governance/cli | P1 | items 2-10 | Owner/proxy cutoff approval path; unregistered mutating commands fail closed after inventory-complete migration. |
| 12 | Dispatcher/quiesce and mutation-permission adapter integration | dispatcher/ops | P1 | items 3-5 | Route dispatcher quiesce and dispatcher-state changes through governed CLI/permission mechanisms. |
| 13 | Canonical/artifact/repository/environment mutation integration | governance/ops | P2 | items 3-11 | Extend governed mutation handling to canonical artifacts, MemBase, repository state, cleanup, deploy, and environment mutations. |
| 14 | Operator UX and dashboard visibility | dashboard/cli | P2 | items 7-10 | Dashboard/API/`gt` projections for active policies, stale snapshots, audit lag, degraded streams, incident freezes, and recovery/import queues. |
| 15 | Full regression and adversarial-diligence test suite | tests | P1 | items 3-14 | Tests for denied mutations, stale snapshots, audit write failure, lag degradation, recovery import, freeze closure, and manifest cutoff. |

## Acceptance Invariants

- A mutating `gt` command cannot be called governed unless it is manifest-registered and uses shared guardrails.
- After the migration cutoff, unregistered mutating `gt` commands fail closed.
- High-risk invocations require separate authority even for governed commands.
- Commands may raise risk but may not lower policy-derived risk.
- Manifest and risk-policy changes require owner/proxy authority plus adversarial review.
- Protected/high-risk mutations fail closed on stale or invalid policy snapshots.
- Low-risk governed mutations may use last valid policy snapshot for four hours.
- Pre-mutation audit write failure blocks mutation.
- Post-mutation audit failure creates structured deficiency/recovery, not silent success.
- Audit records are append-only; repair uses append-only supplements.
- Audit ingestion lag triggers scoped degradation by policy threshold.
- Failed reconciliation creates incident packet plus conservative scoped freeze.
- Verified closure evidence is required before frozen trust is restored.
- LAN service import conflicts freeze affected scopes plus related targets.
- Local mode after service takeover is cache/outbox only, not independent policy/manifest authority.
- Service-only recovery/import review is limited to import disposition; downstream implementation/remediation/policy/canonical mutation requires `NEW` bridge proposal.

## Residual Risks

- The direct filesystem gap remains real. This program improves the compliant path and controlled surfaces; it does not create impossible local security.
- A broad governed CLI exception increases the importance of manifest quality. The inventory slice must be adversarially reviewed.
- Snapshot-first policy avoids hot-path contention but requires strong invalidation and stale-snapshot tests.
- Rich audit records may create local log volume. The implementation should include retention/rotation design without weakening append-only evidence.
- LAN service migration can create authority confusion if local-compatible files are not clearly labeled cache/outbox after takeover.

## Recommended Next Action

Create a normal bridge proposal for the first implementation slice: Governed CLI Inventory And Manifest Specification.

That proposal should cite this package, the WI-5005 seed item, and the deliberation IDs above. It should not propose runtime enforcement yet; it should deliver the inventory, schemas, policy defaults, migration cutoff plan, and static verification checks needed for later implementation slices.
