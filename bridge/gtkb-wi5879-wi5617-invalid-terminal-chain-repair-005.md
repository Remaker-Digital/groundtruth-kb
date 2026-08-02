REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; incident-consumer correction after independent v004; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5879-wi5617-invalid-terminal-chain-repair
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-004.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5879
Related Work Items: WI-5617, WI-5791, WI-5825, WI-5858, WI-5881

target_paths: ["bridge/gtkb-dispatcher-next-foundation-spike-013.md", "bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified", "groundtruth.db"]
implementation_scope: service_owned_metadata_and_evidence_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

# REVISED Incident-Consumer Proposal — WI-5617 Invalid-Terminal Repair

## Revision Disposition

Version 004 correctly proves that v003's incident-specific reservation does not
fence the canonical claim takeover race and duplicates the new generic owner.
This revision removes all generic source and test work from WI-5879. It makes
WI-5879 a three-target incident consumer that may run only after both generic
dependencies are independently implemented and VERIFIED:

- WI-5881 supplies the exact-generation reservation, atomic claim fence,
  fresh-session resume, event journal, and reservation-aware publication mint.
- WI-5825 supplies receipt back-fill and durable capability-row publication
  recovery.

WI-5879 then uses those landed interfaces for one immutable victim tuple. It
does not edit or reimplement the registry, claim CLI, control plane, writer, or
their tests. WI-5791/TEST-11758 remain superseded historical evidence and are
not treated as a landed contract.

## Response To Version 004

### F1 — claim takeover defeats an incident-only publication reservation

**Accepted.** WI-5879 no longer proposes a reservation primitive. Before the
invalid v013 moves, the later incident operation must call the independently
VERIFIED WI-5881 service to atomically persist the exact-generation reservation
and its initial victim-claim fence. Ordinary `draft`, `go_implementation`, and
`no_action_correction` operations must already be denied for that reserved
victim; only the WI-5881 recovery-resume operation may bind an expired/lost
owner under fresh WI-5879 authority.

After the move exposes v012 `GO`, the same reservation-aware claim epoch remains
authoritative. The repair worker uses the generic reserved transition to obtain
the exact claim kind required for the replacement Prime `NO-ACTION`; no ordinary
claim call is allowed in the move-to-replacement window. If that invariant is
not present and independently VERIFIED, WI-5879 remains blocked and does not
move evidence.

### F2 — WI-5881 owns the generic successor

**Accepted and sequenced.** The governed successor is now physical
`bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-001.md`,
status `NEW`, SHA-256
`1E202B943A742483C29F2D913C2F4903516074FBAFE5075E3D6ED5F47E786EDC`.
It declares the eight exact registry/claim/control-plane/writer/test targets,
maps TEST-11809 to multi-process takeover/resume/crash tests, and explicitly
leaves WI-5879 as a later incident consumer.

WI-5879 cannot begin merely because that proposal exists or later receives GO.
It waits for a factual implementation report and an independent VERIFIED that
records the exact TEST-11809 race outcomes. WI-5825 likewise must be
implemented, reported, and independently VERIFIED. All dependency targets must
be clean and their claims/start packets closed before this three-target
incident operation begins.

### F3 — TEST-11807 must test the decisive race without reimplementing it

**Accepted.** TEST-11807 remains an assertion over the live incident result,
not a new source-test carrier. Its expected outcome already requires exact
invalid-byte preservation, a receipt-consumed Prime v013 `NO-ACTION`, a current
independent LO v014 `NO-GO`, WI-5617 open state, and no source/test/dispatcher
byte changes.

The implementation report must cite WI-5881's independently VERIFIED TEST-11809
evidence, then record this incident's exact interleaving:

1. hold the reservation-bound pre-move victim claim;
2. persist and read back the immutable reservation/claim-fence epoch;
3. move the invalid v013 and expose v012 `GO`;
4. attempt a separate foreign ordinary Prime claim before the reserved
   `NO-ACTION` transition and record typed denial with zero mutation;
5. complete or deliberately resume through the authorized reservation-aware
   operation; and
