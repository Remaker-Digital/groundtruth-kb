NEW

# Extend Codex snapshot-window containment to all internal Git-manager commands

bridge_kind: prime_proposal
Document: gtkb-wi5368-codex-git-window-command-family
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5368

target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py"]

implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Complete the hide-only WI-5298 containment by recognizing the full Codex
Desktop internal Git-manager command family. The running monitor currently
matches only the exact argv `git -c core.hooksPath=NUL -c core.fsmonitor= add
-u`. A 20-second live trace against Codex Desktop 26.707.9981.0 observed the
same `ChatGPT.exe` Git manager launching `write-tree`, `read-tree`, `diff`,
`status`, `ls-files`, and `add --pathspec-from-file` commands. Those commands
carry the same exact `core.hooksPath=NUL` and empty `core.fsmonitor=` markers,
but the current matcher rejects them and visible windows continue.

Replace the one-command tuple predicate with a small argv parser that requires
all of the following: executable basename `git.exe`, exactly one
`core.hooksPath=NUL` config override, exactly one empty `core.fsmonitor=`
override, a non-empty Git subcommand, the existing `conhost.exe` relationship,
and a `ChatGPT.exe` ancestor. Preserve the sole side effect
`ShowWindowAsync(SW_HIDE)`. Do not terminate, suspend, intercept, reprioritize,
or alter any process, Git operation, dispatcher route, harness role, or
eligibility value.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - window containment must preserve every Git command and every harness's dispatchability.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Windows Codex gaps use explicit, testable fallback containment when native behavior is unavailable.
- `ADR-CROSS-HARNESS-PARITY-001` - the Codex-specific fallback must not alter other harnesses or shared dispatch behavior.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - process provenance and hide-only behavior require deterministic mechanical enforcement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test repair requires independent GO, matching claim/start authority, a report, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the nonimpairment and enforcement requirements are explicitly linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Harness Parity project, PAUTH, WI-5368, and exact targets are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must exercise static predicates and live window/process evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5368 is the durable owner of the post-WI-5298 residual.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and evidence remain under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the live residual, work item, proposal, implementation, tests, report, and verdict remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5368 remains active through implementation, verification, and exact finalization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the failed live acceptance claim is corrected through a governed child scope rather than transcript-only adjustment.

## Prior Deliberations

- `DELIB-202666274` - project-level modernization authority while retaining bridge, verification, and mechanical Git gates.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - background automation must not surface visible consoles.
- Owner directive, 2026-07-15 - console visibility must be fixed without disabling, suspending, deprioritizing, or excluding any harness.
- WI-5298 - establishes hide-only Codex Desktop snapshot containment and explicitly rejects dispatch impairment.

## Owner Decisions / Input

No new owner decision is required. The owner has already required the
nonimpairing resolution, and the active Harness Parity project PAUTH covers
source/test implementation. Git staging/commit/push, release, deployment,
dispatcher/TAFE/harness mutation, credential lifecycle, process termination,
and destructive cleanup remain excluded.

## Requirement Sufficiency

Existing requirements are sufficient. The defect is incomplete coverage of a
known Codex-specific fallback, not a missing policy choice. The live trace and
WI-5368 identify the exact residual while the linked nonimpairment carrier
defines the required behavior.

## Proposed Scope

