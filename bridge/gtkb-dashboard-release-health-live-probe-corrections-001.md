NEW

# Dashboard release-health live-probe and card consistency corrections

bridge_kind: prime_proposal
Document: gtkb-dashboard-release-health-live-probe-corrections
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

target_paths: ["scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "scripts/gtkb_dashboard/schema.sql", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json", "docs/gtkb-dashboard/grafana/README.md", "README.md", "groundtruth-kb/docs/wiki/release-health.md", "scripts/update_wiki_pages.py", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py", "platform_tests/scripts/test_update_wiki_pages.py"]

implementation_scope: source, documentation, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal is a narrow follow-up to the VERIFIED dashboard provider-neutrality slice `gtkb-dashboard-release-health-schema-provider-neutrality`. That slice correctly made GT-KB dashboard deployment surfaces provider-neutral and self-contained, but the current release-prep live dashboard probe exposed three remaining dashboard-health accuracy defects.

First, `current_metrics.release_blockers` reports `3/red` and the `release_blockers` table contains live blockers, while the `health_cards` table still reports `Release Readiness = 0 blockers/green` and `Project Health = 0 issues/yellow`. Second, `current_metrics.dirty_worktree_paths` reports the startup-model drift count (`8`) while the live release blocker reports the real `git status` dirty count (`304` at probe time, then `305` after a daemon-driven bridge verdict arrived). Third, `integration_status.github` reports `live_state_unavailable` even though `gh auth status` and direct `gh run list --repo Remaker-Digital/groundtruth-kb --branch main` succeed. Reproduction shows `build_startup_model(...)` mutates `XDG_CONFIG_HOME` to the temp directory before the workflow probe runs, causing `gh` to miss the host GitHub CLI auth store.

The fix should make dashboard live probes and dashboard display cards agree with canonical live evidence, without changing dispatcher runtime behavior, restoring retired automation, or introducing any deployment-provider dependency.

## Specification Links

- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` - dashboard release-readiness KPIs must be trustworthy and derived from canonical evidence.
- `GTKB-DASHBOARD-003` - governing dashboard work item for branch/PR health, release health, SLO/flow visibility, and dashboard exposure.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness must be proven from governed local/live evidence rather than stale dashboard rows.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher WARN/backpressure findings must remain visible and not be collapsed into green release status.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - dashboard deployment panels remain provider-neutral; this proposal must not add an Azure or Agent Red platform dependency.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - live release-health findings and deferred work must remain visible as lifecycle artifacts with explicit closure or expiry.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - concrete release-health findings and follow-up work should be preserved as durable artifacts rather than scratch notes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/TAFE numbered files are the authoritative bridge workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal declares concrete governing specs and maps verification to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the linked specs.
- `GOV-STANDING-BACKLOG-001` - remaining dashboard health work stays anchored to the backlog item and bridge chain, not transient notes.

## Prior Deliberations

- `DELIB-20265586` - owner-approved bounded implementation authorization for `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`, including `GTKB-DASHBOARD-003`.
- `DELIB-0840` and `DELIB-0842` - source decisions behind `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`.
- `DELIB-0828` - release readiness requires governed test evidence before release GO.
- `DELIB-20265795` - dispatcher reporting/configuration should be exposed through governed `gt bridge dispatch` surfaces.
- `DELIB-20260630-DEFERRAL-EXPIRY-001` - owner decision that deferred work requires an explicit expiry condition, time limit, or resume trigger.
- `INTAKE-670252e3` - owner clarification that dashboard deployment surfaces are application-populated and deployment-environment agnostic.
- `bridge/gtkb-dashboard-release-health-schema-provider-neutrality-001.md` through `-004.md` - prior dashboard release-health provider-neutrality proposal and VERIFIED verdict. This follow-up does not redo that work; it corrects live-probe/card consistency defects found afterward.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - confirms the dispatcher supervisor is registered, enabled, hidden/headless, and verified; remaining dashboard work must not keep presenting supervisor activation as open.

## Owner Decisions / Input

No new owner decision is required before implementation. The active project authorization is `status=active`, includes `GTKB-DASHBOARD-003`, and permits source, test, CLI/scaffold, and hook-upgrade classes for the dashboard observability project. The owner has already clarified that GT-KB is provider-neutral and that deferred work requires explicit expiry or a resume trigger.

This proposal does not authorize pushing `main`, publishing the GitHub wiki, changing external GitHub settings, deploying an application, changing credentials, or mutating dispatcher runtime behavior. Those actions require their own release-management or bridge authority.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `GTKB-DASHBOARD-003`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and the owner deferral-expiry decision already require accurate live release-health dashboard presentation. No new Azure-specific or deployment-provider requirement is needed.

## Proposed Scope

1. Reconcile `health_cards` with live release-health findings after live probes run, so the cards cannot show `0 blockers` or green readiness while `current_metrics.release_blockers` and `release_blockers` show active blockers.
2. Split or reconcile model dirty-path counts versus live `git status` dirty-path counts. When `--probe-live` is enabled, the dashboard must either expose both counts with distinct labels or consistently use the live count for release-blocker/readiness status.
3. Preserve host GitHub CLI auth for live workflow probes. The implementation should protect `gh` subprocesses from startup-model mutations such as `XDG_CONFIG_HOME=<temp>`, or restore the pre-model GitHub config environment before probing.
4. Add regression coverage proving `_github_workflow_live_status(...)` reports a successful main-branch workflow when `gh run list` succeeds even after startup-model environment mutations.
5. Add regression coverage proving health cards, current metrics, and blocker rows agree under live-probe fixture data.
6. Add a dashboard row or metric for the WI-4937 supervisor health state, using the governed `gt bridge dispatch daemon supervisor status --json` evidence when available. The row must distinguish healthy headless supervisor state from remaining route/runtime WARNs.
7. Keep the existing provider-neutral mock deployment rows intact and keep Azure reconciliation opt-in/application-owned only.
8. Update README/wiki/dashboard docs only as needed to describe the corrected live-probe semantics and to avoid stale claims about supervisor or GitHub workflow health.

Out of scope:

- Fixing dispatcher route/runtime failures for D, E, or F. Those remain dispatcher reliability work and must stay visible as release blockers until separately fixed or explicitly dispositioned.
- Merging or pushing `main`, publishing the GitHub wiki, or changing GitHub branch/workflow settings.
- Global enforcement of deferral expiry across every writer. This proposal only concerns dashboard surfacing and live-probe accuracy.
- Restoring retired cross-harness trigger paths or hook-driven automation.

## Spec-Derived Verification Plan

| Governing surface | Verification |
| --- | --- |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` / `GTKB-DASHBOARD-003` | Focused dashboard DB tests prove `health_cards`, `current_metrics`, and `release_blockers` agree when live release-health findings are present. Expected: no green `Release Readiness` card while blocker rows exist. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Refresh a disposable SQLite DB with `--probe-live` or mocked live probes and assert blocker/readiness values come from current live evidence rather than stale startup-model values. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Test that dispatcher health findings and WI-4937 supervisor health are represented separately: supervisor `healthy=true` is green, while route/runtime WARN findings remain non-green release-health findings. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing provider-neutral deployment-signal tests remain green; no new hardcoded Agent Red or Azure default strings are introduced. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Existing deferral-expiry WARN tests remain green and continue to distinguish bounded deferrals from indefinite ones. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each changed function/table/panel to focused tests and command evidence. |
| README/wiki docs | If docs change, tests verify release-health wording still says Azure reconciliation is opt-in adopter diagnostics only and GT-KB deployment panels default to mock/provider-neutral rows. |
| Bridge governance DCLs | Run applicability and clause preflights for `gtkb-dashboard-release-health-live-probe-corrections`; expected: no blocking gaps. |

Expected focused command set:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py platform_tests/scripts/test_update_wiki_pages.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py platform_tests/scripts/test_update_wiki_pages.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py platform_tests/scripts/test_update_wiki_pages.py
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-live-probe.sqlite --project-root E:\GT-KB --probe-live
```

## Risk / Rollback

Risk: fixing live-card reconciliation could make the dashboard look worse by surfacing blockers that were previously hidden. That is the intended release-health behavior; the implementation should make the evidence easier to interpret, not downgrade it artificially.

Risk: preserving GitHub CLI config for `gh` subprocesses could accidentally depend on host-local auth state in tests. Mitigation: unit tests should mock the subprocess call and assert environment construction, while live refresh evidence can be captured separately when `gh` is available.

Rollback: one commit can revert dashboard refresh/generation/docs/tests. The prior provider-neutrality VERIFIED commit remains intact and this proposal documents the narrower follow-up.

## Bridge Filing

This proposal is filed under `bridge/` as `gtkb-dashboard-release-health-live-probe-corrections-001.md`. Dispatcher/TAFE state plus the numbered bridge file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(dashboard)`: this corrects dashboard release-health live-probe accuracy and display-card consistency.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
