NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3216 Deliberation Archive Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3216-deliberation-archive-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3216

target_paths: ["platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py"]

## Claim

WI-3216 should add explicit deterministic coverage for the live `SPEC-2098` Deliberation Archive contract and route that evidence through the bridge for Loyal Opposition verification.

`SPEC-2098` is implemented platform infrastructure, not an Agent Red application feature. The owner authorization snapshot nevertheless includes `WI-3216`, and the WI is still open/backlogged in `PROJECT-AGENT-RED-TEST-COVERAGE-GAPS`. Current MemBase now has one mapped `SPEC-2098` test artifact, `TEST-11217`, pointing at `platform_tests/scripts/test_fab17_chroma_read_path.py::test_search_degrades_on_chroma_crash`; that test passes, but it covers only the Chroma read-path degradation slice. It does not by itself exercise the broader `SPEC-2098` archive surface: structured deliberation storage, closed source-type set, raw-hash/redacted-content behavior, source-ref idempotence, multi-link lookup, search fallback contract, Chroma metadata/chunk indexing, and harvest linkage for bridge-thread artifacts.

This proposal is therefore a bounded `test_addition` item. It adds one focused platform test module and expects no production source mutation. Existing production code in `groundtruth-kb/src/groundtruth_kb/db.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `scripts/harvest_session_deliberations.py` remains the read-only implementation surface under test.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-2098` and the incorporated proposal text in `applications/Agent_Red/docs/proposals/DELIBERATION-ARCHIVE-PROPOSAL.md` give enough implementation detail for deterministic coverage: the archive stores structured deliberation rows, supports source types `lo_review`, `proposal`, `owner_conversation`, `report`, `session_harvest`, and `bridge_thread`, stores redacted full content with a raw-content hash, supports primary and relation links to specs and work items, supports semantic search with SQLite fallback, indexes Chroma chunks with metadata, and harvests bridge-thread/session artifacts into the archive.

The current WI is a test-coverage gap, not a new feature request. No owner clarification is required because the proposal only adds tests over the already-implemented, in-root platform behavior and does not add new work items, formal artifacts, release state, deployment state, credentials, or Agent Red application behavior.

## In-Root Placement Evidence

The implementation target is under the GT-KB root:

- `E:\GT-KB\platform_tests\scripts\test_deliberation_archive_spec2098_coverage.py`

