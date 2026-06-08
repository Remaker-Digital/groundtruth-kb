NO-GO

# Loyal Opposition Review: gtkb-platform-observability-hygiene-001

**Verdict:** NO-GO
**Reviewer:** Claude (harness B, session-scoped LO override, manual session 2026-06-08)
**Date:** 2026-06-08

---

## Applicability Preflight

```
preflight_passed: false
missing_required_specs:
  - DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  - DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  - GOV-FILE-BRIDGE-AUTHORITY-001
```

Preflight FAILED. Three blocking specs missing.

---

## Findings

### FINDING-P0-001 — No Specification Links section

Mandatory cross-cutting specs missing:
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

The `dispatch-state.json` staleness check builds on the cross-harness trigger spec family. Relevant specs (e.g., from the trigger's governance thread) should be cited.

### FINDING-P0-002 — No `target_paths`, `Requirement Sufficiency`, or spec-to-test mapping

Required before GO. Target files: `groundtruth_kb/cli/platform_doctor.py` (modified), `scripts/check_harness_parity.py` (modified), `scripts/cross_harness_bridge_trigger.py` (modified — cleanup logic).

### FINDING-P0-003 — Builds-on references are LO findings, not formal artifacts

"LO findings 2026-06-03 and 2026-06-04" — cite DELIB IDs or advisory bridge references for the sourcing findings.

### FINDING-P1-001 — Staleness threshold hardcoded to 1 hour without spec

"more than 1 hour old during an active session" — this threshold is not derived from any cited specification. Either cite the spec that mandates this threshold or explain the design rationale and propose a new DCL.

### FINDING-P1-002 — Cleanup of `*.tmp` files in `.gtkb-state/` must not touch live state

The cleanup logic must be scoped narrowly. `.gtkb-state/bridge-poller/*.tmp` files may still be in use by concurrent processes (atomic write pattern uses `.tmp` suffix per the trigger implementation). The proposal must define the staleness criterion for `*.tmp` cleanup (e.g., older than X minutes and no associated PID active).

---

## Required Changes for REVISED

1. Add `Specification Links` with required specs
2. Add `target_paths` and `Requirement Sufficiency`
3. Convert LO finding references to formal artifact citations
4. Specify staleness threshold derivation (cite spec or propose new DCL)
5. Add safety constraints for `*.tmp` cleanup to avoid cleaning live atomic-write temporaries

---

*Loyal Opposition: Claude harness B, session-scoped LO override*
*Manual LO session 2026-06-08 — gtkb-platform-observability-hygiene*
