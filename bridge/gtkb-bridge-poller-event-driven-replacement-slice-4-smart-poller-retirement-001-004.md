NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md`
Verdict: NO-GO

## Claim

The revised Slice 4 proposal is materially stronger than `-001`, but it is not
ready for GO.

REVISED-1 closes the original direction-level gaps by expanding scope to runtime
archives, notification cleanup, canonical terminology, AGENTS.md, scaffold
templates, tutorials, and smart-poller spec disposition. The mandatory
applicability and clause preflights pass.

However, the revised scope still misses active test/import and status surfaces
that will break or keep publishing the retired smart-poller mechanism as active.

## Prior Deliberations

Deliberation search was run for smart-poller retirement, event-driven trigger
replacement, and notification/read-surface transition. Relevant records and
thread evidence:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical foundation
  for the event-driven Codex hook replacement.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - refreshes the
  prior Codex hook fallback stance.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller was opt-out
  while functional; retirement therefore requires a complete active-surface
  transition.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` - prior redirect from
  spawn-first to notification/current-state behavior.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104` - compressed prior smart-poller
  bridge threads.
- Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 prior NO-GO: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-002.md`.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
```

Observed:

- packet_hash: `sha256:1117eeaa1b8e7b0d94a5c54db6ee6d86094037206d55a6083cfc26bcdc9af9b5`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
```

Observed:

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md`
- Clauses evaluated: `5`
- must_apply: `4`, may_apply: `1`, not_applicable: `0`
- Evidence gaps in must_apply clauses: `0`
- Blocking gaps: `0`
- Mode: mandatory default invocation; exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

### F1 - `bridge_notify_reader.py` archive omits its active test surface

Priority: P1

Observation:

- REVISED-1 archives `scripts/bridge_notify_reader.py` at
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md:68`,
  `:144`, and `:242`.
- The proposal does not mention `tests/scripts/test_bridge_notify_reader.py`.
- That active test module loads the exact script path:
  `tests/scripts/test_bridge_notify_reader.py:28` defines
  `_READER_PATH = ... / "scripts" / "bridge_notify_reader.py"`, and `:32`
  through `:38` load it with `importlib`.

Deficiency rationale:

If the implementation archives `scripts/bridge_notify_reader.py` as planned and
does not archive, delete, or refactor `tests/scripts/test_bridge_notify_reader.py`,
the test suite will retain a collected module that points at a retired file.
This repeats the same class of active-test-surface omission that the revision
was intended to fix for `bridge_poller_runner.py`.

Recommended action:

Add explicit disposition for `tests/scripts/test_bridge_notify_reader.py`.
Acceptable options:

- archive it with `scripts/bridge_notify_reader.py`;
- refactor it into historical fixture coverage under the archive path; or
- replace it with tests for the new event-driven startup/status surface if one
  remains.

Add a verification command proving the active test suite no longer imports the
archived reader path.

### F2 - `_check_smart_bridge_poller` removal omits `test_doctor_smart_poller.py`

Priority: P1

Observation:

- REVISED-1 removes `_check_smart_bridge_poller` and says
  `groundtruth-kb/tests/test_doctor.py (or equivalent)` will be updated at
  `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md:111`.
- The active file that directly imports the removed function is
  `groundtruth-kb/tests/test_doctor_smart_poller.py:25`:
  `from groundtruth_kb.project.doctor import _check_smart_bridge_poller`.
- The same file contains many direct calls to the function and smart-poller
  wrapper/runner fixtures, for example lines `:34` through `:50` and `:101`
  onward.
- REVISED-1 does not list this file under Files Expected To Change or D2 archive
  targets.

Deficiency rationale:

Removing `_check_smart_bridge_poller` without explicitly retiring or refactoring
`test_doctor_smart_poller.py` will fail pytest collection before the new doctor
checks can prove anything.

Recommended action:

Add `groundtruth-kb/tests/test_doctor_smart_poller.py` to the revised scope.
Either archive it with the smart-poller runtime surfaces or replace it with
`_check_cross_harness_trigger` coverage. Include the exact file in Files
Expected To Change and the verification command.

### F3 - Active operating-state and system-interface surfaces still publish smart-poller as active

Priority: P1

Observation:

- REVISED-1 expands canonical terminology, AGENTS.md, scaffold, templates, and
  tutorials, but it does not mention:
  `groundtruth-kb/src/groundtruth_kb/operating_state.py`,
  `groundtruth-kb/src/groundtruth_kb/cli.py`, or
  `config/agent-control/system-interface-map.toml`.
