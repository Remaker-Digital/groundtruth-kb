NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; non-live incident-consumer proposal draft; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5898-wi5741-invalid-terminal-chain-repair
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5898
Related Work Items: WI-5741, WI-5718, WI-5825, WI-5858, WI-5879, WI-5881

target_paths: ["bridge/gtkb-wi5741-spec-packet-postimage-completeness-009.md", "bridge/cleanup-evidence/wi5741-invalid-pb-verified-009-20260801/gtkb-wi5741-spec-packet-postimage-completeness-009.md.invalid-pb-verified", "groundtruth.db"]
implementation_scope: service_owned_metadata_and_evidence_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

# NEW Incident-Consumer Proposal — WI-5741 Invalid-Terminal Chain Repair

## Purpose And Scope

WI-5898 repairs one exact strict-invalid bridge generation without erasing its
bytes or absorbing generic recovery behavior. Physical
`bridge/gtkb-wi5741-spec-packet-postimage-completeness-009.md` begins with
`VERIFIED` but carries a Prime Builder author envelope. The strict lifecycle
resolver therefore fails with `WRONG_STATUS_AUTHOR_ROLE` and cannot treat
WI-5741 as terminal.

This proposal is limited to three targets: the exact invalid live v009, its
declared cleanup-evidence archive, and exact service-owned incident rows in
`groundtruth.db`. It does not reopen or implement WI-5741's seven source/test
targets. It does not implement any generic reservation, claim-fence,
publication-recovery, or receipt-backfill behavior owned by WI-5881/WI-5825.

## Why Versions 007 And 008 Require A Corrective Nonterminal Head

- Version 006 was a lawful independent `NO-GO`: the then-current PAUTH did not
  authorize the complete atomic terminal transaction. A later owner approval
  could unblock a corrected report, but it did not retroactively make v006 a
  governance-noncompliant verdict.
- Version 007 used Prime `NO-ACTION` to announce that the blocker had been
  resolved, while also stating that PAUTH creation and terminal action still
  had to occur. `NO-ACTION` is reserved for rejecting a governance-invalid
  Loyal Opposition verdict and must identify the required reviewer correction;
  it is not a disposition-close or a substitute for a corrected substantive
  report.
- Version 008 then issued `GO` for a targetless "disposition-close" and routed
  the pending implemented seven-target work to an unspecified future cycle.
  That accepts the wrong v007 semantics and does not supply the required
  substantive report, spec-derived execution evidence, or atomic terminal
  verification.
- Version 009 compounded the defect by having Prime Builder self-author the
  Loyal Opposition-only `VERIFIED` status while expressly acknowledging that
  role restriction.

The incident repair therefore replaces only physical v009 with a Prime-authored
`NO-ACTION` responding exactly to v008. The replacement must reject v008's
acceptance of v007 and direct a distinct Loyal Opposition session to publish
v010 `NO-GO`. WI-5741 remains open. Its substantive seven-target work continues
only through a fresh by-reference proposal under a new slug, current PAUTH,
independent GO, exact claim/start, factual report, spec-derived execution, and
independent terminal verification. WI-5718 remains blocked until that separate
substantive cycle is genuinely terminal.

## Exact Incident Binding

The reservation and every later recovery operation bind this immutable tuple:

- victim document: `gtkb-wi5741-spec-packet-postimage-completeness`;
- invalid live path/version: `bridge/gtkb-wi5741-spec-packet-postimage-completeness-009.md`
  / `9`;
- invalid content SHA-256:
  `53C59AFC7B8E791CD1A3AF225A1AA06F9BAD29600442B71E840BBC3BA3A78C1C`;
- invalid first-line status and author role: `VERIFIED` / `prime-builder`;
- archive path:
  `bridge/cleanup-evidence/wi5741-invalid-pb-verified-009-20260801/gtkb-wi5741-spec-packet-postimage-completeness-009.md.invalid-pb-verified`;
