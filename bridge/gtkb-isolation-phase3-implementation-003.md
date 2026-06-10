REVISED

# Implementation Proposal — GT-KB Isolation Phase 3: Registration and Doctor

**Status:** REVISED
**Document name:** `gtkb-isolation-phase3-implementation`
**Version:** 003
**Author:** Prime Builder (antigravity, harness C)
**Date:** 2026-06-09 UTC
**Builds on:** `bridge/gtkb-isolation-phase3-occupancy-detection-003.md` (Slice 1 - GO pending), `bridge/gtkb-isolation-completion-plan-2026-04-28-010.md` (GO)

## 0. Scope

This proposal implements **Slices 2 & 3** of the isolation completion plan, building on the occupancy detection engine implemented in Slice 1. It covers:
- The single-active-application cardinality contract and registry management.
- CLI subcommand `gt application register` with self-completion validation.
- CLI subcommand `gt project doctor` (verdict matrix integration).

To address the sibling overlap finding, this proposal explicitly coordinates with and consumes the output of the sister proposal `gtkb-isolation-phase3-occupancy-detection-003.md` (Slice 1).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — File bridge protocol governance (config/governance/gov-file-bridge-authority-001.md)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Implementation proposals must cite specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verified proposals must have spec-to-test mapping
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Placement contract for application isolation
- `SPEC-ISOLATION-APPLICATION-SLOT-CARDINALITY-001` — Defines single-active-application constraint
- `SPEC-ISOLATION-PLATFORM-DOCTOR-VERDICTS-001` — Defines doctor diagnostic matrix
- `REQ-ISOLATION-APPLICATION-REGISTER-001` — FR1-FR5 (register flow, cardinality checks)
- `REQ-ISOLATION-PLATFORM-DOCTOR-001` — FR1-FR8 (doctor verdicts, remediation)
- `DELIB-S509-B1-B5-TRIAGE` — S509 triage deliberation.
- `DELIB-0834` — Agent Red as fully conformant application.
- `DELIB-0877` — GT-KB/application separation.

## 2. Implementation Scope

- **Project:** `PROJECT-GTKB-PLATFORM-CORE`
- **Work Item:** `WI-4327` (Registry/doctor command integration)
- **Requirement Sufficiency:** Existing requirements sufficient
- **target_paths:**
  - `groundtruth-kb/src/groundtruth_kb/cli.py`
  - `groundtruth-kb/src/groundtruth_kb/isolation/validation.py`
  - `applications/registry.toml`
  - `groundtruth-kb/tests/framework/test_application_register_validation.py`
  - `groundtruth-kb/tests/framework/test_platform_doctor_matrix.py`

All target paths reside under the project root (`E:\\GT-KB`), satisfying the in-root requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## 3. Requirement Sufficiency

| Requirement | Source | Satisfied By | Test Coverage |
|-------------|--------|--------------|---------------|
| SPEC-ISOLATION-APPLICATION-SLOT-CARDINALITY-001 | `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` | `applications/registry.toml` + validation checks | `tests/framework/test_application_register_validation.py` |
| REQ-ISOLATION-APPLICATION-REGISTER-001 | `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` | `gt application register` in `cli.py` | `tests/framework/test_application_register_validation.py` |
| REQ-ISOLATION-PLATFORM-DOCTOR-001 | `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` | `gt project doctor` in `cli.py` | `tests/framework/test_platform_doctor_matrix.py` |

## 4. Deliverables

### 4.1 CLI Command Group `gt application`
- Registers the new `application` group and its subcommand `register` in `groundtruth_kb/cli.py`.
- Integrates self-completion preflight validations.

### 4.2 Self-Completion Validation Engine (`groundtruth_kb/isolation/validation.py`)
- Verifies name consistency across files and checks configuration schema versions against `applications/registry.toml` constraints.

### 4.3 Authority Registry (`applications/registry.toml`)
- The authoritative manifest mapping registered application names and slots, enforcing the single-active-application invariant.

### 4.4 Doctor verdict integration in `gt project doctor`
- Integrates the 8-cell verdict matrix (from occupancy detection) into the doctor reporting flow.

## 5. Specification-Derived Verification Plan

### Automated Tests
Run the pytest suite covering the validator, register CLI, and doctor integration:
```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest tests/framework/test_application_register_validation.py -v
groundtruth-kb\.venv\Scripts\python.exe -m pytest tests/framework/test_platform_doctor_matrix.py -v
```

### Spec-to-Test Mapping

| Spec ID | Test File | Test Case(s) |
|---------|-----------|--------------|
| SPEC-ISOLATION-APPLICATION-SLOT-CARDINALITY-001 | `tests/framework/test_application_register_validation.py` | `test_cardinality_constraint_registry` |
| REQ-ISOLATION-APPLICATION-REGISTER-001 | `tests/framework/test_application_register_validation.py` | `test_register_command_success`, `test_register_mismatched_markers_fails` |
| REQ-ISOLATION-PLATFORM-DOCTOR-001 | `tests/framework/test_platform_doctor_matrix.py` | `test_doctor_reports_occupancy_matrix` |

## target_paths

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/isolation/validation.py`
- `applications/registry.toml`
- `groundtruth-kb/tests/framework/test_application_register_validation.py`
- `groundtruth-kb/tests/framework/test_platform_doctor_matrix.py`

## Requirement Sufficiency

Existing requirements sufficient
