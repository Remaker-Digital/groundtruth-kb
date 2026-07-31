NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code dispatched proposal-author worker; transcript-resolved role prime-builder; GT-KB Harness Test Corrections program leader dispatch per DELIB-202667735

# WI-5825 Implementation Proposal — Governed Recovery for Poisoned Publication-Capability Rows, Lawful Receipt Back-Fill for Unreceipted Chains, and Durable Compensation Context

bridge_kind: prime_proposal
Document: gtkb-wi5825-publication-capability-recovery-receipt-backfill
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5825

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Scope confirmation: this filing performs no MemBase artifact mutation and no approval-evidence work; it requires no approval packets. All five target_paths are in-root platform surfaces; all five exist in the working tree (each verified with a fresh read before filing). Two are source modules and three are existing test modules receiving test additions.

## Summary

Close the three linked recovery gaps in the bridge publication-capability lifecycle recorded by WI-5825:

(a) **Governed clearing of `recovery_required` and `compensated` publication-capability rows.** Rows poisoned by `BRIDGE_PUBLICATION_REPAIR_REQUIRED`-class failures are terminal today: no recovery mode accepts `capability_state = 'recovery_required'`, and an exact-byte republish of a compensated file cannot pass compliance because its embedded packet hash binds to the operative head that governed the original authoring, not the head a naive recompute scans at recovery time. This change adds a governed clearing path whose republish computes compliance against the correct operative head for the version being recovered.

(b) **Lawful receipt back-fill for unreceipted Prime-authored chains.** Chain files published outside the governed writer have no capability rows at all; VERIFIED finalization stages the whole untracked chain and fails closed on missing consumed receipts, while receipt minting is author-session-bound, so a Loyal Opposition session has no lawful way to create the missing receipts — a terminal deadlock. This change adds an explicitly-attested, audit-visible back-fill path.

(c) **Durable pending-publication context.** The residual in-memory-only pending-context window still raises "pending capability context is unavailable" when both the process-local map and the WI-5758 sidecar are missing; compensation must survive process death by falling back to the durable capability row itself.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state. Nothing in this design deletes or rewrites a bridge file, and nothing weakens the single-use capability model — every recovery outcome is a recorded state transition plus an append-only aggregate revision.

## Problem Evidence (fresh canonical reads, 2026-07-31 UTC)

All evidence is from fresh reads of the live tree and the control-plane tables at drafting time.

