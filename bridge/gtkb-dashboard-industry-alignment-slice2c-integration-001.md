NEW

# Slice 2.3 (integration): default Grafana alert notifier (alert-list-only) + CI-integration disposition

bridge_kind: prime_proposal
Document: gtkb-dashboard-industry-alignment-slice2c-integration
Version: 001
Author: Prime Builder (Claude Opus 4.8, harness B)
Date: 2026-06-22 UTC

author_identity: prime-builder/claude-opus-4-8
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: opus-4.8
author_model_configuration: interactive Prime Builder, 1m context

Project Authorization: PAUTH-PROJECT-GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION-AUTHORIZE-SLICE-2-3-NOTIFIER-WIRING-IMPLEMENTATION
Project: PROJECT-GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION
Work Item: GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION

target_paths: ["docs/gtkb-dashboard/grafana/provisioning/alerting/contact-points.yaml", "docs/gtkb-dashboard/grafana/provisioning/alerting/notification-policies.yaml", "platform_tests/scripts/test_gtkb_dashboard_alerting.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal completes **Slice 2.3 (integration)** of `GTKB-DASHBOARD-002`, the
final sub-slice of the dashboard industry-alignment program. It is filed **fresh**
to supersede the stale April umbrella (`gtkb-dashboard-industry-alignment-slice2`,
NO-GO at `-002`): current GT-KB target paths, current `platform_tests/scripts/`
test location, no dependency on the removed `bridge/INDEX.md`, and concrete
specification linkage.

Slice 2.3 had two declared deliverables. Their disposition after live-state
investigation:

1. **Notifier wiring (implemented here).** The Grafana alerting provisioning dir
   (`docs/gtkb-dashboard/grafana/provisioning/alerting/`) holds three alert
   *rules* (`failing-ci.yaml`, `release-blockers.yaml`, `stale-data.yaml`) but
   **no contact point and no notification policy** — the rules have no defined
   routing target. This proposal adds a default contact point and a root
   notification policy. Per owner decision **DELIB-20265567** (AskUserQuestion,
   2026-06-22), the default is **alert-list-only**: firing alerts surface in the
   Grafana Alerting UI with **no external delivery** and **no committed delivery
   secret**. External channels (email/Slack/Teams) remain opt-in via env.local.

2. **CI workflow embed (already satisfied — no new code).** The CI-status
   integration is already covered by existing surfaces: the `integration_status`
   table (fed from `testing_service_integrations` in `refresh_dashboard_db.py`),
   the `ci_testing_failing` `current_metrics` key, the `failing-ci.yaml` alert
   rule, the GitHub Actions `third_party_services` row, and `workflow_run`
   delivery-timeline events. **No new `ci_runs` table is introduced.** This is
   the disposition the Slice-2 review's F2 condition asked for ("justify any new
   `ci_runs` persistence against existing `testing_service_integrations`"): the
   justification is that the existing surfaces already cover CI status, so a new
   persistence table would be redundant.

No `src/` runtime code, no schema change, no `refresh_dashboard_db.py` change,
no Grafana dashboard JSON change. The change surface is two provisioning YAML
files plus the alerting test module.

## Specification Links

- `SPEC-GTKB-DASHBOARD-ALERT-NOTIFIER-001` — **primary.** Requires the dashboard
  to provision a default Grafana alert notifier (contact point + root policy)
  with an alert-list-only default and no committed delivery secret. This proposal
  implements that requirement; tests derive directly from its "Provisioning shape"
  and "External channels are opt-in" clauses.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` — governs the GT-KB operations dashboard
  surface (`docs/gtkb-dashboard/**`) that the alert notifier is part of; the
  notifier ensures the dashboard's alert rules have a defined route.
- `GOV-SESSION-SELF-INITIALIZATION-001` — the dashboard is a governed
  session-initialization surface; its operational-visibility alerting must be
  routable.
- `GOV-ENV-LOCAL-AUTHORITY-001` — governs the opt-in path: any future external
  notifier channel's webhook/SMTP config is supplied via env.local, not committed
  to the provisioning YAML.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority for this filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: every
  relevant governing spec is cited above.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project +
  Work Item + Project Authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the
  spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — work item `GTKB-DASHBOARD-002-SLICE-2-3-INTEGRATION`
  is the governing backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — this slice advances durable artifacts
  (spec, provisioning files, derived tests) over transient conversation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the work is captured as
  spec + bridge thread + tests, not ad-hoc edits.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching the previously-unspecified
  notifier surface triggered specify-on-contact (`SPEC-GTKB-DASHBOARD-ALERT-NOTIFIER-001`).

## Prior Deliberations

- `DELIB-20265567` — **owner decision (this slice's gate):** notifier default =
  "None — alert-list only". This proposal implements exactly that selection.
- `DELIB-1000` — Slice 1 GO: established the dashboard alerting rule skeleton
  (`failing-ci`/`release-blockers`/`stale-data`) this proposal routes.
- `DELIB-0999` — Slice 1 VERIFIED: confirmed the alerting-rule provisioning that
  this slice completes by adding the missing contact point + policy.
- `DELIB-20261035` — Dashboard Operations Cockpit advisory (Codex LO): context on
  the operations-dashboard direction; this proposal stays within the existing
  surface and adds no new ingest.

This proposal does **not** revisit any previously-rejected approach. It
explicitly retires the stale `gtkb-dashboard-industry-alignment-slice2` umbrella
(NO-GO `-002`) by filing fresh per that NO-GO's own required action ("file fresh
slice proposals with current specification links, current GT-KB target paths, and
no dependency on `bridge/INDEX.md`").

## Owner Decisions / Input

This proposal depends on one owner decision, recorded via AskUserQuestion:

- **DELIB-20265567** (AUQ `AUQ-2026-06-22-DASHBOARD-002-SLICE-2-3-NOTIFIER-DEFAULT`,
  answer: **"None — alert-list only"**). The owner selected the alert-list-only
  notifier default over email/Slack/Teams. This is the sole gating decision; it
  is formalized as `SPEC-GTKB-DASHBOARD-ALERT-NOTIFIER-001` and authorized for
  implementation by `PAUTH-...-NOTIFIER-WIRING-IMPLEMENTATION`.

No further owner decision is required to implement the alert-list-only default.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirement
`SPEC-GTKB-DASHBOARD-ALERT-NOTIFIER-001` (status `specified`) was captured via
specify-on-contact directly from owner decision `DELIB-20265567`, and fully
defines the provisioning shape (contact point + root policy), the alert-list-only
default, and the no-committed-secret constraint. Supporting governance
(`SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `GOV-SESSION-SELF-INITIALIZATION-001`,
`GOV-ENV-LOCAL-AUTHORITY-001`) is already in force. No new or revised requirement
is needed before implementation.

## Spec-Derived Verification Plan

All tests run with the repo venv interpreter:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dashboard_alerting.py -q --no-header
```

Spec-to-test mapping (`SPEC-GTKB-DASHBOARD-ALERT-NOTIFIER-001`):

| Spec clause | Test (new in `test_gtkb_dashboard_alerting.py`) | Expected |
|---|---|---|
| Provisioning shape (1): contact-points.yaml defines a default contact point | `test_notifier_contact_points_present_and_parse` | file exists, `apiVersion == 1`, `contactPoints[0].name == "gtkb-default"` |
| Provisioning shape (2): root policy references the contact point | `test_notifier_policy_root_receiver_matches_contact_point` | `notification-policies.yaml` parses, `policies[0].receiver == "gtkb-default"` |
| Provisioning shape (3): Grafana v1 docs with required keys | `test_notifier_yamls_are_grafana_v1` | both docs `apiVersion == 1`; contact-points has `contactPoints`, policies has `policies` |
| External channels opt-in / no committed delivery secret | `test_notifier_default_has_no_external_delivery_secret` | no `http(s)://` webhook URL and no `password`/`token`/`secret`/`apiKey` key in either YAML |

Non-regression for the existing alert-rule tests (mixed-YAML hardening):

| Risk | Test change | Expected |
|---|---|---|
| Existing `*.yaml`-globbing tests misparse the new non-rule YAMLs | `test_alert_queries_use_nonzero_relative_time_range` and `test_every_alert_sql_references_only_tables_in_schema` updated to skip docs without a `groups` key (alert-rule docs only) | both still pass; new provisioning YAMLs are correctly excluded from rule-shape assertions |
| All three rule YAMLs still present/valid | `test_all_three_alert_yamls_present_and_parse` (unchanged) | pass |
| Pipeline still emits the alert metric keys | `test_refresh_pipeline_actually_emits_the_alert_metric_keys` (unchanged) | pass |

Code-quality gates on the changed test file:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_gtkb_dashboard_alerting.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_gtkb_dashboard_alerting.py
```

Expected: clean (lint + format).

## Risk / Rollback

Risk surface is low: two additive Grafana provisioning YAML files and a test
module update. No runtime/source code, no schema, no DB refresh path, no Grafana
dashboard JSON. The only cross-file risk is the existing `*.yaml`-globbing alert
tests, explicitly hardened above so the new non-rule YAMLs are excluded from
rule-shape assertions.

The alert-list-only default commits no delivery secret and reaches no external
service, so there is no credential or external-auth exposure. Single-commit
rollback: revert the one commit containing the two YAMLs and the test change;
the dashboard returns to its current (no-contact-point) state with no residue.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-dashboard-industry-alignment-slice2c-integration`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` — net-new dashboard capability (the alert notifier routing surface) plus
its derived tests. Two new provisioning files establish behavior that did not
previously exist.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
