NEW
::init gtkb lo
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T08-18-23Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Protected-commit checker finalizer fix: evidence pre-filter + batch materialization + oversized-blob exemption

bridge_kind: prime_proposal
Document: gtkb-wi5659-protected-commit-finalizer-repair
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true}]
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5659` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: Restore governed commit finalization by removing ALL per-commit blockers in scripts/check_protected_commit_authorization.py. FOUR authorized mechanisms, all implemented. Mechanism 1 (DELIB-202667184; GO at -004): _load_verified_evidence materialized and lifecycle-resolved ALL 472 committed packets per commit (460.8s); per the _packet_binding_errors invariant (packet.target_path_globs == chain.target_paths) a packet can only authorize a staged protected path when its cheap stored globs match, so it now takes a protected_paths parameter and skips the expensive _bridge_snapshot + resolve for non-matching packets. Measured 460.824s -> 9.564s. Mechanism 2 (DELIB-202667185; GO at -010): _load_transaction_verified_evidence -> _bridge_snapshot(index_snapshot) -> _materialize_index_tree fires ONLY when a VERIFIED candidate is staged (exactly during governed finalization) and walked all 19,090 index entries at two subprocess spawns each; measured 159.4 ms/entry = 50.7 min, 86% process spawn. Replaced with one streaming 'git cat-file --batch' process (requests interleaved to avoid deadlocking git against a full stdout pipe): 1.4 ms/entry, full tree ~17s. Mechanism 3 (DELIB-202667186): with mechanism 2 the build reached a deterministic hard failure, GateError 'raw blob exceeds 67108864-byte materialization limit: groundtruth.db', because tracked groundtruth.db is 762720256 bytes (727.4 MB), exceeding MAX_BLOB_BYTES 11.4x and MAX_TREE_BYTES by itself - so the transaction branch failed closed on EVERY governed VERIFIED finalization at any speed, the probable root cause of the file-only VERIFIED class. Oversized blobs are now exempt from CONTENT COPY only: still streamed and hash-verified against the index object id, still enumerated in a separate exempted map, not written to disk, and excluded from MAX_TREE_BYTES accounting. Kept out of ledger because _verify_snapshot_ledger requires each ledger entry to exist on disk and re-hashes its bytes. Mechanism 4 (DELIB-202667187): mechanisms 1-3 unmasked a pre-existing defect - _verify_snapshot_ledger skipped the entire .gtkb-state/ namespace while materialization includes this repository's 25 TRACKED .gtkb-state/* files, so verification always raised a false 'prospective audit tree file set drifted'. Verification now discriminates on ledger membership rather than a hardcoded scratch path list (the audit creates several scratch subtrees at runtime: compliance-audit/, audit-candidate/), so tracked .gtkb-state files are fully verified for file-set, identity and content hash while runtime scratch is ignored as before. Verified end state: full prospective tree builds in ~17s over 19,090 entries (19,089 materialized + 1 exempted groundtruth.db), enumeration complete, ledger verification OK with no drift; end-to-end check_protected_commit_authorization.py --staged runs in 2.4s exit 0 PASS; 113 tests pass; ruff check and ruff format --check clean. One pre-existing test (test_raw_materialization_fails_closed_on_blob_resource_limit) was converted rather than deleted because DELIB-202667186 deliberately supersedes its oversized-blob-is-fatal contract. Scope is source+test in the two declared target paths only; no absorption of WI-5657, WI-5658, WI-5441 or WI-5440; does not authorize untracking groundtruth.db or redesigning the hermetic audit scope. Separate follow-on worth its own work item: groundtruth.db is a 727 MB binary tracked in git and modified nearly every session, appending another ~727 MB blob to history each time (.git measured at 110.6 GB, since reduced by 9.81 GB of orphaned temp garbage).

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5659` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/check_protected_commit_authorization.py`, `platform_tests/scripts/test_check_protected_commit_authorization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667185` - Owner authorizes batch prospective-tree materialization within WI-5659
- `DELIB-202666530` - Loyal Opposition Verdict - NO-GO (finalization-scoped) - WI-5330 Spec-Link Heading Hyphen False Positive
- `DELIB-20265494` - Loyal Opposition NO-GO verdict - WI-4700 narrative approval packet scope fix
- `DELIB-202666888` - NO-GO — Envelope Protocol Slice D Worker Hook Injection
- `DELIB-202666879` - GO — Envelope Protocol Slice D Worker Hook Injection (Revised)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX` - active project authorization covering `WI-5659`.

## Proposed Scope

- Pre-filter verified-evidence packets to scopes that authorize staged protected paths, preserving all current authorization semantics.
- Batch prospective-tree blob materialization, stream-hash oversized blobs without content copying, and narrow audit-scratch exclusion to the compliance-audit subtree only.

## Cross-Harness Disposition

- **codex**: Primary implementation and focused test runner.
- **claude**: No code change; independent Loyal Opposition review required.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5659; PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5659-CHECKER-VERIFIED-EVIDENCE-PREFILTER-FIX; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Restore governed commit finalization by removing ALL per-commit blockers in scripts/check_protected_commit_authorization.py. FOUR authorized mechanisms, all implemented. Mechanism 1 (DELIB-202667184; GO at -004): _load_verified_evidence materialized and lifecycle-resolved ALL 472 committed packets per commit (460.8s); per the _packet_binding_errors invariant (packet.target_path_globs == chain.target_paths) a packet can only authorize a staged protected path when its cheap stored globs match, so it now takes a protected_paths parameter and skips the expensive _bridge_snapshot + resolve for non-matching packets. Measured 460.824s -> 9.564s. Mechanism 2 (DELIB-202667185; GO at -010): _load_transaction_verified_evidence -> _bridge_snapshot(index_snapshot) -> _materialize_index_tree fires ONLY when a VERIFIED candidate is staged (exactly during governed finalization) and walked all 19,090 index entries at two subprocess spawns each; measured 159.4 ms/entry = 50.7 min, 86% process spawn. Replaced with one streaming 'git cat-file --batch' process (requests interleaved to avoid deadlocking git against a full stdout pipe): 1.4 ms/entry, full tree ~17s. Mechanism 3 (DELIB-202667186): with mechanism 2 the build reached a deterministic hard failure, GateError 'raw blob exceeds 67108864-byte materialization limit: groundtruth.db', because tracked groundtruth.db is 762720256 bytes (727.4 MB), exceeding MAX_BLOB_BYTES 11.4x and MAX_TREE_BYTES by itself - so the transaction branch failed closed on EVERY governed VERIFIED finalization at any speed, the probable root cause of the file-only VERIFIED class. Oversized blobs are now exempt from CONTENT COPY only: still streamed and hash-verified against the index object id, still enumerated in a separate exempted map, not written to disk, and excluded from MAX_TREE_BYTES accounting. Kept out of ledger because _verify_snapshot_ledger requires each ledger entry to exist on disk and re-hashes its bytes. Mechanism 4 (DELIB-202667187): mechanisms 1-3 unmasked a pre-existing defect - _verify_snapshot_ledger skipped the entire .gtkb-state/ namespace while materialization includes this repository's 25 TRACKED .gtkb-state/* files, so verification always raised a false 'prospective audit tree file set drifted'. Verification now discriminates on ledger membership rather than a hardcoded scratch path list (the audit creates several scratch subtrees at runtime: compliance-audit/, audit-candidate/), so tracked .gtkb-state files are fully verified for file-set, identity and content hash while runtime scratch is ignored as before. Verified end state: full prospective tree builds in ~17s over 19,090 entries (19,089 materialized + 1 exempted groundtruth.db), enumeration complete, ledger verification OK with no drift; end-to-end check_protected_commit_authorization.py --staged runs in 2.4s exit 0 PASS; 113 tests pass; ruff check and ruff format --check clean. One pre-existing test (test_raw_materialization_fails_closed_on_blob_resource_limit) was converted rather than deleted because DELIB-202667186 deliberately supersedes its oversized-blob-is-fatal contract. Scope is source+test in the two declared target paths only; no absorption of WI-5657, WI-5658, WI-5441 or WI-5440; does not authorize untracking groundtruth.db or redesigning the hermetic audit scope. Separate follow-on worth its own work item: groundtruth.db is a 727 MB binary tracked in git and modified nearly every session, appending another ~727 MB blob to history each time (.git measured at 110.6 GB, since reduced by 9.81 GB of orphaned temp garbage).",
  "after_behavior": "File a governed implementation proposal for `WI-5659` using deterministic project, authorization, target-path, and preflight wiring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5659",
    "project": "PROJECT-GTKB-HOUSEKEEPING-HARDENING",
    "target_paths": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
    ],
    "linked_specifications": [
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "File a governed implementation proposal for `WI-5659` using deterministic project, authorization, target-path, and preflight wiring.",
    "scope": [
      "Pre-filter verified-evidence packets to scopes that authorize staged protected paths, preserving all current authorization semantics.",
      "Batch prospective-tree blob materialization, stream-hash oversized blobs without content copying, and narrow audit-scratch exclusion to the compliance-audit subtree only."
    ],
    "acceptance_criteria": [
      "A governed finalization transaction completes without scanning unrelated packets or copying oversized tracked blobs into its prospective tree.",
      "Focused tests prove packet pre-filtering, batch materialization, oversized-blob exemption, and audit-ledger coverage."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the focused protected-commit authorization suite and a scoped finalization-path regression. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A governed finalization transaction completes without scanning unrelated packets or copying oversized tracked blobs into its prospective tree.
- Focused tests prove packet pre-filtering, batch materialization, oversized-blob exemption, and audit-ledger coverage.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`feat`
