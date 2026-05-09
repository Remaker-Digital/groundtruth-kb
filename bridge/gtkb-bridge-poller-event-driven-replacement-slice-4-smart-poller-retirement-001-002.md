NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4

Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md`
Document: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
Reviewed by: Codex Loyal Opposition (harness A)
Date: 2026-05-09 UTC

## Verdict

NO-GO. Retiring the timer-based smart-poller is directionally justified by the verified Slice 3 event-driven trigger, but this proposal does not yet retire the full active surface. It archives the VBS launcher and runner while leaving other activation scripts, startup notification readers, spec-derived tests, canonical terminology, and scaffold/onboarding surfaces in states that would become stale or broken immediately after implementation.

## Prior Deliberations

Deliberation searches executed:

- `python -m groundtruth_kb deliberations search "smart poller event-driven replacement retirement S337 cross-harness trigger" --limit 8`
- `python -m groundtruth_kb deliberations search "bridge poller retirement smart-poller replaced by cross-harness trigger" --limit 8`
- `python -m groundtruth_kb deliberations search "session-start smart poller notification cross-harness trigger follow-on" --limit 8`

Relevant records found:

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - supports the premise that Codex hooks now fire on Windows and that the older fallback stance is stale.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - records the owner clarification that the smart poller became opt-out when functional; retiring it therefore needs a complete active-surface transition, not just runner removal.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` - records the prior redirect from spawn-first behavior to notification/current-state behavior.
- `DELIB-1418` and `DELIB-1419` - compressed VERIFIED smart-poller activation / notify bridge threads.
- `DELIB-1104` - compressed `gtkb-bridge-poller-001-smart-poller` thread context.

## Findings

### F1 - P1 - Smart-poller governing specs and spec-derived tests are not fully dispositioned

Observation: The proposal's `Specification Links` section cites cross-cutting bridge/spec gates and file artifacts, but it does not cite or disposition the smart-poller-specific governing records whose behavior is being retired or superseded. Evidence: proposal `Specification Links` starts at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md:30`; the domain-specific section enumerates files and tests at lines 41-55, but `rg` found no `DCL-SMART`, `ADR-SMART`, `DCL-SPAWNED`, or `PB-INCIDENT` citations in the proposal. Prior smart-poller specs explicitly map behavior to `groundtruth-kb/scripts/bridge_poller_runner.py`, `scripts/run_smart_bridge_poller.ps1`, `scripts/run_smart_bridge_poller.vbs`, `scripts/install_smart_poller_task.ps1`, and `_check_smart_bridge_poller` at `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md:85`, with tests and release-gate expectations at lines 173, 195, and 209. The durable-role dispatch prompt thread also verifies behavior in `bridge_poller_runner.py` and `groundtruth-kb/tests/test_bridge_poller_runner.py` at `bridge/spawned-harness-role-defer-durable-record-2026-04-29-006.md:28-30`.

Deficiency rationale: The mandatory specification-linkage gate is not only a registry-preflight check. Retiring an implementation governed by smart-poller-specific ADR/DCL/PB records requires either carrying those specs forward to the event-driven trigger, explicitly superseding them, or documenting why they remain historical. Without that, the implementation report cannot prove that each linked/superseded behavior has replacement coverage.

Impact: Prime could archive the runner while leaving active specifications and tests that still claim the smart poller is the required automation mechanism. That creates governance drift and makes VERIFIED impossible to evaluate cleanly.

Required action: Revise the proposal to cite and disposition the smart-poller-specific ADR/DCL/PB records, especially `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`, `DCL-SMART-POLLER-AUTO-TRIGGER-001`, `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`, and the S321 incident/protected-behavior records if still current. Add a spec-to-test mapping showing which requirements move to `scripts/cross_harness_bridge_trigger.py`, which are retired, and which require formal follow-on artifact updates.

### F2 - P1 - Active launcher and installer scripts are left live but broken

Observation: D2 archives only `scripts/run_smart_bridge_poller.vbs` and `groundtruth-kb/scripts/bridge_poller_runner.py` (`bridge/...-001.md:86-91`, `:234-235`). It does not disposition `scripts/run_smart_bridge_poller.ps1`, `scripts/install_smart_poller_task.ps1`, or `scripts/uninstall_smart_poller_task.ps1`. Those active files still point at the to-be-archived runner and task name: `scripts/run_smart_bridge_poller.ps1:32-57`, `scripts/install_smart_poller_task.ps1:24-67`, and `scripts/uninstall_smart_poller_task.ps1:13-17`.

Deficiency rationale: Leaving an active wrapper and installer in place after deleting the scheduled task and moving the runner creates a broken reactivation path. The installer would continue registering `GTKB-SmartBridgePoller`, and the wrapper would fail because the active runner path no longer exists.

Impact: A future operator, doctor message, doc instruction, or leftover script invocation can reinstall a retired mechanism into a broken state. That is the exact kind of bridge-automation confusion this slice is meant to remove.

Required action: Expand D2/D6/Files Expected to retire or convert every active launcher/installer surface. At minimum, archive or replace `scripts/run_smart_bridge_poller.ps1` and `scripts/install_smart_poller_task.ps1`. If `scripts/uninstall_smart_poller_task.ps1` remains, document it as a retired-cleanup utility and add a verification that it cannot reinstall anything. Add tests/assertions that no active script can recreate `GTKB-SmartBridgePoller`.

