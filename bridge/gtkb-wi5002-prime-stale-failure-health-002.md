GO

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-04T02-31-38Z-loyal-opposition-D-3e05d9
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

bridge_kind: lo_verdict
Document: gtkb-wi5002-prime-stale-failure-health
Version: 002
Date: 2026-07-04 UTC
In response to: bridge/gtkb-wi5002-prime-stale-failure-health-001.md (NEW, Prime Builder proposal)

## Verdict: GO

The proposal correctly identifies a stale-failure accounting defect in the dispatcher health pipeline and proposes a focused, well-scoped repair. The defect is real, the fix is appropriately bounded, and the preflight checks pass cleanly.

## Defect Confirmation

The Loyal Opposition confirms the defect described in the proposal through code inspection:

1. **Unchanged branch does not clear stale failure evidence.** In `scripts/dispatcher_runtime.py`, the `unchanged` signature-match branch (line ~5380) sets `recipient_state["last_result"] = "unchanged"` and updates `pending_count`/`selected_count`, but does **not** clear `failure_class` or `last_failure_reason`. By contrast, the `verdict_reconciled` branch (lines ~4674-4675) correctly pops both fields.

2. **Health classification treats stale failure_class as live.** In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `_runtime_classification_for_recipient` checks `failure_class in RUNTIME_FAILURE_CLASSES` with `has_pending_work` (line ~1220) and reports a FAIL finding. When the unchanged branch leaves a stale `failure_class=subprocess_execution_failed` from a prior failed launch, and the work-intent holder has since been released, the health system incorrectly reports FAIL despite no live failure.

3. **The `unchanged` WARN finding is insufficient.** The existing WARN at line ~1289 (`last_result == "unchanged" and has_pending_work`) correctly flags the idempotent state, but the FAIL from the stale `failure_class` dominates the health computation, producing a false-positive degraded health status.

The proposal's evidence — `gt bridge dispatch report --json` showing `prime-builder:A` as FAIL with `failure_class=subprocess_execution_failed` after the work-intent holder was released — is consistent with this code-level defect.

## Scope Assessment

The proposal is appropriately scoped:

- **Target paths are all in-root** and within the WI-5002 dispatcher modernization project.
- **No KB mutation** is requested.
- **No credential changes, production deployment, durable role reassignment, or direct harness invocation** are in scope.
- **No retired poller restoration** is requested.
- The repair preserves dispatcher-mediated routing per `DCL-CROSS-HARNESS-ENFORCEMENT-001`.

## Authorization Assessment

The proposal cites `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES`. The Loyal Opposition finds this PAUTH sufficient: the stale-failure accounting defect is a direct consequence of the WI-5002 dispatcher modernization work, and the repair is a bugfix within the same operational surface. No authorization-scope expansion is needed.

## Specification Compliance

All blocking specs are satisfied:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: Target paths, requirement sufficiency, and spec-derived verification plan are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: Verification plan includes focused tests proving stale health clears and genuine failures still flag.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: The fix preserves the numbered bridge chain and dispatcher-backed state as workflow authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: PAUTH, project, work item, and target paths are present.

## Preflight Results

### Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:88eaf60a4594cb20e680b51446a21be428d399127452b01e24a5e5dd7bd876b2`
- bridge_document_name: `gtkb-wi5002-prime-stale-failure-health`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5002-prime-stale-failure-health-001.md`
- operative_file: `bridge/gtkb-wi5002-prime-stale-failure-health-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

### ADR/DCL Clause Preflight (Slice 2)

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5002-prime-stale-failure-health`
- Operative file: `bridge\gtkb-wi5002-prime-stale-failure-health-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Verification Requirements

Before a VERIFIED verdict can be issued, the implementation must demonstrate:

1. **Stale health clears after unchanged:** A test where a recipient has `failure_class=subprocess_execution_failed` with `pending_count>0`, then the signature matches (unchanged branch), and the health report no longer shows FAIL for that recipient.
2. **Genuine failures still flag:** A test where a recipient has a live `failure_class` from a current failed launch, and the health report correctly shows FAIL.
3. **Unchanged WARN preserved:** The existing `unchanged` WARN finding (idempotent with pending work) must still appear when appropriate.
4. **No regression in verdict_reconciled clearing:** The existing `verdict_reconciled` branch's clearing of `failure_class`/`last_failure_reason` must be unaffected.

## Implementation Notes for Prime Builder

The Loyal Opposition recommends the fix be applied in the `unchanged` branch of `_dispatch_loop_tick` (or equivalent dispatch path) in `scripts/dispatcher_runtime.py`, adding:

```python
recipient_state.pop("failure_class", None)
recipient_state.pop("last_failure_reason", None)
```

alongside the existing `recipient_state["last_result"] = "unchanged"` assignment. This mirrors the clearing already performed in the `verdict_reconciled` branch and ensures the health classification in `bridge_dispatch_config.py` sees no stale failure evidence after the unchanged path is taken.

Alternatively, the health classification in `bridge_dispatch_config.py` could be taught to treat `last_result == "unchanged"` as a signal to ignore stale `failure_class`/`last_failure_reason` fields, but the runtime-side clearing is preferred as it keeps the state canonical and avoids spreading the staleness-detection logic across two modules.
