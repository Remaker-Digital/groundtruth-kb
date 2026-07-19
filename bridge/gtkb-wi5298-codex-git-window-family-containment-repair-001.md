NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning=xhigh; sandbox=none
author_metadata_source: codex-desktop-runtime

Document: gtkb-wi5298-codex-git-window-family-containment-repair
bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5298
target_paths: ["scripts/ops/codex_snapshot_window_hider.py","platform_tests/scripts/test_codex_snapshot_window_hider.py"]
Requirement Sufficiency: SUFFICIENT

# WI-5298 Codex Desktop Git Window-Family Containment Repair

## Summary

Repair the running hide-only Codex Desktop window monitor so it recognizes the full provenance-qualified Git command family rather than only one exact `git add -u` argument tuple. Preserve Codex dispatchability and all Git process behavior. The monitor may call only `ShowWindowAsync(SW_HIDE)` after exact process-ancestry validation; it must never terminate, suspend, reprioritize, intercept, or reroute a process.

Live Windows process evidence on 2026-07-18 shows `ChatGPT.exe` spawning Git inventory commands including `status`, `diff`, `ls-files`, `rev-parse`, `remote`, and `config`, with a visible `conhost.exe` attached to the Git child. The current monitor is healthy but its test suite deliberately classifies `git status` as a near miss. This exact-command matcher is the remaining console-window defect.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, and the owner's WI-5298 nonimpairment direction already require usable Codex operation without weakening dispatchability. This repair changes only the hide-only matcher and its verification; no new or revised requirement is needed before implementation.

## Bridge Authority

This NEW successor proposal is filed as the next numbered versioned bridge file, `bridge/gtkb-wi5298-codex-git-window-family-containment-repair-001.md`, through the governed append-only writer. No existing bridge file is deleted or rewritten. Protected implementation remains forbidden until an independent GO and matching governed claim/start authority exist.

## Scope

1. Replace the exact `SNAPSHOT_GIT_ARGUMENTS` equality check with a predicate that accepts a direct `git.exe` parent for the console and requires `ChatGPT.exe` within a bounded parent walk. Intermediate nested `git.exe` processes remain acceptable; unrelated console ancestry remains rejected.
2. Add a short, bounded, injectable retry only when process metadata is initially unavailable, then fail open and leave the window visible.
3. Bump the named singleton mutex from v1 to v2. The existing v1 monitor remains untouched; the updated source can start a separate v2 monitor through the existing launcher path without stopping any process.
4. Extend focused tests across the observed `add`, `status`, `diff`, `ls-files`, `rev-parse`, `remote`, and `config` families, nested Git ancestry, race recovery, fail-open behavior, and forbidden process-control tokens.

## Explicit Exclusions

- No dispatcher, TAFE, routing, eligibility, ranking, registry, role, model, budget, or harness configuration mutation.
- No process termination, suspension, restart, reprioritization, signal, job-object assignment, input interception, or command rewriting.
- No Git staging, commit, push, reset, checkout, clean, or history operation.
- No credentials, database, deployment, release, external publication, or unrelated worktree mutation.
- No change to `scripts/ops/ensure_gtkb_storm_watchdog.py` or its currently dirty supervision test.

## Requirements

- A top-level console window qualifies only when its owning process is `conhost.exe`, its direct parent is `git.exe`, and a bounded ancestor walk reaches `ChatGPT.exe`.
- Git arguments must not be used as an allowlist; all observed Codex Desktop Git helper verbs are presentation-equivalent because hiding the console does not alter their execution.
- Any missing process, inaccessible metadata, ancestry mismatch, exhausted retry, or window API failure must fail open.
- The only permitted side effect is `ShowWindowAsync(hwnd, SW_HIDE)`.
- The v2 monitor must coexist with v1 and must not require stopping v1.
- Codex remains fully usable and dispatchable throughout.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: native Codex limitations require a local parity fallback that preserves effective harness behavior.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`: Codex must remain usable and available while harness-specific containment is applied.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: the repair must not alter dispatcher selection, execution, or topology.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`: the existing supervision path remains the launcher; this slice changes no supervision behavior.
- `GOV-WORK-TREE-HYGIENE-001`: diagnosis and verification remain report-first and non-destructive.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: source/test changes require independent GO and matching claim/start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: all applicable requirements are linked and mapped to tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: independent verification must execute the specification-derived test plan.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`: console containment must reduce owner-visible noise without removing capability or context.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: implementation remains within the active project PAUTH's source/test classes and forbidden-operation bounds.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: this platform-only repair does not move or modify adopter/application content.

## Prior Deliberations

_No prior deliberations: WI-5298 and its current MemBase history contain the governing owner direction and directly observed matcher gap; no separate DA decision changes this bounded repair._

## Cross-Harness Disposition

This behavior is intentionally Codex Desktop-specific because only the interactive Codex application supplies the qualifying `ChatGPT.exe -> git.exe -> conhost.exe` provenance. Other harnesses and headless workers remain behaviorally unchanged; ancestry mismatch fails open.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5298 live ChatGPT.exe Git/conhost process ancestry evidence",
  "canonical_authority": "ADR-CODEX-HOOK-PARITY-FALLBACK-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "existing Codex snapshot window hider launched by the existing supervision path",
  "before_behavior": "only one exact git add -u console is hidden while status, diff, ls-files, rev-parse, remote, and config consoles remain visible",
  "after_behavior": "all provenance-qualified Codex Desktop Git consoles are hidden while every Git process continues unchanged",
  "self_descriptive_naming": "the v2 mutex and Git-window-family predicate identify the broadened containment contract",
  "obsolete_guidance_disposition": "the exact add-u matcher is replaced in source and tests rather than retained as active guidance",
  "history_preservation": "the running v1 process is not stopped and the committed history remains append-only",
  "baseline": {
    "monitor_state": "healthy v1 process",
    "visible_families": ["status", "diff", "ls-files", "rev-parse", "remote", "config"]
  },
  "expected_result": {
    "monitor_state": "coexisting v2 process",
    "visible_provenance_qualified_git_consoles": 0
  },
  "rollback": {
    "instructions": "revert only the two reviewed source/test hunks; do not stop either monitor process",
    "test": "focused codex snapshot window hider suite"
  },
  "hard_invariants": [
    "ShowWindowAsync SW_HIDE is the only side effect",
    "no harness or dispatcher impairment",
    "all process inspection failures remain fail-open"
  ],
  "fail_closed_conditions": [
    "implementation-start authority absent",
    "target preimage changed",
    "forbidden process-control token introduced"
  ],
  "essential_context_preservation": "all Git commands, output, process lifetime, dispatch capability, and owner workflows remain intact"
}
```

## Implementation Plan

1. Revalidate both clean target hashes immediately before editing.
2. Generalize only the command predicate and bounded ancestry/retry logic; retain the Windows event hook and hide-only API.
3. Bump the mutex name to v2 so the updated monitor can start without terminating v1.
4. Add command-family, nested-ancestry, bounded-race, fail-open, and forbidden-side-effect tests.
5. Run the focused suite, Ruff, format, whitespace checks, and a live observation period after the governed v2 launch.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| Codex-specific provenance only | Parameterized tests accept direct/nested Git ancestry under `ChatGPT.exe` and reject other console, executable, and ancestor families. |
| Full observed Git family | Parameterized tests cover `add`, `status`, `diff`, `ls-files`, `rev-parse`, `remote`, and `config` without argument-specific allowlisting. |
| Fail-open race handling | Injected process factories prove bounded retry can recover once and leaves the window visible after persistent metadata/access failure. |
| Hide-only nonimpairment | Source-token test requires `ShowWindowAsync`/`SW_HIDE` and rejects terminate, kill, suspend, signal, priority, dispatcher, eligibility, and routing controls. |
| v1/v2 coexistence | Test locks the v2 mutex identifier and confirms no code path targets or stops the v1 process. |
| Independent completion | Loyal Opposition reruns focused tests, reviews the exact diff, and issues `VERIFIED` only after live presentation evidence shows no qualifying visible console burst. |

Required commands:

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_snapshot_window_hider.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/ruff.exe check scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py`
- `groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py`
- `git --no-optional-locks diff --check -- scripts/ops/codex_snapshot_window_hider.py platform_tests/scripts/test_codex_snapshot_window_hider.py`

## Risks and Rollback

The main risk is hiding a console that is not owned by Codex Desktop. Requiring exact `conhost.exe -> git.exe` adjacency plus bounded `ChatGPT.exe` ancestry contains that risk without brittle verb matching. Retry is bounded and fail-open, so inspection trouble can only leave a window visible.

Rollback is the exact inverse two-file hunk. No process is stopped during rollback; v1/v2 process lifetime remains an OS/session concern and not a rollback side effect.

## Commit Finalization

After independent `VERIFIED`, finalization must use the same transaction path set:

- Finalization paths: the two declared source/test targets plus this thread's terminal `VERIFIED` bridge file only.
- No whole-file finalization is permitted if either target acquires foreign changes.
- No staging, commit, push, clean, release, or deploy occurs before exact mechanical authority.

Recommended commit subject: `fix(codex): hide provenance-qualified Git consoles`
