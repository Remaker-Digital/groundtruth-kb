REVISED

# GT-KB Bridge Revised Implementation Report - WI-4944 - 009

bridge_kind: implementation_report
Document: gtkb-wi4944-release-dispatcher-lo-dispatch-unblock
Version: 009
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: 2026-07-01T10-30-33Z-prime-builder-A-194b67
author_model: GPT-5 Codex
author_model_version: 2026-07-01 runtime
author_model_configuration: Codex auto-dispatch, Prime Builder role, approval_policy=never, cwd=E:\GT-KB

Responds to NO-GO: bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-008.md
Reviewed implementation report: bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-007.md
Approved proposal: bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-001.md
GO verdict: bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-002.md

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4944-LO-DISPATCH-UNBLOCK
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4944

target_paths: ["scripts/openrouter_harness.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_dispatcher_runtime.py", "bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-*.md"]

Recommended commit type: fix(dispatch)

---

## Revision Summary

The v008 NO-GO's immediate environmental blocker is resolved: this session created the focused WI-4944 commit that prior attempts could not create.

The thread is not ready for VERIFIED. Commit-anchored verification from a clean export of that commit fails because the four-file WI-4944 commit does not include broader dispatcher topology/projection state that is present in the dirty root worktree. This report records the changed blocker instead of overclaiming completion.

## First-Line Role Eligibility And Work-Intent Claim

Prime Builder role was resolved through the canonical reader:

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
```

The role map reports harness `A` (`codex`) as `prime-builder`. The live bridge scan reports latest status `NO-GO` at `bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-008.md`, so Prime Builder is authorized to file this `REVISED` response.

Work-intent claim evidence:

```json
{
  "rowid": 28199,
  "session_id": "2026-07-01T10-30-33Z-prime-builder-A-194b67",
  "acting_role": "prime-builder",
  "claim_kind": "draft",
  "latest_bridge_status": "NO-GO",
  "expired": false
}
```

Implementation-start packet evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4944-release-dispatcher-lo-dispatch-unblock
packet_hash: sha256:753a63b1e4d4bb5b1434fbf103611e712e260f6f2071997ef2a8a04ea26913ab
latest_status: NO-GO
go_file: bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-002.md
```

## NO-GO Response

The v008 blocking issue was: no focused WI-4944 implementation commit exists.

That specific blocker is now resolved:

```text
git commit -m "fix(dispatch): add OpenRouter UTF-8 output safety and explicit stdin prompt transport (WI-4944)" -- scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py

[research c45b5a28d] fix(dispatch): add OpenRouter UTF-8 output safety and explicit stdin prompt transport (WI-4944)
 4 files changed, 34 insertions(+), 2 deletions(-)
```

Commit scope evidence:

```text
git show --name-status --oneline --stat --no-renames c45b5a28d
c45b5a28d fix(dispatch): add OpenRouter UTF-8 output safety and explicit stdin prompt transport (WI-4944)
M       platform_tests/scripts/test_dispatcher_runtime.py
M       platform_tests/scripts/test_openrouter_harness.py
M       scripts/dispatcher_runtime.py
M       scripts/openrouter_harness.py
```

The four WI-4944 paths are clean in the root worktree after the commit:

```text
git diff --cached --name-status -- scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
<no output>

git status --short -- scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
<no output>
```

## Root Worktree Verification Evidence

Focused gates on the root working tree pass:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
4 files already formatted
```

Focused pytest with workspace-local temp roots:

```text
$env:TEMP = E:\GT-KB\.tmp-pytest-wi4944\envtmp
$env:TMP = E:\GT-KB\.tmp-pytest-wi4944\envtmp
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --no-header --basetemp E:\GT-KB\.tmp-pytest-wi4944\basetemp-dispatch-103033 -o cache_dir=.tmp-pytest-wi4944\cache-dispatch-103033
160 passed in 34.95s
```

## Commit-Anchored Verification Evidence

A detached `git worktree` could not be created because this sandbox still cannot write `.git/worktrees` metadata:

```text
git worktree add --detach .gtkb-state/wi4944-clean-c45b5a28d c45b5a28d
fatal: could not create directory of '.git/worktrees/wi4944-clean-c45b5a28d': Permission denied
```

Prime Builder therefore used a clean `git archive` export of the exact commit:

```text
git archive --format=tar c45b5a28d | tar -xf - -C E:\GT-KB\.gtkb-state\wi4944-archive-c45b5a28d
```

Ruff gates pass from that clean commit export:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
All checks passed!

E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/openrouter_harness.py scripts/dispatcher_runtime.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py
4 files already formatted
```

The first archive pytest attempt failed before test bodies because the nested `--basetemp` parent directory did not exist. After creating that temp root, the commit-anchored pytest run executed and failed:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --no-header --basetemp E:\GT-KB\.gtkb-state\wi4944-archive-c45b5a28d\.tmp-pytest-wi4944\basetemp-run2 -o cache_dir=.tmp-pytest-wi4944\cache-run2
42 failed, 118 passed in 42.45s
```

Representative failures are dispatcher topology/projection expectations, not OpenRouter UTF-8 output regressions:

```text
test_resolve_dispatch_target_attaches_invocation_surfaces_from_projection
E   AssertionError: assert 'F' == 'A'

test_lo_provider_failure_backoff_falls_back_after_max_turn_marker
E   AssertionError: assert 'F' == 'D'

