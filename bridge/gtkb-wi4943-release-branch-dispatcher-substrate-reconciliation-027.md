NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1c92-bed2-7861-ba2c-f9c9b2db8bd0
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-01
author_model_configuration: Codex desktop; approval_policy=never; cwd=E:\GT-KB

# GT-KB Bridge Implementation Blocker Report - WI-4943 - 027

bridge_kind: implementation_report
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 027 (NEW; implementation blocker report)
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: NEW

Responds to GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-026.md
Approved proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-025.md
Recommended commit type: fix(dispatch) after revised integration strategy

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

---

## Implementation Claim

Implementation authorization succeeded against v025/v026 and Prime Builder applied exactly the newly authorized `groundtruth-kb/src/groundtruth_kb/cli_skills.py` path. The next release-worktree import check then failed on a non-dispatch hygiene import pulled by the staged `groundtruth-kb/src/groundtruth_kb/cli.py` snapshot.

This blocker is not simply another one-file dependency request. Static audit shows the staged `cli.py` snapshot is a broad research-era CLI expansion, not a narrow dispatcher CLI delta. Continuing to add every imported module risks turning WI-4943 into a broad `research` merge by dependency accretion, contrary to the release lane's reductive scope.

Prime Builder therefore failed closed before adding hygiene modules and recommends a corrected REVISED proposal that changes the implementation strategy: replace the staged full `cli.py` snapshot with a dispatcher-only `cli.py` integration against `origin/main`, rather than expanding this release envelope to unrelated hygiene/skills surfaces.

## Authorization Evidence

Prime Builder acquired a GO-implementation claim and ran:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --session-id 019f1c92-bed2-7861-ba2c-f9c9b2db8bd0
```

Observed result:

```text
"latest_status": "GO"
"proposal_file": "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-025.md"
"go_file": "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-026.md"
"requirement_sufficiency": "sufficient"
"packet_hash": "sha256:5d3aba30a3a1bdabf126de25d91b4ac011c773c1fc2ce1f48af3ef1f91585df8"
```

Prime Builder then applied only:

```text
git checkout 99fbb9db -- groundtruth-kb/src/groundtruth_kb/cli_skills.py
```

from release worktree `E:\GT-KB\.gtkb-state\release-worktrees\wi4943-dispatcher-release-20260701`.

## Blocker Evidence

After `cli_skills.py` was applied, the import smoke check failed:

```text
$env:PYTHONPATH='E:/GT-KB/.gtkb-state/release-worktrees/wi4943-dispatcher-release-20260701/groundtruth-kb/src'
E:/GT-KB/groundtruth-kb/.venv/Scripts/python.exe -c "import groundtruth_kb.cli; print('cli-import-ok')"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import groundtruth_kb.cli; print('cli-import-ok')
  File "E:\GT-KB\.gtkb-state\release-worktrees\wi4943-dispatcher-release-20260701\groundtruth-kb\src\groundtruth_kb\cli.py", line 81, in <module>
    from groundtruth_kb.hygiene import (
    ...<7 lines>...
    )
ImportError: cannot import name 'emit_supersession_json' from 'groundtruth_kb.hygiene'
```

Dispatcher CLI smoke checks failed for the same top-level import reason.

Dependency audit shows the hygiene closure in the verified snapshot:

```text
git diff --name-status origin/main..99fbb9db -- groundtruth-kb/src/groundtruth_kb/hygiene groundtruth-kb/src/groundtruth_kb/hygiene.py
M       groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py
A       groundtruth-kb/src/groundtruth_kb/hygiene/strays.py
A       groundtruth-kb/src/groundtruth_kb/hygiene/supersession.py
```

However, the broader CLI diff is not narrow:

```text
git diff --stat origin/main..99fbb9db -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/hygiene groundtruth-kb/src/groundtruth_kb/cli_skills.py
 groundtruth-kb/src/groundtruth_kb/cli.py           | 2088 ++++++++++++++++++--
 groundtruth-kb/src/groundtruth_kb/cli_skills.py    |  112 ++
 .../src/groundtruth_kb/hygiene/__init__.py         |   20 +
 .../src/groundtruth_kb/hygiene/strays.py           |  329 +++
 .../src/groundtruth_kb/hygiene/supersession.py     |  322 +++
 5 files changed, 2761 insertions(+), 110 deletions(-)

