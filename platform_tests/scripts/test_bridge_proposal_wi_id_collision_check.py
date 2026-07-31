"""Focused tests for bridge proposal related-work collision classification."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "bridge_proposal_wi_id_collision_check.py"


def _load_module():
    module_name = "bridge_proposal_wi_id_collision_check_wi5476"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def module():
    return _load_module()


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "groundtruth.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE current_work_items (id TEXT PRIMARY KEY, title TEXT NOT NULL)")
        conn.executemany(
            "INSERT INTO current_work_items (id, title) VALUES (?, ?)",
            [
                ("WI-100", "Declared work"),
                ("WI-101", "First related work"),
                ("WI-102", "Second related work"),
                ("WI-200", "Foreign work"),
            ],
        )
    return path


def _proposal(*metadata: str, body: str = "") -> str:
    lines = [
        "NEW",
        "bridge_kind: prime_proposal",
        "Work Item: WI-100",
        *metadata,
        "",
        body,
    ]
    return "\n".join(lines) + "\n"


def test_human_related_work_items_are_not_collisions(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal("Related Work Items: WI-101, WI-102"),
        db_path=db_path,
    )

    assert result.has_collisions is False
    assert [item.work_item_id for item in result.related_work_items] == ["WI-101", "WI-102"]
    assert [item.classification for item in result.cited_ids] == [
        "declared_work_item",
        "related_work_item",
        "related_work_item",
    ]
    assert result.collisions == ()
    assert result.relationship_errors == ()


def test_json_related_work_items_are_not_collisions(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal('related_work_items: ["WI-102", "WI-101"]'),
        db_path=db_path,
    )

    assert [item.work_item_id for item in result.related_work_items] == ["WI-102", "WI-101"]
    assert all(item.sources == ("related_work_items",) for item in result.related_work_items)
    assert result.has_collisions is False


def test_matching_forms_compare_sets_and_preserve_human_order(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal(
            "Related Work Items: WI-102, WI-101",
            'related_work_items: ["WI-101", "WI-102"]',
        ),
        db_path=db_path,
    )

    assert [item.work_item_id for item in result.related_work_items] == ["WI-102", "WI-101"]
    assert all(item.sources == ("Related Work Items", "related_work_items") for item in result.related_work_items)
    assert result.has_collisions is False


def test_undeclared_existing_id_remains_the_only_collision(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal("Related Work Items: WI-101", body="Implementation also cites WI-200."),
        db_path=db_path,
    )

    assert [item.work_item_id for item in result.related_work_items] == ["WI-101"]
    assert [item.cited_id for item in result.collisions] == ["WI-200"]
    assert result.has_collisions is True


def test_contradictory_forms_suppress_no_collision(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal(
            "Related Work Items: WI-101",
            'related_work_items: ["WI-102"]',
        ),
        db_path=db_path,
    )

    assert result.related_work_items == ()
    assert [error.code for error in result.relationship_errors] == ["contradictory_related_work_items"]
    assert [item.cited_id for item in result.collisions] == ["WI-101", "WI-102"]


@pytest.mark.parametrize(
    ("metadata", "expected_code"),
    [
        (("Related Work Items:",), "empty_related_work_items"),
        (("related_work_items: not-json",), "malformed_related_work_items_json"),
        (('related_work_items: {"id": "WI-101"}',), "invalid_related_work_items_json_type"),
        (('related_work_items: ["WI-101", 102]',), "non_string_related_work_item"),
        (("Related Work Items: WI-101, WI-101",), "duplicate_related_work_item"),
        (("Related Work Items: GTKB-FOO-1",), "invalid_related_work_item"),
        (("Related Work Items: WI-100",), "self_related_work_item"),
        (("Related Work Items: WI-999",), "unknown_related_work_item"),
    ],
)
def test_invalid_relationship_metadata_is_actionable(
    module,
    db_path: Path,
    metadata: tuple[str, ...],
    expected_code: str,
) -> None:
    result = module.check_content(_proposal(*metadata), db_path=db_path)

    assert expected_code in [error.code for error in result.relationship_errors]
    assert result.has_relationship_errors is True
    assert result.has_collisions is True


def test_repeated_metadata_form_is_actionable(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal(
            "Related Work Items: WI-101",
            "Related Work Items: WI-102",
        ),
        db_path=db_path,
    )

    assert [error.code for error in result.relationship_errors] == ["duplicate_related_work_items_metadata"]
    assert result.related_work_items == ()
    assert [item.cited_id for item in result.collisions] == ["WI-101", "WI-102"]


def test_unknown_free_form_id_is_not_promoted_or_colliding(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal(body="This prose mentions WI-999 but does not declare a relationship."),
        db_path=db_path,
    )

    unknown = next(item for item in result.cited_ids if item.cited_id == "WI-999")
    assert unknown.classification == "unknown_reference"
    assert unknown.related_work_item is False
    assert unknown.collision is False
    assert result.has_collisions is False


def test_fenced_relationship_examples_are_ignored(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal(
            "Related Work Items: WI-101",
            body='```text\nRelated Work Items: WI-200\nrelated_work_items: ["WI-200"]\n```',
        ),
        db_path=db_path,
    )

    assert [item.work_item_id for item in result.related_work_items] == ["WI-101"]
    assert result.relationship_errors == ()
    assert all(item.cited_id != "WI-200" for item in result.cited_ids)
    assert result.has_collisions is False


def test_json_and_markdown_contracts_are_additive(module, db_path: Path) -> None:
    result = module.check_content(
        _proposal("Related Work Items: WI-101", body="Foreign WI-200."),
        db_path=db_path,
    )
    payload = result.to_dict()
    markdown = module.format_markdown(result)

    assert payload["declared_work_item"] == "WI-100"
    assert payload["has_collisions"] is True
    assert [item["cited_id"] for item in payload["collisions"]] == ["WI-200"]
    assert payload["validated_related_ids"] == ["WI-101"]
    assert payload["relationship_errors"] == []
    assert "### Validated Related Work Items" in markdown
    assert "| `WI-101` | `Related Work Items` | `true` |" in markdown
    assert "| `WI-200` | `collision` |" in markdown


def test_strict_mode_fails_for_relationship_error(
    module,
    db_path: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    proposal_path = tmp_path / "proposal.md"
    proposal_path.write_text(_proposal("Related Work Items: WI-999"), encoding="utf-8")

    exit_code = module.main(
        [
            "--content-file",
            str(proposal_path),
            "--db-path",
            str(db_path),
            "--strict",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 3
    assert payload["has_relationship_errors"] is True


def test_strict_mode_passes_for_valid_related_only(
    module,
    db_path: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    proposal_path = tmp_path / "proposal.md"
    proposal_path.write_text(_proposal("Related Work Items: WI-101"), encoding="utf-8")

    exit_code = module.main(
        [
            "--content-file",
            str(proposal_path),
            "--db-path",
            str(db_path),
            "--strict",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["has_collisions"] is False


def test_check_is_read_only(module, db_path: Path) -> None:
    before = hashlib.sha256(db_path.read_bytes()).hexdigest()

    module.check_content(
        _proposal("Related Work Items: WI-101", body="Foreign WI-200."),
        db_path=db_path,
    )

    assert hashlib.sha256(db_path.read_bytes()).hexdigest() == before
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM current_work_items").fetchone()[0] == 4