6. prove only the exact replacement capability/receipt consumes the
   reservation.

No WI-5879 test node is added to registry/writer modules. TEST-11807 is recorded
PASS only after every live expected-outcome predicate and independent v014 are
canonically true.

## Exact Incident Binding

The later reservation and every recovery step bind this immutable tuple:

- victim document: `gtkb-dispatcher-next-foundation-spike`;
- invalid live path/version: `bridge/gtkb-dispatcher-next-foundation-spike-013.md`
  / `13`;
- invalid content SHA-256:
  `ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D`;
- archive path:
  `bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified`;
- exact predecessor path/SHA-256:
  `bridge/gtkb-dispatcher-next-foundation-spike-012.md` /
  `70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12`;
- prior v011 SHA-256:
  `2A3AAE14FA671D7D3FBFF8E6F8F01EF017723F6457091B13563C30D93C84EEDD`;
- replacement path/version/status: the same live v013 path, version 13, Prime
  `NO-ACTION` responding exactly to v012;
- consumer authority: WI-5879, active Bridge Protocol Reliability PAUTH v2,
  its current independent GO, exact claims, and schema-v3 start packet;
- dependencies: exact independently VERIFIED WI-5881 and WI-5825 report/verdict
  identities and TEST-11809 evidence;
- replacement payload: the exact normalized candidate bytes, byte size,
  content digest, compliance digest, specification/resource-bound evidence,
  and original Prime author/session metadata, all durably committed before the
  invalid origin moves;
- recovery invocation: the current recovery session, claim, claim-fence epoch,
  start packet, and invoker identity, recorded separately from the preserved
  original author metadata. Ordinary author-session/claim-session equality
  remains unchanged outside the reservation-aware recovery path.

Any tuple, physical-state, authority, claim-fence, capability, or receipt drift
fails closed before the next operation.

## Current Chain, Authority, And Target State

- WI-5879 versions 001–004 form a strict valid chain: `NEW`, `NO-GO`,
  `REVISED`, `NO-GO`. Current v004 SHA-256 is
  `1C0E97C26F0B756255D9E46AA29E4EDC8E95F2CAB9D47CC43EB03C5C94A02692`.
- The victim strict resolver still fails `WRONG_STATUS_AUTHOR_ROLE` because
  physical v013 is Prime-authored `VERIFIED`. No byte is changed by this
  proposal.
- Invalid v013 is present and untracked at its exact hash; the cleanup target is
  absent. V012 retains its consumed publication capability/receipt; no v013
  capability exists.
- WI-5617 remains open/backlogged and TEST-11662 has no fabricated result.
  WI-5879/TEST-11807 remain open with no result.
- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is active; WI-5879 is an active
  direct member. The list-free project PAUTH in the header is active v2,
  unexpired, and covers bridge, metadata, and governance-evidence operations.
  Legacy WI approval metadata is noncontrolling.
- WI-5879 and victim claims are null at candidate preparation. Physical v005 is
  absent.

`groundtruth.db` is a shared service-owned SoT, not an exclusive whole-file
checkout target. The incident may write only exact WI-5881 reservation/event,
victim-claim, replacement-capability/receipt, registry-observation, WI-5879,
TEST-11807, and WI-5617 rows through governed service APIs and short row-level
transactions/CAS. It does not hash-bind or lock the whole DB file and does not
block unrelated-row work.

Several current strict GO threads also declare `groundtruth.db`. Their claims
are null or expired at preparation, and their record cohorts are not adopted.
Immediately before implementation, the schema-v3/cross-claim gates must prove
no active packet or claim reserves the same exact rows or either bridge path.
Any exact-row collision fails closed; unrelated row-level transactions remain
parallel.

The foreign zero-byte `.git/index.lock` dated
`2026-08-01T08:59:21.8949959Z` remains preserved. WI-5819/WI-5849 own typed
stale-lock remediation. This repair performs no Git finalization while that
lock remains foreign and does not classify, remove, or bypass it.

## Governed Incident Execution

After WI-5881 and WI-5825 are independently VERIFIED and all preconditions are
fresh:

