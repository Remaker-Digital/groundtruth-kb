NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - WI-5039 watchdog heartbeat remediation

bridge_kind: prime_proposal
Document: gtkb-wi5039-watchdog-heartbeat-remediation
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5039

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py", "scripts/ops/harness_storm_watchdog.ps1", "scripts/install_storm_watchdog_task.ps1", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py", "platform_tests/scripts/test_dispatcher_watchdog_control.py", "platform_tests/scripts/test_harness_storm_watchdog.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Convert the WI-5039 advisory into a bounded implementation slice that fixes the dispatcher-complex watchdog heartbeat false-WARN.

Fresh live evidence from `gt bridge dispatch health --json`, `gt bridge dispatch complex status --json`, and `gt bridge dispatch daemon watchdog status --json` shows the daemon and routing dimensions are healthy, the watchdog scheduled task is registered/enabled/healthy, and the only WARN is:

```text
watchdog heartbeat is stale (49.1s > 15.0s)
```

The likely concrete defect is a field-name collision. `scripts/ops/harness_storm_watchdog.ps1` writes `threshold=15` to the heartbeat line as the process-count threshold, while `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py` parses `threshold=` as the heartbeat stale-age threshold. The watchdog scheduled task is installed with default `IntervalMinutes=1`, so a healthy once-per-minute watchdog can be reported stale whenever heartbeat age exceeds the unrelated process-count threshold of 15 seconds.

This proposal authorizes the narrow source/test/config repair needed to separate watchdog process-count thresholds from heartbeat freshness thresholds and make complex health return PASS when the watchdog is registered, enabled, running on its expected cadence, and the heartbeat is fresh relative to that cadence.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5039 names the failure mode and acceptance summary; the existing advisory `bridge/gtkb-wi5039-watchdog-heartbeat-stale-advisory-001.md` provides LO evidence; `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` provides owner approval; and the active PAUTH bounds implementation.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation must wait for LO GO, work-intent claim, implementation-start packet, report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706` authorizes this bounded project work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass the bridge lifecycle.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the relevant governing specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute tests derived from the linked specs.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - dispatcher daemon, supervisor, and watchdog remain separate runtimes but share one management and health surface.
- `SPEC-INTAKE-5e9375` - dispatcher-complex management CLI and unified complex-health contract.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` - dispatch health status must distinguish true degradation from benign or misclassified state.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher health and routing must surface actionable reliability state without false unhealthy classifications.

## Prior Deliberations

- `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` - owner approved WI-5039 for governed implementation planning and authorization.
- `DELIB-202665481` - owner authorized the dispatcher-complex CLI implementation program covering daemon/supervisor/watchdog management and health.
- `bridge/gtkb-wi5039-watchdog-heartbeat-stale-advisory-001.md` - LO advisory evidence that the stale watchdog heartbeat is the sole health WARN.

## Owner Decisions / Input

- `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` - owner approval for WI-5039.
- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706` - active project authorization including WI-5039 and forbidding production deployment, credential lifecycle, destructive bulk cleanup, broad bulk status mutation, and merged daemon/supervisor/watchdog runtime processes.

## Proposed Scope

- Verify and document the current watchdog heartbeat semantics: scheduled task cadence, heartbeat line fields, and complex-health stale-age interpretation.
- Rename or disambiguate heartbeat metadata so process-count thresholds are not parsed as heartbeat freshness thresholds.
- Define the heartbeat freshness threshold from a clear source, such as an explicit heartbeat-stale field emitted by the watchdog, an installer/cadence-derived default with margin, or a dispatcher-complex constant aligned to the one-minute task cadence.
- Keep daemon, supervisor, and watchdog runtimes separate; do not merge their processes or change their fault-isolation model.
- Preserve existing watchdog safety properties: no automatic kill-switch assertion, no raw-count fallback kill, no Claude termination, and liveness-aware reap behavior only.
- Update tests to reproduce the old false-WARN and lock the corrected PASS/WARN behavior.

## Out of Scope

- Production deployment.
- Credential lifecycle changes.
- Merging daemon, supervisor, and watchdog runtimes.
- Broad dispatcher topology changes beyond watchdog-heartbeat health semantics.
- Destructive cleanup or broad backlog/project status mutation.

## Acceptance Criteria

- A heartbeat line containing `threshold=15` as the process-count threshold no longer forces heartbeat stale-age to 15 seconds.
- A watchdog heartbeat approximately 49-60 seconds old is treated as fresh when it is within the configured or cadence-derived heartbeat freshness window.
- A genuinely stale watchdog heartbeat still produces WARN with an actionable finding.
- `gt bridge dispatch health --json` and `gt bridge dispatch complex status --json` can return PASS for complex lifecycle when daemon, supervisor, watchdog scheduled task, and watchdog heartbeat are all healthy relative to expected cadence.
- Tests cover the field-collision regression and the genuinely stale heartbeat case.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-COMPLEX-CLI-001` | Focused complex CLI tests prove daemon/supervisor/watchdog remain separate components and complex health consumes the corrected watchdog heartbeat semantics. |
| `SPEC-INTAKE-5e9375` | CLI tests prove `gt bridge dispatch complex health/status` expose the corrected watchdog component state. |
| `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` | Unit tests prove benign minute-cadence heartbeat age is PASS while genuinely stale or absent heartbeat remains WARN. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Health output should no longer classify a registered/enabled healthy watchdog as degraded solely because of the process-count threshold field. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation report must cite the GO, work-intent claim, implementation-start packet, changed files, and exact commands. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include this table carried forward with executed results. |

Minimum expected commands:

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py platform_tests/scripts/test_dispatcher_watchdog_control.py platform_tests/scripts/test_harness_storm_watchdog.py -q --tb=short
gt bridge dispatch health --json
gt bridge dispatch complex status --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5039-watchdog-heartbeat-remediation --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5039-watchdog-heartbeat-remediation
```

## Risks / Rollback

Risk is under-detecting a truly dormant watchdog if the freshness threshold becomes too loose. Mitigation: derive the heartbeat stale window from the actual scheduled cadence with margin and retain tests for truly stale heartbeat WARN. Rollback is a source/test revert; no production deployment or credential mutation is in scope.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`
- `scripts/ops/harness_storm_watchdog.ps1`
- `scripts/install_storm_watchdog_task.ps1`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`
- `platform_tests/scripts/test_dispatcher_watchdog_control.py`
- `platform_tests/scripts/test_harness_storm_watchdog.py`

## Recommended Commit Type

`fix`
