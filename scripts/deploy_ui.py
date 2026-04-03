#!/usr/bin/env python3
"""Deploy UI components independently — SMOKE HELPER ONLY (S251 OM-1).

WARNING: This script is a UI deployment smoke helper. Its verify command
proves static asset reachability and widget config auth, but it does NOT
prove end-to-end widget conversation readiness. The canonical production
GO/NO-GO path is: scripts/release_pipeline.py

Implements SPEC-1705: Local UI development and staging deployment without
full build. Uses Dockerfile.ui to overlay only the UI dist directories on
top of the existing production image, reducing build+deploy from ~5-8 min
to ~30-60 seconds.

Usage:
    python scripts/deploy_ui.py build                    # Build all UI components
    python scripts/deploy_ui.py build --only standalone   # Build one component
    python scripts/deploy_ui.py deploy --env staging      # Deploy to staging
    python scripts/deploy_ui.py verify --env staging      # Verify deployment
    python scripts/deploy_ui.py status                   # Show component status

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import pathlib
import subprocess
import sys
import time
import urllib.request
import urllib.error

logger = logging.getLogger("deploy_ui")

# ---------------------------------------------------------------------------
# Project root (repo root, one level above scripts/)
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Component registry
# ---------------------------------------------------------------------------
COMPONENTS: dict[str, dict] = {
    "standalone": {
        "source_dir": ROOT / "admin" / "standalone",
        "dist_dir": ROOT / "admin" / "standalone" / "dist",
        "build_cmd": "npm run build",
        "dev_port": 3300,
        "label": "Standalone Admin SPA",
    },
    "provider": {
        "source_dir": ROOT / "admin" / "provider",
        "dist_dir": ROOT / "admin" / "provider" / "dist",
        "build_cmd": "npm run build",
        "dev_port": 3400,
        "label": "Provider Admin SPA",
    },
    "shopify": {
        "source_dir": ROOT / "admin" / "shopify",
        "dist_dir": ROOT / "admin" / "shopify" / "dist",
        "build_cmd": "npm run build",
        "dev_port": 3200,
        "label": "Shopify Embedded Admin SPA",
    },
    "widget": {
        "source_dir": ROOT / "widget",
        "dist_dir": ROOT / "widget" / "dist",
        "build_cmd": "npm run build",
        "dev_port": 3100,
        "label": "Chat Widget Bundle",
    },
}

# ---------------------------------------------------------------------------
# Environment registry
# ---------------------------------------------------------------------------
ENVIRONMENTS: dict[str, dict] = {
    "staging": {
        "container_app": "agent-red-staging",
        "resource_group": "Agent-Red",
        "registry": "acragentredeastus.azurecr.io",
        "fqdn": "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
    },
    "production": {
        "container_app": "agent-red-api-gateway",
        "resource_group": "Agent-Red",
        "registry": "acragentredeastus.azurecr.io",
        "fqdn": "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
    },
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _hash_directory(path: pathlib.Path) -> str:
    """Return a truncated SHA-256 hex digest of all files under *path*."""
    h = hashlib.sha256()
    if not path.is_dir():
        return "missing"
    for f in sorted(path.rglob("*")):
        if f.is_file():
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


def _dir_size(path: pathlib.Path) -> int:
    """Return total size in bytes of all files under *path*."""
    if not path.is_dir():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _human_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _run(
    cmd: str,
    *,
    cwd: pathlib.Path | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    """Run a shell command with logging."""
    logger.info("  $ %s", cmd)
    return subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=capture,
        text=True,
    )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build_component(name: str) -> dict:
    """Build a single UI component and return build metadata.

    Returns dict with keys: name, hash, size, duration_s, dist_dir.
    """
    if name not in COMPONENTS:
        raise ValueError(f"Unknown component: {name!r}. Choose from: {list(COMPONENTS)}")

    comp = COMPONENTS[name]
    source_dir = comp["source_dir"]
    dist_dir = comp["dist_dir"]

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    # Install deps if node_modules missing
    node_modules = source_dir / "node_modules"
    if not node_modules.is_dir():
        logger.info("[%s] Installing dependencies...", name)
        _run("npm install", cwd=source_dir)

    logger.info("[%s] Building %s...", name, comp["label"])
    t0 = time.monotonic()
    _run(comp["build_cmd"], cwd=source_dir)
    duration = time.monotonic() - t0

    if not dist_dir.is_dir():
        raise RuntimeError(f"Build did not produce dist directory: {dist_dir}")

    content_hash = _hash_directory(dist_dir)
    size = _dir_size(dist_dir)
    logger.info(
        "[%s] Built in %.1fs  hash=%s  size=%s",
        name, duration, content_hash, _human_size(size),
    )
    return {
        "name": name,
        "hash": content_hash,
        "size": size,
        "size_human": _human_size(size),
        "duration_s": round(duration, 1),
        "dist_dir": str(dist_dir),
    }


def build_all(components: list[str] | None = None) -> list[dict]:
    """Build multiple components sequentially. Defaults to all."""
    names = components or list(COMPONENTS.keys())
    results = []
    for name in names:
        results.append(build_component(name))
    return results


# ---------------------------------------------------------------------------
# Status / hashing
# ---------------------------------------------------------------------------


def get_ui_status() -> dict[str, dict]:
    """Return the current state of all UI component dist directories."""
    status = {}
    for name, comp in COMPONENTS.items():
        dist = comp["dist_dir"]
        exists = dist.is_dir()
        status[name] = {
            "label": comp["label"],
            "dist_dir": str(dist),
            "exists": exists,
            "hash": _hash_directory(dist) if exists else None,
            "size": _dir_size(dist) if exists else 0,
            "size_human": _human_size(_dir_size(dist)) if exists else "0 B",
        }
    return status


def get_combined_ui_hash() -> str:
    """Return a short combined hash of all dist directories."""
    combined = hashlib.sha256()
    for name in sorted(COMPONENTS.keys()):
        dist = COMPONENTS[name]["dist_dir"]
        combined.update(_hash_directory(dist).encode())
    return combined.hexdigest()[:8]


# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------


def deploy_ui(
    env: str,
    base_version: str,
    suffix: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Build a UI-only Docker image and deploy it.

    Args:
        env: Target environment ("staging" or "production").
        base_version: The base image version tag (e.g. "v1.81.2").
        suffix: Optional tag suffix. Defaults to "ui" + combined hash.
        dry_run: If True, print commands but do not execute.

    Returns:
        Dict with image_tag, deploy_cmd, and status.
    """
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: {env!r}. Choose from: {list(ENVIRONMENTS)}")

    env_cfg = ENVIRONMENTS[env]
    registry = env_cfg["registry"]

    # Verify all dist directories exist
    missing = []
    for name, comp in COMPONENTS.items():
        if not comp["dist_dir"].is_dir():
            missing.append(name)
    if missing:
        raise FileNotFoundError(
            f"Missing dist directories for: {missing}. "
            f"Run 'deploy_ui.py build' first."
        )

    # Construct image tag
    ui_hash = get_combined_ui_hash()
    tag_suffix = suffix or f"ui{ui_hash}"
    base_image = f"{registry}/api-gateway:{base_version}"
    new_tag = f"{base_version}-{tag_suffix}"
    new_image = f"{registry}/api-gateway:{new_tag}"

    dockerfile_ui = ROOT / "Dockerfile.ui"
    if not dockerfile_ui.is_file():
        raise FileNotFoundError(f"Dockerfile.ui not found at {dockerfile_ui}")

    # ACR build command
    acr_cmd = (
        f"az acr build"
        f" --registry acragentredeastus"
        f" --image api-gateway:{new_tag}"
        f" --file Dockerfile.ui"
        f" --build-arg BASE_IMAGE={base_image}"
        f" --no-logs"
        f" ."
    )

    # Container App update command
    deploy_cmd = (
        f"az containerapp update"
        f" --name {env_cfg['container_app']}"
        f" --resource-group {env_cfg['resource_group']}"
        f" --image {new_image}"
    )

    logger.info("=== UI-Only Deploy to %s ===", env.upper())
    logger.info("Base image:  %s", base_image)
    logger.info("New image:   %s", new_image)
    logger.info("UI hash:     %s", ui_hash)

    if dry_run:
        logger.info("[DRY RUN] Would execute:")
        logger.info("  %s", acr_cmd)
        logger.info("  %s", deploy_cmd)
        return {
            "status": "dry_run",
            "base_image": base_image,
            "new_image": new_image,
            "ui_hash": ui_hash,
            "acr_cmd": acr_cmd,
            "deploy_cmd": deploy_cmd,
        }

    # Step 1: ACR cloud build
    logger.info("Step 1/2: Building UI overlay image in ACR...")
    t0 = time.monotonic()
    _run(acr_cmd, cwd=ROOT)
    build_time = time.monotonic() - t0
    logger.info("ACR build completed in %.1fs", build_time)

    # Step 2: Deploy to Container App
    logger.info("Step 2/2: Deploying to %s...", env_cfg["container_app"])
    _run(deploy_cmd)
    logger.info("Deploy command submitted. Waiting 30s for revision activation...")
    time.sleep(30)

    return {
        "status": "deployed",
        "base_image": base_image,
        "new_image": new_image,
        "ui_hash": ui_hash,
        "build_time_s": round(build_time, 1),
        "acr_cmd": acr_cmd,
        "deploy_cmd": deploy_cmd,
    }


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------


