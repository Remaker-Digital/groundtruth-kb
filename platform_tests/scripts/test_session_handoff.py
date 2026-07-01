from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.session import handoff


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