1. **Poisoned row (WI-5825 anchor, dsv4pro-r2b-006).** `sot_registry_bridge_publication_capabilities` holds `document_name = gtkb-wi5808-harness-probe-dsv4pro-r2b`, `version = 6`, `status = NO-GO`, `capability_state = 'recovery_required'`, `consumed_at = NULL`, `failure_reason = "bridge publication aggregate preimage cannot be restored exactly"` (capability_hash `sha256:999443c7736d7be95220ff7252923257d39d1e74a7cb22419cc0cef604b769b3`, created 2026-07-30T23:10:03Z). The published file `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2b-006.md` is retained on disk (untracked) and is a legitimate chain member — a real Loyal Opposition NO-GO verdict.
2. **The poison is population-scale, not a one-off.** Fresh state counts: 14 `recovery_required` rows, 18 `compensated`, 3 `expired`, 557 `consumed`. Same-day `recovery_required` examples include `gtkb-wi5688-terminal-finalization-recovery-014`, `gtkb-advisory-wi5368-cross-thread-target-collision-003/-006`, `gtkb-wi5758-publication-deadlock-closure-004` (the WI-5758 VERIFIED verdict itself), `gtkb-wi5759-ruff-gate-staged-blob-004`, and `gtkb-wi5783-protected-commit-fail-closed-staged-binding-008` — most with the identical failure reason "bridge publication aggregate preimage cannot be restored exactly".
3. **`recovery_required` is unreachable by every recovery mode.** `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`: `recover_bridge_publication` finalize accepts only `consumed` (idempotent) or `minted`/`expired` (line 3101-3102: "bridge publication cannot be finalized from {state}"); rollback accepts only `compensated` (idempotent) or `minted`/`expired`/`consumed` (line 3210-3211). No path accepts `recovery_required`; those rows are terminal by construction.
4. **The stale-preimage proof is the reason the rows can never self-heal.** Finalize requires `_bridge_aggregate_digest_without_target(...) == row["aggregate_preimage_digest"]` and `latest["content_digest"] == row["aggregate_preimage_digest"]` (lines 3105-3117). Once any sibling publication advances the aggregate — which happens within minutes on an active bridge — the recorded preimage is unprovable forever. The same predicate at compensation time (lines 3479-3496) is what minted the poison: "bridge publication aggregate preimage cannot be restored exactly".
5. **Poisoned rows break sibling finalizations of the same chain.** The r2b-008 VERIFIED verdict row was compensated with `failure_reason` capturing the finalization crash: `scripts/check_protected_commit_authorization.py` `_bridge_publication_capability_clearance` hit the 006 row's `consumed_at = NULL` and raised `AttributeError: 'NoneType' object has no attribute 'endswith'` inside `parse_iso`, failing the whole-chain commit. The working tree now guards that crash as a fail-closed deny (`scripts/check_protected_commit_authorization.py` lines 2028-2038, "bridge publication capability has incomplete or invalid timestamps"), but the deny is still terminal: there is no governed way to make the poisoned row clear.
6. **Unreceipted chain deadlock (r2b).** `bridge/gtkb-wi5808-harness-probe-dsv4pro-r2b-001/-003/-005/-007.md` exist on disk (untracked, `git status` verified) with NO capability rows — the control plane holds rows only for versions 2, 4, 6, 8. The Goose Prime Builder wrote them directly, outside the governed writer (the WI-5812 defect). VERIFIED finalization stages the whole untracked chain and `_bridge_publication_capability_clearance` denies each unreceipted path with "registered bridge path lacks exact publication capability evidence" (line 2010). Receipt minting cannot repair this: `mint_bridge_publication_capability` refuses when the target exists (line 2694-2695, "bridge publication target already exists") and refuses when the content's `author_session_context_id` differs from the claiming session (lines 2696-2698, "bridge author session and claim session differ") — so the Loyal Opposition session that must finalize has no lawful receipt path. Terminal deadlock.
7. **Manual incident handling is the current "procedure".** `bridge/cleanup-evidence/wi5671-unreceipted-publication-incident-20260730/`, `bridge/cleanup-evidence/wi5733-unreceipted-publication-incident-20260729/`, `bridge/cleanup-evidence/wi5368-unreceipted-v007-recovery-20260730/`, and `bridge/cleanup-evidence/dsv4pro-r2b-006-recovery-20260730/` each record hand-worked recoveries of this same failure class. SPEC-1830 requires operational procedures to be code, not per-incident lore.
8. **Residual in-memory pending-context window.** `scripts/gtkb_bridge_writer.py` `rollback_pending_bridge_publication` (lines 1108-1117): when the process-local `_PENDING_BRIDGE_PUBLICATIONS` entry is gone AND no pending sidecar exists, it raises `BRIDGE_PUBLICATION_REPAIR_REQUIRED: pending capability context is unavailable; file and claim are retained`. WI-5758 (VERIFIED at `bridge/gtkb-wi5758-publication-deadlock-closure-004.md`) added the secret-free sidecar under `.gtkb-state/bridge-publication-pending/` and `recover_bridge_publication`; the residual gap is every publication whose sidecar is missing (pre-sidecar history, sidecar deleted, or crash in the sidecar-lifecycle window). The durable capability row itself contains every binding recovery needs (`target_path`, `claim_session`, `content_digest`, `document_name`, `version`, `status`), and `recover_bridge_publication` already treats all `expected_*` parameters as optional — the writer just never falls back to it without a sidecar.

## Coordination With WI-5812 (Mandatory Sequencing)

WI-5812 ("Extend bridge author-metadata attestation and the governed filing path to the Goose harness") received GO at `bridge/gtkb-wi5812-goose-governed-filing-attestation-002.md` and its implementation is in flight NOW. WI-5812 is the forward fix: it makes future Goose publications flow through the governed writer so new unreceipted chains stop being created. WI-5825 is the backward fix: it recovers the poisoned rows and unreceipted chains that already exist and any that future crashes create.

