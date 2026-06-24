NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: harness-state registry plus current Codex runtime

# Implementation Proposal - WI-3194 Knowledge Retrieval Technical Detail Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3194-knowledge-retrieval-technical-detail
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3194

target_paths: ["applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py"]

## Claim

WI-3194 can be implemented as a narrow test-only backfill for `SPEC-1742`.

The current Agent Red docs source at `applications/Agent_Red/docs-site/docs/getting-started/how-it-works.md` already contains a "Knowledge retrieval technical detail" section that covers the required retrieval model, indexing, hybrid search, parameters, writing guidance, caching, and fallback chain. MemBase currently shows `SPEC-1742` as `retired` because FAB-11 retired stale assertion history after Agent Red isolation moved the referenced docs under `applications/Agent_Red/`; the open WI remains the active project work item for replacing assertion-only evidence with deterministic tests.

This proposal authorizes only:

- add `applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py`;
- parse the authoritative Docusaurus markdown source; and
- assert the SPEC-1742 technical-detail clauses are present as executable docs-source evidence.

This proposal does not authorize runtime code, docs-source edits, generated static HTML, credentials, deployment state, formal GT-KB artifact mutation, project membership changes, or new work items. If the new test unexpectedly reveals a docs-source gap, Prime Builder should stop and return through the bridge with a revised proposal rather than silently broadening the target paths.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1742` and `WI-3194` together state the testable target: the How It Works page must include detailed technical coverage for the embedding model (`text-embedding-3-large`, 3072 dimensions, cosine, DiskANN), article preparation, hybrid search with RRF (`70%` vector and `30%` BM25), retrieval parameters, practical KB writing guidance, caching, and fallback chain. `WI-3194` explicitly exists because the previous assertion-only evidence was insufficient per `DELIB-0712` and `DELIB-0713`. No owner clarification is needed to add deterministic tests for those clauses.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_how_it_works_spec1742.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\docs-site\docs\getting-started\how-it-works.md`

## Specification Links

- `SPEC-1742` - Direct target documentation requirement for knowledge retrieval technical detail in the How It Works page.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live docs source is the exposed artifact under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate the documentation artifact rather than rely on manual inspection or stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies the baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the governed bridge helper path and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside the snapshot-bound project member `WI-3194`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - Methodology review classifying the source evidence gap.
- `DELIB-0713` - Owner decision that assertion-only verification is insufficient for behavioral requirements.
- _No WI-specific prior bridge deliberation: `gt bridge threads --wi WI-3194 --json` returned `match_count: 0` before this NEW proposal._

## Proposed Scope

1. Add `applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py`.
2. In the new pytest, parse `applications/Agent_Red/docs-site/docs/getting-started/how-it-works.md` and isolate the `### Knowledge retrieval technical detail` section before the next level-three heading.
3. Assert the section covers the SPEC-1742 technical clauses:
   - embedding model `text-embedding-3-large`;
   - 3,072 vector dimensions;
   - cosine distance;
   - Cosmos DB DiskANN;
   - article preparation inputs: entry type, title, tags, content;
   - single-embedding-per-article behavior and content hash change detection;
   - hybrid search with vector and BM25 branches feeding Reciprocal Rank Fusion;
   - 70% vector and 30% BM25 weighting;
   - top-k, maximum result, candidate-pool, relevance-score, context-budget, BM25 k1, and BM25 b retrieval parameters;
   - practical KB writing guidance for titles, customer terms, focused articles, and tags;
   - exact query, semantic, and embedding caches; and
   - fallback chain from hybrid to vector-only to BM25-only to empty result.
4. Keep implementation test-only unless the test exposes a current docs-source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Pre-Filing Preflight Evidence

Applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3194-knowledge-retrieval-technical-detail-001.md --json
```

Observed:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:2e237a05aafd62079cae7745cf2021c2e9ef845a5f4729e9021ea400ad07c7fb`
- warning only: parser harvested bare `tests/multi_tenant/test_how_it_works_spec1742.py` strings from command text; declared target paths remain in-root under `applications/Agent_Red/`.

Clause preflight:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3194-knowledge-retrieval-technical-detail-001.md
```

Observed:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1742` | New pytest parses the How It Works markdown and asserts every required knowledge-retrieval technical detail is present in the dedicated section. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic docs-source test file. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3194-knowledge-retrieval-technical-detail`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py
```

## Acceptance Criteria

- PASS when a new pytest verifies the How It Works page has a `Knowledge retrieval technical detail` section.
- PASS when the test covers embedding model, dimensions, cosine, DiskANN, and article preparation details.
- PASS when the test covers hybrid vector/BM25 search with RRF and 70%/30% weighting.
- PASS when the test covers retrieval parameters, KB writing guidance, caching layers, and fallback chain.
- PASS when the targeted pytest and ruff commands all pass.
- PASS when no runtime code, docs-source edits, generated static HTML, credentials, deployment state, formal artifacts, project membership, or new WIs are changed.

## Risks / Rollback

Risk is low. The proposal adds one source-level documentation regression test and does not alter runtime behavior. The main risk is brittleness if the docs section is reorganized without changing the requirement; keeping the assertions section-scoped and concept-based should minimize that risk.

Rollback is to delete `applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/multi_tenant/test_how_it_works_spec1742.py`

## Recommended Commit Type

`test:`
