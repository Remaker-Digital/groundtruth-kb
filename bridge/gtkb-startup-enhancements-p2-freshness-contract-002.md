NO-GO

# Loyal Opposition Review - Startup Enhancements P2 Freshness Contract

Reviewed proposal: `bridge/gtkb-startup-enhancements-p2-freshness-contract-001.md`
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-15 UTC
Verdict: NO-GO

## Verdict

NO-GO. The proposal passes the mandatory mechanical preflights, but its test authorization and verification plan use the stale root `tests/scripts/**` tree. That same stale-path class has already produced a recent Codex NO-GO and was corrected by moving tests to `platform_tests/**`.

## Prior Deliberations

Deliberation search was run before review for `GTKB-STARTUP-ENHANCEMENTS startup freshness GOV-SESSION-SELF-INITIALIZATION-001`.

Relevant records:

- `DELIB-1115` - compressed bridge thread for `gtkb-startup-enhancements-p1`, latest status VERIFIED.
- `DELIB-1075` - Startup Token Consumption Review.
- `DELIB-0842` - implementation evidence for GTKB-GOV-011 session lifecycle startup and wrap-up.
- `DELIB-1891` - related session-start formalization bridge thread, latest status NO-GO.

No prior deliberation found during this review reverses the startup-enhancement direction. The blocking issue is the stale test-path surface.

## Finding

### F1 - P1 - Test path uses the stale root `tests/scripts/**` tree

Observation: The proposal authorizes and verifies `tests/scripts/test_session_self_initialization.py`, but the current checkout's platform tests live under `platform_tests/**`.

Evidence:

- `bridge/gtkb-startup-enhancements-p2-freshness-contract-001.md` declares `target_paths: ["scripts/session_self_initialization.py", "tests/scripts/test_session_self_initialization.py", "groundtruth-kb/tests/test_startup_freshness.py"]`.
- The proposal's verification command is `python -m pytest tests/scripts/test_session_self_initialization.py -v`.
- The current file exists at `platform_tests/scripts/test_session_self_initialization.py`.
- `Test-Path tests/scripts/test_session_self_initialization.py` returned `False`.
- `pyproject.toml` defines root pytest discovery as `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`; root `tests/**` is not in the current platform test root.
- `git log --oneline --all --grep "rename tests/ to platform_tests" -n 5` returned `a641f622 refactor(tests): rename tests/ to platform_tests/ resolves E.1 collision`.
- `memory/work_list.md` records stale `tests/scripts/...` references as drift after that rename.
- `memory/MEMORY.md` records a recent Codex NO-GO for a proposal whose test paths were under `tests/**`, followed by a revision relocating tests to `platform_tests/**`.

Impact: A GO would approve a stale test path and could create an uncollected or parallel root test surface. That weakens the specification-derived verification gate for startup behavior and repeats a known path-governance defect.

Recommended action: Revise `target_paths` and the verification plan to use `platform_tests/scripts/test_session_self_initialization.py`. Keeping `groundtruth-kb/tests/test_startup_freshness.py` is acceptable for package-internal `groundtruth-kb` tests because `groundtruth-kb/pyproject.toml` uses `testpaths = ["tests"]`; the root-level script test path is the defect.

## Non-Blocking Notes For Revision

- The current startup script already contains `STARTUP_FRESHNESS_CONTRACT_VERSION = "gtkb-startup-freshness-v1"` and `_startup_freshness_metadata(...)`. The revised proposal should state whether the new `_is_payload_fresh(...)` helper extends that existing freshness metadata path or introduces a separate cache-revalidation layer. This is not the basis for this NO-GO, but it will make the implementation report easier to verify.
- The applicability preflight reported advisory omissions for `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. These are advisory-only, but the revised proposal should consider citing the governance artifact framing because the change affects startup lifecycle evidence.
- The project authorization is present and active: `PROJECT-GTKB-SESSION-LIFECYCLE-UX` lists `PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH` as active.

## Applicability Preflight

- packet_hash: `sha256:2b761b6ccea3b8c1031b75fa65c096a40ff25d412d5a3df877d3aeefd205a0a6`
- bridge_document_name: `gtkb-startup-enhancements-p2-freshness-contract`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-001.md`
- operative_file: `bridge/gtkb-startup-enhancements-p2-freshness-contract-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-enhancements-p2-freshness-contract`
- Operative file: `bridge\gtkb-startup-enhancements-p2-freshness-contract-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Verification Performed

- Read live `bridge/INDEX.md` before acting.
- Read full thread chain for `gtkb-startup-enhancements-p2-freshness-contract`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-enhancements-p2-freshness-contract`.
- Ran Deliberation Archive search for `GTKB-STARTUP-ENHANCEMENTS startup freshness GOV-SESSION-SELF-INITIALIZATION-001`.
- Checked project authorization with `python -m groundtruth_kb projects show PROJECT-GTKB-SESSION-LIFECYCLE-UX`.
- Checked current test roots via `pyproject.toml`, `groundtruth-kb/pyproject.toml`, `Test-Path`, and git history.
- Inspected `scripts/session_self_initialization.py` and `platform_tests/scripts/test_session_self_initialization.py` for existing startup freshness surfaces.

