"""Tests for the WI-4534 Slice A role-eligibility guard on go_implementation claims.

Every oracle is the ``acquire()`` outcome (raise vs. acquired) plus the
persisted ``claim_status`` record, exercising the production registry interface.
Authority: GOV-SESSION-ROLE-AUTHORITY-001, DCL-SESSION-ROLE-RESOLUTION-001,
GOV-FILE-BRIDGE-AUTHORITY-001 (the guard adds no canonical INDEX write surface).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REGISTRY_PATH = SCRIPTS_DIR / "bridge_work_intent_registry.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _registry():
    return _load_module(REGISTRY_PATH, "bridge_work_intent_registry")


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


def _write_registry(root: Path, roles: dict[str, str]) -> None:
    """Write a test harness-registry projection mapping harness id -> role token."""
    harness_dir = root / "harness-state"
    harness_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": 1,
        "source_of_truth": "test fixture",
        "harnesses": [
            {"id": harness_id, "harness_name": harness_id.lower(), "role": [role], "status": "active"}
            for harness_id, role in roles.items()
        ],
    }
    (harness_dir / "harness-registry.json").write_text(json.dumps(document), encoding="utf-8")


def _write_marker(root: Path, role: str, session_id: str = "marker-session") -> None:
    marker_dir = root / ".claude" / "session"
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "active-session-role.json").write_text(
        json.dumps({"role": role, "session_id": session_id}), encoding="utf-8"
    )


@pytest.fixture
def env(monkeypatch):
    """Pin registry resolution to the test project_root (ignore ambient override)."""
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(registry, "now_utc", lambda: base)
    return registry


def test_go_impl_rejected_for_lo_dispatch_harness(tmp_path: Path, env) -> None:
    """GOV-SESSION-ROLE-AUTHORITY-001: an LO-role dispatch harness cannot hold go_implementation."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T20-07-29Z-loyal-opposition-D-20c71a"

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_allowed_for_prime_dispatch_harness(tmp_path: Path, env) -> None:
    """GOV-SESSION-ROLE-AUTHORITY-001: a prime-builder dispatch harness may hold go_implementation."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T22-19-33Z-prime-builder-B-6a8e3e"

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_go_impl_rejected_for_unknown_harness_id(tmp_path: Path, env) -> None:
    """F2: an unknown parsed harness id is not authorized even with a prime-builder token."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    # Token says prime-builder, but harness Z is absent from the registry.
    session_id = "2026-06-13T22-00-00Z-prime-builder-Z-a1b2c3"

    with pytest.raises(env.WorkIntentRegistryError, match="harness id absent from registry"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_resolves_from_registry_not_token(tmp_path: Path, env) -> None:
    """F2/d: registry role is authoritative over the session-id role token."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    # Token claims prime-builder, but registry says harness D is loyal-opposition.
    session_id = "2026-06-13T22-00-00Z-prime-builder-D-a1b2c3"

    with pytest.raises(env.WorkIntentRegistryError, match="loyal-opposition"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_rejected_for_uuid_session_without_prime_marker(tmp_path: Path, env) -> None:
    """F3: a raw-UUID session with no/non-Prime marker is rejected (no fail-open)."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"

    # No marker present.
    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None

    # A loyal-opposition marker is also not positive Prime evidence.
    _write_marker(tmp_path, "loyal-opposition", session_id=session_id)
    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_allowed_for_uuid_session_with_prime_marker(tmp_path: Path, env) -> None:
    """F3/b: an owner-declared interactive Prime session (raw-UUID) is accepted."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_marker(tmp_path, "prime-builder", session_id=session_id)

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_draft_claim_unaffected_for_lo_harness_on_non_go_thread(tmp_path: Path, env) -> None:
    """The guard is scoped to go_implementation: an LO harness may draft on a NEW-latest thread."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"draft-thread": "NEW"})
    session_id = "2026-06-13T22-00-00Z-loyal-opposition-D-20c71a"

    assert env.acquire("draft-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("draft-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_DRAFT


def test_go_impl_allowed_for_registry_acting_prime_builder(tmp_path: Path, env) -> None:
    """Compat: a registry acting-prime-builder role is Prime-eligible (READ-accepted)."""
    _write_registry(tmp_path, {"B": "prime-builder", "X": "acting-prime-builder"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T22-00-00Z-acting-prime-builder-X-a1b2c3"

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION
