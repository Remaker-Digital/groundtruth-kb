REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1c92-bed2-7861-ba2c-f9c9b2db8bd0
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-01
author_model_configuration: Codex desktop; approval_policy=never; cwd=E:\GT-KB

# Revised Proposal - WI-4943 Release-Branch Dispatcher Substrate Reconciliation - CLI Skills Dependency Envelope Correction

bridge_kind: prime_proposal
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 025
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: REVISED

Responds to NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-024.md
Prior implementation blocker report: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-023.md
Prior GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-022.md
Prior revised proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-021.md

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/windows_subprocess.py", "scripts/bridge_work_intent_registry.py", "scripts/ensure_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/cursor_harness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_skills.py", "groundtruth-kb/src/groundtruth_kb/backlog.py", "groundtruth-kb/src/groundtruth_kb/backlog/__init__.py", "groundtruth-kb/src/groundtruth_kb/backlog/approval_state.py", "groundtruth-kb/src/groundtruth_kb/backlog/query.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/bridge/role_state.py", "scripts/ops/harness_storm_watchdog_launcher.py", "scripts/ops/harness_storm_watchdog.ps1", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "docs/gtkb-dashboard/grafana/README.md", "groundtruth-kb/docs/wiki/release-health.md", "README.md", "bridge/gtkb-wi4933-*.md", "bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md", "bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md", "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md"]

---

## Revision Claim

This revision responds to the NO-GO at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-024.md`. The v023 blocker report and v024 review confirm that v021/v022 correctly authorized the four backlog dependency paths, but the approved `groundtruth-kb/src/groundtruth_kb/cli.py` snapshot also imports `groundtruth_kb.cli_skills`.

This REVISED proposal changes only the target-path envelope. It carries forward the exact v021 scope, adds exactly one verified dependency path, `groundtruth-kb/src/groundtruth_kb/cli_skills.py`, and preserves all fail-closed conditions from v021/v022/v024.

No broad `research` merge, in-thread CLI lazy-import refactor, new application path, `scripts/openrouter_harness.py`, Agent Red path, deployment work, credential work, retired poller restoration, or unrelated skills/backlog behavior refactor is authorized. If focused verification reveals any further source path outside this envelope, Prime Builder must fail closed with another blocker report.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped governance correction.

The governing requirements, owner authorization, and work item remain the same as v021:

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` authorizes the narrow WI-4943 release-dispatcher lane.
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE` bounds implementation to this project/work item scope until `2026-07-02T00:00:00Z`.
- WI-4943 remains the durable work item for landing the verified dispatcher dependency chain needed by WI-4942.
- The required source/config/test/doc paths are enumerated in `target_paths`, now including the verified `cli_skills.py` import dependency.

No new or revised requirement is needed before implementation. The correction is mechanical target-envelope sufficiency for the implementation-start gate, not a scope expansion beyond verified dependency closure.

## Dependency Audit Before Filing

The v023 blocker and v024 NO-GO identify the concrete dependency edge:

```text
groundtruth-kb/src/groundtruth_kb/cli.py:53:from groundtruth_kb.cli_skills import skills_group
groundtruth-kb/src/groundtruth_kb/cli.py:220:main.add_command(skills_group)
```

The verified snapshot adds the missing module:

```text
git diff --name-status origin/main..99fbb9db -- groundtruth-kb/src/groundtruth_kb/cli_skills.py groundtruth-kb/src/groundtruth_kb/cli_skills
A       groundtruth-kb/src/groundtruth_kb/cli_skills.py
```

The release-worktree import check failed before this path was authorized:

```text
ModuleNotFoundError: No module named 'groundtruth_kb.cli_skills'
```

## Findings Addressed

### P0: `cli_skills.py` missing from approved envelope

Resolution: v025 adds exactly `groundtruth-kb/src/groundtruth_kb/cli_skills.py` to `target_paths` so Prime Builder can apply the verified CLI dependency after renewed GO and implementation authorization.

### Fail-closed behavior

Resolution: v025 preserves the v024 direction that no `cli_skills.py` mutation is authorized until LO grants GO and `scripts/implementation_authorization.py begin` succeeds against this revised proposal.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher CLI health/status/drain/daemon commands cannot be verified until the approved CLI snapshot imports all required modules.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the daemon/runtime verification bundle depends on importing the release CLI and dispatcher modules from the release worktree.
- `ADR-DISPATCHER-ARCHITECTURE-001` - this revision preserves dispatcher-daemon architecture and does not restore retired pollers/triggers.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows headless/no-window dispatcher behavior remains in scope only through the reviewed dispatcher and subprocess support paths.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this is the next numbered Prime Builder response to latest NO-GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites governing dispatcher, bridge, project-authorization, and artifact specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries Project Authorization, Project, Work Item, and inline JSON `target_paths`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation remains bounded by PAUTH, GO status, implementation-start authorization, and target-path validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation evidence must rerun the focused dispatcher plus dashboard/wiki bundle.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the durable backlog authority for this release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this blocker and envelope correction are preserved as append-only bridge artifacts.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization remains `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses helper-mediated bridge filing and explicit preflight checks.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorization for WI-4943 release-dispatcher lane.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-021.md` - corrected REVISED proposal with Requirement Sufficiency.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-022.md` - GO on v021.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-023.md` - Prime Builder blocker report for missing `cli_skills.py`.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-024.md` - LO NO-GO directing this exact target-envelope correction.

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` remains the owner authorization for this narrow release lane.
- PAUTH remains active until `2026-07-02T00:00:00Z`.
- No new owner decision is required for LO to review this corrected proposal. The proposal-level sufficiency phrase states that existing requirements are enough for this scoped governance correction.

## Revised Scope

The v021 implementation scope remains in force with one change: implementation may add/apply `groundtruth-kb/src/groundtruth_kb/cli_skills.py` only as verified dependency closure for the already approved `cli.py` snapshot. Implementation must:

1. Continue from the fresh in-root worktree `E:\GT-KB\.gtkb-state\release-worktrees\wi4943-dispatcher-release-20260701` on branch `codex/wi4943-dispatcher-release-main-20260701`.
2. Apply only verified dependency-chain paths needed to land WI-4942 dispatcher release health.
3. Add `cli_skills.py` only as dependency closure for the already approved `cli.py` snapshot.
4. Re-run dispatcher CLI smoke checks, focused dispatcher tests, and dashboard/wiki verification after renewed GO.
5. Avoid broad `research` merge, unrelated staged files, unapproved backlog/skills behavior refactors, local DB churn, Agent Red paths, deployment changes, or history rewrite.

## Specification-Derived Verification Plan

| Specification | Required verification after GO |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run release-worktree dispatcher CLI smoke checks: `bridge dispatch health --json`, `bridge dispatch status --json`, `bridge dispatch daemon status --json`, and `bridge dispatch drain --timeout 1 --dry-run --json`; run `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_dispatcher_runtime.py`; classify any remaining `psutil` failure separately. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Verify the staged diff still excludes retired poller/trigger fallback restoration and broad `research` merge residue. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Run `platform_tests/scripts/test_dispatcher_daemon_supervision.py` and `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | After GO, run `implementation_authorization.py begin` and validate `cli_skills.py` before applying it. |
| Provider-neutral dashboard directive | Run `scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root <release-worktree>` and `scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki`; verify Azure remains optional/adopter-owned only. |

