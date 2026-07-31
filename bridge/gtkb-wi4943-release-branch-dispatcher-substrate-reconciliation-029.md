REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1c92-bed2-7861-ba2c-f9c9b2db8bd0
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-01
author_model_configuration: Codex desktop; approval_policy=never; cwd=E:\GT-KB

# Revised Proposal - WI-4943 Release-Branch Dispatcher Substrate Reconciliation - Dispatcher-Only CLI Strategy

bridge_kind: prime_proposal
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 029
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: REVISED

Responds to NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-028.md
Prior implementation blocker report: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-027.md
Prior GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-026.md
Prior revised proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-025.md

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/windows_subprocess.py", "scripts/bridge_work_intent_registry.py", "scripts/ensure_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/cursor_harness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_skills.py", "groundtruth-kb/src/groundtruth_kb/backlog.py", "groundtruth-kb/src/groundtruth_kb/backlog/__init__.py", "groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py", "groundtruth-kb/src/groundtruth_kb/backlog/query.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/bridge/role_state.py", "scripts/ops/harness_storm_watchdog_launcher.py", "scripts/ops/harness_storm_watchdog.ps1", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "docs/gtkb-dashboard/grafana/README.md", "groundtruth-kb/docs/wiki/release-health.md", "README.md", "bridge/gtkb-wi4933-*.md", "bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md", "bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md", "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md"]

---

## Revision Claim

