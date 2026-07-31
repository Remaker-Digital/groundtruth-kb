GO
author_identity: Ollama D
author_harness_id: D
author_session_context_id: 2026-07-14T21-27-19Z-loyal-opposition-D-3f00ff
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; endpoint http://localhost:11434

# Loyal Opposition Review Verdict - WI-5233 Dispatcher Selection Order & Cap Repair

bridge_kind: lo_verdict
Document: gtkb-wi5233-dispatch-selection-order-cap-repair
Version: 002
Date: 2026-07-14 UTC

reviewed_file: bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-001.md
result: GO

## Preflight Checks

### Applicability Preflight

- packet_hash: `sha256:cf87599b06764dc87fbd257a137a383a9f58db80d134d50b530b42dc2ca8646e`
- bridge_document_name: `gtkb-wi5233-dispatch-selection-order-cap-repair`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-001.md`
- operative_file: `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-001.md`
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

### ADR/DCL Clause Preflight

- Bridge id: `gtkb-wi5233-dispatch-selection-order-cap-repair`
- Operative file: `bridge\gtkb-wi5233-dispatch-selection-order-cap-repair-001.md`
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

Both preflight scripts exited cleanly (exit 0). Applicability passed with no missing required specs and no blocking ADR/DCL gaps.

## Review Findings

1. **Problem statement is well-supported.** The proposal documents that the current `scripts/dispatcher_runtime.py` reverses the canonical LO actionable list through `_selected_oldest_first` (`return list(reversed(items))[:max_items]`), and that `_effective_max_items_for_target` only consults `target.invocation_surfaces["headless"]["max_items"]` rather than the dispatch-surface `dispatch_max_items`. A quick inspection of the source confirmed `_selected_oldest_first` still contains the `reversed(items)` logic and `_effective_max_items_for_target` does not check the `dispatch` surface cap.

2. **Scope is bounded and appropriate.** The proposal limits changes to `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py`, explicitly excluding runtime JSON, leases, harness roles, credentials, and unrelated dispatcher hunks. This matches the work-item authorization.

3. **Bridge authority is intact.** The proposal is a NEW prime_proposal with correct project authorization, project, work item, and target path metadata. The work-intent claim for `gtkb-wi5233-dispatch-selection-order-cap-repair` was successfully acquired for the Loyal Opposition role (claim row 31141, session `2026-07-14T21-27-19Z-loyal-opposition-D-3f00ff`).

4. **Specification linkage is present.** All mandatory DCL/GOV specs are cited, and the verification plan maps each spec to concrete test activity.

5. **Verification plan is adequate.** Acceptance criteria require:
   - A focused integration test reproducing the raw LO queue order and proving cap=1 returns the oldest (WI-5138) instead of the newest (WI-5226).
   - A regression test proving dispatch-surface `dispatch_max_items=1` is honored even when headless max_items is absent or larger.
   - Existing dispatcher runtime tests remain passing.

## Advisory Notes for Prime Builder / Verification Stage

- When implementing `_selected_oldest_first`, change the logic to simply `return items[:max_items]` when the input is already oldest-first, or document the new contract explicitly. Preserve the `max_items <= 0` short-circuit.
- In `_effective_max_items_for_target`, prefer `target.invocation_surfaces.get("dispatch", {}).get("dispatch_max_items")` before falling back to `headless.max_items`, then `max_items`. This aligns with the dispatch surface as the authoritative source for dispatch caps.
- The existing test file currently contains a single `_selected_oldest_first` call; the verification report should show that the new targeted tests were added and exercised.

## Verdict

The proposal is clear, properly scoped, spec-linked, and the preflight gates pass. I issue **GO** for `gtkb-wi5233-dispatch-selection-order-cap-repair` implementation and independent verification.
