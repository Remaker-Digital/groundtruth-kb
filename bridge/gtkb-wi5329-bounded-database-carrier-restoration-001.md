NEW

# GT-KB WI-5329 Bounded Database Carrier Restoration

bridge_kind: prime_proposal
Document: gtkb-wi5329-bounded-database-carrier-restoration
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-16T01-48-03Z-prime-builder-A-b8e790
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; post-restart continuation; approval policy managed

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-DB-CARRIER-RESTORATION-20260716
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5329

target_paths: ["groundtruth.db", ".gtkb-state/database-carrier-restoration/**"]

implementation_scope: metadata | runtime-state | repository-metadata | bridge-evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Restore the committed `groundtruth.db` carrier to a valid sidecar-free SQLite database without using the corrupt `HEAD:groundtruth.db` blob as a semantic source. The live database is currently valid, while the committed carrier blob at `HEAD` is malformed and blocks row-scoped binary finalization for other governed work. This proposal creates a bounded carrier restoration path for `WI-5329` only.

The implementation will not perform arbitrary MemBase row edits. It will create a candidate carrier from the live valid database after independent GO, normalize only the active restoration work-intent row that exists solely because this implementation claim had to be acquired, prove table/count/digest equivalence against the authorized live source under that exact transient-state exclusion, and produce a reviewed binary patch from `HEAD:groundtruth.db` to the candidate. Finalization must use the verified disposable-index binary-patch path so unrelated dirty worktree and real-index state are excluded.

This proposal does not authorize Git push, release, deployment, credential lifecycle work, destructive cleanup, Git history rewrite, dispatcher mutation, external-system mutation, direct Git garbage collection, worktree pruning, reflog expiration, or registry correction. It is a prerequisite repair so the pending registry readiness repair and later row-scoped database finalizations can proceed against a valid committed carrier.

## Specification Links

- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the committed database carrier must be evaluable by normal SQLite integrity checks before downstream binary finalization can be trusted.
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - the carrier file is the repository carrier for MemBase state, but semantic authority remains in governed records and lifecycle evidence; this repair restores carrier validity rather than inventing new authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the numbered bridge file chain plus independent GO/VERIFIED statuses govern this implementation and finalization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries explicit PAUTH/project/work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing requirements that make the carrier restoration necessary and bounded.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report and Loyal Opposition verdict must map each requirement to executed integrity, equivalence, patch, and commit-scope checks.
- `GOV-WORK-TREE-HYGIENE-001` - the commit must exclude unrelated dirty files and preserve the real index/worktree except for the reviewed finalization transaction.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, work item, PAUTH, bridge proposal, runtime evidence, implementation report, and verification verdict are durable lifecycle artifacts.

## Prior Deliberations

- `DELIB-20260716-GTKB-BOUNDED-DATABASE-CARRIER-RESTORATION` - owner authorization for this bounded carrier restoration, including no semantic row edits beyond explicitly proven transient-state normalization and no push/release/deploy/credential/destructive cleanup.
- `bridge/gtkb-wi5138-database-incident-recovery-evidence-001.md` and `bridge/gtkb-wi5138-database-incident-recovery-evidence-002.md` - prior incident recovery evidence and independent GO that established the live database as structurally valid after row-level recovery while excluding commit/push/deploy.
- `bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-006.md` - NO-GO documenting that shared `groundtruth.db` binary drift cannot be safely finalized while the committed carrier baseline is invalid.
- `bridge/gtkb-wi5229-binary-verified-finalizer-hunk-patch-006.md` - VERIFIED predecessor proving the disposable-index finalizer can apply reviewed binary patches with `git apply --binary --cached`.
- `bridge/gtkb-wi5142-bounded-readiness-repair-003.md` and `bridge/gtkb-wi5142-bounded-readiness-repair-004.md` - registry-readiness repair was independently approved but implementation-start was blocked by the dirty shared database carrier conflict.
- `bridge/gtkb-wi5178-governed-predecessor-closure-001.md` - existing bridge evidence that live DB validity and committed-carrier validity diverged, making a governed predecessor/carrier repair necessary.

## Owner Decisions / Input

Owner authorization is recorded in `DELIB-20260716-GTKB-BOUNDED-DATABASE-CARRIER-RESTORATION` from the active owner reply `AUTHORIZE BOUNDED DATABASE CARRIER RESTORATION`.

The authorization permits a dedicated governed restoration of the committed database carrier from the valid live database with these hard limits:

- no arbitrary semantic row edit;
- no Git push, release, deployment, credential action, destructive cleanup, or history rewrite;
- preserve unrelated real-index and worktree bytes;
- commit only the restored `groundtruth.db` carrier plus the exact bridge evidence authorized for this restoration;
- use independent GO and independent VERIFIED review.

## Requirement Sufficiency

Existing requirements are sufficient for this bounded restoration. The combination of `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`, `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-WORK-TREE-HYGIENE-001`, and the explicit owner decision above covers the repair. No new requirement is needed before implementation.

## Proposed Implementation Procedure

