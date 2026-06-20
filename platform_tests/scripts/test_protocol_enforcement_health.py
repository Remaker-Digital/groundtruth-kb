"""Tests for the read-only protocol enforcement health reporter."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "protocol_enforcement_health.py"
STAMP = "2026-06-20T02:00:00Z"


@pytest.fixture(scope="module")
def health_module():
    spec = importlib.util.spec_from_file_location("protocol_enforcement_health", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["protocol_enforcement_health"] = module
    spec.loader.exec_module(module)
    return module


def _write_bridge(root: Path, slug: str, versions: list[tuple[int, str]]) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    for version, status in versions:
        path = bridge / f"{slug}-{version:03d}.md"
        path.write_text(f"{status}\n\nFixture {status} file.\n", encoding="utf-8")


def _write_packet(root: Path, slug: str, *, expires_at: str = "2026-06-20T04:00:00Z") -> None:
    packet_dir = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet = {
        "bridge_id": slug,
        "expires_at": expires_at,
        "go_file": f"bridge/{slug}-002.md",
        "latest_status": "GO",
        "target_path_globs": ["scripts/protocol_enforcement_health.py"],
    }
    (packet_dir / f"{slug}.json").write_text(json.dumps(packet), encoding="utf-8")


def _write_claim(root: Path, slug: str, *, expires_at: str = "2026-06-20T04:00:00Z") -> None:
    conn = sqlite3.connect(root / "groundtruth.db")
    try:
        conn.execute(
            """
            CREATE TABLE work_intent_claims (
                thread_slug TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                acquired_at TEXT NOT NULL,
                ttl_expires_at TEXT NOT NULL,
                claim_kind TEXT,
                implementation_grace_expires_at TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO work_intent_claims
                (thread_slug, session_id, acquired_at, ttl_expires_at, claim_kind, implementation_grace_expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (slug, "session-a", STAMP, expires_at, "go_implementation", expires_at),
        )
        conn.commit()
    finally:
        conn.close()


def _state_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*")}


def _categories(report: dict[str, Any]) -> set[str]:
    return {item["category"] for item in report["items"]}


def test_empty_state_is_healthy_and_read_only(health_module, tmp_path: Path) -> None:
    before = _state_files(tmp_path)

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert report["status"] == "healthy"
    assert report["items"] == []
    assert report["summary"]["total_items"] == 0
    assert _state_files(tmp_path) == before


def test_latest_no_go_yields_prime_builder_next_action(health_module, tmp_path: Path) -> None:
    _write_bridge(tmp_path, "fixture-no-go", [(1, "NEW"), (2, "NO-GO")])

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert report["status"] == "warning"
    item = report["items"][0]
    assert item["category"] == "unresolved_no_go"
    assert item["next_action"] == "prime_builder_revise_or_record_blocker"
    assert item["owner_visible"] is False


def test_latest_advisory_is_owner_visible(health_module, tmp_path: Path) -> None:
    _write_bridge(tmp_path, "fixture-advisory", [(1, "ADVISORY")])

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    item = report["items"][0]
    assert item["category"] == "unresolved_advisory"
    assert item["next_action"] == "owner_disposition_required"
    assert item["owner_visible"] is True


def test_latest_go_missing_packet_yields_implementation_start_action(health_module, tmp_path: Path) -> None:
    _write_bridge(tmp_path, "fixture-go", [(1, "NEW"), (2, "GO")])

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert report["status"] == "blocked"
    item = report["items"][0]
    assert item["category"] == "missing_implementation_packet"
    assert item["next_action"] == "create_implementation_start_packet"


def test_latest_go_missing_work_intent_claim_is_distinct_gap(health_module, tmp_path: Path) -> None:
    _write_bridge(tmp_path, "fixture-go", [(1, "NEW"), (2, "GO")])
    _write_packet(tmp_path, "fixture-go")

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert _categories(report) == {"missing_work_intent_claim"}
    assert report["items"][0]["next_action"] == "acquire_work_intent_claim"


def test_latest_go_with_packet_and_claim_has_no_implementation_gap(health_module, tmp_path: Path) -> None:
    _write_bridge(tmp_path, "fixture-go", [(1, "NEW"), (2, "GO")])
    _write_packet(tmp_path, "fixture-go")
    _write_claim(tmp_path, "fixture-go")

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert report["status"] == "healthy"
    assert report["items"] == []


def test_protected_mutation_block_reason_code_is_visible(health_module, tmp_path: Path) -> None:
    state_dir = tmp_path / ".gtkb-state" / "protocol-enforcement"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "protected-mutation-blocks.json").write_text(
        json.dumps(
            [
                {
                    "reason_code": "missing_or_stale_claim",
                    "bridge_thread": "fixture-go",
                    "target_paths": ["scripts/protocol_enforcement_health.py"],
                }
            ]
        ),
        encoding="utf-8",
    )

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    item = report["items"][0]
    assert item["category"] == "protected_mutation_block"
    assert item["evidence"]["reason_code"] == "missing_or_stale_claim"
    assert item["next_action"] == "acquire_work_intent_claim"


