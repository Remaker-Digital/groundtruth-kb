NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; owner-directed parallel-SoT repair; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

bridge_kind: prime_proposal
Document: gtkb-wi5881-durable-cross-process-bridge-recovery-reservations
Version: 001
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5881
Related Work Items: WI-5791, WI-5825, WI-5858, WI-5877, WI-5879

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No live KB mutation occurs in this proposal. Tests use isolated temporary stores;
the later WI-5879 incident consumer owns any governed service write to
`groundtruth.db` after this generic contract is independently VERIFIED.

# Implementation Proposal — Durable Cross-Process Bridge Recovery Reservations

## Claim

Implement one generic exact-generation recovery-reservation contract that
atomically fences both work-intent claim takeover and publication-capability
mint before any evidence move. The contract survives process, session, and
ordinary claim expiry; permits a fresh authorized Prime Builder to resume only
the immutable reserved tuple; appends state events; consumes only with the
exact replacement publication receipt; and preserves unrelated-slug
parallelism without a global leader or hard-coded timer.

This is the forward-only successor to falsely terminal WI-5791. WI-5879 becomes
an incident-specific consumer after this contract and WI-5825 are independently
VERIFIED; it does not reimplement any reservation, claim, registry, or writer
primitive.

## Defect And Reproduction

WI-5879 v004 independently proved the decisive interleaving against current
source:

1. A repair worker must claim an invalid victim thread before it moves the
   malformed/role-invalid physical head away.
2. While that invalid head is current, `claim-no-action` is unavailable because
   the visible head is not strict `GO` or `NO-GO`; the repair holds a non-GO
   claim.
3. The move exposes the exact predecessor `GO`.
4. `_can_preempt_lingering_draft` and `_claim_operation` allow a foreign Prime
   Builder's ordinary `go_implementation` acquisition to replace that non-GO
   holder immediately, without waiting for TTL expiry.
5. A reservation that fences only publication mint cannot recover the victim
   claim required by the governed writer, so the evidence move can strand an
   immutable reservation with no eligible claimant.

The existing regression
`platform_tests/scripts/test_bridge_claim_cli.py::test_claim_go_implementation_preempts_lingering_draft_claim`
passes and confirms the ordinary takeover behavior. That behavior remains valid
for unreserved threads; it must be denied only for an active exact-generation
recovery reservation.

WI-5791 and TEST-11758 are preserved as superseded historical evidence. Their
reconciler closure was based on advisory dispositions, not a target-bearing
proposal, implementation report, executable linked-test result, and independent
implementation verification. This proposal does not reopen or rewrite them.

## Proposed Design

### 1. Immutable reservation and append-only state events

Add a narrowly keyed recovery-reservation record and append-only event stream
through the registry control plane. The immutable binding includes:

- document slug, exact missing/replaced version, source and archive paths;
- source digest, replacement path, exact predecessor path and digest;
- required replacement status and author-role class;
- initiating project, PAUTH, work item, bridge proposal, GO, start-packet, and
  reservation-binding digests;
- claim-fence epoch and the exact replacement capability/receipt identities
  when later created.

State derives from ordered events such as `reserved`, `claim_bound`, `moved`,
`publication_minted`, `consumed`, and governed `aborted`; prior rows/events are
never rewritten or deleted. Only one nonterminal reservation may bind an exact
document/version/replacement path. Creation and readback occur before any
filesystem move.

### 2. Atomic claim fence and fresh-session resume

In the work-intent registry, ordinary `draft`, `go_implementation`, and
`no_action_correction` operations consult the active reservation before
preemption or reclassification. For the reserved victim slug they fail with a
typed `ERR_RECOVERY_GENERATION_RESERVED` unless the caller uses the explicit
recovery-resume operation and validates the immutable reservation tuple.

Reservation creation and its initial victim-claim fence are committed in one
short transaction. There is no interval in which the reservation exists but
ordinary claim takeover is still eligible. A fresh Prime Builder session may
resume after process/session loss or bound-claim expiry only by:

