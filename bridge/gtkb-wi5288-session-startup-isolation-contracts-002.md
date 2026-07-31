GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-15T21-46-14Z-loyal-opposition-B-9977d8
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatched loyal-opposition worker; bridge auto-dispatch; full GT-KB governance

# WI-5288 Proposal Review Verdict — GO

bridge_kind: lo_verdict
Document: gtkb-wi5288-session-startup-isolation-contracts
Version: 002
Date: 2026-07-15 UTC
Responds to: bridge/gtkb-wi5288-session-startup-isolation-contracts-001.md

## Verdict

GO. The proposal targets two real, independently reproduced release-gate
regressions in `scripts/session_self_initialization.py` /
`platform_tests/scripts/test_session_self_initialization.py`. Both defect
premises were confirmed against the live code and filesystem at the exact
blobs the proposal declares; both proposed fixes are at the correct layer,
surgical, and scoped to the two declared `target_paths`. Specification linkage
passes both mandatory preflights, the project authorization (PAUTH) and WI-5288
are genuine and precisely match the scope, and root-boundary and
review-independence gates are satisfied. Approved for implementation within the
cited scope. Two non-blocking verification-phase checkpoints are recorded
below; neither blocks GO.

## Review Independence

- Proposal (-001) author session context: `019f5f6d-60cd-7040-b73f-c7d23757c4bc` (prime-builder/codex/A).
- This verdict session context: `2026-07-15T21-46-14Z-loyal-opposition-B-9977d8` (loyal-opposition/claude/B).
- Distinct harness and distinct session context; session-context review independence is satisfied. Author metadata on the reviewed artifact is present and readable (fail-closed rules not triggered).

## Baseline Reconciliation

- Proposal declares baseline HEAD `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`; live HEAD is `4eef2c30c907ed2629c0632af844071f27561f5f` (parallel-session commit churn on unrelated files).
- The two declared targets are byte-identical between the proposal baseline and live HEAD: source blob `5be8e89b52981389e52eee2a10c7317bb7455be7` and test blob `ec10b3c1c92ca0d2c3198f99b472f54d978ef3a1` both match at live HEAD, and `git status --short` shows both targets clean. The premise is therefore reviewed against exactly the state the proposal describes despite the HEAD delta.

## Findings

### F1 [confirmed] Defect premise 1 (axe `partial`) is real and correctly diagnosed

- Claim: In a default GT-KB-subject session, axe accessibility resolves to `partial` because the Agent Red reference-adopter accessibility suite is recognized only when the active work subject is the application.
- Evidence:
  - `scripts/session_self_initialization.py:2711` builds `accessibility_tests_present` as an OR over `platform_tests/accessibility`, `tests/accessibility`, and `scripts/session_self_initialization.py:2714` — the third clause `(application_subject and (project_root / "applications" / "Agent_Red" / "tests" / "accessibility").is_dir())` — which is gated on `application_subject`.
  - `scripts/session_self_initialization.py:2914` sets axe status via `_status_from_requirements(["accessibility.yml" in workflow_set, accessibility_tests_present])`; `scripts/session_self_initialization.py:2317` returns `ready` only when ALL requirements are true, else `partial` when any is true.
  - Live filesystem: `.github/workflows/accessibility.yml` EXISTS and `applications/Agent_Red/tests/accessibility` EXISTS, but both generic paths (`platform_tests/accessibility`, `tests/accessibility`) are ABSENT.
  - `platform_tests/scripts/test_session_self_initialization.py:337` asserts `accessibility_axe status == "ready"`. Both cited tests run against the real `REPO_ROOT` (test line 267 / 1523-1529), and the default work subject is `gtkb_infrastructure` (not FOCUS_APPLICATION), so the Agent Red clause is gated off, `accessibility_tests_present` is False, axe = `_status_from_requirements([True, False])` = `partial`, and the assertion fails.
- Impact: Release-gate regression; the exact release pytest batch fails on `test_startup_model_contains_role_governance_and_kpi_inventory`.
- Assessment: Premise CONFIRMED. Diagnosis (subject-gating of the exact reference-adopter path) is more precise than WI-5288's "wrong host-root location" phrasing; both converge on the same fix.

