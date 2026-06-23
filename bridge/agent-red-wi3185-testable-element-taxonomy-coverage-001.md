NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex Desktop interactive Prime Builder session override; application mode

# Implementation Proposal - WI-3185 Testable Element Dimension Taxonomy Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3185-testable-element-taxonomy-coverage
Version: 001
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3185

target_paths: ["applications/Agent_Red/tests/quality/test_data_normalization.py"]

## Claim

Add deterministic repository-native pytest coverage for `SPEC-1653` by exercising the Agent Red application-facing KnowledgeDB shim for the testable-element taxonomy. The implementation is limited to a test addition in `applications/Agent_Red/tests/quality/test_data_normalization.py`.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirement is already recorded as `SPEC-1653` and the project authorization is already recorded as `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`. No new or revised GOV/SPEC/ADR/DCL/PB/REQ artifact is required for this WI.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `applications/Agent_Red/tests/quality/test_data_normalization.py`.

## Bridge File Chain Evidence

This proposal will be filed as append-only numbered bridge artifact `bridge/agent-red-wi3185-testable-element-taxonomy-coverage-001.md` through the governed bridge-propose helper. No prior bridge version will be deleted, rewritten, or replaced.

## Specification Links

- `SPEC-1653` - Governs the A-N testable-element dimension taxonomy and requires elements to carry applicable dimension categories.
- `GOV-10` - Requires Test artifacts to exercise exposed/live behavior instead of relying on source inspection or assertion-only evidence; this proposal uses the live KnowledgeDB API surface through Agent Red's shim and a temporary database.
- `SPEC-1649` - Restates GOV-10 for the master testing context; relevant because WI-3185 was opened after assertion-only evidence for a behavioral requirement was rejected.
- `GOV-12` - Work-item remediation must create test evidence; this proposal adds a repository-native pytest mapping for WI-3185/SPEC-1653.
- `GOV-13` - Requires test evidence to be visible to the test-plan hierarchy; current FAB-11 amendments allow repository-native pytest coverage mappings as live spec-to-test visibility.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Defines project-scoped authorization as owner-approval evidence that does not replace bridge GO, target-path scoping, impl-start packets, reports, or LO verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies the code-quality baseline to this test-only change.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs bridge status authority and Prime/Loyal Opposition role boundaries for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires concrete specification links and complete target-path metadata in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires `Project Authorization`, `Project`, and `Work Item` metadata lines for implementation-targeting proposals.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application files live under `applications/Agent_Red/` inside the GT-KB root.
- `GOV-STANDING-BACKLOG-001` - Keeps this work tied to the MemBase work item/project authority rather than ad hoc task state.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Requires explicit fallback discipline when Codex hook behavior differs; proposal filing uses the Codex non-bypass helper path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires project-relevant plans and decisions crossing the threshold to be preserved in governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this proposal and later implementation report as lifecycle artifacts for the work item.

## Prior Deliberations

- `DELIB-0712` - POR Step 16.B methodology review classified assertion-only and phantom-only evidence patterns and recommended stream-based remediation.
- `DELIB-0713` - Owner rejected assertion-only verification for regular behavioral requirements and directed those specs to be treated as untested.
- `DELIB-20265586` - Owner authorized snapshot-bound project implementation for the 40 well-formed project buckets, including this project's open WI set.
- `DELIB-20263117` - TAFE Phase 0 GO confirmed that test creation can be deferred to the specific implementation proposal when no valid current production-interface test exists yet.
- `DELIB-20263468` - Loyal Opposition advisory emphasized repository-native pytest evidence as the live verification surface for bridge-linked tests.

## Owner Decisions / Input

- `DELIB-20265586` - Owner decision authorizing the mass project implementation sweep with snapshot-bound scope.
- `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23` - Active project authorization for this project's 38 current open member WIs, including `WI-3185`; allowed mutation class used here is `test_addition`.

## Proposed Scope

