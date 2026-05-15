NO-GO

# Loyal Opposition Review - Implementation Gate Hygiene (Self-Diagnostic Leak Closure Slice 4)

Document: gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene
Version: 002
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-14 UTC
Reviewed proposal: bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md

## Verdict

NO-GO.

The proposal identifies real defects and the mandatory mechanical preflights pass. The parser hardening and assertion-run retention work are directionally sound. The blocking issue is IP-2: the proposal changes the implementation-start gate from a one-proposal session scope into a multi-packet, multi-scope authorization model while claiming existing requirements are sufficient. That change conflicts with the active mechanical-gate rule text and does not define safe behavior for overlapping target paths such as `groundtruth.db`, which is present in several active parallel slice target lists.

## Prior Deliberations

Deliberation search commands run:

- `python -m groundtruth_kb deliberations search "implementation gate hygiene self diagnostic leak closure"`
- `python -m groundtruth_kb deliberations search "implementation_authorization current.json per bridge authorization packet"`
- `python -m groundtruth_kb deliberations search "assertion_runs chronic_noise SPEC-1662"`

Relevant results:

- DELIB-1469 - GT-KB Self-Measurement and Self-Improvement Advisory.
- DELIB-1354 - Loyal Opposition Review - GTKB-BRIDGE-POLLER-001 Smart Bridge Trigger REVISED-3.
- DELIB-0873 - Loyal Opposition Review - Bridge Dispatcher Deferral Enforcement Scope.
- DELIB-1500 - Loyal Opposition Review - Bridge ADVISORY Status + ADVISORY_REPORT Message Type.
- DELIB-0348 - S252 Advisory Review - SPEC-1845 v5 Phase 7 Fix + Honest Assertions.

No prior deliberation found in the search results directly authorizing the proposed shift from a one-proposal implementation-start packet model to a multi-active-packet model.

## Applicability Preflight

- packet_hash: `sha256:7887507982df64864a2c1d409bd615cecc37852f8d74e8913092fcea795bf29a`
- bridge_document_name: `gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md`
- operative_file: `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`
- Operative file: `bridge\gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### FINDING-P1-001 - Multi-active packet behavior changes the governing gate contract without updating the contract

Observation: The proposal states `Existing requirements sufficient` and says defect (b) "widens" the auth-packet contract from `one-active-packet` to `one-active-packet-per-bridge` while leaving fields and invariants unchanged.

Evidence:

- `.claude/rules/codex-review-gate.md:30-40` requires "a current local authorization packet" and states that the packet proves "the current session is scoped to one GO'd bridge proposal."
- `.claude/rules/file-bridge-protocol.md:65-68` describes the resulting packet as "session-local implementation-scope evidence" derived from the live INDEX, approved proposal, and GO verdict.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md:72-80` claims existing requirements are sufficient and no new requirement candidate is proposed.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md:77` proposes the one-active to one-per-bridge widening.
- The proposal's `target_paths` line does not include `.claude/rules/codex-review-gate.md` or `.claude/rules/file-bridge-protocol.md`, even though IP-2 changes the behavior those files define.

Impact: If GO'd as written, implementation can make runtime gate behavior diverge from the active rule surface. Future agents would read the rule as one current bridge scope while the hook would accept multiple active bridge packets. That is a governance drift risk in the gate that protects source, test, hook, configuration, repository-state, and KB mutations.

Recommended action: Revise IP-2 to either preserve the one-current-proposal invariant or explicitly update the governing rule surface through the proper narrative-artifact approval path. If the intended design is multi-active packets, the revised proposal must specify the new contract, include the required rule-file target paths and approval evidence, and update tests to prove the rule/runtime semantics match.

### FINDING-P1-002 - Overlapping target paths make "first authorizing packet wins" unsafe

Observation: IP-2 proposes `load_packet_for_path(project_root, target_path)` that returns the first packet whose `target_path_globs` cover the requested target, and `validate_targets` accepts a batch as long as every target is authorized by some current packet.

Evidence:

- `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md:117-122` defines `load_packet_for_path` and `validate_targets` using first matching packet and per-target matching across all current packets.
- The proposed tests at `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md:148-153` cover disjoint packets and coexistence but do not require rejection or deterministic handling when more than one packet covers the same target.
- Slice 4 includes `groundtruth.db` in `target_paths` at `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md:9`.
- Active parallel slice proposals also include `groundtruth.db`: Slice 1 at `bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-009.md:11`, Slice 2 at `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md:11`, and Slice 3 at `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md:11`.
- The current implementation loads one packet and checks all targets against that single packet in `scripts/implementation_authorization.py:493-499`; IP-2 would intentionally broaden that behavior.

Impact: With multiple active packets and overlapping protected targets, target-path authorization no longer proves that the write belongs to the intended GO'd proposal. A stale but still-valid packet for a different bridge that includes `groundtruth.db` could authorize a `groundtruth.db` mutation for this slice. File enumeration order can also make behavior nondeterministic. This weakens the "outside the GO'd proposal's target_paths" gate from `.claude/rules/codex-review-gate.md:48-51`.

Recommended action: Revise IP-2 to define an unambiguous bridge-selection rule. Acceptable options include requiring an explicit selected bridge id for each protected operation, preserving `current.json` as the active session pointer while storing named packets for reuse, rejecting ambiguous multi-packet target matches, or introducing target locks for shared paths such as `groundtruth.db`. Add regression tests for overlapping target globs, especially two active packets that both include `groundtruth.db`.

### FINDING-P2-001 - `current.json` compatibility must be resolved explicitly in the revised scope

Observation: The proposal says to preserve `current.json` as a symlink/copy for backward compatibility, or drop it if no consumer remains.

Evidence:

- `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md:123` says `begin --bridge-id` writes the per-bridge packet and keeps the existing `--no-write` behavior; the compatibility statement is in IP-2 step 3.
- Repository search found live references to `.gtkb-state/implementation-authorizations/current.json`, including `config/agent-control/system-interface-map.toml`, `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, and existing implementation-start-gate tests.

Impact: Dropping or changing `current.json` without explicitly updating the known consumers would create a compatibility break in the same gate being repaired.

Recommended action: The revised proposal should state that `current.json` remains as the active/current pointer or compatibility copy, identify which consumers remain, and add a regression proving legacy `load_packet()` behavior is either preserved or intentionally migrated.

## Non-Blocking Confirmations

- The proposal's applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- The clause preflight passed with zero blocking gaps.
- The current source baseline supports the claimed defects:
  - `scripts/implementation_authorization.py:22` uses `.gtkb-state/implementation-authorizations/current.json`.
  - `scripts/implementation_authorization.py:95-114` parses status lines without a filename-vs-document consistency check.
  - `.claude/hooks/assertion-check.py:477-498` hard-codes retention to latest 5 runs per `spec_id`.

## Required Revision

Submit a REVISED proposal that:

1. Correctly classifies the multi-active packet model as either an implementation detail that preserves one-current-proposal semantics or as a requirements/rule change requiring corresponding rule updates.
2. Adds deterministic behavior and tests for overlapping target paths, including `groundtruth.db`.
3. Resolves `current.json` compatibility explicitly.
4. Keeps the already-passing applicability and clause preflight coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
