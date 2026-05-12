NO-GO

# Loyal Opposition Review - Single-Harness Bridge Dispatcher Slice 2

bridge_kind: loyal_opposition_verdict
Document: gtkb-single-harness-bridge-dispatcher-slice-2
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-12 UTC
Reviewed file: `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`
Verdict: NO-GO

## Claim

The proposal is mechanically well-formed and the mandatory preflights pass, but
it is not ready for implementation. The plan relies on runtime mutual exclusion
between the cross-harness trigger and the new single-harness scheduled-task
dispatcher, yet it does not include the trigger-side applicability gate or test
coverage needed to make that mutual exclusion true. It also has concrete
scheduled-task command and test-isolation defects that would make the first
implementation likely to fail or mutate the owner's real scheduled task during
tests.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from
  `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed
  `gtkb-single-harness-bridge-dispatcher-slice-2` latest status as
  `NEW: bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review:

- `single harness bridge dispatcher slice 2 scheduled task active session signature dedup`
  returned trigger and dispatcher history including `DELIB-1535`,
  `DELIB-1568`, `DELIB-1550`, `DELIB-1536`, `DELIB-1511`,
  `DELIB-1566`, `DELIB-1544`, `DELIB-1532`, `DELIB-1499`, and
  `DELIB-1643`.
- `single harness dispatcher desktop task DCL Windows launchd cron`
  returned related substrate and dispatcher review history including
  `DELIB-1511`, `DELIB-1516`, `DELIB-1536`, `DELIB-1550`,
  `DELIB-1499`, `DELIB-1515`, `DELIB-1549`, `DELIB-1535`,
  `DELIB-1544`, and `DELIB-1643`.
- `bridge essential single harness dispatcher narrative artifact approval`
  returned bridge/substrate and narrative-approval history including
  `DELIB-1883`, `DELIB-1511`, `DELIB-0484`, `DELIB-1522`,
  `DELIB-2076`, `DELIB-1577`, `DELIB-1567`, `DELIB-1412`,
  `DELIB-1503`, and `DELIB-1575`.

The prior deliberations support a host-scheduled single-harness substrate and
active-session suppression, but they do not waive the proposal's need to prove
runtime coexistence and test isolation.

## Applicability Preflight

- packet_hash: `sha256:a8a9ecb29452053c4b16fe91dc139285b50071b4eda5beafb6f960db1a658a8d`
- bridge_document_name: `gtkb-single-harness-bridge-dispatcher-slice-2`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`
- operative_file: `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-single-harness-bridge-dispatcher-slice-2`
- Operative file: `bridge\gtkb-single-harness-bridge-dispatcher-slice-2-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Mutual-Exclusion Claim Is Not Implemented Or Tested

Observation: The proposal says the dispatcher and the cross-harness trigger can
share `.gtkb-state/bridge-poller/` safely because "the two substrates are
mutually exclusive at runtime" (`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:109`).
It also asks Loyal Opposition to confirm that state-path sharing is safe given
applicability mutual exclusion (`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:313`).

The cited Slice 1 SPEC is stricter: in single-harness topology, "the
cross-harness trigger is registered but spawns nothing" and the two substrates
are mutually exclusive at runtime
(`scripts/_build_spec_single_harness_bridge_dispatcher_packet.py:87-92`).

Evidence: The current cross-harness trigger does not have that single-harness
inertness gate. Its `_resolve_dispatch_target` uses role-set membership and
returns a target when exactly one harness record contains the requested role
(`scripts/cross_harness_bridge_trigger.py:588-604`, `:607-638`). In a
single-harness role-set record containing both roles, that resolution succeeds
for both `prime-builder` and `loyal-opposition`; it does not fail as "no
counterpart resolves." The command builder can then construct a normal
`codex exec` or `claude -p` invocation (`scripts/cross_harness_bridge_trigger.py:380-403`).

I reproduced the behavior with an in-root temporary scratch project and
`scripts.cross_harness_bridge_trigger.run_trigger(..., dry_run=True)`. With a
single `NEW` entry and a single harness record `A: ["prime-builder",
"loyal-opposition"]`, the dry-run result selected `codex exec` for
`loyal-opposition` rather than reporting a missing counterpart. With both a
`NEW` and a `NO-GO` entry pending, the same dry-run selected `codex exec` for
both `loyal-opposition` and `prime-builder`.

Impact: Slice 2 would add a scheduled-task dispatcher while leaving the
event-driven trigger capable of resolving the same harness in single-harness
topology. The proposal's state-sharing and loop-prevention rationale therefore
rests on an unproven assumption. This is exactly the kind of dispatch-loop and
double-dispatch failure the Slice 2 proposal is supposed to avoid.

Recommended action: Revise the scope to include either:

1. a cross-harness-trigger topology gate that makes the trigger inert in
   single-harness multi-role-set topology, plus a regression test such as
   `test_cross_harness_trigger_noop_in_single_harness_topology`; or
2. a revised formal rationale that explicitly allows both substrates to resolve
   the same harness and proves with tests that active-session suppression plus
   signature state prevents duplicate dispatch under stale/missing lock
   conditions.

Without one of those, the proposed implementation does not satisfy
`SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` coexistence semantics.

### F2 - P1 - Scheduled Task Action Points At The Wrong Script Path

Observation: The installer plan says the task action will invoke
`python single_harness_bridge_dispatcher.py` while the working directory is the
GT-KB project root (`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:116-120`).
The file expected by the same proposal is `scripts/single_harness_bridge_dispatcher.py`
(`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:97`,
`:263`).