Sequencing contract for this proposal:

- **Implementation of WI-5825 begins only after WI-5812's implementation lands** (its post-implementation report is filed and the shared surfaces are stable), even if this proposal receives GO first. Rationale: both work items operate on the governed-filing area; the back-fill path (Change B) records author-session provenance that WI-5812's attestation surface defines for harness G, and racing the two implementations would create exactly the cross-thread target churn this program is correcting.
- **No target_paths overlap.** WI-5812's eight paths (`cli_session_handoff.py`, `bridge_author_metadata.py`, `gtkb_session_id.py`, `goose_harness.py`, plus four test modules) are disjoint from this proposal's five paths; the sequencing constraint is temporal, not a file-collision resolution.
- Per the concurrent-target-overlap advisory lineage (`bridge/gtkb-lo-concurrent-go-target-overlap-advisory-001.md`), the Loyal Opposition reviewer is asked to confirm this sequencing note satisfies the program's collision-avoidance expectations.

## Proposed Design

Three changes, mapped one-to-one onto the WI-5825 scope letters. All changes are confined to the five target_paths. Recovery is deterministic service code, never conversational repair (SPEC-1830, GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001).

### Change A (scope a) — governed clearing of `recovery_required`/`compensated` rows with correct-operative-head republish

A1. **Control plane: make `recovery_required` a recoverable source state.** Extend `recover_bridge_publication`:

- `mode="finalize"` additionally accepts `capability_state = 'recovery_required'` when the exact target file is retained on disk and its bytes hash to the row's `content_digest`. Because the recorded `aggregate_preimage_digest` is unprovable once siblings advanced the aggregate (Problem Evidence 4), the recovery_required finalize branch replaces the stale-preimage proof with the same two-read stable-observation discipline the existing finalize branch already uses (observe aggregate, re-verify target bytes, observe again; lines 3118-3130 pattern): it appends a `bridge_publication` revision observing the aggregate's live current head (`evidence_view="recovery"`, `evidence_source_reference=capability_hash`), then transitions the row `recovery_required → consumed` under a race-guarded state-bound UPDATE, setting `consumed_at`, `result_digest`, `revision_id`, and `failure_reason = NULL`. The clearance gate in `scripts/check_protected_commit_authorization.py` then passes with zero changes to that script, because it already accepts any newest exact row that is `consumed` with complete timestamps, no failure reason, and a linked `bridge_publication` revision (lines 2028-2071).
- `mode="rollback"` additionally accepts `capability_state = 'recovery_required'` when the target file is absent (or present only as an exact-byte quarantine): it appends a compensation revision at the live current head and transitions `recovery_required → compensated`, closing rows whose file genuinely should not exist.
- Both branches require non-empty `change_reason` citing the authorizing evidence (this bridge thread + the PAUTH triple); the transition is recorded in the append-only `sot_artifact_revisions` history, so the poisoned episode remains fully audit-visible — clearing is a forward state transition, never history erasure.

A2. **Writer: exact-byte republish for `compensated` rows computes compliance against the correct operative head.** Add a `republish` entrypoint to `scripts/gtkb_bridge_writer.py` (a thin mode of `write_bridge_file`) for the case where the compensated file was removed and must be restored byte-exactly (source bytes from the rollback quarantine or cleanup-evidence capture): it requires the newest exact capability row for the target to be `compensated`, requires the supplied bytes to hash to that row's `content_digest`, and runs the bridge-compliance audit with the operative head pinned to the chain prefix that governs version N (the version-(N-1) predecessor in the same numbered chain), NOT the thread tail scanned at recovery time. This is the "correct operative head" behavior TEST-11781 requires: the file's embedded applicability packet hash was computed against its authoring-time operative head, and recomputing against the advanced tail is what makes exact-byte republish fail today (WI-5825 description, dsv4pro-r2b-006 evidence). The republish then mints and consumes a FRESH capability through the normal single-use lifecycle; the fresh consumed row becomes the newest exact row for the target, and the historical compensated row is left untouched as append-only audit history.

### Change B (scope b) — lawful receipt back-fill for unreceipted Prime-authored chains

