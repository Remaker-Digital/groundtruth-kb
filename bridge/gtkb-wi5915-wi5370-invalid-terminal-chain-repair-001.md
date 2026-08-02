NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ordinary per-WI authority only; former CF-10 all-program serialization authority rescinded; dispatcher and TAFE deliberately disabled
author_metadata_source: task-local interactive transcript and current session envelope

bridge_kind: prime_proposal
Document: gtkb-wi5915-wi5370-invalid-terminal-chain-repair
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5915
Related Work Items: WI-5370, WI-5638, WI-5761, WI-5764, WI-5825, WI-5879, WI-5881, WI-5898, WI-5899, WI-5909, WI-5913

target_paths: ["bridge/gtkb-wi5370-terminal-archive-pilot-execution-007.md", "bridge/cleanup-evidence/wi5915-invalid-pb-verified-007-20260801/gtkb-wi5370-terminal-archive-pilot-execution-007.md.invalid-pb-verified", "groundtruth.db"]

implementation_scope: service_owned_metadata_and_evidence_repair
proposal_authorization_state: review_only_go_ineligible_pending_governance_holds
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

# Review-Only Incident Proposal — WI-5370 Invalid PB-Authored VERIFIED Repair

## Review-Only Disposition

This v001 is design and evidence only. The custom authorization metadata is
descriptive, not a mechanical implementation-start control. Current project
applicability may still mechanically allow packet/start operations for this
target cohort. Loyal Opposition must issue `NO-GO` or an equivalent
non-implementation hold on these exact bytes. It must not issue `GO` until all
generic recovery, dependency, and project-lifecycle holds below are
independently corrected and Prime Builder files later exact `REVISED` bytes for
fresh independent review.

This proposal does not acquire a `go_implementation` claim, create a schema-v3
packet, reserve or move evidence, replace v007, mutate incident rows, record
TEST-11833, change WI-5370/WI-5764 state, touch source/test code, or activate
dispatcher/TAFE.

## Purpose And Exact Scope

Physical `bridge/gtkb-wi5370-terminal-archive-pilot-execution-007.md`
begins `VERIFIED`, but its envelope identifies `prime-builder/goose/G`,
session `G-2026-07-31T19-28-58Z`. Prime Builder cannot author `VERIFIED`, so
the physical artifact is not terminal authority even though superficial
`gt bridge show` reports v007 `VERIFIED`.

WI-5915 repairs only this exact numbered generation without erasing evidence
or absorbing generic recovery behavior. Its three targets are the invalid live
v007, an exact cleanup-evidence archive, and exact service-owned incident rows
in `groundtruth.db`. It does not reimplement the archive pilot, WI-5638 archive
reconciliation, WI-5764 fabricated MemBase closure correction/rule guard, or
generic WI-5881/WI-5825/WI-5899 services.

## Immutable Incident Tuple

- victim document: `gtkb-wi5370-terminal-archive-pilot-execution`;
- invalid live path/version:
  `bridge/gtkb-wi5370-terminal-archive-pilot-execution-007.md` / `7`;
- invalid byte size / SHA-256:
  `1806` / `D4CEB7B4EAF34B791525D492A927909F0F2776DBBF6D3796E83F2499BDA7EC66`;
- invalid status / author role: `VERIFIED` / `prime-builder`;
- invalid author session: `G-2026-07-31T19-28-58Z`;
- archive path:
  `bridge/cleanup-evidence/wi5915-invalid-pb-verified-007-20260801/gtkb-wi5370-terminal-archive-pilot-execution-007.md.invalid-pb-verified`;
- predecessor path / SHA-256:
  `bridge/gtkb-wi5370-terminal-archive-pilot-execution-006.md` /
  `C8B2A3C1ABFD515821945EA5C110486058C76E5C46BF3279AC5D51087229A6FA`;
  full_evidence_reason: v006 is intentionally cited as the immutable
  predecessor that the role-correct replacement must answer, while physical
  v007 is the invalid victim being preserved and replaced;
- replacement path/version/status: the same live v007 path/version, Prime
  `NO-ACTION` responding to exact v006 and rejecting v006's governance-invalid
  disposition-close approval; archived PB `VERIFIED` remains evidence only;
