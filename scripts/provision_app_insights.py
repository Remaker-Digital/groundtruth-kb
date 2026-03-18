"""
Provision Azure Application Insights resource for Agent Red (SPEC-1834, WI-1454).

Creates an Application Insights resource in East US, stores the connection
string in Key Vault, and adds the env var to the container app.

Prerequisites:
    - Azure CLI authenticated (az login)
    - Contributor access to Agent-Red resource group
    - Key Vault access policy for secrets

Usage:
    python scripts/provision_app_insights.py [--dry-run]

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Azure resource configuration
RESOURCE_GROUP = "Agent-Red"
LOCATION = "eastus"
APP_INSIGHTS_NAME = "appi-agentred-eastus"
KEY_VAULT_NAME = "kv-agentred-eastus"
SECRET_NAME = "APPLICATIONINSIGHTS-CONNECTION-STRING"
CONTAINER_APP_NAME = "agent-red-api-gateway"
CONTAINER_APP_ENV = "agent-red-env"
WORKSPACE_NAME = "log-agentred-eastus"


def run_az(args: list[str], *, capture: bool = True, dry_run: bool = False) -> str | None:
    """Run an Azure CLI command."""
    cmd = ["az"] + args
    cmd_str = " ".join(cmd)

    if dry_run:
        logger.info("[DRY RUN] %s", cmd_str)
        return None

    logger.info("Running: %s", cmd_str)
    result = subprocess.run(cmd, capture_output=capture, text=True)

    if result.returncode != 0:
        logger.error("Command failed: %s\n%s", cmd_str, result.stderr)
        sys.exit(1)

    return result.stdout.strip() if capture else None


def check_existing(dry_run: bool = False) -> str | None:
    """Check if Application Insights resource already exists."""
    if dry_run:
        return None

    try:
        output = run_az([
            "monitor", "app-insights", "component", "show",
            "--app", APP_INSIGHTS_NAME,
            "--resource-group", RESOURCE_GROUP,
            "--output", "json",
        ])
        if output:
            data = json.loads(output)
            return data.get("connectionString")
    except SystemExit:
        pass
    return None


def provision(dry_run: bool = False) -> None:
    """Provision Application Insights and wire connection string."""

    # Step 1: Check if already exists
    logger.info("Step 1: Checking for existing Application Insights resource...")
    existing_conn_str = check_existing(dry_run)
    if existing_conn_str:
        logger.info("Application Insights already exists: %s", APP_INSIGHTS_NAME)
        logger.info("Connection string: %s...%s", existing_conn_str[:30], existing_conn_str[-10:])
    else:
        # Step 2: Create Log Analytics workspace (required by App Insights)
        logger.info("Step 2: Creating Log Analytics workspace...")
        run_az([
            "monitor", "log-analytics", "workspace", "create",
            "--resource-group", RESOURCE_GROUP,
            "--workspace-name", WORKSPACE_NAME,
            "--location", LOCATION,
            "--sku", "PerGB2018",
            "--retention-in-days", "30",
        ], dry_run=dry_run)

        # Step 3: Create Application Insights resource
        logger.info("Step 3: Creating Application Insights resource...")
        output = run_az([
            "monitor", "app-insights", "component", "create",
            "--app", APP_INSIGHTS_NAME,
            "--location", LOCATION,
            "--resource-group", RESOURCE_GROUP,
            "--kind", "web",
            "--application-type", "web",
            "--workspace", f"/subscriptions/4dce2122-690a-4654-b531-cc647db62331"
                          f"/resourceGroups/{RESOURCE_GROUP}"
                          f"/providers/Microsoft.OperationalInsights/workspaces/{WORKSPACE_NAME}",
            "--output", "json",
        ], dry_run=dry_run)

        if output:
            data = json.loads(output)
            existing_conn_str = data.get("connectionString")
            logger.info("Created Application Insights: %s", APP_INSIGHTS_NAME)

    if dry_run:
        logger.info("[DRY RUN] Would store connection string in Key Vault and configure container app")
        return

    if not existing_conn_str:
        logger.error("No connection string available — cannot proceed")
        sys.exit(1)

    # Step 4: Store connection string in Key Vault
    logger.info("Step 4: Storing connection string in Key Vault...")
    run_az([
        "keyvault", "secret", "set",
        "--vault-name", KEY_VAULT_NAME,
        "--name", SECRET_NAME,
        "--value", existing_conn_str,
    ])
    logger.info("Secret stored: %s/%s", KEY_VAULT_NAME, SECRET_NAME)

    # Step 5: Add env var reference to container app
    logger.info("Step 5: Adding APPLICATIONINSIGHTS_CONNECTION_STRING to container app...")
    run_az([
        "containerapp", "update",
        "--name", CONTAINER_APP_NAME,
        "--resource-group", RESOURCE_GROUP,
        "--set-env-vars",
        f"APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:{SECRET_NAME}",
    ])
    logger.info("Container app updated with Application Insights connection string")

    # Summary
    logger.info("=" * 60)
    logger.info("Provisioning complete:")
    logger.info("  Resource: %s (East US)", APP_INSIGHTS_NAME)
    logger.info("  Key Vault secret: %s/%s", KEY_VAULT_NAME, SECRET_NAME)
    logger.info("  Container app: %s (env var added)", CONTAINER_APP_NAME)
    logger.info("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Provision Azure Application Insights for Agent Red (SPEC-1834)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()
    provision(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
