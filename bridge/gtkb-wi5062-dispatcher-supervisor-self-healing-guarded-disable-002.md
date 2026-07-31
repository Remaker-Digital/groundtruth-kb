GO

# WI-5062 Dispatcher Supervisor Self-Healing and Guarded Disable Controls -- Proposal Review

bridge_kind: loyal_opposition_verdict
Document: gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable
Version: 002
Author: Loyal Opposition (Antigravity, harness C)
Date: 2026-07-06 UTC

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 76cb35e8-fe90-44b1-b08b-63559bbfea96

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

---

## Scope

- review target: `bridge/gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable-001.md`
- claim under review: Proposes registering `GTKB-DispatcherDaemon` in the SoT registry with `ensure_alive` restore actions, wiring the SOT watchdog runner to execute resource-bounded self-healing restores, and guarding scheduled-task disable operations with TTL/quiesce controls.
- date: 2026-07-06 UTC

## Verdict: GO

The proposal is architecturally sound and directly addresses the operational gaps from today's incident. The pre-implementation test plan is aligned with all cross-cutting specifications and DCL compliance requirements. 

This review grants a **GO** verdict subject to addressing the findings below during implementation.

## Findings

### [P1] Doctor Check Signature Validation Gap in _invoke_health_check

- claim: "Add a SoT registry row for the dispatcher supervisor scheduled task... and a health check that detects registered/enabled/hidden/pythonw/ensure-script compliance through the existing supervisor status probe."
- evidence: In `groundtruth_kb/watchdog/service_sot.py`, the `_invoke_health_check` function calls the registry-registered health check functions using `inspect.signature` validation:
  ```python
  if params == ["target"]:
      return _tool_check_to_dict(func(project_root))
  ```
  However, the existing doctor check function for the supervisor task, `_check_dispatcher_daemon_supervisor_task`, has the signature:
  ```python
  def _check_dispatcher_daemon_supervisor_task(
      target: Path,
      load_complex_health: Callable[[], dict[str, Any]] | None = None,
  ) -> ToolCheck:
  ```
  Because `params` contains `['target', 'load_complex_health']`, `_invoke_health_check` fails to match the `["target"]` condition and immediately returns `status = "FAIL"` with an "unsupported signature" error.
- risk/impact: When the newly added SOT registry row is probed by the watchdog, it will immediately crash/fail the health check due to the signature mismatch, rendering self-healing and monitoring broken out-of-the-box.
- recommended action: Modify `_invoke_health_check` to safely invoke doctor check functions whose first parameter is `target` and all subsequent parameters are optional (i.e. have default values).
- owner decision needed: None.

### [P2] API vs CLI Disable Enforcement / Test Impact

- claim: "gt bridge dispatch daemon supervisor disable and gt bridge dispatch complex disable should refuse unbounded disable by default. Accepted disable operations must supply either a TTL or an explicit owner-quiesce record..."
- evidence: Existing unit/integration tests in `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py` and `platform_tests/scripts/test_dispatcher_complex_control.py` invoke `disable_supervisor()` and `disable_complex()` programmatically without parameters.
- risk/impact: If the underlying Python API functions `disable_supervisor` and `disable_complex` themselves are mutated to enforce TTL/quiesce requirement checks, the existing test suite will regress and fail.
- recommended action: Implement the disable-guard validations at the CLI command/wrapper layer, or update the underlying API functions to support a default/force option (e.g. `unbounded=True` or `force=True` defaulting to `False` but callable by test suites) to preserve backwards compatibility.
- owner decision needed: None.

### [P2] Completeness of Dispatcher Complex Self-Healing

- claim: "Ensure the service/SoT watchdog executes safe ensure_alive restores for disabled or missing scheduled-task services..."
- evidence: While the supervisor task `GTKB-DispatcherDaemon` is proposed to be added to the SOT registry for self-healing, the storm watchdog task `GTKB-HarnessStormWatchdog` is not proposed to be registered, although it can also be disabled via `gt bridge dispatch complex disable`.
- risk/impact: The storm watchdog remains outside the self-healing scope. If the storm watchdog task is disabled (without quiesce, or after TTL expiry), it will not be automatically restored.
- recommended action: Evaluate whether `GTKB-HarnessStormWatchdog` should also be registered in `sot-artifacts.toml` as a self-healed service under `restore_action = "ensure_alive"`.
- owner decision needed: None.

### [P3] Terminology Name Discrepancy: decide_restore_action_for_artifact

- claim: "Wire groundtruth_kb.watchdog.service_sot to evaluate each active SoT artifact probe through decide_restore_action_for_artifact..."
- evidence: No function named `decide_restore_action_for_artifact` exists in `groundtruth_kb/watchdog/restore_policy.py`. The actual function is named `decide_artifact_restoration`.
- risk/impact: Inconsistent terminology/module-wiring specifications.
- recommended action: Ensure the implementation uses the correct function name `decide_artifact_restoration`.
- owner decision needed: None.

## Prior Deliberations

Prior deliberations on the platform service/SoT watchdog, restore-action registry, tiered restoration policies, and resource-bounded execution were consultatively reviewed:
- `DELIB-202665806` (LO Proposal Review - WI-5043 Service and SoT Watchdog Runner)
- `DELIB-202665807` (LO Verification Report - WI-5044 Watchdog Restore-Action Registry)
- `DELIB-202665808` (LO Proposal Review - WI-5044 Watchdog Restore-Action Registry)
- `DELIB-202665809` (GT-KB Bridge Verification Verdict - WI-5045 Watchdog Tiered Restoration Policy)
- `DELIB-202665810` (LO Proposal Review - WI-5045 Watchdog Tiered Restoration Policy)
- `DELIB-202665812` (LO Proposal Review - WI-5046 Watchdog Resource-Bounded Restore Execution)
- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` (Owner decision backlog intake)
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` (Owner safety tiering decision)

## Applicability Preflight

- packet_hash: `sha256:f662f57d944ac7d8218a8b0f314c0f5655bd522d29eb7944020a0f2bfc619bd1`
- bridge_document_name: `gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable-001.md`
- operative_file: `bridge/gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable`
- Operative file: `bridge\gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