1. Re-read exact WI-5879/victim chains, hashes, capability/receipt state,
   cleanup absence, project PAUTH, claims, schema-v3 packets, WI-5617,
   TEST-11662, TEST-11807, and exact row/path overlaps.
2. Acquire WI-5879's fresh exact `go_implementation` claim and schema-v3 start
   packet. Acquire/bind the victim claim only through the WI-5881 reservation
   operation; do not use ordinary claim takeover.
3. Normalize and compliance-audit the exact replacement candidate, then
   atomically commit and canonically read back its exact bytes, byte size,
   content/compliance/resource-bound digests, preserved original-author
   metadata, immutable reservation, and initial claim fence before moving any
   byte.
4. Move invalid v013 once through the reserved evidence operation, with
   no-overwrite semantics. Read back the archive hash. A crash resumes only the
   exact recognized physical state.
5. From a separate eligible Prime session, attempt ordinary victim claim
   takeover after v012 becomes visible. Require typed reservation denial and
   zero claim/event/target/capability/receipt mutation.
6. Through the reservation-aware claim transition, publish the durably stored
   exact replacement v013 bytes as Prime `NO-ACTION` responding to v012. Bind
   its publication capability to the reservation, preserve the original author
   envelope, and separately record/validate the current invoker, claim, start
   packet, and claim-fence epoch. Do not relax ordinary author-session equals
   claim-session enforcement.
7. Use the landed WI-5825 recovery path if publication is ambiguous or crashes
   after create. Canonically read back the exact consumed receipt and reservation
   `consumed` event; never blind-retry a numbered version.
8. Route replacement v013 to a distinct Loyal Opposition session. Require
   receipt-consumed v014 `NO-GO` and strict-valid current readback before
   recording TEST-11807 or filing the report.
9. Record TEST-11807 through the governed test-result service only when every
   predicate below is true; file a factual implementation report. Independent
   verification/finalization remains later and cannot touch the foreign lock.

## WI-5825 And WI-5881 Separation

- WI-5881 owns generic reservation schema/events, claim fencing and resume,
  claim CLI, registry control plane, writer mint enforcement, and TEST-11809.
- WI-5825 owns existing-file receipt back-fill, compensated publication
  recovery, exact-byte republish, and durable capability-row fallback.
- WI-5879 owns only the exact invalid live path, exact archive path, and
  service-managed incident rows for the immutable tuple above.
- WI-5858 remains sole owner of claim TTL/retry/tuning externalization. This
  incident adds no timer value and does not treat a longer TTL as correctness.

No source/test hunk from either dependency is copied, amended, or attributed to
WI-5879.

## Timer, Parallelism, And Append-Only Disposition

All waits, retries, lock bounds, claim TTLs, and concurrency limits come from
the centralized configuration SoT owned by WI-5858/Timer Governance. The
incident introduces no hard-coded value, sleep, global leader, or repository
lock. Only short exact-row reservation/claim/event/CAS transactions serialize;
preparation, validation, unrelated claims, and unrelated publications remain
parallel.

Invalid bytes move once to the declared in-root cleanup evidence path because
the same numbered live path must hold the role-correct replacement. The exact
archive digest and move event preserve append-only provenance; no historical
v001–v012 content is rewritten. Every subsequent correction remains a new
numbered bridge version or append-only service event.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — strict role/status authority, governed
  writer, independent review, and forward correction.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — replacement v013 is a Prime
  nonterminal correction and cannot close WI-5617.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — reservation, claim, capability,
  receipt, registry, work-item, and test evidence uses canonical current APIs.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` — the
  reservation-aware victim claim remains bound to the exact governed document
  authority across owner loss and resume.
- `DCL-SESSION-ROLE-RESOLUTION-001` — original author role and current recovery
  invoker role come from exact session envelopes and cannot be inferred or
  substituted by the reservation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active direct
  project PAUTH governs bridge/metadata/evidence operations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, WI,
  and exact incident targets are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governing
  links precede the repair.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11807 maps to exact
  live predicates and independently VERIFIED TEST-11809 evidence.
- `GOV-ARTIFACT-APPROVAL-001` — project PAUTH does not waive service-owned
  metadata, claim, start, report, or verification gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — invalid evidence, successor
  dependencies, result, report, and review remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5617, WI-5791, WI-5825, WI-5858, WI-5879,
  and WI-5881 retain nonduplicated ownership.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — unrelated DB rows, claims,
  bridge threads, source/tests, and harnesses remain unchanged.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — recovery uses
  the landed deterministic service, not session lore.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — live, archive, and service SoT
  targets remain under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — native Windows execution
  self-enforces exact GO/claim/start and writer boundaries.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` — persistent
  program completion and independent-review boundary.
