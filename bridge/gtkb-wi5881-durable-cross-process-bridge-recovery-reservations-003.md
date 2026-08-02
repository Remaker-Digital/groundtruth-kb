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
Version: 003
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-002.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5881
Related Work Items: WI-5603, WI-5617, WI-5715, WI-5791, WI-5812, WI-5819, WI-5825, WI-5829, WI-5849, WI-5858, WI-5877, WI-5879

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_claim_cli.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This proposal performs no implementation-target or operational KB mutation.
Governed bridge publication may write typed capability, receipt, and registry
revision bookkeeping to `groundtruth.db`; that filing metadata is not
implementation authority and is not represented by `target_paths`.

# REVISED Implementation Proposal — Durable Exact-Byte Bridge Recovery Reservations

## Revision Claim

Implement one generic, exact-generation recovery reservation that durably
stores the authoritative normalized candidate bytes and their immutable
evidence before origin loss, fences ordinary claim takeover and ordinary
publication mint, and permits a different authorized Prime Builder to resume
only through a narrow reservation route that preserves the original author
while separately proving the current invoker, claim, role document, start
authority, and claim-fence epoch.

Preparation, claims on unrelated documents, candidate normalization, audits,
and object/evidence construction remain parallel. Aggregate bridge publication
continues to use the existing short `_RegistryFileLock` plus one-minted-
capability commit point. This revision does not promise concurrent aggregate
mint/consume, add a repository leader, weaken ordinary author/claim equality,
or introduce a timer value.

WI-5879 remains the incident-specific consumer after this generic contract and
WI-5825 are independently VERIFIED. WI-5617 and WI-5791 remain immutable
invalid/false-terminal history, not implementation authority. WI-5812 v013 is
linked as the current forward Goose filing contract and has no exact target
overlap with this nine-target recovery service.

## Response To Version 002

### F1 — exact candidate bytes and pre-move evidence were missing

**Accepted and corrected.** Reservation preparation now persists one immutable
payload before any evidence move:

- exact UTF-8 normalized candidate bytes as a BLOB plus byte size and content
  digest;
- document, exact version, target path, status, predecessor path/digest,
  source/archive paths and digests, and required transition;
- the complete original author envelope and its canonical digest, including
  immutable author identity, harness, session context, model, configuration,
  and metadata source;
- canonical compliance-audit result bytes/digest, provider-guard result
  bytes/digest, and their schema/tool identities;
- canonical resource-binding evidence for the exact target generation,
  candidate byte size, content digest, predecessor, project, PAUTH, work item,
  reviewed proposal, GO, schema-v3 start packet, and binding digest; and
- initiating invoker/session, claim identity, claim-fence epoch, event-head
  preimage, and creation time as separate audit fields.

The writer normalizes and audits the candidate once before reservation. The
control plane persists those exact bytes/evidence, rereads the BLOB, size, and
all digests canonically, and only an `armed` readback permits the consumer to
move the source. Resume never regenerates, re-normalizes, or rewrites candidate
bytes or author metadata. Any BLOB, size, digest, evidence, predecessor, path,
or transition mismatch fails closed without a new claim, event, capability,
file, or receipt mutation.

### F2 — ordinary author-session/claim-session equality must remain intact

**Accepted and corrected.** Ordinary capability mint and consume retain the
existing invariant `author_session == claim_session`. Their APIs and negative
tests remain unchanged.

Add a separate reservation-only entry point. It is reachable only from an
active exact reservation whose stored payload has passed canonical readback.
It preserves the stored original author/session and bytes, while separately
validating and recording:

- current recovery invoker and session;
- current Prime Builder role from the exact worker-session document;
- current exact recovery claim and claim-fence epoch;
- current active project membership and operation-time PAUTH;
- fresh exact schema-v3 implementation-start authority; and
- unchanged reservation binding, event head, physical state, and aggregate
  publication preimage.

