NEW
::init gtkb pb
::open build

# WI-5908 — Repair the WI-5625 invalid Prime-authored terminal without erasing evidence

bridge_kind: prime_proposal
Document: gtkb-wi5908-wi5625-invalid-terminal-chain-repair
Version: 001
Date: 2026-08-01 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ordinary per-WI PB authority only; former CF-10 all-program serialization authority rescinded; dispatcher and TAFE deliberately disabled
author_metadata_source: task-local interactive transcript, CODEX_INTERNAL_ORIGINATOR_OVERRIDE, and open per-session envelope

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5908
Related Work Items: WI-5625, WI-5806, WI-5825, WI-5881, WI-5889, WI-5899, WI-5909

target_paths: ["bridge/gtkb-wi5625-canonical-provider-verdict-status-007.md", "bridge/cleanup-evidence/wi5625-invalid-pb-verified-007-20260801/gtkb-wi5625-canonical-provider-verdict-status-007.md.invalid-pb-verified", "groundtruth.db"]

implementation_scope: service_owned_metadata_and_evidence_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

## Purpose And Exact Scope

WI-5908 repairs one exact strict-invalid bridge generation without erasing its
bytes, rewriting history, or absorbing generic recovery behavior. Physical
`bridge/gtkb-wi5625-canonical-provider-verdict-status-007.md` begins with
`VERIFIED`, but its explicit role envelope and author identity are Prime
Builder. The canonical strict lifecycle resolver therefore rejects the thread
with `WRONG_STATUS_AUTHOR_ROLE`; WI-5625 is not genuinely terminal.

The incident has exactly three targets: the invalid live v007, its declared
in-root cleanup-evidence archive, and exact service-owned incident rows in
`groundtruth.db`. It does not change WI-5625's original writer source or test,
does not implement any recovery primitive, and does not activate or mutate the
dispatcher or TAFE.

## Why Versions 005 And 006 Require A Corrective Nonterminal Head

- V003 was a substantive two-target Prime proposal for
  `scripts/gtkb_bridge_writer.py` and
  `platform_tests/scripts/test_gtkb_bridge_writer.py`.
- V004 was a Loyal Opposition `GO` for that implementation, with explicit
  implementation conditions and the same two targets.
- V005 did not implement or report that approved source/test work. Instead it
  used Prime `NO-ACTION` to relabel the executable GO as a carrier-only routing
  verdict. `NO-ACTION` may reject a governance-invalid Loyal Opposition
  response; it cannot discard a valid substantive GO or close the work.
- V006 then issued Loyal Opposition `GO` for a targetless “disposition-close.”
  That accepts v005's incorrect semantics and expressly routes the still-open
  implementation elsewhere without identifying a governed successor.
- V007 compounded the defect by having Prime Builder author the Loyal
  Opposition-only `VERIFIED` status while accurately disclosing its Prime
  role.

The incident repair therefore replaces only physical v007 with a Prime
`NO-ACTION` responding exactly to v006. The replacement rejects v006's
governance-invalid acceptance of v005 and directs a distinct Loyal Opposition
session to append v008 `NO-GO`, responding exactly to the receipt-consumed
replacement v007. WI-5625 remains open. The preferred substantive continuation
is same-thread v009 `REVISED` after corrective v008. A separately named
by-reference successor is permitted only if independent governance names it as
the sole controller, records collision/supersession disposition, and prevents
duplicate implementation routes.

## Exact Incident Binding

The durable reservation and every later operation bind this immutable tuple:

- victim document: `gtkb-wi5625-canonical-provider-verdict-status`;
- invalid live path/version:
  `bridge/gtkb-wi5625-canonical-provider-verdict-status-007.md` / `7`;
- invalid byte size and SHA-256: `1809` /
  `165A964DE3A58C48A4F3BF33A4CF51835D9426ABB63528A1288FB5C5264E057E`;
- invalid first-line status and author role: `VERIFIED` / `prime-builder`;
- invalid author/session: `prime-builder/goose/G` /
  `G-2026-07-31T19-28-58Z`;
- archive path:
  `bridge/cleanup-evidence/wi5625-invalid-pb-verified-007-20260801/gtkb-wi5625-canonical-provider-verdict-status-007.md.invalid-pb-verified`;
