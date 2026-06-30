NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 3aa60cca-409d-46f5-8f67-db7154c85bba
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop interactive session

# GT-KB Bridge Implementation Report - gtkb-dashboard-release-health-live-probe-corrections - 003

bridge_kind: implementation_report
Document: gtkb-dashboard-release-health-live-probe-corrections
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-dashboard-release-health-live-probe-corrections-002.md
Approved proposal: bridge/gtkb-dashboard-release-health-live-probe-corrections-001.md
Recommended commit type: fix:

## Implementation Claim

Implemented the approved dashboard release-health live-probe corrections without changing dispatcher runtime behavior, retired automation, external GitHub settings, or deployment-provider integration.

The refresh path now restores host GitHub CLI auth-related environment variables after startup-model collection, so a startup-model mutation of `XDG_CONFIG_HOME` or `GH_CONFIG_DIR` cannot make the later `gh run list` live workflow probe miss the host auth store. Live git dirty-path counts now flow into the `dirty_worktree_paths` current metric when live probes run, while the dirty-worktree finding remains visible as a release blocker. Health cards are reconciled from the same current-metric rows as the release blocker table, so `Project Health` and `Release Readiness` cannot remain green/zero while release blockers exist. The live probe also adds a `dispatcher_supervisor` integration row that reports the WI-4937 headless supervisor state independently from dispatcher route/runtime WARNs.

## Scope Actually Changed

- `scripts/gtkb_dashboard/refresh_dashboard_db.py`
- `platform_tests/scripts/test_gtkb_dashboard_grafana.py`

No README, wiki source, Grafana JSON, schema, or wiki updater changes were needed for this implementation. The existing provider-neutral deployment mock rows and optional Azure reconciliation behavior were left intact.

## Governance Evidence

- Work-intent claim: `scripts/bridge_claim_cli.py claim gtkb-dashboard-release-health-live-probe-corrections --session-id 019f18fc-3060-7b83-b9ab-297901b013c9` acquired row `26230`, `claim_kind=go_implementation`, `acting_role=prime-builder`.
- Claim extension: `scripts/bridge_claim_cli.py extend gtkb-dashboard-release-health-live-probe-corrections --session-id 019f18fc-3060-7b83-b9ab-297901b013c9` extended implementation deadline to `2026-06-30T22:59:24Z`, grace to `2026-06-30T23:09:24Z`.
- Implementation-start packet: `scripts/implementation_authorization.py begin --bridge-id gtkb-dashboard-release-health-live-probe-corrections --session-id 019f18fc-3060-7b83-b9ab-297901b013c9`.
- Packet hash: `sha256:ab014765d229baf188bf71e36c14d153a427a0d883e7bf9b970ff35ecb250a01`.
- Protected-target validation:
  - `scripts/implementation_authorization.py validate --target scripts/gtkb_dashboard/refresh_dashboard_db.py` returned `authorized=true`.
  - `scripts/implementation_authorization.py validate --target platform_tests/scripts/test_gtkb_dashboard_grafana.py` returned `authorized=true`.

## Specification Links

- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`
- `GTKB-DASHBOARD-003`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20265586` - owner-approved bounded implementation authorization for `PROJECT-GTKB-DASHBOARD-OBSERVABILITY`, including `GTKB-DASHBOARD-003`.
- `DELIB-0840` and `DELIB-0842` - source decisions behind `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`.
- `DELIB-0828` - release readiness requires governed test evidence before release GO.
- `DELIB-20265795` - dispatcher reporting/configuration should be exposed through governed `gt bridge dispatch` surfaces.
- `DELIB-20260630-DEFERRAL-EXPIRY-001` - owner decision that deferred work requires explicit expiry.
- `INTAKE-670252e3` - owner clarification that dashboard deployment surfaces are application-populated and deployment-environment agnostic.
- `bridge/gtkb-dashboard-release-health-schema-provider-neutrality-001.md` through `-004.md` - prior VERIFIED provider-neutrality slice.
- `bridge/gtkb-wi4937-dispatcher-supervisor-governance-006.md` - dispatcher supervisor is registered, enabled, hidden/headless, and verified.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` / `GTKB-DASHBOARD-003` | `test_release_health_findings_make_release_readiness_non_green` proves `health_cards`, `current_metrics`, and `release_blockers` agree when live release-health blockers exist. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `test_live_dirty_worktree_count_overrides_startup_model_count` proves live git dirty count overrides stale startup-model drift count for release-health metrics. Live refresh evidence below confirms the disposable DB reports live blockers. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `test_probe_live_adds_headless_dispatcher_supervisor_status` proves the supervisor row reports green `healthy_headless`; live refresh evidence below still reports dispatcher route WARN as a separate red blocker. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing `test_azure_reconciliation_is_explicit_opt_in` and `test_azure_reconciliation_requires_application_supplied_container_app_map` stayed green; no deployment-provider-specific dashboard dependency was added. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Existing `test_deferred_records_without_expiry_surface_release_health_warn` stayed green; deferral-expiry WARN behavior remains visible. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps each changed behavior to focused tests and command evidence. |
| README/wiki docs | `test_update_wiki_pages.py` stayed green. No doc source change was needed because semantics remain provider-neutral and existing docs already describe the release-health behavior. |
| Bridge governance DCLs | GO verdict `bridge/gtkb-dashboard-release-health-live-probe-corrections-002.md` records passing applicability and clause preflights; implementation-start packet and target validation above preserve the implementation gate. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dashboard_grafana.py -q --tb=short
```

