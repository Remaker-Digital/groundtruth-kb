# LAN Authority Service Architecture Decision Packet

Date: 2026-07-04 15:37 UTC

Status: candidate architecture / non-authoritative discovery packet

Project: `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY`

Work items: `WI-4909`, `WI-4910`, `WI-4911`

Project authorization: `PAUTH-PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-ADR-DRAFTING`

Authority boundary: This packet is discovery evidence only. It is not a formal ADR, DCL, GOV, specification, implementation proposal, bridge `GO`, or source-change authority. It does not authorize protected source/config/test mutation, substrate migration, direct database mutation, or bypass of the bridge proposal, implementation-start, implementation-report, and Loyal Opposition verification gates.

## Claim

The current least-regret target architecture is a central GT-KB authority/control-plane service on the LAN, with registered harness workers and an authenticated tablet UI client. The service should initially be modeled as the owner of live orchestration state, scheduling, dispatch injection, leases, dashboard/API access, and worker registration, while the governed backlog, bridge artifacts, and formal specs remain under their current authorities until a follow-on ADR/DCL/GOV set changes them.

The recommended first formalization posture is service-owned SQLite as the initial persistence model, with all writes local to the authority host and mediated through the service or governed CLI. PostgreSQL should remain an explicit upgrade candidate rather than a prerequisite for the first architecture slice, because the owner decision is discovery-first and the next step is still governance formalization, not runtime implementation.

## Evidence

- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-FIRST-RELEASE`: owner chose discovery-first release planning and explicitly deferred implementation umbrellas until investigation projects resolve substrate questions.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-LAN-AUTHORITY-SERVICE`: owner chose a central LAN GT-KB authority/control-plane service, registered worker harnesses, and authenticated tablet UI access.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-FIRST-DELIVERABLE-ARCHITECTURE-DECISION-PACKET`: owner chose this Architecture Decision Packet as the first concrete discovery deliverable.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-ADP-INSIGHTS-DROPBOX-LOCATION`: owner chose `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` and an `INSIGHTS-...` discovery packet class.
- `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY`: active project scope is discovery and planning only.
- `PAUTH-PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-ADR-DRAFTING`: active authorization allows governance work for `WI-4909`, `WI-4910`, and `WI-4911`; it forbids source implementation, substrate migration, and protected-file mutation.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPS-LIFECYCLE-DISPATCHER-MODEL-CONSOLIDATION-2026-07-02.md`: non-authoritative consolidation report recommending governance-only formalization of the OPS lifecycle and dispatcher model before source implementation.

## Current Situation

GT-KB currently coordinates bridge-governed work through MemBase, bridge status files, TAFE/dispatcher-backed state, work-intent claims, dispatcher runtime, and harness-specific workers. Recent bridge and harness outage recovery work improved dispatch safety, circuit-breaker behavior, launch hygiene, and mutation guarding, but the current runtime remains workstation-local and artifact-centric.

The target operating scenario is single owner / multiple workstations: Windows for Codex and Claude Code, Mac for Goose/OpenRouter and Antigravity, a separate Mac for Ollama/local/cloud models on wired LAN, and a tablet over Wi-Fi for status, scheduling visibility, and pre-created one-off dispatch injection.

## Resolved Decisions

- Release posture: discovery-first. Do not create implementation umbrellas until the architecture and substrate questions are answered.
- Authority model: central LAN authority/control-plane service, not peer-replicated GT-KB state.
- First deliverable: non-authoritative Architecture Decision Packet.
- Packet location: `CODEX-INSIGHT-DROPBOX` as an `INSIGHTS-...` artifact.
- Current bridge discipline remains active: ordinary work flows through bridge proposals, GO/NO-GO/VERIFIED, work-intent claims, implementation reports, and LO verification.

## Options

### Option A - Service-Owned SQLite First

Summary: Run one LAN authority service on the owner-selected host. The service owns live orchestration state and writes to a local SQLite/MemBase/TAFE-backed store on that host. Workers and tablet clients interact through authenticated APIs or service-client CLI calls. Network-share multiwriter SQLite is explicitly prohibited.

Strengths:
- Implementable with the current GT-KB persistence stack and operational knowledge.
- Preserves the existing MemBase and bridge artifact model while reducing direct multi-process write pressure.
- Lower migration cost than PostgreSQL-first.
- Reversible during early slices because the current dispatcher can remain the production path until service slices are verified.

Weaknesses:
- Single authority host remains a single operational dependency.
- Concurrency safety depends on service mediation and correct fallback discipline.
- May require a later PostgreSQL migration if multi-client write volume or long-lived API usage exceeds SQLite comfort.

Dependencies:
- Formal service authority ADR/DCL/GOV set.
- Explicit CLI service-client default and fallback contract.
- Worker registration and lease lifecycle spec.
- Management-plane security policy.

Reversibility:
- High for governance and read-only/status slices.
- Medium once dispatch injection and live lease ownership move behind the service.

### Option B - PostgreSQL First

Summary: Treat PostgreSQL or an equivalent service-owned SQL backend as a prerequisite before the LAN authority service owns coordination writes.

Strengths:
- Stronger multi-client concurrency posture.
- Cleaner long-term path for service-owned state, API access, dashboards, and tablet workflows.
- Reduces pressure to invent SQLite-specific coordination controls.

Weaknesses:
- Higher operational burden and migration cost before the architecture is fully approved.
- Adds infrastructure decisions before the owner has resolved host placement, API runtime, security, and migration sequencing.
- Risks turning a discovery project into a substrate implementation project prematurely.

Dependencies:
- New deployment and backup/restore posture.
- Formal DB migration and compatibility plan.
- Release gate and recovery procedure updates.

Reversibility:
- Medium to low once production authority moves to PostgreSQL.

### Option C - Peer / Shared-Root Multiwriter Topology

Summary: Multiple workstations directly coordinate against shared GT-KB files or database state, with no single LAN authority service.

Strengths:
- Appears to reduce central host dependency.
- Could seem familiar for file-based workflows.

Weaknesses:
- Conflicts with the owner-selected central authority model.
- Reintroduces direct multiwriter and network-share corruption risk for SQLite and file artifacts.
- Makes bridge, MemBase, dispatcher leases, and implementation evidence harder to audit.

Dependencies:
- A different owner decision reversing the central authority service target.

Reversibility:
- Low if allowed to write live project state.

Recommendation: choose Option A for the next formalization loop. Keep Option B as an explicit future promotion path. Reject Option C for the current program.

## Component Boundaries

- Authority service: owns live orchestration state, worker registration, worker liveness, dispatch scheduling, dispatch injection, leases, dashboard/API projection, and eventually service-mediated coordination writes if formalized.
- MemBase/backlog: remains the governed backlog and project/work-item source of truth until a formal artifact changes the access boundary.
- Bridge artifacts: remain the governed proposal, verdict, implementation report, and verification evidence trail. The service may route or project bridge work, but must not make bridge artifacts obsolete or silently replace bridge status semantics.
- Dispatcher daemon: remains the current production dispatcher until a verified migration slice moves a bounded responsibility.
- Harness workers: register with durable harness identity, role, capabilities, model/runtime constraints, and health. Workers execute authorized packets and report lifecycle events, but do not independently invent authority.
- Tablet UI client: observes operational state and may inject pre-created dispatches only through authenticated, validated, auditable APIs.
- CLI: remains the default human and automation control surface. In the service era, `gt` should become a service client by default when the authority service is reachable, with explicit local fallback behavior.

## API And Worker Model

The service API should expose only bounded management-plane operations at first:

- health/status projection
- worker registration and heartbeat
- capability and role advertisement
- dispatch packet listing and injection for pre-created packets
- lease claim/release/expiry
- append-only lifecycle event recording
- dashboard/tablet read models

Workers should register with:

- durable harness ID
- resolved role and dispatch lane eligibility
- host, OS, and runtime envelope
- model/provider availability when relevant
- allowed mutation class and work-intent constraints
- last heartbeat and current claim/lease state

Dispatch packets should include:

- project and work-item linkage
- bridge thread and latest status evidence
- work-intent claim identifier
- target path class and protected-mutation authorization evidence
- context freshness/TTL metadata
- expected implementation-report or verdict output path
- allowed mutation classes and forbidden operations

## Persistence Model

Initial recommendation:

- Use service-owned SQLite on the authority host for the first service-governance and read-only/status slices.
- Permit writes only through the authority service or governed CLI paths that enforce the same validation.
- Prohibit network-share multiwriter SQLite and direct database writes by workers.
- Keep append-only lifecycle events as first-class records, with projection tables or dashboard JSON treated as derived views.
- Define a PostgreSQL promotion trigger before implementation: for example, concurrent write load, multi-user expansion, tablet/API write volume, backup/restore needs, or service restart/recovery evidence.

Open persistence questions:

- Should MemBase remain a file-backed SQLite database owned by the authority service, or should MemBase become an API-only service boundary before dispatch migration?
- Should TAFE/bridge state remain file-artifact primary with service projections, or should the service eventually own bridge event indexing while files remain evidence?
- What backup, compaction, and recovery evidence is mandatory before service-owned writes become production authority?

## Security Model

Minimum expected policy:

- LAN-only service binding by default.
- Authenticated tablet and worker clients.
- Distinct worker credentials from owner tablet credentials.
- No raw credentials in bridge files, implementation reports, packet context, or dashboard projection artifacts.
- Token storage and rotation policy before any tablet write capability.
- Role-scoped operations: observation, packet injection, claim/release, governance mutation, and source mutation remain separate capabilities.
- Audit event for every dispatch injection, claim, release, timeout, cancellation, and service-mediated governance mutation.

Open security questions:

- Should the first service use bearer tokens, mTLS, OS-user trust, or another local-network credential model?
- Where should worker and tablet credentials be stored on Windows and Mac?
- What is the owner-approved emergency recovery path when a token leaks or a tablet is lost?

## Packet Lifecycle

1. Candidate packet in `CODEX-INSIGHT-DROPBOX` (this artifact).
2. Loyal Opposition/adversarial review under `WI-4909`.
3. Owner grilling and deliberation capture for the high-priority open questions under `WI-4910`.
4. Formal ADR/DCL/GOV candidate set under `WI-4911`.
5. Governance-only bridge proposal for formalization.
6. Separate implementation work items and PAUTH for any source/config/test mutation.
7. Post-implementation reports and LO verification for each implementation slice.
8. Packet is superseded or retired once formal artifacts become authoritative.

## Migration Path

Phase 0 - Current production path:
- Keep the dispatcher daemon, bridge file protocol, MemBase backlog, work-intent claims, and guarded mutation boundaries as the live system.

Phase 1 - Governance formalization:
- Adopt service authority vocabulary, role boundaries, packet lifecycle, lifecycle-first/scoring-last precedence, and security/persistence posture as formal candidates.

Phase 2 - Read-only service projection:
- Build a service that reads and projects dispatcher, bridge, work-item, and worker state without owning writes.

Phase 3 - Worker registration and leases:
- Move worker registration, health, and lease lifecycle behind service-mediated APIs while preserving existing bridge evidence.

Phase 4 - Dispatch injection:
- Allow authenticated injection of pre-created dispatch packets, guarded by bridge status, work-intent claims, and target-path authorization evidence.

Phase 5 - Coordination-write ownership:
- Move selected coordination writes to the authority service only after formal artifacts, tests, and rollback procedures are verified.

Phase 6 - Persistence promotion if needed:
- Promote to PostgreSQL or another service-owned backend only when a documented trigger and migration proposal are approved.

## Risks And Mitigations

- Risk: service becomes a second backlog authority. Mitigation: formal artifacts must keep MemBase/project/work-item authority explicit and require service views to be projections unless a later ADR changes that boundary.
- Risk: dispatch injection bypasses bridge GO or work-intent claims. Mitigation: packet validation must require current bridge status, work-intent claim, target paths, and implementation-start evidence before protected mutation.
- Risk: SQLite corruption through multi-node shared-root writes. Mitigation: prohibit direct worker DB writes and network-share multiwriter SQLite; all writes go through one authority host or service.
- Risk: tablet write access expands too quickly. Mitigation: start with observation and pre-created dispatch injection only; require separate security review before arbitrary task creation or mutation.
- Risk: model/routing optimization outruns lifecycle discipline. Mitigation: lifecycle-first/scoring-last ordering must remain formal: bridge actionability and authorization gates are checked before lane scoring.
- Risk: outage recovery work creates contradictory runtime records. Mitigation: use `WI-4960` portfolio-control findings and current MemBase/project state as the portfolio check before filing implementation umbrellas.

## Candidate Implementation Umbrellas

These are future candidates only, not implementation approval:

- Runtime orchestration formal-governance umbrella: ADR/DCL/GOV set for service authority, dispatch packet lifecycle, persistence posture, and management-plane security.
- Read-only authority-service projection umbrella: status, dashboard, and worker registry projection without coordination writes.
- Worker registration and lease umbrella: harness registration, role/capability advertisement, heartbeat, lease claim/release/expiry.
- CLI service-client umbrella: `gt` client routing to authority service with explicit local fallback and error handling.
- Dispatch packet injection umbrella: pre-created packet validation, tablet-safe injection, and audit trail.
- Coordination-write ownership umbrella: service-mediated MemBase/TAFE/dispatcher writes after read-only and lease slices are verified.
- Persistence promotion umbrella: PostgreSQL or equivalent if the owner accepts the operational burden and trigger evidence justifies the migration.

## Formal Artifact Candidate Set

Dependency order for `WI-4911`:

1. `ADR-LAN-AUTHORITY-SERVICE-TARGET` - central LAN authority/control-plane service is the target topology.
2. `DCL-RUNTIME-ORCHESTRATION-DISCOVERY-FIRST` - implementation umbrellas wait for architecture decisions and formalization.
3. `GOV-RUNTIME-AUTHORITY-SERVICE-BOUNDARY` - authority service may project and mediate live state but cannot silently replace MemBase, bridge artifacts, or specs.
4. `DCL-BRIDGE-ARTIFACT-BOUNDARY` - bridge files remain governed evidence; service records are projections or lifecycle events unless formally elevated.
5. `DCL-WORKER-REGISTRATION-AND-LEASES` - worker identity, role, capability, heartbeat, claim, release, expiry, and cancellation semantics.
6. `GOV-DISPATCH-PACKET-LIFECYCLE` - required packet fields, TTL/freshness, authorization evidence, implementation-report expectations, and terminal disposition.
7. `DCL-LIFECYCLE-FIRST-SCORING-LAST` - lifecycle/actionability and authorization gates precede lane scoring, model selection, and queue ranking.
8. `ADR-PERSISTENCE-POSTURE-SERVICE-OWNED-SQLITE-FIRST` - service-owned SQLite initial posture with explicit PostgreSQL promotion triggers.
9. `DCL-CLI-SERVICE-CLIENT-DEFAULT` - `gt` routes to authority service by default when reachable; local fallback is explicit and auditable.
10. `GOV-MANAGEMENT-PLANE-SECURITY` - tablet/worker authentication, credential storage, role-scoped operations, token rotation, and audit requirements.
11. `DCL-TABLET-DISPATCH-INJECTION-SCOPE` - tablet can observe and inject pre-created dispatches, not bypass proposal or authorization gates.
12. `DCL-OPS-LIFECYCLE-DISPATCHER-MODEL` - formalizes the July 2 OPS lifecycle consolidation concepts that are still non-authoritative today.

## Open Questions For Owner Grilling

These should be resolved, deferred with rationale, or converted into separate work items under `WI-4910`:

1. Which machine should host the first authority service: Windows workstation, Mac workstation, Ollama Mac, or a dedicated small host?
2. Should the first API runtime be Python/FastAPI, a narrower stdlib/local HTTP service, or another owner-preferred service runtime?
3. What credential model should protect tablet and worker clients: bearer tokens, mTLS, OS-local trust, or a staged model?
4. Where should worker and tablet credentials live on Windows and Mac, and what is the recovery plan for credential loss?
5. Should MemBase become service-owned before dispatch migration, or should the first service only project MemBase while dispatcher writes remain current?
6. Should bridge/TAFE files remain primary evidence permanently, or should a future event log become authoritative with files as export evidence?
7. What tablet actions are allowed in the first release: observe only, inject pre-created dispatches, cancel/quiesce, or schedule recurring work?
8. What are the minimum rollback requirements before moving leases or dispatch injection behind the service?
9. What specific metrics trigger PostgreSQL promotion?
10. Which current dispatcher responsibilities should be migrated first: status projection, worker registry, lease ownership, dispatch scheduling, or dispatch injection?

## Architecture Alignment Ledger

- OPS consolidation: This packet keeps OPS artifact-centric. Service lifecycle events and packet records supplement governed bridge artifacts; they do not replace proposals, GO/NO-GO/VERIFIED, implementation reports, or LO verification.
- Dispatcher daemon architecture: The dispatcher daemon remains the live production mechanism during discovery. The service migration path begins with read-only projection and moves responsibilities only through verified slices.
- Lifecycle-first/scoring-last precedence: The packet explicitly keeps bridge actionability, work-intent claims, target-path authorization, and lifecycle state ahead of scoring, ranking, lane selection, or model routing.
- Portfolio reconciliation: The packet is scoped to `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY` and its active P1 discovery work items. It does not reopen terminal Wave 1 dispatcher modernization items or create duplicate dispatcher project-family authority.
- Mutation guard alignment: Service-mediated dispatch must preserve the controlled-artifact and protected-mutation guard posture verified under recent dispatcher/harness recovery work.
- Circuit-breaker alignment: NO-ACTION, suppression, quarantine, and circuit-breaker semantics remain lifecycle records to be formalized before runtime automation expands.
- Harness benchmarking alignment: Harness/model benchmark findings can inform lane capacity and readiness, but they are not authority for dispatching protected implementation work without bridge GO and work-intent evidence.

## Loyal Opposition Review Target

`WI-4909` should review this packet for:

- source-of-truth boundary defects
- dispatch safety gaps
- service ownership ambiguity
- security model insufficiency
- tablet launch overreach
- SQLite/PostgreSQL posture risk
- implementation-slice ordering risk
- contradictions with current dispatcher and bridge governance

## Recommended Next Actions

1. Route this packet for Loyal Opposition/adversarial review under `WI-4909`.
2. Use the review output to tighten the owner grilling list for `WI-4910`.
3. Capture owner decisions one at a time as deliberations.
4. Convert the reviewed packet into the ordered formal artifact proposal under `WI-4911`.
5. File a governance-only bridge proposal for formalization before any source/config/test implementation proposal.

## Decision Needed From Owner

No immediate implementation approval is requested by this packet. The first blocking owner decision for `WI-4910` is host placement for the initial authority service; it should be asked after Loyal Opposition review confirms the packet's open-question list is complete enough to grill from.