- predecessor v006 path/SHA-256:
  `bridge/gtkb-wi5625-canonical-provider-verdict-status-006.md` /
  `D2FC69E7F182BE3CF67D5EAB0E8F2D21202B564297591908FBC970C1CF74B747`;
- prior v005 path/SHA-256:
  `bridge/gtkb-wi5625-canonical-provider-verdict-status-005.md` /
  `8013C66EA36400E81BFB88CBDC1D2DFC55BC227A32E7E6446E5588AB39A4395E`;
- replacement path/version/status: the same live v007 path, version 7, Prime
  `NO-ACTION` responding exactly to v006;
- consumer authority: WI-5908, the exact active project/PAUTH named above,
  its future current independent GO, exact claims, and schema-v3 start packet;
- generic dependencies: exact independently VERIFIED and receipt-complete
  WI-5881 and WI-5825 implementation reports/verdicts and their required race,
  crash, reservation, capability, and receipt evidence;
- archived-victim provenance: the invalid v007 keeps
  `prime-builder/goose/G` / `G-2026-07-31T19-28-58Z` only as immutable
  historical evidence at the archive and in recovery events;
- replacement payload: exact normalized candidate bytes, byte size,
  content/compliance/resource-bound digests, and the eligible Prime session
  that actually authored and reserved the replacement `NO-ACTION`, all
  committed durably before invalid-origin loss;
- recovery invocation: current invoker identity, WI-5908 claim, victim
  claim-fence epoch, schema-v3 packet, capability, and receipt, recorded
  separately from both archived-victim provenance and replacement-candidate
  author/session metadata. A later recovery invoker may differ only through
  WI-5881's independently VERIFIED resume contract.

Any tuple, physical state, authority, role, dependency, claim-fence,
capability, receipt, or candidate-byte drift fails closed before the next
operation.

## Preserved Historical Evidence

Versions 001 through 006 remain byte-for-byte unchanged:

| Version | Status | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| 001 | NEW | `7B7729F843DBD62DE3BB2C3B813693EA17CF0CD25068E903DDC2CC54CBF2EB56` | 11654 |
| 002 | NO-GO | `4068F2EC19D133DA122B2FACF94CE4E5DD9CCC6734367516D48227C077696A0F` | 8998 |
| 003 | REVISED | `9C9C61B2BCEA2377B21936DCA4557F98D2282F7660741B10D4D9B884DBA79D2E` | 15330 |
| 004 | GO | `D1AC4586BC79283C78BA365FA8B3EA8457C7C4FC5DF05FEACEFA98B1BCFA94E9` | 9014 |
| 005 | NO-ACTION | `8013C66EA36400E81BFB88CBDC1D2DFC55BC227A32E7E6446E5588AB39A4395E` | 890 |
| 006 | GO | `D2FC69E7F182BE3CF67D5EAB0E8F2D21202B564297591908FBC970C1CF74B747` | 2308 |

At candidate preparation, invalid v007 is present and untracked at the exact
hash above; the archive and this proposal's live v001 are absent; the victim
and WI-5908 claims are null. No victim, archive, source, test, database,
registry, claim, capability, receipt, Git, dispatcher, or TAFE state is
changed by preparing this proposal.

## Work Item, Project, And Operation-Time Authority

- WI-5908 is P0, open/backlogged, origin `defect`, active direct project
  member, and linked to TEST-11826 in PHASE-002.
- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is active.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  is active v2, unexpired, and list-free. It allows bridge, metadata, and
  governance-evidence mutation classes while forbidding dispatcher mutation,
  external-system mutation, credential lifecycle, push, history rewrite,
  deployment, release, and destructive cleanup.
- Legacy `work_item.approval_state` is not authority. Every later operation
  must re-evaluate exact active membership and the named PAUTH.

The PAUTH does not waive independent GO, exact claim, schema-v3 start,
protected-path enforcement, governed service APIs, factual reporting, or
independent verification.

## Dependency Gate And Structured-Metadata Limitation

- WI-5881's physical head is v005 `REVISED`, SHA-256
  `B36E0146371D91F8BA9C430DDBF61D2C0B7F055A7BA027B34F61273813C30569`.
  It is recovery-held and not independently VERIFIED.
- WI-5825's physical head is v006 `GO`, SHA-256
  `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`.
  It is a non-executable dependency hold and not independently VERIFIED.
