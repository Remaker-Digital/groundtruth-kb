"""Regression tests for WI-4333 harness-state reader migration."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def test_envelope_resolves_identity_and_role_through_entrypoints(monkeypatch: Any, tmp_path: Path) -> None:
    """Session envelope readers use the canonical harness-projection entrypoints."""
    from groundtruth_kb.session import envelope

    calls: list[tuple[str, Path]] = []

    def fake_read_identity(project_root: Path) -> dict[str, Any]:
        calls.append(("identity", project_root))
        return {"harnesses": {"codex": {"id": "A"}}}

    def fake_read_roles(project_root: Path) -> dict[str, Any]:
        calls.append(("roles", project_root))
        return {"harnesses": [{"id": "A", "role": ["loyal-opposition"]}]}

    monkeypatch.setattr(envelope, "read_identity", fake_read_identity)
    monkeypatch.setattr(envelope, "read_roles", fake_read_roles)

    assert envelope.resolve_harness_identity(tmp_path, harness_name="codex") == ("codex", "A")
    assert envelope._resolve_role(tmp_path, "A") == "loyal-opposition"
    assert calls == [("identity", tmp_path), ("roles", tmp_path)]


def test_handoff_resolves_active_harness_through_identity_entrypoint(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    """The handoff resolver no longer reads harness-identities.json directly."""
    from groundtruth_kb.session import handoff

    archive_dir = tmp_path / "harness-state" / "claude" / "session-envelope-archive"
    archive_dir.mkdir(parents=True)
    calls: list[Path] = []

    def fake_read_identity(project_root: Path) -> dict[str, Any]:
        calls.append(project_root)
        return {"harnesses": {"claude": {"id": "B"}}}

    monkeypatch.setattr(handoff, "read_identity", fake_read_identity)

    assert handoff._resolve_active_harness_name(tmp_path) == "claude"
    assert calls == [tmp_path]


def test_mcp_roles_resolve_default_and_current_role_through_entrypoint(
    monkeypatch: Any,
    tmp_path: Path,
) -> None:
    """The MCP role surface uses read_roles for the default production path."""
    from groundtruth_kb.mcp_surface import roles

    projection = {
        "harnesses": [
            {"id": "A", "harness_name": "codex", "role": ["loyal-opposition"]},
            {"id": "B", "harness_name": "claude", "role": ["prime-builder"]},
        ]
    }
    calls: list[Path] = []

    def fake_read_roles(project_root: Path) -> dict[str, Any]:
        calls.append(project_root)
        return projection

    monkeypatch.setattr(roles, "read_roles", fake_read_roles)
    monkeypatch.setattr(roles, "resolve_safe_path", lambda _path: tmp_path)
    monkeypatch.delenv("GTKB_HARNESS_ID", raising=False)
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    for name in list(__import__("os").environ.keys()):
        if name.startswith("CLAUDE_CODE"):
            monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CODEX_HOME", "/tmp/codex-test")

    assert roles._default_harness_id() == "A"
    assert roles.current_role(harness_id="B") == "prime-builder"
    assert calls == [tmp_path, tmp_path]
