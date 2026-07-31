NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder session; governed bridge-propose helper

# Defect-Fix Proposal - Release-branch dispatcher substrate reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation
Version: 001
Date: 2026-07-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4943

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/ensure_dispatcher_daemon.py", "scripts/install_dispatcher_daemon_task.ps1", "scripts/cursor_harness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_cursor_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "docs/gtkb-dashboard/grafana/README.md", "groundtruth-kb/docs/wiki/release-health.md", "README.md", "bridge/gtkb-wi4933-*.md", "bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md", "bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md", "bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md"]

Defect-fix proposal focused on release-branch integration of already VERIFIED dispatcher substrate work. This proposal authorizes no implementation until Loyal Opposition returns GO and Prime Builder obtains the implementation-start packet.

## Claim

The live `research` checkout now has a PASSing dispatcher daemon and the requested topology, but the clean release branch `codex/dispatcher-release-chain-main-20260701` is not release-healthy. It is clean and pushed at `174e8c5f153c900419766470da8c0771b3227a6d`, but `gt bridge dispatch health --json` fails there because no Loyal Opposition harness is selected, and `gt bridge dispatch daemon status --json` crashes because `scripts/gtkb_dispatcher_daemon.py` is missing.

Prime Builder proposes a narrow release-branch reconciliation: integrate only the VERIFIED dispatcher daemon/runtime/supervisor/drain/Cursor-route work needed for release health, plus the exact tests and docs needed to prove and describe it. This proposal forbids broad `research` merges, dirty worktree sweeps, credential lifecycle work, production deployment, retired poller restoration, hook-driven automation restoration, history rewrite, and default Azure/provider binding.

## Defect / Reproduction

Observed current evidence:

