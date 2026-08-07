REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6d5cabf5-dc7d-418a-a495-6f23186a6638
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role via ::init gtkb pb; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

# WI-5825 REVISED Implementation Proposal — Governed Recovery for Poisoned Publication-Capability Rows, Lawful Receipt Back-Fill for Unreceipted Chains, and Durable Compensation Context

bridge_kind: prime_proposal
Document: gtkb-wi5825-publication-capability-recovery-receipt-backfill
Version: 007
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-006.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5825

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This implementation performs no MemBase or KB mutation, write, insert, change or edit of any kind.

Scope confirmation: the five target_paths are unchanged from version 001 and from the version 006 GO cohort. All five are in-root platform surfaces, all five exist in the working tree, and all five were verified Git-clean by fresh read immediately before this filing. Two are source modules and three are existing test modules receiving test additions.

## Revision Disposition

Version 006 recorded an independent GO on the version 001 design and reaffirmed one non-technical condition: that WI-5825 implementation "cannot begin until WI-5812 lands through its own independent GO, fresh claim, start packet, and factual implementation report."

This revision changes exactly two things and nothing else:

1. **The WI-5812 implementation-sequencing gate is released**, on owner authority and on evidence that the gate's own stated premise is now false. Full analysis in the sequencing section below.
2. **An explicit implementation ordering is added** so Change B lands first with its own verification evidence, because Change B is the only change required to clear the live production blockers.

The Change A, Change B, and Change C designs are carried forward from version 001 unchanged in contract. No target path is added, removed, or broadened. No fail-closed control is relaxed. No new owner decision beyond the one recorded below is requested.

## Summary

WI-5825 is the backward-recovery carrier for bridge publication authority. It supplies three governed capabilities: clearing `recovery_required` and `compensated` capability rows through an exact-byte recovery path (Change A), lawful receipt back-fill for chains that were written outside the governed writer and therefore have no capability rows at all (Change B), and durable pending-publication context so compensation survives process death (Change C).

Change B is currently the sole lawful path out of a live production deadlock affecting at least two bridge threads. This revision releases the sequencing gate that has made that path unreachable.

## Problem Evidence (fresh canonical reads, 2026-08-06 UTC)

All evidence below was read directly this session from live state, not from prior reports.

### The live blocker is exactly three files

Direct query of `sot_registry_bridge_publication_capabilities` joined against `git ls-files` and `git status --short`:

| Thread | File | Git state | Capability row |
|---|---|---|---|
| WI-5841 | `bridge/gtkb-wi5841-harness-selector-registry-derived-015.md` | untracked | none |
| WI-5808 | `bridge/gtkb-wi5808-harness-probe-glm52-r3-003.md` | untracked | none |
| WI-5808 | `bridge/gtkb-wi5808-harness-probe-glm52-r3-001.md` | tracked, modified | none |

For WI-5841, versions 001-011 are tracked and clean, so they are never staged and the clearance gate never evaluates them. Versions 012, 013, 014, 016, 017, 018, 019 and 020 each hold a `consumed` row. Version 015 is the only staged path in that thread lacking a receipt.

For WI-5808 `gtkb-wi5808-harness-probe-glm52-r3`, versions 004 through 008 hold `consumed` rows; version 002 is tracked and clean.

### The previously reported stranded rows are already superseded

`_newest_exact_bridge_publication_capability` selects `ORDER BY rowid DESC LIMIT 1`. The two `recovery_required` rows reported by earlier verdicts are both shadowed by newer `consumed` rows for the same version:

- WI-5841 version 016: rowid 1266 `recovery_required` superseded by rowid 1268 `consumed`.
- WI-5841 version 020: rowid 1369 `recovery_required` superseded by rowid 1371 `consumed`.

Consequently Change A is not required to clear the current production blockers. It remains in scope as the durable fix for its own class, but it is correctly sequenced after Change B.

### The gap cannot be closed by republication or by existing recovery

