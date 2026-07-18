"""End-to-end hook tests for WI-5476 relationship classification."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "bridge-proposal-wi-id-collision-gate.py"
DB_ENV_VAR = "GTKB_WI_COLLISION_DB_PATH"


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "groundtruth.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE current_work_items (id TEXT PRIMARY KEY, title TEXT NOT NULL)")
        conn.executemany(
            "INSERT INTO current_work_items (id, title) VALUES (?, ?)",
            [
                ("WI-100", "Declared work"),
                ("WI-101", "Related work"),
                ("WI-200", "Foreign work"),
            ],
        )
    return path


def _proposal(*metadata: str, body: str = "") -> str:
    return "\n".join(
        [
            "NEW",
            "bridge_kind: prime_proposal",
            "Work Item: WI-100",
            *metadata,
            "",
            body,
            "",
        ]
    )


def _run_hook(
    db_path: Path,
    content: str,
    *,
    tool_name: str = "Write",
    file_path: str = "bridge/example-001.md",
) -> dict[str, Any]:
    payload = {
        "tool_name": tool_name,
        "tool_input": {
            "file_path": file_path,
            "content": content,
            "new_string": content,
        },
    }
    env = os.environ.copy()
    env[DB_ENV_VAR] = str(db_path)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        cwd=PROJECT_ROOT,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def _context(output: dict[str, Any]) -> str:
    return str(output.get("hookSpecificOutput", {}).get("additionalContext") or "")


def test_valid_human_related_only_content_is_quiet(db_path: Path) -> None:
    output = _run_hook(db_path, _proposal("Related Work Items: WI-101"))

    assert output == {}


def test_valid_json_related_only_content_is_quiet(db_path: Path) -> None:
    output = _run_hook(db_path, _proposal('related_work_items: ["WI-101"]'))

    assert output == {}


def test_extra_collision_warns_without_labeling_related_id_actionable(db_path: Path) -> None:
    output = _run_hook(
        db_path,
        _proposal("Related Work Items: WI-101", body="Foreign implementation carrier WI-200."),
    )
    context = _context(output)

    assert "WI-ID collision warning" in context
    assert "| `WI-101` | `related_work_item` |" in context
    assert "| `WI-200` | `collision` |" in context
    assert "### Validated Related Work Items" in context


def test_relationship_error_warns_even_without_foreign_collision(db_path: Path) -> None:
    output = _run_hook(db_path, _proposal("Related Work Items: WI-999"))
    context = _context(output)

    assert "WI-ID collision warning" in context
    assert "unknown_related_work_item" in context
    assert "WI-999" in context


def test_contradictory_forms_warn_and_suppress_neither_id(db_path: Path) -> None:
    output = _run_hook(
        db_path,
        _proposal(
            "Related Work Items: WI-101",
            'related_work_items: ["WI-200"]',
        ),
    )
    context = _context(output)

    assert "contradictory_related_work_items" in context
    assert "| `WI-101` | `collision` |" in context
    assert "| `WI-200` | `collision` |" in context


def test_edit_payload_uses_new_string(db_path: Path) -> None:
    output = _run_hook(
        db_path,
        _proposal("Related Work Items: WI-101"),
        tool_name="Edit",
    )

    assert output == {}


@pytest.mark.parametrize(
    ("tool_name", "file_path"),
    [
        ("Read", "bridge/example-001.md"),
        ("Write", "work_area/example.md"),
    ],
)
def test_irrelevant_payloads_remain_quiet(
    db_path: Path,
    tool_name: str,
    file_path: str,
) -> None:
    output = _run_hook(
        db_path,
        _proposal("Related Work Items: WI-999"),
        tool_name=tool_name,
        file_path=file_path,
    )

    assert output == {}
