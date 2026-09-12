"""Specification-derived tests for writer-usable session-envelope CLI provenance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main


def _seed_project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "codex": {"id": "A"},
                    "cursor": {"id": "E"},
                },
            }
        ),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {"id": "A", "harness_name": "codex", "role": ["loyal-opposition"]},
                    {"id": "E", "harness_name": "cursor", "role": ["loyal-opposition"]},
                ],
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


def _with_default_harness(args: tuple[str, ...]) -> list[str]:
    """State the intended harness explicitly.

    WI-7119: ``--harness-name`` no longer defaults to "codex"; it resolves from
    whichever harness-native session variable the host set, and fails closed when
    that is absent or ambiguous. These tests seed a codex identity and intend
    codex, so they now say so rather than depending on a default that silently
    addressed the wrong harness on every non-codex host.
    """
    argv = list(args)
    if "--harness-name" not in argv:
        argv = ["--harness-name", "codex", *argv]
    return argv


def _invoke_open(config: Path, *args: str):
    return CliRunner().invoke(
        main,
        ["--config", str(config), "session", "envelope", "open", *_with_default_harness(args), "--json"],
    )


def _invoke_attest(config: Path, session_id: str, *args: str):
    return CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "session",
            "envelope",
            "attest-author-metadata",
            "--session-id",
            session_id,
            *_with_default_harness(args),
            "--json",
        ],
    )


@pytest.mark.parametrize("host_id", [" ", "unknown", "bad\nthread"])
def test_cli_rejects_invalid_codex_host_thread_before_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    host_id: str,
) -> None:
    root, config = _seed_project(tmp_path)
    monkeypatch.setenv("CODEX_THREAD_ID", host_id)

    result = _invoke_open(config, "--init-keyword", "::init gtkb pb")

    assert result.exit_code != 0
    assert not (root / "harness-state" / "codex" / "session-envelope.json").exists()
    assert not (root / "harness-state" / "codex" / "session-envelopes").exists()


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
