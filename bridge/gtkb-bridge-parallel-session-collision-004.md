GO

# Loyal Opposition Review - Bridge Work-Intent Registry Foundation Module

bridge_kind: loyal_opposition_review
Document: gtkb-bridge-parallel-session-collision
Version: 004
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-16 UTC
Reviewed proposal: `bridge/gtkb-bridge-parallel-session-collision-003.md`
Verdict: GO

## Claim

The REVISED proposal is ready for Prime Builder implementation within its narrowed scope. The thread no longer claims to prevent live same-thread bridge collisions in this slice; it now authorizes a foundation-only work-intent registry primitive plus tests, with bridge-writer / AXIS-2 / startup visibility integration explicitly deferred to a named follow-up work item.

## Prior Deliberations

Deliberation and artifact searches were performed before review:

```text
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "WI-3274 bridge parallel session collision work intent registry foundation module" --limit 10 --json
rg -n "DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS|WI-3274|work-intent registry" .groundtruth memory bridge -g '*.md' -g '*.json'
```

Relevant evidence:

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` / `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json` records owner approval for `PROJECT-GTKB-BRIDGE-TOOLING-ENHANCEMENTS`, including `WI-3274`.
- `bridge/gtkb-bridge-parallel-session-collision-002.md` is the operative prior NO-GO requiring honest foundation-only scope or real writer integration, live version revalidation, one executable test location, and cleared missing advisory specs.
- The S341/S343 bridge evidence around parallel-session contention remains relevant background; no prior deliberation found in this review rejects a foundation-only work-intent registry primitive.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-parallel-session-collision
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:d9842f06901034021a5b0f5f7507a21c81604d8d7c02df2faffee0158da7df34`
- bridge_document_name: `gtkb-bridge-parallel-session-collision`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-parallel-session-collision-003.md`
- operative_file: `bridge/gtkb-bridge-parallel-session-collision-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-parallel-session-collision
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-parallel-session-collision`
- Operative file: `bridge\gtkb-bridge-parallel-session-collision-003.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Positive Confirmations

### C1 - Prior F1 is resolved by honest foundation-only scope

Observation: The revised proposal retitles and rescopes the work as a foundation-only registry module. It explicitly removes the earlier claim that this thread prevents concurrent same-thread bridge writes, states that no bridge writer is required to call the module in this thread, and names a follow-up integration WI for bridge-propose helper, AXIS-2, and startup-payload wiring (`bridge/gtkb-bridge-parallel-session-collision-003.md:18`, `:24`, `:104-118`, `:164`).

Impact: Prime can implement a tested primitive without closing or overclaiming the actual runtime collision fix. The integration risk remains visible rather than silently dropped.

Implementation guardrail: Do not modify bridge writer paths, AXIS-2 surfaces, startup payloads, or compliance gates in this thread. Those remain follow-up integration scope.

### C2 - Prior F2 is resolved by acquire-then-refresh primitive and regression test

Observation: The revised API adds `revalidate_thread_version(thread_slug, project_root)` and documents the integrator contract: acquire the lock, re-read live `bridge/INDEX.md`, recompute next version, assert the target file does not exist, write file and INDEX, then release (`bridge/gtkb-bridge-parallel-session-collision-003.md:84-99`). The verification plan includes `test_revalidate_returns_live_next_version` and `test_stale_next_version_detected_under_lock` (`:130-132`).

Impact: The stale-next-version race called out in the prior NO-GO is now represented as a concrete primitive plus a regression test, even though caller integration remains out of scope.

Implementation guardrail: `revalidate_thread_version()` must read the live working-tree `bridge/INDEX.md`, not cached or committed state. It should report both `next_version` and whether `bridge/<slug>-<next>.md` already exists.

### C3 - Prior F3 and F4 are resolved

Observation: The revised `target_paths` and verification command use the repo-native `platform_tests/scripts/test_bridge_work_intent_registry.py` path only (`bridge/gtkb-bridge-parallel-session-collision-003.md:16`, `:126`, `:140-143`). The mandatory applicability preflight now reports no missing required or advisory specs.

Impact: The implementation has one executable test lane and a complete cross-cutting spec surface for this proposal.

## Implementation Guardrails

- Authorized target paths: `scripts/bridge_work_intent_registry.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`, and `.gtkb-state/work-intent/.gitkeep`.
- The module should ensure its runtime parent directory exists before writing, even if `.gitkeep` is present in the checkout. Runtime cleanup may remove `.gtkb-state/work-intent/`.
- Keep the default TTL and atomic write behavior covered by tests. If the implementation chooses a different TTL or record shape, the post-implementation report must call that out and map the change back to the proposal.
- The post-implementation report must run the proposal's tests and lint command: `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short` and `python -m ruff check scripts/bridge_work_intent_registry.py`.

## Decision

GO. Prime Builder may implement the foundation-only registry primitive within the scoped target paths above. This GO does not authorize bridge-writer integration, AXIS-2 visibility, startup payload changes, or a claim that same-thread bridge collisions are fixed.

File bridge scan contribution: 1 selected entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
