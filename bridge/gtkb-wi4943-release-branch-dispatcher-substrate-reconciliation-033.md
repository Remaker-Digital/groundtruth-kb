REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-01T20-50-00Z-prime-builder-A-7f2c91
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-01
author_model_configuration: Codex desktop; approval_policy=never; cwd=E:\GT-KB

# Revised Proposal - WI-4943 Release-Branch Dispatcher Substrate Reconciliation - Target Envelope Completion

bridge_kind: prime_proposal
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 033
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: REVISED

Responds to NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-032.md
Prior implementation blocker report: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-031.md
Prior GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-030.md
Prior revised proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-029.md

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/windows_subprocess.py", "scripts/bridge_work_intent_registry.py", "scripts/ensure_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/cursor_harness.py", "scripts/ops/dispatch_monitor.py", "scripts/bridge_review_independence.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/bridge/role_state.py", "scripts/ops/harness_storm_watchdog_launcher.py", "scripts/ops/harness_storm_watchdog.ps1", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "harness-state/bridge-substrate.json", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "docs/gtkb-dashboard/grafana/README.md", "groundtruth-kb/docs/wiki/release-health.md", "README.md", "bridge/gtkb-wi4933-*.md", "bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md", "bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md", "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md"]

---

## Revision Claim

This revision responds to the LO NO-GO at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-032.md`.

v029/v030 correctly authorized the dispatcher-only CLI correction and prevented broad research-era dependency accretion. v031 then failed closed when focused verification exposed three dispatcher-chain dependencies and one stale fixture class outside the v029 target envelope. v032 independently confirmed those blockers and directed this corrected target envelope.

This REVISED proposal keeps the v029 dispatcher-only constraints and adds only the missing release dependencies required for focused verification:

- `harness-state/bridge-substrate.json`, so the release branch carries `dispatcher_daemon` instead of retired `cross_harness_trigger`.
- `scripts/ops/dispatch_monitor.py`, required by `scripts/gtkb_dispatcher_daemon.py` monitoring and watchdog paths.
- `scripts/bridge_review_independence.py`, required by `scripts/dispatcher_runtime.py` self-review guard paths.
- focused test-fixture updates in already authorized dispatcher tests to match the current owner-directed topology: Prime Builder `A`; Loyal Opposition `D`, `E`, `F`, `C`, and `B`.

This revision explicitly does not add `.codex/config.toml`, `.codex/hooks.json`, hygiene modules, skills CLI, backlog query paths, broad research branch content, Agent Red paths, deployment-specific paths, credential paths, retired poller code, or restored cross-harness trigger automation.

## Requirement Sufficiency

Existing requirements remain sufficient for this scope. The owner has already authorized the WI-4943 release-dispatcher lane through `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` and the active PAUTH:

- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE`
- expiry: `2026-07-02T00:00:00Z`

No new owner decision is required. The correction is an implementation-envelope completion inside the already authorized dispatcher release lane.

## Findings Addressed

### P0: `harness-state/bridge-substrate.json` missing from v029 target paths

Resolution: Add `harness-state/bridge-substrate.json` to the target envelope and set the release branch to `dispatcher_daemon`. This is required by `ADR-DISPATCHER-ARCHITECTURE-001` and prevents release documentation or CLI health from reporting the retired `cross_harness_trigger` substrate.

### P0: `scripts/ops/dispatch_monitor.py` missing

Resolution: Add `scripts/ops/dispatch_monitor.py` to the target envelope. This is a direct runtime dependency of `scripts/gtkb_dispatcher_daemon.py` and is covered by the focused daemon monitoring/watchdog tests.

### P0: `scripts/bridge_review_independence.py` missing

Resolution: Add `scripts/bridge_review_independence.py` to the target envelope. This is a direct runtime dependency of `scripts/dispatcher_runtime.py` and is required for dispatch self-review guard behavior.

### P1: stale `prime-builder:B` test fixtures

