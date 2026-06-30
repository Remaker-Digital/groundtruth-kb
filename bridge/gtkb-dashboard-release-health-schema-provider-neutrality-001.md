NEW

# Dashboard release-health self-containment and provider-neutral deployment signals

bridge_kind: prime_proposal
Document: gtkb-dashboard-release-health-schema-provider-neutrality
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

target_paths: ["scripts/gtkb_dashboard/schema.sql", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "scripts/update_wiki_pages.py", "docs/gtkb-dashboard/grafana/README.md", "docs/gtkb-dashboard/grafana/PACKAGE-INTEGRATION.md", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json", "docs/gtkb-dashboard/grafana/provisioning/alerting/failing-ci.yaml", "docs/gtkb-dashboard/grafana/provisioning/alerting/stale-data.yaml", "docs/gtkb-dashboard/grafana/provisioning/alerting/release-blockers.yaml", "README.md", "groundtruth-kb/README.md", "groundtruth-kb/mkdocs.yml", "groundtruth-kb/docs/wiki/release-health.md", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_update_wiki_pages.py", "platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py"]

implementation_scope: source, documentation, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal is a narrow follow-up to the VERIFIED dashboard release-health slice `gtkb-dashboard-release-health-docs-and-metrics`. The prior slice improved the dashboard, README, and local wiki sources, but release-prep verification found two remaining release blockers: the verified commit is not self-contained from a clean checkout, and GT-KB-owned dashboard surfaces still carry application/provider-specific defaults.

The self-containment defect is concrete. A clean archive of commit `4c44b0ba6` initializes the dashboard database, then fails the documented refresh with `sqlite3.OperationalError: no such table: application_deployment_signals`. The implementation inserted and refreshed `application_deployment_signals` rows, but the approved target paths did not include `scripts/gtkb_dashboard/schema.sql`, so the table definition remains only as a dirty worktree change and cannot be treated as release-ready.

The provider-neutrality defect is also concrete. Current dashboard code and generated assets still include Agent Red/Azure-specific defaults: Grafana title/uid/tags use `Agent Red` / `agent-red`, the optional Azure reconciliation code contains `agent-red-api-gateway` and `agent-red-staging`, and alerting files retain `agent-red-*` identifiers. Per owner direction on 2026-06-30, GT-KB is not bound to any deployment environment. The GT-KB dashboard may expose application deployment, container, security, throughput/latency, defect, and infrastructure health display areas, but the application owns any integration with Azure, Kubernetes, containers, VMs, or another external environment. GT-KB defaults must therefore be mock/provider-neutral contract rows, not embedded Agent Red or Azure assumptions.

## Specification Links

- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` - dashboard release-readiness KPI must be trustworthy and derived from canonical state rather than dirty local leftovers.
- `GTKB-DASHBOARD-003` - governing dashboard work item for release health, branch/PR health, SLO/flow visibility, and dashboard exposure.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness cannot be declared from a commit that fails clean-checkout dashboard refresh.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dashboard dispatcher health panels must report WARN/stale-terminal findings distinctly and must not hide them behind green release status.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/TAFE numbered files remain authoritative for bridge actionability and release-blocker state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - application integration belongs outside GT-KB platform defaults; dashboard application-deployment data is supplied by the application.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - deferred findings and release-health exceptions must remain visible as lifecycle artifacts, not disappear into scratch state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal declares governing specs and maps verification to them.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include tests derived from the linked specs.
- `GOV-STANDING-BACKLOG-001` - remaining dashboard health work stays anchored to the backlog item, not transient chat state.

## Prior Deliberations

- `DELIB-20265586` - owner-approved bounded implementation authorization for `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`, including `GTKB-DASHBOARD-003`.
- `DELIB-0840` and `DELIB-0842` - source decisions behind `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`.
- `DELIB-0828` - release readiness requires governed test evidence before release GO.
- `DELIB-20265795` - dispatcher reporting/configuration should be exposed through governed `gt bridge dispatch` surfaces.
- `DELIB-20260630-DEFERRAL-EXPIRY-001` - owner decision that every deferred artifact/backlog/bridge/release item needs an explicit expiry condition or resume trigger; indefinite deferral is a governance defect.
- `INTAKE-670252e3` - current dashboard deployment-environment intake evidence; it demonstrates the existing helper can create deferred records without expiry and should not be used as sufficient release evidence until backfilled or confirmed.
- `bridge/gtkb-dashboard-release-health-docs-and-metrics-001.md` through `-004.md` - prior dashboard release-health proposal and VERIFIED verdict. This follow-up does not redo that work; it corrects newly discovered release blockers from clean-checkout and provider-neutrality verification.
- `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-004.md`, `bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-004.md`, and `bridge/gtkb-wi4933-post-verdict-exit-reconciliation-004.md` - dispatcher-adjacent WI-4933 slices that are now VERIFIED but do not eliminate the current dispatch health WARN findings.

## Owner Decisions / Input

No new owner decision is required before implementation. The owner has already clarified that GT-KB is environment-agnostic and that dashboard deployment surfaces must be application-populated, with GT-KB shipping mock application deployment data for testing and display contract purposes.

This proposal does not authorize pushing the root repository, publishing the GitHub wiki, changing provider credentials, deploying an application, or changing external infrastructure. If implementation later requires a wiki push, that publish action must be surfaced separately and the out-of-root wiki clone must remain a publication target, not a source of truth.

## Requirement Sufficiency

Existing dashboard, release-readiness, application-isolation, and artifact-lifecycle requirements are sufficient for this correction. The implementation must not add a new Azure-specific requirement. Any Azure wording left in README/wiki/dashboard docs must be framed as optional adopter/readiness example text, never as a GT-KB dashboard dependency or release gate.

The owner decision on deferral expiry is sufficient to require dashboard surfacing of indefinite deferrals as a health warning. Full schema/enforcement changes for all deferral-producing commands may need a separate governance-hardening implementation proposal if they extend beyond the dashboard target paths.

## Proposed Scope

1. Add the missing `application_deployment_signals` DDL to `scripts/gtkb_dashboard/schema.sql` and add a regression proving a clean checkout or clean archive can initialize and refresh the dashboard database without relying on dirty local files.
2. Keep GT-KB dashboard application-deployment data provider-neutral by default. Rows should describe display contracts such as topology, containers, security posture, throughput/latency, defects, and infrastructure health using mock values and application-supplied source contracts.
3. Remove hardcoded Agent Red and Azure deployment identifiers from GT-KB-owned dashboard defaults, Grafana title/uid/tags, alert rule ids, and refresh-time default reconciliation mappings. Application-specific examples may remain only when clearly marked as adopter-owned examples or optional documentation.
4. Make Azure Container Apps reconciliation fully application-owned and opt-in. GT-KB may expose a generic connector/read-surface contract, but must not ship an Azure app-name map as platform default behavior.
5. Add dashboard health data or tests that classify deferred records lacking an expiry, time limit, or resume trigger as release-health WARN. This implements the 2026-06-30 owner decision in the dashboard layer without claiming full global enforcement.
6. Preserve dispatcher health visibility from governed `gt bridge dispatch` surfaces. WARN/stale-terminal findings and no-drainable-worker anomalies should be shown as release blockers or warnings, not normalized to green.
7. Correct README/wiki release-health wording so the published story is provider-neutral and matches the clean-checkout main-branch state after merge.
8. Correct wiki source handling where needed so tracked in-root wiki source pages are intentional and testable, avoiding ignored source-of-truth pages that require accidental force-adds.

Out of scope:

- Runtime dispatcher fixes such as per-document LO leases, drain process-tree ownership, stale terminal failure cleanup, or provider retry policy. Those remain release blockers but need their own dispatcher reliability proposal if not already covered by an active GO.
- Global schema enforcement for every `deferred` state across MemBase, deliberations, bridge advisories, and spec intake. This proposal only adds dashboard visibility and tests for the condition.
- Publishing to GitHub, changing repository default branches, or deploying any external service.
- Reintroducing retired cross-harness trigger paths or hook-driven automation.

## Spec-Derived Verification Plan

| Governing surface | Verification |
| --- | --- |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Create a clean archive/checkout regression that runs `scripts/gtkb_dashboard/refresh_dashboard_db.py --init-only` and then a full refresh against a new SQLite file. Expected result: exit 0 and `application_deployment_signals` exists. |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` and `GTKB-DASHBOARD-003` | Run focused dashboard tests proving generated Grafana JSON contains provider-neutral dashboard title/uid/tags and application-deployment panels for topology, containers, security, throughput/latency, defects, and infrastructure health. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Add a regression that default dashboard refresh/generation does not contain hardcoded `agent-red-api-gateway`, `agent-red-staging`, `Agent Red GT-KB Dashboard`, or `agent-red-gtkb` strings in GT-KB platform defaults. |
| Owner deferral-expiry decision | Add a dashboard test/fixture where a deferred record with no expiry/resume trigger produces a WARN health row; a deferred record with an explicit state trigger or time limit does not. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Add or update tests proving dispatcher WARN/stale-terminal findings are represented distinctly in dashboard health data and are not counted as release-green. |
| README/wiki docs | Add/update tests for README/wiki source comparison showing provider-neutral wording and no claim that Azure is required for GT-KB dashboard release health. |
| Bridge governance DCLs | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dashboard-release-health-schema-provider-neutrality` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dashboard-release-health-schema-provider-neutrality`; expected result: no blocking gaps. |

Expected focused command set:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_dashboard/schema.sql scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-clean.sqlite --project-root E:\GT-KB --init-only
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-clean.sqlite --project-root E:\GT-KB
```

## Risk / Rollback

Risk: provider-neutralizing dashboard defaults could remove useful Agent Red examples. Mitigation: keep examples only in explicitly adopter-scoped documentation, and ensure the GT-KB dashboard still ships complete mock rows for application deployment surfaces.

Risk: deferral-expiry dashboard WARN may expose many legacy indefinite deferrals. Mitigation: classify as WARN with explicit backfill path; do not auto-close or auto-reprioritize them in this slice.

Rollback: one commit can revert schema/docs/tests/generator changes. The prior dashboard release-health commit remains intact, and this bridge file documents why the follow-up was required.

## Bridge Filing

This proposal is filed under `bridge/` as `gtkb-dashboard-release-health-schema-provider-neutrality-001.md`. Dispatcher/TAFE state plus the numbered bridge file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(dashboard)`: this corrects a verified-but-not-self-contained dashboard release-health slice and removes provider-specific defaults from GT-KB-owned release surfaces.