Observed result: `25 passed in 16.36s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dashboard_grafana.py platform_tests\scripts\test_gtkb_dashboard_clean_checkout.py platform_tests\scripts\test_update_wiki_pages.py -q --tb=short
```

Observed result: `33 passed in 35.37s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\gtkb_dashboard\refresh_dashboard_db.py scripts\gtkb_dashboard\generate_grafana_dashboard.py scripts\update_wiki_pages.py platform_tests\scripts\test_gtkb_dashboard_grafana.py platform_tests\scripts\test_gtkb_dashboard_clean_checkout.py platform_tests\scripts\test_update_wiki_pages.py
```

Observed result: `All checks passed!`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\gtkb_dashboard\refresh_dashboard_db.py scripts\gtkb_dashboard\generate_grafana_dashboard.py scripts\update_wiki_pages.py platform_tests\scripts\test_gtkb_dashboard_grafana.py platform_tests\scripts\test_gtkb_dashboard_clean_checkout.py platform_tests\scripts\test_update_wiki_pages.py
```

Observed result: `6 files already formatted`.

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\gtkb_dashboard\refresh_dashboard_db.py --db-path .tmp\gtkb-dashboard-live-probe-impl.sqlite --project-root E:\GT-KB --probe-live
```

Observed result: completed successfully with run id `1`, started `2026-06-30T22:11:26.129475+00:00`, completed `2026-06-30T22:12:17.930754+00:00`.

## Live Dashboard DB Evidence

Querying `.tmp\gtkb-dashboard-live-probe-impl.sqlite` after the live refresh showed:

- `current_metrics.release_blockers = 3/red`.
- `current_metrics.release_health_findings = 3/red`.
- `current_metrics.dirty_worktree_paths = 318/red` with description `Changed paths from live git status; release prep must classify dirty paths before push.`
- `health_cards.Project Health = 3 issues/red`.
- `health_cards.Release Readiness = 3 blockers/red`.
- `integration_status.github = green/passing`; latest summary was `Dependabot Updates: status=completed conclusion=success created_at=2026-06-30T14:04:39Z`.
- `integration_status.dispatcher_supervisor = green/healthy_headless`; latest summary was `registered=True enabled=True hidden=True uses_pythonw=True healthy=True`.
- `release_blockers` still surfaced the real unresolved release blockers:
  - dirty worktree classification required before release commit/push.
  - dispatcher health WARN for `loyal-opposition:F` route/circuit breaker/max-turn exhaustion.
  - bridge dispatch pending/live in-flight work.

## Acceptance Criteria Status

- [x] Health cards now reconcile against visible release blockers and cannot stay green/zero while current metrics and release blocker rows are red.
- [x] Live dirty worktree count is available to current metrics during live probes and overrides stale startup-model drift count.
- [x] GitHub CLI auth environment is restored after startup-model collection before workflow live probing.
- [x] Supervisor health is displayed separately from dispatcher route/runtime WARNs.
- [x] Provider-neutral deployment mock rows and opt-in Azure reconciliation were preserved.
- [x] Dispatcher route/runtime failures remain out of scope and visible as release blockers.

## Residual Risk And Rollback

Residual release risk remains outside this dashboard slice: `gt bridge dispatch health --json` still reports WARN for Loyal Opposition route reliability (`F` circuit breaker/max-turn exhaustion and `D` worker timeout), and the live dashboard correctly keeps those findings red.

Rollback is a one-commit revert of the two changed files listed in Scope Actually Changed. The bridge proposal, GO verdict, and this implementation report remain append-only governance evidence.

## Loyal Opposition Asks

1. Verify that the dashboard rows/cards/metrics now agree with live release-health evidence.
2. Confirm that the implementation did not add Azure or other deployment-provider coupling.
3. Confirm that dispatcher route/runtime WARNs remain visible and were not misrepresented as fixed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
