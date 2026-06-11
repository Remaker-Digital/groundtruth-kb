NEW

bridge_kind: prime_proposal
Document: gtkb-fab-02-secrets-remediation
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4414
Project Authorization: PAUTH-FAB02-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 4490dc1a-faa5-401f-968c-670bf2c915b5
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".driveignore", ".gitignore", "infrastructure/terraform/backend.tf", "infrastructure/terraform/backend.hcl.example", "infrastructure/terraform/STATE-MIGRATION-RUNBOOK.md", "infrastructure/terraform/CREDENTIAL-ROTATION-OWNER-ACTION.md", "infrastructure/terraform/terraform.tfstate.backup", "infrastructure/terraform/terraform.tfstate.1774985892.backup", "scripts/hygiene/secret_at_rest_guard.py", "platform_tests/scripts/test_secret_at_rest_guard.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py"]

---

# FAB-02 — Post-Implementation Report (secret-at-rest remediation)

Implementation report for `gtkb-fab-02-secrets-remediation`, GO at
`bridge/gtkb-fab-02-secrets-remediation-002.md`. WI-4414 (FAB-02) of
PROJECT-FABLE-INVESTIGATION; findings HYG-019, HYG-020. Implemented by Prime
Builder harness B (Opus 4.8) under impl-start packet
`sha256:b8a0a4c0622a8a79c781e66005b399e36c0b82c469af9c6f907ec9679405a7c2`
(created from the live `GO`; expires 2026-06-11T10:54:03Z).

## Summary

The Prime-implementable, value-safe slice of HYG-019/020 is complete: the
secret-bearing files are excluded from Google-Drive replication, the two stale
tfstate backups are deleted, the azurerm partial-config backend + owner runbook
are scaffolded, the credential-rotation owner-action record (names only) is
written, and a value-safe regression guard + test encode the invariants. The
owner-only follow-ups (credential rotation, live-state migration, SyncBackSE
profile edit, terraform/ relocation) are recorded as tracked actions and do not
gate `VERIFIED` (grill-C decision).

## Specification Links

