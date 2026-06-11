# Terraform State Migration Runbook — Local → Azure Storage (azurerm) Backend

**FAB-02 / WI-4414 (PROJECT-FABLE-INVESTIGATION); HYG-019 remediation.**
**Audience:** owner (Mike). **Execution:** owner-run against live infrastructure
(requires owner Azure credentials). This is an owner-action runbook; the GT-KB
agent does not execute it.

## Why

HYG-019 found `infrastructure/terraform/terraform.tfstate` (and its stale
backups) holding **6 plaintext secret values** on the Google-Drive-synced `E:`
drive — already replicated to the Drive cloud account, so the values are treated
as compromised. FAB-02 has already:

- excluded the state files from further Drive replication (`.driveignore`),
- excluded the real `backend.hcl` from git (`.gitignore`),
- deleted the two stale `*.tfstate*.backup` files,
- added the partial azurerm backend scaffolding (`backend.tf` +
  `backend.hcl.example`),
- added a read-only regression guard (`scripts/hygiene/secret_at_rest_guard.py`).

This runbook is the remaining **owner-executed** step: moving the live state off
the local drive into an Azure Storage backend.

> Prerequisite: rotate the 6 exposed values first — see
> `CREDENTIAL-ROTATION-OWNER-ACTION.md`. The values are already cloud-replicated
> and must be considered compromised regardless of the state migration.

## Steps

1. **Provision / confirm the state Storage account.** Per the project's grill-B
   decision the backend reuses an existing state Storage account/container. Note
   the `resource_group_name`, `storage_account_name`, `container_name`, and the
   `key` path for this state.

2. **Create `backend.hcl`** (gitignored + Drive-excluded) by copying the
   template:

   ```
   cp infrastructure/terraform/backend.hcl.example infrastructure/terraform/backend.hcl
   ```

   Fill in the four values from step 1.

3. **Authenticate to Azure.** Either Azure AD (`az login`) or set
   `ARM_ACCESS_KEY` to the Storage account key for the migration shell only.
   Do not commit or log the key.

4. **Migrate the state** from `cd infrastructure/terraform`:

   ```
   terraform init -migrate-state -backend-config=backend.hcl
   ```

   Terraform detects the existing local state and offers to copy it into the
   azurerm backend. Confirm the prompt. Terraform validates the partial
   `backend "azurerm" {}` block at this point.

5. **Verify** the remote state is the source of truth:

   ```
   terraform plan
   ```

   A clean plan (no unexpected diffs) confirms the migrated state matches the
   live infrastructure.

6. **Remove the local state** once migration is confirmed. The local
   `terraform.tfstate` is now stale and still secret-bearing:

   ```
   rm infrastructure/terraform/terraform.tfstate
   ```

   (Any `terraform.tfstate.backup` Terraform writes during migration is also
   removable; the regression guard asserts no `*.tfstate*.backup` remains.)

7. **Confirm the guard passes:**

   ```
   python scripts/hygiene/secret_at_rest_guard.py
   ```

   Exit 0 = the FAB-02 invariants hold.

## Post-migration

- Add the `.env.local` + `*.tfstate*` + `*.tfvars` exclusions to the SyncBackSE
  backup profile (third-party tool; manual) so the mirror at
  `G:\GT-KB-Backup\` stops carrying the secret-bearing files. Recorded in
  `CREDENTIAL-ROTATION-OWNER-ACTION.md`.
- Close WI-4414's owner-follow-up note once rotation + migration + SyncBackSE
  exclusion are all done.

## Rollback

If migration must be reverted before step 6, the local `terraform.tfstate` is
still intact (it is copied, not moved, by `-migrate-state` until you delete it).
Re-run `terraform init` selecting the local backend, or restore the partial
block to local. No data loss occurs as long as the local state has not yet been
deleted in step 6.