- incident consumer: WI-5915 / TEST-11833;
- generic prerequisites: independently VERIFIED, receipt-complete WI-5881 and
  WI-5825 plus independently VERIFIED WI-5899 dependency-CAS service/postimage;
- lifecycle prerequisite: independently VERIFIED WI-5761 or sole governed
  successor and coherent Bridge Protocol Reliability project lifecycle;
- durable replacement source: normalized bytes, byte size,
  content/compliance/resource-bound digests, original author/session metadata,
  and immutable victim evidence committed before origin loss;
- current recovery authority: invoker session/role, WI-5915 claim, schema-v3
  packet, reservation/claim-fence epoch, capability, receipt, and service
  revision stored separately from original author provenance.

Any path, version, bytes, status, role, predecessor, project, PAUTH,
dependency, claim, reservation, capability, receipt, or physical-state drift
fails closed before the next effect.

## Preserved Chain Evidence

| Version | Status | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| 001 | NEW | 39383 | `967E444AB91B620661D5C0939C78B777B6F6883D0B5B2E08F20B41B517E5450D` |
| 002 | GO | 11338 | `735D72450C68C1A2F1E4B1E8AECF2DC1CC6919305439CC22F5989F5C0739B704` |
| 003 | NEW | 19606 | `56A4460BAF96FB6A7794B048DFA4BF3D268DBD66DDA748A91DC3430A2CA99A04` |
| 004 | NO-GO | 16104 | `8125A56651DD306252321C7EC3B773642517698AC9643120F8505A2EDF0DE834` |
| 005 | NO-ACTION | 2146 | `538788382FDCB8DE8125F190B3ED5DA717F205BD5AA47B3850C4B55C1855E851` |
| 006 | GO | 2301 | `C8B2A3C1ABFD515821945EA5C110486058C76E5C46BF3279AC5D51087229A6FA` |

The invalid v007 remains live/untracked at the tuple above; the archive is
absent. No Git commit contains v007. Versions 001-006 remain byte-identical.
No history is rewritten and no dummy implementation is manufactured.

V005 explicitly says v004's semantic defect requires a substantive revision
to the pilot report and gives a three-step path toward that revision. It is a
Prime `NO-ACTION`, not terminal closure. V006 is governance-invalid because it
calls v005 a "non-implementation carrier / disposition-close", says no
revisions are required, and omits mandatory Clause Applicability evidence. The
role-correct replacement v007 must respond to exact v006, reject all three v006
defects, and request a new independent corrected nonterminal verdict. It must
not use `NO-ACTION` merely to reject the archived same-number victim.

## Why WI-5370 Is Not Terminal

The archive pilot's v004 independent verification found two substantive
failures: archived terminal chains remained actionable, and the implementation
report was not finalization-ready. V005 preserved that correction requirement.
Neither v006's false disposition-close nor v007's PB-authored `VERIFIED`
supplies an implementation, executed correction evidence, valid independent
verification, or lawful terminalization.

WI-5638 owns the separate archive reconciliation implementation and currently
has `GO`, but its target cohort is foreign-dirty and its project lifecycle is
scarred. WI-5764 owns fabricated WI-5370 MemBase closure correction and a
claimed-file-operation rule guard. WI-5915 restores only a role-valid
nonterminal bridge head. WI-5370 remains open for substantive correction after
incident recovery.

## Non-Waivable Dependency And Lifecycle Gate

No incident implementation begins until one current read proves:

1. WI-5899 is independently VERIFIED and has set WI-5915's structured
   `depends_on_work_items` postimage to exactly `["WI-5881","WI-5825"]` with
   expected-version CAS, normalized hash, audit receipt, and zero unrelated
   drift. The field is currently null.
2. WI-5825 is independently VERIFIED and receipt-complete for exact-byte
   republish, compensated recovery, and receipt backfill.
3. WI-5881 is independently VERIFIED and receipt-complete for durable
   candidate bytes, claim fence, crash/race recovery, current-invoker
   separation, and reservation-aware publication mint.
4. WI-5761 or one sole governed successor has independently reconciled the
   active/non-null-`completed_at` invariant and the Bridge Protocol Reliability
   project no longer carries its current lifecycle scar.
