REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; current lawful session envelope; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current_interactive_session_context

bridge_kind: prime_proposal
Document: gtkb-wi5881-durable-cross-process-bridge-recovery-reservations
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-004.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5881
Related Work Items: WI-5603, WI-5617, WI-5715, WI-5761, WI-5784, WI-5791, WI-5812, WI-5819, WI-5825, WI-5829, WI-5839, WI-5841, WI-5849, WI-5858, WI-5877, WI-5879

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No `groundtruth.db` implementation mutation. The future implementation changes
only the nine declared source/test files and uses isolated temporary stores in
tests. Governed bridge publication may create and consume typed capability and
revision bookkeeping in `groundtruth.db`; that protocol evidence is not an
implementation target.

# REVISED Implementation Proposal — Durable Exact-Byte Recovery Reservations With Deterministic Claim-Fence Exhaustion

## Revision Claim

Preserve v003's complete durable exact-byte reservation design and add the one
missing deterministic TEST-11809 node required by v004. The new node drives
the reservation-specific claim-fence CAS into the pre-SQLite, already-spent
monotonic-deadline branch without a competing writer and proves a typed
`contention_exhausted` result, `sqlite_errorcode=None`, no partial fence/event
mutation, rollback, connection closure, and no evidence move.

The flaky pre-existing acquire baseline is not broadened into WI-5881. Its
5-of-10 and 2-of-6 failure evidence is now preserved in canonical WI-5784 v11,
the existing acquire/release contention carrier. WI-5881 retains only its new
reservation claim-fence integration node and must sequence against WI-5784 or
use an independently accepted exact hunk ledger.

This proposal preserves all nine v003 targets, exact normalized candidate-byte
persistence, immutable original-author provenance, separately validated
recovery invoker/claim/role/start/epoch, append-only events, the explicit total
phase/lock order, WI-5825 receipt coordination, foreign-byte boundaries, and
the no-implementation DISARM. It does not change ordinary
`author_session == claim_session`, introduce a global leader, add a timer
or configuration literal in production, or authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5881, TEST-11809, v002/v004, the
current role-authority specifications, active list-free project PAUTH, WI-5879
incident evidence, WI-5825 receipt recovery, and WI-5784 contention ownership
fully specify this correction. No new role, timer value, dispatcher contract,
global serialization policy, or owner decision is needed before independent
review.

## Findings Addressed

### F7 — deterministic coverage for the real pre-SQLite exhaustion branch

**Accepted and corrected.** Add this exact TEST-11809 node:

`platform_tests/scripts/test_bridge_work_intent_registry.py::test_recovery_claim_fence_cas_pre_sqlite_deadline_exhaustion_is_typed_and_leaves_no_partial_fence`

The fixture prepares an isolated exact reservation payload, supplies an
already-exhausted injected monotonic deadline before the claim-fence CAS opens
or begins a SQLite write, and uses no competing writer or timing race. It calls
the new reservation claim-fence install primitive—not ordinary `acquire()`—and
asserts all of the following:

1. the typed result/exception has `contention_exhausted is True`,
   `reason=contention_exhausted`,
   `operation=recovery_claim_fence_install`, `phase=begin_immediate`,
   `attempts=1`, `sqlite_errorcode is None`,
   `sqlite_errorname is None`, and detail
   `monotonic write deadline exhausted`;
2. zero partial reservation claim-fence row exists: the exact victim
   claim/fence row is absent, no fence epoch advanced, and no `claim_fenced`
   or `armed` event was appended;
3. any already-persisted immutable `prepared` payload/event remains unchanged,
   so the failure neither loses nor duplicates recovery evidence;
4. rollback is attempted where a transaction exists, the connection is closed
   on every exit, and an independently reopenable read sees no partial fence;
5. source/archive/target bytes and capability/receipt state are unchanged and
   the consumer cannot move evidence from a merely `prepared` state; and
6. rerunning with the same exhausted deadline remains deterministic and
   idempotent rather than depending on real contention; no retry or sleep is
   observed, and every opened connection is closed.

This node is distinct from the existing BUSY/LOCKED-oriented baseline. It
proves v003 phase 3's new claim-fence CAS failure contract and does not claim to
repair ordinary acquire/release behavior.

### WI-5784 baseline-test ownership and WI-5881 boundary