- WI-5899 is open with no bridge implementation. The governed expected-version
  CAS surface for replacing `depends_on_work_items` does not yet exist, so
  WI-5908's current structured dependency field remains null. This proposal
  does not bypass that gap with raw SQLite or a one-off writer.

WI-5908 remains implementation-disarmed until WI-5899 is independently
VERIFIED and its governed CAS surface has atomically set the current WI-5908
dependency postimage to exactly `["WI-5881","WI-5825"]`, and until WI-5881
and WI-5825 themselves are independently VERIFIED and receipt-complete. The
proposal text is not a substitute for that future canonical dependency row.
The prerequisite dependency-row mutation belongs solely to WI-5899 and
requires its own exact expected-current-version CAS and current-authority
readback. WI-5908 performs no approval-evidence work and creates or writes no
formal-artifact approval packet; this proposal or a later GO is not mutation
authority for the prerequisite row.

## Governed Incident Execution

Only after every dependency and metadata precondition is canonically true:

1. Re-read WI-5908, WI-5625, TEST-11826, exact project/PAUTH, victim lifecycle,
   hashes, archive absence, dependency reports/verdicts, capability/receipt
   state, current claims/start packets, and exact row/path overlaps.
2. Acquire WI-5908's fresh exact `go_implementation` claim and finalize a
   fresh schema-v3 start packet for all three targets. Bind the victim only
   through the independently VERIFIED WI-5881 reservation/claim-fence API.
3. Normalize and compliance-audit the exact role-correct replacement v007.
   Atomically commit and read back its bytes, size, content/compliance/resource
   digests, eligible replacement-candidate author/session, archived-victim
   provenance, reservation tuple, and initial victim claim fence before moving
   any physical byte.
4. Move invalid v007 exactly once to the archive with no-overwrite semantics
   and read back its exact SHA-256. Resume after crash only from a typed,
   exact, recognized physical state.
5. From a separate eligible Prime session, attempt ordinary victim claim
   takeover after v006 becomes visible. Require typed reservation denial and
   zero claim/event/file/capability/receipt mutation.
6. Through the reservation-aware transition, publish only the durably stored
   replacement bytes as Prime `NO-ACTION` responding to v006. Preserve the
   archived-victim provenance separately; attribute the replacement to the
   eligible Prime session that created and reserved its exact bytes; and record
   any later recovery invoker, claim, packet, and claim-fence epoch separately.
   Ordinary author-session equals claim-session enforcement remains unchanged
   outside WI-5881's explicit resume contract.
7. If publication crashes or becomes ambiguous, use only WI-5825's verified
   recovery/readback path. Never blind-retry a numbered version.
8. Require a distinct Loyal Opposition session to publish receipt-consumed
   v008 `NO-GO` responding exactly to the replacement v007, prove the victim
   thread strict-valid and current, keep WI-5625 open, and direct same-thread
   v009 `REVISED` as the default substantive rebaseline. This incident carrier
   is not verification of WI-5625's original implementation.
9. Record TEST-11826 only after every predicate is observed. File a factual
   WI-5908 implementation report and route it to an unrelated Loyal Opposition
   session for independent terminal verification. The independent finalizer
   may create only the exact locally scoped commit authorized by its terminal
   packet; it must exclude `groundtruth.db` and every foreign worktree path,
   and may not push or rewrite history.

## Service-Owned Database Boundary And Parallelism

`groundtruth.db` is a shared service-owned SoT, not a whole-file checkout
target. WI-5908 may mutate only its exact reservation/event, victim claim,
replacement capability/receipt, registry observation, WI-5908, TEST-11826,
and WI-5625 rows through governed APIs and short row-level transactions/CAS.
It does not hash-bind or globally lock the database.

Immediately before implementation, cross-claim and schema-v3 gates must prove
that no current claim or packet reserves either bridge path. Current
implementation authorization treats `groundtruth.db` as one path-wide target,
not as independently claimable row cohorts. Until WI-5909's governed logical
resource reservations are independently VERIFIED and adopted by every packet,
claim, start, and dispatcher consumer, WI-5908 start therefore requires zero
other active packet or claim containing `groundtruth.db`. The proposal does
not pretend that current machinery admits unrelated claimed DB work in
parallel.

