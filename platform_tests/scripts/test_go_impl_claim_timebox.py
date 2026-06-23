"""Tests for GO-implementation work-intent claim time boxes."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REGISTRY_PATH = SCRIPTS_DIR / "bridge_work_intent_registry.py"
CLI_PATH = SCRIPTS_DIR / "bridge_claim_cli.py"
AXIS2_PATH = PROJECT_ROOT / ".claude" / "hooks" / "bridge-axis-2-surface.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_index(root: Path, statuses: dict[str, str]) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for slug, status in statuses.items():
        existing = sorted(
            (
                int(path.stem.rsplit("-", 1)[1])
                for path in bridge.glob(f"{slug}-*.md")
                if path.stem.rsplit("-", 1)[-1].isdigit()
            ),
            reverse=True,
        )
        if existing:
            version_number = existing[0] + 1
        else:
            version_number = 2 if status == "GO" else 1
            if status == "GO":
                (bridge / f"{slug}-001.md").write_text("NEW\n", encoding="utf-8")
        version = f"{version_number:03d}"
        (bridge / f"{slug}-{version}.md").write_text(f"{status}\n", encoding="utf-8")
        lines.extend([f"Document: {slug}", f"{status}: bridge/{slug}-{version}.md", ""])
    (bridge / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def _write_prime_marker(root: Path) -> None:
    """Write an owner-declared interactive Prime session-role marker into ``root``.

    WI-4534 Slice A made ``go_implementation`` claims Prime-only. These timebox
    tests exercise the deadline/extension/grace behavior of a *held* GO claim, so
    each must present positive Prime evidence. The interactive marker
    (``.claude/session/active-session-role.json`` with ``role == "prime-builder"``)
    is read from ``project_root`` with no env-override path, making it the
    hermetic eligibility source for a non-dispatch session id — see
    ``bridge_work_intent_registry._interactive_marker_role`` and the F3/b case in
    ``test_work_intent_role_eligibility``. Authority: GOV-SESSION-ROLE-AUTHORITY-001,
    DCL-SESSION-ROLE-RESOLUTION-001, DELIB-20263205 (scope expansion).
    """
    marker_dir = root / ".claude" / "session"
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "active-session-role.json").write_text(
        json.dumps({"role": "prime-builder", "session_id": "marker-session"}), encoding="utf-8"
    )


def _registry():
    return _load_module(REGISTRY_PATH, "bridge_work_intent_registry")


def _item(document: str):
    return SimpleNamespace(document_name=document, top_status="GO", top_file=f"bridge/{document}-002.md")


def test_go_claim_records_deadline_and_non_go_keeps_draft_ttl(tmp_path: Path, monkeypatch) -> None:
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(registry, "now_utc", lambda: base)
    _write_index(tmp_path, {"go-thread": "GO", "draft-thread": "NEW"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", ttl_seconds=123, project_root=tmp_path)
    go_holder = registry.current_holder("go-thread", project_root=tmp_path)
    assert go_holder["claim_kind"] == registry.CLAIM_KIND_GO_IMPLEMENTATION
    assert go_holder["implementation_deadline"] == "2026-06-13T00:30:00Z"
    assert go_holder["implementation_grace_expires_at"] == "2026-06-13T00:40:00Z"
    assert go_holder["ttl_expires_at"] == "2026-06-13T00:40:00Z"

    assert registry.acquire("draft-thread", "session-a", ttl_seconds=123, project_root=tmp_path)
    draft_holder = registry.current_holder("draft-thread", project_root=tmp_path)
    assert draft_holder["claim_kind"] == registry.CLAIM_KIND_DRAFT
    assert draft_holder["implementation_deadline"] is None
    assert draft_holder["ttl_expires_at"] == "2026-06-13T00:02:03Z"


def test_extend_adds_fixed_increment_and_refuses_past_total_hold_cap(tmp_path: Path, monkeypatch) -> None:
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    for extension_number, expected_deadline in enumerate(
        ("2026-06-13T01:00:00Z", "2026-06-13T01:30:00Z", "2026-06-13T02:00:00Z"),
        start=1,
    ):
        now["value"] = base + timedelta(minutes=extension_number)
        holder = registry.extend("go-thread", "session-a", project_root=tmp_path)
        assert holder["extensions_used"] == extension_number
        assert holder["implementation_deadline"] == expected_deadline

    with pytest.raises(registry.WorkIntentRegistryError, match="Extension cap reached"):
        registry.extend("go-thread", "session-a", project_root=tmp_path)
    assert registry.claim_status("go-thread", project_root=tmp_path)["extension_capped"] is True


def test_lapsed_go_claim_releases_for_takeover_after_grace(tmp_path: Path, monkeypatch) -> None:
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    now["value"] = base + timedelta(minutes=41)
    assert registry.current_holder("go-thread", project_root=tmp_path) is None
    assert [claim["thread_slug"] for claim in registry.lapsed_go_implementation_claims(project_root=tmp_path)] == [
        "go-thread"
    ]
    assert registry.acquire("go-thread", "session-b", project_root=tmp_path)
    assert registry.current_holder("go-thread", project_root=tmp_path)["session_id"] == "session-b"


def test_report_latest_status_stops_lapsed_go_claim_detection(tmp_path: Path, monkeypatch) -> None:
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)

    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    _write_index(tmp_path, {"go-thread": "NEW"})
    now["value"] = base + timedelta(hours=3)
    assert registry.lapsed_go_implementation_claims(project_root=tmp_path) == []


def test_cli_claim_extend_status_reports_go_implementation_fields(tmp_path: Path) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})
    # WI-4534 Slice A: a go_implementation claim now requires positive Prime
    # evidence. Provide it hermetically via the in-tmp_path interactive Prime
    # marker plus an explicit non-dispatch --session-id (arg-first resolution,
    # immune to ambient harness session env vars). The prior form copied
    # os.environ and injected CODEX_THREAD_ID, which made the subprocess's
    # eligibility depend on the running harness's leaked session/registry env —
    # non-deterministic across Prime/LO verification environments.
    _write_prime_marker(tmp_path)
    session_id = "interactive-prime-session"
    claim = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "claim",
            "go-thread",
            "--session-id",
            session_id,
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert claim.returncode == 0, claim.stderr
    assert json.loads(claim.stdout)["claim_kind"] == "go_implementation"

    extended = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "extend",
            "go-thread",
            "--session-id",
            session_id,
            "--project-root",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert extended.returncode == 0, extended.stderr
    assert json.loads(extended.stdout)["extensions_used"] == 1

    status = subprocess.run(
        [sys.executable, str(CLI_PATH), "status", "go-thread", "--project-root", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert status.returncode == 0, status.stderr
    payload = json.loads(status.stdout)
    assert payload["claim_kind"] == "go_implementation"
    assert payload["latest_bridge_status"] == "GO"
    assert payload["lapsed_go_implementation"] is False


def test_axis2_render_surfaces_available_go_implementation_work() -> None:
    mod = _load_module(AXIS2_PATH, "bridge_axis_2_surface_timebox")

    rendered = mod._render_surface([_item("gtkb-go-thread")], mod.ROLE_PRIME, [])

    assert "AVAILABLE GO-IMPLEMENTATION" in rendered
    assert "gtkb-go-thread" in rendered


def test_doctor_warns_on_lapsed_go_implementation_claim(tmp_path: Path, monkeypatch) -> None:
    registry = _registry()
    sys.modules["bridge_work_intent_registry"] = registry
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    now = {"value": base}
    monkeypatch.setattr(registry, "now_utc", lambda: now["value"])
    _write_index(tmp_path, {"go-thread": "GO"})
    _write_prime_marker(tmp_path)
    assert registry.acquire("go-thread", "session-a", project_root=tmp_path)
    now["value"] = base + timedelta(minutes=41)

    from groundtruth_kb.project import doctor

    check = doctor._check_lapsed_go_implementation_claims(tmp_path)

    assert check.status == "warning"
    assert "go-thread" in check.message


def test_registry_migrates_existing_minimal_claim_table(tmp_path: Path) -> None:
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.execute(
        """
        CREATE TABLE work_intent_claims (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_slug TEXT NOT NULL,
            session_id TEXT NOT NULL,
            acquired_at TEXT NOT NULL,
            ttl_expires_at TEXT NOT NULL,
            UNIQUE(thread_slug)
        )
        """
    )
    conn.commit()
    conn.close()
    _write_index(tmp_path, {"draft-thread": "NEW"})

    registry = _registry()
    assert registry.acquire("draft-thread", "session-a", project_root=tmp_path)
    holder = registry.current_holder("draft-thread", project_root=tmp_path)
    assert holder["claim_kind"] == registry.CLAIM_KIND_DRAFT