- `mint_bridge_publication_capability` in `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` refuses when the target exists: `if target.exists() or target.is_symlink(): raise RegistryAuthorizationError(f"bridge publication target already exists: {relative}")`. Every affected file already exists on disk, so no mint is possible.
- The same function additionally requires `_bridge_publication_author_session(content) == session_id`, so a session that did not author the file cannot mint for it even if the file were absent.
- `recover_bridge_publication` requires an existing row and raises `exact bridge publication recovery row was not found` when none exists. It recovers crashed publications; it cannot serve a publication that never minted.

Change B (`backfill_bridge_publication_receipt`) is therefore the only designed lawful path, exactly as version 001 stated and version 006 independently accepted.

### Back-fill provenance does not depend on WI-5812

Each of the three affected files carries its own author provenance in its header, which is the value Change B records:

- `gtkb-wi5841-harness-selector-registry-derived-015.md`: `author_identity: prime-builder/goose`, `author_session_context_id: G-2026-08-04T22-30-56Z`
- `gtkb-wi5808-harness-probe-glm52-r3-003.md`: `author_identity: prime-builder/goose/G`, `author_session_context_id: G-2026-08-03T15-24-47Z`
- `gtkb-wi5808-harness-probe-glm52-r3-001.md`: `author_identity: prime-builder/goose/G`, `author_session_context_id: G-2026-07-30T19-27-10Z`

Back-fill reads author provenance from already-written content. It does not consume WI-5812's forward attestation surface.

### The five target paths are clean

`git status --short` over the five declared targets returned no output at filing time.

## Sequencing Disposition — Release Of The WI-5812 Gate

### What the gate said and why

Version 001 conditioned implementation on WI-5812 landing first. Its stated rationale, verbatim, was that WI-5812's "implementation is in flight NOW" and that "racing the two implementations would create exactly the cross-thread target churn this program is correcting." The same section recorded two qualifications that govern this revision:

- "No target_paths overlap. WI-5812's eight paths ... are disjoint from this proposal's five paths; the sequencing constraint is temporal, not a file-collision resolution."
- Loyal Opposition was explicitly asked to confirm whether the sequencing note satisfied collision-avoidance expectations.

The gate was therefore a temporal race-avoidance measure, self-described as not a file-collision resolution.

### Why the premise no longer holds

1. **WI-5812 is not in flight and cannot begin.** Its own GO'd proposal, `bridge/gtkb-wi5812-goose-governed-filing-attestation-013.md`, makes WI-5723 completion a hard prerequisite. Acceptance Criterion 1 requires that "WI-5723 has completed its governed implementation and independent VERIFIED cycle", and its F1 sequencing contract states that until then "WI-5812 is not implementation-ready."
2. **WI-5723 is itself only at proposal GO.** `bridge/gtkb-wi5723-session-resolver-fallback-removal-010.md` is a GO on the version 009 proposal dated 2026-08-05. There is no implementation report and no VERIFIED. That GO further preserves a dependency: "WI-5653 exact-session rebind work remains a prior dependency for the shared envelope lane."
3. **WI-5653 has no bridge thread at all.** No `bridge/*wi5653*` file exists; the work item is open at P2 with no proposal.
4. **The target sets remain disjoint**, as version 001 asserted and version 006 independently confirmed ("its eight targets are disjoint").
5. **The asserted technical coupling does not apply to back-fill.** Version 001 justified coupling on the ground that "the back-fill path (Change B) records author-session provenance that WI-5812's attestation surface defines for harness G." For files already written, that provenance is read from the file's own header, as shown in the Problem Evidence above.

Holding the gate therefore blocks WI-5825 behind five governed cycles (WI-5653 proposal, WI-5723 implementation and verification, WI-5812 implementation and verification, then WI-5825) while protecting against a race that cannot occur and a collision that the design already excludes.

### What replaces it

The gate is replaced with a narrower, mechanically checkable condition that preserves the collision-avoidance intent:

