NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; transcript-defined Prime Builder; build envelope; owner-directed persistent Dispatcher Next goal
author_metadata_source: explicit_owner_direction

bridge_kind: prime_proposal
Document: gtkb-wi5879-wi5617-invalid-terminal-chain-repair
Version: 001
Date: 2026-08-01 UTC
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5879
Related Work Items: WI-5617
target_paths: ["bridge/gtkb-dispatcher-next-foundation-spike-013.md", "bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified", "groundtruth.db"]

# Defect-Fix Proposal — Repair WI-5617 invalid PB-authored terminal bridge chain without erasing evidence

## Claim

The current WI-5617 bridge head is not lawful terminal authority. Version 013 is authored by Prime Builder but carries the Loyal-Opposition-only status `VERIFIED`; the strict lifecycle resolver therefore rejects the thread with `WRONG_STATUS_AUTHOR_ROLE`. The least-destructive correction is a narrow, receipt-backed replacement of that exact invalid version: preserve its exact bytes under canonical cleanup evidence, restore aggregate currentness through the registry control surface, publish a role-correct Prime Builder version 013 `NO-ACTION` that rejects versions 011 and 012 without closing WI-5617, and route that replacement to a distinct Loyal Opposition session for version 014 `NO-GO`. No WI-5617 source, test, project, dispatcher, or TAFE mutation belongs to this repair.

## Defect / Reproduction

Read-only reproduction on branch `research` at HEAD `75decbfa704fe50288aecbc5669def329a0825df`:

1. `gt bridge show gtkb-dispatcher-next-foundation-spike --json` reports physical version 013 as the latest file and its first-line status as `VERIFIED`.
2. Direct strict resolution with `scripts/bridge_lifecycle_resolver.py::resolve_bridge_lifecycle()` fails with code `WRONG_STATUS_AUTHOR_ROLE`, path `bridge/gtkb-dispatcher-next-foundation-spike-013.md`, and version 13.
3. Version 013 declares `author_identity: prime-builder/goose/G`, `author_harness_id: G`, `::init gtkb pb`, and first-line status `VERIFIED`. Prime Builder is prohibited from authoring that status.
4. Exact current hashes are:
   - version 011: `2A3AAE14FA671D7D3FBFF8E6F8F01EF017723F6457091B13563C30D93C84EEDD`;
   - version 012: `70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12`;
   - invalid version 013: `ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D`.
5. Version 011 is a Prime `NO-ACTION` that claims an owner-selected rehome and attempts to close the v010 blocker. Version 012 is an LO `GO` accepting that disposition. Neither is implementation evidence, and version 012's applicability assertions do not make a later PB-authored terminal status lawful.
6. Canonical backlog state still records WI-5617 open/backlogged with no completion evidence. Its five source/test targets are clean, its sixth proposed requirements manifest is absent, and TEST-11662 has no bound result. No scoped atomic terminal commit exists.
7. The cleanup-evidence destination declared in this proposal is absent. The invalid version 013 is untracked and has no consumed publication receipt; the prior version 012 has a consumed receipt. These facts must be revalidated immediately before any recovery mutation.

This is a governance-chain defect, not permission to rewrite history or normalize the invalid bytes in place.

## In-Root Placement Evidence