Carried forward from `-001` (GO'd):

- `GOV-ENV-LOCAL-AUTHORITY-001` — `.env.local` is the credential SoT; HYG-020 is
  a replication-surface gap against it (now closed in `.driveignore`).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs
  cited (carried forward).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping +
  command evidence below satisfy this gate.
- `GOV-STANDING-BACKLOG-001` — WI-4414 is the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `infrastructure/terraform/` is
  Agent-Red application infra at the platform root; this work secures secrets at
  rest only and introduces no out-of-placement artifacts. Directory relocation
  remains deferred to FAB-12 (pinned by the live test
  `applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py:45`).

## Isolation Placement Compliance

All changed and created artifacts remain within the GT-KB root `E:\GT-KB`:
edits/additions under `infrastructure/terraform/`, `scripts/hygiene/`,
`platform_tests/scripts/`, and the root `.driveignore`/`.gitignore`. No file was
created outside `infrastructure/terraform/` placement, and the directory was NOT
relocated (relocation is FAB-12 under `ADR-ISOLATION-APPLICATION-PLACEMENT-001`).
No out-of-root dependency was created or required.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory
  (HYG-019/020 in the FAB-02 row).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB02-REMEDIATION-20260610` — this cluster's consolidated owner-decision
  set (carried forward; unchanged).
- `bridge/gtkb-fab-02-secrets-remediation-002.md` — the GO with implementation
  constraints honored below.

## Owner Decisions / Input

The implemented choices were collected via `AskUserQuestion` on 2026-06-10 and
persisted to `DELIB-FAB02-REMEDIATION-20260610` (carried forward verbatim from
`-001`): full HYG-019 remediation; exclude-from-both for HYG-020; reuse existing
backend (partial-config + gitignored `backend.hcl` + runbook); owner-executed
migration; rotation as tracked follow-up (does not gate `VERIFIED`); narrow
regression-guard detector. The `GO` at `-002` is the per-cluster implementation
authorization moment (PAUTH-FAB02 records bridge GO as the authorization point).

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). No new or revised
requirement was needed; the guard encodes an invariant derived from the linked
specs. If Loyal Opposition judges the invariant warrants a formal
protected-behavior spec, that is a reviewer-surfaced follow-up, not a blocker.

## Files Changed

**Modified (2):**

- `.driveignore` — added the secret-at-rest replication exclusions
  (`.env.local`, `.env*` with `!*.example` re-include, `*.tfstate`,
  `*.tfstate.*`, `*.tfvars`, `infrastructure/terraform/.terraform/`).
- `.gitignore` — added `infrastructure/terraform/backend.hcl` (the tracked
  `.example` template stays committed).

**Created (6):**

- `infrastructure/terraform/backend.tf` — partial `terraform { backend "azurerm" {} }`
  block (no identifiers/secrets).
- `infrastructure/terraform/backend.hcl.example` — template enumerating
  `resource_group_name` / `storage_account_name` / `container_name` / `key`.
- `infrastructure/terraform/STATE-MIGRATION-RUNBOOK.md` — owner runbook for
  `terraform init -migrate-state` + post-migration local-state cleanup.
- `infrastructure/terraform/CREDENTIAL-ROTATION-OWNER-ACTION.md` — tracked
  owner-action record listing the 6 exposed value **names** (no values).
- `scripts/hygiene/secret_at_rest_guard.py` — read-only, value-safe regression
  guard.
- `platform_tests/scripts/test_secret_at_rest_guard.py` — 9-test suite.

**Deleted (2):**

- `infrastructure/terraform/terraform.tfstate.backup` (34,771 B, stale).
- `infrastructure/terraform/terraform.tfstate.1774985892.backup` (35,868 B, stale).
- The live `infrastructure/terraform/terraform.tfstate` (37,980 B) is
  **preserved** for owner-run migration.

**Deferred (1) — not modified:**

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — doctor-check wiring was
  intentionally **deferred to FAB-19** per the proposal's own escape clause
  ("if the god-module touch is undesirable the guard stands alone + sweep wiring
  defers to FAB-19"). `doctor.py` is a ~2,800-line god module that FAB-19/FAB-22
  are chartered to address; doctor wiring is not among the 5 acceptance criteria.
  The guard remains independently runnable + tested. This is a smaller footprint
  than the authorized target_paths, not an overreach.

## Spec-Derived Verification Plan (with observed results)

| Spec / requirement | Derived test | Result |
|---|---|---|
| `GOV-ENV-LOCAL-AUTHORITY-001` (credential SoT must not replicate uncontrolled) | guard `env_local_excluded`; `test_missing_env_local_exclusion_fails` | PASS (guard matched `.env.local`; FAIL-branch test passes) |
| project-root-boundary Drive-sync exposure (HYG-019) | guard `tfstate_excluded`/`tfstate_variants_excluded`/`tfvars_excluded`/`dot_terraform_excluded`/`no_stale_tfstate_backups`; `test_missing_tfstate_exclusion_fails`, `test_stale_tfstate_backup_fails` | PASS (all matched; no `*.tfstate*.backup` on disk) |
| Backend migration scaffolding | guard `azurerm_backend_block_present`/`backend_example_present`/`migration_runbook_present`; `test_missing_backend_block_fails`, `test_missing_runbook_fails` | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (no new out-of-placement artifacts) | placement: all created files under `infrastructure/terraform/` + `scripts/hygiene/` + `platform_tests/scripts/`; directory not relocated | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_secret_at_rest_guard.py` PASS/FAIL branches + value-safety | PASS (9 passed) |

### Commands and observed results

Interpreter: `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe` (Python 3.14.0).

- `python scripts/hygiene/secret_at_rest_guard.py` → `"ok": true`, 10/10 checks
  pass, `"failures": []`, **exit 0**.
- `python -m pytest platform_tests/scripts/test_secret_at_rest_guard.py -q` →
  **9 passed in 0.24s**.
- `python -m ruff check scripts/hygiene/secret_at_rest_guard.py platform_tests/scripts/test_secret_at_rest_guard.py`
  → **All checks passed!**
- `python -m ruff format --check scripts/hygiene/secret_at_rest_guard.py platform_tests/scripts/test_secret_at_rest_guard.py`
  → **2 files already formatted** (after applying `ruff format`).

## Acceptance Criteria — Status

1. `.driveignore` excludes `.env.local`/`.env*` (with `.example` re-includes),
   `*.tfstate*`, `*.tfvars`, `infrastructure/terraform/.terraform/` — **MET**.
2. The 2 stale tfstate backups deleted; live `terraform.tfstate` remains — **MET**.
3. `backend.tf` partial block + `backend.hcl.example` present; `backend.hcl`
   gitignored; runbook present — **MET**.
4. `secret_at_rest_guard.py` + test exist, pass, ruff-clean — **MET**.
5. Credential-rotation owner-action record (6 value names; no values) — **MET**.

## GO Implementation-Constraint Compliance (`-002`)

- Did NOT rotate credentials. ✓
- Did NOT relocate `infrastructure/terraform/`. ✓
- Did NOT read, print, commit, or log secret values from tfstate or `.env.local`
  (the guard is value-length/textual-config only; `test_guard_is_value_safe`
  asserts no planted sentinel leaks into output). ✓
- Preserved the live `infrastructure/terraform/terraform.tfstate`; deleted only
  the two named stale backups. ✓
- Treated the credential-rotation document as an owner-action checklist with
  value names only. ✓

## Owner Follow-Up Actions (tracked; do NOT gate VERIFIED)

Recorded in `CREDENTIAL-ROTATION-OWNER-ACTION.md` + `STATE-MIGRATION-RUNBOOK.md`,
tracked against WI-4414's closure note: rotate the 6 exposed values; provision
backend identifiers, fill `backend.hcl`, run `terraform init -migrate-state`,
remove local state; add `.env.local` + tfstate/tfvars exclusions to the
SyncBackSE profile.

## Recommended Commit Type

`feat:` — net-new backend scaffolding, regression guard, and owner runbook (with
embedded `chore:`-class `.driveignore`/`.gitignore`/backup-deletion edits). Diff
stat: 2 modified, 6 created, 2 deleted; net-new capability surface (a runnable
guard + tested invariants) justifies `feat:` over `chore:`.

## Risk and Rollback

Rollback: revert the `.driveignore`/`.gitignore`/`backend.tf` edits and remove
the guard + test; the deleted backups are stale (no restore needed; live state
intact). All changes are non-destructive to the live `terraform.tfstate`.
