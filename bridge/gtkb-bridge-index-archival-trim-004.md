NO-GO

# Loyal Opposition Review - bridge/INDEX.md Archival Trim Revision

Document: gtkb-bridge-index-archival-trim
Reviewed: bridge/gtkb-bridge-index-archival-trim-003.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-18 UTC

## Verdict

NO-GO. The revised direction is closer: dropping `bridge/INDEX-ARCHIVE.md` and reusing the existing Deliberation Archive backed VERIFIED-thread archival pipeline resolves the duplicate-archive concern from `-002`.

Two blockers remain. First, the `exclude_threads` guard protects only the bridge thread being written; it does not protect already-VERIFIED work-item evidence for active project authorizations awaiting owner completion confirmation. Second, the reused archival pipeline currently writes GT-KB bridge-thread deliberations with hard-coded Agent Red origin metadata. Making that pipeline run on every bridge write would amplify existing misclassification.

## Prior Deliberations

Deliberation checks performed before review:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` resolved via `KnowledgeDB.get_deliberation()`: supports moving repetitive mechanical work into deterministic services.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` resolved via `KnowledgeDB.get_deliberation()`: supports deterministic event-driven maintenance and does not support scheduled AI churn.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` resolved via `KnowledgeDB.get_deliberation()`: supports the standing reliability fast-lane when the proposal remains a small defect fix.
- Keyword searches for this exact archival-trim topic returned no additional relevant Deliberation Archive rows beyond the thread and cited decisions above.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:1834d9a7271c4047da3f237039b580e355d64abddbb38cf33bfaafffaaf087cc`
- bridge_document_name: `gtkb-bridge-index-archival-trim`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-index-archival-trim-003.md`
- operative_file: `bridge/gtkb-bridge-index-archival-trim-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-index-archival-trim`
- Operative file: `bridge\gtkb-bridge-index-archival-trim-003.md`
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

### F1 - Event-driven pruning can still erase VERIFIED evidence before active authorization completion

Severity: P1 governance drift / lifecycle evidence risk.

Observation:
The revision adds `exclude_threads` so a bridge write does not prune the thread it just wrote. That closes the zero-observation window for a just-VERIFIED current thread, but it does not protect already-VERIFIED threads that are still needed by active project authorizations awaiting owner completion confirmation.

Evidence:
- `bridge/gtkb-bridge-index-archival-trim-003.md` says IP-1 excludes only the current thread from `archive_verified_threads_and_prune_index()`.
- `bridge/gtkb-bridge-index-archival-trim-003.md` says IP-3 invokes the archive-and-prune entry point after all four bridge-write paths.
- `scripts/project_verified_completion_scanner.py:69-95` derives verified work items only from live `bridge/INDEX.md` documents whose top status is `VERIFIED`.
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py:486-491` re-runs the same live-INDEX verified-work-item check during `complete_project_authorization()` and rejects unverified work items.
- Live MemBase currently has active authorization `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HOOK-IMPORT-LATENCY` with `included_work_item_ids = ["WI-3319"]`.
- Live `bridge/INDEX.md` currently has `gtkb-hook-import-latency-chromadb-lazy` latest `VERIFIED`, and `verified_work_items(Path("."))` currently includes `WI-3319`.

Deficiency rationale:
The proposal makes pruning run on unrelated later bridge writes. On such a later write, `exclude_threads` protects only that later thread, not `gtkb-hook-import-latency-chromadb-lazy` or any other already-VERIFIED thread tied to an active authorization. If the event-driven prune removes that VERIFIED block before the owner confirms completion, `complete_project_authorization()` can fail because its live-INDEX check no longer sees `WI-3319`, even though the implementation was VERIFIED and archived.

Impact:
This turns INDEX bloat cleanup into a lifecycle-completion race. It can suppress owner completion workflows or make a valid owner-confirmed completion fail after the bridge evidence has been pruned from the only surface the completion service reads.

Required revision:
Make pruning preserve VERIFIED work-item evidence until lifecycle completion no longer depends on live INDEX. Any one of these designs is acceptable if tested:

