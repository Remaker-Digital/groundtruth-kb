"""Slice 7: doctor session-role marker checks.

bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-001.md
(Codex GO at -002).

Covers the two read-only doctor checks:
- _check_session_role_marker_validity: structural validation
  (DCL-SESSION-ROLE-RESOLUTION-001 assertion 6 non-null session id; assertion 7
  role-set membership).
- _check_session_role_marker_session_id_alignment: best-effort staleness using
  the resolver's env fallback session id; INFO when none is available; PASS when
  the marker is structurally invalid (no double-WARN).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
for p in (str(REPO_ROOT), str(_PACKAGE_SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

from groundtruth_kb.project import doctor  # noqa: E402

_ALL_ENV = (
    "GTKB_SESSION_ID",
    "CODEX_SESSION_ID",
    "CODEX_THREAD_ID",
    "CLAUDE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
)


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip all session-id env vars so each test controls them explicitly.

    Necessary because CLAUDE_CODE_SESSION_ID is set in a live session runtime.
    """
    for name in _ALL_ENV:
        monkeypatch.delenv(name, raising=False)


def _write_marker(target: Path, body: object) -> Path:
    marker = doctor._session_role_marker_path(target)
    marker.parent.mkdir(parents=True, exist_ok=True)
    text = body if isinstance(body, str) else json.dumps(body)
    marker.write_text(text, encoding="utf-8")
    return marker


# ---------------------------------------------------------------------------
# Validity check.
# ---------------------------------------------------------------------------


def test_validity_pass_when_no_marker(tmp_path: Path) -> None:
    assert doctor._check_session_role_marker_validity(tmp_path).status == "pass"


def test_validity_pass_for_valid_marker(tmp_path: Path) -> None:
    _write_marker(tmp_path, {"role": "loyal-opposition", "session_id": "sess-1", "source": "init_keyword"})
    check = doctor._check_session_role_marker_validity(tmp_path)
    assert check.status == "pass"
    assert "loyal-opposition" in check.message


def test_validity_warns_on_malformed_json(tmp_path: Path) -> None:
    _write_marker(tmp_path, "{ not valid json")
    assert doctor._check_session_role_marker_validity(tmp_path).status == "warning"


@pytest.mark.parametrize("session_id", [None, "", "   ", 123])
def test_validity_warns_on_missing_session_id(tmp_path: Path, session_id: object) -> None:
    _write_marker(tmp_path, {"role": "prime-builder", "session_id": session_id})
    assert doctor._check_session_role_marker_validity(tmp_path).status == "warning"


def test_validity_warns_on_bad_role(tmp_path: Path) -> None:
    _write_marker(tmp_path, {"role": "bogus-role", "session_id": "sess-1"})
    assert doctor._check_session_role_marker_validity(tmp_path).status == "warning"


# ---------------------------------------------------------------------------
# Alignment check (best-effort env-based).
# ---------------------------------------------------------------------------


def test_alignment_pass_when_no_marker(tmp_path: Path, clean_env: None) -> None:
    assert doctor._check_session_role_marker_session_id_alignment(tmp_path).status == "pass"


def test_alignment_pass_when_aligned(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    _write_marker(tmp_path, {"role": "prime-builder", "session_id": "sess-XYZ"})
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "sess-XYZ")
    assert doctor._check_session_role_marker_session_id_alignment(tmp_path).status == "pass"


def test_alignment_warns_on_stale_marker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, clean_env: None) -> None:
    _write_marker(tmp_path, {"role": "prime-builder", "session_id": "old-session"})
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "new-session")
    check = doctor._check_session_role_marker_session_id_alignment(tmp_path)
    assert check.status == "warning"
    assert "stale" in check.message


def test_alignment_info_when_no_env_session_id(tmp_path: Path, clean_env: None) -> None:
    _write_marker(tmp_path, {"role": "prime-builder", "session_id": "sess-1"})
    assert doctor._check_session_role_marker_session_id_alignment(tmp_path).status == "info"


def test_alignment_pass_when_marker_invalid_no_double_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, clean_env: None
) -> None:
    """A structurally invalid marker -> validity warns, alignment passes."""
    _write_marker(tmp_path, {"role": "prime-builder", "session_id": ""})  # invalid session id
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "anything")
    assert doctor._check_session_role_marker_validity(tmp_path).status == "warning"
    assert doctor._check_session_role_marker_session_id_alignment(tmp_path).status == "pass"


def test_alignment_pass_when_bad_role_and_stale_session_no_double_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, clean_env: None
) -> None:
    """Codex NO-GO -004 F1: a marker with an INVALID role AND a stale session id
    must NOT double-WARN. Validity owns the role warning; alignment defers (pass)
    even though the session id would otherwise compare as stale."""
    _write_marker(tmp_path, {"role": "bogus-role", "session_id": "old-session"})
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "new-session")
    assert doctor._check_session_role_marker_validity(tmp_path).status == "warning"
    assert doctor._check_session_role_marker_session_id_alignment(tmp_path).status == "pass"


def test_env_fallback_priority_first_listed_wins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, clean_env: None
) -> None:
    """The first env in the documented order is preferred (matches the resolver)."""
    _write_marker(tmp_path, {"role": "prime-builder", "session_id": "from-first"})
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "from-last")
    monkeypatch.setenv("GTKB_SESSION_ID", "from-first")
    assert doctor._check_session_role_marker_session_id_alignment(tmp_path).status == "pass"


# ---------------------------------------------------------------------------
# Drift guard: the doctor's marker path must equal the resolver's writer path.
# ---------------------------------------------------------------------------


def test_doctor_marker_path_matches_resolver() -> None:
    import scripts.session_role_resolution as srr

    root = REPO_ROOT
    assert doctor._session_role_marker_path(root) == srr.session_role_marker_path(root)


def test_doctor_env_fallbacks_match_resolver() -> None:
    """The duplicated env-fallback tuple must equal the resolver's set."""
    import scripts.workstream_focus as wsf

    assert tuple(doctor._SESSION_ID_ENV_FALLBACKS) == tuple(wsf._SESSION_ID_ENV_FALLBACKS)
