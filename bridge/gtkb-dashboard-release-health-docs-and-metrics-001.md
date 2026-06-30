NEW

# Dashboard release-health docs and metrics correction

bridge_kind: prime_proposal
Document: gtkb-dashboard-release-health-docs-and-metrics
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-30 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-DASHBOARD-OBSERVABILITY
Work Item: GTKB-DASHBOARD-003

target_paths: ["README.md", "groundtruth-kb/README.md", "groundtruth-kb/mkdocs.yml", "groundtruth-kb/docs/wiki/azure-enterprise-readiness.md", "groundtruth-kb/docs/wiki/release-health.md", "docs/gtkb-dashboard/index.html", "docs/gtkb-dashboard/grafana/README.md", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "scripts/gtkb_dashboard/generate_bridge_swimlane.py", "scripts/update_wiki_pages.py", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_gtkb_dashboard_alerting.py", "platform_tests/scripts/test_update_wiki_pages.py"]

implementation_scope: source, documentation, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal implements the remaining dashboard and GitHub documentation health fixes required before the ad hoc GT-KB release can be presented as clean on `main`. It is deliberately limited to the dashboard/wiki/README health surfaces: it does not implement dispatcher runtime fixes, merge branches, push commits, deploy anything, or mutate GitHub settings.

Live release-prep evidence from this session shows the current published and local health surfaces are not trustworthy enough for release signoff:

- `scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root E:\GT-KB` completed but warned that bridge-swimlane generation failed with `ImportError: attempted relative import with no known parent package`.
- The refreshed dashboard SQLite reported `current_metrics.release_blockers = 0` and green, even though the active release program still has unresolved blockers: broad dirty worktree classification, a clean release-candidate test self-containment failure, and dispatcher LO path uncertainty that only later produced a NO-GO on an unrelated hygiene thread.
- `integration_status` reported `live_state_unavailable` or `no_recent_run` for most GitHub gates, while `gh run list --repo Remaker-Digital/groundtruth-kb --branch main --limit 10` returned real main-branch workflow runs for Docs Quality, CodeQL, Dependabot, and Secrets Scan.
- The published wiki exists at `https://github.com/Remaker-Digital/groundtruth-kb.wiki.git` with only `Home.md` and `Azure-Enterprise-Readiness.md`; it does not describe the current release, dashboard health gates, dispatcher daemon state, or README/wiki comparison procedure.
- `scripts/update_wiki_pages.py` is still an Agent Red wiki updater aimed at a temp `agent-red.wiki` clone and is not a GT-KB wiki compare/publish mechanism.
- `README.md` still uses GitHub Actions badges with `branch=develop` even though GitHub reports `Remaker-Digital/groundtruth-kb` default branch `main`.

The implementation should make the dashboard, root/package README, and local wiki source pages agree with the post-merge `main` branch state and should add tests that prevent false-green release-health reporting.

## Specification Links

- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` - primary dashboard requirement. The dashboard must provide live KPI for release-readiness, bridge/contention, drift, regression, and related startup health. False-green release blockers and missing GitHub workflow state violate the spirit of this requirement.
- `GTKB-DASHBOARD-003` - governing work item. Requires SLO/error-budget model, flow metrics, branch/PR health, incident/MTTR, remote exposure, and WCAG audit visibility. This proposal implements the release-doc and branch/PR/wiki health portion needed for the ad hoc release path.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - a GT-KB release candidate cannot be treated as production-release GO without governed release-readiness evidence or explicit owner-approved deferral.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher reporting must expose reliability, failure taxonomy, live state, pending counts, and history through governed surfaces. The dashboard may consume these read surfaces, but must not hide WARN/NO-GO/unbounded states behind a green release metric.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/TAFE state and numbered bridge chains remain the live source for bridge actionability; dashboard/wiki/readme summaries are derived context only.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps GT-KB release-health source artifacts inside `E:\GT-KB` and prevents an out-of-root GitHub wiki clone from becoming a live project dependency.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications and maps them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the linked specs before this work can be VERIFIED.
- `GOV-STANDING-BACKLOG-001` - the work stays anchored to the MemBase backlog item instead of transient chat state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - release-health findings crossing from investigation into accepted future work must be preserved as durable artifacts, not scratchpad notes.

## Prior Deliberations

- `DELIB-20265586` - owner-approved bounded implementation authorization for `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`, including `GTKB-DASHBOARD-003`.
- `DELIB-0840` and `DELIB-0842` - source decisions behind `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`.
- `DELIB-0828` - release readiness requires governed test evidence, now captured in `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`.
- `DELIB-20265795` - dispatcher reporting/configuration must be exposed through governed `gt bridge dispatch` surfaces.
- `bridge/gtkb-dashboard-industry-alignment-slice2c-integration-006.md` - Slice 2.3 was VERIFIED; this proposal does not redo notifier work and builds on the existing dashboard integration.
- `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-004.md` and `bridge/gtkb-wi4933-post-verdict-exit-reconciliation-004.md` - WI-4933 route and post-verdict slices are VERIFIED; this proposal must display their release-health implications without reopening them.

## Owner Decisions / Input

No new owner decision is required to file or implement this proposal. The active project authorization `PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23` covers `GTKB-DASHBOARD-003` source, test addition, CLI extension, scaffold update, and related dashboard implementation work.

This proposal does not ask Codex to rotate credentials, change GitHub settings, deploy production assets, force-push, or mutate a wiki repository outside the GT-KB root. If implementation later needs to push the GitHub wiki repository, that publish action must be reported separately as an external Git operation and must not treat the out-of-root wiki clone as an authoritative GT-KB artifact.

## Requirement Sufficiency

Existing requirements are sufficient for this bounded dashboard/docs-health implementation. The work item itself names branch/PR health, remote exposure, and SLO/flow visibility; `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` requires release-readiness and bridge/contention KPI; and `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` requires release evidence before release GO.

No new formal requirement is needed before implementation, but the implementation report must be explicit about any remaining non-dashboard release blockers that are displayed rather than fixed by this slice.

## Proposed Scope

1. Correct dashboard release-health metrics so the dashboard cannot show `release_blockers = 0` green when the current release-prep branch still has unmerged verified work, unverified release-scope work, dirty unsafe paths, failed clean-candidate tests, dispatcher health WARN/NO-GO, or live unresolved Prime/LO bridge actionability.
2. Correct GitHub workflow health collection so `integration_status` distinguishes: real recent run success/failure, workflow absent, workflow not wired, manual/local-only gate, authentication unavailable, and no recent run. It must use the canonical `Remaker-Digital/groundtruth-kb` repository and current default branch unless an explicit release branch is supplied.
3. Fix direct-script dashboard refresh so bridge-swimlane generation does not warn under the documented command shape. The direct `python scripts/gtkb_dashboard/refresh_dashboard_db.py ...` path should either import `generate_bridge_swimlane` correctly or surface a hard dashboard-health finding when swimlane generation fails.
4. Add or correct dashboard panels for release blockers, dirty/release-ready classification, dispatcher daemon health, bridge Prime/LO actionability, GitHub workflow state, README/wiki drift, and docs publish status.
5. Replace, retire, or quarantine the stale Agent Red `scripts/update_wiki_pages.py` path so GT-KB has a governed wiki compare/update command for the `Remaker-Digital/groundtruth-kb` wiki. The implementation should prefer local source pages under `groundtruth-kb/docs/wiki/` and should publish only from those in-root sources.
6. Add a release-health wiki source page covering the current GT-KB release model, dispatcher/dashboard health gates, README/wiki comparison procedure, and release-blocker semantics. Wire it into `groundtruth-kb/mkdocs.yml` if it belongs in the package docs navigation.
7. Correct root `README.md` and package `groundtruth-kb/README.md` so branch badges, release state, dashboard URL/run commands, wiki references, and main-branch documentation claims match the post-merge `main` reality.
8. Keep implementation reductive: remove stale Agent Red/adopter release claims from GT-KB release surfaces where they are not authority, and replace broad warnings with deterministic source-of-truth checks.

Out of scope:

- Changing dispatcher selection, provider credentials, model routing, process lifetime, or bridge verdict logic.
- Declaring the release ready.
- Merging `research`, `develop`, or `main`.
- Pushing the root repository or wiki repository.
- Editing out-of-root wiki clones as canonical GT-KB artifacts.

## Spec-Derived Verification Plan

All commands should run from `E:\GT-KB` unless the implementation report gives a narrower clean-worktree candidate path.

| Spec or governing surface | Verification |
| --- | --- |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` | Add tests proving dashboard DB refresh emits non-green release-health KPI when fixture data includes dirty unsafe paths, unresolved release blockers, dispatcher WARN/NO-GO, or bridge GO/NO-GO actionability. Run `python -m pytest platform_tests/scripts/test_gtkb_dashboard_grafana.py -q --tb=short`. |
| `GTKB-DASHBOARD-003` | Add dashboard panel/query tests for branch/PR or GitHub workflow health, release blockers, dispatcher health, and wiki/docs drift. Confirm generated `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` contains the expected panel titles and SQLite datasource queries. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Add a regression proving the dashboard does not treat a release candidate as green solely because `memory/release-readiness.md` reports no blockers when live git/bridge/dispatcher checks contradict it. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Use `gt bridge dispatch daemon status --json`, `gt bridge dispatch health --json`, and `gt bridge dispatch report --json` fixtures or monkeypatches to prove dispatcher live state, WARN, provider backoff, and NO-GO outcomes are rendered distinctly. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Prove dashboard/wiki health derives bridge actionability from TAFE/dispatcher state plus numbered bridge files, not from cached startup summaries. |
| Wiki/README release docs | Add tests for the GT-KB wiki source/update tool that compare `groundtruth-kb/docs/wiki/*.md` to the checked-out wiki clone content without treating the clone as authority. Add README assertions that badges use `main` where main is the release branch. |
| Bridge governance DCLs | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dashboard-release-health-docs-and-metrics` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dashboard-release-health-docs-and-metrics`; expect no missing required specs and zero blocking gaps. |

Expected focused verification command set:

```text
python -m pytest platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_gtkb_dashboard_alerting.py platform_tests/scripts/test_update_wiki_pages.py -q --tb=short
python -m ruff check scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/generate_bridge_swimlane.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_gtkb_dashboard_alerting.py platform_tests/scripts/test_update_wiki_pages.py
python -m ruff format --check scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/generate_bridge_swimlane.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_gtkb_dashboard_alerting.py platform_tests/scripts/test_update_wiki_pages.py
python scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root E:\GT-KB
```

## Acceptance Criteria

- Dashboard refresh has no bridge-swimlane import warning under the documented direct-script command.
- Dashboard release blockers cannot be green when live git, bridge, dispatcher, or clean-candidate verification evidence is release-blocking.
- GitHub workflow health surfaces real `Remaker-Digital/groundtruth-kb` main-branch runs when `gh` is authenticated, and explicitly classifies absent/manual/unavailable workflows.
- Root README badges and package README release/dashboard/wiki references match the selected `main` release branch after merge.
- The GT-KB wiki has in-root source pages for current release-health and Azure readiness, and the update/compare tool no longer silently targets Agent Red as if it were the GT-KB wiki.
- Tests cover README/wiki drift and dashboard false-green release-health regressions.
- Implementation report includes a post-change comparison of local `main` README/wiki source versus the published GitHub README/wiki, without relying on stale chat state.

## Risk / Rollback

Risk is moderate because this slice touches release-health reporting and public documentation. A false positive can block releases unnecessarily; a false negative can make a dirty or unverified release look safe.

Rollback is a normal single-commit revert of dashboard/docs/test changes. If a wiki push happens in a later authorized publish step, rollback requires a follow-up wiki commit restoring the previous wiki content; the out-of-root wiki clone must not become a GT-KB authority surface.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-dashboard-release-health-docs-and-metrics`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered bridge file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - the implementation should correct false-green release-health reporting and stale documentation publish/update behavior.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
