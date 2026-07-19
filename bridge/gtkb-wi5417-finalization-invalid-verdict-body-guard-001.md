NEW

# WI-5417: Block helper-invalid VERIFIED bodies from finalization repair

bridge_kind: prime_proposal
Document: gtkb-wi5417-finalization-invalid-verdict-body-guard
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
Work Item: WI-5417

target_paths: ["docs/procedures/per-thread-finalization-repair.md", "scripts/per_thread_finalization_repair.py", "platform_tests/scripts/test_per_thread_finalization_repair.py"]

implementation_scope: source, test, documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Adopt the exact three-path follow-up that makes the report-only per-thread
finalization planner reuse the canonical `write_verdict.validate_verified_body`
evidence floor. A clean-target terminal `VERIFIED` body that lacks recommended
commit type, spec-to-test mapping, or executed-command evidence is currently
classified commit-ready. The candidate instead returns
`terminal_verified_blocked_invalid_verdict_body`, preserves STOP, and directs a
governed archive/reissue path. Eleven focused tests pass.

The scope does not mutate bridge history, stage or commit files, alter
dispatcher/TAFE/harness state, change finalizer validation semantics, or
perform cleanup. It imports and applies the existing canonical validator,
updates one fixture and regression, and documents the new classification.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` — requires deterministic report-first classification and explicit owner/governance authority before any cleanup or commit.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — requires reliable automatic terminal-resolution handling and therefore rejects malformed terminal evidence from the automatic-ready path.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` — requires scoped finalization to fail closed when verification or authority evidence is incomplete or ambiguous.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — requires the planner to preserve report-only behavior and fail closed on unreliable evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires append-only bridge history and independent GO/VERIFIED around the protected implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — binds the exact planner, test, and runbook changes to all governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5417 to its active tree-stabilization authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — defines the evidence floor reused by the planner and requires independent test execution before VERIFIED.

## Prior Deliberations

- `INTAKE-9314e628` — Intake: LO VERIFIED verdict required fields for OPS work

That intake establishes that `VERIFIED` is structurally meaningful only when
its required evidence fields are present. WI-5417 applies the already canonical
validator to the repair planner rather than inventing a second field list; it
does not change who may review or write verdicts.

## Owner Decisions / Input

The owner authorized the full modernization and tree-stabilization programs at
the project level, directed flawed audit trails to be fixed without blocking
work, and set clean-tree completion as the active goal. Active authorization
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` covers source,
test, documentation, and governance evidence while retaining independent GO,
claim/start, VERIFIED, and mechanical Git gates. No additional owner decision
is required for this proposal or its independently GO-approved implementation.

## Requirement Sufficiency

Existing requirements sufficient. Worktree hygiene, VERIFIED evidence,
governed Git lifecycle, non-impairment, bridge authority, and project linkage
fully define the expected fail-closed behavior. No requirement change is
proposed.

## Spec-Derived Verification Plan

`GOV-WORK-TREE-HYGIENE-001`, `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`,
`DCL-GIT-BRANCH-BINDING-PROMOTION-001`, and the VERIFIED evidence requirement
map to the focused planner suite. Expected result: 11 passed; a helper-valid
clean terminal verdict remains a candidate, while a helper-invalid body is a
STOP classification with the canonical validation error.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_per_thread_finalization_repair.py -q --tb=short
```

Source hygiene maps to lint, format, whitespace, and exact three-path diff
inspection. Expected result: clean checks and no unrelated hunks.

```text
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
git diff --check -- docs/procedures/per-thread-finalization-repair.md scripts/per_thread_finalization_repair.py platform_tests/scripts/test_per_thread_finalization_repair.py
```

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` maps to independent LO review
of exact diff hashes and all commands above. Expected result: the implementation
is `VERIFIED` only when the test, source, and runbook agree on the fail-closed
classification.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5417 follow-up to resolved WI-5116 and the active modernization clean-tree finalization goal",
  "canonical_authority": "write_verdict.validate_verified_body and DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
  "primary_route": "python scripts/per_thread_finalization_repair.py --format json",
  "before_behavior": "a clean-target terminal VERIFIED body can be classified commit-ready even when the canonical finalizer would reject its evidence body",
  "after_behavior": "the planner calls the canonical validator and emits a named STOP classification with governed archive and reissue guidance",
  "self_descriptive_naming": "terminal_verified_blocked_invalid_verdict_body and finalizer_validation_error expose the exact blocking state",
  "obsolete_guidance_disposition": "the runbook replaces the prior clean-target-only candidate rule with the canonical evidence-floor requirement",
  "history_preservation": "invalid terminal history remains unchanged and is repaired only through append-only archive and reissue governance",
  "baseline": {
    "invalid_body_classification": "terminal_verified_repair_candidate",
    "planner_mode": "report-only",
    "focused_tests": "11 passed in 6.40 seconds"
  },
  "expected_result": {
    "invalid_body_classification": "terminal_verified_blocked_invalid_verdict_body",
    "planner_mode": "report-only",
    "valid_candidate_regression": "unchanged and passing"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the later focused three-path commit without amending history",
    "test": "rerun the 11 focused planner tests and report-only mutation audit"
  },
  "hard_invariants": [
    "the planner remains report-only and performs no stage, commit, delete, revert, push, bridge, dispatcher, TAFE, harness, credential, deployment, or release mutation",
    "terminal bridge history is never edited in place",
    "one canonical finalizer validation implementation defines verdict-body sufficiency"
  ],
  "fail_closed_conditions": [
    "canonical verdict validation raises any error",
    "candidate diff hashes differ from independent review",
    "any focused test, lint, format, whitespace, or exact-scope check fails",
    "implementation-start authority is absent or mismatched"
  ],
  "essential_context_preservation": "valid candidate behavior, bridge history, independent review authority, existing finalizer semantics, and all foreign worktree bytes remain intact"
}
```

## Risk / Rollback

Risk is bounded to importing the canonical helper and adding one new
classification; path/import drift could make the planner unavailable, while an
overbroad catch could hide programming errors. The candidate catches only
`VerifiedFinalizationError`, and 11 tests cover valid, invalid, dirty, missing,
and mixed-provenance cases. Under separate mechanical authority, finalization
should be one focused `fix` commit containing only these three paths. Rollback,
if later required, is a separately governed revert of that exact commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5417-finalization-invalid-verdict-body-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — closes a false commit-ready classification in the finalization repair
planner and aligns its documentation/test contract with the canonical helper.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
