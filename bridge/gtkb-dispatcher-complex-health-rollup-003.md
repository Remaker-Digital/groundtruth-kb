REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-05T10-44-22Z-prime-builder-A-d394b2
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex auto-dispatched Prime Builder worker; ::init gtkb pb; model gpt-5.5

# Revised Implementation Proposal - Slice 3 - health complex rollup

bridge_kind: prime_proposal
Document: gtkb-dispatcher-complex-health-rollup
Version: 003
Date: 2026-07-05 UTC
Responds-To: bridge/gtkb-dispatcher-complex-health-rollup-002.md

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5025

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_dispatcher_complex_control.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Response

This REVISED proposal addresses the P1 blocking finding in `bridge/gtkb-dispatcher-complex-health-rollup-002.md` by replacing the helper-stub `Prior Deliberations` section with concrete decision-history citations. No design or target-path change is made.

The P2 advisory dependency is preserved: Slice 3 still must not begin source implementation unless WI-5024 is VERIFIED. A fresh bridge state read during this revision found `gtkb-dispatcher-complex-command-group` latest `VERIFIED` at `bridge/gtkb-dispatcher-complex-command-group-004.md`; the implementation report must restate this dependency and cite the observed bridge state.

## Summary

Slice 3 of PROJECT-GTKB-DISPATCHER-COMPLEX-CLI: implement the complex-health rollup for `gt bridge dispatch health`, conditioned on WI-5024 verification.

Work item description: Refactor `gt bridge dispatch health` into a two-dimension aggregate verdict: (a) complex-lifecycle (daemon liveness + supervisor + watchdog task-state + heartbeats), (b) existing routing/config findings. Define per-component WARN/FAIL severity. Per ADR-DISPATCHER-COMPLEX-CLI-001 decisions 3-4.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5025` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any future membership or PAUTH-state correction would require explicit owner-decision evidence before it could broaden implementation authority.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_dispatcher_complex_control.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

## Specification Links

- `SPEC-INTAKE-5e9375` - owner requirement for a harmonized dispatcher daemon complex management CLI and unified complex-health contract; explicitly constrains this slice to control-plane and observability harmonization only.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - architecture decision for the unified control-plane CLI and complex-health rollup; this slice implements decisions 3 and 4.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable artifact preservation for decisions, plans, and review findings.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - governs owner-decision evidence through AskUserQuestion-derived records.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - preserves MemBase work item and backlog authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant to Codex self-enforcement and hook-parity fallback during bridge filing.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governs artifact-first development and durable rationale capture.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - defines when plans, review findings, and accepted future work become durable artifacts.
- `ADR-DISPATCHER-ARCHITECTURE-001` - preserves the persistent daemon, external supervisor, storm watchdog, and harness-isolation architecture; no runtime process merger is allowed.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - constrains supervisor liveness and scheduled-task health semantics.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - constrains centralized dispatcher visibility and health/status/report surfaces.

## Prior Deliberations

- `DELIB-202665481` - owner AUQ authorization for `PROJECT-GTKB-DISPATCHER-COMPLEX-CLI`, including PAUTH coverage for WI-5023 through WI-5026 and the explicit prohibition on merging daemon, supervisor, and watchdog runtime processes.
- `DELIB-202665470` - owner AUQ decision to resume GT-KB dispatch and re-enable dispatcher supervision plus storm-watchdog containment; this decision surfaced the health-fragmentation that Slice 3 remediates.
- `SPEC-INTAKE-5e9375` / intake source `INTAKE-6554ff58` - the requirement candidate formalized into the dispatcher daemon complex management and health-rollup requirement.
- `DELIB-20266276` - daemon-resilience scope-lock preserving dedicated supervision, storm containment, degraded continuity, and deterministic testing constraints that this rollup must continue to respect.

## Owner Decisions / Input

- `DELIB-202665481` records the AskUserQuestion-backed owner authorization for the project PAUTH named above. That authorization covers `WI-5025` once a Loyal Opposition `GO` exists and Prime Builder obtains implementation-start authorization.
- No new owner decision is required for this revision. The only blocking review finding was the missing Prior Deliberations citation set.

## Proposed Scope

- Condition any implementation on WI-5024 latest VERIFIED; if WI-5024 is superseded by a later non-terminal bridge state before implementation starts, stop this slice and revise the proposal instead of building on an unverified surface.
- Refactor `gt bridge dispatch health` into a two-dimension aggregate: complex lifecycle (daemon, supervisor, watchdog) and existing routing/config health findings.
- Add per-component WARN/FAIL severity rules for daemon liveness, supervisor task state, watchdog task state, and heartbeat freshness without merging the three runtime processes.
- Keep `gt bridge dispatch complex status/health` and direct daemon/supervisor/watchdog commands available; preserve lifecycle-first/scoring-last precedence and make no lane scoring changes.
- Keep dispatcher report and status JSON consumers aligned with the new health shape while preserving existing routing/config findings.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-5e9375` | Focused CLI tests prove the health rollup exists and is owner-facing through `gt bridge dispatch health` plus complex health. |
| `ADR-DISPATCHER-COMPLEX-CLI-001` | Tests verify ADR decisions 3 and 4: two-dimensional aggregate health and per-component WARN/FAIL severity. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Candidate and live bridge applicability preflights must pass; implementation report must carry targeted test evidence. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The implementation report must preserve the proposal/report/verdict evidence chain and the review finding response. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight must report no missing required or advisory specification links for this proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each material linked spec to executed tests and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance and implementation-start authorization must validate PAUTH, project, work item, and target paths. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner-decision evidence remains cited through the project PAUTH deliberation and no prose-only decision dependency is introduced. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target-path validation and implementation diff review must confirm all work remains inside GT-KB platform paths. |
| `GOV-STANDING-BACKLOG-001` | Implementation report must cite `WI-5025` and leave MemBase status mutation to governed follow-on workflow. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex uses helper-mediated bridge filing and self-enforces role/status authority before writes. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Proposal, implementation report, and verification preserve rationale and review findings as durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The NO-GO response and revised proposal preserve the review-finding lifecycle transition. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests verify daemon, supervisor, and watchdog remain separate components and no lifecycle command merges their runtime responsibilities. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Supervisor/watchdog existing regression tests continue to pass alongside the new complex-health tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch health/status/report` smoke or focused tests prove central dispatcher visibility is preserved. |

## Pre-Filing Preflight Subsection

Prime Builder runs the governed revision helper path for this completed body:

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/revise_bridge.py file gtkb-dispatcher-complex-health-rollup --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-complex-health-rollup-003.completed.md
```