1. presenting the exact reservation id and binding digest;
2. proving current active project PAUTH, current reviewed repair authority, and
   a fresh schema-v3 start packet for the consumer WI;
3. proving the same source/archive/replacement/predecessor tuple and physical
   state; and
4. atomically advancing the claim-fence epoch and binding the new exact claim.

An unexpired bound recovery owner denies takeover. An expired or absent bound
owner may be replaced once through the recovery operation, never through the
ordinary claim path. Unrelated slugs continue to claim and publish in parallel.

### 3. Explicit CLI surface

Expose deterministic CLI operations for reservation create, status, resume,
and governed abort. The CLI returns typed JSON containing reservation id,
binding digest, event head, claim-fence epoch, bound session/claim, and exact
denial/recovery reason. It never accepts raw SQL, caller-invented event state,
or a session-only ownership assertion.

The existing ordinary `claim` command remains unchanged for unreserved slugs.
For a reserved slug it reports the typed fence and points to the explicit
recovery-resume operation; it must never print a foreign-holder record with a
success exit code.

### 4. Reservation-aware publication mint and receipt consumption

The governed bridge writer asks the control plane whether the exact target
generation is reserved before ordinary capability mint. Any active reservation
blocks ordinary mint. The reservation-aware path additionally proves:

- current exact recovery claim and claim-fence epoch;
- current schema-v3 start authority and PAUTH;
- exact archive/replacement/predecessor paths and digests;
- required version, status, author role, and transition; and
- no ambiguous source/archive physical state.

Only then may it mint the ordinary WI-5825-backed publication capability. A
`publication_minted` event binds that capability digest. Reservation
`consumed` is appended only after canonical readback proves the exact
replacement receipt consumed the exact capability. A crash after file creation
uses WI-5825's landed capability-row recovery; it does not create another
receipt or a second reservation protocol.

### 5. Crash and ambiguity handling

The contract recognizes only the exact bound physical states:

- source present / archive absent before move;
- source absent / exact archive present after move;
- exact replacement plus consumed receipt after publication.

Source and archive both present, both absent, symlinks, digest drift, changed
predecessor, mismatched role/status, foreign capability, or conflicting event
head fail closed with zero new claim, event, file, or receipt mutation. A
governed abort is allowed only before replacement capability mint, with exact
physical-state proof and an append-only reason event.

## Sequencing And Current Overlap Boundary

This proposal may be independently reviewed now, but implementation cannot
start until every shared-path owner below is terminal/independently VERIFIED
and clean, or both threads carry an independently accepted exact non-overlap
ledger and order:

- WI-5825 current strict GO v006, SHA-256
  `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`,
  overlaps registry control plane, writer, and both matching tests. It owns
  receipt back-fill and capability-row recovery and must land first.
- WI-5715 current v004 `NO-GO` owns the foreign modified optimistic registry
  reader bytes in `registry_control_plane.py` and
  `test_registry_control_plane.py`; those bytes must be finalized and clean.
- WI-5877 current `REVISED` owns the one-line foreign modification in
  `bridge_work_intent_registry.py`; it must be independently VERIFIED and clean.
- Current strict GO `gtkb-authority-foundations-project-authorization` v015,
  SHA-256
  `1047F39753698FEA8558A0409597C06030AF4B069A5BB88804C33DCFF2892F9F`,
  overlaps the work-intent registry, claim CLI, and registry test.
- Current strict GO `gtkb-wi5237-wi5229-pauth-configuration-coverage` v010,
  SHA-256
  `6B22288E7E4D737F323CE02CE1DB317880D62412A67DC5A89AA6F8CC063BE036`,
  and `gtkb-wi5240-wi5236-pauth-registered-vocabulary` v008, SHA-256
  `1A14BB8FBA697171A9FFF6B904E77CD9227AA64538BE3705A642157265289234`,
  overlap the claim CLI.
- Current strict GO `gtkb-wi5603-ipa-advisory-envelope-semantics` v004,
  SHA-256
  `B6C3F6348FC741FE603C83783173C437DDF229827712F05CCCAE8483FEDCD881`,
  overlaps the governed writer.

The listed current claims are null or expired/lapsed; no active exact claim
collision was observed. GO authority and foreign bytes still require explicit
sequencing even when claims are absent. Fresh current heads, hashes, claims,
schema-v3 packets, and exact hunks must be re-read immediately before any later
GO and implementation start.

The foreign zero-byte `.git/index.lock` dated
`2026-08-01T08:59:21.8949959Z` is preserved. WI-5819/WI-5849 own typed stale-lock
remediation; this proposal neither classifies nor removes it. Finalization must
fail closed while the lock remains foreign.

## Current Exact Target State

At proposal preparation the thread has no physical v001 and no claim. Target
states are:

| Target | SHA-256 / state |
|---|---|
| `scripts/bridge_work_intent_registry.py` | `633E22ACFF0E6E5B9964827CCAC40A3299D7FD513918F24C90469AC9A338F1E3`; foreign modified by WI-5877 |
| `scripts/bridge_claim_cli.py` | `E6B0B5002FCB9F4D2FA5B1E20938C112F090EEA19BEE95AD97E8DB15AD0FC0A3`; clean |
| `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` | `A063E0CB057FACFC86D077360B02EB9805A1EB516C7CE16CCED0B472D06C3006`; foreign modified by WI-5715 |
| `scripts/gtkb_bridge_writer.py` | `9399A3878D99C0CB007C9A7E979F25C09B6EDFAC841CB75C6FB78D3C8472F2F4`; clean |
| `platform_tests/scripts/test_bridge_work_intent_registry.py` | `F886F15E229BA1BC56E7C2513F67772031459B14A5C49A7C8A258CA23158A5AB`; clean |
| `platform_tests/scripts/test_bridge_claim_cli.py` | `8708469B5EA002B0BA73BD690229BE5C9828B3E4293C696FA849EA110AC06387`; clean |
| `groundtruth-kb/tests/test_registry_control_plane.py` | `FDA19AED075D4D397BF7A97556CB4395D6EA97324012DA08A8E39BE327349073`; foreign modified by WI-5715 |
| `platform_tests/scripts/test_gtkb_bridge_writer.py` | `38A4BDEFF74BB9AA3F841C35F103DE3393945C36CBCA42925314D9605DA6D871`; clean |

No foreign bytes are adopted or rebaselined. Drift before filing, review, GO,
or implementation returns the proposal to revision.

## Project And Operation-Time Authority

- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is active and WI-5881 is an
  active direct member in subproject `publication-linearizability`.
- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  v2 is active, list-free, unexpired, and covers source, test, test addition,
  metadata, governance-evidence, and bridge classes.
- Current list-free project authority controls operation time. Deprecated
  `work_items.approval_state` is noncontrolling.
- The PAUTH does not replace independent GO, exact claims, schema-v3 start,
  target isolation, factual report, independent VERIFIED, or atomic finalization.

No new owner decision or WI-specific approval is required for this proposal.

## Timer And Concurrency Disposition

WI-5858 and the Timer Governance program remain the only carriers for claim
TTL, retry, wait, throttle, and per-harness concurrency values. This proposal
introduces no literal timeout, TTL, sleep, retry, backoff, fan-out, or global
worker leader. Any bounded lock/retry behavior is injected from the centralized
environment/configuration SoT. Preparation and unrelated-slug operations remain
parallel; only one short exact reservation/claim/event/CAS transaction is
serialized.

## Cross-Harness Disposition

- Claude and Codex CLI callers receive the same typed reservation and claim
  outcomes through deterministic services.
- Cursor has no separate recovery helper assumption; it consumes the shared CLI
  and writer contract when available.
- Goose, Antigravity, Ollama, OpenRouter, and other harnesses receive equivalent
  claim fencing and publication denial through the shared service, independent
  of harness-local hooks.