The reserved capability and receipt record both identities:
`original_author_session` and `recovery_invoker_session`, plus the exact claim
and fence epoch. The current invoker never becomes artifact author and cannot
substitute new bytes. Ordinary mint must still reject an original-author /
different-claim-session pair; only the reservation-specific route may accept
the exact stored tuple after all current invoker checks pass.

### F3 — unrelated publication and lock order were overstated

**Accepted and corrected.** Current `_RegistryFileLock` serializes the registry
control plane, and the one-minted-capability gate serializes aggregate bridge
publication. This revision preserves that short aggregate commit point. It
claims parallel preparation, claims, normalization, audits, and reservation
reads—not simultaneous aggregate mint/consume. Removing the aggregate
serialization is a separate future design requiring its own measured evidence.

The recovery state machine has this total phase order:

1. normalize candidate bytes and run compliance/provider guards without any
   work-intent or control-plane lock;
2. acquire `_RegistryFileLock`, then the control-plane SQLite transaction,
   append the immutable `prepared` payload/event, commit, and release both;
3. acquire only the work-intent SQLite transaction, CAS-install the exact
   reservation claim fence, commit, and release it;
4. reacquire `_RegistryFileLock`, then the control-plane SQLite transaction,
   prove the fence and payload readback, append `armed`, commit, and release;
5. perform the exact source-to-archive move with no database or registry file
   lock held;
6. acquire `_RegistryFileLock`, then the control-plane SQLite transaction for
   the reservation-only mint and aggregate revision/one-capability CAS, commit,
   and release;
7. perform exclusive target creation and byte-for-byte reread with no database
   or registry file lock held; and
8. reacquire `_RegistryFileLock`, then the control-plane SQLite transaction for
   receipt consumption, aggregate revision, and reservation `consumed` event.

The work-intent database transaction is never held while acquiring the file
lock or control-plane database, and neither control-plane lock is held while
opening the work-intent transaction. The only nested acquisition order is
`_RegistryFileLock` before control-plane SQLite. This eliminates a cyclic lock
graph and preserves current file-before-control-plane-database ordering.

A crash between `prepared`, fence installation, and `armed` is recoverable:
`prepared` alone authorizes no move; an installed fence blocks ordinary
takeover; only canonical `armed` state authorizes the move. Ambiguous write
results require canonical readback of the expected event head/fence epoch
before any continuation; no blind duplicate append or reversed lock order is
allowed.

An independently observed WI-5603 publication showed the physical file and
capability completion while its `no_action_correction` claim was briefly still
visible; two later reads returned null. This is evidence of a transient
publication-to-claim-release visibility window, not a persistent failed
release. Recovery classifies exact receipt/capability completion plus a still-
live same-transaction claim as `publication_completed_claim_release_pending`:
it neither remints nor permits takeover, and it uses bounded canonical readback
until the claim release is visible or a typed ambiguity result is returned.
WI-5829 retains ownership of ordinary implementation-report claim lifecycle;
WI-5881 applies this rule only to its reserved recovery transaction.

### F4 — document-authoritative role authority and its test surface were absent

**Accepted and corrected.** The scope adds
`platform_tests/scripts/test_work_intent_role_eligibility.py` and cites both
`SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` and
`DCL-SESSION-ROLE-RESOLUTION-001` v7.

Every reservation create/resume/abort and reservation-only mint resolves the
acting role from the exact current worker-session document. Missing, malformed,
closed, ambiguous, mismatched, or non-Prime evidence fails closed. Durable
registry role, dispatcher mappings, runtime markers, ambient environment role,
and fallback labels are never authority. The current document role, invoker,
claim session, original author, and reservation epoch are validated as distinct
fields rather than collapsed into one session identity.

### F5 — the crash/race test plan was not decisive

**Accepted and corrected.** TEST-11809 now names reserve/readback-before-move,
move-before-mint origin loss, fresh original-author/different-invoker resume,
ordinary mint rejection, stale epoch racing resume, two-slug aggregate
serialization, and every mint/file/consume boundary. Exact nodes appear in the
verification plan below.