This temporary current-system exclusion is a disclosed start constraint, not
a new global leader or repository lock. WI-5909 owns replacement with bounded
row-cohort reservations so disjoint governed service work can proceed in
parallel. Validation and candidate preparation that create no claim or packet,
unrelated non-DB claims, and unrelated publications remain parallel.

## Ownership Separation

- WI-5881 owns generic durable candidate/reservation bytes and evidence,
  event journal, claim fencing, fresh-session resume, and reservation-aware
  publication mint.
- WI-5825 owns existing-file receipt backfill, compensated publication
  recovery, exact-byte republish, and durable capability-row fallback.
- WI-5899 owns the generic governed CAS dependency-update/readiness surface.
- WI-5909 owns logical row-cohort packet/claim reservations that replace the
  current path-wide `groundtruth.db` collision without weakening true overlap
  exclusion.
- WI-5889 owns proposal-time rejection of structurally impossible declared
  lifecycles.
- WI-5908 owns only this exact invalid v007, exact archive, and exact
  service-managed incident rows.
- A later strict-valid WI-5625 substantive recovery owns the original writer
  source/test behavior. Those files are outside this proposal.

No dependency source/test behavior is copied, amended, or attributed to
WI-5908.

## Timers, Retries, And Resource Bounds

All waits, retries, lock bounds, claim TTLs, throttles, fan-out, and concurrency
limits must come from the operational-control configuration foundation and
Timer Governance program after those surfaces are governed and available.
Until then, operators use generous bounded waits and typed current-state
rechecks under the owner's timer-tolerance direction. WI-5908 introduces no
hard-coded timer, sleep, cap, throttle, retry loop, or global coordinator.

Candidate normalization and compliance checks are bounded by the verified
generic recovery contracts. Oversized, malformed, non-UTF-8, noncompliant, or
drifted replacement bytes fail closed before origin loss.

## Requirement Sufficiency

Existing requirements sufficient.

The cited bridge-authority, session-role, claim-document, project-authorization,
freshness, deterministic-service, and specification-derived-verification
requirements already define the incident correction. WI-5908 introduces no
new product behavior or generic recovery primitive: it consumes the exact
independently VERIFIED contracts eventually landed by WI-5881, WI-5825, and
WI-5899. If any landed prerequisite changes the assumed reservation, receipt,
or dependency-readiness contract, this proposal becomes inapplicable and must
be revised before implementation rather than silently extending authority.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — strict role/status authority, governed
  publication, independent review, and forward-only correction.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — replacement v007 is a Prime
  nonterminal correction and cannot close WI-5625.
- `DCL-SESSION-ROLE-RESOLUTION-001` — archived-victim role,
  replacement-candidate author role, current recovery-invoker role, and
  reviewer role are independently resolved and fail closed.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` — the
  current exact document and session control claim eligibility; recovery does
  not relax ordinary author-session/claim-session equality.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every claim, capability, receipt,
  registry, work-item, and test decision uses canonical current state.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — the recovery is
  a deterministic service workflow, not a conversation-only procedure.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — exact current
  membership/PAUTH are evaluated for each operation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — project and
  concrete specification links are mandatory.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent terminal
  verification derives from mapped predicates, not the status token alone.
- `GOV-ARTIFACT-APPROVAL-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the incident and its decisions stay
  durable and forward-only.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all live and evidence paths stay
  within `E:/GT-KB`.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the correction preserves
  unrelated work, concurrency, ordinary claims, and current operator flows.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex uses the governed helper and
  explicit fallback checks; it does not assume Claude-only hook coverage.
- `GOV-STANDING-BACKLOG-001` — WI-5908 and TEST-11826 preserve the derived
  defect before implementation.

## Specification-Derived Verification

