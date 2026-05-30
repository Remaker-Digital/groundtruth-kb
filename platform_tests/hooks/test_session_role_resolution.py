"""Unit tests for the shared session-role resolver (Slice 4).

bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-001.md
(Codex GO at -002).

Covers the interactive rows of ``DCL-SESSION-ROLE-RESOLUTION-001``:

- assertion 7: marker role must be in {prime-builder, loyal-opposition}.
- assertion 6: a marker whose session id mismatches the current session id is
  stale and falls back to durable.
- marker > durable precedence; durable fallback on absent/invalid/stale marker.
- the resolver is READ-ONLY (never writes the marker or the durable role map).
- the resolver's marker path equals the Slice 2 writer path (no drift).
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


def _write_marker(root: Path, role: str, session_id: str | None) -> Path:
    marker = srr.session_role_marker_path(root)
    marker.parent.mkdir(parents=True, exist_ok=True)
    body = {"role": role, "session_id": session_id, "source": "init_keyword"}
    marker.write_text(json.dumps(body, sort_keys=True) + "\n", encoding="utf-8")
    return marker


def _seed_registry(root: Path, role_set: list[str]) -> None:
    """Seed an isolated groundtruth.db harnesses registry + projection.

    Mirrors platform_tests/hooks/test_workstream_focus.py: tests that exercise
    the REAL durable lookup seed an isolated DB under tmp_path so they never
    touch the live registry.
    """
    from groundtruth_kb.db import KnowledgeDB
    from groundtruth_kb.harness_projection import generate_harness_projection

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    db.insert_harness(
        id="B",
        harness_name="claude",
        harness_type="claude",
        role=list(role_set),
        changed_by="test",
        change_reason="Slice 4 resolver read-only fixture",
        status="active",
    )
    generate_harness_projection(db, root)


# ---------------------------------------------------------------------------
# Resolution table (monkeypatched durable so the table logic is isolated).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("role", "expected"), [("pb", srr.ROLE_PRIME), ("lo", srr.ROLE_LO)])
def test_resolver_marker_beats_durable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, role: str, expected: str
) -> None:
    # durable is the OPPOSITE of the marker so a "marker wins" result is unambiguous.
    opposite = srr.ROLE_LO if expected == srr.ROLE_PRIME else srr.ROLE_PRIME
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: opposite)
    _write_marker(tmp_path, expected, "sess-1")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == expected
    assert source == "marker"


def test_resolver_invalid_role_falls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    _write_marker(tmp_path, "bogus-role", "sess-1")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_PRIME
    assert source == "durable_marker_invalid_role"


def test_resolver_stale_session_falls_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    _write_marker(tmp_path, srr.ROLE_LO, "old-session")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="new-session")
    assert resolved == srr.ROLE_PRIME
    assert source == "durable_marker_stale_session"


def test_resolver_accepts_unverified_when_no_session_id(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    _write_marker(tmp_path, srr.ROLE_LO, "sess-1")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id=None)
    assert resolved == srr.ROLE_LO
    assert source == "marker_session_id_unverified"


@pytest.mark.parametrize("durable", [srr.ROLE_PRIME, srr.ROLE_LO])
def test_resolver_no_marker_uses_durable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, durable: str) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: durable)
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == durable
    assert source == "durable_marker_absent"


def test_resolver_malformed_marker_uses_durable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(srr, "_durable_role", lambda *a, **k: srr.ROLE_PRIME)
    marker = srr.session_role_marker_path(tmp_path)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("{ not valid json", encoding="utf-8")
    resolved, source = srr.resolve_interactive_session_role(tmp_path, current_session_id="sess-1")
    assert resolved == srr.ROLE_PRIME
    assert source == "durable_marker_absent"


# ---------------------------------------------------------------------------
# Path parity + read-only guarantees (real durable lookup, seeded registry).
# ---------------------------------------------------------------------------


def test_resolver_marker_path_matches_writer() -> None:
    """The resolver's read target must equal the Slice 2 writer's path."""
    import scripts.workstream_focus as wsf

    root = REPO_ROOT
    assert srr.session_role_marker_path(root) == wsf._session_role_marker_path(root)


def test_resolver_is_read_only(tmp_path: Path) -> None:
    """The REAL resolver mutates neither the marker nor the durable role map."""
    _seed_registry(tmp_path, ["prime-builder"])
    marker = _write_marker(tmp_path, srr.ROLE_LO, "sess-1")
    projection = tmp_path / "harness-state" / "harness-registry.json"

    def _sha(p: Path) -> str | None:
        try:
            return hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError:
            return None

    marker_before, proj_before = _sha(marker), _sha(projection)
    # Real durable lookup (no monkeypatch): durable is prime-builder; marker is
    # lo with a matching session id, so the marker wins.
    resolved, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id="sess-1", harness_name="claude"
    )
    assert resolved == srr.ROLE_LO
    assert source == "marker"
    assert _sha(marker) == marker_before, "resolver mutated the marker file"
    assert _sha(projection) == proj_before, "resolver mutated the durable role map"


def test_durable_lookup_reads_seeded_role(tmp_path: Path) -> None:
    """The durable fallback returns the seeded harness role (read path works)."""
    _seed_registry(tmp_path, ["loyal-opposition"])
    # No marker -> durable fallback returns the seeded role.
    resolved, source = srr.resolve_interactive_session_role(
        tmp_path, current_session_id="sess-1", harness_name="claude"
    )
    assert resolved == srr.ROLE_LO
    assert source == "durable_marker_absent"