5. Fresh operation-time authority confirms exact WI-5915 membership, active
   applicable PAUTH, immutable tuple, null competing claim/start, and no
   reservation, capability, receipt, row, or path conflict.

Proposal existence or mechanically `allowed` PAUTH output cannot substitute
for these predicates.

## Governed Future Execution

Only after a later exact `REVISED` proposal receives independent implementation
approval and every hold closes:

1. Re-read WI-5915, WI-5370, WI-5764, TEST-11833, project/PAUTH, complete victim
   chain, all hashes, archive absence, dependency reports/verdicts, claims,
   packets, capabilities, receipts, and exact row/path overlaps.
2. Acquire WI-5915's exact `go_implementation` claim and fresh schema-v3 start;
   bind the victim through WI-5881's verified reservation and claim fence.
3. Normalize and durably store the role-correct replacement v007 plus all
   evidence/provenance before moving any invalid byte.
4. Move invalid v007 once to the exact archive with no-overwrite semantics and
   verify the 1,806-byte SHA. Ambiguity uses typed recovery only.
5. Prove a separate ordinary claimant cannot take over after v006 exposure,
   with zero claim/event/path/capability/receipt mutation.
6. Publish receipt-consumed Prime v007 `NO-ACTION` responding to exact v006,
   rejecting v006's false disposition-close, no-revision, and missing-clause
   defects, and requiring corrected independent nonterminal review.
7. A distinct Loyal Opposition session publishes the next strict-current
   nonterminal verdict. It must keep WI-5370 open and must not attribute archive
   semantics or WI-5764 work to WI-5915.
8. Record TEST-11833 only after every exact predicate, file a factual WI-5915
   report, and route independent verification.

## Service-Owned Database And Parallelism Boundary

`groundtruth.db` is a shared service-owned SoT, not a whole-file checkout
target. Future execution mutates only exact reservation/event, victim-claim,
capability/receipt, registry-observation, WI-5915, TEST-11833, and WI-5370
incident rows through governed APIs and short row-level CAS transactions. It
never uses raw SQLite for mutation.

Until WI-5909 is independently VERIFIED and adopted by all consumers, current
path-wide database collision rules remain binding. That compatibility rule is
not authority for a global leader. No literal timer, retry sleep, throttle,
concurrency cap, repository-wide lock, or global serialization leader is added.

## Scope Separation And Nonimpairment

- WI-5915: exact invalid live v007, its archive, and incident rows only.
- WI-5881: generic reservation, claim fence, recovery invoker, event, and mint.
- WI-5825: existing-file recovery and receipt backfill.
- WI-5899: generic dependency-postimage CAS.
- WI-5761: project-reactivation lifecycle coherence.
- WI-5638: archive/live-state reconciliation implementation.
- WI-5764: fabricated WI-5370 MemBase closure correction and rule guard.
- WI-5370: substantive archive-pilot correction and terminal verification.

No source/test, dispatcher/TAFE, project/PAUTH, credential, Git/index/lock,
deployment, release, push, history rewrite, destructive cleanup, or unrelated
row/claim mutation belongs to WI-5915.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — only Loyal Opposition may author
  `VERIFIED`; repair is forward-only and independently reviewed.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — replacement v007 rejects v006's false
  disposition-close/no-revision decision and missing mandatory clause evidence;
  it is not itself closure or verification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — all tuple, dependency, project, claim,
  reservation, capability, receipt, and test predicates are current.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` — original author and current recovery
  invoker authority remain separate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — project,
  membership, PAUTH, operation, target, and lifecycle gates are conjunctive.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — exact project,
  PAUTH, WI, targets, and specifications precede review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11833 records PASS
  only from executed exact predicates and independent dependency evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — foreign bytes, WI-5638,
  WI-5764, and unrelated state remain separate.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — typed services,
  not session lore or raw DB mutation, perform recovery.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — evidence and corrections remain
  durable, explicit, and append-only.
- `GOV-STANDING-BACKLOG-001` — all named WIs/tests retain separate ownership.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every artifact stays under
  `E:/GT-KB`.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` — persistent program
  completion and independent-review boundary.
