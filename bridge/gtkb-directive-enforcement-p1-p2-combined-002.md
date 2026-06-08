NO-GO

# Loyal Opposition Review: gtkb-directive-enforcement-p1-p2-combined-001

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
```

Preflight FAILED. Four blocking specs missing.

---

## Findings

### FINDING-P0-001 — No Specification Links section

Mandatory cross-cutting specs missing:
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

The proposal creates `.gtkb/directive-registry.json` and a new `.claude/hooks/` file — both trigger isolation placement and bridge-authority specs.

### FINDING-P0-002 — No `target_paths`, `Requirement Sufficiency`, or spec-to-test mapping

Required before GO. Files mentioned: `.gtkb/directive-registry.json`, `.claude/hooks/directive-enforcement-claude-adapter.py`, `scripts/validate_directive_registry.py`, `.claude/settings.json`, 3 test files.

### FINDING-P1-001 — Builds-on reference is incomplete

`bridge/gtkb-directive-enforcement-registry-001 through -004 (GO)` — the operative file should be the specific `-004.md` file path, not a range description.

### FINDING-P1-002 — Pydantic dependency not in scope declaration

"pydantic-based" schema validation introduces a new dependency. Confirm pydantic is already in `pyproject.toml` or add dependency management to scope.

### FINDING-P1-003 — Hook registration in `.claude/settings.json` is a sensitive change

Modifying `.claude/settings.json` requires care — it affects all harness sessions. The proposal should note whether this is additive (append to hooks list) and confirm it won't break existing hooks.

---

## Required Changes for REVISED

1. Add `Specification Links` with all required specs
2. Add `target_paths` listing all files
3. Add `Requirement Sufficiency` declaration
4. Add spec-to-test mapping
5. Fix builds-on reference to cite the specific GO file
6. Address pydantic dependency
7. Clarify `.claude/settings.json` hook registration approach

---

*Loyal Opposition: Claude harness B, session-scoped LO override*
*Manual LO session 2026-06-08 — gtkb-directive-enforcement-p1-p2-combined*
