"""Tests for the Ollama harness 4-store consistency doctor check (WI-4323).

Spec-derived tests for ``_check_ollama_harness`` per the Phase-1 Child 3
proposal (bridge/gtkb-ollama-integration-phase-1-verification-005.md) and
the GO verdict (bridge/gtkb-ollama-integration-phase-1-verification-006.md).

The check is 4-layer + cross-store consistency:

- L1 — identity store: ``harness-state/harness-identities.json`` has ``ollama → D``.
- L2 — registry store: ``harness-state/harness-registry.json`` has ``id=D`` with
  ``harness_name=ollama``, ``harness_type=ollama``, ``status=registered``,
  ``role=[]``.
- L3 — capability registry: ``config/agent-control/harness-capability-registry.toml``
  has ``[harnesses.ollama]`` with the four Phase-1 capability-floor keys.
- L4 — routing TOML: ``.ollama/routing.toml`` parseable with at least one
  ``tool_calling_supported=true`` model.
- Cross-store drift: identities-vs-registry consistency.

Layer 4b (advertised-model verification) is reachability-gated; tests neither
require nor exercise a live Ollama daemon.

Severity is ``warning`` per the Phase-1 rollout convention.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.project.doctor import _check_ollama_harness


@pytest.fixture(autouse=True)
def _skip_l4b_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    """Auto-skip the L4b advertised-model probe in unit tests.

    Without this fixture, the doctor check probes the local
    ``http://localhost:11434/api/tags`` endpoint when routing models are
    present in the fixture. If the developer's machine happens to have
    Ollama running with a different model set, the probe surfaces a
    spurious advertised-model finding that has nothing to do with the
    fixture's correctness.
    """
    monkeypatch.setenv("GTKB_DOCTOR_OLLAMA_SKIP_PROBE", "1")
    monkeypatch.setenv("GTKB_DOCTOR_OLLAMA_SKIP_HOST_READINESS", "1")


def _write_clean_ollama_fixtures(root: Path) -> None:
    """Create a 4-store fixture set with all stores consistent and clean."""
    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "ollama": {
                        "id": "D",
                        "assigned_at": "2026-06-05T05:11:00Z",
                        "assigned_by": "fixture",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "status": "registered",
                        "role": [],
                        "event_driven_hooks": False,
                        "invocation_surfaces": {},
                        "reviewer_precedence": None,
                        "version": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "config" / "agent-control").mkdir(parents=True, exist_ok=True)
    (root / "config" / "agent-control" / "harness-capability-registry.toml").write_text(
        "[harnesses.ollama]\n"
        "bridge_compliance_gate_respect = true\n"
        "root_boundary_respect = true\n"
        "author_metadata_env_var_setting = true\n"
        "destructive_gate_delegation = true\n",
        encoding="utf-8",
    )
    (root / ".ollama").mkdir(parents=True, exist_ok=True)
    (root / ".ollama" / "routing.toml").write_text(
        "schema_version = 1\n"
        "\n"
        "[models.qwen-coder-14b]\n"
        'model_id = "qwen2.5-coder:14b-instruct-q4_K_M"\n'
        'model_version = "q4_K_M"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "\n"
        "[routing]\n"
        'default_model = "qwen-coder-14b"\n',
        encoding="utf-8",
    )


def test_clean_4_store_returns_pass(tmp_path: Path) -> None:
    """All four stores present, consistent, and well-formed → PASS."""
    _write_clean_ollama_fixtures(tmp_path)
    result = _check_ollama_harness(tmp_path)
    assert result.status == "pass", f"expected pass, got {result.status}: {result.message}"
    assert "clean" in result.message.lower()


def test_missing_identity_returns_warning(tmp_path: Path) -> None:
    """L1: missing identities file surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    (tmp_path / "harness-state" / "harness-identities.json").unlink()
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L1" in result.message