test_resolve_exactly_one_active_dispatches
E   AssertionError: assert 'A' == 'B'
```

This means the focused commit exists and is lint-clean, but the clean commit alone is not yet independently verifiable by the focused pytest slice.

## Scope-Drift Evidence

The root worktree differs from commit `c45b5a28d` in dispatcher topology/projection files outside the four-file WI-4944 focused commit:

```text
git diff --name-status c45b5a28d -- harness-state/harness-registry.json config/dispatcher/rules.toml groundtruth-kb/src/groundtruth_kb/bridge/role_state.py scripts/ops/harness_storm_watchdog_launcher.py
M       config/dispatcher/rules.toml
M       harness-state/harness-registry.json

git diff --stat c45b5a28d -- harness-state/harness-registry.json config/dispatcher/rules.toml groundtruth-kb/src/groundtruth_kb/bridge/role_state.py scripts/ops/harness_storm_watchdog_launcher.py
 config/dispatcher/rules.toml        | 14 +++++------
 harness-state/harness-registry.json | 50 +++++++++++++++++++++----------------
 2 files changed, 35 insertions(+), 29 deletions(-)
```

Inference from the evidence: the root working tree's passing pytest result depends on uncommitted dispatcher topology/projection state outside the focused WI-4944 commit. That state is not in the four-file commit and is not inside this WI-4944 v009 report's target path set except for dispatcher config in the original proposal. The adjacent WI-4943 GO explicitly includes release topology/projection reconciliation, including `config/dispatcher/rules.toml` and `harness-state/harness-registry.json`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this `REVISED` report continues the numbered bridge chain and responds to the live latest `NO-GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal v001 remains the governing implementation scope for the committed source/test fix.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries Project Authorization, Project, Work Item, and target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - `VERIFIED` is not requested because commit-anchored pytest is not passing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the changed blocker is preserved as append-only bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation evidence is tied to a concrete commit hash plus test results instead of staged state.
- `GOV-STANDING-BACKLOG-001` - WI-4944 remains visible until Loyal Opposition can verify the committed implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the PAUTH expiry remains explicit at `2026-07-02T00:00:00Z`.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the committed code remains dispatcher-owned and topology-driven.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - the clean export failures indicate dispatcher topology/projection state is now the verification constraint.
- `ADR-DISPATCHER-ARCHITECTURE-001` - no retired poller or alternate queue was restored.
- `DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001` - failing LO components remain isolated by dispatcher fallback behavior.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - worker lifecycle boundedness remains covered by the focused dispatcher runtime test slice, but not yet clean-commit passing.

## Owner Decisions / Input

Existing owner authorization remains `DELIB-202665107` and `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4944-LO-DISPATCH-UNBLOCK`, expiring `2026-07-02T00:00:00Z` unless renewed or replaced.

No new owner decision was requested or available to this non-interactive auto-dispatch worker. The next technical dependency is to reconcile the dispatcher topology/projection state already covered by the adjacent WI-4943 GO, or to file a separate scoped revision if Loyal Opposition determines WI-4944 must own that topology state directly.

## Prior Deliberations

- `DELIB-202665107` - owner authorized WI-4944 scoped LO dispatch unblock lane.
- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized the adjacent WI-4943 release-branch dispatcher substrate reconciliation lane.
- `DELIB-20266276` - daemon-resilience scope-lock.
- `DELIB-20266084` - dispatcher daemon foundation authorization.
- `bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-001.md` - approved WI-4944 proposal.
- `bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-002.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-008.md` - latest NO-GO requiring a focused commit and clean verification.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-006.md` - adjacent GO for release topology/projection reconciliation.

## Findings Addressed

- `v008 blocking issue: no focused WI-4944 commit exists` - resolved by commit `c45b5a28d`.

## Remaining Blocker

The focused commit does not yet satisfy `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` because commit-anchored focused pytest fails (`42 failed, 118 passed`). The verification blocker is now clean-commit topology/projection state, not Git commit permission.

## Scope Changes

This dispatch created one focused implementation commit:

- `c45b5a28d fix(dispatch): add OpenRouter UTF-8 output safety and explicit stdin prompt transport (WI-4944)`

It did not edit additional source/test/config files after creating the commit. The only new live bridge artifact requested by this report is `bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-009.md`.

## Pre-Filing Preflight Subsection

The governed revision helper runs `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4944-release-dispatcher-lo-dispatch-unblock --content-file <candidate>` and `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4944-release-dispatcher-lo-dispatch-unblock --content-file <candidate>` before filing this live bridge artifact. The revision is filed only if those candidate preflights pass.

## Verification Plan

No `VERIFIED` request is made. The remaining verification plan is:

1. Reconcile the dispatcher topology/projection state covered by WI-4943 or a revised WI-4944 scope.
2. Create a commit or commit series whose clean export includes the required topology/projection state.
3. Rerun ruff check, ruff format check, and the focused pytest slice from that clean commit state.
4. File a new implementation report only when commit-anchored verification passes or an explicit owner waiver is recorded.

## Risk And Rollback

Risk is that Loyal Opposition sees a focused commit and assumes the WI-4944 implementation is verifiable. This report prevents that by recording the clean-export failure and keeping `VERIFIED` out of scope.

Rollback for the WI-4944 implementation commit is a focused revert of `c45b5a28d` if the committed source/test changes must be backed out. Rollback for this report is not applicable because bridge files are append-only audit evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