1. Update both completion readers (`project_verified_completion_scanner.py` and `ProjectLifecycleService._verified_work_items`) to read VERIFIED coverage from the Deliberation Archive as well as live INDEX before event-driven pruning can run.
2. Teach `archive_verified_threads_and_prune_index()` to skip VERIFIED threads whose `Work Item:` metadata is included in an active project authorization that is not completed.
3. Add a durable completion-readiness/evidence table or record consumed by `complete_project_authorization()`, and prune only after that surface is populated.

Regression tests must include an active authorization with an included work item whose bridge thread is already VERIFIED, then run the event-driven prune from an unrelated `current_thread` and prove completion readiness still survives.

### F2 - Reused archival pipeline hard-codes Agent Red origin metadata for GT-KB bridge threads

Severity: P1 governance drift / knowledge-base classification error.

Observation:
The revision makes `archive_verified_threads_and_prune_index()` the event-driven archive path for GT-KB bridge threads, but that function currently upserts Deliberation Archive rows with hard-coded Agent Red origin metadata.

Evidence:
- `scripts/retroactive_harvest_bridge_threads.py:548-557` calls `db.upsert_deliberation_source(...)` with `origin_project="agent-red"` and `origin_repo="Remaker-Digital/agent-red-customer-engagement"`.
- The same hard-coded Agent Red metadata appears elsewhere in the script (`scripts/retroactive_harvest_bridge_threads.py:494-495` and `:681-682`).
- `.claude/rules/project-root-boundary.md` states Agent Red is a separate project and Agent Red artifacts must not be treated as live GT-KB artifacts.
- `.claude/rules/operating-model.md` distinguishes GT-KB as the platform from Agent Red as an application/adopter.
- The proposal target is GT-KB infrastructure (`bridge/INDEX.md`, bridge helpers, `groundtruth.db` Deliberation Archive rows), not Agent Red.

Deficiency rationale:
Reusing this pipeline without correcting origin metadata would archive GT-KB bridge history as Agent Red history. That contaminates the Deliberation Archive classification surface and downstream inventory/rehearsal split logic that uses `origin_project` as a classification signal.

Impact:
The first event-driven archival run is expected to process a large backlog of VERIFIED GT-KB bridge threads. If they are written with Agent Red origin metadata, the cleanup would trade token-cost bloat for durable knowledge-base misclassification.

Required revision:
Include origin metadata correction in scope for `scripts/retroactive_harvest_bridge_threads.py`. The implementation should derive or parameterize the archive origin for GT-KB bridge maintenance and add tests proving GT-KB bridge-thread archive rows are not written with Agent Red origin metadata. A reasonable expected value is `origin_project="groundtruth-kb"` with an appropriate GT-KB repo identifier, or an explicit null/unknown policy if no canonical repo value exists.

## Non-Blocking Observations

- The applicability preflight and ADR/DCL clause preflight both pass for `-003`.
- WI-3364 exists with `origin = defect`, and active membership `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3364` links it to `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers reliability fast-lane work by active project membership.
- Opportunity radar: the deterministic trigger is a good direction, but the material opportunity is now the deterministic lifecycle-safe pruning contract described in F1. No separate advisory is needed because it is blocking in this thread.

## Required Revision Before GO

1. Preserve completion-readiness evidence for VERIFIED work items tied to active project authorizations before event-driven pruning removes their live INDEX blocks.
2. Correct the Deliberation Archive origin metadata emitted by the reused archival pipeline for GT-KB bridge-thread archive rows.
3. Add regression tests for both conditions, including an unrelated bridge write that triggers pruning while an active project authorization is awaiting owner completion confirmation.

## Verification Performed

- Read live `bridge/INDEX.md`; latest status for `gtkb-bridge-index-archival-trim` was `REVISED`.
- Read the full thread via `show_thread_bridge.py`; no index/file drift reported.
- Read `bridge/gtkb-bridge-index-archival-trim-002.md` and `bridge/gtkb-bridge-index-archival-trim-003.md`.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/report-depth-prime-builder-context.md`, and `.claude/rules/project-root-boundary.md`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-archival-trim`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-archival-trim`.
- Queried the Deliberation Archive by exact IDs for `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, and `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.
- Inspected `scripts/retroactive_harvest_bridge_threads.py`, `scripts/session_self_initialization.py`, `scripts/project_verified_completion_scanner.py`, `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `scripts/gtkb_bridge_writer.py`, and the three bridge helper writer paths.
- Queried MemBase directly for `WI-3364`, `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HOOK-IMPORT-LATENCY`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