def test_identity_wrong_id_returns_warning(tmp_path: Path) -> None:
    """L1: identities store with wrong id (E instead of D) surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    (tmp_path / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"ollama": {"id": "E"}}}),
        encoding="utf-8",
    )
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L1" in result.message


def test_registry_status_drift_returns_warning(tmp_path: Path) -> None:
    """L2: registry status drift (active instead of registered) surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    registry = json.loads((tmp_path / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    registry["harnesses"][0]["status"] = "active"
    (tmp_path / "harness-state" / "harness-registry.json").write_text(json.dumps(registry), encoding="utf-8")
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L2" in result.message
    assert "status" in result.message.lower()


def test_registry_role_drift_returns_warning(tmp_path: Path) -> None:
    """L2: registry role drift (non-empty role) surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    registry = json.loads((tmp_path / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    registry["harnesses"][0]["role"] = ["prime-builder"]
    (tmp_path / "harness-state" / "harness-registry.json").write_text(json.dumps(registry), encoding="utf-8")
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L2" in result.message
    assert "role" in result.message.lower()


def test_capability_missing_section_returns_warning(tmp_path: Path) -> None:
    """L3: capability registry missing [harnesses.ollama] surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    (tmp_path / "config" / "agent-control" / "harness-capability-registry.toml").write_text(
        "[harnesses.claude]\nplaceholder = true\n", encoding="utf-8"
    )
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L3" in result.message


def test_capability_missing_keys_returns_warning(tmp_path: Path) -> None:
    """L3: [harnesses.ollama] missing one or more floor keys surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    (tmp_path / "config" / "agent-control" / "harness-capability-registry.toml").write_text(
        "[harnesses.ollama]\nbridge_compliance_gate_respect = true\n",
        encoding="utf-8",
    )
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L3" in result.message


def test_routing_missing_returns_warning(tmp_path: Path) -> None:
    """L4: routing TOML missing surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    (tmp_path / ".ollama" / "routing.toml").unlink()
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L4" in result.message


def test_routing_no_tool_calling_returns_warning(tmp_path: Path) -> None:
    """L4: routing TOML with no tool_calling_supported=true models surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    (tmp_path / ".ollama" / "routing.toml").write_text(
        "schema_version = 1\n"
        "\n"
        "[models.demo]\n"
        'model_id = "demo:latest"\n'
        'model_version = "latest"\n'
        "tool_calling_supported = false\n"
        "allowed_tools = []\n"
        "\n"
        "[routing]\n"
        'default_model = "demo"\n',
        encoding="utf-8",
    )
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L4" in result.message


def test_cross_store_identity_vs_registry_drift(tmp_path: Path) -> None:
    """Cross-store: identities has ollama→D but registry missing id=D."""
    _write_clean_ollama_fixtures(tmp_path)
    # Drop the registry entry for D
    (tmp_path / "harness-state" / "harness-registry.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": []}),
        encoding="utf-8",
    )
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    # Either L2 (registry missing id=D) or Cross-store catches it.
    assert "L2" in result.message or "Cross-store" in result.message


def test_capability_unreadable_returns_warning(tmp_path: Path) -> None:
    """L3: malformed TOML in capability registry surfaces as warning."""
    _write_clean_ollama_fixtures(tmp_path)
    (tmp_path / "config" / "agent-control" / "harness-capability-registry.toml").write_text(
        "this is = = not = valid TOML at all", encoding="utf-8"
    )
    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L3" in result.message


def test_pass_message_mentions_all_four_layers(tmp_path: Path) -> None:
    """The clean-pass message names the layers covered for diagnostic clarity."""
    _write_clean_ollama_fixtures(tmp_path)
    result = _check_ollama_harness(tmp_path)
    assert result.status == "pass"
    assert "L1" in result.message and "L2" in result.message
    assert "L3" in result.message and "L4" in result.message


# ── Layer 4b — advertised-model verification (hermetic, GO@-006 Constraint 4) ─


class _FakeApiTagsResponse:
    """Minimal context-manager response object for a mocked ``/api/tags`` GET.

    Mirrors the shape ``urllib.request.urlopen`` returns: a context manager
    whose ``read()`` returns the JSON body bytes. ``status`` is included for
    parity with ``http.client.HTTPResponse``; the doctor check does not read
    it but real responses carry it.
    """

    def __init__(self, body: bytes) -> None:
        self._body = body
        self.status = 200

    def __enter__(self) -> _FakeApiTagsResponse:
        return self

    def __exit__(self, *exc_info: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._body


def test_advertised_model_present_via_api_tags(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """L4b: when the routing model appears in the mocked ``/api/tags`` response,
    the check stays at ``pass`` (no L4b finding).

    Hermetic test: monkeypatches ``urllib.request.urlopen`` so no live Ollama
    daemon is required. The autouse ``_skip_l4b_probe`` fixture is overridden
    via ``monkeypatch.delenv`` to re-enable the Layer 4b code path.
    """
    _write_clean_ollama_fixtures(tmp_path)
    # Re-enable the L4b probe (override the autouse skip fixture).
    monkeypatch.delenv("GTKB_DOCTOR_OLLAMA_SKIP_PROBE", raising=False)
    body = json.dumps({"models": [{"name": "qwen2.5-coder:14b-instruct-q4_K_M"}]}).encode("utf-8")

    def _fake_urlopen(_url: str, timeout: float = 2.0) -> _FakeApiTagsResponse:
        return _FakeApiTagsResponse(body)

    import urllib.request as _urlreq

    monkeypatch.setattr(_urlreq, "urlopen", _fake_urlopen)

    result = _check_ollama_harness(tmp_path)
    assert result.status == "pass", (
        f"expected pass with advertised model present; got {result.status}: {result.message}"
    )
    assert "L4b" not in result.message, f"unexpected L4b finding when model present: {result.message}"


def test_advertised_model_absent_via_api_tags(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """L4b: when the routing model is missing from the mocked ``/api/tags``
    response, the check returns ``warning`` with an L4b finding.

    Hermetic test: the mock advertises only an unrelated model so the routing
    model is provably absent. The autouse ``_skip_l4b_probe`` fixture is
    overridden via ``monkeypatch.delenv`` to re-enable the Layer 4b code path.
    """
    _write_clean_ollama_fixtures(tmp_path)
    monkeypatch.delenv("GTKB_DOCTOR_OLLAMA_SKIP_PROBE", raising=False)
    body = json.dumps({"models": [{"name": "unrelated-model:latest"}]}).encode("utf-8")

    def _fake_urlopen(_url: str, timeout: float = 2.0) -> _FakeApiTagsResponse:
        return _FakeApiTagsResponse(body)

    import urllib.request as _urlreq

    monkeypatch.setattr(_urlreq, "urlopen", _fake_urlopen)

    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning", (
        f"expected warning with advertised model absent; got {result.status}: {result.message}"
    )
    assert "L4b" in result.message, f"expected L4b finding when routing model absent; got: {result.message}"
    assert "not advertised" in result.message.lower(), f"expected 'not advertised' diagnostic; got: {result.message}"


def test_api_tags_unreachable_returns_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """L4b: unreachable API is an explicit host-readiness warning."""
    import urllib.error
    import urllib.request as _urlreq

    _write_clean_ollama_fixtures(tmp_path)
    monkeypatch.delenv("GTKB_DOCTOR_OLLAMA_SKIP_PROBE", raising=False)

    def _raise_url_error(_url: str, timeout: float = 2.0):  # noqa: ANN202
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(_urlreq, "urlopen", _raise_url_error)

    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L4b" in result.message
    assert "/api/tags unreachable" in result.message


def test_windows_autostart_missing_returns_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """L5: missing Windows task/service is a diagnostic warning."""
    from groundtruth_kb.project import doctor as doctor_mod

    _write_clean_ollama_fixtures(tmp_path)
    monkeypatch.delenv("GTKB_DOCTOR_OLLAMA_SKIP_HOST_READINESS", raising=False)
    monkeypatch.setattr(doctor_mod.sys, "platform", "win32")
    monkeypatch.setattr(doctor_mod.shutil, "which", lambda _name: "powershell.exe")

    def _fake_run(args, **kwargs):  # noqa: ANN001, ANN202
        return doctor_mod.subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"scheduled_tasks":[],"services":[]}',
            stderr="",
        )

    monkeypatch.setattr(doctor_mod.subprocess, "run", _fake_run)

    result = _check_ollama_harness(tmp_path)
    assert result.status == "warning"
    assert "L5" in result.message
    assert "autostart not detected" in result.message