1. Immediately before the implementation-start packet, Prime Builder rereads the WI-5812 and WI-5723 bridge heads and their claims. If either thread has become an in-flight implementation holding a live claim, or has acquired a live GO over any of WI-5825's five target paths, WI-5825 fails closed and returns to revision.
2. Prime Builder rereads the five target paths for Git-clean state and matching hashes at implementation-start; any foreign dirty state fails closed.
3. WI-5825 absorbs no WI-5812, WI-5723, WI-5653 or WI-5880 scope. Its diff must remain inside the five declared paths, and diff inspection is an acceptance criterion.

This condition is strictly stronger than the original at the moment that matters (implementation-start readback of live claims and live GO overlap) and does not impose an unbounded ordering dependency on threads that cannot proceed.

## Proposed Design

Three changes, carried forward from version 001 unchanged in contract, all confined to the five target_paths. Recovery is deterministic service code, never conversational repair (SPEC-1830, GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001).

### Implementation ordering (new in this revision)

Implementation proceeds Change B, then Change A, then Change C. Change B is the only change required to clear the live blockers, so it lands first with its own executed test evidence recorded in the implementation report. Change A and Change C follow in the same governed cycle. The implementation report must present per-change test evidence so a reviewer can evaluate each change on its own merits.

### Change B (scope b) — lawful receipt back-fill for unreceipted Prime-authored chains

New control-plane function `backfill_bridge_publication_receipt` in `registry_control_plane.py`, exposed to operators through the writer module.

