NEW

bridge_kind: prime_proposal
Document: gtkb-fab-02-secrets-remediation
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4414
Project Authorization: PAUTH-FAB02-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 07ef97df-2cb3-45a4-9c32-be60d702f29c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".driveignore", ".gitignore", "infrastructure/terraform/backend.tf", "infrastructure/terraform/backend.hcl.example", "infrastructure/terraform/STATE-MIGRATION-RUNBOOK.md", "infrastructure/terraform/CREDENTIAL-ROTATION-OWNER-ACTION.md", "infrastructure/terraform/terraform.tfstate.backup", "infrastructure/terraform/terraform.tfstate.1774985892.backup", "scripts/hygiene/secret_at_rest_guard.py", "platform_tests/scripts/test_secret_at_rest_guard.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py"]

---

# FAB-02 — Secure stranded Terraform state + credential replication surfaces

WI-4414 (FAB-02) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-019, HYG-020.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

## Summary

Two verified secret-at-rest exposures on the Google-Drive-synced `E:\` drive:

- **HYG-019 (P0):** `infrastructure/terraform/terraform.tfstate` (37,980 B) + 2 stale
  backups hold **6 non-empty plaintext secret values** (the `admin_password`,
  `primary_key`, and four SQL connection-string keys — names only; no values were
  ever read, a value-length-only JSON walk produced the count). Gitignored, so
  uncommitted — but plaintext on a drive the project's own rules document as
  Drive-synced, so the values are already replicated to the owner's Drive cloud
  account and are treated as compromised.
- **HYG-020:** `.env.local` (the platform credential SoT per
  `GOV-ENV-LOCAL-AUTHORITY-001`, 12,696 B) is gitignored but `.driveignore` does
  not exclude it, so it uploads to Drive cloud and mirrors unencrypted to
  `G:\GT-KB-Backup\.env.local`.

This proposal implements the **full-remediation** path the owner selected
(`DELIB-FAB02-REMEDIATION-20260610`): Drive-exclude the secret-bearing files,
delete the 2 stale tfstate backups, scaffold an azurerm partial-config remote
backend + owner runbook, and add a narrow regression-guard so the exposure
cannot silently recur. Credential rotation and the live-infra state migration
are owner-scoped follow-ups (tracked, not gating `VERIFIED`).

## Specification Links

- `GOV-ENV-LOCAL-AUTHORITY-001` — establishes `.env.local` as the platform
  credential source of truth; HYG-020 is a replication-surface gap against it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority governing this
  proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal must
  cite all relevant governing specs (satisfied here).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  derives tests from the linked specs.
- `GOV-STANDING-BACKLOG-001` — WI-4414 is the governed backlog authority for this
  work; this proposal is its bridge vehicle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `infrastructure/terraform/` is
  Agent-Red application infra at the platform root, an isolation-placement concern
  under this ADR. FAB-02 **secures the secrets at rest only** and deliberately does
  **not** relocate the directory (relocation is FAB-12, currently pinned by the
  live test `applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py:45`).
  This proposal stays consistent with the ADR: it introduces no new out-of-placement
  artifacts and explicitly scopes the placement-remediation to FAB-12.

Governing rules (non-spec): `.claude/rules/project-root-boundary.md` records the
"Google Drive currently syncs E:" rationale and the Sandbox Output Exception that
this exposure violates. Context workstream (prose, not a `specifications` row):
`GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` (the standing P0 controlling
workstream per `.claude/rules/codex-standing-priorities.md`); HYG-019 is its
current-file-purge half.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — the chartering advisory
  (HYG-019/020 in the FAB-02 row); evidence frozen, do not re-derive.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — the project chartering decisions
  (verified-merge, full-milestone scope, hybrid clusters, per-cluster AUQ,
  repeatability architecture, advisory packaging, auq_resolved creation timing).
- `DELIB-FAB02-REMEDIATION-20260610` — this cluster's consolidated owner-decision
  set (the AUQ batch + the grill-me-for-clarification sub-decision tree).
- _No prior bridge thread exists on tfstate secret-at-rest remediation. The
  S251-era `*TERRAFORM*` advisory-routing work items surfaced by
  `gt backlog list --contains terraform` are deployment-lifecycle reviews, not
  secret-at-rest; they belong to the FAB-18 advisory-drain cluster and are NOT
  absorbed here._

## Owner Decisions / Input

All decisions below were collected via `AskUserQuestion` on 2026-06-10 (interactive
owner Prime Builder session) and persisted to `DELIB-FAB02-REMEDIATION-20260610`:

1. **HYG-019 remediation = Full remediation** — Drive-exclude state, delete the 2
   stale backups, add an azurerm remote-backend config; owner rotates the 6 values
   + runs the migration. (Rejected: containment-only; accept-risk-with-record.)
2. **HYG-020 = Exclude from both** — `.driveignore` entry (Prime) + SyncBackSE
   profile exclusion (owner); KV-recoverable. (Rejected: Drive-only; accept-both.)
3. **Grill A — backend target = Reuse existing** — a state Storage account/container
   already exists; Prime writes a `backend "azurerm" {}` partial-config block +
   gitignored `backend.hcl` template + runbook; owner supplies values at init time.
4. **Grill B — execution split = Owner-executed migration** (constraint-determined:
   `terraform init -migrate-state` touches live infra + needs owner creds).
5. **Grill C — rotation gate = Tracked follow-up** — rotation is an explicit
   owner-action record + tracked item; it does NOT gate `VERIFIED`.
6. **Grill D — detector = Narrow regression-guard** — FAB-02 adds a focused check
   of its own invariants; generalized at-rest scanning deferred to FAB-19.

## Requirement Sufficiency

**Existing requirements sufficient.** The remediation is governed by
`GOV-ENV-LOCAL-AUTHORITY-001` (credential SoT), `.claude/rules/project-root-boundary.md`
(Drive-sync exposure rationale), and the `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT`
workstream; the specific remediation choices are fixed by
`DELIB-FAB02-REMEDIATION-20260610`. No new or revised requirement is required
before implementation. The narrow regression-guard encodes an invariant derived
from these existing requirements; if Loyal Opposition judges that invariant
warrants a formal protected-behavior spec, that is a reviewer-surfaced follow-up,
not a precondition of this config/security remediation.

## Scope and Boundaries

In scope (the Prime-implementable surface that `VERIFIED` covers):

- `.driveignore` / `.gitignore` exclusion edits.
- Deletion of the 2 stale tfstate backups.
- `backend.tf` partial azurerm block + `backend.hcl.example` template + migration
  runbook.
- A narrow regression-guard (`scripts/hygiene/secret_at_rest_guard.py`) + test +
  minimal doctor wiring.
- A credential-rotation owner-action record (6-value checklist).

Explicitly OUT of scope (frozen boundaries):

- **No** relocation of `infrastructure/terraform/` out of the platform root —
  blocked by the live test `applications/Agent_Red/tests/unit/test_deploy_pipeline_scaling.py:45`
  (reads `PROJECT_ROOT/infrastructure/terraform/main.tf`); that relocation is the
  FAB-12 residue/isolation concern under `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- **No** purge of the ~272 MB `.terraform/` provider cache — that is FAB-04 storage.