| Requirement | Test or evidence | Acceptance predicate |
| --- | --- | --- |
| Role-correct bridge lifecycle | Strict resolver on exact replacement v007 and independent v008 | v007 is Prime `NO-ACTION`; v008 is unrelated-LO `NO-GO`; no `WRONG_STATUS_AUTHOR_ROLE` |
| Invalid-byte preservation | Archive readback and reservation/event evidence | archive equals exact 1809-byte SHA-256 and v001-v006 hashes are unchanged |
| Durable reservation and claim fence | Independently VERIFIED WI-5881 race/crash evidence plus exact incident interleaving | ordinary takeover is denied after move; only exact reserved recovery proceeds |
| Publication receipt recovery | Independently VERIFIED WI-5825 evidence plus exact v007 capability/receipt | no blind retry; exact replacement receipt consumes the reservation |
| Dependency readiness | WI-5899 governed CAS readback | WI-5908 dependency postimage is exactly WI-5881/WI-5825 and both evaluate ready |
| Bounded incident scope | target inventory, service event/row audit, and Git/worktree readback | only three declared targets/exact rows change; original source/test and unrelated state are unchanged |
| Nonterminal parent disposition | WI-5625 and victim-thread readback | WI-5625 remains open and requires a fresh substantive proposal |
| Finalization and external non-mutation | terminal packet, exact local commit inventory, `KB Mutations Applied (Governed CLI; Committed By DB Sweep)` report section, service revision/receipt readback, before/after state, and path-scoped diff | PB performs no manual Git/index action; independent finalizer commits only its exact verified bridge cohort, excludes DB/foreign paths, and performs no push, history rewrite, dispatcher/TAFE, deployment, or release mutation; DB snapshot finalization remains a separate governed sweep |

TEST-11826 is recorded only through the governed test-result service after all
predicates pass. The WI-5908 implementation report must provide executed
commands, exact report/verdict hashes, exact capability/receipt/reservation
identities, race/crash results, before/after row inventory, and path hashes.

## Acceptance Criteria

1. Every byte of v001-v006 is unchanged.
2. The exact invalid v007 is preserved once at the declared archive and its
   immutable reservation/event chain binds the stated tuple.
3. Live v007 is a receipt-consumed Prime `NO-ACTION` rejecting v006's
   governance-invalid acceptance of v005 and responding exactly to v006.
4. An unrelated Loyal Opposition session publishes receipt-consumed v008
   `NO-GO`; strict resolution succeeds and WI-5625 remains open.
5. WI-5881, WI-5825, and WI-5899 prerequisites are independently terminal and
   their exact landed contracts are used rather than reimplemented.
6. TEST-11826 passes with exact claim-fence, crash/recovery, receipt, archive,
   role, currentness, and nonimpairment evidence.
7. No original WI-5625 source/test, unrelated row/path, dispatcher/TAFE,
   credential, deployment, release, push, history rewrite, or
   destructive-cleanup mutation occurs. Prime Builder performs no manual
   Git/index operation; the independent finalizer may create only the exact
   authorized local commit and must exclude `groundtruth.db` and foreign paths.