1. After independent GO, acquire a `go_implementation` claim for `gtkb-wi5329-bounded-database-carrier-restoration` and create the implementation-start packet for exactly `groundtruth.db` and `.gtkb-state/database-carrier-restoration/**`.
2. Record a run directory under `.gtkb-state/database-carrier-restoration/wi5329-YYYYMMDDTHHMMSSZ/` containing command transcripts, manifests, table/count/digest inventories, and candidate hashes. Runtime evidence is by-reference evidence and is not part of the final commit.
3. Validate the live DB with `PRAGMA quick_check` and `PRAGMA foreign_key_check`; stop unless quick check is `ok` and foreign-key check is empty.
4. Fingerprint the active restoration claim row in `work_intent_claims` by exact `thread_slug` and current `session_id`. This table is registered as transient runtime state; the active restoration claim exists only because this implementation had to acquire the lock.
5. Create a sidecar-free SQLite candidate from the live valid DB using the repository snapshot path (`gt db snapshot` / SQLite `VACUUM INTO` semantics) into the run directory.
6. Normalize only the exact active restoration claim row out of the candidate, then create a second sidecar-free final candidate with `VACUUM INTO`. Stop unless exactly one row was normalized and no other table changes are observed.
7. Compute deterministic table counts and row digests for the live source under the same transient-row exclusion and for the final candidate. Stop unless the inventories match exactly and the candidate also passes `quick_check` and empty `foreign_key_check`.
8. Create a reviewed binary patch from committed `HEAD:groundtruth.db` to the final candidate using a disposable Git index: hash the candidate as `groundtruth.db`, update only that path in the disposable index, and emit `git diff --cached --binary --full-index HEAD -- groundtruth.db` to the run directory.
9. Verify the patch in a fresh disposable index with `git apply --binary --cached --check`, apply it, extract the resulting indexed `groundtruth.db`, and rerun SQLite integrity plus candidate SHA comparison.
10. File a Prime Builder implementation report that includes candidate SHA-256, patch SHA-256, exact transient-row normalization evidence, inventory equality evidence, and the intended Loyal Opposition finalization command using `.claude/skills/verify/helpers/write_verdict.py --finalize-verified --hunk-patch .gtkb-state/database-carrier-restoration/RUN_ID/groundtruth-db-carrier.patch`.
11. Loyal Opposition must independently verify and, if satisfied, finalize through the disposable-index binary-patch helper. The final commit path set must be exactly `groundtruth.db` plus `bridge/gtkb-wi5329-bounded-database-carrier-restoration-001.md` through the VERIFIED verdict file.

## Spec-Derived Verification Plan

| Requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | SQLite `PRAGMA quick_check` and `PRAGMA foreign_key_check` against live source, final candidate, patch-applied candidate, and committed `HEAD:groundtruth.db` after finalization | `quick_check` returns `ok`; `foreign_key_check` returns zero rows at every stage |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Table/count/digest inventory comparing live source under exact transient claim exclusion to final candidate | Inventories match exactly; only the current restoration claim row is excluded and documented |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge chain status and author metadata inspection | NEW by Prime Builder, GO/VERIFIED by Loyal Opposition, no same-session self-review |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5329-bounded-database-carrier-restoration` | Preflight passes with no missing required specs |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report plus LO verdict spec-to-test tables | Every linked requirement maps to executed evidence |
| `GOV-WORK-TREE-HYGIENE-001` | Disposable-index finalizer output and `git diff-tree --name-only HEAD` after commit | Commit path set is exactly `groundtruth.db` plus this bridge chain; unrelated staged/worktree paths are excluded |

Additional implementation checks:

```text
groundtruth-kb\.venv\Scripts\gt.exe db snapshot --output-dir .gtkb-state\database-carrier-restoration\RUN_ID\snapshots --staging-dir .gtkb-state\database-carrier-restoration\RUN_ID\staging --retain 1 --daily-days 0 --json
git diff --cached --binary --full-index HEAD -- groundtruth.db
git apply --binary --cached --check .gtkb-state\database-carrier-restoration\RUN_ID\groundtruth-db-carrier.patch
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_lo_verified_commit_atomicity.py -q --tb=short
```

## Risk / Rollback

Primary risk is committing a carrier whose bytes are valid but whose rowset accidentally includes transient implementation state or omits legitimate live rows. The mitigation is exact transient-row fingerprinting plus deterministic live-vs-candidate table/count/digest equality before the implementation report.

Secondary risk is contaminating the commit with unrelated dirty worktree or staged paths. The mitigation is the already-VERIFIED disposable-index binary-patch finalizer and post-commit path-set assertion.

Rollback, if required, is a normal forward Git revert of the single carrier-restoration commit plus a new bridge report explaining the reason. No bridge file is deleted or rewritten. Runtime evidence under `.gtkb-state/database-carrier-restoration/` remains historical by-reference evidence until separately governed cleanup.

## Bridge Filing

This proposal is filed under `bridge/` as `bridge/gtkb-wi5329-bounded-database-carrier-restoration-001.md`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(database): restore valid GroundTruth DB carrier`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