Read-only verification may inspect these in-root implementation and historical evidence paths:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\scripts\harvest_session_deliberations.py`
- `E:\GT-KB\groundtruth-kb\tests\test_deliberations.py`
- `E:\GT-KB\groundtruth-kb\tests\test_cli_deliberations.py`
- `E:\GT-KB\groundtruth-kb\tests\test_search_deliberations_always_on_like_merge.py`
- `E:\GT-KB\groundtruth-kb\tests\test_deliberation_index_embedding_timeout.py`
- `E:\GT-KB\platform_tests\scripts\test_fab17_chroma_read_path.py`
- `E:\GT-KB\platform_tests\scripts\test_harvest_session_thread_level.py`
- `E:\GT-KB\applications\Agent_Red\docs\proposals\DELIBERATION-ARCHIVE-PROPOSAL.md`

## Specification Links

- `SPEC-2098` - Direct Deliberation Archive requirement for structured storage, source types, ChromaDB semantic search, SQLite fallback, and session/bridge harvest.
- `GOV-08` - Canonical Knowledge Database / MemBase behavior; the Deliberation Archive is a governed MemBase-adjacent memory tier and must preserve canonical SQLite rows even when ChromaDB is unavailable.
- `GOV-10` - Test artifacts must exercise live project interfaces; this proposal adds executable tests over production `KnowledgeDB` and harvest interfaces instead of phantom-only evidence.
- `SPEC-1649` - Master test plan/live-interface policy; the new test file provides deterministic repository-native coverage.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance; the new test file creates visible executable evidence for the WI.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - The Deliberation Archive search/read path is a source-of-truth freshness surface and must not silently lose recently inserted rows when semantic indexing is degraded.
- `SPEC-DA-HARVEST-INCLUSION` - The test plan covers bridge-thread/session harvest inclusion behavior as part of the `SPEC-2098` archive surface.
- `SPEC-DA-MECHANICAL-ENFORCE` - Harvest/index behavior must be mechanically testable rather than hand-waved in reports.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies changed-file hygiene; Python coverage will use targeted pytest plus ruff check and ruff format checks on the touched test file.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing AUQ-backed project authorization; this proposal requests no new owner decision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms all files are under `E:\GT-KB`; this proposal does not depend on out-of-root archives.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3216`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying phantom-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0651` - Historical Deliberation Archive completion NO-GO identifying missing known-answer and search-enabled regression evidence.
- `DELIB-20261682` - FAB-17 DA/Chroma read-path GO carrying `SPEC-2098` search-degradation coverage forward.
- `DELIB-20263399` - ChromaDB Python 3.14 gate VERIFIED evidence, confirming semantic-only search behavior after Chroma availability repair.
- `DELIB-20263581` - GroundTruth DB migration VERIFIED evidence, including Deliberation Archive path migration and known-answer search test execution.
- `gt deliberations list --work-item-id WI-3216 --limit 5 --json` returned `[]`; no WI-linked deliberation entries exist for `WI-3216`.
- `gt deliberations list --spec-id SPEC-2098 --limit 5 --json` returned several unrelated/high-volume GT-KB bridge records. They confirm the archive itself is in active use, but they do not provide a bridge chain specific to this work item or broad replacement coverage for this test-gap item.
- `gt bridge threads --wi WI-3216 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3216 --json` shows open/backlogged `WI-3216`, source spec `SPEC-2098`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and an acceptance summary to add or map deterministic test evidence for the feature/spec gap.
- `gt spec show SPEC-2098 --json` shows title "Deliberation archive: structured storage and semantic search for reasoning artifacts", status `implemented`, and requirements for a deliberations table, structured source types, ChromaDB semantic search, session harvest indexing, and bridge-thread source type support.
- `gt tests list --spec-id SPEC-2098 --json` now returns `TEST-11217`, mapped to `platform_tests/scripts/test_fab17_chroma_read_path.py::test_search_degrades_on_chroma_crash`, with `last_result: null`.
- `python -m pytest platform_tests\scripts\test_fab17_chroma_read_path.py -q --tb=short` passed locally with `7 passed`, confirming that the existing mapped test is executable and healthy.
- `groundtruth-kb/src/groundtruth_kb/db.py` implements `insert_deliberation()`, `upsert_deliberation_source()`, `link_deliberation_spec()`, `link_deliberation_work_item()`, `_index_deliberation_in_chroma()`, `search_deliberations()`, and `rebuild_deliberation_index()`.
- `groundtruth-kb/tests/test_deliberations.py` already covers broad CRUD, source types, redaction, multi-link, fallback search, chunking, metadata builder, optional semantic search, stale chunk deletion, rebuild, and Chroma failure containment; the coverage is real but not directly bridged to this work item.
- `groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py` covers always-on SQLite LIKE merge behavior.
- `groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py` covers bounded Chroma indexing and search degradation.
- `scripts/harvest_session_deliberations.py` harvests LO reports and bridge-thread artifacts into the Deliberation Archive using `upsert_deliberation_source()` and relation links.
- `platform_tests/scripts/test_harvest_session_thread_level.py` covers the newer thread-level harvest extension, but does not serve as a broad SPEC-2098 WI-3216 closure artifact.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3216-deliberation-archive-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `work_items: ["WI-3216"]`
- `warnings.missing_parent_dirs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3216-deliberation-archive-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py`.
2. In the new test file, create a temp `KnowledgeDB` instance and verify that all `SPEC-2098` source types can be inserted through `insert_deliberation()`, including `bridge_thread` and `session_harvest`.
3. Verify structured storage fields on a representative row: `spec_id`, `work_item_id`, `source_ref`, `participants`, `outcome`, `session_id`, `origin_project`, `origin_repo`, `content_hash`, `sensitivity`, and `redaction_state`.
4. Verify raw content hashing plus redacted stored content by inserting content containing a synthetic credential pattern and asserting the raw value is absent from SQLite-returned content while the raw-content hash matches the pre-redaction text.
5. Verify source-ref/content-hash idempotence through `upsert_deliberation_source()`.
6. Verify primary plus relation-link lookup through `link_deliberation_spec()`, `link_deliberation_work_item()`, `get_deliberations_for_spec()`, and `get_deliberations_for_work_item()`.
7. Verify `search_deliberations()` returns the newly inserted row through the SQLite LIKE path when ChromaDB is unavailable or disabled, including stable result contract fields `search_method`, `score`, `matched_chunk_id`, and `matched_chunk_preview`.
8. Verify `_index_deliberation_in_chroma()` against a deterministic stub collection: stale chunks are deleted by `delib_id`, indexed documents use redacted content, chunk IDs are unique and versioned, and metadata includes `delib_id`, `source_type`, `chunk_index`, `chunk_count`, `source_ref`, `sensitivity`, and `redaction_state`.
9. Verify `scripts/harvest_session_deliberations.py` bridge-thread harvest behavior with a synthetic in-root bridge file: extracted `SPEC-2098`/`WI-3216` IDs are passed into the archive path, the source type is `bridge_thread`, and repeated source-ref/content-hash handling remains idempotent.
10. Do not change production source, formal artifacts, project membership, release/deployment state, existing MemBase test rows, ChromaDB persisted state, credentials, or Agent Red application behavior.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-2098` | New deterministic tests verify source-type acceptance, structured row storage, redaction/hash behavior, source-ref idempotence, relation links, search fallback contract, Chroma chunk metadata, and bridge-thread harvest behavior. |
| `GOV-08`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Tests prove SQLite rows remain canonical and immediately searchable through LIKE when semantic indexing is unavailable/degraded. |
| `SPEC-DA-HARVEST-INCLUSION`, `SPEC-DA-MECHANICAL-ENFORCE` | The synthetic bridge-thread harvest test proves bridge artifacts enter the archive path with parsed spec/WI identifiers and idempotent source-ref/content-hash behavior. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against live `KnowledgeDB` and harvest interfaces, creating an explicit test file for WI-3216 rather than relying on phantom-only or narrow historical evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3216-deliberation-archive-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, targeted pytest, adjacent pytest, and whitespace diff checks on touched files. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py -q --tb=short
python -m pytest platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py platform_tests/scripts/test_fab17_chroma_read_path.py platform_tests/scripts/test_harvest_session_thread_level.py groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py -q --tb=short
python -m ruff check platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py
python -m ruff format --check platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py
git diff --check -- platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py
```

## Acceptance Criteria

- PASS when all six `SPEC-2098` source types are accepted by the live `KnowledgeDB.insert_deliberation()` path.
- PASS when a representative deliberation row preserves structured fields and participants while storing redacted content rather than raw credential text.
- PASS when `content_hash` is computed from pre-redaction content.
- PASS when source-ref/content-hash upsert returns the existing row instead of creating duplicates.
- PASS when relation-link lookup returns deliberations linked to additional specs and work items.
- PASS when `search_deliberations()` returns a fresh SQLite row via `search_method="text_match"` with stable result-contract fields when ChromaDB is unavailable.
- PASS when deterministic Chroma stub coverage proves deleted stale chunks, versioned unique chunk IDs, redacted indexed documents, and required metadata.
- PASS when bridge-thread harvest coverage proves `SPEC-2098` and `WI-3216` identifiers are extracted and routed to a `bridge_thread` deliberation source.
- PASS when targeted pytest, adjacent pytest, ruff check, ruff format check, and diff whitespace checks pass.
- PASS when no production source, formal artifacts, project membership, new work items, credentials, release tags, deployment state, live ChromaDB persisted state, or Agent Red application behavior are changed.

## Risks / Rollback

Risk is low. This is additive test coverage over implemented platform behavior. The main implementation risk is brittle coupling to ChromaDB internals; the proposal avoids that by using a small stub collection and asserting the `KnowledgeDB` contract at the Python boundary rather than requiring a live ChromaDB store.

Rollback is to delete `platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `platform_tests/scripts/test_deliberation_archive_spec2098_coverage.py`

## Recommended Commit Type

`test:`
