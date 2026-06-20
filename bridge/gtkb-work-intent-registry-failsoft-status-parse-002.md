NO-GO

bridge_kind: lo_verdict
Document: gtkb-work-intent-registry-failsoft-status-parse
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-work-intent-registry-failsoft-status-parse-001.md
Verdict: NO-GO
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4658

# Loyal Opposition Review - Work-Intent Registry Fail-Soft Status Parse

## Verdict Summary

NO-GO.

The proposal correctly identifies the live dispatch failure but selects an unsafe and incomplete repair. It would make the work-intent registry treat the current broken `GO test` file as a valid GO, even though that file contains no substantive Loyal Opposition verdict. It also omits the owner-directed health-finding/quarantine scope recorded in `DELIB-20265221`. Prime should not implement this narrower thread as filed.

## Prior Deliberations

- `DELIB-20265221` - Owner directive: fix bridge-dispatcher live poisoning first via graceful work-intent quarantine plus a health finding, then drive the result to VERIFIED.
- `DELIB-20261120` - Prior bridge dispatch deadlock/contention critique; relevant to the head-of-line-blocking failure mode.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` and `DELIB-20264098` / `DELIB-20264099` - body-status-token/proposal-standards context. These records explain why parser behavior matters, but they do not authorize treating a placeholder `GO test` file as substantive implementation approval.
- `bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md` and `bridge/gtkb-dispatch-malformed-status-token-quarantine-002.md` - overlapping WI-4658 thread with the owner-aligned quarantine plus dispatch-health scope. This NO-GO is intended to converge implementation onto that thread.

Semantic Deliberation Archive search via `python -m groundtruth_kb deliberations search ...` timed out during review, consistent with the current ChromaDB hang risk already tracked in `WI-4568`. I used a deterministic SQLite keyword search over `groundtruth.db.deliberations` as the read fallback and cited the relevant current records above.

## Evidence Reviewed

- Proposal under review: `bridge/gtkb-work-intent-registry-failsoft-status-parse-001.md`.
- Overlapping proposal: `bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md`.
- Owner decision: `DELIB-20265221`.
- Poisoned file: `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md`, full content `GO test`.
- Current parser: `scripts/bridge_work_intent_registry.py::_bridge_file_status`.
- Canonical status helper: `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py::_line_status_token`.
- Bridge compliance gate status recognition: `.claude/hooks/bridge-compliance-gate.py::_first_line_is_recognized_status`.
- Current dispatch health collector: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py::collect_bridge_dispatch_status`.
- Live failure logs: `.gtkb-state/bridge-poller/dispatch-failures.jsonl` and `.gtkb-state/cross-harness-trigger/dispatch-failures.jsonl`.

## Findings

### F1 (P1) - The proposal would convert a broken placeholder into GO authorization

Observation: The proposal says `_bridge_file_status` should parse `GO test` as `GO`. The live file at `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` contains only `GO test`; it has no `bridge_kind`, reviewer metadata, `Responds to`, findings, applicability preflight, clause preflight, or rationale.

Deficiency rationale: A parser can be marker-tolerant without treating a one-line placeholder as a valid implementation-authorization verdict. If this proposal lands as written, the dispatch lane may acquire and launch the `gtkb-wi4232-bridge-index-drift-pb-classification` Prime implementation from a non-substantive malformed verdict file.

Impact: This weakens the bridge's core safety property: Prime implementation starts only after a real Loyal Opposition GO. It risks turning malformed audit debris into executable work.

Recommended action: Do not parse the current `GO test` file as a valid dispatchable GO. Either withdraw this thread in favor of `gtkb-dispatch-malformed-status-token-quarantine`, or revise it to quarantine non-substantive/malformed status-bearing files and preserve the requirement that a dispatchable GO be backed by a real verdict artifact.

### F2 (P1) - The proposal omits the owner-directed health-finding/quarantine scope

Observation: `DELIB-20265221` records the desired fix as graceful work-intent quarantine plus a health finding. This proposal's `target_paths` are only `scripts/bridge_work_intent_registry.py` and `platform_tests/scripts/test_bridge_work_intent_registry.py`. It does not touch `scripts/cross_harness_bridge_trigger.py`, dispatch-state persistence, or `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`.

Deficiency rationale: Fixing the immediate exception is not the same as satisfying the owner decision. The current health problem includes false-green dispatch health and repeated failure evidence in `.gtkb-state`; the proposal would leave that observability gap in place.

Impact: Prime could implement this narrower fix and still leave the dashboard/CLI health story misleading, while the duplicate owner-aligned proposal remains unimplemented.

Recommended action: Use the approved `gtkb-dispatch-malformed-status-token-quarantine` scope, or revise this proposal to include dispatch-state quarantine evidence plus `collect_bridge_dispatch_status` warning behavior and tests.

### F3 (P2) - Owner-input evidence is not specific enough for the claimed alternate scope

Observation: The proposal's `Owner Decisions / Input` section says the owner selected "Fix work-intent registry (fail-soft)" via AskUserQuestion, but it does not cite an AUQ ID, DECISION ID, or DELIB ID for that exact alternate scope. The current DA fallback search surfaced `DELIB-20265221`, whose summary is broader and different: "graceful work-intent quarantine + health finding."

Deficiency rationale: When a proposal depends on owner approval, the bridge protocol requires a substantive `Owner Decisions / Input` section enumerating the relevant evidence. This proposal's evidence is not precise enough to override the captured `DELIB-20265221` scope.

Impact: The review cannot safely treat the narrower two-file implementation as owner-authorized when the durable owner decision points to a broader quarantine/health repair.

Recommended action: If Prime wants to keep this narrower direction, revise with exact owner-decision evidence and explain why it supersedes `DELIB-20265221`. Otherwise retire/withdraw this duplicate and proceed under the GO'd quarantine/health proposal.

## Applicability Preflight

- packet_hash: `sha256:4c7ed88f1430057a684fbfd33a15e2d602dc18c1160e7df53b701078568f1943`
- bridge_document_name: `gtkb-work-intent-registry-failsoft-status-parse`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-work-intent-registry-failsoft-status-parse-001.md`
- operative_file: `bridge/gtkb-work-intent-registry-failsoft-status-parse-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-work-intent-registry-failsoft-status-parse`
- Operative file: `bridge\gtkb-work-intent-registry-failsoft-status-parse-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prime Builder Context

Recommended path: implement `bridge/gtkb-dispatch-malformed-status-token-quarantine-002.md` instead. If this narrower proposal is kept, revise it so it cannot treat `GO test` as a substantive GO and so it satisfies the `DELIB-20265221` health-finding requirement.

