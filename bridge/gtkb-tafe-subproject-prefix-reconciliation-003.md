NEW

# TAFE Subproject Prefix Reconciliation Implementation Report

bridge_kind: implementation_report
Document: gtkb-tafe-subproject-prefix-reconciliation
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC
Responds-To: bridge/gtkb-tafe-subproject-prefix-reconciliation-002.md
Implements: bridge/gtkb-tafe-subproject-prefix-reconciliation-001.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ec000-83c6-72f3-9351-69d7afb8bdde
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop automation run; approval_policy=never; danger-full-access filesystem

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4511

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cli_projects_reconcile.py", "groundtruth.db"]

---

## Implementation Claim

Implemented WI-4511 by generalizing the existing deterministic `gt projects reconcile-doubled-prefix` service and applying it to the TAFE project scope.

The service now detects doubled leading project-id segments structurally instead of only matching the literal `PROJECT-PROJECT-*` prefix. The old literal constant and old behavior remain covered by tests. A new `--project` option scopes reconciliation to phantoms whose canonical id is the requested project id or a child id, which allowed the live TAFE cleanup to avoid a global reconciliation pass.

The live scoped apply reconciled the TAFE duplicate sub-project rows in `groundtruth.db`:

- 8 TAFE phantom sub-projects retired.
- 24 live work-item memberships re-linked to canonical TAFE sub-project rows.
- 24 phantom work-item memberships superseded.
- A second scoped apply made zero writes, confirming idempotence.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` - replaced literal-prefix-only detection with structural repeated-leading-segment detection, added project-scope filtering to the request/report path, and preserved the existing append-only relink/supersede/retire algorithm.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - added `--project` to `gt projects reconcile-doubled-prefix` and updated CLI help text for generalized doubled-segment reconciliation.
- `platform_tests/scripts/test_cli_projects_reconcile.py` - added WI-4511 coverage for TAFE-style doubled parent prefixes and project-scoped apply behavior, while preserving WI-3355 `PROJECT-PROJECT-*` regression coverage.
- `groundtruth.db` - live MemBase data reconciliation: canonical TAFE sub-project memberships inserted, phantom memberships superseded, and phantom TAFE sub-project rows retired. The database is an ignored local canonical store and is not staged as a Git blob.

Recommended commit type: `fix:`

## Specification Links

- `GOV-STANDING-BACKLOG-001` - WI-4511 is the backlog authority for this cleanup.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state remains governed by `bridge/INDEX.md`; the runtime service does not write the index.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation used the active tranche-3 PAUTH plus the live latest `GO`.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the cleanup is delivered by a deterministic, idempotent service instead of a one-shot row edit script.
- `SPEC-TAFE-R7` - MemBase remains canonical for project/backlog state; no generated authority or markdown authority is introduced.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries PAUTH, project, work item, target paths, and bridge linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps the generalized detection, scoped apply, idempotence, and data outcome to tests and read-back commands.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all code, tests, and live database mutation are inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation preserves durable MemBase artifact history through append-only canonical memberships, phantom membership supersessions, retired phantom project rows, and bridge verification handoff.

## Owner Decisions / Input

No new owner decision was required. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-TRANCHE-3-PHASE-2-OBSERVABILITY-HYGIENE-WI-4504-4505-4506-4507-4511-CUTOVER-EXCLUDED`, backed by `DELIB-20263164`, and the live `GO` at `bridge/gtkb-tafe-subproject-prefix-reconciliation-002.md`.

The implementation did not perform cutover, dual-write, live dispatch substrate work, generated-authority promotion, or schema changes.

## Requirement Sufficiency

Existing requirements remain sufficient. The implementation follows the approved proposal exactly: generalize detection, add a project scope filter, preserve the reconciliation algorithm, run scoped apply for `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`, and prove idempotence plus read-back. No new or revised requirement was needed.

## Spec-To-Test Mapping

- Structural doubled-prefix detection: `test_canonical_id_derivation_strips_exactly_one_prefix` now covers both `PROJECT-PROJECT-*` and TAFE parent-segment duplication.
- Scope filter: `test_project_scoped_plan_detects_tafe_subproject_phantom_only` verifies `--project` planning finds the TAFE phantom and excludes seeded global phantoms.
- Scoped apply safety: `test_project_scoped_apply_reconciles_tafe_without_touching_global_phantoms` verifies the TAFE phantom is reconciled while old global phantoms remain untouched.
- Existing WI-3355 behavior: the original ten tests still cover dry-run no-write behavior, active and retired canonical relink, redundant canonical membership skip, phantom membership supersession, phantom retirement, idempotence, JSON shape, and missing-canonical skip.
- Live MemBase data outcome: read-back script verified 8 TAFE phantom rows are retired, TAFE phantom active memberships are 0, and TAFE canonical active memberships are 24.

## Verification Commands

```text
python -m pytest platform_tests/scripts/test_cli_projects_reconcile.py -q --tb=short
```

Observed result: `13 passed in 6.42s`.

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cli_projects_reconcile.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cli_projects_reconcile.py
```

Observed result: `3 files already formatted`.

```text
git diff --check -- groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_cli_projects_reconcile.py
```

Observed result: no whitespace errors; exit 0.

```text
python scripts/check_dev_environment_inventory_drift.py --changed-path groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py --changed-path groundtruth-kb/src/groundtruth_kb/cli.py --changed-path platform_tests/scripts/test_cli_projects_reconcile.py
```

Observed result: `Inventory drift check: PASS (clean)`.

```text
python -m groundtruth_kb projects reconcile-doubled-prefix --project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --apply --json
```

Observed first apply totals: `phantom_count=8`, `canonical_links_created=24`, `phantom_memberships_superseded=24`, `phantom_projects_retired=8`, `skipped_count=0`.

Observed second apply totals: `phantom_count=8`, `canonical_links_created=0`, `phantom_memberships_superseded=0`, `phantom_projects_retired=0`, `skipped_count=0`.

```text
DB read-back script over groundtruth.db
```

Observed result: `tafe_phantom_count=8`, `tafe_phantom_statuses=['retired']`, `tafe_phantom_active_memberships=0`, `tafe_canonical_active_memberships=24`.

## Acceptance Status

Accepted for Loyal Opposition verification. The implementation is bounded to WI-4511, preserves the deterministic reconciliation service, and leaves cutover, dual-write, live-dispatch substrate, generated authority, and schema changes out of scope.

## Risk / Rollback

Primary risk is overmatching repeated project-id segments. The detector only targets ids with a repeated leading `*-` segment, planning still requires a canonical counterpart to proceed, tests cover the TAFE case and the old literal case, and the live apply was bounded by `--project PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`.

Rollback for code/test changes is a normal commit revert. The live MemBase cleanup is append-only: canonical links, phantom membership supersessions, and phantom project retirements are preserved as history rows. Reversing the data outcome would require a separate governed corrective reconciliation rather than deleting rows.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
