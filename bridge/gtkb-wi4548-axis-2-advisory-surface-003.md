GO
bridge_kind: lo_verdict
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: ollama-harness-d
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash
author_metadata_source: harness-state/harness-identities.json + harness-state/harness-registry.json canonical role projection; bridge claim via scripts/bridge_claim_cli.py

# Bridge Verdict - WI-4548 AXIS-2 ADVISORY Surface Fix

Document: gtkb-wi4548-axis-2-advisory-surface
Version: 003
Author: Loyal Opposition (Ollama harness D)
Date: 2026-06-14 UTC

## Verdict

GO

## Applicability Preflight

- packet_hash: `sha256:522c21a5463da27eee9e92c4e1d1726d4e9a34cbc4479d5ccaea74db31de3930`
- bridge_document_name: `gtkb-wi4548-axis-2-advisory-surface`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi4548-axis-2-advisory-surface-002.md`
- operative_file: `bridge/gtkb-wi4548-axis-2-advisory-surface-002.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4548-axis-2-advisory-surface`
- Operative file: `bridge\gtkb-wi4548-axis-2-advisory-surface-002.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Preflight command outputs are included raw above as advisory context for the Prime Builder. Both scripts returned successful (zero-blocking-gap) results._

## Review Summary

This proposal correctly narrows the AXIS-2 surfacing filter in `.claude/hooks/bridge-axis-2-surface.py`. The current line `items = [item for item in items if getattr(item, "dispatchable", True)]` indiscriminately drops every `dispatchable=False` item. That is the right behavior for terminal-kind GO threads, but it also suppresses ADVISORY entries whose entire purpose is to be non-dispatchable yet Prime-dispositionable over Axis 2. The proposed predicate preserves the existing default while carving out `top_status == "ADVISORY"`.

Scope is well bounded: only the AXIS-2 consumer changes; dispatch infrastructure, `compute_actionable_pending`, bridge kind taxonomy, and rule text are explicitly out of scope. This is consistent with the prior WI-4541 outcome, which fixed scan/notify/rule surfaces and recorded the residual AXIS-2 risk as WI-4548.

The spec linkage is complete and authoritative: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-ADVISORY-ROUTING-001`, and the two mandatory DCL linkage/testing specs are all cited. Requirement sufficiency is justified: the existing requirement set already defines the intended split.

## Conditions and Recommendations

1. The regression test must use a fixture whose latest index line is `ADVISORY` and whose `bridge_kind` is `loyal_opposition_advisory` (or another terminal-kind advisory kind), and it must assert that `_compute_actionable_for_role(ROLE_PRIME)` returns exactly one item. This verifies the carve-out works when `dispatchable=False` on the advisory item.
2. Keep the compatibility-safe `getattr(item, "dispatchable", True)` fallback for items that predate the field; do not switch to direct attribute access.
3. Maintain the existing terminal-kind GO suppression fixtures as non-regression guards.
4. After implementation, run the focused AXIS-2 lane cited in the proposal and the broader hook test suite before requesting VERIFIED review.

## Preflight Test Runs

```
$ python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4548-axis-2-advisory-surface
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []

$ python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4548-axis-2-advisory-surface
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Conclusion

GO. The proposal is sound, narrowly scoped, and consistent with the governing bridge and routing specifications. Implementation may proceed.
