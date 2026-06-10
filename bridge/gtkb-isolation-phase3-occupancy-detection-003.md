REVISED

# Implementation Proposal — GT-KB Isolation Phase 3: Occupancy Detection Implementation

**Status:** REVISED
**Document name:** `gtkb-isolation-phase3-occupancy-detection`
**Version:** 003
**Author:** Prime Builder (antigravity, harness C)
**Date:** 2026-06-09 UTC
**Builds on:** `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md` (GO)

## 0. Scope

This is **Slice 1 of 3** for the isolation completion plan Phase 3/4/5 implementation. It covers:
- Occupancy detection algorithm (§1.1 of -009)
- `gt platform doctor` occupancy verdict cells (§1.2.2 of -009)
- Test contract tests 8-16 (§1.3 of -009)

**Out of scope for this slice:**
- Self-completion validation gate (Slice 2: implemented by `gtkb-isolation-phase3-implementation`)
- Application registration flow integration (Slice 3: implemented by `gtkb-isolation-phase3-implementation`)

To address LO review concerns about package layout, the detector code has been relocated from `scripts/isolation/` to `groundtruth_kb/isolation/` (within the core package structure).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — File bridge protocol governance (config/governance/gov-file-bridge-authority-001.md)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Implementation proposals must cite specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verified proposals must have spec-to-test mapping
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Placement contract for application isolation
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Artifact-oriented development guidelines
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Artifact-oriented governance
- `SPEC-ISOLATION-APPLICATION-SLOT-OCCUPANCY-001` — Defines occupancy semantics (default-occupied, allowlisted exceptions)
- `SPEC-ISOLATION-APPLICATION-SLOT-CARDINALITY-001` — Defines single-active-application constraint
- `SPEC-ISOLATION-PLATFORM-DOCTOR-VERDICTS-001` — Defines doctor diagnostic matrix
- `REQ-ISOLATION-APPLICATION-REGISTER-001` — FR1-FR5 (register flow, cardinality checks)
- `REQ-ISOLATION-PLATFORM-DOCTOR-001` — FR1-FR8 (doctor verdicts, remediation)
- `DELIB-S509-B1-B5-TRIAGE` — S509 triage deliberation.
- `DELIB-0834` — Agent Red as fully conformant application.
- `DELIB-0877` — GT-KB/application separation.
- `DELIB-1327` — Codex verification of application isolation sub-slice 1.
- `DELIB-1329` — Codex NO-GO on earlier application isolation revision.

## 2. Implementation Scope

- **Project:** `PROJECT-GTKB-PLATFORM-CORE`
- **Work Item:** `WI-4329` (Add doctor occupancy / validation checks)
- **Requirement Sufficiency:** Existing requirements sufficient
- **target_paths:**
  - `groundtruth-kb/src/groundtruth_kb/isolation/occupancy_detector.py`
  - `groundtruth-kb/src/groundtruth_kb/isolation/allowlist.py`
  - `groundtruth-kb/src/groundtruth_kb/isolation/strong_markers.py`
  - `groundtruth-kb/src/groundtruth_kb/isolation/registry_check.py`
  - `groundtruth-kb/src/groundtruth_kb/isolation/doctor_verdicts.py`
  - `groundtruth-kb/tests/framework/test_occupancy_detection.py`

All target paths reside under the project root (`E:\\GT-KB`), satisfying the in-root requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## 3. Requirement Sufficiency

| Requirement | Source | Satisfied By | Test Coverage |
|-------------|--------|--------------|---------------|
| SPEC-ISOLATION-APPLICATION-SLOT-OCCUPANCY-001 | `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` | `groundtruth_kb/isolation/occupancy_detector.py` | `tests/framework/test_occupancy_detection.py` |
| SPEC-ISOLATION-APPLICATION-SLOT-CARDINALITY-001 | `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` | `groundtruth_kb/isolation/registry_check.py` | `tests/framework/test_occupancy_detection.py` |
| SPEC-ISOLATION-PLATFORM-DOCTOR-VERDICTS-001 | `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` | `groundtruth_kb/isolation/doctor_verdicts.py` | `tests/framework/test_occupancy_detection.py` |

## 4. Deliverables

### 4.1 Occupancy Detection Module (`groundtruth_kb/isolation/occupancy_detector.py`)
- Detects if `applications/<name>/` is occupied by walking directory contents.
- Restricts content to allowlisted items (e.g. `.gitkeep`, cleanup-marked READMEs) and checks registry entries.

### 4.2 Allowlist implementation (`groundtruth_kb/isolation/allowlist.py`)
- Validates directories/files against allowlisted names and verifies the existence of cleanup tags inside `README.md`.

### 4.3 Strong markers checking (`groundtruth_kb/isolation/strong_markers.py`)
- Checks for standard application signatures like `application.toml`, `.gtkb-app-isolation.json`, `src/`, etc.

### 4.4 Registry entry check (`groundtruth_kb/isolation/registry_check.py`)
- Validates configuration slots against `applications/registry.toml`.

### 4.5 Doctor verdicts implementation (`groundtruth_kb/isolation/doctor_verdicts.py`)
- Integrates verdict classifications with `gt platform doctor` CLI, enabling detailed feedback on occupancy states.

## 5. Specification-Derived Verification Plan

### Automated Tests
Run the occupancy detection test suite:
```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest tests/framework/test_occupancy_detection.py -v
```

### Spec-to-Test Mapping

| Spec ID | Test File | Test Case(s) |
|---------|-----------|--------------|
| SPEC-ISOLATION-APPLICATION-SLOT-OCCUPANCY-001 | `tests/framework/test_occupancy_detection.py` | `test_non_marker_blocks_register`, `test_allowlisted_readme_succeeds` |
| SPEC-ISOLATION-APPLICATION-SLOT-CARDINALITY-001 | `tests/framework/test_occupancy_detection.py` | `test_registry_only_conflict` |
| SPEC-ISOLATION-PLATFORM-DOCTOR-VERDICTS-001 | `tests/framework/test_occupancy_detection.py` | `test_doctor_verdict_matrix` |

## target_paths

- `groundtruth-kb/src/groundtruth_kb/isolation/occupancy_detector.py`
- `groundtruth-kb/src/groundtruth_kb/isolation/allowlist.py`
- `groundtruth-kb/src/groundtruth_kb/isolation/strong_markers.py`
- `groundtruth-kb/src/groundtruth_kb/isolation/registry_check.py`
- `groundtruth-kb/src/groundtruth_kb/isolation/doctor_verdicts.py`
- `groundtruth-kb/tests/framework/test_occupancy_detection.py`

## Requirement Sufficiency

Existing requirements sufficient