New control-plane function `backfill_bridge_publication_receipt` in `registry_control_plane.py`, exposed to operators through the writer module:

- **Preconditions (all fail-closed):** the target resolves under `bridge/` via the existing `_bridge_publication_target` binding; the file exists on disk as a regular file; its first non-blank line is a canonical status token; NO capability row exists for the exact `(aggregate_entry_id, target_path)` (the function refuses to shadow any existing row — poisoned rows are Change A's jurisdiction, and the newest-row-wins clearance semantics must never be used to paper over a real row); a non-empty `authorization_evidence` string cites the authorizing owner decision / bridge GO; the invoking session holds the live work-intent claim for the document, or the claim-holder gate is explicitly recorded as a back-fill exemption in the audit trail (Loyal Opposition ask 2).
- **Attested provenance instead of author-session equality.** The normal mint path's author-session binding (mint lines 2696-2698) is the reason LO cannot mint receipts for Prime-authored files. The back-fill records BOTH identities truthfully: the file's `author_session_context_id` extracted from its on-disk content (stored in the row's `author_session_context_id` column, exactly as mint would have), and the invoking session in `claim_session` — plus the `authorization_evidence` in `change_reason`. Nothing is fabricated: the row says who authored and who back-filled, under what authority. The author-session-equality gate on the normal mint path is not touched and continues to reject live cross-session minting.
- **Receipt creation:** in one locked control-plane transaction, insert a single row with `authority_kind = 'bridge_publication'`, `operation = 'bridge_publication'`, `content_digest` = hash of on-disk bytes, a compliance digest computed by a fresh bridge-compliance audit against the chain-prefix operative head for that version (same resolution as Change A2), `capability_state = 'consumed'`, `consumed_at = now`, and a same-transaction appended aggregate revision (`evidence_view = "receipt_backfill"`) providing `revision_id` and `result_digest`. `authority_kind`/`operation` keep the standard values so `_bridge_publication_capability_clearance` accepts the receipt without modifying `check_protected_commit_authorization.py`; the back-fill remains distinguishable in audit via `evidence_view` and `change_reason`.
- **Chain ordering:** a convenience wrapper back-fills a chain oldest-first so each version's compliance binds to a fully receipted prefix; per-file back-fill remains available for single-gap chains.

### Change C (scope c) — pending-publication context survives process death

- `rollback_pending_bridge_publication` and `finalize_pending_bridge_publication` in `scripts/gtkb_bridge_writer.py` gain a third resolution tier: in-memory map → WI-5758 sidecar → **durable capability-row fallback**. When both process-local tiers are missing, resolve the newest exact capability row by `target_path` plus the session id extracted from the on-disk file's author metadata, and drive `recover_bridge_publication` from the row alone (its `expected_*` parameters are already optional; Problem Evidence 8). `BRIDGE_PUBLICATION_REPAIR_REQUIRED: pending capability context is unavailable` is raised only when no row exists at all — and that terminal case now has a lawful answer too (Change B).
- The existing sidecar-before-file-create ordering in `write_bridge_file` (sidecar write at lines 1233-1245 precedes exclusive create at lines 1247-1250) is pinned by a crash-ordering regression test: whenever the target exists and a row is minted, recovery context is durably resolvable.
- No new hard-coded timer, TTL, interval, or retry literals are introduced anywhere in this design (DELIB-202667722); recovery reuses the existing capability TTL and lock-timeout constants unchanged.

### Explicitly rejected alternatives

- **Shadow-row clearing for `recovery_required` rows** (insert a fresh consumed row that wins newest-by-rowid, leaving the poisoned row untouched): rejected as primary because it makes the newest-row-wins clearance semantics load-bearing for correctness and leaves two live rows for one publication; retained only as the natural by-product of Change A2's fresh mint on compensated-and-removed files, where the old row is genuinely historical.
- **Relaxing `_bridge_publication_capability_clearance` to accept `recovery_required` rows:** rejected — it would convert a truthful fail-closed deny into silent acceptance of unrecovered anomalies.
- **LO-side mint bypass of the author-session gate:** rejected — the gate is a live anti-fabrication control; Change B adds a distinct, attested, audit-visible operation instead of weakening the existing one.
- **Store the capability secret durably to enable replayed consume:** rejected — secrets stay memory-only; every durable recovery path operates on the hash-keyed row without exposing the secret, exactly as `recover_bridge_publication` does today.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs bridge publication authority, the append-only numbered bridge file chain, permanent bridge repair authority, and the audit-trail durability this recovery design serves; WI-5825's source spec.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal's obligation to cite all governing specifications concretely.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED is conditional on executed spec-derived tests; satisfied by the Specification-to-Test Mapping below.
- `GOV-ARTIFACT-APPROVAL-001` — no formal-artifact mutation is in scope; bridge artifacts and the authorization chain remain subject to the gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — this work proceeds under the active list-free PAUTH cited in the header plus this thread's future GO; PAUTH metadata does not broaden target_paths and does not replace the live latest-GO requirement.
- `GOV-17` — automation script modification approval gate: `scripts/gtkb_bridge_writer.py` is publication automation; this proposal plus Loyal Opposition GO under the cited project authorization is the approval evidence for modifying it.
- `GOV-10` — tests exercise exposed production interfaces (`recover_bridge_publication`, `backfill_bridge_publication_receipt`, `write_bridge_file` republish mode, the pending finalize/rollback helpers, and the protected-commit clearance evaluation), never private re-implementations.
- `SPEC-1662` — assertion quality (GOV-18): recovery tests assert behavioral outcomes — capability states, revision linkage, clearance verdicts, currentness — not structure.
- `SPEC-1830` — operational procedures must be code: this design replaces four hand-worked cleanup-evidence incident procedures with deterministic recovery entrypoints.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — repetitive deterministic recovery belongs in service code, not per-incident session judgement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary containment: all five target paths are in-root platform surfaces; no application subtree is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory: durable-artifact framing of the corrections program.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory: traceability across proposal, tests, report, and decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory: defect-origin WI lifecycle transitions.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory: the clearance gate and capability lifecycle are write-time mechanical enforcement; this WI extends recovery coverage without bypassing them.
- `GOV-STANDING-BACKLOG-001` — advisory: WI-5825 is a MemBase-carried backlog work item; no markdown backlog surface is created.

## Prior Deliberations

- **DELIB-202667735** (Delegated proposal authoring and unblock-implementation mandate with role-transition plan): the owner mandate under which this dispatched worker files this proposal in the parallel-operation program.
- **DELIB-202667731** (Harness Test Corrections whole-project authorization decision): owner grant of PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 cited in this header.
- **DELIB-202667730** (Harness Test final synthesis): the evaluation synthesis whose VERIFIED-stumble diagnoses produced WI-5825's three-gap defect record.
- **DELIB-202667726** (Program pause + Harness Test program directive): originating owner mandate for the Harness Test program and its corrections follow-on.
- **DELIB-202667722** (Timer and throttle governance): no-new-hard-coded-timer constraint honored explicitly in Change C.
- **DELIB-202667533** (Advisory-triage synthesis AT-01..04): commit-first finalization ordering — the design authority WI-5758 implemented and this recovery layer preserves (no pending-then-promote lifecycle state is introduced).

## Owner Decisions / Input

1. **DELIB-202667735** (delegated proposal authoring and unblock-implementation mandate): the owner authorized dispatched worker sessions to author and file implementation proposals for the corrections program, which is the authority under which this proposal is filed by a leader-dispatched worker.
2. **AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT → DELIB-202667731**: the owner selected the clean list-free whole-project grant PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730. Per its scope summary, WI-5825 still requires its own full governed cycle: this proposal, independent Loyal Opposition GO with complete Clause Applicability evidence, fresh work-intent claim, implementation-start packet, exact target-path enforcement, implementation report, and independent VERIFIED with governed atomic finalization. No additional owner decision is requested by this filing.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5825 defect description (fresh-read verified against `gt backlog show WI-5825 --json`), GOV-FILE-BRIDGE-AUTHORITY-001, SPEC-1830, GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, the linked test TEST-11781's expected outcome, and the WI-5758/WI-5812 thread lineage provide complete requirements for this implementation. No new or revised specification is required before implementation.

## Specification-to-Test Mapping

Linked test of record: **TEST-11781** ("Compensated rows clear via governed republish and unreceipted chains gain a lawful receipt path", spec_id GOV-FILE-BRIDGE-AUTHORITY-001). Expected outcome, verbatim: "A recovery_required row can be cleared by a governed republish that computes compliance against the correct operative head; an unreceipted Prime-authored chain can be receipted through an authorized back-fill path; finalization succeeds afterward."

| Requirement source | Behavior under test | Test coverage |
|---|---|---|
| TEST-11781 clause 1 / GOV-FILE-BRIDGE-AUTHORITY-001 (Change A1) | A fixture `recovery_required` row with retained exact-byte target clears via `recover_bridge_publication(mode="finalize")`: row becomes `consumed` with `consumed_at`, `result_digest`, `revision_id` set and `failure_reason` NULL; appended revision observes the live head; wrong-byte and absent-target paths still fail closed | `groundtruth-kb/tests/test_registry_control_plane.py` (new `recovery_required` finalize/rollback cases) |
| TEST-11781 clause 1 (Change A2) | Exact-byte republish of a compensated-and-removed file passes compliance computed against the version-(N-1) chain-prefix operative head and fails when computed against the advanced tail; byte-mismatch republish is refused | `platform_tests/scripts/test_gtkb_bridge_writer.py` (new republish cases) |
| TEST-11781 clause 2 (Change B) | An unreceipted Prime-authored chain fixture gains consumed receipts oldest-first through `backfill_bridge_publication_receipt` with recorded author-session + invoker-session + authorization evidence; existing-row, bad-status, and missing-authorization paths fail closed | `groundtruth-kb/tests/test_registry_control_plane.py` (new back-fill cases) |
| TEST-11781 clause 3 ("finalization succeeds afterward") | After Change A clearing + Change B back-fill on a mixed fixture chain, `_bridge_publication_capability_clearance` returns clear for every staged chain path and the registry-commit assessment reports no bridge-publication findings | `platform_tests/scripts/test_check_protected_commit_authorization.py` (new post-recovery clearance cases) |
| WI-5825 scope (c) / DELIB-202667533 commit-first ordering (Change C) | With in-memory state dropped (fresh module state) and the sidecar deleted, rollback/finalize resolve recovery from the durable capability row; with no row at all, the fail-closed REPAIR_REQUIRED message is preserved; sidecar-before-create ordering is pinned | `platform_tests/scripts/test_gtkb_bridge_writer.py` (new crash-survival cases) |
| DELIB-202667722 (timer discipline) | The diff introduces zero new hard-coded timeout/TTL/interval/retry literals | assertion inside the new writer test module cases |

## Acceptance Criteria

1. Every `recovery_required` fixture row with a retained exact-byte target can be cleared to `consumed` through the governed finalize path, and the protected-commit clearance then passes for that path with `scripts/check_protected_commit_authorization.py` unmodified.
2. Exact-byte republish of a compensated fixture file succeeds with compliance computed against the correct (version-prefix) operative head, minting a fresh consumed row; the historical compensated row is untouched.
3. An unreceipted fixture chain gains lawful consumed receipts recording true author-session, invoker-session, and authorization evidence; no existing row is ever shadowed or mutated by back-fill.
4. Whole-chain finalization (clearance evaluation over all staged chain paths) succeeds after recovery + back-fill on the mixed fixture.
5. Compensation and finalization survive process death: durable-row fallback recovers when both in-memory map and sidecar are gone; the REPAIR_REQUIRED fail-closed message survives only for the genuinely-unknown (no-row) case.
6. All fail-closed rejections named in the design are covered by executed rejection-path tests; no existing rejection is weakened.
7. `ruff check` and `ruff format --check` pass clean on all five target paths.
8. `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` passes green.
9. Zero new hard-coded timer/TTL/interval/retry literals in the diff.
10. Implementation begins only after WI-5812's implementation lands (sequencing contract above).

## Risk and Rollback

- **Risk: recovery becomes a laundering path for bad publications.** Mitigated: Change A finalize demands exact-byte identity with the recorded `content_digest`; Change B refuses to shadow existing rows, demands explicit authorization evidence, and records both identities truthfully; every recovery appends an audit revision; nothing relaxes the clearance gate itself.
- **Risk: current-head observation races a concurrent publication.** Mitigated: all recovery/back-fill work runs under the existing `_RegistryFileLock` + `BEGIN IMMEDIATE` discipline with the two-read stable-observation pattern already used by finalize; race-guarded state-bound UPDATEs preserve single-use semantics.
- **Risk: operative-head pinning computes the wrong prefix.** Mitigated: the pin derives mechanically from the numbered chain (version N binds to N-1); tests assert both the passing prefix computation and the failing tail computation.
- **Risk: collision with WI-5812 in-flight implementation.** Mitigated: disjoint target_paths plus the explicit implementation-sequencing contract (begin only after WI-5812 lands).
- **Rollback:** revert the two source-file diffs and the test additions. All Change A/B/C behaviors are additive branches and new functions; the pre-change fail-closed behaviors are preserved verbatim underneath and re-emerge on revert. Bridge files remain append-only evidence; capability rows already transitioned by executed recoveries remain truthful history and require no rollback.

## Recommended Commit Type

Recommended commit type: fix — repairs broken recovery behavior (terminal poisoned rows, terminal receipt deadlock, process-death compensation loss) with regression coverage; no new capability surface beyond the recovery entrypoints the defect requires.

## DISARM — KB Mechanics

This proposal mutates no MemBase artifact records. No specifications, tests-of-record, work items, deliberations, documents, or other managed KB artifacts are created, updated, or retired by this filing or by the proposed implementation. The implementation's writes are confined to the control-plane runtime-evidence tables (`sot_registry_bridge_publication_capabilities`, `sot_artifact_revisions`) inside the existing locked, race-guarded control-plane transaction discipline — publication evidence, not managed artifact content. The `kb_mutation_in_scope: false` flag reflects that boundary. All descriptions of capability rows, receipts, revisions, and clearance in this document are descriptive of the implementation domain, not requests to mutate KB artifacts.

## DISARM — Packet Mechanics

References to the implementation-start packet in this document are descriptive of the governed cycle, not packet operations performed by this filing. The packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5825-publication-capability-recovery-receipt-backfill`, run only after an independent Loyal Opposition GO and after the WI-5812 sequencing gate clears) is session-local implementation-scope evidence: it derives from TAFE/dispatcher bridge state, the approved proposal file, and the GO verdict file; it expires and fails closed on bridge status drift. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and does not require a separate approval packet. The PAUTH triple in this header supplies the project-authorization evidence the packet validator requires; it does not replace the bridge GO, the claim, or the packet itself.

## DISARM — Capability Mechanics

This document necessarily discusses publication-capability minting, consumption, compensation, recovery, and receipts throughout; all such discussion is design description of the target subsystem. This filing itself performs exactly one capability operation: the single governed mint-and-consume executed by the bridge writer to publish this proposal file. No recovery, back-fill, clearing, or republish operation is performed by this filing; those operations exist only after GO, implementation, and verification. No capability secret is recorded in this document or in any artifact this design produces.

## Loyal Opposition Asks

1. Review the Change A1 decision to replace the unprovable stale-preimage proof with a live-head stable observation for `recovery_required` finalize: is exact-byte identity plus two-read stable observation an acceptable proof floor, given the recorded preimage is mathematically unprovable once siblings advance the aggregate?
2. Review the Change B claim-gate question: should back-fill require the invoker to hold the live work-intent claim for the document, or is the recorded back-fill exemption (with authorization evidence) the better audit shape for chains whose original claims are long expired?
3. Review the Change A2/B operative-head pinning: confirm version-(N-1) chain-prefix resolution is the correct reading of TEST-11781's "correct operative head".
4. Confirm the WI-5812 sequencing contract and the disjoint-target-paths analysis satisfy the program's collision-avoidance expectations.
5. GO only if the specification linkage, spec-to-test mapping, fail-closed preservation, and append-only claims withstand inspection; otherwise NO-GO with concrete findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
