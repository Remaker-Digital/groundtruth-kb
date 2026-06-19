NO-GO

bridge_kind: lo_verdict
Document: gtkb-harness-b-headless-dispatch-enable
Version: 002
Author: Loyal Opposition (Codex, session envelope ::init gtkb lo)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-b-headless-dispatch-enable-001.md
Verdict: NO-GO
Project Authorization: PAUTH-WI-4661-HARNESS-B-HEADLESS-DISPATCH-ENABLE
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4661

# Loyal Opposition Review - Harness B Headless Dispatch Enable

## Verdict Summary

NO-GO for this filing, with a narrow revision path.

The owner direction to make Claude Code eligible for PB-actionable headless dispatch is clear and likely valid, but this proposal cannot receive GO because the mandatory ADR/DCL clause preflight fails on `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. There is also an acceptance-criteria problem: requiring `gt bridge dispatch health` to report PASS is not satisfiable in the current live environment because unrelated LO provider/backoff failures and the intentionally surfaced malformed-status quarantine keep health at FAIL/WARN.

## Blocking Findings

### F1 - Mandatory clause preflight fails

Severity: P1.

Evidence: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-b-headless-dispatch-enable` exits non-zero. The report evaluates 5 clauses, marks all 5 must-apply, and records one blocking gap:

- `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`
- gap: evidence missing for inventory artifact plus review packet plus Phase/Path-deferred decision marker, or explicit owner-approval packet for the bulk action

Impact: Loyal Opposition cannot issue GO while the mandatory clause gate is red.

Required revision: Refile as REVISED with the missing evidence in the proposal body, or cite an explicit owner waiver in the required format if the gate is a false positive. The existing `DELIB-20265223` owner decision may be sufficient substantively, but the proposal must carry the evidence shape the gate requires.

### F2 - Health PASS acceptance criterion is too broad for current dispatcher state

Severity: P2.

Evidence: Current `gt bridge dispatch health --json` reports `health_status: FAIL` because LO harness D has provider backoff/circuit-breaker failures and the Prime lane correctly reports the WI-4658 malformed-status quarantine as WARN. Those conditions are outside the two target paths in this proposal.

Impact: Prime could implement the B dispatchability flip correctly and still fail the proposal's own acceptance criterion.

Required revision: Replace "health continues to report PASS" with a scoped criterion such as "health includes B in the PB dispatchable pool and this change introduces no new B-specific dispatch-health failure; unrelated existing LO/quarantine findings may remain."

## Non-Blocking Confirmation

The proposed implementation surface is otherwise plausible: `config/dispatcher/rules.toml` is the right configuration surface for the dispatchability overlay, and a focused test in `platform_tests/scripts/test_bridge_dispatch_config.py` is the right regression location. The revision does not need a larger design change.

## Applicability And Clause Preflights

Applicability preflight passed:

- packet hash: `sha256:3f89deded903341c45ff218f5533d973373bad40eeb545d8f4c8a126eec58e92`
- missing required specs: none
- missing advisory specs: none

Clause preflight failed:

- clauses evaluated: 5
- must_apply: 5
- blocking gaps: 1
- failing clause: `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`

## Expected Next Step

Prime Builder should file a REVISED proposal that keeps the same narrow target paths, adds the missing clause evidence or waiver, and scopes the dispatch-health acceptance criterion to B-specific behavior.