The pre-existing flaky baseline node is not a new WI-5881 defect carrier.
Canonical ownership remains WI-5784 v11, whose exact source/test cohort is
`scripts/bridge_work_intent_registry.py` and
`platform_tests/scripts/test_bridge_work_intent_registry.py`. Its governed
scope already owns bounded write deadlines, phase/attempt/elapsed/error-code
diagnostics, deterministic deadline exhaustion, no-partial-claim proof,
rollback, and connection closure. Its target-bearing implementation thread
`gtkb-wi5784-work-intent-claim-lock-retry` is current strict `NO-GO` v006,
SHA-256
`E981D831CD1803A8135911E47556BFF17A3379793AC3F11BCC904AC6660B3372`,
open and nonterminal. Its retained draft claim row is expired, not an active
lease.

Exact evidence is now append-only in WI-5784 v11: PB repetition produced five
passes/five failures, and independent v004 review produced four passes/two
failures for
`test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim`.
Failures stop at line 970 because `_deadline_exhausted_error` intentionally
has no SQLite error code before SQLite provides BUSY/LOCKED metadata. WI-5784
owns correction and deterministic baseline coverage; no duplicate WI exists.

WI-5881 implementation must wait for WI-5784 correction/terminalization or an
independently accepted exact non-overlapping hunk ledger. It may not rewrite,
absorb, or claim completion of WI-5784's baseline repair.

### F8 — current WI-5603 citation and explicit dropped-overlap disposition

**Accepted and corrected.** WI-5603 current head is targetless v006 `NO-GO`,
SHA-256 `2D188BC3BC9F0244715C7970B4566C43DA820584051BD0AFB3AEF773D1DD8D79`.
It supersedes targetless v005 and has no source/test overlap with WI-5881.

The three citations dropped between v001 and v003 are explicitly dispositioned:

- `gtkb-authority-foundations-project-authorization` v015, SHA-256
  `1047F39753698FEA8558A0409597C06030AF4B069A5BB88804C33DCFF2892F9F`;
- `gtkb-wi5237-wi5229-pauth-configuration-coverage` v010, SHA-256
  `6B22288E7E4D737F323CE02CE1DB317880D62412A67DC5A89AA6F8CC063BE036`;
  and
- `gtkb-wi5240-wi5236-pauth-registered-vocabulary` v008, SHA-256
  `1A14BB8FBA697171A9FFF6B904E77CD9227AA64538BE3705A642157265289234`.

Each current head targets only `groundtruth.db`. None overlaps this proposal's
nine source/test targets. Their removal from the live overlap set is correct;
their immutable bridge history remains preserved and grants no WI-5881 scope.

### F9 — prevent reservation schema initialization from creating a hidden DB target

**Route A selected.** Reservation tables and events use reservation-specific
lazy schema initialization invoked only by an explicit future reservation
operation. They are not added to or called by ordinary
`ensure_control_plane_schema()` paths used during proposal, report, verdict,
capability, or receipt publication. WI-5881 tests use isolated temporary
databases. Its implementation report must record before/after canonical
`groundtruth.db` schema/table fingerprints and prove them identical.

The first live reservation is a later, independently governed consumer action;
WI-5879 owns its incident-specific use. If implementation cannot preserve this
boundary, work stops and returns to proposal revision: Route B would have to add
`groundtruth.db`, set `kb_mutation_in_scope: true`, obtain exact formal database
authority, and sequence the three strict database-only GOs above. The current
nine-target proposal does not authorize Route B.

## Preserved Durable Reservation Contract

### Immutable exact-byte payload before move

Before any source/archive move, the writer normalizes and audits the candidate
once. The control plane persists and canonically rereads an immutable payload
containing:

- exact normalized UTF-8 candidate bytes as a BLOB, byte size, and content
  digest;
- document/version/target/status/transition, predecessor path/digest, and
  source/archive paths/digests;
- the complete immutable original author envelope and digest;
- compliance-audit and provider-guard result bytes/digests plus tool/schema
  identities;
- resource-binding evidence for generation, size, content, predecessor,
  project, PAUTH, WI, reviewed proposal, GO, schema-v3 start, and binding
  digest; and
- initiating invoker/session/claim, fence epoch, event-head preimage, and
  creation time as separate audit fields.

Only canonical `armed` readback permits the move. Resume consumes stored bytes
and evidence only; it never regenerates, renormalizes, or rewrites the original
author. Payload, size, digest, evidence, predecessor, path, or transition drift
fails closed without claim, event, capability, file, or receipt mutation.

