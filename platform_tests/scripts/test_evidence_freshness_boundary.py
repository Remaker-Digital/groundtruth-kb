from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "evidence_freshness_boundary.py"
CONFIG = REPO_ROOT / "config" / "governance" / "evidence-freshness-boundaries.toml"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("evidence_freshness_boundary", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def module() -> ModuleType:
    return _load_module()


@pytest.fixture()
def config(module: ModuleType) -> dict:
    return module.load_config(CONFIG)


def test_config_declares_required_classes_and_sot_relationship(config: dict) -> None:
    class_ids = {item["id"] for item in config["evidence_classes"]}

    assert {"current", "stale", "archival-citation-only", "full-read-justified", "missing"} <= class_ids
    assert config["relationship_to_sot_registry"]["mode"] == "complements_not_supersedes"
    assert config["relationship_to_sot_registry"]["duplicate_sot_inventory"] is False
    assert "artifacts" not in config


def test_current_state_canonical_reader_output_is_current(module: ModuleType, config: dict) -> None:
    now = datetime(2026, 7, 6, 2, 0, tzinfo=UTC)
    result = module.classify_reference(
        {
            "id": "bridge-state",
            "claim_kind": "current_state",
            "source_kind": "compact_output",
            "source_path": "gt bridge show gtkb-wi4971-evidence-freshness-boundaries --json --compact",
            "canonical_reader": "gt bridge show",
            "canonical_reader_output": True,
            "observed_at": (now - timedelta(minutes=5)).isoformat(),
        },
        config,
        now=now,
    )

    assert result["classification"] == "current"
    assert result["sufficient_for_claim"] is True
    assert result["read_mode"] == "compact"


def test_compact_summary_cannot_satisfy_current_state_claim(module: ModuleType, config: dict) -> None:
    now = datetime(2026, 7, 6, 2, 0, tzinfo=UTC)
    result = module.classify_reference(
        {
            "id": "copied-bridge-summary",
            "claim_kind": "current_state",
            "source_kind": "compact_summary",
            "source_path": "docs/gtkb-dashboard/dashboard-data.json",
            "observed_at": (now - timedelta(minutes=3)).isoformat(),
        },
        config,
        now=now,
    )

    assert result["classification"] == "stale"
    assert result["sufficient_for_claim"] is False
    assert any("summary/paraphrase" in reason for reason in result["reasons"])


def test_declared_ttl_exception_with_fallback_can_be_current(module: ModuleType, config: dict) -> None:
    now = datetime(2026, 7, 6, 2, 0, tzinfo=UTC)
    result = module.classify_reference(
        {
            "id": "relay-cache",
            "claim_kind": "current_state",
            "source_kind": "declared_ttl_cache",
            "source_path": ".claude/hooks/last-user-visible-startup-codex.md",
            "ttl_declared": True,
            "ttl_source": ".claude/hooks/last-user-visible-startup-codex.meta.json",
            "fallback_to_canonical": True,
            "ttl_minutes": 30,
            "generated_at": (now - timedelta(minutes=10)).isoformat(),
        },
        config,
        now=now,
    )

    assert result["classification"] == "current"
    assert result["sufficient_for_claim"] is True


def test_archival_bridge_path_is_citation_only(module: ModuleType, config: dict) -> None:
    result = module.classify_reference(
        {
            "id": "prior-go",
            "claim_kind": "historical",
            "source_kind": "bridge_file",
            "source_path": "bridge/gtkb-wi4966-cli-compactness-sot-size-controls-002.md",
        },
        config,
    )

    assert result["classification"] == "archival-citation-only"
    assert result["read_mode"] == "citation_only"


def test_full_read_requires_justification_and_stable_citation(module: ModuleType, config: dict) -> None:
    result = module.classify_reference(
        {
            "id": "handoff-debug",
            "claim_kind": "historical",
            "source_kind": "session_archive",
            "source_path": "harness-state/codex/session-envelope-archive/2026-07-01.json",
            "full_read_reason": "dispute-or-reproduce",
        },
        config,
    )

    assert result["classification"] == "full-read-justified"
    assert result["read_mode"] == "full"


def test_missing_reference_is_missing(module: ModuleType, config: dict) -> None:
    result = module.classify_reference(
        {
            "id": "provider-transcript",
            "claim_kind": "current_state",
            "source_kind": "missing",
            "source_path": "harness-state/openrouter/session-envelope.json",
        },
        config,
    )

    assert result["classification"] == "missing"
    assert result["sufficient_for_claim"] is False


def test_forbidden_substitute_blocks_current_state_claim(module: ModuleType, config: dict) -> None:
    now = datetime(2026, 7, 6, 2, 0, tzinfo=UTC)
    result = module.classify_reference(
        {
            "id": "role-prose",
            "claim_kind": "current_state",
            "source_kind": "canonical_reader_output",
            "source_path": ".claude/rules/operating-role.md",
            "canonical_reader_output": True,
            "observed_at": now.isoformat(),
        },
        config,
        now=now,
    )

    assert result["classification"] == "stale"
    assert result["sufficient_for_claim"] is False
    assert any("forbidden_substitute" in reason for reason in result["reasons"])


def test_report_links_b1_through_b7_to_boundary_rules(module: ModuleType, config: dict) -> None:
    report = module.build_report(
        config,
        generated_at=datetime(2026, 7, 6, 2, 45, tzinfo=UTC),
        implementation_packet_hash="sha256:test",
    )

    for idx in range(1, 8):
        assert f"`B{idx}`" in report
    assert "B1-B7 Boundary Mapping" in report
    assert "forbidden_substitutes" in report
    assert "Implementation authorization packet: sha256:test" in report
