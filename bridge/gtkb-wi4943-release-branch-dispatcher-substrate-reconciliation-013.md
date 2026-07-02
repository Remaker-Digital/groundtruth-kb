REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1c92-bed2-7861-ba2c-f9c9b2db8bd0
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-01
author_model_configuration: Codex desktop; approval_policy=never; cwd=E:\GT-KB

# Revised Proposal - WI-4943 Release-Branch Dispatcher Substrate Reconciliation - Windows Subprocess Dependency Envelope Correction

bridge_kind: prime_proposal
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 013
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC
Status: REVISED


Responds to NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-012.md
Prior implementation blocker report: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-011.md
Prior GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-010.md
Prior revised proposal: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-009.md
Prior NO-GO: bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-008.md

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/windows_subprocess.py", "scripts/bridge_work_intent_registry.py", "scripts/ensure_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/cursor_harness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/bridge/role_state.py", "scripts/ops/harness_storm_watchdog_launcher.py", "scripts/ops/harness_storm_watchdog.ps1", "config/dispatcher/rules.toml", "harness-state/harness-registry.json", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "docs/gtkb-dashboard/grafana/README.md", "groundtruth-kb/docs/wiki/release-health.md", "README.md", "bridge/gtkb-wi4933-*.md", "bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md", "bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md", "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md"]

---

## Revision Claim

This revision responds to the NO-GO at `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-012.md`. The implementation report at `-011.md` correctly failed closed after focused release-worktree testing exposed one additional dispatcher-substrate dependency outside the approved v009/v010 target envelope:

| Newly added target path | Why it is required |
| --- | --- |
| `scripts/windows_subprocess.py` | `scripts/dispatcher_runtime.py` imports `no_window_subprocess_kwargs` and `prefer_pythonw_executable` from this support module. Without it, dispatcher runtime tests fail with `ModuleNotFoundError: No module named 'windows_subprocess'`. |

This REVISED proposal changes only the bridge authorization envelope and release-worktree execution plan. It does not implement release-branch reconciliation, modify `scripts/windows_subprocess.py` in the root checkout, narrow acceptance criteria, alter dispatcher topology, deploy anything, restore retired pollers or hook-triggered automation, rewrite history, or authorize a broad merge from `research`.

The corrected envelope now contains the prior v009 target set plus exactly `scripts/windows_subprocess.py`. If post-GO implementation finds another required path outside this revised envelope, Prime Builder must fail closed with another blocker report rather than expanding scope directly.

## Dependency Audit Before Filing

This dispatch performed a read-only dependency check before filing this revision:

```text
Test-Path E:/GT-KB/scripts/windows_subprocess.py
Test-Path E:/GT-KB/scripts/dispatcher_runtime.py
rg -n "windows_subprocess|WindowStyle|CREATE_NO_WINDOW|hidden" E:/GT-KB/scripts/dispatcher_runtime.py E:/GT-KB/scripts/windows_subprocess.py E:/GT-KB/platform_tests/scripts/test_dispatcher_runtime.py
git status --short --branch
git worktree list --porcelain
```

Observed audit result:

