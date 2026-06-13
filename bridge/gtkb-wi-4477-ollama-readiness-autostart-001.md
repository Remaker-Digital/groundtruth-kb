NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

bridge_kind: prime_proposal
Document: gtkb-wi-4477-ollama-readiness-autostart
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4477
target_paths: ["scripts/verify_ollama_dispatch.py", "scripts/ops/install_ollama_autostart_task.ps1", "platform_tests/scripts/test_ollama_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_ollama.py"]

# WI-4477 Ollama Readiness Autostart Proposal

## Claim

Implement the bounded Ollama server readiness and autostart visibility slice for `WI-4477`. The work will make the preferred local Ollama Loyal Opposition reviewer visibly dispatch-ready when `/api/tags` is reachable, visibly warned when host autostart is missing, and operator-installable through a tracked Windows scheduled-task installer script.

This proposal does not change ordered fallback routing, does not run the installer, does not create a Windows scheduled task during implementation, and does not promote or demote any harness role.

## Scope

- Extend `scripts/verify_ollama_dispatch.py` so readiness results distinguish:
  - registry/shim/routing readiness;
  - `/api/tags` daemon/model availability;
  - host autostart posture as a warning surface rather than a dispatch blocker when the daemon is currently reachable.
- Add a tracked `scripts/ops/install_ollama_autostart_task.ps1` operator script that registers a user-logon scheduled task to run `ollama serve` using the local Ollama executable. The script is not executed as part of this bridge implementation.
- Extend the `gt project doctor` Ollama harness check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` so unreachable `/api/tags` and missing autostart/service/task evidence surface as WARN findings.
- Add focused tests in `platform_tests/scripts/test_ollama_dispatch.py`, `platform_tests/scripts/test_verify_ollama_dispatch.py`, and `groundtruth-kb/tests/test_doctor_ollama.py` for reachable API, unreachable API, missing autostart, and current graceful fallback behavior.

No KB mutation is in implementation scope. If the implementation is VERIFIED, Prime Builder may then update the work item closure evidence through the normal verified-work closure path.

## Out Of Scope

- No dispatch-time start-if-down behavior; cold-start orchestration is explicitly deferred unless a later proposal asks for it.
- No changes to `scripts/cross_harness_bridge_trigger.py`; the already-verified ordered fallback behavior is preserved and covered by existing/targeted tests.
- No service installation, scheduled-task registration, desktop app configuration, external deployment, or credential use during implementation.
- No OpenRouter routing changes; those are separate verified work and separate environment handling.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all GT-KB artifacts and tooling changes remain inside `E:\GT-KB` and do not route unqualified tooling to Agent Red or any external checkout.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation remains bridge-mediated and bounded to explicit `target_paths`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable project authorization, project, work item, and target-path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the governing specifications and maps verification to them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must execute the mapped readiness, doctor, fallback, lint, and format checks.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the reliability fast-lane PAUTH does not bypass the required GO verdict or implementation-start packet.
- `GOV-RELIABILITY-FAST-LANE-001` - `WI-4477` is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`; this is a small reliability/readiness fix preserving the bridge and safety gates.
- `GOV-STANDING-BACKLOG-001` - `WI-4477` remains the canonical backlog work item; implementation performs no bulk backlog mutation.
- `ADR-OLLAMA-HARNESS-ADOPTION-001` - Ollama is an adopted harness surface whose readiness must be governed before relying on it as a local reviewer.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - the doctor/readiness surface extends the Ollama harness capability floor with non-blocking diagnostic visibility.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - readiness still requires the bridge-review route to expose the full LO tool set before dispatch can use the harness.
- `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` - readiness continues to resolve the configured Ollama bridge-review route from `.ollama/routing.toml`.
- `DCL-OLLAMA-AUTHOR-METADATA-INJECTION-001` - this slice preserves the existing Ollama harness invocation and metadata path; no author-metadata weakening is proposed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the advisory and work item are preserved as durable artifacts rather than transient chat context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation preserves traceability across work item, advisory, proposal, tests, and implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - `WI-4477` remains open until implementation is reported and Loyal Opposition records VERIFIED.

## Owner Decisions / Input

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - owner directed cost-optimized automatic bridge dispatch as top-priority work, with Ollama local as the cheapest preferred reviewer.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner approved the standing reliability fast-lane structure, preserving bridge review while reducing per-fix authorization ceremony for active reliability project members.
- `bridge/gtkb-ollama-server-readiness-autostart-advisory-001.md` - Loyal Opposition advisory specifically recommended a bounded readiness/autostart slice for `WI-4477` and stated no additional owner action was required for Prime Builder to propose it.

## Prior Deliberations

