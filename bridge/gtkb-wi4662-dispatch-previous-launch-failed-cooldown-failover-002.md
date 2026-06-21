GO

author_identity:
  role: loyal-opposition
  harness_id: A
  harness_name: codex
  session_context_id: 2026-06-21T03-21-39Z-loyal-opposition-A-d60a9f
  dispatch_context: cross-harness-auto-dispatch
document: gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover
version: 002
responds_to: bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-001.md
date: 2026-06-21 UTC

# Loyal Opposition Verdict: WI-4662 Previous Launch Failure Cooldown Failover

## Verdict

GO.

Prime Builder may implement the scoped cooldown and failover fix for WI-4662.
The proposal is linked to active project authorization, targets bounded source
and test paths, and now has a satisfied dependency on WI-4703's VERIFIED
non-transient fast-trip work.

## First-Line Role Eligibility Check

Resolved harness identity and role were checked through the canonical harness
reader using:

`groundtruth-kb/.venv/Scripts/gt.exe harness roles`

The active harness is Codex harness `A` in `loyal-opposition` role. Under
`GOV-FILE-BRIDGE-AUTHORITY-001`, Loyal Opposition may author `GO`, `NO-GO`,
and `VERIFIED` bridge statuses. This `GO` verdict is role-eligible.

## Current Bridge State Check

Before acting, the selected thread was re-read from the status-bearing bridge
file chain. Latest status for this document remained `NEW` at
`bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-001.md`.
No later `GO`, `NO-GO`, `REVISED`, or `VERIFIED` file existed for this thread.

## Independence Check

The proposal was authored by Prime Builder context
`2026-06-18T16-08-27Z-prime-builder-B-600dda`. This review was performed in
the unrelated Loyal Opposition auto-dispatch context
`2026-06-21T03-21-39Z-loyal-opposition-A-d60a9f`. The review is not a same
session self-review.

## Applicability Preflight

Command:

`groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover`

Result:

- packet_hash: `sha256:f02feca675c975a0119a8d0823c7bef038daf14232e56a81fa5b85dd5d1f8556`
- content_path: `bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-001.md`
- operative_file: `bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs:
  `["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]`

Linked specs:

| spec_id | required | linked |
| --- | --- | --- |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | no | no |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | no | no |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | yes | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | yes | yes |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | no | no |
| GOV-FILE-BRIDGE-AUTHORITY-001 | yes | yes |

The required applicability gate is clean: no required specs are missing and
the script reported `preflight_passed: true`. The advisory omissions are not a
GO blocker for this implementation-scoped source/test change, but Prime Builder
should either cite the advisory artifact-governance specs in the implementation
report or state why no durable artifact lifecycle mutation occurred.

## ADR/DCL Clause Preflight

Command:

`groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover`

Result:

- operative_file:
  `bridge\gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-001.md`
- clauses_evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- evidence_gaps: `0`
- blocking_gaps: `0`
- mode: `mandatory`

Evaluated clauses:

| spec_id | clause_id | applicability | decision |
| --- | --- | --- | --- |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | CLAUSE-IN-ROOT | must_apply | yes |
| GOV-FILE-BRIDGE-AUTHORITY-001 | CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| GOV-STANDING-BACKLOG-001 | CLAUSE-VISIBILITY-BULK-OPS | may_apply | not applicable |

Clause preflight is clean: zero evidence gaps and zero blocking gaps.

## Prior Deliberations And Related Bridge Evidence

- `DELIB-20265459`: owner authorized the bounded WI-4565/WI-4662/WI-4701
  source/test implementation batch under
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002`.
- `DELIB-20265287`: owner corrected the automation value principle: avoid
  expensive repeated work without commensurate value, while cheap deterministic
  checks remain acceptable.
- `DELIB-20261120`: dispatch reliability critique and contention/deadlock
  context for prior dispatch failures.
- `DELIB-20263487`: cost-optimized autodispatch priority handoff context.
- `DELIB-20261075`: dispatcher investigation context showing the dispatch
  path works while post-dispatch quality/reliability needed tightening.
- `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-016.md`: VERIFIED
  closure for the proposal's declared dependency on non-transient fast-trip
  behavior.

## Positive Confirmations

- Backlog item `WI-4662` is open/backlogged and describes the same defect:
  repeated `previous_launch_failed` emission without cooldown or failover.
- Active project authorization
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002`
  includes `WI-4662`, is active, and allows source and test mutation.
- Strict target-path coverage preflight passed for the proposal content.
- Current target paths are bounded to:
  - `scripts/cross_harness_bridge_trigger.py`
  - `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py`
- `scripts/cross_harness_bridge_trigger.py` already contains the WI-4703
  fast-trip machinery (`FAST_TRIP_FAILURE_CLASSES` and
  `effective_trip_threshold`), so the WI-4662 implementation can integrate
  without reopening the completed dependency.

## GO Conditions

Prime Builder must keep implementation scope to the proposal's source and test
paths plus the follow-on implementation report:

- Modify only `scripts/cross_harness_bridge_trigger.py`,
  `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py`,
  and the follow-on bridge implementation report unless a revised proposal is
  filed.
- Do not mutate formal specs, GOV/ADR/DCL records, narrative artifacts,
  MemBase, dispatcher configuration, deployment files, credentials, or harness
  registry state under this GO.
- Preserve WI-4703 non-transient fast-trip behavior. Do not loosen
  `FAST_TRIP_FAILURE_CLASSES` or the single-attempt fast-trip threshold except
  for narrowly necessary integration with the cooldown/failover logic.
- Apply cooldown behavior at every `previous_launch_failed` re-recording
  chokepoint, including provider backoff and repeated dispatched-signature
  launch-failure paths.
- Clear cooldown/failure marker state after the relevant worker succeeds or
  the selected recipient changes such that the stale failure no longer applies.
- Add focused regression tests covering:
  - repeated `previous_launch_failed` detection does not launch or log every
    cycle inside the cooldown window;
  - cooldown expiry re-allows the expected attempt path;
  - same-recipient failover or exhaustion state is recorded deterministically;
  - WI-4703 fast-trip behavior remains intact.
- The implementation report must include spec-to-test mapping, cite the
  applicable deliberations above, and include the clean preflight results for
  any requested `VERIFIED` verdict.

## Verification Expected From Prime Builder

Run and report the focused and adjacent regression commands:

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py`

Dispatcher runtime health currently has unrelated recorded launch failures in
dispatch state; this GO does not require global dispatch-health `PASS` before
implementation starts. If Prime Builder claims the WI-4662 change repairs live
dispatch health, the implementation report must include a fresh
`gt bridge dispatch health --json` result after the change.

## Owner Action Required

None.
