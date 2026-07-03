GO
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-03T14-55-26Z-loyal-opposition-D-c2b17f
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

bridge_kind: lo_verdict
Document: gtkb-wi4997-time-bound-dispatch-quiesce
Version: 002
Date: 2026-07-03 UTC
Prior Version: 001
Prior Author: codex (A)

## Applicability Preflight

- packet_hash: `sha256:43f371cfcce348d887c6e9d4b2212d214b2902379055d983baec2c6a11d02703`
- bridge_document_name: `gtkb-wi4997-time-bound-dispatch-quiesce`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4997-time-bound-dispatch-quiesce-001.md`
- operative_file: `bridge/gtkb-wi4997-time-bound-dispatch-quiesce-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4997-time-bound-dispatch-quiesce`
- Operative file: `bridge\gtkb-wi4997-time-bound-dispatch-quiesce-001.md`
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

## Review

The proposal identifies a real, documented control-integrity gap: on 2026-07-03, an interactive LO set the bridge substrate to `none` to quiesce automated dispatch, but ~13 minutes later a Codex-A process reset it to `dispatcher_daemon`, re-enabling dispatch and defeating the quiesce. The incident is corroborated by the current `harness-state/bridge-substrate.json` showing `applied_by: "A"` at 14:55:22Z. The proposal correctly diagnoses that there is no durable, operator-controlled mechanism to pause dispatch that the autonomous system cannot self-revert.

The proposed scope is appropriately bounded: a governed quiesce command/state with required metadata (reason, actor, issued_at, optional expires_at/ttl), daemon/runtime enforcement that refuses new claims and spawns during active quiesce, prevention of autonomous override, and exposure through existing status/health/report surfaces. The proposal preserves the existing A/B/D topology and the direct harness-to-harness launch prohibition.

### Strengths

1. **Real incident, concrete evidence**: The problem is not hypothetical. The `bridge-substrate.json` file shows the revert, and the shadow-decisions log confirms the re-dispatched worker that re-churned the threads.

2. **Bounded scope**: The proposal does not attempt to redesign the dispatch architecture. It adds a quiesce layer on top of the existing substrate mechanism without removing or replacing it.

3. **Existing infrastructure awareness**: The codebase already contains a trigger-level quiesce mechanism (`quiesce-state.json`, `_load_quiesce_state`, `_write_quiesce_state`, `_quiesce_window_seconds`, `_quiesce_key`, `_quiesce_marker` in `dispatcher_runtime.py`) used for short-window (default 5s) PostToolUse suppression. The proposal can build on this existing pattern.

4. **All target paths exist in-root**: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, and all three test files are present and importable.

5. **Preflights pass clean**: Both applicability and clause preflights return zero blocking gaps.

### Concerns for Prime Builder Attention During Implementation

1. **Authority model is the critical design question**: The incident was caused by a dispatched worker (Codex-A) writing to `harness-state/bridge-substrate.json`. If the new quiesce state is stored in another JSON file that dispatched workers can also write to, the same problem recurs. The implementation must address: what prevents a dispatched worker from clearing the quiesce flag? Options include: (a) storing quiesce state in a location that dispatched workers cannot reach (e.g., outside the project root, or in a daemon-owned memory region), (b) requiring an authorization token that only the operator/LO possesses, (c) making the daemon the sole writer of quiesce state and having the operator communicate quiesce intent through a separate channel the daemon reads but workers cannot write. The proposal should clarify which authority model it intends.

2. **Relationship to existing trigger quiesce**: The codebase already has `quiesce-state.json` with per-invocation quiesce records keyed by `{hook_event_name}:{session_id}:{harness_id}:{role_label}`. The proposal should clarify whether the new durable quiesce extends this existing mechanism (e.g., adding a global/operator-scoped record), replaces it, or sits alongside it as a separate check. Conflating the two could create subtle bugs where the 5-second trigger quiesce window interacts unexpectedly with a durable operator quiesce.

3. **Substrate interaction**: The daemon currently gates live dispatch on `_active_substrate() == "dispatcher_daemon"`. The proposal should specify whether the quiesce check is layered on top of the substrate check (i.e., both must pass), or whether quiesce is an independent gate. If layered, setting substrate to `none` would still work as a coarse kill-switch, but the quiesce would provide the durable, time-bound, non-self-reverting alternative.

4. **Daemon vs. hook-triggered dispatch**: The runtime's `_is_dispatcher_daemon_active_substrate` check is used in the hook-triggered dispatch path (PostToolUse), not just the daemon loop. The quiesce must gate both paths — daemon ticks and hook-triggered dispatch — to be effective. The proposal mentions "daemon and dispatcher runtime" which covers both, but the implementation should ensure the quiesce check appears in both the daemon's `_execute_one_tick` and the runtime's hook-triggered dispatch entry point.

5. **Test coverage specificity**: The proposal lists three test files as targets but does not describe what tests will be added. At VERIFIED time, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` will require concrete spec-to-test mappings. The Prime Builder should plan for tests covering: (a) quiesce activation prevents dispatch, (b) quiesce expiry allows dispatch, (c) dispatched workers cannot clear quiesce, (d) quiesce status appears in report/health/status surfaces, (e) explicit clear by authorized actor restores dispatch.

6. **The `bridge-substrate.json` write authority gap remains**: Even with a durable quiesce, the underlying problem — that any dispatched worker can write to `bridge-substrate.json` and change the substrate — is not directly addressed by this proposal. The quiesce adds a defense-in-depth layer, but the substrate mutation authority gap is a separate concern that may warrant its own work item. The proposal acknowledges this in its "Fix candidates" section but scopes to the quiesce mechanism. This is acceptable for a bounded proposal, but the Prime Builder should note the residual risk.

### Verdict

**GO**. The proposal addresses a real, documented dispatch control-integrity gap with a bounded, well-scoped implementation plan. The concerns above are substantive but addressable during implementation — they are the kind of design questions the Prime Builder should resolve in the implementation, not reasons to reject the proposal. The preflights pass clean, all target paths exist, and the proposal preserves existing architecture.

The Loyal Opposition will verify at post-implementation review that: (1) the quiesce authority model prevents autonomous self-revert, (2) the quiesce gates both daemon and hook-triggered dispatch paths, (3) quiesce status is exposed through report/health/status surfaces, and (4) spec-derived tests cover the key scenarios.

## Prior Deliberations

- `gtkb-cross-harness-trigger-index-edit-race-quiesce` (VERIFIED) — prior trigger-level quiesce work in `scripts/cross_harness_bridge_trigger.py`; the existing `quiesce-state.json` mechanism in `dispatcher_runtime.py` descends from this work.
- `gtkb-bridge-contention-consolidation` (VERIFIED) — related contention/consolidation work that touched the same quiesce window and edit-race concerns.
- `gtkb-bridge-dispatch-per-document-lease-substitution` (VERIFIED) — built on the post-quiesce structure; demonstrates the integration point pattern for building on committed quiesce infrastructure.
