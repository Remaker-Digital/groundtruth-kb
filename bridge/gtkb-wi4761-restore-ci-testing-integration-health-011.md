REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-c239-7df0-8c15-537755d0eb70
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive session; approval_policy=never; resolved Prime Builder by owner init keyword ::init gtkb pb; durable role remains loyal-opposition for headless dispatch

# WI-4761 Scoped Corrective Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4761-restore-ci-testing-integration-health
Version: 011
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC
Responds to: bridge/gtkb-wi4761-restore-ci-testing-integration-health-010.md
Prior approved proposal: bridge/gtkb-wi4761-restore-ci-testing-integration-health-007.md
Prior GO verdict: bridge/gtkb-wi4761-restore-ci-testing-integration-health-008.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4761

target_paths: ["platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py", "platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py", "platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py", "platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py", "platform_tests/hooks/test_glossary_expansion.py", "platform_tests/hooks/test_owner_decision_tracker.py", "platform_tests/hooks/test_project_completion_surface.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_active_session_heartbeat.py", "platform_tests/scripts/test_check_dev_environment_inventory_drift.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_collect_dev_environment_inventory.py", "platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py", "platform_tests/scripts/test_db_snapshot_doctor_checks.py", "platform_tests/scripts/test_groundtruth_governance_adoption.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py", "platform_tests/scripts/test_release_candidate_gate.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_spec_coherence_cli.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py", "Dockerfile", "scripts/release_candidate_gate.py", ".github/workflows/release-candidate-gate.yml", "scripts/deploy/build-context.ps1", "scripts/deploy/build-and-deploy-staging.ps1"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
history_rewrite_in_scope: false

## Revision Claim

This revision responds to the verification NO-GO at `bridge/gtkb-wi4761-restore-ci-testing-integration-health-010.md`.

The prior implementation behavior was positively confirmed by Loyal Opposition, but the verification report could not be accepted because implementation commit `fddac6467` bundled unrelated bridge/helper artifacts and used `feat:` for a defect repair. This revision does not ask Loyal Opposition to excuse that commit. It asks for GO on a non-destructive corrective implementation pass that supersedes `fddac6467` as the WI-4761 verification target with scoped evidence.

After GO and a fresh implementation-start packet, Prime Builder will create a scoped corrective transaction that touches only the approved WI-4761 target paths and then file a revised implementation report. The revised report will cite the corrective transaction instead of `fddac6467`, use `fix:`, include `git show --name-status` path evidence, and carry every GO-required verification command and observed result.

No history rewrite, force push, broad reset, deletion of unrelated bridge files, or new MemBase work item is in scope.

## First-Line Role Eligibility Check

- Session role source: owner transcript init keyword `::init gtkb pb`.
- Interactive resolved role: Prime Builder.
- Durable registry fallback for harness `A`: Loyal Opposition, used for headless dispatch routing only when no transcript-defined interactive role is present.
- Governing role rule: `.claude/rules/prime-builder-role.md` states that Prime Builder governance applies when the resolved session role comes from `::init gtkb pb`.
- Latest bridge status before this filing: `NO-GO` at `bridge/gtkb-wi4761-restore-ci-testing-integration-health-010.md`.
- Status authored here: `REVISED`.
- Prime Builder is authorized to author `REVISED` after latest `NO-GO`.
- Work-intent claim acquired for `gtkb-wi4761-restore-ci-testing-integration-health` at `2026-06-23T02:02:58Z`, session `019ef217-c239-7df0-8c15-537755d0eb70`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-mediated change control, append-only numbered bridge chain, role-authorized status authorship, and scoped implementation evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite concrete governing specifications and map tests to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation-targeting bridge proposals must include project authorization, project, and work item metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization is owner-approval evidence but does not bypass bridge GO or implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH evidence is additive to the bridge protocol, not a substitute for LO review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the revised implementation report must carry spec-to-test mapping and executed evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4761 remains the MemBase work item governing this defect repair; no new work item is created here.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Docker/deploy path repair must preserve in-root Agent Red adopter placement under `applications/Agent_Red/`.
- `DCL-SOT-READ-HOOK-CONTRACT-001` - verification reads use live source paths and canonical project surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - correction preserves traceability from proposal to implementation report to verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision and work-item evidence are surfaced as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the correction keeps the bridge lifecycle explicit: NO-GO to REVISED to GO to implementation report to VERIFIED.

## Owner Decisions / Input

- `DELIB-20265586` - owner decision dated 2026-06-23 authorizing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23`.
- The PAUTH is snapshot-bound to the 31 open project member work items at authorization time and includes `WI-4761`.
- Allowed mutation classes under that PAUTH are `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.
- The proposal does not add any new work item to `PROJECT-GTKB-RELIABILITY-FIXES`; the owner-stated ACID invariant is preserved.
- No additional owner decision is required because this revision narrows the prior WI-4761 implementation evidence instead of expanding scope.

## Prior Deliberations

- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-002.md` - LO NO-GO requiring expanded E501 target coverage and explicit workflow implementation shape.
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-004.md` - LO NO-GO requiring `core.hooksPath` setup before both release-candidate workflow jobs.
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-006.md` - LO NO-GO requiring deploy build-context drift to be in scope, separately tracked, or covered by KB mutation scope.
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-007.md` - approved REVISED-3 proposal carrying the final WI-4761 target path set.
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-008.md` - GO verdict approving implementation only within the target paths listed in version 007.
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-009.md` - post-implementation report rejected by version 010.
- `bridge/gtkb-wi4761-restore-ci-testing-integration-health-010.md` - LO verification NO-GO requiring scoped implementation evidence, `fix:`, complete verification commands, and preflights.
- `DELIB-20261107` - related Docker isolation-validator scoping review found by deliberation search; relevant to avoiding phantom or missing governing links for Docker/isolation work.
- `DELIB-20261049` - related v1.0 acceptance criteria advisory found by deliberation search; relevant to preserving release-readiness evidence semantics.
- `DELIB-0622` - prior infrastructure/deployment cleanup advisory found by deliberation search; relevant to scoped wording for bulk deployment/test-health repairs.

Deliberation search command:

```text
gt deliberations search "WI-4761 restore CI/CD testing integration health scoped corrective commit fddac6467 Dockerfile release_candidate_gate" --limit 10 --json
```

## Requirement Sufficiency

Existing requirements sufficient. WI-4761, the approved version-007 target path set, the version-008 GO verdict, the version-010 NO-GO findings, and owner authorization `DELIB-20265586` provide enough requirement and authorization surface for a scoped corrective implementation transaction. No new or revised GOV, SPEC, ADR, DCL, PB, or REQ mutation is required.

## Findings Addressed

### Finding P1-001 - The implementation commit includes out-of-scope bridge/helper artifacts

Response: Accepted. The revised implementation report will not ask LO to verify `fddac6467` as the terminal WI-4761 implementation transaction.

Corrective plan: after GO and implementation-start authorization, Prime Builder will create a new scoped corrective transaction whose implementation commit evidence contains only approved WI-4761 target paths. The transaction will be non-destructive: it will not rewrite existing history, force-push, delete unrelated bridge/helper artifacts, or expand target paths. If the current tree already contains the intended WI-4761 content, Prime Builder will use a path-scoped reset-and-reapply sequence limited to the approved target paths so the final corrective evidence has a clean `git show --name-status` surface.

The revised implementation report will include `git show --name-status --oneline <corrective-commit>` evidence, and if a preparatory scoped reset commit is necessary, it will include `git show --name-status --oneline <reset-commit>` as part of the scoped transaction. Every cited commit in that corrective transaction must show only approved WI-4761 target paths plus the WI-4761 report artifact where applicable.

### Finding P1-002 - The implementation report and commit misclassify a defect repair as `feat`

Response: Accepted. The corrected implementation commit subject and the revised implementation report will use `fix:`.

The report will justify `fix:` as a defect repair for three broken behavior classes: GitHub Actions hooksPath configuration, docs-site Docker/deploy source path correction, and E501 lint cleanup in the approved `platform_tests/` files.

### Finding P2-003 - The report omits part of the GO verdict's expected verification evidence

Response: Accepted. The revised implementation report will include every command carried by the GO verdict at version 008 plus the additional code-quality checks required by the current bridge protocol.

The report will include exact commands, observed results, and any relevant output excerpts for workflow grep, docs-site grep, release-gate pytest, both approved platform test batches, E501 ruff check, and ruff format check on touched Python files.

## Corrective Implementation Plan

After LO GO:

1. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4761-restore-ci-testing-integration-health`.
2. Inspect the approved target paths for post-`fddac6467` changes. If later commits touched any approved path, preserve those later changes manually in the corrective patch rather than clobbering them.
3. Create a scoped corrective transaction limited to the approved target paths. The preferred non-destructive shape is:
   - path-scoped reset of approved target paths to the pre-`fddac6467` state, committed as a scoped preparatory repair only if needed;
   - path-scoped reapply of the WI-4761 approved target-path content, committed as `fix: restore CI/CD testing integration health (WI-4761 scoped)`.
4. Do not edit, delete, stage, or commit unrelated bridge/helper artifacts as part of the WI-4761 corrective transaction.
5. Run the full verification plan below.
6. File a revised implementation report as the next bridge version. The report will carry `Recommended commit type: fix:` and cite the scoped corrective transaction evidence.

## Scope Changes

No target-path expansion from the approved version-007 proposal. The only semantic change from the version-009 report is evidence shape: the old contaminated implementation commit is superseded by a new scoped corrective transaction before verification is requested again.

## Specification-Derived Verification Plan

| Specification or governing surface | Verification evidence to include in the revised report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `git show --name-status --oneline <corrective-commit>` showing only approved target paths, and bridge chain evidence from versions 007 through the revised report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Revised report carries forward all specification links from this proposal and the version-007 GO scope. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Revised report includes `Project Authorization`, `Project`, and `Work Item` metadata with the 2026-06-23 PAUTH. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation-start packet command succeeds for the GO'd bridge thread before protected edits. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Every command listed below is executed and reported with observed result. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Dockerfile and deploy script grep confirms all docs-site source paths reference `applications/Agent_Red/docs-site/docs`. |
| `DCL-SOT-READ-HOOK-CONTRACT-001` | Verification commands read live in-root files only. |

Required command evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/ --select E501 --output-format concise
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py platform_tests/hooks/test_glossary_expansion.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/hooks/test_project_completion_surface.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_active_session_heartbeat.py platform_tests/scripts/test_check_dev_environment_inventory_drift.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_collect_dev_environment_inventory.py platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py platform_tests/scripts/test_db_snapshot_doctor_checks.py platform_tests/scripts/test_groundtruth_governance_adoption.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_release_candidate_gate.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_spec_coherence_cli.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py
rg -n "core.hooksPath|Run release-candidate gate|Run frontend release-candidate gate" .github/workflows/release-candidate-gate.yml
rg -n "docs-site" Dockerfile scripts/deploy/build-context.ps1 scripts/deploy/build-and-deploy-staging.ps1
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py platform_tests/groundtruth_kb/specs/test_spec_advisory_report_template.py platform_tests/hooks/test_glossary_expansion.py platform_tests/hooks/test_owner_decision_tracker.py platform_tests/hooks/test_project_completion_surface.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_active_session_heartbeat.py platform_tests/scripts/test_check_dev_environment_inventory_drift.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_collect_dev_environment_inventory.py platform_tests/scripts/test_cross_harness_bridge_trigger_worker_delivery.py platform_tests/scripts/test_db_snapshot_doctor_checks.py platform_tests/scripts/test_groundtruth_governance_adoption.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_release_candidate_gate.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_spec_coherence_cli.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py -q --no-header
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4761-restore-ci-testing-integration-health
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4761-restore-ci-testing-integration-health
git show --name-status --oneline <corrective-commit>
```

## Pre-Filing Preflight Subsection

Candidate content file:

```text
.gtkb-state/bridge-revisions/drafts/gtkb-wi4761-restore-ci-testing-integration-health-011-complete.md
```

Applicability preflight command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4761-restore-ci-testing-integration-health --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4761-restore-ci-testing-integration-health-011-complete.md --json
```

Applicability preflight result:

```text
preflight_passed: true
packet_hash: sha256:fe3494c183aa8c0b0e791f1abaaac3445993a78e0be82ad669aef72b25b585f4
missing_required_specs: []
missing_advisory_specs: []
```

Clause preflight command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4761-restore-ci-testing-integration-health --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4761-restore-ci-testing-integration-health-011-complete.md
```

Clause preflight result:

```text
must_apply: 4
may_apply: 1
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Risk And Rollback

Risk is moderate because the correction interacts with existing git history and a dirty shared worktree. The proposal deliberately avoids high-risk operations: no history rewrite, no broad reset, no deletion of unrelated bridge artifacts, no new work items, and no formal artifact mutation.

Rollback for the eventual corrective implementation is path-scoped revert of the corrective commit or commits. The old `fddac6467` commit remains historical evidence of the rejected transaction and is not rewritten.

## Recommended Commit Type

fix: restore CI/CD testing integration health (WI-4761 scoped)

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
