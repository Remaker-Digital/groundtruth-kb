NEW

# WI-5416: Restore the missing runtime-recovery package residue

bridge_kind: prime_proposal
Document: gtkb-wi5416-runtime-recovery-package-residue
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5416

target_paths: ["groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py", "groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt exactly the two pre-existing untracked runtime-recovery package files
omitted when WI-5313 was physically finalized. Commit `42a252ab` already
contains the frozen eight-test acceptance contract, but HEAD cannot import
`groundtruth_kb.runtime_recovery` without these source carriers. The candidate
implements deterministic SQLite-backed claims, leases, checkpoints, bounded
retry, quarantine, idempotent completion, and read-only recovery observation;
all eight focused tests pass.

This is a byte-preserving residue closure. It does not alter the candidate,
integrate the later modernization workflow, touch live dispatcher/TAFE/harness
state, mutate `groundtruth.db`, or perform any Git operation. A later exact
mechanical finalizer may commit only independently VERIFIED source bytes under
separate authority.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — requires modernization recovery behavior to remain reportable and durable without mutating live dispatcher, bridge, harness, or application state.
- `GOV-WORK-TREE-HYGIENE-001` — requires explicit ownership and governed finalization of the two dirty source carriers without absorbing foreign dirt.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires independent GO before protected source adoption and independent verification afterward.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — binds the exact source residue to the governing requirements and focused tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5416 to its active tree-stabilization project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent execution of every spec-derived test before VERIFIED.

## Prior Deliberations

- `INTAKE-8242840e` — Intake: Simple dispatcher retry and OPS-owned failed-workflow recovery
- `INTAKE-07c68e70` — Intake: Failed workflow recovery uses supersede terminology

Those records establish bounded retry/recovery semantics and append-only
supersession language for failed operations. This proposal restores the generic
durable substrate already tested by WI-5313; it does not change dispatcher
recovery policy or bridge lineage metadata.

## Owner Decisions / Input

The owner authorized the full modernization program at the project level and
directed every discovered flaw or omission to become an `origin=hygiene` work
item while work continues. Active authorization
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` covers source,
test, metadata, and governance evidence while retaining independent GO,
claim/start, VERIFIED, and mechanical Git gates. No additional owner decision
is required for this proposal or its independently GO-approved source adoption.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
governs the recovery boundary, `GOV-WORK-TREE-HYGIENE-001` governs physical
residue closure, and the bridge/project-linkage requirements govern the
transaction. No requirement change is proposed.

## Spec-Derived Verification Plan

`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` and the behavior-bearing package
surface map to the frozen eight-test recovery contract. Expected result: eight
passed, with no access to live dispatcher, bridge, harness, or `groundtruth.db`.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_runtime_recovery.py -q --tb=short
```

`GOV-WORK-TREE-HYGIENE-001` maps to exact source hygiene. Expected result: no
lint, format, whitespace, or undeclared-file discrepancy within the two target
paths.

```text
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py
```

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` maps to independent LO review
of the exact two source hashes and all commands above. Expected result: the next
terminal verdict is `VERIFIED` only when candidate bytes and evidence match.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5416 recovering falsely closed WI-5313 source residue under the frozen modernization acceptance contract",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the committed platform_tests/scripts/test_modernization_runtime_recovery.py contract",
  "primary_route": "groundtruth_kb.runtime_recovery.RecoveryStore",
  "before_behavior": "HEAD contains the frozen runtime-recovery test but no importable runtime_recovery package, leaving a partial implementation and dirty source residue",
  "after_behavior": "the exact reviewed package is the canonical import surface and eight focused tests prove claims, retries, recovery, quarantine, idempotency, and observation",
  "self_descriptive_naming": "runtime_recovery, RecoveryStore, ClaimOutcome, RuntimeStatus, and operation event names state their ownership and lifecycle semantics",
  "obsolete_guidance_disposition": "no guidance carrier is changed; the falsely closed checker-only state is superseded by the governed package addition",
  "history_preservation": "WI-5313 and commit 42a252ab remain unchanged while WI-5416 records the missing physical residue append-only",
  "baseline": {
    "head_package_present": false,
    "dirty_source_files": 2,
    "focused_tests": "8 passed in 0.73 seconds"
  },
  "expected_result": {
    "head_package_present_after_separate_finalization": true,
    "focused_tests": "8 passed",
    "foreign_paths_changed": 0
  },
  "rollback": {
    "instructions": "under separate authority, revert only the later focused source-addition commit without amending history",
    "test": "rerun the eight focused recovery tests and exact two-path Git inspection"
  },
  "hard_invariants": [
    "no live groundtruth.db, dispatcher, TAFE, bridge, harness, credential, external-system, deployment, or release mutation",
    "no Git action in this implementation transaction",
    "stale ownership, operation collisions, exhausted retries, and conflicting completion fail closed"
  ],
  "fail_closed_conditions": [
    "candidate bytes differ from independently reviewed hashes",
    "any focused test, lint, format, or whitespace check fails",
    "implementation-start authority is absent or mismatched",
    "any path outside the two declared source additions would change"
  ],
  "essential_context_preservation": "the frozen test, WI-5313 history, project PAUTH, independent bridge gates, and all foreign worktree bytes remain intact"
}
```

## Risk / Rollback

Risk is bounded to introducing a SQLite journal package; accidental inclusion
of WI-5315 workflow or live runtime state is the principal transaction risk.
Exact target paths, byte hashes, and the frozen tests constrain it. Under
separate mechanical authority, finalization should be one focused `fix` commit
containing only these additions. Rollback, if later required, is a separately
governed revert of that exact commit; existing history is not amended and
foreign worktree content is untouched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5416-runtime-recovery-package-residue`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — restores source implementation omitted from an earlier independently
reviewed runtime-recovery slice; it is not a new feature or test-only change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