def verify_deployment(env: str) -> dict:
    """Verify UI deployment by checking health and admin console endpoints.

    Returns dict with endpoint statuses.
    """
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: {env!r}")

    fqdn = ENVIRONMENTS[env]["fqdn"]
    base_url = f"https://{fqdn}"

    checks = {
        "health": f"{base_url}/health",
        "admin_standalone": f"{base_url}/admin/standalone/",
        "admin_provider": f"{base_url}/admin/provider/",
        "admin_shopify": f"{base_url}/admin/shopify/",
        "widget_js": f"{base_url}/widget.js",
    }

    results = {}
    for name, url in checks.items():
        try:
            req = urllib.request.Request(url, method="GET")
            req.add_header("User-Agent", "deploy-ui-verify/1.0")
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.getcode()
                results[name] = {"url": url, "status": status, "ok": 200 <= status < 400}
                logger.info("  [%s] %s -> %d", "OK" if results[name]["ok"] else "FAIL", name, status)
        except urllib.error.HTTPError as e:
            results[name] = {"url": url, "status": e.code, "ok": False}
            logger.warning("  [FAIL] %s -> HTTP %d", name, e.code)
        except Exception as e:
            results[name] = {"url": url, "status": 0, "ok": False, "error": str(e)}
            logger.warning("  [FAIL] %s -> %s", name, e)

    # Widget config auth check — verifies widget key auth works on /api/config
    # (S251: the exact failure mode diagnosed when the admin widget returned 401)
    # Environment-specific key resolution (mirrors deploy.py pattern)
    widget_key = os.environ.get("DEPLOY_SMOKE_WIDGET_KEY", "")
    if not widget_key:
        if env == "staging":
            widget_key = os.environ.get("STAGING_REMAKER_WIDGET_KEY", "")
        elif env == "production":
            widget_key = os.environ.get("PRODUCTION_WIDGET_KEY", "")

    if widget_key:
        config_url = f"{base_url}/api/config?page_type=all"
        try:
            req = urllib.request.Request(config_url, method="GET")
            req.add_header("X-Widget-Key", widget_key)
            req.add_header("User-Agent", "deploy-ui-verify/1.0")
            with urllib.request.urlopen(req, timeout=15) as resp:
                status = resp.getcode()
                results["widget_config_auth"] = {"url": config_url, "status": status, "ok": status == 200}
                logger.info("  [%s] widget_config_auth -> %d", "OK" if status == 200 else "FAIL", status)
        except urllib.error.HTTPError as e:
            results["widget_config_auth"] = {"url": config_url, "status": e.code, "ok": False}
            logger.warning("  [FAIL] widget_config_auth -> HTTP %d", e.code)
        except Exception as e:
            results["widget_config_auth"] = {"url": config_url, "status": 0, "ok": False, "error": str(e)}
            logger.warning("  [FAIL] widget_config_auth -> %s", e)
    else:
        # No widget key = hard fail (not a skip). Widget verification is mandatory.
        results["widget_config_auth"] = {
            "url": f"{base_url}/api/config", "status": 0, "ok": False,
            "error": "No widget key configured (set DEPLOY_SMOKE_WIDGET_KEY or environment-specific key)",
        }
        logger.warning("  [FAIL] widget_config_auth — no widget key configured")

    passed = sum(1 for k, r in results.items() if k != "summary" and isinstance(r, dict) and r.get("ok"))
    total = sum(1 for k, r in results.items() if k != "summary" and isinstance(r, dict))
    results["summary"] = {"passed": passed, "total": total, "all_ok": passed == total}
    logger.info("Verification: %d/%d passed", passed, total)
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deploy UI components without a full system build (SPEC-1705).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- build ---
    p_build = sub.add_parser("build", help="Build UI components locally")
    p_build.add_argument(
        "--only", choices=list(COMPONENTS.keys()),
        help="Build a single component instead of all",
    )

    # --- deploy ---
    p_deploy = sub.add_parser("deploy", help="Deploy UI overlay to an environment")
    p_deploy.add_argument("--env", required=True, choices=list(ENVIRONMENTS.keys()))
    p_deploy.add_argument("--base-version", required=True, help="Base image version (e.g. v1.81.2)")
    p_deploy.add_argument("--suffix", help="Custom tag suffix (default: uiHASH)")
    p_deploy.add_argument("--dry-run", action="store_true", help="Print commands without executing")

    # --- verify ---
    p_verify = sub.add_parser("verify", help="Verify UI deployment health")
    p_verify.add_argument("--env", required=True, choices=list(ENVIRONMENTS.keys()))

    # --- status ---
    sub.add_parser("status", help="Show current UI component status")

    args = parser.parse_args(argv)
    _setup_logging(args.verbose)

    if args.command == "build":
        components = [args.only] if args.only else None
        results = build_all(components)
        for r in results:
            print(f"  {r['name']:12s}  hash={r['hash']}  size={r['size_human']}  time={r['duration_s']}s")
        return 0

    if args.command == "deploy":
        result = deploy_ui(
            env=args.env,
            base_version=args.base_version,
            suffix=args.suffix,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "verify":
        result = verify_deployment(args.env)
        print(json.dumps(result, indent=2))
        return 0 if result.get("summary", {}).get("all_ok") else 1

    if args.command == "status":
        status = get_ui_status()
        for name, info in status.items():
            mark = "OK" if info["exists"] else "MISSING"
            print(f"  [{mark:7s}] {name:12s}  hash={info['hash'] or 'n/a':12s}  size={info['size_human']}")
        combined = get_combined_ui_hash()
        print(f"\n  Combined UI hash: {combined}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
