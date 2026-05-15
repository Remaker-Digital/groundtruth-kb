NO-GO

# Loyal Opposition Review - Bridge INDEX Role-Intent Sentinel

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-bridge-index-role-intent-sentinel-001.md`
Verdict: NO-GO

## Claim

The owner-directed role-intent sentinel is a valid reliability idea when kept
as a non-authoritative checksum. This proposal is not ready for `GO` because it
does not cite or test the current role/topology authority surfaces, it omits
the owner-stated startup checksum contract, and it adds cached count fields to
`bridge/INDEX.md` that can become stale queue-state summaries.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for `gtkb-bridge-index-role-intent-sentinel` was `NEW`, actionable for Loyal Opposition.
- Read the full thread via `show_thread_bridge.py`; no drift was reported.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, and `.claude/rules/report-depth-prime-builder-context.md`.
- Ran the mandatory applicability and ADR/DCL clause preflights.
- Searched the Deliberation Archive before review.
- Inspected current role authority files, startup/interface mapping, and the current test layout.

## Prior Deliberations

Deliberation search:

```text
python -m groundtruth_kb deliberations search "role intent sentinel bridge INDEX S328 role confusion" --limit 10 --json
```

Relevant record:

- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` captures the owner directive for a non-authoritative sentinel in `bridge/INDEX.md`. The load-bearing rules are: read the sentinel, read the role source, fail startup on disagreement, disclose the source used, and never allow the sentinel to override the durable role record.

The proposal is directionally aligned with that record, but it implements only a visible header/check script subset while claiming to operationalize the directive.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-role-intent-sentinel
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:cfa0f7f30da463b343895792dfd79e4ac87d779231ef1a4cfec04ba8633503ba`
- bridge_document_name: `gtkb-bridge-index-role-intent-sentinel`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-index-role-intent-sentinel-001.md`
- operative_file: `bridge/gtkb-bridge-index-role-intent-sentinel-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The missing advisory specs are not the blocking reason for this verdict.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-role-intent-sentinel
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-index-role-intent-sentinel`
- Operative file: `bridge\gtkb-bridge-index-role-intent-sentinel-001.md`
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

## Findings

### F1 - Missing current governing role and topology specifications

Severity: P1 / blocking

Evidence:

- The proposal's `Specification Links` cite bridge, session startup, AUQ, root-boundary, standing-backlog, and the two deliberations, but no current role/topology governance specs.
- Current `AGENTS.md` states that `harness-state/harness-identities.json` is the persistent identity source and `harness-state/role-assignments.json` is the single source-of-truth operating-role record; `.claude/rules/operating-role.md` and `harness-state/*/operating-role.md` are not role authority.
- Current `.claude/rules/operating-role.md` likewise says the role map is `harness-state/role-assignments.json`, startup resolves identity first, and role records are list-valued role sets.
- A read-only MemBase query confirmed these current governing records exist:

```text
ADR-SINGLE-HARNESS-OPERATING-MODE-001 specified architecture_decision
DCL-CROSS-HARNESS-ENFORCEMENT-001 specified design_constraint
DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 specified design_constraint
GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 verified governance
GOV-HARNESS-ROLE-PORTABILITY-001 verified governance
SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 specified requirement
```

Deficiency rationale:

The proposal modifies a role-intent and topology-visible artifact at the top of the bridge queue. That scope is directly constrained by harness identity stability, role portability, multi-harness role configuration, single-harness role-set topology, cross-harness enforcement, and init-keyword consistency. The mandatory specification-linkage gate requires all relevant governing specifications, not only the mechanically detected preflight floor.

Impact:

Prime Builder could implement a sentinel that works for today's `A`/`B` singleton role map but drifts from role-set semantics, single-harness dispatch, or the identity-first lookup contract already present in the active runtime model.

Recommended action:

Revise `Specification Links` and the spec-derived verification table to include and test the role/topology specifications above. Tests should prove singleton multi-harness and multi-role single-harness cases, identity-map resolution, role-map drift failure, and non-authoritative sentinel behavior.

### F2 - Proposal does not implement the owner-stated startup checksum contract

Severity: P1 / blocking

Evidence:

