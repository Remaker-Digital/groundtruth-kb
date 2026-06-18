GO

bridge_kind: lo_verdict
Document: gtkb-dispatch-malformed-status-token-quarantine
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md
Verdict: GO
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4658-DISPATCH-MALFORMED-STATUS-TOKEN-GRACEFUL-QUARANTINE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4658

# Loyal Opposition Review - Malformed Status Token Quarantine

## Verdict Summary

GO.

The proposal is approved for Prime Builder implementation. It satisfies the mandatory specification-linkage, project-linkage, owner-decision, root-boundary, applicability-preflight, and clause-preflight gates. The live failure evidence supports the selected design: a single malformed status-bearing bridge file currently causes Prime dispatch work-intent acquisition to fail repeatedly, and the proposed fix quarantines that defective thread while preserving dispatch for other selected work and surfacing the condition in dispatch health.

## Prior Deliberations

- `DELIB-20265221` - Owner directive: fix the bridge-dispatcher live poisoning first. The recorded decision specifically calls for graceful work-intent quarantine plus a health finding and asks that the fix be driven to VERIFIED.
- `DELIB-20261120` - Prior Loyal Opposition bridge dispatch deadlock/contention critique. Relevant because this proposal removes one current head-of-line blocking mode in the dispatch lane.
- `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-001.md` and `bridge/gtkb-bridge-dispatcher-canonical-verdict-repair-002.md` - sibling thread for orphan `.lo-verdict.md` reconciliation. This GO is limited to the separate malformed numbered-file status-token failure.
- `bridge/gtkb-work-intent-registry-failsoft-status-parse-001.md` - overlapping WI-4658 proposal reviewed separately. It is not the approved scope because it would treat the broken `GO test` file as a valid GO while omitting the owner-directed health-finding surface.

Semantic Deliberation Archive search via `python -m groundtruth_kb deliberations search ...` timed out during review, consistent with the current ChromaDB hang risk already tracked in `WI-4568`. I used a deterministic SQLite keyword search over `groundtruth.db.deliberations` as the read fallback and cited the relevant current records above.

## Evidence Reviewed

- Bridge thread: `bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md`.
- Poisoned bridge file: `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md`, whose full body is only `GO test`; it is not a substantive Loyal Opposition verdict.
- Prior proposal in the poisoned thread: `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-001.md`.
- Current parser site: `scripts/bridge_work_intent_registry.py::_bridge_file_status`, which uses `BRIDGE_FILE_STATUS_RE.fullmatch(...)` and raises `WorkIntentRegistryError` on `GO test`.
- Current batch-acquire behavior: `scripts/cross_harness_bridge_trigger.py::_acquire_prime_work_intent_batch`, which releases the batch and returns `ok: False` when one selected slug fails acquisition.
- Current health surface: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py::collect_bridge_dispatch_status`, which reports topology and eligibility findings but does not currently surface the recorded malformed-status dispatch failures.
- Live failure evidence: `.gtkb-state/bridge-poller/dispatch-failures.jsonl` and `.gtkb-state/cross-harness-trigger/dispatch-failures.jsonl` contain repeated `work_intent_acquire_failed` records for `gtkb-wi4232-bridge-index-drift-pb-classification` with `error_message` citing `GO test`.
- Backlog check: `gt backlog list --project PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` shows adjacent open bridge-reliability work, but none supersedes this immediate WI-4658 poison fix.

## Review Findings

No blocking findings.

### Confirmation C1 - Scope Matches Owner Decision

Observation: `DELIB-20265221` records the owner-directed fix as graceful work-intent quarantine plus a dispatch-health finding. The proposal includes both surfaces in target paths: `scripts/bridge_work_intent_registry.py`, `scripts/cross_harness_bridge_trigger.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, and matching tests.

Impact: This keeps the implementation aligned with the durable owner decision instead of only fixing the immediate parser exception.

Recommended action: Implement the proposal as written. The implementation report must prove the quarantined thread no longer blocks unrelated Prime dispatch and that `gt bridge dispatch health` or `collect_bridge_dispatch_status` surfaces a warning while quarantine evidence exists.

### Confirmation C2 - Does Not Treat Placeholder `GO test` As Implementation Authorization

Observation: `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` contains only `GO test`. The file has no `bridge_kind`, no reviewer metadata, no reviewed proposal reference, no findings, and no verdict rationale.

Impact: Treating that file as a valid GO would create implementation authority from a placeholder/broken verdict. Quarantining it is the safer behavior until the original thread is repaired through a proper bridge verdict or reconciliation action.

Recommended action: Preserve the append-only file and quarantine it as drift. Do not rewrite or delete `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` in this WI-4658 implementation.

### Confirmation C3 - Verification Plan Is Spec-Derived

Observation: The proposal maps the linked specs to focused tests for typed malformed-status errors, batch quarantine-and-continue behavior, preservation of non-malformed error semantics, and dispatch-health warning output.

Impact: The verification plan is sufficient for `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` at proposal time.

Recommended action: The implementation report must include exact pytest, ruff check, ruff format, applicability-preflight, and clause-preflight outputs. If Python files change, both lint and format checks must be reported separately.

## Applicability Preflight

- packet_hash: `sha256:ba06ddfdfd988f41e0bcc39c88f8c442db16760f5cd48fead0963cfb169d7174`
- bridge_document_name: `gtkb-dispatch-malformed-status-token-quarantine`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md`
- operative_file: `bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-dispatch-malformed-status-token-quarantine`
- Operative file: `bridge\gtkb-dispatch-malformed-status-token-quarantine-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Required Implementation Evidence

Prime Builder should file a post-implementation report carrying forward this GO and showing:

- focused pytest results for `platform_tests/scripts/test_bridge_work_intent_registry.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, and `platform_tests/scripts/test_bridge_dispatch_config.py`;
- separate `ruff check` and `ruff format --check` results for every changed Python file;
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-malformed-status-token-quarantine`;
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-malformed-status-token-quarantine`;
- evidence that the broken `GO test` thread is recorded as quarantined and does not prevent remaining eligible Prime work from being selected/acquired;
- evidence that dispatch health reports a warning while malformed-status quarantine evidence is present.

## Residual Risk

The touched surfaces are load-bearing dispatch and work-intent code. The implementation must keep non-malformed `WorkIntentRegistryError` and normal lease/contention semantics unchanged. Any expansion beyond the six declared target paths requires a revised bridge proposal.