- Role/status authority still derives from the exact active session envelope;
  the reservation never grants or changes a worker role.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only role/status authority and
  governed publication require exact replacement and independent review.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — reservation, claim, event, capability,
  and receipt reads use canonical current service state.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — incident replacement remains a Prime
  nonterminal correction, never closure.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active direct
  project PAUTH controls every later source/test and metadata operation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — explicit PAUTH,
  project, WI, and exact targets are declared.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing
  requirements are concrete before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11809 maps to exact
  executable multi-process nodes and live predicates.
- `GOV-ARTIFACT-APPROVAL-001` — project authority does not waive formal
  artifact or service-owned metadata gates.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — unrelated claims,
  publications, and harnesses remain behaviorally unchanged.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — recovery and
  concurrency decisions live in deterministic code, not session lore.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — superseded evidence, successor scope,
  reports, and verification remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5791, WI-5825, WI-5858, WI-5879, and WI-5881
  remain distinct, nonduplicated carriers.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all eight targets and generated
  evidence stay under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — native Windows work self-enforces
  GO/claim/start checks through shared services.

## Prior Deliberations

- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — exact
  record/path CAS and unrelated-worker parallelism replace global leadership.
- `DELIB-202667724` and `DELIB-202667732` — Bridge Protocol Reliability
  whole-project authorization and active v2 correction.
- `DELIB-202667722` — timers, throttles, retries, and concurrency configuration
  must be centralized and data-tuned.
- `DELIB-20265660` — prior VERIFIED finalization atomicity design evidence;
  preserved but not treated as this implementation.
- `DELIB-20263296` — role-eligibility guard history for implementation claims.
- `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-004.md` — exact
  independent claim-takeover reproduction and required generic successor split.

## Requirement Sufficiency

