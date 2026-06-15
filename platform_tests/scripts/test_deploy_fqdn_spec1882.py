# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-4572 regression: deploy FQDN routed through the deploy_config SoT (SPEC-1882).

SPEC-1882 declares ``scripts/deploy_config.py`` the single source of truth for
deployment environment config: "No hardcoded tenant IDs, FQDNs, or credential
env var names anywhere else." Four live deploy/verify scripts had drifted out of
compliance by carrying their own Container Apps FQDN literal. WI-4572 routed all
four through ``deploy_config.get_environment(env)["fqdn"]`` and made the SoT
FQDNs env-overridable (defaults preserve the current hostnames).

This test enforces the SPEC-1882 contract going forward.

Authority: bridge/gtkb-wi4572-deploy-fqdn-spec1882-config-ization-002.md (GO).
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# conftest.py auto-injects REPO_ROOT onto sys.path; resolve it explicitly too so
# the source-text scans below do not depend on import side effects.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# The Container Apps hostname suffix that marks a deploy-target FQDN literal.
_FQDN_SUFFIX = "azurecontainerapps.io"

# Current (default) FQDN literals — must live ONLY in the SoT.
_STAGING_FQDN = "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"
_PRODUCTION_FQDN = "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"

_SOT = REPO_ROOT / "scripts" / "deploy_config.py"

# The four scripts WI-4572 brought into compliance.
_REFACTORED_SCRIPTS = [
    REPO_ROOT / "scripts" / "deploy.py",
    REPO_ROOT / "scripts" / "deploy_ui.py",
    REPO_ROOT / "scripts" / "repair_widget_hash.py",
    REPO_ROOT / "scripts" / "test_run.py",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("script", _REFACTORED_SCRIPTS, ids=lambda p: p.name)
def test_no_hardcoded_fqdn_in_deploy_scripts(script: Path) -> None:
    """No Container Apps FQDN literal remains in any of the four refactored scripts."""
    source = _read(script)
    assert _FQDN_SUFFIX not in source, (
        f"{script.name} still contains a hardcoded '{_FQDN_SUFFIX}' FQDN literal; "
        "SPEC-1882 requires reading it from deploy_config (WI-4572)."
    )


@pytest.mark.parametrize("script", _REFACTORED_SCRIPTS, ids=lambda p: p.name)
def test_scripts_source_fqdn_from_deploy_config(script: Path) -> None:
    """Each refactored script sources the FQDN from deploy_config's get_environment."""
    source = _read(script)
    assert "deploy_config" in source, f"{script.name} does not reference deploy_config"
    assert "get_environment" in source, f"{script.name} does not call get_environment()"
    assert '["fqdn"]' in source, f"{script.name} does not read the ['fqdn'] field from the SoT"


def test_deploy_config_fqdn_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """deploy_config FQDNs are env-overridable; the default preserves the current value."""
    import scripts.deploy_config as deploy_config

    # Default (no override) must equal the current hostnames — behavior preservation.
    monkeypatch.delenv("STAGING_FQDN", raising=False)
    monkeypatch.delenv("PRODUCTION_FQDN", raising=False)
    deploy_config = importlib.reload(deploy_config)
    assert deploy_config.get_environment("staging")["fqdn"] == _STAGING_FQDN
    assert deploy_config.get_environment("production")["fqdn"] == _PRODUCTION_FQDN

    # With overrides set, get_environment returns the override (setdefault loader
    # keeps shell env precedence, so .env.local cannot mask these).
    monkeypatch.setenv("STAGING_FQDN", "staging.example.test")
    monkeypatch.setenv("PRODUCTION_FQDN", "production.example.test")
    try:
        deploy_config = importlib.reload(deploy_config)
        assert deploy_config.get_environment("staging")["fqdn"] == "staging.example.test"
        assert deploy_config.get_environment("production")["fqdn"] == "production.example.test"
    finally:
        # Restore the module to its default-env state for later tests in the session.
        monkeypatch.delenv("STAGING_FQDN", raising=False)
        monkeypatch.delenv("PRODUCTION_FQDN", raising=False)
        importlib.reload(deploy_config)


def test_deploy_config_is_sole_fqdn_source() -> None:
    """The staging/production FQDN literals live in deploy_config and nowhere else."""
    sot_source = _read(_SOT)
    assert _STAGING_FQDN in sot_source, "staging FQDN default missing from deploy_config SoT"
    assert _PRODUCTION_FQDN in sot_source, "production FQDN default missing from deploy_config SoT"

    for script in _REFACTORED_SCRIPTS:
        source = _read(script)
        assert _STAGING_FQDN not in source, f"staging FQDN literal leaked into {script.name}"
        assert _PRODUCTION_FQDN not in source, f"production FQDN literal leaked into {script.name}"
