GO

bridge_kind: lo_verdict
Document: gtkb-wi3384-clause-in-root-disclosure-exemption
Version: 002
Reviewed version: 001
Author: Loyal Opposition (Ollama harness, id D)
author_identity: loyal-opposition/ollama
author_harness_id: D
author_session_context_id: ollama-harness-d
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash
Date: 2026-06-14 UTC

# LO Review: WI-3384 CLAUSE-IN-ROOT disclosure exemption

## Verdict

**GO**

The implementation proposal for WI-3384 is approved to proceed to implementation.

## Applicability Preflight (advisory context)

### `bridge_applicability_preflight.py`

```
## Applicability Preflight

- packet_hash: `sha256:461dbbef699bff79f44f69899cc27d09d6de5a9e80c2da53043e10256cc8249b`
- bridge_document_name: `gtkb-wi3384-clause-in-root-disclosure-exemption`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi3384-clause-in-root-disclosure-exemption-001.md`
- operative_file: `bridge/gtkb-wi3384-clause-in-root-disclosure-exemption-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

### `adr_dcl_clause_preflight.py`

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi3384-clause-in-root-disclosure-exemption`
- Operative file: `bridge\gtkb-wi3384-clause-in-root-disclosure-exemption-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Review findings

### What is being proposed

WI-3384 fixes a false-positive in the `adr_dcl_clause_preflight` CLAUSE-IN-ROOT detector. Currently, the detector's `failure_pattern` is applied to the entire proposal `content`, so an out-of-root path mentioned only in an explicit disclosure (e.g., "I installed X under `C:\Users\...` but that is not a GT-KB artifact") refutes an otherwise in-root proposal.

### Why this is acceptable

1. **False-negative-safe by construction.** The proposal always scans the `target_paths` declaration, so any proposal that genuinely DECLARES an out-of-root artifact is still refuted. This preserves the core invariant of ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT.
2. **Opt-in and scoped.** A new per-clause config flag (`failure_pattern_disclosure_exempt`) gates the new behavior; only the CLAUSE-IN-ROOT clause opts in. All other clauses continue to apply `failure_pattern` to the full content exactly as before.
3. **Conservative default for prose.** Unmarked out-of-root mentions still refute. Only content inside an explicit `<!-- in-root-disclosure -->...<!-- /in-root-disclosure -->` marker is exempted.
4. **Well-specified verification plan.** The proposal includes tests for:
   - marked disclosure no longer refutes (the fix),
   - out-of-root `target_paths` still refutes even inside a disclosure marker (no false-negative),
   - unmarked prose still refutes (conservative default),
   - other clauses unchanged,
   - rehearsal exception preserved,
   - loader default for the new flag.
5. **Appropriate authorization.** The work is covered by PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001 and the owner cycle-17 decision to seed WI-3384 with the safe-hybrid design.

### Minor notes for the implementation report

- Ensure the disclosure-marker convention is documented in the config comment and in the preflight docstring as planned; the rules-file update is correctly deferred to a narrative-artifact authorization.
- Include the actual executed test output and `ruff` lint/format status in the implementation report.
- Confirm that the existing clause-preflight regression suite still passes with the change.

## Conclusion

The proposal is coherent, correctly scoped, preserves governance invariants, and includes adequate test coverage. I find no substantive basis for a NO-GO.

**GO** — proceed to implementation.
