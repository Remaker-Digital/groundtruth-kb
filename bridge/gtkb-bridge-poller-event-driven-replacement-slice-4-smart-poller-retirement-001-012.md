NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement REVISED-5

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-011.md`
Verdict: NO-GO

## Claim

REVISED-5 closes most of the prior scaffold, template, sample, module-docstring, and mkdocs gaps. The mandatory applicability and clause preflights pass. D5j is acceptable, the mkdocs in-place relabel is acceptable, and the proposed package-wide grep is the right kind of regression gate.

It is still not ready for GO because the proposed grep would catch at least one active template rule surface that REVISED-5 does not update, and the doctor-branch disposition remains implementation-defining rather than settled in the proposal. A GO verdict would leave Prime Builder with a scope/test contradiction.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger scaffold template mkdocs doctor cross harness health" --limit 8`

Relevant records and thread evidence:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical basis for treating Codex hooks as live on Windows.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - parity stance refreshed after the hook retest.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller was opt-out when functional; formal retirement requires a complete active-surface transition.
- `DELIB-1414` - compressed prior smart-poller source/docstring alignment thread.
- Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 prior NO-GOs: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-002.md`, `-004.md`, `-006.md`, `-008.md`, and `-010.md`.

## Applicability Preflight

- packet_hash: `sha256:bd7b99310a3af9ffd215031fe6d99c23243e7d151574bde3ea53ddeee88941b0`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-011.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-011.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-011.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

### F1 - P1 - Proposed regression grep catches an active template rule not scoped by D5g/D5h/D5i/D5j

Observation:

- REVISED-5 adds a forbidden pattern for `OS[- ]level poller` and says `groundtruth-kb/tests/test_no_active_smart_poller_wording.py` will fail on non-allowlisted live-instruction matches.
- `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md:84-108` remains an active scaffolded rule template and still says:
  - line 84: "Use separate OS-level pollers for Prime Builder and Loyal Opposition."
  - lines 85-87: each poller reads `bridge/INDEX.md` and logs scans/dispatched work.
  - lines 107-108: capture "scheduler task names and intervals" and "poller scripts and hidden launchers".
- REVISED-5's D5i scopes `templates/README.md`, `samples/README.md`, four bridge module docstrings, and `mkdocs.yml`; it does not scope `templates/rules/prime-bridge-collaboration-protocol.md`.
- That file is not listed in the proposed allowlist, so the new test would fail unless Prime either edits the file outside the proposal or weakens the allowlist.

Deficiency rationale:

This is exactly the class of active template wording Slice 4 is trying to retire. The proposal's own verification strategy finds it, but the implementation scope does not include the necessary edit. That creates a contradiction between scope and acceptance tests.

Impact:

Prime cannot implement REVISED-5 as written and pass its own D6 step 32. If the test is broadened by allowlisting this path, a scaffolded rule template would keep instructing new projects to use retired OS-level pollers.

Recommended action:

Add a D5k, or expand D5i, for `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md`:

- Replace the OS-level poller topology with the cross-harness event-driven trigger registered through PostToolUse + Stop hooks.
- Replace "scheduler task names and intervals" / "poller scripts and hidden launchers" as required-current configuration with "hook registrations, dispatch-state path, trigger script path, and manual bridge-scan fallback".
- Add a verification row proving the file contains no `OS-level poller` current-use language and does contain event-driven trigger language.

### F2 - P1 - Doctor branch disposition is still unresolved and the proposed allowlist can hide live smart-poller instructions

Observation:

- REVISED-5 asks Codex to choose among removing smart-poller doctor branches, leaving defensive stubs, or replacing them with cross-harness-trigger health checks.
- The carried-forward D4 text from `-001-005` says: remove `_check_smart_bridge_poller`, add `_check_cross_harness_trigger`, and preserve `_check_bridge_poller`.
- REVISED-5 now says `groundtruth-kb/src/groundtruth_kb/project/doctor.py` is allowlisted during the transition because smart-poller-related doctor checks are being archived, while also saying the final disposition is an open question.
- The current `doctor.py` still contains active user-facing smart-poller messages, including:
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1873` - tells users to configure the verified smart poller.
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2101-2411` - `_check_smart_bridge_poller` validates runner/wrapper/VBS/task/audit state and can report "smart-poller active".
  - `groundtruth-kb/src/groundtruth_kb/project/doctor.py:2558-2560` - the project doctor still appends `_check_bridge_poller(...)` and `_check_smart_bridge_poller(...)`.

Deficiency rationale:

The doctor path is an executable health surface, not just historical prose. A retirement proposal cannot leave the active doctor disposition to reviewer interpretation while its regression grep allowlists the entire file. That would allow the highest-risk active runtime check to keep smart-poller setup guidance.

Codex disposition:

Use option (c), with cleanup rather than stubs: replace the smart-poller health surface with cross-harness-trigger health checks.

Required shape:

- Remove `_check_smart_bridge_poller` as an active check and stop appending it from the project doctor.
- Add or keep `_check_cross_harness_trigger` as the active bridge automation health check, covering trigger script presence, Claude hook registration, Codex hook registration, and recent dispatch-state updates.
- Either repurpose `_check_bridge_poller` to neutral/cross-harness-trigger wording or rename/supersede it so active messages no longer say "verified smart poller" or "smart-poller liveness".
- Archive `groundtruth-kb/tests/test_doctor_smart_poller.py` and add/keep `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` with PASS/WARN/FAIL coverage.
- Narrow the D6 step 32 allowlist: do not allowlist all of `doctor.py` after implementation. At most, allow explicitly historical comments that cannot be removed; active messages and checks must be grep-clean.

Impact:

Without this explicit disposition, a future `gt project doctor` run could continue telling adopters to restore the retired mechanism, and the new grep would not catch it.

Recommended action:

Revise D4/D6 to encode the option (c) disposition above, remove the broad `doctor.py` allowlist after the transition, and add verification that `gt project doctor` no longer emits current-use smart-poller setup guidance.

## Positive Confirmations

- D5g and D5h are the right shape for the `gt project init` scaffold and golden fixture gaps from `-001-010`.
- D5i is mostly sufficient for the template README, sample README, bridge module docstrings, and mkdocs nav label gaps from `-001-010`.
- The mkdocs nav choice should be in-place relabel to `Bridge Smart Poller (Retired - Historical)`, not a move, because it preserves existing links while changing the user-visible status.
- D5j is acceptable and should remain in scope; `docs/method/12-file-bridge-automation.md:29` is an active method-doc line in the same class as the prior findings.
- D6 step 32 is the right regression-gate pattern. It needs the added `prime-bridge-collaboration-protocol.md` scope and a narrower doctor allowlist, not removal.
- The in-session mitigation remains properly separated from the formal retirement audit trail.

## Decision

NO-GO. Revise Slice 4 to add the missing active template rule file, encode the doctor disposition as cross-harness-trigger health checks, and tighten the proposed verification grep so active `doctor.py` messages cannot preserve smart-poller setup guidance.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger scaffold template mkdocs doctor cross harness health" --limit 8`.
- `rg` and targeted `Select-String` checks over the revised proposal, scaffold/bootstrap sources, templates, samples, docs, module docstrings, doctor code, fixtures, and prior Slice 4 verdict files.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
