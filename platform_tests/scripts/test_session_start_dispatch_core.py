# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/session_start_dispatch_core.py — WI-4564 Part A.

Part A of the WI-4564 startup-service timeout alignment (bridge thread
``gtkb-wi4564-startup-service-timeout-and-fanout``, GO at -004) makes the inner
subprocess timeout env-configurable and raises its default so the inner bound
no longer fires ~3.6x short of the 180 s ``asyncTimeout`` the SessionStart hook
allows. These spec-derived tests cover the resolver
``_startup_service_timeout_seconds`` and the budget-aligned default.

Spec linkage (per the GO'd proposal -003 verification plan):
- GOV-RELIABILITY-FAST-LANE-001 / PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001:
  the timeout resolves from ``GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS`` when set
  and falls back to the raised 150.0 default when unset/invalid/non-positive.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_start_dispatch_core.py"


def _load_module():
    # The core module imports in-root ``scripts.*`` helpers, so REPO_ROOT must
    # be importable as the ``scripts`` package parent.
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("session_start_dispatch_core", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_start_dispatch_core"] = module
    spec.loader.exec_module(module)
    return module


def test_timeout_env_name_and_default_constant() -> None:
    """The env var name is canonical and the default is the raised 150.0 budget."""

    module = _load_module()
    assert module.STARTUP_SERVICE_TIMEOUT_ENV == "GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS"
    # Raised from the prior 50.0 to ~30 s under the 180 s asyncTimeout budget.
    assert module.STARTUP_SERVICE_TIMEOUT_SECONDS == 150.0


def test_timeout_falls_back_to_default_when_unset(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.delenv(module.STARTUP_SERVICE_TIMEOUT_ENV, raising=False)
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)


def test_timeout_reads_env_when_set(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "200")
    assert module._startup_service_timeout_seconds() == pytest.approx(200.0)


def test_timeout_reads_fractional_env(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "75.5")
    assert module._startup_service_timeout_seconds() == pytest.approx(75.5)


def test_timeout_invalid_value_falls_back(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "not-a-number")
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)


def test_timeout_blank_value_falls_back(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, "   ")
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)


@pytest.mark.parametrize("value", ["0", "-5", "-0.1"])
def test_timeout_non_positive_falls_back(monkeypatch, value) -> None:
    """A non-positive override is rejected so the wait is never zero/negative."""

    module = _load_module()
    monkeypatch.setenv(module.STARTUP_SERVICE_TIMEOUT_ENV, value)
    assert module._startup_service_timeout_seconds() == pytest.approx(150.0)