- exact predecessor path/SHA-256:
  `bridge/gtkb-wi5741-spec-packet-postimage-completeness-008.md` /
  `08EC394D374E2AE7277BCF29A5861C0E912B865092A70AEA2160230F89D7EEA2`;
- exact v007 path/SHA-256:
  `bridge/gtkb-wi5741-spec-packet-postimage-completeness-007.md` /
  `047D425B8910838B3AA03C6B6AF02E2FE7DDE479630722960EA38EFD8AF3DC2D`;
- replacement path/version/status: the same live v009 path, version 9, Prime
  `NO-ACTION` responding exactly to v008;
- consumer authority: WI-5898, active Bridge Protocol Reliability PAUTH v2,
  its future current independent GO, exact claims, and schema-v3 start packet;
- dependencies: exact independently VERIFIED WI-5881 and WI-5825
  report/verdict identities and executed TEST-11809/recovery evidence;
- replacement payload: exact normalized candidate bytes, byte size,
  content/compliance/resource-bound digests, and original Prime author/session
  metadata, durably committed before invalid-origin loss;
- recovery invocation: current recovery invoker identity, WI-5898 claim,
  victim claim-fence epoch, start packet, capability, and receipt, separately
  recorded from preserved original-author metadata.

Any tuple, physical-state, role, authority, dependency, claim-fence,
capability, or receipt drift fails closed before the next operation.

## Preserved Predecessor Evidence

Versions 001 through 008 must remain byte-for-byte unchanged:

| Version | Status | SHA-256 |
|---|---|---|
| 001 | NEW | `E2FBF7C7896FC801701D305594533DED6F32E110730411F5D250BCE056D5A8D4` |
| 002 | NO-GO | `67350850DB2AD9A9786DBC90D089B00EE97F75D6610595BF35ACCFE20D1F7045` |
| 003 | REVISED | `775D6D80D88E4EF1FFE6C2CF4C1EAE66B72A12BABB89B228F57B73E3CA2DE04B` |
| 004 | GO | `40E1DE97B56E59C9972ADE2FD0842352A1CD60889CC80DC2FE3095A4320F5028` |
| 005 | NEW | `1A30DCB6A56F32A25324D399196A472652DDE9424143B484688A5A9DF61D81C6` |
| 006 | NO-GO | `BB45FDFBAF8000FB0FF0D2D2F68308125DE7951EBF6E30F856531BC3F26DE53F` |
| 007 | NO-ACTION | `047D425B8910838B3AA03C6B6AF02E2FE7DDE479630722960EA38EFD8AF3DC2D` |
| 008 | GO | `08EC394D374E2AE7277BCF29A5861C0E912B865092A70AEA2160230F89D7EEA2` |

The current invalid v009 is 4,328 bytes and matches the exact WI-5898 and
TEST-11817 digest. The declared archive and this proposal's live v001 thread
are absent at candidate preparation. The incident claim is null. No live,
archive, registry, claim, capability, receipt, work-item, test, source, Git, or
dispatcher/TAFE state is changed by this draft.

## Current Work-Item, Project, And PAUTH Authority

- WI-5898 is version 2, P0, open/backlogged, origin `defect`, source test
  TEST-11817, and explicitly depends on WI-5881 and WI-5825.
