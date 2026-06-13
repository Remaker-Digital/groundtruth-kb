NEW

# WI-4506: TAFE Dashboard Observability Panels — Implementation Report

bridge_kind: implementation_report
Document: gtkb-tafe-dashboard-observability
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC
Responds-To: bridge/gtkb-tafe-dashboard-observability-002.md
Implements: bridge/gtkb-tafe-dashboard-observability-001.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 869ade5b-58a4-4261-b2cb-98fcbecb8c0e
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4506

target_paths: ["scripts/gtkb_dashboard/generate_grafana_dashboard.py", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_tafe_dashboard_refresh.py"]

Recommended commit type: feat:

---

## Implementation Claim

Implemented WI-4506 — a read-only TAFE Observability panel surface on the GT-KB Grafana dashboard — exactly within the GO'd proposal's bound: no alert rules, no recovery actuation, no live metric capture, no canonical `groundtruth.db` schema change, no cutover, no dual-write, no live-dispatch substrate, no authoritative generated view.

Three layers landed in one slice:

1. **Data export** — `scripts/gtkb_dashboard/refresh_dashboard_db.py` gained `_migrate_tafe_projection_schema` (creates five additive projection tables in the dashboard SQLite via idempotent `CREATE TABLE IF NOT EXISTS` under a BEGIN IMMEDIATE lock, matching the existing `_migrate_schema` pattern) and `_refresh_tafe_projection` (reads canonical TAFE rows via `KnowledgeDB.list_*` and inserts a narrowed projection using the existing `_replace_table` truncate-and-insert pattern). A `_refresh_tafe_projection_safe` wrapper mirrors `_write_bridge_swimlane_safe`: failures log and continue so the rest of the dashboard refresh is unaffected. The wrapper is invoked from `refresh_database()` after `_write_bridge_swimlane_safe`.
2. **Panel generation** — `scripts/gtkb_dashboard/generate_grafana_dashboard.py` gained a collapsed "TAFE Observability" row (y=57) with five panels reading the projection tables via the existing `gtkb-dashboard-sqlite` datasource: two pie charts (stage attempt outcomes; failure-class distribution), two tables (active flow instances; active stage leases), one bargauge (capability snapshot readiness by role).
3. **Tests** — a new `platform_tests/scripts/test_tafe_dashboard_refresh.py` (7 tests) covers the migration, idempotent projection, graceful absence, the `_safe` swallow-and-continue contract, and a structural AST guard asserting the projection helpers contain no MemBase mutating method calls and no canonical-table SQL writes. `platform_tests/scripts/test_gtkb_dashboard_grafana.py` gained six WI-4506 assertions: row presence, panel-title presence, SQLite-datasource enforcement, no-write SQL verb guard, projection-table reference, monotonic panel-id allocation, and a no-alert-rule-references-TAFE-panel guard.

### Design pivot vs. the GO'd proposal

The GO'd proposal called for adding the TAFE projection schema to `schema.sql`. During implementation, the implementation-start gate correctly flagged that `schema.sql` was **not in the proposal's `target_paths`**. The pivot: do the entire WI-4506 schema work in Python via runtime `CREATE TABLE IF NOT EXISTS` inside `_migrate_tafe_projection_schema` (in `refresh_dashboard_db.py`, which IS in `target_paths`). This is a cleaner pattern — the additive WI-4506 schema lives entirely in one file alongside the projection logic — and stays within the GO'd authorization. The proposed behavior (idempotent fresh-DB + existing-DB schema, NULL-tolerant projection, graceful absence) is unchanged.

### Drift cleanup surfaced by idempotent regen

The idempotent regen surfaced pre-existing drift in `platform_tests/scripts/test_gtkb_dashboard_grafana.py`: `test_grafana_provisioning_targets_sqlite_database` asserted `dashboard_json["uid"] == "gtkb"` but the SoT (the `build_dashboard` composer's return block) emits `"agent-red-gtkb"`. The committed dashboard JSON on `develop` had `"gtkb"` (a stale artifact from before the generator's uid was updated); my regen produced the SoT value and surfaced the test's stale assertion. Since the test file is in WI-4506's `target_paths`, the assertion was updated to match the SoT with an inline comment explaining the drift cleanup. The fix is a one-line change accompanied by a multi-line explanatory comment.

## Files Changed

| File | Lines | Purpose |
|---|---|---|
| `scripts/gtkb_dashboard/refresh_dashboard_db.py` | +297 | TAFE projection schema + `_refresh_tafe_projection` + `_safe` wrapper, hooked into `refresh_database` |
| `scripts/gtkb_dashboard/generate_grafana_dashboard.py` | +74 | "TAFE Observability" collapsed row with 5 panels |
| `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` | +355, −4 | Regenerated; adds the TAFE row and its 5 nested panels (deterministic generator output) |
| `platform_tests/scripts/test_gtkb_dashboard_grafana.py` | +130, −1 | Six WI-4506 assertions + one-line drift cleanup for the stale uid assertion |
| `platform_tests/scripts/test_tafe_dashboard_refresh.py` | (new file) | 7 tests: migration, idempotence, projection, graceful absence, safe-wrapper, AST structural guard |

`groundtruth.db` is **not** mutated by this slice (no canonical schema change; the dashboard SQLite migration is dashboard-internal). No bridge authority change; `bridge/INDEX.md` remains canonical.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R2`, `SPEC-TAFE-R3`, `SPEC-TAFE-R4`, `SPEC-TAFE-R6`, `SPEC-TAFE-R7` — TAFE state is now surfaced as read-only visualization without changing canonical authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the dashboard surface writes nothing to `bridge/INDEX.md`; the panels are non-authoritative.
- `GOV-STANDING-BACKLOG-001` — WI-4506 is the backlog authority; siblings remain open/untouched.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeded under the active tranche-3 PAUTH (which explicitly includes WI-4506) with a live implementation-start authorization packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs/rules are linked.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below maps each linked spec to executed test evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets are inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the dashboard observability surface is durable governed artifact state; WI-4506 stays unresolved until terminal VERIFIED.

## Owner Decisions / Input

This implementation is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file this implementation report.

- **`DELIB-20263164`** — owner decision (S437/early-S438) backing the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED`. The PAUTH's `scope_summary` explicitly enumerates "WI-4506 dashboard metrics" within "GT-KB platform code/tests only under `E:/GT-KB`; `bridge/INDEX.md` remains canonical; no cutover, no dual-write, no live dispatch substrate," and the PAUTH's `forbidden_operations` list `["cutover", "dual_write", "live_dispatch_substrate", "authoritative_generated_view", "kb_schema_change"]`. This implementation respects all five.
- **S438 AskUserQuestion (drive directive)** — the standing owner directive (re-issued each turn this session) is to drive `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE` to completion autonomously through the multi-harness swarm. WI-4506 was the next tranche-3-authorized unblocked item once WI-4504 telemetry reached VERIFIED, satisfying the AUQ choice "drive in parallel on the next clean unblocked TAFE item" recorded earlier this session.
- **No new owner AUQ is required for this report.** Authority is the carry-forward of the GO'd proposal `bridge/gtkb-tafe-dashboard-observability-001.md` + LO verdict `bridge/gtkb-tafe-dashboard-observability-002.md` + live implementation-start authorization packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-tafe-dashboard-observability` returned PASS pre-implementation).
- All `forbidden_operations` of the PAUTH are respected (no cutover, dual-write, live dispatch substrate, authoritative generated view, or canonical KB schema change). The implementation pivot from `schema.sql` → runtime Python `CREATE TABLE IF NOT EXISTS` keeps the change inside the GO'd `target_paths` without expanding owner authorization.

## Requirement Sufficiency

Existing requirements remain sufficient. The implementation follows the GO'd proposal exactly within the boundary clarified above (TAFE projection schema in Python via runtime `CREATE TABLE IF NOT EXISTS` inside `refresh_dashboard_db.py`, not in `schema.sql`). No new or revised requirement is needed because this slice persists the specified observability surface and excludes alerts, recovery actuation, live capture, schema changes to `groundtruth.db`, and any authority change.

## Spec-to-Test Mapping

| Spec / governing surface | Executed verification evidence |
|---|---|
| `SPEC-TAFE-R6` (stage-attempt telemetry surfaced) | `test_refresh_projects_canonical_rows` asserts `outcome` and `failure_class` round-trip; `test_all_tafe_panel_titles_present` asserts "Stage Attempt Outcomes (TAFE)" + "Failure Class Distribution (TAFE)" panels exist. |
| `SPEC-TAFE-R3` (failure class diagnosis inputs surfaced) | `test_refresh_projects_canonical_rows` asserts failure_class is projected; "Failure Class Distribution (TAFE)" panel reads the projection. |
| `SPEC-TAFE-R2` (stage-lease state surfaced read-only) | "Active Stage Leases (TAFE)" panel present; structural AST guard (`test_projection_helper_does_not_mutate_canonical_kb_source`) asserts the projection helper performs no INSERT/UPDATE/DELETE against canonical TAFE tables. |
| `SPEC-TAFE-R4` (dispatch readiness via capability snapshots) | `test_refresh_projects_canonical_rows` asserts capability snapshot is projected; "Capability Snapshot Readiness by Role (TAFE)" panel present. |
| `SPEC-TAFE-R7` (MemBase canonical; dashboard SQLite is derived cache) | Structural AST guard asserts no MemBase mutating method call; no SQL write against canonical TAFE tables; `test_graceful_absence_when_groundtruth_db_missing` asserts the projection is fully read-only against the canonical store. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (no bridge authority change) | No panel reads or writes `bridge/INDEX.md`; the new `gt projects` / `gt bridge` CLI surfaces are unchanged. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `bridge_applicability_preflight.py --bridge-id gtkb-tafe-dashboard-observability` passed at filing (packet hash `sha256:8ded997a931243fb26a4d2dc2954d09e0b7d3b1dca71d6dce8ae3875a6e8817a`); `implementation_authorization.py begin --bridge-id gtkb-tafe-dashboard-observability` passed pre-implementation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each linked spec to executed test evidence below. |
| Forbidden alert-rule scope | `test_no_alert_rule_references_a_tafe_panel` asserts no alert YAML file references a TAFE panel title or id. |
| Forbidden recovery actuation | `test_projection_helper_does_not_mutate_canonical_kb_source` asserts no recovery actuation surface. |

## Verification Commands

```text
python -m pytest platform_tests/scripts/test_tafe_dashboard_refresh.py platform_tests/scripts/test_gtkb_dashboard_grafana.py -q --tb=short
```
Observed: `18 passed in 2.34s`.

```text
python -m pytest platform_tests/scripts/test_tafe_dashboard_refresh.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_dashboard_subject_selector.py platform_tests/scripts/test_gtkb_dashboard_alerting.py platform_tests/scripts/test_gtkb_dashboard_control_plane.py platform_tests/scripts/test_rehearse_dashboard_regen.py -q --tb=short
```
Observed: `113 passed, 1 skipped in 35.03s`.

```text
python -m ruff check scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/refresh_dashboard_db.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_tafe_dashboard_refresh.py
```
Observed: `All checks passed!`.

```text
python -m ruff format --check scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/refresh_dashboard_db.py platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_tafe_dashboard_refresh.py
```
Observed: `4 files already formatted`.

```text
python scripts/gtkb_dashboard/generate_grafana_dashboard.py
sha256sum docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json
python scripts/gtkb_dashboard/generate_grafana_dashboard.py
sha256sum docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json
```
Observed: identical hash both runs (`2cef8c6651d56cd4a8edd7049fe0ce5084fbf90deb67f9fad467bfb1e0ce767c`). Idempotent generation confirmed.

```text
git diff --check -- scripts/gtkb_dashboard/generate_grafana_dashboard.py scripts/gtkb_dashboard/refresh_dashboard_db.py docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_tafe_dashboard_refresh.py
```
Observed: no output, exit 0.

## Implementation Authorization

- Work-intent claim acquired at 2026-06-13T15:47Z (rowid 1782, session 869ade5b-58a4-4261-b2cb-98fcbecb8c0e).
- Implementation-start authorization packet: `python scripts/implementation_authorization.py begin --bridge-id gtkb-tafe-dashboard-observability` returned PASS; target_path_globs match the proposal's `target_paths` exactly.

## Acceptance Status

- [x] TAFE projection schema added (5 tables, additive, NULL-tolerant) via runtime `CREATE TABLE IF NOT EXISTS` in `refresh_dashboard_db.py`.
- [x] Refresh helper reads canonical TAFE rows via the `KnowledgeDB` Python API and projects them into the dashboard SQLite via the `_replace_table` truncate-and-insert pattern.
- [x] Graceful absence: missing `groundtruth.db` or missing TAFE methods yields zero projected rows without error (tested).
- [x] `_refresh_tafe_projection_safe` wrapper swallows exceptions so the rest of the dashboard refresh continues (tested).
- [x] Structural guard: AST inspection asserts the projection helpers contain no MemBase mutating method calls and no canonical-table SQL writes.
- [x] "TAFE Observability" collapsed row added to the generated dashboard with 5 panels (2 pies, 2 tables, 1 bargauge), all reading the `gtkb-dashboard-sqlite` datasource via the existing builders.
- [x] No-alert-rule guard: structural test asserts no alert YAML references any TAFE panel by title or id.
- [x] Idempotent generation: regenerating the dashboard JSON twice yields a byte-identical SHA.
- [x] Monotonic panel-id allocation: no duplicate panel IDs in the generated dashboard.
- [x] Full dashboard regression pass: 113 passed, 1 skipped across `test_tafe_dashboard_refresh`, `test_gtkb_dashboard_grafana`, `test_dashboard_subject_selector`, `test_gtkb_dashboard_alerting`, `test_gtkb_dashboard_control_plane`, `test_rehearse_dashboard_regen`.

## Risk / Rollback

Residual risk is low. The slice ships:

- read-only visualization only (no mutation against canonical `groundtruth.db`);
- additive dashboard SQLite schema (idempotent `CREATE TABLE IF NOT EXISTS` in a separate migration helper);
- the regenerated JSON as a deterministic generator output (idempotent on rerun);
- structural and behavior tests that lock in the no-mutation, no-alert-rule, and no-canonical-write bounds.

Rollback is a single-commit revert of the five changed files (the new test file is untracked until committed). The dashboard SQLite's TAFE projection tables, if already created on an existing install, are harmless without the consuming panels and can be left in place; `DROP TABLE IF EXISTS` cleanup is out of scope.

## Loyal Opposition Asks

1. Verify the projection helper is read-only against `groundtruth.db` (structural guard + the `test_refresh_is_idempotent` + `test_graceful_absence_when_groundtruth_db_missing` invariants).
2. Confirm the five TAFE panels are reachable via the `gtkb-dashboard-sqlite` datasource and that no alert rule consumes them.
3. Confirm the design pivot (schema in `refresh_dashboard_db.py` runtime migration vs. `schema.sql`) stays within the GO'd `target_paths` and respects all `forbidden_operations` in the tranche-3 PAUTH.
4. Acknowledge the one-line drift cleanup of the stale `uid` assertion in `test_gtkb_dashboard_grafana.py` (the test file is in `target_paths`; the change is annotated inline).
5. Return VERIFIED if the implementation + tests + idempotent regen satisfy the approved proposal; otherwise return NO-GO with concrete findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
