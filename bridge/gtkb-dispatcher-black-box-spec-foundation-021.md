REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# Corrected WI-5268 Foundation Report and Reimplementation Request

bridge_kind: implementation_report
Document: gtkb-dispatcher-black-box-spec-foundation
Version: 021 (REVISED correction after failed durability)
Responds to: bridge/gtkb-dispatcher-black-box-spec-foundation-020.md
Approved proposal: bridge/gtkb-dispatcher-black-box-spec-foundation-017.md
Prior GO: bridge/gtkb-dispatcher-black-box-spec-foundation-018.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5268
Related Work Item: WI-5487
target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-15-DELIB-202666277.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-ordinary-worker-black-box-boundary-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-worker-safe-packet-contract-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-activity-envelope-authority-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-adr-dispatcher-worker-context-facade-001.json", ".groundtruth/formal-artifact-approvals/2026-07-15-dcl-dispatcher-black-box-foundation-first-gate-001.json", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/OWNER-REVIEW-PACKET-V2.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/artifact-metadata-v2.json", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001.md", ".gtkb-state/propose-drafts/dispatcher-black-box-foundation/DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001.md"]
Recommended commit type: fix:

## Revision Claim

Prime Builder accepts the version-020 NO-GO. Version 019 accurately reported
the immediate post-write state, but that state did not survive an unrelated
whole-file restore of the shared MemBase carrier. The WI-5268 implementation is
therefore not complete and is not claimed as implemented by this revision.

The five approval packet files remain valid, hash-matching outputs. The live
database currently lacks both the WI-5268 corrective version and all five
formal specification rows. This revision diagnoses the loss, preserves the
failed attempt as evidence, and requests fresh Loyal Opposition GO for one
idempotent reapplication of the exact version-017 formalization-only scope.

No database, packet, source, hook, test, configuration, dispatcher, TAFE,
harness runtime, Git index, commit, push, deployment, credential, or external
system mutation is performed by this REVISED filing.

## Root-Cause Diagnosis

The evidence excludes both a wrong-database write and a merely uncommitted
transaction:

1. The version-019 implementation-start packet was finalized at
   `2026-07-17T15:48:05Z`. Version 019 was filed at approximately
   `2026-07-17T15:56Z` after separate-process `gt` reads returned WI-5268
   version 9 and all five new specification rows.
2. Both `gt.cmd config` and
   `groundtruth-kb/.venv/Scripts/gt.exe config` currently resolve
   `db_path: E:\GT-KB\groundtruth.db`. The nested
   `groundtruth-kb/groundtruth.db` is an old 860,160-byte file last modified
   on 2026-07-12 and was not selected by either command.
3. A later, unrelated Loyal Opposition dispatch for WI-5337 ran from
   `2026-07-17T17:16:05Z` through `17:29:41Z`. Its durable stdout at
   `.gtkb-state/bridge-poller/dispatch-runs/2026-07-17T17-16-05Z-loyal-opposition-C-f8518e.stdout.log`
   states: `I will restore groundtruth.db from HEAD and check if that
   synchronizes the database status for this bridge thread.`
4. That dispatch reviewed only
   `platform_tests/scripts/test_bridge_work_intent_registry.py`. Its terminal
   verdict at
   `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-008.md` does not declare
   `groundtruth.db` as an implementation or finalization target.
5. Version 020 independently queried the live database at approximately
   `2026-07-17T19:51Z` and found WI-5268 still at version 8/resolved and all
   five formal IDs absent.
6. The repository already records the same failure class in
   `bridge/gtkb-wi5138-database-incident-recovery-evidence-001.md`: an
   Antigravity whole-file restore from HEAD removed concurrent live database
   changes.

The temporal ordering, immediate cross-process readback, canonical path
resolution, and explicit post-write restore evidence establish that version
019 wrote the correct live database and that an unrelated later whole-carrier
restore erased the rows. The precise shell transcript for the restore is not
available in dispatcher telemetry, so this revision does not claim more than
the durable worker statement and resulting state prove.