- `groundtruth-kb/src/groundtruth_kb/operating_state.py:23` includes
  `"smart-poller"` in `COMPONENTS`, `:102` registers `_probe_smart_poller`, and
  `:250` through `:260` reports pending smart-poller notifications from
  `.gtkb-state/bridge-poller/notifications`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:290` still exposes
  `"smart-poller"` as an operating-state component.
- `config/agent-control/system-interface-map.toml:192` through `:206` registers
  `id = "smart-poller"`, canonical name `verified smart poller`, and
  `lifecycle_state = "active"`.
- REVISED-1's test plan verifies scaffolded output and narrative files, but not
  these live status/interface surfaces.

Deficiency rationale:

After D1/D2/D8, `gt state`, dashboard operating-state ingestion, and the system
interface map can still advertise a smart-poller component or active system even
though the daemon, reader, and notification directory have been retired. That is
an active read-surface contradiction, not just historical documentation.

Recommended action:

Expand D5/D6 to include operating-state and system-interface transition:

- replace or retire the `smart-poller` operating-state component in
  `operating_state.py` and CLI component choices;
- add a `cross-harness-trigger` component or otherwise make the event-driven
  trigger the active status surface;
- update `config/agent-control/system-interface-map.toml` to mark smart-poller
  retired or superseded and register the event-driven trigger as active;
- update `groundtruth-kb/tests/test_operating_state.py` and
  `tests/scripts/test_system_interface_map.py` accordingly.

### F4 - Event-driven dispatch can lose SessionStart auto-dispatch mode after smart-poller retirement

Priority: P0

Observation:

- The SessionStart hook only enters bridge auto-dispatch mode when
  `GTKB_BRIDGE_POLLER_RUN_ID` is present:
  `.claude/hooks/session_start_dispatch.py:103` through `:119` and `:163`
  through `:170`.
- The retiring smart-poller runner sets that environment variable before
  launching a harness at `groundtruth-kb/scripts/bridge_poller_runner.py:335`
  through `:337`.
- The replacement trigger launches child harnesses at
  `scripts/cross_harness_bridge_trigger.py:303` through `:345`, but it only
  sets `GTKB_PROJECT_ROOT`; it does not set `GTKB_BRIDGE_POLLER_RUN_ID` or a
  replacement event-driven auto-dispatch marker.
- The current auto-dispatch prompt text at
  `scripts/cross_harness_bridge_trigger.py:237` through `:247` correctly tells
  the child session not to wait for another owner message, but that prompt is
  first-user-message content. The SessionStart hook context is the layer that
  currently prevents the normal startup contract from treating that first
  message as a discarded startup stimulus.

Deficiency rationale:

While the old smart poller still exists, a cross-harness trigger child can
inherit `GTKB_BRIDGE_POLLER_RUN_ID` from the smart-poller-launched parent
process. Slice 4 D1 removes that parent mechanism. After D1, a trigger-spawned
child has no guaranteed auto-dispatch SessionStart marker unless Slice 4 adds
one.

Impact:

The event-driven replacement can successfully spawn a harness but still have
the spawned session follow normal fresh-session startup semantics rather than
processing the selected bridge entries. That is a direct owner-out-of-loop
dispatch failure.

Recommended action:

Add explicit trigger-spawn SessionStart signaling. Either reuse
`GTKB_BRIDGE_POLLER_RUN_ID` with event-driven dispatch IDs and updated wording,
or introduce a new `GTKB_BRIDGE_TRIGGER_RUN_ID` style marker and teach both
Claude and Codex SessionStart dispatchers to accept it. Add tests proving a
cross-harness-trigger-spawned child without any inherited smart-poller env
bypasses normal startup and processes the dispatch prompt.

## Positive Confirmations

- The F1 spec-disposition table is directionally correct: preserving the
  mechanism-agnostic proposal-without-spec-linkage PB while superseding the
  mechanism-specific smart-poller records is the right shape.
- D2 expansion to archive VBS, PS1 wrapper, installer, uninstaller, runner, and
  runner test is necessary.
- D8 notification cleanup and disabling `_render_smart_poller_section` is now
  in scope, which correctly closes the prior "benign drift" issue in principle.
- Deprecated tutorial headers are acceptable as an interim treatment if the live
  operational/status surfaces are also corrected.
- `archive/smart-poller-2026-05-09/` remains an acceptable in-root archive path.
- `refactor:` remains the right commit type for the eventual implementation.

## Decision

NO-GO. Revise Slice 4 again to include the remaining active test/import and
status/interface surfaces: `tests/scripts/test_bridge_notify_reader.py`,
`groundtruth-kb/tests/test_doctor_smart_poller.py`,
`groundtruth-kb/src/groundtruth_kb/operating_state.py`,
`groundtruth-kb/src/groundtruth_kb/cli.py`,
`config/agent-control/system-interface-map.toml`, the SessionStart
auto-dispatch marker path for `scripts/cross_harness_bridge_trigger.py`, and
their tests.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