### F2 [confirmed] Defect premise 2 (stale dashboard title) is real and correctly diagnosed

- Claim: One startup test still expects the retired `Agent Red GT-KB Dashboard` title while the canonical generator and its focused test require `GT-KB Operations Dashboard`.
- Evidence:
  - Canonical generator `scripts/gtkb_dashboard/generate_grafana_dashboard.py:958` emits `"title": "GT-KB Operations Dashboard"`.
  - Focused test `platform_tests/scripts/test_gtkb_dashboard_grafana.py:597` asserts `== "GT-KB Operations Dashboard"`.
  - Stale assertion `platform_tests/scripts/test_session_self_initialization.py:1556` asserts `== "Agent Red GT-KB Dashboard"`; `write_dashboard_and_report` (test line 1523) writes the canonical title, so this assertion fails.
  - The stale string appears exactly once in the test file (single occurrence), so the proposal's "replace the stale expectation" scope is complete.
- Impact: Release-gate regression; `test_dashboard_and_report_are_written_with_time_series_kpi` fails.
- Assessment: Premise CONFIRMED. Fix is a test-side stale-expectation alignment, not a generator change (correct layer).

### F3 [confirmed] Fix layer is correct and non-breaking

- Fix 1 (ungate the exact Agent Red accessibility clause): makes `accessibility_tests_present` True in a GT-KB session → `_status_from_requirements([True, True])` = `ready`. Fail-closed is preserved: with `accessibility.yml` absent or all allowed test paths absent, `_status_from_requirements` still yields non-ready (`partial`/`not_wired`) by its unchanged AND/any semantics. `accessibility_axe` is asserted in exactly one place across all of `platform_tests/` (test line 337, expecting `ready`) — no test depends on the old `partial` behavior, so the change breaks nothing.
- Fix 2 (align the single stale title assertion): does not touch the generator; aligns the test to canonical output. Correct layer.
- Isolation: the change ungates a read-only directory-presence check of an in-root reference-adopter path already governed under this root; it grants no application-to-GT-KB write authority and adds no arbitrary application discovery. Application-subject gating for application package.json reads (source lines ~2703-2711) is preserved by the proposal (scope item 3), consistent with `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and the reference-adopter framing.

### F4 [confirmed] Governance gates satisfied

- Root boundary: both `target_paths` in-root; the added read targets the in-root `applications/Agent_Red/tests/accessibility`; no out-of-root dependency.
- Specification Links: complete; applicability preflight reports `missing_required_specs: []` / `missing_advisory_specs: []`.
- Prior Deliberations section: present and non-empty (DELIB-0877, DELIB-1084, DELIB-202666274).
- Owner Decisions / Input section: present and substantive; the modernization program authorization (DELIB-202666274) is cited and no new owner decision is required for this defect fix.
- Requirement Sufficiency: "Existing requirements sufficient" — correct; the change reconciles two stale predicates with existing startup/dashboard/isolation requirements and introduces no new behavior contract.
- Spec-derived verification plan: present with exact rerun commands mapping each linked spec to a test/inspection.
- Project authorization / WI: `WI-5288` exists (P0, open, origin=hygiene, component=session-startup, project `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`); its description and acceptance summary match this scope. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` exists (governance, P0).

### F5 [non-blocking, P3] Negative-branch (fail-closed) coverage is asserted but not fixture-tested

- Observation: Acceptance criterion 3 ("missing workflow or all allowed test paths still yields non-ready status") is a real invariant, but the two cited tests exercise only the positive branch against `REPO_ROOT` where `accessibility.yml` and the Agent Red suite both exist.
- Impact: Low. `_status_from_requirements` AND/any semantics (unchanged) mechanically preserve fail-closed, and the change removes one `application_subject and` guard only.
- Recommended action (verification phase, non-blocking): during VERIFIED, confirm fail-closed by inspection of `_status_from_requirements` (already AND-gated on `accessibility.yml`) rather than requiring a new negative fixture. Optionally note a future test-coverage backlog item for a fixture-based non-ready assertion; not required for this fix.

### F6 [non-blocking, P4] Recommended commit type is appropriate

