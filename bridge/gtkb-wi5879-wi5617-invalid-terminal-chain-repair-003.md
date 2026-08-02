REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; parallel-audited WI-5879 revision; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5879-wi5617-invalid-terminal-chain-repair
Version: 003
Responds to: bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-002.md
Date: 2026-08-01 UTC
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5879
Related Work Items: WI-5617, WI-5825, WI-5858
target_paths: ["bridge/gtkb-dispatcher-next-foundation-spike-013.md", "bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

# Revised Defect-Fix Proposal - Durable exact-slot reservation for WI-5617 invalid-terminal repair

## Revision Claim

Version 002 correctly found that version 001's ordinary victim-thread draft claim
cannot protect the interval after invalid version 013 moves away and before its
role-correct replacement is receipt-consumed. This revision adds only the missing
durable exact-slot reservation primitive and its focused tests. The incident
transaction remains limited to the same three targets. The four added source/test
targets are the minimum surfaces required to create, enforce, resume, consume, and
test that reservation.

The reservation is durable and explicitly released by state transition; it does
not inherit the draft claim's TTL. It blocks only the exact victim document,
version, and replacement path. Preparation, validation, hashing, evidence-copy
planning, and unrelated publication remain parallel. The existing registry
transaction lock protects only each short reservation/event/CAS operation. No
global worker leader, repository-wide lease, raw SQLite edit, dispatcher/TAFE
operation, or new hard-coded timeout is introduced.

## Exact response to version 002

### P0 - post-move recovery was protected only by an expiring draft lease

**Accepted.** Before any evidence move, the control plane will persist an
immutable reservation binding:

- victim document `gtkb-dispatcher-next-foundation-spike` and version `13`;
- invalid source path and SHA-256
  `ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D`;
- archive path
  `bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified`;
- intended replacement path `bridge/gtkb-dispatcher-next-foundation-spike-013.md`;
- exact predecessor path and SHA-256
  `bridge/gtkb-dispatcher-next-foundation-spike-012.md` /
  `70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12`;
- required replacement status `NO-ACTION`, authorizing WI-5879 bridge/PAUTH
  evidence, initiating session, and reservation state.

The ordinary mint path must deny any publication to the reserved replacement
slot unless it is supplied the matching reservation and validates every binding.
A later Prime Builder session may resume after the original draft claim expires,
but only with a fresh WI-5879 GO-implementation claim and schema-v3 start packet,
an exact victim claim, the same archive/predecessor hashes, and the same intended
replacement transition. A fresh worker cannot publish an unrelated version 013
or reclassify the reservation.

### TEST-11807 executable and recordable route

TEST-11807 maps to these exact executable nodes:

1. `groundtruth-kb/tests/test_registry_control_plane.py::test_bridge_repair_reservation_binds_exact_slot_and_blocks_ordinary_mint`
2. `groundtruth-kb/tests/test_registry_control_plane.py::test_bridge_repair_reservation_survives_owner_claim_expiry_and_resumes_exactly`
3. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_invalid_terminal_move_crash_resumes_single_replacement`
4. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_invalid_terminal_move_rejects_archive_predecessor_and_replacement_drift`

The implementation report must record the exact pytest command, observed result,
reservation/event IDs, invalid/archive/replacement/predecessor hashes, replacement
publication capability/receipt ID, strict resolver output, and WI-5617 open
readback. Those fields form the TEST-11807 result evidence; no synthetic pass or
unbound narrative result is permitted.

## Why WI-5825 is a prerequisite, not the missing reservation carrier

The current physical WI-5825 head is v006 `GO`, SHA-256
`FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`.
Its approved v001 design supplies three useful prerequisites:

- Change B back-fills a **consumed receipt for an existing file**, binding its
  target/content digest, author, invoker, and authorization evidence.
- Change C recovers pending publication from the **durable capability row after
  that row already exists**.
- Change A2 exact-byte republishes a compensated publication only when supplied
  bytes match that row's original content digest.

None reserves a now-missing replacement slot, records the permanent cleanup
archive path, or prevents the ordinary mint path from accepting different bytes
after an expiring work-intent claim is lost. The WI-5879 replacement is
intentionally role-correct content and therefore cannot equal the quarantined
PB-authored `VERIFIED` digest. This revision does not silently widen WI-5825.

WI-5879 source/test implementation must begin only after WI-5825 is implemented,
reported, independently VERIFIED, and its shared targets are clean. WI-5825 owns
publication receipt back-fill, compensated/recovery-required clearing, exact-byte
republish, and durable capability-row fallback. WI-5879 then layers the exact-slot
reservation on those landed APIs. WI-5825's own WI-5812 sequencing condition
remains its responsibility; WI-5879 neither duplicates nor bypasses it.

The four shared paths are:

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `scripts/gtkb_bridge_writer.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

The fifth WI-5825 target,
`platform_tests/scripts/test_check_protected_commit_authorization.py`, is not
required by WI-5879 and is excluded.

WI-5858 remains the sole carrier for work-intent TTL divergence,
externalization, and tuning. WI-5879 introduces no timeout/TTL/retry literal and
does not claim that a longer claim lease fixes durable ownership.

## Current exact evidence and target identity

Fresh read-only evidence on 2026-08-01 UTC:

- strict resolution of `gtkb-dispatcher-next-foundation-spike` fails
  `WRONG_STATUS_AUTHOR_ROLE` at version 013;
- v011/v012/v013 hashes remain respectively
  `2A3AAE14FA671D7D3FBFF8E6F8F01EF017723F6457091B13563C30D93C84EEDD`,
  `70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12`, and
  `ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D`;
- the invalid v013 is present and untracked; the declared cleanup destination is
  absent;
- WI-5617 is open/backlogged with no completion evidence; TEST-11662 has no
  bound pass;
- WI-5879 and victim claims were null before this revision's draft claim;
- the current filing claim is row 36058, held by author session
  `019fb19b-7814-73c1-8707-204e432cbf00` from
  `2026-08-01T12:58:35Z` through `2026-08-01T13:08:35Z`;
- the only current valid schema-v3 implementation packet found by the bounded
  compact packet census is WI-5760, whose four targets are disjoint;
- the compact census evaluated 551 packets in 73.7 seconds; no unbounded scan
  was used;
- current shared-target baselines are
  `registry_control_plane.py` `A063E0CB...06C3006` (modified),
  `gtkb_bridge_writer.py` `9399A387...472F2F4` (clean),
  `test_registry_control_plane.py` `FDA19AED...349073` (modified), and
  `test_gtkb_bridge_writer.py` `38A4BDEF...6D871` (clean).

The two modified shared targets are foreign/in-flight state already disclosed by
WI-5825 v006. This proposal authorizes no harvesting. Exact hashes, ownership,
claims, diff attribution, and clean landing of WI-5825 must be re-read before
WI-5879 begins.

## Project and implementation authority

- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is direct and active (v3).
- WI-5879 has active direct membership
  `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-5879` v1.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  v2 is active, list-free, unexpired, and allows source, test, test addition,
  metadata, governance evidence, and bridge classes. Legacy
  `work_items.approval_state` is noncontrolling.
- The PAUTH still does not replace independent GO, exact claims, schema-v3
  implementation-start authority, exact target-path checks, implementation
  report, or independent VERIFIED finalization.

No owner decision is required. Version 002 expressly required a minimal
claim/writer/control-plane expansion if current mechanisms could not supply the
invariant, and the direct project's active list-free PAUTH covers the declared
classes. The revised proposal remains subject to a new independent GO.

## Requirement Sufficiency

Existing requirements sufficient. Version 002's required correction,
`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, WI-5879,
and TEST-11807 already require durable, exact, fail-closed recovery. This design
adds the minimal mechanism needed to satisfy those requirements; it does not
create a new role, status, global leader, timer policy, or dispatcher contract.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Independent GO, WI-5825 VERIFIED prerequisite, fresh exact claims and schema-v3 start packet, durable reservation, recoverable evidence move, reserved governed replacement publication, independent LO NO-GO, TEST-11807 execution, factual report, and independent verification.",
  "baseline": {
    "repair_thread": "WI-5879 v001 NEW followed by v002 NO-GO",
    "victim_chain": "gtkb-dispatcher-next-foundation-spike v013 is PB-authored VERIFIED and strict resolution fails WRONG_STATUS_AUTHOR_ROLE",
    "invalid_digest": "ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D",
    "predecessor_digest": "70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12",
    "recovery_prerequisite": "WI-5825 v006 GO; implementation and independent VERIFIED not yet complete",
    "timer_carrier": "WI-5858 owns work-intent TTL divergence, externalization, and tuning"
  },
  "before_behavior": "After invalid v013 moves, only an expiring ordinary draft claim protects the vacant replacement path. Claim expiry allows a different worker to mint a competing v013 before the original repair resumes.",
  "after_behavior": "An immutable exact-slot reservation is persisted before the move. Append-only events record move, replacement-capability mint, and receipt-bound consumption; ordinary mint is denied while the reservation is active, and a later authorized session can resume only the exact bound repair.",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, the strict numbered bridge chain, the registry control plane, active PAUTH v2, and TEST-11807.",
  "essential_context_preservation": "Preserve exact invalid, archive, replacement, and predecessor paths and hashes; WI-5617 open state; role-correct nonterminal semantics; author/invoker/authorization provenance; WI-5825 prerequisite ownership; WI-5858 timer ownership; and the no-dispatcher/TAFE boundary.",
  "obsolete_guidance_disposition": "Version 001's statement that the draft claim itself blocks the crash window is superseded. Historical v001 and v002 remain unchanged. No WI-5825 recovery API is misrepresented as already reserving a missing replacement slot.",
  "history_preservation": "Victim versions 001 through 012 remain byte-for-byte unchanged. Invalid v013 bytes move once to the declared cleanup-evidence path. Reservation events, capability receipts, replacement v013, LO v014, report, and verdict are append-only evidence.",
  "provenance": "WI-5879; TEST-11807; bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-001.md and -002.md; WI-5825 v001/v006; WI-5858; DELIB-202667724; DELIB-202667732; DELIB-202667722; DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT.",
  "self_descriptive_naming": "Use bridge-repair reservation, exact slot, victim target, archive path, predecessor digest, replacement capability, and reservation event names; do not reuse generic claim or leader terminology for durable ownership.",
  "expected_result": {
    "reservation": "one durable exact binding exists before the evidence move and reaches consumed only with the exact replacement receipt",
    "replacement": "v013 is a role-correct Prime NO-ACTION over exact v012 and receives one consumed publication receipt",
    "review": "a distinct Loyal Opposition session publishes v014 NO-GO",
    "work_item": "WI-5617 remains open/backlogged without fabricated TEST-11662 or requirements evidence",
    "nonimpairment": "no unrelated source, test, project, dispatcher/TAFE, foreign claim/packet, timer, or Git-lock mutation"
  },
  "hard_invariants": [
    "Reservation is committed and read back before invalid v013 moves",
    "Only one nonterminal reservation exists for the exact replacement path",
    "Ordinary mint cannot bypass an active exact-slot reservation",
    "Claim expiry does not release or alter reservation authority",
    "Resume validates the immutable binding plus fresh WI-5879 claims and schema-v3 start authority",
    "Reservation consumption requires the exact replacement publication capability to be consumed",
    "WI-5825 lands and is independently VERIFIED before shared-target implementation",
    "WI-5858 remains the sole timer/TTL carrier",
    "Victim versions 001 through 012 and all unrelated paths remain unchanged",
    "No dispatcher or TAFE activation or mutation"
  ],
  "fail_closed_conditions": [
    "Changed invalid or predecessor hash",
    "Archive path already exists or is not a regular in-root file",
    "Source and archive both exist, neither exists, or either is a symlink",
    "Missing or mismatched reservation ID, binding digest, claim, PAUTH, or schema-v3 packet",
    "Replacement status, version, target, predecessor, role, or transition mismatch",
    "Foreign active reservation, claim, or implementation-packet overlap",
    "WI-5825 not independently VERIFIED or shared targets not clean",
    "Ambiguous publication success, missing consumed receipt, or reservation event drift"
  ],
  "rollback": {
    "instructions": "Before incident execution, revert only the four WI-5879 source/test hunks after WI-5825 attribution is separated. After reservation creation, preserve its append-only event history and use a governed abort only with exact physical-state proof and no replacement capability. After replacement publication, correct forward through later numbered bridge versions; never restore the invalid VERIFIED bytes as authority.",
    "verification": "Rerun the four TEST-11807 pytest nodes, both mandatory bridge preflights, strict lifecycle resolution, exact hash/receipt/reservation readback, WI-5617 open-state readback, and target nonimpairment checks."
  }
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - role/status authority, exact numbered chain,
  governed publication, independent review, and fail-closed correction.
- `GOV-ARTIFACT-APPROVAL-001` - project authorization plus bridge/claim/start
  evidence gates source, tests, bridge, and service-owned metadata mutation.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - replacement v013 remains a Prime
  nonterminal correction carrier awaiting an independent LO response.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - reservation/currentness reads and writes
  use the canonical registry control plane, never raw SQLite.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - invalid bytes, reservation events,
  receipts, implementation report, and verification remain durable evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing
  links precede implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - TEST-11807 maps to exact
  executable nodes and terminal readback evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - direct project,
  work-item, and PAUTH metadata are explicit.
- `GOV-STANDING-BACKLOG-001` - WI-5879, WI-5825, and WI-5858 remain distinct
  MemBase work carriers; no duplicate backlog item is created.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the exact-slot addition must
  preserve all existing lawful publication, recovery, and parallel-worker paths.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` - crash recovery
  and exact-slot reservation are deterministic service behavior, not session
  lore.
- `GOV-10`, `GOV-12`, `SPEC-1662`, and `GOV-17` - production-interface tests,
  WI-linked verification, behavioral assertions, and automation-script review.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all seven targets are under
  `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - native Windows execution self-enforces
  the GO/claim/start boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - forward-only incident evidence and
  explicit lifecycle transitions are retained.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner-directed
  Dispatcher Next program and independent-review boundary.
- `DELIB-202667082` - preserved WI-5617 NO-GO history.
- `DELIB-202667724` and `DELIB-202667732` - whole-project Bridge Protocol
  Reliability grant and active v2 repair.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` - exact
  record/path CAS rather than a global worker leader.
- `DELIB-202667731` - Harness Test Corrections authorization governing WI-5825.
- `DELIB-202667722` - timer/concurrency settings must move to central
  configuration and must not be duplicated by incident repairs.
- `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-002.md` - independent
  P0 finding requiring a durable archive/replacement ownership binding and
  executable TEST-11807 route.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-001.md`
  and `-006.md` - approved prerequisite API scope and current sequencing gate.

## Owner Decisions / Input

- The active list-free PAUTH v2 is controlled by `DELIB-202667732`.
- The owner directed autonomous Dispatcher Next construction, correction of
  governance blockers, high-parallel SoT coordination, preservation of evidence,
  generous waits, and centralized timer/concurrency configuration.
- No new owner approval, waiver, priority choice, destructive cleanup, or
  dispatcher/TAFE action is requested. The move is an exact in-root evidence
  preservation operation performed only after independent GO and reservation.

## Minimal reservation design

### 1. Immutable binding plus append-only events

`ensure_control_plane_schema` adds a narrowly keyed recovery-reservation record
and append-only event history. The immutable binding contains the exact tuple
listed in the P0 response plus a binding digest. State is derived from ordered
events (`reserved`, `moved`, `publication_minted`, `consumed`, or governed
`aborted`); historical events are never rewritten. Only one nonterminal
reservation may exist for an exact replacement path.

### 2. Reserve before any physical move

`reserve_bridge_repair_slot(...)` runs under the existing registry lock and one
short DB transaction. It verifies exact source/predecessor bytes, absent archive,
strict wrong-role diagnosis, active WI-5879 authorization evidence, and no
competing reservation, then commits the immutable binding and `reserved` event.
No file changes in this step. A crash now leaves the original file plus a durable
reservation; ordinary publication to the slot is already blocked.

### 3. Recoverable evidence move

`move_reserved_bridge_evidence(...)` validates the reservation, source, archive,
and hashes, then performs a no-overwrite exact move. It appends `moved` only
after readback. If the process dies between filesystem move and event append,
resume recognizes the only lawful physical state (source absent, exact archive
present) and appends the missing event. Source+archive, neither path, symlink,
wrong hash, or changed predecessor fails closed without publication.

### 4. Exact-slot mint enforcement and session-loss recovery

The ordinary bridge-capability mint path consults active reservations by exact
target path. A matching active reservation blocks ordinary mint. The
recovery-aware writer path accepts a reservation ID only after canonical
revalidation of its binding, fresh WI-5879 schema-v3 start packet, current
claims, exact archive/predecessor hashes, version 013, and `NO-ACTION` transition.
It then uses the ordinary WI-5825-backed publication capability lifecycle and
records the replacement capability hash in a `publication_minted` event.

Session ownership is evidence, not an unrecoverable lock. After claim expiry, a
new PB session may resume only after acquiring fresh exact claims and start
authority and proving the same reservation tuple. It cannot alter archive path,
replacement path, predecessor, required status, or invalid digest.

### 5. Receipt-bound completion

Reservation `consumed` is appended only when the exact replacement capability is
itself consumed for the exact replacement bytes. If the process dies after file
creation, WI-5825's durable capability-row fallback finalizes that capability;
reservation recovery then appends `consumed` idempotently. The reservation is
not cleared merely because a draft claim expires, a file appears, or registry
observation runs.

### 6. Incident execution after the shared API lands

1. Confirm WI-5825 is independently VERIFIED, shared targets are clean, and no
   foreign claim/packet overlaps the seven paths.
2. Revalidate v001-v013, all exact hashes, PAUTH/membership, receipts,
   cleanup-path absence, strict diagnosis, and WI-5617 open state.
3. Acquire WI-5879 GO-implementation claim and fresh schema-v3 start packet;
   acquire the exact victim claim before the move.
4. Persist and read back the exact reservation.
5. Move invalid v013 through the reserved writer path and read back exact
   archive bytes. Never overwrite either side.
6. Reclassify the same victim claim through `claim-no-action` after physical
   head is v012 GO; publish role-correct replacement v013 through the reserved
   writer path.
7. Read back the exact replacement receipt and consumed reservation; strict
   lifecycle must be role-correct and nonterminal.
8. Route replacement v013 to a distinct LO session for v014 `NO-GO`; v014 is
   not a PB target and must be read back before the WI-5879 report.
9. Execute TEST-11807's exact nodes and live readbacks, then file a factual
   implementation report. Independent verification/finalization remains later.

## Specification-derived verification plan

| Requirement | Executed evidence | Pass condition |
| --- | --- | --- |
| Durable binding | reservation API tests and live reservation readback | exact invalid/archive/replacement/predecessor tuple exists before move and survives process/session loss |
| Collision denial | ordinary mint plus foreign-session negative tests | any mint without matching reservation fails with zero target/event mutation |
| Crash after move | writer crash injection before `moved` event and after claim expiry | exact archive remains; replacement slot stays blocked; fresh authorized session resumes once |
| Exact replacement | reserved mint/consume tests | only v013 Prime `NO-ACTION` over exact v012 predecessor obtains consumed receipt and consumes reservation |
| WI-5825 reuse | capability recovery integration test | post-create crash finalizes through landed durable capability-row recovery; no duplicate recovery API |
| Timer ownership | diff scan and WI-5858 reference | zero new timeout/TTL/retry literals; no claim-TTL changes |
| Evidence preservation | SHA-256 before/after | cleanup artifact equals `ECDF0876...E42870D`; v001-v012 unchanged |
| Nonterminal semantics | strict resolver and distinct LO response | replacement v013 role-correct; v014 independently LO-authored `NO-GO`; WI-5617 remains open |
| Nonimpairment | exact target status/hash plus dispatcher/TAFE no-touch check | no WI-5617 source/test/project, dispatcher/TAFE, foreign claim/packet, or unrelated path mutation |
| TEST-11807 | four exact pytest nodes plus live receipt/reservation/hash/lifecycle readback | all executable nodes pass and every expected-outcome predicate is recorded |

## Acceptance Criteria

1. No shared source/test mutation starts until WI-5825 is implemented,
   independently VERIFIED, and its shared targets are clean.
2. A durable exact-slot reservation exists and is canonically read back before
   invalid v013 moves.
3. Claim expiry or process death never frees the reserved replacement slot; a
   fresh worker without exact reservation recovery authority produces zero
   target or receipt mutation.
4. Crash after move/before event and after file-create/before receipt both resume
   idempotently through reservation plus WI-5825 capability recovery.
5. Invalid bytes are preserved once at the declared cleanup path with exact
   SHA-256; v001-v012 remain byte-for-byte unchanged.
6. Replacement v013 is a receipt-consumed Prime `NO-ACTION` over exact v012;
   its exact capability consumption appends reservation `consumed`.
7. A distinct LO session publishes receipt-consumed v014 `NO-GO`; strict
   lifecycle resolution has no wrong-role or ambiguity diagnostic.
8. WI-5617 remains open/backlogged, TEST-11662 is not fabricated, and no
   missing requirements manifest is manufactured.
9. TEST-11807's four exact executable nodes and live predicates pass and are
   recorded in the implementation report.
10. No new hard-coded timer/TTL/retry literal, global worker leader, raw SQLite,
    dispatcher/TAFE mutation, foreign-lock handling, or unrelated path change.

## Pre-filing preflight subsection

Applicability and mandatory clause preflights must be run against this exact
completed content file immediately before live filing. Live filing is permitted
only with `preflight_passed: true`, both missing-spec lists empty, zero blocking
errors, zero blocking clause gaps, a current v002 hash, a fresh exact claim, and
canonical readback of the resulting v003 bytes/receipt.

## Risks and rollback

- **Shared-target collision:** WI-5825 has priority on all four source/test
  targets. WI-5879 waits for its independent VERIFIED and clean readback.
- **Reservation orphan:** it is intentionally durable and non-expiring. A
  governed abort requires exact binding readback, source/archive state proof,
  explicit reason, and no replacement capability. An abort event never deletes
  history.
- **Crash before move:** original invalid file remains and ordinary replacement
  mint is blocked by the reservation.
- **Crash after move:** exact archive remains and reservation blocks the vacant
  path; a newly authorized PB session resumes the same tuple.
- **Crash after replacement create:** WI-5825 capability recovery completes or
  compensates exact publication; reservation remains active until exact receipt.
- **Wrong content or predecessor drift:** fail closed before publication. Do not
  restore invalid `VERIFIED` bytes as authority.
- **Registry contention:** use externally configured generous waits and
  canonical re-observation. Never edit SQLite directly or create a global
  worker-leader lock.
- **Rollback of source work:** revert only WI-5879's four source/test hunks after
  preserving the reservation/event audit trail. Incident evidence is
  forward-only; after replacement publication, corrections use later numbered
  bridge versions.

## Files expected to change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `scripts/gtkb_bridge_writer.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
- `groundtruth.db` through the service-owned reservation/event and publication
  evidence writes only
- `bridge/gtkb-dispatcher-next-foundation-spike-013.md`
- `bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified`

## Explicit exclusions

No WI-5617 source/test/requirements implementation; no project membership or
PAUTH mutation; no TEST-11662 fabrication; no WI-5825 scope widening; no WI-5858
timer work; no `platform_tests/scripts/test_check_protected_commit_authorization.py`
change; no dispatcher or TAFE activation/configuration/runtime mutation; no raw
SQL; no manual capability/receipt insertion; no global lock; no credential,
deployment, release, push, history rewrite, destructive cleanup, or foreign
`.git/index.lock` operation.

## Recommended Commit Type

`fix`