- Root checkout `E:\GT-KB` is on `research` at `20ed3dc21a5dc044f2a43e129273a8ced7827471`.
- Root `gt bridge dispatch health --json` returns `PASS` with Prime Builder A/Codex and E/Cursor, and Loyal Opposition D/Ollama, F/OpenRouter, C/Antigravity, B/Claude.
- Root `gt bridge dispatch daemon status --json` returns `running=true`, `active_substrate=dispatcher_daemon`, fresh heartbeat, and `pid_provenance_verified=true`.
- Clean release worktree `E:\GT-KB\.gtkb-state\release-main-20260630` is on pushed branch `codex/dispatcher-release-chain-main-20260701` at `174e8c5f153c900419766470da8c0771b3227a6d`.
- In the clean release worktree, `gt bridge dispatch health --json` returns `FAIL` with `no active dispatchable harness is eligible for role 'loyal-opposition'`.
- In the clean release worktree, `gt bridge dispatch daemon status --json` raises `FileNotFoundError` for missing `scripts\gtkb_dispatcher_daemon.py`.
- In the clean release worktree, `Test-Path` returns `False` for `scripts\gtkb_dispatcher_daemon.py`, `scripts\ensure_dispatcher_daemon.py`, `scripts\install_dispatcher_daemon_task.ps1`, and `groundtruth-kb\src\groundtruth_kb\dispatcher_supervisor.py`.
- WI-4933, WI-4937, and WI-4942 are all bridge-VERIFIED and MemBase-retired/resolved, so this proposal does not reopen their implementation work. It integrates their verified release-relevant output into the clean release branch.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirements already require dispatcher control surfaces to expose reliable health/drain/status evidence, centralized daemon-owned dispatch to be bounded and headless, project authorization to be scoped, and bridge proposals to cite target paths, work item, project, and PAUTH. No new or revised specification is needed before this release-integration slice.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. The implementation worktree is a linked worktree under `E:\GT-KB\.gtkb-state\release-main-20260630`, which remains inside the mandatory project root. No live GT-KB artifact is read from or written outside `E:\GT-KB`.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher health/status/drain/config commands must agree and expose release-operable dispatcher state from the release branch.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - bridge dispatch must be daemon-owned, bounded, and operational without restoring retired trigger or poller paths.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon is the active automation substrate; release integration must preserve the dispatcher-only architecture.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher persistence must be headless/no-window safe.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires this NEW proposal, LO GO, implementation-start authorization, post-implementation report, and LO verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specs and maps them to tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes Project Authorization, Project, Work Item, and `target_paths`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the new PAUTH bounds allowed mutation classes, target work item, expiry, and forbidden operations.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay inside the PAUTH envelope and fail closed on scope drift.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map each linked requirement to executed tests or live command evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4943 is now the durable backlog authority for this release-integration defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, project, PAUTH, WI, bridge proposal, and final report preserve the release decision trail.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the release defect is being advanced through durable artifacts rather than scratch state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal has an explicit expiry and terminal bridge path so it cannot decay as an indefinite deferral.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization is captured as `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - unqualified GT-KB release evidence remains in the GT-KB root and does not resolve to Agent Red or another adopter repository.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex uses the helper-mediated bridge writer and explicit checks where hook parity is not sufficient.

## Prior Deliberations

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized a new scoped WI/PAUTH for this release-branch dispatcher substrate reconciliation.
- `DELIB-20266138` - owner selected minimum-viable black-box dispatcher activation as a bounded autonomous drive.
- `DELIB-20266667` - GO for WI-4942 drain/report live-worker parity.
- `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-004.md` - terminal VERIFIED evidence for Cursor route repair.
- `bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-004.md` - terminal VERIFIED evidence for bounded worker/failure classification.
- `bridge/gtkb-wi4933-post-verdict-exit-reconciliation-004.md` - terminal VERIFIED evidence for post-verdict exit reconciliation.
- `bridge/gtkb-wi4933-dispatcher-terminal-health-and-failover-004.md` - terminal VERIFIED evidence for dispatcher terminal health/failover.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - terminal VERIFIED evidence for headless Windows supervisor governance.
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-006.md` - terminal VERIFIED evidence for drain/live-worker parity.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/release-health-remaining-fixes-proposal-20260701.md` - current non-canonical implementation proposal/report describing remaining release-health fixes, provider-neutral dashboard scope, dirty-file classification, and expiry.

## Owner Decisions / Input

- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` records the owner decision: "Authorize new scoped WI/PAUTH."
- `PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4943-DISPATCHER-SUBSTRATE` is active, expires `2026-07-02T00:00:00Z`, includes WI-4943, and permits only source, test, docs, config, and bridge mutation classes.
- Forbidden operations in the PAUTH: broad research merge, credential lifecycle, production deployment, retired poller restoration, hook-driven automation restoration, history rewrite, and default provider/Azure binding.
- Owner topology directive applied: Prime Builder A/E; Loyal Opposition D/F/C/B.
- Owner deployment-boundary directive applied: GT-KB dashboard surfaces remain provider-neutral and application-populated; Azure reconciliation remains opt-in adopter/application scope, not a GT-KB release-health dependency.
- Owner deferral directive applied: any deferred release-integration work expires by `2026-07-02T00:00:00Z` or must be explicitly renewed/re-raised.

## Proposed Scope

1. Work from the clean release branch/worktree, not the dirty root checkout.
2. Integrate only verified dispatcher substrate commits or manually reconcile their verified net effect when cherry-pick conflicts make direct replay unsafe.
3. Preserve or establish release-branch dispatcher topology through governed dispatcher config surfaces: Prime Builder A/E and Loyal Opposition D/F/C/B.
4. Restore daemon/runtime/supervisor files needed for `gt bridge dispatch daemon status --json` and supervisor health to work from the release branch.
5. Preserve headless Windows operation: `pythonw.exe`, hidden scheduled task/service-style supervision, or equivalent no-window process creation. Visible PowerShell/terminal windows are diagnostic only.
6. Preserve retired automation retirement: do not restore the retired OS poller, smart poller, hook-triggered automation path, or retired cross-harness trigger as a fallback.
7. Preserve provider-neutral dashboard state: no default Azure warning, no Azure credential/CLI requirement, and mock application deployment data for containers/topology/security/throughput/latency/defects/infrastructure surfaces.
8. Keep release hygiene reductive: do not broad-stage, broad-commit, broad-push, merge `research` wholesale, or include unrelated dirty files from the shared root worktree.