- `DELIB-202667724` and `DELIB-202667732` — Bridge Protocol Reliability project
  authorization and v2 mutation-class correction.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` and
  `DELIB-202667517` — short atomic critical sections and useful parallelism,
  never a steady-state global leader.
- `bridge/gtkb-wi5764-wi5370-fabricated-closure-correction-011.md` — current
  separate WI-5764 correction scope; it is not physical v007 recovery.
- `bridge/gtkb-wi5913-wi5636-invalid-terminal-chain-repair-002.md` (current
  `NO-GO`, SHA-256
  `484BDC5761C9A1BE81AE551E863CD524A2AB5441B47EED6B15F430B1943BFB34`) —
  exact incident-consumer precedent and current dependency hold for a distinct
  victim tuple.

## Owner Decisions / Input

No new owner decision is requested. Existing direction requires genuine
terminal governance, evidence preservation, independent review, high
parallelism, generous governed waits, and correction of concurrency
bottlenecks. Project authorization does not waive later GO, claim, start,
report, verification, or finalization authority.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5915, TEST-11833, the exact physical
v007, strict role/status authority, generic recovery dependencies, WI-5764
separation, and the accepted incident pattern determine the repair. No generic
source contract or new owner policy is introduced.

## Specification-Derived Verification Plan

| Requirement | Required executed evidence |
| --- | --- |
| Generic claim/publication fence | exact independently VERIFIED WI-5881 report/verdict and recovery tests |
| Receipt recovery | exact independently VERIFIED WI-5825 report/verdict and exact-byte recovery tests |
| Dependency authority | independently VERIFIED WI-5899 postimage and audit receipt |
| Project lifecycle | independently VERIFIED WI-5761/successor evidence and coherent project/PAUTH readback |
| Immutable tuple | reservation binds every path/hash/status/role/authority before move |
| Evidence preservation | archive is 1,806 bytes at exact SHA; v001-v006 equal the table |
| Claim-race denial | ordinary claimant receives typed reserved-generation denial with zero mutation |
| Replacement authority | v007 is receipt-consumed Prime `NO-ACTION` over exact v006 rejecting all v006 defects |
| Independent review | distinct LO publishes strict-current nonterminal verdict and keeps WI-5370 open |
| Scope separation | no WI-5638, WI-5764, archive implementation, or generic recovery work is attributed to WI-5915 |
| Work/test integrity | TEST-11833 PASS only after all observed predicates and changed-row census |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-FILE-BRIDGE-AUTHORITY-001; DCL-NO-ACTION-STATUS-SEMANTICS-001; WI-5915; TEST-11833; exact WI-5370 v006/v007 incident tuple",
  "canonical_authority": "Status-bearing numbered bridge files plus service-owned reservation, publication receipt, incident, work-item, and test records",
  "primary_route": "WI-5881 reservation and claim fence, WI-5825 exact-byte publication recovery, governed bridge writer, and independent Loyal Opposition review",
  "before_behavior": "PB-authored VERIFIED v007 superficially makes WI-5370 terminal, while v006 incorrectly treats v005 as disposition-close, says no revision is required, and omits mandatory Clause Applicability.",
  "after_behavior": "Invalid v007 is preserved at an exact archive, receipt-consumed Prime v007 NO-ACTION rejects all v006 defects, and a distinct Loyal Opposition session restores a strict-current nonterminal head for substantive WI-5370 correction.",
  "self_descriptive_naming": "victim_document, invalid_live_path, invalid_sha256, archive_path, predecessor_sha256, reservation_epoch, claim_fence_epoch, original_author_session, recovery_invoker_session, capability, receipt, and service_revision",
  "obsolete_guidance_disposition": "V005 is not terminal closure; v006's disposition-close, no-revision, and missing-clause approval is rejected; archived PB VERIFIED is evidence only.",
  "history_preservation": "Versions 001-006 remain byte-identical; invalid v007 moves once without overwrite; replacement v007 is forward recovery with separate original/recovery provenance.",
  "baseline": {
    "strict_state": "invalid because v007 VERIFIED is PB-authored",
    "v006_governance": "false disposition-close, false no-revision conclusion, and missing mandatory Clause Applicability",
    "archive": "absent",
    "wi5370_substance": "v004 blockers unresolved"
  },
  "expected_result": {
    "strict_state": "role-valid and nonterminal after corrected independent review",
    "replacement_v007": "receipt-consumed Prime NO-ACTION responding to exact v006 and rejecting all three defects",
    "archive": "exact 1806-byte invalid victim at declared SHA/path",
    "wi5370_substance": "remains separate and open until genuinely verified"
  },
  "rollback": {
    "instructions": "Before reservation there is no effect; after reservation use typed append-only abort/recovery; after replacement correct only through later numbered versions and never restore invalid evidence as authority.",
    "verification": "Re-read live/archive hashes, reservation/receipt states, v001-v006 hashes, claim/capability census, TEST-11833, WI-5764 separation, and strict nonterminal chain."
  },
  "hard_invariants": [
    "Prime Builder never authors GO, NO-GO, or VERIFIED",
    "NO-ACTION never creates terminal closure",
    "replacement v007 responds to exact v006 and rejects all v006 governance defects",
    "invalid v007 bytes and original author provenance remain durable",
    "WI-5370 substantive correction, WI-5638, and WI-5764 remain separate",
    "no dispatcher, TAFE, Git, index, timer, project, PAUTH, source, test, credential, or unrelated-row mutation"
  ],
  "fail_closed_conditions": [
    "any incident path, byte, hash, status, role, or predecessor drifts",
    "WI-5881, WI-5825, WI-5899, or lifecycle repair is not independently VERIFIED/current",
    "project, PAUTH, claim, packet, reservation, capability, or receipt authority is missing/stale",
    "replacement bytes/evidence are not durable before origin loss",
    "an ordinary claimant can take over the reserved generation",
    "replacement semantics reject only the archived victim instead of v006",
    "corrected independent review would treat WI-5370 as terminal"
  ],
  "essential_context_preservation": "Preserve v001-v006 hashes, exact invalid-v007 tuple, original author/session, current recovery invoker/claim/epoch, v005 semantics, all v006 defects, WI-5638/WI-5764 boundaries, dependency evidence, reservation events, capability, receipt, service revision, and TEST-11833."
}
```

