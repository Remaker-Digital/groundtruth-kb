NO-GO

# Loyal Opposition Review: gtkb-ollama-lo-prompt-hardening-001

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
missing_advisory_specs:
  - DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
packet_hash: sha256:00e0dc4e7d4e89a25a9025c35c3659f2db2e19e2c925190f7d2f44fa68b777ef
```

Preflight FAILED. Three blocking specs are missing.

---

## Findings

### FINDING-P0-001 — Missing mandatory cross-cutting Specification Links

The proposal's `Specification Links` section is absent. The following blocking specs are required for every bridge proposal and must be cited:

1. **`GOV-FILE-BRIDGE-AUTHORITY-001`** — Governs the file bridge protocol itself. Required for all proposals filed as `bridge/*.md`.
2. **`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`** — Mandates that every implementation proposal cite all relevant governing specifications before receiving GO.
3. **`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`** — Mandates that a spec-to-test mapping be included, showing which tests cover which specification clauses.

Additionally, advisory spec `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is triggered by lifecycle-state content and should be cited.

### FINDING-P0-002 — No formal Requirement Sufficiency declaration

The proposal lacks the mandatory `Requirement Sufficiency` subsection with one of:
- `Existing requirements sufficient`
- `New or revised requirement required before implementation`

### FINDING-P0-003 — No `target_paths` metadata

The proposal describes changes to `scripts/ollama_harness.py` but does not include a `target_paths` metadata list as required by the Mandatory Implementation-Start Authorization Metadata gate.

### FINDING-P1-001 — `build_system_prompt()` signature change is breaking

The proposed `build_system_prompt(role, bridge_slug)` signature replaces the current `build_system_prompt(skill, model_route)` signature. The current signature is used by `_dispatch_from_routing()`. This is an undisclosed breaking change that needs a migration path or compatibility shim.

### FINDING-P1-002 — `--bridge-id` flag referenced but does not exist

The testing plan references `python scripts/ollama_harness.py --bridge-id gtkb-test-bridge-001` but `--bridge-id` is not a current CLI flag. The test plan should reference the actual flag (`-p` prompt) or propose adding `--bridge-id` as a new flag.

### FINDING-P2-001 — Prompt template doesn't update INDEX.md

The 5-step protocol describes writing the verdict file (Step 4) but omits updating `bridge/INDEX.md`. LO writes both the verdict file AND the INDEX entry. This must be explicit in Step 4 or as a separate Step 4b.

---

## Required Changes for REVISED

1. Add a `Specification Links` table citing at minimum:
   - `GOV-FILE-BRIDGE-AUTHORITY-001`
   - `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
   - `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
   - `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
   - Any existing specs governing `scripts/ollama_harness.py` behavior (e.g. specs from the Ollama integration project)
2. Add `Requirement Sufficiency: Existing requirements sufficient` (or identify what new spec is needed)
3. Add `target_paths: [scripts/ollama_harness.py]` and any test files
4. Fix the `build_system_prompt()` migration: either keep backward-compatible signature or provide explicit migration plan
5. Fix the testing plan to use the actual CLI interface
6. Add INDEX.md update to the numbered steps in the prompt protocol

---

## Disposition

The underlying problem statement and proposed solution are sound. The prompt-restructuring approach is the right fix for the model turn-exhaustion issue. This NO-GO is procedural — the proposal needs the mandatory governance scaffolding and a few design corrections.

**Priority:** High. Revise and resubmit promptly — Ollama LO dispatch remains non-functional until this lands.

---

*Loyal Opposition: Claude harness B, session-scoped LO override*
*Manual LO session 2026-06-08 — gtkb-ollama-lo-prompt-hardening*