- `scripts/windows_subprocess.py` exists in the root checkout.
- `scripts/dispatcher_runtime.py` exists in the root checkout.
- `scripts/dispatcher_runtime.py` imports `no_window_subprocess_kwargs` and `prefer_pythonw_executable` from `windows_subprocess` at line 149.
- `scripts/windows_subprocess.py` is the support module that centralizes no-window subprocess kwargs and Python executable preference for Windows dispatch paths.
- The root checkout remains dirty on branch `research`, so implementation must not stage or commit from the root checkout.
- The stale `.gtkb-state/release-main-20260630` worktree is no longer listed by `git worktree list --porcelain`; the only release-like worktree currently listed is `archive/worktrees/release-integration-20260701`.
- The post-GO implementation should create or use a fresh in-root worktree/branch from `origin/main` for the WI-4942 dispatcher release-health slice, rather than relying on the stale locked release worktree from the prior blocker report.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher health/status/drain/config commands must agree and expose release-operable dispatcher state from the release branch; the Windows subprocess support module is required for dispatcher runtime behavior under focused tests.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - bridge dispatch must remain daemon-owned, bounded, and operational without restoring retired trigger or poller paths; the added support module preserves headless subprocess behavior for the dispatcher runtime.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher daemon remains the active automation substrate; this revision preserves dispatcher-only architecture and does not reintroduce retired poller or trigger paths.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher persistence must remain headless/no-window safe; `scripts/windows_subprocess.py` exists specifically to support that behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this REVISED proposal is the next numbered Prime Builder response to the latest NO-GO and requires Loyal Opposition GO before implementation can resume.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the revision cites the governing dispatcher, bridge, authorization, and artifact specs that constrain the corrected implementation envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the revision carries Project Authorization, Project, Work Item, and inline JSON `target_paths`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bounded by the active PAUTH, the revised bridge target paths, and implementation-start packet validation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the revision directly corrects the third envelope mismatch found by implementation authorization validation and focused tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must map each linked requirement to executed tests or live release-worktree evidence before verification.
- `GOV-STANDING-BACKLOG-001` - WI-4943 remains the durable backlog authority for this release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the blocker, corrected envelope, and follow-on approval are preserved as bridge artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the release defect remains represented as an artifact graph across DELIB, WI, PAUTH, proposal, report, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - unresolved work remains bounded by the PAUTH expiry and bridge state rather than becoming indefinite deferred work.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization remains the existing `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under `E:\GT-KB`; any fresh release worktree must remain in-root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses explicit helper-mediated bridge filing and preflight checks.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized the scoped WI/PAUTH for release-branch dispatcher substrate reconciliation.
- `DELIB-202665118` - Loyal Opposition GO for v001 under the original target envelope.
- `DELIB-20266138` - owner selected minimum-viable black-box dispatcher activation and autonomous drive of the critical dispatcher path.
- `DELIB-20266667` - GO for WI-4942 drain/report live-worker parity, one of the verified substrate sources to reconcile.
- `DELIB-20266456` - prior release-integration drift repair pattern for applying verified watchdog output-file transport deltas without broad merging.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - terminal VERIFIED supervisor governance evidence.
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-006.md` - terminal VERIFIED drain live-worker parity evidence.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-008.md` - Loyal Opposition NO-GO confirming the prior dependency-envelope mismatch.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-009.md` - Prime Builder revised proposal adding the prior dependency paths.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-010.md` - Loyal Opposition GO for the v009 envelope.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-011.md` - Prime Builder blocker report proving the `scripts/windows_subprocess.py` mismatch.
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-012.md` - Loyal Opposition NO-GO confirming the `scripts/windows_subprocess.py` gap and the stale worktree index-lock risk.

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` records the owner decision to create a narrow governed lane for integrating only verified dispatcher daemon/runtime/supervisor/drain work into the clean release branch.
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE` remains the carried-forward project authorization for WI-4943 and permits source, test, docs, config, and bridge mutation classes until `2026-07-02T00:00:00Z`.
- Owner follow-up in this session directed Prime Builder to force-clear stale claim contention and proceed, then retry, then go ahead after dispatcher/bridge state moved WI-4943 to latest `NO-GO`.
- This revision uses the v012 NO-GO's first remediation path: file a revised bridge proposal adding `scripts/windows_subprocess.py` to the PAUTH envelope. It does not choose the alternate option of refactoring `scripts/dispatcher_runtime.py` to remove the dependency.
- No new owner decision is required before Loyal Opposition reviews this corrected envelope. If Loyal Opposition determines the current PAUTH text is insufficient for the added path or the fresh-worktree execution plan, the correct verdict is NO-GO identifying the exact missing owner authorization.

## Requirement Sufficiency

Existing requirements are sufficient for review of this revised envelope. The cited dispatcher, bridge, project-authorization, and artifact-governance records already cover the corrected support module and acceptance criteria. The implementation must still wait for a fresh Loyal Opposition GO and a new implementation-start packet before mutating any protected source, test, config, harness-state, docs, bridge, or release-worktree target path.

## Revised Scope

The proposed implementation scope from v001, v005, and v009 remains in force with one change: the implementation envelope now includes `scripts/windows_subprocess.py`, identified in the v012 NO-GO. The implementation must:

1. Create or use a fresh clean in-root release worktree/branch from `origin/main` for the WI-4942 dispatcher release-health slice, rather than staging from the dirty root checkout or stale locked `.gtkb-state/release-main-20260630` worktree.
2. Integrate only verified dispatcher daemon/runtime/supervisor/drain/Cursor-route net effects needed for the WI-4942/WI-4943 release-health acceptance criteria.
3. Cherry-pick or manually apply only the verified dependency chain needed to land WI-4942, including the newly authorized `scripts/windows_subprocess.py` support module only because the verified dispatcher runtime imports it.
4. Preserve Prime Builder A/E and Loyal Opposition D/F/C/B topology through governed dispatcher control surfaces.
5. Preserve retired automation retirement: do not restore the retired OS poller, smart poller, hook-triggered automation path, or retired cross-harness trigger as a fallback.
6. Preserve provider-neutral dashboard state: no default Azure warning, no Azure credential or CLI requirement, and mock application deployment data remains acceptable for dashboard release-health surfaces.
7. Run a dependency check before implementation changes: verify every staged dispatcher file's root-relative script/config references either already exist in the fresh release worktree or are listed in this target envelope.
8. Avoid broad staging, broad commits, broad pushes, whole-branch `research` merges, unrelated dirty files, local DB churn, scratch artifacts, stale worktree lock reuse, or history rewrite.

## Specification-Derived Verification Plan

| Specification | Required verification after GO |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | On the clean release branch run `gt bridge dispatch health --json`, `gt bridge dispatch status --json`, `gt bridge dispatch daemon status --json`, and `gt bridge dispatch drain --timeout 1 --dry-run --json`; run `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run dispatcher daemon/runtime tests including `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_dispatcher_runtime.py`; verify bounded terminal classification for daemon-driven LO dispatch or explicit failure evidence. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Search changed files for retired poller/trigger fallback restoration and run dispatcher-only/no-retired-worker-reference tests where present. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Run `platform_tests/scripts/test_dispatcher_daemon_supervision.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py`, and no-window spawn audit coverage where available. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | After GO, run `implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation`; validate `scripts/windows_subprocess.py` as authorized before modifying or adding it in the release worktree. |
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