- WI-5898 is an active direct member of
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`. That project is active.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  is active v2, unexpired, list-free, and allows bridge, metadata, and
  governance-evidence mutation classes while forbidding dispatcher mutation,
  external mutation, credential lifecycle, push, history rewrite, deployment,
  release, and destructive cleanup.
- A later compatibility backfill also created an active membership in
  `PROJECT-BRIDGE-PROTOCOL-RELIABILITY`, which has no authorization. It does
  not replace or broaden the exact project and PAUTH named in this proposal.
  Every operation-time check must bind the exact header project, PAUTH, and
  active direct membership above; ambiguity or membership drift fails closed.
- Legacy `work_item.approval_state` is not operation-time authority. The active
  exact project membership and current list-free project PAUTH control.

The PAUTH does not waive independent GO, exact work-intent claims, schema-v3
implementation start, exact target enforcement, governed service APIs,
factual reporting, or independent verification.

## Dependency Gate And Precedent

- WI-5881's physical strict-valid head is v005 `REVISED`, SHA-256
  `B36E0146371D91F8BA9C430DDBF61D2C0B7F055A7BA027B34F61273813C30569`.
  It is not independently VERIFIED and cannot yet supply the generic durable
  candidate-byte reservation, claim fence, fresh-owner recovery, event journal,
  or reservation-aware publication-mint contract.
- WI-5825's physical strict-valid head is v006 `GO`, SHA-256
  `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`.
  It is not independently VERIFIED and cannot yet supply durable capability
  recovery, exact-byte republish, or receipt back-fill.
- WI-5879 v005 `REVISED`, SHA-256
  `E91CB0A7467C068AD81C0D2D95A2E5D92DA43439379D5DBB377B22A7AC752EE4`,
  is the governed incident-consumer precedent. WI-5898 uses the same three-
  target split and dependency ordering for a different immutable victim; it
  does not share or mutate WI-5879's victim paths or incident rows.

WI-5898 must remain implementation-disarmed until WI-5881 and WI-5825 each
have a factual report, distinct-session independent `VERIFIED`, current exact
hashes, closed claims/start packets, and clean shared implementation targets.
Proposal existence or `GO` alone is insufficient.

## Governed Incident Execution

Only after both dependencies are independently VERIFIED and all preconditions
are freshly revalidated:

1. Re-read WI-5898, WI-5741, TEST-11817, exact project/PAUTH, victim lifecycle,
   all hashes, archive absence, dependency reports/verdicts, capability/receipt
   state, current claims/start packets, and exact row/path overlaps.
2. Acquire WI-5898's fresh exact `go_implementation` claim and schema-v3 start
   packet. Bind the victim only through the independently VERIFIED WI-5881
   reservation/claim-fence operation; do not use ordinary claim takeover.
3. Normalize and compliance-audit the exact role-correct replacement v009,
   then atomically commit and canonically read back its exact bytes, byte size,
   content/compliance/resource-bound digests, original-author metadata,
   immutable reservation, and initial victim claim fence before moving any
   physical byte.
4. Move invalid v009 once to the exact archive with no-overwrite semantics and
   read back SHA-256
   `53C59AFC7B8E791CD1A3AF225A1AA06F9BAD29600442B71E840BBC3BA3A78C1C`.
   A crash may resume only from a typed, exact recognized physical state.
5. From a separate eligible Prime session, attempt ordinary victim claim
   takeover after v008 becomes visible. Require typed reservation denial and
   zero claim/event/file/capability/receipt mutation.
6. Through the reservation-aware transition, publish only the durably stored
   replacement v009 bytes as Prime `NO-ACTION` responding exactly to v008 and
   explaining the v007/v008 correction. Preserve original author provenance
   while separately recording and validating current invoker, claim, start
   packet, and claim-fence epoch. Ordinary author-session equals claim-session
   enforcement remains unchanged.
7. If publication crashes or is ambiguous, use only the independently VERIFIED
   WI-5825 recovery/readback path. Never blind-retry a numbered version.
8. Require a distinct Loyal Opposition session to publish receipt-consumed
   v010 `NO-GO` and canonically prove the strict lifecycle current and
   role-correct. The verdict must keep WI-5741 open and require the separate
   substantive by-reference cycle; it must not treat this incident carrier as
   implementation verification.
9. Record TEST-11817 only after every expected predicate is observed; then
   file a factual WI-5898 implementation report and route independent
   verification. Do not resume WI-5718 from this incident result alone.

## Service-Owned Database Boundary

`groundtruth.db` is a shared service-owned SoT, not an exclusive whole-file
checkout target. This incident may mutate only exact WI-5881 reservation/event,
victim-claim, replacement-capability/receipt, registry-observation, WI-5898,
TEST-11817, and WI-5741 rows through governed APIs and short row-level
transactions/CAS. It does not hash-bind or lock the whole DB file.

Immediately before implementation, cross-claim and schema-v3 gates must prove
that no current claim or packet reserves either exact bridge path or the same
incident rows. Exact-row/path collision fails closed. Unrelated row operations,
claims, proposals, and publications remain parallel.

## WI-5881, WI-5825, And WI-5898 Separation

- WI-5881 owns generic durable candidate bytes/evidence, reservation schema and
  events, claim fencing, current-invoker resume, claim/control-plane behavior,
  writer mint enforcement, and TEST-11809.
- WI-5825 owns existing-file receipt back-fill, compensated publication
  recovery, exact-byte republish, and durable capability-row fallback.
- WI-5898 owns only the exact invalid live v009, exact archive path, and exact
  service-managed incident rows for the immutable WI-5741 tuple.
- WI-5741's original seven source/test targets remain outside this proposal and
  must be carried by the later fresh substantive by-reference thread.
- WI-5718 remains blocked until WI-5741 is independently terminal through that
  substantive cycle, not merely until this incident consumer is VERIFIED.
- WI-5858 remains the timer/tuning owner. WI-5898 introduces no timer value.

No dependency source/test hunk or generic behavior is copied, amended, or
attributed to WI-5898.

## Timer, Parallelism, Append-Only, And Git Disposition

All waits, retries, lock bounds, claim TTLs, throttles, fan-out, and concurrency
limits come from the centralized configuration SoT owned by Timer Governance.
The incident introduces no hard-coded timer, sleep, repository-wide lock, or
global leader. Only irreducible exact-row reservation/claim/event/CAS
transactions serialize; preparation, validation, unrelated claims, and
unrelated publications remain parallel.

Invalid v009 moves once to the declared in-root evidence archive because the
same numbered live path must hold the role-correct replacement. The archive
digest and append-only recovery events preserve provenance; versions 001
through 008 are never rewritten. Later corrections append higher versions.

No Git operation, index read/write, lock classification/removal, staging,
commit, push, or history rewrite belongs to this incident proposal. The
foreign `.git/index.lock` remains outside scope and untouched. Dispatcher/TAFE
is deliberately disabled for repairs and remains unactivated and unmodified.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — strict role/status authority, governed
  writer, independent review, and forward correction.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — replacement v009 is a Prime
  reviewer-correction response to v008, not a close or implementation verdict.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every reservation, claim, capability,
  receipt, registry, work-item, and test predicate uses current canonical APIs.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` — victim
  claim authority remains bound to the exact reserved document generation.
