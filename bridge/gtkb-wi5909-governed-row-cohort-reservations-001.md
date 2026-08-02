NEW
::init gtkb pb
::open build

# WI-5909 — Replace path-wide `groundtruth.db` exclusions with governed row-cohort reservations

bridge_kind: prime_proposal
Document: gtkb-wi5909-governed-row-cohort-reservations
Version: 001
Date: 2026-08-01 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ordinary per-WI PB authority only; former CF-10 all-program serialization authority rescinded; dispatcher and TAFE deliberately disabled
author_metadata_source: task-local interactive transcript, parent Prime Builder delegation, and current session envelope

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5909
Related Work Items: WI-4378, WI-4471, WI-5297, WI-5510, WI-5521, WI-5546, WI-5617, WI-5675, WI-5715, WI-5761, WI-5784, WI-5806, WI-5823, WI-5825, WI-5841, WI-5877, WI-5881, WI-5899, WI-5908

target_paths: ["scripts/work_intent_resource_cohorts.py", "scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_work_intent_resource_cohorts.py", "groundtruth.db"]

implementation_scope: source_test_and_lazy_membase_schema
proposal_authorization_state: review_only_go_ineligible_pending_governance_holds
bootstrap_claim_mode: legacy_path_wide_single_claim_and_start
logical_resource_claim_activation_in_scope: false
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_source_in_scope: true
dispatcher_configuration_in_scope: false
dispatcher_runtime_activation_in_scope: false
current_pauth_dispatcher_operation_hold: true
tafe_mutation_in_scope: false
external_system_mutation_in_scope: false
git_push_or_history_rewrite_in_scope: false

---

## Summary

**Version 001 is review-only and governance-held.** The custom metadata above
is descriptive, not a mechanical start control: current applicability still
reports `implementation_packet_create` and `implementation_start` allowed for
the target classes, while a direct operation-time request for
`dispatcher_mutation` is denied. Loyal Opposition must therefore issue
`NO-GO` or an equivalent non-implementation hold on these bytes. It must not
issue implementation-authorizing `GO` until one comprehensive replacement
PAUTH covers the bounded dispatcher-source operation and WI-5761's governed
lifecycle correction is complete. Prime Builder must then file a later
exact-byte `REVISED` proposal for fresh independent implementation-authorizing
review.

Replace the current path-only cross-claim collision rule for `groundtruth.db`
with one canonical, bounded logical-resource reservation contract. A reviewed
proposal may declare exact MemBase row or domain cohorts in addition to its
physical `target_paths`. The normalized declaration is bound into the
implementation-authorization packet, atomically installed with the work-intent
claim, copied into the schema-v3 implementation-start evidence, rechecked at
every protected mutation, and evaluated by the dispatcher through the same
shadow-only evaluator.

Two workers with current authority for disjoint row cohorts may therefore
proceed concurrently even though both correctly declare `groundtruth.db` as a
physical target. Same-row, ancestor, wildcard, whole-file, malformed, unknown,
legacy, stale, or authority-drifted cohorts remain mutually exclusive and fail
closed. All non-`groundtruth.db` path collisions retain their current semantics.
This WI's own implementation, including additive schema creation, remains under
one legacy path-wide claim and one unchanged schema-v3 start packet from first
source mutation through report. Resource-bound claims begin only in separately
governed canaries after this implementation is independently verified.

This is not a global-lock optimization and does not make SQLite multi-writer.
SQLite continues to serialize only its short atomic write transaction. The
change removes a much broader application-level exclusion that currently holds
an unrelated work item merely because both use the same durable store. It adds
no global leader, repository lock, fixed timer, retry schedule, throttle,
capacity default, dispatcher configuration, daemon activation, TAFE mutation,
raw worker SQL route, deployment, or release action.

## Standing Backlog Bulk-Operation Disposition

This exact implementation is not a bulk backlog or project mutation. WI-5909
and linked Test `TEST-11827` already exist as the durable work and acceptance
carriers. The implementation adds one bounded service, integrates three
existing callers, adds one focused integration suite, and performs one lazy,
additive work-intent schema migration through the work-intent registry service.
It does not bulk-update work items, projects, tests, authorizations, bridge
threads, or historical records.

## Current Baseline And Scope Identity

Repository HEAD at candidate preparation is
`75decbfa704fe50288aecbc5669def329a0825df`.

| Path | Current state and SHA-256 | Intended WI-5909 ownership |
| --- | --- | --- |
| `scripts/work_intent_resource_cohorts.py` | absent | new closed schema, canonicalizer, digest, overlap evaluator, and typed result model |
| `scripts/bridge_work_intent_registry.py` | foreign-modified; current worktree SHA-256 `633E22ACFF0E6E5B9964827CCAC40A3299D7FD513918F24C90469AC9A338F1E3` | additive lazy schema, atomic resource-CAS acquisition/renewal/takeover/release, readback, and events; never adopt the foreign selector hunk |
| `scripts/implementation_authorization.py` | clean; SHA-256 `BB9F5C731D8920793D17305CD5D78F8B8F038CED8189C0D1E4ED9E953BBD3891` | proposal extraction, packet/start binding, and compatibility wrapper for protected-mutation evaluation |
| `scripts/dispatcher_runtime.py` | clean; SHA-256 `02A54EA1E819157C6C41C2232E7244D73AAFEFF3D1BA47FD3F53A89DE9FE4189` | add shadow-only comparison and bounded diagnostics; legacy selected/inflight and same-role-project suppression remain authoritative and launch eligibility is unchanged |
| `platform_tests/scripts/test_work_intent_resource_cohorts.py` | absent | hermetic schema, packet, multi-process, dispatcher, migration, compatibility, and non-impairment evidence |
| `groundtruth.db` | ignored live SoT; 861,818,880 bytes at the `2026-08-01T21:01:10.1165982Z` observation; its whole-file digest is deliberately not a row-cohort preimage because unrelated governed rows continue to change | only the additive normalized current-reservation, retained lineage, and per-claim-epoch event schema created by the governed work-intent service under the unchanged legacy envelope, with exact pre/post schema/resource readback; never a Git target |

The only current worktree delta among the five code/test paths is the one-line
foreign edit in `scripts/bridge_work_intent_registry.py` that removes
`CODEX_HOME` as a live Codex-session signal. That hunk belongs to the active
`gtkb-wi584x-codex-home-harness-selector-false-positive` / WI-5877 / WI-5841
identity line and is not WI-5909 work. It must remain
byte-identical unless its own governed chain terminalizes it before WI-5909
starts. A fresh exact-hunk ledger and independent acceptance are required if
both lines remain active.

