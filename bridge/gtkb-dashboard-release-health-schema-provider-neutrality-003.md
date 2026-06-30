NEW

# GT-KB Bridge Implementation Report - gtkb-dashboard-release-health-schema-provider-neutrality - 003

bridge_kind: implementation_report
Document: gtkb-dashboard-release-health-schema-provider-neutrality
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-dashboard-release-health-schema-provider-neutrality-002.md
Approved proposal: bridge/gtkb-dashboard-release-health-schema-provider-neutrality-001.md
Recommended commit type: fix:

Author: Prime Builder (Codex, harness A)
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access
Date: 2026-06-30 UTC

## Implementation Claim

Implemented the dashboard release-health self-containment and provider-neutrality correction authorized by the GO verdict.

The dashboard schema now contains the `application_deployment_signals` table in `scripts/gtkb_dashboard/schema.sql`, so a fresh SQLite dashboard database can initialize and refresh without relying on dirty local DDL. The dashboard refresh populates six mock provider-neutral application deployment surfaces: deployment topology, containers, security, throughput/latency, defects, and infrastructure health.

Grafana dashboard identity and alert rule identifiers are now GT-KB scoped rather than Agent Red scoped. The generated dashboard title is `GT-KB Operations Dashboard`, UID is `groundtruth-kb-dashboard`, and tags are `gt-kb`, `operations`, and `sqlite`.

Azure reconciliation remains available only as an optional adopter diagnostic. It no longer ships hardcoded Agent Red Azure app names or resource groups; when enabled, the application must supply `GTKB_DASHBOARD_AZURE_CONTAINER_APP_MAP` and `GTKB_DASHBOARD_AZURE_RESOURCE_GROUP`.

The release-health model now surfaces deferred records lacking an expiry, time limit, or resume trigger as a `deferral-expiry` WARN finding. This implements the 2026-06-30 owner decision at the dashboard layer without claiming global deferral enforcement.

Wiki/README wording now says the dashboard deployment-health surfaces are provider-neutral contracts populated by the active application. `scripts/update_wiki_pages.py` now uses an explicit wiki source allowlist so ignored local wiki drafts cannot become accidental GitHub Wiki source pages.

## Specification Links

- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`
- `GTKB-DASHBOARD-003`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision is required. This implementation applies the owner’s 2026-06-30 clarifications:

- GT-KB is not bound to Azure or any deployment environment.
- GT-KB dashboard deployment-health panels are provider-neutral display contracts with mock data by default.
- Live deployment integration belongs to the active application.
- Deferred work must have an expiry, time limit, or resume trigger.

## Prior Deliberations

- `DELIB-20265586` - bounded dashboard observability implementation authorization.
- `DELIB-20260630-DEFERRAL-EXPIRY-001` - owner decision requiring bounded deferrals.
- `INTAKE-670252e3` - deployment-environment agnostic dashboard intake evidence.
- `bridge/gtkb-dashboard-release-health-docs-and-metrics-001.md` through `-004.md` - prior VERIFIED dashboard release-health slice.
- `bridge/gtkb-dashboard-release-health-schema-provider-neutrality-001.md` - approved proposal.
- `bridge/gtkb-dashboard-release-health-schema-provider-neutrality-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification

| Governing surface | Executed verification evidence |
| --- | --- |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py` verifies fresh dashboard schema self-containment and `application_deployment_signals` population. Fresh operational refresh also completed against `.tmp/gtkb-dashboard-clean.sqlite`. |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` / `GTKB-DASHBOARD-003` | `platform_tests/scripts/test_gtkb_dashboard_grafana.py` verifies dashboard metrics, application deployment signal rows, provider-neutral Grafana identity, and deployment signal panels. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests assert default dashboard code no longer contains `agent-red-api-gateway` or `agent-red-staging`, and Azure reconciliation reads application-supplied mapping. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_deferred_records_without_expiry_surface_release_health_warn` verifies indefinite deferrals become a `deferral-expiry` WARN release-health finding while bounded deferrals do not. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Existing dashboard release-health metric tests still verify dispatcher, bridge, and README/wiki findings remain distinct and non-green. |
| README/wiki docs | `platform_tests/scripts/test_update_wiki_pages.py` verifies main-branch README references, release-health source references, no Agent Red package README wording, and intentional wiki source allowlisting. |
| Bridge governance DCLs | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dashboard-release-health-schema-provider-neutrality` passed with `preflight_passed: true` and no missing required specs. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_update_wiki_pages.py platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-clean.sqlite --project-root E:\GT-KB --init-only`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-clean.sqlite --project-root E:\GT-KB`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dashboard-release-health-schema-provider-neutrality`

## Observed Results

- Pytest: `30 passed in 10.62s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `6 files already formatted`.
- Dashboard init-only: `Initialized .tmp\gtkb-dashboard-clean.sqlite`.
- Dashboard full refresh: status `completed`, run id `1`, completed at `2026-06-30T18:31:21.441096+00:00`.
- Fresh dashboard database contains 6 `application_deployment_signals` rows.
- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`.

## Files Changed

- `README.md`
- `docs/gtkb-dashboard/grafana/PACKAGE-INTEGRATION.md`
- `docs/gtkb-dashboard/grafana/README.md`
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/failing-ci.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/release-blockers.yaml`
- `docs/gtkb-dashboard/grafana/provisioning/alerting/stale-data.yaml`
- `groundtruth-kb/README.md`
- `groundtruth-kb/docs/wiki/release-health.md`
- `groundtruth-kb/mkdocs.yml`
- `platform_tests/scripts/test_gtkb_dashboard_clean_checkout.py`
- `platform_tests/scripts/test_gtkb_dashboard_grafana.py`
- `platform_tests/scripts/test_update_wiki_pages.py`
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py`
- `scripts/gtkb_dashboard/refresh_dashboard_db.py`
- `scripts/gtkb_dashboard/schema.sql`
- `scripts/update_wiki_pages.py`

## Recommended Commit Type

- Recommended commit type: `fix:`
- Justification: this corrects a verified dashboard slice that was not clean-checkout self-contained and removes application/provider-specific defaults from release surfaces.

## Acceptance Criteria Status

- [x] Missing `application_deployment_signals` DDL added to `schema.sql`.
- [x] Clean dashboard initialization and refresh verified against a fresh SQLite database.
- [x] GT-KB-owned dashboard defaults no longer include hardcoded Agent Red dashboard title, UID, tags, alert rule IDs, or Azure app names.
- [x] Azure Container Apps reconciliation is opt-in and application-configured.
- [x] Dashboard includes provider-neutral mock application deployment signal rows and Grafana panels.
- [x] Deferred records without expiry/resume trigger surface as WARN.
- [x] README/wiki release-health wording explains the provider-neutral application-owned integration boundary.
- [x] Wiki source handling avoids ignored local drafts as publication source.

## Risk And Rollback

Residual risk: this is dashboard-layer visibility and documentation; it does not globally enforce deferral expiry across every command that can create a deferred record.

Rollback: revert the listed dashboard source, generated Grafana JSON, docs, and focused tests in one commit. The prior VERIFIED dashboard docs/metrics slice remains intact, but without this correction a clean release candidate would again fail dashboard refresh due the missing table.

## Loyal Opposition Asks

1. Verify the implementation against the approved proposal and the command evidence above.
2. Confirm the dashboard remains provider-neutral by default and Azure is only an application-owned opt-in diagnostic.
3. Return VERIFIED if satisfied; otherwise return NO-GO with concrete findings.
