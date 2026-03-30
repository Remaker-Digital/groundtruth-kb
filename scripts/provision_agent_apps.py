"""Provision 6 Azure Container Apps for agent containers.

Creates or updates Container Apps for each agent in the Agent Red
pipeline. Each app connects to the shared NATS/SLIM transport and
exposes its agent-specific endpoints.

Usage:
    python scripts/provision_agent_apps.py [--env staging|production] [--tag VERSION]

SPEC-1535: Containerized Agent Deployment
WI-0846: Provision Azure Container Apps for 6 agents

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys

# Windows cp1252 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Azure infrastructure
SUBSCRIPTION = "4dce2122-690a-4654-b531-cc647db62331"
RESOURCE_GROUP = "rg-agentred-eastus"
ACR_REGISTRY = "acragentredeastus.azurecr.io"
IMAGE_PREFIX = "agent-red"

ENVIRONMENTS = {
    "staging": {
        "container_app_env": "agent-red-staging-env",
        "min_replicas": 0,
        "max_replicas": 1,
    },
    "production": {
        "container_app_env": "agent-red-prod-env",
        "min_replicas": 1,
        "max_replicas": 3,
    },
}

# Agent containers listen on 8080 inside ACA; the ingress proxy handles
# the external/internal routing surface separately.
AGENT_PORT = 8080
DEFAULT_NATS_ENDPOINT = "ws://agent-red-nats"

# Agent configurations: (name, port, cpu, memory)
AGENT_APPS = [
    ("intent-classifier", AGENT_PORT, "0.25", "0.5Gi"),
    ("knowledge-retrieval", AGENT_PORT, "0.5", "1.0Gi"),
    ("response-generator", AGENT_PORT, "0.5", "1.0Gi"),
    ("escalation-handler", AGENT_PORT, "0.25", "0.5Gi"),
    ("analytics-collector", AGENT_PORT, "0.25", "0.5Gi"),
    ("critic-supervisor", AGENT_PORT, "0.25", "0.5Gi"),
]


def provision_app(
    name: str,
    port: int,
    cpu: str,
    memory: str,
    env_name: str,
    tag: str,
    env_config: dict,
    nats_endpoint: str,
) -> bool:
    """Provision a single agent Container App."""
    app_name = f"agent-red-{name}"
    image = f"{ACR_REGISTRY}/{IMAGE_PREFIX}-{name}:{tag}"

    print(f"\n{'='*60}")
    print(f"Provisioning {app_name}")
    print(f"  Image:    {image}")
    print(f"  Port:     {port}")
    print(f"  CPU/Mem:  {cpu} / {memory}")
    print(f"  Replicas: {env_config['min_replicas']}-{env_config['max_replicas']}")
    print(f"{'='*60}")

    cmd = [
        "az", "containerapp", "create",
        "--name", app_name,
        "--resource-group", RESOURCE_GROUP,
        "--environment", env_config["container_app_env"],
        "--image", image,
        "--registry-server", ACR_REGISTRY,
        "--target-port", str(port),
        "--ingress", "internal",
        "--min-replicas", str(env_config["min_replicas"]),
        "--max-replicas", str(env_config["max_replicas"]),
        "--cpu", cpu,
        "--memory", memory,
        "--env-vars",
        f"AGENT_PORT={port}",
        f"AGNTCY_NATS_ENDPOINT={nats_endpoint}",
        f"NATS_URL={nats_endpoint}",
        "AGNTCY_TRANSPORT_TYPE=slim",
        "LOG_LEVEL=INFO",
        "--subscription", SUBSCRIPTION,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            # May already exist — try update instead
            if "already exists" in result.stderr or "Conflict" in result.stderr:
                print(f"  App exists, updating revision...")
                update_cmd = [
                    "az", "containerapp", "update",
                    "--name", app_name,
                    "--resource-group", RESOURCE_GROUP,
                    "--image", image,
                    "--min-replicas", str(env_config["min_replicas"]),
                    "--max-replicas", str(env_config["max_replicas"]),
                    "--subscription", SUBSCRIPTION,
                ]
                update_result = subprocess.run(
                    update_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if update_result.returncode != 0:
                    print(f"  UPDATE FAILED: {update_result.stderr[:500]}")
                    return False
                print(f"  OK (updated)")
                return True
            print(f"  FAILED: {result.stderr[:500]}")
            return False
        print(f"  OK (created)")
        return True
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after 5 minutes")
        return False
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision agent Container Apps")
    parser.add_argument(
        "--env", choices=["staging", "production"], default="staging",
        help="Target environment",
    )
    parser.add_argument("--tag", type=str, default=None, help="Image tag")
    parser.add_argument("--agent", type=str, default=None, help="Provision only this agent")
    parser.add_argument(
        "--nats-endpoint",
        type=str,
        default=None,
        help="Override the NATS WebSocket endpoint (default: AGNTCY_NATS_ENDPOINT/NATS_URL env or ws://agent-red-nats)",
    )
    args = parser.parse_args()

    env_config = ENVIRONMENTS[args.env]
    tag = args.tag or "latest"
    nats_endpoint = (
        args.nats_endpoint
        or os.environ.get("AGNTCY_NATS_ENDPOINT")
        or os.environ.get("NATS_URL")
        or DEFAULT_NATS_ENDPOINT
    )

    print(f"Agent Container Provisioning")
    print(f"Environment: {args.env}")
    print(f"Tag: {tag}")
    print(f"Container App Env: {env_config['container_app_env']}")
    print(f"NATS endpoint: {nats_endpoint}")

    results: list[tuple[str, bool]] = []
    for name, port, cpu, memory in AGENT_APPS:
        if args.agent and args.agent != name:
            continue
        ok = provision_app(name, port, cpu, memory, args.env, tag, env_config, nats_endpoint)
        results.append((name, ok))

    # Summary
    print(f"\n{'='*60}")
    print("Provisioning Summary")
    print(f"{'='*60}")
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    for name, ok in results:
        status = "OK" if ok else "FAILED"
        print(f"  {name}: {status}")
    print(f"\nTotal: {passed} OK, {failed} FAILED")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
