NEW

# Defect-Fix Proposal - GT-KB Mass Release Candidate Blocker Repair

bridge_kind: prime_proposal
Document: gtkb-mass-release-candidate-blocker-repair
Version: 001
Date: 2026-06-27 UTC
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-formal-release-2026-06-27
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop; reasoning=medium; release-blocker repair

Project Authorization: PAUTH-PROJECT-GTKB-MASS-001-MASS-001-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MASS-001
Work Item: GTKB-MASS-001

target_paths: ["platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_fab09_safety_gate_registration.py", "platform_tests/scripts/test_governing_specs_preserved.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_single_harness_dispatcher_task_installer.py", "platform_tests/scripts/test_ops_activity_context.py", "platform_tests/scripts/test_spec_coherence_cli.py", "platform_tests/skills/test_auto_retire_actuation_helper_parity.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py", "applications/Agent_Red/tests/integrations/test_shopify_compliance.py", "applications/Agent_Red/docs/owner-messages-all.json", ".github/workflows/secrets-scan.yml", "README.md", "groundtruth-kb/docs/start-here.md", "groundtruth-kb/docs/day-in-the-life.md", "groundtruth-kb/docs/evidence.md", "groundtruth-kb/docs/troubleshooting/auth.md", "docs/gtkb-systems-and-tools.md"]

Defect-fix proposal focused on current release-candidate blockers observed on the clean `codex/formal-release-main-20260627` branch. This proposal does not authorize unrelated daemon, dispatcher, storm-watchdog, auto-finalizer, or dirty-`develop` work.

## Claim

Repair only the current release-candidate blockers that prevent a solid main cut from the clean release branch:

1. Release-candidate lint failures in platform test files.
2. Agent Red integration tests that fail because they assume every FastAPI app route exposes `.path`.
3. The duplicate legacy secrets workflow that runs `scripts/scan_secrets.py` and reports high findings, while the canonical redacted GT-KB scanner workflow already exists.
4. A tracked noncanonical owner-message dump under `applications/Agent_Red/docs/` that should not ship in a release branch.
5. Public README and in-repo documentation drift that would describe the release branch with obsolete poller or branch-status claims.

## Defect / Reproduction

All findings were reproduced against the clean release worktree at `E:\GT-KB\.tmp\formal-release-main-20260627`.

1. `groundtruth-kb\.venv\Scripts\python.exe -m ruff check applications\Agent_Red\src platform_tests --select E,F` exits nonzero with 14 E/F findings. The blockers are E741 ambiguous `l` loop variables in six platform test files and E501 line-length findings in four platform test/docstring literals.
2. `groundtruth-kb\.venv\Scripts\python.exe -m pytest applications\Agent_Red\tests\integrations\test_shopify_compliance.py::TestKBCRUDViaAPI::test_knowledge_api_has_crud_endpoints applications\Agent_Red\tests\integrations\test_shopify_compliance.py::TestTeamListViaAPI::test_team_api_has_list_endpoint applications\Agent_Red\tests\integrations\test_shopify_compliance.py::TestGDPRExportViaAPI::test_gdpr_export_endpoint_exists -q --tb=short` exits nonzero. Each failure is `_IncludedRouter object has no attribute path`, caused by list comprehensions over `app.routes` that do not filter for path-bearing route objects.
3. `groundtruth-kb\.venv\Scripts\python.exe scripts\scan_secrets.py` exits nonzero and reports high-severity findings. The output includes redacted high findings in `applications/Agent_Red/docs/owner-messages-all.json`; the proposal must not expose raw values. The same branch already has `.github/workflows/gtkb-secrets-scan.yml`, which runs `python -m groundtruth_kb secrets scan --tracked --redacted --report-json .quality/gtkb-secrets.json --fail-on verified-provider`.
4. `applications/Agent_Red/docs/owner-messages-all.json` is a tracked 6.4 MB owner-message dump. It is noncanonical release clutter and contradicts the hygiene direction to remove stray non-authoritative artifacts instead of documenting that they are unreliable.
5. GitHub-published README/wiki/docs comparison found README badges still tied to `develop`, wiki Home still using older toolkit framing, wiki Azure link pointing to a path missing `groundtruth-kb/`, and in-repo docs still referring to retired poller surfaces. The in-repo docs in `target_paths` are the release-branch source changes; the external GitHub wiki update will be performed after the code release branch is green and pushed.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. The implementation branch lives under `E:\GT-KB\.tmp\formal-release-main-20260627`, which is a linked git worktree of the same project root. No live GT-KB artifact is read from or written outside the mandated root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected test, workflow, and documentation changes require bridge review before implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - release blockers, documentation drift, and hygiene decisions must be preserved as durable artifacts rather than scattered scratch notes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing rules and maps the proposed tests to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute the reproduced lint/test/secrets/doc checks.
- `SPEC-AUQ-POLICY-ENGINE-001` - the implementation proceeds under existing owner AUQ-backed PAUTH `PAUTH-PROJECT-GTKB-MASS-001-MASS-001-BOUNDED-IMPLEMENTATION-2026-06-23`; no fresh owner approval is invented here.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red remains the in-root reference adopter under `applications/Agent_Red/`; release evidence must not silently switch to an external application repo.
- `GOV-STANDING-BACKLOG-001` - `GTKB-MASS-001` is the MemBase work item for the mass-adoption/release readiness program.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed helper paths and explicit authorization rather than relying on unobserved hook parity for protected writes.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - release-readiness and documentation state become durable artifacts, not chat-only conclusions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - observed release blockers and noncanonical artifacts trigger remediation or explicit deferral.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - formal release work must include governed release-readiness evidence and no false green claims.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - Agent Red is explicitly in scope as the reference adopter validation surface for this GT-KB release.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - README/wiki/dashboard health claims must be checked against live branch, workflow, and test state.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - health and docs updates must not rely on stale generated startup summaries as authority.

