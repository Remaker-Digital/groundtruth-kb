NEW

# WI-3412 Dashboard Headless Start Mode

bridge_kind: prime_proposal
Document: gtkb-wi3412-dashboard-headless-start-mode
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ef218-0e11-7133-939d-e1d62c0025f0
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-LO-ADVISORY-ROUTING
Work Item: WI-3412

target_paths: ["scripts/gtkb_dashboard/start_local_dashboard.ps1", "platform_tests/scripts/test_start_local_dashboard_headless.py"]

implementation_scope: cli_extension + test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-3412 routes the Loyal Opposition advisory in
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-00-10.md`.
That advisory found the local dashboard outage was not database corruption or a
port conflict; it was a launcher lifecycle defect in
`scripts/gtkb_dashboard/start_local_dashboard.ps1`, which uses
`Start-Process -WindowStyle Hidden` for both the refresh service and Grafana.
That path is brittle in headless/agent PowerShell sessions.

This proposal asks LO to approve one narrow implementation: add a headless-safe
launch path to `start_local_dashboard.ps1`, preferably exposed as a `-Headless`
switch and/or deterministic non-interactive detection, while preserving the
existing interactive `Start-Process -WindowStyle Hidden` behavior for normal
desktop use. Add a focused static regression test that verifies the script has
an explicit headless path, keeps PID-file behavior, and does not require
Grafana to be installed for test execution.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is the required bridge state
  before any protected script/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the proposed
  script/test change is linked to the advisory, backlog WI, project
  authorization, and verification obligations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the required
  `Project Authorization`, `Project`, and `Work Item` metadata are present for
  this project-scoped implementation proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the post-implementation
  report must map the launcher behavior to executed test evidence.
- `GOV-STANDING-BACKLOG-001` — WI-3412 is a governed backlog item created from
  an advisory and must be routed through durable bridge evidence, not handled as
  an untracked chat/task note.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — dashboard/startup state should not go
  stale because the local refresh service could not be launched from a headless
  harness.
- `GOV-AUTOMATION-VALUE-VS-COST-001` — a dashboard launcher that silently fails
  in the harness context imposes repeated owner/operator recovery cost; the
  fix should make the common automation path reliable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are GT-KB
  platform/dashboard files under `E:\GT-KB`, not Agent Red or another adopter.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserve the advisory-to-WI-to-
  proposal lifecycle and keep the implementation traceable.

## Prior Deliberations

- `WI-3412` — backlog record for routing
  `INSIGHTS-2026-05-28-00-10.md` through the LO advisory workflow.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-00-10.md`
  — source advisory identifying the headless dashboard launcher failure and
  recommending a permanent preventive action in `start_local_dashboard.ps1`.
- `PROJECT-GTKB-LO-ADVISORY-ROUTING` — owner-directed project for converting
  standalone LO advisories into durable dispositions or implementation work.
- `DELIB-20265586` — owner decision that authorized bounded implementation for
  the 19 current open member WIs in this project, including WI-3412.
- `PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23`
  — active project authorization covering the snapshot-bound WI set and the
  allowed mutation classes `source`, `test_addition`, `hook_upgrade`,
  `cli_extension`, and `scaffold_update`.

## Owner Decisions / Input

No new owner decision is required for this proposal. The owner authorized this
bounded implementation lane through `DELIB-20265586` and the active PAUTH named
above. The proposed mutation class is `cli_extension + test_addition`, both
within the allowed PAUTH set. The proposal does not add new WIs, mutate formal
GOV/SPEC/ADR/DCL/PB/REQ artifacts, change credentials, deploy to production, or
touch adopter/application files.

## Requirement Sufficiency

Existing requirements are sufficient. WI-3412 and the source advisory provide a
specific failure mode and target path; the active project authorization provides
bounded owner approval for source/CLI/test work; the bridge/project-linkage
specs require LO review before implementation; and the verification spec
requires executable evidence after the change. No new or revised specification
is needed for this narrow launcher hardening.

## Spec-Derived Verification Plan

| Linked specification or requirement | Planned verification evidence | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | After LO `GO`, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi3412-dashboard-headless-start-mode` before editing. | Impl-start packet authorizes only the proposal target paths. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi3412-dashboard-headless-start-mode --content-file bridge/gtkb-wi3412-dashboard-headless-start-mode-001.md` before and after filing. | `preflight_passed: true`; no missing required specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run `python .claude/hooks/bridge-compliance-gate.py --audit-only --file bridge/gtkb-wi3412-dashboard-headless-start-mode-001.md`. | Project authorization, project, WI, and inline JSON `target_paths` are accepted. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / WI-3412 | Add `platform_tests/scripts/test_start_local_dashboard_headless.py` to statically verify `start_local_dashboard.ps1` exposes an explicit headless/non-interactive launch path, preserves PID writes for both services, and keeps `-WindowStyle Hidden` confined to the interactive path. Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_start_local_dashboard_headless.py -q --tb=short`. | Focused test passes without requiring local Grafana installation. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Same focused test plus code inspection in the implementation report showing the headless branch uses a non-windowing process start mechanism such as `System.Diagnostics.ProcessStartInfo` with `UseShellExecute = $false` and `CreateNoWindow = $true`, or an equivalent PowerShell background-job path. | Harness/headless launch no longer depends on an interactive window-manager context. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Include the spec-to-test mapping and exact command outputs in the post-implementation report. | LO can verify the behavior from focused evidence rather than prose. |

Repo-native verification after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_start_local_dashboard_headless.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_start_local_dashboard_headless.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_start_local_dashboard_headless.py
```

PowerShell syntax verification should also be run if the local host provides
PowerShell:

```text
powershell -NoProfile -Command "$null = [scriptblock]::Create((Get-Content -LiteralPath 'scripts/gtkb_dashboard/start_local_dashboard.ps1' -Raw))"
```

## Risk / Rollback

Risk is limited to the local dashboard launcher. The implementation must not
start services during tests and must not alter dashboard schemas, Grafana
provisioning, MemBase state, or runtime PID files as part of verification.
Rollback is a single-file revert of `scripts/gtkb_dashboard/start_local_dashboard.ps1`
plus removing the additive regression test if the launch approach is rejected.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi3412-dashboard-headless-start-mode`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `fix:`

Rationale: repair a dashboard startup defect in headless/agent PowerShell
sessions without adding a new dashboard capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