### Ordinary path unchanged; narrow reserved recovery path

Ordinary mint/consume retains `author_session == claim_session` and its
existing negative tests. The reservation-only entry point preserves the stored
original author/session and candidate bytes while separately validating and
recording the current recovery invoker/session, Prime role from the exact
worker-session document, exact recovery claim/fence epoch, active project
membership/PAUTH, fresh schema-v3 start, unchanged binding/event head/physical
state, and aggregate publication preimage.

Reserved capability and receipt records carry original author, recovery
invoker, exact claim, and epoch as distinct fields. Altered author, bytes,
invoker authority, role evidence, claim, epoch, or aggregate preimage produces
zero mutation.

### Append-only state and exact physical states

The immutable payload is followed only by append-only `prepared`,
`claim_fenced`, `armed`, `moved`, `publication_minted`, `file_created`,
`receipt_consumed`, `consumed`, or governed `aborted` events. Every event binds
its prior head, payload digest, epoch, actor/invoker, and canonical state
evidence. No payload or event row is updated or deleted.

Accepted physical states are source-present/archive-absent before move,
source-absent/exact-archive-present after move, exact stored candidate bytes at
the target, and exact consumed receipt/capability after publication. Both
source/archive present or absent, symlink/reparse ambiguity, digest drift,
changed predecessor/status/role/evidence, foreign capability, or stale epoch
fails closed.

### Total phase and lock order

1. Normalize bytes and run compliance/provider guards without a work-intent or
   control-plane lock.
2. Acquire `_RegistryFileLock`, then control-plane SQLite; append immutable
   `prepared`, commit, release.
3. Acquire only work-intent SQLite; CAS-install the exact reservation claim
   fence, commit, release. The new deterministic F7 node covers failure here.
4. Reacquire `_RegistryFileLock`, then control-plane SQLite; prove fence and
   payload readback, append `armed`, commit, release.
5. Perform the exact source-to-archive move with no database/file lock held.
6. Acquire `_RegistryFileLock`, then control-plane SQLite for reserved mint and
   aggregate revision/one-capability CAS; commit, release.
7. Create target exclusively and reread exact bytes with no database/file lock
   held.
8. Reacquire `_RegistryFileLock`, then control-plane SQLite for receipt,
   aggregate revision, and `consumed`; commit, release.

Work-intent SQLite is never held while acquiring either control-plane lock.
The only nested order is file lock before control-plane SQLite. Ambiguous write
results require canonical readback of the expected event head/epoch; no blind
append, reversed order, duplicate mint, or global leader is allowed.

Preparation, claims on unrelated documents, normalization, audits, and object
construction remain parallel. Existing aggregate mint/consume serialization
is explicit and short; this proposal does not promise simultaneous aggregate
publication.

### Crash and release-pending behavior

Crashes after `prepared`, fence, `armed`, move, mint, file creation, or receipt
consumption resume forward from exact canonical readback. `prepared` alone
cannot move evidence. A fence blocks ordinary takeover. Move-before-mint
recovery uses stored original-author bytes. Post-file capability recovery is
coordinated with WI-5825 and cannot mint a second receipt.

Physical/capability completion plus a same-transaction claim still briefly
visible is `publication_completed_claim_release_pending`, not failure. It
forbids remint and takeover until bounded canonical readback resolves release
or returns a typed ambiguity. WI-5829 retains ordinary report-claim ownership.

## Currentness, Collision, And Sequencing

- WI-5825 v006 `GO`, SHA-256
  `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`,
  is the sole strict-GO overlap on the control plane, writer, and their tests.
  It owns capability-row/receipt recovery and must land first. Current audit
  confirms WI-5812 v013 and WI-5715 v004 still block WI-5825 implementation.
- WI-5715 v004 `NO-GO` owns the foreign control-plane source/test bytes; they
  must be finalized/clean or exactly separated.
- WI-5877's carrier v005 remains `REVISED`, SHA-256
  `123C872537F1F22DA8E69746FCC35BB2A7A005CA01CE80AC1411CD2830336258`,
  and overlaps both the work-intent registry and
  `test_work_intent_role_eligibility.py`; both paths must become independently
  VERIFIED/clean or carry an accepted ledger.
- WI-5784 v11 owns the pre-existing deadline baseline and overlaps the
  work-intent source/test. It must land or be exactly hunk-separated.
- WI-5841 v005 remains `REVISED`, SHA-256
  `1F2EA995554F909C470B604B088AFCFD7E2F4F05B8D79ADE00CEDABA87163836`,
  and overlaps the work-intent registry plus its test.
- WI-5839 v005 remains `REVISED`, SHA-256
  `EB787061A06B65D464BB8DE6846E60CADF50D0936B71F6A0657B834A02824EC2`,
  and overlaps `registry_control_plane.py`.
- WI-5812 v013 `REVISED`, SHA-256
  `0ECC074257FBCD3EF7C2E48B6AF0886B18D721E128C20963939873E9D0BE79F3`,
  is the forward Goose filing contract and has no exact nine-target overlap.
- WI-5879 v005 `REVISED`, SHA-256
  `E91CB0A7467C068AD81C0D2D95A2E5D92DA43439379D5DBB377B22A7AC752EE4`,
  remains incident-only and must not reimplement the service.
- WI-5617 physical v013 `VERIFIED` remains strict-invalid history, never
  current authority. WI-5603 v006 and the three groundtruth.db-only chains are
  non-overlaps only under the selected lazy-schema Route A above.

Null/expired claims do not clear GO authority, foreign-byte ownership, or sequencing.
Fresh heads, hashes, claims, PAUTH, session documents, overlap ledgers, event
heads, and schema-v3 packets must be reread before any later start. The foreign
zero-byte `.git/index.lock` remains untouched; WI-5819/WI-5849 own remediation.

## Current Exact Target State

| Target | SHA-256 / state |
|---|---|
| `scripts/bridge_work_intent_registry.py` | `633E22ACFF0E6E5B9964827CCAC40A3299D7FD513918F24C90469AC9A338F1E3`; foreign/shared WI-5877/WI-5784/WI-5841 surface |
| `scripts/bridge_claim_cli.py` | `E6B0B5002FCB9F4D2FA5B1E20938C112F090EEA19BEE95AD97E8DB15AD0FC0A3`; clean |
| `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` | `A063E0CB057FACFC86D077360B02EB9805A1EB516C7CE16CCED0B472D06C3006`; foreign/shared WI-5715/WI-5839 |
| `scripts/gtkb_bridge_writer.py` | `9399A3878D99C0CB007C9A7E979F25C09B6EDFAC841CB75C6FB78D3C8472F2F4`; clean |
| `platform_tests/scripts/test_bridge_work_intent_registry.py` | `F886F15E229BA1BC56E7C2513F67772031459B14A5C49A7C8A258CA23158A5AB`; clean, shared WI-5784 target |
| `platform_tests/scripts/test_bridge_claim_cli.py` | `8708469B5EA002B0BA73BD690229BE5C9828B3E4293C696FA849EA110AC06387`; clean |
| `groundtruth-kb/tests/test_registry_control_plane.py` | `FDA19AED075D4D397BF7A97556CB4395D6EA97324012DA08A8E39BE327349073`; foreign WI-5715 |
| `platform_tests/scripts/test_gtkb_bridge_writer.py` | `38A4BDEFF74BB9AA3F841C35F103DE3393945C36CBCA42925314D9605DA6D871`; clean |
| `platform_tests/scripts/test_work_intent_role_eligibility.py` | `D45D755A1CBBBE65B122919B058F52FA2486EA379EDD1442334FFA4D1C88AC05`; clean, shared WI-5877 target |

No foreign byte is adopted or rebaselined. Drift before filing, review, GO, or
implementation returns the proposal to revision.

## Project And Operation-Time Authority

