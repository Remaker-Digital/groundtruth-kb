NEW

# WI-4562 Deliberation Search Backend Doctor Check

bridge_kind: prime_proposal
Document: gtkb-wi4562-delib-search-backend-doctor
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
Work Item: WI-4562

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_doctor.py", "platform_tests/scripts/test_deliberation_search_backend_doctor.py"]

implementation_scope: source, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add a `gt project doctor` health check for the deliberation-search backend. The check should surface whether ChromaDB is importable/available through the canonical `HAS_CHROMADB` path and whether the canonical Chroma index is present and fresh enough for mandatory deliberation searches.

This is the visibility half of the deliberation-search reliability pair. It should warn or fail loudly enough to prevent silent governance degradation, while WI-4563 handles search-time fail-loud behavior.

## Specification Links

- `SPEC-2098` - Requires the Deliberation Archive to provide structured storage and semantic search for reasoning artifacts.
- `ADR-0001` - Defines the Three-Tier Memory Architecture with MemBase, Deliberation Archive, and MEMORY.md as distinct tiers.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Requires state claims to derive from fresh canonical reads, not stale derived substitutes.
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires platform-wide scheduled availability verification for service components including Deliberation Archive/ChromaDB.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Requires fail-loud escalation for unavailable canonical or at-risk service state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires implementation paths to stay inside `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires bridge-mediated workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires complete specification linkage and verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the project authorization, project, and work item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires executed spec-derived tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - Treats WI-4562 as durable work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Require durable artifact linkage and lifecycle evidence.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized WI-4562 as part of the watchdog project.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner policy says service and SoT failures must be auto-healed when safe or fail loud when not.
- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` specifically notes WI-4562 and WI-4563 are re-scoped into this project.

Deliberation search command used before drafting:

```powershell
gt deliberations search "WI-4562 ChromaDB deliberation search backend doctor check index fresh HAS_CHROMADB" --json
```

## Owner Decisions / Input

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` authorizes WI-4562 implementation under the active project envelope.
- The WI-4562 status detail records owner-requested un-deferral and re-scope with WI-4563 under this project.

## Requirement Sufficiency

Existing requirements sufficient. WI-4562, `SPEC-2098`, `ADR-0001`, and the watchdog ADR/DCL define the required doctor visibility.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `SPEC-2098`, `ADR-0001` | Doctor check distinguishes healthy semantic backend from unavailable/degraded backend and reports Chroma index presence/freshness. | `python -m pytest platform_tests/scripts/test_deliberation_search_backend_doctor.py groundtruth-kb/tests/test_doctor.py -q --tb=short` |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Check reads canonical backend/index state instead of stale generated summaries. | `python -m pytest platform_tests/scripts/test_deliberation_search_backend_doctor.py -q --tb=short` |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | Doctor result can be consumed as a watchdog service-health component. | `python -m pytest platform_tests/scripts/test_deliberation_search_backend_doctor.py -q --tb=short` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files stay under declared GT-KB root paths. | `git diff --name-only -- groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_doctor.py platform_tests/scripts/test_deliberation_search_backend_doctor.py` |

Implementation report must also include `ruff check` and `ruff format --check` for changed Python files.

## Risk / Rollback

Primary risk is a noisy doctor check that fails when semantic search is intentionally absent in lightweight environments. The implementation should classify expected no-search environments separately from a GT-KB governance degradation where semantic search is required. Rollback is a single-commit revert of the doctor check and tests.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4562-delib-search-backend-doctor`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: this slice repairs a silent observability gap in mandatory deliberation-search health.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
