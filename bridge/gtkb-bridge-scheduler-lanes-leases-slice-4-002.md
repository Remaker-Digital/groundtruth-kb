GO

# Loyal Opposition Review - Bridge Scheduler Slice 4: Per-Role Dispatch Concurrency

bridge_kind: lo_verdict
Document: gtkb-bridge-scheduler-lanes-leases-slice-4
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md
Recommended commit type: feat:

## Verdict

GO for Slice 4 implementation.

This verdict approves the additive per-role dispatch concurrency primitive described in `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md`. It confirms Prime's proposed disposition for Loyal Opposition Ask 1: Slice 4 may deliver the standalone worker-slot module and focused tests without wiring `scripts/cross_harness_bridge_trigger.py` or `scripts/single_harness_bridge_dispatcher.py` yet.

The later dispatch-loop integration must still consume the Slice 2 lease registry, Slice 3 serialized INDEX writer, and Slice 4 concurrency module before the fixed `DEFAULT_MAX_ITEMS = 2` behavior is actually retired.

## Prior Deliberations

Deliberation Archive searches were run before review:

- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "bridge scheduler lanes leases per role concurrency WI-3375 S350" --limit 8 --json` returned no direct matches.
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "DELIB-2182 bridge scheduler lanes leases AskUserQuestion" --limit 8 --json` returned no direct matches.
- `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations get DELIB-2182` retrieved the controlling owner authorization.

Relevant decision and bridge history:

- `DELIB-2182` records the owner's 2026-05-18 authorization for the full bridge scheduler program, including Slice 4 as per-role dispatch concurrency limits.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-002.md` is the GO verdict approving the five-slice scheduler plan and requiring follow-on slices to restate concrete test coverage.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-2-004.md` VERIFIED the sibling per-document lease registry.
- `bridge/gtkb-bridge-scheduler-lanes-leases-slice-3-002.md` GO'd the sibling serialized `bridge/INDEX.md` writer and explicitly deferred dispatch-path wiring.

## Review Findings

No blocking findings.

### P3-CONSTRAINT - Validate role labels before deriving paths or env-var names

Observation: The proposal derives slot paths from `<state_dir>/workers/<role>/slot-<n>.lock` and env-var names from `GTKB_DISPATCH_CONCURRENCY_<ROLE>` (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md:81`, `:90`). Existing dispatch role labels are currently hardcoded to `prime-builder` and `loyal-opposition` (`scripts/cross_harness_bridge_trigger.py:713-714`; `scripts/single_harness_bridge_dispatcher.py:79`), so the current caller surface is controlled.

Deficiency rationale: The new module is a reusable filesystem-writing primitive. Without canonical role normalization and rejection of invalid role strings, a future caller could accidentally create unexpected worker-slot directories or produce inconsistent env-var lookup keys. The Slice 2 lease registry already treats slug validation as the path-traversal defense (`scripts/bridge_lease_registry.py:42-43`, `:77-78`); Slice 4 should apply the same standard to role labels.

Proposed solution: Implement a small role-normalization/validation helper that accepts only the canonical scheduler roles (`prime-builder`, `loyal-opposition`) for filesystem paths, derives env-var suffixes deterministically by uppercasing and replacing hyphens with underscores, and raises `ValueError` for path separators, dots, empty strings, and unknown roles. Add focused invalid-role tests alongside T1-T13.

Option rationale: Constraining the role set is lower-risk than trying to sanitize arbitrary labels because the bridge scheduler has exactly two role lanes today and the dispatch scripts already operate on those durable role labels.

### P4-INFO - Standalone primitive boundary is accepted, but integration must not disappear

Observation: The approved scoping bullet says Slice 4 should replace `DEFAULT_MAX_ITEMS = 2` with per-role concurrency and track in-flight worker count (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-1-scoping-001.md:85`). This proposal intentionally delivers only the standalone concurrency module and defers the actual dispatch-loop replacement (`bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md:21`, `:23`, `:96`).

Deficiency rationale: That boundary matches the isolated-primitive pattern accepted for Slices 2 and 3, but it means Slice 4 alone will not improve live bridge throughput. The dispatch cap remains visible at `scripts/cross_harness_bridge_trigger.py:112` and `scripts/single_harness_bridge_dispatcher.py:72` until a later integration slice consumes the primitive.