git diff --numstat origin/main..99fbb9db -- groundtruth-kb/src/groundtruth_kb/cli.py
1978    110     groundtruth-kb/src/groundtruth_kb/cli.py
```

A static AST pass over the staged `cli.py` found dozens of non-dispatch imports and command surfaces. The first observed top-level blocker is hygiene; continuing by adding hygiene modules is likely to pull additional unrelated CLI features into this release branch.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher CLI health/status/drain/daemon verification remains blocked until the CLI integration is dispatcher-scoped and importable.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher daemon/runtime verification remains blocked by CLI import failure.
- `ADR-DISPATCHER-ARCHITECTURE-001` - this report preserves dispatcher-daemon architecture and does not restore retired pollers or triggers.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows headless/no-window dispatcher behavior remains in scope only through reviewed dispatcher paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is the next numbered Prime Builder implementation report after latest GO v026.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal cites specs but the current integration strategy is proving over-broad.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must fail closed on target-path and scope validation gaps.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused verification is blocked because CLI import fails before dispatcher commands/tests can execute.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the durable backlog authority for the release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this blocker and strategy correction are preserved as append-only bridge artifacts.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization remains `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all cited work remains under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex is using helper-mediated bridge filing and explicit implementation-start evidence.

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` remains the owner authorization for this narrow release lane.
- PAUTH remains active until `2026-07-02T00:00:00Z`.
- No new owner decision is requested in this blocker report. The requested correction is a narrower engineering strategy inside the existing WI-4943 dispatcher release lane: avoid broad `cli.py` import closure and integrate only dispatcher CLI deltas needed for the approved dispatcher commands.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorization for the WI-4943 release-dispatcher lane.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-021.md` - corrected REVISED proposal with Requirement Sufficiency.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-022.md` - GO on v021.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-023.md` - Prime Builder blocker report for missing `cli_skills.py`.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-024.md` - LO NO-GO directing `cli_skills.py` target-envelope correction.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-025.md` - REVISED proposal adding `cli_skills.py`.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-026.md` - GO on v025.

## Specification-Derived Verification Plan

| Specification / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `implementation_authorization.py begin` succeeded against v025/v026; `cli_skills.py` was applied; next import check exposed broad non-dispatch hygiene dependency. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `import groundtruth_kb.cli` and dispatcher CLI smoke checks fail before execution with `ImportError: emit_supersession_json`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher daemon/runtime test execution is intentionally blocked until CLI import scope is corrected. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Prime Builder is reporting the blocker as the next numbered `NEW` implementation report after latest GO v026. |

## Commands Run

- `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --session-id 019f1c92-bed2-7861-ba2c-f9c9b2db8bd0` - succeeded with `requirement_sufficiency: sufficient`.
- `git checkout 99fbb9db -- groundtruth-kb/src/groundtruth_kb/cli_skills.py` in the release worktree - applied exactly the v025 newly approved path.
- `python -c "import groundtruth_kb.cli; print('cli-import-ok')"` with release-worktree `PYTHONPATH` - failed with `ImportError: emit_supersession_json`.
- Release-worktree dispatcher CLI smoke checks for `bridge dispatch status --json` and `bridge dispatch health --json` - failed with the same import error.
- `rg -n "emit_supersession_json|from groundtruth_kb.hygiene import|groundtruth_kb.hygiene" ...` - confirmed the import edge.
- `git diff --stat origin/main..99fbb9db -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/hygiene groundtruth-kb/src/groundtruth_kb/cli_skills.py` - confirmed broad CLI/hygiene scope.

## Observed Results

- Implementation authorization is healthy for v025/v026.
- The release worktree still cannot import `groundtruth_kb.cli`.
- The current integration approach is dragging unrelated non-dispatch CLI features into the release lane.
- No hygiene module was added.
- Focused dispatcher and dashboard/wiki verification remains pending until a corrected strategy receives GO and implementation authorization succeeds again.

## Files Changed

This blocker report changes only the append-only bridge audit chain through the helper-mediated filing of:

- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-027.md`

The release worktree staged dependency-chain output remains uncommitted.

## Acceptance Criteria Status

- [x] Run implementation-start authorization after v026 GO.
- [x] Apply only the approved `cli_skills.py` path.
- [x] Fail closed before adding out-of-envelope hygiene modules.
- [x] Preserve the strategy blocker as append-only bridge evidence.
- [ ] Receive LO NO-GO on this blocker report.
- [ ] File a corrected REVISED proposal changing the `cli.py` integration strategy to dispatcher-only deltas, or receive explicit LO direction that the hygiene closure is still appropriate.
- [ ] After renewed GO, rerun `implementation_authorization.py begin`, correct the release-worktree CLI scope, and rerun the focused dispatcher plus dashboard/wiki verification bundle.

## Risk And Rollback

Risk is that adding every transitive import from the staged `cli.py` snapshot becomes a broad research merge by another name. The mitigation is to stop dependency accretion now and revise the implementation strategy. Rollback is append-only for bridge evidence and, if needed, resetting/replacing only the staged `groundtruth-kb/src/groundtruth_kb/cli.py` in the release worktree with a dispatcher-scoped integration after renewed GO.

## Loyal Opposition Asks

1. Return `NO-GO` on this implementation blocker report because verification cannot proceed and adding hygiene modules would widen the release lane.
2. Confirm that the next Prime Builder action should be a corrected `REVISED` proposal authorizing a dispatcher-only `cli.py` integration strategy rather than a full research-era `cli.py` snapshot.
3. If Loyal Opposition believes adding the hygiene closure is acceptable instead, identify the exact paths and rationale so Prime Builder can evaluate whether that remains within the PAUTH and owner release-hygiene constraints.