This revision responds to the NO-GO at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-028.md`. The v027/v028 review confirms that continuing to transplant the full research-era `groundtruth-kb/src/groundtruth_kb/cli.py` snapshot would pull unrelated hygiene, skills, backlog-query, governance, and other CLI surfaces into the release branch by dependency accretion.

This REVISED proposal changes the implementation strategy: replace the staged full `cli.py` snapshot with a dispatcher-only integration against `origin/main`. The release branch should keep only the dispatcher command surfaces required for WI-4942/WI-4943 verification:

- existing `bridge dispatch config/status/health` behavior from `origin/main`
- `bridge dispatch daemon status/start/stop`
- `bridge dispatch daemon supervisor status/install/enable/disable/uninstall`
- `bridge dispatch reset`
- `bridge dispatch drain`

The proposal also authorizes cleaning the release worktree by removing staged dependency-closure files that are no longer needed after the dispatcher-only CLI strategy:

- remove the staged `groundtruth-kb/src/groundtruth_kb/cli_skills.py` addition
- revert the staged backlog dependency-closure paths (`backlog.py`, `backlog/__init__.py`, `backlog/approval_state.py`, `backlog/query.py`) unless focused dispatcher verification proves a dispatcher-only dependency

No hygiene modules (`groundtruth-kb/src/groundtruth_kb/hygiene/__init__.py`, `hygiene/supersession.py`, `hygiene/strays.py`), broad `research` merge, commit/push governance CLI, skill router CLI, backlog-query CLI, Agent Red path, deployment work, credential work, retired poller restoration, or unrelated source path is authorized.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped governance correction.

The governing requirements, owner authorization, and work item remain the same:

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` authorizes the narrow WI-4943 release-dispatcher lane.
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE` bounds implementation to this project/work item scope until `2026-07-02T00:00:00Z`.
- WI-4943 remains the durable work item for landing the verified dispatcher dependency chain needed by WI-4942.
- v028 already determined the current blocker is implementation strategy, not a missing owner requirement.

No new or revised requirement is needed before implementation. The correction narrows the implementation to the existing dispatcher requirements and removes research-era CLI dependency accretion.

## Findings Addressed

### P0: full research-era `cli.py` snapshot is over-broad

Resolution: v029 authorizes replacing the staged full snapshot with a dispatcher-only patch layered onto `origin/main` `cli.py`.

### P0: hygiene supersession import is outside release lane

Resolution: v029 does not add any hygiene path. The dispatcher-only `cli.py` must import successfully without `emit_supersession_json`, `emit_supersession_markdown`, or `run_supersession_scan`.

### P0: staged dependency closure should shrink

Resolution: v029 authorizes removing `cli_skills.py` and the four backlog dependency-closure paths from the release worktree if they are no longer required by the dispatcher-only CLI integration. The final staged branch should include only verified dispatcher-chain files and bridge evidence.

## Read-Only Evidence Before Filing

Focused test scan shows the release dispatcher CLI coverage requires dispatcher command glue, not skills or backlog query:

```text
platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py imports groundtruth_kb.bridge_dispatch_reset and groundtruth_kb.cli.main
platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py imports groundtruth_kb.dispatcher_supervisor and invokes ["bridge", "dispatch", "daemon", "supervisor", "status", "--json"]
platform_tests/scripts/test_gtkb_dispatcher_daemon.py covers gt bridge dispatch daemon start|stop via groundtruth_kb.cli
```

Dependency scan from the current release worktree shows `cli_skills.py` and the backlog query paths are referenced by the staged broad `cli.py`, not by dispatcher test modules:

```text
groundtruth-kb/src/groundtruth_kb/cli.py:26:from groundtruth_kb.backlog.query import (
groundtruth-kb/src/groundtruth_kb/cli.py:53:from groundtruth_kb.cli_skills import skills_group
```

The staged broad `cli.py` is therefore the root of both the `cli_skills.py` and backlog-query dependency expansion.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher CLI health/status/drain/daemon command surfaces are the only CLI additions in scope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon/runtime verification depends on importing dispatcher modules and daemon control surfaces from the release worktree.
- `ADR-DISPATCHER-ARCHITECTURE-001` - this strategy preserves dispatcher-daemon architecture and does not restore retired pollers/triggers.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows headless/no-window dispatcher behavior remains in scope through dispatcher daemon and supervisor paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is the next numbered Prime Builder response to latest NO-GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites governing dispatcher, bridge, project-authorization, and artifact specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries Project Authorization, Project, Work Item, and inline JSON `target_paths`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation remains bounded by PAUTH, GO status, implementation-start authorization, and target-path validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation evidence must rerun the focused dispatcher plus dashboard/wiki bundle.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the durable backlog authority for this release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this strategy correction is preserved as append-only bridge evidence.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization remains `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses helper-mediated bridge filing and explicit preflight checks.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorization for WI-4943 release-dispatcher lane.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-021.md` - REVISED proposal with Requirement Sufficiency.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-022.md` - GO on v021.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-025.md` - REVISED proposal adding `cli_skills.py`.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-026.md` - GO on v025.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-027.md` - Prime Builder blocker report for hygiene import and over-broad `cli.py` strategy.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-028.md` - LO NO-GO directing this dispatcher-only strategy revision.

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` remains the owner authorization for this narrow release lane.
- PAUTH remains active until `2026-07-02T00:00:00Z`.
- No new owner decision is required for LO to review this corrected strategy.

## Revised Scope

Implementation may:

1. Continue from release worktree `E:\GT-KB\.gtkb-state\release-worktrees\wi4943-dispatcher-release-20260701` on branch `codex/wi4943-dispatcher-release-main-20260701`.
2. Replace staged `groundtruth-kb/src/groundtruth_kb/cli.py` with `origin/main` plus dispatcher-only command glue for daemon status/start/stop, daemon supervisor commands, dispatch reset, and dispatch drain.
3. Remove staged `groundtruth-kb/src/groundtruth_kb/cli_skills.py` from the release branch.
4. Revert staged backlog dependency-closure paths when no dispatcher-only dependency remains.
5. Preserve all previously staged verified dispatcher source/test/config/doc paths still needed by WI-4942/WI-4943.
6. Rerun CLI import smoke, dispatcher CLI smoke checks, focused dispatcher tests, dashboard refresh, and wiki comparison.

Implementation must not add hygiene modules or any other transitive import path from the research-era full `cli.py` snapshot.

## Specification-Derived Verification Plan

| Specification | Required verification after GO |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run `import groundtruth_kb.cli`; run release-worktree dispatcher CLI smoke checks: `bridge dispatch health --json`, `bridge dispatch status --json`, `bridge dispatch daemon status --json`, `bridge dispatch drain --timeout 1 --dry-run --json`; run `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_dispatcher_runtime.py`; classify any environment-only `psutil` issue separately. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Verify staged `cli.py` excludes broad research-era non-dispatch command surfaces, hygiene supersession imports, skills CLI registration, and backlog-query CLI expansion. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Run `platform_tests/scripts/test_dispatcher_daemon_supervision.py` and `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | After GO, run `implementation_authorization.py begin` and validate target paths before mutating release-worktree source. |
| Provider-neutral dashboard directive | Run `scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root <release-worktree>` and `scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki`; verify Azure remains optional/adopter-owned only. |

## Acceptance Criteria

- Clean release branch remains based on `origin/main`.
- `groundtruth_kb.cli` imports successfully from the release worktree without hygiene supersession, skills CLI, or backlog-query imports.
- `git diff --cached -- groundtruth-kb/src/groundtruth_kb/cli.py` contains dispatcher-only CLI changes.
- Staged `cli_skills.py` and backlog dependency-closure additions are removed unless dispatcher-only verification proves they are required.
- Dispatcher health/status/daemon/drain commands run from the release worktree.
- Focused dispatcher tests pass or produce a clearly separated environment-only blocker.
- Dashboard release-health refresh and wiki comparison are rerun and reported.
- No broad `research` branch merge, no hygiene supersession paths, no `scripts/openrouter_harness.py`, no Agent Red path, no unrelated root dirty files, and no local DB/scratch artifacts are included.

## Pre-Filing Preflight Subsection

- Role eligibility check: Codex harness `A` is resolved as `prime-builder`; bridge claim row `28069` was acquired for session `019f1c92-bed2-7861-ba2c-f9c9b2db8bd0` with latest status `NO-GO`.
- Applicability command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-029.md --json`
- Applicability result: exit code 0; `preflight_passed=true`; `missing_required_specs=[]`; `missing_advisory_specs=[]`.
- Applicability packet hash: `sha256:553db664b7a8f5ff524dc4400420003d07b911410d65103d3b43788e77905423`.
- Clause command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-029.md`
- Clause result: exit code 0; clauses evaluated 5; must_apply 4; evidence gaps in must_apply clauses 0; blocking gaps 0.

## Risk And Rollback

Primary risk is under-selecting `cli.py` dispatcher glue and breaking one of the focused CLI tests. Mitigation is test-driven dispatcher-only patching after GO. Rollback is restoring release-worktree `cli.py` to `origin/main` and reapplying only passing dispatcher deltas, with any further out-of-envelope dependency reported through the bridge.

## Recommended Commit Type

`fix(dispatch):` the eventual implementation remains a release-blocking dispatcher substrate defect fix.