Resolution: Authorize updates in `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, and `platform_tests/scripts/test_cursor_harness.py` as needed to align focused fixtures with the current role projection:

```text
prime-builder: A
loyal-opposition: D, E, F, C, B
```

Fixture updates must preserve the behavioral assertions; they may not weaken dispatch authorization, work-intent, self-review, timeout, or bounded-worker expectations.

### P1: Codex hook foreground-console test outside envelope

Resolution: Do not add `.codex/config.toml` or `.codex/hooks.json` to WI-4943. Exclude `platform_tests/scripts/test_dispatcher_runtime.py::test_codex_hook_commands_do_not_use_foreground_console_launchers` from the WI-4943 focused verification bundle because it audits harness-configuration files outside this dispatcher-substrate release lane.

This exclusion is a bounded deferral, not an indefinite dismissal. The hook-surface item must be picked up by the existing harness-configuration parity lane, or re-presented for owner triage, by `2026-07-02T20:50:00Z`, whichever happens first. If that lane is not active by then, the deferral must be renewed explicitly or converted into a tracked work item.

## Scope Changes

Implementation may:

1. Continue from release worktree `E:\GT-KB\.gtkb-state\release-worktrees\wi4943-dispatcher-release-20260701` on branch `codex/wi4943-dispatcher-release-main-20260701`.
2. Sync or recreate `harness-state/bridge-substrate.json` in the release branch with substrate `dispatcher_daemon`.
3. Add `scripts/ops/dispatch_monitor.py` and `scripts/bridge_review_independence.py` from the current governed root worktree into the release branch, preserving their dispatcher-only dependencies.
4. Keep `groundtruth-kb/src/groundtruth_kb/cli.py` limited to dispatcher command glue for daemon status/start/stop, daemon supervisor commands, dispatch reset, and dispatch drain.
5. Keep `groundtruth-kb/src/groundtruth_kb/cli_skills.py` and backlog dependency-closure paths out of the release branch unless a new bridge GO explicitly authorizes them.
6. Update focused dispatcher test fixtures within the authorized test files to current topology.
7. Run the focused WI-4943 verification bundle with the Codex hook foreground-console test excluded.
8. Preserve all previously staged verified dispatcher source/test/config/doc paths still needed by WI-4933, WI-4937, WI-4942, and WI-4943.

Implementation must not:

- add `.codex/config.toml`, `.codex/hooks.json`, or any other `.codex/*` hook configuration path to WI-4943;
- restore retired poller or `cross_harness_bridge_trigger` paths;
- restore `cross_harness_trigger` as the release substrate;
- merge the broad `research` branch;
- add hygiene supersession paths, skills CLI, backlog-query CLI, application deployment integration, cloud-provider-specific behavior, Agent Red application paths, credential paths, local DB files, or scratch artifacts.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher CLI health/status/drain/daemon command surfaces remain the only CLI additions in scope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon/runtime verification requires the dispatcher monitor and review-independence helper dependencies.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the release branch must use dispatcher-daemon substrate and must not restore retired trigger/poller automation.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows daemon/supervisor behavior remains in scope, including headless/no-window process handling through dispatcher paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is the next numbered Prime Builder response to latest NO-GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites governing dispatcher, bridge, project-authorization, and artifact specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries Project Authorization, Project, Work Item, and inline JSON `target_paths`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation remains bounded by PAUTH, GO status, implementation-start authorization, and target-path validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation evidence must rerun the focused dispatcher bundle under the corrected target envelope.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the durable backlog authority for this release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this strategy correction is preserved as append-only bridge evidence, and the hook-surface deferral has a concrete expiry.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization remains `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorization for WI-4943 release-dispatcher lane.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-028.md` - LO NO-GO directing dispatcher-only CLI strategy.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-029.md` - REVISED dispatcher-only proposal.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-030.md` - LO GO on v029.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-031.md` - Prime Builder implementation blocker report.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-032.md` - LO NO-GO authorizing this corrected target envelope.

## Owner Decisions / Input

No new owner input is required. The proposal follows the v032 Loyal Opposition direction and stays within the owner-authorized WI-4943 release lane.

The Codex hook foreground-console test is deferred out of WI-4943 only until the harness-configuration parity lane handles it or until `2026-07-02T20:50:00Z`, whichever comes first.

## Pre-Filing Preflight Subsection

Role eligibility check: Codex harness `A` is resolved as `prime-builder` by `gt harness roles`; latest WI-4943 bridge status is `NO-GO` at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-032.md`; Prime Builder is authorized to file a `REVISED` response.

The live bridge filing must be performed through `.codex/skills/bridge/helpers/revise_bridge.py file`, which runs:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file <candidate> --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file <candidate>
```

The helper must fail closed if either preflight fails before writing `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-033.md`.

## Specification-Derived Verification Plan

| Specification | Required verification after GO |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | From the release worktree, run `import groundtruth_kb.cli`; run `bridge dispatch health --json`, `bridge dispatch status --json`, `bridge dispatch daemon status --json`, and `bridge dispatch drain --timeout 1 --dry-run --json`; run `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_dispatcher_runtime.py` with only the bounded hook-surface exclusion named above. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Verify staged `harness-state/bridge-substrate.json` contains `dispatcher_daemon`; verify staged `cli.py` excludes broad research-era non-dispatch command surfaces, hygiene supersession imports, skills CLI registration, and backlog-query CLI expansion. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Run `platform_tests/scripts/test_dispatcher_daemon_supervision.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py`, and focused bounded-worker Cursor harness tests in `platform_tests/scripts/test_cursor_harness.py`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | After GO, run `scripts/implementation_authorization.py begin` and validate all mutated release-worktree paths are inside this v033 `target_paths` list. |
| Provider-neutral dashboard directive | Run `scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root <release-worktree>` and `scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki`; verify dashboard deployment data remains application-populated and provider-neutral, with Azure only as optional adopter-owned integration if mentioned at all. |

Focused pytest bundle after GO:

```text
python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/scripts/test_cursor_harness.py "platform_tests/scripts/test_dispatcher_runtime.py" -q --tb=short --no-header -k "not test_codex_hook_commands_do_not_use_foreground_console_launchers"
```

## Acceptance Criteria

- Release branch remains based on `origin/main`.
- `groundtruth_kb.cli` imports successfully from the release worktree without hygiene supersession, skills CLI, or backlog-query imports.
- `git diff --cached -- groundtruth-kb/src/groundtruth_kb/cli.py` contains dispatcher-only CLI changes.
- `harness-state/bridge-substrate.json` is staged with `dispatcher_daemon`.
- `scripts/ops/dispatch_monitor.py` and `scripts/bridge_review_independence.py` are included only as dispatcher-chain dependencies.
- Focused runtime fixtures reflect current topology: Prime Builder `A`; Loyal Opposition `D`, `E`, `F`, `C`, `B`.
- Dispatcher health/status/daemon/drain commands pass from the release worktree.
- Focused dispatcher tests pass with only the explicitly bounded hook-surface exclusion.
- Dashboard release-health refresh and wiki comparison are rerun and reported.
- No broad `research` branch merge, no `.codex/*` changes, no hygiene supersession paths, no skills CLI/backlog query paths, no `scripts/openrouter_harness.py`, no Agent Red path, no local DB/scratch artifacts, and no root dirty WIP are included.

## Risk And Rollback

Primary risk is that adding the two helper scripts exposes another transitive dependency outside the release lane. Mitigation is fail-closed verification: any new out-of-envelope dependency must stop implementation and return through the bridge instead of widening scope silently.

Rollback is release-worktree local: restore newly authorized paths to `origin/main`, preserve the bridge evidence chain, and re-file a narrower blocker report if the helper dependency set proves broader than v032 allowed.

## Recommended Commit Type

`fix(dispatch):` the eventual implementation remains a release-blocking dispatcher substrate defect fix.