Existing requirements sufficient. WI-5881, TEST-11809, physical WI-5879 v004,
the linked bridge/freshness/project/testing constraints, and the owner's
parallel-SoT direction specify the exact claim-plus-publication invariant. No
new role, status, global lock, timer policy, dispatcher contract, or owner
choice is required before independent review.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Independent GO after exact overlap sequencing, fresh claim and schema-v3 start, generic reservation/claim/writer implementation, factual report, and independent VERIFIED; WI-5879 consumes the landed contract later.",
  "baseline": {
    "generic_predecessor": "WI-5791 is falsely terminal historical evidence with no target-bearing verified implementation",
    "incident_evidence": "WI-5879 v004 proves foreign ordinary GO claim takeover immediately after a move exposes the predecessor GO",
    "current_shared_state": "three targets contain foreign WI-5715/WI-5877 bytes and five current strict GO threads overlap the cohort",
    "timer_owner": "WI-5858 and centralized Timer Governance own values and tuning"
  },
  "before_behavior": "A publication-only reservation does not prevent the ordinary go_implementation path from preempting the recovery worker's non-GO victim claim, so a move can strand the reservation without an eligible governed writer claimant.",
  "after_behavior": "One immutable exact-generation reservation atomically installs a claim fence and publication-mint fence; only an explicitly authorized recovery resume can transfer an expired bound owner and only the exact replacement receipt consumes the reservation.",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, active project PAUTH v2, the work-intent registry, registry control plane, governed writer, and TEST-11809.",
  "essential_context_preservation": "Preserve exact source/archive/replacement/predecessor bytes and authority, claim-fence epoch, event history, capability/receipt identity, WI-5791 superseded history, WI-5879 incident ownership, shared-path sequencing, and the no-dispatcher/TAFE boundary.",
  "obsolete_guidance_disposition": "The incident-specific publication-only reservation design in WI-5879 v003 is superseded by the generic claim-plus-publication contract; WI-5791 remains immutable historical evidence and is not reopened.",
  "history_preservation": "Reservations and state transitions are append-only; existing bridge, claim, capability, receipt, work-item, test, and deliberation evidence is not rewritten or deleted.",
  "provenance": "WI-5881; TEST-11809; WI-5879 v004; WI-5791/TEST-11758 history; WI-5825; WI-5858; WI-5877; DELIB-202667724; DELIB-202667732; DELIB-202667722; DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT.",
  "self_descriptive_naming": "Use exact-generation recovery reservation, claim fence epoch, bound recovery owner, reserved publication capability, receipt-bound consumption, and governed abort; do not call a global leader or ordinary TTL claim a durable reservation.",
  "expected_result": {
    "claim_takeover": "ordinary draft/go_implementation/no-action claims cannot preempt or reclassify a reserved victim",
    "fresh_resume": "one fresh authorized session atomically binds the next claim-fence epoch after owner expiry",
    "publication": "ordinary mint is denied and only the exact bound replacement receipt consumes the reservation",
    "parallelism": "unrelated slugs continue claiming and publishing concurrently",
    "consumer": "WI-5879 uses the generic interface without source-level reimplementation"
  },
  "hard_invariants": [
    "Reservation and initial victim-claim fence commit atomically before evidence moves",
    "Ordinary claims and ordinary publication mint cannot bypass an active exact-generation reservation",
    "Fresh-session resume validates current authority, exact tuple, physical state, and one claim-fence epoch CAS",
    "Only the exact replacement capability receipt consumes the reservation",
    "Shared-path owners land or provide independently accepted non-overlap before implementation",
    "Unrelated-slug operations remain parallel without a global leader",
    "No new timer literal, raw SQLite write, dispatcher/TAFE action, or foreign lock mutation"
  ],
  "fail_closed_conditions": [
    "Changed source, archive, replacement, predecessor, status, role, authority, capability, or receipt binding",
    "Source/archive physical ambiguity, symlink, or digest drift",
    "Foreign unexpired bound recovery owner or claim-fence epoch mismatch",
    "Missing current GO, PAUTH, exact claim, schema-v3 packet, or clean shared-target sequencing",
    "Ambiguous publication success or non-exact receipt consumption"
  ],
  "rollback": {
    "instructions": "Before any live reservation exists, revert only the approved eight implementation hunks after separating foreign owners. After a reservation exists, preserve its append-only events and use governed abort only before capability mint with exact state proof. Never delete reservation or incident evidence rows.",
    "verification": "Run all TEST-11809 nodes, current applicability/clause gates, exact claim/reservation/capability/receipt readbacks, unrelated-slug concurrency checks, lint/format/compile/diff checks, and dispatcher/TAFE no-touch evidence."
  }
}
```

## Specification-Derived Verification Plan

TEST-11809 maps to these exact planned executable nodes:

1. `platform_tests/scripts/test_bridge_work_intent_registry.py::test_recovery_reservation_blocks_foreign_go_claim_takeover`
2. `platform_tests/scripts/test_bridge_work_intent_registry.py::test_recovery_reservation_resume_transfers_expired_owner_atomically`
3. `platform_tests/scripts/test_bridge_work_intent_registry.py::test_reserved_and_unrelated_slugs_claim_in_parallel`
4. `platform_tests/scripts/test_bridge_claim_cli.py::test_recovery_claim_cli_denies_ordinary_takeover_and_resumes_exactly`
5. `groundtruth-kb/tests/test_registry_control_plane.py::test_bridge_recovery_reservation_binds_exact_generation_and_append_only_events`
6. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_generation_blocks_ordinary_publication_mint`
7. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_recovery_crash_boundaries_resume_once`
8. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_recovery_rejects_binding_drift_without_mutation`

Required multi-process cases hold a pre-move non-GO claim, atomically reserve
the victim generation, expose the predecessor GO, race a foreign ordinary
claim before `claim-no-action`, and prove denial plus one authorized fresh
resume. Additional injection points cover crash before/after move and
before/after capability consumption. Every negative case records zero mutation
across claim, reservation event, target, capability, and receipt surfaces.

Planned command after implementation:

```text
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py::test_recovery_reservation_blocks_foreign_go_claim_takeover platform_tests/scripts/test_bridge_work_intent_registry.py::test_recovery_reservation_resume_transfers_expired_owner_atomically platform_tests/scripts/test_bridge_work_intent_registry.py::test_reserved_and_unrelated_slugs_claim_in_parallel platform_tests/scripts/test_bridge_claim_cli.py::test_recovery_claim_cli_denies_ordinary_takeover_and_resumes_exactly groundtruth-kb/tests/test_registry_control_plane.py::test_bridge_recovery_reservation_binds_exact_generation_and_append_only_events platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_generation_blocks_ordinary_publication_mint platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_recovery_crash_boundaries_resume_once platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_recovery_rejects_binding_drift_without_mutation -q --tb=short
```