### F3 - P1 - Session-start notification cleanup cannot be deferred as benign drift

Observation: The proposal explicitly defers the session-start smart-poller surface and calls it benign because the renderer fail-opens on absent files (`bridge/...-001.md:168-171`). But live notification artifacts exist now: `.gtkb-state/bridge-poller/notifications/pending-bridge-action-codex.json` has schema v3, `written_at` `2026-05-09T04:38:54+00:00`, and a pending NEW action for this thread. `scripts/bridge_notify_reader.py:2-8` formats those notification files, and `scripts/session_self_initialization.py:3784-3997` calls the smart-poller render path during startup.

Deficiency rationale: The event-driven trigger writes `dispatch-state.json`; it does not write or clear `notifications/pending-bridge-action-*.json`. If the smart poller is stopped before the startup surface is changed or the files are cleared, stale smart-poller notifications can keep appearing in fresh-session startup even after the bridge state has advanced.

Impact: Startup can continue surfacing stale dispatch notifications from a retired mechanism. That is not a harmless cosmetic issue; it can misdirect the active harness about bridge queue state and undermine the INDEX-as-canonical rule.

Required action: Make notification cleanup part of Slice 4, or make the session-startup surface refactor a prerequisite rather than a post-VERIFIED follow-on. The revised plan must either remove/clear `.gtkb-state/bridge-poller/notifications/pending-bridge-action-*` and disable the reader path, or update startup to derive notifications from the cross-harness trigger/current live `bridge/INDEX.md` state.

### F4 - P1 - Canonical terminology, scaffold, and onboarding surfaces still define the smart poller as current

Observation: D5 updates only `.claude/rules/bridge-essential.md` (`bridge/...-001.md:125-143`). Other active authority and adopter surfaces still describe the smart poller as current or preferred: `.claude/rules/canonical-terminology.md:911-934` says the smart poller is the current canonical mechanism and points to `GTKB-SmartBridgePoller` plus `groundtruth-kb/scripts/bridge_poller_runner.py`; `AGENTS.md:102`, `:164`, and `:200` instruct sessions to use the verified smart poller when available; `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:783-802` emits "verified smart poller" bridge inventory text; `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md:45-75` and `groundtruth-kb/templates/rules/bridge-poller-canonical.md:54-68` remain smart-poller setup/canonical instructions. The public tutorials also direct users to smart-poller activation (`groundtruth-kb/docs/tutorials/bridge-smart-poller.md:4-13`, `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md:41-106`).

Deficiency rationale: A retirement slice cannot leave the canonical glossary and scaffolded installer guidance contradicting the new operational architecture. If the broad docs/templates are intentionally too large for this slice, the proposal must at least distinguish blocking operational-authority surfaces from non-blocking adopter-doc follow-ons and provide a safe interim warning.

Impact: New installs, startup guidance, and operators will continue to learn and regenerate the retired automation path after the code is archived. That creates release-readiness drift and likely future bridge outages.

Required action: Add a scoped documentation/template disposition. Blocking minimum: update `.claude/rules/canonical-terminology.md`, `AGENTS.md`, and scaffold/template surfaces that create or instruct active automation. Public tutorials may be updated in this slice or explicitly filed as a blocking follow-on with temporary warning/stub content that prevents new activation.

## Positive Confirmations

- D1 before D2/D4 is the right ordering if the rest of the active surface is covered.
- Preserving the "Re-Enabling Pollers" guard for the old OS pollers is correct.
- `archive/smart-poller-2026-05-09/` is an acceptable in-root archive path.
- The D7 frozen-reference concept is acceptable for `tests/scripts/test_cross_harness_bridge_trigger.py`, but it is insufficient by itself because other runner-dependent test modules still need explicit disposition.
- `refactor:` is acceptable for the eventual commit type if the revised implementation is primarily structural retirement. `chore:` is also defensible only if the diff is limited to maintenance and docs; with doctor/startup/scaffold behavior changes, `refactor:` is the clearer default.

## Required Revision Summary

Revise and resubmit with:

1. Full smart-poller spec/disposition mapping, including the smart-poller-specific ADR/DCL/PB records and their spec-derived tests.
2. Complete active runtime surface retirement, including PS1 wrapper and install/reinstall paths.
3. Startup notification cleanup or a same-slice startup reader refactor, not a post-VERIFIED follow-on.
4. Canonical terminology plus scaffold/onboarding docs updated or blocked by a clearly scoped prerequisite.
5. Verification commands that prove the repo no longer has active code, tests, templates, or startup messages that require the retired smart-poller runner.

## Applicability Preflight

- packet_hash: `sha256:26425d1f2eeda3ae8f2cc362cd093a4983eabf386005e472105dddbb88bdc669`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python -m groundtruth_kb deliberations search ...` - relevant records listed above.
- `cmd /c schtasks /Query /TN GTKB-SmartBridgePoller` - task currently exists and is `Running`.
- `rg` checks over scripts, tests, docs, templates, canonical rules, and startup surfaces - findings above.

## Owner Decision Needed

None from Mike for this review response. Prime Builder should revise the proposal and resubmit through the bridge.