### F6 — timer externalization was claimed before it existed

**Accepted and corrected.** Current 30-second registry-lock behavior and
capability lifetime remain compatibility facts, not capabilities delivered by
WI-5881. This scope adds no timer/configuration target or literal. Any touched
wait/retry path keeps its current behavior unless WI-5858 first supplies the
governed typed configuration interface; implementation and its report may not
claim externalization merely because this proposal requires it eventually.
Lock timeout and ambiguous-result recurrences remain evidence for WI-5858 and
the Timer Governance program.

## Durable Reservation State Machine

### Immutable payload and append-only events

The authoritative payload is immutable after `prepared`. State derives from
append-only events: `prepared`, `claim_fenced`, `armed`, `moved`,
`publication_minted`, `file_created`, `receipt_consumed`, `consumed`, and
governed `aborted`. Each event binds the prior event head, payload digest,
claim-fence epoch, actor/invoker, and canonical state evidence. No event or
payload row is updated or deleted.

Only one nonterminal reservation may bind an exact document/version/target
generation. A second reservation, altered payload, or changed predecessor
fails before mutation. `prepared` may be governed-aborted only before the claim
fence; an armed reservation may be aborted only before capability mint and only
when exact physical-state proof establishes safe recovery. After mint, WI-5825
capability/file/receipt recovery governs forward completion.

### Exact physical states

The contract accepts only:

- source present / archive absent before move;
- source absent / exact archive present after move;
- exact stored replacement bytes at the target after creation; and
- exact consumed receipt/capability after publication.

Source and archive both present, both absent, symlinks/reparse ambiguity,
digest drift, changed predecessor, changed status/role, foreign capability,
altered original author, changed evidence bundle, or stale event/fence epoch
fails closed with zero new mutation.

### Fresh-session recovery

A fresh Prime Builder may resume only after the prior bound owner is absent,
expired, or otherwise proven lost under the governed claim rule. Resume must
present the reservation id/binding digest and CAS the next claim-fence epoch.
It rereads the stored bytes/evidence and current physical state, resolves its
role from the exact session document, proves current PAUTH/start authority, and
binds a new recovery claim. An unexpired owner, stale epoch, different tuple,
or ordinary claim operation is denied with typed evidence.

## Currentness, Collision, And Sequencing

- Canonical head is v002 `NO-GO`, SHA-256
  `52384C6B6ED21BECDF878FA0806A884FEB6E32155870BC24AC4102D9F88A9328`;
  v003 is absent and the current claim is null.
- WI-5825 v006 `GO`, SHA-256
  `FABBEEE32234A9DF7801EFF2400F2EBD465EC2612B9BAB44DDB79244AF4A42DD`,
  is the only exact current strict-GO overlap: registry control plane, its test,
  governed writer, and writer test. It owns capability-row and receipt recovery
  and must land first or carry an independently accepted exact order/ledger.
- WI-5715 v004 `NO-GO` owns the foreign modified control-plane source/test
  bytes. It is not strict GO, but its bytes must be finalized/clean or exactly
  separated before WI-5881 starts.
- WI-5877 is carried by
  `gtkb-wi584x-codex-home-harness-selector-false-positive` v005 `REVISED`,
  SHA-256
  `123C872537F1F22DA8E69746FCC35BB2A7A005CA01CE80AC1411CD2830336258`,
  and owns the foreign work-intent-registry hunk. It must become independently
  VERIFIED/clean or carry an accepted hunk ledger.
- WI-5812 v013 `REVISED`, SHA-256
  `0ECC074257FBCD3EF7C2E48B6AF0886B18D721E128C20963939873E9D0BE79F3`,
  is linked for current forward Goose filing and has no exact nine-target
  overlap.
- WI-5879 v005 `REVISED`, SHA-256
  `E91CB0A7467C068AD81C0D2D95A2E5D92DA43439379D5DBB377B22A7AC752EE4`,
  remains the incident consumer and must not reimplement this service.
