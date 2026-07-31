REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-06T02-17-02Z-prime-builder-A-7d12ee
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex dispatcher-spawned headless; resolved_role=prime-builder
author_metadata_source: bridge-auto-dispatch-runtime-envelope

# Revised Implementation Proposal - WI-5039 Watchdog Heartbeat Remediation

bridge_kind: prime_proposal
Document: gtkb-wi5039-watchdog-heartbeat-remediation
Version: 003
Responds to: gtkb-wi5039-watchdog-heartbeat-remediation-002 (NO-GO, loyal-opposition/claude/B)
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5039

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision addresses both P2 findings from `bridge/gtkb-wi5039-watchdog-heartbeat-remediation-002.md` and narrows WI-5039 to the parser-side remediation Loyal Opposition identified as sufficient.

The implementation scope is now intentionally limited to `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py` and `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`. The watchdog heartbeat writer, scheduled-task installer, `scripts/dispatcher_runtime.py`, and `scripts/ops/dispatch_monitor.py` remain out of scope because the shared heartbeat `threshold=` field remains process-count metadata and is not renamed or re-emitted in this slice.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5039 identifies the false-WARN failure mode; `bridge/gtkb-wi5039-watchdog-heartbeat-stale-advisory-001.md` supplies Loyal Opposition evidence; `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` supplies owner approval for governed implementation planning; and the active PAUTH bounds implementation. The NO-GO findings refine implementation scope and acceptance criteria; they do not require a new owner decision.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation must wait for Loyal Opposition GO, work-intent claim, implementation-start packet, implementation report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706` authorizes this bounded project work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass the bridge lifecycle.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute tests derived from the linked specs.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - dispatcher daemon, supervisor, and watchdog remain separate runtimes but share one management and health surface.
- `SPEC-INTAKE-5e9375` - dispatcher-complex management CLI and unified complex-health contract.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` - dispatch health status must distinguish true degradation from benign or misclassified state.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher health and routing must surface actionable reliability state without false unhealthy classifications.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - bridge proposal and revision findings are durable artifacts in the implementation lifecycle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - NO-GO findings crossing from review into implementation scope are lifecycle triggers for a revised artifact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the revised proposal preserves the decision and review context as governed project evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active proposal, source, and test paths remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` - owner approved WI-5039 for governed implementation planning and project authorization.
- `DELIB-202665481` - owner authorized the dispatcher-complex CLI implementation program and forbade merging daemon, supervisor, and watchdog runtime processes.
- `bridge/gtkb-wi5039-watchdog-heartbeat-stale-advisory-001.md` - Loyal Opposition advisory evidence that the stale watchdog heartbeat classification was the live health blocker.
- `bridge/gtkb-wi5039-watchdog-heartbeat-remediation-002.md` - Loyal Opposition NO-GO that accepted the root-cause diagnosis and required this parser-side scope correction plus stronger freshness-window criteria.

Deliberation searches for `WI-5039 watchdog heartbeat dispatcher complex threshold` and `watchdog heartbeat stale threshold dispatcher complex health` returned no additional remediation-design deliberations. No previously rejected approach is being reintroduced.

## Owner Decisions / Input

- `DELIB-20260706-WI5039-IMPLEMENTATION-APPROVAL` - owner approval for WI-5039.
- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5039-WATCHDOG-HEARTBEAT-20260706` - active project authorization including WI-5039 and forbidding production deployment, credential lifecycle changes, destructive bulk cleanup, broad bulk status mutation, and merged daemon/supervisor/watchdog runtime processes.

No new owner decision is required for this revision. The NO-GO states that no owner decision is blocked and that both findings are implementation-scope refinements.

## Findings Addressed

### Finding 1 (P2) - Scope points at the wrong layer; target_paths mismatch and two out-of-scope sibling consumers

Response: accepted. This revision commits the implementation to the parser-side fix in `dispatcher_complex.py`.

The implementation must stop treating the heartbeat line's shared `threshold=` field as a heartbeat freshness source. That field remains process-count metadata emitted by `scripts/ops/harness_storm_watchdog.ps1` and consumed/displayed by sibling watchdog surfaces. The remediation should use `DEFAULT_HEARTBEAT_STALE_SECONDS = 180.0` in `dispatcher_complex.py` as the freshness window for this slice, or an equivalent dispatcher-complex freshness source that is separate from `threshold=`.

No writer rename, writer re-emission, scheduled-task installer edit, `dispatcher_runtime.py` edit, or `dispatch_monitor.py` edit is authorized by this revised scope. `scripts/dispatcher_runtime.py` remains the reference pattern: parse `threshold=` only as process-count/display data and compute heartbeat staleness from a separate freshness constant.

Scope change: `scripts/ops/harness_storm_watchdog.ps1`, `scripts/install_storm_watchdog_task.ps1`, `platform_tests/scripts/test_dispatcher_watchdog_control.py`, and `platform_tests/scripts/test_harness_storm_watchdog.py` were removed from `target_paths`. They may still be read or used as context, but they are not mutation targets for this implementation slice.

### Finding 2 (P2) - Acceptance Criterion 2 under-specifies the freshness window; fix could still emit intermittent false WARNs

Response: accepted. Acceptance criteria and tests now require a freshness window that covers the full one-minute scheduled cadence plus scheduler/execution margin.

The implementation must treat watchdog heartbeat ages within `DEFAULT_HEARTBEAT_STALE_SECONDS = 180.0` as fresh for dispatcher-complex health, including heartbeat lines that contain `threshold=15` as process-count metadata. Tests must cover a heartbeat age above 60 seconds and still within the freshness window, such as 120 seconds. Tests must also cover a genuinely stale heartbeat above the freshness window, such as 181 seconds or greater, and assert WARN/actionable finding behavior.

