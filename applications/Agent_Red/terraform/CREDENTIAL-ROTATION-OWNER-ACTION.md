# Credential Rotation — Owner Action Required (FAB-02 / WI-4414; HYG-019)

**Status:** tracked owner follow-up. Does NOT gate FAB-02 `VERIFIED` (grill-C
decision). **Execution:** owner-run.

## Why

HYG-019 found 6 non-empty plaintext secret values in
`infrastructure/terraform/terraform.tfstate` (and its stale backups) on the
Google-Drive-synced `E:` drive — already replicated to the owner's Drive cloud
account. They are treated as **compromised** and must be rotated regardless of
the state migration.

No secret VALUES were read by the investigation or this remediation; only a
value-length JSON walk produced the count of 6. This record lists the value
NAMES only.

## The 6 exposed values to rotate

| # | Value (name only) | Where it lives | Rotate by |
|---|---|---|---|
| 1 | SQL administrator password (`administrator_login_password` / `admin_password`) | Azure SQL / MSSQL server | reset the server admin password in Azure; update `.env.local` + Key Vault |
| 2 | Resource primary access key (`primary_key` / `primary_access_key`) | the keyed Azure resource (Storage / Cosmos / etc.) | regenerate the primary key in Azure; update `.env.local` + Key Vault |
| 3 | SQL connection string #1 | SQL database connection string stored in state | regenerate after #1 (it embeds the rotated password) |
| 4 | SQL connection string #2 | SQL database connection string stored in state | regenerate after #1 |
| 5 | SQL connection string #3 | SQL database connection string stored in state | regenerate after #1 |
| 6 | SQL connection string #4 | SQL database connection string stored in state | regenerate after #1 |

The exact Azure resource names are known to the owner; this record deliberately
does not enumerate them from state to avoid reading secret-adjacent values.

## Other tracked owner follow-ups (WI-4414 closure note)

- **State migration:** run `STATE-MIGRATION-RUNBOOK.md` to move state off the
  local drive into the azurerm backend, then delete the local
  `terraform.tfstate`.
- **SyncBackSE profile:** add `.env.local`, `*.tfstate*`, and `*.tfvars` to the
  SyncBackSE backup profile exclusions so the `G:\GT-KB-Backup\` mirror stops
  carrying the secret-bearing files (third-party tool; manual).
