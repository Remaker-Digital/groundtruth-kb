REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-02-secrets-remediation
Version: 005
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4414
Project Authorization: PAUTH-FAB02-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 430d5513-21a1-4e1c-b244-743f2ca7ed00
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".driveignore", ".gitignore", "infrastructure/terraform/backend.tf", "infrastructure/terraform/backend.hcl.example", "infrastructure/terraform/STATE-MIGRATION-RUNBOOK.md", "infrastructure/terraform/CREDENTIAL-ROTATION-OWNER-ACTION.md", "infrastructure/terraform/terraform.tfstate.backup", "infrastructure/terraform/terraform.tfstate.1774985892.backup", "scripts/hygiene/secret_at_rest_guard.py", "platform_tests/scripts/test_secret_at_rest_guard.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py"]

---

# FAB-02 — Post-Implementation Report (secret-at-rest remediation), REVISED

Revised implementation report for `gtkb-fab-02-secrets-remediation`, GO at
`bridge/gtkb-fab-02-secrets-remediation-002.md`, addressing the verification
NO-GO at `bridge/gtkb-fab-02-secrets-remediation-004.md`. WI-4414 (FAB-02) of
PROJECT-FABLE-INVESTIGATION; findings HYG-019, HYG-020. Revised by Prime Builder
harness B (Opus 4.8) under resumable impl-start packet
`sha256:21cca9ad49f874f5de49369ac9c80d6f8c00858129761a80e5b328e56d0923bc`
(created from the live `GO`; resumable post-GO NO-GO state; expires
2026-06-11T12:38:56Z).

## Revision Scope

This revision addresses the single P1 finding in the `-004` NO-GO:

> `backend.hcl` is claimed Drive-excluded but is not excluded by `.driveignore`.

The docs (`backend.hcl.example`, `STATE-MIGRATION-RUNBOOK.md`) stated the real
owner-filled `infrastructure/terraform/backend.hcl` is "gitignored +
Drive-excluded / never Drive-synced", and `.gitignore` did exclude it, but
`.driveignore` — an INDEPENDENT cloud-replication surface — did not. Per Codex's
preferred remediation path (make the claim mechanically true rather than soften
the docs), this revision:

1. **`.driveignore`** — adds `infrastructure/terraform/backend.hcl` to the
   FAB-02 secret-at-rest exclusion block (with an explanatory comment). The
   exact-path entry does not touch `backend.hcl.example`, which stays synced via
   the existing `!*.example` re-include.
2. **`scripts/hygiene/secret_at_rest_guard.py`** — adds a `backend_hcl_excluded`
   invariant to `_REQUIRED_DRIVEIGNORE` so the replication-control claim is
   mechanically asserted on every run (the Opportunity-Radar deterministic-
   service cue from `-004`), plus a docstring bullet documenting it.
3. **`platform_tests/scripts/test_secret_at_rest_guard.py`** — adds
   `infrastructure/terraform/backend.hcl` to the clean-tree fixture and a new
   negative test `test_missing_backend_hcl_exclusion_fails` asserting the
   `backend_hcl_excluded` failure branch.

No other change. The fix stays inside the existing GO'd `target_paths` and
PAUTH-FAB02-20260610 mutation classes (`config`, `source`, `test_addition`); no
new owner decision was required (Codex directed the mechanical fix in `-004`).

## Summary

The Prime-implementable, value-safe slice of HYG-019/020 is complete: the
secret-bearing files (including the owner-filled `backend.hcl`) are excluded from
Google-Drive replication AND from Git, the two stale tfstate backups are deleted,
the azurerm partial-config backend + owner runbook are scaffolded, the
credential-rotation owner-action record (names only) is written, and a value-safe
regression guard + test encode the invariants — now including the backend-config
replication-control invariant. The owner-only follow-ups (credential rotation,
live-state migration, SyncBackSE profile edit, terraform/ relocation) are recorded
as tracked actions and do not gate `VERIFIED` (grill-C decision).

## Specification Links

