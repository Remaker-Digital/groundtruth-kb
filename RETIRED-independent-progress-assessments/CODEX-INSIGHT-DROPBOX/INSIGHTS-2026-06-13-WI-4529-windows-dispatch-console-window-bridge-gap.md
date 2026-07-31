Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
WIs: WI-4529

# WI-4529 Windows Dispatch Console Window Bridge Gap

Date: 2026-06-13 UTC
Author: Loyal Opposition (Codex harness A)
Scope: read-only advisory investigation during `keep-working-lo`

## Claim

The current dirty worktree contains the apparent source fix for `WI-4529`
(replace visible Windows console creation with `CREATE_NO_WINDOW` at bridge
dispatch spawn surfaces), but the live bridge does not currently contain an
indexed `NEW`/`REVISED` proposal or `GO` whose target paths authorize those
two source files.

This is not a code-quality objection to the patch shape. The patch is small and
plausibly correct. The issue is governance/audit sequencing: source changes for
a bridge-dispatch defect should be tied to a bridge proposal before they are
committed.

## Evidence

- Durable role check: Codex harness `A` is currently assigned
  `loyal-opposition` in `harness-state/harness-registry.json`; Claude `B` is
  `prime-builder`.
- Live bridge scan at `2026-06-13T17:12:27Z`: Loyal Opposition actionable count
  `0`; summary `ADVISORY=13`, `GO=29`, `VERIFIED=196`, `WITHDRAWN=61`.
- Live Prime-actionable GO threads at the time of inspection were:
  `gtkb-impl-auth-per-session-pointer-isolation`,
  `gtkb-prompt-role-hint-authority-emergency-fix`, and
  `gtkb-tafe-bridge-index-preview`.
- The current dirty diff changes:
  - `groundtruth-kb/src/groundtruth_kb/bridge/worker.py`: Windows Codex worker
    invocation changes from `subprocess.CREATE_NEW_CONSOLE` to
    `subprocess.CREATE_NO_WINDOW`.
  - `scripts/cross_harness_bridge_trigger.py`: `_spawn_harness` changes Windows
    `creationflags` from `CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP` to
    `CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP`, and changes the non-Windows
    fallback from `getattr(subprocess, "CREATE_NO_WINDOW", 0)` to `0`.
- Current line references after the dirty edit:
  - `scripts/cross_harness_bridge_trigger.py:2449` and `:2450` use
    `CREATE_NO_WINDOW` plus `CREATE_NEW_PROCESS_GROUP`; `:2496` passes the
    computed `creationflags` into `subprocess.Popen`.
  - `groundtruth-kb/src/groundtruth_kb/bridge/worker.py:311` and `:345` use
    `subprocess.CREATE_NO_WINDOW`.
- The three live GO proposals do not authorize these two files:
  - `bridge/gtkb-impl-auth-per-session-pointer-isolation-003.md:17` targets
    implementation authorization scripts and tests, not the trigger or worker.
  - `bridge/gtkb-prompt-role-hint-authority-emergency-fix-001.md:22` targets
    role-hint/session-start source and tests, not the trigger or worker.
  - `bridge/gtkb-tafe-bridge-index-preview-001.md:22` targets TAFE preview
    source and tests, not the trigger or worker.
- `python .claude/skills/bridge/helpers/show_thread_bridge.py
  gtkb-impl-auth-per-session-pointer-isolation --format json --preview-lines
  60` reports no drift and latest status `GO`, but that GO is for `WI-4443`,
  not `WI-4529`.

## Finding

### FINDING-P1-001 - WI-4529 fix appears present without bridge authorization

Observation: The dirty source edit directly implements the behavior described
by `WI-4529`, but the live bridge has no matching indexed thread for `WI-4529`
and the current Prime-actionable GO threads do not list either touched source
file in `target_paths`.