1. Replace the exact `SNAPSHOT_GIT_ARGUMENTS` equality check with a deterministic parser for Git `-c key=value` overrides followed by a non-empty subcommand.
2. Require executable basename `git.exe`, exact case-insensitive key names, exact Windows value `NUL` for `core.hooksPath`, and an exact empty value for `core.fsmonitor`.
3. Reject duplicate required keys, missing values, malformed `-c` pairs, absent subcommands, non-Git executables, and every marker near miss.
4. Preserve the existing top-level show-event filter, `conhost.exe` requirement, bounded `ChatGPT.exe` ancestry, fail-open inspection behavior, named mutex, and sole `ShowWindowAsync(SW_HIDE)` side effect.
5. Add parameterized tests for all observed subcommand shapes, extra benign Codex config overrides, both outer and inner Git executable paths, and unrelated user/tool Git near misses.
6. Do not change the launcher, dispatcher, TAFE, bridge routing, roles, eligibility, Git execution, process lifetime, or any third file.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"2026-07-16 live ChatGPT.exe process trace plus running WI-5298 monitor source","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"exact process provenance plus Codex internal Git-manager config markers","before_behavior":"Only add -u is hidden; current write-tree, read-tree, diff, status, ls-files, and pathspec-add windows remain visible.","after_behavior":"Every Codex internal Git-manager console is hidden while its command executes and exits naturally.","self_descriptive_naming":"Codex internal Git marker parsing names the qualifying provenance instead of one historical subcommand.","obsolete_guidance_disposition":"No dispatcher-disable guidance is introduced; WI-5356 separately retires the stale guard.","history_preservation":"WI-5298 remains intact; WI-5368 owns only the observed residual.","baseline":{"focused_tests":"13 passed but encode only add -u","live_trace":"20 seconds; multiple marker-qualified non-add commands observed"},"expected_result":{"focused":"all observed command families accepted; near misses rejected","live":"zero visible qualifying windows; every command exits naturally"},"rollback":{"instructions":"revert only the WI-5368 matcher and test hunks through a governed change","verification":"focused near-miss tests and live observer"},"hard_invariants":["hide only","no process lifecycle action","no Git interception","no dispatch or eligibility mutation","fail open on ambiguity"],"fail_closed_conditions":["ancestry broadened beyond ChatGPT.exe","required markers made optional","arbitrary Git windows hidden","process or dispatcher state changed"],"essential_context_preservation":"Retain exact event, process, marker, singleton, and nonimpairment evidence."}
```

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Full current command coverage | Run `python -m pytest $env:WI5368_FOCUSED_TEST -q --tb=short`, with the variable bound to the test target declared in `target_paths` | Every observed write-tree/read-tree/diff/status/ls-files/add shape passes; all near misses remain untouched. |
| Hide-only source | Static source assertions plus review of `hide_qualifying_window` | `ShowWindowAsync(SW_HIDE)` remains the only target-window/process side effect; no kill, suspend, priority, interception, or dispatch API exists. |
| Live nonimpairment | Run the monitor and a timed `psutil` plus Win32 `EnumWindows` observer while Codex performs snapshot/review operations | All marker-qualified commands complete naturally; zero qualifying windows remain visible; unrelated consoles are unchanged. |
| Scope | Run `git diff --` and `git diff --check --` against exactly the two paths declared in `target_paths` | Only matcher and focused-test hunks exist; diff check exits zero. |
| Harness continuity | Read-only governed dispatch health after the live observer | Roles and eligibility are unchanged; no harness is disabled or suppressed because of visibility. |

## Acceptance Criteria

1. All Codex internal Git-manager commands carrying both exact markers and the existing ChatGPT/conhost provenance are hidden.
2. The commands continue running and exit naturally with unchanged results.
3. User/tool Git, non-ChatGPT ancestry, malformed markers, missing markers, and non-top-level events remain untouched.
4. No process, Git, dispatcher, TAFE, bridge route, harness role, or eligibility mutation is performed.
5. Independent VERIFIED precedes exact mechanical finalization.

## Risk / Rollback

The main risk is hiding an unrelated Git console. Exact executable, two Codex
Git-manager markers, top-level event shape, `conhost.exe`, and `ChatGPT.exe`
ancestry constrain that risk without pinning volatile subcommands. Inspection
ambiguity continues to fail open. Rollback is the exact two-file hunk through a
new governed change; no broad reset, process termination, or dispatcher change
is permitted.

## Bridge Filing

File the proposal as the next numbered append-only bridge file through the
governed Codex non-bypass helper. No prior version is deleted or rewritten.
Deterministic TAFE/bridge routing remains external to this authoring task; no
manual routing or direct harness contact occurs.

## Recommended Commit Type

`fix` - completes nonimpairing Windows containment for current Codex Desktop Git review operations.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
