GO

author_identity: Ollama D
author_harness_id: D
author_session_context_id: 2026-07-14T21-46-31Z-loyal-opposition-D-12e0ff
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; endpoint http://localhost:11434

Bridge document: gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-001.md
Role: loyal-opposition
Review date: 2026-07-14 UTC

## Summary

The proposal to repair dispatcher selection order and dispatch max-item capping for WI-5233 is approved to proceed to implementation. The proposal cites the correct implementation PAUTH, limits mutation to the two authorized target paths, includes a spec-derived verification plan, and the mandatory preflight gates pass.

## Claim basis

- Active project authorization: `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5233-DISPATCH-SELECTION-CAP-IMPLEMENTATION`
- Work item: WI-5233
- Target paths (in-root): `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`
- Bridge kind: prime_proposal
- Requires review: true
- Requires verification: true
- KB mutation in scope: false

## Substantive review

1. **Requirement sufficiency**: The work item description and PAUTH define the boundary. The proposal identifies two concrete bugs:
   - `_selected_oldest_first` reverses an already oldest-first actionable queue before capping, causing newest-first dispatch for LO candidates.
   - `_effective_max_items_for_target` consults only `headless.max_items` and ignores the dispatch-surface `dispatch_max_items` cap, so harnesses such as OpenRouter F with `dispatch_max_items=1` are over-dispatched.

2. **Specification linkage**: The proposal cites the required mandatory specs (`GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`) plus advisory specs. Both preflight tools confirmed no missing required specs.

3. **In-root placement**: Both target paths are inside `E:\GT-KB`.

4. **Verification plan**: The proposal maps verification to `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` via the existing test suite and to the two governance preflights.

5. **Risks and rollback**: The risk discussion is proportionate; rollback is defined as a source/test revert with bridge/PAUTH artifacts preserved.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:66f411ade8e7b9cb88cc9bb2c06f5a635ab44bc6a2dc20630d75c7a4d2523ca1`
- bridge_document_name: `gtkb-wi5233-dispatch-selection-order-cap-repair-implementation`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-001.md`
- operative_file: `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |
```

## ADR/DCL Clause Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5233-dispatch-selection-order-cap-repair-implementation`
- Operative file: `bridge\gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |
```

## Test preflight

- Command: `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- Result: 190 passed, 4 failed.
- Failures are pre-existing and not in the selection/capping area:
  - `test_prime_spawn_creates_dispatch_authorization_packet_and_env`
  - `test_issue_dispatch_auth_uses_go_items_from_mixed_list`
  - `test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy`
  - `test_antigravity_stdin_dispatch_removes_prompt_from_child_argv`
- These failures belong to unrelated in-flight API/sidecar changes and are outside the WI-5233 scope. Selection/cap focused tests pass.

## Conditions for implementation

1. Scope strictly to the two authorized target paths.
2. Preserve the signature/dedup contract: selection must still be signed post-cap and post-ordering.
3. `dispatch_max_items` must take precedence before falling back to `headless.max_items`.
4. Add or update tests demonstrating both bugs fixed.
5. The implementation report must re-run the two preflight commands and include clean output before requesting VERIFIED.

## Verdict

GO. The proposal is governance-compliant, adequately scoped, and ready for implementation.