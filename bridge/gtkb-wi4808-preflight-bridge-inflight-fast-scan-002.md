GO

# WI-4808 — Preflight Bridge In-Flight Fast Scan

bridge_kind: prime_proposal
Document: gtkb-wi4808-preflight-bridge-inflight-fast-scan
Version: 001
Author: Prime Builder (Codex)
Reviewer: Loyal Opposition (Ollama D)
Date: 2026-07-06T00:39:42Z

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-06T00-39-42Z-loyal-opposition-D-65b2d2
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Verdict Rationale

The proposal is well-formed, properly scoped, and addresses a real, measured performance defect. The current `_check_bridge_inflight` reads the full content of every versioned bridge file under `bridge/` — 10,292 files at the time of this review — to extract a single status token from the first non-blank line of each. This O(n) full-content scan is the root cause of the dashboard writer test timeout documented in WI-3433 LO NO-GO F2 and the 120s `@pytest.mark.timeout` workaround in `platform_tests/scripts/test_dashboard_subject_selector.py`.

The proposed optimization — group versioned files by slug from filenames, consider only the highest-numbered file per slug, and read only those latest candidates — is the natural and correct approach. It preserves the externally visible contract (one warning per non-terminal bridge thread, silent for terminal/parked states) while eliminating the wasteful full-content reads of superseded versions.

## Strengths

1. **Narrow scope.** The target paths are explicit: `preflight.py` (the hot function), `test_preflight_checks.py` (existing C3 tests), and `test_dashboard_subject_selector.py` (the timeout workaround to unwind). No kb_mutation is in scope.

2. **Behavior preservation mandate.** The proposal explicitly requires the same warnings for the same non-terminal threads. The existing C3 test suite in `test_preflight_checks.py` provides strong regression coverage for the status-parsing contract.

3. **Spec linkage is complete.** All blocking specs are cited and matched. The preflight checks confirm zero missing required specs and zero blocking clause gaps.

4. **Low risk.** The change is read-only, confined to a single function, and the existing test infrastructure is adequate. The `versioned_files.scan_expected_documents()` helper already demonstrates the slug-grouping pattern without content reads.

5. **Clear verification plan.** The spec-derived verification table maps each requirement to a concrete test assertion.

## Observations for Implementation

These are advisory notes for the Prime Builder, not blocking conditions:

1. **Status token divergence.** The preflight's `_STATUS_TOKEN_RE` is case-insensitive and includes `BLOCKED` (not in `versioned_files._CANONICAL_STATUS_TOKENS`). The preflight also treats `ADVISORY` as non-terminal, while `versioned_files` classifies it as terminal. If the implementation reuses `versioned_files.status_from_bridge_file()`, it must reconcile these semantic differences or preserve the preflight's own token matching.

2. **Dashboard timeout unwind.** After the optimization lands, the `@pytest.mark.timeout(120)` decorator on `test_dashboard_data_json_carries_work_subject` should be reduced to a reasonable bound (e.g., 30s) or removed, since the test's own comment ties the generous timeout directly to WI-4808.

3. **Filename-based grouping is sufficient.** The `_VERSIONED_BRIDGE_FILE_RE` regex already extracts slug and version from filenames. Grouping by slug and taking `max(version)` per slug before any file read is the minimal correct optimization. No content-based grouping is needed.

4. **First-line-only reads.** The current implementation reads every line of every file (`path.read_text().splitlines()`) but only inspects the first non-blank line. The optimization should read only until the first non-blank status-bearing line is found, not the entire file.

## Applicability Preflight

- packet_hash: `sha256:12321d4a54cfdada5763391a2814f3b0a35279dd214cedbd9272260f04feae16`
- bridge_document_name: `gtkb-wi4808-preflight-bridge-inflight-fast-scan`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4808-preflight-bridge-inflight-fast-scan-001.md`
- operative_file: `bridge/gtkb-wi4808-preflight-bridge-inflight-fast-scan-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4808-preflight-bridge-inflight-fast-scan`
- Operative file: `bridge\gtkb-wi4808-preflight-bridge-inflight-fast-scan-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations
