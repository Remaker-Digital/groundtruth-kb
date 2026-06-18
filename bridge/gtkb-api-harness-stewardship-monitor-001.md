NEW

Document: gtkb-api-harness-stewardship-monitor
Version: 001
Status: NEW
Date: 2026-06-18
From: Prime Builder (harness B / Claude)
To: Loyal Opposition
Project Authorization: PAUTH-WI4558-STEWARDSHIP-MONITOR-REPORT-ONLY
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4558
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b62b4604-b1fb-4fba-8106-a25898ac122e
author_model: claude-opus-4-8
author_model_version: Claude Opus 4.8
author_model_configuration: Claude Code interactive Prime Builder session; explanatory output style

# Ollama/OpenRouter harness stewardship monitor - report-only (Slice 1)

## Summary

Implement a report-only stewardship monitor for the Ollama (harness D) and
OpenRouter (harness F) API harnesses. The monitor fresh-reads the existing
heterogeneous state surfaces, detects MATERIAL status changes against a persisted
prior-state snapshot, scores stuck-work risk, and emits a regenerable status
report - so ongoing Ollama/OpenRouter integration work does not get lost or
stuck (the 2026-06-14 owner directive). It is strictly REPORT-ONLY: it performs
no auto-remediation, no auto-dispatch or auto-kill, and no paid external
pricing-API / credential / network calls (cost reporting uses existing static
config only), per the bounded authorization.

Optional doctor-check and `gt` CLI-subcommand exposure are DEFERRED to a
follow-on sub-slice; this slice delivers the monitor engine plus its tests.

## Specification Links

- GOV-HARNESS-ONBOARDING-CONTRACT-001 - the WI source spec and the contract whose
  required artifacts/capability-floor the monitor observes; cited in the
  governing authorization PAUTH-WI4558-STEWARDSHIP-MONITOR-REPORT-ONLY.
- GOV-STANDING-BACKLOG-001 - the monitor keeps owner-visible harness status
  aligned with the durable backlog (MemBase work-item/project state).
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 - the monitor fresh-reads canonical surfaces
  on each run rather than caching, consistent with the freshness contract.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the aggregation,
  change-detection, risk-scoring, and report-only tests derive from this.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites
  every relevant governing specification per this constraint.
- GOV-FILE-BRIDGE-AUTHORITY-001 - filed and tracked through the governed bridge
  protocol path with append-only versioning.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - the monitor and its decision
  trail are preserved as durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - the status snapshots are
  durable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - the monitor's status snapshot
  is a new durable artifact class, exercising artifact-lifecycle triggers.

## Prior Deliberations

<!-- reviewed -->

- DELIB-20265216 - the owner AskUserQuestion decision (2026-06-18) that unlocked
  WI-4558 and authorized minting the bounded report-only authorization from the
  2026-06-14 owner directive.
- WI-4558 source_owner_directive (2026-06-14) - the owner directed Prime Builder
  to take responsibility for ongoing Ollama/OpenRouter harness integration so
  work is not lost or stuck.
- gtkb-wi-4556-ollama-provider-fallback-backoff (related, distinct) - addressed
  the WI-4556 provider fallback/backoff path; explicitly does not cover the
  combined stewardship monitor (WI-4558).
- No direct prior deliberation exists on the stewardship-monitor implementation
  itself.

## Owner Decisions / Input

This proposal depends on owner approval, supplied by AskUserQuestion and recorded
as DELIB-20265216:

- AUQ id: AUQ-WI4558-UNLOCK-20260618.
- Owner answer: "Unlock a hard item (WI-4558)."
- Authorization granted: mint a bounded, report-only project authorization
  (PAUTH-WI4558-STEWARDSHIP-MONITOR-REPORT-ONLY) from the prior 2026-06-14 owner
  directive, then file this proposal and resume autonomous filing.
- Scope constraint set by the owner decision: report-only over existing
  surfaces; NO auto-remediation, NO auto-dispatch/auto-kill, NO paid external
  pricing-API / credential / network calls. Any of those remain separate owner
  decisions and are out of scope here.

## Requirement Sufficiency

Existing requirements sufficient. The monitor observes the artifacts that
GOV-HARNESS-ONBOARDING-CONTRACT-001 and GOV-STANDING-BACKLOG-001 already mandate
and reports status; it introduces no new or revised requirement or specification.
No policy/architecture sign-off is required (report-only; no behavior change to
dispatch or onboarding), and no destructive/deployment/credential action is in
scope (the bounded authorization forbids them).

## Problem / Background

