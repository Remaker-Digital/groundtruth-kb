Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-4413, WI-4479, WI-4404, WI-4408, WI-4410

# WI-4413 FAB-01 Disposition Gap

Role: Loyal Opposition
Harness: Codex A
Automation: keep-working-lo
Date: 2026-06-13

## Claim

FAB-01 / WI-4413 should not be selected for another implementation pass. The
live bridge thread `gtkb-fab-01-dispatch-substrate-revival` is latest
`VERIFIED`, has no INDEX drift, and the targeted FAB-01 tests plus live harness
launchability check pass. The remaining gap is backlog disposition: MemBase
still reports WI-4413 as open/backlogged with no completion evidence.

## Evidence

- Durable role check: `python -m groundtruth_kb.cli harness roles` reports
  Codex harness `A` with role `loyal-opposition`.
- Bridge authority: `python .claude\skills\bridge\helpers\scan_bridge.py --role
  loyal-opposition --format json` reports `actionable: []` and summary
  `ADVISORY=13`, `GO=28`, `VERIFIED=195`, `WITHDRAWN=61`.
- Thread state: `python .claude\skills\bridge\helpers\show_thread_bridge.py
  gtkb-fab-01-dispatch-substrate-revival --format json --preview-lines 0`
  reports latest `VERIFIED:
  bridge/gtkb-fab-01-dispatch-substrate-revival-004.md`, no drift, and the full
  chain `NEW -> GO -> NEW -> VERIFIED`.
- Canonical INDEX evidence: `bridge/INDEX.md:501` through `:505` list the
  FAB-01 document block with `VERIFIED` at the top.
- Backlog evidence: `python -m groundtruth_kb.cli backlog list --id WI-4413
  --json` reports `resolution_status: open`, `stage: backlogged`,
  `approval_state: unapproved`, and `completion_evidence: null`.
- Owner-decision evidence: `python -m groundtruth_kb.cli deliberations get
  DELIB-FAB01-REMEDIATION-20260610` records the owner-approved FAB-01
  remediation choices for WI-4413: spawn-time argv normalization, launchability
  doctor check, capability-axis split, and gated 5-minute scheduled wake.
- Project-charter evidence: `python -m groundtruth_kb.cli deliberations get
  DELIB-FABLE-GRILL-20260610-Q7` records that cluster implementation still
  requires normal bridge proposal, LO GO, and implementation-start packet; the
  FAB-01 thread already completed that cycle.
- Related-work check: `python -m groundtruth_kb.cli backlog list --id WI-4413
  --id WI-4479 --id WI-4404 --id WI-4408 --id WI-4410 --json` shows WI-4404 is
  resolved, WI-4413 and WI-4479 are still open P1 bridge-dispatch rows, and
  WI-4408/WI-4410 remain low-priority advisory-routing rows.

## Verification

- `python -m pytest platform_tests\scripts\test_fab01_dispatch_substrate_revival.py platform_tests\scripts\test_single_harness_bridge_automation.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_single_harness_doctor_check_upgrade.py -q --tb=short`
  passed: 51 passed.
- `python scripts\bridge_applicability_preflight.py --bridge-id
  gtkb-fab-01-dispatch-substrate-revival` passed with
  `missing_required_specs: []`.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id
  gtkb-fab-01-dispatch-substrate-revival` passed with blocking gaps: 0.
- Direct launchability doctor call returned `pass` with message: `all 5 active
  dispatch target(s) launchable after argv-head normalization (codex, claude,
  antigravity, ollama, openrouter)`.

## Finding

Severity: P1 governance/backlog drift.

The bridge and code evidence show FAB-01 is complete, but the canonical backlog
still presents WI-4413 as an unfinished high-priority implementation item. That
creates duplicate-effort pressure: future autonomous runs can keep selecting
FAB-01 as open P1 work even though the bridge thread is terminal and targeted
verification passes. It also obscures the real remaining dispatch work, such as
WI-4479 or FAB-10 telemetry/claim-contract follow-through, by leaving a
completed cluster in the active queue.

## Recommended Action

Prime Builder should perform a governed backlog disposition for WI-4413 rather
than file another FAB-01 implementation proposal:

1. Mark WI-4413 resolved or superseded by
   `bridge/gtkb-fab-01-dispatch-substrate-revival-004.md`, with completion
   evidence citing the 51-pass targeted test run and live launchability PASS.
2. Review WI-4479 during that disposition. If the Codex headless startup crash
   is fully covered by the later Codex hook feature-flag repair plus FAB-01
   launchability verification, close or supersede it; otherwise restate the
   remaining scope so it no longer reads as the same launchability defect.
3. Leave WI-4408 and WI-4410 as advisory-routing backlog only unless Prime
   explicitly converts them into implementation work.

## Owner Decision Needed

No owner decision is required for this Loyal Opposition report. Any future
MemBase close/supersede mutation should use the normal governed approval path
required for backlog disposition.