## Prior Deliberations

- `DELIB-2234` - v1 release strategy establishes quality-driven pacing, Agent Red green-on-clean as the release gate, and release-readiness evidence as gating rather than advisory.
- `DELIB-20265586` - owner AUQ authorized snapshot-bound implementation for `PROJECT-GTKB-MASS-001`, including current open member WI `GTKB-MASS-001`.
- `DELIB-20260674` - confirms v1 release strategy scoping-only authorization; useful contrast because this proposal uses the separate active MASS PAUTH, not the scoping-only v1 PAUTH.
- `bridge/gtkb-mass-adoption-readiness-scoping-003.md` and `bridge/gtkb-mass-adoption-readiness-scoping-006.md` - prior mass-adoption thread deferred implementation until isolation completion or explicit owner reprioritization; current `GTKB-MASS-001` PAUTH and owner top-priority release direction make this release-blocker slice timely, but only within the existing PAUTH and bridge GO.
- `DELIB-20266171` - main is the production mirror target; release merge work must not push or merge red branch state.

## Owner Decisions / Input

- `DELIB-20265586` records the owner AUQ that authorized `PROJECT-GTKB-MASS-001` with snapshot-bound included work item `GTKB-MASS-001`.
- Active PAUTH: `PAUTH-PROJECT-GTKB-MASS-001-MASS-001-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Current owner session directive, 2026-06-27: make the formal release the top priority, separate release-ready verified work from WIP/scratch, and release as soon as reasonably possible. This directive is used as work-selection context only; implementation authority remains the existing AUQ-backed PAUTH plus the required Loyal Opposition GO.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped release-blocker repair. `GTKB-MASS-001`, `DELIB-2234`, `DELIB-20265586`, the active MASS PAUTH, and the reproduced release-candidate failures define the allowed work. New requirements would be required only if implementation expands into dashboard health architecture, daemon PID-reuse repair, storm-watchdog repair, auto-finalizer metadata compatibility repair, external production deployment, or force-push/history rewrite.

## Proposed Scope

### IP-1: Lint-only platform test cleanup

Rename ambiguous local loop variables and wrap long literals in the listed platform test files. This is test-source hygiene only; no behavioral production source changes.

### IP-2: Agent Red route-introspection test repair

Update the three failing route-list comprehensions in `applications/Agent_Red/tests/integrations/test_shopify_compliance.py` so they inspect only route objects with a `path` attribute. Preserve the existing endpoint assertions.

### IP-3: Secrets workflow and tracked dump cleanup

Remove the duplicate legacy `secrets-scan.yml` workflow or change it to delegate to the canonical redacted `groundtruth_kb secrets scan` behavior already represented in `gtkb-secrets-scan.yml`. Remove `applications/Agent_Red/docs/owner-messages-all.json` from the release branch unless implementation evidence proves it is a canonical release artifact, which current evidence does not support.

### IP-4: README and in-repo release documentation alignment

Update README and target-path docs so they describe the release branch as an Internal Developer Platform with MemBase, Deliberation Archive, dispatcher/TAFE bridge state, and the cross-harness event-driven trigger. Remove or replace obsolete smart-poller/OS-poller wording in the target docs. Do not add blanket "this may be stale" disclaimers where removing obsolete content is possible.

### Explicit Exclusions

- No edits to dirty `develop` WIP outside this proposal's target paths.
- No WI-4893 daemon PID-reuse implementation.
- No WI-4894 storm-watchdog decider implementation.
- No WI-4889 auto-finalization metadata compatibility implementation.
- No production deploy.
- No force push or destructive history rewrite.
- No release tag until the release branch is green and owner/governance release conditions are satisfied.
- No external GitHub wiki push until the code/docs branch being described is verified and pushed.

## Specification-Derived Verification Plan

| Specification / behavior | Verification command or check | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, protected target scope | `python scripts/implementation_authorization.py begin --bridge-id gtkb-mass-release-candidate-blocker-repair` after GO, then `python scripts/implementation_authorization.py validate --target <each protected target>` | Authorization packet exists and every edited protected target is in scope. |
| Release lint blocker | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check applications\Agent_Red\src platform_tests --select E,F` | Exit 0. |
| Agent Red route-introspection blocker | `groundtruth-kb\.venv\Scripts\python.exe -m pytest applications\Agent_Red\tests\integrations\test_shopify_compliance.py::TestKBCRUDViaAPI::test_knowledge_api_has_crud_endpoints applications\Agent_Red\tests\integrations\test_shopify_compliance.py::TestTeamListViaAPI::test_team_api_has_list_endpoint applications\Agent_Red\tests\integrations\test_shopify_compliance.py::TestGDPRExportViaAPI::test_gdpr_export_endpoint_exists -q --tb=short` | Exit 0. |
| Canonical secrets workflow | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb secrets scan --tracked --redacted --report-json .tmp\gtkb-secrets-release.json --fail-on verified-provider` | Exit 0; report contains no verified-provider blockers. |
| Legacy secrets workflow removal/delegation | `rg -n "scripts/scan_secrets.py" .github/workflows` | No release-blocking workflow invokes the legacy scanner directly. |
| Noncanonical dump removal | `git ls-files applications/Agent_Red/docs/owner-messages-all.json` | No tracked path in release branch. |
| README/docs current-state alignment | `rg -n "smart poller|OS poller|bridge/INDEX.md|branch=develop" README.md docs/gtkb-systems-and-tools.md groundtruth-kb/docs/start-here.md groundtruth-kb/docs/day-in-the-life.md groundtruth-kb/docs/evidence.md groundtruth-kb/docs/troubleshooting/auth.md` | No obsolete release-surface claims remain, except clearly historical/deprecated contexts where the wording is intentional. |
| General formatting guard | `git diff --check HEAD -- <changed paths>` | Exit 0. |
| Release candidate gate | GitHub Actions on pushed candidate branch and local non-deploying gate where interpreter version allows it | Green or explicitly blocked by an environment-only Python-version mismatch documented in the implementation report. |

## Acceptance Criteria

- The release branch remains separated from unrelated dirty `develop` WIP.
- All target-path edits are scoped to the reproduced release blockers and docs alignment.
- The E/F lint command exits 0.
- The three Agent Red integration tests exit 0.
- The canonical redacted secrets scanner reports no verified-provider blockers.
- The duplicate legacy scanner workflow no longer creates a false high-severity health failure.
- The tracked owner-message dump is absent from the release branch unless contradicted by canonical evidence.
- README/in-repo docs no longer describe the new main release with obsolete poller or develop-branch claims.
- Post-implementation report includes exact command evidence and any residual release blockers or formal deferrals.

## Risks / Rollback

- Risk: deleting the owner-message dump removes a file someone used informally. Mitigation: current evidence says it is noncanonical release clutter, and the repo should not ship large owner transcript dumps with credential-shaped contents. Rollback restores the file from git history if a future canonical need is proven.
- Risk: removing the legacy secrets workflow hides issues the old scanner caught. Mitigation: the canonical GT-KB scanner remains in CI, uses the shared credential catalog, redacts output, and fails on verified-provider evidence. Any remaining scanner-design disagreements become a separate health proposal.
- Risk: docs/wiki drift still remains outside the target list. Mitigation: this slice only aligns the release-critical in-repo docs and produces a separate dashboard/wiki health implementation proposal after code verification.
- Rollback: one commit revert restores tests, workflow, docs, and the removed tracked dump. Bridge files remain append-only.

## Files Expected To Change

- `platform_tests/scripts/test_claude_session_start_dispatcher.py`
- `platform_tests/scripts/test_codex_session_start_dispatcher.py`
- `platform_tests/scripts/test_fab09_safety_gate_registration.py`
- `platform_tests/scripts/test_governing_specs_preserved.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_single_harness_dispatcher_task_installer.py`
- `platform_tests/scripts/test_ops_activity_context.py`
- `platform_tests/scripts/test_spec_coherence_cli.py`
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py`
- `platform_tests/skills/test_verified_finalization_validation_hardening.py`
- `applications/Agent_Red/tests/integrations/test_shopify_compliance.py`
- `applications/Agent_Red/docs/owner-messages-all.json`
- `.github/workflows/secrets-scan.yml`
- `README.md`
- `groundtruth-kb/docs/start-here.md`
- `groundtruth-kb/docs/day-in-the-life.md`
- `groundtruth-kb/docs/evidence.md`
- `groundtruth-kb/docs/troubleshooting/auth.md`
- `docs/gtkb-systems-and-tools.md`

## Recommended Commit Type

`fix`
