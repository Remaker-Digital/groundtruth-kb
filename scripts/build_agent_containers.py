"""Build and push 6 agent container images to Azure Container Registry.

Each agent runs as an independent container using the shared agent_app.py
factory with its specific agent class. Images are tagged with the product
version and pushed to ACR for deployment as Azure Container Apps.

Usage:
    python scripts/build_agent_containers.py [--push] [--tag VERSION]

SPEC-1535: Containerized Agent Deployment
WI-0845: Build and push 6 agent container images to ACR

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys

# Windows cp1252 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Agent container configurations: (name, entry_module, port)
AGENT_CONTAINERS = [
    ("intent-classifier", "src.agents.containers.intent_classifier_app", 8081),
    ("knowledge-retrieval", "src.agents.containers.knowledge_retrieval_app", 8082),
    ("response-generator", "src.agents.containers.response_generator_app", 8083),
    ("escalation-handler", "src.agents.containers.escalation_handler_app", 8084),
    ("analytics-collector", "src.agents.containers.analytics_collector_app", 8085),
    ("critic-supervisor", "src.agents.containers.critic_supervisor_app", 8086),
]

ACR_REGISTRY = "acragentredeastus.azurecr.io"
IMAGE_PREFIX = "agent-red"


def get_product_version() -> str:
    """Read the current product version from api_versioning.py."""
    try:
        sys.path.insert(0, ".")
        from src.multi_tenant.api_versioning import PRODUCT_VERSION

        return PRODUCT_VERSION
    except ImportError:
        return "dev"


def build_image(name: str, entry_module: str, port: int, tag: str, push: bool) -> bool:
    """Build a single agent container image via ACR build."""
    image_name = f"{IMAGE_PREFIX}-{name}"
    full_tag = f"{ACR_REGISTRY}/{image_name}:{tag}"

    print(f"\n{'=' * 60}")
    print(f"Building {image_name}:{tag}")
    print(f"  Entry: {entry_module}")
    print(f"  Port:  {port}")
    print(f"  Image: {full_tag}")
    print(f"{'=' * 60}")

    # Build using az acr build (no-logs to avoid Windows charmap crash)
    build_cmd = [
        "az",
        "acr",
        "build",
        "--registry",
        "acragentredeastus",
        "--image",
        f"{image_name}:{tag}",
        "--build-arg",
        f"AGENT_MODULE={entry_module}",
        "--build-arg",
        f"AGENT_PORT={port}",
        "--file",
        "Dockerfile.agent",
        "--no-logs",
        ".",
    ]

    if push:
        print(f"  Building + pushing to ACR...")
    else:
        print(f"  Building (no push)...")
        build_cmd = [
            "docker",
            "build",
            "--build-arg",
            f"AGENT_MODULE={entry_module}",
            "--build-arg",
            f"AGENT_PORT={port}",
            "-f",
            "Dockerfile.agent",
            "-t",
            full_tag,
            ".",
        ]

    try:
        result = subprocess.run(
            build_cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            print(f"  FAILED: {result.stderr[:500]}")
            return False
        print(f"  OK")
        return True
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after 10 minutes")
        return False
    except Exception as exc:
        print(f"  ERROR: {exc}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Build agent container images")
    parser.add_argument("--push", action="store_true", help="Push to ACR (uses az acr build)")
    parser.add_argument("--tag", type=str, default=None, help="Image tag (default: product version)")
    parser.add_argument("--agent", type=str, default=None, help="Build only this agent (by name)")
    args = parser.parse_args()

    tag = args.tag or get_product_version()
    print(f"Agent Container Build — tag: {tag}")
    print(f"Registry: {ACR_REGISTRY}")
    print(f"Agents: {len(AGENT_CONTAINERS)}")

    results: list[tuple[str, bool]] = []
    for name, module, port in AGENT_CONTAINERS:
        if args.agent and args.agent != name:
            continue
        ok = build_image(name, module, port, tag, args.push)
        results.append((name, ok))

    # Summary
    print(f"\n{'=' * 60}")
    print("Build Summary")
    print(f"{'=' * 60}")
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
