"""WI-4540 per-session resolver authority tests (additive transition, R-B1).

bridge/gtkb-wi4540-per-session-role-marker-context-envelope-003.md (Codex/Ollama
GO at -004).

These tests cover the WI-4540 additions to
``scripts.session_role_resolution.resolve_interactive_session_role``:

- the per-session marker (``.claude/session/role-<sanitized_session_id>.json``)
  is the AUTHORITY when a ``current_session_id`` is available — it is read
  before the legacy shared single-file marker;
- the per-session marker's stored ``session_id`` is validated against the
  querying id (``DCL-SESSION-ROLE-RESOLUTION-001`` assertion 6);
- an invalid per-session role falls back to durable (assertion 7);
- absent a per-session marker, the resolver falls back to the legacy single-file
  marker (the existing behavior, preserved during the transition window);
- the resolver remains strictly READ-ONLY.

The pre-WI-4540 resolution table (legacy single-file marker) is covered by
``platform_tests/hooks/test_session_role_resolution.py`` and is intentionally
not duplicated here.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
_PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

import scripts.session_role_resolution as srr  # noqa: E402
from scripts.gtkb_session_id import per_session_role_marker_path  # noqa: E402


def _write_per_session(root: Path, role: str, session_id: str, *, stored_session_id: str | None = None) -> Path:
    """Write a per-session marker keyed under ``session_id``.

    ``stored_session_id`` defaults to ``session_id`` but can be overridden to
    simulate a (rare) sanitized-key collision where the stored raw id differs.
    """
    marker = per_session_role_marker_path(root, session_id)
    marker.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "role": role,
        "session_id": session_id if stored_session_id is None else stored_session_id,
        "session_id_source": "payload",
        "source": "init_keyword",
    }
    marker.write_text(json.dumps(body, sort_keys=True) + "\n", encoding="utf-8")
    return marker


def _write_legacy(root: Path, role: str, session_id: str | None) -> Path:
    marker = srr.session_role_marker_path(root)
    marker.parent.mkdir(parents=True, exist_ok=True)
    body = {"role": role, "session_id": session_id, "source": "init_keyword"}
    marker.write_text(json.dumps(body, sort_keys=True) + "\n", encoding="utf-8")
    return marker


def _write_envelope(root: Path, harness_name: str, role: str) -> Path:
    envelope = root / "harness-state" / harness_name / "session-envelope.json"
    envelope.parent.mkdir(parents=True, exist_ok=True)
    envelope.write_text(
        json.dumps(
            {
                "status": "open",
                "role_resolved": role,
                "role_asserted": role,
                "init_keyword": "::init gtkb pb" if role == srr.ROLE_PRIME else "::init gtkb lo",
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return envelope


@pytest.mark.parametrize(("role", "expected"), [("pb", srr.ROLE_PRIME), ("lo", srr.ROLE_LO)])
def test_per_session_marker_beats_durable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, role: str, expected: str
) -> None:
    opposite = srr.ROLE_LO if expected == srr.ROLE_PRIME else srr.ROLE_PRIME
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: opposite)
    _write_per_session(tmp_path, expected, "sess-1")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == expected
    assert source == "marker"


def test_per_session_marker_is_authority_over_legacy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """When BOTH a per-session marker and the legacy single-file marker exist for
    the same querying id, the per-session marker is authoritative."""
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    _write_legacy(tmp_path, srr.ROLE_PRIME, "sess-1")
    _write_per_session(tmp_path, srr.ROLE_LO, "sess-1")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_LO
    assert source == "marker"


def test_per_session_invalid_role_falls_back_to_durable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    _write_per_session(tmp_path, "bogus-role", "sess-1")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_PRIME
    assert source == "durable_marker_invalid_role"

    details = srr.resolve_interactive_session_role_details(tmp_path, current_session_id="sess-1")
    assert details["interactive_resolved_role"] == srr.ROLE_PRIME
    assert details["interactive_role_source"] == "durable_marker_invalid_role"
    assert details["durable_registry_role"] == srr.ROLE_PRIME
    assert details["authority_mode"] == "durable_registry_fallback"


def test_per_session_stored_id_mismatch_falls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A per-session marker whose stored raw session_id differs from the querying
    id (sanitized-key collision) is treated as stale (assertion 6)."""
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    _write_per_session(tmp_path, srr.ROLE_LO, "sess-1", stored_session_id="a-different-raw-id")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_PRIME
    assert source == "durable_marker_stale_session"

    details = srr.resolve_interactive_session_role_details(tmp_path, current_session_id="sess-1")
    assert details["interactive_resolved_role"] == srr.ROLE_PRIME
    assert details["interactive_role_source"] == "durable_marker_stale_session"
    assert details["durable_registry_role"] == srr.ROLE_PRIME
    assert details["authority_mode"] == "durable_registry_fallback"


def test_no_per_session_marker_falls_back_to_legacy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Absent a per-session marker, the resolver falls back to the legacy
    single-file marker (transition-window behavior, unchanged)."""
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    _write_legacy(tmp_path, srr.ROLE_LO, "sess-1")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_LO
    assert source == "marker"


def test_no_marker_at_all_uses_durable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_LO)
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_LO
    assert source == "durable_marker_absent"


def test_open_envelope_role_beats_durable_and_reports_envelope_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Durable Codex LO + transcript PB envelope resolves PB and does not label the source as durable."""
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_LO)
    _write_envelope(tmp_path, "codex", srr.ROLE_PRIME)

    resolved, source = srr.resolve_interactive_session_role(
        tmp_path,
        current_session_id="sess-1",
        harness_name="codex",
    )
    assert resolved == srr.ROLE_PRIME
    assert source == "session_envelope"

    details = srr.resolve_interactive_session_role_details(
        tmp_path,
        current_session_id="sess-1",
        harness_name="codex",
    )
    assert details["interactive_resolved_role"] == srr.ROLE_PRIME
    assert details["interactive_role_source"] == "session_envelope"
    assert details["durable_registry_role"] == srr.ROLE_LO
    assert details["authority_mode"] == "interactive_transcript"


def test_per_session_resolver_is_read_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    marker = _write_per_session(tmp_path, srr.ROLE_LO, "sess-1")

    def _sha(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    before = _sha(marker)
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_LO
    assert source == "marker"
    assert _sha(marker) == before, "resolver mutated the per-session marker file"


def test_per_session_path_matches_writer(tmp_path: Path) -> None:
    """The resolver's per-session read target equals the WI-4540 writer's path."""
    import scripts.workstream_focus as wsf

    assert per_session_role_marker_path(tmp_path, "sess-1") == wsf._per_session_role_marker_path(tmp_path, "sess-1")
