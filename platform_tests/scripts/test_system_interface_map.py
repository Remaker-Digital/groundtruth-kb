"""Tests for the GT-KB system/interface terminology map."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "resolve_system_interface.py"
REPO_ROOT = Path(__file__).resolve().parents[2]

STARTUP_CONTROL_TERMS = {
    "startup index": ("startup-index", "config/agent-control/SESSION-STARTUP-INDEX.md"),
    "startup control map": ("startup-control-map", "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md"),
    "role overlay": ("startup-role-overlay", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md"),
    "hot-path projection": ("harness-registry-hot-path-projection", "harness-state/harness-registry.json"),
    "repo-local adapter": ("repo-local-adapter", "config/agent-control/harness-capability-registry.toml"),
}


def _load_module():
    spec = importlib.util.spec_from_file_location("resolve_system_interface", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["resolve_system_interface"] = module
    spec.loader.exec_module(module)
    return module


def test_system_interface_map_is_valid_and_seeded() -> None:
    module = _load_module()

    system_map = module.load_map()

    assert module.validate_map(system_map) == []
    row_ids = {row["id"] for row in module.system_rows(system_map)}
    assert row_ids >= module.REQUIRED_SEED_IDS


def test_backlog_row_points_to_unified_work_items_authority() -> None:
    module = _load_module()
    system_map = module.load_map()
    backlog = next(row for row in module.system_rows(system_map) if row["id"] == "backlog")
    combined = " ".join(str(backlog[field]) for field in backlog)

    assert backlog["authoritative_source"] == "MemBase table: current_work_items"
    assert "current_work_items" in combined
    assert "work_items" in combined
    assert "bridge/INDEX.md" in combined
    assert "dashboard/startup rows are summaries" in combined


def test_common_owner_terms_resolve_to_expected_systems() -> None:
    module = _load_module()

    assert module.resolve_term("backlog")["system"]["id"] == "backlog"
    assert module.resolve_term("bridge queue")["system"]["id"] == "bridge-queue"
    assert module.resolve_term("resource registry")["system"]["id"] == "resource-alias-registry"
    assert module.resolve_term("release gate")["system"]["id"] == "release-gate"


def test_startup_control_owner_terms_resolve_to_authoritative_sources() -> None:
    module = _load_module()

    for term, (expected_id, expected_source) in STARTUP_CONTROL_TERMS.items():
        result = module.resolve_term(term)
        assert result["status"] == "resolved"
        assert result["system"]["id"] == expected_id
        assert expected_source in result["system"]["authoritative_source"]


def test_ambiguous_owner_term_fails_closed() -> None:
    module = _load_module()
    system_map = {
        "schema_version": 1,
        "systems": [
            {"id": "first", "canonical_name": "first", "accepted_aliases": ["shared"]},
            {"id": "second", "canonical_name": "second", "accepted_aliases": ["shared"]},
        ],
    }

    result = module.resolve_term("shared", system_map=system_map)

    assert result["status"] == "ambiguous"
    assert {candidate["id"] for candidate in result["candidates"]} == {"first", "second"}


def test_human_companion_declares_map_is_not_authority() -> None:
    companion = REPO_ROOT / "docs" / "gtkb-systems-and-tools.md"
    text = companion.read_text(encoding="utf-8")

    assert "config/agent-control/system-interface-map.toml" in text
    assert "not a replacement authority" in text
    assert "bridge/INDEX.md is bridge queue state, not the backlog" in text


def test_human_companion_path_declared_in_map_exists_in_root() -> None:
    """Displacement guard (WI-3487).

    The ``human_companion`` path declared in
    ``config/agent-control/system-interface-map.toml`` must resolve to an
    existing file under the repo root. This is a named, self-documenting check
    so that a future relocation of the platform doc out of its in-root home
    (as happened in isolation-018 Slice 18.C, which renamed it into
    ``applications/Agent_Red/docs/``) fails here explicitly, rather than only
    surfacing as a ``FileNotFoundError`` in the not-an-authority assertion or a
    ``human_companion_exists: False`` in the operating-state probe. The correct
    fix for a failure is to restore the doc in-root, NOT to repoint the map at
    an ``applications/`` copy (ADR-ISOLATION-APPLICATION-PLACEMENT-001).
    """
    module = _load_module()
    system_map = module.load_map()
    declared = system_map["human_companion"]

    assert declared == "docs/gtkb-systems-and-tools.md"
    companion = REPO_ROOT / declared
    assert companion.is_file(), (
        f"human_companion declared in system-interface-map.toml ({declared}) is "
        f"missing from its in-root platform home. Restore the doc in-root; do not "
        f"repoint the map at an applications/ copy."
    )


def test_compact_status_is_startup_safe() -> None:
    module = _load_module()

    status = module.compact_status()

    assert status["status"] == "pass"
    assert status["systems"] >= len(module.REQUIRED_SEED_IDS)
    assert status["human_companion_exists"] is True
    assert status["first_reconciliation_case"] == "backlog"
    assert status["backlog_authoritative_source"] == "MemBase table: current_work_items"


def test_cli_resolves_json_term() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "backlog", "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "resolved"
    assert payload["system"]["id"] == "backlog"
    assert payload["system"]["authoritative_source"] == "MemBase table: current_work_items"


def test_cli_status_reports_compact_payload() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--status", "--json"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["first_reconciliation_case"] == "backlog"


def test_cli_resolves_startup_control_terms() -> None:
    for term, (expected_id, expected_source) in STARTUP_CONTROL_TERMS.items():
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), term, "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["status"] == "resolved"
        assert payload["system"]["id"] == expected_id
        assert expected_source in payload["system"]["authoritative_source"]