`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is physically current v3 `active`
and WI-5881 is an active direct member. Its retained
`completed_at=2026-06-21T09:48:38Z` conflicts with active state; WI-5761 owns
that reactivation-invariant defect. Current operation-time evaluation permits
proposal review, but implementation start is fail-closed until the project
lifecycle is owner-evidenced and reconciled. List-free
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
v2 is active, unexpired, has no WI exclusions, and covers the nine source/test
targets. Deprecated WI approval metadata is noncontrolling.

The PAUTH does not replace independent GO, exact claim, schema-v3 start, clean
target ordering, factual report, independent VERIFIED, or atomic finalization.
No new owner decision or WI-specific approval is required for review.

## Timer, Parallelism, And Cross-Harness Disposition

WI-5858 and Timer Governance own timeout/TTL/retry/throttle/concurrency values.
WI-5881 adds no production timer/config/fallback literal or configuration
target and preserves current production behavior until a governed typed
interface exists. Its deterministic test may inject an already-spent monotonic
deadline/test clock sentinel; that is test control, not a production timer.
The 5/10 and 2/6 recurrence is routed to WI-5784 as evidence, not used to invent
a local production bound.

All harnesses consume the same deterministic reservation/claim/writer
semantics. Cursor has no helper assumption. Original author provenance remains
immutable; the current recovery invoker is separate. Every acting-role decision
uses the exact worker-session document and rejects registry, dispatcher,
marker, ambient-environment, or fallback role authority.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only status authority and exact
  governed publication.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` v7 — recovery role comes only from the exact
  worker-session document and fails closed without fallback.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — payload, events, claim/fence, PAUTH,
  start, aggregate, capability, and receipt are current at each CAS.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — incident corrections remain
  nonterminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active direct
  list-free project authority controls later operations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH/project/WI,
  targets, related ownership, and requirements are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11809 maps to exact
  executable persistence, role, deadline, crash, race, and aggregate nodes.
- `GOV-ARTIFACT-APPROVAL-001`, `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`,
  `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`, and `SPEC-1830` — formal metadata,
  ordinary paths, and deterministic recovery remain intact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — history, payloads, events, reports,
  and verification remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5617, WI-5715, WI-5761, WI-5784, WI-5791,
  WI-5812, WI-5825, WI-5829, WI-5839, WI-5841, WI-5858, WI-5877, WI-5879,
  and WI-5881 remain distinct.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — all targets are in-root and native
  Windows self-enforces GO/claim/start boundaries.

## Prior Deliberations

- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — exact
  record/path CAS and useful parallel work without an all-program leader.
- `DELIB-202667517` — owner rejected persistent global serialization/read-only
  operation while preserving exact-WI governance.
- `DELIB-202667724` and `DELIB-202667732` — Bridge Protocol Reliability
  whole-project authority and v2 correction.
- `DELIB-202667722` — timer/concurrency values belong in a centralized,
  data-tuned SoT.
- `DELIB-20265660` and `DELIB-20263296` — finalization atomicity and claim-role
  guard history; neither substitutes for this implementation.
