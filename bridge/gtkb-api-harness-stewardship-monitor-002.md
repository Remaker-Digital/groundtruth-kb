GO

bridge_kind: lo_verdict
Document: gtkb-api-harness-stewardship-monitor
Version: 002
Author: Loyal Opposition (Codex, session envelope ::init gtkb lo)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-api-harness-stewardship-monitor-001.md
Verdict: GO
Project Authorization: PAUTH-WI4558-STEWARDSHIP-MONITOR-REPORT-ONLY
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4558

# Loyal Opposition Review - API Harness Stewardship Monitor

## Verdict Summary

GO.

The proposal is approved. A report-only monitor for Ollama/OpenRouter harness state is directly useful while the LO dispatch lane is degraded, and the proposed scope is appropriately bounded: read existing surfaces, compare material status changes, score stuck-work risk, and emit regenerable reports without auto-remediation, auto-dispatch, credential use, paid API calls, or live network calls.

No blocking findings.

## Evidence Reviewed

- Proposal: `bridge/gtkb-api-harness-stewardship-monitor-001.md`.
- Owner authorization: `DELIB-20265216` / `PAUTH-WI4558-STEWARDSHIP-MONITOR-REPORT-ONLY`.
- Current dispatch health: LO lane is unhealthy with pending work and D provider backoff/circuit-breaker evidence, making report-only D/F stewardship relevant.
- Target paths: `scripts/api_harness_stewardship_monitor.py`, `platform_tests/scripts/test_api_harness_stewardship_monitor.py`.

## Findings

No blockers.

Advisory A1: The implementation must keep readiness probing injectable and mocked by default. Any live network call, paid pricing API call, credential action, auto-remediation, or auto-dispatch is outside this GO.

Advisory A2: Treat `.gtkb-state/api-harness-stewardship/` outputs as regenerable runtime reports, not canonical backlog or bridge authority. The monitor should cite canonical surfaces rather than become one.

## Prior Deliberations

- `DELIB-20265216` - owner AUQ unlocking bounded report-only stewardship monitor work.
- `WI-4558` - source owner directive for stewarding Ollama/OpenRouter harness integration.
- `gtkb-wi-4556-ollama-provider-fallback-backoff` - related but distinct fallback/backoff repair.

## Applicability And Clause Preflights

Applicability preflight passed for `gtkb-api-harness-stewardship-monitor`:

- packet hash: `sha256:c5190dfe9e5d37dd0a31da254d8b3b2f84a7acca12a2d335658606f9ebda0573`
- missing required specs: none
- missing advisory specs: none

ADR/DCL clause preflight passed:

- clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- blocking gaps: 0

## Required Implementation Evidence

Prime Builder should file a post-implementation report with:

- tests for all six read surfaces: bridge state, harness registry/identities, API harness routing config, dispatch JSONL/state files including rotation, mocked readiness, and MemBase work-item/project state;
- tests for material-change detection against a persisted prior-state snapshot;
- tests for stuck-work risk scoring with cited evidence;
- structural/no-mutation tests proving no live network call, paid pricing call, credential action, auto-dispatch, or auto-remediation path exists;
- proof that writes are limited to `.gtkb-state/api-harness-stewardship/`;
- focused pytest for `platform_tests/scripts/test_api_harness_stewardship_monitor.py`;
- ruff check and format checks for the new monitor and test files.

## Residual Risk

The main risk is parser drift across heterogeneous state surfaces. The proposal mitigates this by requiring defensive readers that degrade to unknown/absent sub-status rather than crashing or mutating source surfaces.

