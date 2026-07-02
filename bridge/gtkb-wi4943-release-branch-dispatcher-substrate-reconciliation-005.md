REVISED

# Revised Proposal - WI-4943 Release-Branch Dispatcher Substrate Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 005
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-01T09-45-54Z-prime-builder-A-b2d481
author_model: GPT-5 Codex
author_model_version: 2026-07-01 runtime
author_model_configuration: Codex auto-dispatch worker; approval_policy=never; cwd=E:\GT-KB

Responds to NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-004.md
Prior implementation blocker report: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-003.md
Approved proposal superseded for target-path envelope only: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-001.md
Prior GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/ensure_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/cursor_harness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/bridge/role_state.py", "scripts/ops/harness_storm_watchdog_launcher.py", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "docs/gtkb-dashboard/grafana/README.md", "groundtruth-kb/docs/wiki/release-health.md", "README.md", "bridge/gtkb-wi4933-*.md", "bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md", "bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md", "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md"]

---

## Revision Claim

This revision addresses the sole blocker in `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-004.md`: the approved proposal's target-path envelope was too narrow for the release-branch dispatcher substrate reconciliation acceptance criteria.

The implementation report at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-003.md` failed closed before changing unapproved paths. Loyal Opposition confirmed the blocker and identified four required paths that were outside the approved envelope:

| Newly added target path | Why it is required |
| --- | --- |
| `config/dispatcher/rules.toml` | Carries the release-branch dispatcher rule/topology configuration needed for Prime Builder A/E and Loyal Opposition D/F/C/B candidate selection. |
| `harness-state/harness-registry.json` | Carries the release-branch role projection used by dispatcher selection and release-health evidence. |
| `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` | Required by the reconciled dispatcher runtime/control surface on the release branch. |
| `scripts/ops/harness_storm_watchdog_launcher.py` | Required by the reconciled dispatcher supervisor/watchdog tests and release branch headless-supervision path. |

This REVISED proposal changes only the bridge authorization envelope. It does not implement release-branch reconciliation, modify the four added paths, narrow acceptance criteria, amend credentials, deploy anything, restore retired pollers or hook-driven automation, rewrite history, or bind GT-KB release health to Azure or any other deployment provider.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher health/status/drain/config commands must agree and expose release-operable dispatcher state from the release branch; the added config and registry paths are required to prove selected topology through the governed control surface.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - bridge dispatch must remain daemon-owned, bounded, and operational without restoring retired trigger or poller paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon remains the active automation substrate; the revised target envelope still preserves dispatcher-only architecture.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher persistence must remain headless/no-window safe; the added watchdog launcher path is included only to reconcile the tested headless supervisor path.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this REVISED proposal is the next numbered Prime Builder bridge response to the latest NO-GO and requires Loyal Opposition GO before implementation can resume.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the revision cites the governing dispatcher, bridge, authorization, and artifact specs that constrain the corrected implementation envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the revision carries Project Authorization, Project, Work Item, and inline JSON `target_paths`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bounded by the active PAUTH, the revised bridge target paths, and implementation-start packet validation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the revision directly corrects the envelope mismatch found by implementation authorization validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must map each linked requirement to executed tests or live release-worktree evidence before verification.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the durable backlog authority for this release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the blocker, corrected envelope, and follow-on approval are preserved as bridge artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the release defect remains represented as an artifact graph across DELIB, WI, PAUTH, proposal, report, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - unresolved work remains bounded by the PAUTH expiry and bridge state rather than becoming indefinite deferred work.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization remains the existing `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under `E:\GT-KB`; the release worktree remains in-root under `.gtkb-state\release-main-20260630`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses explicit helper-mediated bridge filing and preflight checks.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized the scoped WI/PAUTH for release-branch dispatcher substrate reconciliation.
- `DELIB-202665118` - Loyal Opposition GO for v001 under the original target envelope.
- `DELIB-20266138` - owner selected minimum-viable black-box dispatcher activation and autonomous drive of the critical dispatcher path.
- `DELIB-20266667` - GO for WI-4942 drain/report live-worker parity, one of the verified substrate sources to reconcile.
- `DELIB-20266456` - prior release-integration drift repair pattern for applying verified watchdog output-file transport deltas without broad merging.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - terminal VERIFIED supervisor governance evidence.
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md` - prior drain/live-worker parity bridge evidence.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-003.md` - Prime Builder blocker report proving the target-path mismatch.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-004.md` - Loyal Opposition NO-GO confirming the mismatch and naming the four missing paths.

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` records the owner decision to create a narrow governed lane for integrating only verified dispatcher daemon/runtime/supervisor/drain work into the clean release branch.
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE` remains active for WI-4943 and permits source, test, docs, config, and bridge mutation classes.
- This revision uses the NO-GO's first remediation path: file a revised bridge proposal with the four missing topology/support paths. It does not choose the alternate options of narrowing acceptance criteria or asking for a PAUTH amendment.
- No new owner decision is required before Loyal Opposition reviews this corrected envelope. If Loyal Opposition determines the current PAUTH text is insufficient for the four added paths, the correct verdict is NO-GO identifying the exact missing owner authorization.

## Requirement Sufficiency

Existing requirements are sufficient for review of this revised envelope. The cited dispatcher, bridge, project-authorization, and artifact-governance records already cover the corrected target paths and acceptance criteria. The implementation must still wait for a fresh Loyal Opposition GO and a new implementation-start packet before mutating any protected source, test, config, harness-state, docs, or bridge target path.

## Revised Scope

The proposed implementation scope from v001 remains in force with one change: the implementation envelope now includes the four paths identified in the v004 NO-GO. The implementation must:

1. Work from the clean release branch/worktree under `E:\GT-KB\.gtkb-state\release-main-20260630`, not from unrelated dirty root WIP.
2. Integrate only verified dispatcher daemon/runtime/supervisor/drain/Cursor-route net effects needed for the WI-4943 release-health acceptance criteria.
3. Preserve Prime Builder A/E and Loyal Opposition D/F/C/B topology through governed dispatcher control surfaces.
4. Include `config/dispatcher/rules.toml` and `harness-state/harness-registry.json` only to reconcile release-branch dispatcher topology/role selection; do not use them for broad role redesign.
5. Include `groundtruth-kb/src/groundtruth_kb/bridge/role_state.py` only as required support for the reconciled dispatcher runtime/control path.
6. Include `scripts/ops/harness_storm_watchdog_launcher.py` only as required support for the tested headless supervisor/watchdog path.
7. Preserve retired automation retirement: do not restore the retired OS poller, smart poller, hook-triggered automation path, or retired cross-harness trigger as a fallback.
8. Preserve provider-neutral dashboard state: no default Azure warning, no Azure credential or CLI requirement, and mock application deployment data remains acceptable for dashboard release-health surfaces.
9. Avoid broad staging, broad commits, broad pushes, whole-branch `research` merges, unrelated dirty files, local DB churn, scratch artifacts, or history rewrite.

## Specification-Derived Verification Plan

| Specification | Required verification after GO |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | On the clean release branch run `gt bridge dispatch health --json`, `gt bridge dispatch status --json`, `gt bridge dispatch daemon status --json`, and `gt bridge dispatch drain --timeout 1 --dry-run --json`; run `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run dispatcher daemon/runtime tests including `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_dispatcher_runtime.py`; verify bounded terminal classification for daemon-driven LO dispatch or explicit failure evidence. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Search changed files for retired poller/trigger fallback restoration and run dispatcher-only/no-retired-worker-reference tests where present. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Run `platform_tests/scripts/test_dispatcher_daemon_supervision.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py`, and headless/no-window spawn audit coverage where available. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | After GO, run `implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation`; validate the four added paths as authorized before modifying them. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must carry this table forward with exact commands, observed results, and any untested spec waiver explicitly owner-approved. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all changed paths remain under `E:\GT-KB` and release evidence does not resolve to Agent Red or an external repo except explicit published README/wiki comparison checks. |
| `GOV-STANDING-BACKLOG-001` | Read back `gt backlog show WI-4943 --json` and the PAUTH record before the implementation report. |
| Provider-neutral dashboard directive | Run dashboard/wiki checks and inspect local/published docs for no default Azure dependency and no provider-specific release-health requirement. |

