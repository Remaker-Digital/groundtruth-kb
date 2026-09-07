"""Startup index must not require a filesystem session envelope (WI-6185)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STARTUP_FILES = (
    ROOT / "config" / "agent-control" / "SESSION-STARTUP-INDEX.md",
    ROOT / "config" / "agent-control" / "PRIME-BUILDER-STARTUP-OVERLAY.md",
    ROOT / "config" / "agent-control" / "gtkb-session-startup-index.md",
    ROOT / "config" / "agent-control" / "gtkb-pb-startup-overlay.md",
)
FORBIDDEN = ("session envelope open", "gt session envelope open")


def test_startup_files_have_no_envelope_open_instruction() -> None:
    for path in STARTUP_FILES:
        text = path.read_text(encoding="utf-8").lower()
        for needle in FORBIDDEN:
            assert needle not in text, f"{path} still instructs {needle!r}"


def test_startup_files_retain_init_marker_as_role_authority() -> None:
    for path in STARTUP_FILES:
        text = path.read_text(encoding="utf-8")
        assert "::init gtkb" in text, f"{path} lost ::init gtkb role authority"
