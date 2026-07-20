# LAN Authority Service Decision Queue Addendum

Date: 2026-07-04 16:02 UTC

Status: candidate decision tree / non-authoritative discovery addendum

Project: `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY`

Work items: `WI-4910`, `WI-4911`

Depends on completed review: `WI-4909`

Project authorization: `PAUTH-PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-DELIBERATION-ADR-DRAFTING`

Authority boundary: This addendum is discovery evidence only. It is not a formal ADR, DCL, GOV, specification, implementation proposal, bridge `GO`, or source-change authority. It does not authorize protected source/config/test mutation, runtime service scaffolding, dispatcher migration, substrate migration, direct database mutation, or bypass of bridge/implementation-start/report/verification gates.

## Claim

`WI-4909` is terminal enough to unlock the next discovery steps: Loyal Opposition issued `GO` in `bridge/gtkb-wi4909-lan-authority-service-adversarial-review-002.md`, confirming that the LAN authority service Architecture Decision Packet is sufficient to proceed to owner grilling (`WI-4910`) and formal artifact candidate drafting (`WI-4911`).

The next least-regret sequence is:

1. Resolve the owner decision queue below, one decision at a time.
2. Capture each answer as a deliberation.
3. Promote only the resolved decisions into the final `WI-4911` formal artifact candidate set.
4. File a governance-only formalization bridge proposal before any implementation or protected-file mutation.

## Evidence