The implementation report must record exact collection counts and observed
results, reservation/binding/event/claim-fence/capability/receipt identities,
crash-injection outcomes, unrelated-slug concurrency evidence, and exact diff
attribution. Planned tests are not present execution evidence.

## Acceptance Criteria

1. Reservation creation and the initial victim-claim fence commit atomically
   before any evidence move; canonical readback proves the exact tuple.
2. Incoming ordinary `draft`, `go_implementation`, and
   `no_action_correction` operations cannot preempt, reclassify, or deny the
   bound recovery owner after the predecessor GO becomes visible.
3. A fresh authorized Prime session resumes only after prior owner expiry/loss,
   exact authority and physical-state validation, and one claim-fence epoch CAS.
4. Ordinary publication mint cannot occupy a reserved generation; only the
   bound recovery path may mint the exact replacement capability.
5. Reservation consumption requires canonical consumption of the exact bound
   replacement receipt; claim expiry, file presence, or observation alone does
   not consume or release it.
6. Every crash boundary resumes idempotently once; drift and ambiguous
   physical state produce zero mutation and retained evidence.
7. Unrelated slugs claim and publish concurrently; no repository-wide leader
   or long critical section is introduced.
8. WI-5825, WI-5715, WI-5877, and every current strict-GO shared-path owner are
   terminal/independently VERIFIED and clean, or carry an independently
   accepted exact non-overlap ledger, before implementation starts.
9. TEST-11809's eight exact nodes execute and pass with live predicate evidence.
10. WI-5879 remains an incident consumer; no incident path or replacement bytes
    enter this generic eight-target implementation.
11. No new hard-coded timer/TTL/retry/throttle/concurrency value, raw SQLite
    write, dispatcher/TAFE activation or mutation, foreign-lock handling,
    project mutation, credential operation, deployment, release, push, history
    rewrite, or destructive cleanup occurs.
12. Ruff check, Ruff format check, Python compile, focused/full adjacent tests,
    and scoped diff checks pass on the exact final cohort.

## Risks And Rollback

- **Cross-store atomicity:** claim and reservation state must share one governed
  transaction boundary or an explicit recoverable journal; a best-effort pair
  of writes recreates the race and fails acceptance.
- **Overbroad blocking:** reservation lookup is exact document/version/path;
  unrelated slugs and generations remain parallel.
- **Stale owner capture:** session identity alone is never durable authority;
  resume requires current governed evidence and claim-fence epoch CAS.
- **Receipt ambiguity:** ambiguous publication never consumes a reservation;
  canonical capability and receipt readback governs recovery.
- **Foreign-byte absorption:** all dirty target owners land or are exactly
  separated before implementation; current hashes are evidence, not a rebase.
- **Rollback:** before any live reservation, revert only the approved eight
  implementation hunks. After reservation creation, preserve events and use
  governed abort under the stated conditions. Correct later incidents forward;
  never delete durable evidence.

## Candidate Pre-Filing Gates

Run applicability, mandatory clause, and writer-compliance audits against this
exact non-live candidate. Live filing additionally requires physical v001
absence, current active project/PAUTH, fresh exact draft claim, current target
and overlap readback, registry observation, governed writer publication, and
canonical status/path/hash/claim-consumption readback.

## DISARM — Implementation Boundary

This proposal authorizes no protected edit, database write, reservation, claim
takeover, evidence move, or dispatcher/TAFE action. Implementation requires an
independent current GO, all stated shared-path sequencing, a fresh exact
`go_implementation` claim, fresh schema-v3 start packet, exact target/hunk
isolation, factual report, and independent atomic VERIFIED.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_claim_cli.py`
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_claim_cli.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
