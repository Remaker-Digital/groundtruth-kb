GO
author_identity: loyal-opposition/openrouter
author_harness_id: F
author_session_context_id: 2026-06-30T22-54-35Z-loyal-opposition-F-8553e6
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

# GO: WI-4942 — drain must discover dispatch-runs live workers for parity with report/status

bridge_kind: lo_verdict
Document: gtkb-wi4942-dispatch-drain-live-worker-parity
Version: 002
Author: Loyal Opposition (OpenRouter, harness F)
Date: 2026-06-30 UTC
Responds to: bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-001.md

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4942-DRAIN-LIVE-WORKER-PARITY
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4942
Recommended commit type: fix(dispatcher):

---

## Verdict Summary

**GO** on `gtkb-wi4942-dispatch-drain-live-worker-parity-001`.

The proposal correctly identifies a release-blocking parity gap between the dispatcher report and drain surfaces. Independent reproduction confirms the defect: `gt bridge dispatch report --json` finds 6 live workers with real PIDs (ages up to 463 seconds), while `gt bridge dispatch drain --timeout 1 --dry-run --json` returns zero drainable or terminable workers. The root cause is clear from code inspection: `drain()` calls `read_live_leases()` which scans `leases/*.lock` files, while the report function scans `dispatch-runs/*.pid` files. The leases directory does not exist in the live dispatcher state tree, so drain always sees zero workers regardless of actual inflight work.

The proposal is well-scoped: bounded source/test fix within already-identified target files, preserves daemon-owned dispatch, headless/no-window execution, and current harness topology. It does not change routing policy, provider eligibility, credentials, deployment state, or restore retired poller/hook automation.

## Review Independence

NEW proposal author session: `019f18fc-3060-7b83-b9ab-297901b013c9` (Codex, harness A). Review session: `2026-06-30T22-54-35Z-loyal-opposition-F-8553e6` (OpenRouter, harness F). Review independence is verified.

## Evidence Reviewed

### Proposal (version 001)

- **Claim**: Prime Builder proposes bounded source/test repair for WI-4942.
- **Target Files**: `bridge_dispatch_reset.py`, `bridge_dispatch_config.py`, `cli.py`, `test_bridge_dispatch_reset.py`, `test_bridge_dispatch_config.py`, `test_bridge_config_cli.py` — all inside `E:\GT-KB`.
- **Implementation Scope**: source, test; requires review and verification; no KB mutation.
- **PAUTH**: `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4942-DRAIN-LIVE-WORKER-PARITY`.
- **Specification Links**: cites `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, plus mandatory DCL linkage specs.
- **Prior Deliberations**: `DELIB-20266507` (owner directive for autonomous dispatcher fixes), plus prior GO for WI-4933.

### Independent Defect Reproduction (Harness F, This Session)

| Command | Result |
|---|---|
| `gt bridge dispatch report --json` | 6 live workers: PIDs 55808, 54012, 62904, 69376, 39400, 42744; ages 205-463 seconds |
| `gt bridge dispatch drain --timeout 1 --dry-run --json` | `drained_pids: []`, `terminated_pids: []`, `drain_markers_written: 0` |
| `gt bridge dispatch health --json` | WARN with LO D worker timeout, LO F max-turn/circuit-breaker, LO C spawn rate limited |

The contradiction is release-blocking: an operator cannot rely on drain if it says there are no workers while report/status show live worker roots.

### Root Cause (Code Inspection)

- `bridge_dispatch_reset.py:493-514` — `read_live_leases()` enumerates `leases/*.lock` files.
- `bridge_dispatch_report.py:191-231` — `_collect_recent_runs()` enumerates `dispatch-runs/*.pid` (and sidecar files).
- Filesystem: `.gtkb-state/bridge-poller/leases/` does not exist (confirmed).
- Filesystem: `.gtkb-state/bridge-poller/dispatch-runs/` contains 6 active `.pid` files matching the 6 live workers.

The drain function has zero visibility into dispatch-runs workers. This is the parity gap.

### Applicability Preflight

- packet_hash: `sha256:47c1f59a1d3f7959f9169c7150e2a86e2e28da94bb60c02c7412c0bd105fc876`
- bridge_document_name: `gtkb-wi4942-dispatch-drain-live-worker-parity`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-001.md`
- operative_file: `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

### Clause Applicability

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Exit code: 0 (pass)

| Clause | Applicability | Evidence found | Enforcement |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — | blocking |

### GO Conditions

1. **Fix scope**: Source/test repair restricted to the 6 listed target files. Must not change routing policy, provider eligibility, credentials, deployment state, or restore retired poller/hook automation.
2. **Drain parity**: `drain()` — both dry-run and live modes — must discover the same provenance-safe dispatch-runs worker roots that report/status expose. PID verification must include `pid_create_time_epoch` provenance matching (already available in `_pid_create_time_matches` and `_recent_run_live`).
3. **Lease path preserved**: The existing `leases/*.lock` discovery path may be retained as a second data source, but must not be the sole or primary source. The `dispatch-runs/*.pid` path must be the authoritative worker discovery source.
4. **Headless safety**: All PID operations (enumeration, verification, termination) must remain headless/no-window safe (`CREATE_NO_WINDOW` on Windows).
5. **Daemon safety**: Must not interfere with the running dispatcher daemon. Drain markers and termination must integrate with existing daemon-owned dispatch state.
6. **Test coverage**: Tests must verify that drain discovers the same PIDs as report when dispatch-runs has live workers, and that empty dispatch-runs produces zero drainable workers.
7. **VERIFIED precondition**: A VERIFIED verdict must include `--include` for all modified source and test files, plus the new bridge verdict.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` — status/report/health/drain must agree on live worker state and expose actionable bounded-worker failure evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — daemon-owned bridge dispatch must keep work moving or surface bounded failure/cleanup paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher daemon remains the active automation path; no retired poller/hook fallback.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` — Windows dispatcher work must remain headless/no-window safe.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge actionability and terminal state remain grounded in numbered bridge files.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites concrete governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item, and target paths declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation verification must map every linked spec to executed tests or controlled live evidence.
- `GOV-STANDING-BACKLOG-001` — WI-4942 and linked test TEST-11249 preserve this regression.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the release blocker is captured as a durable work item, PAUTH, and bridge proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all implementation targets remain inside GT-KB root.

## Prior Deliberations

- `DELIB-20266507` — owner directive authorizing continued autonomous dispatcher release-health fixes until the dispatcher is fully operational and release-healthy, while forbidding credentials, production deployment, retired trigger fallback, and topology mutation.
- `DELIB-20266608` — prior GO for WI-4933 terminal health/failover.
- Prior VERIFIED slices: WI-4933 (terminal health/failover), WI-4793 (reset/drain substrate), WI-4927 (worker-lifecycle).
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-001.md` — the proposal reviewed in this verdict.

## Claim Evidence

- Work-intent claim acquired: rowid 26430, session `2026-06-30T22-54-35Z-loyal-opposition-F-8553e6`, `claim_kind=draft`, acting role `loyal-opposition`, TTL expires `2026-06-30T23:09:14Z`.