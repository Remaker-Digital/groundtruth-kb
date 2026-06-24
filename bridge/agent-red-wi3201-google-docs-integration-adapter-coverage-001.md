NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3201 Google Docs Integration Adapter Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3201-google-docs-integration-adapter-coverage
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3201

target_paths: ["applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py"]

## Claim

WI-3201 should be implemented as a narrow test-only backfill for `SPEC-1777`.

Current Agent Red source already contains a Google Docs / Drive knowledge adapter under `applications/Agent_Red/src/integrations/google_docs/`, a shared ingestion pipeline under `applications/Agent_Red/src/integrations/knowledge_ingestion.py`, and an existing general-purpose `test_google_docs_adapter.py`. The open work item exists because prior assertion-only coverage was rejected under `DELIB-0712` and `DELIB-0713`; this proposal adds deterministic, spec-mapped coverage with explicit `SPEC-1777` clause assertions without changing runtime code.

This proposal does not authorize source edits, existing-test rewrites, generated artifacts, deployment state, release tagging, formal GT-KB artifact mutation, project membership changes, credentials, or new work items. If the new test exposes a current source gap, Prime Builder should stop and return through the bridge with a revised source-plus-test proposal rather than broadening target paths under this NEW proposal.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1777` directly states the target Google Docs / Drive knowledge source behavior: OAuth2 auth; Drive readonly and Documents readonly scope coverage; source-articles capability for Docs, Sheets, PDF, TXT, MD, and CSV; folder selection; Google Doc HTML export; Google Sheets CSV export; normalization, chunking, embedding, content-hash tracking, unchanged-content skip behavior, Drive `changes.list` incremental sync, one-hour default polling, daily full sweep, and Connect -> OAuth -> folder selection -> initial sync -> periodic setup flow.

`SPEC-1770` supplies the shared ingestion-pipeline contract for the `normalize -> chunk -> hash -> embed -> store` stages referenced by `SPEC-1777`. The work item asks for deterministic test evidence for an existing requirement; no owner clarification is needed to add a mapped regression test.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_google_docs_spec1777.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\integrations\google_docs\adapter.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\google_docs\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\knowledge_ingestion.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\manifest.py`
- `E:\GT-KB\applications\Agent_Red\src\integrations\models.py`
- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_google_docs_adapter.py`

## Specification Links

- `SPEC-1777` - Direct historical requirement text and source spec for the Google Docs / Drive knowledge source adapter.
- `SPEC-1770` - Shared multi-source knowledge ingestion pipeline requirement covering normalization, chunking, hashing, embedding, storage metadata, and unchanged-content skip behavior referenced by `SPEC-1777`.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live Google Docs adapter, manifest, and ingestion pipeline surfaces are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than rely on manual inspection or stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3201`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `gt bridge threads --wi WI-3201 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.
- `gt deliberations search "WI-3201 SPEC Google Docs Integration Knowledge Source Adapter"` returned broad bridge/governance records (`DELIB-20265851`, `DELIB-20265307`, `DELIB-20265446`, `DELIB-20265445`, `DELIB-2296`) but no WI-3201-specific blocking prior decision.

## Current-State Evidence

- MemBase `SPEC-1777` title: "Google Docs Integration - Knowledge Source Adapter".
- MemBase `SPEC-1777` description requires OAuth2; Drive readonly and Documents readonly scope coverage; `source.articles` capability for Docs, Sheets, PDF, TXT, MD, and CSV; folder selection; Google Doc HTML export; normalization, chunking, embedding, content-hash tracking, unchanged-content skip behavior; Drive `changes.list` incremental polling; default one-hour polling; daily full sweep; and Connect -> OAuth -> folder selection -> initial sync -> periodic setup.
- MemBase `SPEC-1770` description defines the shared ingestion pipeline stages: normalize, chunk, hash, embed, store, source metadata, and changed-content reprocessing behavior.
- `gt bridge threads --wi WI-3201 --json` currently returns `match_count: 0`.
- `applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py` does not currently exist.
- `applications/Agent_Red/src/integrations/google_docs/manifest.py` declares OAuth2, Google readonly scopes, knowledge category, source-articles capability, polling sync strategy, one-hour polling interval, professional tier gate, and available status.
- `applications/Agent_Red/src/integrations/google_docs/adapter.py` declares supported Docs / Sheets / PDF / TXT / MD / CSV MIME types, Google native export MIME mappings, one-hour default polling, daily full sync interval, Drive file listing, Drive `changes.list` incremental sync, content extraction, content hash tracking, normalized article mapping, search, folder sync, and health checks.
- `applications/Agent_Red/src/integrations/knowledge_ingestion.py` declares the content normalizer, chunker, content-hash-based ingest pipeline, source attribution metadata, and sync aggregation used to satisfy `SPEC-1777` ingestion clauses.
- `applications/Agent_Red/tests/integrations/test_google_docs_adapter.py` already covers many behaviors, but it is not a WI-3201/SPEC-1777 named mapping file and does not bind all SPEC-1777 clauses plus the shared ingestion-pipeline mapping into one deterministic coverage artifact.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3201-google-docs-integration-adapter-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3201-google-docs-integration-adapter-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py`.
2. In the new pytest, import live Google Docs manifest, adapter constants/helpers, adapter class, normalized article model, and shared knowledge ingestion pipeline surfaces where useful.
3. Assert manifest evidence for OAuth2, Google readonly scopes, knowledge category, source-articles capability, polling strategy, one-hour polling interval, tier gate, available status, and setup-relevant OAuth URLs/env names without storing any credential values.
4. Assert adapter constants and mappings for supported Docs, Sheets, PDF, TXT, MD, CSV file types; Google Doc HTML export; Google Sheets CSV export; one-hour default polling; and daily full sweep interval.
5. Assert folder listing and article listing use Drive folder selection, supported MIME filtering, normalized article fields, category-as-folder selection, and cursor pagination.
6. Assert full article retrieval uses Drive metadata plus export/download content extraction and records content hashes on normalized articles.
7. Assert sync behavior covers content-hash tracking, unchanged-content skip behavior, folder sync counts, Drive `changes.list` incremental start-token behavior, changed-file processing, and trashed/unsupported-file skipping.
8. Assert shared ingestion pipeline evidence for HTML normalization, CSV row normalization, chunking, source attribution metadata, embedding/storage call flow, and unchanged-content skip behavior for Google Docs sourced articles.
9. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1777` | New pytest imports live Google Docs adapter/manifest surfaces and asserts OAuth2/scopes, `source.articles`, supported file families, folder selection, HTML and CSV export mappings, normalized article behavior, Drive changes incremental sync, one-hour polling, daily full sweep, content hash tracking, unchanged-content skip behavior, and setup-relevant OAuth configuration. |
| `SPEC-1770` | New pytest imports live ingestion-pipeline surfaces and asserts normalization, chunking, hash-based skip behavior, embed/store call flow, and source attribution metadata for Google Docs sourced articles. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic Google Docs spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3201-google-docs-integration-adapter-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py
python -m ruff format --check applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py
```

## Acceptance Criteria

- PASS when the new pytest verifies OAuth2 auth and required Google readonly scope coverage.
- PASS when the new pytest verifies knowledge category, source-articles capability, polling strategy, one-hour default polling, and daily full-sweep constants.
- PASS when the new pytest verifies supported Docs, Sheets, PDF, TXT, MD, and CSV content families.
- PASS when the new pytest verifies Google Doc HTML export and Google Sheets CSV export mappings.
- PASS when the new pytest verifies folder selection, normalized article fields, cursor pagination, full article retrieval, and search behavior against mocked live adapter requests.
- PASS when the new pytest verifies content hash tracking and unchanged-content skip behavior.
- PASS when the new pytest verifies Drive `changes.list` incremental sync behavior.
- PASS when the new pytest verifies shared ingestion-pipeline normalization, chunking, embed/store flow, and source attribution metadata for Google Docs sourced articles.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low. The proposal adds one deterministic test module and does not alter runtime behavior. The main risk is that the test may reveal a real source gap in the historical Google Docs adapter or shared ingestion pipeline; if that happens, Prime Builder will stop and revise rather than widening this proposal.

Rollback is to delete `applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/integrations/test_google_docs_spec1777.py`

## Recommended Commit Type

`test:`