- `DCL-SESSION-ROLE-RESOLUTION-001` — original author and current recovery
  invoker roles come from exact session envelopes and stay distinct.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active direct
  membership and list-free PAUTH are revalidated at each effect boundary.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project, PAUTH, WI,
  and exact incident targets are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant
  governing link precedes review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11817 maps exact
  live predicates and consumes independently VERIFIED dependency evidence.
- `GOV-ARTIFACT-APPROVAL-001` — project PAUTH does not waive formal record,
  claim, packet, report, or verification gates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — invalid evidence, dependencies,
  results, reports, and review remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5741, WI-5718, WI-5825, WI-5858, WI-5879,
  WI-5881, and WI-5898 retain nonduplicated ownership.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — unrelated DB rows, claims,
  bridge threads, source/tests, and harnesses remain unchanged.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — recovery uses
  landed deterministic services, never session lore or raw SQLite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every live/archive/service SoT
  target stays inside `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — native Windows execution
  self-enforces exact GO/claim/start and governed writer boundaries.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` — persistent
  program completion and independent-review boundary.
- `DELIB-202667724` and `DELIB-202667732` — Bridge Protocol Reliability
  project grant and active v2 list-free repair authority.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` —
  exact row/path CAS and unrelated-worker parallelism, not a global leader.
- `DELIB-202667722` — centralized timer/concurrency configuration.
- `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-005.md` — governed
  three-target incident-consumer and dependency-split precedent.
- `bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-005.md`
  — current generic dependency proposal; its physical presence is not
  implementation or verification.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-006.md`
  — current receipt-recovery dependency GO; GO is not implementation or
  verification.

