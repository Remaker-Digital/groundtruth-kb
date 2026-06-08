NEW

# Implementation Proposal — GT-KB Isolation Phase 3: Registration and Doctor

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-isolation-phase3-implementation`
**Builds on:** `bridge/gtkb-isolation-completion-plan-2026-04-28-010` (GO)

## 1. Scope

Implements the single-active-application cardinality contract, default-occupied invariant, and self-completion validation for `gt application register`.

## 2. Deliverables

### 2.1 Occupancy Detection Engine

- Implements §1.1 of GO-010.
- Logic to classify `applications/<name>/` as OCCUPIED or UNOCCUPIED.
- Supports the narrow allowlist: `.gitkeep`, empty dirs, README with cleanup-marker.

### 2.2 CLI Enhancement: `gt application register`

- Adds the self-completion preflight (§1.2 of GO-010).
- Parses `application.toml`, `.gtkb-app-isolation.json`, and registry entries.
- Validates name consistency and schema compatibility.
- Aborts on malformed or mismatched markers.

### 2.3 CLI Enhancement: `gt platform doctor`

- Implements the verdict matrix (§1.2.2 of GO-010).
- Reports exactly WHY a slot is occupied (strong marker vs. unrecognized content).
- Flags registry drift.

### 2.4 Registry Management

- Authoritative `applications/registry.toml` at root.
- Tools to add/remove entries with cardinality enforcement (only one entry allowed).

### 2.5 Test Suite

- `tests/framework/test_application_occupancy_invariant.py`
- `tests/framework/test_application_register_validation.py`
- `tests/framework/test_platform_doctor_matrix.py`

## 3. Execution Plan

1. Implement `groundtruth_kb.isolation.occupancy` detector.
2. Implement `groundtruth_kb.isolation.validation` preflight.
3. Update `groundtruth_kb.cli.application_register` to use the new occupancy and validation logic.
4. Update `groundtruth_kb.cli.platform_doctor` to implement the 8-cell matrix.
5. Implement `applications/registry.toml` as a single-entry TOML manifest.
6. Verify with the suite of 16 cardinality tests defined in GO-010.

## 4. Reversibility

- The cardinality check can be relaxed if needed (though not planned).
- All metadata remains in-directory or in the root registry.

## 5. Decision Needed

None. This follows the owner-approved plan.
