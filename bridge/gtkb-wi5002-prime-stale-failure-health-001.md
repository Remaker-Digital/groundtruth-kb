NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-04T02-31-00Z-prime-builder-A-interactive-stale-health
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex interactive Prime Builder; dispatcher-control bridge stability goal; no direct harness launch

# WI-5002 Prime Stale Failure Health Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi5002-prime-stale-failure-health
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: dispatcher-health-state-reconciliation, prime-work-intent-suppression, focused-tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Proposal Claim

During the WI-5002 bridge-stability soak, the dispatcher remained in `WARN` after an expired Prime Builder work-intent holder was released. The live `prime-builder:A` recipient had no live A worker and no active claim for `gtkb-wi4975-claimed-path-subpath-overmatch`, yet dispatcher health still reported:

- `dispatch runtime failure: prime-builder:A failure_class=subprocess_execution_failed with pending_count=1`
- `dispatch runtime warning: prime-builder:A last_result=unchanged with pending_count=1`

The current state evidence shows a stale-failure accounting defect rather than active Codex work:

- `python scripts/bridge_claim_cli.py status gtkb-wi4975-claimed-path-subpath-overmatch` first reported an expired draft claim from `2026-07-03T22-32-16Z-prime-builder-A-62cf7d`; after governed release, it returned `null`.
- `gt bridge dispatch report --json` still classified `prime-builder:A` as `FAIL`, with `failure_class=subprocess_execution_failed`, `last_launch.reason=work_intent_already_held`, `last_result=unchanged`, `pending_count=1`, and no live A worker.
- `scripts/gtkb_dispatcher_daemon.py` has an `unchanged` branch for Prime fanout that updates `last_result`, `pending_count`, and `selected_count`, but does not clear older `failure_class` / `last_failure_reason` evidence.
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` then treats the retained `failure_class` as live failure evidence when pending work remains.

This proposal authorizes a focused repair so benign Prime dedupe / work-intent contention states cannot keep dispatcher health degraded after the actual holder or failed launch evidence is gone.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, the active WI-5002 stability goal, and the existing dispatcher-health/bridge protocol rules already require unattended headless processing to distinguish live failures from stale history. No new or revised requirement is needed before implementation.

If Loyal Opposition determines that the WI-5002 PAUTH is too narrow for this dispatcher-health accounting repair, it should issue `NO-GO` with an authorization-scope finding rather than approving implementation.

## Owner Decisions / Input

Owner direction in this session authorizes the operational goal: enable the bridge and keep testing and fixing until it is stable and processing headlessly without intervention, using Claude Code and Ollama as active LO targets and Codex as active PB. The same owner direction also prohibits direct harness-to-harness fallback, so this repair must preserve dispatcher-mediated routing and must not directly trigger a Codex, Claude Code, Antigravity, or Ollama worker.

No new owner decision is required for this proposal. It does not request credential changes, production deployment, durable role reassignment, retired poller restoration, broad sandbox bypass, or direct harness invocation.

## In-Root Placement Evidence

All target paths are inside `E:/GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

Out-of-root writes, raw runtime-state mutation, direct worker launch, retired poller restoration, credential mutation, production deployment, and durable role reassignment are out of scope.

This proposal will be filed as `bridge/gtkb-wi5002-prime-stale-failure-health-001.md`, the first versioned bridge file in this append-only numbered bridge chain. Prior bridge files are not deleted, rewritten, or treated as live state substitutes.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher health must reflect true unattended processing state, not stale failure residue after a holder clears.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - recovery must remain dispatcher-mediated and must not directly trigger another harness as a fallback.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the fix must preserve the numbered bridge chain and dispatcher-backed state as workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal declares target paths, requirement sufficiency, and a spec-derived verification plan before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include focused tests proving stale health clears and genuine failures still degrade health.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must begin only after a live `GO` and implementation-start authorization packet.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live soak finding is preserved as durable bridge evidence instead of manual state surgery.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - rejected alternatives and observed failure modes remain explicit in the bridge record.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated live dispatcher-health drift during the stability goal triggers this lifecycle repair.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner goal for stable unattended headless bridge processing with Codex as active PB and Claude Code/Ollama as active LO.
- `bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-*` - Prime Builder fanout dispatcher work established per-document signature routing and fanout state.
- `bridge/gtkb-wi4995-document-lease-held-health-*` - related stale-health repair for document-lease-held non-launch evidence.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-*` and `bridge/gtkb-wi5002-codex-headless-add-dir-invocation-*` - live WI-5002 chain that exposed Codex PB dispatch blockers during stability soaking.

## Proposed Implementation

1. Add a dispatcher-health regression for the observed state: pending Prime work, no live Prime worker, no active work-intent holder, current `last_result=unchanged`, `last_launch.reason=work_intent_already_held`, and retained `failure_class=subprocess_execution_failed`. Expected result: stale failure evidence is ignored or cleared and health does not report `FAIL`.
2. Repair the state accounting path so benign Prime `unchanged` / `work_intent_already_held` non-launches do not preserve old `failure_class` / `last_failure_reason` as live health evidence after the holder clears.
3. Preserve genuine failure behavior: active subprocess failures, non-retryable failures, circuit breaker trips, launchability failures, and pending work with real failed launch evidence must still degrade health.
4. Ensure per-document signature dedupe remains intact for already-dispatched live work, while expired or released work-intent contention remains retryable or health-neutral as appropriate.
5. Add focused daemon/runtime/report tests covering the regression and the preserved failure cases.

## Verification Plan

The implementation report must include spec-to-test mapping and exact observed results for:

- `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py`

Acceptance criteria:

- A state equivalent to the observed live WI-4975 stale-holder case no longer reports dispatcher health `FAIL`.
- Releasing an expired work-intent holder does not leave the Prime recipient stuck in stale failure health.
- `work_intent_already_held` remains a suppression/backpressure condition, not an actionable subprocess failure.
- The repair does not clear or hide genuine currently actionable runtime failures.
- No implementation path directly launches another harness or mutates dispatcher runtime JSON by hand.

## Risk And Rollback

Risk is medium because dispatcher health classification is a release/readiness signal. The fix must be narrowly tested so it does not mask real failures. Rollback is conventional git revert of the source/test changes; no data migration is proposed.

## Pre-Filing Preflight

Content-file preflight was run before live filing against `.gtkb-state/bridge-propose-drafts/gtkb-wi5002-prime-stale-failure-health-body.md`:

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-prime-stale-failure-health-body.md --json`
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
  - `packet_hash: sha256:76293f9d08c8802fe8d00676c9e8fbd7c34519e00e40a9f200d0f40be6e4d8f0`
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5002-prime-stale-failure-health-body.md`
  - `Blocking gaps: 0`
  - `Evidence gaps in must_apply clauses: 0`
