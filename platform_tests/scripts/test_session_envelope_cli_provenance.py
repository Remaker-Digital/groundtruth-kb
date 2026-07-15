"""Specification-derived tests for writer-usable session-envelope CLI provenance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.session.envelope import resolve_worker_role_provenance, worker_session_envelope_path

import scripts._kb_attribution as kb


def _seed_project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [{"id": "A", "harness_name": "codex", "role": ["loyal-opposition"]}],
            }
        ),
        encoding="utf-8",
    )
    config = root / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\nproject_root = "{root.as_posix()}"\ndb_path = "{(root / "groundtruth.db").as_posix()}"\n',
        encoding="utf-8",
    )
    return root, config


def _invoke_open(config: Path, *args: str):
    return CliRunner().invoke(main, ["--config", str(config), "session", "envelope", "open", *args, "--json"])


@pytest.mark.parametrize(
    ("subject", "role_token", "role"),
    [
        ("gtkb", "pb", "prime-builder"),
        ("gtkb", "lo", "loyal-opposition"),
        ("application", "pb", "prime-builder"),
        ("application", "lo", "loyal-opposition"),
    ],
)
def test_cli_role_bearing_keyword_creates_writer_usable_provenance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    subject: str,
    role_token: str,
    role: str,
) -> None:
    root, config = _seed_project(tmp_path)

    result = _invoke_open(
        config,
        "--harness-name",
        "codex",
        "--harness-id",
        "A",
        "--init-keyword",
        f"::init {subject} {role_token}",
        "--subject",
        subject,
        "--role",
        role,
    )

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    provenance = envelope["worker_role_provenance"]
    assert provenance == {
        "schema_version": 1,
        "session_id": envelope["session_id"],
        "harness_id": "A",
        "harness_name": "codex",
        "role": role,
        "role_resolution_source": "transcript_init_keyword",
        "dispatch_run_id": None,
        "issued_at": provenance["issued_at"],
    }
    assert (
        resolve_worker_role_provenance(
            root,
            current_session_id=envelope["session_id"],
            harness_name="codex",
        )["role"]
        == role
    )

    monkeypatch.setattr(kb, "PROJECT_ROOT", root)
    monkeypatch.setattr(kb, "_current_session_id", lambda: envelope["session_id"])
    monkeypatch.setenv(kb.ENV_VAR_HARNESS_NAME, "codex")
    assert kb.resolve_changed_by() == f"{role}/codex"


def test_cli_role_bearing_keyword_can_supply_the_transcript_role(tmp_path: Path) -> None:
    _, config = _seed_project(tmp_path)

    result = _invoke_open(config, "--init-keyword", "::init gtkb pb")

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    assert envelope["role_asserted"] == "prime-builder"
    assert envelope["subject_asserted"] == "gtkb"
    assert envelope["worker_role_provenance"]["role"] == "prime-builder"


@pytest.mark.parametrize("keyword", ["::init gtkb", "::init application"])
def test_cli_role_free_keyword_preserves_durable_fallback(tmp_path: Path, keyword: str) -> None:
    _, config = _seed_project(tmp_path)

    result = _invoke_open(config, "--init-keyword", keyword)

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    assert envelope["role"] == "loyal-opposition"
    assert envelope["role_asserted"] is None
    assert envelope["role_resolution"]["authority_mode"] == "durable_registry_fallback"
    assert "worker_role_provenance" not in envelope


@pytest.mark.parametrize(
    "args",
    [
        ("--role", "prime-builder"),
        ("--init-keyword", "::init gtkb", "--role", "prime-builder"),
        ("--init-keyword", "::init gtkb pb", "--role", "loyal-opposition"),
        ("--init-keyword", "::init gtkb pb", "--subject", "application"),
        ("--init-keyword", " ::init gtkb pb"),
        ("--init-keyword", "::init gtkb prime-builder"),
        ("--init-keyword", "::init gtkb pb\nnext"),
    ],
)
def test_cli_rejects_unvalidated_or_conflicting_authority_before_write(
    tmp_path: Path,
    args: tuple[str, ...],
) -> None:
    root, config = _seed_project(tmp_path)

    result = _invoke_open(config, *args)

    assert result.exit_code != 0
    assert not (root / "harness-state" / "codex" / "session-envelope.json").exists()
    assert not (root / "harness-state" / "codex" / "session-envelopes").exists()


def test_cli_successor_does_not_overwrite_closed_predecessor(tmp_path: Path) -> None:
    root, config = _seed_project(tmp_path)
    predecessor = worker_session_envelope_path(root, "codex", "desktop-thread")
    predecessor.parent.mkdir(parents=True)
    predecessor.write_text(
        json.dumps({"session_id": "desktop-thread", "status": "closed"}, indent=2) + "\n",
        encoding="utf-8",
    )
    before = predecessor.read_bytes()

    result = _invoke_open(config, "--init-keyword", "::init gtkb pb", "--role", "prime-builder")

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    assert envelope["session_id"] != "desktop-thread"
    assert worker_session_envelope_path(root, "codex", envelope["session_id"]).is_file()
    assert predecessor.read_bytes() == before


def test_cli_uses_package_parser_without_local_grammar_copy() -> None:
    source = (
        Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src" / "groundtruth_kb" / "cli_session_handoff.py"
    ).read_text(encoding="utf-8")
    assert "parse_canonical_init_keyword" in source
    assert "re.compile" not in source
    assert '"pb"' not in source
    assert '"lo"' not in source
