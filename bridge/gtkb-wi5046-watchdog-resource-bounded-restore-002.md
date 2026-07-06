GO
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-06T16-32-28Z-loyal-opposition-D-6c0bc8
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

# Loyal Opposition Proposal Review - WI-5046 Watchdog Resource-Bounded Restore Execution

bridge_kind: lo_verdict
Document: gtkb-wi5046-watchdog-resource-bounded-restore
Version: 002
Responds to: gtkb-wi5046-watchdog-resource-bounded-restore-001 (NEW, prime_proposal, Codex/A)
Reviewer: Loyal Opposition (Ollama, harness D, dispatcher-spawned headless)
Date: 2026-07-06 UTC
Verdict: GO

## Verdict Summary

GO. The proposal is technically sound, root-contained, and properly authorized under the active watchdog project envelope. All governance preflights pass with zero blocking gaps. The resource-bounding execution layer is correctly scoped as a consumer of WI-5045 policy decisions and does not broaden policy authorization.

## Positive Confirmations (verified; do not rework)

- **Authorization chain INTACT**: `PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION` is active in MemBase, maps to `PROJECT-GTKB-SERVICE-SOT-WATCHDOG`, and covers `WI-5046` with allowed mutation classes `["source", "tests"]`. The same authorization already received GO verdicts for WI-5043 (runner) and WI-5045 (tiered policy).
- **Spec-linkage completeness**: Cited specifications correctly cover all relevant requirements, including `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- **Preflights Pass**: Both the applicability preflight and the ADR/DCL clause preflight completed successfully with zero blocking gaps. The `missing_parent_dirs` warning for `resource_limits.py` is expected for a new-file proposal.
- **Requirement Sufficiency**: The proposal correctly states that existing specifications/requirements are sufficient for this resource-bounded execution slice. WI-5046 and `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` specify the load-aware, process-tree, probe-before-restore, and symptom-based success constraints.
- **Scope discipline**: The proposal explicitly states it "must not broaden policy authorization beyond the WI-5045 safe/canonical decision result," correctly positioning this slice as an execution wrapper that consumes policy decisions rather than reinterpreting them.

## Prime Builder Implementation Context

- **Windows Job Object abstraction**: The proposal correctly identifies the platform divergence (Windows Job Objects vs. cgroups) and commits to a clean abstraction with safe degradation when unavailable. Ensure the abstraction is a distinct class/interface rather than inline `if sys.platform` branches scattered through the execution path.
- **Probe-before-restore integration**: The resource-bounded execution wrapper must call the fresh availability probe itself (per DCL clause 4), not rely on a stale probe result passed in from the caller. The wrapper should accept a probe callable and invoke it immediately before the heavy restore, not reuse a cached diagnosis.
- **Symptom-based success, not load-threshold**: DCL clause 6 requires health to be judged by a failure-symptom probe (can the dependent critical operation proceed), not an aggregate-load threshold alone. The proposal mentions "deferred or throttled when the host is already under load" — ensure the implementation treats load as a gating/deferral input but uses a symptom probe as the success criterion, not a load metric.
- **Dependency on WI-5045**: The resource-bounded execution layer consumes WI-5045 policy decision objects. If WI-5045 is not yet implemented when this slice lands, provide a minimal decision-object stub or type definition so the resource-limits module can be developed and tested independently.
- **Test coverage**: The verification plan maps to `platform_tests/scripts/test_gtkb_service_sot_resource_limits.py`. Ensure tests cover: (a) deferral under simulated load, (b) process-tree cap application, (c) safe degradation when Job Objects are unavailable, (d) fresh-probe gating before restore, and (e) symptom-based success judgment.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized the full watchdog project (all 6 WIs) under the active project authorization.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected tiered auto-restore for safe/idempotent actions and fail-loud escalation for canonical/at-risk actions; this slice executes safe restores under resource bounds.
- `DELIB-20266276` - Dispatcher self-healing precedent includes auto-recovery but not unbounded host saturation; this slice closes that gap.

## Applicability Preflight

- packet_hash: `sha256:f5a0864ecbb0677866629d957b1321ca4656f74cf68f8a529a0029f831b3ca1a`
- bridge_document_name: `gtkb-wi5046-watchdog-resource-bounded-restore`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5046-watchdog-resource-bounded-restore-001.md`
- operative_file: `bridge/gtkb-wi5046-watchdog-resource-bounded-restore-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py", "groundtruth-kb/src/groundtruth_kb/watchdog/resource_limits.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py"]
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## ADR/DCL Clause Preflight

- Bridge id: `gtkb-wi5046-watchdog-resource-bounded-restore`
- Operative file: `bridge\gtkb-wi5046-watchdog-resource-bounded-restore-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory**. Exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Methodology Trail

Files inspected:
- `bridge/gtkb-wi5046-watchdog-resource-bounded-restore-001.md` (proposal under review)
- `bridge/gtkb-wi5043-service-sot-watchdog-runner-001.md` (WI-5043 proposal, GO'd)
- `bridge/gtkb-wi5043-service-sot-watchdog-runner-002.md` (WI-5043 GO verdict, harness C)
- `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md` (WI-5045 proposal, GO'd)
- `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-002.md` (WI-5045 GO verdict, harness C)
- `groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py` (existing watchdog package init)
- `groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py` (existing detection-only runner)
- `scripts/gtkb_service_sot_watchdog.py` (existing CLI wrapper)
- `harness-state/harness-identities.json` (identity resolution)
- `harness-state/harness-registry.json` (role resolution)

Commands run:
- `python scripts\bridge_claim_cli.py claim gtkb-wi5046-watchdog-resource-bounded-restore`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5046-watchdog-resource-bounded-restore`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5046-watchdog-resource-bounded-restore`
- `groundtruth-kb\.venv\Scripts\gt.exe spec show DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`
- `groundtruth-kb\.venv\Scripts\gt.exe spec show ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status`

## Owner Decisions / Input

None required. The project authorization is active and fully covers the scope of work. The owner's tiered-restoration policy decision (`DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED`) is correctly cited and scoped.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