Proposed solution: Keep Slice 4 additive and do not modify dispatch scripts in this implementation. In the post-implementation report, explicitly repeat that live dispatch behavior is unchanged. The later scheduler proposal that first changes dispatch selection must cite this deferral and consume the Slice 2, Slice 3, and Slice 4 primitives together.

Option rationale: Approving the standalone primitive keeps the current slice small and testable. Forcing full dispatch integration into Slice 4 would bundle leases, INDEX serialization, role slots, and selector behavior into one larger change, increasing review risk.

## Positive Confirmations

- Live `bridge/INDEX.md` was reread before verdict; latest status remained `NEW: bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md`.
- `show_thread_bridge.py` reported no drift for the Slice 4 thread.
- The proposal includes project-linkage metadata for active authorization `PAUTH-PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES-BRIDGE-SCHEDULER-PROGRAM-IMPLEMENTATION-AUTHORIZATION`, project `PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES`, and work item `WI-3375`.
- `groundtruth_kb projects authorizations PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json` shows that authorization is active and includes `WI-3375`.
- `groundtruth_kb projects show PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json` shows `WI-3375` is the Slice 4 per-role dispatch concurrency work item.
- Current state inspection found `scripts/bridge_dispatch_concurrency.py` and `platform_tests/scripts/test_bridge_dispatch_concurrency.py` do not yet exist, matching the pre-implementation state.
- Current dispatch state still has fixed caps in both dispatchers (`scripts/cross_harness_bridge_trigger.py:112`; `scripts/single_harness_bridge_dispatcher.py:72`), and this GO does not authorize changing those files in Slice 4.

## Applicability Preflight

- packet_hash: `sha256:075ec2df831eee3988f8da595dfc93c8477888b7eca51ab63efa5b356685720e`
- bridge_document_name: `gtkb-bridge-scheduler-lanes-leases-slice-4`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md`
- operative_file: `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-scheduler-lanes-leases-slice-4`
- Operative file: `bridge\gtkb-bridge-scheduler-lanes-leases-slice-4-001.md`
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

## Follow-On Constraints for Prime Builder

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4` before implementation edits.
2. Keep implementation within `scripts/bridge_dispatch_concurrency.py` and `platform_tests/scripts/test_bridge_dispatch_concurrency.py`; do not modify dispatch code in this slice.
3. Preserve the approved public API names: `role_limit`, `register_worker`, `release_worker`, `refresh_worker`, `in_flight_count`, `available_slots`, `reclaim_stale_workers`, and `worker_slot`.
4. Implement role-label normalization/validation before using `role` in a filesystem path or env-var suffix.
5. Preserve the bounded atomic slot-pool design: `slot-<n>.lock` for `n` in `0 .. role_limit(role) - 1`, with `os.open(..., O_CREAT | O_EXCL | O_WRONLY)` acquisition.
6. Preserve token-guarded release/reclaim and atomic heartbeat refresh with `os.replace`.
7. Include tests T1-T13 from the proposal, plus invalid-role validation coverage for path separators, dots, empty strings, and unknown roles.
8. Re-run and report `python -m pytest platform_tests/scripts/test_bridge_dispatch_concurrency.py -q`. If the default pytest temp path is outside the project root or inaccessible, set `TMP` and `TEMP` to an in-root directory such as `E:\GT-KB\.tmp` and report that command explicitly.
9. Re-run and report both bridge preflights in the post-implementation report.
10. In the post-implementation report, state that live dispatch behavior remains unchanged until a later integration proposal wires this module into the dispatch path.

## Opportunity Radar

No separate advisory was filed. This proposal is itself a deterministic-service step: it turns ad hoc per-role worker capacity tracking into a reusable module with objective tests. The material follow-on opportunity is the later integration proposal that should consume the Slice 2, Slice 3, and Slice 4 primitives together rather than reimplementing their logic inside dispatcher code.

## Commands Executed

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4
```

Observed: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-scheduler-lanes-leases-slice-4
```

Observed: 5 clauses evaluated; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`; exit 0.

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-bridge-scheduler-lanes-leases-slice-4 --format json
```

Observed: full chain found with latest live status `NEW` on `bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md`; no drift reported.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations get DELIB-2182
```

Observed: DELIB-2182 records owner authorization for the full bridge scheduler program and confirms Slice 4 as the per-role dispatch concurrency slice.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:/GT-KB/groundtruth.toml projects authorizations PROJECT-GTKB-BRIDGE-SCHEDULER-LANES-LEASES --json
```

Observed: the project authorization is active and includes `WI-3375`.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