At candidate preparation:

- WI-5909 v1 is P0, open/backlogged, and an active member of
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` under subproject
  `publication-linearizability`.
- The controlling project row is currently lifecycle-incoherent: canonical
  project readback returns version 3, `status:"active"`, and retained
  `completed_at:"2026-06-21T09:48:38Z"`. WI-5761 remains open/backlogged;
  its original thread is terminal WITHDRAWN v007 and explicitly requires a
  governed successor plus a fresh scarred-project census. The current row must
  not be treated as implementation eligibility merely because status says
  active.
- `TEST-11827` v1 is an integration Test linked to
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  v2 is active, unexpired, list-free, and allows source, test, metadata,
  governance-evidence, and bridge classes while forbidding dispatcher mutation,
  push, history rewrite, deployment, release, external mutation, credentials,
  and destructive cleanup. Its current mechanical proposal preflight allows
  the six target classes for `implementation_packet_create` and
  `implementation_start`, but a direct current operation-time evaluation of
  `dispatcher_mutation` against `scripts/dispatcher_runtime.py` denies with
  `forbidden_operation: Operation 'dispatcher_mutation' is forbidden.` Because
  WI-5909 deliberately changes dispatcher source to add shadow comparison and
  diagnostics, that is
  a real implementation-authorization hold, not a wording escape. The current
  packet format extracts only one Project Authorization ID for the complete
  target cohort, so a supplemental second envelope cannot lawfully be combined.
  Before GO can authorize implementation, the owner must approve one fresh
  comprehensive WI-5909 PAUTH covering all six targets and the bounded
  dispatcher-source operation while continuing to forbid configuration/runtime
  activation, TAFE, external systems, push, history rewrite, deployment,
  release, credentials, and destructive cleanup; a later proposal revision
  must bind that exact PAUTH.
- No numbered bridge file exists for this slug, the WI-5909 claim is null, and
  the exact six-target cross-claim check returns no current collision. The
  initially absent foreign `.git/index.lock` reappeared during final read-only
  preflight as a zero-byte lock with UTC mtime
  `2026-08-01T20:21:56.6433002Z`; it was not touched. These are observations,
  not continuing authority.
- WI-4378 is resolved with independent VERIFIED v006 and its dispatcher
  suppression reason `same_role_project_claim_active` is live. It remains the
  authoritative same-role/same-project stand-down during this slice's shadow;
  WI-5909 v001 does not narrow or bypass it.

The final read-only inventory covered 2,456 physical thread chains. That count
is observational only; this proposal does not freeze an unreproducible total of
"nonterminal" overlaps because different lifecycle consumers classify older
`NO-GO` chains differently. One exact current shared-source blocker is
`gtkb-wi5546-read-only-git-probes-clean-slice` v002 `GO`, SHA-256
`CF56737657325B53197249858640838F0DE8B8223A848E35C724A7A5021BAE21`,
which declares `scripts/implementation_authorization.py`. Other directly
related declarations include WI-5784, WI-5841, WI-5877, and WI-5881 on the
work-intent registry; WI-5521 and WI-5823 on implementation authorization; and
WI-5510 and WI-5297 on dispatcher runtime. These are declarations, not current
claims. Exact latest status, hash, target ownership, and claim/packet state for
every shared path are rescanned by the canonical operation-time evaluator;
each owner must be terminal or covered by an independently accepted exact
non-overlapping hunk ledger before WI-5909 starts.

Any code/test target hash, worktree hunk, relevant schema/resource observation,
project, PAUTH, Test, claim, bridge, dependency, or lock-state change invalidates
this baseline and requires fresh canonical readback before filing or
implementation. Unrelated governed `groundtruth.db` row changes do not invalidate
the proposal by changing a whole-file digest; the exact logical cohort and its
registered precondition are the intended future comparison boundary.

## Requirement Sufficiency

**Existing requirements are sufficient.** The owner made highly parallel,
SoT-coordinated operation a hard platform and Dispatcher Next acceptance
criterion in `DELIB-202667517` and
`DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT`.
WI-5909 and TEST-11827 narrow that requirement to the observed path-only
collision defect. Existing project-authorization, claim-document, freshness,
deterministic-service, dispatcher, non-impairment, bridge, and spec-derived
verification requirements fully constrain the change. No new formal
requirement, global serialization exception, runtime activation decision, or
timer value is needed. WI-4378's independently VERIFIED same-role project
guard and WI-5761's still-open project-lifecycle invariant are binding adjacent
requirements, not optional implementation details.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 — resource reservations are an additive implementation-authorization boundary and never grant implementation by themselves.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` v1 — active PAUTH does not replace independent GO, exact work-intent ownership, or a fresh schema-v3 start packet.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` v1 — ordinary implementation claims remain document-authoritative and Prime-eligible; resource declarations cannot manufacture claim eligibility.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` v1 — PAUTH, target, operation, resource, expected-state, and session authority are re-evaluated at packet creation, claim acquisition, start, protected mutation, and dispatcher eligibility.
- `GOV-SOT-SINGLETON-001` v1 — one canonical parser/evaluator and one transactionally coherent claim-plus-normalized-current-reservation state own live logical authority; retained per-thread/per-claim-epoch chains are audit evidence, and packets/dispatcher projections are bound consumers rather than competing authorities.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — proposal bytes, claim rows, expected observations, PAUTH, packet, start evidence, and competing reservations are read freshly at action time.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` v2 — normalization, digesting, overlap, diagnostics, and migration are one reusable deterministic service rather than caller-specific heuristics.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` v1 — malformed, unknown, stale, over-bound, or partially evaluated resource declarations fail closed with typed evidence.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` v1 — dispatcher reporting exposes the shared reservation decision in shadow while legacy selection and WI-4378 remain authoritative; this slice does not mutate dispatcher configuration, alter launch eligibility, or activate a runtime.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` v1 — no dispatcher configuration file, daemon state, cap, route, model, or provider setting is changed outside the governed CLI.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` v1 — legacy and whole-file safety are preserved while the overly broad exclusion is narrowed only for fully governed disjoint cohorts.
- `GOV-STANDING-BACKLOG-001` v5 — WI-5909 and TEST-11827 are the durable carriers; WI-5675 remains the broader load/replace decision umbrella.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 — owner decisions, defect evidence, proposal, claim events, implementation report, verification, rollout, and supersession remain one durable artifact graph.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — every governing dimension is linked here and mapped to executable evidence below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v3 — only the append-only numbered chain controls proposal, independent verdict, implementation report, and terminal verification status.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 — implementation, temporary databases, evidence, and tests remain under `E:/GT-KB`; no harness-local scratchpad is authority.

## Prior Deliberations And Adjacent Work

- `DELIB-202667517` — multiple Prime Builders must operate concurrently; shared control planes may serialize only short atomic critical sections and must preserve unrelated accepted work.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — workers must coordinate through SoT CLI/skills plus bridge/dispatcher, CF-10 global leadership is incident-only, and MemBase must be enhanced or replaced if measured parallel load cannot be supported.
- `DELIB-202667748` — operational timers, retries, throttles, fan-out, and concurrency values belong in a typed centralized control surface and must be tuned from evidence. WI-5909 adds none; it preserves current retry timing under its existing owners and aligns later tunable controls with WI-5806.
- WI-4471 introduced the current cross-claim path check. Its same-path safety invariant is retained; only the false equivalence between a database pathname and every logical row inside it is corrected.
- WI-4378 independently VERIFIED the dispatcher reason
  `same_role_project_claim_active`. It remains authoritative during WI-5909
  implementation and shadow. Any later narrowing is a separate activation
  change and must accept only fully valid disjoint cohorts while proving both
  same-project coexistence and same/ancestor/wildcard negative canaries.
- WI-5761 remains open/backlogged after its original proposal thread closed
  WITHDRAWN v007. Its successor must govern the active-plus-completed project
  invariant and produce coherent project lifecycle readback before WI-5909 can
  implement; the current operation-time evaluator's status-only acceptance is
  the defect, not evidence that the hold is satisfied.
- WI-5675 is the broad MemBase concurrency, allocation, WAL, load, crash, and replace/no-replace umbrella. WI-5909 is a subordinate authorization/claim slice and may contribute evidence, but cannot claim closure of WI-5675.
- WI-5784 owns existing work-intent SQLite contention deadlines, retry/backoff behavior, typed exhaustion, and no-partial-claim tests. WI-5909 neither changes nor retunes those values.
- WI-5881 owns durable exact-byte bridge-recovery reservations and a reservation-specific claim fence. WI-5909 must reuse the independently VERIFIED generic fence/event primitives where applicable; it must not create a second recovery-reservation journal or absorb incident recovery behavior.
- WI-5806 owns the typed operational-control configuration foundation. WI-5909 introduces no operational value. Any later tunable reservation retry, wait, throttle, resource-count, or concurrency control must use that governed foundation after its consumer route is available.
- WI-5908 is the incident consumer whose audit exposed this generic path-wide bottleneck. It remains legacy/path-wide until WI-5909 is independently VERIFIED and explicitly adopted in a later governed version; WI-5909 does not silently widen WI-5908 authority.

## Owner Decisions / Input

No new owner decision is required to preserve or independently review this
technical design. The exact owner decisions above already require parallel SoT
coordination and reject a global writer as the steady state. However, the
current list-free project PAUTH expressly forbids `dispatcher_mutation`, and
WI-5909 changes dispatcher source to add shadow comparison/diagnostic logic.
Before an
implementation-authorizing GO, the owner must approve one comprehensive
WI-5909 PAUTH for the complete six-target cohort, and Prime Builder must file a
fresh revision bound to it. The current single-PAUTH packet evaluator cannot
combine a narrow dispatcher supplement with the existing envelope.

That revision must also follow governed WI-5761 successor/closure evidence and
fresh canonical readback proving the Bridge Protocol Reliability project has a
coherent active lifecycle state, including `completed_at` cleared or an
independently approved equivalent invariant. The current
`status:"active"`/non-null-`completed_at` row is a hard implementation hold.

Separate owner input is required later only if measured WI-5675 evidence shows
that the enhanced MemBase design cannot meet the accepted parallel PB plus LO
workload and a replacement durable store must be selected. This proposal does
not make or pre-empt that architectural decision.

## Proposed Logical Resource Contract

### 1. One closed declaration surface

A Prime proposal may carry one single-line JSON metadata field:

```text
logical_resource_cohorts: [{"authority":"groundtruth.db","domain":"work_items","key":["WI-5909"],"intent":"exclusive_write","expected":{"kind":"row_version","value":1}}]
```

The declaration is optional for compatibility, but omission never narrows
`groundtruth.db`: legacy packets remain path-wide. The field is parsed only by
`work_intent_resource_cohorts.py`. Callers do not parse, normalize, compare, or
hash it independently.

Schema v1 is closed:

- the root is a non-empty JSON array;
- each entry contains exactly `authority`, `domain`, `key`, `intent`, and
  `expected`;
- `authority` is initially only `groundtruth.db`;
- `domain` is either an exact registered lower-ASCII leaf-domain identifier or
  the reserved whole-authority sentinel `*`, never a caller-supplied SQL table,
  query, parent-domain expression, or prefix;
- `key` is a non-empty ordered tuple of bounded canonical segments; there is no
  keyless root in schema v1;
- a wildcard is the entire segment `*`, never embedded text, and is allowed
  only where that exact registered domain permits it; `key:["*"]` is the sole
  whole-domain representation, and `{domain:"*",key:["*"]}` is the sole
  whole-authority representation;
- `intent` is initially only `exclusive_write`;
- `expected` is a tagged closed union: `row_version` with a non-negative
  integer, `absent`, or a registered bounded `state_digest` value;
- unknown fields, duplicate normalized entries, duplicate or conflicting
  expected states, booleans masquerading as integers, Unicode/case aliases,
  empty values, traversal-like segments, NUL/control characters, and
  unsupported authorities/domains fail closed.

The normalized representation is stable compact JSON with sorted object keys,
preserved cohort/key order after deterministic sorting, UTF-8/LF encoding, a
schema version, exact proposal-relative path and content SHA-256, and a
`sha256:` reservation digest. The input is read once and no caller mapping is
retained by reference.

Schema safety maxima are protocol-shape bounds, not operational tuning knobs:
64 KiB encoded declaration bytes, 256 cohorts, 8 key segments per cohort, and
128 UTF-8 bytes per identifier/segment. Tests exercise exact boundaries and
one-over rejection. These deliberately generous, versioned maxima prevent
unbounded parser or quadratic comparison input; they are not timers,
throttles, worker caps, dispatch fan-out, or performance thresholds. Any
future operationally tuned limit is a WI-5806 consumer and cannot be added as a
new literal here.

### 2. Exact overlap algebra

Two cohorts overlap when their authorities and exact leaf domains match and
their non-empty key tuples have a compatible prefix: each common-position
segment is equal or one is the full-segment wildcard, and either tuple may be
an ancestor of the other. The reserved whole-authority sentinel overlaps every
domain under `groundtruth.db`; otherwise different domains are always disjoint
in schema v1. There is no cross-domain parent registry or implicit containment.
Consequently:

- `work_items/WI-5909` and `work_items/WI-5908` are disjoint;
- `work_items/*` overlaps both;
- a keyless `work_items` declaration is invalid rather than a root alias;
- exact same keys overlap even when expected versions differ; version drift is
  not a concurrency escape;
- different registered leaf domains are disjoint; only the exact reserved
  `{domain:"*",key:["*"]}` sentinel crosses domains;
- same session never bypasses overlap except byte-identical renewal of the
  same thread's same claim. Different threads in one session can launch child
  processes and therefore receive the same safety rule as different sessions.

Physical-path evaluation remains conjunctive with logical resources:

1. Any overlapping non-`groundtruth.db` target path denies exactly as today.
2. An actual database-file copy, replacement, restore, migration, vacuum-
   into, destructive schema rebuild, or other whole-file operation declares
   the whole-authority cohort and denies every peer.
3. If either side is legacy, lacks a declaration, has unreadable/malformed
   reservation evidence, uses an unknown schema/domain, or cannot prove the
   packet/claim binding, `groundtruth.db` remains path-wide and the pair denies.
4. Only two fully valid, current, disjoint logical declarations may narrow a
   shared `groundtruth.db` pathname.
5. A declaration never authorizes an undeclared physical path or an operation
   outside PAUTH. It can only make an already-authorized database path more
   precise for collision purposes.

### 3. Registered observations and expected-state binding

Registered domains expose fixed, parameterized read adapters through the
governed service; declaration text can never choose SQL. Each adapter returns a
bounded observation containing domain/key, present/absent state, current row
version or stable state digest, source view/service identity, observation time,
and database/schema fingerprint. Unsupported domains fail closed.

The proposal's expected state is validated before claim mutation. Claim-time
validation and claim insert occur in the same `BEGIN IMMEDIATE` transaction so
another writer cannot change the observed row between the precondition check
and reservation install. The actual governed mutation service must still apply
its own expected-version CAS; reservation is coordination, not a write bypass.

For operations whose canonical service owns a richer domain-specific CAS, the
service supplies and later verifies the same expected-state digest. A mismatch
between proposal, packet, claim, implementation-start evidence, fresh
observation, or mutation-service CAS is typed drift and produces no protected
mutation. No worker-facing raw SQLite query or direct table-name parameter is
introduced.

### 4. Atomic claim-time reservation CAS

`bridge_work_intent_registry.acquire()` derives the approved proposal's
normalized resource declaration for GO implementation claims before opening a
write transaction. Inside the existing short work-intent transaction it:

1. re-reads the exact thread claim and queries non-expired peer reservations
   through the normalized current-reservation indexes;
2. validates the expected observation through registered fixed adapters;
3. evaluates physical and logical overlap with the shared service;
4. CAS-checks the proposal path/hash, normalized digest, current holder,
   session, acting role, project, claim kind, expected version/state, and prior
   claim epoch;
5. inserts or updates the claim identity/liveness row and its normalized
   current-reservation rows with immutable reservation JSON/digest, proposal
   path/hash, expected-observation digest, and a monotonic per-thread epoch;
6. updates the retained per-thread lineage head and appends the corresponding
   acquired, renewed, replaced, released, or conflict-observed event in the
   exact `(thread_slug, claim_epoch)` lineage; and
7. commits once.

The transaction holds no Git, bridge-file, registry-file, dispatcher, or TAFE
lock. Proposal parsing and hashing occur before the transaction; the
transaction rechecks their exact bound digest, not the filesystem. Disjoint
claims still serialize for the few SQLite statements required by the durable
CAS, then run in parallel. No global worker leader or application-wide lease is
introduced.

Absent/expired/lapsed takeover re-evaluates every reservation and expected
observation in the same transaction. Same-thread renewal is idempotent only
when the reservation/proposal/expected-state binding is byte-identical;
otherwise it fails and requires an explicit release/reacquire after fresh
authority. Release appends a terminal event before deleting current reservation
rows and the current claim. The retained per-thread lineage row preserves the
maximum epoch and last terminal digest, so a reacquisition always receives a
higher epoch even after release. Event predecessor links never cross thread or
claim-epoch lineage and there is no database-global event head. Ambiguous
SQLite results require canonical readback of thread/session/epoch, normalized
current rows, lineage head, and event head; no blind retry is reported as
success.

The schema migration is lazy and local to an explicit work-intent resource
operation. It additively extends `work_intent_claims` with bounded reservation
and epoch fields and creates three service-owned structures:

- `work_intent_current_resource_reservations`, one normalized row per active
  claim cohort, bound by thread/session/claim epoch and indexed on
  `(authority, domain, key0)` plus `(thread_slug, claim_epoch)`;
- `work_intent_resource_reservation_lineages`, one retained row per thread with
  its monotonic maximum epoch and last terminal lineage digest; and
- append-only `work_intent_resource_reservation_events`, whose predecessor and
  head are scoped to one `(thread_slug, claim_epoch)` lineage.

Conflict lookup uses the `(authority, domain, key0)` index to prefilter exact
domain, the whole-authority domain `*`, exact first segment, and first-segment
wildcard candidates. If the incoming cohort itself uses either wildcard, the
predicate selects the corresponding indexed domain/key range. It then streams
candidate rows in deterministic thread/epoch/ordinal order and applies the
closed maximum-eight-segment prefix algebra in bounded memory; it never loads
all active claims or scans event history. Legacy/path-wide claim rows are
checked separately and always conflict. Tests must capture `EXPLAIN QUERY PLAN`
for exact, wildcard, and whole-authority lookups and prove indexed plans plus
deterministic decisions under a large temporary-store load; a full reservation
or event-table scan fails acceptance.

The migration is not added to a global MemBase initialization loop. Ordinary
read-only status calls do not create schema. Migration is idempotent, tested
against legacy and partially upgraded temporary stores, and records exact
before/after schema fingerprints. The entire WI-5909 implementation runs under
one pre-existing legacy path-wide GO/claim/schema-v3 start envelope: source
lands first, then that same governed work-intent service creates and reads back
the additive schema without claim release, reissue, upgrade, or authority-epoch
transition. A migration failure rolls back its transaction, fails the
implementation, and leaves the legacy path-wide claim controlling. Future
resource-bound claims are impossible until implementation report and
independent verification are terminal, so schema bootstrap has no circular
resource-start dependency.

### 5. Packet, start, and protected-mutation binding

`create_authorization_packet()` extracts the declaration from the exact
approved proposal, validates it, captures current observation evidence, and
adds a `logical_resource_reservation` object to the packet before computing
the existing packet hash. A malformed or unknown declaration is an
authorization error, not a path-wide silent downgrade. Complete absence is the
only compatibility case that becomes explicit legacy path-wide evidence.

This review-only v001 intentionally omits the top-level declaration. Its future
implementation revision must do the same for the bootstrap transaction, so its
single claim and single schema-v3 start packet carry explicit legacy path-wide
evidence for their entire lifetime. No code path may reinterpret, upgrade,
replace, release/reacquire, or reissue that envelope after the new parser or
schema exists. Declaration-bearing packets are exercised hermetically during
WI-5909 verification and become live only through later independently governed
canary proposals after WI-5909 is terminal VERIFIED.

`finalize_implementation_start_packet()` requires the current claim's
reservation JSON/digest, proposal hash, session, role, project, claim kind,
expected observation, and epoch to match the packet exactly. It re-observes
expected state and writes the complete binding into
`implementation_start.logical_resource_reservation` before computing the
schema-v3 packet hash.

The protected-mutation gate uses the packet and current claim rather than
reconstructing authority from prose. It rechecks PAUTH, target path, claim,
reservation digest/epoch, expected observation, and peer overlap on every
protected mutation. The existing `cross_claim_path_collision_reason()` name
may remain as a compatibility wrapper, but it delegates to the resource-aware
service and must fail closed on registry read errors. The current fail-soft
behavior in `scripts/implementation_authorization.py:3265-3266` is removed for
protected resource decisions: unreadable claim/reservation authority can no
longer convert uncertainty into permission.

### 6. Dispatcher shadow evaluation without eligibility change

`dispatcher_runtime._filter_prime_selected_by_target_paths()` keeps its legacy
path-only result authoritative for selection, suppression, and launch. WI-5909
adds a side-effect-free shadow call to the shared physical-plus-logical service
and records stable comparison fields:

- `reason_code` (`target_path_overlap_selected`,
  `target_resource_overlap_selected`,
  `target_resource_overlap_inflight`, or typed malformed/stale authority);
- both document names and reservation digests;
- only bounded normalized overlapping resource identifiers, never payload or
  arbitrary database values;
- current holder/session/claim epoch where applicable; and
- whether legacy/whole-file fallback caused the exclusion.

The shadow result cannot retain an item rejected by legacy path selection,
reject an item legacy selection retained, mint a packet/claim/start, change
ordering, or alter launch eligibility. The atomic claim-time CAS remains the
future resource authority; during this slice the legacy dispatcher decision is
the only operative decision. Any shadow mismatch is bounded evidence for a
later governed canary/activation WI, never permission.

WI-4378's independently VERIFIED project/role guard remains conjunctive and
authoritative. `same_role_project_claim_active` continues to suppress a second
same-role worker on the same project even when WI-5909 shadow says its row
cohorts are disjoint. A later activation proposal may narrow that guard only
when both claims have complete current resource bindings and fully valid,
disjoint cohorts. It must fail closed to the WI-4378 behavior for legacy,
missing, malformed, stale, same-row, ancestor, wildcard, whole-domain, or
whole-authority evidence, and must prove same-project disjoint positive canaries
plus same/ancestor/wildcard negative canaries before launch semantics change.

Existing capacity, provider, route/model, model, role, and harness gates remain
conjunctive. Missing or unknown capacity continues to fail closed, and cap 0
continues to disable. A disjoint resource result cannot override a capacity
denial, circuit state, PAUTH failure, document lease, role mismatch, missing
claim, or packet/start error. WI-5909 adds no capacity default and changes no
dispatch configuration or daemon state.

### 7. Durable readback and audit

`current_holder()`, claim status, packet listing, start evidence, and dispatcher
suppression output expose bounded additive reservation fields with stable
reason codes. The live claim identity/liveness row and its normalized
`work_intent_current_resource_reservations` rows are one transactionally
coherent current authority; the retained per-thread lineage row and append-only
per-claim-epoch event chain are audit/recovery evidence. Neither a packet cache
nor dispatcher JSON projection can override them.

Every event binds its previous event digest, event type, thread, session,
claim kind, role, project, claim epoch, proposal hash, reservation digest,
expected-observation digest, competing holder/digest for conflict events, and
event time. Its predecessor must belong to the same thread and claim epoch;
release retains the lineage epoch/head but removes current reservation rows.
No event has or updates a global predecessor/head. Raw row contents,
credentials, arbitrary environment values, or database pages are never
emitted. Event-chain corruption, missing predecessor, epoch regression, stale
normalized row, or claim/reservation/lineage disagreement is typed and fails
closed.

## Serialization, Dependencies, And Start Holds

This proposal is reviewable now but implementation is disabled until all of
the following are true at operation time:

1. The owner has approved one comprehensive WI-5909 PAUTH for the complete
   six-target cohort, including the bounded dispatcher-source operation but no
   configuration/runtime activation; Prime Builder has bound a fresh proposal
   revision to it; and an independent session has issued GO against those exact
   revised bytes. The current v2 whole-project PAUTH cannot authorize this
   implementation and cannot be combined with a supplemental envelope. The WI,
   TEST-11827, project membership, and replacement PAUTH remain current.
2. WI-5761 has a governed successor/closure that enforces the project
   reactivation invariant, and fresh canonical project/membership/PAUTH
   readback is coherent. In particular, a project accepted as active for
   operation-time authority has `completed_at` cleared, or an independently
   governed equivalent state is explicitly accepted. The current
   Bridge Protocol Reliability v3 row (`active` plus non-null
   `completed_at`) fails this hold.
3. WI-4378 VERIFIED behavior remains the authoritative dispatcher guard through
   implementation and shadow. The exact `same_role_project_claim_active`
   caller/tests are current, or an independent ledger accepts their successor;
   this slice makes no eligibility change. Later activation owns any narrowing
   and its same-project positive/negative canaries.
4. WI-5881 is receipt-complete and independently VERIFIED, or an independent
   review explicitly proves which reusable claim-fence/event primitives do not
   yet exist and accepts a non-duplicating WI-5909 implementation boundary.
   WI-5909 must not create a competing recovery-reservation journal.
5. WI-5784's ordinary acquire/release contention line is terminal, or an
   independent exact hunk ledger proves WI-5909 changes no timer, retry,
   deadline, error-code, rollback, or connection-close behavior owned there.
6. The foreign `CODEX_HOME` selector hunk and the
   `gtkb-wi584x-codex-home-harness-selector-false-positive` / WI-5877 / WI-5841
   identity chain are terminal and clean, or independently accepted exact
   line/semantic ledgers preserve their bytes and tests. WI-5909 never edits
   `_worker_harness_selector()`.
7. Every other current strict-GO or dirty shared-target overlap is terminal,
   clean, or covered by an independently accepted exact non-overlap ledger.
   Latest bridge state, worktree diffs, exact hashes, and claims are re-read;
   prose in this proposal is not future collision authority.
8. The current session acquires the exact live `go_implementation` claim for
   this slug while no legacy/path-wide `groundtruth.db` claimant is active.
   Because the old evaluator controls this bootstrap acquisition, WI-5909 does
   not claim row-level parallelism for any part of its own implementation.
9. One fresh schema-v3 implementation-start packet is finalized under the old
   path-wide gate before the first source mutation and remains the sole start
   authority through source changes, additive schema creation, tests, and
   implementation report. There is no mid-run recheck/reissue, resource
   upgrade, release/reacquire, second claim, or epoch transition. The governed
   service creates the schema under that unchanged envelope; failure rolls
   back and fails the implementation. Resource-bound claims activate only in
   later governed canaries after independent verification.
10. `.git/index.lock` is absent immediately before implementation and before
   finalization. A reappearing foreign lock is preserved and routed through its
   governed remediation rather than removed or adopted.
11. WI-5806 alignment is rechecked. WI-5909 may proceed independently only
   because it adds no timer, retry, throttle, threshold, fan-out, or concurrency
   value. If implementation discovers that a new operational value is needed,
   stop, file/deduplicate a correction WI, and sequence through the typed
   operational-control consumer route.

There is no global worker quiescence, CF-10 leader, daemon drain, dispatcher or
TAFE activation, foreign claim takeover, fixed wait, or raw database edit.
Long-running checks receive generous outer tool budgets and repeated canonical
state observation rather than being classified as failures merely because an
arbitrary short timer elapsed.

## Migration And Rollout

1. **Legacy authoritative:** before WI-5909, all `groundtruth.db` claim
   collisions and WI-4378 same-role-project suppressions remain authoritative.
   The new metadata has no live effect.
2. **Single-envelope implementation:** a later independently approved WI-5909
   revision acquires one legacy path-wide claim and one schema-v3 start packet.
   It lands source, creates the additive normalized schema through the governed
   service, performs canonical readback, runs hermetic tests, and files its
   implementation report without releasing, upgrading, or reissuing authority.
   Ordinary reads never migrate. Migration failure rolls back and fails the
   implementation.
3. **Implementation shadow:** hermetic packet/claim fixtures and dispatcher
   shadow diagnostics compute logical decisions alongside legacy path and
   project-role decisions. Legacy selection and
   `same_role_project_claim_active` remain authoritative; no real
   resource-bound claim or extra worker launch occurs.
4. **Independent verification:** an unrelated LO verifies source, schema,
   indexed lookup/load evidence, migration rollback, compatibility, shadow
   non-interference, and the complete negative matrix. Until that terminal
   verdict, all live proposals remain legacy/path-wide.
5. **Later governed claim canaries:** only after WI-5909 is independently
   VERIFIED may separate approved canary WIs declare live cohorts. At least two
   PB canaries with distinct rows and same project/role must coexist at the
   claim layer, while same-row, ancestor, wildcard, whole-domain,
   whole-authority, malformed, stale, and legacy controls deny. During these
   canaries the dispatcher still honors WI-4378 and therefore need not launch
   both workers automatically; controlled headless/CLI claim evidence is
   sufficient. A reliable independent LO remains available.
6. **Later governed dispatcher activation:** a distinct activation WI may make
   resource-aware selection `next_authoritative` only after accepted claim
   canaries and exact same-project positive/negative dispatcher canaries. It
   owns any narrowing of WI-4378, automatic launch eligibility, operational
   controls, shadow comparison closure, rollback proof, and migration-state
   transition. WI-5909 changes none of those semantics.
7. **Adoption and rollback:** later proposals opt in only with reviewed exact
   cohorts; there is no inference from SQL, prose, work-item ID, or CLI command.
   The activation WI must prove rollback to legacy path-wide plus
   same-role-project suppression. Additive normalized rows, retained lineage
   epochs, and audit events remain inert history and are not dropped or purged.

The rollout does not declare Dispatcher Next active. It supplies one required
parallel-control primitive and evidence to WI-5675 and the Dispatcher Next
program. Replacement activation still requires the complete shadow, chaos,
canary, rollback, lifecycle, and terminal-governance program.

## Cross-Harness Disposition

Claude, Codex, Cursor, Goose, Antigravity, Ollama, OpenRouter, and future
registered harnesses consume identical proposal bytes, normalized reservation
JSON, claim rows, packet/start evidence, and overlap results. Harness identity
and role are bound inputs but never change resource semantics. A harness-local
cache, scratchpad, memory file, transcript excerpt, or dispatcher projection is
not reservation authority. Multi-process tests use ordinary OS processes and
the canonical service rather than vendor-specific mocks.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202667517; DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT; DELIB-202667748; WI-5909; TEST-11827",
  "primary_route": "review-only design -> one legacy path-wide implementation claim/start -> governed additive schema -> independent verification -> later governed resource-bound claim canaries; dispatcher remains shadow-only in WI-5909",
  "baseline": "cross_claim_path_collision_reason treats groundtruth.db as one path and currently fails soft on claim-registry read errors; claim acquisition occurs before resource-aware collision evaluation",
  "expected_result": "unrelated governed row cohorts share the MemBase store concurrently while same-row, ancestor, wildcard, whole-file, legacy, malformed, stale, and unreadable authority fail closed",
  "canonical_authority": "the current work_intent_claims identity/liveness row plus indexed normalized current-reservation rows in one transaction; retained per-thread lineage and per-claim-epoch events are audit evidence; proposal, packet, start, and dispatcher records are bound consumers",
  "hard_invariants": [
    "logical precision can only narrow groundtruth.db and can never authorize an undeclared path or operation",
    "claim-time resource conflict evaluation and reservation install are one short atomic transaction",
    "WI-5909 implementation uses one unchanged legacy path-wide claim/start; resource-bound claims begin only after independent verification",
    "legacy dispatcher selection and same_role_project_claim_active remain authoritative throughout WI-5909 shadow",
    "non-groundtruth paths and whole-file database operations remain path-wide exclusive",
    "legacy or uncertain reservation evidence fails closed",
    "same-session different-thread overlap is not exempt",
    "missing or unknown capacity fails closed and cap zero disables",
    "no global leader, repository lock, timer, throttle, raw worker SQL, dispatcher activation, or TAFE mutation"
  ],
  "fail_closed_conditions": [
    "unknown or malformed declaration/schema/domain/key/intent/expected state",
    "resource limit exceeded or normalization alias/duplicate",
    "proposal, packet, claim, start, PAUTH, session, role, epoch, or observation drift",
    "claim/event chain unreadable or inconsistent",
    "same-row, ancestor, wildcard, whole-domain, or whole-authority overlap; schema v1 has no keyless root or cross-domain parent containment",
    "either peer is legacy/path-wide or lacks complete binding evidence",
    "foreign hunk, claim, target, schema, or index-lock state changes without accepted disposition"
  ],
  "before_behavior": "two unrelated governed MemBase changes block each other solely because both proposals list groundtruth.db",
  "after_behavior": "after WI-5909 verification and later governed canary activation, both retain the truthful physical target while reviewed row/domain tuples provide a second conjunctive precision boundary; WI-5909 itself remains legacy-authoritative/shadow-only",
  "self_descriptive_naming": "logical_resource_cohorts, authority, domain, key, key0, intent, expected, normalized_cohort_digest, resource_reservation_epoch, lineage_id, and lineage_event_head expose the governed resource boundary and its binding state without relying on hidden inference",
  "essential_context_preservation": "existing PAUTH, GO, claim, start, path, capacity, role, dispatcher, Git, and whole-file safeguards remain mandatory",
  "history_preservation": "legacy claims remain path-wide; normalized current rows are removed only with claim release; per-thread monotonic epochs and per-claim-epoch events remain durable without a global event head; foreign source hunks and every numbered bridge version keep their original owner",
  "obsolete_guidance_disposition": "path-only groundtruth.db exclusion remains compatibility fallback but is superseded as the preferred route for newly reviewed governed row mutations after VERIFIED adoption",
  "rollback": "separately govern a code-only return to path-wide evaluation; retain additive schema/audit history inertly and prove the legacy denial matrix"
}
```

## Spec-Derived Verification Plan

Linked Test of record: `TEST-11827`, **Logical row-cohort claims permit
disjoint MemBase work and deny overlapping resources**.

| Assertion | Governing requirements | Required executable evidence |
| --- | --- | --- |
| `WI5909-A1` closed schema and canonical digest | deterministic service, freshness, evaluability | Table-driven exact-boundary tests for every valid/invalid field, authority/domain/key/expected form, Unicode/case alias, duplicate, wildcard, control/traversal token, byte/count/segment bound, input immutability, stable compact JSON, proposal path/hash, and digest. Keyless roots and cross-domain parent expressions deny; `key:["*"]` is the exact whole-domain form and `{domain:"*",key:["*"]}` the exact whole-authority form. Unknown or malformed input produces typed fail-closed output and zero DB mutation. |
| `WI5909-A2` overlap algebra and legacy safety | singleton, modernization non-impairment | Exhaustive pair matrix for exact, disjoint, same-domain ancestor/descendant, wildcard, whole domain, reserved whole authority, differing expected versions, different leaf domains, same-session different-thread, non-DB path overlap, DB plus other path, legacy-left/right/both, malformed/unreadable peer, and whole-file operations. No v1 cross-domain parent containment exists. Only two fully valid disjoint DB cohorts may later narrow the path. |
| `WI5909-A3` atomic claim/install/takeover/release | project authorization, claim document authority, owner parallelism | Barrier-synchronized multi-process tests against isolated databases: at least 16 disjoint row claims all succeed and coexist; for 16 same/ancestor/wildcard contenders exactly one succeeds; expired/lapsed takeover rechecks resources; same-thread identical renewal is idempotent; changed digest/expected state denies. Claim plus normalized current rows are coherent; release removes current rows but retains a strictly monotonic per-thread epoch and terminal lineage digest; every event predecessor stays within one thread/claim epoch; no global event head exists. No test uses arbitrary short sleeps as correctness evidence. |
| `WI5909-A4` expected-state and authority drift | operation-time enforcement, freshness | Registered fixed adapters validate present/version, absent, and state-digest preconditions in the same claim transaction. Proposal/packet/claim/start/session/role/project/PAUTH/epoch/observation mismatches deny with zero protected mutation. Actual mutation-service expected-version CAS remains mandatory. |
| `WI5909-A5` packet/start/protected-mutation integration | no bridge bypass, file bridge authority | The WI-5909 implementation proposal intentionally omits resource metadata and uses one legacy path-wide claim/start packet unchanged through schema creation and report; no mid-run reissue, upgrade, release, reacquire, or epoch transition is possible. Declaration-bearing hermetic fixtures bind exact packet/claim/start evidence for later canaries. Malformed declarations never silently downgrade. Existing GO/claim/start negative tests remain green. |
| `WI5909-A6` dispatcher shadow and capacity conjunction | dispatcher control surface, WI-4378, CLI-only config | For every selected batch, old path-only and `same_role_project_claim_active` results remain launch-authoritative while resource decisions are bounded shadow evidence only. Tests prove the shadow cannot add/drop/reorder/launch work; same-project disjoint, same-row, ancestor, wildcard, legacy, and stale fixtures preserve WI-4378 suppression. Missing/unknown capacity and cap 0 still deny; no config/runtime/TAFE state changes. Later activation owns positive/negative launch canaries. |
| `WI5909-A7` lazy schema, indexed lookup, and audit integrity | singleton, artifact lifecycle | Legacy, empty, partially upgraded, repeated-upgrade, crash-before-commit, crash-after-commit-readback, release, and takeover fixtures prove additive idempotent schema, normalized-current/claim coherence, retained monotonic per-thread lineage epochs, per-claim-epoch event chains, no global event head, no ordinary read-triggered migration, and rollback on migration failure under the unchanged legacy envelope. `EXPLAIN QUERY PLAN` and large-store tests prove `(authority,domain,key0)` indexed exact/wildcard/whole-authority prefilter, deterministic streaming bounded postfilter, and no reservation/event full scan. Live pre/post fingerprints and row counts are recorded without exposing data values. |
| `WI5909-A8` compatibility and cross-harness parity | modernization, isolation | Existing claims/packets without fields remain path-wide and readable; current non-DB collisions remain unchanged; every registered harness receives byte-identical decisions for identical inputs; no scratch or vendor signal influences results; full focused legacy suites pass. |
| `WI5909-A9` exact scope, lifecycle, and non-impairment | standing backlog, bridge/spec-derived verification | Exact source/test/DB schema attribution, current foreign selector hunk preserved, WI-5761 successor/closure plus coherent active project lifecycle readback, WI-4378 behavior preserved, no unrelated worktree/DB row/Git/index/dispatcher configuration/runtime/TAFE changes, Ruff/format/compile/diff checks pass, and a separate session reviews implementation plus executed evidence before terminal disposition. |

Required focused commands use generous outer execution budgets and trust actual
collection rather than estimates:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_work_intent_resource_cohorts.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/work_intent_resource_cohorts.py scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py scripts/dispatcher_runtime.py platform_tests/scripts/test_work_intent_resource_cohorts.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/work_intent_resource_cohorts.py scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py scripts/dispatcher_runtime.py platform_tests/scripts/test_work_intent_resource_cohorts.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/work_intent_resource_cohorts.py scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py scripts/dispatcher_runtime.py platform_tests/scripts/test_work_intent_resource_cohorts.py
git --no-optional-locks diff --check -- scripts/work_intent_resource_cohorts.py scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py scripts/dispatcher_runtime.py platform_tests/scripts/test_work_intent_resource_cohorts.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5909-governed-row-cohort-reservations
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5909-governed-row-cohort-reservations
```

The implementation report must also include:

- exact old/new code hashes and an independently reviewable hunk ledger;
- exact `groundtruth.db` pre/post work-intent schema fingerprints, migration
  event ID/digest, and proof that unrelated tables/rows are unchanged;
- exact `EXPLAIN QUERY PLAN` evidence for indexed exact/wildcard/whole-authority
  prefilter plus deterministic large-store load measurements and proof that no
  current-reservation or event-history full scan is accepted;
- process count, claim outcomes, resource digests, normalized-current/claim
  coherence, retained per-thread epochs, per-claim-epoch event-head coherence,
  and database integrity for every concurrency/crash node;
- one-envelope bootstrap evidence proving claim/start identity and epoch are
  unchanged from first source mutation through schema creation and report, plus
  canonical WI-5761 successor/closure and coherent project lifecycle readback;
- the actual full focused collection count and pass/fail output;
- an explicit unchanged-state inventory for dispatcher configuration/runtime,
  TAFE, Git/index, foreign selector bytes, and unrelated worktree paths; and
- separate independent LO adversarial disposition covering claim-time TOCTOU,
  proposal/packet substitution, same-session child concurrency, wildcard and
  ancestor ambiguity, keyless-root rejection, cross-domain isolation, legacy
  downgrade, malformed per-lineage event chains, SQLite
  contention/ambiguous commit, crash/takeover/release races, resource bounds,
  indexed prefilter/postfilter bounds, path canonicalization, expected-version
  drift, WI-4378 same-project guard preservation, dispatcher shadow
  non-interference, capacity fail-closed behavior, and CLI compatibility.

## Risks And Rollback

The principal safety risk is treating a resource declaration as positive
authorization instead of a precision constraint. The conjunctive design,
legacy fail-closed fallback, exact packet/claim/start binding, fixed registered
adapters, and same-transaction CAS prevent that inversion.

The principal concurrency risk is a TOCTOU gap between dispatcher selection,
claim acquisition, and row mutation. Dispatcher output is deliberately
shadow-only here; legacy path and WI-4378 project-role decisions remain
authoritative. In later claim canaries, claim-time CAS is authoritative and the
mutation service retains its own expected-version CAS. A race therefore yields
a visible loser, not two owners.

The principal migration risk is changing the live work-intent schema while
unrelated workers are active. The first migration remains path-wide under the
old evaluator, uses one short transaction, requires zero active competing
database claim, and performs canonical readback under the same unchanged claim
and start packet. It neither releases nor upgrades authority; ordinary reads
never migrate; failure rolls back and stops the implementation. No broad
MemBase migration, vacuum, rewrite, or table copy is allowed.

Rollback is fail-safe and forward-only for durable evidence: a separately
governed source revert makes every database collision path-wide again. The
additive claim columns and event rows remain inert audit history and are not
dropped. Any destructive schema cleanup requires its own WI, GO, exact claim,
start packet, backup/restore proof, and independent verification. The same
legacy-denial, focused regression, and unrelated-state checks must pass after
rollback.

## Bridge Filing

This is a non-live candidate for the first status-bearing file under
`gtkb-wi5909-governed-row-cohort-reservations`. Version 001 is review-only and
governance-held, not mechanically disarmed by its custom metadata. Current
target-class applicability allows ordinary packet/start operations even though
a direct `dispatcher_mutation` request is forbidden, so the independent review
must issue `NO-GO` or an equivalent non-implementation hold rather than `GO`.
After a comprehensive replacement PAUTH, governed WI-5761 successor/closure,
coherent lifecycle readback, and all other holds, Prime Builder must publish a
later exact-byte `REVISED` proposal for fresh independent
implementation-authorizing review. Filing v001 must use the governed,
credential-scanned no-index writer after fresh candidate applicability, clause,
collision, duplicate-thread, pattern, compliance, project/PAUTH, claim, target,
and role checks. Filing creates reviewable bridge state only. It does not
acquire a claim, create a schema-v3 packet, migrate the database, edit source,
activate dispatcher/TAFE, stage, commit, push, deploy, or release.

## Recommended Commit Type

`fix` — replaces an overbroad claim-collision defect with a governed,
fail-closed logical reservation CAS while preserving legacy and whole-file
safety.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
