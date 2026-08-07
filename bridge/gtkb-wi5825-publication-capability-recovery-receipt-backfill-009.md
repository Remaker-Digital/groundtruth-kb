NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6d5cabf5-dc7d-418a-a495-6f23186a6638
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role via ::init gtkb pb; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

# GT-KB Bridge Implementation Report — WI-5825 Change B receipt back-fill — 009

bridge_kind: implementation_report
Document: gtkb-wi5825-publication-capability-recovery-receipt-backfill
Version: 009
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-008.md

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

## Scope Delivered And Scope Deliberately Deferred

Version 008 GO'd the full Change A + B + C design with Change-B-first ordering, and answered Loyal Opposition Ask 5 by accepting "Change B first with per-change evidence in one governed cycle."

**This report covers Change B only.** Changes A and C are implemented in neither source nor tests by this report. That is an owner decision recorded in the Owner Decisions section below, not an omission: Change B is the only change required to clear the live production blockers, because both `recovery_required` rows in the affected threads are already superseded by newer `consumed` rows.

Acceptance criteria 3, 4, 5 and 6 of the approved proposal are therefore **not claimed** by this report. They remain open for the Change A/C follow-on cycle. Criteria 1, 2, 7, 8, 9, 10, 11 and 12 are claimed and evidenced below.

## Implementation-Start Authority

- Fresh `go_implementation` work-intent claim rowid `36830`, session `6d5cabf5-dc7d-418a-a495-6f23186a6638`.
- Implementation-start packet created from GO v008: `latest_status: GO`, `go_file: bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-008.md`, `pre_start_packet_hash: sha256:acd57f6862696f822e9c5ce5f02b8712fbd593735e678d0bbbe3e92b7630f9af`.
- PAUTH operation-time evaluation allowed `implementation_start` with all five targets classified (`source` x2, `test` x3).

### Acceptance criterion 12 readback (performed before any edit)

- All five declared targets `git status --short` clean at HEAD `7d6b00f68`.
- Target-set overlap with WI-5812's eight paths: **none**. With WI-5723's six paths: **none**.
- Live work-intent claims at readback time: **zero**.
- WI-5812 head `GO v014` (targets non-overlapping); WI-5723 head `NO-GO v012`, so neither holds a live GO over any of the five paths.

## Changes Implemented

### `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`

1. **`backfill_bridge_publication_receipt`** — the Change B entrypoint. Inserts one `consumed` capability row for a bridge file that has no row at all, in a single locked control-plane transaction. Fail-closed preconditions, all covered by executed rejection tests: target resolves under `bridge/` via the existing `_bridge_publication_target` binding; file exists as a regular file; file is non-empty; first non-blank line is a canonical status token; declared status (when supplied) matches the observed token; authorization evidence non-empty; the invoking session holds the live work-intent claim unless `claim_exempt=True` is explicitly requested; and **no capability row already exists for the exact `(aggregate_entry_id, target_path)` pair**, so back-fill can never shadow a real row.
2. **Dual provenance, nothing fabricated.** The row records the file's own `author_session_context_id`, parsed from its on-disk content through the existing `_bridge_publication_author_session` helper, in the same column mint would have used; the invoking session is recorded separately in `claim_session`; and the authorizing evidence is carried into the appended revision's `change_reason` and `evidence_source_reference`. The mint path's author-session-equality gate is **not touched** and continues to reject live cross-session minting.
3. **`_bridge_publication_prefix_transition_digest`** — the operative-head resolution for an already-written file. The mint-time `_bridge_publication_transition_digest` copies the whole live chain and then refuses when the candidate already exists, which is unconditionally true for a back-fill target. The new helper copies only versions **strictly less than** the target version and writes the existing bytes as the candidate, reproducing the version-(N-1) chain-prefix operative head. It runs the same strict `resolve_bridge_lifecycle` validation, so status-token legality, `Responds to` linkage, ordinary-transition legality, and author-role/status agreement are all enforced against the back-fill target.
4. **`_bridge_file_status_token`** — canonical first-non-blank-line status validation using `CANONICAL_STATUSES` from the strict resolver rather than a local copy.
5. **`_newest_exact_bridge_publication_capability_row`** — byte-identical row selection to `_newest_exact_bridge_publication_capability` in the checker, so the never-shadow precondition is evaluated against exactly the row the clearance gate would consult.
6. **`backfill_bridge_publication_chain`** — oldest-first convenience wrapper; ordering is enforced inside the function rather than trusted to the caller, because a later version's chain-prefix binding is only meaningful once its predecessors are receipted.
7. **`receipt_backfill` added to `EvidenceView` and `SUPPORTED_EVIDENCE_VIEWS`** — required before `_append_revision` accepts the revision, and the mechanism by which back-fill stays distinguishable in the append-only audit trail.

The inserted row uses the standard `authority_kind` and `operation` values (`bridge_publication`), so `_bridge_publication_capability_clearance` accepts it **with zero changes to `scripts/check_protected_commit_authorization.py`** — proven end-to-end by the new clearance test.

### `scripts/gtkb_bridge_writer.py`

8. **`backfill_publication_receipt`** — the operator entrypoint. It computes the compliance digest here, not in the control plane, so the control plane keeps its layering (it must not import the writer) and the digest is produced by exactly the same `run_bridge_compliance_audit` + `_publication_compliance_digest` surface mint uses. Guards are intentionally empty and the reason is documented in the docstring: `_run_provider_verdict_guards` evaluates a candidate publication this session is about to write, whereas a back-fill target was authored by another session and already exists. An audit denial fails closed rather than being papered over, because a file that cannot pass the compliance gate is a genuine finding, not a back-fill candidate.

### Tests

9. **`groundtruth-kb/tests/test_registry_control_plane.py`** — nine new cases: clearance-shaped consumed row with dual provenance and verified revision linkage; content-digest binding to on-disk bytes; refusal to shadow an existing row after a normal mint/consume; absent target; non-canonical status token; empty authorization evidence; claim required unless explicitly exempt (both branches); declared-status mismatch; and oldest-first chain ordering.
10. **`platform_tests/scripts/test_check_protected_commit_authorization.py`** — one new end-to-end case proving the before/after transition against the real gate.

## Files Changed

```text
groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py   | 383 ++++++++++++++-
groundtruth-kb/tests/test_registry_control_plane.py                   | 282 +++++++++++++
platform_tests/scripts/test_check_protected_commit_authorization.py   | 103 ++++++
scripts/gtkb_bridge_writer.py                                         |  56 +++
4 files changed, 823 insertions(+), 1 deletion(-)
```

The single deletion is the one-line `SUPPORTED_EVIDENCE_VIEWS` frozenset literal, replaced by its multi-line form with the new member. `platform_tests/scripts/test_gtkb_bridge_writer.py` is declared in `target_paths` but **unchanged**, because its cases in the approved plan belong to Change A2 and Change C.

### Live SHA-256 at HEAD `7d6b00f68`