- **Preconditions (all fail-closed):** the target resolves under `bridge/` via the existing `_bridge_publication_target` binding; the file exists on disk as a regular file; its first non-blank line is a canonical status token; NO capability row exists for the exact `(aggregate_entry_id, target_path)` pair, so the function refuses to shadow any existing row (poisoned rows remain Change A's jurisdiction, and newest-row-wins clearance semantics must never be used to paper over a real row); a non-empty `authorization_evidence` string cites the authorizing owner decision and bridge GO; the invoking session holds the live work-intent claim for the document, or the claim-holder gate is explicitly recorded as a back-fill exemption in the audit trail.
- **Attested provenance instead of author-session equality.** The normal mint path's author-session binding is precisely why a finalizing session cannot mint receipts for another session's files. Back-fill records both identities truthfully: the file's `author_session_context_id` extracted from its on-disk content, stored in the row's `author_session_context_id` column exactly as mint would have, and the invoking session in `claim_session`, plus the `authorization_evidence` in `change_reason`. Nothing is fabricated. The author-session-equality gate on the normal mint path is not touched and continues to reject live cross-session minting.
- **Receipt creation:** in one locked control-plane transaction, insert a single row with `authority_kind = 'bridge_publication'`, `operation = 'bridge_publication'`, `content_digest` equal to the hash of the on-disk bytes, a compliance digest computed by a fresh bridge-compliance audit against the chain-prefix operative head for that version, `capability_state = 'consumed'`, `consumed_at` set, and a same-transaction appended aggregate revision (`evidence_view = "receipt_backfill"`) providing `revision_id` and `result_digest`. Standard `authority_kind` and `operation` values mean `_bridge_publication_capability_clearance` accepts the receipt with zero changes to `scripts/check_protected_commit_authorization.py`; the back-fill stays distinguishable in audit through `evidence_view` and `change_reason`.
- **Chain ordering:** a convenience wrapper back-fills a chain oldest-first so each version's compliance binds to a fully receipted prefix; per-file back-fill remains available for single-gap chains.

### Change A (scope a) — governed clearing of `recovery_required` and `compensated` rows with correct-operative-head republish

A1. **Control plane: make `recovery_required` a recoverable source state.** Extend `recover_bridge_publication`:

- `mode="finalize"` additionally accepts `capability_state = 'recovery_required'` when the exact target file is retained on disk and its bytes hash to the row's `content_digest`. Because the recorded `aggregate_preimage_digest` is unprovable once siblings advanced the aggregate, the `recovery_required` finalize branch replaces the stale-preimage proof with the same two-read stable-observation discipline the existing finalize branch already uses: observe aggregate, re-verify target bytes, observe again. It appends a `bridge_publication` revision observing the aggregate's live current head (`evidence_view="recovery"`, `evidence_source_reference=capability_hash`), then transitions the row from `recovery_required` to `consumed` under a race-guarded state-bound UPDATE, setting `consumed_at`, `result_digest`, `revision_id`, and `failure_reason = NULL`.
- `mode="rollback"` additionally accepts `capability_state = 'recovery_required'` when the target file is absent, or present only as an exact-byte quarantine: it appends a compensation revision at the live current head and transitions the row to `compensated`, closing rows whose file genuinely should not exist.
- Both branches require a non-empty `change_reason` citing the authorizing evidence, being this bridge thread plus the PAUTH triple. The transition is recorded in the append-only `sot_artifact_revisions` history, so the poisoned episode remains fully audit-visible. Clearing is a forward state transition, never history erasure.

A2. **Writer: exact-byte republish for `compensated` rows computes compliance against the correct operative head.** Add a `republish` entrypoint to `scripts/gtkb_bridge_writer.py`, a thin mode of `write_bridge_file`, for the case where a compensated file was removed and must be restored byte-exactly. It requires the newest exact capability row for the target to be `compensated`, requires the supplied bytes to hash to that row's `content_digest`, and runs the bridge-compliance audit with the operative head pinned to the chain prefix that governs version N, being the version-(N-1) predecessor in the same numbered chain, not the thread tail scanned at recovery time. The republish then mints and consumes a fresh capability through the normal single-use lifecycle; the historical compensated row is left untouched as append-only audit history.

### Change C (scope c) — pending-publication context survives process death

- `rollback_pending_bridge_publication` and `finalize_pending_bridge_publication` in `scripts/gtkb_bridge_writer.py` gain a third resolution tier: in-memory map, then sidecar, then durable capability-row fallback. When both process-local tiers are missing, resolve the newest exact capability row by `target_path` plus the session id extracted from the on-disk file's author metadata, and drive `recover_bridge_publication` from the row alone, whose `expected_*` parameters are already optional. `BRIDGE_PUBLICATION_REPAIR_REQUIRED: pending capability context is unavailable` is raised only when no row exists at all, and that terminal case now has a lawful answer through Change B.
- The existing sidecar-before-file-create ordering in `write_bridge_file` is pinned by a crash-ordering regression test: whenever the target exists and a row is minted, recovery context is durably resolvable.
- No new hard-coded timer, TTL, interval, or retry literals are introduced anywhere in this design; recovery reuses the existing capability TTL and lock-timeout constants unchanged.

### Explicitly rejected alternatives

- **Shadow-row clearing for `recovery_required` rows** (insert a fresh consumed row that wins newest-by-rowid, leaving the poisoned row untouched): rejected as primary because it makes newest-row-wins clearance semantics load-bearing for correctness and leaves two live rows for one publication. It is retained only as the natural by-product of Change A2's fresh mint on compensated-and-removed files, where the old row is genuinely historical.
- **Relaxing `_bridge_publication_capability_clearance` to accept `recovery_required` rows:** rejected, because it would convert a truthful fail-closed deny into silent acceptance of unrecovered anomalies.
- **Mint bypass of the author-session gate:** rejected, because that gate is a live anti-fabrication control. Change B adds a distinct, attested, audit-visible operation instead of weakening the existing one.
- **Store the capability secret durably to enable replayed consume:** rejected. Secrets stay memory-only; every durable recovery path operates on the hash-keyed row without exposing the secret, exactly as `recover_bridge_publication` does today.
- **A new bridge thread implementing back-fill outside WI-5825:** rejected. It would duplicate WI-5825's carrier against `GOV-STANDING-BACKLOG-001` non-duplication and would strand the version 006 GO. Revising WI-5825 is the correct governed shape.
- **Waiting out the WI-5653 to WI-5723 to WI-5812 chain:** rejected on the evidence in the sequencing section, and superseded by the owner decision recorded below.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs bridge publication authority, the append-only numbered bridge file chain, permanent bridge repair authority, and the audit-trail durability this recovery design serves; WI-5825's source spec.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal's obligation to cite all governing specifications concretely.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED is conditional on executed spec-derived tests; satisfied by the Specification-to-Test Mapping below.
- `GOV-ARTIFACT-APPROVAL-001` — the owner decision cited below was recorded as a Deliberation Archive artifact through the formal-artifact approval gate with a matching approval packet; the proposed implementation mutates no formal artifact.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — this work proceeds under the active list-free PAUTH cited in the header plus this thread's future GO; PAUTH metadata does not broaden target_paths and does not replace the live latest-GO requirement.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — current project authorization controls at operation time rather than legacy per-work-item approval metadata.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item, and exact target linkage carried in this header.
- `GOV-17` — automation script modification approval gate: `scripts/gtkb_bridge_writer.py` is publication automation; this proposal plus Loyal Opposition GO under the cited project authorization is the approval evidence for modifying it.
- `GOV-10` — tests exercise exposed production interfaces (`recover_bridge_publication`, `backfill_bridge_publication_receipt`, `write_bridge_file` republish mode, the pending finalize and rollback helpers, and the protected-commit clearance evaluation), never private re-implementations.
- `SPEC-1830` — operational procedures must be code, not conversation; recovery is deterministic service code.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — repeatable recovery belongs in deterministic services rather than per-incident session repair.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every state claim in this revision derives from a fresh canonical read performed this session.
- `GOV-STANDING-BACKLOG-001` — WI-5825 remains the single non-duplicated carrier for publication recovery; no sibling carrier is created.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets and generated bridge artifacts remain in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory durable traceability of the sequencing decision.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory specification, test, and evidence linkage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory GO to REVISED lifecycle transition recorded here.

## Prior Deliberations

- **DELIB-20260806011613** (Owner releases the WI-5812 sequencing gate on WI-5825 and authorizes receipt back-fill as the coded alternate): the owner decision authorizing this revision, recorded 2026-08-06 with approval packet `.groundtruth/formal-artifact-approvals/2026-08-06-DELIB-20260806011613.json` and content hash `5caa725a8c543c715a7ab1165e6d71c51b7f22873f9d07179cbbb3eacfa978c5`, which already exists on disk and is not created, modified, or required by this filing or its implementation.
- **DELIB-202668125** (Loyal Opposition GO, WI-5825 corrected nonterminal review): the version 006 GO record whose sequencing condition this revision addresses.
- **DELIB-20260805195214** (Owner by-reference finalization waiver): established that the waiver removes the HEAD-clean target-include obligation but does not create publication receipts, which is the finding that isolates receipt back-fill as the remaining blocker.
- **DELIB-20260803084763** (Timer bound and TTL raise): the independently cured `evaluation_bound` blocker, no longer operative.
- **DELIB-202667731** (Harness Test Corrections whole-project authorization): owner grant of the PAUTH cited in this header.
- **DELIB-202667730** (Harness Test final synthesis): the evaluation synthesis whose VERIFIED-stumble diagnoses produced WI-5825's three-gap defect record.
- **DELIB-202667722** (Timer and throttle governance): the no-new-hard-coded-timer constraint honored explicitly in Change C.
- **DELIB-202667533** (Advisory-triage synthesis AT-01..04): commit-first finalization ordering, preserved by this recovery layer.
- **DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD** — active project members inherit project authority; legacy approval metadata is not authority.

## Owner Decisions / Input

1. **AskUserQuestion, 2026-08-06, path selection.** Question: given that WI-5812 requires WI-5723 VERIFIED, WI-5723 requires WI-5653, and WI-5653 has no bridge thread, which direction should Prime Builder take? Owner answer: **"Coded alternate for receipts"** — take the escape hatch recorded in `bridge/gtkb-wi5841-harness-selector-registry-derived-020.md` Finding 1, probe the receipt mechanism, then file one proposal that durably fixes the receipt class for both WI-5841 and WI-5808.
2. **AskUserQuestion, 2026-08-06, deliberation approval.** Question: approve inserting DELIB-20260806011613 as the durable owner-decision record authorizing this REVISED? Owner answer: **"Approve as written"** — write the approval packet, insert the deliberation, link it to WI-5825, then proceed to the REVISED; those steps completed before this filing and are not part of this proposal's implementation scope. Executed: deliberation inserted at rowid 13554 with `outcome=owner_decision`, `source_type=owner_conversation`, `work_item_id=WI-5825`.
3. **AskUserQuestion, 2026-08-06, implementation scope.** Question: what implementation scope should the WI-5825 REVISED carry? Owner answer: **"Full 3-change design, Change B first"** — keep Change A, B and C intact against the same five GO'd target paths, and state an explicit implementation ordering that lands Change B first with its own verification.
4. **DELIB-202667731** supplies the active list-free whole-project PAUTH inherited by active member WI-5825. No per-work-item approval field creates a second gate.
5. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This proposal does not activate, dispatch through, configure, or mutate either.

No further owner decision is requested by this filing.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5825 defect description, `GOV-FILE-BRIDGE-AUTHORITY-001`, `SPEC-1830`, `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`, the linked test TEST-11781's expected outcome, the version 006 GO, and the owner decision recorded at DELIB-20260806011613 provide complete requirements for this implementation. No new or revised specification is required before implementation.

## Specification-to-Test Mapping

Linked test of record: **TEST-11781** ("Compensated rows clear via governed republish and unreceipted chains gain a lawful receipt path", spec_id `GOV-FILE-BRIDGE-AUTHORITY-001`). Expected outcome, verbatim: "A recovery_required row can be cleared by a governed republish that computes compliance against the correct operative head; an unreceipted Prime-authored chain can be receipted through an authorized back-fill path; finalization succeeds afterward."

| Requirement source | Behavior under test | Test coverage |
|---|---|---|
| TEST-11781 clause 2 / `GOV-FILE-BRIDGE-AUTHORITY-001` (Change B, lands first) | An unreceipted Prime-authored chain fixture gains consumed receipts oldest-first through `backfill_bridge_publication_receipt` with recorded author-session, invoker-session, and authorization evidence; existing-row, bad-status, non-bridge-path, absent-file, and missing-authorization paths fail closed | `groundtruth-kb/tests/test_registry_control_plane.py` (new back-fill cases) |
| TEST-11781 clause 3 ("finalization succeeds afterward"), Change B slice | After back-fill on a fixture chain with a single receipt gap, `_bridge_publication_capability_clearance` returns clear for every staged chain path with `scripts/check_protected_commit_authorization.py` unmodified | `platform_tests/scripts/test_check_protected_commit_authorization.py` (new post-back-fill clearance cases) |
| TEST-11781 clause 1 (Change A1) | A fixture `recovery_required` row with retained exact-byte target clears via `recover_bridge_publication(mode="finalize")`: the row becomes `consumed` with `consumed_at`, `result_digest` and `revision_id` set and `failure_reason` NULL; the appended revision observes the live head; wrong-byte and absent-target paths still fail closed | `groundtruth-kb/tests/test_registry_control_plane.py` (new `recovery_required` finalize and rollback cases) |
| TEST-11781 clause 1 (Change A2) | Exact-byte republish of a compensated-and-removed file passes compliance computed against the version-(N-1) chain-prefix operative head and fails when computed against the advanced tail; byte-mismatch republish is refused | `platform_tests/scripts/test_gtkb_bridge_writer.py` (new republish cases) |
| TEST-11781 clause 3, full mixed fixture | After Change A clearing plus Change B back-fill on a mixed fixture chain, the registry-commit assessment reports no bridge-publication findings | `platform_tests/scripts/test_check_protected_commit_authorization.py` (mixed-fixture clearance case) |
| WI-5825 scope (c) / DELIB-202667533 commit-first ordering (Change C) | With fresh module state and the sidecar deleted, rollback and finalize resolve recovery from the durable capability row; with no row at all the fail-closed REPAIR_REQUIRED message is preserved; sidecar-before-create ordering is pinned | `platform_tests/scripts/test_gtkb_bridge_writer.py` (new crash-survival cases) |
| DELIB-202667722 (timer discipline) | The diff introduces zero new hard-coded timeout, TTL, interval or retry literals | assertion inside the new writer test module cases |
| Sequencing replacement condition (this revision) | Implementation-start readback rejects when WI-5812 or WI-5723 holds a live claim or a live GO overlapping any of the five target paths | recorded as executed implementation-start evidence in the implementation report |

## Acceptance Criteria

1. An unreceipted fixture chain gains lawful consumed receipts recording true author-session, invoker-session, and authorization evidence; no existing row is ever shadowed or mutated by back-fill.
2. After back-fill, protected-commit clearance passes for every staged chain path with `scripts/check_protected_commit_authorization.py` unmodified.
3. Every `recovery_required` fixture row with a retained exact-byte target can be cleared to `consumed` through the governed finalize path.
4. Exact-byte republish of a compensated fixture file succeeds with compliance computed against the correct version-prefix operative head, minting a fresh consumed row; the historical compensated row is untouched.
5. Whole-chain finalization succeeds after recovery plus back-fill on the mixed fixture.
6. Compensation and finalization survive process death: durable-row fallback recovers when both the in-memory map and the sidecar are gone; the REPAIR_REQUIRED fail-closed message survives only for the genuinely-unknown no-row case.
7. All fail-closed rejections named in the design are covered by executed rejection-path tests; no existing rejection is weakened, and the normal mint path's author-session-equality gate is unchanged.
8. `ruff check` and `ruff format --check` pass clean on all five target paths.
9. `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` passes green, with per-change collection counts recorded in the implementation report.
10. Zero new hard-coded timer, TTL, interval or retry literals in the diff.
11. Only the five declared paths change; diff inspection proves no WI-5812, WI-5723, WI-5653 or WI-5880 implementation entered them.
12. At implementation-start, fresh readback confirms neither WI-5812 nor WI-5723 holds a live claim or a live GO overlapping the five target paths, and all five paths are Git-clean with matching hashes; any drift fails closed and returns this thread to revision.

## Risk and Rollback

- **Risk: recovery becomes a laundering path for bad publications.** Mitigated: Change A finalize demands exact-byte identity with the recorded `content_digest`; Change B refuses to shadow existing rows, demands explicit authorization evidence, and records both identities truthfully; every recovery appends an audit revision; nothing relaxes the clearance gate itself.
- **Risk: releasing the sequencing gate permits a real collision.** Mitigated: the replacement condition performs live claim and live-GO overlap readback at implementation-start, which is strictly more current than a static ordering assertion made at proposal time. The target sets are disjoint by independent confirmation in version 006.
- **Risk: current-head observation races a concurrent publication.** Mitigated: all recovery and back-fill work runs under the existing `_RegistryFileLock` plus `BEGIN IMMEDIATE` discipline with the two-read stable-observation pattern already used by finalize; race-guarded state-bound UPDATEs preserve single-use semantics.
- **Risk: operative-head pinning computes the wrong prefix.** Mitigated: the pin derives mechanically from the numbered chain, where version N binds to N-1; tests assert both the passing prefix computation and the failing tail computation.
- **Risk: WI-5812 later lands and expects a different provenance shape.** Mitigated: back-fill reads provenance from already-written file content and does not depend on the forward attestation surface, so WI-5812 can land afterward without reworking receipts already written.
- **Rollback:** revert the two source-file diffs and the test additions. All Change A, B and C behaviors are additive branches and new functions; the pre-change fail-closed behaviors are preserved verbatim underneath and re-emerge on revert. Bridge files remain append-only evidence; capability rows already transitioned by executed recoveries remain truthful history and require no rollback.

## Recommended Commit Type

Recommended commit type: `fix` — repairs broken recovery behavior (terminal receipt deadlock, poisoned rows, process-death compensation loss) with regression coverage; no new capability surface beyond the recovery entrypoints the defect requires.

## DISARM — KB Mechanics

The proposed implementation mutates no MemBase artifact records. No specifications, tests-of-record, work items, deliberations, documents, or other managed KB artifacts are created, updated, or retired by the proposed implementation. The implementation's writes are confined to the control-plane runtime-evidence tables (`sot_registry_bridge_publication_capabilities`, `sot_artifact_revisions`) inside the existing locked, race-guarded control-plane transaction discipline — publication evidence, not managed artifact content. The `kb_mutation_in_scope: false` flag reflects that boundary. The deliberation cited in the Owner Decisions section was inserted before this filing through the governed formal-artifact approval gate with a matching approval packet, and is referenced here as pre-existing evidence, not as a mutation performed by this proposal or its implementation.

## DISARM — Packet Mechanics

References to the implementation-start packet in this document are descriptive of the governed cycle, not packet operations performed by this filing. The packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5825-publication-capability-recovery-receipt-backfill`, run only after an independent Loyal Opposition GO on this revision) is session-local implementation-scope evidence: it derives from bridge state, the approved proposal file, and the GO verdict file; it expires and fails closed on bridge status drift. It is not a formal artifact under `GOV-ARTIFACT-APPROVAL-001` and does not require a separate approval packet. The PAUTH triple in this header supplies the project-authorization evidence the packet validator requires; it does not replace the bridge GO, the claim, or the packet itself.

## DISARM — Capability Mechanics

This document necessarily discusses publication-capability minting, consumption, compensation, recovery, and receipts throughout; all such discussion is design description of the target subsystem. This filing itself performs exactly one capability operation: the single governed mint-and-consume executed by the bridge writer to publish this proposal file. No recovery, back-fill, clearing, or republish operation is performed by this filing; those operations exist only after GO, implementation, and verification. No capability secret is recorded in this document or in any artifact this design produces.

## Loyal Opposition Asks

1. **Sequencing release.** Evaluate whether the evidence in the sequencing section supports releasing the WI-5812 gate: the gate's own text calls the constraint temporal rather than collision-based, the target sets are disjoint by version 006's independent confirmation, and WI-5812 is unreachable behind WI-5723 and WI-5653. If the replacement implementation-start readback condition is insufficient, state the concrete stronger condition required.
2. **Change B claim gate.** Should back-fill require the invoker to hold the live work-intent claim for the document, or is the recorded back-fill exemption with authorization evidence the better audit shape for chains whose original claims are long expired? This ask is carried forward unresolved from version 001.
3. **Change A1 proof floor.** Is exact-byte identity plus two-read stable observation an acceptable proof floor for `recovery_required` finalize, given the recorded preimage is unprovable once siblings advance the aggregate?
4. **Operative-head pinning.** Confirm version-(N-1) chain-prefix resolution is the correct reading of TEST-11781's "correct operative head".
5. **Implementation ordering.** Confirm that landing Change B first, with per-change test evidence in the implementation report, is acceptable within a single governed cycle.
6. GO only if the specification linkage, spec-to-test mapping, fail-closed preservation, sequencing evidence, and append-only claims withstand inspection; otherwise NO-GO with concrete findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