- The live `terraform.tfstate` is **migrated, not deleted**; `production.tfvars` /
  `staging.tfvars` scanned clean (0 secret-shaped keys) and are **retained**
  (Drive-excluded as defense-in-depth, not deleted).

## Proposed Implementation

1. **`.driveignore`** — add exclusions: `.env.local`, `.env*` (with `!*.example`
   re-includes for the two tracked example files), `*.tfstate`, `*.tfstate.*`,
   `*.tfvars`, `infrastructure/terraform/.terraform/`. Stops further cloud
   replication of all secret-bearing surfaces.
2. **`.gitignore`** — add `infrastructure/terraform/backend.hcl` so the real
   (secret-bearing) backend config is never committed; the `.example` template is
   tracked.
3. **Delete** `infrastructure/terraform/terraform.tfstate.backup` and
   `infrastructure/terraform/terraform.tfstate.1774985892.backup` (confirmed
   present; stale; the live state is preserved for migration).
4. **`infrastructure/terraform/backend.tf`** — a `terraform { backend "azurerm" {} }`
   partial-config block (no identifiers/secrets committed).
5. **`infrastructure/terraform/backend.hcl.example`** — template enumerating the
   `resource_group_name`, `storage_account_name`, `container_name`, `key` the owner
   supplies via `-backend-config` (real `backend.hcl` gitignored).
