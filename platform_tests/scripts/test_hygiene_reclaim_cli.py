"""CLI integration coverage for the deterministic hygiene reclaim service."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.hygiene import reclaim


def test_reclaim_help_lists_bounded_command_family() -> None:
    result = CliRunner().invoke(main, ["hygiene", "reclaim", "--help"])

    assert result.exit_code == 0, result.output
    for command in ("plan", "history", "trash", "restore"):
        assert command in result.output
    assert "purge" not in result.output


def test_reclaim_plan_wires_compact_json_and_timezone(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_plan(root: Path, **kwargs: object) -> dict[str, object]:
        captured["root"] = root
        captured.update(kwargs)
        return {
            "run_id": "run-1",
            "plan_hash": "sha256:plan",
            "summary": {"candidate_count": 2, "executable": False},
        }

    monkeypatch.setattr(reclaim, "plan_reclaim", fake_plan)
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "reclaim",
            "plan",
            "--root",
            str(tmp_path),
            "--state-root",
            str(tmp_path / "state"),
            "--min-age-hours",
            "24",
            "--now",
            "2026-07-16T04:00:00Z",
            "--actor",
            "prime-builder/codex/A",
            "--session-id",
            "session-1",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["plan_hash"] == "sha256:plan"
    assert payload["summary"] == {"candidate_count": 2, "executable": False}
    assert captured["root"] == tmp_path.resolve()
    assert captured["state_root"] == (tmp_path / "state").resolve()
    assert captured["min_age_hours"] == 24
    assert captured["actor"] == "prime-builder/codex/A"
    assert captured["session_id"] == "session-1"
    assert captured["now"].isoformat() == "2026-07-16T04:00:00+00:00"  # type: ignore[union-attr]


def test_reclaim_history_wires_exact_run_and_item(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_history(root: Path, **kwargs: object) -> dict[str, object]:
        captured["root"] = root
        captured.update(kwargs)
        return {"run_id": "run-1", "integrity": "pass", "status": "planned"}

    monkeypatch.setattr(reclaim, "history_reclaim", fake_history)
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "reclaim",
            "history",
            "--root",
            str(tmp_path),
            "--run-id",
            "run-1",
            "--item-id",
            "item-1",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["integrity"] == "pass"
    assert captured["run_id"] == "run-1"
    assert captured["item_id"] == "item-1"


def test_reclaim_trash_requires_and_wires_exact_evidence(monkeypatch, tmp_path: Path) -> None:
    missing = CliRunner().invoke(
        main,
        [
            "hygiene",
            "reclaim",
            "trash",
            "--root",
            str(tmp_path),
            "--run-id",
            "run-1",
            "--plan-hash",
            "sha256:plan",
            "--item-id",
            "item-1",
        ],
    )
    assert missing.exit_code == 2
    assert "--owner-evidence" in missing.output

    captured: dict[str, object] = {}

    def fake_trash(root: Path, **kwargs: object) -> dict[str, object]:
        captured["root"] = root
        captured.update(kwargs)
        return {
            "run_id": "run-1",
            "status": "trashed",
            "logical_bytes": 123,
            "physical_bytes_reclaimed": 0,
        }

    monkeypatch.setattr(reclaim, "trash_reclaim", fake_trash)
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "reclaim",
            "trash",
            "--root",
            str(tmp_path),
            "--run-id",
            "run-1",
            "--plan-hash",
            "sha256:plan",
            "--item-id",
            "item-1",
            "--item-id",
            "item-2",
            "--owner-evidence",
            "DELIB-EXACT-BATCH",
            "--quiescence-evidence",
            "QUIESCE-20260716",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["physical_bytes_reclaimed"] == 0
    assert captured["item_ids"] == ("item-1", "item-2")
    assert captured["owner_evidence"] == ("DELIB-EXACT-BATCH",)
    assert captured["quiescence_evidence"] == ("QUIESCE-20260716",)


def test_reclaim_restore_wires_exact_items(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_restore(root: Path, **kwargs: object) -> dict[str, object]:
        captured["root"] = root
        captured.update(kwargs)
        return {"run_id": "run-1", "status": "restored", "restored_count": 1}

    monkeypatch.setattr(reclaim, "restore_reclaim", fake_restore)
    result = CliRunner().invoke(
        main,
        [
            "hygiene",
            "reclaim",
            "restore",
            "--root",
            str(tmp_path),
            "--run-id",
            "run-1",
            "--item-id",
            "item-1",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "restored"
    assert captured["item_ids"] == ("item-1",)