1. Add a focused pytest class in `applications/Agent_Red/tests/quality/test_data_normalization.py`.
2. Define the canonical `SPEC-1653` dimension-code list from A1 through N3 inside the test module as test data.
3. Use the Agent Red compatibility shim (`tools/knowledge-db/db.py`) to create a temporary `KnowledgeDB` database under pytest's `tmp_path`.
4. Insert a testable element linked to `SPEC-1653` with the complete canonical dimension list.
5. Assert the API returns the dimension list through `applicable_dimensions_parsed`, preserves the raw JSON storage field, supports filtered listing, and reports active/total coverage counts through `get_element_coverage_summary()`.
6. Do not mutate live `groundtruth.db`, formal artifacts, source modules, hooks, configuration, or project membership.

## Specification-Derived Verification Plan

| Linked spec | Verification |
|---|---|
| `SPEC-1653` | `python -m pytest applications/Agent_Red/tests/quality/test_data_normalization.py -q --tb=short` must include a test that persists and reads back every canonical A-N dimension code through the KnowledgeDB testable-element API. |
| `GOV-10`, `SPEC-1649` | The same pytest must exercise the real KnowledgeDB API with a temporary SQLite database, not source text inspection or a mocked API. |
| `GOV-12`, `GOV-13`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must map `WI-3185` and `SPEC-1653` to the executed pytest command and observed result. |
| Bridge/project governance specs | Pre-filing bridge compliance, implementation-start authorization, scoped diff review, and post-implementation LO verification must remain in force. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `python -m ruff check applications/Agent_Red/tests/quality/test_data_normalization.py` and `python -m ruff format --check applications/Agent_Red/tests/quality/test_data_normalization.py` after implementation. |

## Acceptance Criteria

- A deterministic pytest exists for `SPEC-1653` in `applications/Agent_Red/tests/quality/test_data_normalization.py`.
- The test covers the full canonical dimension-code set from A1 through N3.
- The test uses a temporary database and the Agent Red KnowledgeDB shim rather than mutating live `groundtruth.db`.
- The targeted pytest command passes.
- Ruff lint and format checks pass for the touched test file.
- No source, hook, config, formal artifact, project-membership, or live DB mutation occurs under this bridge thread.

## Code Quality Baseline

| Rule | Applicability |
|---|---|
| `CQ-SECRETS-001` | Applies; no credentials or tenant-specific values will be introduced. |
| `CQ-PATHS-001` | Applies; the test will use pytest `tmp_path` and repository-relative imports already used by the test suite. |
| `CQ-CONSTANTS-001` | Applies; the dimension-code list is domain-stable test data derived from `SPEC-1653`. |
| `CQ-DOCS-001` | Applies lightly; test names/docstrings should explain the SPEC-1653 behavior under test. |
| `CQ-COMPLEXITY-001` | Applies; the change is a small test addition. |
| `CQ-TESTS-001` | Applies and is the purpose of the WI. |
| `CQ-LOGGING-001` | Not applicable; no logging changes. |
| `CQ-SECURITY-001` | Not applicable beyond confirming no auth/input/secrets surface changes. |
| `CQ-VERIFICATION-001` | Applies; verification is automated pytest plus ruff lint/format. |
| `CQ-PERF-001` | Not applicable; tiny temporary DB fixture, no hot-path code. |
| `CQ-DEPS-001` | Not applicable; no dependency changes. |

## Risks / Rollback

- Risk: the existing Agent Red quality tests may assume root-relative execution. Mitigation: run the targeted pytest from `E:\GT-KB` as the current repo-native pattern already does.
- Risk: the test could accidentally bind to the live `groundtruth.db`. Mitigation: instantiate `KnowledgeDB(tmp_path / "taxonomy.db")` explicitly and close it in the test.
- Rollback: remove the added test block from `applications/Agent_Red/tests/quality/test_data_normalization.py`.

## Files Expected To Change

- `applications/Agent_Red/tests/quality/test_data_normalization.py`

## Recommended Commit Type

`test`

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