That helper performs credential scanning, candidate applicability preflight, candidate ADR/DCL clause preflight, bridge status validation, and TAFE-backed publication before writing `bridge/gtkb-dispatcher-complex-health-rollup-003.md`. The expected clean conditions are `missing_required_specs: []`, `missing_advisory_specs: []`, and zero blocking clause gaps; any non-zero preflight exit fails closed before live filing.

Candidate self-check evidence before filing:

- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatcher-complex-health-rollup --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-complex-health-rollup-003.completed.md --json` exited 0 with `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`.
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatcher-complex-health-rollup --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatcher-complex-health-rollup-003.completed.md` exited 0 with `Evidence gaps in must_apply clauses: 0` and `Blocking gaps (gate-failing): 0`.

## Acceptance Criteria

- No source implementation starts until WI-5024 is VERIFIED; the implementation report restates this dependency and cites the observed bridge state.
- `gt bridge dispatch health --json` reports both complex_lifecycle and routing_config dimensions, with an aggregate health_status that escalates WARN/FAIL deterministically.
- Complex lifecycle WARN/FAIL findings identify the affected component and reason; routing/config findings remain visible and are not hidden by lifecycle rollup.
- Existing complex status/health and direct component commands continue to work; no daemon/supervisor/watchdog process merger is introduced.
- Focused CLI/report/dispatcher tests and ruff gates pass.

## Risks / Rollback

Risk is moderate because this proposal authorizes later protected-file work after GO. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, implementation-start authorization, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_dispatcher_complex_control.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
