NEW

# WI-5060 Follow-On: SDK Bash self-invocation guard

bridge_kind: prime_proposal
Document: gtkb-wi5060-sdk-bash-self-invocation-guard
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f39ff-4e44-7a32-b5d0-6969ec4d55ec
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive session; role prime-builder; approval_policy=never; danger-full-access workspace

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5060

target_paths: ["scripts/sdk_bridge_bash_guard.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py"]

implementation_scope: source | tests | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal repairs the D/Ollama self-invocation recursion observed during real bridge dispatch verification after the route max-turn budget was raised. D no longer failed early with `max-turn exhaustion`; instead, it used the Bash tool to start `scripts/ollama_harness.py` with the same dispatch prompt under itself, creating nested `pythonw.exe scripts/ollama_harness.py ...` descendants and holding bridge leases until worker lifetime cleanup.

The proposed repair is intentionally narrow: extend the shared SDK Bash guard so Bash commands that launch SDK harness entrypoints (`scripts/ollama_harness.py` or `scripts/openrouter_harness.py`) are denied before subprocess execution. Both D/Ollama and F/OpenRouter already call this guard before executing Bash commands, so the common guard is the smallest effective containment point.

## Current Evidence

- D verification run `2026-07-07T08-08-46Z-loyal-opposition-D-8f7cde` launched with no explicit `--max-turns`, exercising the new route default, but then created child `pythonw.exe scripts/ollama_harness.py` processes with the same bridge dispatch prompt beneath itself.
- D verification run `2026-07-07T08-15-12Z-loyal-opposition-D-f9d177` reproduced the same nested self-invocation shape.
- A fresh D run `2026-07-07T08-23-44Z-loyal-opposition-D-bb580f` also reproduced the recursion immediately after dispatcher state was reset.
- The recursion occurs inside a Bash tool call, so ordinary turn-budget accounting and repeated assistant tool-signature detection do not fire until the child command returns.
- C/Antigravity successfully filed `bridge/gtkb-wi5060-ollama-route-max-turn-budget-004.md` as VERIFIED and `bridge/gtkb-wi5060-openrouter-direct-timeout-retry-002.md` as GO before the dispatcher complex was paused.
- The dispatcher complex is temporarily disabled until `2026-07-07T08:41:07Z` to prevent D from re-grabbing work while this guard proposal is prepared.
- `scripts/sdk_bridge_bash_guard.py` currently denies Bash bridge artifact mutations but does not deny SDK harness self-invocation.
- Both `scripts/ollama_harness.py` and `scripts/openrouter_harness.py` call `bridge_bash_mutation_reason(command)` before invoking Bash subprocesses.

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

## Prior Deliberations

- `DELIB-20260707-HARNESS-A-C-D-F-REPAIR-GOAL` - owner-directed goal to test and fix harnesses A, C, D, and F for their currently assigned roles.
- `bridge/gtkb-wi5037-invoke-ban-false-positive-advisory-001.md` - related advisory warning that invoke-ban logic must avoid broad false positives; this proposal is narrower, matching actual SDK harness entrypoint invocation rather than prose references.
- `bridge/gtkb-wi5060-ollama-route-max-turn-budget-004.md` - VERIFIED route max-turn repair; the self-invocation evidence arose during post-fix D dispatch.
- `bridge/gtkb-wi5060-openrouter-direct-timeout-retry-002.md` - GO for the adjacent OpenRouter/F timeout repair, whose D review attempt reproduced the self-invocation recursion.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5060-HARNESS-REPAIR-20260707` - active bounded WI-5060 source/test/config/governance authorization.

## Owner Decisions / Input

No additional owner decision is needed for this filing. The repair stays inside the active WI-5060 PAUTH and does not change credentials, model routes, registry state, dispatcher ranking, deployment, or backlog status. The dispatcher pause is a bounded operational containment measure, not a durable configuration change.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5060, the active PAUTH, the runtime evidence of D recursive self-invocation, and the dispatcher service/control specifications provide enough authority to add a precise SDK harness self-invocation guard.

## Proposed Scope

1. Extend `scripts/sdk_bridge_bash_guard.py` with a precise detector for Bash commands that execute `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` through Python/Pythonw.
2. Return a clear denial reason before subprocess execution, for example: `Bash SDK harness self-invocation denied ...`.
3. Preserve existing bridge artifact mutation detection and read-only bridge reference behavior.
4. Add focused tests in `platform_tests/scripts/test_sdk_bridge_bash_guard.py` proving:
   - direct `python scripts/ollama_harness.py ...` invocation is denied;
   - direct `pythonw.exe scripts/openrouter_harness.py ...` invocation is denied;
   - read-only prose or `Get-Content scripts/ollama_harness.py` style references remain allowed;
   - existing bridge artifact mutation and read-only bridge reference tests still pass.

## Out Of Scope

- No dispatcher registry, eligibility, ranking, route, model, or scheduled-task configuration mutation.
- No credential, environment, OpenRouter/Ollama endpoint, provider account, or key lifecycle change.
- No broad command-ban pattern that blocks ordinary prose, `gt` commands, or read-only inspection merely because provider or harness names are mentioned.
- No changes to `scripts/ollama_harness.py` or `scripts/openrouter_harness.py`; both already call the shared guard before Bash subprocess execution.
- No deployment, push, destructive cleanup, broad backlog/status mutation, or untracked file deletion.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5060-sdk-bash-self-invocation-guard` after GO | Latest status is `GO`; implementation-start packet authorizes only the listed target paths. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect proposal/report headers and active PAUTH record | Proposal cites the active WI-5060 PAUTH; target paths fit source/test/governance scope. |
| SDK harness self-invocation denial | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_sdk_bridge_bash_guard.py -q --tb=short --basetemp .test-tmp/pytest-sdk-bash-self-invocation` | Direct Bash commands invoking `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` are denied. |
| False-positive control | Same focused pytest suite | Read-only references and existing benign bridge references remain allowed. |
| Existing bridge mutation guard behavior | Same focused pytest suite | Existing bridge mutation tests continue to pass. |
| Code quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check --no-cache scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_sdk_bridge_bash_guard.py`; `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check --no-cache scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_sdk_bridge_bash_guard.py` | Python lint and format checks pass. |
| Dispatcher status truth | `gt bridge dispatch complex status --json`; later re-enable check after verified guard | Pause is explicit and bounded during repair; complex is re-enabled only after guard evidence is available. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Diff review | No env file, credential, provider secret, key, account, or model routing mutation. |

## Acceptance Criteria

- Bash commands that execute `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` through Python/Pythonw are denied before subprocess execution.
- The denial reason is explicit enough for the model to choose a different inspection path.
- Read-only references to those files remain allowed.
- Existing bridge artifact mutation denial behavior remains intact.
- Focused pytest and Ruff checks pass.
- Dispatcher complex can be re-enabled without immediately recreating D self-invocation recursion.

## Risk / Rollback

Risk is moderate and mostly false-positive related. The detector must be specific to actual Python/Pythonw execution of the SDK harness entrypoint scripts, not mentions in prose or read-only inspection commands. Rollback is a source/test revert for `scripts/sdk_bridge_bash_guard.py` and `platform_tests/scripts/test_sdk_bridge_bash_guard.py`.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing bridge file for `gtkb-wi5060-sdk-bash-self-invocation-guard`; no prior version is deleted or rewritten.

## Recommended Commit Type

`fix(harness):`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
