"""Specification-derived tests for writer-usable session-envelope CLI provenance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.session.envelope import open_session, resolve_worker_role_provenance, worker_session_envelope_path

import scripts._kb_attribution as kb


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


def _invoke_open(config: Path, *args: str):
    return CliRunner().invoke(main, ["--config", str(config), "session", "envelope", "open", *args, "--json"])


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
            *args,
            "--json",
        ],
    )


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


def test_cli_role_bearing_codex_open_binds_exact_host_thread(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")

    result = _invoke_open(config, "--init-keyword", "::init gtkb pb")

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    assert envelope["session_id"] == "codex-thread-123"
    assert envelope["worker_role_provenance"]["session_id"] == "codex-thread-123"
    assert envelope["worker_role_provenance"]["role"] == "prime-builder"
    exact = worker_session_envelope_path(root, "codex", "codex-thread-123")
    assert json.loads(exact.read_text(encoding="utf-8")) == envelope


def test_cli_role_bearing_cursor_open_binds_exact_host_conversation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    conversation_id = "12a16794-f84d-457f-81b4-8e803034e4d5"
    monkeypatch.setenv("CURSOR_CONVERSATION_ID", conversation_id)

    result = _invoke_open(
        config,
        "--harness-name",
        "cursor",
        "--harness-id",
        "E",
        "--init-keyword",
        "::init gtkb lo",
        "--subject",
        "gtkb",
        "--role",
        "loyal-opposition",
    )

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    assert envelope["session_id"] == conversation_id
    assert envelope["worker_role_provenance"]["session_id"] == conversation_id
    exact = worker_session_envelope_path(root, "cursor", conversation_id)
    assert json.loads(exact.read_text(encoding="utf-8")) == envelope


def test_cli_cursor_init_upgrades_unasserted_startup_subject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    conversation_id = "12a16794-f84d-457f-81b4-8e803034e4d5"
    monkeypatch.setenv("CURSOR_CONVERSATION_ID", conversation_id)
    startup = open_session(
        root,
        harness_name="cursor",
        harness_id="E",
        role="loyal-opposition",
        session_id=conversation_id,
        worker_role_source="session_resolver_fallback",
    )
    assert startup["subject"] == "gtkb_infrastructure"
    assert startup["subject_asserted"] is None

    result = _invoke_open(
        config,
        "--harness-name",
        "cursor",
        "--harness-id",
        "E",
        "--init-keyword",
        "::init gtkb lo",
        "--subject",
        "gtkb",
        "--role",
        "loyal-opposition",
    )

    assert result.exit_code == 0, result.output
    envelope = json.loads(result.output)
    assert envelope["session_id"] == conversation_id
    assert envelope["subject"] == "gtkb"
    assert envelope["subject_asserted"] == "gtkb"


def test_cli_same_host_refresh_returns_exact_envelope_without_rewrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")
    opened = _invoke_open(config, "--init-keyword", "::init gtkb pb")
    assert opened.exit_code == 0, opened.output
    exact_path = worker_session_envelope_path(root, "codex", "codex-thread-123")
    current_path = root / "harness-state" / "codex" / "session-envelope.json"
    projection_path = root / ".claude" / "session" / "envelope.json"
    before = exact_path.read_bytes()

    refreshed = _invoke_open(config)

    assert refreshed.exit_code == 0, refreshed.output
    envelope = json.loads(refreshed.output)
    assert envelope["session_id"] == "codex-thread-123"
    assert envelope["role"] == "prime-builder"
    assert envelope["worker_role_provenance"]["role_resolution_source"] == "transcript_init_keyword"
    assert exact_path.read_bytes() == before
    assert not current_path.exists()
    assert not projection_path.exists()


def test_cli_same_host_conflict_fails_before_exact_or_projection_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")
    opened = _invoke_open(config, "--init-keyword", "::init gtkb pb")
    assert opened.exit_code == 0, opened.output
    exact_path = worker_session_envelope_path(root, "codex", "codex-thread-123")
    current_path = root / "harness-state" / "codex" / "session-envelope.json"
    projection_path = root / ".claude" / "session" / "envelope.json"
    before = exact_path.read_bytes()

    conflicting = _invoke_open(config, "--init-keyword", "::init gtkb lo")

    assert conflicting.exit_code != 0
    assert "conflicts with the exact host-bound session envelope" in conflicting.output
    assert exact_path.read_bytes() == before
    assert not current_path.exists()
    assert not projection_path.exists()


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


def test_cli_attests_exact_open_codex_session_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    opened = _invoke_open(config, "--init-keyword", "::init gtkb lo", "--role", "loyal-opposition")
    assert opened.exit_code == 0, opened.output
    session_id = json.loads(opened.output)["session_id"]
    monkeypatch.setenv("GTKB_SESSION_ID", session_id)

    result = _invoke_attest(
        config,
        session_id,
        "--model",
        "gpt-5.6-sol",
        "--reasoning-effort",
        "xhigh",
        "--thread-source",
        "user",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["model_id"] == "gpt-5.6-sol"
    assert payload["model_version"] == "gpt-5.6-sol"
    assert payload["model_configuration"] == "reasoning_effort=xhigh; thread_source=user"
    assert payload["model_metadata_source"] == "x-codex-turn-metadata"
    authoritative = json.loads(worker_session_envelope_path(root, "codex", session_id).read_text(encoding="utf-8"))
    assert not (root / "harness-state" / "codex" / "session-envelope.json").exists()
    assert not (root / ".claude" / "session" / "envelope.json").exists()
    assert authoritative["model_id"] == "gpt-5.6-sol"
    assert authoritative["model_metadata_source"] == "x-codex-turn-metadata"


def test_cli_attests_exact_open_cursor_session_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root, config = _seed_project(tmp_path)
    conversation_id = "12a16794-f84d-457f-81b4-8e803034e4d5"
    monkeypatch.setenv("CURSOR_CONVERSATION_ID", conversation_id)
    opened = _invoke_open(
        config,
        "--harness-name",
        "cursor",
        "--harness-id",
        "E",
        "--init-keyword",
        "::init gtkb lo",
        "--role",
        "loyal-opposition",
    )
    assert opened.exit_code == 0, opened.output
    assert json.loads(opened.output)["session_id"] == conversation_id
    monkeypatch.setenv("GTKB_SESSION_ID", conversation_id)

    result = _invoke_attest(
        config,
        conversation_id,
        "--model",
        "gpt-5.6-terra",
        "--reasoning-effort",
        "xhigh",
        "--thread-source",
        "cursor-agent-runtime",
        "--harness-name",
        "cursor",
        "--harness-id",
        "E",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["session_id"] == conversation_id
    assert payload["model_id"] == "gpt-5.6-terra"
    assert payload["model_metadata_source"] == "cursor-conversation-metadata"
    authoritative = json.loads(
        worker_session_envelope_path(root, "cursor", conversation_id).read_text(encoding="utf-8")
    )
    assert authoritative["model_configuration"] == "reasoning_effort=xhigh; thread_source=cursor-agent-runtime"
    assert authoritative["model_metadata_source"] == "cursor-conversation-metadata"


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--model", "unknown"),
        ("--reasoning-effort", "tbd"),
        ("--thread-source", "none"),
        ("--model", "bad\nmodel"),
    ],
)
def test_cli_attestation_rejects_placeholder_or_multiline_metadata_before_write(
    tmp_path: Path,
    option: str,
    value: str,
) -> None:
    root, config = _seed_project(tmp_path)
    opened = _invoke_open(config, "--init-keyword", "::init gtkb lo", "--role", "loyal-opposition")
    session_id = json.loads(opened.output)["session_id"]
    path = worker_session_envelope_path(root, "codex", session_id)
    before = path.read_bytes()
    values = {
        "--model": "gpt-5.6-sol",
        "--reasoning-effort": "xhigh",
        "--thread-source": "user",
    }
    values[option] = value

    result = _invoke_attest(
        config,
        session_id,
        "--model",
        values["--model"],
        "--reasoning-effort",
        values["--reasoning-effort"],
        "--thread-source",
        values["--thread-source"],
    )

    assert result.exit_code != 0
    assert path.read_bytes() == before


def test_cli_attestation_rejects_noncurrent_session_without_replacing_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    opened = _invoke_open(config, "--init-keyword", "::init gtkb lo", "--role", "loyal-opposition")
    current = json.loads(opened.output)
    stale = dict(current)
    stale["session_id"] = "stale-session"
    stale["worker_role_provenance"] = dict(stale["worker_role_provenance"])
    stale["worker_role_provenance"]["session_id"] = "stale-session"
    stale_path = worker_session_envelope_path(root, "codex", "stale-session")
    stale_path.parent.mkdir(parents=True, exist_ok=True)
    stale_path.write_text(json.dumps(stale, indent=2) + "\n", encoding="utf-8")
    current_path = worker_session_envelope_path(root, "codex", current["session_id"])
    before_current = current_path.read_bytes()
    monkeypatch.setenv("GTKB_SESSION_ID", current["session_id"])

    result = _invoke_attest(
        config,
        "stale-session",
        "--model",
        "gpt-5.6-sol",
        "--reasoning-effort",
        "xhigh",
        "--thread-source",
        "user",
    )

    assert result.exit_code != 0
    assert "not the current harness session" in result.output
    assert current_path.read_bytes() == before_current
    assert not (root / "harness-state" / "codex" / "session-envelope.json").exists()


def test_cli_attestation_rebinds_valid_dispatch_envelope_to_exact_codex_thread(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    opened = _invoke_open(config, "--init-keyword", "::init gtkb lo", "--role", "loyal-opposition")
    dispatch_envelope = json.loads(opened.output)
    dispatch_path = worker_session_envelope_path(root, "codex", dispatch_envelope["session_id"])
    before_dispatch = dispatch_path.read_bytes()
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")

    result = _invoke_attest(
        config,
        "codex-thread-123",
        "--model",
        "gpt-5.6-sol",
        "--reasoning-effort",
        "xhigh",
        "--thread-source",
        "user",
    )

    assert result.exit_code == 0, result.output
    exact = json.loads(worker_session_envelope_path(root, "codex", "codex-thread-123").read_text(encoding="utf-8"))
    assert not (root / "harness-state" / "codex" / "session-envelope.json").exists()
    assert exact["session_id"] == "codex-thread-123"
    assert exact["worker_role_provenance"]["session_id"] == "codex-thread-123"
    assert exact["model_metadata_source"] == "x-codex-turn-metadata"
    assert dispatch_path.read_bytes() == before_dispatch


def test_cli_attestation_promotes_existing_exact_open_codex_thread(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, config = _seed_project(tmp_path)
    opened = _invoke_open(config, "--init-keyword", "::init gtkb lo", "--role", "loyal-opposition")
    current = json.loads(opened.output)
    exact = dict(current)
    exact["session_id"] = "codex-thread-123"
    exact["worker_role_provenance"] = dict(exact["worker_role_provenance"])
    exact["worker_role_provenance"]["session_id"] = "codex-thread-123"
    exact_path = worker_session_envelope_path(root, "codex", "codex-thread-123")
    exact_path.parent.mkdir(parents=True, exist_ok=True)
    exact_path.write_text(json.dumps(exact, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-thread-123")
    monkeypatch.setenv("GTKB_SESSION_ID", "codex-thread-123")

    result = _invoke_attest(
        config,
        "codex-thread-123",
        "--model",
        "gpt-5.6-sol",
        "--reasoning-effort",
        "xhigh",
        "--thread-source",
        "user",
    )

    assert result.exit_code == 0, result.output
    promoted = json.loads(exact_path.read_text(encoding="utf-8"))
    assert promoted["session_id"] == "codex-thread-123"
    assert promoted["model_id"] == "gpt-5.6-sol"
    assert promoted["model_metadata_source"] == "x-codex-turn-metadata"
    assert not (root / "harness-state" / "codex" / "session-envelope.json").exists()


def test_cli_uses_package_parser_without_local_grammar_copy() -> None:
    source = (
        Path(__file__).resolve().parents[2] / "groundtruth-kb" / "src" / "groundtruth_kb" / "cli_session_handoff.py"
    ).read_text(encoding="utf-8")
    assert "parse_canonical_init_keyword" in source
    assert "re.compile" not in source
    assert '"pb"' not in source
    assert '"lo"' not in source
