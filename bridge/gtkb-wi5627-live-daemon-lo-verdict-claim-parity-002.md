GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5627-live-daemon-lo-verdict-claim-parity
Version: 002
Responds to: bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md
Date: 2026-07-19 UTC

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5627

## First-Line Role Eligibility Check

PASS. The current owner transcript assigns this interactive session to Loyal Opposition, and the reviewer is writing a Loyal Opposition `GO` status. This is authorized by `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. The proposal was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`; this verdict is authored from Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Verdict

GO. WI-5627 identifies a real production-daemon parity gap. WI-5400 added dispatcher-owned, pre-launch Loyal Opposition verdict-claim acquisition to the `dispatcher_runtime.py::run_dispatch_cycle` path, but `scripts/gtkb_dispatcher_daemon.py::_execute_live_spawns` uses a separate live-spawn loop. That loop currently acquires document leases and establishes worker authority, then reaches `_spawn_harness` without first acquiring LO verdict claims for the selected document batch or attaching trusted verdict-claim context.

The proposal correctly applies the already-accepted WI-5400 lifecycle to the live daemon path without changing dispatcher configuration, routing, eligibility, allowances, leases outside the existing API, or provider behavior. Implementation is approved only as an exact WI-5627 hunk slice.

## Applicability Preflight

Command run: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity --json`

- packet_hash: `sha256:2b7365e035163c8279c8fefc71bb4ff8ae5e4773cb32fc0326e00b6f3879d5dd`
- bridge_document_name: `gtkb-wi5627-live-daemon-lo-verdict-claim-parity`
- content_source.mode: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md`
- operative_file: `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md`
- operative_status: `NEW`
- operative_version: `001`
- preflight_passed: `true`
- declared_target_paths: `[ "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "scripts/gtkb_dispatcher_daemon.py" ]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:3adecee4be7d65c00f0dfd48dfa6aa887f3c532fff81dced4a7f41c9d478107e`

## Clause Applicability

Command run: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity`

- Bridge id: `gtkb-wi5627-live-daemon-lo-verdict-claim-parity`
- Operative file: `bridge\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md`
- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | not required for this single work item | blocking | blocking |

## Prior Deliberations

- `DELIB-202666762` is the direct WI-5400 owner decision: the owner selected dispatcher-owned pre-launch verdict-claim acquisition, including neutral peer-held suppression, worker-lifetime-aligned claim TTL, and owned-claim-only release on launch failure or incomplete exit.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorizes the standing reliability fast-lane structure while preserving bridge proposal, review, work-item, and safety gates.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` is carried by the proposal as the canonical-source boundary; this review used canonical bridge, MemBase, source, and test evidence.

The deliberation search for `WI-5627 live daemon LO verdict claim parity provider spawn peer held claim` surfaced no decision rejecting live-daemon parity with WI-5400.

## Evidence Reviewed

- `scripts/gtkb_dispatcher_daemon.py::_execute_live_spawns` currently acquires LO document leases, creates a dispatcher worker session, and calls `_spawn_harness`, but does not call `_acquire_lo_verdict_work_intent_batch` before provider launch.
- `scripts/dispatcher_runtime.py::run_dispatch_cycle` already calls `_acquire_lo_verdict_work_intent_batch` after trusted worker-session creation and before `_spawn_harness`; on claim failure it records a non-launched result and releases document leases.
- `TEST-11672` exists and states the required live-daemon behavior: acquire the exact selected LO document batch before provider spawn, suppress peer-held contention neutrally with no provider call, release only daemon-owned claims on failure, and record trusted claim context.
- `WI-5627` exists as P0/open in `PROJECT-GTKB-RELIABILITY-FIXES` with source test `TEST-11672`.
- `git diff --stat` on the two declared targets currently reports 544 insertions and 4 deletions. This dirty state is material and must be handled by exact hunk ownership, not whole-file staging.

## Positive Findings

1. The defect is real and cost-bearing. The live daemon path can launch an LO provider without owning the selected verdict claims, leaving the governed publisher to discover a peer-held claim only after provider spend.

2. The proposed repair is a parity application of an already approved architecture. It does not create a new claim model; it reuses the existing `dispatcher_runtime` LO verdict-claim lifecycle and the same worker-session authority boundary.

3. The verification plan is well matched to the failure mode. It requires free-batch pre-spawn acquisition, peer-held neutral suppression with no provider call, partial-claim failure, authority failure, launch failure, incomplete-exit cleanup, and exact daemon-owned claim release.

4. The scope is appropriately narrow: only `scripts/gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` are declared as implementation targets, and the proposal explicitly forbids dispatcher configuration, runtime-state, eligibility, routing, role, lease-file, allowance, process, live-worker, credential, deployment, release, and cleanup mutation.

## Implementation-Start Conditions

This GO is conditioned on all of the following:

1. Prime Builder must acquire an exact WI-5627 work-intent claim and schema-v3 implementation-start packet for the two declared target paths.
2. The implementation must be based on current bytes after GO and carried as an exact WI-5627 patch/hunk set.
3. Whole-file staging of `scripts/gtkb_dispatcher_daemon.py` or `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` is prohibited while those files contain foreign dirty bytes.
4. The implementation report must include exact hunk hash, hunk size, forward/reverse apply checks, focused diff evidence, and explicit exclusion of foreign hunks.
5. Post-implementation verification must run `TEST-11672` coverage through focused daemon tests plus Ruff, format check, py_compile, diff check, applicability preflight, and clause preflight.

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5627-live-daemon-lo-verdict-claim-parity --format json --preview-lines 160
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity
git status --short -- scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md
Get-Content bridge\gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md
rg -n "_execute_live_spawns|_spawn_harness|_acquire_lo_verdict_work_intent_batch|ensure.*worker|claim|release|document leases|document_leases|worker_session" scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb\.venv\Scripts\gt.exe tests show TEST-11672 --json
groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-5627 --json
git diff --stat -- scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
git diff --numstat -- scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb\.venv\Scripts\gt.exe deliberations show DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "WI-5627 live daemon LO verdict claim parity provider spawn peer held claim" --json
```

## Decision

GO. Prime Builder may implement the WI-5627 live-daemon parity repair only as an exact hunk slice from current bytes, preserving the WI-5400 claim lifecycle semantics and every dispatcher-configuration hold.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
