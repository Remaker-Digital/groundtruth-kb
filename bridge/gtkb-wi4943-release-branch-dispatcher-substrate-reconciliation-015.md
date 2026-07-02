NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-01T17-43-00Z-prime-builder-A-c0d3a1
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; Prime Builder via ::init gtkb pb; bridge helper filing with governed workspace tools

# GT-KB Bridge Implementation Blocker Report - gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation - 015

bridge_kind: implementation_report
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 015 (NEW; implementation blocker report)
Responds to GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-014.md
Approved proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-013.md
Recommended commit type: fix(dispatch) after renewed GO

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

## Implementation Claim

Prime Builder opened the GO-scoped implementation lane, created a fresh in-root release worktree from `origin/main`, and applied only the approved dispatcher-substrate path snapshot from verified commit `99fbb9db` into that worktree. No release commit was created and no root dirty worktree staging was used.

Implementation failed closed before release verification could proceed. The verified dispatcher snapshot updates `groundtruth-kb/src/groundtruth_kb/cli.py` so that importing the CLI requires `groundtruth_kb.backlog.query`, but the fresh `origin/main` worktree does not contain that module and the v013/v014 target envelope does not authorize the backlog module paths. Per the v014 implementation precondition, Prime Builder is filing this blocker report instead of adding out-of-envelope source paths.

The release worktree currently contains staged, uncommitted integration output at `E:/GT-KB/.gtkb-state/release-worktrees/wi4943-dispatcher-release-20260701` on branch `codex/wi4943-dispatcher-release-main-20260701`. It must not be committed until Loyal Opposition returns a renewed GO and the implementation completes successfully.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` remains the owner authorization for this WI-4943 release-dispatcher lane.
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE` remains active and expires `2026-07-02T00:00:00Z`.
- Owner deployment-boundary directive preserved: GT-KB remains provider-neutral; Azure is not a default GT-KB release-health dependency.
- Owner deferral directive preserved: this blocker is not deferred indefinitely. It expires with the PAUTH on `2026-07-02T00:00:00Z` unless explicitly renewed or resolved by a revised GO.

## Prior Deliberations

- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-013.md` - revised proposal adding `scripts/windows_subprocess.py` to the envelope.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-014.md` - LO GO with explicit precondition to fail closed if another out-of-envelope dependency appears.
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-006.md` - terminal VERIFIED source snapshot used for the scoped checkout boundary.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - terminal VERIFIED supervisor-governance evidence included in the scoped checkout boundary.
- `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-004.md` - terminal VERIFIED Cursor-route evidence included in the scoped checkout boundary.

## Commands Run

```text
git fetch origin main
git worktree add -b codex/wi4943-dispatcher-release-main-20260701 .gtkb-state/release-worktrees/wi4943-dispatcher-release-20260701 origin/main
git checkout 99fbb9db -- <approved v013/v014 target pathspecs>
git status --short --branch
git diff --name-only --cached | rg "groundtruth-kb/src/groundtruth_kb/backlog|openrouter_harness|applications/Agent_Red"
rg -n "Azure|azure" README.md docs/gtkb-dashboard/grafana/README.md groundtruth-kb/docs/wiki/release-health.md groundtruth-kb/docs/method/12-file-bridge-automation.md
python -c "import sys; sys.path.insert(0, '<release-worktree>/groundtruth-kb/src'); from groundtruth_kb.cli import main; main()" bridge dispatch daemon status --json
python -c "import sys; sys.path.insert(0, '<release-worktree>/groundtruth-kb/src'); from groundtruth_kb.cli import main; main()" bridge dispatch health --json
python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_cursor_harness.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py -q --tb=short
git diff --name-status origin/main..99fbb9db -- groundtruth-kb/src/groundtruth_kb/backlog groundtruth-kb/src/groundtruth_kb/backlog.py
```

## Observed Results

- Fresh worktree created from `origin/main` at `4c9da49148adf6bae91b66da51b3308b33be4678`.
- Pre-integration baseline in the fresh worktree: `gt bridge dispatch health --json` returned `PASS`, but `gt bridge dispatch daemon status --json` failed because `daemon` was not a command on `origin/main`.
- Approved-path checkout from `99fbb9db` succeeded and staged only the v013/v014 target path set.
- Diff guard returned `NO_MATCH` for `groundtruth-kb/src/groundtruth_kb/backlog`, `openrouter_harness`, and `applications/Agent_Red`, confirming the staged integration did not silently add those paths.
- Provider-neutral docs check found only acceptable Azure text: Azure reconciliation is described as optional adopter/application diagnostic scope, not a default GT-KB dependency.
- All four dispatch CLI commands attempted after integration failed at import time with:

```text
ModuleNotFoundError: No module named 'groundtruth_kb.backlog.query'
```

- Evidence line: `groundtruth-kb/src/groundtruth_kb/cli.py:26` imports `from groundtruth_kb.backlog.query import ...`.
- The release worktree contains `groundtruth-kb/src/groundtruth_kb/backlog/__init__.py` and `approval_state.py`, but not `query.py`.
- Dependency audit shows the verified snapshot has backlog changes outside the v013/v014 target envelope:

```text
M groundtruth-kb/src/groundtruth_kb/backlog.py
M groundtruth-kb/src/groundtruth_kb/backlog/__init__.py
M groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py
A groundtruth-kb/src/groundtruth_kb/backlog/query.py
```

- Focused pytest could not proceed past collection:
  - `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py` failed on the same missing `groundtruth_kb.backlog.query` import.
  - `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` also reported `ModuleNotFoundError: No module named 'psutil'` in the current test environment. This is a test-environment dependency observation, not the source-envelope blocker. The source-envelope blocker is the missing backlog query module.

## Blocker Findings

### P0 - `groundtruth_kb.backlog.query` dependency is outside the approved envelope

Evidence: after applying only approved v013/v014 paths, `groundtruth-kb/src/groundtruth_kb/cli.py:26` requires `groundtruth_kb.backlog.query`, but `groundtruth-kb/src/groundtruth_kb/backlog/query.py` is absent from `origin/main` and absent from the approved target path list.

Impact: no `gt` CLI command can import from the release worktree after the dispatcher CLI snapshot is applied, including the dispatcher health/status/daemon/drain commands required for release verification.

Recommended action: return `NO-GO` and require a revised proposal that either adds the exact backlog dependency paths to the target envelope or explicitly authorizes an in-envelope CLI refactor that removes the top-level dependency for dispatcher commands. Prime Builder recommends adding the observed backlog dependency paths if Loyal Opposition agrees they are the verified dependency closure.

### P2 - Focused daemon test environment lacks `psutil`

Evidence: `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` failed collection with `ModuleNotFoundError: No module named 'psutil'`.

Impact: after the source-envelope blocker is resolved, focused daemon tests may still require the test environment to provide `psutil` or the test dependency to be handled by the repo's release-test dependency path.

Recommended action: do not treat this as the current bridge-envelope blocker. Re-run the focused tests after the source dependency closure is approved; then classify `psutil` as either environment setup, dependency metadata, or test refactor if it still blocks release verification.

## Specification-Derived Verification Status

| Specification | Status |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | BLOCKED. Dispatcher CLI commands cannot import because `groundtruth_kb.backlog.query` is missing. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | BLOCKED. Daemon/runtime tests could not run to behavior verification. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | PARTIAL. Scoped diff did not include `openrouter_harness`, Agent Red, or retired poller/trigger path expansion. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | BLOCKED. Supervisor/no-window tests could not complete past import/test-environment setup. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | PASS for fail-closed behavior. Implementation stopped when an out-of-envelope source dependency appeared. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | BLOCKED. This report provides negative evidence; no release verification is claimed. |
| Provider-neutral dashboard directive | PASS for the checked docs: Azure appears only as optional adopter/application diagnostic wording. |

## Files Touched

Release worktree only, staged and uncommitted:

- The approved v013/v014 dispatcher, supervisor, Cursor, config, harness-state, doc, test, and bridge evidence target paths from `99fbb9db`.

Root checkout:

- This bridge implementation blocker report will be filed as the next numbered bridge artifact.

No commit or push was created.

## Acceptance Criteria Status

- [x] Fresh in-root worktree from `origin/main` created.
- [x] Dirty root checkout was not used for release staging.
- [x] Integration source snapshot stopped at verified `99fbb9db`, avoiding later WI-4944 `scripts/openrouter_harness.py` changes.
- [x] Provider-neutral dashboard/Azure wording remained acceptable in checked docs.
- [ ] Release-worktree `gt bridge dispatch daemon status --json` succeeds.
- [ ] Release-worktree dispatcher health/status/drain/daemon commands pass after integration.
- [ ] Focused dispatcher tests pass.
- [ ] Daemon-driven bounded LO dispatch path verified.
- [ ] Release commit prepared.

## Loyal Opposition Asks

1. Return `NO-GO` if you agree the backlog query dependency is outside the v013/v014 envelope.
2. In the NO-GO, identify whether the corrected revision should add the observed backlog dependency paths or authorize an in-envelope CLI lazy-import/refactor approach.
3. Treat `psutil` separately from the source-envelope blocker unless the source dependency closure is approved and focused tests still fail on environment setup.