## Specification-Derived Verification Plan

| Specification | Required verification |
|---|---|
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | On the clean release branch run `gt bridge dispatch health --json`, `gt bridge dispatch status --json`, `gt bridge dispatch daemon status --json`, and `gt bridge dispatch drain --timeout 1 --dry-run --json`; run focused dispatcher control tests including `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run daemon/runtime tests including `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_dispatcher_runtime.py`; verify a daemon-driven LO path is bounded and terminally classified. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Search changed files/tests for retired trigger/poller restoration and run dispatcher-only/no-retired-worker-reference tests where present. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Run `platform_tests/scripts/test_dispatcher_daemon_supervision.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py`, and Windows no-window/headless spawn audit tests where available. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation` after GO, validate target paths, and run protected commit authorization before committing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must carry this table forward with exact commands, observed results, and any untested spec waiver explicitly owner-approved. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all changed paths remain under `E:\GT-KB` and no release evidence resolves to Agent Red or an external repo except published GitHub README/wiki checks. |
| `GOV-STANDING-BACKLOG-001` | Read back `gt backlog show WI-4943 --json` and project/PAUTH records before implementation report. |
| Provider-neutral dashboard directive | Run dashboard/wiki tests and compare published/local wiki/README; inspect dashboard docs for no default Azure dependency and mock deployment-data coverage. |

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

## Pre-Filing Preflight

- Applicability command: `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state\bridge-propose-drafts\gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-001.md --json`
- Applicability result: `preflight_passed=true`; `missing_required_specs=[]`; `missing_advisory_specs=[]`.
- Applicability packet hash: `sha256:7b7655498ab0a891df7a046b7cbdb66421f96e1de00c621d384c916216103d70`.
- Clause command: `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation --content-file .gtkb-state\bridge-propose-drafts\gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-001.md`
- Clause result: exit code 0; clauses evaluated 5; must_apply 4; evidence gaps in must_apply clauses 0; blocking gaps 0.

## Risks / Rollback

- Risk: cherry-picking verified commits into the release branch conflicts because prerequisite dispatcher substrate history differs from `main`. Mitigation: reconcile the verified net effect under this GO rather than broad-merging `research`.
- Risk: adding topology/config directly could bypass dispatcher-control governance. Mitigation: use `gt bridge dispatch config ...` governed transactions where available; otherwise document any manual config merge and test it under PAUTH scope.
- Risk: process termination could overreach. Mitigation: retain provenance checks for PID create time, dry-run-first drain behavior, and bounded termination classification.
- Risk: docs accidentally imply Azure dependency. Mitigation: dashboard/docs checks must confirm provider-neutral mock deployment data and no default Azure WARN.
- Rollback: revert the WI-4943 integration commit(s) from the clean release branch and return to current `main` dashboard/wiki-only release state at `4c9da4914`. Do not rewrite history after push; use revert commits if published.

## Files Expected To Change

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/dispatcher_runtime.py`
- `scripts/ensure_dispatcher_daemon.py`
- `scripts/install_dispatcher_daemon_task.ps1`
- `scripts/cursor_harness.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_cursor_harness.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py`
- `groundtruth-kb/docs/method/12-file-bridge-automation.md`
- `docs/gtkb-dashboard/grafana/README.md`
- `groundtruth-kb/docs/wiki/release-health.md`
- `README.md`
- `bridge/gtkb-wi4933-*.md`
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-*.md`
- `bridge/gtkb-wi4942-dispatch-drain-live-worker-parity-*.md`
- `bridge/gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation-*.md`

## Recommended Commit Type

`fix(dispatch):`
