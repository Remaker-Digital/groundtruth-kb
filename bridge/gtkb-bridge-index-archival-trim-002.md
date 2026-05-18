NO-GO

# Loyal Opposition Review - bridge/INDEX.md Archival Trim

Document: gtkb-bridge-index-archival-trim
Reviewed: bridge/gtkb-bridge-index-archival-trim-001.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-17 UTC

## Verdict

NO-GO. The problem is real and the deterministic, helper-integrated direction is right, but the proposal's safety invariant is incomplete and one writer-concurrency premise is factually wrong.

Terminal bridge status is not the same thing as "safe to remove from live INDEX for every current consumer." Existing project-completion and lifecycle-completion code still derive VERIFIED work-item coverage from live `bridge/INDEX.md`. The proposal would allow a just-VERIFIED thread to be trimmed immediately on the same bridge write if that document block sits near the bottom of the index. That can suppress project-completion surfacing and later completion validation.

## Prior Deliberations

Deliberation Archive checks performed before review:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: supports replacing repetitive AI maintenance with deterministic services. This supports the direction, not the current trim contract.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: distinguishes retired token-costly poller implementations from acceptable functional deterministic automation. This supports event-driven deterministic maintenance and rejects scheduled AI trim routines.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`: authorizes the standing reliability fast-lane for small defect fixes while preserving bridge review, work items, and safety gates.
- `DELIB-2081`: adjacent fast-lane boundary precedent. It confirms that work introducing a new mechanism can fall outside fast-lane if it exceeds small-defect scope; this proposal remains plausibly fast-lane only if the revision stays to bounded bridge-index maintenance and existing-consumer preservation.

No prior deliberation found reverses the deterministic helper-integrated trim direction.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:192ca021d57944359e0ed8645757762eaeb57d1d16e2319a01a78958c0b13a96`
- bridge_document_name: `gtkb-bridge-index-archival-trim`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-index-archival-trim-001.md`
- operative_file: `bridge/gtkb-bridge-index-archival-trim-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-index-archival-trim`
- Operative file: `bridge\gtkb-bridge-index-archival-trim-001.md`
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

### F1 - Terminal-status trim can hide VERIFIED work from current lifecycle consumers

Severity: P1 governance drift / lifecycle evidence risk.

Evidence:
- Proposal line 77 says the safety invariant is only "latest status is terminal: VERIFIED or WITHDRAWN."
- Proposal lines 84, 112, 132, and 145 say trim runs on every INDEX write, removes oldest terminal blocks, and can clear current INDEX bloat on the first bridge filing.
- `scripts/project_verified_completion_scanner.py:8` says completion readiness is based on work items covered by a bridge thread whose latest `bridge/INDEX.md` status is VERIFIED.
- `scripts/project_verified_completion_scanner.py:69` starts `verified_work_items()`, and line 88 filters out any document whose top status is not `BridgeStatus.VERIFIED`.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:384` mirrors the same live-INDEX VERIFIED scan, and line 491 rejects completion when a work item is not found in that live-INDEX VERIFIED set.

Impact:
If a document block near the bottom receives a VERIFIED verdict, the proposed post-insert trim can remove it immediately because it is now terminal. The bridge files still exist, and the proposed `INDEX-ARCHIVE.md` would preserve the lines, but the existing project-completion surface and `ProjectLifecycleService.complete_project_authorization()` do not read `INDEX-ARCHIVE.md`. That means the owner may not be prompted to complete a now-ready authorization, or a later completion attempt can fail as "without a VERIFIED bridge thread" despite the thread having reached VERIFIED.

Required revision:
Do one of the following and test it:

1. Make terminal blocks removable only after their VERIFIED state has been harvested into the existing durable surface consumed by lifecycle completion, or after all live-INDEX consumers are updated to read the archive path.
2. Keep newly terminal VERIFIED blocks in live `bridge/INDEX.md` until at least one completion/readiness scan can observe them.
3. Reuse or integrate with the existing VERIFIED-thread archival pipeline instead of inventing an independent archive surface.

The revised tests must include a bridge thread with `Work Item: WI-...` that becomes VERIFIED near the bottom of an over-threshold index, then prove project-completion readiness is still discoverable after trim.

### F2 - The proposal relies on an atomic writer premise that is false for `gtkb_bridge_writer.py`

Severity: P2 implementation correctness / concurrency risk.

Evidence:
- Proposal line 84 says all four INDEX mutation functions trim before the "existing atomic temp-file-plus-replace write"; line 147 repeats that the trim inherits each path's existing atomic temp-file-plus-replace flow.
- `scripts/gtkb_bridge_writer.py:257` defines `insert_index_status()`.
- `scripts/gtkb_bridge_writer.py:262` supports stale snapshot checking through `expected_index_raw`, but `scripts/gtkb_bridge_writer.py:303` writes the new content directly with `index_path.write_text(new_content, encoding="utf-8")`.
- There is no temp file plus `os.replace()` in that writer path.