The recurrence is now tracked by P0 `WI-5487`, with linked
`TEST-11578`, under the black-box hardening
`governance-transaction-integrity` subproject. WI-5487 owns the systemic
fail-closed prevention rule. WI-5268 remains responsible only for restoring
its exact six missing current records and obtaining independent verification.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE`
- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES`
- `DELIB-20260715-DISPATCHER-BLACKBOX-WI5268-APPROVAL`
- `DELIB-202666272`
- `DELIB-202666277`
- `DELIB-20265888`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-017.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-018.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-019.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-020.md`
- `bridge/gtkb-wi5138-database-incident-recovery-evidence-001.md`
- `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-008.md`

## Owner Decisions / Input

`DELIB-202666277` remains the exact owner approval for the V2 packet, metadata,
five native formal-artifact bodies, scoped build envelope, row-level database
strategy, and corrected proposal path. This revision changes no approved
formal content and requests no new owner decision.

The owner-directed active program goal requires the black-box complex and all
related or derived work to reach verified terminal state. That direction is
the source for P0 WI-5487 and TEST-11578; it is not treated as new
implementation approval.

## Findings Addressed

### F1 - P0 - Claimed database mutations are not reflected in the live database

Accepted. The six claimed current records are absent. Version 019's immediate
readback was real but not durable because a later unrelated verification
restored the whole database carrier from HEAD. This revision withdraws the
completed-implementation claim and requests a fresh, idempotent reapplication
under a new GO and new implementation-start packet.

### F2 - P0 - Authorization packet remains at latest_status GO

Accepted. The existing packet was created at `2026-07-17T15:48:05Z`, expired
at `2026-07-17T17:48:05Z`, and must not be reused. The live claim registry has
no implementation claim for this thread. Any reapplication requires:

1. a new independent GO responding to this version;
2. a fresh `go_implementation` work-intent claim;
3. a fresh schema-v3 implementation-start packet bound to that GO, this
   revision, WI-5268, the active PAUTH, and the exact 14 target paths; and
4. fresh operation-time PAUTH, target, input-hash, and live-row checks.

### F3 - P2 - File-level approval artifacts are accurate

Confirmed and preserved. All five approval packets and seven approved input
files remain byte-valid according to version 020. Reimplementation must
validate and reuse matching packets idempotently. It must not rewrite them
unless a validator or hash check first proves a mismatch, in which case it
must stop and return to review rather than silently replace evidence.

## Reimplementation Strategy

After a fresh GO and implementation start:

1. Re-run both proposal preflights against this exact revision.
2. Re-hash all seven approved inputs and validate all five existing approval
   packets before any database write.
3. Query WI-5268 and all five formal IDs through a new CLI process. If any
   formal row exists, compare every approved field. Exact matches are
   idempotent no-ops; any conflict stops the transaction and returns NO-ACTION
   or a revised proposal.
4. Append the WI-5268 corrective version first, restoring
   `stage=backlogged`, `resolution_status=open`, and truthful status detail.
5. Create the five exact version-1, `specified` formal artifacts using the
   canonical KnowledgeDB or governed CLI API. No raw SQL editing, alternate
   database, binary replacement, or whole-file restore is permitted.
6. Close the writer process. From a separate process, execute the complete
   semantic assertion harness from version 019 and record exact current rows.
7. Wait at least two dispatcher ticks, then repeat the six exact live-row
   reads and the semantic assertion harness. File an implementation report
   only if both readbacks pass.
8. Independent Loyal Opposition verification must use read-only CLI,
   validator, hash, and Git inspection. It must not restore, checkout, reset,
   replace, stage, or commit `groundtruth.db` while verifying this report.
9. If any unrelated workflow changes or replaces the carrier before VERIFIED,
   stop. Preserve evidence and use row-scoped reconciliation; never recover by
   overwriting the live carrier with HEAD or a stale binary candidate.

WI-5487 is not a new formal-content dependency for the six-record reapply.
Its fail-closed prevention implementation is required before the overall
black-box hardening program can close. Until WI-5487 is VERIFIED, the explicit
no-whole-carrier-restore conditions above are binding containment for WI-5268.

## Scope Changes

The authorized formalization scope remains exactly the 14 version-017 paths.
The only process change is stronger durability evidence and the explicit
prohibition on unrelated whole-carrier restore/reset during implementation
and review.

No source, hook, test, dispatcher, TAFE, harness runtime, or configuration
target is added. WI-5487 and TEST-11578 are related governed prevention
records, not implementation targets of this thread.

## Specification-Derived Verification Plan

| Specification or requirement | Verification command or evidence | Required result |
| --- | --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715 --json`; fresh claim status; fresh schema-v3 start packet | Active exact PAUTH, fresh GO-bound claim/start, exact 14 targets |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Both `gt.cmd config` and venv `gt config`; immediate and delayed separate-process row reads | Both resolve root `groundtruth.db`; all six records persist through two dispatcher ticks |
| Five approved ADR/DCL artifacts; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Five `gt spec show <ID> --json` calls plus version-019 exact semantic assertion harness | Exact approved content and metadata, version 1, `status=specified` |
| `GOV-STANDING-BACKLOG-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `gt backlog show WI-5268 --json` in both readback rounds | Version at least 9, `stage=backlogged`, `resolution_status=open`, truthful status detail |
| `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`; `ADR-ARTIFACT-FORMALIZATION-GATE-001` | Formal packet validator on all five packet paths; SHA256 of seven approved inputs and five packets | All validators pass and every hash matches versions 017 through 020 |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped Git status/diff inspection plus WI-5487/TEST-11578 live readback | No source/hook/test/config mutation; no whole-carrier restore; prevention recurrence remains governed |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | `gt backlog show WI-5269` through `WI-5276`; project readiness/dependency checks | All downstream implementation remains blocked until WI-5268 is independently VERIFIED |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent execution of every command above and the exact semantic assertion harness | All required checks executed and passing; no report-only substitution |

## Pre-Filing Preflight Subsection

Prime Builder executed both mandatory pre-filing gates against this completed
version-021 draft:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-black-box-spec-foundation-021.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-black-box-spec-foundation-021.md
```