- v002 and v004 in this append-only chain — exact independent findings answered
  by v003 and this revision.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Independent GO after all overlap sequencing, fresh exact claim/schema-v3 start, nine-target implementation, factual report, and independent VERIFIED.",
  "before_behavior": "Exact bytes and author can survive origin loss under v003, but the new claim-fence CAS has no deterministic proof for pre-SQLite monotonic-deadline exhaustion.",
  "after_behavior": "The preserved exact-byte state machine adds deterministic typed pre-SQLite exhaustion coverage with no partial fence, closed connection, and no move; the ordinary flaky baseline stays with WI-5784.",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, document-role SPEC/DCL, current project PAUTH/start, work-intent registry, registry control plane, governed writer, TEST-11809, and WI-5784 ownership.",
  "essential_context_preservation": "Preserve candidate bytes/original author, recovery invoker/claim/role/epoch, audit/resource evidence, lock order, append-only events, exact physical states, capability/receipt, foreign owners, and incident/history separation.",
  "obsolete_guidance_disposition": "WI-5603 v005 citation is replaced by targetless v006; the three groundtruth.db-only heads remain non-overlaps only under selected lazy-schema Route A; no baseline-test ownership is duplicated.",
  "history_preservation": "All prior bridge versions, WI-5784 v11 evidence, reservation payloads/events, capabilities, receipts, and incident history remain append-only.",
  "baseline": {
    "bridge_head": "v004 NO-GO at C6023639F2A03580F9D57D3E430CCF97DB4AA421574DC2786DBFE47E5D4F69AB",
    "target_count": 9,
    "planned_test11809_nodes": 16,
    "ordinary_acquire_baseline_owner": "WI-5784 v11 and its target-bearing v006 NO-GO implementation thread",
    "canonical_database_schema": "Ordinary publication must not initialize reservation tables"
  },
  "expected_result": {
    "bridge_head": "v005 REVISED awaiting independent Loyal Opposition review",
    "target_count": 9,
    "planned_test11809_nodes": 17,
    "recovery_fence_exhaustion": "Deterministic pre-SQLite typed zero-new-mutation coverage with every connection closed",
    "canonical_database_schema": "Unchanged across WI-5881 implementation and report publication under lazy-schema Route A"
  },
  "provenance": "WI-5881 v001-v004; TEST-11809; WI-5784 v11 and bridge v006; WI-5879 incident evidence; WI-5825 receipt recovery; current exact overlap and target hashes.",
  "self_descriptive_naming": "Use prepared payload, claim fence CAS, armed, moved, publication minted, receipt consumed, release pending, original author, recovery invoker, and fence epoch.",
  "hard_invariants": [
    "No move before immutable payload and fence armed readback",
    "Pre-SQLite deadline exhaustion leaves no partial claim fence and closes the connection",
    "Ordinary author-session equals claim-session remains unchanged",
    "Recovery invoker never replaces original author or candidate bytes",
    "Work-intent SQLite is never nested with control-plane locks",
    "No production timer/config/fallback literal, global leader, raw SQLite bypass, dispatcher/TAFE mutation, or foreign lock handling",
    "Ordinary publication leaves the canonical groundtruth.db schema/table fingerprint unchanged",
    "Project active/completed_at state is reconciled under WI-5761 before implementation start"
  ],
  "fail_closed_conditions": [
    "Missing or mismatched worker-session role, PAUTH, GO, claim, start, payload, epoch, predecessor, physical state, aggregate preimage, capability, or receipt",
    "Any dirty owner is unresolved without an accepted hunk ledger",
    "Any exhausted-deadline path creates a row/event, moves evidence, leaks a connection, or depends on timing"
  ],
  "rollback": {
    "instructions": "Before a live reservation, revert only approved nine-target hunks after foreign attribution. After prepared, preserve payload/events and recover or govern abort forward; never delete evidence.",
    "verification": "Run all 17 TEST-11809 nodes, adjacent claim/role/control-plane/writer suites, exact readbacks, lint/format/compile/diff, and no-dispatcher/TAFE checks."
  }
}
```

## Specification-Derived Verification Plan

| Node | Specification-derived assertion | Executed |
|---|---|---|
| `test_recovery_reservation_persists_exact_normalized_bytes_evidence_and_size_before_move` | exact byte/evidence persistence | no — planned |
| `test_recovery_reservation_readback_must_match_before_move_is_allowed` | armed readback gate | no — planned |
| `test_recovery_fence_blocks_foreign_go_and_draft_takeover_after_predecessor_exposed` | ordinary takeover denial | no — planned |
| `test_recovery_claim_fence_cas_pre_sqlite_deadline_exhaustion_is_typed_and_leaves_no_partial_fence` | deterministic F7 typed exhaustion, zero partial fence/event, rollback/close, no move | no — planned |
| `test_recovery_resume_stale_epoch_race_has_one_winner_and_zero_loser_mutation` | epoch CAS | no — planned |
| `test_recovery_resume_after_move_before_mint_uses_exact_stored_tuple` | origin-loss recovery | no — planned |
| `test_recovery_claim_denies_lo_missing_malformed_closed_and_registry_fallback_roles` | fail-closed role authority | no — planned |
| `test_recovery_claim_role_is_exact_session_document_authoritative` | exact role document | no — planned |
| `test_recovery_claim_rejects_document_claim_role_mismatch_without_fallback` | role/claim match | no — planned |
| `test_ordinary_mint_rejects_original_author_different_claim_session` | ordinary equality unchanged | no — planned |
| `test_reserved_mint_preserves_original_author_and_records_current_invoker_claim_epoch` | reservation-only identity split | no — planned |
| `test_crash_after_reserve_readback_before_move_resumes_without_regeneration` | pre-move crash | no — planned |
| `test_crash_after_move_before_mint_recovers_original_author_bytes_once` | move-before-mint crash | no — planned |
| `test_reserved_mint_file_consume_boundaries_coordinate_with_wi5825_once` | WI-5825 receipt coordination | no — planned |
| `test_two_slug_publication_parallel_preparation_serialized_aggregate_commit_no_deadlock` | parallel preparation/serialized commit | no — planned |
| `test_recovery_drift_matrix_has_zero_claim_event_file_capability_or_receipt_mutation` | zero-mutation drift failures | no — planned |
| `test_reserved_publication_complete_live_claim_window_is_release_pending_not_duplicate` | transient release window | no — planned |

The nodes live in the same four v003 test surfaces. Multi-process fixtures
inject every prepared/fence/armed/move/mint/file/receipt boundary. Planned
nodes are absent pre-implementation evidence. The implementation report must
record exact collection/results, event/fence/capability/receipt identities,
process exits, and scoped diff attribution.

## Acceptance Criteria

1. Exact bytes, size, author, audit/guard/resource evidence, authority,
   predecessor, transition, paths, and digests persist and reread before move.
2. Only `armed` permits move; partial phases are safe and recoverable.
3. Ordinary mint/consume author/claim equality remains unchanged.
4. Reserved mint preserves original author/bytes and separately validates
   current invoker, claim, role document, PAUTH/start, and epoch.
5. Role-document absence/mismatch and all fallback evidence fail closed.
6. Ordinary claims cannot take the reserved generation; one fresh resume wins.
7. The new deterministic exhausted-deadline node passes without a competing
   writer and proves the recovery operation, one attempt, typed no-code
   diagnostics, no retry/sleep, no partial fence/event, rollback/close, and no
   move.
8. Move-before-mint resumes exact stored bytes without regeneration.
9. Phase/lock order is implemented with no cyclic nesting or filesystem work
   under locks.
10. Parallel preparation plus short aggregate serialization has no deadlock or
    duplicate receipt.
11. WI-5825 lands first; WI-5715/WI-5784/WI-5839/WI-5841/WI-5877 bytes are
    clean or carry accepted exact ledgers before implementation.
12. All 17 TEST-11809 nodes execute and pass; WI-5784 separately stabilizes its
    existing baseline and no completion is claimed here.
13. No production timer/config/fallback literal or externalization claim is
    added; deterministic injected test-time deadline control is permitted.
14. WI-5879 remains incident-only; WI-5617/WI-5791 history and WI-5812 scope
    remain separate.
15. Only the nine targets change; reservation schema initialization is explicit
    and lazy; canonical `groundtruth.db` schema/table fingerprints are unchanged;
    adjacent suites, Ruff, format, compile, and scoped diff checks pass.
16. No raw SQLite bypass, dispatcher/TAFE activation or mutation, lock action,
    credential operation, deployment, release, push, rewrite, or cleanup.
17. WI-5761 reconciles the project's active/non-null-`completed_at` state before
    implementation start.

## Risks And Rollback

- Exact-byte payload growth is necessary for authoritative takeover; measure
  exceptional reservation storage/read latency and route evidence to the
  existing SoT-latency advisory.
- Prepared/fence/armed journaling makes cross-store partial phases recoverable;
  failure before `armed` cannot move evidence.
- Ordinary author equality remains the anti-forgery boundary; the reserved
  route accepts only the immutable tuple and separate current authority.
- No work-intent/control-plane lock nesting prevents cycles; current aggregate
  contention remains explicit rather than hidden.
- Foreign owners land or are exactly separated; hashes are evidence, not a
  rebase.
- Before reservation creation, revert only approved target hunks. After
  `prepared`, preserve payload/events and recover or govern abort forward;
  never erase durable evidence.

## Candidate Pre-Filing Gates

Run exact physical currentness, v004 hash/status, project/WI/PAUTH, target
hash/ownership, project lifecycle/WI-5761, strict overlap, claim, applicability, clause,
collision/pattern, report-shape, and compliance checks. Live filing additionally
requires an exact draft claim, registry observation, governed writer append,
and canonical path/status/hash/claim-release readback.

## Owner Decisions / Input

No new owner decision is required for this proposal. Active list-free Bridge
Protocol Reliability PAUTH v2 and prior owner decisions authorize governed
review only. Implementation remains separately gated, including lifecycle
reconciliation through WI-5761.

## DISARM — Implementation Boundary

This revision performs no protected edit, database reservation/event, claim
takeover, evidence move, capability, receipt, Git/index/lock action, or
dispatcher/TAFE use. Implementation requires a future independent GO, all
overlap sequencing, WI-5761 lifecycle reconciliation, a fresh exact
`go_implementation` claim, a fresh schema-v3 start packet for exactly nine
targets, factual report, and independent atomic VERIFIED. The current foreign
`.git/index.lock` is preserved.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_claim_cli.py`
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
- `platform_tests/scripts/test_work_intent_role_eligibility.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
