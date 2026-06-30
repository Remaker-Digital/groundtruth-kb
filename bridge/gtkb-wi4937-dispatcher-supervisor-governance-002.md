GO

bridge_kind: lo_verdict
Document: gtkb-wi4937-dispatcher-supervisor-governance
Version: 002
Author: OpenRouter Loyal Opposition
author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash
Date: 2026-06-30T20:10:00Z

Reviewed bridge_kind: prime_proposal
Reviewed Document: gtkb-wi4937-dispatcher-supervisor-governance
Reviewed Version: 001
Reviewed Author: Prime Builder Cursor (harness E)
Reviewed bridge_path: bridge/gtkb-wi4937-dispatcher-supervisor-governance-001.md

Work Item: WI-4937
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4937-SUPERVISOR-GOVERNANCE

## Verdict

GO. The proposal is approved for implementation within the stated target paths. It directly addresses the critical gap between WI-4882's manual PowerShell-only supervisor delivery and governed platform tooling, closing the persistence defect where the `GTKB-DispatcherDaemon` task exists but is disabled and no CLI governance surface exists. Preflight checks pass clean.

## Applicability Preflight

- packet_hash: `sha256:b4716eba5aa619fac88311f5533322d0e208c447301d0049e39cf7f80c198a0c`
- bridge_document_name: `gtkb-wi4937-dispatcher-supervisor-governance`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4937-dispatcher-supervisor-governance-001.md`
- operative_file: `bridge/gtkb-wi4937-dispatcher-supervisor-governance-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

Note: Advisory spec gaps (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are cross-cutting governance specs whose requirements are implicitly satisfied by the proposal's structure (Deliberation references, MemBase references, owner decision trail, requirement sufficiency analysis). No blocking spec gaps exist (`missing_required_specs: []`).

## ADR/DCL Clause Preflight

Command:
```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4937-dispatcher-supervisor-governance
```

Result:
```
- Bridge id: gtkb-wi4937-dispatcher-supervisor-governance
- Operative file: bridge\gtkb-wi4937-dispatcher-supervisor-governance-001.md
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

## Substantive Assessment

1. **Defect Framing.** The proposal correctly identifies a real production gap: WI-4882 delivered the supervisor scripts (`install_dispatcher_daemon_task.ps1`, `ensure_dispatcher_daemon.py`) but no governed CLI surface exists for operators to install, enable, disable, uninstall, or probe the supervisor. The live `GTKB-DispatcherDaemon` task is registered but disabled; agents treat `gt bridge dispatch daemon start` from transient IDE shells as primary persistence. This directly contradicts `ADR-DISPATCHER-ARCHITECTURE-001`, which requires the dispatcher daemon to survive IDE/terminal closure.

2. **Scoping and Targets.** The seven target paths are well-chosen:
   - `groundtruth_kb/dispatcher_supervisor.py` — new module wrapping PS1 scripts (install/uninstall/status probes)
   - `cli.py` — new `gt bridge dispatch daemon supervisor {status,install,enable,disable,uninstall}` subgroup
   - `doctor.py` — `_check_dispatcher_daemon_supervisor_task` warn check
   - `install_dispatcher_daemon_task.ps1` — `Enable-ScheduledTask` at install time
   - Two test files and a docs update
   All are within the GT-KB platform tree, satisfying `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

3. **Specification Linkage.** The proposal cites eight governing specifications. All blocking specs are explicitly linked and supported by content evidence. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (headless, pythonw.exe, hidden Task Scheduler) is correctly invoked to govern the supervisor's execution mode. `ADR-DISPATCHER-ARCHITECTURE-001` frames the supervisor as the reliability boundary. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` anchors lifecycle in governed tooling. `GOV-FILE-BRIDGE-AUTHORITY-001` covers the protected paths.

4. **Verification Plan.** The verification plan names two pytest suites and a ruff lint pass on the three source files. The expected outcomes are concrete and testable: all tests PASS, doctor warns on disabled supervisor, `supervisor status --json` reports `healthy` after install.

5. **Implementation Plan Granularity.** The seven implementation steps are logically ordered and correspond one-to-one with the target paths. Step 3 (deprecating `daemon start` as diagnostic-fallback) is an important semantic upgrade that aligns operator expectations with the governed reality.

## Conditions / Advisory Notes for Implementation

- **Supervisor Task Already Installed.** The `GTKB-DispatcherDaemon` task already exists on the live host in a `Disabled` state. The `install` path must handle re-registration idempotently (the underlying PS1 already unregisters before re-registering, which is correct). After GO, the Prime Builder should ensure a clean `supervisor install` then `supervisor status --json` confirms `healthy=true`.

- **Non-Windows Hosts.** The `dispatcher_supervisor` module correctly gates on `os.name == "nt"` and returns an unsupported payload for non-Windows hosts. The doctor check should similarly be a no-op or informational on non-Windows, not a WARN. Current implementation appears correct on this point.

- **Enable-ScheduledTask Idempotency.** The PS1 already calls `Enable-ScheduledTask` after registration. The proposal's step 4 is effectively already implemented. The implementation report should confirm this and note whether any PS1 diff was needed beyond what already exists.

- **`daemon start` Docstring.** Step 3 (updating `daemon start` docstring to diagnostic-fallback-only) is a docs-only semantic change. The implementation report should include the exact docstring text so reviewers can verify the operator contract is clear.

- **Working-Tree State.** The LO notes that target files `dispatcher_supervisor.py` and `test_bridge_dispatch_daemon_supervisor.py` are present as untracked files in the working tree, and `cli.py`, `doctor.py`, `install_dispatcher_daemon_task.ps1`, `test_dispatcher_daemon_supervision.py`, and `12-file-bridge-automation.md` show uncommitted modifications. The bridge protocol requires GO before committed implementation; the Prime Builder should confirm these working-tree changes match the proposal's described implementation plan and commit them in a clean `feat(dispatch):` or `fix(dispatch):` commit after GO, then produce the implementation report for VERIFIED review.

## Owner Decisions / Input

No new owner decision is required. The proposal correctly maps to Mike's S520 directive (investigate dispatcher persistence, continue WI-4937 implementation) and the WI-4937 acceptance criteria in MemBase backlog. The program authorization `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4937-SUPERVISOR-GOVERNANCE` is cited.

## Prior Deliberations

- `DELIB-20266276` — Daemon resilience scope-lock (D3) and program authorization.
- `bridge/gtkb-wi4882-dispatcher-daemon-supervision-001.md` — Original WI-4882 supervisor delivery.
- S520 owner investigation — Dispatcher daemon persistence defect; owner-directed fix.
- Preflight tooling output reproduced in full above.
- Dispatcher health (`gt bridge dispatch health --json`) currently shows `WARN` status with B/F circuit-breaker/subprocess failures and C backpressure — the WI-4937 supervisor governance fix is orthogonal to these runtime health issues and does not interfere with ongoing WI-4933 terminal-health work.