| Target | SHA-256 | State |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` | `DE9444528D80D060E9602C0B5AACFB3F8EE116AAB7B3027B76EBB3B9483A605C` | modified |
| `scripts/gtkb_bridge_writer.py` | `F8FB5ECD2FE16E9A31C762490CFA1E485C2A3D232695B9F2B11968FAEDDDAA35` | modified |
| `groundtruth-kb/tests/test_registry_control_plane.py` | `DAB6E2471AC358E1FE79405A43D1DD2DC3F914C7FDD2AE83CC1037CE50E6AFA7` | modified |
| `platform_tests/scripts/test_check_protected_commit_authorization.py` | `103B9FA1614A9A097417D97840AB5FBE237F35FB79C74FC45B636D40B5EA978E` | modified |
| `platform_tests/scripts/test_gtkb_bridge_writer.py` | `44F2A048E5F6B9B2E720519878270D7F7F7DE56F0D93412AFE83D90863434B90` | unchanged |

## Specification-Derived Verification: Executed Evidence

Linked test of record **TEST-11781**, clause 2 ("an unreceipted Prime-authored chain can be receipted through an authorized back-fill path") and clause 3 ("finalization succeeds afterward").

| Requirement | Behavior verified | Executed evidence |
|---|---|---|
| TEST-11781 clause 2 / `GOV-FILE-BRIDGE-AUTHORITY-001` | Unreceipted file gains a consumed receipt recording author session, invoker session, and authorization evidence; revision linkage matches the gate's four-field check; `evidence_view` is `receipt_backfill` | `test_backfill_receipt_creates_consumed_row_with_dual_provenance` — passed |
| TEST-11781 clause 2 (never shadow) | After a normal mint/consume, back-fill refuses and leaves the row count at 1 | `test_backfill_receipt_refuses_to_shadow_an_existing_row` — passed |
| TEST-11781 clause 2 (fail-closed set) | Absent target, non-canonical status token, empty authorization evidence, declared-status mismatch, and missing claim each reject before any row is written | five rejection cases — all passed, each asserting zero rows remain |
| TEST-11781 clause 2 (attested exemption) | An explicitly exempt invoker succeeds and is recorded truthfully in `claim_session` while the file's author session is preserved | `test_backfill_receipt_requires_live_claim_unless_explicitly_exempt` — passed |
| TEST-11781 clause 2 (chain ordering) | Targets supplied out of order are back-filled oldest-first and both rows land `consumed` | `test_backfill_chain_orders_oldest_first` — passed |
| Digest binding | `content_digest` equals the exact on-disk bytes, which is what the gate compares to the staged blob | `test_backfill_receipt_binds_content_digest_to_on_disk_bytes` — passed |
| **TEST-11781 clause 3** | A staged unreceipted bridge path is denied with the exact production message `registered bridge path lacks exact publication capability evidence`, and the same path returns `(True, "")` after back-fill, with the checker module unmodified | `test_backfilled_receipt_clears_a_previously_unreceipted_staged_bridge_path` — passed |
| Operative-head correctness | The prefix binding enforces the real protocol: fixtures were rejected in turn for a missing `Responds to` link, an unlawful `NEW -> REVISED` transition, and a `NO-GO` carrying a Prime author role, until the chain was made lawful | observed during implementation; final case passes |
| `GOV-17` / `GOV-10` | Tests exercise the exposed production interfaces (`backfill_bridge_publication_receipt`, `backfill_bridge_publication_chain`, `_bridge_publication_capability_clearance`), not private re-implementations | test bodies |
| DELIB-202667722 timer discipline | No new hard-coded timeout, TTL, interval, retry, throttle or concurrency literal in the diff | diff inspection; no numeric literal of that class added |

### Commands Executed

```text
python -m pytest groundtruth-kb/tests/test_registry_control_plane.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short
298 passed, 1 warning in 142.64s

python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short
70 passed in 28.83s

python -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=line
177 passed, 1 warning in 111.43s

python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=line
51 passed, 1 warning in 8.76s

python -m ruff check <the four changed paths>
All checks passed!

python -m ruff format --check <the four changed paths>
4 files already formatted