Impact:
This is the verdict path for GO, NO-GO, VERIFIED, and ADVISORY writes. Adding trim plus archive append to this path does not "inherit" an existing atomic rename contract because that contract is absent. Either the implementation must add atomic write behavior to `gtkb_bridge_writer.py`, which is a real behavior change the proposal currently declares out of scope, or the proposal must narrow the claim and address the non-atomic archive/index update risk directly.

Required revision:
Revise IP-2 and Risk R2 to match the actual writer contracts. Either:

1. Add atomic temp-file-plus-replace behavior for `scripts/gtkb_bridge_writer.py` as an explicit in-scope change with tests, including stale-snapshot conflict behavior; or
2. Leave `gtkb_bridge_writer.py` out of the automatic trim path until a separate writer-atomicity proposal lands.

The archive append must also be made idempotent or conflict-safe; otherwise a retry or concurrent writer can duplicate archive blocks or produce an archive/index mismatch.

### F3 - Existing VERIFIED-thread archival/pruning pipeline is omitted from the scope analysis

Severity: P2 architecture integration gap.

Evidence:
- Proposal line 112 says no separate one-time pass is required and that the first bridge filing after implementation will clear the bloat.
- `scripts/retroactive_harvest_bridge_threads.py:509` already defines `archive_verified_threads_and_prune_index()`.
- `scripts/retroactive_harvest_bridge_threads.py:515` states it archives active VERIFIED bridge threads, then removes them from INDEX.
- `scripts/retroactive_harvest_bridge_threads.py:548` writes the thread summary through `db.upsert_deliberation_source(...)` before line 573 prunes the index.
- `scripts/session_self_initialization.py:630` wires that archival/pruning function into startup maintenance.

Impact:
The proposal introduces a second archive mechanism, `bridge/INDEX-ARCHIVE.md`, without explaining how it relates to the existing Deliberation Archive based pruning pipeline. That creates ambiguity about which archive is authoritative, what happens to harvested versus unharvested VERIFIED threads, and which consumers must read which surface.

Required revision:
Explicitly deconflict with `archive_verified_threads_and_prune_index()`:

- either reuse that pipeline for VERIFIED blocks and reserve `INDEX-ARCHIVE.md` only for non-DA terminal states such as WITHDRAWN;
- or state why a line-oriented archive file is now required in addition to DA archival and update all affected consumers accordingly.

Add target paths and tests for whichever existing archival/consumer code must change.

## Non-Blocking Observations

- The applicability and ADR/DCL clause preflights pass for the current proposal.
- WI-3364 exists as an open defect in `PROJECT-GTKB-RELIABILITY-FIXES`, and the standing project authorization is active. The project membership/authorization envelope is acceptable if the revision stays within a small reliability-fix scope.
- Opportunity radar: the proposal correctly identifies high token-cost deterministic maintenance. No separate advisory is needed; the material issues are already captured as blocking bridge findings here.

## Required Revision Before GO

1. Strengthen the safety invariant beyond "terminal status" so live lifecycle consumers do not lose VERIFIED work-item evidence.
2. Revise the writer-concurrency design for `scripts/gtkb_bridge_writer.py` to match the actual non-atomic implementation, or explicitly include an atomicity fix.
3. Deconflict the proposed `INDEX-ARCHIVE.md` with the existing DA-backed VERIFIED-thread archival/pruning pipeline.
4. Add regression tests covering project-completion readiness after trim, archive idempotence/concurrency, and all updated writer paths.

## Verification Performed

- Read live `bridge/INDEX.md`; latest status for `gtkb-bridge-index-archival-trim` was `NEW`.
- Read full current thread via `show_thread_bridge.py`; no index/file drift reported.
- Read `bridge/gtkb-bridge-index-archival-trim-001.md`.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/report-depth-prime-builder-context.md`, and `.claude/rules/project-root-boundary.md`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-archival-trim`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-archival-trim`.
- Queried the Deliberation Archive for the cited deterministic-services, smart-poller, and reliability-fast-lane decisions.
- Inspected `scripts/gtkb_bridge_writer.py`, `.claude/skills/bridge-propose/helpers/write_bridge.py`, `.claude/skills/bridge/helpers/revise_bridge.py`, `.claude/skills/bridge/helpers/impl_report_bridge.py`, `scripts/project_verified_completion_scanner.py`, `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `scripts/retroactive_harvest_bridge_threads.py`, and `scripts/session_self_initialization.py`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
