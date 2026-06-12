NEW

# FAB-07 Post-Implementation Report: Doctor False-Signal Fixes

bridge_kind: implementation_report
Project Authorization: PAUTH-FAB07-20260610
Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4419
author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

## Summary

Implements all four verification-plan items from the FAB-07 proposal
(gtkb-fab-07-doctor-false-signals-001.md GO at -004):

| HYG ID | Fix | Status |
|--------|-----|--------|
| HYG-049 | DA-harvest coverage uses prefix matching (not exact `source_ref`) | Done |
| HYG-035 | Three narrative files cite `groundtruth-kb/examples/` (not "four demo applications"); `project-root-boundary.md` has the examples carve-out | Done |
| HYG-067 | AUQ-coverage excludes prose-pattern false positives (`detected_via` starting with `prose:`) | Done |
| HYG-068 | Isolation suite gates adopter-context checks when running against the platform dev repo | Done |

Authority: DELIB-FAB07-REMEDIATION-20260610.

## Specification Links

- GOV-18 / SPEC-1662: Assertion Quality Standard — meaningfulness over coverage
- GOV-STANDING-BACKLOG-001: Standing backlog governance contract
- GOV-FILE-BRIDGE-AUTHORITY-001: Live bridge index authority and permanent bridge repair authority
- ADR-ISOLATION-APPLICATION-PLACEMENT-001: Application isolation placement architecture decision
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001: Implementation proposals must cite all relevant specs
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: Verification requires spec-derived testing
- DELIB-FAB07-REMEDIATION-20260610: FAB-07 remediation authority

## Prior Deliberations

- DELIB-FAB07-REMEDIATION-20260610: Owner decision authorizing remediation of doctor false signals identified during PROJECT-FABLE-INVESTIGATION.

## Carried-Forward Proposal Evidence

Per GO at gtkb-fab-07-doctor-false-signals-004.md. All four verification items
from Codex GO's acceptance criteria are addressed.

## Owner Decisions / Input

Owner authorized auto-approve-inline for narrative/formal approval packets in
this session (2026-06-12), covering the four narrative-artifact approval packets
minted for FAB-07 protected-file edits.

## Files Changed

### Source changes

1. **groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py** (HYG-049)
   - Lines 108-116: Single `list_deliberations(source_type="bridge_thread")` fetch
     plus prefix matching (`prefix = f"bridge/{name}-"`; `any(str(d.get("source_ref", "")).startswith(prefix) for d in all_bridge)`).
   - Replaces prior exact `source_ref` match that missed per-file versioned refs.

2. **groundtruth-kb/src/groundtruth_kb/project/doctor.py** (HYG-067)
   - Lines 1455-1492: `_check_auq_coverage` now filters out `detected_via` entries
     starting with `"prose:"` before computing coverage. All-prose returns pass
     with `"(N prose-pattern false positives excluded)"`. Genuine-only fail path
     uses `len(genuine)` (not `len(in_window)`) for denominator accuracy.

3. **groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py** (HYG-068)
   - Lines 512-541: `run_isolation_checks()` detects platform-dev context via
     `(product_root / "groundtruth-kb").is_dir()`. When detected, adopter-specific
     checks (`adopter-root-placement`, `work-subject`,
     `hooks-point-to-wrappers`, `workstream-focus-hook-absent`,
     `release-readiness-app-subject-header`) return pass with
     `"Skipped: platform development repository"` message.

### Narrative edits (HYG-035)

4. **AGENTS.md** — Replaced "four small demo applications" with
   `groundtruth-kb/examples/` reference (+7 lines).
5. **.claude/rules/canonical-terminology.md** — Agent Red entry updated to cite
   `groundtruth-kb/examples/` as distinct from Agent Red (+41 lines).
6. **.claude/rules/acting-prime-builder.md** — Agent Red Reference Adopter
   section updated with `groundtruth-kb/examples/` distinction.

### Boundary edit (HYG-035)