- `bridge/gtkb-wi4909-lan-authority-service-adversarial-review-002.md`: Loyal Opposition `GO` with seven findings and four additional owner-grilling questions.
- `WI-4909`: resolved in MemBase after the LO review; current terminal row cites `gtkb-wi4909-lan-authority-service-adversarial-review`.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-04-15-37-lan-authority-service-architecture-decision-packet.md`: base Architecture Decision Packet.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPS-LIFECYCLE-DISPATCHER-MODEL-CONSOLIDATION-2026-07-02.md`: non-authoritative OPS lifecycle/dispatcher consolidation context.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-FIRST-RELEASE`: owner selected discovery-first posture.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-LAN-AUTHORITY-SERVICE`: owner selected the central LAN authority service target.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-FIRST-DELIVERABLE-ARCHITECTURE-DECISION-PACKET`: owner selected this packet class as the first deliverable.
- `DELIB-20260629-GTKB-RUNTIME-ORCHESTRATION-ADP-INSIGHTS-DROPBOX-LOCATION`: owner selected `CODEX-INSIGHT-DROPBOX` for the non-authoritative packet.

## LO Findings Carried Forward

| ID | Severity | Finding | Decision impact |
|---|---|---|---|
| F1 | High | Dual-writer / split-brain risk in CLI local fallback | Decide whether local fallback is read-only or queue-and-sync. |
| F2 | High | Security model insufficiency around plaintext LAN API vulnerability | Decide first-release security floor before service writes or tablet injection. |
| F3 | High | Lack of rollback and state reconciliation plan | Decide rollback authority and require reconciliation protocol before write ownership. |
| F4 | Medium | Harness state axis alignment omission | Decide whether worker registry formalization includes `registration_state` and `dispatch_state`. |
| F5 | Medium | Ambiguity in pre-created dispatch validation | Decide where pre-created dispatch packets live and how validation proves bridge/work-intent authority. |
| F6 | Low | SQLite connection and concurrency serialization | Include WAL/single-writer serialization as a formal candidate unless owner rejects SQLite-first. |
| F7 | Low | Discovery PAUTH containment | Keep all implementation work outside the current governance-only PAUTH. |

## WI-4910 Decision Tree

Ask these one at a time. A later question should not be asked until the dependency column is resolved or explicitly deferred.

| Order | Decision | Recommended default | Dependencies | Persistence target |
|---|---|---|---|---|
| 1 | CLI fallback write policy when authority service is unreachable | Read-only fallback for all writes; no queue-and-sync in first release | none | Deliberation |
| 2 | First-release security floor | HTTPS/TLS plus secure invite-token pairing before tablet or worker write capability | none | Deliberation; likely `GOV-MANAGEMENT-PLANE-SECURITY` candidate |
| 3 | Initial authority service host | Windows workstation for first slice unless owner prefers Mac/Ollama host for operational reasons | decisions 1-2 preferred but not required | Deliberation |
| 4 | Initial API runtime | Python/FastAPI if service is networked; narrower stdlib/local HTTP only if owner wants minimal dependency surface | decision 2 | Deliberation |
| 5 | Worker/tablet credential storage and recovery | OS-native secure storage where available; explicit emergency revoke/re-pair procedure | decision 2 | Deliberation; security GOV candidate |
| 6 | Rollback state authority | Service database is source of truth for service-owned writes; rollback requires export/reconciliation before local fallback writes resume | decisions 1, 3 | Deliberation; rollback DCL candidate |
| 7 | Worker registry state axes | Include `registration_state`, `dispatch_state`, and health state as separate axes | none; informed by OPS consolidation | Deliberation; worker registry DCL candidate |
| 8 | Pre-created dispatch storage and validation | Store pre-created dispatch packets as governed artifacts or service event records with bridge latest-status and work-intent validation | decisions 1-2, 7 | Deliberation; dispatch packet GOV candidate |
| 9 | MemBase write boundary | First service projects MemBase; service-owned writes require a later formal slice | decisions 1, 6 | Deliberation; service boundary GOV candidate |
| 10 | Bridge/TAFE evidence boundary | Bridge files remain primary evidence; service event log is projection/lifecycle supplement until formal elevation | decisions 8-9 | Deliberation; bridge artifact DCL candidate |
| 11 | Tablet first-release action scope | Observe plus inject pre-created dispatches only; no arbitrary task creation in first release | decisions 2, 8, 10 | Deliberation; tablet scope DCL candidate |
| 12 | PostgreSQL promotion trigger | Promote only after measured SQLite/service constraints or multi-user/write-load requirements justify operational burden | decisions 6, 9 | Deliberation; persistence ADR candidate |
| 13 | First dispatcher responsibility to migrate | Read-only status projection first, then worker registry/leases, then dispatch injection, then write ownership | decisions 7-11 | Deliberation; migration DCL candidate |

## First Decision Candidate

The first `WI-4910` decision should be CLI fallback write policy, because it gates F1, rollback posture, MemBase write boundary, and service-client design.

Recommended question:

Should the LAN authority service design require local CLI fallback to be read-only for all coordination writes when the authority service is unreachable?

Recommended answers:

- Option A (Recommended): Read-only fallback only; writes fail closed until the authority service returns or an explicit recovery procedure runs.
- Option B: Queue-and-sync fallback; local writes queue while offline and later reconcile through explicit conflict-resolution rules.
- Option C: No local fallback; CLI requires service availability for all authority-scoped operations.

## WI-4911 Formal Artifact Candidate Set, Revised After LO Review

The base packet listed twelve candidates. LO findings suggest the following refined order:

1. `ADR-LAN-AUTHORITY-SERVICE-TARGET`: central LAN authority/control-plane service is the target topology.
2. `DCL-RUNTIME-ORCHESTRATION-DISCOVERY-FIRST`: implementation umbrellas wait for owner decisions, formalization, bridge review, and fresh implementation PAUTH.
3. `GOV-RUNTIME-AUTHORITY-SERVICE-BOUNDARY`: service may project and later mediate live state, but it cannot become a second backlog/spec/bridge authority without explicit formal elevation.
4. `DCL-CLI-SERVICE-CLIENT-FALLBACK`: CLI service-client behavior and local fallback write policy. This is blocked on WI-4910 decision 1.
5. `GOV-MANAGEMENT-PLANE-SECURITY`: HTTPS/TLS, secure client pairing, credential storage/recovery, role-scoped operations, and audit requirements. This is blocked on WI-4910 decisions 2 and 5.
6. `DCL-WORKER-REGISTRATION-STATE-AXES`: worker identity, registration state, dispatch state, health, capabilities, heartbeat, claim/release/expiry, and cancellation semantics. This is blocked on WI-4910 decision 7.
7. `GOV-DISPATCH-PACKET-LIFECYCLE`: required packet fields, TTL/freshness, bridge status, work-intent, authorization evidence, expected report/verdict, and terminal disposition. This is blocked on WI-4910 decision 8.
8. `DCL-BRIDGE-ARTIFACT-AND-SERVICE-EVENT-BOUNDARY`: bridge files remain governed evidence; service event records are projections or lifecycle supplements unless formally elevated. This is blocked on WI-4910 decision 10.
9. `ADR-PERSISTENCE-POSTURE-SERVICE-OWNED-SQLITE-FIRST`: service-owned SQLite initial posture, WAL/single-writer serialization, direct worker DB-write prohibition, and PostgreSQL triggers. This is blocked on WI-4910 decisions 6, 9, and 12.
10. `DCL-ROLLBACK-AND-STATE-RECONCILIATION`: rollback authority, export/reconciliation requirements, and no split-brain fallback writes. This is blocked on WI-4910 decision 6.
11. `DCL-TABLET-DISPATCH-INJECTION-SCOPE`: tablet can observe and inject pre-created dispatches only within validated authorization boundaries. This is blocked on WI-4910 decision 11.
12. `DCL-LIFECYCLE-FIRST-SCORING-LAST`: lifecycle/actionability and authorization gates precede lane scoring, model selection, and queue ranking.
13. `DCL-OPS-LIFECYCLE-DISPATCHER-MODEL`: formalizes the July 2 OPS lifecycle consolidation concepts that remain non-authoritative today.
14. `DCL-DISPATCHER-MIGRATION-SEQUENCE`: read-only projection first, then worker registry/leases, then dispatch injection, then coordination-write ownership. This is blocked on WI-4910 decision 13.

## Architecture Alignment Ledger

- OPS consolidation: The revised candidate set preserves artifact-centric OPS lifecycle records and keeps service events supplemental until formal elevation.
- Dispatcher daemon architecture: The migration sequence explicitly leaves the daemon as production authority until bounded, reviewed, verified slices move responsibility.
- Lifecycle-first/scoring-last: The candidate set keeps lifecycle actionability, bridge latest status, work-intent claims, and authorization evidence ahead of scoring/routing decisions.
- Portfolio reconciliation: This addendum stays inside `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY`, cites terminal WI-4909 evidence, and does not reopen terminal dispatcher modernization WIs or create duplicate project-family authority.
- Mutation guard alignment: Every implementation candidate remains outside the discovery PAUTH and requires a fresh bridge proposal, GO, work-intent claim, implementation-start packet, report, and LO verification.

## Current Terminality Assessment

- `WI-4909`: terminal/resolved. Evidence: `bridge/gtkb-wi4909-lan-authority-service-adversarial-review-002.md` and current MemBase resolved row.
- `WI-4910`: not terminal. Owner decisions remain unresolved.
- `WI-4911`: not terminal. Candidate list is materially advanced but cannot be complete until the owner decisions above are resolved, deferred, or converted into separate WIs.

## Recommended Next Actions

1. Ask the WI-4910 decisions one at a time, beginning with CLI fallback write policy.
2. Capture each answer into the Deliberation Archive.
3. Update the formal artifact candidate set after each answer.
4. Once all high-priority decisions are resolved/deferred/split, resolve `WI-4910`.
5. File a governance-only formalization bridge proposal for `WI-4911` after the candidate set is complete.