def test_missing_post_action_receipt_is_reported_when_completion_fixture_requires_it(
    health_module, tmp_path: Path
) -> None:
    state_dir = tmp_path / ".gtkb-state" / "protocol-enforcement"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "completed-mutations.json").write_text(
        json.dumps([{"bridge_thread": "completed-thread", "mutation_class": "file", "receipt_required": True}]),
        encoding="utf-8",
    )

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert _categories(report) == {"missing_post_action_receipt"}
    assert report["items"][0]["next_action"] == "write_or_link_post_action_receipt"


def test_existing_post_action_receipt_satisfies_completion_fixture(health_module, tmp_path: Path) -> None:
    state_dir = tmp_path / ".gtkb-state" / "protocol-enforcement"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "completed-mutations.json").write_text(
        json.dumps([{"bridge_thread": "completed-thread", "mutation_class": "file", "receipt_required": True}]),
        encoding="utf-8",
    )
    receipt_dir = tmp_path / ".gtkb-state" / "post-action-receipts" / "2026-06-20"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    (receipt_dir / "receipt.json").write_text(
        json.dumps({"receipt_id": "receipt-1", "bridge_thread": "completed-thread"}),
        encoding="utf-8",
    )

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert report["status"] == "healthy"
    assert report["items"] == []


def test_external_mutation_gap_is_gracefully_empty_until_state_exists(health_module, tmp_path: Path) -> None:
    empty_report = health_module.generate_report(tmp_path, generated_at=STAMP)
    assert "external_mutation_authorization_gap" not in _categories(empty_report)

    state_dir = tmp_path / ".gtkb-state" / "protocol-enforcement"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "external-mutation-requests.json").write_text(
        json.dumps([{"bridge_thread": "external-thread", "target": "vendor-api", "authorized": False}]),
        encoding="utf-8",
    )

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert _categories(report) == {"external_mutation_authorization_gap"}
    assert report["items"][0]["owner_visible"] is True


def test_report_is_json_serializable_and_stable(health_module, tmp_path: Path) -> None:
    _write_bridge(tmp_path, "b-thread", [(1, "ADVISORY")])
    _write_bridge(tmp_path, "a-thread", [(1, "NEW"), (2, "GO")])

    report = health_module.generate_report(tmp_path, generated_at=STAMP)
    encoded = json.dumps(report, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded == report
    assert [item["evidence"]["bridge_thread"] for item in report["items"]] == ["a-thread", "b-thread"]


def test_source_paths_stay_within_fixture_root_and_no_files_are_written(health_module, tmp_path: Path) -> None:
    _write_bridge(tmp_path, "fixture-go", [(1, "NEW"), (2, "GO")])
    before = _state_files(tmp_path)

    report = health_module.generate_report(tmp_path, generated_at=STAMP)

    assert _state_files(tmp_path) == before
    for relative_path in report["source_paths"]:
        resolved = (tmp_path / relative_path).resolve()
        assert tmp_path.resolve() == resolved or tmp_path.resolve() in resolved.parents
