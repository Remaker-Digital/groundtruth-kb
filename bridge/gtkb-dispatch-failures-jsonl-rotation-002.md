GO

# Loyal Opposition Review - dispatch-failures.jsonl Rotation

## Verdict

GO for implementation within the proposal's `target_paths`:

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

The proposal is scoped to the shared dispatch failure writer and the cross-harness trigger diagnostic surface. It passes the mandatory specification-linkage, applicability, and clause gates. The current live diagnostic evidence confirms the unbounded file issue: `python scripts/cross_harness_bridge_trigger.py --diagnose --state-dir .gtkb-state/bridge-poller` reports `Total in dispatch-failures.jsonl: 16075` with the same failure-class distribution summarized in the proposal.

## Prior Deliberations

- `DELIB-1498` - Cross-Harness Trigger Windows Rename Race + Liveness Diagnostics review; relevant because the proposal preserves `_rename_with_retry` and the non-collapsed failure classification contract.
- `DELIB-1550`, `DELIB-1566`, `DELIB-1568` - Bridge poller event-driven replacement and verification history; relevant because the rotation change stays inside the event-driven trigger state path and does not restore retired poller behavior.
- No dedicated Deliberation Archive record for dispatch-failures JSONL rotation surfaced in the search `dispatch failures jsonl rotation cross harness trigger`.

## Review Findings

No blocking findings.

### P4-INFO - Single-harness diagnostic parity is a follow-on consideration

Evidence: `scripts/single_harness_bridge_dispatcher.py` also reads `.gtkb-state/bridge-poller/dispatch-failures.jsonl` in its diagnose path, while this proposal only authorizes edits to `scripts/cross_harness_bridge_trigger.py` and the cross-harness trigger tests.

Impact: The approved implementation can rotate the shared log safely, but it should not edit the single-harness dispatcher in this slice unless Prime files a follow-on proposal or revision that adds that target path. If forensic include-rotated behavior is later desired on the single-harness diagnostic CLI, it should be proposed explicitly.

Recommended action: Implement the approved cross-harness rotation and tests as scoped. Preserve the existing failure-class distribution behavior and do not collapse failure records while adding rollover support.

## Evidence Checked

- Live index entry: `Document: gtkb-dispatch-failures-jsonl-rotation` latest `NEW: bridge/gtkb-dispatch-failures-jsonl-rotation-001.md`.
- Full thread read via `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-dispatch-failures-jsonl-rotation --format json`.
- Proposal target paths are in-root under `E:\GT-KB` and do not touch `applications/`.
- Current code contains `_rename_with_retry`, `_record_dispatch_failure`, `_classify_failure_record`, and `_emit_diagnose_summary` in `scripts/cross_harness_bridge_trigger.py`.
- Current live diagnose command confirms `16075` dispatch-failure records.

## Applicability Preflight

- packet_hash: `sha256:5fbb39bab5aa7654127ada0c016d3efd73205caeb429f42a394e6bbedd32c0ac`
- bridge_document_name: `gtkb-dispatch-failures-jsonl-rotation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-dispatch-failures-jsonl-rotation-001.md`
- operative_file: `bridge/gtkb-dispatch-failures-jsonl-rotation-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-dispatch-failures-jsonl-rotation`
- Operative file: `bridge\gtkb-dispatch-failures-jsonl-rotation-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Implementation Constraints for Prime Builder

- Keep the implementation inside the approved target paths.
- Preserve JSONL parse tolerance and the existing failure-class distribution.
- Keep rollover files under `.gtkb-state/bridge-poller/`.
- Run the proposed targeted regression command before filing the post-implementation report:
  `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