Deficiency rationale: GT-KB's file bridge is the implementation authorization
path for source, hook, script, test, and configuration changes. A small,
obvious fix still needs a bridge proposal, target paths, specification links,
and a verification plan so later reviewers can connect the committed diff to
the accepted work item and run the right tests. Otherwise the commit history
will show an unscoped bridge-dispatch source change and the backlog row will
remain difficult to reconcile.

Proposed solution/enhancement: Prime Builder should file a narrow bridge
proposal for `WI-4529` before committing the dirty source changes, or explicitly
revise an existing active bridge thread to include `WI-4529` and both target
paths if the work is intentionally bundled. The clean proposal should include:

- `Work Item: WI-4529`
- target paths for `scripts/cross_harness_bridge_trigger.py` and
  `groundtruth-kb/src/groundtruth_kb/bridge/worker.py`
- a Windows-specific verification plan asserting `CREATE_NO_WINDOW` is passed
  at the direct trigger spawn, monitor spawn, and bridge worker spawn surfaces
- a non-Windows regression assertion that `creationflags` remains `0`
- ruff check and format gates for touched Python files

Option rationale: A normal bridge proposal is lower-risk than committing the
dirty patch as an emergency exception. The issue is user-visible annoyance, not
a bridge outage or credential-safety incident, and the source delta is small
enough to review quickly.

## Prime Builder Implementation Context

| Element | Details |
|---|---|
| Objective | Land `WI-4529` through the normal bridge lifecycle so Windows dispatch no longer flashes empty Python consoles. |
| Preconditions | Resolve any unrelated dirty worktree changes; preserve current unowned edits until ownership is clear. |
| Evidence paths | `scripts/cross_harness_bridge_trigger.py`, `groundtruth-kb/src/groundtruth_kb/bridge/worker.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, bridge thread target path lists cited above. |
| File touchpoints | Likely the two source files above plus focused tests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` and/or an existing bridge worker test surface. |
| Implementation sequence | File `WI-4529` proposal, receive GO, acquire implementation authorization, apply or retain the two-line/four-line creationflags change, add regression tests, file implementation report. |
| Verification steps | Focused pytest for trigger/worker spawn flags; `ruff check` and `ruff format --check` on touched Python files; live diagnose smoke check with no bridge work consumed. |
| Rollback notes | Revert only the `CREATE_NO_WINDOW` creationflag changes and associated tests. |
| Open decisions | None for this report. |

## Commands Executed

```text
python -m groundtruth_kb.cli backlog list --id WI-4529 --json
rg -n "WI-4529|flash empty python.exe|CREATE_NO_WINDOW|CREATE_NEW_CONSOLE|WindowStyle|subprocess|python.exe console" independent-progress-assessments bridge memory .claude .codex scripts groundtruth-kb platform_tests config -g "!archive/**" -g "!*.lock"
rg -n "Popen|run\(|CREATE_NO_WINDOW|CREATE_NEW_CONSOLE|DETACHED_PROCESS|STARTF_USESHOWWINDOW|creationflags|start_new_session|python.exe|sys.executable|subprocess" scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\bridge\worker.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
git diff -- scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\bridge\worker.py
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-prompt-role-hint-authority-emergency-fix --format json --preview-lines 80
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-tafe-bridge-index-preview --format json --preview-lines 80
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-impl-auth-per-session-pointer-isolation --format json --preview-lines 60
rg -n "CREATE_NO_WINDOW|CREATE_NEW_PROCESS_GROUP|CREATE_NEW_CONSOLE|creationflags" scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\bridge\worker.py
rg -n "target_paths:|Work Item:|Document:" bridge\gtkb-prompt-role-hint-authority-emergency-fix-001.md bridge\gtkb-tafe-bridge-index-preview-001.md bridge\gtkb-impl-auth-per-session-pointer-isolation-003.md
```

## Owner Action Required

None. This report asks Prime Builder to route the already-visible fix through
the normal bridge protocol before committing it.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
