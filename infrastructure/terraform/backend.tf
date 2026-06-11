# Azure remote state backend — PARTIAL configuration.
#
# FAB-02 / WI-4414 (PROJECT-FABLE-INVESTIGATION); HYG-019 remediation.
#
# HYG-019 found Terraform state (terraform.tfstate, 6 plaintext secret values)
# held on the Google-Drive-synced E: drive, i.e. replicated to the owner's Drive
# cloud account. Migrating state into an Azure Storage backend removes the
# plaintext-at-rest exposure.
#
# This is a PARTIAL backend block: it declares the azurerm backend but carries
# NO identifiers and NO secrets. The owner supplies resource_group_name /
# storage_account_name / container_name / key at init time via
#   terraform init -migrate-state -backend-config=backend.hcl
# (see STATE-MIGRATION-RUNBOOK.md). The real backend.hcl is gitignored and
# Drive-excluded; only backend.hcl.example is tracked.
#
# Until the owner runs the migration this block is inert scaffolding. The owner
# validates the configuration at migration time (terraform init); FAB-02 does
# not run Terraform.

terraform {
  backend "azurerm" {}
}