8. WI-5908's factual report receives independent Loyal Opposition terminal
   verification before this incident is treated as complete.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5908; TEST-11826; WI-5625 versions 001 through 007; WI-5881; WI-5825; WI-5899; WI-5909",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, DCL-SESSION-ROLE-RESOLUTION-001, SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001, and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Independent GO, exact go_implementation claim, fresh schema-v3 start packet, verified WI-5881/WI-5825 recovery services, factual implementation report, and independent terminal review",
  "before_behavior": "WI-5625 has an invalid Prime-authored VERIFIED v007 that strict resolution rejects while its earlier substantive proposal remains unresolved.",
  "after_behavior": "The exact invalid bytes are durably preserved, live v007 is a role-correct Prime NO-ACTION, an unrelated Loyal Opposition v008 records NO-GO, and WI-5625 remains open for a fresh substantive proposal.",
  "self_descriptive_naming": "The WI, test, bridge slug, archive directory, archive filename, and service evidence all name WI-5908 and the WI-5625 invalid-terminal incident.",
  "obsolete_guidance_disposition": "The invalid v007 and governance-invalid v005/v006 interpretation remain preserved as history but cannot authorize or evidence terminal WI-5625 completion.",
  "history_preservation": "Versions 001 through 006 remain byte-identical; the invalid v007's exact bytes and provenance remain byte-identical in the declared archive and evidence chain before live v007 is replaced; later corrections are append-only.",
  "baseline": {
    "wi_5625_bridge_head": "physical v007 VERIFIED with Prime Builder author metadata and strict WRONG_STATUS_AUTHOR_ROLE",
    "archive": "declared archive absent before governed recovery",
    "parent_disposition": "WI-5625 remains substantively open",
    "parallelism": "unrelated bridge and non-database work remains parallel; current groundtruth.db path-wide exclusion is temporary and assigned to WI-5909"
  },
  "expected_result": {
    "live_v007": "receipt-consumed Prime NO-ACTION",
    "independent_v008": "receipt-consumed Loyal Opposition NO-GO",
    "test_11826": "passes all role, preservation, reservation, receipt, dependency, currentness, and nonimpairment predicates",
    "dispatcher": "legacy dispatcher and TAFE remain quiesced and unchanged"
  },
  "rollback": "Before origin movement, failure leaves all targets untouched; after reservation or movement, only the typed WI-5881/WI-5825 state machine may resume the exact tuple; semantic correction appends a higher bridge version.",
  "hard_invariants": [
    "No original WI-5625 source or test mutation",
    "No byte change to WI-5625 versions 001 through 006",
    "No Prime Builder GO, NO-GO, or VERIFIED authorship",
    "No raw SQLite, manual Git/index, dispatcher, TAFE, push, history rewrite, deployment, release, or unrelated cleanup mutation",
    "Independent finalization excludes groundtruth.db and foreign paths from the exact local commit cohort"
  ],
  "fail_closed_conditions": [
    "WI-5881, WI-5825, or WI-5899 is not independently terminal and applicable",
    "Exact victim bytes, size, author/session metadata, claim/owner epoch, or reservation evidence drifts",
    "An overlapping claim, packet, capability, receipt, archive, or live replacement already exists",
    "Current project membership or PAUTH does not allow every declared target and operation",
    "The replacement candidate or independent verdict fails strict role, status, currentness, compliance, or receipt validation"
  ],
  "essential_context_preservation": "The archived victim keeps exact bytes and original authorship provenance; the live replacement separately records its Prime author, current recovery invoker, claim, owner epoch, capability, receipt, and independent reviewer without conflating those identities."
}
```

## Rollback And Failure Recovery

There is no destructive rollback. Before the invalid origin moves, failure
leaves every target untouched. After reservation or move, only the typed
WI-5881/WI-5825 recovery state machine may resume the exact tuple. No operator
deletes the archive, sidecar, capability, receipt, claim, event, or live file;
no raw database repair, lock deletion, blind retry, history rewrite, or
unrelated cleanup is permitted. Later semantic corrections append a higher
numbered bridge version.

## Database Finalization Disposition

The factual implementation report must include an exact
`## KB Mutations Applied (Governed CLI; Committed By DB Sweep)` section. It
must enumerate the governed CLI/service operations, exact affected logical
rows, before/after versions and digests, reservation/capability/receipt event
identities, commands, timestamps, and independent readback. As established by
the independently VERIFIED dispatcher-portfolio reconciliation precedent,
that section removes `groundtruth.db` from this bridge thread's local
finalization commit cohort without pretending the database mutation is absent.

The independent finalizer may stage and commit only the exact verified bridge
and cleanup-evidence files named by its terminal packet. It must not stage
`groundtruth.db` or any foreign path. The database carrier is finalized later
by the normal separately governed DB sweep, or by a separate exact-target
authorization if a dedicated snapshot commit is required. The DB-sweep route
must preserve concurrent rows and must not restore, replace, or rewrite the
live carrier. No by-reference waiver is claimed by this proposal.

## Owner Decisions And Input

No new owner input is required for this proposal. The owner-directed
Dispatcher Next goal requires all derived blockers to become genuinely
terminal and explicitly forbids Prime Builder from authoring `VERIFIED`.
`DELIB-202667724` and `DELIB-202667732` provide the current Bridge Protocol
Reliability whole-project authorization while preserving all ordinary gates.
The owner also requires high parallelism without a global MemBase leader and
generous evidence-based timer handling; this design follows both constraints.

## Pre-Filing Preflight

Before governed publication, Prime Builder must revalidate exact hashes,
absence/presence, current WI/test/project/PAUTH state, current claims and
packets, strict lifecycle error, cross-claim collision, proposal pattern,
credential/compliance scan, candidate applicability, mandatory clauses, and
independent Prime design audit. Publication uses only the governed writer and
must produce a consumed receipt. A failed or ambiguous publication is retained
for governed recovery and is never blindly retried.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