Carried forward from `-001` (GO'd) and `-003`:

- `GOV-ENV-LOCAL-AUTHORITY-001` — `.env.local` is the credential SoT; HYG-020 is
  a replication-surface gap against it (closed in `.driveignore`).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs
  cited (carried forward).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping +
  command evidence below satisfy this gate (now covering the backend.hcl
  replication invariant).
- `GOV-STANDING-BACKLOG-001` — WI-4414 is the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `infrastructure/terraform/` is
  Agent-Red application infra at the platform root; this work secures secrets at
  rest only and introduces no out-of-placement artifacts. Directory relocation
  remains deferred to FAB-12.

## Isolation Placement Compliance

All changed and created artifacts remain within the GT-KB root `E:\GT-KB`:
the `-005` revision touches only the root `.driveignore`, `scripts/hygiene/`, and
`platform_tests/scripts/` — all in-root. No file was created outside
`infrastructure/terraform/` placement, and the directory was NOT relocated
(relocation is FAB-12 under `ADR-ISOLATION-APPLICATION-PLACEMENT-001`). No
out-of-root dependency was created or required.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory
  (HYG-019/020 in the FAB-02 row).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB02-REMEDIATION-20260610` — this cluster's consolidated owner-decision
  set (carried forward; unchanged — the `-005` fix introduced no new decision).
- `bridge/gtkb-fab-02-secrets-remediation-002.md` — the GO with implementation
  constraints honored below.
- `bridge/gtkb-fab-02-secrets-remediation-004.md` — the verification NO-GO whose
  single P1 this revision closes.

## Owner Decisions / Input

The implemented choices were collected via `AskUserQuestion` on 2026-06-10 and
persisted to `DELIB-FAB02-REMEDIATION-20260610` (carried forward verbatim from
`-001`/`-003`): full HYG-019 remediation; exclude-from-both for HYG-020; reuse
existing backend (partial-config + gitignored `backend.hcl` + runbook);
owner-executed migration; rotation as tracked follow-up (does not gate
`VERIFIED`); narrow regression-guard detector. The `-005` revision required **no
new owner decision**: it is the mechanical reconciliation Codex directed in the
`-004` NO-GO ("add the backend config exclusion and test it"), inside the
existing PAUTH mutation classes. The `GO` at `-002` remains the per-cluster
implementation authorization moment.

## Requirement Sufficiency

Existing requirements sufficient (carried forward from `-001`). No new or revised
requirement was needed; the new `backend_hcl_excluded` invariant encodes an
invariant already implied by the linked specs and the existing owner decision
(exclude the credential-bearing surfaces from BOTH replication channels).

## Files Changed

**Modified (3):**

- `.driveignore` — the FAB-02 secret-at-rest exclusions plus the new
  `infrastructure/terraform/backend.hcl` exact-path exclusion (`-005`).
- `.gitignore` — `infrastructure/terraform/backend.hcl` (the tracked `.example`
  template stays committed). Unchanged in `-005`.
- `scripts/hygiene/secret_at_rest_guard.py` — read-only, value-safe regression
  guard; `-005` added the `backend_hcl_excluded` invariant + docstring bullet.
- `platform_tests/scripts/test_secret_at_rest_guard.py` — `-005` added the
  backend.hcl fixture line + `test_missing_backend_hcl_exclusion_fails` (now 10
  tests).

**Created (4, from `-003`; unchanged in `-005`):**

- `infrastructure/terraform/backend.tf` — partial `terraform { backend "azurerm" {} }`
  block (no identifiers/secrets).
- `infrastructure/terraform/backend.hcl.example` — non-secret template (stays
  Drive-synced via `!*.example`).
- `infrastructure/terraform/STATE-MIGRATION-RUNBOOK.md` — owner migration runbook.
- `infrastructure/terraform/CREDENTIAL-ROTATION-OWNER-ACTION.md` — tracked
  owner-action record listing the 6 exposed value **names** (no values).

**Deleted (2, from `-003`; unchanged in `-005`):**

- `infrastructure/terraform/terraform.tfstate.backup` (34,771 B, stale).
- `infrastructure/terraform/terraform.tfstate.1774985892.backup` (35,868 B, stale).
- The live `infrastructure/terraform/terraform.tfstate` (37,980 B) is
  **preserved** for owner-run migration.

**Deferred (1) — not modified:**

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — doctor-check wiring
  remains intentionally deferred to FAB-19 (god-module touch out of FAB-02 scope;
  not among the acceptance criteria). The guard remains independently runnable +
  tested. Smaller footprint than the authorized `target_paths`, not an overreach.

## Spec-Derived Verification Plan (with observed results)

| Spec / requirement | Derived test | Result |
|---|---|---|
| `GOV-ENV-LOCAL-AUTHORITY-001` (credential SoT must not replicate uncontrolled) | guard `env_local_excluded`; `test_missing_env_local_exclusion_fails` | PASS |
| project-root-boundary Drive-sync exposure (HYG-019) | guard `tfstate_excluded`/`tfstate_variants_excluded`/`tfvars_excluded`/`dot_terraform_excluded`/`no_stale_tfstate_backups`; `test_missing_tfstate_exclusion_fails`, `test_stale_tfstate_backup_fails` | PASS |
| **backend-config secret-at-rest (`-004` P1)** — owner-filled `backend.hcl` excluded from Drive so the doc claim is true | guard `backend_hcl_excluded`; `test_missing_backend_hcl_exclusion_fails` | **PASS** (guard matched `infrastructure/terraform/backend.hcl`; FAIL-branch test passes) |
| Backend migration scaffolding | guard `azurerm_backend_block_present`/`backend_example_present`/`migration_runbook_present`; `test_missing_backend_block_fails`, `test_missing_runbook_fails` | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (no new out-of-placement artifacts) | placement review; directory not relocated | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_secret_at_rest_guard.py` PASS/FAIL branches + value-safety | PASS (10 passed) |

### Commands and observed results

Interpreter: `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe` (Python 3.14.0).

- `python scripts/hygiene/secret_at_rest_guard.py` → `"ok": true`, **11/11 checks
  pass** (now including `backend_hcl_excluded`), `"failures": []`, **exit 0**.
- `python -m pytest platform_tests/scripts/test_secret_at_rest_guard.py -q` →
  **10 passed in 0.65s**.
- `python -m ruff check scripts/hygiene/secret_at_rest_guard.py platform_tests/scripts/test_secret_at_rest_guard.py`
  → **All checks passed!**
- `python -m ruff format --check scripts/hygiene/secret_at_rest_guard.py platform_tests/scripts/test_secret_at_rest_guard.py`
  → **2 files already formatted**.

## Acceptance Criteria — Status

1. `.driveignore` excludes `.env.local`/`.env*` (with `.example` re-includes),
   `*.tfstate*`, `*.tfvars`, `infrastructure/terraform/.terraform/`, **and now
   `infrastructure/terraform/backend.hcl`** — **MET**.
2. The 2 stale tfstate backups deleted; live `terraform.tfstate` remains — **MET**.
3. `backend.tf` partial block + `backend.hcl.example` present; real `backend.hcl`
   gitignored AND Drive-excluded; runbook present — **MET**.
4. `secret_at_rest_guard.py` + test exist, pass (11 checks / 10 tests),
   ruff-clean — **MET**.
5. Credential-rotation owner-action record (6 value names; no values) — **MET**.

## GO Implementation-Constraint Compliance (`-002`)

- Did NOT rotate credentials. ✓
- Did NOT relocate `infrastructure/terraform/`. ✓
- Did NOT read, print, commit, or log secret values (the guard is textual-config
  / pattern-presence only; `test_guard_is_value_safe` asserts no planted sentinel
  leaks). ✓
- Preserved the live `infrastructure/terraform/terraform.tfstate`; deleted only
  the two named stale backups. ✓
- Treated the credential-rotation document as an owner-action checklist with
  value names only. ✓

## Bridge Protocol Compliance

This revised report is filed as `bridge/gtkb-fab-02-secrets-remediation-005.md`
and its `REVISED` status line is inserted at the top of the
`gtkb-fab-02-secrets-remediation` entry in `bridge/INDEX.md`, which remains the
canonical bridge workflow state. The append-only version chain is preserved
(`-001` NEW → `-002` GO → `-003` NEW report → `-004` NO-GO → `-005` REVISED
report); no prior bridge file was modified or deleted.

## Owner Follow-Up Actions (tracked; do NOT gate VERIFIED)

Recorded in `CREDENTIAL-ROTATION-OWNER-ACTION.md` + `STATE-MIGRATION-RUNBOOK.md`,
tracked against WI-4414's closure note: rotate the 6 exposed values; provision
backend identifiers, fill `backend.hcl`, run `terraform init -migrate-state`,
remove local state; add `.env.local` + tfstate/tfvars exclusions to the
SyncBackSE profile.

## Recommended Commit Type

`feat:` — the cluster commit adds net-new backend scaffolding, a runnable
regression guard, and an owner runbook (with embedded `chore:`-class
`.driveignore`/`.gitignore`/backup-deletion edits). The `-005` revision on top is
a `fix:`-class replication-control hardening, but the eventual single cluster
commit remains `feat:` because the dominant surface is net-new capability. Diff
stat: 3 modified, 4 created, 2 deleted.

## Risk and Rollback

Rollback: revert the `.driveignore`/`.gitignore`/`backend.tf` edits and remove
the guard + test; the deleted backups are stale (no restore needed; live state
intact). All changes are non-destructive to the live `terraform.tfstate`. The
`-005` delta is additive (one ignore line + one guard invariant + one test) and
reverts cleanly to the `-003` state.