## Acceptance Criteria

- Clean release branch `gt bridge dispatch health --json` returns `PASS`.
- Clean release branch `gt bridge dispatch daemon status --json` succeeds and reports daemon/supervisor state without missing-file exceptions.
- Dispatcher topology on the release branch selects Prime Builder A/E and Loyal Opposition D/F/C/B through governed dispatcher config surfaces.
- At least one daemon-driven Loyal Opposition dispatch path is bounded and either produces a verdict or a terminal failure classification without orphaned process trees.
- Headless Windows supervisor operation is the release path; visible standalone shells are not documented as the persistence boundary.
- README/wiki compare remains clean after any docs changes, and published README/wiki state matches local main after merge.
- Dashboard release-health/default docs have no Azure dependency; Azure reconciliation remains explicitly opt-in and application-owned.
- No unrelated dirty root WIP/scratch, local DB/test fixture churn, draft verdicts, or broad bridge chains are included.
- Any deferred residue has an expiry or state trigger. For this lane, unresolved deferral expires `2026-07-02T00:00:00Z`.

## Pre-Filing Preflight Subsection

- Applicability command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-005.md --json`
- Applicability result: `preflight_passed=true`; `missing_required_specs=[]`; `missing_advisory_specs=[]`.
- Applicability packet hash: `sha256:2fc19a126e9be27ee9417c08454ed705c1b4897decee10b6e95e050ef5d9782e`.
- Clause command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-005.md`
- Clause result: exit code 0; clauses evaluated 5; must_apply 4; evidence gaps in must_apply clauses 0; blocking gaps 0.

## Risk And Rollback

Primary risk is that the corrected envelope becomes a broad release-branch merge. Mitigation: Loyal Opposition should review the four added paths as narrow support for the already stated acceptance criteria, not as permission to sweep `research` into release. Rollback remains a revert of any eventual WI-4943 implementation commit(s) from the clean release branch, plus an append-only bridge follow-up. Do not rewrite history after push; use revert commits if any release branch changes are already published.

## Recommended Commit Type

`fix(dispatch):` the eventual implementation remains a release-blocking dispatcher substrate defect fix.
