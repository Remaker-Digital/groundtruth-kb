from __future__ import annotations

import json
import types
from dataclasses import fields
from pathlib import Path

import groundtruth_kb.cli_session_handoff as cli_session_handoff
import groundtruth_kb.session.envelope as session_envelope
from click.testing import CliRunner
from groundtruth_kb.session import handoff
from groundtruth_kb.session.attestation.service import Binding, bind_exact_init


def _write_identities(root: Path) -> None:
    state_dir = root / "harness-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "harness-identities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "codex": {"id": "A"},
                    "claude": {"id": "B"},
                },
            }
        ),
        encoding="utf-8",
    )


def _write_envelope(root: Path, harness: str, filename: str, *, session_id: str, closed_at: str) -> Path:
    archive_dir = root / "harness-state" / harness / "session-envelope-archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    path = archive_dir / filename
    path.write_text(
        json.dumps(
            {
                "session_id": session_id,
                "harness_id": "A" if harness == "codex" else "B",
                "harness_name": harness,
                "closed_at": closed_at,
                "role": "prime-builder",
            }
        ),
        encoding="utf-8",
    )
    return path


def test_explicit_session_id_selects_matching_archive_not_lex_latest(tmp_path: Path) -> None:
    archive_dir = tmp_path / "harness-state" / "codex" / "session-envelope-archive"
    old_path = _write_envelope(
        tmp_path,
        "codex",
        "2026-07-01T01-00-00Z-session-envelope.json",
        session_id="target-session",
        closed_at="2026-07-01T01:00:00Z",
    )
    _write_envelope(
        tmp_path,
        "codex",
        "2026-07-01T02-00-00Z-session-envelope.json",
        session_id="newer-session",
        closed_at="2026-07-01T02:00:00Z",
    )

    selected = handoff._select_envelope_for_session_id(archive_dir, "target-session")

    assert selected == old_path


def test_explicit_session_id_resolves_across_registered_harness_archives(tmp_path: Path) -> None:
    _write_identities(tmp_path)
    _write_envelope(
        tmp_path,
        "claude",
        "2026-07-01T01-00-00Z-session-envelope.json",
        session_id="other-session",
        closed_at="2026-07-01T01:00:00Z",
    )
    codex_path = _write_envelope(
        tmp_path,
        "codex",
        "2026-07-01T02-00-00Z-session-envelope.json",
        session_id="target-session",
        closed_at="2026-07-01T02:00:00Z",
    )

    harness_name, selected = handoff._select_envelope_across_archives(tmp_path, "target-session")

    assert harness_name == "codex"
    assert selected == codex_path


def _bound_envelope(tmp_path: Path) -> tuple[dict[str, object], Binding]:
    native_context_id = "native-context-7692"
    binding = bind_exact_init(
        tmp_path / "groundtruth.db",
        native_context_id=native_context_id,
        init_command="::init gtkb pb",
    )
    envelope: dict[str, object] = {
        "session_id": native_context_id,
        "worker_role_provenance": {"role_resolution_source": "session_resolver_fallback"},
        "role_resolution": {"interactive_role_source": None},
    }
    return envelope, binding


def test_reconcile_reports_only_current_binding_fields(tmp_path: Path) -> None:
    envelope, binding = _bound_envelope(tmp_path)

    reconciled = cli_session_handoff._reconcile_with_session_binding(tmp_path, envelope)

    binding_fields = {field.name for field in fields(Binding)}
    assert {"session_context_id", "subject", "created_at"} <= binding_fields
    assert reconciled["session_init_binding"] == {
        "session_context_id": binding.session_context_id,
        "subject": binding.subject,
        "created_at": binding.created_at,
        "source": "session_init_bindings (database, authoritative for governed writes)",
    }
    assert "minimum_idempotency_identity" not in reconciled["session_init_binding"]
    assert "init_command_digest" not in reconciled["session_init_binding"]
    assert "envelope_id" not in reconciled["session_init_binding"]


def test_reconcile_without_binding_returns_envelope_unchanged(tmp_path: Path) -> None:
    envelope = {"session_id": "unbound-context", "role": "prime-builder"}

    assert cli_session_handoff._reconcile_with_session_binding(tmp_path, envelope) == envelope


def test_envelope_show_with_binding_exits_zero(tmp_path: Path, monkeypatch) -> None:
    envelope, binding = _bound_envelope(tmp_path)
    monkeypatch.setattr(
        cli_session_handoff,
        "_resolve_config",
        lambda _ctx: types.SimpleNamespace(project_root=str(tmp_path)),
    )
    monkeypatch.setattr(session_envelope, "load_current", lambda *_args, **_kwargs: envelope)

    result = CliRunner().invoke(
        cli_session_handoff.session_group,
        ["envelope", "show", "--harness-name", "codex"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["session_init_binding"]["session_context_id"] == binding.session_context_id
