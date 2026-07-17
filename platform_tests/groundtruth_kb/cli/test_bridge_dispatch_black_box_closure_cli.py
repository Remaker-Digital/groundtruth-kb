from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb import cli as gtcli
from groundtruth_kb.cli import main


class _FakeScanner:
    def __init__(self, report: dict[str, object]) -> None:
        self.report = report
        self.calls: list[dict[str, object]] = []

    def closure_status(self, *, project_root: Path, project_id: str, evidence_paths: list[Path]) -> dict[str, object]:
        self.calls.append(
            {
                "project_root": project_root,
                "project_id": project_id,
                "evidence_paths": evidence_paths,
            }
        )
        return self.report

    def format_text(self, report: dict[str, object]) -> str:
        state = "READY" if report["ready"] else "NOT READY"
        return f"[{state}] {report['project_id']}\n"


def test_black_box_closure_cli_emits_json_and_fails_closed(tmp_path: Path, monkeypatch) -> None:
    config = _write_project(tmp_path)
    evidence = tmp_path / "safe-evidence.txt"
    evidence.write_text("ordinary worker uses worker-context assigned-content packet\n", encoding="utf-8")
    fake = _FakeScanner(
        {
            "project_id": "PROJECT-X",
            "ready": False,
            "member_completion_ready": False,
            "boundary_finding_count": 0,
            "blocking_boundary_finding_count": 0,
            "member_completion": {"nonterminal_work_item_ids": ["WI-5276"]},
            "findings": [],
        }
    )
    monkeypatch.setattr(gtcli, "_load_dispatch_black_box_boundary_scanner", lambda _project_root: fake)

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "dispatch",
            "black-box",
            "closure",
            "--project-id",
            "PROJECT-X",
            "--evidence",
            str(evidence),
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["ready"] is False
    assert payload["member_completion"]["nonterminal_work_item_ids"] == ["WI-5276"]
    assert fake.calls == [
        {
            "project_root": tmp_path.resolve(),
            "project_id": "PROJECT-X",
            "evidence_paths": [evidence.resolve()],
        }
    ]


def test_black_box_closure_cli_text_exits_zero_when_ready(tmp_path: Path, monkeypatch) -> None:
    config = _write_project(tmp_path)
    fake = _FakeScanner(
        {
            "project_id": "PROJECT-X",
            "ready": True,
            "member_completion_ready": True,
            "boundary_finding_count": 0,
            "blocking_boundary_finding_count": 0,
            "member_completion": {"nonterminal_work_item_ids": []},
            "findings": [],
        }
    )
    monkeypatch.setattr(gtcli, "_load_dispatch_black_box_boundary_scanner", lambda _project_root: fake)

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "dispatch",
            "black-box",
            "closure",
            "--project-id",
            "PROJECT-X",
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output == "[READY] PROJECT-X\n"


def test_black_box_closure_cli_rejects_evidence_outside_project_root(tmp_path: Path, monkeypatch) -> None:
    config = _write_project(tmp_path)
    outside = tmp_path.parent / "outside-evidence.txt"
    outside.write_text("ordinary worker uses worker-context assigned-content packet\n", encoding="utf-8")
    monkeypatch.setattr(
        gtcli,
        "_load_dispatch_black_box_boundary_scanner",
        lambda _project_root: (_ for _ in ()).throw(AssertionError("scanner should not load")),
    )

    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "bridge",
            "dispatch",
            "black-box",
            "closure",
            "--project-id",
            "PROJECT-X",
            "--evidence",
            str(outside),
        ],
    )

    assert result.exit_code != 0
    assert "black-box closure evidence must be inside the project root" in result.output


def _write_project(root: Path) -> Path:
    config = root / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\ndb_path = "{(root / "groundtruth.db").as_posix()}"\nproject_root = "{root.as_posix()}"\n',
        encoding="utf-8",
    )
    return config
