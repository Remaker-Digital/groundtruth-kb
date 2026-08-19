"""Harness identity may describe an author but never selects the session role."""

from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(SRC) not in os.sys.path:
    os.sys.path.insert(0, str(SRC))

from groundtruth_kb.bridge import verdict_filing as vf  # noqa: E402
from groundtruth_kb.session import envelope as env_mod  # noqa: E402
from groundtruth_kb.session.attestation import bind_exact_init  # noqa: E402

CONTENT = (
    "GO\n\n"
    "author_model: test-model\n"
    "author_model_version: test-model-v1\n"
    "author_model_configuration: fixture configuration\n"
)


@pytest.fixture(autouse=True)
def _clear_harness_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GTKB_HARNESS_NAME", raising=False)


def _schema(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "CREATE TABLE session_init_bindings ("
            "invoking_context TEXT PRIMARY KEY, envelope_id TEXT, command_digest TEXT, "
            "subject TEXT, created_at TEXT)"
        )
        conn.execute(
            "CREATE TABLE session_role_attestations ("
            "envelope_id TEXT, seq INTEGER, role TEXT, source_event TEXT, "
            "issuer TEXT, created_at TEXT, evidence_digest TEXT, "
            "PRIMARY KEY (envelope_id, seq))"
        )
    conn.close()


def _bind(root: Path, context: str, role: str) -> None:
    _schema(root / "groundtruth.db")
    bind_exact_init(
        root / "groundtruth.db",
        invoking_context=context,
        init_command=f"::init gtkb {role}",
        issuer="fixture-harness",
    )


@pytest.mark.parametrize("harness_name", ["codex", "claude", "goose"])
def test_harness_identity_cannot_change_lo_attestation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    harness_name: str,
) -> None:
    context = f"lo-on-{harness_name}"
    _bind(tmp_path, context, "lo")
    monkeypatch.setenv("GTKB_HARNESS_NAME", harness_name)

    derived = vf._metadata_from_envelope(context, tmp_path, CONTENT)

    assert derived["author_identity"].startswith(f"loyal-opposition/{harness_name}")
    assert derived["author_role_attestation"].startswith("role-attestation:SENV-")


def test_harness_identity_cannot_change_pb_attestation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = "pb-on-goose"
    _bind(tmp_path, context, "pb")
    monkeypatch.setenv("GTKB_HARNESS_NAME", "goose")

    derived = vf._metadata_from_envelope(context, tmp_path, CONTENT)

    assert derived["author_identity"].startswith("prime-builder/goose")


def test_unbound_context_never_falls_back_to_harness_registry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _schema(tmp_path / "groundtruth.db")
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    registry = tmp_path / "harness-state" / "harness-registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        '{"harnesses":[{"id":"A","harness_name":"codex","role":["loyal-opposition"]}]}',
        encoding="utf-8",
    )

    with pytest.raises(vf.VerdictFilingError, match="session-init binding exists"):
        vf._metadata_from_envelope("unbound-context", tmp_path, CONTENT)


def test_harness_name_returns_none_when_identity_unresolvable() -> None:
    assert vf._harness_name() is None
    assert vf._harness_name(None) is None


def test_harness_name_returns_none_on_identity_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(*_args: object, **_kwargs: object) -> tuple[str, str]:
        raise env_mod.EnvelopeError("conflicting runtime markers")

    monkeypatch.setattr(env_mod, "resolve_acting_harness_identity", _raise)
    assert vf._harness_name(PROJECT_ROOT) is None


def test_explicit_harness_env_retains_identity_precedence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")

    def _must_not_run(*_args: object, **_kwargs: object) -> tuple[str, str]:
        raise AssertionError("fallback consulted despite GTKB_HARNESS_NAME being set")

    monkeypatch.setattr(env_mod, "resolve_acting_harness_identity", _must_not_run)
    assert vf._harness_name(PROJECT_ROOT) == "codex"


def test_marker_continuity_order_unchanged() -> None:
    """This slice does not alter invoking-context environment precedence."""

    rel = "scripts/gtkb_session_id.py"
    head = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    def _block(text: str) -> str:
        marker = "MARKER_CONTINUITY_ORDER"
        start = text.index(marker)
        end = text.index("]", start)
        return text[start : end + 1]

    current = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
    assert _block(current) == _block(head)


@pytest.mark.parametrize(
    ("harness_name", "expected_id"),
    [("claude", "B"), ("codex", "A"), ("antigravity", "C")],
)
def test_harness_id_map_is_identity_only(harness_name: str, expected_id: str) -> None:
    assert vf._harness_id_for(harness_name, PROJECT_ROOT) == expected_id
