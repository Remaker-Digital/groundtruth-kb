NO-GO

# Loyal Opposition Review: gtkb-mcp-stable-harness-surface-implementation-001

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

Additionally: the proposal introduces a new `fastmcp` dependency and a new package surface (`groundtruth_kb.mcp_surface`). Relevant governing specs for MemBase API stability (`REQ-HARNESS-REGISTRY-001` FR5 or equivalent) and any spec governing MCP server additions should be cited.

### FINDING-P0-002 — No `target_paths`, `Requirement Sufficiency`, or spec-to-test mapping

Required before GO. Target files: `groundtruth_kb/mcp_surface/server.py` (new), harness configuration templates (paths unspecified), `tests/framework/test_mcp_surface_tools.py`.

### FINDING-P0-003 — Builds-on reference is an ADVISORY, not a GO

`bridge/gtkb-mcp-stable-harness-surface-advisory-2026-05-09-001.md` is an ADVISORY. Confirm this ADVISORY was formally adopted by Prime before treating it as a live build-from reference. If not adopted, cite the adoption mechanism.

### FINDING-P1-001 — `fastmcp` dependency not declared

The proposal assumes `fastmcp` is available but it is not in `pyproject.toml`. Adding a new PyPI dependency requires an explicit scope entry and dependency-management discussion.

### FINDING-P1-002 — Role-based access control design is underspecified

"Guards: Authority check for the active role (Prime vs. LO)" — this is a critical security surface but has no design detail. How is the active role determined? What happens when role resolution fails? This needs a concrete design before GO.

---

## Required Changes for REVISED

1. Add `Specification Links` with required specs
2. Add `target_paths` listing new package files and test files
3. Add `Requirement Sufficiency` declaration
4. Confirm ADVISORY adoption or document adoption path
5. Declare `fastmcp` as a new dependency with version pinning
6. Specify the role-based guard design concretely

---

*Loyal Opposition: Claude harness B, session-scoped LO override*
*Manual LO session 2026-06-08 — gtkb-mcp-stable-harness-surface-implementation*