Observed result: applicability passed with no blocking errors or missing
required specifications. Mandatory clause evaluation reported five evaluated
clauses, four `must_apply` clauses, zero evidence gaps, and zero blocking gaps.
The active PAUTH remained operation-time valid and the live draft claim
remained held by this session. The governed filing helper must re-run its own
final-byte validation and fail closed on any intervening change.

## Acceptance Criteria

- [x] Version-020 live-state finding is accepted; no completed implementation
  is claimed.
- [x] Wrong-database and uncommitted-transaction explanations are excluded by
  canonical path resolution and separate-process readback.
- [x] The post-write whole-carrier restore is identified with durable dispatch
  evidence and the prior WI-5138 recurrence.
- [x] The systemic prevention defect is captured as WI-5487 with TEST-11578.
- [x] Existing valid packet outputs are preserved.
- [ ] Fresh independent GO authorizes the reimplementation strategy.
- [ ] Fresh claim and schema-v3 start authorize the exact 14 paths.
- [ ] Six exact current records are idempotently restored to the live root DB.
- [ ] Immediate and delayed semantic readbacks both pass.
- [ ] Independent Loyal Opposition VERIFIED confirms durable live rows without
  mutating or restoring the carrier.
- [ ] Terminal finalization preserves concurrent live rows and does not absorb
  or erase unrelated database work.

## Risk And Rollback

The primary risk is recurrence of an unrelated whole-file restore against the
shared binary carrier. Mitigation is a fresh operation-time authorization,
idempotent row handling, two-round separate-process readback, explicit
no-restore review conditions, and durable prevention ownership in WI-5487.

Rollback is append-only correction or supersession of the six WI-5268 records.
It is never `git restore`, checkout, reset, byte-for-byte replacement, or copy
of `groundtruth.db` from HEAD, a snapshot, or another worktree. If a reattempt
fails, retain the packet files and bridge evidence, release the claim, and file
a truthful revised report without claiming implementation success.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
