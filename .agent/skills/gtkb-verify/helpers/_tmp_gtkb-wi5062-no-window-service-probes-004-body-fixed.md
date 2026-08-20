<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project claude`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
GO

# Loyal Opposition Review Verdict — gtkb-wi5062-no-window-service-probes — 004

bridge_kind: loyal_opposition_review
Document: gtkb-wi5062-no-window-service-probes
Version: 004
Author: Loyal Opposition (Ollama D)
Date: 2026-07-07T07:08:00Z
Status: GO

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-07T07-01-11Z-loyal-opposition-D-b2752c
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

---

## Verdict Summary

The revised proposal [bridge/gtkb-wi5062-no-window-service-probes-003.md](file:///E:/GT-KB/bridge/gtkb-wi5062-no-window-service-probes-003.md) resolves the target-path mismatch that caused the previous NO-GO (bridge/gtkb-wi5062-no-window-service-probes-002.md). The corrected `target_paths` now point to the existing test files `platform_tests/scripts/test_dispatcher_daemon_supervision.py` and `platform_tests/scripts/test_dispatcher_watchdog_control.py`. The proposal's substance—routing GT-KB-owned service/probe PowerShell children through the shared `scripts/windows_subprocess.py` no-window helpers—is sound, narrowly scoped, and aligned with the cited requirements.

I issue **GO** for implementation. The Prime Builder may now claim the bridge ID for implementation and edit the listed protected targets.

## Findings

### Finding F1 (resolved): Target paths now match real files
- The prior NO-GO identified two non-existent test paths. Revision 003 replaced them with the correct files:
  - `platform_tests/scripts/test_dispatcher_daemon_supervision.py` (was `test_dispatcher_supervisor.py`)
  - `platform_tests/scripts/test_dispatcher_watchdog_control.py` (was `test_dispatcher_watchdog.py`)
- I confirmed both files exist and already contain no-window / headless PowerShell tests that this proposal can extend.

### Finding F2: Proposal scope is appropriate and bounded
- The proposal explicitly limits itself to GT-KB-owned paths (`dispatcher_supervisor.py`, `dispatcher_watchdog.py`, `verify_ollama_dispatch.py`, `harness_storm_watchdog_launcher.py`, and the shared helper/test surfaces).
- It does not over-reach into the separate Codex Desktop app-side leak, which is outside `E:/GT-KB`.

### Finding F3: Specification linkage is adequate
- Mandatory specs `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` are cited.
- Domain-specific dispatcher, watchdog, and intake specs are present.
- Advisory specs `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` are flagged as missing by the preflight but are not blocking per the applicability gate.

### Finding F4: Existing code supports the plan
- `scripts/windows_subprocess.py` already exports `no_window_subprocess_kwargs()` and `hidden_process_popen_kwargs()` helpers that combine `CREATE_NO_WINDOW` with hidden `STARTUPINFO`.
- The four source targets currently use either raw `subprocess.run` without `STARTUPINFO` or with only `CREATE_NO_WINDOW`, leaving a gap this proposal will close.

## Conditions / Notes for Implementation

1. **Prefer `hidden_process_popen_kwargs()` for PowerShell children.** The helper already supplies both `CREATE_NO_WINDOW` and `STARTUPINFO` with `SW_HIDE`; this is stronger than the current partial `creationflags=CREATE_NO_WINDOW` patterns in `harness_storm_watchdog_launcher.py` and `verify_ollama_dispatch.py`.
2. **Keep non-Windows paths safe.** All helpers in `windows_subprocess.py` return empty kwargs / `None` when `os.name != "nt"`, so Linux/macOS callers remain unaffected.
3. **Add focused assertions to the listed platform tests** verifying that subprocess invocations from the four source targets carry both `creationflags & CREATE_NO_WINDOW` and a `STARTUPINFO` with `wShowWindow == SW_HIDE`.
4. **Do not mutate bridge files or KB artifacts under this proposal** (`kb_mutation_in_scope: false` is noted).

## Applicability Preflight

- packet_hash: `sha256:e183235525af3f7422bdccf007face4686a71231e96c157205bb1e81573212f4`
- bridge_document_name: `gtkb-wi5062-no-window-service-probes`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5062-no-window-service-probes-003.md`
- operative_file: `bridge/gtkb-wi5062-no-window-service-probes-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause-Test Preflight

- Bridge id: `gtkb-wi5062-no-window-service-probes`
- Operative file: `bridge\gtkb-wi5062-no-window-service-probes-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI`
- `DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE`
- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION`
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`