## Owner Decisions / Input

No new owner decision is requested. WI-5898 is an active direct member of the
active, list-free authorized project. Existing owner direction requires exact
parallel-SoT repair, generous externally configured waits, evidence
preservation, and disabled dispatcher/TAFE. Independent bridge review, current
claims, schema-v3 start, factual reporting, and independent verification remain
mandatory.

## Requirement Sufficiency

Existing requirements sufficient. WI-5898, TEST-11817, the exact physical
v009, strict resolver failure, governing bridge/PAUTH/freshness/testing rules,
the WI-5879 incident precedent, and the two generic dependency contracts fully
determine this repair. No new generic source contract, role, status, timer
policy, or owner choice is needed before independent review.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Independent GO, independently VERIFIED WI-5881 and WI-5825, fresh claims/start, immutable reserved-evidence repair, independent LO v010 NO-GO, TEST-11817 result, factual report, and independent verification.",
  "baseline": {
    "victim": "WI-5741 physical v009 is PB-authored VERIFIED and strict-invalid",
    "invalid_digest": "53C59AFC7B8E791CD1A3AF225A1AA06F9BAD29600442B71E840BBC3BA3A78C1C",
    "predecessor_digest": "08EC394D374E2AE7277BCF29A5861C0E912B865092A70AEA2160230F89D7EEA2",
    "generic_dependency": "WI-5881 v005 REVISED; not independently VERIFIED",
    "receipt_dependency": "WI-5825 v006 GO; not independently VERIFIED",
    "incident_precedent": "WI-5879 v005 REVISED; separate victim tuple"
  },
  "before_behavior": "The physical PB-authored VERIFIED head is strict-invalid, while v007/v008 incorrectly treat a pending substantive implementation as a targetless disposition-close.",
  "after_behavior": "The exact invalid bytes are archived, a receipt-consumed Prime v009 NO-ACTION rejects v007/v008, independent LO v010 NO-GO is strict-current, and WI-5741 remains open for a separately governed substantive cycle.",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, active list-free PAUTH v2, independently VERIFIED WI-5881/WI-5825 contracts, strict bridge chain, governed service rows, and TEST-11817.",
  "essential_context_preservation": "Preserve v001-v008 bytes, exact invalid/archive/replacement hashes, original and current role provenance, claim-fence epoch, capability/receipt identity, WI-5741 open state, seven-target ownership, WI-5718 dependency block, row-level parallelism, and no-dispatcher/TAFE/Git boundary.",
  "obsolete_guidance_disposition": "V007's resolved-blocker NO-ACTION and v008's disposition-close GO are explicitly rejected; generic recovery remains solely WI-5881/WI-5825.",
  "history_preservation": "V001-v008 remain unchanged; invalid v009 bytes are preserved once at the declared archive; reservation/events/receipt/test/report/review evidence is append-only.",
  "provenance": "WI-5898; TEST-11817; WI-5741 v006-v009; WI-5881/TEST-11809; WI-5825; WI-5879 v005; DELIB-202667724; DELIB-202667732; DELIB-202667722; DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT.",
  "self_descriptive_naming": "Use exact WI-5741 victim generation, invalid-evidence archive, reservation-bound claim, role-correct replacement, receipt-bound consumption, and independent nonterminal review.",
  "expected_result": {
    "archive": "one exact invalid-byte artifact at the declared cleanup-evidence path",
    "replacement": "receipt-consumed Prime v009 NO-ACTION over exact v008 rejecting v007/v008",
    "review": "distinct Loyal Opposition session publishes strict-valid current v010 NO-GO",
    "work_item": "WI-5741 remains open and WI-5718 remains blocked pending separate substantive terminal verification",
    "nonimpairment": "v001-v008, seven source/test targets, dispatcher/TAFE, Git/index, and unrelated rows/claims remain unchanged"
  },
  "hard_invariants": [
    "WI-5881 and WI-5825 are independently VERIFIED before incident mutation",
    "Exact normalized candidate bytes, size, compliance/resource evidence, and original author metadata are durable before origin loss",
    "Reservation and initial claim fence are committed and read back before the move",
    "Ordinary claim and publication mint cannot bypass the active reservation",
    "Only the exact replacement receipt consumes the reservation",
    "TEST-11817 is recorded only after current independent v010 and every live predicate",
    "Only exact incident bridge paths and exact service-owned rows change",
    "No seven-target, dispatcher/TAFE, Git/index, timer, global-leader, or raw-SQLite work occurs"
  ],
  "fail_closed_conditions": [
    "Dependency not independently VERIFIED or shared targets/claims not closed",
    "Changed v001-v009/archive/role/status/authority/candidate-byte binding",
    "Ambiguous source/archive state, wrong digest, claim-fence drift, or foreign owner",
    "Missing GO, PAUTH, exact claim, schema-v3 packet, capability, receipt, or independent v010",
    "Exact-row/path collision, compatibility-project ambiguity, or ambiguous publication result"
  ],
  "rollback": {
    "instructions": "Before reservation creation, no incident mutation exists. After reservation, preserve append-only events and use only the governed abort before mint with exact state proof. After replacement publication, correct forward through later numbered versions; never restore invalid VERIFIED bytes as authority.",
    "verification": "Re-run dependency evidence, strict lifecycle, exact hashes, reservation/events/claims/capability/receipt readbacks, foreign takeover denial, WI-5741/TEST-11817/WI-5718 state, exact changed-row census, and source/test/dispatcher/TAFE/Git/index nonimpairment."
  }
}
```

## Specification-Derived Verification Plan

| Requirement | Required executed evidence |
|---|---|
| Generic claim/publication fence | exact independently VERIFIED WI-5881 report/verdict and TEST-11809 results |
| Receipt recovery | exact independently VERIFIED WI-5825 report/verdict and crash-recovery results |
| Immutable tuple | reservation readback binds declared paths, hashes, status/role, authority, and claim-fence epoch before move |
| Durable replacement source | readback before move proves normalized candidate bytes, byte size, content/compliance/resource-bound digests, and original author metadata |
| Author/invoker separation | recovery preserves original author/session and separately validates current invoker/claim/epoch; ordinary equality is unchanged |
| Claim-race denial | a separate Prime ordinary claim after v008 exposure receives typed reserved-generation denial with zero mutation |
| Evidence preservation | archive SHA equals `53C59AFC...A78C1C`; victim v001-v008 hashes equal the table |
| Replacement authority | v009 is Prime `NO-ACTION`, responds exactly to v008, rejects v007/v008, and has an exact consumed capability/receipt |
| Independent review | a distinct LO session publishes receipt-consumed v010 `NO-GO`; strict resolver is valid and current |
| Work-item/test integrity | WI-5741 remains open; TEST-11817 records PASS only from every observed predicate; WI-5718 remains blocked |
| Scope separation | no WI-5741 seven-target or generic WI-5881/WI-5825 source/test change is attributed to WI-5898 |
| Nonimpairment | no dispatcher/TAFE, Git/index, project/PAUTH, foreign claim/packet, or unrelated DB-row mutation |
| Parallelism/timers | unrelated row/slug operations remain concurrent; zero new literal timer/TTL/retry/throttle/leader |

TEST-11817's result packet must record exact dependency report/verdict hashes,
reservation/event/claim-fence identities, v001-v009 and archive/replacement
hashes, foreign-denial evidence, replacement capability/receipt, strict v010
readback, WI-5741 and WI-5718 state, exact changed-row census, seven-target
nonimpairment, and dispatcher/TAFE/Git/index no-touch evidence.

## Acceptance Criteria

1. WI-5881 and WI-5825 are implemented, factually reported, independently
   VERIFIED, and their implementation targets and claims are closed/clean.
2. The exact reservation plus initial claim fence is committed/read back before
   invalid v009 moves, with exact normalized replacement bytes, byte size,
   content/compliance/resource evidence, and original-author metadata.
3. Invalid v009 moves once to the declared archive at exact SHA-256; v001-v008
   remain byte-for-byte unchanged.
4. A separate Prime ordinary claim attempt after v008 becomes head is denied by
   the reservation with zero claim/event/path/capability/receipt mutation.
5. The reservation-aware operation publishes only exact Prime v009 `NO-ACTION`
   over exact v008, expressly rejecting v007/v008; the exact replacement
   receipt consumes the reservation while original author and current invoker
   provenance remain separate and validated.
6. A distinct Loyal Opposition session publishes receipt-consumed v010
   `NO-GO`; strict lifecycle resolution is current and role-correct.
7. WI-5741 remains open, WI-5718 remains blocked, and TEST-11817 records PASS
   only after every exact live predicate is observed.
8. WI-5898 changes no WI-5741 seven-target source/test path and reimplements no
   WI-5881 or WI-5825 generic behavior.
9. Only the two exact bridge paths and exact service-owned incident rows change;
   unrelated DB rows, claims, packets, and slugs remain parallel.
10. A fresh by-reference proposal under a new slug separately governs the
    original seven targets/current PAUTH through independent terminal
    verification before WI-5718 may resume.
11. No hard-coded timer/TTL/retry/throttle/concurrency value, global leader,
    raw SQLite, dispatcher/TAFE, project/PAUTH mutation, credential, Git/index,
    deployment, release, push, history rewrite, or destructive cleanup occurs.

## Risks And Rollback

- **Dependency drift:** any WI-5881/WI-5825 head, report, verdict, target,
  claim, or API drift returns WI-5898 to revision before mutation.
- **Claim takeover:** no move occurs until the generic claim fence is live and
  read back; ordinary post-move takeover is an executed negative test.
- **Shared DB contention:** only exact rows/CAS serialize. Typed contention or
  currentness failure pauses safely; it never triggers raw SQL or blind retry.
- **Ambiguous publication:** use only WI-5825 canonical recovery/readback;
  never publish another numbered file based solely on an exception.
- **Wrong closure:** v010 must be `NO-GO`, WI-5741 must remain open, and WI-5718
  must remain blocked until the separate substantive terminal cycle.
- **Rollback:** before reservation, there is nothing to undo. After reservation,
  preserve events and use governed abort only before mint. After replacement,
  correct forward; invalid evidence remains archived.

## Candidate Pre-Filing Gates

Applicability, mandatory clause, credential/pattern, and writer-compliance
audits must pass against these exact stable candidate bytes. Live filing also
requires physical v001 absence, current WI/test/project/PAUTH/dependency/victim
evidence, exact claim, unchanged three-target tuple, governed writer append,
and canonical status/path/hash/capability/claim-consumption readback. No live
filing or claim is performed by this draft task.

## DISARM — Implementation Boundary

This proposal is completely implementation-disarmed until WI-5881 and WI-5825
are each independently VERIFIED. It authorizes no evidence move, DB row
mutation, claim acquisition/reclassification, reservation, replacement
publication, TEST result, WI status change, source/test edit, Git/index action,
or dispatcher/TAFE operation. Independent GO does not waive the dependency
gate. After dependency closure, fresh exact currentness/overlap checks, claims,
schema-v3 start, service-owned effects, factual report, and independent
verification remain mandatory.

## Files Expected To Change

- `bridge/gtkb-wi5741-spec-packet-postimage-completeness-009.md`
- `bridge/cleanup-evidence/wi5741-invalid-pb-verified-009-20260801/gtkb-wi5741-spec-packet-postimage-completeness-009.md.invalid-pb-verified`
- `groundtruth.db` through exact governed service rows only

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