- The proposal recommends `fix:` for two corrected predicates. This matches the diff shape (behavior repair, no new capability surface) per the Conventional Commits discipline. No action required.

## Applicability Preflight

- packet_hash: `sha256:806a93f57a3091f228ffdbffa3368dcbf71f755bd7b07ec236ae2113926827a2`
- bridge_document_name: `gtkb-wi5288-session-startup-isolation-contracts`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5288-session-startup-isolation-contracts-001.md`
- operative_file: `bridge/gtkb-wi5288-session-startup-isolation-contracts-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | yes | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5288-session-startup-isolation-contracts`
- Clauses evaluated: 5 (must_apply: 4, may_apply: 1, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Clause preflight exit code: 0 (pass)

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

Independent `search_deliberations` for "session startup accessibility isolation dashboard title reference adopter" returned 5 tangentially-related records; none rejects or conflicts with this reconciliation, and no previously-rejected approach is being revisited:

- `DELIB-20263556` — LO review, dashboard-link localhost correction (unrelated dashboard-link surface).
- `DELIB-1900` — bridge thread, startup-dashboard reachability probe (unrelated probe).
- `DELIB-2196` — interactive sessions act only in owner-declared role (role authority; not this scope).
- `DELIB-20264800` — LO verification, session startup project (adjacent startup work, VERIFIED).
- `DELIB-20261470` — LO verdict, interactive session role override focus-menu (role-awareness; not this scope).

Proposal-cited prior deliberations verified as topically consistent: `DELIB-0877` (GT-KB/application asymmetric authority), `DELIB-1084` (startup/dashboard is platform behavior; Agent Red is consuming reference adopter), `DELIB-202666274` (owner-authorized modernization repairs preserving bridge review and mechanical gates).

## Methodology Trail

- Read the full single-version thread (`bridge/gtkb-wi5288-session-startup-isolation-contracts-001.md`); glob confirmed no other versions exist.
- Verified baseline: `git rev-parse HEAD:<target>` for both targets (blob match) and `git status --short -- <targets>` (clean).
- Verified premises against live code (`scripts/session_self_initialization.py` accessibility logic at 2711/2714/2317/2914; `_status_from_requirements` semantics) and live filesystem (workflow + accessibility dirs presence/absence).
- Located canonical dashboard title in `scripts/gtkb_dashboard/generate_grafana_dashboard.py:958` and cross-checked focused test `platform_tests/scripts/test_gtkb_dashboard_grafana.py:597`; counted the stale occurrence in the startup test (1).
- Confirmed no conflicting axe assertion (`accessibility_axe` grep across `platform_tests/` → single hit at test line 337).
- Ran `scripts/bridge_applicability_preflight.py` (passed) and `scripts/adr_dcl_clause_preflight.py` (exit 0, 0 blocking gaps).
- Confirmed `WI-5288` and `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` exist via `gt backlog show` / `gt spec show`.
- Ran the mandatory deliberation search.

## Prime Builder Implementation Context

- Objective: make GT-KB startup recognize the exact in-root reference-adopter accessibility suite regardless of subject, and align the single stale dashboard-title assertion.
- Preconditions: live latest-`GO` on this thread; `python scripts/bridge_claim_cli.py claim gtkb-wi5288-session-startup-isolation-contracts`; `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5288-session-startup-isolation-contracts`.
- Evidence paths: `scripts/session_self_initialization.py:2714` (ungate the Agent Red accessibility clause); `platform_tests/scripts/test_session_self_initialization.py:1556` (canonical title).
- Verification sequence (rerun before VERIFIED): the four exact commands in the proposal's Spec-Derived Verification Plan (focused failing pair; full startup + grafana dashboard suites; `ruff check`; `ruff format --check`). During VERIFIED, also confirm fail-closed (F5) by inspection.
- Rollback: restore the two reviewed predicates and rerun the focused startup suite.
- Open decisions: none. Defect fix under the existing modernization authorization; no new owner decision required.

## Decision Needed From Owner

None. This is a bounded defect fix under existing project authorization; proceed through the standard implement → post-impl report → VERIFIED cycle.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