- `DELIB-20260612-COST-OPTIMIZED-AUTODISPATCH-TOP-PRIORITY` - establishes this work as part of the top-priority cost-optimized autodispatch program and names `WI-4477` as a member preserving reliability fast-lane authority.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - establishes the standing fast-lane model for small reliability fixes that still require bridge review.
- `bridge/gtkb-ollama-server-readiness-autostart-advisory-001.md` - source advisory for this proposal; identifies the gap as host readiness and autostart visibility, not fallback-routing correctness.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-008.md` - VERIFIED fallback-routing thread; leaves Ollama readiness/autostart outside WI-4484 scope and confirms fallback should degrade when Ollama is not ready.
- `bridge/gtkb-ollama-integration-phase-1-verification-006.md` - GO authority for the existing Ollama Phase-1 doctor/check surfaces that this proposal extends.

## Requirement Sufficiency

Existing requirements sufficient.

The owner priority directive, existing Ollama harness adoption specifications, the active `WI-4477` work item, and the Loyal Opposition advisory fully constrain this readiness/autostart visibility slice. No new or revised requirement is needed before implementation.

## Clause Scope Clarification

This proposal mentions `work item`, `backlog`, and `doctor`, but it is not a bulk standing-backlog operation. Implementation is limited to the listed source, test, and operator-script paths. Any eventual `WI-4477` status update is deferred until after Loyal Opposition records VERIFIED and will cite the verified bridge evidence.

The tracked PowerShell script is an installer artifact, not an executed deployment. It must be syntax-checkable and documented by its own `-WhatIf`/dry-run behavior or equivalent guard, and Prime Builder will not register or start a scheduled task under this implementation report.

## Implementation Plan

1. Add an autostart-detection helper to `scripts/verify_ollama_dispatch.py` that checks Windows scheduled-task/service evidence when available and returns structured warning details without printing secrets or launching processes.
2. Include that helper's result in readiness JSON and human-readable `--readiness-only` output. Missing autostart should warn; it should not make `ready=false` when `/api/tags` is reachable and the configured model is advertised.
3. Add `scripts/ops/install_ollama_autostart_task.ps1` with guarded parameters for task name, Ollama executable path, endpoint/process expectations, and dry-run behavior. The script should create a user-logon scheduled task that runs `ollama serve` only when the operator executes it.
4. Extend `_check_ollama_harness` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` so `/api/tags` unreachable and autostart missing are WARN findings, while existing registry/routing checks remain intact.
5. Add tests covering API reachable/model advertised, API unreachable, missing autostart warning, installer-script syntax/guard behavior, and existing fallback degradation when Ollama readiness fails.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify changed paths are inside `E:\GT-KB` and target only GT-KB platform surfaces, not Agent Red or any outside checkout. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi-4477-ollama-readiness-autostart` before edits; implementation stays within `target_paths`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-4477-ollama-readiness-autostart`; expected `missing_required_specs: []` and `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this mapping forward with observed command results. |
| `ADR-OLLAMA-HARNESS-ADOPTION-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `DCL-OLLAMA-TOOL-PARITY-GATE-001`, `DCL-OLLAMA-ROUTING-CONFIG-SCHEMA-001` | `python -m pytest platform_tests/scripts/test_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py groundtruth-kb/tests/test_doctor_ollama.py -q --tb=short`. |
| `GOV-STANDING-BACKLOG-001`, `GOV-RELIABILITY-FAST-LANE-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Proposal and report state no bulk backlog mutation; verified bridge evidence is used before any WI closure update. |

Planned commands:

- `python -m pytest platform_tests/scripts/test_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py groundtruth-kb/tests/test_doctor_ollama.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short -k "ollama and readiness"`
- `python -m ruff check scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py groundtruth-kb/tests/test_doctor_ollama.py`
- `python -m ruff format --check scripts/verify_ollama_dispatch.py groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py groundtruth-kb/tests/test_doctor_ollama.py`
- PowerShell syntax validation for `scripts/ops/install_ollama_autostart_task.ps1` using `pwsh` when available, or Windows PowerShell parser fallback when `pwsh` is unavailable.

## Acceptance Criteria

- `evaluate_dispatch_readiness(..., require_daemon=True)` returns `ready=false` with an explicit `/api/tags` check when the API is unreachable.
- When `/api/tags` is reachable and the configured model is advertised, missing autostart evidence appears as a warning but does not block dispatch readiness.
- `gt project doctor` exposes WARN findings for missing autostart and unreachable `/api/tags` instead of silently skipping those host-readiness gaps.
- The new scheduled-task installer script is tracked, syntax-checkable, and dry-run/guarded; it is not executed during implementation.
- Existing fallback behavior still records `ollama_dispatch_not_ready` and avoids dispatch storms when Ollama is unavailable.
- Ruff lint and format checks pass for changed Python files.

## Risk / Rollback

The main risk is over-blocking dispatch when only autostart evidence is missing. The implementation must keep autostart as warning-only while the live daemon/model route is ready. Rollback is straightforward: revert the changed source/test/operator-script files and file a NO-GO/repair report if Loyal Opposition finds the warning/blocking boundary wrong.

## Conventional Commit Type

`feat`