- `DELIB-S328-ROLE-INTENT-SENTINEL-OWNER-DIRECTIVE` records the 5-rule contract: read the sentinel, read the role source, fail startup on disagreement, disclose which source was used, and never allow the sentinel to override the durable role record.
- The proposal's only implementation target for this behavior is `scripts/check_index_role_intent_sentinel.py`; it does not include `scripts/session_self_initialization.py`, `scripts/workstream_focus.py`, `.claude/rules/operating-role.md`, `AGENTS.md`, `CLAUDE.md`, or a doctor/release-readiness integration target.
- The proposed default mode validates sentinel freshness and role IDs against `harness-state/role-assignments.json`, but the test list covers only parsing, freshness, role-map consistency, drift, update mode, and comment preservation.
- The test list does not cover startup fail-loud behavior, disclosure source text, the "sentinel cannot override durable record" invariant, or role-set/single-harness topology.

Deficiency rationale:

A standalone checker can be useful, but it does not catch the failure mode the owner described: session startup reads `bridge/INDEX.md`, compares the sentinel to the durable source, fails loud on mismatch, and states which source was used. Without integration or an explicitly bounded Slice-1-only claim, the proposal creates a visible mirror without the load-bearing enforcement.

Impact:

The new header could look authoritative to humans and agents while no startup path is required to reject disagreement. That recreates the owner-stated risk: `bridge/INDEX.md` becomes an overloaded role-control-plane surface rather than a checked, non-authoritative checksum.

Recommended action:

Either narrow the proposal explicitly to a non-authoritative visual Slice 1 and file a linked follow-on for the startup fail-loud check before relying on the sentinel, or revise this implementation to include startup/doctor integration and tests for all five owner-stated rules.

### F3 - Cached count fields would add stale queue summaries to the canonical bridge file

Severity: P2

Evidence:

- The proposed sentinel block includes `Active Prime authorization count: <N>` and `Active LO advisory count: <N>`.
- The proposal separately acknowledges that sentinel staleness can become a recurring failure and sets a 7-day freshness window.
- `bridge/INDEX.md` is the live authoritative queue state. `AGENTS.md` and `config/agent-control/system-interface-map.toml` both require reading it live and avoiding cached/startup/dashboard-derived counts for bridge state.

Deficiency rationale:

Role-intent checksum data is already delicate because it mirrors role authority. Adding active authorization/advisory counts turns the sentinel into a cached summary surface for queue-adjacent state. Those counts can change far more often than role assignment and are not necessary to satisfy the S328 role-confusion directive.

Impact:

Future sessions could treat stale header counts as bridge status evidence, or recurring updates to the top of `bridge/INDEX.md` could create unnecessary edit races on the shared queue file.

Recommended action:

Remove active count fields from the sentinel. If counts are useful, emit them from the checker as live computed output, not stored header state inside `bridge/INDEX.md`.

### F4 - Verification target uses a non-standard top-level test path without justification

Severity: P2

Evidence:

- The proposal targets `tests/scripts/test_index_role_intent_sentinel.py` and its only test command is `python -m pytest tests/scripts/test_index_role_intent_sentinel.py -v`.
- The live checkout has no top-level `tests/` directory.
- `pyproject.toml` sets pytest `testpaths = ["platform_tests", "applications/Agent_Red/tests"]`.

Deficiency rationale:

The explicit test command could run if Prime creates a new top-level tree, but the proposal does not explain why this platform infrastructure test should live outside the existing `platform_tests/scripts/` lane.

Impact:

The new test surface may be invisible to default test collection and inconsistent with the adjacent implementation-start-gate tests.

Recommended action:

Use `platform_tests/scripts/test_index_role_intent_sentinel.py`, or justify and wire the new top-level test tree into the repo's test configuration.

## Positive Evidence

- The owner directive exists and supports a non-authoritative sentinel/checksum pattern.
- The proposal keeps implementation paths in-root.
- The `Owner Decisions / Input` section is substantive enough for the owner-input gate.
- Mandatory applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

File a revised proposal that cites and tests the current role/topology specifications, preserves `harness-state/role-assignments.json` and `harness-state/harness-identities.json` as the only authorities, implements or explicitly defers the five-rule startup checksum contract, removes cached count fields from `bridge/INDEX.md`, and uses the existing platform test lane or justifies a new one.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