## Acceptance Criteria

- Clean release branch remains based on `origin/main`.
- Release branch includes only verified WI-4933/WI-4937/WI-4942/WI-4943 dependency-chain paths approved by bridge target envelope.
- `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation` succeeds after renewed GO.
- `groundtruth_kb.cli` imports successfully from the release worktree.
- Dispatcher health/status/daemon/drain commands run from the release worktree.
- Focused dispatcher tests pass or produce a clearly separated environment-only blocker.
- Dashboard release-health refresh and wiki comparison are rerun and reported.
- No broad `research` branch merge, no `scripts/openrouter_harness.py`, no Agent Red path, no unrelated root dirty files, and no local DB/scratch artifacts are included.

## Pre-Filing Preflight Subsection

- Role eligibility check: Codex harness `A` is resolved as `prime-builder`; per-session marker `role-019f1c92-bed2-7861-ba2c-f9c9b2db8bd0.json` resolves to `prime-builder`.
- Applicability command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-025.content.md --json`
- Applicability expectation: exit code 0; `preflight_passed=true`; `missing_required_specs=[]`; `missing_advisory_specs=[]`.
- Clause command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-025.content.md`
- Clause expectation: exit code 0; evidence gaps in must_apply clauses 0; blocking gaps 0.

## Risk And Rollback

Primary risk is continued dependency discovery after `cli_skills.py` is authorized. Mitigation remains fail-closed behavior and exact target-path expansion only for verified dependency closure. Rollback is a revert of any eventual release-branch implementation commit plus append-only bridge follow-up. The staged release worktree must remain uncommitted until renewed GO, successful verification, post-implementation report, and LO verification.

## Recommended Commit Type

`fix(dispatch):` the eventual implementation remains a release-blocking dispatcher substrate defect fix.
