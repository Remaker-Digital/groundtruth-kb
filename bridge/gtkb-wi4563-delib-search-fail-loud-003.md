NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3821-e2fc-75d2-814f-2a3ec0f71244
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB
Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-4563

# GT-KB Bridge Implementation Report - WI-4563 Deliberation Search Fail-Loud - 003

bridge_kind: implementation_report
Document: gtkb-wi4563-delib-search-fail-loud
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4563-delib-search-fail-loud-002.md
Approved proposal: bridge/gtkb-wi4563-delib-search-fail-loud-001.md
Recommended commit type: fix:

## Implementation Claim

Implemented fail-loud deliberation-search degradation behavior while preserving the existing explicit text-match fallback path.

- Added `DeliberationSearchDegradedError` and `KnowledgeDB.search_deliberations(..., require_semantic=True)`.
- Required semantic callers now raise a structured exception before SQLite LIKE fallback rows can masquerade as authoritative semantic results.
- Default search behavior is preserved: semantic search is attempted, SQLite LIKE still returns rows, and degradation status remains available through `_deliberation_search_status()`.
- `gt deliberations search --semantic-only` now uses the same structured fail-loud path.
- Non-JSON default CLI output now warns when semantic search degrades and results are partial LIKE fallback rows.
- Bridge prior-deliberation prepopulation now records an explicit degradation note instead of silently producing an empty Prior Deliberations section when opted-in semantic search fails.

## Specification Links

- `SPEC-2098`
- `ADR-0001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. This implements the owner-authorized watchdog project scope and the tiered fail-loud restoration/search policy from `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED`.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION`
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED`
- `bridge/gtkb-wi4563-delib-search-fail-loud-001.md`
- `bridge/gtkb-wi4563-delib-search-fail-loud-002.md`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-2098` / `ADR-0001` | `platform_tests/scripts/test_deliberation_search_fail_loud.py` and `groundtruth-kb/tests/test_deliberations.py` verify required semantic search raises on ChromaDB degradation instead of returning silent LIKE fallback rows. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Default search still exposes `_deliberation_search_status()` with `semantic_degraded` and `degradation_reason`, so callers can distinguish canonical SQLite fallback from derived semantic backend state. |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Fail-loud errors and prior-deliberation degradation notes make repeated/unavailable backend failures visible for watchdog escalation. |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | Behavior is surfaced through reusable DB, CLI, and bridge prepopulation paths rather than an ad hoc caller branch. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changes are confined to the approved GT-KB root target paths. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / project-linkage DCL | Work ran after live claim and implementation authorization packet `sha256:2f048701d927c96e517a68de5abb271cc8f7130c32a20ec62ced32abe03d9b26`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff, and format checks passed; exact commands are below. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-wi4563-delib-search-fail-loud --ttl-seconds 2400` - acquired live Prime Builder implementation claim.
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4563-delib-search-fail-loud` - passed; packet `sha256:2f048701d927c96e517a68de5abb271cc8f7130c32a20ec62ced32abe03d9b26`.
- `python -m pytest platform_tests\scripts\test_deliberation_search_fail_loud.py groundtruth-kb\tests\test_deliberations.py groundtruth-kb\tests\test_search_deliberations_always_on_like_merge.py -q --tb=short` - 81 passed, 1 ChromaDB dependency deprecation warning.
- `python -m ruff check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\bridge\prior_deliberations.py groundtruth-kb\tests\test_deliberations.py groundtruth-kb\tests\test_search_deliberations_always_on_like_merge.py platform_tests\scripts\test_deliberation_search_fail_loud.py` - passed.
- `python -m ruff format --check groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\bridge\prior_deliberations.py groundtruth-kb\tests\test_deliberations.py groundtruth-kb\tests\test_search_deliberations_always_on_like_merge.py platform_tests\scripts\test_deliberation_search_fail_loud.py` - passed.

## Observed Results

- Required semantic search fails loudly with structured degradation status.
- Default search still returns LIKE fallback rows and marks degradation explicitly.
- CLI `--semantic-only` exits non-zero with the degradation reason.
- Bridge prior-deliberation prepopulation includes a visible degradation note when semantic search fails.
- Existing always-on LIKE merge behavior is preserved.

## Files Changed

Files changed by this WI:

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py`
- `groundtruth-kb/tests/test_deliberations.py`
- `platform_tests/scripts/test_deliberation_search_fail_loud.py`

No change was required in `groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py`; it was executed as a regression guard.

Other dirty worktree files pre-existed or belong to concurrent bridge and project work and were not edited for this WI.

## Acceptance Criteria Status

- [x] Required governance search callers receive explicit degradation errors instead of silent empty/fallback results.
- [x] Explicit text-match/default fallback remains available and tested.
- [x] Search status distinguishes derived semantic backend degradation from canonical SQLite fallback rows.
- [x] Prior-deliberation prepopulation emits visible degradation evidence.
- [x] Focused spec-derived tests, ruff check, and ruff format check pass.

## Risk And Rollback

Residual risk is moderate because this changes CLI/error behavior for strict semantic search. Default search remains backward-compatible. Rollback is a single revert of the five WI files above; bridge audit files remain append-only and must not be removed.

## Loyal Opposition Asks

1. Verify that default fallback compatibility is preserved while required semantic callers now fail loud.
2. Return `VERIFIED` if the implementation satisfies the approved proposal, otherwise return `NO-GO` with concrete target-path findings.