- Role eligibility check: Codex harness `A` is resolved as `prime-builder` in `harness-state/harness-identities.json`, `harness-state/harness-registry.json`, and `gt bridge status --json`; Prime Builder is authorized to write a `REVISED` response.
- Applicability command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .tmp/bridge-revisions/wi4943-013.content.md --json`
- Applicability result: exit code 0; `preflight_passed=true`; `missing_required_specs=[]`; `missing_advisory_specs=[]`.
- Applicability packet hash: `sha256:11d2f4e3989027819756087b3230e5efe7c59abc04946e740a28c0266449e605`.
- Clause command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .tmp/bridge-revisions/wi4943-013.content.md`
- Clause result: exit code 0; clauses evaluated 5; must_apply 4; evidence gaps in must_apply clauses 0; blocking gaps 0.

## Risk And Rollback

Primary risk is that repeated dependency-envelope corrections become a broad release-branch merge. Mitigation: this revision adds exactly one path, ties it to a concrete import edge, requires a fresh branch/worktree from `origin/main`, and keeps broad `research` merge or broad staging outside scope. A second risk is another hidden dependency layer; mitigation is an explicit post-GO fail-closed requirement if focused tests reveal any additional out-of-envelope path.

Rollback remains a revert of any eventual WI-4943 implementation commit from the clean release branch, plus an append-only bridge follow-up. Do not rewrite history after push; use revert commits if any release branch changes are already published.

## Recommended Commit Type

`fix(dispatch):` the eventual implementation remains a release-blocking dispatcher substrate defect fix.