- WI-5617 physical v013 `VERIFIED` is strict-invalid historical evidence and
  never grants current authority.
- WI-5603's old writer GO is now physically superseded by targetless v005
  `NO-ACTION`; no source implementation from that old GO may be inferred.

Claims being null or expired does not clear GO authority, foreign byte
ownership, or sequencing. Fresh exact heads, hashes, claims, PAUTH, session
documents, overlap ledgers, event heads, and schema-v3 packets are mandatory
immediately before any later GO/start.

The foreign zero-byte `.git/index.lock` remains untouched. WI-5819/WI-5849 own
typed stale-lock remediation; finalization fails closed while it is foreign.

## Current Exact Target State

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
| `platform_tests/scripts/test_work_intent_role_eligibility.py` | `D45D755A1CBBBE65B122919B058F52FA2486EA379EDD1442334FFA4D1C88AC05`; clean |

No foreign byte is adopted or rebaselined. Drift before filing, review, GO, or
implementation returns the proposal to revision.

## Project And Operation-Time Authority

`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` is active v3 and WI-5881 is an
active direct member. List-free
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
v2 is active, unexpired, has no WI exclusions, and covers the nine source/test
targets. Deprecated WI approval metadata is noncontrolling.

The project PAUTH does not replace a fresh independent GO, exact
`go_implementation` claim, schema-v3 start packet, clean/ordered targets,
factual implementation report, independent VERIFIED, or atomic finalization.
No new owner decision or WI-specific approval is required for review.

## Timer And Concurrency Disposition

This proposal introduces no timeout, TTL, retry count, sleep, backoff,
throttle, threshold, fan-out, concurrency limit, or global-leader literal.
WI-5858 and Timer Governance own configuration externalization and tuning.
Until their typed interface exists, WI-5881 preserves current timer behavior
and reports it truthfully; it does not add another environment key or local
fallback.

Candidate normalization, compliance/provider audits, claims on unrelated
documents, object construction, and reservation status reads remain parallel.
The short aggregate mint/consume commit point stays serialized by the current
control-plane lock and one-capability invariant. That is aggregate
linearization, not a persistent all-program leader.

## Cross-Harness And Role Disposition

- Claude, Codex, Goose, Antigravity, Ollama, OpenRouter, Cursor, and other
  callers consume the same reservation/claim/writer service semantics.
- Cursor has no helper-specific implementation assumption.
- Original author identity is immutable candidate provenance; the fresh
  recovery invoker is separately recorded and never substituted as author.
- Every acting-role decision resolves from the exact current worker-session
  document under DCL v7. Registry, dispatcher, marker, ambient-environment, or
  fallback role evidence is rejected.
- Ordinary author-session/claim-session equality remains unchanged outside the
  narrow exact reservation route.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only role/status authority and
  exact governed publication.
- `SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001` — recovery
  claim/resume role is authoritative only from the exact worker-session
  document.
- `DCL-SESSION-ROLE-RESOLUTION-001` v7 — no registry, dispatcher, marker, or
  fallback role authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — current payload, event, claim, fence,
  PAUTH, start, capability, aggregate, and receipt state is reread at each CAS.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — incident corrections remain
  nonterminal and never close work by status alone.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — current project
  PAUTH controls later operations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, WI,
  related work, and exact targets are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requirements are
  concrete before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11809 maps to exact
  executable persistence, role, crash, race, and aggregate-serialization nodes.