Impact: A Windows scheduled task with working directory `E:\GT-KB` and action
`python single_harness_bridge_dispatcher.py` will not find the script. That
would make the core Slice 2 runtime nonfunctional even if the task registers
successfully.

Recommended action: Revise IP-2 to use an explicit rooted script path, for
example `python E:\GT-KB\scripts\single_harness_bridge_dispatcher.py
--project-root E:\GT-KB`, or invoke through the same Python interpreter/path
resolution discipline used by the repo's other scripts. Add an installer test
that asserts the task action references `scripts\single_harness_bridge_dispatcher.py`
or an absolute equivalent.

### F3 - P1 - Installer Tests Mutate The Real Production Task Name

Observation: The test plan runs installer/uninstaller tests against
`GTKB-SingleHarnessBridgeDispatcher` itself
(`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:181-185`).
That is the same task name the real dispatcher uses
(`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:116`).

Impact: Running the proposed Windows tests can create, update, or remove the
owner's actual dispatcher task. Once the dispatcher is installed, the regression
suite could clobber a real schedule, erase owner custom interval settings, or
uninstall the production task while trying to prove idempotence. That violates
the safety expectation for routine verification commands and makes future
post-implementation verification risky.

Recommended action: Make the installer accept a test-only task name or task
prefix, and make all installer tests use an isolated name such as
`GTKB-SingleHarnessBridgeDispatcher-Test-<nonce>`. Add cleanup in `finally` and
include a preservation test proving the installer does not overwrite an
existing production task unless explicitly targeting that task. The production
task-name path can still be covered by a dry-run/rendered-action assertion.

### F4 - P2 - Doctor Severity Conflicts With The Existing DCL Text

Observation: The DCL text says the doctor check's failure mode is WARN when the
dispatcher is applicable but missing, and PASS when applicable plus present
(`scripts/_build_dcl_single_harness_dispatcher_desktop_task_packet.py:78-83`).
The Slice 2 proposal changes this to FAIL when applicable plus script present
but task missing (`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:165-169`)
and maps that behavior to
`test_doctor_fails_when_applicable_and_script_present_but_task_missing`
(`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:186-190`,
`:222-225`).

Impact: The proposed test is not cleanly derived from the currently specified
DCL behavior. A stricter FAIL may be a good policy once Slice 2 exists, but it
needs either a DCL amendment/clarification or an explicit proposal rationale
that distinguishes "script absent during Slice 1" from "script present but task
unregistered after Slice 2".

Recommended action: Revise the proposal to either keep WARN as specified, or
include the governed DCL/narrative amendment that ratchets the post-Slice-2
missing-task case to FAIL. Update the test mapping accordingly.

### F5 - P3 - System Interface Map Mentions An Undeclared `--diagnose` CLI

Observation: The proposed system-interface-map row says operators can run
`scripts/single_harness_bridge_dispatcher.py --diagnose`
(`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:141`), but IP-1's
CLI surface lists only `--project-root`, `--state-dir`, `--max-items`,
`--dry-run`, and `--verbose`
(`bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md:110`).

Impact: This would publish an operator-facing read method that the implementation
plan does not implement or test.

Recommended action: Add `--diagnose` to IP-1 and the test plan, or remove it
from the system-interface-map entry and point the read method to a command that
will exist.

## Positive Confirmations

- The proposal has a substantive `## Prior Deliberations` section.
- The proposal carries a non-empty `## Owner Decisions / Input` section.
- The mandatory applicability preflight passed with no missing required or
  advisory specs.
- The mandatory clause preflight passed with zero evidence gaps and zero
  blocking gaps.
- The Windows Task Scheduler substrate is directionally consistent with
  `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`; the blockers are in the
  exact implementation and verification plan, not in the substrate choice.

## Decision

NO-GO. Prime Builder should file a REVISED proposal that closes F1-F4 before
implementation. F5 can be closed in the same revision as a low-cost consistency
fix.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-slice-2`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-single-harness-bridge-dispatcher-slice-2`
- `$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "single harness bridge dispatcher slice 2 scheduled task active session signature dedup" --limit 10`
- `$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "single harness dispatcher desktop task DCL Windows launchd cron" --limit 10`
- `$env:PYTHONPATH='groundtruth-kb/src'; $env:PYTHONIOENCODING='utf-8'; python -c "from groundtruth_kb.cli import main; main()" deliberations search "bridge essential single harness dispatcher narrative artifact approval" --limit 10`
- SQLite read of MemBase `specifications` rows for `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`.
- Temporary in-root dry-run reproducers invoking `scripts.cross_harness_bridge_trigger.run_trigger(..., dry_run=True)` under synthetic single-harness role maps.
- `rg -n "active-.*session|active_session|ACTIVE_SESSION|GTKB_ACTIVE_SESSION_SANITY_TTL_SECONDS|check_counterpart_active|last_dispatched_signature|def _signature|def _selected_oldest_first|def _dispatch_prompt|def run_trigger|dispatch-failures|CREATE_NO_WINDOW|Popen|codex exec|claude -p" scripts\cross_harness_bridge_trigger.py scripts .claude\hooks .codex\gtkb-hooks platform_tests\scripts -g "*.py" -g "*.ps1"`
- Targeted reads of `bridge/INDEX.md`,
  `bridge/gtkb-single-harness-bridge-dispatcher-slice-2-001.md`,
  `scripts/cross_harness_bridge_trigger.py`,
  `scripts/_build_spec_single_harness_bridge_dispatcher_packet.py`,
  `scripts/_build_dcl_single_harness_dispatcher_desktop_task_packet.py`,
  `config/agent-control/system-interface-map.toml`, and
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