All targets are inside `E:\GT-KB`. The invalid bytes move only to `bridge/cleanup-evidence/`, a canonical in-root non-actionable evidence surface. No live dependency is created outside the project root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - status-role authority, append-only numbered history, independent review, and fail-closed correction govern the repair.
- `GOV-ARTIFACT-APPROVAL-001` - the formal bridge and MemBase targets remain gated by active PAUTH, independent GO, exact claim, and a fresh start packet.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - the replacement v013 is a nonterminal Prime correction carrier and must receive an independent LO response.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - aggregate currentness must be reconciled through canonical registry services after the evidence-preserving move.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - invalid bytes are preserved as governed incident evidence and the derived defect is tracked as WI-5879.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal supplies concrete controlling links before any mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal review must execute TEST-11807's exact chain, receipt, hash, and nonimpairment assertions.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5879 is an active atomic member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY.
- `SPEC-AUQ-POLICY-ENGINE-001` - no new owner choice is inferred; this repair follows the existing owner directive and active project authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - every target and evidence path remains under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - the newly observed defect was captured as WI-5879 rather than hidden in scratch state.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - native Windows execution self-enforces the same GO/claim/start boundary when hooks cannot do so.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair preserves a durable proposal, evidence copy, receipts, report, and verdict trail.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the invalid terminal observation triggered a distinct governed defect cycle rather than an in-place edit.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner-directed Dispatcher Next program and non-self-review constraints.
- `DELIB-202667082` - independent WI-5617 NO-GO history remains evidence and may not be erased by the later malformed close.
- `DELIB-202667724` - original whole-project Bridge Protocol Reliability grant.
- `DELIB-202667732` - active v2 project authorization repair and operation-time authority.
- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` - coordinate by exact thread/row CAS, not a global single-writer rule.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` v2 is active, list-free, unexpired, and controlled by `DELIB-202667732`.
- The owner has directed continued autonomous construction of Dispatcher Next, correction of governance blockers, preservation of unrelated work, and high-parallel SoT coordination without global MemBase serialization.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-APPROVAL-001`,
`DCL-NO-ACTION-STATUS-SEMANTICS-001`, and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` already define the role/status boundary,
independent review, exact governed authorization, nonterminal correction, and
canonical currentness obligations needed for this repair. WI-5879 and
TEST-11807 translate those controls into exact hash, receipt, claim,
crash-safety, and nonimpairment acceptance. This proposal corrects a breach of
existing governance; it does not introduce a new product or authority model.

## Proposed Scope

### Authorized implementation sequence after independent GO

1. Revalidate the exact three targets, active PAUTH v2, WI-5879 membership, strict resolver error, v013 hash, receipt state, foreign claims, and cleanup-destination absence.
2. Acquire an exact `go_implementation` claim for the WI-5879 thread and finalize a fresh schema-v3 implementation-start packet before any target mutation.
3. Acquire a separate ordinary draft claim for the victim slug `gtkb-dispatcher-next-foundation-spike` under the same PB session. If any other holder exists, stop before moving bytes. This is exact-thread coordination, not global MemBase serialization.
4. Recheck that victim version 013 still hashes exactly `ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D` and that the evidence destination is absent.
5. Move, without content change, the invalid v013 to `bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/`. The move is recoverable evidence preservation, not deletion or destructive cleanup. Never overwrite either side.
6. Invoke the canonical registry observation/control service for `bridge-versioned-files` to record the truthful post-move aggregate. No raw SQLite write or forced database edit is allowed.
7. Reclassify the same victim-thread session claim for a Prime `NO-ACTION` publication only after physical latest is again v012 `GO`. Revalidate the claim, transition, predecessor hash, target absence, PAUTH, and registry currentness.
8. Publish replacement `bridge/gtkb-dispatcher-next-foundation-spike-013.md` through the governed bridge writer. It must be Prime-authored `NO-ACTION`, respond exactly to v012, cite the preserved invalid-byte evidence, reject v011/v012 as closure authority, keep WI-5617 open, and authorize no source/test/project or dispatcher mutation.
9. Read back exact bytes, consumed receipt/capability, strict resolver state, claims, hashes, aggregate currentness, and WI-5617 open status. Release only claims the implementation session owns.
10. Route the replacement v013 to a distinct Loyal Opposition session for independent v014 `NO-GO`. The LO file is not a PB implementation target; the WI-5879 report must wait for its canonical receipt-backed readback.
11. File a factual WI-5879 implementation report. Independent WI-5879 verification and any Git finalization remain separate; the preserved foreign `.git/index.lock` must not be removed or bypassed.

### Explicit exclusions

No change to WI-5617 source, tests, missing requirements manifest, project membership, PAUTH, TAFE, dispatcher configuration/runtime, credentials, deployment, release, Git history, or the foreign index lock. No overwrite, raw SQL, manual capability mint, manual receipt insertion, or broad repository/MemBase lock.

## Specification-Derived Verification Plan