## Acceptance Criteria

1. WI-5899, WI-5881, WI-5825, and WI-5761 lifecycle successor are
   independently VERIFIED/current before incident mutation.
2. Replacement bytes/evidence, original provenance, reservation, and initial
   claim fence are durable before invalid v007 moves.
3. Invalid v007 moves once to the exact archive; v001-v006 remain unchanged.
4. Ordinary claim takeover after v006 exposure is denied with zero mutation.
5. Reservation-aware publication installs receipt-consumed Prime v007
   `NO-ACTION` over exact v006, rejects all v006 governance defects, requests
   corrected independent nonterminal review, and consumes the reservation.
6. Distinct LO publishes a strict-current nonterminal verdict; WI-5370 remains
   open for substantive correction.
7. TEST-11833 records PASS only after every live predicate and exact changed-row
   census is observed.
8. Only two exact bridge paths and exact service rows change; no source/test,
   WI-5638, WI-5764, dispatcher/TAFE, Git/index, timer, project, credential,
   release, or unrelated work is absorbed.

## Risks And Rollback

- Dependency, authority, tuple, claim, or physical-state drift stops before
  mutation and returns the proposal to revision.
- No move occurs before durable bytes/evidence and reservation/claim-fence
  readback. Ambiguity uses typed recovery, never blind retry.
- Before reservation there is nothing to undo. After reservation, append-only
  abort/recovery evidence remains. After replacement, corrections move forward
  through later versions; invalid evidence is never restored as authority.

## Candidate Pre-Filing Gates

Exact candidate applicability, mandatory clause, credential, pattern,
collision, duplicate-thread, citation, project/PAUTH, claim, target, and writer
compliance checks must pass. Filing requires v001 absence, exact victim bytes,
null WI-5915 claim, governed draft claim, receipt-consumed publication, claim
release, canonical readback, and no pending sidecar.

## Files Expected To Change

- `bridge/gtkb-wi5370-terminal-archive-pilot-execution-007.md`
- `bridge/cleanup-evidence/wi5915-invalid-pb-verified-007-20260801/gtkb-wi5370-terminal-archive-pilot-execution-007.md.invalid-pb-verified`
- `groundtruth.db` through exact governed service rows only

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
