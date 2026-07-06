NEW

# WI-4563 Deliberation Search Fail-Loud Degradation

bridge_kind: prime_proposal
Document: gtkb-wi4563-delib-search-fail-loud
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3821-e2fc-75d2-814f-2a3ec0f71244
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-4563

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py", "groundtruth-kb/tests/test_deliberations.py", "groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py", "platform_tests/scripts/test_deliberation_search_fail_loud.py"]

implementation_scope: source, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make mandatory deliberation search degradation loud instead of silently falling back to low-recall SQLite LIKE behavior. When ChromaDB is unavailable, stale, or failing in a context that requires semantic deliberation search, the search surface should emit explicit degradation evidence and fail or warn according to the calling context rather than returning an apparently authoritative empty result.

This slice must preserve safe canonical SQLite storage and should avoid breaking explicit lightweight or test contexts that intentionally choose text-match behavior. The behavior should be controlled and testable, not hidden behind implicit fallback.

## Specification Links

- `SPEC-2098` - Requires the Deliberation Archive to support semantic search for reasoning artifacts.
- `ADR-0001` - Separates authoritative MemBase/Deliberation Archive records from derived semantic indexes, while preserving the DA semantic tier as a required retrieval surface for proposal/review work.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Requires current-state claims and search-quality claims to be explicit about canonical and derived sources.
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires DA/ChromaDB availability to be covered by the platform watchdog.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Requires fail-loud escalation for unavailable or unsafe restoration/search dependencies.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires implementation paths to stay inside `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires bridge-mediated workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires complete specification linkage and verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the project authorization, project, and work item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires executed spec-derived tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - Treats WI-4563 as durable work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Require durable artifact linkage and lifecycle evidence.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized WI-4563 as part of the watchdog project.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected fail-loud handling for unsafe/canonical failures and service degradation.
- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` records that WI-4563 was un-deferred because silent degradation should no longer be accepted.

Deliberation search command used before drafting:

```powershell
gt deliberations search "WI-4563 mandatory deliberation search degrades silently SQLite LIKE fail loudly ChromaDB unavailable" --json
```

## Owner Decisions / Input

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` authorizes WI-4563 implementation under the active project authorization.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` is the owner policy that moves this from silent degradation to fail-loud visibility.

## Requirement Sufficiency

Existing requirements sufficient. WI-4563, `SPEC-2098`, `ADR-0001`, and the watchdog safety DCL define the needed search-time degradation behavior.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `SPEC-2098`, `ADR-0001` | Required deliberation-search callers receive explicit degradation evidence instead of silent empty SQLite-LIKE results when semantic search is unavailable. | `python -m pytest platform_tests/scripts/test_deliberation_search_fail_loud.py groundtruth-kb/tests/test_deliberations.py -q --tb=short` |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Search responses distinguish canonical DA rows from derived ChromaDB search state and expose stale/unavailable derived state. | `python -m pytest platform_tests/scripts/test_deliberation_search_fail_loud.py -q --tb=short` |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Repeated/unavailable backend failure is reported as fail-loud degradation suitable for watchdog escalation, not invisible fallback. | `python -m pytest platform_tests/scripts/test_deliberation_search_fail_loud.py -q --tb=short` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files stay under declared GT-KB root paths. | `git diff --name-only -- groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge/prior_deliberations.py groundtruth-kb/tests/test_deliberations.py groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py platform_tests/scripts/test_deliberation_search_fail_loud.py` |

Implementation report must also include `ruff check` and `ruff format --check` for changed Python files.

## Risk / Rollback

Primary risk is breaking intentional text-match fallback in tests or lightweight adopter environments. The implementation should distinguish mandatory-governance search contexts from explicit text-match/fallback contexts. Rollback is a single-commit revert of search behavior and tests.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4563-delib-search-fail-loud`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: this slice repairs silent deliberation-search degradation in mandatory governance search paths.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