- `GOV-ARTIFACT-APPROVAL-001` — project authority does not waive service-owned
  formal metadata gates.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — ordinary mint/consume, foreign
  bytes, roles, and unrelated claims remain intact.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — recovery and
  concurrency decisions live in deterministic services.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — invalid history, reservation payload,
  events, reports, and verification remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5617, WI-5791, WI-5812, WI-5825, WI-5829,
  WI-5858, WI-5877, WI-5879, and WI-5881 retain distinct ownership.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets/evidence remain under
  `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — native Windows self-enforces shared
  GO/claim/start and writer boundaries.

## Prior Deliberations

- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — exact
  record/path CAS and useful parallel work without an all-program leader.
- `DELIB-202667517` — later owner direction rejects persistent global
  serialization/read-only operation while preserving exact-WI governance.
- `DELIB-202667724` and `DELIB-202667732` — Bridge Protocol Reliability
  whole-project authority and v2 correction.
- `DELIB-202667722` — timer/concurrency values belong in a centralized,
  data-tuned source of truth.
- `DELIB-20265660` — prior finalization atomicity evidence, not this
  implementation.
- `DELIB-20263296` — role-eligibility guard history for implementation claims.
- `bridge/gtkb-wi5881-durable-cross-process-bridge-recovery-reservations-002.md`
  — exact independent findings answered here.

## Requirement Sufficiency

Existing requirements sufficient. WI-5881, TEST-11809, v002, current role
authority, active project PAUTH, WI-5879 incident evidence, and WI-5825 receipt
recovery define the correction. No new role, status, timer value, global
leader, dispatcher contract, or owner choice is required before independent
review.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "primary_route": "Independent GO after exact overlap sequencing, fresh claim/schema-v3 start, exact-byte reservation implementation, factual report, and independent VERIFIED.",
  "baseline": {
    "thread": "WI-5881 v002 NO-GO; no executable TEST-11809 nodes",
    "payload_gap": "v001 stored digests but not authoritative normalized candidate bytes/evidence",
    "identity_gap": "ordinary mint correctly requires author_session == claim_session",
    "publication": "current control-plane file lock and one-minted-capability gate serialize aggregate publication",
    "dirty_owners": "WI-5715 owns two control-plane paths; WI-5877 owns one work-intent path"
  },
  "before_behavior": "Origin loss after move can leave no authoritative byte source, while a different recovery owner cannot lawfully mint the original-author candidate and ordinary claim takeover can steal the victim generation.",
  "after_behavior": "An immutable pre-move payload stores exact normalized bytes/evidence and original author; an append-only fence state machine permits only a separately validated current recovery invoker to publish that exact tuple through the serialized aggregate commit point.",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, claim-document authority SPEC, DCL role v7, current PAUTH/start, work-intent registry, registry control plane, governed writer, and TEST-11809.",
  "essential_context_preservation": "Preserve original bytes/author, current invoker/role/claim/epoch, predecessor and physical tuple, audit/guard/resource evidence, aggregate preimage, capability/receipt, append-only events, foreign owners, and incident/history separation.",
  "obsolete_guidance_disposition": "v001 unlimited unrelated-publication wording is replaced by parallel preparation plus existing short aggregate serialization; no ordinary mint invariant is relaxed.",
  "history_preservation": "Candidate payload and all reservation transitions are append-only; WI-5617/WI-5791/WI-5879 and every numbered bridge file remain unchanged.",
  "provenance": "WI-5881 v001/v002; TEST-11809; WI-5879 incident reproduction; WI-5617/WI-5791 historical defects; WI-5812 v013; WI-5825; WI-5829 transient release window; WI-5858; WI-5877; current exact target hashes; active Bridge Protocol Reliability PAUTH v2.",
  "self_descriptive_naming": "Use prepared payload, claim fenced, armed, moved, publication minted, receipt consumed, release pending, original author session, recovery invoker session, and claim-fence epoch rather than generic reserved/resumed booleans.",
  "expected_result": {
    "origin_loss": "fresh invoker publishes exact stored original-author bytes after move-before-mint crash",
    "ordinary_mint": "different claim session remains rejected",
    "reserved_mint": "exact current invoker/claim/role/start/epoch succeeds without author rewrite",
    "aggregate": "two-slug publication is linearized without deadlock or duplicate receipt",
    "failures": "all drift/ambiguity cases produce zero mutation and typed evidence"
  },
  "hard_invariants": [
    "No move before immutable payload/fence armed readback",
    "Ordinary author-session equals claim-session remains unchanged",
    "Recovery invoker never replaces original author or candidate bytes",
    "Work-intent DB is never nested with control-plane locks",
    "Control-plane file lock precedes control-plane SQLite",
    "No new timer literal, global leader, raw SQLite bypass, dispatcher/TAFE mutation, or foreign lock handling"
  ],
  "fail_closed_conditions": [
    "Missing/malformed/mismatched worker-session role evidence",
    "Payload/BLOB/size/digest/evidence/predecessor/physical-state drift",
    "Stale claim-fence epoch or current authority change",
    "Foreign capability/aggregate preimage mismatch or ambiguous result",
    "Missing GO, exact claim, schema-v3 start, clean overlap order, or WI-5825 receipt contract"
  ],
  "rollback": {
    "instructions": "Before any live reservation, revert only approved nine-target hunks after foreign attribution. After prepare, preserve payload/events and recover or govern abort forward; never delete evidence rows.",
    "verification": "Run all TEST-11809 nodes, adjacent claim/role/writer/control-plane suites, exact readbacks, lint/format/compile/diff, and no-dispatcher/TAFE checks."
  }
}
```