| Requirement | Verification evidence | Pass condition |
| --- | --- | --- |
| Role-correct authority | strict resolver plus first-line/author metadata inspection | replacement v013 resolves as Prime `NO-ACTION`; independent v014 resolves as LO `NO-GO`; no wrong-role diagnostic |
| Exact evidence preservation | SHA-256 both archive copy and pre-repair v013 evidence | archive hash equals `ECDF0876...E42870D`; no byte loss or overwrite |
| Receipt-backed publication | canonical capability/receipt readback | replacement v013 and v014 each have one consumed receipt for exact bytes; no recovery-required or duplicate row |
| Append-only correction | chain inventory and `Responds to` checks | v001-v012 unchanged; replacement v013 responds to v012; v014 responds to replacement v013 |
| Nonterminal WI semantics | `gt backlog show WI-5617` and bridge resolution | WI-5617 remains open/backlogged with no completion evidence and latest victim status is `NO-GO` |
| Exact-thread concurrency | claim history and negative collision test | move occurs only while this session holds both exact claims; foreign holder causes zero target mutations |
| Crash safety | injected stop after move and before replacement, then governed resume | original bytes remain in cleanup evidence, victim claim prevents a competing append, and resume produces one replacement only |
| Source/dispatcher nonimpairment | hashes/status/diff for WI-5617 cohort and dispatcher/TAFE readback | no source, test, project, dispatcher, TAFE, or foreign-lock mutation |
| SoT freshness | canonical registry currentness/aggregate readback | registry records each physical state through supported services and reports current after the completed repair |
| Linked acceptance | TEST-11807 assertion result | exact expected outcome passes with timestamped evidence |

## Acceptance Criteria

1. Independent Loyal Opposition issues GO on this exact proposal before any three-target mutation; PB then holds an exact WI-5879 claim and a fresh successful schema-v3 start packet.
2. The invalid v013 exact bytes are preserved once at the declared cleanup path, with the stated SHA-256, and the original path is never overwritten while those bytes remain there.
3. Versions 001 through 012 remain byte-for-byte unchanged.
4. Replacement victim v013 is a receipt-consumed, role-correct Prime `NO-ACTION` responding to v012 and explicitly denying that v011/v012 or the quarantined invalid v013 closed WI-5617.
5. A distinct LO session publishes receipt-consumed v014 `NO-GO`; strict lifecycle resolution has no structural ambiguity or wrong-role error.
6. WI-5617 remains open/backlogged with no completion evidence, TEST-11662 is not fabricated, and the missing requirements manifest is not manufactured.
7. TEST-11807 passes, including collision, crash-resume, hash, receipt, currentness, and nonimpairment evidence.
8. No unrelated worktree path, foreign claim, `.git/index.lock`, dispatcher, TAFE, project/PAUTH record, source, or test is changed.
9. A factual implementation report records exact commands, hashes, row IDs, capability/receipt IDs, claims, start packet, and any interruption. It does not overstate terminality.
10. Only an independent WI-5879 verification and governed exact-set finalization may terminalize this repair work item.

## Risks / Rollback

- Crash after the move: the exact bytes remain recoverable under cleanup evidence and the victim-thread claim blocks a competing publication. Resume only after revalidating both claims and the fresh start authority.
- Concurrent publisher: any foreign victim claim, changed v013 hash, created destination, new receipt, changed predecessor, or aggregate drift aborts before mutation. Do not wait behind a global lock.
- Registry write contention: use generous externally governed waits and canonical retry/reobservation; never edit the SQLite file directly.
- Failure after actual publication: reread exact target bytes, receipt, capability, claim, and strict chain before retrying so an ambiguous success cannot create a duplicate.
- Rollback before replacement publication means leaving the exact invalid bytes preserved in cleanup evidence and reporting recovery-pending; do not restore an unlawful terminal file as authority. After replacement publication, correction is forward-only through the independent v014 response.
- Git finalization remains blocked while the foreign index lock exists. The repair may produce a truthful nonterminal implementation report, but it must not remove the lock, stage foreign bytes, or claim terminal completion.

## Files Expected To Change

- `bridge/gtkb-dispatcher-next-foundation-spike-013.md`
- `bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified`
- `groundtruth.db`

## Recommended Commit Type

`fix`