This removes the insufficient 49-60 second cap and prevents an implementation that merely passes a narrow example while still producing intermittent false WARNs on normal one-minute cadence jitter.

## Proposed Scope

- Inspect `dispatcher_complex._read_watchdog_heartbeat` and its freshness-source path.
- Remove or bypass `_parse_heartbeat_threshold(line)` as a source of heartbeat stale-age seconds.
- Preserve `threshold=` as process-count metadata owned by the watchdog heartbeat writer.
- Use `DEFAULT_HEARTBEAT_STALE_SECONDS = 180.0` or an equivalent dispatcher-complex freshness source separate from `threshold=`.
- Add focused tests in `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py` for:
  - a heartbeat line containing `threshold=15` with age above 60 seconds but within 180 seconds returning fresh/PASS semantics; and
  - a heartbeat age above the dispatcher-complex freshness window returning stale/WARN semantics.
- Keep daemon, supervisor, and watchdog runtimes separate; do not merge their processes or change fault isolation.

## Out of Scope

- Production deployment.
- Credential lifecycle changes.
- Merging daemon, supervisor, and watchdog runtimes.
- Editing `scripts/ops/harness_storm_watchdog.ps1`.
- Editing `scripts/install_storm_watchdog_task.ps1`.
- Editing `scripts/dispatcher_runtime.py`.
- Editing `scripts/ops/dispatch_monitor.py`.
- Broad dispatcher topology changes beyond dispatcher-complex watchdog-heartbeat health semantics.
- Destructive cleanup or broad backlog/project status mutation.

## Acceptance Criteria

- A heartbeat line containing `threshold=15` as a process-count threshold no longer causes dispatcher-complex heartbeat freshness to use a 15-second stale-age threshold.
- A watchdog heartbeat older than 60 seconds but within `DEFAULT_HEARTBEAT_STALE_SECONDS = 180.0`, such as 120 seconds old, is treated as fresh by dispatcher-complex health.
- A watchdog heartbeat older than the dispatcher-complex freshness window, such as 181 seconds or greater when the window is 180 seconds, still produces WARN with an actionable stale-heartbeat finding.
- `gt bridge dispatch health --json` and `gt bridge dispatch complex status --json` can return PASS for complex lifecycle when daemon, supervisor, watchdog scheduled task, and watchdog heartbeat are all healthy relative to the dispatcher-complex freshness window.
- Tests cover the `threshold=15` field-collision regression and the genuinely stale heartbeat case.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-COMPLEX-CLI-001` | Focused complex CLI tests prove daemon/supervisor/watchdog remain separate components and dispatcher-complex health consumes watchdog heartbeat freshness independent of process-count `threshold=` metadata. |
| `SPEC-INTAKE-5e9375` | CLI tests prove `gt bridge dispatch complex health/status` expose corrected watchdog component state without requiring writer or installer changes. |
| `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` | Unit tests prove benign minute-cadence heartbeat age above 60 seconds is PASS/fresh while genuinely stale age above the freshness window remains WARN/stale. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Health output no longer classifies a registered/enabled healthy watchdog as degraded solely because of the process-count threshold field; no runtime process merge is performed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation report must cite the GO, work-intent claim, implementation-start packet, changed files, and exact commands. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry this table forward with executed results. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation report must cite this revised proposal and the NO-GO findings that shaped the final implementation scope. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The implementation report must show the NO-GO revision lifecycle was followed before source mutation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The bridge chain remains the governed durable record for this implementation and verification cycle. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation report must show changed files remained under `E:\GT-KB` and did not route unqualified GT-KB evidence to external or adopter repository paths. |

Minimum expected commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py -q --tb=short
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch complex status --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5039-watchdog-heartbeat-remediation --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5039-watchdog-heartbeat-remediation
```

The broader watchdog tests from the original proposal may be run as regression context, but they are no longer required mutation targets for this slice.

## Pre-Filing Preflight Subsection

Role and authority check:

- `groundtruth-kb/.venv/Scripts/gt.exe harness roles` resolved harness `A` (`codex`) as `prime-builder`.
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json` showed `gtkb-wi5039-watchdog-heartbeat-remediation` as latest `NO-GO` and Prime-actionable.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5039-watchdog-heartbeat-remediation` acquired draft claim rowid `30262` for session `2026-07-06T02-17-02Z-prime-builder-A-7d12ee`.

Applicability preflight:

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5039-watchdog-heartbeat-remediation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5039-watchdog-heartbeat-remediation-003.md --json`
- bridge_document_name: `gtkb-wi5039-watchdog-heartbeat-remediation`
- content_source: `.gtkb-state/bridge-revisions/drafts/gtkb-wi5039-watchdog-heartbeat-remediation-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

Clause preflight:

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5039-watchdog-heartbeat-remediation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5039-watchdog-heartbeat-remediation-003.md`
- Clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`
- Exit status: `0`

## Risks / Rollback

Risk is under-detecting a truly dormant watchdog if the freshness window is too loose. This revision uses the existing dispatcher-complex `DEFAULT_HEARTBEAT_STALE_SECONDS = 180.0`, which is 3x the installed one-minute cadence and remains stricter than the sibling monitor's larger window. Tests must retain a stale-above-window case so the remediation does not collapse into always-fresh behavior.

Rollback is a source/test revert of `dispatcher_complex.py` and `test_bridge_dispatch_complex.py`. No production deployment, credential mutation, destructive cleanup, or runtime-process merge is in scope.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`

## Recommended Commit Type

`fix`