## Specification-Derived Verification Plan

TEST-11809 maps to these exact planned nodes:

1. `groundtruth-kb/tests/test_registry_control_plane.py::test_recovery_reservation_persists_exact_normalized_bytes_evidence_and_size_before_move`
2. `groundtruth-kb/tests/test_registry_control_plane.py::test_recovery_reservation_readback_must_match_before_move_is_allowed`
3. `platform_tests/scripts/test_bridge_work_intent_registry.py::test_recovery_fence_blocks_foreign_go_and_draft_takeover_after_predecessor_exposed`
4. `platform_tests/scripts/test_bridge_work_intent_registry.py::test_recovery_resume_stale_epoch_race_has_one_winner_and_zero_loser_mutation`
5. `platform_tests/scripts/test_bridge_claim_cli.py::test_recovery_resume_after_move_before_mint_uses_exact_stored_tuple`
6. `platform_tests/scripts/test_bridge_claim_cli.py::test_recovery_claim_denies_lo_missing_malformed_closed_and_registry_fallback_roles`
7. `platform_tests/scripts/test_work_intent_role_eligibility.py::test_recovery_claim_role_is_exact_session_document_authoritative`
8. `platform_tests/scripts/test_work_intent_role_eligibility.py::test_recovery_claim_rejects_document_claim_role_mismatch_without_fallback`
9. `groundtruth-kb/tests/test_registry_control_plane.py::test_ordinary_mint_rejects_original_author_different_claim_session`
10. `groundtruth-kb/tests/test_registry_control_plane.py::test_reserved_mint_preserves_original_author_and_records_current_invoker_claim_epoch`
11. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_crash_after_reserve_readback_before_move_resumes_without_regeneration`
12. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_crash_after_move_before_mint_recovers_original_author_bytes_once`
13. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_mint_file_consume_boundaries_coordinate_with_wi5825_once`
14. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_two_slug_publication_parallel_preparation_serialized_aggregate_commit_no_deadlock`
15. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_recovery_drift_matrix_has_zero_claim_event_file_capability_or_receipt_mutation`
16. `platform_tests/scripts/test_gtkb_bridge_writer.py::test_reserved_publication_complete_live_claim_window_is_release_pending_not_duplicate`

The drift matrix covers bytes, byte size, original author, compliance/guard
evidence, resource binding, role document, current PAUTH/start, predecessor,
source/archive state, event head, fence epoch, aggregate preimage, capability,
and receipt. Multi-process fixtures inject crashes after `prepared`, after
claim fence, after `armed`, after move, after mint, after file create, and after
receipt consumption. Planned nodes are absent pre-implementation evidence; the
implementation report must record collection, results, exact state identities,
and process exit outcomes.

## Acceptance Criteria

1. Exact normalized candidate bytes, byte size, original author envelope,
   compliance/guard evidence, resource binding, authority, paths, predecessor,
   transition, and digests persist and canonically reread before any move.
2. Only canonical `armed` state permits the move; `prepared` or fence-only
   states are safe, visible, and recoverable after crash.
3. Ordinary mint/consume retains author-session equals claim-session and rejects
   an original-author/different-resumer pair.
4. Reservation-only mint preserves exact original author/bytes and separately
   validates/records current invoker, exact claim, session-document Prime role,
   current PAUTH/start, and claim-fence epoch.
5. Missing/malformed/closed/ambiguous/mismatched role documents and all
   registry/dispatcher/marker/fallback role evidence fail closed.
6. Ordinary GO/draft/no-action claim operations cannot take the reserved victim
   generation; one exact fresh resume wins a stale-epoch race.
7. Move-before-mint origin loss resumes from stored bytes/evidence without
   regeneration or author rewrite.
8. Existing aggregate publication serialization is explicit: preparation is
   parallel, while mint/consume is linearized through the current short lock
   and one-capability CAS with no deadlock or duplicate receipt.
9. The stated phase/lock order is implemented; no work-intent transaction nests
   with control-plane locks and no filesystem move/create occurs while they are
   held.
10. WI-5825 is terminal/independently VERIFIED and clean or has an accepted
    exact ordering ledger; WI-5715/WI-5877 foreign bytes are likewise resolved
    or exactly separated before implementation.
11. TEST-11809's sixteen exact nodes execute and pass with state/readback and
    multi-process evidence.
12. No timer/configuration literal or externalization claim is added; WI-5858
    retains that scope.
13. WI-5879 remains incident-only; WI-5617/WI-5791 history and WI-5812 forward
    filing scope remain separate.
14. Only the nine declared targets change; adjacent claim, role, control-plane,
    writer, receipt, provider-guard, and publication suites plus Ruff,
    formatting, compile, and scoped diff checks pass.
15. No raw SQLite bypass, dispatcher/TAFE activation or mutation, foreign-lock
    handling, credential action, deployment, release, push, history rewrite,
    or destructive cleanup occurs.

## Risks And Rollback

- **Append-only payload growth:** exact bytes are required for authoritative
  takeover. Reservations are exceptional exact-generation records; measure
  payload/storage/read latency and report it for the existing SoT-latency
  advisory rather than weakening byte durability.
- **Cross-store crash:** the prepared/fence/armed journal makes every partial
  phase recoverable and forbids a move until both stores canonically agree.
- **Author forgery:** the ordinary path is unchanged; the reserved route uses
  stored bytes/author plus separately authenticated current invoker evidence.
- **Deadlock:** no work-intent/control-plane nesting; file lock always precedes
  control-plane SQLite; filesystem operations occur after release.
- **Aggregate contention:** the current serialized commit point remains; this
  item does not promise unlimited publication throughput.
- **Foreign-byte absorption:** dirty owners land or are exactly separated before
  start; current hashes are evidence, not a rebase.
- **Rollback:** before reservation creation, revert only approved target hunks.
  After `prepared`, preserve payload/events and recover or govern abort forward;
  never erase reservation, incident, bridge, capability, or receipt evidence.

## Candidate Pre-Filing Gates

Run exact physical-currentness, active membership/PAUTH, target hash/dirty
ownership, strict-overlap, claim, applicability, mandatory clause,
collision/pattern, and writer-compliance checks on these candidate bytes. Live
filing additionally requires an exact draft claim, registry observation,
governed writer append, and canonical path/status/hash/claim-consumption
readback.

## DISARM — Implementation Boundary

This revision authorizes no protected edit, database payload/reservation/event,
claim takeover, evidence move, capability, receipt, Git action, or
dispatcher/TAFE use. Implementation requires a new independent current GO,
all stated overlap/foreign-byte sequencing, a fresh exact
`go_implementation` claim, fresh schema-v3 start packet for exactly nine
targets, factual report, and independent atomic VERIFIED.

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
