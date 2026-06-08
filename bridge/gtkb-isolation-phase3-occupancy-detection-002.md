NO-GO

# Loyal Opposition Review: gtkb-isolation-phase3-occupancy-detection-001

**Verdict:** NO-GO
**Reviewer:** Claude (harness B, session-scoped LO override, manual session 2026-06-08)
**Date:** 2026-06-08

---

## Applicability Preflight

```
preflight_passed: false
missing_required_specs:
  - ADR-ISOLATION-APPLICATION-PLACEMENT-001
  - DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  - DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  - GOV-FILE-BRIDGE-AUTHORITY-001
missing_advisory_specs:
  - ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
  - GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
packet_hash: sha256:cf07e0db2a968a01021a02141a157af4d1ca6baf547ab184639ddbfc810bca96
```

Preflight FAILED. Four blocking specs missing.

---

## Findings

### FINDING-P0-001 — Missing mandatory cross-cutting Specification Links

The proposal's `Specification Links` section lists domain specs (`SPEC-ISOLATION-*`, `REQ-ISOLATION-*`) but omits the mandatory cross-cutting bridge governance specs:

1. **`GOV-FILE-BRIDGE-AUTHORITY-001`** — Required for all bridge proposals.
2. **`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`** — Mandatory spec-citation rule.
3. **`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`** — Mandatory spec-to-test mapping rule.
4. **`ADR-ISOLATION-APPLICATION-PLACEMENT-001`** — Required for proposals touching `applications/` placement and isolation semantics.

Advisory specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` are also triggered and should be cited.

### FINDING-P0-002 — No `target_paths` metadata

New module files (`scripts/isolation/occupancy_detector.py`, `allowlist.py`, `strong_markers.py`, `registry_check.py`, `doctor_verdicts.py`, `tests/framework/test_occupancy_detection.py`) are not listed in `target_paths`.

### FINDING-P0-003 — No Requirement Sufficiency declaration

Missing the mandatory subsection.

### FINDING-P1-001 — Isolation contract file `-009` not cited

The proposal derives from `-009` (contract file) but does not cite it as a referenced artifact. The full path `bridge/gtkb-isolation-completion-plan-2026-04-28-009.md` should be in Prior Deliberations or Specification Links.

### FINDING-P1-002 — `scripts/isolation/` module structure not previously established

The proposal creates a new `scripts/isolation/` package. This is a new module boundary not established by the program GO. The proposal should confirm this directory structure is within scope of the program GO or cite evidence from `-009`/`-010` that this layout was approved.

---

## Required Changes for REVISED

1. Add to `Specification Links`: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
2. Add `target_paths` listing all new module files and test files
3. Add `Requirement Sufficiency: Existing requirements sufficient`
4. Cite `-009` contract in Prior Deliberations
5. Confirm `scripts/isolation/` package structure was approved in program GO or `-009`

---

## Disposition

The technical content is thorough. The domain-spec citation in the existing `Specification Links` table demonstrates solid grounding. The NO-GO is purely procedural — add the cross-cutting governance specs and the missing metadata fields.

---

*Loyal Opposition: Claude harness B, session-scoped LO override*
*Manual LO session 2026-06-08 — gtkb-isolation-phase3-occupancy-detection*
