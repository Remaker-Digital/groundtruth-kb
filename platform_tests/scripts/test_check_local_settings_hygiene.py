# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the Slice B machine-local settings hygiene guard.

GTKB-STARTUP-REFRACTOR-001 Slice B (WI-4269), advisory F3. Verifies that
``scripts/check_local_settings_hygiene.py`` flags legacy-archive path references
and credential-shaped literals in ``.claude/settings.local.json`` permission
entries, passes clean input, and never leaks a matched value verbatim.

Credential-shaped fixture strings are assembled at runtime via concatenation so
no contiguous secret-shaped span exists in this source file (avoids a
false-positive credential-scan block on the test itself).

Authority: ``bridge/gtkb-startup-refractor-slice-b-local-settings-hygiene-002.md``
(GO); ``GOV-ARTIFACT-APPROVAL-001`` (credential safety);
``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` (in-root boundary).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import check_local_settings_hygiene as guard  # noqa: E402

# Runtime-assembled fixtures (no contiguous secret span in source).
_ARCHIVE_ENTRY = "Read(" + "E:\\Claude-Playground\\CLAUDE-PROJECTS\\groundtruth-kb\\**)"
_ACCESS_KEY_ENTRY = "Bash(export X=...;" + "access" + "key=" + "FAKEPLACEHOLDER123)"
_CONNECTION_STRING_ENTRY = "Bash(" + "AZURE_COMMUNICATION_" + "CONNECTION_" + "STRING=endpoint=https://x;)"
_CLEAN_ENTRIES = ["Read(E:\\GT-KB\\**)", "Bash(python -m pytest:*)", "Bash(git status:*)"]


def _settings(allow: list[str]) -> dict:
    return {"permissions": {"allow": list(allow)}}


def test_flags_legacy_archive_path() -> None:
    violations = guard.find_violations(_settings([*_CLEAN_ENTRIES, _ARCHIVE_ENTRY]))
    assert any(v.startswith("legacy-archive-path") for v in violations), violations


def test_flags_credential_access_key() -> None:
    violations = guard.find_violations(_settings([_ACCESS_KEY_ENTRY]))
    assert any(v.startswith("credential-access-key") for v in violations), violations


def test_flags_credential_connection_string() -> None:
    violations = guard.find_violations(_settings([_CONNECTION_STRING_ENTRY]))
    assert any(v.startswith("credential-connection-string") for v in violations), violations


def test_clean_settings_pass() -> None:
    assert guard.find_violations(_settings(_CLEAN_ENTRIES)) == []


def test_violations_are_redacted() -> None:
    """The matched value must never appear verbatim in the violation report."""
    violations = guard.find_violations(_settings([_ACCESS_KEY_ENTRY, _ARCHIVE_ENTRY]))
    blob = "\n".join(violations)
    assert "FAKEPLACEHOLDER123" not in blob
    assert "Claude-Playground" not in blob
    assert all("<redacted" in v for v in violations), violations


def test_main_exit_codes(tmp_path: Path) -> None:
    clean = tmp_path / "clean.json"
    clean.write_text(json.dumps(_settings(_CLEAN_ENTRIES)), encoding="utf-8")
    assert guard.main(["--path", str(clean)]) == 0

    dirty = tmp_path / "dirty.json"
    dirty.write_text(json.dumps(_settings([*_CLEAN_ENTRIES, _ARCHIVE_ENTRY])), encoding="utf-8")
    assert guard.main(["--path", str(dirty)]) == 1


def test_main_absent_file_is_ok(tmp_path: Path) -> None:
    assert guard.main(["--path", str(tmp_path / "nope.json")]) == 0