python -m py_compile <the two changed source paths>
OK
```

The 298-test combined run is the exact command named by acceptance criterion 9 of the approved proposal.

## Acceptance Criteria Assessment

| # | Criterion | State |
|---|---|---|
| 1 | Unreceipted chain gains lawful consumed receipts with true author, invoker and authorization evidence; no existing row shadowed or mutated | **met** |
| 2 | After back-fill, protected-commit clearance passes with `check_protected_commit_authorization.py` unmodified | **met** |
| 3 | `recovery_required` fixture rows clear via governed finalize (Change A1) | **deferred** — not claimed |
| 4 | Exact-byte republish of a compensated file (Change A2) | **deferred** — not claimed |
| 5 | Whole-chain finalization after recovery plus back-fill on a mixed fixture | **deferred** — depends on Change A |
| 6 | Compensation and finalization survive process death (Change C) | **deferred** — not claimed |
| 7 | All named fail-closed rejections covered; no existing rejection weakened; mint author-session-equality gate unchanged | **met** for Change B |
| 8 | `ruff check` and `ruff format --check` clean on changed paths | **met** |
| 9 | Combined three-module pytest green with per-change counts recorded | **met** — 298 passed |
| 10 | Zero new hard-coded timer/TTL/interval/retry literals | **met** |
| 11 | Only the declared paths change; no WI-5812/5723/5653/5880 implementation entered them | **met** — 4 of 5 declared paths changed, none outside |
| 12 | Implementation-start readback of claims, GO overlap, cleanliness and hashes | **met** — recorded above |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge publication authority and the append-only audit trail this receipt path serves; WI-5825's source spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed spec-derived evidence presented above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — links carried forward from the approved proposal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active list-free PAUTH cited in this header, operation-time gated.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time evaluation recorded in the start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item and exact target linkage.
- `GOV-17` — automation script modification approval gate; `scripts/gtkb_bridge_writer.py` is publication automation modified under this thread's GO.
- `GOV-10` — tests exercise exposed production interfaces.
- `SPEC-1830` and `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — recovery is deterministic service code, not per-incident session repair.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every state claim here derives from a fresh canonical read this session.
- `GOV-WORK-TREE-HYGIENE-001` — no path outside the declared set was modified.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable traceability and the GO to post-implementation lifecycle transition.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed paths and bridge artifacts remain in-root.
- `GOV-STANDING-BACKLOG-001` — WI-5825 remains the single non-duplicated carrier for publication recovery.

## Prior Deliberations

- `DELIB-20260806011613` — owner decision releasing the WI-5812 sequencing gate and authorizing receipt back-fill as the coded alternate; the authority this implementation proceeds under.
- `DELIB-202668125` — the version 006 GO whose sequencing condition version 007 addressed.
- `DELIB-20260805195214` — by-reference finalization waiver; established that the waiver does not create publication receipts, which is precisely the gap Change B closes.
- `DELIB-202667731` — owner-approved list-free whole-project PAUTH cited in this header.
- `DELIB-202667722` — timer and throttle governance; no new hard-coded literal introduced.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-008.md` — the GO authorizing this implementation and answering Ask 5 on Change-B-first ordering.

## Owner Decisions / Input

This report depends on owner approval for its scope split. The authorizing evidence is:

1. **AskUserQuestion, 2026-08-06, implementation scope.** Question: WI-5825 now has GO v008; implementation spans five files — how should Prime Builder proceed? Owner answer: **"Implement Change B only, then report"** — take the claim and start packet, implement `backfill_bridge_publication_receipt` plus its writer exposure and tests, run the focused suite and ruff, then file the implementation report, with Changes A and C following in a second governed cycle. This is the sole authority for the deferral of acceptance criteria 3 through 6.
2. **`DELIB-20260806011613`** — owner decision authorizing the receipt back-fill as the coded alternate contemplated by `bridge/gtkb-wi5841-harness-selector-registry-derived-020.md` Finding 1. Its approval packet already exists on disk and is not created, modified, or required by this filing.
3. **`DELIB-202667731`** — the active list-free whole-project PAUTH inherited by active member WI-5825.
4. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This implementation does not activate, dispatch through, configure, or mutate either.

No new owner decision is requested by this filing.

## Requested Loyal Opposition Action

Verify Change B against the executed evidence above and record **VERIFIED**, or **NO-GO** with concrete findings. Reviewers are specifically asked to check:

1. That the never-shadow precondition uses byte-identical row selection to the clearance gate, so back-fill cannot mask a poisoned row.
2. That the chain-prefix operative head is the correct TEST-11781 reading, given it validates transitions and author-role/status agreement against versions strictly below the target.
3. That empty guards in the writer wrapper are the right compliance shape for a file authored by another session, and that failing closed on audit denial is preferred to bypassing it.
4. That the scope split is acceptable, with acceptance criteria 3 through 6 explicitly not claimed.

## Recommended Commit Type

Recommended commit type: `feat` — adds a new governed capability surface (`backfill_bridge_publication_receipt`, `backfill_bridge_publication_chain`, the writer entrypoint, and the `receipt_backfill` evidence view) that did not previously exist, with regression coverage. This is net-new capability rather than a repair of existing behavior, so `fix` would understate it despite the defect-driven motivation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
