NEW

# GT-KB Bridge Implementation Report - gtkb-wi5060-sdk-bash-self-invocation-guard - 003

bridge_kind: implementation_report
Document: gtkb-wi5060-sdk-bash-self-invocation-guard
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive session; role prime-builder; approval_policy=never; danger-full-access workspace

Responds to GO: bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-002.md
Approved proposal: bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060

## Implementation Claim

Implemented the approved narrow D/F SDK Bash self-invocation guard.

- `scripts/sdk_bridge_bash_guard.py` now detects Bash commands that launch
  `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` through
  `python`, `python.exe`, `pythonw`, or `pythonw.exe`.
- Matching commands fail before subprocess execution with an explicit
  `Bash SDK harness self-invocation denied ...` reason so the model can switch
  to normal read/search/helper commands.
- Existing bridge artifact mutation denial and benign read-only bridge
  reference behavior remain in place.
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py` now covers the
  observed direct, venv Python, and quoted `pythonw.exe` invocation forms, plus
  read-only false-positive controls.

Dispatcher re-enable is intentionally not performed in this implementation
report. The complex remains paused until Loyal Opposition verifies this guard,
then the operational step is to re-enable/restart and run live dispatcher
health/smoke checks.

## Implementation-Start Authorization

Executed before source/test mutation:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5060-sdk-bash-self-invocation-guard
```

Observed result:

- `latest_status`: `GO`
- `proposal_file`: `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-001.md`
- `go_file`: `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-002.md`
- `packet_hash`: `sha256:a45f121dc13fc7939115cdbbb4323650765ae3cfe92589a565bdea74a09aef11`
- `target_path_globs`: `["scripts/sdk_bridge_bash_guard.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py"]`
- `project_authorization.id`: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707`
- `project_authorization.work_item_id`: `WI-5060`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require a live bridge GO, matching target paths, and append-only bridge evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must stay inside active project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO, implementation-start gates, post-implementation reporting, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal must link work item, project, PAUTH, target paths, specs, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation proposals require Project Authorization, Project, Work Item, and target_paths metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map behavior claims to concrete tests/evidence before VERIFIED.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher-owned harnesses must fail predictably and avoid recursive worker storms during bridge dispatch.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/health/report commands and the bounded disable guard are the authoritative topology and containment evidence surfaces.
- `GOV-ENV-LOCAL-AUTHORITY-001` - no credential lifecycle, disclosure, provider credential mutation, or key rotation is in scope.
- `GOV-STANDING-BACKLOG-001` - this follow-on is tied to WI-5060 runtime evidence and does not mutate unrelated backlog state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner goal, PAUTH, proposal, implementation report, verification, and runtime evidence remain durable linked artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change is handled through a small artifact graph rather than an untracked local patch.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fresh self-invocation runtime failure is preserved as follow-on bridge evidence.

## Owner Decisions / Input

No new owner decision is required by this implementation report. The work stays
inside the active WI-5060 PAUTH, the approved bridge GO, and the approved target
paths. It does not change credentials, model routes, provider accounts,
dispatcher ranking, dispatcher eligibility, deployment state, or backlog status.

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5037-invoke-ban-false-positive-advisory-001.md` - related advisory warning that invoke-ban logic must avoid broad false positives.
- `bridge/gtkb-wi5060-ollama-route-max-turn-budget-004.md` - VERIFIED route max-turn repair; the self-invocation evidence arose during post-fix D dispatch.
- `bridge/gtkb-wi5060-openrouter-direct-timeout-retry-002.md` - GO for the adjacent OpenRouter/F timeout repair, whose D review attempt reproduced the self-invocation recursion.
- `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5060-sdk-bash-self-invocation-guard-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation-start packet `sha256:a45f121dc13fc7939115cdbbb4323650765ae3cfe92589a565bdea74a09aef11` reports latest `GO` and only the two approved target paths. This report is filed as the next numbered bridge entry. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | The packet carries active PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707`, project `PROJECT-GTKB-RELIABILITY-FIXES`, and work item `WI-5060`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Work proceeded only after bridge `GO` and implementation-start packet creation; the report requests Loyal Opposition verification rather than self-closing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal `001`, GO `002`, and this report carry forward the governing spec links and target paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal/report headers include Project Authorization, Project, Work Item, and scoped target paths evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest suite executed against the changed guard and tests: `39 passed, 1 warning`. Ruff lint and format gates also passed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | New tests prove Python/Pythonw execution of D/F SDK harness scripts is denied before subprocess execution, preventing the observed nested worker recursion path. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch complex status --json` showed the complex intentionally paused by the bounded disable guard, with scheduled tasks hidden and using `pythonw`. Re-enable is held until after VERIFIED. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Scoped diff touches only the shared Bash guard and its tests; no `.env`, `env.local`, provider credential, account, key, endpoint, or model-route files are changed in this bridge item. |
| `GOV-STANDING-BACKLOG-001` | Work is tied to WI-5060 and does not mutate backlog rows or status. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Runtime defect, proposal, GO, implementation packet, tests, and report are preserved in the bridge chain. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Repair is represented as a focused artifact chain rather than an untracked local patch. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The fresh D self-invocation failure is captured as a follow-on bridge item with verification evidence. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5060-sdk-bash-self-invocation-guard
```