- `DELIB-202667082` — preserved WI-5617 NO-GO history.
- `DELIB-202667724` and `DELIB-202667732` — Bridge Protocol Reliability
  project grant and active v2 repair authority.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — exact
  row/path CAS and unrelated-worker parallelism, not a global leader.
- `DELIB-202667722` — centralized timer/concurrency configuration.
- `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-004.md` — exact
  independent claim-takeover and successor-ownership findings answered here.
- `bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-001.md`
  — current generic dependency proposal; existence is not implementation.

## Owner Decisions / Input

No new owner decision is requested. WI-5879 is an active direct member of an
active list-free authorized project. The owner has already directed exact
parallel-SoT repair, generous externally configured waits, evidence
preservation, and disabled dispatcher/TAFE. All independent bridge, claim,
schema-v3, report, and verification gates remain mandatory.

## Requirement Sufficiency

Existing requirements sufficient. WI-5879, TEST-11807, physical v004,
GOV-FILE-BRIDGE-AUTHORITY-001, active project/freshness/testing requirements,
and the now-filed generic WI-5881 scope fully determine this incident consumer.
No new role, status, timer policy, source contract, or owner choice is needed
before independent review.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Independent GO, independently VERIFIED WI-5881 and WI-5825 prerequisites, fresh exact claims/start, immutable reserved evidence repair, independent LO v014, TEST-11807 result, factual report, and independent verification.",
  "baseline": {
    "repair_thread": "WI-5879 v004 NO-GO proves incident-only reservation lacks claim fencing",
    "victim": "gtkb-dispatcher-next-foundation-spike v013 is PB-authored VERIFIED and strict-invalid",
    "invalid_digest": "ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D",
    "predecessor_digest": "70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12",
    "generic_dependency": "WI-5881 v001 NEW; not yet GO, implemented, or VERIFIED",
    "receipt_dependency": "WI-5825 v006 GO; not yet implemented or VERIFIED"
  },
  "before_behavior": "Moving invalid v013 exposes v012 GO while the recovery worker holds a preemptible non-GO victim claim; a foreign ordinary GO claim can take over before replacement publication.",
  "after_behavior": "WI-5879 consumes the independently VERIFIED generic reservation/claim fence and WI-5825 receipt recovery for one immutable tuple; ordinary takeover is denied and only the exact replacement receipt consumes the reservation.",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, active PAUTH v2, independently VERIFIED WI-5881/WI-5825 contracts, strict bridge chain, governed service rows, and TEST-11807.",
  "essential_context_preservation": "Preserve exact invalid/archive/replacement/predecessor paths and hashes, role-correct nonterminal status, claim-fence epoch, capability/receipt identity, WI-5617 open state, WI-5791 history, dependency ownership, row-level parallelism, and no-dispatcher/TAFE boundary.",
  "obsolete_guidance_disposition": "WI-5879 v003 generic reservation design is removed from incident scope; WI-5881 is the sole successor owner. WI-5791 remains superseded evidence and is not reopened.",
  "history_preservation": "Victim v001-v012 and WI-5879 v001-v004 remain unchanged; invalid v013 bytes are preserved once at the declared archive; reservation/events/receipt/test/report/review evidence is append-only.",
  "provenance": "WI-5879; TEST-11807; WI-5879 v004; WI-5881 v001/TEST-11809; WI-5825; WI-5858; WI-5791/TEST-11758; DELIB-202667724; DELIB-202667732; DELIB-202667722; DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT.",
  "self_descriptive_naming": "Use exact victim generation, invalid evidence archive, reservation-bound victim claim, claim-fence epoch, replacement capability, receipt-bound consumption, and independent nonterminal review.",
  "expected_result": {
    "archive": "one exact invalid-byte artifact at the declared cleanup path",
    "replacement": "receipt-consumed Prime v013 NO-ACTION over exact v012 from exact candidate bytes durably stored before the move",
    "provenance": "original author/session metadata is preserved while current recovery invoker, claim, start packet, and claim-fence epoch are separately validated",
    "claim_race": "foreign ordinary Prime takeover after the move is denied with zero mutation",
    "review": "distinct Loyal Opposition session publishes current strict-valid v014 NO-GO",
    "work_item": "WI-5617 remains open and no source/test/dispatcher bytes change"
  },
  "hard_invariants": [
    "WI-5881 and WI-5825 are independently VERIFIED before incident mutation",
    "Exact normalized candidate bytes, size, content/compliance/resource-bound digests, and original author metadata are durable before origin loss",
    "Reservation and initial claim fence are committed/read back before the move",
    "Ordinary claim and publication mint cannot bypass the active reservation",
    "Only exact replacement receipt consumption completes the reservation",
    "TEST-11807 is recorded only after current independent v014 and every live predicate",
    "Only exact incident bridge paths and exact governed service rows change",
    "No hard-coded timer, global leader, raw SQLite, dispatcher/TAFE, Git-lock, or source/test mutation"
  ],
  "fail_closed_conditions": [
    "Dependency not independently VERIFIED or shared targets/claims not closed",
    "Changed invalid/archive/replacement/predecessor/role/status/authority/candidate-byte binding",
    "Ambiguous source/archive state, symlink, wrong digest, claim-fence epoch drift, or foreign owner",
    "Missing GO, PAUTH, exact claim, schema-v3 packet, capability, receipt, or independent v014",
    "Exact-row/path collision or ambiguous publication result"
  ],
  "rollback": {
    "instructions": "Before reservation creation, no incident mutation exists. After reservation creation, preserve append-only events and use only the generic governed abort before capability mint with exact state proof. After replacement publication, correct forward through later numbered versions; never restore invalid VERIFIED bytes as authority.",
    "verification": "Re-run dependency TEST-11809 evidence, strict lifecycle, exact hashes, reservation/events/claims/capability/receipt readbacks, foreign takeover denial, WI-5617 and TEST-11807 readbacks, source/test nonimpairment, and dispatcher/TAFE/Git-lock no-touch checks."
  }
}
```

## Specification-Derived Verification Plan

| Requirement | Required executed evidence |
|---|---|
| Generic claim/publication fence | exact independently VERIFIED WI-5881 report/verdict and TEST-11809 node results |
| Receipt recovery | exact independently VERIFIED WI-5825 report/verdict and crash-recovery results |
| Immutable tuple | reservation readback binds all declared paths, hashes, status/role, authority, and claim-fence epoch before move |
| Durable replacement source | readback before move proves exact normalized candidate bytes, byte size, content/compliance/resource-bound digests, and original author metadata; a fresh owner can publish without reconstructing bytes |
| Author/invoker separation | reserved recovery preserves original author/session metadata and separately validates current invoker/claim/epoch; ordinary mint equality remains unchanged |
| Claim-race denial | separate Prime ordinary claim after v012 exposure returns typed reserved-generation denial and changes no row/event/file/capability/receipt |
| Evidence preservation | archive SHA equals `ECDF0876...E42870D`; victim v001-v012 hashes unchanged |
| Replacement authority | v013 is Prime `NO-ACTION`, responds exactly to v012, and has exact consumed capability/receipt |
| Independent review | distinct LO session publishes receipt-consumed v014 `NO-GO`; strict resolver is valid and current |
| Work-item/test integrity | WI-5617 remains open; TEST-11662 is not fabricated; TEST-11807 is recorded only from exact observed predicates |
| Nonimpairment | no source/test, dispatcher/TAFE, project/PAUTH, foreign claim/packet, unrelated DB row, or Git-lock mutation |
| Parallelism/timers | unrelated row/slug operations remain concurrent; zero new literal timer/TTL/retry/throttle/leader |

TEST-11807's result packet must record dependency verdict/report hashes,
reservation/event/claim-fence identities, exact source/archive/replacement and
predecessor hashes, foreign denial JSON, replacement capability/receipt,
strict v014 readback, WI-5617/TEST-11662 state, exact changed-row census, and
source/test/dispatcher/TAFE/Git-lock nonimpairment.

## Acceptance Criteria

1. WI-5881 and WI-5825 are implemented, factually reported, independently
   VERIFIED, and their shared source/test targets and claims are closed/clean.
2. The exact reservation plus initial claim fence commits and is canonically
   read back before invalid v013 moves, together with exact normalized
   replacement bytes, byte size, content/compliance/resource-bound evidence,
   and preserved original author metadata.
3. Invalid v013 moves once to the declared archive with exact SHA-256; v001-v012
   remain byte-for-byte unchanged.
4. A separate Prime ordinary claim attempt after v012 becomes head is denied by
   the reservation with zero claim/event/target/capability/receipt mutation.
5. The reservation-aware operation publishes only exact Prime v013 `NO-ACTION`
   over exact v012 from the durable candidate bytes; the exact replacement
   receipt consumes the reservation. Original author provenance and current
   recovery invoker/claim/epoch remain distinct and validated, with no change
   to ordinary mint equality.
6. A distinct LO session publishes receipt-consumed v014 `NO-GO`; strict
   lifecycle is current and role-correct.
7. WI-5617 remains open/backlogged, TEST-11662 is not fabricated, and
   TEST-11807 records PASS only after every exact live predicate is observed.
8. WI-5879 changes no generic source/test target and reimplements no WI-5881 or
   WI-5825 behavior.
9. Only the two exact bridge paths and exact service-managed incident rows
   change; unrelated DB rows, claims, packets, and slugs remain parallel.
10. No hard-coded timer/TTL/retry/throttle/concurrency value, global leader,
    raw SQLite, dispatcher/TAFE, project/PAUTH, credential, source/test,
    foreign-lock, deployment, release, push, history rewrite, or destructive
    cleanup operation occurs.

## Risks And Rollback

- **Dependency drift:** any WI-5881/WI-5825 head, report, verdict, target, claim,
  or API drift returns WI-5879 to revision before mutation.
- **Claim takeover:** no move occurs until the generic claim fence is live and
  read back; ordinary post-move takeover is an executed negative test.
- **Shared DB contention:** only exact rows/CAS serialize. A typed contention or
  currentness failure pauses safely; it never triggers raw SQL or blind retry.
- **Ambiguous publication:** use WI-5825 canonical capability recovery/readback;
  never publish another numbered file based only on an exception.
- **Rollback:** before reservation, there is nothing to undo. After reservation,
  preserve events and use governed abort only before mint. After replacement,
  correct forward; invalid evidence remains archived.

## Candidate Pre-Filing Gates

Applicability, mandatory clause, and writer-compliance audits must pass against
these exact stable bytes. Live filing additionally requires current v004/hash,
physical v005 absence, active project/PAUTH, fresh exact claim, unchanged
incident tuple/dependency heads, registry observation, governed writer append,
and canonical status/path/hash/claim-consumption readback.

## DISARM — Implementation Boundary

This proposal authorizes no evidence move, database row mutation, claim
reclassification, reservation, replacement publication, TEST result, source or
test edit, Git action, or dispatcher/TAFE operation. All prerequisites,
independent GO, fresh claims/start, exact tuple/overlap checks, factual report,
and independent verification remain mandatory.

## Files Expected To Change

- `bridge/gtkb-dispatcher-next-foundation-spike-013.md`
- `bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified`
- `groundtruth.db` through exact governed service rows only

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
