"""Deploy Agent Red agent containers to Azure Container Apps.

Creates 6 Container Apps (one per pipeline agent) using the existing
api-gateway image with command overrides to start the correct agent module.

Usage:
    python scripts/deploy_agent_containers.py --env staging
    python scripts/deploy_agent_containers.py --env staging --agent intent-classifier
    python scripts/deploy_agent_containers.py --env staging --verify-only

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import yaml


# Agent definitions: name -> module path
AGENTS = {
    "intent-classifier": "src.agents.containers.intent_classifier_app:app",
    "knowledge-retrieval": "src.agents.containers.knowledge_retrieval_app:app",
    "response-generator": "src.agents.containers.response_generator_app:app",
    "escalation-handler": "src.agents.containers.escalation_handler_app:app",
    "analytics-collector": "src.agents.containers.analytics_collector_app:app",
    "critic-supervisor": "src.agents.containers.critic_supervisor_app:app",
    "co-pilot": "src.agents.containers.co_pilot_app:app",
}

RESOURCE_GROUP = "Agent-Red"
MANAGED_ENV_ID = (
    "/subscriptions/4dce2122-690a-4654-b531-cc647db62331"
    "/resourceGroups/Agent-Red/providers/Microsoft.App"
    "/managedEnvironments/agent-red-env"
)
ACR_SERVER = "acragentredeastus.azurecr.io"
GATEWAY_IMAGE = f"{ACR_SERVER}/api-gateway:v1.85.0"
AGENT_PORT = 8080
NATS_ENDPOINT = os.environ.get("AGNTCY_NATS_ENDPOINT", "ws://agent-red-nats")
OPENAI_ENDPOINT = "https://agent-red-openai.openai.azure.com/"


def _build_yaml(agent_name: str, module_path: str, env: str, openai_key: str) -> dict:
    """Build the Container App YAML configuration for an agent."""
    container_name = f"agent-{agent_name}"
    return {
        "properties": {
            "managedEnvironmentId": MANAGED_ENV_ID,
            "configuration": {
                "activeRevisionsMode": "Single",
                "ingress": {
                    "external": False,
                    "targetPort": AGENT_PORT,
                    "transport": "Auto",
                },
                "registries": [
                    {"server": ACR_SERVER, "identity": "system"},
                ],
            },
            "template": {
                "containers": [
                    {
                        "name": container_name,
                        "image": GATEWAY_IMAGE,
                        "command": [
                            "tini",
                            "--",
                            "uvicorn",
                            module_path,
                            "--host",
                            "0.0.0.0",
                            "--port",
                            str(AGENT_PORT),
                            "--log-level",
                            "info",
                        ],
                        "resources": {"cpu": 0.5, "memory": "1Gi"},
                        "env": [
                            {"name": "ENVIRONMENT", "value": env},
                            {"name": "AZURE_OPENAI_ENDPOINT", "value": OPENAI_ENDPOINT},
                            {"name": "AZURE_OPENAI_API_KEY", "value": openai_key},
                            {"name": "AGNTCY_NATS_ENDPOINT", "value": NATS_ENDPOINT},
                        ],
                    }
                ],
                "scale": {"minReplicas": 1, "maxReplicas": 3},
            },
        }
    }


def _deploy_agent(agent_name: str, module_path: str, env: str, openai_key: str) -> dict:
    """Deploy a single agent Container App."""
    app_name = f"agent-red-{agent_name}"
    config = _build_yaml(agent_name, module_path, env, openai_key)

    # Write YAML to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, prefix=f"agent-{agent_name}-") as f:
        yaml.dump(config, f, default_flow_style=False)
        yaml_path = f.name

    try:
        # Check if Container App already exists
        check = subprocess.run(
            [
                "az",
                "containerapp",
                "show",
                "--name",
                app_name,
                "--resource-group",
                RESOURCE_GROUP,
                "--query",
                "name",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
        )

        if check.returncode == 0 and check.stdout.strip():
            # Update existing
            print(f"  Updating existing Container App: {app_name}")
            result = subprocess.run(
                [
                    "az",
                    "containerapp",
                    "update",
                    "--name",
                    app_name,
                    "--resource-group",
                    RESOURCE_GROUP,
                    "--yaml",
                    yaml_path,
                    "--query",
                    "{name:name, fqdn:properties.configuration.ingress.fqdn}",
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
            )
        else:
            # Create new
            print(f"  Creating new Container App: {app_name}")
            result = subprocess.run(
                [
                    "az",
                    "containerapp",
                    "create",
                    "--name",
                    app_name,
                    "--resource-group",
                    RESOURCE_GROUP,
                    "--yaml",
                    yaml_path,
                    "--query",
                    "{name:name, fqdn:properties.configuration.ingress.fqdn}",
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}")
            return {"name": app_name, "status": "failed", "error": result.stderr.strip()}

        info = json.loads(result.stdout) if result.stdout.strip() else {}
        fqdn = info.get("fqdn", "unknown")
        print(f"  OK: {app_name} -> {fqdn}")
        return {"name": app_name, "status": "deployed", "fqdn": fqdn}

    finally:
        os.unlink(yaml_path)


def _verify_agent(app_name: str) -> dict:
    """Verify an agent Container App is healthy."""
    result = subprocess.run(
        [
            "az",
            "containerapp",
            "show",
            "--name",
            app_name,
            "--resource-group",
            RESOURCE_GROUP,
            "--query",
            "{name:name, fqdn:properties.configuration.ingress.fqdn, "
            "running:properties.runningStatus, "
            "replicas:properties.template.scale.minReplicas}",
            "-o",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"name": app_name, "status": "not_found"}

    info = json.loads(result.stdout) if result.stdout.strip() else {}
    fqdn = info.get("fqdn", "")

    # Try health endpoint
    if fqdn:
        import urllib.request

        try:
            url = f"https://{fqdn}/health"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = json.loads(resp.read().decode())
                return {
                    "name": app_name,
                    "status": "healthy",
                    "fqdn": fqdn,
                    "health": body,
                }
        except Exception as exc:
            return {
                "name": app_name,
                "status": "unhealthy",
                "fqdn": fqdn,
                "error": str(exc),
            }

    return {"name": app_name, "status": "no_fqdn"}


def main():
    parser = argparse.ArgumentParser(description="Deploy agent containers")
    parser.add_argument("--env", default="staging", choices=["staging", "production"])
    parser.add_argument("--agent", help="Deploy only this agent (e.g., intent-classifier)")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing containers")
    parser.add_argument("--openai-key", help="Azure OpenAI API key (reads from env if not provided)")
    args = parser.parse_args()

    openai_key = args.openai_key or os.environ.get("AZURE_OPENAI_API_KEY", "")
    if not openai_key and not args.verify_only:
        # Read from staging Container App
        result = subprocess.run(
            [
                "az",
                "containerapp",
                "show",
                "--name",
                "agent-red-staging",
                "--resource-group",
                RESOURCE_GROUP,
                "--query",
                "properties.template.containers[0].env[?name=='AZURE_OPENAI_API_KEY'].value | [0]",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
        )
        openai_key = result.stdout.strip()

    agents_to_deploy = AGENTS
    if args.agent:
        if args.agent not in AGENTS:
            print(f"Unknown agent: {args.agent}")
            print(f"Available: {', '.join(AGENTS.keys())}")
            sys.exit(1)
        agents_to_deploy = {args.agent: AGENTS[args.agent]}

    if args.verify_only:
        print(f"Verifying {len(agents_to_deploy)} agent containers...")
        for agent_name in agents_to_deploy:
            app_name = f"agent-red-{agent_name}"
            result = _verify_agent(app_name)
            status = result.get("status", "unknown")
            fqdn = result.get("fqdn", "")
            print(f"  {app_name}: {status} ({fqdn})")
        return

    print(f"Deploying {len(agents_to_deploy)} agent containers to {args.env}...")
    print(f"  Image: {GATEWAY_IMAGE}")
    print(f"  NATS:  {NATS_ENDPOINT}")
    print()

    results = []
    for agent_name, module_path in agents_to_deploy.items():
        print(f"[{agent_name}]")
        result = _deploy_agent(agent_name, module_path, args.env, openai_key)
        results.append(result)
        print()

    # Summary
    deployed = sum(1 for r in results if r["status"] == "deployed")
    failed = sum(1 for r in results if r["status"] == "failed")
    print(f"Summary: {deployed} deployed, {failed} failed")

    if failed:
        sys.exit(1)

    # Print AGENT_URL env vars for gateway configuration
    print("\nGateway AGENT_URL environment variables:")
    for r in results:
        if r["status"] == "deployed" and r.get("fqdn"):
            agent_type = r["name"].replace("agent-red-", "")
            env_name = f"AGENT_{agent_type.upper().replace('-', '_')}_URL"
            print(f"  {env_name}=https://{r['fqdn']}")


if __name__ == "__main__":
    main()