7. **.claude/rules/project-root-boundary.md** — Added exemption:
   `**EXCEPTION:** groundtruth-kb/examples/ (adopter fixtures) are exempt from the applications/ mandate.`

### Test file

8. **platform_tests/scripts/test_fab07_doctor_false_signals.py** — 10 new tests:

| Test | HYG | Verifies |
|------|-----|----------|
| `test_harvest_coverage_prefix_match` | HYG-049 | Prefix matching finds coverage for versioned source_refs |
| `test_harvest_coverage_genuine_gap` | HYG-049 | Uncovered thread still registers as gap |
| `test_narrative_files_cite_examples_dir` | HYG-035 | Three narrative files reference `groundtruth-kb/examples/` |
| `test_project_root_boundary_examples_carveout` | HYG-035 | `project-root-boundary.md` has the examples carve-out |
| `test_narrative_approval_packets_exist` | HYG-035 | >=4 fab07 approval packets exist with correct metadata |
| `test_auq_coverage_excludes_prose_false_positives` | HYG-067 | Prose entries excluded; genuine entry still counted |
| `test_auq_coverage_all_prose_returns_pass` | HYG-067 | All-prose yields pass (no genuine entries) |
| `test_auq_coverage_genuine_missing_still_fails` | HYG-067 | Genuine non-AUQ entry still causes failure |
| `test_isolation_suite_skips_adopter_checks_on_platform` | HYG-068 | Platform context -> adopter checks pass-with-skip |
| `test_isolation_suite_runs_adopter_checks_on_adopter` | HYG-068 | Non-platform context -> adopter checks run normally |

### Approval packets

9. `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-agents-md.json`
10. `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-canonical-terminology.json`
11. `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-acting-prime-builder.json`
12. `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-project-root-boundary.json`

## Spec-to-Test Mapping

| Specification | Test(s) | Result |
|---------------|---------|--------|
| SPEC-1662 / HYG-049 (prefix match) | `test_harvest_coverage_prefix_match`, `test_harvest_coverage_genuine_gap` | PASS |
| SPEC-1662 / HYG-035 (narrative rewording) | `test_narrative_files_cite_examples_dir`, `test_project_root_boundary_examples_carveout`, `test_narrative_approval_packets_exist` | PASS |
| SPEC-1662 / HYG-067 (AUQ precision) | `test_auq_coverage_excludes_prose_false_positives`, `test_auq_coverage_all_prose_returns_pass`, `test_auq_coverage_genuine_missing_still_fails` | PASS |
| SPEC-1662 / HYG-068 (isolation gating) | `test_isolation_suite_skips_adopter_checks_on_platform`, `test_isolation_suite_runs_adopter_checks_on_adopter` | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | All 10 tests above derived from SPEC-1662 HYG items | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Specification Links section carries all triggered cross-cutting specs | SATISFIED |

## Verification Evidence

### Test execution

```
$ python -m pytest platform_tests/scripts/test_fab07_doctor_false_signals.py -q --tb=short
10 passed in 1.42s
```

### Code quality

```
$ ruff check groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py platform_tests/scripts/test_fab07_doctor_false_signals.py
All checks passed!

$ ruff format --check groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py platform_tests/scripts/test_fab07_doctor_false_signals.py
4 files already formatted.
```

## Requirement Sufficiency

Existing requirements sufficient. GOV-18 / SPEC-1662 (Assertion Quality
Standard) governs all four HYG items. No new specifications required.

## Recommended Commit Type

`fix:` — repairs four false-signal defects in doctor/harvest/isolation checks;
no net-new capability surface.

## Acceptance Criteria Check

Per Codex GO at -004:

- [x] HYG-049: `compute_active_bridge_thread_coverage` uses prefix matching
- [x] HYG-035: Narrative files cite `groundtruth-kb/examples/`; `project-root-boundary.md` has carve-out; approval packets exist
- [x] HYG-067: `_check_auq_coverage` excludes `prose:` entries
- [x] HYG-068: `run_isolation_checks` gates adopter checks on platform context

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
