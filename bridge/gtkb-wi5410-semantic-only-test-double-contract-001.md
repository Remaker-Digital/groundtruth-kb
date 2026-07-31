NEW

# WI-5410: Refresh semantic-only search test doubles

bridge_kind: prime_proposal
Document: gtkb-wi5410-semantic-only-test-double-contract
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-desktop-019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5410

target_paths: ["groundtruth-kb/tests/test_cli_deliberations.py", "platform_tests/scripts/test_deliberation_search_stale_segment.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Update two deterministic `KnowledgeDB.search_deliberations` test doubles to
accept and verify the production `require_semantic` keyword. Production now
calls `search_deliberations(..., require_semantic=True)` for
`gt deliberations search --semantic-only`, but both fakes still expose the old
`query, limit` signature. The current adjacent lane therefore stops with two
`TypeError` failures before exercising either the text-fallback filter or the
fail-loud degraded-search behavior.

The first fake will capture/assert `require_semantic=True` while returning its
canned text-only row, preserving the CLI defense-in-depth assertion that such a
row is never printed. The stale-segment fake will capture/assert the same flag
and raise `DeliberationSearchDegradedError` with its existing `stale_segment`
status, matching the current database contract and preserving the non-zero,
no-fallback-output assertions. No production source, database, Chroma store,
search semantics, or CLI behavior changes.

## Specification Links

- `SPEC-2098` - requires executable semantic search for Deliberation Archive reasoning artifacts.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - requires semantic-only consumers and tests to reflect the current production API rather than a stale test-double contract.
- `GOV-RELIABILITY-FAST-LANE-001` - supports the bounded two-test-file correction of a deterministic regression without broad source churn.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires preservation of fail-loud semantic-only behavior and default SQLite fallback behavior.
- `GOV-WORK-TREE-HYGIENE-001` - requires exact ownership of the clean two-file test-only scope.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - requires separate exact mechanical authority before any later test-only finalization commit.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO/start and post-implementation VERIFIED for the protected tests.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - binds both stale doubles to the semantic-search and fail-loud requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5410 to the active modernization-assurance project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires independent execution of the focused and adjacent semantic-search lanes before VERIFIED.

## Prior Deliberations

- `DELIB-20265309` - independently VERIFIED the production `require_semantic` fail-closed implementation and its stale-segment behavior.
- `DELIB-FAB17-REMEDIATION-20260610` - owner-backed Deliberation Archive/Chroma read-path reliability scope that the verified implementation extended.
- `DELIB-0703` and `DELIB-20263645` - prior findings that semantic degradation must be distinguishable from a genuine no-result search.

WI-5410 changes only stale test adapters. It does not reopen or alter the
already verified production decision.

## Owner Decisions / Input

No additional owner decision is required. The full modernization assurance
program is project-authorized, and the owner directed every discovered defect
or omission to be captured and corrected while work continues. Active
authorization
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
covers tests and governance evidence while preserving independent GO/start,
VERIFIED, and mechanical Git gates.

## Requirement Sufficiency

Existing requirements sufficient. Production behavior and the previously
VERIFIED fail-loud contract are clear: semantic-only mode passes
`require_semantic=True`, rejects degraded semantic search, and never presents
SQLite fallback as semantic evidence. Only the test doubles are stale.

## Spec-Derived Verification Plan

`SPEC-2098`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, and the non-impairment rule
map to the full adjacent semantic-search lane. Current baseline: 11 passed and
2 failed, both with an unexpected `require_semantic` keyword. Expected result
after the exact two-file correction: 13 passed.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_deliberations.py::TestDeliberationsSearch groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py platform_tests/scripts/test_deliberation_search_stale_segment.py -q --tb=short --timeout=600
```

The exact original failing node must also pass independently and assert that
the fake observed `require_semantic=True` while the canned text row remained
absent from output.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_cli_deliberations.py::TestDeliberationsSearch::test_search_semantic_only_rejects_text_fallback_rows -q --tb=short --timeout=600
```

Test hygiene maps to Ruff, format, whitespace, and exact-scope inspection.
Expected result: clean checks and no production-file diff.

```text
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/tests/test_cli_deliberations.py platform_tests/scripts/test_deliberation_search_stale_segment.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/tests/test_cli_deliberations.py platform_tests/scripts/test_deliberation_search_stale_segment.py
git diff --check -- groundtruth-kb/tests/test_cli_deliberations.py platform_tests/scripts/test_deliberation_search_stale_segment.py
git diff -- groundtruth-kb/tests/test_cli_deliberations.py platform_tests/scripts/test_deliberation_search_stale_segment.py
```

`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires independent LO to
rerun every command and verify both doubles assert the current keyword contract
without weakening any output or exit-code assertion.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5410 broad-suite modernization failure after the require_semantic production API change",
  "canonical_authority": "KnowledgeDB.search_deliberations require_semantic contract and DELIB-20265309 VERIFIED behavior",
  "primary_route": "gt deliberations search --semantic-only",
  "before_behavior": "two monkeypatched search doubles reject the production keyword and prevent semantic-only assertions from running",
  "after_behavior": "both doubles verify require_semantic=True and exercise the existing text-row suppression and degraded-search error paths",
  "self_descriptive_naming": "captured require_semantic flags and DeliberationSearchDegradedError make each test's contract explicit",
  "obsolete_guidance_disposition": "old two-argument fake signatures are replaced; no production guidance changes",
  "history_preservation": "existing test intent, canned rows, stale_segment reason, exit-code checks, and output exclusions remain intact",
  "baseline": {
    "adjacent_lane": "11 passed, 2 failed",
    "failure_class": "TypeError unexpected keyword require_semantic"
  },
  "expected_result": {
    "adjacent_lane": "13 passed",
    "semantic_only_flag": "asserted true in both doubles"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the later two-test-file commit without changing production source",
    "test": "rerun the 13-test adjacent lane, original node, Ruff, and whitespace checks"
  },
  "hard_invariants": [
    "no production source, database, Chroma index, bridge, dispatcher, TAFE, harness, credential, deployment, release, or external-system mutation",
    "semantic-only degradation remains non-zero and fail loud",
    "text_match fallback rows remain absent from semantic-only output",
    "default non-semantic-only fallback behavior remains covered and unchanged"
  ],
  "fail_closed_conditions": [
    "either fake does not assert require_semantic=True",
    "fallback rows appear or degraded search exits successfully",
    "any adjacent test, lint, format, whitespace, or exact-scope check fails",
    "implementation-start or independent VERIFIED authority is absent or mismatched"
  ],
  "essential_context_preservation": "the verified production API, semantic/text result distinction, stale-segment diagnostics, and concurrent worktree ownership remain intact"
}
```

## Risk / Rollback

Risk is limited to accidentally weakening the mocks so they no longer prove
the current keyword or fail-loud behavior. Explicit flag assertions and the
full adjacent lane prevent that. Under separate exact mechanical authority,
finalization should be one focused `test` commit containing only these two
files. Rollback is a separately governed revert of that exact commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5410-semantic-only-test-double-contract`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - updates stale deterministic doubles to the already implemented API
without changing production behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