Ollama (D) and OpenRouter (F) harness integration state is spread across many
surfaces with distinct parse/freshness models, so it is hard to tell at a glance
whether their work is healthy, stuck, or failing: the bridge state (versioned
files + INDEX), the harness registry + identities, the API-harness routing
config, the dispatch-poller JSONL family (dispatch-state with
circuit_breaker/backoff, dispatch-failures, suppressions, starvation telemetry),
live readiness, and MemBase work-item/project state. The 2026-06-14 owner
directive asked Prime Builder to steward this so work is not lost or stuck. No
single surface reports it; this monitor aggregates them read-only and surfaces
material changes and stuck-work risk.

## Proposed Change

Add a report-only monitor module scripts/api_harness_stewardship_monitor.py:

1. Surface readers (read-only, defensive): normalize the six surfaces -
   (a) bridge state (status-bearing versioned files + INDEX), (b) harness
   registry + identities, (c) the API-harness routing config, (d) the
   dispatch-poller JSONL family (dispatch-state circuit-breaker/backoff/
   failure-count, dispatch-failures, suppressions, starvation telemetry,
   handling JSONL rotation), (e) readiness (an injectable probe seam defaulting
   to a mock so tests and report-only runs make NO live network/paid call), and
   (f) MemBase work-item/project state for D and F via the groundtruth_kb API.
2. Material-change detection: persist a prior-state snapshot under
   .gtkb-state/api-harness-stewardship/ and report only material changes since
   the last snapshot (deterministic diff/dedup), so the report is quiet when
   nothing changed.
3. Stuck-work risk scoring: deterministic heuristics over circuit-breaker/backoff
   state, no_verdict failure classes, work-intent holds, starvation telemetry,
   and actionable-but-un-progressed bridge threads, producing a per-harness
   risk flag with cited evidence.
4. Cost/quality rollup from EXISTING static config (dispatcher rules
   dispatch_cost/dispatch_quality + the routing config) - no live pricing-API
   call.
5. Report emission: a regenerable status report (JSON + markdown summary) under
   .gtkb-state/api-harness-stewardship/<run_id>/. No mutation of any read
   surface.

target_paths: ["./scripts/api_harness_stewardship_monitor.py", "./platform_tests/scripts/test_api_harness_stewardship_monitor.py"]

## Verification Plan (spec-derived)

- Six-surface aggregation -> test: per-surface fixtures (bridge, registry,
  routing config, dispatch JSONL incl. a rotated file, mocked readiness, MemBase)
  are read and normalized into the status structure.
- Material-change detection -> test: given a prior snapshot, only material
  changes are reported; an unchanged run reports no material change.
- Stuck-work risk scoring -> test: circuit-breaker-tripped / no_verdict /
  un-progressed-actionable fixtures raise a risk flag with cited evidence; a
  healthy fixture does not.
- Report-only / no-mutation (the bounded authorization) -> AST/structural test:
  the module imports no live MemBase/bridge/dispatch MUTATING API, performs no
  network call (readiness probe is the injected mock in tests), and never
  auto-dispatches/remediates; it writes only under
  .gtkb-state/api-harness-stewardship/.
- Commands: groundtruth-kb/.venv/Scripts/python.exe -m pytest
  platform_tests/scripts/test_api_harness_stewardship_monitor.py -q ; plus ruff
  check and ruff format --check on the new files.

## Risk / Rollback

- Risk: a surface parser is brittle to format drift. Mitigation: each reader is
  defensive (missing/unreadable surface yields an absent/"unknown" sub-status,
  not a crash); read-only, so a misread degrades report completeness but cannot
  corrupt any surface.
- Risk: the readiness probe accidentally makes a live/paid call. Mitigation: the
  probe is an injected seam defaulting to mock; the report-only no-network test
  asserts no live call; the bounded authorization forbids paid pricing/credential/
  network calls.
- Rollback: delete the module and its test; the snapshot dir under .gtkb-state is
  regenerable runtime evidence. No data migration, no canonical state written.
- Blast radius: one additive module plus tests; read-only aggregation; no change
  to dispatch, onboarding, bridge, or MemBase behavior.

## Authorization

Authorized by PAUTH-WI4558-STEWARDSHIP-MONITOR-REPORT-ONLY (active; owner decision
DELIB-20265216; includes WI-4558 and GOV-HARNESS-ONBOARDING-CONTRACT-001; allowed
mutation classes source + test_addition; forbids auto_remediation,
auto_dispatch_or_kill, paid_pricing_api_call, credential_action,
live_external_network_call, deployment). Per the bridge protocol, source/test
implementation proceeds only after this proposal receives a Loyal Opposition GO
and a work-intent claim is taken. The report-only scope is enforced by the
authorization's forbidden-operations set and by the no-mutation/no-network tests.

## Recommended Commit Type

`feat:` - a net-new report-only stewardship-monitor subsystem plus tests, not a
defect repair or refactor.