6. **`infrastructure/terraform/STATE-MIGRATION-RUNBOOK.md`** — owner runbook for
   `terraform init -migrate-state -backend-config=backend.hcl` (with Azure AD auth
   or `ARM_ACCESS_KEY`), including the post-migration local-state cleanup step.
7. **`scripts/hygiene/secret_at_rest_guard.py`** — a read-only check asserting the
   FAB-02 invariants (see verification) — no secret bytes printed, value-length
   semantics only, JSON-serializable result.
8. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** — minimal registration
   of the guard as a WARN-severity doctor check (implementer confirms exact path;
   if the god-module touch is undesirable the guard stands alone + sweep wiring
   defers to FAB-19).
9. **`infrastructure/terraform/CREDENTIAL-ROTATION-OWNER-ACTION.md`** — the tracked
   owner-action record listing the 6 exposed value *names* to rotate (no values).

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-ENV-LOCAL-AUTHORITY-001` (credential SoT must not replicate uncontrolled) | guard asserts `.env.local` matched by `.driveignore`; `pytest` asserts guard returns FAIL when the entry is absent |
| project-root-boundary Drive-sync exposure (HYG-019) | guard asserts `*.tfstate*` + `*.tfvars` + `.terraform/` matched by `.driveignore`; asserts **no** `*.tfstate*.backup` files on disk under `infrastructure/terraform/` |
| Backend migration scaffolding | guard asserts a `backend "azurerm"` block exists in `infrastructure/terraform/*.tf`; runbook + `backend.hcl.example` present |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (no new out-of-placement artifacts) | guard/test confirms FAB-02 adds no files outside `infrastructure/terraform/` placement and does not relocate the directory |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/scripts/test_secret_at_rest_guard.py` exercises the guard's PASS/FAIL branches with a tmp fixture tree |

Commands (run at verification): `python scripts/hygiene/secret_at_rest_guard.py`
(exit 0 = invariants hold), `pytest platform_tests/scripts/test_secret_at_rest_guard.py`,
`ruff check` + `ruff format --check` on the changed `.py` files.

## Acceptance Criteria

1. `.driveignore` excludes `.env.local`/`.env*` (with `.example` re-includes),
   `*.tfstate*`, `*.tfvars`, `infrastructure/terraform/.terraform/`.
2. The 2 stale tfstate backups are deleted; the live `terraform.tfstate` remains.
3. `backend.tf` partial block + `backend.hcl.example` present; `backend.hcl`
   gitignored; runbook present.
4. `secret_at_rest_guard.py` + its test exist, pass, and are ruff-clean.
5. The credential-rotation owner-action record exists (6 value names; no values).

## Owner Follow-Up Actions (tracked; do NOT gate VERIFIED)

- Rotate the 6 exposed values (already cloud-replicated → compromised).
- Provision/confirm backend identifiers, fill `backend.hcl`, run
  `terraform init -migrate-state`, then remove local state per the runbook.
- Add the `.env.local` + tfstate exclusion to the SyncBackSE profile (third-party
  tool, manual). These are recorded in `CREDENTIAL-ROTATION-OWNER-ACTION.md` and
  tracked against WI-4414's closure note.

## Risk and Rollback

- **Risk:** an over-broad `.env*` exclusion could stop Drive-backing intended
  files — mitigated by explicit `!*.example` re-includes; the guard test covers it.
- **Risk:** backend migration is owner-executed against live infra — mitigated by
  partial-config + runbook; if migration is deferred, the Drive exclusion +
  backup deletion still contain the active cloud-replication vector.
- **Rollback:** revert the `.driveignore`/`.gitignore`/`backend.tf` edits and remove
  the guard; deleted backups are stale (no restore needed; live state intact). All
  changes are non-destructive to the live `terraform.tfstate`.

## Recommended Implementation Routing

Determined-mechanical surface (config edits + runbook + a small read-only guard) —
a **tier-1 local Ollama Qwen2.5-Coder** candidate under the campaign routing
(`DELIB`-recorded: tiered local→cheap→Claude). Reserve Claude/Codex for reviewing
the `doctor.py` registration. The guard must remain value-length-only (never print
secret bytes) regardless of which model implements it.

## Recommended Commit Type

`feat:` — net-new backend scaffolding, regression guard, and owner runbook
(with embedded `chore:`-class `.driveignore`/backup-deletion edits).