Observed: latest status `GO`; packet hash
`sha256:a45f121dc13fc7939115cdbbb4323650765ae3cfe92589a565bdea74a09aef11`;
target paths limited to `scripts/sdk_bridge_bash_guard.py` and
`platform_tests/scripts/test_sdk_bridge_bash_guard.py`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_sdk_bridge_bash_guard.py -q --tb=short --basetemp .test-tmp\pytest-sdk-bash-self-invocation
```

Observed: `39 passed, 1 warning in 0.69s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check --no-cache scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_sdk_bridge_bash_guard.py
```

Observed: `All checks passed!`

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check --no-cache scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_sdk_bridge_bash_guard.py
```

Observed: `2 files already formatted`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli bridge dispatch complex status --json
```

Observed before report filing: aggregate status `inactive` / health `WARN`
because the dispatcher daemon was stopped and supervisor/watchdog scheduled
tasks were intentionally disabled by the active temporary disable guard. The
scheduled tasks reported `hidden: true` and `uses_pythonw: true`, which is the
expected no-window configuration.

## Observed Results

- Direct `python scripts/ollama_harness.py ...` Bash self-invocation is denied.
- Venv `python.exe scripts/openrouter_harness.py ...` Bash self-invocation is denied.
- Quoted `pythonw.exe scripts\ollama_harness.py ...` Bash self-invocation is denied.
- `Get-Content scripts/ollama_harness.py`, `python -c "print('scripts/ollama_harness.py')"`, and `rg ollama_harness scripts` remain allowed.
- Existing bridge artifact mutation denial tests still pass.
- Existing benign bridge reference adapter tests still pass.
- No dispatcher registry, route, model, credential, environment, deployment, or backlog mutation was performed in this bridge item.

## Files Changed

- `scripts/sdk_bridge_bash_guard.py`
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py`

## Acceptance Criteria Status

- Bash commands that execute `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` through Python/Pythonw are denied before subprocess execution: satisfied by focused pytest.
- The denial reason is explicit enough for the model to choose a different inspection path: satisfied by the returned `Bash SDK harness self-invocation denied ...` message.
- Read-only references to those files remain allowed: satisfied by false-positive-control tests.
- Existing bridge artifact mutation denial behavior remains intact: satisfied by existing guard tests.
- Focused pytest and Ruff checks pass: satisfied.
- Dispatcher complex can be re-enabled without immediately recreating D self-invocation recursion: implementation evidence is ready for post-VERIFIED operational validation; live re-enable is intentionally deferred until this report is VERIFIED.

## Risk And Rollback

Residual risk is false-positive scope. The regex intentionally targets actual
Python/Pythonw execution of the SDK harness entrypoints rather than prose,
search, or read-only references. Rollback is a source/test revert for
`scripts/sdk_bridge_bash_guard.py` and
`platform_tests/scripts/test_sdk_bridge_bash_guard.py`, leaving the append-only
bridge audit chain intact.

## Recommended Commit Type

Recommended commit type: `fix(harness):`

Diff-stat justification: this is a focused repair to the existing SDK Bash
guard so D/Ollama and F/OpenRouter cannot recursively dispatch themselves from
inside Bash.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
